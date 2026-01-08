"""
Tests for RAG Retriever Module
"""

import tempfile
from pathlib import Path

import pytest

# Skip tests if dependencies not available
pytest.importorskip("sentence_transformers")
pytest.importorskip("faiss")

from codex.rag.indexer import build_index_from_files
from codex.rag.retriever import MultiIndexRetriever, Retriever


class TestRetriever:
    """Tests for Retriever class"""

    @pytest.fixture
    def sample_index(self):
        """Create a sample index for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create sample files
            docs_dir = tmpdir / "docs"
            docs_dir.mkdir()
            
            files = []
            contents = [
                "Python is a high-level programming language. " * 20,
                "Machine learning uses algorithms to learn from data. " * 20,
                "Docker is a containerization platform. " * 20,
            ]
            
            for i, content in enumerate(contents):
                file_path = docs_dir / f"doc{i}.txt"
                with open(file_path, "w") as f:
                    f.write(content)
                files.append(file_path)
            
            # Build index
            index_dir = tmpdir / "indices"
            build_index_from_files(
                files=files,
                index_name="test_docs",
                tenant_id="test",
                index_dir=str(index_dir),
                chunk_size=300,
                overlap=50,
            )
            
            yield {
                "index_dir": str(index_dir),
                "index_name": "test_docs",
                "tenant_id": "test",
            }

    def test_retriever_initialization(self, sample_index):
        """Test retriever initialization"""
        retriever = Retriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
        )
        
        assert retriever is not None
        assert retriever.faiss_index is not None
        assert len(retriever.chunks_metadata) > 0

    def test_retriever_query_basic(self, sample_index):
        """Test basic query functionality"""
        retriever = Retriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
        )
        
        results = retriever.query("Python programming", top_k=3)
        
        assert len(results) > 0
        assert len(results) <= 3
        
        # Check result structure
        for result in results:
            assert "text" in result
            assert "file" in result
            assert "start_line" in result
            assert "end_line" in result
            assert "score" in result
            assert "generated_at" in result
            assert "chunk_id" in result
            assert isinstance(result["score"], float)

    def test_retriever_query_empty(self, sample_index):
        """Test query with empty string"""
        retriever = Retriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
        )
        
        results = retriever.query("", top_k=5)
        assert len(results) == 0
        
        results = retriever.query("   ", top_k=5)
        assert len(results) == 0

    def test_retriever_query_with_min_score(self, sample_index):
        """Test query with minimum score threshold"""
        retriever = Retriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
        )
        
        # Very strict threshold should return fewer results
        results_strict = retriever.query("Python", top_k=10, min_score=0.5)
        results_all = retriever.query("Python", top_k=10)
        
        assert len(results_strict) <= len(results_all)

    def test_retriever_query_top_k_validation(self, sample_index):
        """Test top_k parameter validation"""
        retriever = Retriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
        )
        
        # Should handle invalid top_k gracefully
        results = retriever.query("test", top_k=0)
        assert isinstance(results, list)
        
        results = retriever.query("test", top_k=-1)
        assert isinstance(results, list)

    def test_retriever_get_stats(self, sample_index):
        """Test statistics retrieval"""
        retriever = Retriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
        )
        
        stats = retriever.get_stats()
        
        assert "index_name" in stats
        assert "tenant_id" in stats
        assert "num_vectors" in stats
        assert "num_chunks" in stats
        assert stats["num_vectors"] > 0
        assert stats["num_chunks"] > 0

    def test_retriever_reload(self, sample_index):
        """Test index reloading"""
        retriever = Retriever(
            index_dir=sample_index["index_dir"],
            index_name=sample_index["index_name"],
            tenant_id=sample_index["tenant_id"],
        )
        
        initial_stats = retriever.get_stats()
        retriever.reload()
        reloaded_stats = retriever.get_stats()
        
        assert initial_stats["num_vectors"] == reloaded_stats["num_vectors"]

    def test_retriever_nonexistent_index(self):
        """Test initialization with non-existent index"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Should not raise during init, but warn
            retriever = Retriever(
                index_dir=tmpdir,
                index_name="nonexistent",
                tenant_id="test",
            )
            
            # Should have no index loaded
            assert retriever.faiss_index is None

    def test_retriever_query_without_index(self):
        """Test querying without a loaded index"""
        with tempfile.TemporaryDirectory() as tmpdir:
            retriever = Retriever(
                index_dir=tmpdir,
                index_name="nonexistent",
                tenant_id="test",
            )
            
            results = retriever.query("test query", top_k=5)
            assert len(results) == 0


