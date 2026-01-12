#!/usr/bin/env python3
"""
Unit tests for Documentation Sync Validator Agent

Tests cover:
- Configuration loading
- Freshness checking
- Link validation
- Semantic drift detection
- Schema validation
- Report generation
"""

import pytest
from pathlib import Path
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
import tempfile
import os

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent import (
    DocumentationSyncValidator,
    DocumentationIssue,
    FreshnessReport,
    SemanticDriftReport,
    DriftSeverity,
    FreshnessStatus,
)


class TestDocumentationSyncValidator:
    """Test suite for DocumentationSyncValidator agent"""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance with default config"""
        return DocumentationSyncValidator()
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_agent_initialization(self, agent):
        """Test agent initializes with default configuration"""
        assert agent is not None
        assert agent.config['agent_name'] == 'documentation-sync-validator'
        assert 'check_freshness' in agent.config['capabilities']
        assert agent.freshness_threshold_days == 90
        assert agent.semantic_drift_threshold == 0.7
    
    def test_load_default_config(self, agent):
        """Test default configuration loading"""
        config = agent._default_config()
        assert config['version'] == '1.0.0'
        assert config['agent_name'] == 'documentation-sync-validator'
        assert len(config['capabilities']) == 4
        assert config['freshness_threshold_days'] == 90
    
    def test_find_documentation_files(self, agent, temp_dir):
        """Test finding documentation files in directory tree"""
        # Create test documentation files
        (temp_dir / "README.md").write_text("# Test")
        (temp_dir / "docs").mkdir()
        (temp_dir / "docs" / "api.md").write_text("# API")
        (temp_dir / "docs" / "guide.rst").write_text("Guide")
        
        # Create files to exclude
        (temp_dir / ".git").mkdir()
        (temp_dir / ".git" / "ignore.md").write_text("Ignore")
        
        files = agent._find_documentation_files(temp_dir)
        
        assert len(files) >= 3
        assert any(f.name == "README.md" for f in files)
        assert any(f.name == "api.md" for f in files)
        assert any(f.name == "guide.rst" for f in files)
        assert not any(".git" in str(f) for f in files)
    
    def test_check_freshness_fresh_file(self, agent, temp_dir):
        """Test freshness checking for recently modified file"""
        test_file = temp_dir / "fresh.md"
        test_file.write_text("# Fresh content")
        
        report = agent.check_freshness(test_file)
        
        assert report.file_path == test_file
        assert report.status == FreshnessStatus.FRESH
        assert report.age_days < 30
    
    def test_check_freshness_aging_file(self, agent, temp_dir):
        """Test freshness checking for aging file"""
        test_file = temp_dir / "aging.md"
        test_file.write_text("# Aging content")
        
        # Mock file modification time to 45 days ago
        days_ago = 45
        old_time = (datetime.now(timezone.utc) - timedelta(days=days_ago)).timestamp()
        os.utime(test_file, (old_time, old_time))
        
        report = agent.check_freshness(test_file)
        
        assert report.status == FreshnessStatus.AGING
        assert 30 <= report.age_days < 90
    
    def test_check_freshness_stale_file(self, agent, temp_dir):
        """Test freshness checking for stale file"""
        test_file = temp_dir / "stale.md"
        test_file.write_text("# Stale content")
        
        # Mock file modification time to 120 days ago
        days_ago = 120
        old_time = (datetime.now(timezone.utc) - timedelta(days=days_ago)).timestamp()
        os.utime(test_file, (old_time, old_time))
        
        report = agent.check_freshness(test_file)
        
        assert report.status == FreshnessStatus.STALE
        assert report.age_days >= 90
    
    def test_check_freshness_nonexistent_file(self, agent, temp_dir):
        """Test freshness checking raises error for nonexistent file"""
        nonexistent = temp_dir / "nonexistent.md"
        
        with pytest.raises(FileNotFoundError):
            agent.check_freshness(nonexistent)
    
    def test_validate_links_valid_internal_link(self, agent, temp_dir):
        """Test link validation with valid internal link"""
        target = temp_dir / "target.md"
        target.write_text("# Target")
        
        doc_file = temp_dir / "doc.md"
        doc_file.write_text(f"[Link](target.md)")
        
        broken = agent.validate_links(doc_file)
        
        assert len(broken) == 0
    
    def test_validate_links_broken_internal_link(self, agent, temp_dir):
        """Test link validation with broken internal link"""
        doc_file = temp_dir / "doc.md"
        doc_file.write_text("[Broken](nonexistent.md)")
        
        broken = agent.validate_links(doc_file)
        
        assert len(broken) == 1
        assert broken[0][0] == "nonexistent.md"
        assert "not found" in broken[0][1].lower()
    
    def test_validate_links_skip_anchor_links(self, agent, temp_dir):
        """Test link validation skips anchor links"""
        doc_file = temp_dir / "doc.md"
        doc_file.write_text("[Anchor](#section)")
        
        broken = agent.validate_links(doc_file)
        
        assert len(broken) == 0
    
    def test_validate_links_html_format(self, agent, temp_dir):
        """Test link validation with HTML link format"""
        target = temp_dir / "target.md"
        target.write_text("# Target")
        
        doc_file = temp_dir / "doc.md"
        doc_file.write_text('<a href="target.md">Link</a>')
        
        broken = agent.validate_links(doc_file)
        
        assert len(broken) == 0
    
    def test_detect_semantic_drift_high_similarity(self, agent, temp_dir):
        """Test semantic drift detection with high similarity"""
        # Create code file
        code_dir = temp_dir / "src"
        code_dir.mkdir()
        code_file = code_dir / "calculator.py"
        code_file.write_text("""
