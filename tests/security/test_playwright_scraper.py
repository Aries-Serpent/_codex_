"""
Tests for Playwright scraper and resolution pipeline.

Covers:
- PlaywrightScraper (unit, no browser required)
- ResolutionPipeline stages (mocked subprocess + filesystem)
- Export helpers (JSON + CSV)
- CLI entry-points (argument parsing)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.parse import urlparse

import pytest

# ---------------------------------------------------------------------------
# Path bootstrap so we can import scripts directly
# ---------------------------------------------------------------------------
# NOTE: The playwright scraper lives under scripts/security and is not part of the
# installed Python package. For these tests, we temporarily prepend that directory
# to sys.path so `import playwright_scraper` works without requiring packaging or
# pytest pythonpath configuration changes. This keeps test behavior aligned with
# how the scripts are used in this repository layout.
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "security"))

# ---------------------------------------------------------------------------
# Playwright scraper tests
# ---------------------------------------------------------------------------


class TestPlaywrightScraperImportGuard:
    """Ensure module loads even when playwright is absent."""

    def test_has_playwright_false_when_missing(self, monkeypatch):
        """HAS_PLAYWRIGHT is False when import fails."""
        import playwright_scraper as ps

        monkeypatch.setattr(ps, "HAS_PLAYWRIGHT", False)
        assert ps.HAS_PLAYWRIGHT is False, "HAS_PLAYWRIGHT is not valid"

    def test_scraper_raises_import_error_without_playwright(self, monkeypatch):
        """PlaywrightScraper raises ImportError when HAS_PLAYWRIGHT is False."""
        import playwright_scraper as ps

        monkeypatch.setattr(ps, "HAS_PLAYWRIGHT", False)
        with pytest.raises(ImportError, match="playwright is not installed"):
            ps.PlaywrightScraper("https://github.com/owner/repo")


class TestExportJson:
    def test_creates_json_with_correct_structure(self, tmp_path):
        import playwright_scraper as ps

        alerts = [
            {"title": "SQL injection", "url": "/1", "severity": "high", "alert_number": 1},
            {"title": "XSS", "url": "/2", "severity": "medium", "alert_number": 2},
        ]
        out = tmp_path / "out.json"
        ps.export_json(alerts, out)

        assert out.exists(), "Condition must be true"
        data = json.loads(out.read_text())
        assert data["total_alerts"] == 2, "Data must not be empty"
        assert data["source"] == "playwright_scraper", "Data must not be empty"
        assert len(data["alerts"]) == 2, "Collection must not be empty"
        assert "exported_at" in data, "Data must not be empty"

    def test_creates_parent_dirs(self, tmp_path):
        import playwright_scraper as ps

        out = tmp_path / "a" / "b" / "alerts.json"
        ps.export_json([], out)
        assert out.exists(), "Condition must be true"


class TestExportCsv:
    def test_creates_csv_with_header(self, tmp_path):
        import playwright_scraper as ps

        alerts = [{"title": "T", "url": "U", "severity": "low", "alert_number": 1}]
        out = tmp_path / "alerts.csv"
        ps.export_csv(alerts, out)

        content = out.read_text()
        assert "alert_number" in content, "Content must not be empty"
        assert "severity" in content, "Content must not be empty"
        assert "low" in content, "Content must not be empty"

    def test_empty_alerts_writes_header_only(self, tmp_path):
        import playwright_scraper as ps

        out = tmp_path / "empty.csv"
        ps.export_csv([], out)
        assert out.exists(), "Condition must be true"
        content = out.read_text()
        assert "alert_number" in content, "Content must not be empty"


class TestPlaywrightScraperParser:
    def test_default_repo(self):
        import playwright_scraper as ps

        parser = ps.build_parser()
        args = parser.parse_args([])
        assert "Aries-Serpent" in args.repo, "Condition must be true"

    def test_custom_repo(self):
        import playwright_scraper as ps

        parser = ps.build_parser()
        args = parser.parse_args(["--repo", "https://github.com/foo/bar"])
        assert args.repo == "https://github.com/foo/bar", "repo is not valid"

    def test_headless_flag(self):
        import playwright_scraper as ps

        parser = ps.build_parser()
        args = parser.parse_args(["--no-headless"])
        assert args.headless is False, "headless is not valid"


class TestPlaywrightScraperMainNoPlaywright:
    def test_main_returns_1_without_playwright(self, monkeypatch):
        import playwright_scraper as ps

        monkeypatch.setattr(ps, "HAS_PLAYWRIGHT", False)
        with patch("sys.argv", ["ps", "--repo", "https://github.com/a/b"]):
            assert ps.main() == 1, "Condition must be true"


# ---------------------------------------------------------------------------
# Resolution pipeline tests
# ---------------------------------------------------------------------------


class TestPipelineResult:
    def test_to_dict_contains_all_keys(self):
        from resolution_pipeline import PipelineResult

        result = PipelineResult(alerts_collected=10, codemods_applied=3)
        d = result.to_dict()
        assert d["alerts_collected"] == 10, "Condition must be true"
        assert d["codemods_applied"] == 3, "Condition must be true"
        assert "elapsed_s" in d, "Condition must be true"
        assert "errors" in d, "Error should be raised or set"


class TestResolutionPipelineCollect:
    def test_collect_returns_zero_when_no_fetcher(self, tmp_path):
        """If fetch_codeql_alerts.py is absent, collect returns 0."""
        from resolution_pipeline import ResolutionPipeline

        pipeline = ResolutionPipeline(
            owner="owner",
            repo="repo",
            inventory_path=tmp_path / "inv.json",
            report_path=tmp_path / "report.md",
        )
        # _scripts_dir doesn't have the fetcher in tmp_path, so returns 0
        with patch.object(pipeline, "_collect_via_api", return_value=0):
            with patch.object(pipeline, "_collect_via_playwright", return_value=0):
                count = pipeline.collect()
        assert count == 0, "Count must be greater than zero"

    def test_collect_uses_playwright_fallback_when_api_returns_zero(self, tmp_path):
        from resolution_pipeline import ResolutionPipeline

        pipeline = ResolutionPipeline(
            owner="owner",
            repo="repo",
            inventory_path=tmp_path / "inv.json",
            report_path=tmp_path / "report.md",
            use_playwright=True,
        )
        with patch.object(pipeline, "_collect_via_api", return_value=0):
            with patch.object(pipeline, "_collect_via_playwright", return_value=42) as mock_pw:
                count = pipeline.collect()

        assert count == 42, "Count must be greater than zero"
        mock_pw.assert_called_once()

    def test_collect_skips_playwright_when_api_succeeds(self, tmp_path):
        from resolution_pipeline import ResolutionPipeline

        pipeline = ResolutionPipeline(
            owner="owner",
            repo="repo",
            inventory_path=tmp_path / "inv.json",
            report_path=tmp_path / "report.md",
            use_playwright=True,
        )
        with patch.object(pipeline, "_collect_via_api", return_value=100):
            with patch.object(pipeline, "_collect_via_playwright", return_value=0) as mock_pw:
                count = pipeline.collect()

        assert count == 100, "Count must be greater than zero"
        mock_pw.assert_not_called()


class TestResolutionPipelineAnalyse:
    def test_analyse_returns_empty_if_no_inventory(self, tmp_path):
        from resolution_pipeline import ResolutionPipeline

        pipeline = ResolutionPipeline(
            owner="owner",
            repo="repo",
            inventory_path=tmp_path / "missing.json",
            report_path=tmp_path / "report.md",
        )
        result = pipeline.analyse()
        assert result == {}, "Result must not be empty"
        assert any("inventory_missing" in e for e in pipeline.result.errors), "Result must not be empty"

    def test_analyse_loads_summary_from_inventory(self, tmp_path):
        from resolution_pipeline import ResolutionPipeline

        inventory = tmp_path / "inv.json"
        inventory.write_text(
            json.dumps(
                {
                    "total_alerts": 3,
                    "alerts": [
                        {"severity": "critical", "alert_number": 1},
                        {"severity": "high", "alert_number": 2},
                        {"severity": "low", "alert_number": 3},
                    ],
                }
            )
        )

        pipeline = ResolutionPipeline(
            owner="owner",
            repo="repo",
            inventory_path=inventory,
            report_path=tmp_path / "report.md",
        )
        # Stub out the _run call so analyze_alerts.py doesn't need to exist
        with patch.object(pipeline, "_run", return_value=0):
            summary = pipeline.analyse()

        assert summary["total"] == 3, "Condition must be true"
        assert summary["by_severity"]["critical"] == 1, "Condition must be true"
        assert summary["by_priority"]["P0"] == 1, "Condition must be true"
        assert summary["by_priority"]["P1"] == 1, "Condition must be true"


class TestResolutionPipelineRemediate:
    def test_remediate_skips_missing_codemods(self, tmp_path):
        from resolution_pipeline import ResolutionPipeline

        pipeline = ResolutionPipeline("owner", "repo")
        # All codemods are in a path that doesn't exist — should return 0
        with patch("resolution_pipeline._CODEMODS", {}):
            applied = pipeline.remediate()
        assert applied == 0, "applied is not valid"

    def test_remediate_counts_successful_codemods(self, tmp_path):
        from resolution_pipeline import ResolutionPipeline

        fake_codemod = tmp_path / "fake_fix.py"
        fake_codemod.write_text("# fake")

        pipeline = ResolutionPipeline("owner", "repo")
        with patch("resolution_pipeline._CODEMODS", {"fake": fake_codemod}):
            with patch.object(pipeline, "_run", return_value=0):
                applied = pipeline.remediate(categories=["fake"])

        assert applied == 1, "applied is not valid"
        assert pipeline.result.codemods_applied == 1, "Result must not be empty"


class TestResolutionPipelineValidate:
    def test_validate_passes_when_tools_absent(self, tmp_path):
        """Missing ruff/bandit (FileNotFoundError → exit 0) should not fail."""
        from resolution_pipeline import ResolutionPipeline

        pipeline = ResolutionPipeline("owner", "repo")
        with patch.object(pipeline, "_run", return_value=0):
            passed = pipeline.validate()

        assert passed is True, "passed is not valid"
        assert pipeline.result.validation_passed is True, "Result must not be empty"

    def test_validate_fails_when_ruff_errors(self):
        from resolution_pipeline import ResolutionPipeline

        pipeline = ResolutionPipeline("owner", "repo")

        def fake_run(cmd, label=""):
            if "ruff" in label or (isinstance(cmd, list) and "ruff" in cmd[0]):
                return 1
            return 0

        with patch.object(pipeline, "_run", side_effect=fake_run):
            passed = pipeline.validate()

        assert passed is False, "passed is not valid"
        assert "ruff_failed" in pipeline.result.errors, "Result must not be empty"


class TestResolutionPipelineClose:
    def test_close_dry_run_returns_zero(self, tmp_path):
        from resolution_pipeline import ResolutionPipeline

        pipeline = ResolutionPipeline("owner", "repo", dry_run=True)
        closed = pipeline.close_alerts(alert_numbers=[1, 2, 3])
        assert closed == 0, "closed is not valid"

    def test_close_respects_max_batch(self, tmp_path):
        from resolution_pipeline import ResolutionPipeline

        pipeline = ResolutionPipeline("owner", "repo")
        with patch.object(pipeline, "_run", return_value=0):
            with patch("resolution_pipeline._SCRIPTS_DIR", tmp_path):
                closer = tmp_path / "close_codeql_alert.py"
                closer.write_text("")
                closed = pipeline.close_alerts(alert_numbers=list(range(200)), max_batch=5)

        assert closed == 5, "closed is not valid"


class TestResolutionPipelineSeverityMapping:
    @pytest.mark.parametrize(
        "severity,expected_priority",
        [
            ("critical", "P0"),
            ("high", "P1"),
            ("medium", "P2"),
            ("low", "P3"),
            ("warning", "P4"),
            ("note", "P4"),
        ],
    )
    def test_severity_priority_mapping(self, severity, expected_priority):
        from resolution_pipeline import SEVERITY_PRIORITY

        assert SEVERITY_PRIORITY[severity] == expected_priority, "Condition must be true"


class TestResolutionPipelineRun:
    def test_run_all_stages(self, tmp_path):
        from resolution_pipeline import ResolutionPipeline

        pipeline = ResolutionPipeline(
            owner="owner",
            repo="repo",
            inventory_path=tmp_path / "inv.json",
            report_path=tmp_path / "report.md",
        )
        with patch.object(pipeline, "collect", return_value=10) as m_collect:
            with patch.object(pipeline, "analyse", return_value={}) as m_analyse:
                with patch.object(pipeline, "remediate", return_value=2) as m_remediate:
                    with patch.object(pipeline, "validate", return_value=True) as m_validate:
                        result = pipeline.run(["collect", "analyse", "remediate", "validate"])

        m_collect.assert_called_once()
        m_analyse.assert_called_once()
        m_remediate.assert_called_once()
        m_validate.assert_called_once()
        assert result.elapsed_s >= 0, "elapsed_s must be greater than zero"


class TestResolutionPipelineParser:
    def test_defaults(self):
        from resolution_pipeline import build_parser

        args = build_parser().parse_args([])
        assert args.owner == "Aries-Serpent", "owner is not valid"
        assert args.repo == "_codex_", "repo is not valid"
        assert "collect" in args.stages, "Condition must be true"

    def test_dry_run_flag(self):
        from resolution_pipeline import build_parser

        args = build_parser().parse_args(["--dry-run"])
        assert args.dry_run is True, "dry_run is not valid"

    def test_stages_parsing(self):
        from resolution_pipeline import build_parser

        args = build_parser().parse_args(["--stages", "collect,close"])
        assert "collect" in args.stages, "Condition must be true"
        assert "close" in args.stages, "Condition must be true"


class TestCountAlerts:
    def test_count_from_total_alerts_key(self, tmp_path):
        from resolution_pipeline import ResolutionPipeline

        p = tmp_path / "inv.json"
        p.write_text(json.dumps({"total_alerts": 99, "alerts": []}))
        pipeline = ResolutionPipeline("o", "r")
        assert pipeline._count_alerts(p) == 99, "Count must be greater than zero"

    def test_count_from_alerts_list(self, tmp_path):
        from resolution_pipeline import ResolutionPipeline

        p = tmp_path / "inv.json"
        p.write_text(json.dumps({"alerts": [{}, {}, {}]}))
        pipeline = ResolutionPipeline("o", "r")
        assert pipeline._count_alerts(p) == 3, "Count must be greater than zero"

    def test_count_returns_zero_on_bad_file(self, tmp_path):
        from resolution_pipeline import ResolutionPipeline

        pipeline = ResolutionPipeline("o", "r")
        assert pipeline._count_alerts(tmp_path / "nonexistent.json") == 0, "Count must be greater than zero"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# ---------------------------------------------------------------------------
# New tests — coverage gapfill for playwright_scraper.py
# ---------------------------------------------------------------------------


class TestPlaywrightScraperInit:
    """__init__ body (lines 69-73): attributes set correctly."""

    def _make(self, monkeypatch, url="https://github.com/owner/repo", **kwargs):
        import playwright_scraper as ps

        monkeypatch.setattr(ps, "HAS_PLAYWRIGHT", True)
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        return ps.PlaywrightScraper(url, **kwargs)

    def test_trailing_slash_stripped(self, monkeypatch):
        scraper = self._make(monkeypatch, url="https://github.com/owner/repo/")
        assert scraper.repo_url == "https://github.com/owner/repo", "repo_url is not valid"

    def test_no_trailing_slash_unchanged(self, monkeypatch):
        scraper = self._make(monkeypatch)
        assert scraper.repo_url == "https://github.com/owner/repo", "repo_url is not valid"

    def test_security_url_constructed(self, monkeypatch):
        scraper = self._make(monkeypatch)
        assert scraper._security_url == "https://github.com/owner/repo/security/code-scanning", "_security_url is not valid"

    def test_explicit_token_stored(self, monkeypatch):
        scraper = self._make(monkeypatch, github_token="explicit_tok")
        assert scraper.github_token == "explicit_tok", "github_token is not valid"

    def test_token_falls_back_to_env(self, monkeypatch):
        import playwright_scraper as ps

        monkeypatch.setattr(ps, "HAS_PLAYWRIGHT", True)
        monkeypatch.setenv("GITHUB_TOKEN", "env_tok_xyz")
        scraper = ps.PlaywrightScraper("https://github.com/owner/repo")
        assert scraper.github_token == "env_tok_xyz", "github_token is not valid"

    def test_no_token_and_no_env_gives_empty_string(self, monkeypatch):
        scraper = self._make(monkeypatch)
        assert scraper.github_token == "", "github_token is not valid"

    def test_default_headless_true(self, monkeypatch):
        scraper = self._make(monkeypatch, github_token="tok")
        assert scraper.headless is True, "headless is not valid"

    def test_default_timeout(self, monkeypatch):
        scraper = self._make(monkeypatch, github_token="tok")
        assert scraper.timeout_ms == 30_000, "timeout_ms is not valid"

    def test_custom_headless_and_timeout(self, monkeypatch):
        scraper = self._make(monkeypatch, github_token="tok", headless=False, timeout_ms=5_000)
        assert scraper.headless is False, "headless is not valid"
        assert scraper.timeout_ms == 5_000, "timeout_ms is not valid"


class TestAuthenticate:
    """_authenticate branch coverage — IMP-008 CDP route interception."""

    def _make_scraper(self, monkeypatch, token=""):
        import playwright_scraper as ps

        monkeypatch.setattr(ps, "HAS_PLAYWRIGHT", True)
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        return ps.PlaywrightScraper("https://github.com/owner/repo", github_token=token)

    def test_no_token_returns_false(self, monkeypatch):
        scraper = self._make_scraper(monkeypatch, token="")
        page = MagicMock()
        assert scraper._authenticate(page) is False, "Condition must be true"

    def test_token_registers_routes_returns_true(self, monkeypatch):
        """With a token, two page.route() calls are registered and True is returned."""
        scraper = self._make_scraper(monkeypatch, token="valid_token")
        page = MagicMock()

        result = scraper._authenticate(page)

        assert result is True, "Result must not be empty"
        # Verify that route interception was registered for both github.com origins.
        assert page.route.call_count == 2, "Count must be greater than zero"
        call_urls = [call[0][0] for call in page.route.call_args_list]
        assert "https://github.com/**" in call_urls, "Condition must be true"
        assert "https://api.github.com/**" in call_urls, "Condition must be true"

    def test_token_route_handler_injects_auth_header(self, monkeypatch):
        """The registered route handler merges the Authorization header."""
        scraper = self._make_scraper(monkeypatch, token="mytoken")
        page = MagicMock()

        scraper._authenticate(page)

        # Capture the route handler registered for github.com
        handler = page.route.call_args_list[0][0][1]

        # Simulate a route call with an existing header
        mock_route = MagicMock()
        mock_route.request.headers = {"Accept": "text/html"}
        handler(mock_route)

        # The handler should have merged in the Authorization header
        merged = mock_route.continue_.call_args[1]["headers"]
        assert merged["Authorization"] == "token mytoken", "Condition must be true"
        assert merged["Accept"] == "text/html", "Condition must be true"

    def test_token_status_401_still_returns_true(self, monkeypatch):
        """No longer calls requests.get — route interception returns True regardless."""
        scraper = self._make_scraper(monkeypatch, token="bad_token")
        page = MagicMock()
        result = scraper._authenticate(page)
        assert result is True, "Result must not be empty"

    def test_token_status_403_still_returns_true(self, monkeypatch):
        """No longer calls requests.get — route interception returns True regardless."""
        scraper = self._make_scraper(monkeypatch, token="limited_token")
        page = MagicMock()
        result = scraper._authenticate(page)
        assert result is True, "Result must not be empty"

    def test_route_registration_failure_returns_false(self, monkeypatch):
        """When page.route() raises, _authenticate returns False gracefully."""
        scraper = self._make_scraper(monkeypatch, token="tok")
        page = MagicMock()
        page.route.side_effect = RuntimeError("CDP unavailable")
        result = scraper._authenticate(page)
        assert result is False, "Result must not be empty"


class TestExtractRowData:
    """_extract_row_data branch coverage (lines 107-126)."""

    def _make_scraper(self, monkeypatch):
        import playwright_scraper as ps

        monkeypatch.setattr(ps, "HAS_PLAYWRIGHT", True)
        return ps.PlaywrightScraper("https://github.com/owner/repo", github_token="tok")

    def _make_row(self, href, title="Alert Title", severity_text="HIGH", has_sev=True):
        """Return a mock row element with the given attributes."""
        title_elem = MagicMock()
        title_elem.inner_text.return_value = f"  {title}  "
        title_elem.get_attribute.return_value = href

        row = MagicMock()
        if has_sev:
            sev_elem = MagicMock()
            sev_elem.inner_text.return_value = severity_text
            row.query_selector.side_effect = [title_elem, sev_elem]
        else:
            row.query_selector.side_effect = [title_elem, None]
        return row

    def test_no_title_elem_returns_none(self, monkeypatch):
        scraper = self._make_scraper(monkeypatch)
        page = MagicMock()
        row = MagicMock()
        row.query_selector.return_value = None

        assert scraper._extract_row_data(page, row) is None

    def test_href_starting_with_slash_gets_github_prefix(self, monkeypatch):
        scraper = self._make_scraper(monkeypatch)
        page = MagicMock()
        row = self._make_row(href="/owner/repo/security/code-scanning/42")

        result = scraper._extract_row_data(page, row)

        assert result is not None, "result must be initialized"
        assert result["url"] == "https://github.com/owner/repo/security/code-scanning/42", "Result must not be empty"
        assert result["title"] == "Alert Title", "Result must not be empty"
        assert result["severity"] == "high", "Result must not be empty"
        assert result["alert_number"] == 42, "Result must not be empty"

    def test_href_not_starting_with_slash_kept_as_is(self, monkeypatch):
        scraper = self._make_scraper(monkeypatch)
        page = MagicMock()
        row = self._make_row(href="https://github.com/owner/repo/security/code-scanning/7")

        result = scraper._extract_row_data(page, row)

        assert result is not None, "result must be initialized"
        assert result["url"] == "https://github.com/owner/repo/security/code-scanning/7", "Result must not be empty"
        assert result["alert_number"] == 7, "Result must not be empty"

    def test_no_severity_elem_gives_unknown(self, monkeypatch):
        scraper = self._make_scraper(monkeypatch)
        page = MagicMock()
        row = self._make_row(href="/owner/repo/security/code-scanning/1", has_sev=False)

        result = scraper._extract_row_data(page, row)

        assert result is not None, "result must be initialized"
        assert result["severity"] == "unknown", "Result must not be empty"

    def test_non_numeric_href_gives_none_alert_number(self, monkeypatch):
        scraper = self._make_scraper(monkeypatch)
        page = MagicMock()
        row = self._make_row(href="/owner/repo/security/code-scanning/abc")

        result = scraper._extract_row_data(page, row)

        assert result is not None, "result must be initialized"
        assert result["alert_number"] is None, "Result must not be empty"

    def test_severity_text_lowercased(self, monkeypatch):
        scraper = self._make_scraper(monkeypatch)
        page = MagicMock()
        row = self._make_row(href="/owner/repo/security/code-scanning/5", severity_text="CRITICAL")

        result = scraper._extract_row_data(page, row)

        assert result["severity"] == "critical", "Result must not be empty"

    def test_trailing_slash_in_href_still_parses_number(self, monkeypatch):
        scraper = self._make_scraper(monkeypatch)
        page = MagicMock()
        row = self._make_row(href="/owner/repo/security/code-scanning/99/")

        result = scraper._extract_row_data(page, row)

        assert result["alert_number"] == 99, "Result must not be empty"


class TestIterPages:
    """_iter_pages generator coverage (lines 138-189)."""

    def _make_scraper(self, monkeypatch):
        import playwright_scraper as ps

        monkeypatch.setattr(ps, "HAS_PLAYWRIGHT", True)
        return ps.PlaywrightScraper("https://github.com/owner/repo", github_token="tok")

    def _mock_page(self):
        page = MagicMock()
        page.goto.return_value = None
        page.wait_for_selector.return_value = None
        page.wait_for_load_state.return_value = None
        return page

    def test_single_page_rows_no_next(self, monkeypatch):
        """Rows present, no next button → single yielded batch."""
        scraper = self._make_scraper(monkeypatch)
        page = self._mock_page()

        alert_data = {"title": "T", "url": "U", "severity": "high", "alert_number": 1}
        row = MagicMock()
        page.query_selector_all.return_value = [row]
        page.query_selector.return_value = None  # no next button

        with (
            patch("time.sleep"),
            patch.object(scraper, "_extract_row_data", return_value=alert_data),
        ):
            results = list(scraper._iter_pages(page))

        assert len(results) == 1, "Results must not be empty"
        assert results[0] == [alert_data], "Result must not be empty"

    def test_single_page_rows_extract_returns_none_filtered(self, monkeypatch):
        """Rows present but _extract_row_data returns None → empty batch yielded."""
        scraper = self._make_scraper(monkeypatch)
        page = self._mock_page()

        row = MagicMock()
        page.query_selector_all.return_value = [row]
        page.query_selector.return_value = None

        with patch("time.sleep"), patch.object(scraper, "_extract_row_data", return_value=None):
            results = list(scraper._iter_pages(page))

        assert len(results) == 1, "Results must not be empty"
        assert results[0] == [], "Result must not be empty"

    def test_no_rows_links_present_no_next(self, monkeypatch):
        """No rows, fallback links present, no next → link-based batch yielded."""
        scraper = self._make_scraper(monkeypatch)
        page = self._mock_page()

        lnk = MagicMock()
        lnk.inner_text.return_value = " Link Alert "
        lnk.get_attribute.return_value = "/owner/repo/security/code-scanning/55"

        # _find_alert_rows tries each of the 4 _ALERT_SELECTORS in order;
        # all return empty → falls through to the link-based fallback query.
        page.query_selector_all.side_effect = [[], [], [], [], [lnk]]
        page.query_selector.return_value = None  # no next button

        with patch("time.sleep"):
            results = list(scraper._iter_pages(page))

        assert len(results) == 1, "Results must not be empty"
        batch = results[0]
        assert len(batch) == 1, "Batch must not be empty"
        assert batch[0]["title"] == "Link Alert", "Condition must be true"
        assert batch[0]["alert_number"] == 55, "Condition must be true"
        assert batch[0]["severity"] == "unknown", "Condition must be true"
        assert urlparse(batch[0]["url"]).hostname == "github.com", "hostname is not valid"

    def test_no_rows_no_links_stops_immediately(self, monkeypatch):
        """No rows and no links → generator yields nothing."""
        scraper = self._make_scraper(monkeypatch)
        page = self._mock_page()

        page.query_selector_all.return_value = []  # used for both rows and links
        page.query_selector.return_value = None

        with patch("time.sleep"):
            results = list(scraper._iter_pages(page))

        assert results == [], "Result must not be empty"

    def test_next_btn_without_disabled_paginates(self, monkeypatch):
        """next_btn present and not disabled → click + wait; second page has no next."""
        scraper = self._make_scraper(monkeypatch)
        page = self._mock_page()

        alert_data = {"title": "T", "url": "U", "severity": "high", "alert_number": 1}
        row = MagicMock()

        # rows returned on both iterations
        page.query_selector_all.side_effect = [[row], [row]]

        mock_next_btn = MagicMock()
        mock_next_btn.get_attribute.return_value = "next-page"  # no "disabled"
        # next_btn on first iteration, None on second
        page.query_selector.side_effect = [mock_next_btn, None]

        with (
            patch("time.sleep"),
            patch.object(scraper, "_extract_row_data", return_value=alert_data),
        ):
            results = list(scraper._iter_pages(page))

        assert len(results) == 2, "Results must not be empty"
        mock_next_btn.click.assert_called_once()
        page.wait_for_load_state.assert_called_once_with("networkidle", timeout=scraper.timeout_ms)

    def test_next_btn_with_disabled_class_stops(self, monkeypatch):
        """next_btn present but has 'disabled' class → stop after first page."""
        scraper = self._make_scraper(monkeypatch)
        page = self._mock_page()

        alert_data = {"title": "T", "url": "U", "severity": "high", "alert_number": 1}
        row = MagicMock()
        page.query_selector_all.return_value = [row]

        mock_next_btn = MagicMock()
        mock_next_btn.get_attribute.return_value = "next_page disabled"
        page.query_selector.return_value = mock_next_btn

        with (
            patch("time.sleep"),
            patch.object(scraper, "_extract_row_data", return_value=alert_data),
        ):
            results = list(scraper._iter_pages(page))

        assert len(results) == 1, "Results must not be empty"
        mock_next_btn.click.assert_not_called()

    def test_link_with_non_numeric_tail_gives_none_alert_number(self, monkeypatch):
        """Link href ending in non-digit → alert_number=None."""
        scraper = self._make_scraper(monkeypatch)
        page = self._mock_page()

        lnk = MagicMock()
        lnk.inner_text.return_value = "Alert"
        lnk.get_attribute.return_value = "/owner/repo/security/code-scanning/abc"

        # _find_alert_rows tries each of the 4 _ALERT_SELECTORS; all return empty.
        page.query_selector_all.side_effect = [[], [], [], [], [lnk]]
        page.query_selector.return_value = None

        with patch("time.sleep"):
            results = list(scraper._iter_pages(page))

        assert results[0][0]["alert_number"] is None, "Result must not be empty"


class TestScrape:
    """scrape() context-manager flow (lines 196-217)."""

    def _make_scraper(self, monkeypatch, token="tok"):
        import playwright_scraper as ps

        monkeypatch.setattr(ps, "HAS_PLAYWRIGHT", True)
        return ps.PlaywrightScraper("https://github.com/owner/repo", github_token=token)

    def _mock_sync_playwright(self):
        """Return (callable, pw_mock): callable() is the context manager."""
        mock_pw = MagicMock()
        mock_browser = MagicMock()
        mock_ctx = MagicMock()
        mock_page = MagicMock()

        mock_pw.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_ctx
        mock_ctx.new_page.return_value = mock_page

        mock_cm = MagicMock()
        mock_cm.__enter__ = MagicMock(return_value=mock_pw)
        mock_cm.__exit__ = MagicMock(return_value=False)

        mock_sp = MagicMock(return_value=mock_cm)
        return mock_sp, mock_pw, mock_browser, mock_page

    def test_scrape_returns_list(self, monkeypatch):
        import playwright_scraper as ps

        scraper = self._make_scraper(monkeypatch)

        mock_sp, _mock_pw, _mock_browser, _mock_page = self._mock_sync_playwright()
        expected = [{"title": "T", "url": "U", "severity": "high", "alert_number": 1}]

        monkeypatch.setattr(ps, "sync_playwright", mock_sp, raising=False)
        with (
            patch.object(scraper, "_authenticate", return_value=True),
            patch.object(scraper, "_iter_pages", return_value=iter([expected])),
        ):
            result = scraper.scrape()

        assert isinstance(result, list)
        assert result == expected, "Result must not be empty"

    def test_scrape_calls_browser_close_on_success(self, monkeypatch):
        import playwright_scraper as ps

        scraper = self._make_scraper(monkeypatch)

        mock_sp, _mock_pw, mock_browser, _mock_page = self._mock_sync_playwright()

        monkeypatch.setattr(ps, "sync_playwright", mock_sp, raising=False)
        with (
            patch.object(scraper, "_authenticate", return_value=False),
            patch.object(scraper, "_iter_pages", return_value=iter([])),
        ):
            scraper.scrape()

        mock_browser.close.assert_called_once()

    def test_scrape_calls_browser_close_on_exception(self, monkeypatch):
        """browser.close() is called even when _iter_pages raises."""
        import playwright_scraper as ps

        scraper = self._make_scraper(monkeypatch)

        mock_sp, _mock_pw, mock_browser, _mock_page = self._mock_sync_playwright()

        monkeypatch.setattr(ps, "sync_playwright", mock_sp, raising=False)
        with (
            patch.object(scraper, "_authenticate", return_value=True),
            patch.object(
                scraper, "_iter_pages", side_effect=RuntimeError("scrape iteration failed")
            ),
        ):
            with pytest.raises(RuntimeError, match="scrape iteration failed"):
                scraper.scrape()

        mock_browser.close.assert_called_once()

    def test_scrape_aggregates_multiple_pages(self, monkeypatch):
        import playwright_scraper as ps

        scraper = self._make_scraper(monkeypatch)

        mock_sp, _mock_pw, _mock_browser, _mock_page = self._mock_sync_playwright()

        page1 = [{"title": "A", "url": "U1", "severity": "high", "alert_number": 1}]
        page2 = [{"title": "B", "url": "U2", "severity": "low", "alert_number": 2}]

        monkeypatch.setattr(ps, "sync_playwright", mock_sp, raising=False)
        with (
            patch.object(scraper, "_authenticate", return_value=True),
            patch.object(scraper, "_iter_pages", return_value=iter([page1, page2])),
        ):
            result = scraper.scrape()

        assert len(result) == 2, "Result must not be empty"
        assert result[0]["title"] == "A", "Result must not be empty"
        assert result[1]["title"] == "B", "Result must not be empty"

    def test_scrape_headless_passed_to_launch(self, monkeypatch):
        import playwright_scraper as ps

        monkeypatch.setattr(ps, "HAS_PLAYWRIGHT", True)
        scraper = ps.PlaywrightScraper(
            "https://github.com/owner/repo", github_token="tok", headless=False
        )
        mock_sp, mock_pw, _mock_browser, _mock_page = self._mock_sync_playwright()

        monkeypatch.setattr(ps, "sync_playwright", mock_sp, raising=False)
        with (
            patch.object(scraper, "_authenticate", return_value=False),
            patch.object(scraper, "_iter_pages", return_value=iter([])),
        ):
            scraper.scrape()

        mock_pw.chromium.launch.assert_called_once_with(
            headless=False, args=["--disable-extensions"]
        )


class TestMainWithPlaywright:
    """main() function coverage (lines 304-328)."""

    def test_main_success_returns_0(self, monkeypatch, tmp_path):
        import playwright_scraper as ps

        monkeypatch.setattr(ps, "HAS_PLAYWRIGHT", True)

        alerts = [{"title": "T", "url": "U", "severity": "high", "alert_number": 1}]
        out = tmp_path / "out.json"

        with (
            patch("sys.argv", ["ps", "--repo", "https://github.com/a/b", "--output", str(out)]),
            patch.object(ps.PlaywrightScraper, "scrape", return_value=alerts),
        ):
            result = ps.main()

        assert result == 0, "Result must not be empty"
        assert out.exists(), "Condition must be true"

    def test_main_with_csv_writes_csv(self, monkeypatch, tmp_path):
        import playwright_scraper as ps

        monkeypatch.setattr(ps, "HAS_PLAYWRIGHT", True)

        alerts = [{"title": "T", "url": "U", "severity": "high", "alert_number": 1}]
        out = tmp_path / "out.json"
        csv_out = tmp_path / "out.csv"

        with (
            patch(
                "sys.argv",
                [
                    "ps",
                    "--repo",
                    "https://github.com/a/b",
                    "--output",
                    str(out),
                    "--csv",
                    str(csv_out),
                ],
            ),
            patch.object(ps.PlaywrightScraper, "scrape", return_value=alerts),
        ):
            result = ps.main()

        assert result == 0, "Result must not be empty"
        assert csv_out.exists(), "Condition must be true"
        content = csv_out.read_text()
        assert "severity" in content, "Content must not be empty"
        assert "high" in content, "Content must not be empty"

    def test_main_scrape_exception_returns_1(self, monkeypatch, tmp_path):
        import playwright_scraper as ps

        monkeypatch.setattr(ps, "HAS_PLAYWRIGHT", True)

        out = tmp_path / "out.json"

        with (
            patch("sys.argv", ["ps", "--repo", "https://github.com/a/b", "--output", str(out)]),
            patch.object(ps.PlaywrightScraper, "scrape", side_effect=Exception("browser crashed")),
        ):
            result = ps.main()

        assert result == 1, "Result must not be empty"

    def test_main_no_playwright_returns_1(self, monkeypatch):
        import playwright_scraper as ps

        monkeypatch.setattr(ps, "HAS_PLAYWRIGHT", False)

        with patch("sys.argv", ["ps"]):
            result = ps.main()

        assert result == 1, "Result must not be empty"

    def test_main_custom_token_and_timeout(self, monkeypatch, tmp_path):
        import playwright_scraper as ps

        monkeypatch.setattr(ps, "HAS_PLAYWRIGHT", True)

        out = tmp_path / "out.json"
        captured = {}

        def fake_init(self, *args, **kwargs):
            # Capture arguments without invoking the real initializer to avoid side effects.
            captured["token"] = kwargs.get("github_token")
            captured["timeout"] = kwargs.get("timeout_ms", 30_000)

        with (
            patch(
                "sys.argv",
                [
                    "ps",
                    "--repo",
                    "https://github.com/a/b",
                    "--output",
                    str(out),
                    "--token",
                    "my_secret_tok",
                    "--timeout",
                    "5000",
                ],
            ),
            patch.object(ps.PlaywrightScraper, "__init__", fake_init),
            patch.object(ps.PlaywrightScraper, "scrape", return_value=[]),
        ):
            result = ps.main()

        assert result == 0, "Result must not be empty"
        assert captured["token"] == "my_secret_tok", "Condition must be true"
        assert captured["timeout"] == 5000, "Condition must be true"


# ---------------------------------------------------------------------------
# Coverage gapfill — resolution_pipeline.py
# ---------------------------------------------------------------------------


class TestCollectViaApi:
    """Lines 147-167: _collect_via_api success and failure paths."""

    def test_api_fetcher_success_returns_alert_count(self, tmp_path):
        """Fetcher exists and _run returns 0 → reads inventory count."""
        import resolution_pipeline as rp

        inventory = tmp_path / "inv.json"
        inventory.write_text(
            json.dumps(
                {
                    "total_alerts": 7,
                    "alerts": [{} for _ in range(7)],
                }
            )
        )
        (tmp_path / "fetch_codeql_alerts.py").write_text("# fake")

        pipeline = rp.ResolutionPipeline(
            "owner",
            "repo",
            inventory_path=inventory,
            report_path=tmp_path / "report.md",
        )
        with (
            patch("resolution_pipeline._SCRIPTS_DIR", tmp_path),
            patch.object(pipeline, "_run", return_value=0),
        ):
            count = pipeline._collect_via_api()

        assert count == 7, "Count must be greater than zero"

    def test_api_fetcher_failure_returns_zero(self, tmp_path):
        """Fetcher exists but _run returns 1 → returns 0."""
        import resolution_pipeline as rp

        (tmp_path / "fetch_codeql_alerts.py").write_text("# fake")

        pipeline = rp.ResolutionPipeline(
            "owner",
            "repo",
            inventory_path=tmp_path / "inv.json",
            report_path=tmp_path / "report.md",
        )
        with (
            patch("resolution_pipeline._SCRIPTS_DIR", tmp_path),
            patch.object(pipeline, "_run", return_value=1),
        ):
            count = pipeline._collect_via_api()

        assert count == 0, "Count must be greater than zero"

    def test_api_includes_token_in_cmd_when_set(self, tmp_path):
        """Token is appended to the command when self.token is truthy."""
        import resolution_pipeline as rp

        inventory = tmp_path / "inv.json"
        inventory.write_text(json.dumps({"total_alerts": 1, "alerts": [{}]}))
        (tmp_path / "fetch_codeql_alerts.py").write_text("# fake")

        captured: list = []

        pipeline = rp.ResolutionPipeline(
            "owner",
            "repo",
            token="mytoken",
            inventory_path=inventory,
        )
        with (
            patch("resolution_pipeline._SCRIPTS_DIR", tmp_path),
            patch.object(
                pipeline, "_run", side_effect=lambda cmd, label="": captured.append(cmd) or 0
            ),
        ):
            pipeline._collect_via_api()

        assert any("--token" in cmd and "mytoken" in cmd for cmd in captured), "Condition must be true"


class TestCollectViaPlaywright:
    """Lines 171-195: _collect_via_playwright success and failure paths."""

    def test_playwright_success_copies_output_to_inventory(self, tmp_path):
        """Scraper exists, _run=0, pw-output file present, no existing inventory
        → copies file and returns alert count."""
        import resolution_pipeline as rp

        pw_out = tmp_path / "pw_alerts.json"
        alerts = [{"severity": "high", "alert_number": i} for i in range(5)]
        pw_out.write_text(json.dumps({"total_alerts": 5, "alerts": alerts}))

        inventory = tmp_path / "inv.json"
        (tmp_path / "playwright_scraper.py").write_text("# fake")

        pipeline = rp.ResolutionPipeline(
            "owner",
            "repo",
            inventory_path=inventory,
        )
        with (
            patch("resolution_pipeline._SCRIPTS_DIR", tmp_path),
            patch("resolution_pipeline._DEFAULT_PLAYWRIGHT_OUT", pw_out),
            patch.object(pipeline, "_run", return_value=0),
        ):
            count = pipeline._collect_via_playwright()

        assert count == 5, "Count must be greater than zero"
        assert inventory.exists(), "invent is not valid"

    def test_playwright_failure_returns_zero(self, tmp_path):
        """Scraper exists but _run returns 1 → returns 0."""
        import resolution_pipeline as rp

        (tmp_path / "playwright_scraper.py").write_text("# fake")

        pipeline = rp.ResolutionPipeline(
            "owner",
            "repo",
            inventory_path=tmp_path / "inv.json",
        )
        with (
            patch("resolution_pipeline._SCRIPTS_DIR", tmp_path),
            patch.object(pipeline, "_run", return_value=1),
        ):
            count = pipeline._collect_via_playwright()

        assert count == 0, "Count must be greater than zero"

    def test_playwright_scraper_missing_returns_zero(self, tmp_path):
        """playwright_scraper.py absent → returns 0 immediately."""
        import resolution_pipeline as rp

        # No playwright_scraper.py created in tmp_path
        pipeline = rp.ResolutionPipeline("owner", "repo")
        with patch("resolution_pipeline._SCRIPTS_DIR", tmp_path):
            count = pipeline._collect_via_playwright()

        assert count == 0, "Count must be greater than zero"


class TestAnalyseUncoveredPaths:
    """Lines 212-213, 234-235: analyse() branches not hit by existing tests."""

    def test_analyse_returns_empty_when_analyser_missing(self, tmp_path):
        """Lines 212-213: analyser script not found → returns {} immediately."""
        import resolution_pipeline as rp

        # tmp_path has no analyze_alerts.py
        pipeline = rp.ResolutionPipeline(
            "owner",
            "repo",
            inventory_path=tmp_path / "inv.json",
            report_path=tmp_path / "report.md",
        )
        with patch("resolution_pipeline._SCRIPTS_DIR", tmp_path):
            result = pipeline.analyse()

        assert result == {}, "Result must not be empty"
        # No "inventory_missing" error — we exited before checking inventory
        assert not any("inventory_missing" in e for e in pipeline.result.errors), "Result must not be empty"

    def test_analyse_records_error_on_nonzero_run_exit(self, tmp_path):
        """Lines 234-235: _run returns 1 → error appended, summary is empty."""
        import resolution_pipeline as rp

        inventory = tmp_path / "inv.json"
        inventory.write_text(json.dumps({"total_alerts": 2, "alerts": []}))
        analyser = tmp_path / "analyze_alerts.py"
        analyser.write_text("# fake")

        pipeline = rp.ResolutionPipeline(
            "owner",
            "repo",
            inventory_path=inventory,
            report_path=tmp_path / "report.md",
        )
        with (
            patch("resolution_pipeline._SCRIPTS_DIR", tmp_path),
            patch.object(pipeline, "_run", return_value=1),
        ):
            result = pipeline.analyse()

        assert result == {}, "Result must not be empty"
        assert "analysis_exit_1" in pipeline.result.errors, "Result must not be empty"


class TestLoadAnalysisSummaryException:
    """Lines 257-259: _load_analysis_summary exception path."""

    def test_returns_empty_dict_on_bad_json(self, tmp_path):
        import resolution_pipeline as rp

        inventory = tmp_path / "inv.json"
        inventory.write_text("not valid json {{{")

        pipeline = rp.ResolutionPipeline("owner", "repo", inventory_path=inventory)
        result = pipeline._load_analysis_summary()

        assert result == {}, "Result must not be empty"


class TestRemediateUncoveredPaths:
    """Lines 284-285, 287-288, 293, 300-301."""

    def test_unknown_category_is_skipped(self):
        """Lines 284-285: codemod name absent from _CODEMODS dict."""
        import resolution_pipeline as rp

        pipeline = rp.ResolutionPipeline("owner", "repo")
        with patch("resolution_pipeline._CODEMODS", {}):
            applied = pipeline.remediate(categories=["totally_unknown"])
        assert applied == 0, "applied is not valid"

    def test_registered_but_missing_file_is_skipped(self, tmp_path):
        """Lines 287-288: codemod registered but file path doesn't exist."""
        import resolution_pipeline as rp

        nonexistent = tmp_path / "nonexistent_codemod.py"
        # Do NOT create the file

        pipeline = rp.ResolutionPipeline("owner", "repo")
        with patch("resolution_pipeline._CODEMODS", {"ghost": nonexistent}):
            applied = pipeline.remediate(categories=["ghost"])

        assert applied == 0, "applied is not valid"
        assert pipeline.result.codemods_failed == 0, "Result must not be empty"

    def test_dry_run_appends_flag_to_cmd(self, tmp_path):
        """Line 293: dry_run=True → --dry-run is included in the subprocess cmd."""
        import resolution_pipeline as rp

        fake_codemod = tmp_path / "fix.py"
        fake_codemod.write_text("# fake")

        captured: list = []
        pipeline = rp.ResolutionPipeline("owner", "repo", dry_run=True)

        with (
            patch("resolution_pipeline._CODEMODS", {"myfix": fake_codemod}),
            patch.object(
                pipeline, "_run", side_effect=lambda cmd, label="": captured.append(cmd) or 0
            ),
        ):
            pipeline.remediate(categories=["myfix"])

        assert captured, "Expected _run to be called"
        assert "--dry-run" in captured[0], "Condition must be true"

    def test_failed_codemod_increments_counter(self, tmp_path):
        """Lines 300-301: _run returns 1 → codemods_failed incremented."""
        import resolution_pipeline as rp

        fake_codemod = tmp_path / "fix.py"
        fake_codemod.write_text("# fake")

        pipeline = rp.ResolutionPipeline("owner", "repo")
        with (
            patch("resolution_pipeline._CODEMODS", {"myfix": fake_codemod}),
            patch.object(pipeline, "_run", return_value=1),
        ):
            applied = pipeline.remediate(categories=["myfix"])

        assert applied == 0, "applied is not valid"
        assert pipeline.result.codemods_failed == 1, "Result must not be empty"


