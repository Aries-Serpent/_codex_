"""
Comprehensive tests for documentation-system detector.

Tests documentation detection across markdown, reStructuredText,
and documentation generators (MkDocs, Sphinx, Docusaurus).
"""

from scripts.space_traversal.detectors.documentation_system import detect


def test_documentation_system_no_docs():
    """Test when no documentation files exist."""
    file_index = {
        "files": [
            {"path": "src/main.py", "ext": ".py"},
            {"path": "tests/test_main.py", "ext": ".py"},
        ]
    }

    result = detect(file_index)

    assert result["id"] == "documentation-system", "Result must not be empty"
    assert result["evidence_files"] == [], "Result must not be empty"
    assert "found_patterns" in result, "Result must not be empty"


def test_documentation_system_markdown_docs():
    """Test detection of markdown documentation."""
    file_index = {
        "files": [
            {"path": "docs/guide.md", "ext": ".md"},
            {"path": "docs/api.md", "ext": ".md"},
            {"path": "docs/tutorial.md", "ext": ".md"},
            {"path": "src/main.py", "ext": ".py"},
        ]
    }

    result = detect(file_index)

    assert result["id"] == "documentation-system", "Result must not be empty"
    assert len(result["evidence_files"]) == 3, "Collection must not be empty"
    assert "markdown" in result["found_patterns"], "Result must not be empty"
    assert "docs" in result["found_patterns"], "Result must not be empty"
    assert result["meta"]["markdown_count"] == 3, "Result must not be empty"


def test_documentation_system_rst_docs():
    """Test detection of reStructuredText documentation."""
    file_index = {
        "files": [
            {"path": "docs/index.rst", "ext": ".rst"},
            {"path": "docs/api.rst", "ext": ".rst"},
        ]
    }

    result = detect(file_index)

    assert result["id"] == "documentation-system", "Result must not be empty"
    assert len(result["evidence_files"]) == 2, "Collection must not be empty"
    assert result["meta"]["rst_count"] == 2, "Result must not be empty"


def test_documentation_system_mkdocs_config():
    """Test detection of MkDocs configuration."""
    file_index = {
        "files": [
            {"path": "mkdocs.yml", "ext": ".yml"},
            {"path": "docs/index.md", "ext": ".md"},
        ]
    }

    result = detect(file_index)

    assert result["id"] == "documentation-system", "Result must not be empty"
    assert "mkdocs" in result["found_patterns"], "Result must not be empty"
    assert result["meta"]["config_count"] == 1, "Result must not be empty"


def test_documentation_system_sphinx_config():
    """Test detection of Sphinx documentation."""
    file_index = {
        "files": [
            {"path": "docs/conf.py", "ext": ".py"},
            {"path": "docs/index.rst", "ext": ".rst"},
        ]
    }

    result = detect(file_index)

    assert result["id"] == "documentation-system", "Result must not be empty"
    assert "sphinx" in result["found_patterns"], "Result must not be empty"


def test_documentation_system_readme():
    """Test detection of README files."""
    file_index = {
        "files": [
            {"path": "README.md", "ext": ".md"},
            {"path": "docs/governance/CONTRIBUTING.md", "ext": ".md"},
        ]
    }

    result = detect(file_index)

    assert result["id"] == "documentation-system", "Result must not be empty"
    assert "README.md" in result["evidence_files"], "Result must not be empty"


def test_documentation_system_comprehensive():
    """Test comprehensive documentation setup."""
    file_index = {
        "files": [
            {"path": "README.md", "ext": ".md"},
            {"path": "docs/index.md", "ext": ".md"},
            {"path": "docs/guide.md", "ext": ".md"},
            {"path": "docs/api.rst", "ext": ".rst"},
            {"path": "mkdocs.yml", "ext": ".yml"},
            {"path": "docs/conf.py", "ext": ".py"},
        ]
    }

    result = detect(file_index)

    assert result["id"] == "documentation-system", "Result must not be empty"
    assert len(result["evidence_files"]) >= 6, "Collection must not be empty"
    assert "markdown" in result["found_patterns"], "Result must not be empty"
    assert "mkdocs" in result["found_patterns"], "Result must not be empty"
    assert "sphinx" in result["found_patterns"], "Result must not be empty"


def test_documentation_system_required_patterns():
    """Test that required patterns are properly defined."""
    file_index = {"files": []}
    result = detect(file_index)

    assert "required_patterns" in result, "Result must not be empty"
    assert "markdown" in result["required_patterns"], "Result must not be empty"
    assert "docs" in result["required_patterns"], "Result must not be empty"


def test_documentation_system_docs_keywords():
    """Test that docs_keywords metadata is present."""
    file_index = {"files": []}
    result = detect(file_index)

    assert "docs_keywords" in result, "Result must not be empty"
    assert "documentation" in result["docs_keywords"], "Result must not be empty"
    assert "markdown" in result["docs_keywords"], "Result must not be empty"