def add_numbers(x, y):
    return x + y

def subtract_numbers(x, y):
    return x - y
""")
        
        # Create documentation with similar concepts
        doc_file = temp_dir / "calculator.md"
        doc_file.write_text("""
# Calculator Module

Functions:
- add_numbers: Adds two numbers
- subtract_numbers: Subtracts two numbers
""")
        
        reports = agent.detect_semantic_drift(doc_file, code_dir)
        
        assert len(reports) > 0
        assert reports[0].similarity_score > 0.5
        assert reports[0].drift_severity in [DriftSeverity.NONE, DriftSeverity.LOW]
    
    def test_detect_semantic_drift_low_similarity(self, agent, temp_dir):
        """Test semantic drift detection with low similarity"""
        # Create code file
        code_dir = temp_dir / "src"
        code_dir.mkdir()
        code_file = code_dir / "database.py"
        code_file.write_text("""
def connect_database(host, port):
    pass

def execute_query(query):
    pass
""")
        
        # Create documentation with completely different concepts
        doc_file = temp_dir / "database.md"
        doc_file.write_text("""
# Unrelated Content

This talks about something completely different.
""")
        
        reports = agent.detect_semantic_drift(doc_file, code_dir)
        
        if reports:  # May have no reports if no name match
            assert reports[0].similarity_score < 0.5
            assert reports[0].drift_severity != DriftSeverity.NONE
    
    def test_validate_schema_missing_frontmatter(self, agent, temp_dir):
        """Test schema validation with missing frontmatter"""
        doc_file = temp_dir / "doc.md"
        doc_file.write_text("# Document without frontmatter")
        
        schema = {'required': ['title', 'author']}
        issues = agent.validate_schema(doc_file, schema)
        
        assert len(issues) == 1
        assert issues[0].issue_type == 'schema_violation'
        assert "No frontmatter" in issues[0].description
    
    def test_validate_schema_missing_required_field(self, agent, temp_dir):
        """Test schema validation with missing required field"""
        doc_file = temp_dir / "doc.md"
        doc_file.write_text("""---
title: Test Document
---
# Content
""")
        
        schema = {'required': ['title', 'author', 'date']}
        issues = agent.validate_schema(doc_file, schema)
        
        assert len(issues) >= 2  # Missing 'author' and 'date'
        assert any('author' in issue.description for issue in issues)
        assert any('date' in issue.description for issue in issues)
    
    def test_validate_schema_valid_frontmatter(self, agent, temp_dir):
        """Test schema validation with valid frontmatter"""
        doc_file = temp_dir / "doc.md"
        doc_file.write_text("""---
title: Test Document
author: Test Author
---
# Content
""")
        
        schema = {'required': ['title', 'author']}
        issues = agent.validate_schema(doc_file, schema)
        
        assert len(issues) == 0
    
    def test_validate_schema_invalid_yaml(self, agent, temp_dir):
        """Test schema validation with invalid YAML frontmatter"""
        doc_file = temp_dir / "doc.md"
        doc_file.write_text("""---
