from dataclasses import dataclass, field
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv(override=True)

@dataclass
class EmbeddingConfig:
    provider: str = "openai"
    model_name: str = "text-embedding-3-small"
    batch_size: int = 64

@dataclass
class VectorStoreConfig:
    md_articles_dir: str  = os.path.join(os.getcwd(),'articles')
    chroma_db_dir: str = os.path.join(os.getcwd(),'chroma_db')
    collection_name: str = "green_lantern_lore"
    top_k: int = 3

@dataclass
class MDSplitterConfig:
    md_doc_split_pattern: List[tuple] = field(
        default_factory=lambda: [
            ("# ", "Header 1"),
            ("## ", "Header 2"),
            ("### ", "Header 3"),
            ("#### ", "Header 4"),
            ("##### ", "Header 5"),
            ("###### ", "Header 6"),
        ]
    )

@dataclass
class TextSplitterConfig:
    chunk_size: int = 500
    chunk_overlap: int = 50

@dataclass
class LLMConfig:
    model_name: str = "gpt-4o-mini"
    temperature: float = 0
    max_tokens: int = 1024
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))

@dataclass
class VectorStoreBuilderConfig:
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    vector_store: VectorStoreConfig = field(default_factory=VectorStoreConfig)
    text_splitter: TextSplitterConfig = field(default_factory=TextSplitterConfig)
    md_splitter: MDSplitterConfig = field(default_factory=MDSplitterConfig)

@dataclass
class VectorIndexConfig:
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    vector_store: VectorStoreConfig = field(default_factory=VectorStoreConfig)

@dataclass
class TavilyToolConfig:
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("TAVILY_API_KEY"))
    max_results=3
    topic = "general"

@dataclass
class RAGAgentConfig:
    vector_index_config:VectorIndexConfig = field(default_factory=VectorIndexConfig)
    llm_config: LLMConfig = field(default_factory=LLMConfig)
    tavily_config:TavilyToolConfig = field(default_factory=TavilyToolConfig)



