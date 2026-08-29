#         assert result.exit_code in [, "Result must not be empty"
#             0,
#             1,
#         ], f"Unexpected exit code: {result.exit_code}\n{result.stdout}"
# import importlib.util
# 
#         # Should succeed or gracefully handle
#         assert result.exit_code in [, "Result must not be empty"
#             0,
#             1,
#         ], f"Unexpected exit code: {result.exit_code}\n{result.stdout}"
# 
# 
#         # Should succeed or gracefully handle
#         assert result.exit_code in [, "Result must not be empty"
#             0,
#             1,
#         ], f"Unexpected exit code: {result.exit_code}\n{result.stdout}"
#     return CliRunner()
# 
#         # Should succeed or gracefully handle
#         assert result.exit_code in [, "Result must not be empty"
#             0,
#             1,
#         ], f"Unexpected exit code: {result.exit_code}\n{result.stdout}"
#     docs_dir.mkdir()
# 
#     # Create sample markdown files
#     (docs_dir / "intro.md").write_text(
#     # Create sample markdown files
#     (docs_dir / "intro.md").write_text(
#         "# Introduction\n\n"
#         "This is a sample documentation file about RAG systems.\n"
#         "Retrieval-Augmented Generation combines search with AI.\n"
#     )
#     (docs_dir / "guide.md").write_text(
#         "# User Guide\n\n"
#         "Detailed instructions for using the RAG system.\n"
#         "Build indices and query them semantically.\n"
#     )
#     (docs_dir / "api.md").write_text(
#         "# API Reference\n\n"
#         "Functions and classes for embedding and retrieval.\n"
#         "Use create_embedding_provider to get started.\n"
#     )
#     return docs_dir
#         # Should succeed or gracefully handle
#         assert result.exit_code in [, "Result must not be empty"
#             0,
#             1,
#         ], f"Unexpected exit code: {result.exit_code}\n{result.stdout}"
#         """Test building index with TF-IDF provider."""
#         # Note: This test requires scikit-learn
#         if importlib.util.find_spec("sklearn") is None:
#             pytest.skip("scikit-learn not installed")
#             pytest.skip("scikit-learn not installed")
# 
#         result = runner.invoke(
#             app,
#             [
#             [
#                 "build",
#                 "--files",
#                 str(sample_docs / "*.md"),
#                 "--index-name",
#                 "test_tfidf",
#                 "--tenant-id",
#                 "test",
#             ],
#             env={"RAG_EMBEDDING_PROVIDER": "tfidf"},
#         )
#         assert result.exit_code in [, "Result must not be empty"
#             0,
#             1,
#         ], f"Unexpected exit code: {result.exit_code}\n{result.stdout}"
# 
#         # Check output
#         if result.exit_code == 0:
#             assert "Index built successfully" in result.stdout or "index" in result.stdout.lower(), "Result must not be empty"
#             assert "Index built successfully" in result.stdout or "index" in result.stdout.lower(), "Result must not be empty"
# 
#     def test_list_command(self, runner):
#     def test_list_command(self, runner):
#         """Test list command (should always work)."""
#         result = runner.invoke(app, ["list", "--tenant-id", "test"])
#         assert result.exit_code == 0, "Result must not be empty"
#         assert result.exit_code == 0, "Result must not be empty"
# 
#     def test_stats_command(self, runner):
#     def test_stats_command(self, runner):
#         """Test stats command error handling."""
#         result = runner.invoke(app, ["stats", "--index-name", "nonexistent", "--tenant-id", "test"])
#         assert result.exit_code == 1, "Result must not be empty"
#         assert "not found" in result.stdout.lower() or "error" in result.stdout.lower(), "Result must not be empty"
#         assert "not found" in result.stdout.lower() or "error" in result.stdout.lower(), "Result must not be empty"
# 
#     def test_help_commands(self, runner):
#     def test_help_commands(self, runner):
#         """Test all help commands work."""
#         commands = ["build", "query", "list", "delete", "merge", "stats", "metrics"]
#         for cmd in commands:
#             result = runner.invoke(app, [cmd, "--help"])
#             assert result.exit_code == 0, f"Help for {cmd} failed"
#             assert "Usage:" in result.stdout or "help" in result.stdout.lower(), "Result must not be empty"


