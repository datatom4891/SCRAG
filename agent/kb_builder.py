import os
import shutil
import logging


from pathlib import Path
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import  MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from agent.config import VectorStoreBuilderConfig, EmbeddingConfig, VectorStoreConfig, TextSplitterConfig, MDSplitterConfig



class KnowledgeBaseBuilder:

    def __init__(self, config: VectorStoreBuilderConfig):
        self.config = config
        self.embedding_config = self.config.embedding
        self.vs_config = self.config.vector_store
        self.ts_config = self.config.text_splitter
        self.mds_config = self.config.md_splitter
        
        self.embedding_model = OpenAIEmbeddings(model=self.embedding_config.model_name)
        
        self.md_doc_dir = self.vs_config.md_articles_dir
        self.chroma_dir = self.vs_config.chroma_db_dir
        
        self.md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=self.mds_config.md_doc_split_pattern)
        
        self.recursive_splitter = RecursiveCharacterTextSplitter(chunk_size=self.ts_config.chunk_size, chunk_overlap=self.ts_config.chunk_overlap)
        
        self.chunked_documents = self._chunk_documents()
        self.vector_store = self._build_vector_store()

    def _chunk_documents(self):
        article_chunks =[]
        md_articles = list(Path(self.md_doc_dir).glob('**/*.md'))

        for md_article in md_articles:
            article_name = md_article.stem
            with open(md_article, 'r', encoding='utf-8') as f:
                article_content = f.read()

            md_header_chunks = self.md_splitter.split_text(article_content)
            for chunk in md_header_chunks:
                chunk.metadata["article_name"] = article_name

            sub_chunks_of_chunk = self.recursive_splitter.split_documents(md_header_chunks)
            article_chunks.extend(sub_chunks_of_chunk)

        return article_chunks

    def _build_vector_store(self):
        vector_store = Chroma.from_documents(documents=self.chunked_documents,
                                             embedding=self.embedding_model,
                                             persist_directory=self.chroma_dir)
        return vector_store

    def get_kb_vector_store(self):
        return self.vector_store