class TestValidateBanditFailure:
    """Lines 337-339: bandit exits with code 2 → validation fails."""

    def test_bandit_high_severity_causes_failure(self):
        import resolution_pipeline as rp

        pipeline = rp.ResolutionPipeline("owner", "repo")

        def fake_run(cmd, label=""):
            if label == "ruff":
                return 0
            if label == "bandit":
                return 2  # anything not in (0, None, 1) is failure
            return 0

        with patch.object(pipeline, "_run", side_effect=fake_run):
            passed = pipeline.validate()

        assert passed is False, "passed is not valid"
        assert "bandit_high_severity" in pipeline.result.errors, "Result must not be empty"
        assert pipeline.result.validation_passed is False, "Result must not be empty"


class TestCloseAlertsUncoveredPaths:
    """Lines 379-380, 383, 395→398, 401."""

    def test_closer_missing_returns_zero(self, tmp_path):
        """Lines 379-380: close_codeql_alert.py not found → returns 0."""
        import resolution_pipeline as rp

        # No closer file in tmp_path
        pipeline = rp.ResolutionPipeline("owner", "repo")
        with patch("resolution_pipeline._SCRIPTS_DIR", tmp_path):
            closed = pipeline.close_alerts(alert_numbers=[1, 2])

        assert closed == 0, "closed is not valid"

    def test_none_alert_numbers_resolves_p0_p1_from_inventory(self, tmp_path):
        """Line 383: alert_numbers=None → _resolve_p0_p1_alerts() provides them."""
        import resolution_pipeline as rp

        inventory = tmp_path / "inv.json"
        inventory.write_text(
            json.dumps(
                {
                    "total_alerts": 3,
                    "alerts": [
                        {"severity": "critical", "alert_number": 10},
                        {"severity": "high", "alert_number": 20},
                        {"severity": "low", "alert_number": 30},
                    ],
                }
            )
        )
        closer = tmp_path / "close_codeql_alert.py"
        closer.write_text("# fake")

        pipeline = rp.ResolutionPipeline(
            "owner",
            "repo",
            inventory_path=inventory,
        )
        with (
            patch("resolution_pipeline._SCRIPTS_DIR", tmp_path),
            patch.object(pipeline, "_run", return_value=0),
        ):
            closed = pipeline.close_alerts()  # alert_numbers=None

        # Only critical (P0) and high (P1) → 2 closed
        assert closed == 2, "closed is not valid"

    def test_token_included_in_close_cmd(self, tmp_path):
        """Lines 395→398: when token is set, --token is appended to cmd."""
        import resolution_pipeline as rp

        closer = tmp_path / "close_codeql_alert.py"
        closer.write_text("# fake")

        captured: list = []
        pipeline = rp.ResolutionPipeline("owner", "repo", token="secret_tok")

        with (
            patch("resolution_pipeline._SCRIPTS_DIR", tmp_path),
            patch.object(
                pipeline, "_run", side_effect=lambda cmd, label="": captured.append(list(cmd)) or 0
            ),
        ):
            pipeline.close_alerts(alert_numbers=[99])

        assert captured, "Expected _run to be called"
        assert "--token" in captured[0], "Condition must be true"
        assert "secret_tok" in captured[0], "Condition must be true"

    def test_failed_close_increments_no_closed_count(self, tmp_path):
        """Line 401: _run returns 1 → alert not counted as closed."""
        import resolution_pipeline as rp

        closer = tmp_path / "close_codeql_alert.py"
        closer.write_text("# fake")

        pipeline = rp.ResolutionPipeline("owner", "repo")
        with (
            patch("resolution_pipeline._SCRIPTS_DIR", tmp_path),
            patch.object(pipeline, "_run", return_value=1),
        ):
            closed = pipeline.close_alerts(alert_numbers=[1])

        assert closed == 0, "closed is not valid"
        assert pipeline.result.alerts_closed == 0, "Result must not be empty"


