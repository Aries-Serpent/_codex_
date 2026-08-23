import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.ci import session_wrapup_autofix as swa

#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#   - auto_fix_all_missing() : orchestrator correctness (mocked sub-fixes)
#   - main()                 : CLI argument routing
#             ### ✅ Always Required — fire automatically on every push (cannot be skipped)
#             - [x] pre-merge-validation.yml — Pre-merge checks (always required)
#             - [ ] resilient_validation.yml — Resilient Validation Suite (full pytest, 4 shards)
#             - [x] nox_gates.yml — Nox quality gates (ruff, mypy, coverage)
# 
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
# import pytest
#         block = swa._build_wec_block()
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
# for _candidate_root in [_THIS_FILE.parent] + list(_THIS_FILE.parent.parents):
#     _candidate = _candidate_root / "scripts" / "ci"
#     _SEARCHED_ROOTS.append(_candidate)
#     if (_candidate / "session_wrapup_autofix.py").is_file():
#         _SCRIPTS_CI = _candidate
#         break
#         block = swa._build_wec_block()
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
# if str(_SCRIPTS_CI) not in sys.path:
#     sys.path.insert(0, str(_SCRIPTS_CI))
#         block = swa._build_wec_block()
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
# 
#         block = swa._build_wec_block()
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
# 
#     def test_new_format_checked(self):
#         body = textwrap.dedent("""\
#             ## 🔄 Workflow Execution Checklist
#             ### ✅ Always Required — fire automatically on every push (cannot be skipped)
#             - [x] pre-merge-validation.yml — Pre-merge checks (always required)
#             - [ ] resilient_validation.yml — Resilient Validation Suite (full pytest, 4 shards)
#             - [x] nox_gates.yml — Nox quality gates (ruff, mypy, coverage)
#             - [ ] resilient_validation.yml — Resilient Validation Suite (full pytest, 4 shards)
#             - [x] nox_gates.yml — Nox quality gates (ruff, mypy, coverage)
#         """)
#         state = swa._extract_wec_state(body)
#         assert state["pre-merge-validation.yml"] is True, "Condition must be true"
#         assert state["resilient_validation.yml"] is False, "Condition must be true"
#         assert state["nox_gates.yml"] is True, "Condition must be true"
#     def test_legacy_format_checked(self):
#         body = textwrap.dedent("""\
#             **🔄 Workflow Execution Checklist**:
# 
#             🔐 Agent Token Delegation
#             - [x] 🔐 Enable Agent Token Delegation (`COPILOT_AGENT_AUTH_ENABLED`)
#             - [x] 💰 Cost Proposal Approved
#             - [ ] 🔄 Auto-Post @copilot review After Agent Session
#             - [ ] 🔄 Auto-Post @copilot review After Agent Session
#         """)
#         state = swa._extract_wec_state(body)
#         # Legacy items don't match workflow filenames — dict may be sparse
#         assert isinstance(state, dict)
#     def test_uppercase_X_treated_as_checked(self):
#         body = "- [X] security-scanning-suite.yml — Full security audit\n"
#         state = swa._extract_wec_state(body)
#         assert state.get("security-scanning-suite.yml") is True, "Condition must be true"
# 
#     def test_auto_approve_item(self):
#         body = "- [x] auto-approve-workflows — Auto-Approve workflow to run\n"
#         state = swa._extract_wec_state(body)
#         assert state.get("auto-approve-workflows") is True, "Condition must be true"
# 
#     def test_mixed_section_body(self):
#         body = textwrap.dedent("""\
#             Some preamble text.
# 
#             - [x] comment-review-gate.yml — Comment review gate (always required)
#             - [ ] documentation-link-checker.yml — Documentation link checker
#             - [x] cost-gate.yml — Cost governance gate
#             - [ ] auto-approve-workflows — Auto-Approve workflow to run
#             - [ ] documentation-link-checker.yml — Documentation link checker
#             - [x] cost-gate.yml — Cost governance gate
#             - [ ] auto-approve-workflows — Auto-Approve workflow to run
#         """)
#         state = swa._extract_wec_state(body)
#         assert state["comment-review-gate.yml"] is True, "Condition must be true"
#         assert state["documentation-link-checker.yml"] is False, "Condition must be true"
#         assert state["cost-gate.yml"] is True, "Condition must be true"
#         assert state["auto-approve-workflows"] is False, "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
# class TestBuildWecBlock:
#     def test_always_required_always_checked(self):
#         block = swa._build_wec_block(existing_state={})
#         for fname in swa._WEC_ALWAYS_REQUIRED:
#             assert f"- [x] {fname}" in block, "Condition must be true"
# 
#     def test_optional_items_unchecked_by_default(self):
#         # Patch _auth_enabled_in_env to False for determinism: we want to verify
#         # genuinely-optional items (not autonomous-auto-check items) default to [ ].
#         mock = unittest.mock
#         with mock.patch.object(swa, "_auth_enabled_in_env", return_value=False):
#             block = swa._build_wec_block(existing_state={})
#         optional = [
#         optional = [
#             "resilient_validation.yml",
#             "nox_gates.yml",
#             "validate.yml",
#             "test-rag.yml",
#             "security-scanning-suite.yml",
#             "documentation-link-checker.yml",
#             # NOTE: auto-approve-workflows is in _WEC_AUTONOMOUS_AUTO_CHECK —
#             # it is auto-checked when COPILOT_AGENT_AUTH_ENABLED=true (full autonomy).
#             # See test_autonomous_auto_check_items_checked_when_auth_enabled below.
#         ]
#         for fname in optional:
#             assert f"- [ ] {fname}" in block, f"{fname} should be unchecked by default"
#     def test_autonomous_auto_check_items_checked_when_auth_enabled(self):
#     def test_autonomous_auto_check_items_checked_when_auth_enabled(self):
#         """Items in _WEC_AUTONOMOUS_AUTO_CHECK are [x] when COPILOT_AGENT_AUTH_ENABLED=true."""
#         mock = unittest.mock
#         with mock.patch.object(swa, "_auth_enabled_in_env", return_value=True):
#             block = swa._build_wec_block(existing_state={})
#         for fname in swa._WEC_AUTONOMOUS_AUTO_CHECK:
#             assert (f"- [x] {fname}" in block, "Condition must be true"
#             ), f"{fname} should be [x] when COPILOT_AGENT_AUTH_ENABLED=true"
#     def test_autonomous_auto_check_items_unchecked_when_auth_disabled(self):
#     def test_autonomous_auto_check_items_unchecked_when_auth_disabled(self):
#         """Items in _WEC_AUTONOMOUS_AUTO_CHECK stay [ ] when auth is disabled + state empty."""
#         mock = unittest.mock
#         with mock.patch.object(swa, "_auth_enabled_in_env", return_value=False):
#             block = swa._build_wec_block(existing_state={})
#         for fname in swa._WEC_AUTONOMOUS_AUTO_CHECK:
#             assert (f"- [ ] {fname}" in block, "Condition must be true"
#             ), f"{fname} should be [ ] when auth disabled and no existing state"
#     def test_autonomous_auto_check_respects_explicit_uncheck(self):
#     def test_autonomous_auto_check_respects_explicit_uncheck(self):
#         """Explicit maintainer uncheck (state[fname]=False) is respected even when auth is on."""
#         mock = unittest.mock
#         with mock.patch.object(swa, "_auth_enabled_in_env", return_value=True):
#             block = swa._build_wec_block(existing_state={"auto-approve-workflows": False})
#         assert ("- [ ] auto-approve-workflows" in block, "Condition must be true"
#         ), "explicit [ ] uncheck by maintainer must be preserved even with auth enabled"
#     def test_never_check_items_are_unchecked_by_default(self):
#         block = swa._build_wec_block(existing_state={})
#         for fname in swa._WEC_NEVER_CHECK:
#             assert f"- [ ] {fname}" in block, f"{fname} should default unchecked"
# 
#     def test_existing_state_preserves_maintainer_selections(self):
#         existing = {
#         existing = {
#             "resilient_validation.yml": True,
#             "cost-gate.yml": True,
#             "auto-approve-workflows": True,
#         }
#         block = swa._build_wec_block(existing_state=existing)
#         assert "- [x] resilient_validation.yml" in block, "Condition must be true"
#         # cost-gate.yml is always_required=True so always [x] regardless
#         assert "- [x] cost-gate.yml" in block, "Condition must be true"
#         assert "- [x] auto-approve-workflows" in block, "Condition must be true"
#     def test_always_required_not_overridden_by_false_state(self):
#         # Even if existing_state has always-required as False, they must stay [x]
#         existing = {fname: False for fname in swa._WEC_ALWAYS_REQUIRED}
#         block = swa._build_wec_block(existing_state=existing)
#         for fname in swa._WEC_ALWAYS_REQUIRED:
#             assert f"- [x] {fname}" in block, "Condition must be true"
# 
#     def test_sections_present(self):
#         block = swa._build_wec_block()
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
# 
#     def test_instructions_footer_present(self):
#         block = swa._build_wec_block()
#         assert "HARDENED AGENT INSTRUCTION" in block, "Condition must be true"
#         assert "report_progress" in block, "Condition must be true"
#         # New instruction directs agents to use --print-wec-block CLI
#         assert "print-wec-block" in block.lower() or "never reconstruct" in block.lower(), "Condition must be true"
# 
#     def test_heading_marker_present(self):
#         block = swa._build_wec_block()
#         assert swa._WEC_MARKER in block, "Condition must be true"
# 
#     def test_no_duplicate_entries(self):
#         block = swa._build_wec_block()
#         for fname, _, _ in swa._WEC_ITEMS:
#             # Use word-boundary pattern so 'pre-merge-validation.yml' does not
#             # match as a substring of 'pages-pre-merge-validation.yml'.
#             pattern = re.compile(r"(?<![a-zA-Z0-9/-])" + re.escape(fname))
#             count = len(pattern.findall(block))
#             assert count == 1, f"{fname} appears more than once in WEC block"
# 
#     def test_none_existing_state_same_as_empty(self):
#         assert swa._build_wec_block(None) == swa._build_wec_block({}), "Condition must be true"
#         block = swa._REQUIRED_PR_CHECKBOXES
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
# class TestFixPrBodyCheckboxes:
#     def _make_run(self, stdout: str, returncode: int = 0):
#         r = MagicMock()
#         r.stdout = stdout
#         r.returncode = returncode
#         return r
# 
#     def test_no_update_needed_when_wec_present(self):
#         body = "## intro\n\n" + swa._build_wec_block()
#         with patch("subprocess.run") as mock_run:
#             mock_run.return_value = self._make_run(body)
#             result = swa.fix_pr_body_checkboxes("42", dry_run=False)
#         assert result is False, "Result must not be empty"
#         # gh pr edit should NOT have been called
#         edit_calls = [c for c in mock_run.call_args_list if "edit" in str(c)]
#         assert len(edit_calls) == 0, "Edit_calls must not be empty"
# 
#     def test_update_called_when_wec_missing(self):
#         body = "## My PR\n\nSome content without WEC block.\n"
#         with patch("subprocess.run") as mock_run:
#             mock_run.return_value = self._make_run(body)
#             result = swa.fix_pr_body_checkboxes("42", dry_run=False)
#         assert result is True, "Result must not be empty"
#         calls_str = str(mock_run.call_args_list)
#         assert "edit" in calls_str, "Condition must be true"
# 
#     def test_dry_run_does_not_call_edit(self):
#         body = "## My PR\n\nNo WEC here.\n"
#         with patch("subprocess.run") as mock_run:
#             mock_run.return_value = self._make_run(body)
#             result = swa.fix_pr_body_checkboxes("42", dry_run=True)
#         assert result is True, "Result must not be empty"
#         edit_calls = [c for c in mock_run.call_args_list if "edit" in str(c)]
#         assert len(edit_calls) == 0, "Edit_calls must not be empty"
# 
#     def test_legacy_format_replaced_with_canonical(self):
#         body = textwrap.dedent("""\
#             ## PR body
# 
#             **🔄 Workflow Execution Checklist**:
# 
#             🔐 Agent Token Delegation
#             - [x] 🔐 Enable Agent Token Delegation (`COPILOT_AGENT_AUTH_ENABLED`)
#             - [x] 💰 Cost Proposal Approved
#             - [ ] 🔄 Auto-Post @copilot review After Agent Session
#             - [ ] 🔄 Auto-Post @copilot review After Agent Session
#         """)
#         captured_body: list[str] = []
#         def fake_run(cmd, **kwargs):
#             if "edit" in cmd:
#                 # Capture the new body passed to gh pr edit
#                 body_idx = cmd.index("--body") + 1
#                 captured_body.append(cmd[body_idx])
#             return self._make_run(body)
# 
#         with patch("subprocess.run", side_effect=fake_run):
#             result = swa.fix_pr_body_checkboxes("42", dry_run=False)
# 
#         assert result is True, "Result must not be empty"
#         if captured_body:
#             assert swa._WEC_MARKER in captured_body[0], "Condition must be true"
#             # Legacy marker should be gone
#             assert swa._WEC_MARKER_LEGACY not in captured_body[0], "Condition must be true"
# 
#     def test_maintainer_checked_items_preserved_on_update(self):
#     def test_maintainer_checked_items_preserved_on_update(self):
#         """Existing [x] items must survive a WEC rebuild triggered by legacy format."""
#         body = textwrap.dedent("""\
#             ## PR
#             - [x] pre-merge-validation.yml — Pre-merge checks (always required)
#             - [x] resilient_validation.yml — Resilient Validation Suite (full pytest, 4 shards)
#             - [ ] nox_gates.yml — Nox quality gates (ruff, mypy, coverage)
#             - [x] resilient_validation.yml — Resilient Validation Suite (full pytest, 4 shards)
#             - [ ] nox_gates.yml — Nox quality gates (ruff, mypy, coverage)
# 
#             ### ⚡ Auto-Approve
#             - [x] auto-approve-workflows — Auto-Approve workflow to run
#             ### ⚡ Auto-Approve
#             - [x] auto-approve-workflows — Auto-Approve workflow to run
#         """)
#         captured_body: list[str] = []
#         def fake_run(cmd, **kwargs):
#             if "edit" in cmd:
#                 body_idx = cmd.index("--body") + 1
#                 captured_body.append(cmd[body_idx])
#             return self._make_run(body)
# 
#         with patch("subprocess.run", side_effect=fake_run):
#             result = swa.fix_pr_body_checkboxes("42", dry_run=False)
# 
#         assert result is True, "Result must not be empty"
#         assert captured_body, "captured_body is not valid"
#         assert "- [x] resilient_validation.yml" in captured_body[0], "Condition must be true"
#         assert "- [x] auto-approve-workflows" in captured_body[0], "Condition must be true"
#         assert "- [ ] nox_gates.yml" in captured_body[0], "Condition must be true"


