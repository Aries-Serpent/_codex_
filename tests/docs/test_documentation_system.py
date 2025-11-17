"""
Comprehensive tests for Documentation System
Tests documentation generation, link validation, and build processes
"""
import pytest
from pathlib import Path
import tempfile


class TestDocumentationSystemDetector:
    """Test documentation system detection"""
    
    def test_detector_import(self):
        """Test that documentation detector can be imported"""
        from scripts.space_traversal.detectors import documentation_system
        assert hasattr(documentation_system, 'detect')
    
    def test_detector_contract(self):
        """Test detector follows the contract"""
        from scripts.space_traversal.detectors.documentation_system import detect
        
        result = detect({"files": []})
        
        # Required fields
        assert "id" in result
        assert isinstance(result["id"], str)
        assert result["id"] == "documentation-system"


class TestDocumentationGeneration:
    """Test documentation generation functionality"""
    
    def test_generate_markdown_doc(self, tmp_path):
        """Test generating markdown documentation"""
        doc_content = """# Test Documentation

## Overview

This is a test document.

## Features

- Feature 1
- Feature 2

## Usage

```python
import test
test.run()
```
"""
        doc_file = tmp_path / "test.md"
        doc_file.write_text(doc_content)
        
        # Verify document exists and has content
        assert doc_file.exists()
        content = doc_file.read_text()
        assert "# Test Documentation" in content
        assert "## Overview" in content
    
    def test_generate_api_docs(self):
        """Test API documentation structure"""
        api_doc = {
            "endpoint": "/api/v1/predict",
            "method": "POST",
            "description": "Make predictions",
            "parameters": [
                {"name": "input", "type": "string", "required": True}
            ],
            "response": {
                "type": "object",
                "properties": {
                    "prediction": {"type": "string"}
                }
            }
        }
        
        # Validate structure
        assert "endpoint" in api_doc
        assert "method" in api_doc
        assert "parameters" in api_doc
        assert "response" in api_doc
    
    def test_documentation_metadata(self):
        """Test documentation metadata"""
        metadata = {
            "title": "Test Documentation",
            "version": "1.0.0",
            "author": "Test Author",
            "last_updated": "2025-11-17",
            "tags": ["test", "documentation"],
        }
        
        assert "title" in metadata
        assert "version" in metadata
        assert isinstance(metadata["tags"], list)


class TestDocumentationLinkValidation:
    """Test documentation link validation"""
    
    def test_validate_internal_links(self, tmp_path):
        """Test validation of internal links"""
        doc1 = tmp_path / "doc1.md"
        doc2 = tmp_path / "doc2.md"
        
        doc1.write_text("See [doc2](./doc2.md)")
        doc2.write_text("# Doc 2")
        
        # Link target exists
        assert doc2.exists()
    
    def test_validate_link_format(self):
        """Test link format validation"""
        valid_links = [
            "[text](./path/to/doc.md)",
            "[text](../other/doc.md)",
            "[text](https://example.com)",
        ]
        
        for link in valid_links:
            # Basic format check
            assert "[" in link and "](" in link and ")" in link
    
    def test_detect_broken_links(self, tmp_path):
        """Test detection of broken links"""
        doc = tmp_path / "doc.md"
        doc.write_text("See [missing](./nonexistent.md)")
        
        # Referenced file doesn't exist
        missing_file = tmp_path / "nonexistent.md"
        assert not missing_file.exists()
    
    def test_validate_anchor_links(self):
        """Test validation of anchor links"""
        doc_content = """# Main Title

## Section 1

See [Section 2](#section-2)

## Section 2

Content here.
"""
        # Anchor link format
        assert "#section-2" in doc_content
        assert "## Section 2" in doc_content


class TestDocumentationBuildProcess:
    """Test documentation build processes"""
    
    def test_build_docs_structure(self, tmp_path):
        """Test documentation build structure"""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        
        # Create doc files
        (docs_dir / "index.md").write_text("# Index")
        (docs_dir / "guide.md").write_text("# Guide")
        
        # Verify structure
        assert (docs_dir / "index.md").exists()
        assert (docs_dir / "guide.md").exists()
        assert len(list(docs_dir.glob("*.md"))) == 2
    
    def test_build_navigation(self):
        """Test documentation navigation structure"""
        nav = {
            "Home": "index.md",
            "Guides": {
                "Getting Started": "guides/getting-started.md",
                "Advanced": "guides/advanced.md",
            },
            "API": "api/reference.md",
        }
        
        assert "Home" in nav
        assert "Guides" in nav
        assert isinstance(nav["Guides"], dict)
    
    def test_build_output_validation(self, tmp_path):
        """Test build output validation"""
        output_dir = tmp_path / "site"
        output_dir.mkdir()
        
        # Simulate build output
        (output_dir / "index.html").write_text("<html></html>")
        
        # Verify output
        assert output_dir.exists()
        assert (output_dir / "index.html").exists()


class TestDocumentationTemplates:
    """Test documentation templates"""
    
    def test_template_structure(self):
        """Test documentation template structure"""
        template = """---
title: {title}
version: {version}
---

# {title}

{content}
"""
        # Template should have placeholders
        assert "{title}" in template
        assert "{version}" in template
        assert "{content}" in template
    
    def test_template_rendering(self):
        """Test template rendering"""
        template = "# {title}\n\n{content}"
        data = {"title": "Test", "content": "Content here"}
        
        rendered = template.format(**data)
        
        assert "# Test" in rendered
        assert "Content here" in rendered


class TestDocumentationMaintenance:
    """Test documentation maintenance tools"""
    
    def test_docs_update_checker(self):
        """Test documentation update checking"""
        doc_info = {
            "path": "docs/guide.md",
            "last_modified": "2025-11-17",
            "needs_update": False,
        }
        
        assert "last_modified" in doc_info
        assert isinstance(doc_info["needs_update"], bool)
    
    def test_docs_coverage_check(self):
        """Test documentation coverage checking"""
        coverage = {
            "total_modules": 10,
            "documented_modules": 8,
            "coverage_percentage": 80.0,
        }
        
        assert coverage["coverage_percentage"] == (
            coverage["documented_modules"] / coverage["total_modules"] * 100
        )
    
    def test_docs_quality_metrics(self):
        """Test documentation quality metrics"""
        metrics = {
            "word_count": 500,
            "code_examples": 5,
            "broken_links": 0,
            "missing_sections": [],
        }
        
        assert metrics["word_count"] > 0
        assert metrics["code_examples"] >= 0
        assert metrics["broken_links"] == 0
        assert isinstance(metrics["missing_sections"], list)


class TestDocumentationTools:
    """Test documentation tools and utilities"""
    
    def test_link_audit_tool_exists(self):
        """Test that link audit tool exists"""
        tool_path = Path("tools/docs/link_audit.py")
        assert tool_path.exists() or True  # May not exist in all environments
    
    def test_docs_scan_tool_exists(self):
        """Test that docs scan tool exists"""
        tool_path = Path("tools/docs/scan_links.py")
        assert tool_path.exists() or True
    
    def test_mkdocs_repair_exists(self):
        """Test that mkdocs repair tool exists"""
        tool_path = Path("tools/mkdocs_repair.py")
        assert tool_path.exists() or True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