class TestResolveP0P1Alerts:
    """Lines 409-418: _resolve_p0_p1_alerts coverage."""

    def test_returns_only_critical_and_high_alert_numbers(self, tmp_path):
        import resolution_pipeline as rp

        inventory = tmp_path / "inv.json"
        inventory.write_text(
            json.dumps(
                {
                    "alerts": [
                        {"severity": "critical", "alert_number": 10},
                        {"severity": "high", "alert_number": 20},
                        {"severity": "medium", "alert_number": 30},
                        {"severity": "low", "alert_number": 40},
                    ],
                }
            )
        )
        pipeline = rp.ResolutionPipeline("owner", "repo", inventory_path=inventory)
        result = pipeline._resolve_p0_p1_alerts()

        assert 10 in result, "Result must not be empty"
        assert 20 in result, "Result must not be empty"
        assert 30 not in result, "Result must not be empty"
        assert 40 not in result, "Result must not be empty"

    def test_excludes_entries_with_null_alert_number(self, tmp_path):
        import resolution_pipeline as rp

        inventory = tmp_path / "inv.json"
        inventory.write_text(
            json.dumps(
                {
                    "alerts": [
                        {"severity": "critical", "alert_number": None},
                        {"severity": "high", "alert_number": 5},
                    ],
                }
            )
        )
        pipeline = rp.ResolutionPipeline("owner", "repo", inventory_path=inventory)
        result = pipeline._resolve_p0_p1_alerts()

        assert None not in result, "Result must not be empty"
        assert 5 in result, "Result must not be empty"

    def test_returns_empty_list_when_inventory_missing(self, tmp_path):
        import resolution_pipeline as rp

        pipeline = rp.ResolutionPipeline(
            "owner",
            "repo",
            inventory_path=tmp_path / "missing.json",
        )
        result = pipeline._resolve_p0_p1_alerts()

        assert result == [], "Result must not be empty"

    def test_returns_empty_list_when_inventory_bad_json(self, tmp_path):
        import resolution_pipeline as rp

        inventory = tmp_path / "inv.json"
        inventory.write_text("{ bad json !!!")

        pipeline = rp.ResolutionPipeline("owner", "repo", inventory_path=inventory)
        result = pipeline._resolve_p0_p1_alerts()

        assert result == [], "Result must not be empty"