def test_append_session_evidence_strips_values_and_uses_full_second_timestamp(tmp_path):
    evidence_path = tmp_path / "pda_iterations.jsonl"
    with patch.object(swa, "_session_evidence_path", return_value=evidence_path):
        swa._append_session_evidence(
            "smoke-test",
            issue_summary="needs fixing",
            files_changed=["  scripts/ci/foo.py  ", "bar.py"],
            commands=["  python -m pytest  ", "  "],
            evidence_refs=["  https://example.test  "],
        )

    record = json.loads(evidence_path.read_text(encoding="utf-8").strip().splitlines()[-1])
    assert record["affected_files"] == ["scripts/ci/foo.py", "bar.py"]
    assert record["commands"] == ["python -m pytest"]
    assert record["evidence_refs"] == ["https://example.test"]
    assert record["timestamp"].endswith("Z")
    assert record["timestamp"].count(":") == 2


def test_append_session_evidence_ignores_duplicate_tail_records(tmp_path):
    evidence_path = tmp_path / "pda_iterations.jsonl"
    with patch.dict("os.environ", {"CODEX_SESSION_ID": "session-auto"}, clear=False), patch.object(
        swa, "_session_evidence_path", return_value=evidence_path
    ), patch.object(swa, "_now_iso", return_value="2026-08-23T00:00:00Z"):
        payload = {
            "type": "session_loop",
            "session_id": "session-auto",
            "timestamp": "2026-08-23T00:00:00Z",
            "branch": "unknown",
            "target_base": "0D_base_",
            "phase": "duplicate-check",
            "issue_summary": "",
            "root_cause": "",
            "affected_files": ["path/to/file.py"],
            "commands": ["python -m pytest"],
            "status": "pass",
            "evidence_refs": ["https://example.test"],
            "doc_summary": "",
            "gate_status": "pass",
            "final_decision": "ready",
            "wec_state": "preserved",
            "follow_up_required": False,
        }
        evidence_path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")

        swa._append_session_evidence(
            "duplicate-check",
            files_changed=["path/to/file.py"],
            commands=["python -m pytest"],
            evidence_refs=["https://example.test"],
        )

    assert evidence_path.read_text(encoding="utf-8").count('"phase": "duplicate-check"') == 1
