"""Comprehensive unit tests for Project Architect Researcher Agent."""
import pytest
from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent import ProjectArchitectResearcher, NotebookLMSource, ResearchArtifact


class TestProjectArchitectResearcher:
    """Test suite for ProjectArchitectResearcher class."""
    
    def test_researcher_initialization(self):
        """Test researcher initializes with default config."""
        researcher = ProjectArchitectResearcher()
        assert researcher.config is not None
        assert researcher.config['enabled'] is True
        assert researcher.artifacts == []
    
    def test_parse_markdown_file(self, tmp_path):
        """Test parsing markdown file."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\n\nContent with [link](https://example.com)")
        
        researcher = ProjectArchitectResearcher()
        source = researcher.parse_file(md_file)
        
        assert source is not None
        assert source.title == "test.md"
        assert source.source_type == "markdown"
        assert len(source.citations) >= 1
    
    def test_parse_json_file(self, tmp_path):
        """Test parsing JSON file."""
        json_file = tmp_path / "data.json"
        json_file.write_text('{"key": "value"}')
        
        researcher = ProjectArchitectResearcher()
        source = researcher.parse_file(json_file)
        
        assert source is not None
        assert source.source_type == "json"
    
    def test_scan_directory_recursive(self, tmp_path):
        """Test scanning directory recursively."""
        (tmp_path / "file1.md").write_text("# File 1")
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "file2.md").write_text("# File 2")
        
        researcher = ProjectArchitectResearcher()
        sources = researcher.scan_directory(tmp_path, recursive=True)
        
        assert len(sources) == 2
    
    def test_scan_directory_non_recursive(self, tmp_path):
        """Test scanning directory non-recursively."""
        (tmp_path / "file1.md").write_text("# File 1")
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "file2.md").write_text("# File 2")
        
        researcher = ProjectArchitectResearcher()
        sources = researcher.scan_directory(tmp_path, recursive=False)
        
        assert len(sources) == 1
    
    def test_create_artifact(self):
        """Test creating research artifact."""
        sources = [
            NotebookLMSource(
                title="Source 1",
                content="Content 1",
                source_type="markdown",
                metadata={},
                citations=[],
                created_at="2026-01-12T00:00:00Z"
            )
        ]
        
        researcher = ProjectArchitectResearcher()
        artifact = researcher.create_artifact("Test Artifact", sources, ["tag1", "tag2"])
        
        assert artifact.title == "Test Artifact"
        assert len(artifact.sources) == 1
        assert "tag1" in artifact.tags
        assert len(researcher.artifacts) == 1
    
    def test_export_artifact_json(self, tmp_path):
        """Test exporting artifact as JSON."""
        source = NotebookLMSource(
            title="Test",
            content="Content",
            source_type="markdown",
            metadata={},
            citations=[],
            created_at="2026-01-12T00:00:00Z"
        )
        artifact = ResearchArtifact(
            artifact_id="test_id",
            title="Test",
            sources=[source],
            summary="Summary",
            tags=["test"],
            created_at="2026-01-12T00:00:00Z"
        )
        
        researcher = ProjectArchitectResearcher()
        output_file = tmp_path / "artifact.json"
        exported = researcher.export_artifact(artifact, output_file, 'json')
        
        assert exported.exists()
        data = json.loads(exported.read_text())
        assert data['artifact_id'] == "test_id"
    
    def test_export_artifact_markdown(self, tmp_path):
        """Test exporting artifact as markdown."""
        source = NotebookLMSource(
            title="Test",
            content="Content",
            source_type="markdown",
            metadata={'file_size_kb': 0.5},
            citations=[],
            created_at="2026-01-12T00:00:00Z"
        )
        artifact = ResearchArtifact(
            artifact_id="test_id",
            title="Test",
            sources=[source],
            summary="Summary",
            tags=["test"],
            created_at="2026-01-12T00:00:00Z"
        )
        
        researcher = ProjectArchitectResearcher()
        output_file = tmp_path / "artifact.md"
        exported = researcher.export_artifact(artifact, output_file, 'markdown')
        
        assert exported.exists()
        content = exported.read_text()
        assert "# Test" in content
    
    def test_generate_report(self):
        """Test report generation."""
        sources = [
            NotebookLMSource("S1", "Content1", "markdown", {}, [], "2026-01-12T00:00:00Z"),
            NotebookLMSource("S2", "Content2", "markdown", {}, [], "2026-01-12T00:00:00Z"),
        ]
        artifact = ResearchArtifact(
            "id1", "Title", sources, "Summary", ["tag1"], "2026-01-12T00:00:00Z"
        )
        
        researcher = ProjectArchitectResearcher()
        report = researcher.generate_report([artifact])
        
        assert report['total_artifacts'] == 1
        assert report['total_sources'] == 2
        assert 'total_content_chars' in report


def test_real_world_scenario(tmp_path):
    """Test complete workflow."""
    # Create test files
    (tmp_path / "README.md").write_text("# Project\n\n[Link](https://example.com)")
    (tmp_path / "data.json").write_text('{"config": "value"}')
    
    researcher = ProjectArchitectResearcher()
    sources = researcher.scan_directory(tmp_path)
    
    assert len(sources) == 2
    
    artifact = researcher.create_artifact("Test Project", sources, ["research"])
    assert artifact.title == "Test Project"
    
    output_file = tmp_path / "output" / "artifact.json"
    exported = researcher.export_artifact(artifact, output_file, 'json')
    assert exported.exists()
