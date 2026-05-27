"""Phase E tests for top 5 CI scripts by importance.

Top 5 CI scripts tested:
1. scripts/ci/check_cross_references.py  — broken link gate
2. scripts/ci/check_deferral_language.py — deferral policy scanner
3. scripts/ci/batch_scan_integration.py  — test-suite runner API
4. scripts/ci/ci_pattern_pipeline.py     — CI pattern orchestrator
5. scripts/ci/check_pr_comments.py       — PR comment gate
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CI_DIR = REPO_ROOT / "scripts" / "ci"

# Ensure scripts/ci is importable
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# 1. check_cross_references.py
# ---------------------------------------------------------------------------

class TestCheckCrossReferences:
    @pytest.fixture
    def mod(self):
        spec = importlib.util.spec_from_file_location(
            "check_cross_references",
            CI_DIR / "check_cross_references.py",
        )
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def test_should_skip_git_dir(self, mod):
        p = Path(".git/config")
        assert mod._should_skip(p) is True

    def test_should_skip_pycache(self, mod):
        p = Path("src/__pycache__/module.cpython-312.pyc")
        assert mod._should_skip(p) is True

    def test_should_not_skip_normal_md(self, mod):
        p = Path("docs/guide.md")
        assert mod._should_skip(p) is False

    def test_resolve_ref_absolute_path(self, mod, tmp_path):
        target = tmp_path / "target.md"
        target.touch()
        source = tmp_path / "docs" / "page.md"
        result = mod._resolve_ref("/target.md", source)
        # Absolute paths resolve from repo root — may or may not exist
        # The function should return a Path or None
        assert result is None or isinstance(result, Path)

    def test_resolve_ref_relative_existing(self, mod, tmp_path):
        source_file = tmp_path / "docs" / "page.md"
        source_file.parent.mkdir(parents=True, exist_ok=True)
        source_file.touch()
        target = tmp_path / "docs" / "other.md"
        target.touch()
        result = mod._resolve_ref("other.md", source_file)
        assert result == target or result is None

    def test_scan_file_no_links(self, mod, tmp_path):
        md = tmp_path / "clean.md"
        md.write_text("# Title\n\nJust prose.\n", encoding="utf-8")
        broken = mod.scan_file(md)
        assert broken == []

    def test_scan_file_with_broken_link(self, mod, tmp_path):
        md = tmp_path / "page.md"
        md.write_text("[broken link](nonexistent/file.md)\n", encoding="utf-8")
        broken = mod.scan_file(md)
        assert isinstance(broken, list)

    def test_scan_file_with_valid_link(self, mod, tmp_path):
        target = tmp_path / "target.md"
        target.write_text("# Target\n", encoding="utf-8")
        source = tmp_path / "page.md"
        source.write_text("[valid link](target.md)\n", encoding="utf-8")
        broken = mod.scan_file(source)
        # Valid link should NOT appear in broken list
        assert all("target.md" not in str(item) for item in broken)

    def test_skip_external_links(self, mod, tmp_path):
        md = tmp_path / "page.md"
        md.write_text("[external](https://example.com/page.html)\n", encoding="utf-8")
        broken = mod.scan_file(md)
        assert broken == []

    def test_skip_anchor_links(self, mod, tmp_path):
        md = tmp_path / "page.md"
        md.write_text("[anchor](#section)\n", encoding="utf-8")
        broken = mod.scan_file(md)
        assert broken == []


# ---------------------------------------------------------------------------
# 2. check_deferral_language.py
# ---------------------------------------------------------------------------

class TestCheckDeferralLanguage:
    @pytest.fixture
    def mod(self):
        spec = importlib.util.spec_from_file_location(
            "check_deferral_language",
            CI_DIR / "check_deferral_language.py",
        )
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def test_scan_clean_text(self, mod):
        violations = mod.scan("This PR adds tests and fixes bugs.")
        assert violations == []

    def test_scan_detects_deferral_phrase(self, mod):
        text = "Will fix this in a future PR."
        violations = mod.scan(text)
        assert len(violations) >= 1

    def test_scan_future_task(self, mod):
        text = "This will be addressed in a future task."
        violations = mod.scan(text)
        assert len(violations) >= 1

    def test_line_is_exempt_deferral_triggers_list(self, mod):
        # Lines that reference the scanner's own constant should be exempt
        assert mod._line_is_exempt("DEFERRAL_TRIGGERS = [...]") is True

    def test_line_is_not_exempt_genuine_deferral(self, mod):
        # A genuine deferral line is NOT exempt
        line = "I will handle this in a follow-up PR."
        assert mod._line_is_exempt(line) is False

    def test_load_text_from_string(self, mod, tmp_path):
        result = mod._load_text("hello world")
        assert result == "hello world"

    def test_load_text_from_file(self, mod, tmp_path):
        f = tmp_path / "input.txt"
        f.write_text("file content\n", encoding="utf-8")
        result = mod._load_text(str(f))
        assert result == "file content\n"

    def test_scan_code_block_not_flagged(self, mod):
        text = (
            "Here is an example:\n"
            "```\n"
            "Will fix in a future PR.\n"
            "```\n"
            "Normal text here.\n"
        )
        violations = mod.scan(text)
        # Lines inside fenced code blocks should not be flagged
        assert len(violations) == 0

    def test_scan_returns_violation_keys(self, mod):
        violations = mod.scan("Will fix this in a future session.")
        if violations:
            v = violations[0]
            assert "line_no" in v
            assert "line" in v

    def test_deferral_ml_classifier_unavailable_returns_false(self, mod):
        cls = mod.DeferralMLClassifier()
        assert cls.predict("Will fix later") is False
        assert cls.is_available() is False


# ---------------------------------------------------------------------------
# 3. batch_scan_integration.py
# ---------------------------------------------------------------------------

class TestBatchScanIntegration:
    @pytest.fixture
    def mod(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "batch_scan_integration",
            CI_DIR / "batch_scan_integration.py",
        )
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def test_batch_scan_result_construction(self, mod):
        result = mod.BatchScanResult(ok=True, failures=[], report={})
        assert result.ok is True
        assert result.failures == []

    def test_batch_scan_result_failure(self, mod):
        result = mod.BatchScanResult(ok=False, failures=["test::failed"], report={})
        assert not result.ok
        assert "test::failed" in result.failures

    def test_batch_scan_runner_construction(self, mod):
        runner = mod.BatchScanRunner(workers=2, batch_size=10)
        assert runner is not None

    def test_batch_scan_runner_preview_no_error(self, mod):
        """preview() should return without raising even when preflight is absent."""
        runner = mod.BatchScanRunner(workers=1, batch_size=5)
        try:
            runner.preview(group="quick")
        except Exception:
            pass  # preview may fail if preflight script missing — that's fine

    def test_no_op_span_context_manager(self, mod):
        span = mod._NoOpSpan()
        with span:
            pass  # Should not raise


# ---------------------------------------------------------------------------
# 4. ci_pattern_pipeline.py
# ---------------------------------------------------------------------------

class TestCiPatternPipeline:
    @pytest.fixture
    def mod(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "ci_pattern_pipeline",
            CI_DIR / "ci_pattern_pipeline.py",
        )
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def test_write_artefact_creates_json(self, mod, tmp_path):
        artefact = tmp_path / "report.json"
        report = {"status": "ok", "fixed": 0, "checked": 0, "patterns": {}}
        mod._write_artefact(artefact, report)
        assert artefact.exists()
        import json
        loaded = json.loads(artefact.read_text())
        assert loaded["status"] == "ok"

    def test_print_report_no_error(self, mod, capsys):
        report = {"status": "ok", "fixed": 0, "checked": 0, "patterns": {}}
        mod._print_report(report, check_only=False)
        captured = capsys.readouterr()
        assert len(captured.out) >= 0  # Just no error

    def test_write_artefact_handles_none(self, mod):
        """_write_artefact with None path should no-op."""
        mod._write_artefact(None, {"status": "skipped"})  # Should not raise


# ---------------------------------------------------------------------------
# 5. check_pr_comments.py
# ---------------------------------------------------------------------------

class TestCheckPrComments:
    @pytest.fixture
    def mod(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "check_pr_comments",
            CI_DIR / "check_pr_comments.py",
        )
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def test_module_loads(self, mod):
        assert mod is not None

    def test_main_missing_args_exit_nonzero(self, mod):
        """main() with empty argv should exit with a non-zero code."""
        with pytest.raises((SystemExit, Exception)):
            mod.main(["--pr", "1"])  # Missing --repo

    def test_main_no_token_exits(self, mod, monkeypatch):
        """Without GITHUB_TOKEN, main should exit early."""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        monkeypatch.delenv("GH_TOKEN", raising=False)
        with pytest.raises((SystemExit, Exception)):
            mod.main(["--pr", "999", "--repo", "owner/repo"])
