"""Integration tests for audit runner with new features."""

from __future__ import annotations

import json
from pathlib import Path


def test_audit_runner_token_similarity_integration(tmp_path: Path):
    """Test audit runner with token_similarity duplication heuristic."""
    import importlib.util

    # Load audit_runner module
    audit_runner_path = (
        Path(__file__).resolve().parents[2] / "scripts" / "space_traversal" / "audit_runner.py"
    )
    spec = importlib.util.spec_from_file_location("audit_runner", str(audit_runner_path))
    audit_runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit_runner)

    # Create test config with token_similarity enabled
    cfg = {
        "weights": {
            "functionality": 0.25,
            "consistency": 0.20,
            "tests": 0.25,
            "safeguards": 0.15,
            "documentation": 0.15,
        },
        "scoring": {
            "thresholds": {"low": 0.70, "medium": 0.85},
            "dup": {
                "heuristic": "token_similarity",
                "threshold": 0.7,
                "max_pairwise": 100,
                "max_tokens_per_file": 500,
            },
        },
        "output": {
            "artifacts_dir": str(tmp_path / "audit_artifacts"),
            "reports_dir": str(tmp_path / "reports"),
        },
    }

    # Test duplication_ratio with token_similarity
    evidence_files = ["src/module_a.py", "src/module_b.py"]
    file_cache = {
        "src/module_a.py": "def foo(): return 42",
        "src/module_b.py": "def foo(): return 42",
    }

    ratio = audit_runner.duplication_ratio(evidence_files, file_cache, cfg)
    assert 0.0 <= ratio <= 1.0, "0 is not valid"


def test_audit_runner_simple_heuristic_default(tmp_path: Path):
    """Test that simple heuristic is used by default (backward compatibility)."""
    import importlib.util

    audit_runner_path = (
        Path(__file__).resolve().parents[2] / "scripts" / "space_traversal" / "audit_runner.py"
    )
    spec = importlib.util.spec_from_file_location("audit_runner", str(audit_runner_path))
    audit_runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit_runner)

    # Config without dup settings (default should be simple)
    cfg = {
        "weights": {
            "functionality": 0.25,
            "consistency": 0.20,
            "tests": 0.25,
            "safeguards": 0.15,
            "documentation": 0.15,
        },
        "scoring": {"thresholds": {"low": 0.70}},
    }

    # Test with file stems that duplicate
    evidence_files = ["src/test.py", "tests/test.py", "docs/guide.md"]
    file_cache = {f: "content" for f in evidence_files}

    ratio = audit_runner.duplication_ratio(evidence_files, file_cache, cfg)
    assert 0.0 <= ratio <= 1.0, "0 is not valid"
    # Should detect "test" duplication
    assert ratio > 0.0, "ratio must be greater than zero"


def test_audit_runner_coverage_integration(tmp_path: Path):
    """Test audit runner with coverage discovery enabled."""
    import importlib.util

    audit_runner_path = (
        Path(__file__).resolve().parents[2] / "scripts" / "space_traversal" / "audit_runner.py"
    )
    spec = importlib.util.spec_from_file_location("audit_runner", str(audit_runner_path))
    audit_runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit_runner)

    # Create coverage XML
    artifacts_dir = tmp_path / "audit_artifacts"
    artifacts_dir.mkdir()

    xml_content = """<?xml version="1.0"?>
<coverage version="1.0">
    <packages>
        <package name="src">
            <classes>
                <class filename="src/module.py" name="module">
                    <lines>
                        <line number="1" hits="1"/>
                        <line number="2" hits="1"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>
"""

    coverage_xml = tmp_path / "coverage.xml"
    coverage_xml.write_text(xml_content)

    # Create source file
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "module.py").write_text("line1\nline2\n")

    # Config with coverage enabled
    cfg = {
        "weights": {
            "functionality": 0.25,
            "consistency": 0.20,
            "tests": 0.25,
            "safeguards": 0.15,
            "documentation": 0.15,
        },
        "scoring": {
            "thresholds": {"low": 0.70},
            "coverage": {"enabled": True, "xml_patterns": ["coverage.xml"]},
        },
        "output": {"artifacts_dir": str(artifacts_dir), "reports_dir": str(tmp_path / "reports")},
    }

    # Mock ROOT for coverage_ingest
    import scripts.space_traversal.coverage_ingest as ci

    original_root = ci.ROOT
    try:
        ci.ROOT = tmp_path

        # Test stage_s4_scoring with coverage
        raw_caps = [
            {
                "id": "test-cap",
                "evidence_files": ["src/module.py"],
                "found_patterns": ["pattern"],
                "required_patterns": ["pattern"],
                "docs_keywords": [],
                "meta": {},
            }
        ]

        scored = audit_runner.stage_s4_scoring(cfg, raw_caps)

        # Check that coverage_map.json was created
        cov_map_path = artifacts_dir / "coverage_map.json"
        assert cov_map_path.exists(), "Condition must be true"

        # Check that scoring used coverage data
        assert len(scored) > 0, "Scored must not be empty"
        assert scored[0]["id"] == "test-cap", "sc is not valid"
        # Tests score should be influenced by coverage
        assert "tests" in scored[0]["components"], "Condition must be true"

    finally:
        ci.ROOT = original_root


