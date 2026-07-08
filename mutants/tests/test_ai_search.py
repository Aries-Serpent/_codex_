"""Tests for AI-optimized repository search system."""

import sys
from pathlib import Path

import pytest

# Add scripts to path for importing
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ai_search import AIRepositorySearch
from generate_ai_index import CodeEntity, RepositoryIndexer


@pytest.fixture
def temp_repo(tmp_path):
    """Create a temporary repository for testing."""
    # Create directory structure
    src_dir = tmp_path / "src" / "package"
    src_dir.mkdir(parents=True)

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()

    # Create sample Python file
    sample_code = '''"""Sample module for testing."""

class TestClass:
    """A test class."""

    def method_one(self, arg1):
        """First method."""
        pass

    def method_two(self, arg2):
        """Second method."""
        pass

def test_function():
    """A test function."""
    return True

CONSTANT_VALUE = 42
'''

    (src_dir / "module.py").write_text(sample_code)
    (tests_dir / "test_module.py").write_text(sample_code)

    # Create config file
    (tmp_path / "config.yaml").write_text("key: value\n")

    return tmp_path


def test_code_entity_creation():
    """Test CodeEntity dataclass creation."""
    entity = CodeEntity(
        type="function", name="test_func", path="test.py", line_start=10, line_end=20
    )

    assert entity.type == "function", "type is not valid"
    assert entity.name == "test_func", "name is not valid"
    assert entity.hash, "Condition must be true"
    assert len(entity.hash) == 16, "Collection must not be empty"


def test_repository_indexer_init(temp_repo):
    """Test RepositoryIndexer initialization."""
    indexer = RepositoryIndexer(temp_repo)

    assert indexer.repo_path == temp_repo, "repo_path is not valid"
    assert indexer.output_dir.exists(), "Condition must be true"
    assert indexer.content_index == {}, "Content must not be empty"
    assert indexer.semantic_index == {}, "semantic_index is not valid"


def test_extract_python_entities(temp_repo):
    """Test Python entity extraction."""
    indexer = RepositoryIndexer(temp_repo)
    module_file = temp_repo / "src" / "package" / "module.py"

    entities = indexer.extract_python_entities(module_file)

    # Should find: TestClass, method_one, method_two, test_function
    assert len(entities) >= 3, "Entities must not be empty"

    entity_names = [e.name for e in entities]
    assert "TestClass" in entity_names, "Condition must be true"
    assert "test_function" in entity_names, "Condition must be true"


def test_extract_imports(temp_repo):
    """Test import extraction."""
    indexer = RepositoryIndexer(temp_repo)

    # Create file with imports
    test_file = temp_repo / "test_imports.py"
    test_file.write_text("""
import os
import sys
from pathlib import Path
from typing import List, Dict
""")

    imports = indexer.extract_imports(test_file)

    assert "os" in imports, "Condition must be true"
    assert "sys" in imports, "Condition must be true"
    assert "pathlib" in imports, "Condition must be true"
    assert "typing" in imports, "Condition must be true"


def test_index_file_python(temp_repo):
    """Test file indexing for Python files."""
    indexer = RepositoryIndexer(temp_repo)
    module_file = temp_repo / "src" / "package" / "module.py"

    file_index = indexer.index_file(module_file)

    assert file_index is not None, "file_index must be initialized"
    assert file_index.language == "python", "language is not valid"
    assert file_index.relative_path == "src/package/module.py", "relative_path is not valid"
    assert len(file_index.entities) >= 3, "Collection must not be empty"
    assert file_index.size > 0, "size must be greater than zero"


def test_index_file_config(temp_repo):
    """Test file indexing for config files."""
    indexer = RepositoryIndexer(temp_repo)
    config_file = temp_repo / "config.yaml"

    file_index = indexer.index_file(config_file)

    assert file_index is not None, "file_index must be initialized"
    assert file_index.language == "config", "language is not valid"
    assert file_index.relative_path == "config.yaml", "relative_path is not valid"


def test_scan_repository(temp_repo):
    """Test full repository scanning."""
    indexer = RepositoryIndexer(temp_repo)
    indexer.scan_repository()

    # Should have indexed Python and config files
    assert len(indexer.content_index) >= 2, "Collection must not be empty"
    assert len(indexer.entity_index) >= 3, "Collection must not be empty"
    assert len(indexer.semantic_index) > 0, "Collection must not be empty"
    assert indexer.metadata_index["total_files"] >= 2, "Value must be greater than zero"
    assert "python" in indexer.metadata_index["languages"], "Data must not be empty"


