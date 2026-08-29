"""
MCP Tooling Registry comprehensive tests.

Tests for MCP tool registry detection, validation, and configuration.
Implements deterministic, reproducible test patterns with bounded operations.
"""


class TestMCPToolingRegistry:
    """Test MCP tooling registry detection."""

    def test_detector_import(self):
        """Test mcp tooling registry detector can be imported."""
        from scripts.space_traversal.detectors import mcp_tooling_registry

        assert hasattr(mcp_tooling_registry, "detect")

    def test_detector_output_contract(self):
        """Test detector output follows contract."""
        from scripts.space_traversal.detectors.mcp_tooling_registry import detect

        result = detect({"files": []})

        assert "id" in result, "Result must not be empty"
        assert result["id"] == "mcp-tooling-registry", "Result must not be empty"
        assert "evidence_files" in result, "Result must not be empty"
        assert "found_patterns" in result, "Result must not be empty"
        assert "required_patterns" in result, "Result must not be empty"

    def test_required_patterns(self):
        """Test required patterns are defined."""
        from scripts.space_traversal.detectors.mcp_tooling_registry import detect

        result = detect({"files": []})

        assert "registry" in result["required_patterns"], "Result must not be empty"
        assert "mcp.json" in result["required_patterns"], "Result must not be empty"

    def test_safeguards_metadata(self):
        """Test safeguards metadata is present."""
        from scripts.space_traversal.detectors.mcp_tooling_registry import detect

        result = detect({"files": []})

        assert "safeguards" in result, "Result must not be empty"
        assert "bounded" in result["safeguards"], "Result must not be empty"
        assert "deterministic" in result["safeguards"], "Result must not be empty"

    def test_docs_keywords(self):
        """Test docs_keywords are present."""
        from scripts.space_traversal.detectors.mcp_tooling_registry import detect

        result = detect({"files": []})

        assert "docs_keywords" in result, "Result must not be empty"
        assert "mcp" in result["docs_keywords"], "Result must not be empty"
        assert "registry" in result["docs_keywords"], "Result must not be empty"


class TestMCPToolingDetection:
    """Test MCP tooling detection patterns."""

    def test_empty_file_index(self):
        """Test detection with empty file index."""
        from scripts.space_traversal.detectors.mcp_tooling_registry import detect

        result = detect({"files": []})
        assert isinstance(result["evidence_files"], list)

    def test_registry_detection(self):
        """Test registry file detection."""
        from scripts.space_traversal.detectors.mcp_tooling_registry import detect

        file_index = {
            "files": [
                {"path": "mcp/registry.py"},
                {"path": "tools/mcp.json"},
            ]
        }
        result = detect(file_index)
        assert len(result["evidence_files"]) > 0, "Collection must not be empty"

    def test_deterministic_output(self):
        """Test deterministic detection output."""
        from scripts.space_traversal.detectors.mcp_tooling_registry import detect

        file_index = {"files": [{"path": "mcp/registry.py"}]}

        results = [detect(file_index) for _ in range(3)]
        for i in range(1, len(results)):
            assert results[i]["found_patterns"] == results[0]["found_patterns"], "Result must not be empty"

    def test_related_files_defined(self):
        """Test related files are defined."""
        from scripts.space_traversal.detectors.mcp_tooling_registry import RELATED_FILES

        assert len(RELATED_FILES) > 0, "Related_files must not be empty"

    def test_meta_category(self):
        """Test meta category is mcp."""
        from scripts.space_traversal.detectors.mcp_tooling_registry import detect

        result = detect({"files": []})
        assert result["meta"]["category"] == "mcp", "Result must not be empty"