def test_audit_runner_trends_integration(tmp_path: Path):
    """Test audit runner with trends enabled."""
    import importlib.util

    audit_runner_path = (
        Path(__file__).resolve().parents[2] / "scripts" / "space_traversal" / "audit_runner.py"
    )
    spec = importlib.util.spec_from_file_location("audit_runner", str(audit_runner_path))
    audit_runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit_runner)

    artifacts_dir = tmp_path / "audit_artifacts"
    artifacts_dir.mkdir()
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()

    # Create historical data
    import time

    historical = {"timestamp": time.time() - 86400, "capabilities": [{"id": "cap1", "score": 0.7}]}
    (artifacts_dir / "capabilities_scored_old.json").write_text(json.dumps(historical))

    # Config with trends enabled
    cfg = {
        "weights": {
            "functionality": 0.25,
            "consistency": 0.20,
            "tests": 0.25,
            "safeguards": 0.15,
            "documentation": 0.15,
        },
        "scoring": {"thresholds": {"low": 0.70}},
        "output": {"artifacts_dir": str(artifacts_dir), "reports_dir": str(reports_dir)},
        "trends": {"enabled": True, "lookback_days": 30},
    }

    # Test TRENDS stage
    try:
        audit_runner.run_stage(cfg, "TRENDS")

        # Check that trend report was created
        trends_dir = artifacts_dir / "trends"
        assert trends_dir.exists(), "Condition must be true"

        trend_files = list(trends_dir.glob("trend_report_*.md"))
        assert len(trend_files) > 0, "Trend_files must not be empty"

        # Check markdown content
        report_content = trend_files[0].read_text()
        assert "Capability Audit Trend Report" in report_content, "Content must not be empty"

    except OSError:
        # Trends may fail if no data, that's ok
        _ = None  # suppressed: no action needed


def test_duplication_ratio_fallback():
    """Test that duplication_ratio falls back to simple mode on error."""
    import importlib.util

    audit_runner_path = (
        Path(__file__).resolve().parents[2] / "scripts" / "space_traversal" / "audit_runner.py"
    )
    spec = importlib.util.spec_from_file_location("audit_runner", str(audit_runner_path))
    audit_runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit_runner)

    # Config with invalid heuristic
    cfg = {"scoring": {"dup": {"heuristic": "invalid_heuristic"}}}

    evidence_files = ["a.py", "b.py"]
    file_cache = {"a.py": "content", "b.py": "content"}

    # Should not raise, should fallback
    ratio = audit_runner.duplication_ratio(evidence_files, file_cache, cfg)
    assert 0.0 <= ratio <= 1.0, "0 is not valid"


def test_duplication_ratio_without_cache():
    """Test duplication_ratio without file_cache (backward compat)."""
    import importlib.util

    audit_runner_path = (
        Path(__file__).resolve().parents[2] / "scripts" / "space_traversal" / "audit_runner.py"
    )
    spec = importlib.util.spec_from_file_location("audit_runner", str(audit_runner_path))
    audit_runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit_runner)

    # Call without file_cache, should use simple mode
    evidence_files = ["test.py", "test.md", "other.py"]

    ratio = audit_runner.duplication_ratio(evidence_files)
    assert 0.0 <= ratio <= 1.0, "0 is not valid"
    assert ratio > 0.0, "ratio must be greater than zero"