# 
#     def test_gh_cli_failure_returns_false(self):
#         with patch("subprocess.run", side_effect=FileNotFoundError("gh not found")):
#             result = swa.fix_pr_body_checkboxes("42", dry_run=False)
#         assert result is False, "Result must not be empty"
#         block = swa._REQUIRED_PR_CHECKBOXES
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
# class TestFixManifestBaseline:
# class TestFixManifestBaseline:
#     """Tests for fix_manifest_baseline() which delegates to sync_tracked_files.py."""
#     def _make_proc(self, returncode: int = 0) -> MagicMock:
#         p = MagicMock()
#         p.returncode = returncode
#         p.stdout = ""
#         p.stderr = ""
#         return p
# 
#     def _make_repo(self, tmp_path: Path) -> Path:
#     def _make_repo(self, tmp_path: Path) -> Path:
#         """Create a fake repo root with sync_tracked_files.py present."""
#         script = tmp_path / "scripts" / "ci" / "sync_tracked_files.py"
#         script.parent.mkdir(parents=True, exist_ok=True)
#         script.write_text("# stub", encoding="utf-8")
#         return tmp_path
#     def test_updates_stale_hash(self, tmp_path: Path):
#     def test_updates_stale_hash(self, tmp_path: Path):
#         """When sync_tracked_files --fix succeeds and --check passes, returns True."""
#         repo = self._make_repo(tmp_path)
#         with (
#             patch.object(swa, "REPO_ROOT", repo),
#             patch.object(swa.subprocess, "run", return_value=self._make_proc(0)) as mock_run,
#         ):
#             result = swa.fix_manifest_baseline(pr_number="42", dry_run=False)
#         assert result is True, "Result must not be empty"
#         assert mock_run.call_count == 2, "Count must be greater than zero"
#     def test_no_update_when_hash_correct(self, tmp_path: Path):
#     def test_no_update_when_hash_correct(self, tmp_path: Path):
#         """When both --fix and --check exit 0, returns True (sync completed)."""
#         repo = self._make_repo(tmp_path)
#         with (
#             patch.object(swa, "REPO_ROOT", repo),
#             patch.object(swa.subprocess, "run", return_value=self._make_proc(0)),
#         ):
#             result = swa.fix_manifest_baseline(pr_number="42", dry_run=False)
#         assert result is True, "Result must not be empty"
#     def test_dry_run_does_not_write(self, tmp_path: Path):
#     def test_dry_run_does_not_write(self, tmp_path: Path):
#         """In dry-run mode, calls --check only (non-zero rc -> True = would change)."""
#         repo = self._make_repo(tmp_path)
#         with (
#             patch.object(swa, "REPO_ROOT", repo),
#             patch.object(swa.subprocess, "run", return_value=self._make_proc(1)) as mock_run,
#         ):
#             result = swa.fix_manifest_baseline(pr_number="42", dry_run=True)
#         assert result is True, "Result must not be empty"
#         assert mock_run.call_count == 1, "Count must be greater than zero"
#         args = mock_run.call_args[0][0]
#         assert "--check" in args, "Condition must be true"
#     def test_missing_manifest_returns_false(self, tmp_path: Path):
#     def test_missing_manifest_returns_false(self, tmp_path: Path):
#         """If sync_tracked_files.py does not exist, return False without calling it."""
#         with patch.object(swa, "REPO_ROOT", tmp_path):
#             result = swa.fix_manifest_baseline()
#         assert result is False, "Result must not be empty"
#     def test_missing_baseline_returns_false(self, tmp_path: Path):
#     def test_missing_baseline_returns_false(self, tmp_path: Path):
#         """Same behaviour: no script file -> return False immediately."""
#         with patch.object(swa, "REPO_ROOT", tmp_path):
#             result = swa.fix_manifest_baseline()
#         assert result is False, "Result must not be empty"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#             patch.object(swa, "fix_manifest_baseline", return_value=False),
#             patch.object(swa, "fix_pda_entry_today", return_value=False),
#             patch.object(swa, "update_pr_description", return_value=False),
#             patch.object(swa, "fix_pr_body_checkboxes", return_value=False),
#             patch.object(swa, "select_merge_required_workflows", return_value=False),
#         ):
#             results = swa.auto_fix_all_missing(pr_number="42")
#         with (
#             patch.object(swa, "_last_commit_changed", return_value=False),
#             patch.object(swa, "_changelog_has_unreleased", return_value=False),
#             patch.object(swa, "fix_accountability_report", return_value=True) as mock_acct,
#             patch.object(swa, "fix_changelog", return_value=True) as mock_cl,
#             patch.object(swa, "fix_manifest_baseline", return_value=True) as mock_mfst,
#             patch.object(swa, "fix_pda_entry_today", return_value=True) as mock_pda,
#             patch.object(swa, "update_pr_description", return_value=True) as mock_desc,
#             patch.object(swa, "fix_pr_body_checkboxes", return_value=True) as mock_wec,
#             patch.object(swa, "select_merge_required_workflows", return_value=True) as mock_act,
#             patch.object(swa, "check_req14_agents_used", return_value=False),
#             patch.object(swa, "fix_req14_agents_used", return_value=True) as mock_req14,
#         ):
#             results = swa.auto_fix_all_missing(pr_number="42", sha="abc123", run_url="http://x")
#         mock_acct.assert_called_once()
#         mock_cl.assert_called_once()
#         mock_mfst.assert_called_once()
#         mock_pda.assert_called_once()
#         mock_desc.assert_called_once()
#         mock_wec.assert_called_once()
#         mock_act.assert_called_once()
#         mock_req14.assert_called_once()
#         assert all(results.values()), "Result must not be empty"
# 
#     def test_skips_pr_body_when_pr_unknown(self):
#         with (
#             patch.object(swa, "_last_commit_changed", return_value=True),
#             patch.object(swa, "_changelog_has_unreleased", return_value=True),
#             patch.object(swa, "fix_manifest_baseline", return_value=False),
#             patch.object(swa, "fix_pda_entry_today", return_value=False),
#             patch.object(swa, "update_pr_description") as mock_desc,
#             patch.object(swa, "fix_pr_body_checkboxes") as mock_wec,
#             patch.object(swa, "select_merge_required_workflows") as mock_act,
#         ):
#             swa.auto_fix_all_missing(pr_number="unknown")
#         mock_desc.assert_not_called()
#         mock_wec.assert_not_called()
#         mock_act.assert_not_called()
# 
#     def test_dry_run_passed_through(self):
#         with (
#             patch.object(swa, "_last_commit_changed", return_value=False),
#             patch.object(swa, "_changelog_has_unreleased", return_value=False),
#             patch.object(swa, "fix_accountability_report", return_value=True) as mock_acct,
#             patch.object(swa, "fix_changelog", return_value=True),
#             patch.object(swa, "fix_manifest_baseline", return_value=False),
#             patch.object(swa, "fix_pda_entry_today", return_value=False),
#             patch.object(swa, "update_pr_description", return_value=False),
#             patch.object(swa, "fix_pr_body_checkboxes", return_value=False),
#             patch.object(swa, "select_merge_required_workflows", return_value=False),
#         ):
#             swa.auto_fix_all_missing(pr_number="42", dry_run=True)
#         _, kwargs = mock_acct.call_args
#         assert kwargs.get("dry_run") is True, "Condition must be true"
#         block = swa._REQUIRED_PR_CHECKBOXES
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
# class TestMain:
#     def test_fix_all_calls_auto_fix_all_missing(self):
#         with patch.object(swa, "auto_fix_all_missing", return_value={}) as mock_fn:
#             rc = swa.main(["--pr-number", "42", "--fix-all"])
#         mock_fn.assert_called_once()
#         assert rc == 0, "rc is not valid"
# 
#     def test_check_mode_returns_0_when_both_ok(self):
#         with (
#             patch.object(swa, "_last_commit_changed", return_value=True),
#             patch.object(swa, "CODEX_MANIFEST", Path("/fake/CODEX_MANIFEST.json")),
#             patch.object(swa, "SECRETS_BASELINE", Path("/fake/.secrets.baseline")),
#         ):
#             # Patch Path.exists to return True for fake paths
#             with patch.object(Path, "exists", return_value=True):
#                 rc = swa.main(["--pr-number", "42", "--check"])
#         assert rc == 0, "rc is not valid"
# 
#     def test_check_mode_returns_1_when_acct_missing(self):
#         def fake_last_commit(p: Path) -> bool:
#             return "CHANGELOG" in str(p)  # CHANGELOG OK, accountability NOT
# 
#         with patch.object(swa, "_last_commit_changed", side_effect=fake_last_commit):
#             rc = swa.main(["--pr-number", "42", "--check"])
#         assert rc == 1, "rc is not valid"
# 
#     def test_fix_manifest_flag(self):
#         with patch.object(swa, "fix_manifest_baseline", return_value=False) as mock_fn:
#             with (
#                 patch.object(swa, "_last_commit_changed", return_value=True),
#                 patch.object(swa, "_changelog_has_unreleased", return_value=True),
#                 patch.object(swa, "fix_pr_body_checkboxes", return_value=False),
#             ):
#                 rc = swa.main(["--pr-number", "42", "--fix-manifest"])
#         mock_fn.assert_called_once()
#         assert rc == 0, "rc is not valid"
# 
#     def test_fix_pr_body_flag(self):
#         with (
#             patch.object(swa, "fix_pr_body_checkboxes", return_value=True) as mock_fn,
#             patch.object(swa, "_last_commit_changed", return_value=True),
#             patch.object(swa, "_changelog_has_unreleased", return_value=True),
#             patch.object(swa, "fix_manifest_baseline", return_value=False),
#         ):
#             rc = swa.main(["--pr-number", "42", "--fix-pr-body"])
#         mock_fn.assert_called_once()
#         assert rc == 0, "rc is not valid"
# 
#     def test_dry_run_propagated(self):
#         with (
#             patch.object(swa, "fix_accountability_report", return_value=True) as mock_acct,
#             patch.object(swa, "_last_commit_changed", return_value=False),
#             patch.object(swa, "_changelog_has_unreleased", return_value=True),
#             patch.object(swa, "fix_manifest_baseline", return_value=False),
#             patch.object(swa, "fix_pr_body_checkboxes", return_value=False),
#         ):
#             swa.main(["--pr-number", "42", "--fix-accountability", "--dry-run"])
#         _, kwargs = mock_acct.call_args
#         assert kwargs.get("dry_run") is True, "Condition must be true"
#         block = swa._REQUIRED_PR_CHECKBOXES
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
# class TestWecConstants:
#     def test_wec_items_count_matches_sections(self):
#     def test_wec_items_count_matches_sections(self):
#         """Ensure _WEC_ITEMS covers all sections and has not accidentally lost entries.
#         The list has grown from 16 (original) to the current count as new workflows
#         were added in subsequent sessions.  This test guards against accidental
#         truncation by enforcing a hard floor (the always-required + always-active
#         items must always be present) and by re-asserting that each item is a
#         valid (filename, label, required) tuple.
#         valid (filename, label, required) tuple.
#         """
#         # Hard floor: the 5 always-required gates + the 4 always-active items
#         # (copilot-agent-checkin, copilot-agent-session-done, copilot-iterative-self-healing,
#         # cost-gate) + auto-approve-workflows = 10.  Anything less means the list
#         # was truncated.
#         MIN_EXPECTED = 10
#         assert len(swa._WEC_ITEMS) >= MIN_EXPECTED, (
#             f"_WEC_ITEMS truncated below required floor: got {len(swa._WEC_ITEMS)}, "
#             f"expected at least {MIN_EXPECTED} (always-required + always-active + auto-approve)."
#         )
#         # Structural check: every entry must be a (filename, label, required) tuple.
#         for entry in swa._WEC_ITEMS:
#             assert isinstance(entry, tuple) and len(entry) == 3, f"Bad _WEC_ITEMS entry: {entry!r}"
#             fname, label, required = entry
#             assert isinstance(fname, str) and fname, f"Empty/non-str filename in {entry!r}"
#             assert isinstance(label, str), f"Non-str label in {entry!r}"
#             assert isinstance(required, bool), f"Non-bool required flag in {entry!r}"
#     def test_always_required_items_in_wec_items(self):
#         filenames = {item[0] for item in swa._WEC_ITEMS}
#         for fname in swa._WEC_ALWAYS_REQUIRED:
#             assert fname in filenames, f"{fname} missing from _WEC_ITEMS"
# 
#     def test_auto_approve_item_present(self):
#         filenames = [item[0] for item in swa._WEC_ITEMS]
#         assert "auto-approve-workflows" in filenames, "Condition must be true"
# 
#     def test_new_wec_drift_workflows_present(self):
#         filenames = {item[0] for item in swa._WEC_ITEMS}
#         expected = {
#         expected = {
#             "e-to-d-transition-gate.yml",
#             "d-capable-promotion-gate.yml",
#             "mcp-health.yml",
#         }
#         assert expected.issubset(filenames), (
#             "WEC drift remains: expected template workflows missing from _WEC_ITEMS: "
#             f"{sorted(expected - filenames)}"
#         )
#     def test_never_check_items_are_not_always_required(self):
#         assert swa._WEC_NEVER_CHECK.isdisjoint(swa._WEC_ALWAYS_REQUIRED), "Condition must be true"
# 
#     def test_merge_required_disjoint_from_never_check(self):
#     def test_merge_required_disjoint_from_never_check(self):
#         """S178 hardening: a never-check workflow must NEVER appear in the
#         merge-required activation set — the runtime guard in
#         ``update_pr_wec_for_merge_readiness`` and the module-load assertion
#         both depend on this invariant. This test catches accidental edits
#         before they reach runtime.
#         """
#         overlap = swa._MERGE_REQUIRED_WORKFLOWS & swa._WEC_NEVER_CHECK
#         assert not overlap, (
#             f"_MERGE_REQUIRED_WORKFLOWS overlaps with _WEC_NEVER_CHECK on "
#             f"{sorted(overlap)} — these workflows would be auto-activated "
#             "and re-enter the Copilot continuation loop."
#         )
#     def test_merge_required_subset_of_wec_items(self):
#     def test_merge_required_subset_of_wec_items(self):
#         """Every merge-required workflow must be a known _WEC_ITEMS entry —
#         otherwise activation would silently no-op (loop body never matches).
#         """
#         wec_filenames = {item[0] for item in swa._WEC_ITEMS}
#         unknown = swa._MERGE_REQUIRED_WORKFLOWS - wec_filenames
#         assert not unknown, (
#             f"_MERGE_REQUIRED_WORKFLOWS contains workflows not in _WEC_ITEMS: " f"{sorted(unknown)}"
#         )
#     def test_build_wec_block_does_not_auto_check_never_check_when_state_empty(self):
#     def test_build_wec_block_does_not_auto_check_never_check_when_state_empty(self):
#         """``_build_wec_block`` must render every _WEC_NEVER_CHECK item as
#         ``[ ]`` when no maintainer override exists in ``existing_state``.
#         """
#         block = swa._build_wec_block({})
#         for fname in swa._WEC_NEVER_CHECK:
#             # Each never-check item must appear in the block, unchecked.
#             assert (f"- [ ] {fname}" in block, "Condition must be true"
#             ), f"never-check item {fname!r} not rendered as `[ ]` in WEC block"
#             assert (f"- [x] {fname}" not in block, "Condition must be true"
#             ), f"never-check item {fname!r} was auto-rendered as `[x]`"
#     def test_build_wec_block_preserves_maintainer_x_for_never_check(self):
#     def test_build_wec_block_preserves_maintainer_x_for_never_check(self):
#         """When a maintainer has explicitly checked a never-check item in the
#         existing PR body, ``_build_wec_block`` must preserve that ``[x]``.
#         """
#         for fname in swa._WEC_NEVER_CHECK:
#             block = swa._build_wec_block({fname: True})
#             assert f"- [x] {fname}" in block, f"maintainer [x] for {fname!r} was not preserved"
#     def test_required_pr_checkboxes_contains_auto_approve(self):
#         assert "auto-approve-workflows" in swa._REQUIRED_PR_CHECKBOXES, "Condition must be true"
# 
#     def test_required_pr_checkboxes_contains_all_sections(self):
#         block = swa._REQUIRED_PR_CHECKBOXES
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
# 
#     def test_wec_marker_is_heading_format(self):
#         assert swa._WEC_MARKER.startswith(", "Condition must be true"
# 
#     def test_legacy_marker_different_from_current(self):
#         assert swa._WEC_MARKER != swa._WEC_MARKER_LEGACY, "_WEC_MARKER is not valid"


