"""
Tests for Duplication Analyzer
"""
import pytest
import tempfile
from pathlib import Path

from tools.duplication_analyzer import DuplicationAnalyzer, ACCEPTABLE_DUP_RATIO


@pytest.fixture
def temp_project_dir():
    """Create a temporary project with some duplicate files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create some duplicate files (same stem)
        (root / "module1").mkdir()
        (root / "module2").mkdir()
        (root / "tests").mkdir()
        
        # Duplicate stems
        (root / "module1" / "utils.py").write_text("# Utils module 1")
        (root / "module2" / "utils.py").write_text("# Utils module 2")
        (root / "tests" / "utils.py").write_text("# Test utils")
        
        # Identical content
        (root / "config.yaml").write_text("key: value\n")
        (root / "config_copy.yaml").write_text("key: value\n")
        
        # Unique files
        (root / "main.py").write_text("# Main")
        (root / "README.md").write_text("# Project")
        
        yield root


class TestDuplicationAnalyzer:
    """Test duplication analyzer functionality"""
    
    def test_init(self, temp_project_dir):
        """Test initialization"""
        analyzer = DuplicationAnalyzer(temp_project_dir)
        assert analyzer.root_path == temp_project_dir
        assert analyzer.acceptable_ratio == ACCEPTABLE_DUP_RATIO
    
    def test_analyze_finds_duplicates(self, temp_project_dir):
        """Test that analyzer finds duplicate files"""
        analyzer = DuplicationAnalyzer(temp_project_dir)
        result = analyzer.analyze()
        
        assert "stats" in result
        assert result["stats"]["total_files"] >= 5
        assert result["stats"]["duplicate_count"] > 0
        assert "duplicate_groups" in result
    
    def test_analyze_calculates_ratio(self, temp_project_dir):
        """Test duplication ratio calculation"""
        analyzer = DuplicationAnalyzer(temp_project_dir)
        result = analyzer.analyze()
        
        ratio = result["stats"]["duplication_ratio"]
        assert isinstance(ratio, float)
        assert 0 <= ratio <= 1
    
    def test_severity_assessment(self, temp_project_dir):
        """Test severity assessment"""
        analyzer = DuplicationAnalyzer(temp_project_dir, acceptable_ratio=0.01)
        result = analyzer.analyze()
        
        # With low threshold, should detect severity
        severity = result["stats"]["severity"]
        assert severity in ["acceptable", "warning", "high", "critical"]
    
    def test_content_duplicates_detection(self, temp_project_dir):
        """Test detection of files with identical content"""
        analyzer = DuplicationAnalyzer(temp_project_dir)
        result = analyzer.analyze()
        
        # Should find config.yaml and config_copy.yaml as identical
        content_dups = result["content_duplicates"]
        assert len(content_dups) > 0
    
    def test_recommendations_generation(self, temp_project_dir):
        """Test that recommendations are generated"""
        analyzer = DuplicationAnalyzer(temp_project_dir)
        result = analyzer.analyze()
        
        recs = result["recommendations"]
        assert isinstance(recs, list)
        assert len(recs) > 0
    
    def test_report_generation(self, temp_project_dir):
        """Test markdown report generation"""
        analyzer = DuplicationAnalyzer(temp_project_dir)
        report = analyzer.generate_report()
        
        assert isinstance(report, str)
        assert "# Duplication Analysis Report" in report
        assert "## Summary" in report
        assert "## Recommendations" in report
    
    def test_refactoring_candidates(self, temp_project_dir):
        """Test finding refactoring candidates"""
        analyzer = DuplicationAnalyzer(temp_project_dir)
        analyzer.analyze()
        
        candidates = analyzer.find_refactoring_candidates(min_duplicates=2)
        assert isinstance(candidates, list)
        
        # Should find utils.py as a candidate (3 copies)
        utils_candidates = [c for c in candidates if c["stem"] == "utils"]
        assert len(utils_candidates) > 0
        assert utils_candidates[0]["count"] >= 2


class TestDuplicationAnalyzerEdgeCases:
    """Test edge cases"""
    
    def test_empty_directory(self):
        """Test analyzer on empty directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = DuplicationAnalyzer(Path(tmpdir))
            result = analyzer.analyze()
            
            assert result["stats"]["total_files"] == 0
            assert result["stats"]["duplication_ratio"] == 0.0
    
    def test_no_duplicates(self):
        """Test analyzer on directory with no duplicates"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            
            # Create unique files
            (root / "file1.py").write_text("# File 1")
            (root / "file2.py").write_text("# File 2")
            (root / "file3.py").write_text("# File 3")
            
            analyzer = DuplicationAnalyzer(root)
            result = analyzer.analyze()
            
            assert result["stats"]["total_files"] == 3
            assert result["stats"]["duplicate_count"] == 0
            assert result["stats"]["duplication_ratio"] == 0.0
            assert result["stats"]["severity"] == "acceptable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
