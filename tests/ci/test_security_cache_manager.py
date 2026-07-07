#!/usr/bin/env python3
"""
Unit tests for Security Cache Manager
"""

import json
import pytest
from pathlib import Path
from datetime import datetime, timezone
from scripts.ci.security_cache_manager import SecurityCacheManager


@pytest.fixture
def temp_cache_dir(tmp_path):
    """Create temporary cache directory"""
    return tmp_path / "security-cache"


@pytest.fixture
def sample_findings_json(tmp_path):
    """Create sample findings JSON"""
    findings = {
        "scan_metadata": {
            "repository": "Aries-Serpent/_codex_",
            "commit": "abc123",
            "run_id": "12345",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "summary": {
            "total_findings": 10,
            "critical_count": 2,
            "high_count": 3,
            "medium_count": 4,
            "low_count": 1,
        },
        "finding_index": [
            {
                "id": "CODEQL-CWE-79-001",
                "tool": "codeql",
                "cwe_id": "CWE-79",
                "severity": "CRITICAL",
                "file": "codex/cli.py",
                "line": 125,
            },
            {
                "id": "CODEQL-CWE-79-002",
                "tool": "codeql",
                "cwe_id": "CWE-79",
                "severity": "HIGH",
                "file": "codex/api.py",
                "line": 45,
            },
            {
                "id": "SEMGREP-CWE-22-001",
                "tool": "semgrep",
                "cwe_id": "CWE-22",
                "severity": "HIGH",
                "file": "codex/utils.py",
                "line": 78,
            },
        ],
    }
    
    json_file = tmp_path / "findings.json"
    json_file.write_text(json.dumps(findings, indent=2))
    return json_file


class TestSecurityCacheManager:
    """Test suite for SecurityCacheManager"""

    def test_cache_manager_initialization(self, temp_cache_dir):
        """Test cache manager initialization"""
        manager = SecurityCacheManager(temp_cache_dir)
        assert temp_cache_dir.exists()
        assert (temp_cache_dir / "runs").exists()
        assert (temp_cache_dir / "index.json").exists()

    def test_cache_findings(self, temp_cache_dir, sample_findings_json):
        """Test caching findings"""
        manager = SecurityCacheManager(temp_cache_dir)
        cache_path = manager.cache_findings(
            run_id="12345",
            commit_sha="abc123def",
            findings_json_path=sample_findings_json,
            repo="Aries-Serpent/_codex_",
        )

        assert cache_path is not None
        assert cache_path.exists()
        
        # Verify cache content
        cache_data = json.loads(cache_path.read_text())
        assert cache_data["metadata"]["run_id"] == "12345"
        assert cache_data["summary"]["total_findings"] == 10
        assert cache_data["summary"]["critical_count"] == 2

    def test_index_update(self, temp_cache_dir, sample_findings_json):
        """Test index file is updated"""
        manager = SecurityCacheManager(temp_cache_dir)
        manager.cache_findings(
            run_id="12345",
            commit_sha="abc123",
            findings_json_path=sample_findings_json,
        )

        index = json.loads((temp_cache_dir / "index.json").read_text())
        assert len(index["runs"]) > 0
        assert index["runs"][0]["run_id"] == "12345"

    def test_prune_old_runs(self, temp_cache_dir, sample_findings_json):
        """Test pruning of old cached runs"""
        manager = SecurityCacheManager(temp_cache_dir)

        # Cache 35 runs (exceeds MAX_CACHED_RUNS)
        for i in range(35):
            manager.cache_findings(
                run_id=f"run-{i}",
                commit_sha=f"sha-{i}",
                findings_json_path=sample_findings_json,
            )

        # Should only have 30 runs
        cache_files = list((temp_cache_dir / "runs").glob("run-*.json"))
        assert len(cache_files) <= 30

    def test_compute_trend_deltas(self, temp_cache_dir, sample_findings_json):
        """Test trend delta computation"""
        manager = SecurityCacheManager(temp_cache_dir)

        # Cache two runs
        manager.cache_findings(
            run_id="run-1",
            commit_sha="sha-1",
            findings_json_path=sample_findings_json,
        )
        manager.cache_findings(
            run_id="run-2",
            commit_sha="sha-2",
            findings_json_path=sample_findings_json,
        )

        deltas = manager.compute_trend_deltas()
        assert "new_findings" in deltas
        assert "resolved_findings" in deltas
        assert "unchanged_findings" in deltas

    def test_get_historical_findings(self, temp_cache_dir, sample_findings_json):
        """Test historical findings retrieval"""
        manager = SecurityCacheManager(temp_cache_dir)
        manager.cache_findings(
            run_id="12345",
            commit_sha="abc123",
            findings_json_path=sample_findings_json,
        )

        findings = manager.get_historical_findings("CWE-79")
        assert len(findings) > 0
        assert all(f["cwe_id"] == "CWE-79" for f in findings)

    def test_compute_aggregate_metrics(self, temp_cache_dir, sample_findings_json):
        """Test aggregate metrics computation"""
        manager = SecurityCacheManager(temp_cache_dir)
        manager.cache_findings(
            run_id="12345",
            commit_sha="abc123",
            findings_json_path=sample_findings_json,
        )

        metrics = manager.compute_aggregate_metrics()
        assert metrics.run_count >= 1
        assert metrics.total_findings > 0
        assert metrics.avg_critical >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