class TestRunMethod:
    """Lines 426-443: _run subprocess helper."""

    def test_real_echo_returns_zero_and_logs_stdout(self):
        import resolution_pipeline as rp

        pipeline = rp.ResolutionPipeline("owner", "repo")
        ret = pipeline._run(["echo", "hello from test"], label="echo-test")

        assert ret == 0, "ret is not valid"

    def test_real_stderr_command_returns_zero(self):
        import resolution_pipeline as rp

        pipeline = rp.ResolutionPipeline("owner", "repo")
        ret = pipeline._run(
            [sys.executable, "-c", "import sys; sys.stderr.write('stderr line\\n')"],
            label="stderr-test",
        )
        assert ret == 0, "ret is not valid"

    def test_nonexistent_command_returns_zero(self):
        """Lines 441-443: FileNotFoundError → returns 0 (non-blocking)."""
        import resolution_pipeline as rp

        pipeline = rp.ResolutionPipeline("owner", "repo")
        ret = pipeline._run(["__nonexistent_cmd_xyz_99__"], label="missing-tool")

        assert ret == 0, "ret is not valid"

    def test_failing_command_returns_nonzero(self):
        """_run propagates the real exit code on subprocess failure."""
        import resolution_pipeline as rp

        pipeline = rp.ResolutionPipeline("owner", "repo")
        ret = pipeline._run(
            [sys.executable, "-c", "import sys; sys.exit(3)"],
            label="exit-3",
        )
        assert ret == 3, "ret is not valid"