class TestWecTemplateDefaults:
    def test_primary_pr_template_keeps_never_check_items_unchecked(self):
        template_path = Path(__file__).resolve().parents[2] / ".github" / "pull_request_template.md"
        if not template_path.exists():
            pytest.skip(f"Template file not available in this environment: {template_path}")
        template = template_path.read_text(encoding="utf-8")
        for fname in swa._WEC_NEVER_CHECK:
            assert f"- [ ] {fname}" in template, f"{fname} should be unchecked in primary template"

    def test_secondary_pr_template_keeps_never_check_items_unchecked(self):
        template_path = Path(__file__).resolve().parents[2] / ".github" / "PULL_REQUEST_TEMPLATE.md"
        if not template_path.exists():
            pytest.skip(f"Template file not available in this environment: {template_path}")
        template = template_path.read_text(encoding="utf-8")
        for fname in swa._WEC_NEVER_CHECK:
            assert (f"- [ ] {fname}" in template, "Condition must be true"
            ), f"{fname} should be unchecked in secondary template"


class TestWecNeverCheckTelemetry:
    """Telemetry counter for ⚠ WEC activation skipped never-check items (S178c)."""

    def _build_pr_body_with_never_check_in_merge_required(self, never_check_fname: str) -> str:
        """Build a minimal PR body that has the WEC block present."""
        block = swa._build_wec_block({})
        return f"## My PR\n\nDescription.\n\n{block}"

    def test_step_summary_written_when_never_check_skipped(self, tmp_path, monkeypatch):
        """select_merge_required_workflows must write to GITHUB_STEP_SUMMARY when a
        never-check item is encountered during activation — not just to stderr.
        """
        summary_file = tmp_path / "step_summary.md"
        monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary_file))

        # Inject a never-check item into _MERGE_REQUIRED_WORKFLOWS so the guard fires.
        never_check_item = next(iter(swa._WEC_NEVER_CHECK))
        original_merge_required = swa._MERGE_REQUIRED_WORKFLOWS
        monkeypatch.setattr(
            swa,
            "_MERGE_REQUIRED_WORKFLOWS",
            original_merge_required | {never_check_item},
        )

        pr_body = swa._build_wec_block({})

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=f"## My PR\n\n{pr_body}",
            )
            swa.select_merge_required_workflows("9999", dry_run=True)

        # The step summary file must exist and contain the warning text.
        assert summary_file.exists(), "GITHUB_STEP_SUMMARY was not written"
        content = summary_file.read_text(encoding="utf-8")
        assert ("WEC Never-Check Guard" in content, "Content must not be empty"
        ), "Step summary missing 'WEC Never-Check Guard' telemetry heading"
        assert (never_check_item in content, "Content must not be empty"
        ), f"Step summary missing the skipped item name '{never_check_item}'"

    def test_no_step_summary_when_no_skipped_items(self, tmp_path, monkeypatch):
        """When no never-check items are skipped, GITHUB_STEP_SUMMARY must NOT
        receive the WEC Never-Check Guard section.
        """
        summary_file = tmp_path / "step_summary.md"
        monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary_file))

        pr_body = swa._build_wec_block({})
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=pr_body)
            swa.select_merge_required_workflows("9999", dry_run=True)

        if summary_file.exists():
            content = summary_file.read_text(encoding="utf-8")
            assert "WEC Never-Check Guard" not in content, "Content must not be empty"