class TestMultiIndexRetriever:
    """Tests for MultiIndexRetriever class"""

    @pytest.fixture
    def multiple_indices(self):
        """Create multiple indices for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create two separate indices
            indices_info = []
            
            for idx in range(2):
                docs_dir = tmpdir / f"docs_{idx}"
                docs_dir.mkdir()
                
                files = []
                content = f"Index {idx} content. " * 30
                
                file_path = docs_dir / f"doc.txt"
                with open(file_path, "w") as f:
                    f.write(content)
                files.append(file_path)
                
                index_dir = tmpdir / "indices"
                build_index_from_files(
                    files=files,
                    index_name=f"index_{idx}",
                    tenant_id="test",
                    index_dir=str(index_dir),
                    chunk_size=200,
                    overlap=50,
                )
                
                indices_info.append({
                    "index_name": f"index_{idx}",
                    "tenant_id": "test",
                })
            
            yield {
                "index_dir": str(tmpdir / "indices"),
                "indices": indices_info,
            }

    def test_multi_index_initialization(self, multiple_indices):
        """Test multi-index retriever initialization"""
        retriever = MultiIndexRetriever(
            indices=multiple_indices["indices"],
            index_dir=multiple_indices["index_dir"],
        )
        
        assert len(retriever.retrievers) == 2

    def test_multi_index_query(self, multiple_indices):
        """Test querying across multiple indices"""
        retriever = MultiIndexRetriever(
            indices=multiple_indices["indices"],
            index_dir=multiple_indices["index_dir"],
        )
        
        results = retriever.query("content", top_k=5)
        
        assert len(results) > 0
        # Results should have index_name and tenant_id
        for result in results:
            assert "index_name" in result
            assert "tenant_id" in result

    def test_multi_index_query_with_min_score(self, multiple_indices):
        """Test multi-index query with score threshold"""
        retriever = MultiIndexRetriever(
            indices=multiple_indices["indices"],
            index_dir=multiple_indices["index_dir"],
        )
        
        results = retriever.query("content", top_k=10, min_score=1.0)
        
        # All results should have score <= min_score
        for result in results:
            assert result["score"] <= 1.0

    def test_multi_index_get_stats(self, multiple_indices):
        """Test getting stats from multiple indices"""
        retriever = MultiIndexRetriever(
            indices=multiple_indices["indices"],
            index_dir=multiple_indices["index_dir"],
        )
        
        stats = retriever.get_stats()
        
        assert len(stats) == 2
        for stat in stats:
            assert "index_name" in stat
            assert "num_vectors" in stat

    def test_multi_index_with_invalid_index(self, multiple_indices):
        """Test multi-index with some invalid indices"""
        indices = multiple_indices["indices"] + [
            {"index_name": "nonexistent", "tenant_id": "test"}
        ]
        
        retriever = MultiIndexRetriever(
            indices=indices,
            index_dir=multiple_indices["index_dir"],
        )
        
        # Should only load valid indices
        assert len(retriever.retrievers) == 2

    def test_multi_index_empty_list(self):
        """Test multi-index with empty indices list"""
        with tempfile.TemporaryDirectory() as tmpdir:
            retriever = MultiIndexRetriever(
                indices=[],
                index_dir=tmpdir,
            )
            
            assert len(retriever.retrievers) == 0
            
            results = retriever.query("test", top_k=5)
            assert len(results) == 0


class TestRetrieverEdgeCases:
    """Edge case tests for retriever"""

    def test_estimate_line_number(self):
        """Test line number estimation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            retriever = Retriever(
                index_dir=tmpdir,
                index_name="test",
                tenant_id="test",
            )
            
            # Test various positions
            assert retriever._estimate_line_number(0) == 1
            assert retriever._estimate_line_number(-10) == 1
            assert retriever._estimate_line_number(80) == 2
            assert retriever._estimate_line_number(160) == 3

    def test_extract_file_from_metadata(self):
        """Test file extraction from metadata"""
        with tempfile.TemporaryDirectory() as tmpdir:
            retriever = Retriever(
                index_dir=tmpdir,
                index_name="test",
                tenant_id="test",
            )
            
            # Chunk with direct file reference
            chunk1 = {"file": "test.txt"}
            assert retriever._extract_file_from_metadata(chunk1) == "test.txt"
            
            # Chunk without file reference
            chunk2 = {}
            retriever.index_metadata = {}
            assert retriever._extract_file_from_metadata(chunk2) == "unknown"
            
            # With files in index metadata
            retriever.index_metadata = {
                "files": [{"file": "metadata_file.txt"}]
            }
            assert retriever._extract_file_from_metadata(chunk2) == "metadata_file.txt"


class TestRetrieverIntegration:
    """Integration tests for retriever"""

    def test_full_workflow_with_query(self):
        """Test complete workflow from index building to querying"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create diverse content
            docs_dir = tmpdir / "docs"
            docs_dir.mkdir()
            
            files = []
            corpus = {
                "python.txt": "Python is a versatile programming language used for web development, data science, and automation. " * 20,
                "machine_learning.txt": "Machine learning algorithms learn patterns from data to make predictions and decisions without explicit programming. " * 20,
                "docker.txt": "Docker provides containerization for consistent deployment across different environments. " * 20,
            }
            
            for filename, content in corpus.items():
                file_path = docs_dir / filename
                with open(file_path, "w") as f:
                    f.write(content)
                files.append(file_path)
            
            # Build index
            index_dir = tmpdir / "indices"
            build_index_from_files(
                files=files,
                index_name="integration_test",
                tenant_id="test",
                index_dir=str(index_dir),
                chunk_size=400,
                overlap=100,
            )
            
            # Create retriever
            retriever = Retriever(
                index_dir=str(index_dir),
                index_name="integration_test",
                tenant_id="test",
            )
            
            # Test queries for each topic
            python_results = retriever.query("programming language", top_k=3)
            ml_results = retriever.query("data science algorithms", top_k=3)
            docker_results = retriever.query("containerization deployment", top_k=3)
            
            # Should get relevant results
            assert len(python_results) > 0
            assert len(ml_results) > 0
            assert len(docker_results) > 0
            
            # Results should contain the query terms (roughly)
            assert any("Python" in r["text"] or "programming" in r["text"] for r in python_results)
            assert any("learning" in r["text"] or "algorithm" in r["text"] for r in ml_results)
            assert any("Docker" in r["text"] or "container" in r["text"] for r in docker_results)