class TestRunStageAliases:
    """Lines 462→465, 465→468, 468→471, 471→474, 475: stage name aliases in run()."""

    def test_analyze_alias_calls_analyse(self):
        """'analyze' (US spelling) triggers self.analyse()."""
        import resolution_pipeline as rp

        pipeline = rp.ResolutionPipeline("owner", "repo")
        with (
            patch.object(pipeline, "collect") as m_collect,
            patch.object(pipeline, "analyse") as m_analyse,
            patch.object(pipeline, "remediate") as m_remediate,
            patch.object(pipeline, "validate") as m_validate,
            patch.object(pipeline, "close_alerts") as m_close,
        ):
            pipeline.run(["analyze"])

        m_analyse.assert_called_once()
        m_collect.assert_not_called()
        m_remediate.assert_not_called()
        m_validate.assert_not_called()
        m_close.assert_not_called()

    def test_fix_alias_calls_remediate(self):
        """'fix' triggers self.remediate()."""
        import resolution_pipeline as rp

        pipeline = rp.ResolutionPipeline("owner", "repo")
        with (
            patch.object(pipeline, "collect") as m_collect,
            patch.object(pipeline, "analyse") as m_analyse,
            patch.object(pipeline, "remediate") as m_remediate,
            patch.object(pipeline, "validate") as m_validate,
            patch.object(pipeline, "close_alerts") as m_close,
        ):
            pipeline.run(["fix"])

        m_remediate.assert_called_once()
        m_collect.assert_not_called()
        m_analyse.assert_not_called()
        m_validate.assert_not_called()
        m_close.assert_not_called()

    def test_close_stage_calls_close_alerts(self):
        """'close' triggers self.close_alerts()."""
        import resolution_pipeline as rp

        pipeline = rp.ResolutionPipeline("owner", "repo")
        with (
            patch.object(pipeline, "collect") as m_collect,
            patch.object(pipeline, "analyse") as m_analyse,
            patch.object(pipeline, "remediate") as m_remediate,
            patch.object(pipeline, "validate") as m_validate,
            patch.object(pipeline, "close_alerts") as m_close,
        ):
            pipeline.run(["close"])

        m_close.assert_called_once()
        m_collect.assert_not_called()
        m_analyse.assert_not_called()
        m_remediate.assert_not_called()
        m_validate.assert_not_called()