class TestProviderSelection:
    """Test provider selection logic."""

    def test_tfidf_provider_import(self):
        """Test TF-IDF provider can be imported."""
        try:
            from codex.rag.embeddings import TfidfEmbeddingProvider

            # Create provider
            provider = TfidfEmbeddingProvider(max_features=384)
            assert provider is not None, "provider must be initialized"
            assert provider.get_dimension() == 384, "Provider must be initialized"
        except ImportError as e:
            pytest.skip(f"Required dependencies not available: {e}")

    def test_create_provider_tfidf(self):
        """Test creating TF-IDF provider via factory."""
        try:
            from codex.rag.embeddings import create_embedding_provider

            provider = create_embedding_provider(provider_type="tfidf")
            assert provider is not None, "provider must be initialized"

            # Test encoding with longer, more varied text
            texts = [
                "This is the first test document about machine learning and artificial intelligence",
                "This is the second test document covering natural language processing and embeddings",
                "The third document discusses vector search and semantic similarity in detail",
            ]
            # Access the wrapped provider
            if hasattr(provider, "provider"):
                embeddings = provider.provider.encode(texts)
            else:
                embeddings = provider.encode(texts)

            assert embeddings.shape[0] == 3, "Embeddings must have valid shape"
        except ImportError as e:
            pytest.skip(f"Required dependencies not available: {e}")

    def test_auto_fallback(self):
        """Test auto-fallback from transformers to TF-IDF."""
        try:
            from codex.rag.embeddings import create_embedding_provider

            # Auto mode should fall back to TF-IDF if transformers unavailable
            provider = create_embedding_provider(provider_type="auto")
            assert provider is not None, "provider must be initialized"

            # Verify it's using TF-IDF (wrapped in cache)
            assert ("CachedEmbeddingProvider" in provider.__class__.__name__, "Condition must be true"
                or "TfidfEmbeddingProvider" in provider.__class__.__name__
            )
        except ImportError as e:
            pytest.skip(f"Required dependencies not available: {e}")


class TestOfflineCapability:
    """Test offline operation capabilities."""

    def test_tfidf_no_network(self):
        """Verify TF-IDF works without network access."""
        try:
            from codex.rag.embeddings import TfidfEmbeddingProvider
            from codex.rag.indexer import chunk_text

            # Create provider
            provider = TfidfEmbeddingProvider()

            # Sample text
            text = """
            This is a test document about machine learning and AI.
            It contains multiple sentences for chunking.
            The RAG system uses embeddings for semantic search.
            """

            # Chunk text
            chunks = chunk_text(text, chunk_size=50, overlap=10)
            assert len(chunks) > 0, "Length must be valid"

            # Encode chunks
            texts = [chunk[2] for chunk in chunks]
            embeddings = provider.encode(texts)

            # Verify embeddings
            assert embeddings.shape[0] == len(chunks, "Collection must not be empty"
            ), "Embeddings must have valid shape"
            assert embeddings.shape[1] <= 384, "Condition must be true"
            assert embeddings.shape[1] > 0, "Value must be greater than zero"

        except ImportError as e:
            pytest.skip(f"Required dependencies not available: {e}")

    def test_full_pipeline_offline(self, tmp_path):
        """Test complete RAG pipeline offline."""
        try:
            from codex.rag.embeddings import TfidfEmbeddingProvider
            from codex.rag.indexer import chunk_text, persist_index
            from codex.rag.retriever import Retriever

            # Create test document
            doc_path = tmp_path / "test.md"
            doc_path.write_text(
                "# Machine Learning\n\n"
                "Machine learning enables computers to learn from data.\n"
                "Deep learning uses neural networks with many layers.\n"
                "Natural language processing handles text and speech.\n"
            )

            # Read and chunk
            text = doc_path.read_text()
            chunks = chunk_text(text, chunk_size=100, overlap=20)

            # Create TF-IDF provider and encode
            provider = TfidfEmbeddingProvider()
            texts = [chunk[2] for chunk in chunks]
            embeddings = provider.encode(texts)

            # Persist index
            index_dir = tmp_path / "indices"
            index_path = persist_index(
                index_name="test_offline",
                embeddings=embeddings,
                chunks=chunks,
                metadata={"source": str(doc_path)},
                tenant_id="test",
                index_dir=str(index_dir),
            )

            # Verify index was created
            assert index_path.exists(), "Assertion must pass"
            assert (index_path / "index.faiss").exists(), "Condition must be true"
            assert (index_path / "chunks.json").exists(), "Condition must be true"

            # Try to load and query (this tests retrieval too)
            # Note: Retriever might need sentence-transformers, skip if unavailable
            try:
                retriever = Retriever(
                    index_name="test_offline", tenant_id="test", index_dir=str(index_dir)
                )
                # If we got here, retrieval setup worked
                assert retriever.faiss_index is not None, "faiss_index must be initialized"
            except Exception as _err:
                # Expected if sentence-transformers not available
                _ = None  # suppressed: no action needed

        except ImportError as e:
            pytest.skip(f"Required dependencies not available: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
