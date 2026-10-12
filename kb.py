import os

from dotenv import load_dotenv


from langchain.chat_models import init_chat_model
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import LLMChainExtractor

from kb_builder import KnowledgeBaseBuilder
from prompt_templates.system_prompts import system_prompt
from prompt_templates.user_prompts import user_prompt

load_dotenv(override=True)

default_chroma_dir = os.path.join(os.getcwd(),'chroma_db')

class KnowledgeBase:

    def __init__(self,
                 build_kb_from_scratch=True,
                 embedding_model_name="text-embedding-3-small",
                 chroma_db_dir = default_chroma_dir
                 ):
        self.embedding_model = OpenAIEmbeddings(model=embedding_model_name)

        if build_kb_from_scratch:
            kb_builder = KnowledgeBaseBuilder(embedding_model=embedding_model_name,
                                                   chroma_dir=chroma_db_dir)
            self.vector_store = kb_builder.get_kb_vector_store()
        else:
            self.vector_store = Chroma(persist_directory=default_chroma_dir,
                                       embedding_function=OpenAIEmbeddings(model=embedding_model_name)
                                       )

    def _retrieved_docs_formatter(self, retrieved_docs):
        formatted_context = []

        if not retrieved_docs:
            return "No relevant documents found"

        for i, doc in enumerate(retrieved_docs):
            source = doc.metadata.get('article_name', 'Unknown')
            formatted_context.append(f"[Article Source {i + 1}: {source}]\n {doc.page_content}")

        return "\n\n-----------------------------------------------------------\n\n".join(formatted_context)

    def _get_all_kb_articles(self):
        kb = self.vector_store
        raw_articles = kb.get()
        all_articles = []

        for text, metadata in zip(raw_articles["documents"], raw_articles["metadatas"]):
            doc_obj = Document(page_content=text, metadata=metadata)
            all_articles.append(doc_obj)

        return all_articles

    def doc_retriever(self, query):
        retriever = self.vector_store.as_retriever()
        ALL_KB_ARTICLES = self._get_all_kb_articles()

        bm25_retriever = BM25Retriever.from_documents(ALL_KB_ARTICLES)
        bm25_retriever.k = 5

        semantic_retriever = self.vector_store.as_retriever(search_kwargs={"k":5})
        hybrid_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, semantic_retriever],
            weights=[0.4, 0.6]
        )

        retrieved_docs = hybrid_retriever.invoke(query)

        return self._retrieved_docs_formatter(retrieved_docs)

