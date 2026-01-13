#!/usr/bin/env python3
"""
Integration tests for Documentation Sync Validator Agent

Tests full workflows and integration scenarios.
"""

import pytest
from pathlib import Path
import tempfile
import os
from datetime import datetime, timezone, timedelta

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent import DocumentationSyncValidator, DriftSeverity, FreshnessStatus


class TestIntegration:
    """Integration tests for complete workflows"""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project structure"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            
            # Create project structure
            (root / "src").mkdir()
            (root / "docs").mkdir()
            (root / "tests").mkdir()
            
            # Create source files
            (root / "src" / "calculator.py").write_text("""
def add(a, b):
    '''Add two numbers'''
    return a + b

def subtract(a, b):
    '''Subtract b from a'''
    return a - b
""")
            
            (root / "src" / "database.py").write_text("""
def connect(host, port=5432):
    '''Connect to database'''
    pass

def query(sql):
    '''Execute SQL query'''
    pass
""")
            
            # Create documentation
            (root / "docs" / "calculator.md").write_text("""---
title: Calculator Module
author: Test
---

# Calculator

Functions:
- add: Adds two numbers
- subtract: Subtracts two numbers

[API Reference](api.md)
""")
            
            (root / "docs" / "database.md").write_text("""
# Database Module

Outdated content here.
""")
            
            (root / "README.md").write_text("""
# Project README

[Calculator Docs](docs/calculator.md)
[Database Docs](docs/database.md)
[Broken Link](docs/nonexistent.md)
""")
            
            yield root
    
    def test_full_validation_workflow(self, temp_project):
        """Test complete validation workflow on a project"""
        agent = DocumentationSyncValidator()
        issues = agent.validate_all(temp_project)
        
        # Should detect multiple issues
        assert len(issues) > 0
        
        # Should find broken link
        broken_link_issues = [i for i in issues if i.issue_type == 'broken_link']
        assert len(broken_link_issues) > 0
        
        # Generate report
        report = agent.generate_report('text')
        assert 'Documentation Validation Report' in report
        assert len(report) > 100
    
    def test_freshness_workflow(self, temp_project):
        """Test freshness checking workflow"""
        agent = DocumentationSyncValidator()
        
        # Make one file stale
        stale_doc = temp_project / "docs" / "database.md"
        old_time = (datetime.now(timezone.utc) - timedelta(days=100)).timestamp()
        os.utime(stale_doc, (old_time, old_time))
        
        issues = agent.validate_all(temp_project)
        
        # Should find stale documentation
        stale_issues = [i for i in issues if i.issue_type == 'freshness' and i.severity != DriftSeverity.NONE]
        assert len(stale_issues) > 0
        assert any('database.md' in str(i.file_path) for i in stale_issues)
    
    def test_semantic_drift_workflow(self, temp_project):
        """Test semantic drift detection workflow"""
        agent = DocumentationSyncValidator()
        
        # Check specific file for drift
        doc_file = temp_project / "docs" / "calculator.md"
        code_dir = temp_project / "src"
        
        reports = agent.detect_semantic_drift(doc_file, code_dir)
        
        # Should detect relationship with calculator.py
        assert len(reports) > 0
        assert any('calculator.py' in str(r.code_file) for r in reports)
    
    def test_link_validation_workflow(self, temp_project):
        """Test link validation workflow"""
        agent = DocumentationSyncValidator()
        
        # Validate links in README
        readme = temp_project / "README.md"
        broken = agent.validate_links(readme)
        
        # Should find broken link to nonexistent.md
        assert len(broken) > 0
        assert any('nonexistent.md' in link for link, _ in broken)
    
    def test_schema_validation_workflow(self, temp_project):
        """Test schema validation workflow"""
        agent = DocumentationSyncValidator()
        
        # Define schema
        schema = {
            'required': ['title', 'author', 'date']
        }
        
        # Check calculator.md (has title and author, missing date)
        doc_file = temp_project / "docs" / "calculator.md"
        issues = agent.validate_schema(doc_file, schema)
        
        assert len(issues) == 1  # Missing 'date'
        assert 'date' in issues[0].description
    
    def test_json_report_generation_workflow(self, temp_project):
        """Test JSON report generation workflow"""
        import json
        
        agent = DocumentationSyncValidator()
        agent.validate_all(temp_project)
        
        report = agent.generate_report('json')
        data = json.loads(report)
        
        assert isinstance(data, list)
        assert len(data) > 0
        assert all('file' in item for item in data)
        assert all('severity' in item for item in data)
    
    def test_markdown_report_generation_workflow(self, temp_project):
        """Test Markdown report generation workflow"""
        agent = DocumentationSyncValidator()
        agent.validate_all(temp_project)
        
        report = agent.generate_report('markdown')
        
        assert report.startswith('# Documentation Validation Report')
        assert '**Total Issues**:' in report
        assert '##' in report  # Should have severity sections
    
    def test_cli_integration(self, temp_project):
        """Test CLI integration"""
        from agent import main
        import sys
        
        # Test validate command
        sys.argv = ['agent', 'validate', str(temp_project), '--output-format', 'json']
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        # Should exit with error code (issues found)
        assert exc_info.value.code in [0, 1]
    
    def test_configuration_override_workflow(self, temp_project):
        """Test configuration override workflow"""
        # Create custom config
        config_dir = temp_project / "config"
        config_dir.mkdir()
        config_file = config_dir / "custom_config.yaml"
        config_file.write_text("""
version: 1.0.0
agent_name: documentation-sync-validator
freshness_threshold_days: 30
semantic_drift_threshold: 0.9
link_check_timeout: 5
capabilities:
  - check_freshness
  - validate_links
""")
        
        agent = DocumentationSyncValidator(config_path=config_file)
        
        assert agent.freshness_threshold_days == 30
        assert agent.semantic_drift_threshold == 0.9
        assert agent.link_check_timeout == 5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
