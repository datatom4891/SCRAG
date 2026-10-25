import os

from langchain.chat_models import init_chat_model
from langchain_openai.embeddings import OpenAIEmbeddings

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

from agent.config import VectorIndexConfig

class KnowledgeBase:

    def __init__(self, config: VectorIndexConfig):
            self.top_k = config.vector_store.top_k
            self.vector_store = Chroma(persist_directory=config.vector_store.chroma_db_dir,
                                       embedding_function=OpenAIEmbeddings(model=config.embedding.model_name))

    def _retrieved_docs_formatter(self, retrieved_docs):
        formatted_context = []

        if not retrieved_docs:
            return "No relevant documents found"

        for i, doc in enumerate(retrieved_docs):
            source = doc.metadata.get('article_name', 'Unknown')
            formatted_context.append(f"[Article Source {i + 1}: {source}]\n\n {doc.page_content}")
        
        return formatted_context
        #return "\n\n-----------------------------------------------------------\n\n".join(formatted_context)

    def _get_all_kb_articles(self):
        kb = self.vector_store
        raw_articles = kb.get()
        all_articles = []

        for text, metadata in zip(raw_articles["documents"], raw_articles["metadatas"]):
            doc_obj = Document(page_content=text, metadata=metadata)
            all_articles.append(doc_obj)

        return all_articles

    def doc_retriever(self, query):
        retriever = self.vector_store.as_retriever(search_kwargs={"k":self.top_k})
        ALL_KB_ARTICLES = self._get_all_kb_articles()

        bm25_retriever = BM25Retriever.from_documents(ALL_KB_ARTICLES)
        bm25_retriever.k = 5

        semantic_retriever = self.vector_store.as_retriever(search_kwargs={"k":self.top_k})
        hybrid_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, semantic_retriever],
            weights=[0.4, 0.6]
        )

        retrieved_docs = hybrid_retriever.invoke(query)

        return self._retrieved_docs_formatter(retrieved_docs)