def test_documentation_system_safeguards():
    """Test that safeguards metadata is present."""
    file_index = {"files": []}
    result = detect(file_index)

    assert "safeguards" in result, "Result must not be empty"
    assert "validation" in result["safeguards"], "Result must not be empty"
    assert "bounded" in result["safeguards"], "Result must not be empty"


def test_documentation_system_functionality():
    """Test that functionality score is calculated."""
    file_index = {
        "files": [
            {"path": "docs/index.md", "ext": ".md"},
            {"path": "mkdocs.yml", "ext": ".yml"},
        ]
    }
    result = detect(file_index)

    assert "functionality_impl" in result, "Result must not be empty"
    assert isinstance(result["functionality_impl"], float)
    assert 0.0 <= result["functionality_impl"] <= 1.0, "Result must not be empty"


def test_documentation_system_meta_fields():
    """Test that meta fields are properly populated."""
    file_index = {
        "files": [
            {"path": "docs/guide.md", "ext": ".md"},
            {"path": "docs/api.rst", "ext": ".rst"},
        ]
    }
    result = detect(file_index)

    assert "meta" in result, "Result must not be empty"
    assert "markdown_count" in result["meta"], "Result must not be empty"
    assert "rst_count" in result["meta"], "Result must not be empty"
    assert "config_count" in result["meta"], "Result must not be empty"
    assert "total_docs" in result["meta"], "Result must not be empty"
    assert result["meta"]["deterministic"] is True, "Result must not be empty"


def test_documentation_system_sorted_evidence():
    """Test that evidence files are sorted deterministically."""
    file_index = {
        "files": [
            {"path": "docs/z_file.md", "ext": ".md"},
            {"path": "docs/a_file.md", "ext": ".md"},
            {"path": "docs/m_file.md", "ext": ".md"},
        ]
    }
    result = detect(file_index)

    evidence = result["evidence_files"]
    assert evidence == sorted(evidence), "evidence is not valid"


def test_documentation_system_docusaurus():
    """Test detection of Docusaurus documentation."""
    file_index = {
        "files": [
            {"path": "docusaurus.config.js", "ext": ".js"},
            {"path": "docs/intro.md", "ext": ".md"},
        ]
    }
    result = detect(file_index)

    assert result["id"] == "documentation-system", "Result must not be empty"
    assert len(result["evidence_files"]) >= 1, "Collection must not be empty"


def test_documentation_system_changelog():
    """Test detection of CHANGELOG files."""
    file_index = {
        "files": [
            {"path": "docs/CHANGELOG.md", "ext": ".md"},
        ]
    }
    result = detect(file_index)

    assert result["id"] == "documentation-system", "Result must not be empty"
    assert "docs/CHANGELOG.md" in result["evidence_files"], "Result must not be empty"


def test_documentation_system_contributing():
    """Test detection of CONTRIBUTING files."""
    file_index = {
        "files": [
            {"path": "docs/governance/CONTRIBUTING.md", "ext": ".md"},
        ]
    }
    result = detect(file_index)

    assert result["id"] == "documentation-system", "Result must not be empty"
    assert "docs/governance/CONTRIBUTING.md" in result["evidence_files"], "Result must not be empty"


def test_documentation_system_readthedocs():
    """Test detection of ReadTheDocs configuration."""
    file_index = {
        "files": [
            {"path": ".readthedocs.yml", "ext": ".yml"},
            {"path": "docs/index.rst", "ext": ".rst"},
        ]
    }
    result = detect(file_index)

    assert result["id"] == "documentation-system", "Result must not be empty"
    assert result["meta"]["config_count"] >= 1, "Value must be greater than zero"


def test_documentation_system_empty_file_index():
    """Test handling of empty file index."""
    file_index = {}
    result = detect(file_index)

    assert result["id"] == "documentation-system", "Result must not be empty"
    assert result["evidence_files"] == [], "Result must not be empty"
    assert result["meta"]["total_docs"] == 0, "Result must not be empty"


def test_documentation_system_mixed_extensions():
    """Test handling of mixed file extensions."""
    file_index = {
        "files": [
            {"path": "docs/guide.md", "ext": ".md"},
            {"path": "docs/api.rst", "ext": ".rst"},
            {"path": "docs/tutorial.txt", "ext": ".txt"},
            {"path": "src/code.py", "ext": ".py"},
        ]
    }
    result = detect(file_index)

    # Should only detect .md and .rst as documentation
    assert result["meta"]["markdown_count"] == 1, "Result must not be empty"
    assert result["meta"]["rst_count"] == 1, "Result must not be empty"
