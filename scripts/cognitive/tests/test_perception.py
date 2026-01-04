"""
Tests for Cognitive Brain Perception Layer
"""
import pytest
import json
from pathlib import Path
import tempfile


def test_git_data_collector():
    """Test Git data collection."""
    from scripts.cognitive.collect_git_data import collect_git_commits
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "git_data.json"
        
        # Collect data
        result = collect_git_commits("7 days ago", str(output_path))
        
        # Verify structure
        assert isinstance(result, dict)
        assert "collection_timestamp" in result
        assert "commits" in result
        assert isinstance(result["commits"], list)


def test_pattern_detection():
    """Test pattern detection."""
    from scripts.cognitive.detect_patterns import detect_patterns
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mock data
        input_dir = Path(tmpdir) / "input"
        input_dir.mkdir()
        
        mock_git_data = {
            "commits": [
                {
                    "hash": "abc123",
                    "author_name": "Test User",
                    "author_email": "test@example.com",
                    "timestamp": 1704326400,
                    "subject": "Test commit",
                    "files_changed": [
                        {"file": "test.py", "additions": 10, "deletions": 5}
                    ],
                    "additions": 10,
                    "deletions": 5
                }
            ]
        }
        
        with open(input_dir / "git_data.json", 'w') as f:
            json.dump(mock_git_data, f)
        
        output_path = Path(tmpdir) / "patterns.json"
        
        # Detect patterns
        result = detect_patterns(str(input_dir), str(output_path))
        
        # Verify structure
        assert isinstance(result, dict)
        assert "patterns_detected" in result
        assert isinstance(result["patterns_detected"], list)


def test_anomaly_detection():
    """Test anomaly detection."""
    from scripts.cognitive.detect_anomalies import detect_anomalies
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mock data
        input_dir = Path(tmpdir) / "input"
        input_dir.mkdir()
        
        mock_ci_data = {
            "metrics": {
                "total_runs": 100,
                "successful_runs": 60,
                "failed_runs": 40,
                "success_rate_percent": 60,
                "avg_duration_minutes": 45
            }
        }
        
        with open(input_dir / "ci_data.json", 'w') as f:
            json.dump(mock_ci_data, f)
        
        output_path = Path(tmpdir) / "anomalies.json"
        
        # Detect anomalies
        result = detect_anomalies(str(input_dir), str(output_path))
        
        # Verify structure
        assert isinstance(result, dict)
        assert "anomalies_detected" in result
        assert isinstance(result["anomalies_detected"], list)
        
        # Should detect low success rate anomaly
        anomaly_types = [a["anomaly_type"] for a in result["anomalies_detected"]]
        assert "low_ci_success_rate" in anomaly_types


def test_perception_report_generation():
    """Test perception report generation."""
    from scripts.cognitive.generate_perception_report import generate_perception_report
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mock data
        input_dir = Path(tmpdir) / "input"
        input_dir.mkdir()
        
        mock_data = {
            "git_data": {
                "total_commits": 10,
                "total_additions": 100,
                "total_deletions": 50,
                "unique_authors": 3,
                "since_date": "7 days ago"
            },
            "patterns": {
                "patterns_detected": [
                    {
                        "pattern_type": "test_pattern",
                        "description": "Test pattern description",
                        "confidence": 0.90,
                        "data": []
                    }
                ]
            }
        }
        
        with open(input_dir / "git_data.json", 'w') as f:
            json.dump(mock_data["git_data"], f)
        
        with open(input_dir / "patterns.json", 'w') as f:
            json.dump(mock_data["patterns"], f)
        
        output_path = Path(tmpdir) / "report.md"
        
        # Generate report
        report = generate_perception_report(str(input_dir), str(output_path))
        
        # Verify report
        assert isinstance(report, str)
        assert "Cognitive Brain - Perception Report" in report
        assert "Executive Summary" in report
        assert output_path.exists()


def test_cognitive_brain_core():
    """Test main Cognitive Brain coordinator."""
    from scripts.cognitive.cognitive_brain_core import CognitiveBrain
    
    with tempfile.TemporaryDirectory() as tmpdir:
        brain = CognitiveBrain(workspace_dir=tmpdir)
        
        # Run one cycle
        results = brain.run_pda_cycle()
        
        # Verify results
        assert isinstance(results, dict)
        assert "cycle_number" in results
        assert "stages" in results
        assert "perception" in results["stages"]
        assert "decision" in results["stages"]
        assert "action" in results["stages"]
        assert "aftermath" in results["stages"]
        assert results["overall_status"] == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
