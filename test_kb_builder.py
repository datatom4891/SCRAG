from unittest.mock import MagicMock, patch

from kb_builder import KnowledgeBaseBuilder


def test_knowledge_base_builder_chunks_markdown_and_builds_vector_store(tmp_path):
    articles_dir = tmp_path / "articles"
    articles_dir.mkdir()
    article_path = articles_dir / "sample.md"
    article_path.write_text(
        "# Title\n\nThis is a paragraph.\n\n## Details\n\nMore content.",
        encoding="utf-8",
    )

    fake_embedding = object()
    fake_store = MagicMock()

    with patch("kb_builder.OpenAIEmbeddings", return_value=fake_embedding) as mock_embeddings, patch(
        "kb_builder.Chroma.from_documents", return_value=fake_store
    ) as mock_from_documents:
        builder = KnowledgeBaseBuilder(
            md_doc_dir=str(articles_dir),
            chroma_dir=str(tmp_path / "chroma"),
        )

    assert builder.embedding_model is fake_embedding
    assert mock_embeddings.call_args.kwargs["model"] == "text-embedding-3-small"
    assert len(builder.chunked_documents) >= 1
    assert all(doc.metadata["article_name"] == "sample" for doc in builder.chunked_documents)
    assert builder.vector_store is fake_store
    mock_from_documents.assert_called_once()

    _, kwargs = mock_from_documents.call_args
    assert kwargs["documents"] == builder.chunked_documents
    assert kwargs["embedding"] is fake_embedding
    assert kwargs["persist_directory"] == str(tmp_path / "chroma")