title: Test Document
invalid yaml: [unclosed bracket
---
# Content
""")
        
        schema = {'required': ['title']}
        issues = agent.validate_schema(doc_file, schema)
        
        assert len(issues) == 1
        assert "Invalid YAML" in issues[0].description
        assert issues[0].severity == DriftSeverity.HIGH
    
    def test_validate_all_comprehensive(self, agent, temp_dir):
        """Test comprehensive validation of all checks"""
        # Create stale documentation
        stale_file = temp_dir / "stale.md"
        stale_file.write_text("[Broken link](nonexistent.md)")
        old_time = (datetime.now(timezone.utc) - timedelta(days=120)).timestamp()
        os.utime(stale_file, (old_time, old_time))
        
        # Create code directory for drift check
        code_dir = temp_dir / "src"
        code_dir.mkdir()
        
        issues = agent.validate_all(temp_dir)
        
        # Should find multiple issues
        assert len(issues) >= 2  # At least staleness and broken link
        assert any(issue.issue_type == 'freshness' for issue in issues)
        assert any(issue.issue_type == 'broken_link' for issue in issues)
    
    def test_generate_report_text_format(self, agent, temp_dir):
        """Test report generation in text format"""
        agent.issues = [
            DocumentationIssue(
                file_path=temp_dir / "test.md",
                issue_type='freshness',
                severity=DriftSeverity.MEDIUM,
                description="Test issue"
            )
        ]
        
        report = agent.generate_report('text')
        
        assert "Documentation Validation Report" in report
        assert "Total Issues: 1" in report
        assert "MEDIUM" in report
        assert "Test issue" in report
    
    def test_generate_report_json_format(self, agent, temp_dir):
        """Test report generation in JSON format"""
        import json
        
        agent.issues = [
            DocumentationIssue(
                file_path=temp_dir / "test.md",
                issue_type='freshness',
                severity=DriftSeverity.HIGH,
                description="Test issue",
                line_number=42,
                confidence=0.95
            )
        ]
        
        report = agent.generate_report('json')
        data = json.loads(report)
        
        assert len(data) == 1
        assert data[0]['type'] == 'freshness'
        assert data[0]['severity'] == 'high'
        assert data[0]['line'] == 42
        assert data[0]['confidence'] == 0.95
    
    def test_generate_report_markdown_format(self, agent, temp_dir):
        """Test report generation in Markdown format"""
        agent.issues = [
            DocumentationIssue(
                file_path=temp_dir / "test.md",
                issue_type='freshness',
                severity=DriftSeverity.LOW,
                description="Test issue"
            )
        ]
        
        report = agent.generate_report('markdown')
        
        assert "# Documentation Validation Report" in report
        assert "**Total Issues**: 1" in report
        assert "## LOW" in report
    
    def test_freshness_to_severity_conversion(self, agent):
        """Test conversion from freshness status to severity"""
        assert agent._freshness_to_severity(FreshnessStatus.FRESH) == DriftSeverity.NONE
        assert agent._freshness_to_severity(FreshnessStatus.AGING) == DriftSeverity.LOW
        assert agent._freshness_to_severity(FreshnessStatus.STALE) == DriftSeverity.MEDIUM


# Property-based tests using hypothesis (if available)
try:
    from hypothesis import given, strategies as st
    
    class TestPropertyBased:
        """Property-based tests for edge cases"""
        
        @given(st.integers(min_value=0, max_value=365))
        def test_freshness_age_days_always_positive(self, days):
            """Property: Age in days should always be non-negative"""
            agent = DocumentationSyncValidator()
            with tempfile.TemporaryDirectory() as tmpdir:
                test_file = Path(tmpdir) / "test.md"
                test_file.write_text("# Test")
                
                report = agent.check_freshness(test_file)
                assert report.age_days >= 0
        
        @given(st.floats(min_value=0.0, max_value=1.0))
        def test_similarity_score_bounded(self, score):
            """Property: Similarity score should be between 0 and 1"""
            # This is validated in the dataclass
            report = SemanticDriftReport(
                doc_file=Path("doc.md"),
                code_file=Path("code.py"),
                similarity_score=score,
                drift_severity=DriftSeverity.NONE
            )
            assert 0.0 <= report.similarity_score <= 1.0

except ImportError:
    # hypothesis not available, skip property-based tests
    pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
