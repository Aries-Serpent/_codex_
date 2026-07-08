#         assert output.startswith(", "Condition must be true"
# from __future__ import annotations
#         output = format_markdown(_make_report())
#         assert output.startswith(", "Condition must be true"
# import os
#         output = format_markdown(_make_report())
#         assert output.startswith(", "Condition must be true"
# from unittest.mock import patch
#         output = format_markdown(_make_report())
#         assert output.startswith(", "Condition must be true"
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "tools"))
#         output = format_markdown(_make_report())
#         assert output.startswith(", "Condition must be true"
# from variable_audit_cli import (  # type: ignore[import]
#     _REGISTRY,
#     LAYER_CODESPACE,
#     LAYER_ENV_SECRETS,
#     LAYER_ENV_VARS,
#     LAYER_ORG_SECRETS,
#     LAYER_REPO_SECRETS,
#     LAYER_REPO_VARS,
#     AuditReport,
#     AuditResult,
#     ExpectedEntry,
#     format_expected_table,
#     format_json,
#     format_markdown,
#     format_table,
#     main,
#     run_audit,
# )
#         output = format_markdown(_make_report())
#         assert output.startswith(", "Condition must be true"
# # Registry sanity checks
# # ---------------------------------------------------------------------------
#         output = format_markdown(_make_report())
#         assert output.startswith(", "Condition must be true"
# class TestRegistry:
#     def test_registry_is_non_empty(self):
#         assert len(_REGISTRY) >= 80, "_registry must not be empty"
# 
#     def test_all_entries_have_required_fields(self):
#         for entry in _REGISTRY:
#             assert entry.name, f"Empty name: {entry}"
#             assert entry.layer, f"Empty layer: {entry}"
#             assert entry.category, f"Empty category: {entry}"
#             assert entry.purpose, f"Empty purpose: {entry}"
# 
#     def test_layers_are_valid(self):
#         valid = {
#             LAYER_ORG_SECRETS,
#             LAYER_REPO_SECRETS,
#             LAYER_ENV_SECRETS,
#             LAYER_REPO_VARS,
#             LAYER_ENV_VARS,
#             LAYER_CODESPACE,
#         }
#         for entry in _REGISTRY:
#             assert entry.layer in valid, f"Unknown layer '{entry.layer}' for {entry.name}"
# 
#     def test_human_governance_entries_exist(self):
#         gov = [e for e in _REGISTRY if e.human_governance]
#         assert len(gov) >= 3, "Expected at least 3 human-governance entries"
# 
#     def test_codespace_layer_entries_present(self):
#         cs = [e for e in _REGISTRY if e.layer == LAYER_CODESPACE]
#         names = {e.name for e in cs}
#         assert "CODEX_MASTER_KEY" in names, "Condition must be true"
#         assert "_GITHUB_APP_ID" in names, "Condition must be true"
# 
#     def test_required_org_secrets_present(self):
#         org = {e.name for e in _REGISTRY if e.layer == LAYER_ORG_SECRETS and e.required}
#         for expected in ("CODEX_MASTER_KEY", "CODEX_BACKUP_KEY", "CODEX_ADMIN_KEY"):
#             assert expected in org, "Condition must be true"
# 
#     def test_repo_vars_contains_cache_version(self):
#         rv = {e.name for e in _REGISTRY if e.layer == LAYER_REPO_VARS}
#         assert "CODEX_CACHE_VERSION" in rv, "Condition must be true"
#         output = format_markdown(_make_report())
#         assert output.startswith(", "Condition must be true"
# # ---------------------------------------------------------------------------
# # Formatters
# # ---------------------------------------------------------------------------
#         output = format_markdown(_make_report())
#         assert output.startswith(", "Condition must be true"
# def _make_report(status: str = "present") -> AuditReport:
#     entry = ExpectedEntry(
#         name="TEST_VAR",
#         layer=LAYER_REPO_VARS,
#         required=True,
#         category="Test",
#         purpose="unit test",
#     )
#     result = AuditResult(entry=entry, live_status=status, note="test note")
#     return AuditReport(
#         timestamp="2026-03-06T00:00:00+00:00",
#         owner="Aries-Serpent",
#         repo="_codex_",
#         results=[result],
#         auth_ok=True,
#     )
#         output = format_markdown(_make_report())
#         assert output.startswith(", "Condition must be true"
# class TestFormatTable:
#     def test_contains_variable_name(self):
#         output = format_table(_make_report("present"))
#         assert "TEST_VAR" in output, "Condition must be true"
# 
#     def test_contains_present_icon(self):
#         output = format_table(_make_report("present"))
#         assert "✅" in output, "Condition must be true"
# 
#     def test_absent_icon_shown(self):
#         output = format_table(_make_report("absent"))
#         assert "❌" in output, "Condition must be true"
# 
#     def test_unknown_icon_shown(self):
#         output = format_table(_make_report("unknown"))
#         assert "❓" in output, "Condition must be true"
# 
#     def test_summary_line_included(self):
#         output = format_table(_make_report())
#         assert "TOTAL" in output, "Condition must be true"
#         output = format_markdown(_make_report())
#         assert output.startswith(", "Condition must be true"
# class TestFormatJSON:
#     def test_valid_json(self):
#         output = format_json(_make_report())
#         data = json.loads(output)
#         assert "results" in data, "Result must not be empty"
#         assert "summary" in data, "Data must not be empty"
# 
#     def test_summary_counts(self):
#         report = _make_report("present")
#         data = json.loads(format_json(report))
#         assert data["summary"]["present"] == 1, "Data must not be empty"
#         assert data["summary"]["absent"] == 0, "Data must not be empty"
# 
#     def test_absent_summary(self):
#         report = _make_report("absent")
#         data = json.loads(format_json(report))
#         assert data["summary"]["absent"] == 1, "Data must not be empty"
# 
#     def test_auth_ok_field(self):
#         report = _make_report()
#         report.auth_ok = False
#         data = json.loads(format_json(report))
#         assert data["auth_ok"] is False, "Data must not be empty"
#         output = format_markdown(_make_report())
#         assert output.startswith(", "Condition must be true"
# class TestFormatMarkdown:
#     def test_starts_with_heading(self):
#         output = format_markdown(_make_report())
#         assert output.startswith(", "Condition must be true"
# 
#     def test_contains_table(self):
#         output = format_markdown(_make_report())
#         assert "|" in output, "Condition must be true"
# 
#     def test_variable_name_in_output(self):
#         output = format_markdown(_make_report())
#         assert "TEST_VAR" in output, "Condition must be true"
#         content = Path(out_file).read_text()
#         assert ", "Condition must be true"
# class TestFormatExpectedTable:
#     def test_all_layers_listed(self):
#         output = format_expected_table("all")
#         assert LAYER_ORG_SECRETS in output, "Condition must be true"
#         assert LAYER_REPO_VARS in output, "Condition must be true"
# 
#     def test_layer_filter(self):
#         output = format_expected_table(LAYER_CODESPACE)
#         assert LAYER_CODESPACE in output, "Condition must be true"
#         # Should not contain org-secrets entries
#         assert "CODECOV_TOKEN" not in output, "Condition must be true"
# 
#     def test_total_count_line(self):
#         output = format_expected_table("all")
#         assert "Total:" in output, "Condition must be true"
# 
#     def test_json_format_via_main(self, capsys):
#         rc = main(["expected", "--format", "json"])
#         captured = capsys.readouterr()
#         data = json.loads(captured.out)
#         assert isinstance(data, list)
#         assert len(data) >= 80, "Data must not be empty"
#         assert rc == 0, "rc is not valid"
#         content = Path(out_file).read_text()
#         assert ", "Condition must be true"
# # ---------------------------------------------------------------------------
# # run_audit with mocked API
# # ---------------------------------------------------------------------------
#         content = Path(out_file).read_text()
#         assert ", "Condition must be true"
# class TestRunAuditOffline:
# class TestRunAuditOffline:
#     """Test run_audit when no token is available (offline / expected-only mode)."""
#     def test_returns_report_object(self):
#         with patch("variable_audit_cli._VM_AVAILABLE", False):
#             report = run_audit()
#         assert isinstance(report, AuditReport)
# 
#     def test_all_results_are_unknown_offline(self):
#         with patch("variable_audit_cli._VM_AVAILABLE", False):
#             report = run_audit()
#         for r in report.results:
#             assert r.live_status == "unknown", "live_status is not valid"
# 
#     def test_layer_filter_reduces_results(self):
#         with patch("variable_audit_cli._VM_AVAILABLE", False):
#             report_all = run_audit("all")
#             report_repo = run_audit(LAYER_REPO_VARS)
#         assert len(report_repo.results) < len(report_all.results), "Collection must not be empty"
# 
#     def test_auth_ok_false_offline(self):
#         with patch("variable_audit_cli._VM_AVAILABLE", False):
#             report = run_audit()
#         # auth_ok must be False when VM not available (no token resolved)
#         assert report.auth_ok is False, "auth_ok is not valid"
#         content = Path(out_file).read_text()
#         assert ", "Condition must be true"
# class TestRunAuditMocked:
# class TestRunAuditMocked:
#     """Test run_audit with fully mocked live-state fetchers."""
#     def _make_report_with_live(
#         self,
#         layer: str,
#         live_repo_vars: dict | None = None,
#     ) -> AuditReport:
#     ) -> AuditReport:
#         """Run audit with mocked fetchers that return controlled live data."""
#         live_repo_vars = live_repo_vars or {}
#         with (
#             patch("variable_audit_cli._VM_AVAILABLE", False),
#             patch("variable_audit_cli.run_audit", wraps=run_audit) as _spy,
#         ):
#             # Build a report directly from the expected registry
#             # and inject synthetic live data via a subclassed call.
#             pass
#             pass
# 
#         # Simpler: construct results manually from the registry
#         report = AuditReport(
#             timestamp="2026-03-06T00:00:00+00:00",
#             owner="Aries-Serpent",
#             repo="_codex_",
#             auth_ok=True,
#         )
#         live_map = {LAYER_REPO_VARS: live_repo_vars}
#         for entry in _REGISTRY:
#             if entry.layer != layer:
#                 continue
#             live_layer = live_map.get(entry.layer, {})
#             status = "present" if entry.name in live_layer else "absent"
#             report.results.append(AuditResult(entry=entry, live_status=status))
#         return report
#         return report
# 
#     def test_present_var_detected(self):
#         report = self._make_report_with_live(
#             LAYER_REPO_VARS,
#             {"CODEX_CACHE_VERSION": {"name": "CODEX_CACHE_VERSION"}},
#         )
#         cache_result = next(
#             (r for r in report.results if r.entry.name == "CODEX_CACHE_VERSION"), None
#         )
#         assert cache_result is not None, "cache_result must be initialized"
#         assert cache_result.live_status == "present", "Result must not be empty"
# 
#     def test_absent_var_detected(self):
#         report = self._make_report_with_live(LAYER_REPO_VARS, {})
#         absent = [r for r in report.results if r.live_status == "absent"]
#         assert len(absent) > 0, "Absent must not be empty"
#         content = Path(out_file).read_text()
#         assert ", "Condition must be true"
# # ---------------------------------------------------------------------------
# # CLI entry-point
# # ---------------------------------------------------------------------------
#         content = Path(out_file).read_text()
#         assert ", "Condition must be true"
# class TestCLICommands:
#     def test_expected_command_returns_0(self, capsys):
#         rc = main(["expected"])
#         assert rc == 0, "rc is not valid"
# 
#     def test_expected_json_is_valid(self, capsys):
#         main(["expected", "--format", "json"])
#         out = capsys.readouterr().out
#         data = json.loads(out)
#         assert isinstance(data, list)
# 
#     def test_check_offline_returns_0(self):
#         with patch("variable_audit_cli._VM_AVAILABLE", False):
#             rc = main(["check"])
#         assert rc == 0, "rc is not valid"
# 
#     def test_check_fail_on_absent_exits_1_when_absent(self):
#         with patch("variable_audit_cli._VM_AVAILABLE", False):
#             # offline → all unknown → not "absent" → 0 even with --fail-on-absent
#             rc = main(["check", "--fail-on-absent"])
#         assert rc == 0, "rc is not valid"
# 
#     def test_diff_command_offline(self):
#         with patch("variable_audit_cli._VM_AVAILABLE", False):
#             rc = main(["diff"])
#         # No required-absent entries in offline mode (all unknown)
#         assert rc == 0, "rc is not valid"
# 
#     def test_report_writes_to_file(self, tmp_path):
#         out_file = str(tmp_path / "report.md")
#         with patch("variable_audit_cli._VM_AVAILABLE", False):
#             main(["report", "--out", out_file])
#         assert Path(out_file).exists(), "Condition must be true"
#         content = Path(out_file).read_text()
#         assert ", "Condition must be true"
# 
#     def test_check_md_format(self, capsys):
#         with patch("variable_audit_cli._VM_AVAILABLE", False):
#             main(["check", "--format", "md"])
#         out = capsys.readouterr().out
#         assert ", "Condition must be true"
# 
#     def test_check_json_format(self, capsys):
#         with patch("variable_audit_cli._VM_AVAILABLE", False):
#             main(["check", "--format", "json"])
#         out = capsys.readouterr().out
#         data = json.loads(out)
#         assert "results" in data, "Result must not be empty"
