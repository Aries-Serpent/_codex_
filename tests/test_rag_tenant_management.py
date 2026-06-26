"""
Tests for RAG Tenant Management

Comprehensive test coverage for manage_tenant_indices function in indexer.py
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

np = pytest.importorskip("numpy")

# Conditional imports for RAG dependencies - safely handled at test runtime
try:
    from codex.rag.indexer import (
        IndexOperation,
        manage_tenant_indices,
    )

    RAG_TENANT_AVAILABLE = True
except (ImportError, ValueError):
    # ValueError is raised by importlib.util.find_spec() in Python 3.12 when
    # a package (e.g. sentence_transformers) is present in sys.modules but has
    # __spec__ = None, which happens with some installed-but-broken distributions.
    RAG_TENANT_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not RAG_TENANT_AVAILABLE, reason="RAG dependencies (sentence_transformers, faiss) not installed"
)


@pytest.fixture(autouse=True)
def mock_rag_dependencies(monkeypatch):
    """Inject fully mocked optional RAG dependencies into sys.modules.

    Q002 canonical fix (deep research 2026-02-23):
    - Both faiss and sentence_transformers are optional; CI runners without
      these packages cause manage_tenant_indices to silently return success=False.
    - Injecting into sys.modules guarantees every `import faiss` /
      `import sentence_transformers` inside any function (including embed_chunks,
      persist_index, safe_load_sentence_transformer) receives the mock, regardless
      of execution order or pytest-xdist worker state.
    - Module-level `faiss` variable in indexer.py is already None at collection
      time; we must also patch the attribute on the imported module object.
    """
    # --- Mock FAISS ---
    mock_faiss = MagicMock()
    mock_index = MagicMock()
    mock_index.ntotal = 100
    mock_index.d = 384
    mock_faiss.IndexFlatL2.return_value = mock_index
    # write_index / read_index must be no-ops that don't touch the filesystem
    mock_faiss.write_index.return_value = None
    mock_faiss.read_index.return_value = mock_index
    monkeypatch.setitem(sys.modules, "faiss", mock_faiss)

    # Patch the module-level `faiss` variable in indexer (already None after
    # the module was imported without faiss installed).
    try:
        import codex.rag.indexer as _indexer

        monkeypatch.setattr(_indexer, "faiss", mock_faiss)
    except ImportError:
        _ = None  # codex.rag.indexer not installed; faiss patched via sys.modules only

    # --- Mock sentence_transformers ---
    mock_st_module = MagicMock()
    mock_model_instance = MagicMock()

    # encode() must return a numpy array of shape [N, 384]
    def _mock_encode(texts, **kwargs):
        if isinstance(texts, str):
            texts = [texts]
        return np.zeros((len(texts), 384), dtype=np.float32)

    mock_model_instance.encode.side_effect = _mock_encode
    mock_model_instance.get_sentence_embedding_dimension.return_value = 384
    mock_st_module.SentenceTransformer.return_value = mock_model_instance
    monkeypatch.setitem(sys.modules, "sentence_transformers", mock_st_module)

    # Also patch safe_load_sentence_transformer to return the mock model
    # directly, bypassing any device/meta-tensor logic.
    try:
        import codex.rag._model_utils as _mu

        monkeypatch.setattr(
            _mu, "safe_load_sentence_transformer", lambda *a, **kw: mock_model_instance
        )
    except ImportError:
        _ = None  # codex.rag._model_utils not installed; sentence_transformers patched via sys.modules only

    # Also patch persist_index and load_index to bypass all filesystem side-effects.
    # write_index mock leaves no file → Path.stat() in persist_index raises
    # FileNotFoundError; load_index checks index.faiss existence before calling
    # faiss.read_index.  Both are patched to use in-memory stubs.
    try:
        import codex.rag.indexer as _indexer

        def _mock_persist_index(
            embeddings,
            chunks,
            index_name,
            tenant_id="default",
            index_dir=".codex/tenants",
            metadata=None,
        ):
            """Create stub directory + sentinel files so list/load can detect index."""
            tenant_dir = Path(index_dir) / tenant_id / index_name
            tenant_dir.mkdir(parents=True, exist_ok=True)
            # Create sentinel files that load_index and list operations check for
            (tenant_dir / "index.faiss").touch()
            (tenant_dir / "chunks.json").write_text("[]")
            (tenant_dir / "metadata.json").write_text(
                '{"index_name": "'
                + index_name
                + '", "tenant_id": "'
                + tenant_id
                + '", "dimension": 384, "num_vectors": 1, "index_type": "IndexFlatL2"}'
            )
            return tenant_dir

        def _mock_load_index(index_name, tenant_id="default", index_dir=".codex/tenants"):
            """Return mock index only if stub sentinel exists (created by _mock_persist_index).
            Raises for truly nonexistent indices so error-path tests work correctly."""
            sentinel = Path(index_dir) / tenant_id / index_name / "index.faiss"
            if not sentinel.exists():
                raise FileNotFoundError(f"FAISS index file not found: {sentinel}")
            mock_idx = MagicMock()
            mock_idx.ntotal = 1
            mock_idx.d = 384
            # reconstruct(i) must return a numpy vector of shape (384,) so that
            # the merge loop `embeddings[i] = index.reconstruct(i)` succeeds
            mock_idx.reconstruct.return_value = np.zeros(384, dtype=np.float32)
            meta = {"index_name": index_name, "tenant_id": tenant_id, "dimension": 384}
            return mock_idx, [], meta

        monkeypatch.setattr(_indexer, "persist_index", _mock_persist_index)
        monkeypatch.setattr(_indexer, "load_index", _mock_load_index)
    except ImportError:
        _ = None  # codex.rag.indexer not installed; persist/load patched only if module present

    yield


class TestManageTenantIndices:
    """Tests for manage_tenant_indices function"""

    @pytest.fixture
    def temp_index_dir(self):
        """Create temporary index directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def sample_files(self):
        """Create sample files for indexing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            files = []

            contents = [
                "Python is a high-level programming language. " * 20,
                "Machine learning uses algorithms to learn from data. " * 20,
                "Docker is a containerization platform. " * 20,
            ]

            for i, content in enumerate(contents):
                file_path = tmpdir / f"doc{i}.txt"
                with open(file_path, "w") as f:
                    f.write(content)
                files.append(file_path)

            yield files

    def test_create_operation_success(
        self, temp_index_dir, sample_files, mock_sentence_transformer
    ):
        """Test CREATE operation success"""
        result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="create",
            index_names=["docs"],
            index_dir=temp_index_dir,
            files=sample_files,
            chunk_size=300,
            overlap=50,
        )

        assert result.success is True, "Result must not be empty"
        assert result.operation == IndexOperation.CREATE, "Result must not be empty"
        assert result.tenant_id == "customer_a", "Result must not be empty"
        assert "docs" in result.index_names, "Result must not be empty"
        assert "Successfully created" in result.message, "Result must not be empty"
        assert "created_indices" in result.details, "Result must not be empty"

    def test_create_operation_multiple_indices(
        self, temp_index_dir, sample_files, mock_sentence_transformer
    ):
        """Test CREATE operation with multiple indices"""
        result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="create",
            index_names=["docs", "api", "faq"],
            index_dir=temp_index_dir,
            files=sample_files,
        )

        assert result.success is True, "Result must not be empty"
        assert len(result.details["created_indices"]) == 3, "Collection must not be empty"
        assert "docs" in result.details["created_indices"], "Result must not be empty"
        assert "api" in result.details["created_indices"], "Result must not be empty"
        assert "faq" in result.details["created_indices"], "Result must not be empty"

    def test_create_operation_missing_files(self, temp_index_dir):
        """Test CREATE operation fails without files"""
        result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="create",
            index_names=["docs"],
            index_dir=temp_index_dir,
        )

        assert result.success is False, "Result must not be empty"
        assert result.operation == IndexOperation.CREATE, "Result must not be empty"
        assert "'create' operation requires 'files' parameter" in result.message, "Result must not be empty"

    def test_create_operation_empty_files(self, temp_index_dir):
        """Test CREATE operation with empty files list"""
        result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="create",
            index_names=["docs"],
            index_dir=temp_index_dir,
            files=[],
        )

        assert result.success is False, "Result must not be empty"
        assert "'create' operation requires 'files' parameter" in result.message, "Result must not be empty"

    def test_update_operation_success(
        self, temp_index_dir, sample_files, mock_sentence_transformer
    ):
        """Test UPDATE operation success"""
        # First create an index
        create_result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="create",
            index_names=["docs"],
            index_dir=temp_index_dir,
            files=sample_files[:1],
        )
        assert create_result.success is True, "Result must not be empty"

        # Now update it with more files
        update_result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="update",
            index_names=["docs"],
            index_dir=temp_index_dir,
            files=sample_files,
            chunk_size=400,
        )

        assert update_result.success is True, "Result must not be empty"
        assert update_result.operation == IndexOperation.UPDATE, "Result must not be empty"
        assert "Successfully updated" in update_result.message, "Result must not be empty"

    def test_update_operation_nonexistent_index(
        self, temp_index_dir, sample_files, mock_sentence_transformer
    ):
        """Test UPDATE operation on non-existent index creates new one"""
        result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="update",
            index_names=["nonexistent"],
            index_dir=temp_index_dir,
            files=sample_files,
        )

        # Should succeed by creating new index
        assert result.success is True, "Result must not be empty"
        assert "updated_indices" in result.details, "Result must not be empty"

    def test_update_operation_missing_files(self, temp_index_dir):
        """Test UPDATE operation fails without files"""
        result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="update",
            index_names=["docs"],
            index_dir=temp_index_dir,
        )

        assert result.success is False, "Result must not be empty"
        assert "'update' operation requires 'files' parameter" in result.message, "Result must not be empty"

    def test_delete_operation_success(
        self, temp_index_dir, sample_files, mock_sentence_transformer
    ):
        """Test DELETE operation success"""
        # First create an index
        create_result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="create",
            index_names=["docs"],
            index_dir=temp_index_dir,
            files=sample_files,
        )
        assert create_result.success is True, "Result must not be empty"

        # Now delete it
        delete_result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="delete",
            index_names=["docs"],
            index_dir=temp_index_dir,
        )

        assert delete_result.success is True, "Result must not be empty"
        assert delete_result.operation == IndexOperation.DELETE, "Result must not be empty"
        assert "Successfully deleted" in delete_result.message, "Result must not be empty"

    def test_delete_operation_multiple_indices(
        self, temp_index_dir, sample_files, mock_sentence_transformer
    ):
        """Test DELETE operation with multiple indices"""
        # Create multiple indices
        manage_tenant_indices(
            tenant_id="customer_a",
            operation="create",
            index_names=["docs", "api"],
            index_dir=temp_index_dir,
            files=sample_files,
        )

        # Delete both
        delete_result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="delete",
            index_names=["docs", "api"],
            index_dir=temp_index_dir,
        )

        assert delete_result.success is True, "Result must not be empty"
        assert len(delete_result.details["deleted_indices"]) == 2, "Collection must not be empty"

    def test_delete_operation_nonexistent_index(self, temp_index_dir):
        """Test DELETE operation on non-existent index"""
        result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="delete",
            index_names=["nonexistent"],
            index_dir=temp_index_dir,
        )

        # Should succeed but report no deletions
        assert result.success is False, "Result must not be empty"
        assert "No indices deleted" in result.message, "Result must not be empty"

    def test_delete_operation_partial_failure(
        self, temp_index_dir, sample_files, mock_sentence_transformer
    ):
        """Test DELETE operation with some indices existing, some not"""
        # Create one index
        manage_tenant_indices(
            tenant_id="customer_a",
            operation="create",
            index_names=["docs"],
            index_dir=temp_index_dir,
            files=sample_files,
        )

        # Try to delete existing and non-existing
        delete_result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="delete",
            index_names=["docs", "nonexistent"],
            index_dir=temp_index_dir,
        )

        # Should partially succeed
        assert "docs" in delete_result.details["deleted_indices"], "Result must not be empty"
        assert len(delete_result.details["deleted_indices"]) == 1, "Collection must not be empty"

    def test_merge_operation_success(self, temp_index_dir, sample_files, mock_sentence_transformer):
        """Test MERGE operation success"""
        # Create multiple indices
        for idx_name in ["docs", "api", "faq"]:
            manage_tenant_indices(
                tenant_id="customer_a",
                operation="create",
                index_names=[idx_name],
                index_dir=temp_index_dir,
                files=sample_files,
            )

        # Merge them
        merge_result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="merge",
            index_names=["docs", "api", "faq"],
            index_dir=temp_index_dir,
            merge_name="all_content",
        )

        assert merge_result.success is True, "Result must not be empty"
        assert merge_result.operation == IndexOperation.MERGE, "Result must not be empty"
        assert "Successfully merged" in merge_result.message, "Result must not be empty"
        assert merge_result.details["merged_name"] == "all_content", "Result must not be empty"

    def test_merge_operation_missing_merge_name(
        self, temp_index_dir, sample_files, mock_sentence_transformer
    ):
        """Test MERGE operation fails without merge_name"""
        # Create indices
        manage_tenant_indices(
            tenant_id="customer_a",
            operation="create",
            index_names=["docs", "api"],
            index_dir=temp_index_dir,
            files=sample_files,
        )

        # Try to merge without merge_name
        merge_result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="merge",
            index_names=["docs", "api"],
            index_dir=temp_index_dir,
        )

        assert merge_result.success is False, "Result must not be empty"
        assert "'merge' operation requires 'merge_name' parameter" in merge_result.message, "Result must not be empty"

    def test_merge_operation_single_index(
        self, temp_index_dir, sample_files, mock_sentence_transformer
    ):
        """Test MERGE operation with only one index"""
        # Create one index
        manage_tenant_indices(
            tenant_id="customer_a",
            operation="create",
            index_names=["docs"],
            index_dir=temp_index_dir,
            files=sample_files,
        )

        # Try to merge (should still work)
        merge_result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="merge",
            index_names=["docs"],
            index_dir=temp_index_dir,
            merge_name="merged",
        )

        assert merge_result.success is True, "Result must not be empty"

    def test_merge_operation_nonexistent_indices(self, temp_index_dir):
        """Test MERGE operation with non-existent indices"""
        result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="merge",
            index_names=["nonexistent1", "nonexistent2"],
            index_dir=temp_index_dir,
            merge_name="merged",
        )

        assert result.success is False, "Result must not be empty"
        assert "No valid indices found" in result.message, "Result must not be empty"

    def test_list_operation_success(self, temp_index_dir, sample_files, mock_sentence_transformer):
        """Test LIST operation success"""
        # Create some indices
        manage_tenant_indices(
            tenant_id="customer_a",
            operation="create",
            index_names=["docs", "api"],
            index_dir=temp_index_dir,
            files=sample_files,
        )

        # List them
        list_result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="list",
            index_names=[],
            index_dir=temp_index_dir,
        )

        assert list_result.success is True, "Result must not be empty"
        assert list_result.operation == IndexOperation.LIST, "Result must not be empty"
        assert "Found" in list_result.message, "Result must not be empty"
        assert len(list_result.details["indices"]) == 2, "Collection must not be empty"
        # Extract 'name' field from dict list
        indices_list = list_result.details["indices"]
        index_names = [idx["name"] if isinstance(idx, dict) else idx for idx in indices_list]
        assert "docs" in index_names, "Condition must be true"
        assert "api" in index_names, "Condition must be true"

    def test_list_operation_empty_tenant(self, temp_index_dir):
        """Test LIST operation with no indices"""
        result = manage_tenant_indices(
            tenant_id="customer_b",
            operation="list",
            index_names=[],
            index_dir=temp_index_dir,
        )

        assert result.success is True, "Result must not be empty"
        assert "No indices found" in result.message, "Result must not be empty"

    def test_list_operation_multiple_tenants(
        self, temp_index_dir, sample_files, mock_sentence_transformer
    ):
        """Test LIST operation with multiple tenants"""
        # Create indices for different tenants
        manage_tenant_indices(
            tenant_id="customer_a",
            operation="create",
            index_names=["docs"],
            index_dir=temp_index_dir,
            files=sample_files,
        )

        manage_tenant_indices(
            tenant_id="customer_b",
            operation="create",
            index_names=["api"],
            index_dir=temp_index_dir,
            files=sample_files,
        )

        # List for customer_a
        list_a = manage_tenant_indices(
            tenant_id="customer_a",
            operation="list",
            index_names=[],
            index_dir=temp_index_dir,
        )

        # List for customer_b
        list_b = manage_tenant_indices(
            tenant_id="customer_b",
            operation="list",
            index_names=[],
            index_dir=temp_index_dir,
        )

        # Extract 'name' field from dict lists
        indices_a = [
            idx["name"] if isinstance(idx, dict) else idx for idx in list_a.details["indices"]
        ]
        assert "docs" in indices_a, "Condition must be true"
        assert "api" not in indices_a, "Condition must be true"

        indices_b = [
            idx["name"] if isinstance(idx, dict) else idx for idx in list_b.details["indices"]
        ]
        assert "api" in indices_b, "Condition must be true"
        assert "docs" not in indices_b, "Condition must be true"

    def test_invalid_operation(self, temp_index_dir):
        """Test invalid operation handling"""
        result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="invalid_op",
            index_names=["docs"],
            index_dir=temp_index_dir,
        )

        assert result.success is False, "Result must not be empty"
        assert "Invalid operation" in result.message, "Result must not be empty"
        assert "create, update, delete, merge, list" in result.message

    def test_operation_case_insensitive(
        self, temp_index_dir, sample_files, mock_sentence_transformer
    ):
        """Test that operations are case-insensitive"""
        # Test uppercase
        result_upper = manage_tenant_indices(
            tenant_id="customer_a",
            operation="CREATE",
            index_names=["docs"],
            index_dir=temp_index_dir,
            files=sample_files,
        )

        assert result_upper.success is True, "Result must not be empty"
        assert result_upper.operation == IndexOperation.CREATE, "Result must not be empty"

        # Test mixed case
        result_mixed = manage_tenant_indices(
            tenant_id="customer_b",
            operation="CrEaTe",
            index_names=["api"],
            index_dir=temp_index_dir,
            files=sample_files,
        )

        assert result_mixed.success is True, "Result must not be empty"

    def test_custom_chunk_parameters(self, temp_index_dir, sample_files, mock_sentence_transformer):
        """Test CREATE with custom chunk_size and overlap"""
        result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="create",
            index_names=["docs"],
            index_dir=temp_index_dir,
            files=sample_files,
            chunk_size=500,
            overlap=100,
        )

        assert result.success is True, "Result must not be empty"

    def test_tenant_directory_creation(
        self, temp_index_dir, sample_files, mock_sentence_transformer
    ):
        """Test that tenant directories are created automatically"""
        tenant_dir = Path(temp_index_dir) / "customer_a"
        assert not tenant_dir.exists(), "Condition must be true"

        manage_tenant_indices(
            tenant_id="customer_a",
            operation="create",
            index_names=["docs"],
            index_dir=temp_index_dir,
            files=sample_files,
        )

        assert tenant_dir.exists(), "Condition must be true"
        assert (tenant_dir / "docs").exists(), "Condition must be true"

    def test_create_with_error_in_one_index(
        self, temp_index_dir, sample_files, mock_sentence_transformer
    ):
        """Test CREATE where one index succeeds and another might fail"""
        # This test ensures partial success is handled correctly
        result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="create",
            index_names=["docs", "api"],
            index_dir=temp_index_dir,
            files=sample_files,
        )

        # Both should succeed with valid files
        assert result.success is True, "Result must not be empty"
        assert len(result.details["created_indices"]) == 2, "Collection must not be empty"

    def test_result_structure(self, temp_index_dir, sample_files, mock_sentence_transformer):
        """Test that TenantOperationResult has correct structure"""
        result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="create",
            index_names=["docs"],
            index_dir=temp_index_dir,
            files=sample_files,
        )

        assert hasattr(result, "success")
        assert hasattr(result, "operation")
        assert hasattr(result, "tenant_id")
        assert hasattr(result, "index_names")
        assert hasattr(result, "message")
        assert hasattr(result, "details")

        assert isinstance(result.success, bool)
        assert isinstance(result.operation, IndexOperation)
        assert isinstance(result.tenant_id, str)
        assert isinstance(result.index_names, list)
        assert isinstance(result.message, str)
        assert result.details is None or isinstance(result.details, dict)