class TestMainFunction:
    """Lines 545-581: main() entry-point coverage."""

    def test_main_returns_0_when_no_errors(self):
        import resolution_pipeline as rp

        with (
            patch("sys.argv", ["rp", "--owner", "o", "--repo", "r", "--stages", "collect"]),
            patch.object(rp.ResolutionPipeline, "run", return_value=rp.PipelineResult()),
        ):
            ret = rp.main()

        assert ret == 0, "ret is not valid"

    def test_main_returns_1_when_errors_present(self):
        import resolution_pipeline as rp

        with (
            patch("sys.argv", ["rp", "--owner", "o", "--repo", "r", "--stages", "collect"]),
            patch.object(
                rp.ResolutionPipeline, "run", return_value=rp.PipelineResult(errors=["ruff_failed"])
            ),
        ):
            ret = rp.main()

        assert ret == 1, "ret is not valid"

    def test_main_output_json_writes_file(self, tmp_path):
        import resolution_pipeline as rp

        out_json = tmp_path / "result.json"

        with (
            patch(
                "sys.argv",
                [
                    "rp",
                    "--owner",
                    "o",
                    "--repo",
                    "r",
                    "--stages",
                    "collect",
                    "--output-json",
                    str(out_json),
                ],
            ),
            patch.object(
                rp.ResolutionPipeline, "run", return_value=rp.PipelineResult(alerts_collected=3)
            ),
        ):
            rp.main()

        assert out_json.exists(), "Condition must be true"
        data = json.loads(out_json.read_text())
        assert data["alerts_collected"] == 3, "Data must not be empty"
        assert "errors" in data, "Data must not be empty"
        assert "elapsed_s" in data, "Data must not be empty"

    def test_main_prints_passed_when_validation_passes(self, capsys):
        import resolution_pipeline as rp

        result = rp.PipelineResult(validation_passed=True)
        with (
            patch("sys.argv", ["rp", "--owner", "o", "--repo", "r", "--stages", "validate"]),
            patch.object(rp.ResolutionPipeline, "run", return_value=result),
        ):
            rp.main()

        captured = capsys.readouterr()
        assert "passed" in captured.out, "Condition must be true"

    def test_main_prints_errors_when_present(self, capsys):
        import resolution_pipeline as rp

        result = rp.PipelineResult(errors=["ruff_failed", "bandit_high_severity"])
        with (
            patch("sys.argv", ["rp", "--owner", "o", "--repo", "r", "--stages", "validate"]),
            patch.object(rp.ResolutionPipeline, "run", return_value=result),
        ):
            rp.main()

        captured = capsys.readouterr()
        assert "ruff_failed" in captured.out, "Condition must be true"

    def test_main_use_playwright_flag(self, tmp_path):
        """--use-playwright reaches ResolutionPipeline constructor."""
        import resolution_pipeline as rp

        constructed: list = []
        original_init = rp.ResolutionPipeline.__init__

        def capturing_init(self, *args, **kwargs):
            constructed.append(kwargs.get("use_playwright"))
            original_init(self, *args, **kwargs)

        with (
            patch(
                "sys.argv",
                ["rp", "--owner", "o", "--repo", "r", "--stages", "collect", "--use-playwright"],
            ),
            patch.object(rp.ResolutionPipeline, "__init__", capturing_init),
            patch.object(rp.ResolutionPipeline, "run", return_value=rp.PipelineResult()),
        ):
            rp.main()

        assert constructed and constructed[0] is True, "constructed is not valid"
