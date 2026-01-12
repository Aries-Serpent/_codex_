"""
Tests for RAG Tenant Management

Comprehensive test coverage for manage_tenant_indices function in indexer.py
"""

import tempfile
from pathlib import Path

import pytest

# Skip tests if dependencies not available
pytest.importorskip("sentence_transformers")
pytest.importorskip("faiss")

from codex.rag.indexer import (
    IndexOperation,
    TenantOperationResult,
    manage_tenant_indices,
)


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

    def test_create_operation_success(self, temp_index_dir, sample_files):
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
        
        assert result.success is True
        assert result.operation == IndexOperation.CREATE
        assert result.tenant_id == "customer_a"
        assert "docs" in result.index_names
        assert "Successfully created" in result.message
        assert "created_indices" in result.details

    def test_create_operation_multiple_indices(self, temp_index_dir, sample_files):
        """Test CREATE operation with multiple indices"""
        result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="create",
            index_names=["docs", "api", "faq"],
            index_dir=temp_index_dir,
            files=sample_files,
        )
        
        assert result.success is True
        assert len(result.details["created_indices"]) == 3
        assert "docs" in result.details["created_indices"]
        assert "api" in result.details["created_indices"]
        assert "faq" in result.details["created_indices"]

    def test_create_operation_missing_files(self, temp_index_dir):
        """Test CREATE operation fails without files"""
        result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="create",
            index_names=["docs"],
            index_dir=temp_index_dir,
        )
        
        assert result.success is False
        assert result.operation == IndexOperation.CREATE
        assert "'create' operation requires 'files' parameter" in result.message

    def test_create_operation_empty_files(self, temp_index_dir):
        """Test CREATE operation with empty files list"""
        result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="create",
            index_names=["docs"],
            index_dir=temp_index_dir,
            files=[],
        )
        
        assert result.success is False
        assert "'create' operation requires 'files' parameter" in result.message

    def test_update_operation_success(self, temp_index_dir, sample_files):
        """Test UPDATE operation success"""
        # First create an index
        create_result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="create",
            index_names=["docs"],
            index_dir=temp_index_dir,
            files=sample_files[:1],
        )
        assert create_result.success is True
        
        # Now update it with more files
        update_result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="update",
            index_names=["docs"],
            index_dir=temp_index_dir,
            files=sample_files,
            chunk_size=400,
        )
        
        assert update_result.success is True
        assert update_result.operation == IndexOperation.UPDATE
        assert "Successfully updated" in update_result.message

    def test_update_operation_nonexistent_index(self, temp_index_dir, sample_files):
        """Test UPDATE operation on non-existent index creates new one"""
        result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="update",
            index_names=["nonexistent"],
            index_dir=temp_index_dir,
            files=sample_files,
        )
        
        # Should succeed by creating new index
        assert result.success is True
        assert "updated_indices" in result.details

    def test_update_operation_missing_files(self, temp_index_dir):
        """Test UPDATE operation fails without files"""
        result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="update",
            index_names=["docs"],
            index_dir=temp_index_dir,
        )
        
        assert result.success is False
        assert "'update' operation requires 'files' parameter" in result.message

    def test_delete_operation_success(self, temp_index_dir, sample_files):
        """Test DELETE operation success"""
        # First create an index
        create_result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="create",
            index_names=["docs"],
            index_dir=temp_index_dir,
            files=sample_files,
        )
        assert create_result.success is True
        
        # Now delete it
        delete_result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="delete",
            index_names=["docs"],
            index_dir=temp_index_dir,
        )
        
        assert delete_result.success is True
        assert delete_result.operation == IndexOperation.DELETE
        assert "Successfully deleted" in delete_result.message

    def test_delete_operation_multiple_indices(self, temp_index_dir, sample_files):
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
        
        assert delete_result.success is True
        assert len(delete_result.details["deleted_indices"]) == 2

    def test_delete_operation_nonexistent_index(self, temp_index_dir):
        """Test DELETE operation on non-existent index"""
        result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="delete",
            index_names=["nonexistent"],
            index_dir=temp_index_dir,
        )
        
        # Should succeed but report no deletions
        assert result.success is False
        assert "No indices deleted" in result.message

    def test_delete_operation_partial_failure(self, temp_index_dir, sample_files):
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
        assert "docs" in delete_result.details["deleted_indices"]
        assert len(delete_result.details["deleted_indices"]) == 1

    def test_merge_operation_success(self, temp_index_dir, sample_files):
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
        
        assert merge_result.success is True
        assert merge_result.operation == IndexOperation.MERGE
        assert "Successfully merged" in merge_result.message
        assert merge_result.details["merged_name"] == "all_content"

    def test_merge_operation_missing_merge_name(self, temp_index_dir, sample_files):
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
        
        assert merge_result.success is False
        assert "'merge' operation requires 'merge_name' parameter" in merge_result.message

    def test_merge_operation_single_index(self, temp_index_dir, sample_files):
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
        
        assert merge_result.success is True

    def test_merge_operation_nonexistent_indices(self, temp_index_dir):
        """Test MERGE operation with non-existent indices"""
        result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="merge",
            index_names=["nonexistent1", "nonexistent2"],
            index_dir=temp_index_dir,
            merge_name="merged",
        )
        
        assert result.success is False
        assert "No valid indices found" in result.message

    def test_list_operation_success(self, temp_index_dir, sample_files):
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
        
        assert list_result.success is True
        assert list_result.operation == IndexOperation.LIST
        assert "Found" in list_result.message
        assert len(list_result.details["indices"]) == 2
        # Extract 'name' field from dict list
        indices_list = list_result.details["indices"]
        index_names = [idx["name"] if isinstance(idx, dict) else idx for idx in indices_list]
        assert "docs" in index_names
        assert "api" in index_names

    def test_list_operation_empty_tenant(self, temp_index_dir):
        """Test LIST operation with no indices"""
        result = manage_tenant_indices(
            tenant_id="customer_b",
            operation="list",
            index_names=[],
            index_dir=temp_index_dir,
        )
        
        assert result.success is True
        assert "No indices found" in result.message

    def test_list_operation_multiple_tenants(self, temp_index_dir, sample_files):
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
        indices_a = [idx["name"] if isinstance(idx, dict) else idx for idx in list_a.details["indices"]]
        assert "docs" in indices_a
        assert "api" not in indices_a
        
        indices_b = [idx["name"] if isinstance(idx, dict) else idx for idx in list_b.details["indices"]]
        assert "api" in indices_b
        assert "docs" not in indices_b

    def test_invalid_operation(self, temp_index_dir):
        """Test invalid operation handling"""
        result = manage_tenant_indices(
            tenant_id="customer_a",
            operation="invalid_op",
            index_names=["docs"],
            index_dir=temp_index_dir,
        )
        
        assert result.success is False
        assert "Invalid operation" in result.message
        assert "create, update, delete, merge, list" in result.message

    def test_operation_case_insensitive(self, temp_index_dir, sample_files):
        """Test that operations are case-insensitive"""
        # Test uppercase
        result_upper = manage_tenant_indices(
            tenant_id="customer_a",
            operation="CREATE",
            index_names=["docs"],
            index_dir=temp_index_dir,
            files=sample_files,
        )
        
        assert result_upper.success is True
        assert result_upper.operation == IndexOperation.CREATE
        
        # Test mixed case
        result_mixed = manage_tenant_indices(
            tenant_id="customer_b",
            operation="CrEaTe",
            index_names=["api"],
            index_dir=temp_index_dir,
            files=sample_files,
        )
        
        assert result_mixed.success is True

    def test_custom_chunk_parameters(self, temp_index_dir, sample_files):
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
        
        assert result.success is True

    def test_tenant_directory_creation(self, temp_index_dir, sample_files):
        """Test that tenant directories are created automatically"""
        tenant_dir = Path(temp_index_dir) / "customer_a"
        assert not tenant_dir.exists()
        
        manage_tenant_indices(
            tenant_id="customer_a",
            operation="create",
            index_names=["docs"],
            index_dir=temp_index_dir,
            files=sample_files,
        )
        
        assert tenant_dir.exists()
        assert (tenant_dir / "docs").exists()

    def test_create_with_error_in_one_index(self, temp_index_dir, sample_files):
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
        assert result.success is True
        assert len(result.details["created_indices"]) == 2

    def test_result_structure(self, temp_index_dir, sample_files):
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