def test_save_and_load_indices(temp_repo):
    """Test saving and loading indices."""
    # Generate indices
    indexer = RepositoryIndexer(temp_repo)
    indexer.scan_repository()
    indexer.save_indices()

    # Check files exist
    output_dir = temp_repo / ".codex" / "ai_index"
    assert (output_dir / "content_index.json").exists(), "Content must not be empty"
    assert (output_dir / "semantic_index.json").exists(), "Condition must be true"
    assert (output_dir / "structural_index.json").exists(), "Condition must be true"
    assert (output_dir / "entity_index.json").exists(), "Condition must be true"
    assert (output_dir / "metadata_index.json").exists(), "Data must not be empty"

    # Load and verify
    search = AIRepositorySearch(output_dir)
    assert len(search.content_index) >= 2, "Collection must not be empty"
    assert len(search.entity_index) >= 3, "Collection must not be empty"


def test_search_by_keyword(temp_repo):
    """Test keyword search."""
    # Generate indices
    indexer = RepositoryIndexer(temp_repo)
    indexer.scan_repository()
    indexer.save_indices()

    # Search
    search = AIRepositorySearch(temp_repo / ".codex" / "ai_index")
    results = search.search_by_keyword("TestClass")

    assert len(results) > 0, "Results must not be empty"
    assert any("module.py" in r.path for r in results), "Result must not be empty"


def test_search_by_entity(temp_repo):
    """Test entity search."""
    # Generate indices
    indexer = RepositoryIndexer(temp_repo)
    indexer.scan_repository()
    indexer.save_indices()

    # Search for class
    search = AIRepositorySearch(temp_repo / ".codex" / "ai_index")
    results = search.search_by_entity("TestClass", entity_type="class")

    assert len(results) > 0, "Results must not be empty"
    assert results[0].match_type == "entity_exact", "Result must not be empty"
    assert "line_start" in results[0].context, "Result must not be empty"


def test_search_by_path_pattern(temp_repo):
    """Test path pattern search."""
    # Generate indices
    indexer = RepositoryIndexer(temp_repo)
    indexer.scan_repository()
    indexer.save_indices()

    # Search
    search = AIRepositorySearch(temp_repo / ".codex" / "ai_index")
    results = search.search_by_path_pattern("test_")

    assert len(results) > 0, "Results must not be empty"
    assert all("test" in r.path.lower() for r in results), "Result must not be empty"


def test_multi_search(temp_repo):
    """Test multi-strategy search."""
    # Generate indices
    indexer = RepositoryIndexer(temp_repo)
    indexer.scan_repository()
    indexer.save_indices()

    # Search
    search = AIRepositorySearch(temp_repo / ".codex" / "ai_index")
    results = search.multi_search("test")

    assert len(results) > 0, "Results must not be empty"
    # Results should be sorted by relevance
    if len(results) > 1:
        assert results[0].relevance_score >= results[-1].relevance_score, "relevance_score must be greater than zero"


def test_get_file_details(temp_repo):
    """Test getting detailed file information."""
    # Generate indices
    indexer = RepositoryIndexer(temp_repo)
    indexer.scan_repository()
    indexer.save_indices()

    # Get details
    search = AIRepositorySearch(temp_repo / ".codex" / "ai_index")
    details = search.get_file_details("src/package/module.py")

    assert details is not None, "details must be initialized"
    assert details["language"] == "python", "Condition must be true"
    assert len(details["entities"]) >= 3, "Collection must not be empty"


def test_get_repository_summary(temp_repo):
    """Test repository summary retrieval."""
    # Generate indices
    indexer = RepositoryIndexer(temp_repo)
    indexer.scan_repository()
    indexer.save_indices()

    # Get summary
    search = AIRepositorySearch(temp_repo / ".codex" / "ai_index")
    summary = search.get_repository_summary()

    assert "total_files" in summary, "Condition must be true"
    assert "total_entities" in summary, "Condition must be true"
    assert "languages" in summary, "Condition must be true"
    assert summary["total_files"] >= 2, "Value must be greater than zero"


def test_skip_directories(temp_repo):
    """Test that skip directories are properly excluded."""
    # Create skip directories
    (temp_repo / ".git").mkdir()
    (temp_repo / ".git" / "file.py").write_text("# Should be skipped")

    (temp_repo / "node_modules").mkdir()
    (temp_repo / "node_modules" / "package.py").write_text("# Should be skipped")

    # Index
    indexer = RepositoryIndexer(temp_repo)
    indexer.scan_repository()

    # Check that skip dirs were excluded
    indexed_paths = [data.relative_path for data in indexer.content_index.values()]

    assert not any(".git" in path for path in indexed_paths), "Condition must be true"
    assert not any("node_modules" in path for path in indexed_paths), "Condition must be true"