class TestHumanGrantTracking:
    """Tests for the human-vs-agent WEC checkbox tracking system."""

    def test_detect_human_grant_when_agent_had_unchecked(self, tmp_path, monkeypatch):
        """A box that is [x] NOW but was [ ] in agent's last write → human grant."""
        state_file = tmp_path / "wec_state.json"
        state_data = {
            "schema_version": "2",
            "pr_entries": {
                "1234": {
                    "last_agent_write": {"auto-approve-workflows": False},
                    "human_grants": {},
                }
            },
        }
        import json

        state_file.write_text(json.dumps(state_data))
        monkeypatch.setattr(swa, "_WEC_STATE_FILE", state_file)

        grants = swa._detect_human_grants("1234", {"auto-approve-workflows": True})
        assert "auto-approve-workflows" in grants, "Condition must be true"
        assert grants["auto-approve-workflows"]["status"] == "active", "Condition must be true"

    def test_detect_human_revoke_when_agent_had_checked(self, tmp_path, monkeypatch):
        """A box the agent wrote [x] but is now [ ] → human revoke."""
        state_file = tmp_path / "wec_state.json"
        state_data = {
            "schema_version": "2",
            "pr_entries": {
                "1234": {
                    "last_agent_write": {"auto-approve-workflows": True},
                    "human_grants": {
                        "auto-approve-workflows": {
                            "status": "active",
                            "granted_at": "...",
                            "granted_sha": "abc",
                        },
                    },
                }
            },
        }
        import json

        state_file.write_text(json.dumps(state_data))
        monkeypatch.setattr(swa, "_WEC_STATE_FILE", state_file)

        grants = swa._detect_human_grants("1234", {"auto-approve-workflows": False})
        assert grants["auto-approve-workflows"]["status"] == "revoked", "Condition must be true"

    def test_human_grant_overrides_never_check(self):
        """A human grant must render [x] even for _WEC_NEVER_CHECK items."""
        mock = unittest.mock
        never_check_item = next(iter(swa._WEC_NEVER_CHECK))
        grants = {never_check_item: {"status": "active", "granted_at": "...", "granted_sha": "x"}}
        with mock.patch.object(swa, "_auth_enabled_in_env", return_value=False):
            block = swa._build_wec_block(
                existing_state={never_check_item: False},
                human_grants=grants,
            )
        assert (f"- [x] {never_check_item}" in block, "Item must not be empty"
        ), "human grant must override _WEC_NEVER_CHECK and render [x]"

    def test_revoked_grant_does_not_force_checked(self):
        """A revoked human grant must NOT force [x]."""
        mock = unittest.mock
        grants = {
            "auto-approve-workflows": {"status": "revoked", "granted_at": "...", "granted_sha": "x"}
        }
        with mock.patch.object(swa, "_auth_enabled_in_env", return_value=False):
            block = swa._build_wec_block(
                existing_state={"auto-approve-workflows": False},
                human_grants=grants,
            )
        assert ("- [ ] auto-approve-workflows" in block, "Condition must be true"
        ), "revoked grant should result in [ ] when state is False"

    def test_no_grant_for_unchanged_state(self, tmp_path, monkeypatch):
        """No grant should be recorded when agent last wrote [x] and it's still [x]."""
        state_file = tmp_path / "wec_state.json"
        state_data = {
            "schema_version": "2",
            "pr_entries": {
                "1234": {
                    "last_agent_write": {"auto-approve-workflows": True},
                    "human_grants": {},
                }
            },
        }
        import json

        state_file.write_text(json.dumps(state_data))
        monkeypatch.setattr(swa, "_WEC_STATE_FILE", state_file)

        grants = swa._detect_human_grants("1234", {"auto-approve-workflows": True})
        # No new grant — agent already had it as [x]
        assert "auto-approve-workflows" not in grants, "Condition must be true"
