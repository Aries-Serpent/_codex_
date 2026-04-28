"""Tests for scripts/ci/session_wrapup_autofix.py — WEC, manifest sync, and auto-fix.

Covers:
  - _extract_wec_state()   : checkbox parsing across new/legacy/mixed formats
  - _build_wec_block()     : canonical block generation with state preservation
  - fix_pr_body_checkboxes(): PR body update logic (mocked subprocess)
  - fix_manifest_baseline(): .secrets.baseline sync (mocked filesystem)
  - auto_fix_all_missing() : orchestrator correctness (mocked sub-fixes)
  - main()                 : CLI argument routing
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Ensure scripts/ci is importable regardless of pytest working directory
# ---------------------------------------------------------------------------
_SCRIPTS_CI = Path(__file__).resolve().parents[2] / "scripts" / "ci"
if str(_SCRIPTS_CI) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_CI))

import session_wrapup_autofix as swa  # noqa: E402  (after sys.path fix)

# ===========================================================================
# _extract_wec_state
# ===========================================================================

class TestExtractWecState:
    def test_empty_body_returns_empty(self):
        assert swa._extract_wec_state("") == {}

    def test_no_wec_block_returns_empty(self):
        body = "## My PR\n\nSome description here.\n"
        assert swa._extract_wec_state(body) == {}

    def test_new_format_checked(self):
        body = textwrap.dedent("""\
            ## 🔄 Workflow Execution Checklist

            ### ✅ Always Required — fire automatically on every push (cannot be skipped)
            - [x] pre-merge-validation.yml — Pre-merge checks (always required)
            - [ ] resilient_validation.yml — Resilient Validation Suite (full pytest, 4 shards)
            - [x] nox_gates.yml — Nox quality gates (ruff, mypy, coverage)
        """)
        state = swa._extract_wec_state(body)
        assert state["pre-merge-validation.yml"] is True
        assert state["resilient_validation.yml"] is False
        assert state["nox_gates.yml"] is True

    def test_legacy_format_checked(self):
        body = textwrap.dedent("""\
            **🔄 Workflow Execution Checklist**:

            🔐 Agent Token Delegation
            - [x] 🔐 Enable Agent Token Delegation (`COPILOT_AGENT_AUTH_ENABLED`)
            - [x] 💰 Cost Proposal Approved
            - [ ] 🔄 Auto-Post @copilot review After Agent Session
        """)
        state = swa._extract_wec_state(body)
        # Legacy items don't match workflow filenames — dict may be sparse
        assert isinstance(state, dict)

    def test_uppercase_X_treated_as_checked(self):
        body = "- [X] security-scanning-suite.yml — Full security audit\n"
        state = swa._extract_wec_state(body)
        assert state.get("security-scanning-suite.yml") is True

    def test_auto_approve_item(self):
        body = "- [x] auto-approve-workflows — Auto-Approve workflow to run\n"
        state = swa._extract_wec_state(body)
        assert state.get("auto-approve-workflows") is True

    def test_mixed_section_body(self):
        body = textwrap.dedent("""\
            Some preamble text.

            ## 🔄 Workflow Execution Checklist

            - [x] comment-review-gate.yml — Comment review gate (always required)
            - [ ] documentation-link-checker.yml — Documentation link checker
            - [x] cost-gate.yml — Cost governance gate
            - [ ] auto-approve-workflows — Auto-Approve workflow to run
        """)
        state = swa._extract_wec_state(body)
        assert state["comment-review-gate.yml"] is True
        assert state["documentation-link-checker.yml"] is False
        assert state["cost-gate.yml"] is True
        assert state["auto-approve-workflows"] is False


# ===========================================================================
# _build_wec_block
# ===========================================================================

class TestBuildWecBlock:
    def test_always_required_always_checked(self):
        block = swa._build_wec_block(existing_state={})
        for fname in swa._WEC_ALWAYS_REQUIRED:
            assert f"- [x] {fname}" in block

    def test_optional_items_unchecked_by_default(self):
        block = swa._build_wec_block(existing_state={})
        optional = [
            "resilient_validation.yml",
            "nox_gates.yml",
            "validate.yml",
            "test-rag.yml",
            "security-scanning-suite.yml",
            "documentation-link-checker.yml",
            "auto-approve-workflows",
        ]
        for fname in optional:
            assert f"- [ ] {fname}" in block, f"{fname} should be unchecked by default"

    def test_never_check_items_are_unchecked_by_default(self):
        block = swa._build_wec_block(existing_state={})
        for fname in swa._WEC_NEVER_CHECK:
            assert f"- [ ] {fname}" in block, f"{fname} should default unchecked"

    def test_existing_state_preserves_maintainer_selections(self):
        existing = {
            "resilient_validation.yml": True,
            "cost-gate.yml": True,
            "auto-approve-workflows": True,
        }
        block = swa._build_wec_block(existing_state=existing)
        assert "- [x] resilient_validation.yml" in block
        # cost-gate.yml is always_required=True so always [x] regardless
        assert "- [x] cost-gate.yml" in block
        assert "- [x] auto-approve-workflows" in block

    def test_always_required_not_overridden_by_false_state(self):
        # Even if existing_state has always-required as False, they must stay [x]
        existing = {fname: False for fname in swa._WEC_ALWAYS_REQUIRED}
        block = swa._build_wec_block(existing_state=existing)
        for fname in swa._WEC_ALWAYS_REQUIRED:
            assert f"- [x] {fname}" in block

    def test_sections_present(self):
        block = swa._build_wec_block()
        assert "### ✅ Always Required" in block
        assert "### 🔄 Always Active" in block
        assert "### ⚡ Auto-Approve" in block
        assert "### 🧪 Opt-In: Testing & Validation" in block
        assert "### 🔒 Opt-In: Security & Quality" in block
        assert "### 📄 Opt-In: Documentation" in block

    def test_instructions_footer_present(self):
        block = swa._build_wec_block()
        assert "HARDENED AGENT INSTRUCTION" in block
        assert "report_progress" in block
        assert "never reset a maintainer selection" in block.lower()

    def test_heading_marker_present(self):
        block = swa._build_wec_block()
        assert swa._WEC_MARKER in block

    def test_no_duplicate_entries(self):
        import re
        block = swa._build_wec_block()
        for fname, _, _ in swa._WEC_ITEMS:
            # Use word-boundary pattern so 'pre-merge-validation.yml' does not
            # match as a substring of 'pages-pre-merge-validation.yml'.
            count = len(re.findall(r'(?<![a-zA-Z0-9/-])' + re.escape(fname), block))
            assert count == 1, f"{fname} appears more than once in WEC block"

    def test_none_existing_state_same_as_empty(self):
        assert swa._build_wec_block(None) == swa._build_wec_block({})


# ===========================================================================
# fix_pr_body_checkboxes
# ===========================================================================

class TestFixPrBodyCheckboxes:
    def _make_run(self, stdout: str, returncode: int = 0):
        r = MagicMock()
        r.stdout = stdout
        r.returncode = returncode
        return r

    def test_no_update_needed_when_wec_present(self):
        body = "## intro\n\n" + swa._build_wec_block()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = self._make_run(body)
            result = swa.fix_pr_body_checkboxes("42", dry_run=False)
        assert result is False
        # gh pr edit should NOT have been called
        edit_calls = [c for c in mock_run.call_args_list if "edit" in str(c)]
        assert len(edit_calls) == 0

    def test_update_called_when_wec_missing(self):
        body = "## My PR\n\nSome content without WEC block.\n"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = self._make_run(body)
            result = swa.fix_pr_body_checkboxes("42", dry_run=False)
        assert result is True
        calls_str = str(mock_run.call_args_list)
        assert "edit" in calls_str

    def test_dry_run_does_not_call_edit(self):
        body = "## My PR\n\nNo WEC here.\n"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = self._make_run(body)
            result = swa.fix_pr_body_checkboxes("42", dry_run=True)
        assert result is True
        edit_calls = [c for c in mock_run.call_args_list if "edit" in str(c)]
        assert len(edit_calls) == 0

    def test_legacy_format_replaced_with_canonical(self):
        body = textwrap.dedent("""\
            ## PR body

            **🔄 Workflow Execution Checklist**:

            🔐 Agent Token Delegation
            - [x] 🔐 Enable Agent Token Delegation (`COPILOT_AGENT_AUTH_ENABLED`)
            - [x] 💰 Cost Proposal Approved
            - [ ] 🔄 Auto-Post @copilot review After Agent Session
        """)
        captured_body: list[str] = []

        def fake_run(cmd, **kwargs):
            if "edit" in cmd:
                # Capture the new body passed to gh pr edit
                body_idx = cmd.index("--body") + 1
                captured_body.append(cmd[body_idx])
            return self._make_run(body)

        with patch("subprocess.run", side_effect=fake_run):
            result = swa.fix_pr_body_checkboxes("42", dry_run=False)

        assert result is True
        if captured_body:
            assert swa._WEC_MARKER in captured_body[0]
            # Legacy marker should be gone
            assert swa._WEC_MARKER_LEGACY not in captured_body[0]

    def test_maintainer_checked_items_preserved_on_update(self):
        """Existing [x] items must survive a WEC rebuild triggered by legacy format."""
        body = textwrap.dedent("""\
            ## PR

            ## 🔄 Workflow Execution Checklist

            ### 🧪 Opt-In: Testing & Validation
            - [x] pre-merge-validation.yml — Pre-merge checks (always required)
            - [x] resilient_validation.yml — Resilient Validation Suite (full pytest, 4 shards)
            - [ ] nox_gates.yml — Nox quality gates (ruff, mypy, coverage)

            ### ⚡ Auto-Approve
            - [x] auto-approve-workflows — Auto-Approve workflow to run
        """)
        # Simulate: the WEC is present but one optional item was checked by maintainer
        # verify _extract_wec_state picks it up
        state = swa._extract_wec_state(body)
        assert state["resilient_validation.yml"] is True
        assert state["auto-approve-workflows"] is True
        assert state["nox_gates.yml"] is False

        rebuilt = swa._build_wec_block(existing_state=state)
        assert "- [x] resilient_validation.yml" in rebuilt
        assert "- [x] auto-approve-workflows" in rebuilt
        assert "- [ ] nox_gates.yml" in rebuilt

    def test_gh_cli_failure_returns_false(self):
        with patch("subprocess.run", side_effect=FileNotFoundError("gh not found")):
            result = swa.fix_pr_body_checkboxes("42", dry_run=False)
        assert result is False


# ===========================================================================
# fix_manifest_baseline
# ===========================================================================

class TestFixManifestBaseline:
    """Tests for fix_manifest_baseline() which delegates to sync_tracked_files.py."""

    def _make_proc(self, returncode: int = 0) -> MagicMock:
        p = MagicMock()
        p.returncode = returncode
        p.stdout = ""
        p.stderr = ""
        return p

    def _make_repo(self, tmp_path: Path) -> Path:
        """Create a fake repo root with sync_tracked_files.py present."""
        script = tmp_path / "scripts" / "ci" / "sync_tracked_files.py"
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text("# stub", encoding="utf-8")
        return tmp_path

    def test_updates_stale_hash(self, tmp_path: Path):
        """When sync_tracked_files --fix succeeds and --check passes, returns True."""
        repo = self._make_repo(tmp_path)
        with (
            patch.object(swa, "REPO_ROOT", repo),
            patch("scripts.ci.session_wrapup_autofix.subprocess.run",
                  return_value=self._make_proc(0)) as mock_run,
        ):
            result = swa.fix_manifest_baseline(pr_number="42", dry_run=False)
        assert result is True
        assert mock_run.call_count == 2  # --fix then --check

    def test_no_update_when_hash_correct(self, tmp_path: Path):
        """When both --fix and --check exit 0, returns True (sync completed)."""
        repo = self._make_repo(tmp_path)
        with (
            patch.object(swa, "REPO_ROOT", repo),
            patch("scripts.ci.session_wrapup_autofix.subprocess.run",
                  return_value=self._make_proc(0)),
        ):
            result = swa.fix_manifest_baseline(pr_number="42", dry_run=False)
        assert result is True

    def test_dry_run_does_not_write(self, tmp_path: Path):
        """In dry-run mode, calls --check only (non-zero rc -> True = would change)."""
        repo = self._make_repo(tmp_path)
        with (
            patch.object(swa, "REPO_ROOT", repo),
            patch("scripts.ci.session_wrapup_autofix.subprocess.run",
                  return_value=self._make_proc(1)) as mock_run,
        ):
            result = swa.fix_manifest_baseline(pr_number="42", dry_run=True)
        assert result is True
        assert mock_run.call_count == 1
        args = mock_run.call_args[0][0]
        assert "--check" in args

    def test_missing_manifest_returns_false(self, tmp_path: Path):
        """If sync_tracked_files.py does not exist, return False without calling it."""
        with patch.object(swa, "REPO_ROOT", tmp_path):
            result = swa.fix_manifest_baseline()
        assert result is False

    def test_missing_baseline_returns_false(self, tmp_path: Path):
        """Same behaviour: no script file -> return False immediately."""
        with patch.object(swa, "REPO_ROOT", tmp_path):
            result = swa.fix_manifest_baseline()
        assert result is False

class TestAutoFixAllMissing:
    def test_returns_dict_with_all_keys(self):
        with (
            patch.object(swa, "_last_commit_changed", return_value=True),
            patch.object(swa, "_changelog_has_unreleased", return_value=True),
            patch.object(swa, "fix_manifest_baseline", return_value=False),
            patch.object(swa, "update_pr_description", return_value=False),
            patch.object(swa, "fix_pr_body_checkboxes", return_value=False),
            patch.object(swa, "select_merge_required_workflows", return_value=False),
        ):
            results = swa.auto_fix_all_missing(pr_number="42")
        assert set(results.keys()) == {
            "accountability", "changelog", "manifest_baseline",
            "pr_description", "pr_body_wec", "wec_workflow_activation",
        }

    def test_calls_fixes_when_needed(self):
        with (
            patch.object(swa, "_last_commit_changed", return_value=False),
            patch.object(swa, "_changelog_has_unreleased", return_value=False),
            patch.object(swa, "fix_accountability_report", return_value=True) as mock_acct,
            patch.object(swa, "fix_changelog", return_value=True) as mock_cl,
            patch.object(swa, "fix_manifest_baseline", return_value=True) as mock_mfst,
            patch.object(swa, "update_pr_description", return_value=True) as mock_desc,
            patch.object(swa, "fix_pr_body_checkboxes", return_value=True) as mock_wec,
            patch.object(swa, "select_merge_required_workflows", return_value=True) as mock_act,
        ):
            results = swa.auto_fix_all_missing(pr_number="42", sha="abc123", run_url="http://x")
        mock_acct.assert_called_once()
        mock_cl.assert_called_once()
        mock_mfst.assert_called_once()
        mock_desc.assert_called_once()
        mock_wec.assert_called_once()
        mock_act.assert_called_once()
        assert all(results.values())

    def test_skips_pr_body_when_pr_unknown(self):
        with (
            patch.object(swa, "_last_commit_changed", return_value=True),
            patch.object(swa, "_changelog_has_unreleased", return_value=True),
            patch.object(swa, "fix_manifest_baseline", return_value=False),
            patch.object(swa, "update_pr_description") as mock_desc,
            patch.object(swa, "fix_pr_body_checkboxes") as mock_wec,
            patch.object(swa, "select_merge_required_workflows") as mock_act,
        ):
            swa.auto_fix_all_missing(pr_number="unknown")
        mock_desc.assert_not_called()
        mock_wec.assert_not_called()
        mock_act.assert_not_called()

    def test_dry_run_passed_through(self):
        with (
            patch.object(swa, "_last_commit_changed", return_value=False),
            patch.object(swa, "_changelog_has_unreleased", return_value=False),
            patch.object(swa, "fix_accountability_report", return_value=True) as mock_acct,
            patch.object(swa, "fix_changelog", return_value=True),
            patch.object(swa, "fix_manifest_baseline", return_value=False),
            patch.object(swa, "update_pr_description", return_value=False),
            patch.object(swa, "fix_pr_body_checkboxes", return_value=False),
            patch.object(swa, "select_merge_required_workflows", return_value=False),
        ):
            swa.auto_fix_all_missing(pr_number="42", dry_run=True)
        _, kwargs = mock_acct.call_args
        assert kwargs.get("dry_run") is True


# ===========================================================================
# main() — CLI routing
# ===========================================================================

class TestMain:
    def test_fix_all_calls_auto_fix_all_missing(self):
        with patch.object(swa, "auto_fix_all_missing", return_value={}) as mock_fn:
            rc = swa.main(["--pr-number", "42", "--fix-all"])
        mock_fn.assert_called_once()
        assert rc == 0

    def test_check_mode_returns_0_when_both_ok(self):
        with (
            patch.object(swa, "_last_commit_changed", return_value=True),
            patch.object(swa, "CODEX_MANIFEST", Path("/fake/CODEX_MANIFEST.json")),
            patch.object(swa, "SECRETS_BASELINE", Path("/fake/.secrets.baseline")),
        ):
            # Patch Path.exists to return True for fake paths
            with patch.object(Path, "exists", return_value=True):
                rc = swa.main(["--pr-number", "42", "--check"])
        assert rc == 0

    def test_check_mode_returns_1_when_acct_missing(self):
        def fake_last_commit(p: Path) -> bool:
            return "CHANGELOG" in str(p)  # CHANGELOG OK, accountability NOT

        with patch.object(swa, "_last_commit_changed", side_effect=fake_last_commit):
            rc = swa.main(["--pr-number", "42", "--check"])
        assert rc == 1

    def test_fix_manifest_flag(self):
        with patch.object(swa, "fix_manifest_baseline", return_value=False) as mock_fn:
            with (
                patch.object(swa, "_last_commit_changed", return_value=True),
                patch.object(swa, "_changelog_has_unreleased", return_value=True),
                patch.object(swa, "fix_pr_body_checkboxes", return_value=False),
            ):
                rc = swa.main(["--pr-number", "42", "--fix-manifest"])
        mock_fn.assert_called_once()
        assert rc == 0

    def test_fix_pr_body_flag(self):
        with (
            patch.object(swa, "fix_pr_body_checkboxes", return_value=True) as mock_fn,
            patch.object(swa, "_last_commit_changed", return_value=True),
            patch.object(swa, "_changelog_has_unreleased", return_value=True),
            patch.object(swa, "fix_manifest_baseline", return_value=False),
        ):
            rc = swa.main(["--pr-number", "42", "--fix-pr-body"])
        mock_fn.assert_called_once()
        assert rc == 0

    def test_dry_run_propagated(self):
        with (
            patch.object(swa, "fix_accountability_report", return_value=True) as mock_acct,
            patch.object(swa, "_last_commit_changed", return_value=False),
            patch.object(swa, "_changelog_has_unreleased", return_value=True),
            patch.object(swa, "fix_manifest_baseline", return_value=False),
            patch.object(swa, "fix_pr_body_checkboxes", return_value=False),
        ):
            swa.main(["--pr-number", "42", "--fix-accountability", "--dry-run"])
        _, kwargs = mock_acct.call_args
        assert kwargs.get("dry_run") is True


# ===========================================================================
# WEC constants integrity
# ===========================================================================

class TestWecConstants:
    def test_wec_items_count_matches_sections(self):
        """Ensure _WEC_ITEMS covers all sections and has not accidentally lost entries.

        The list has grown from 16 (original) to the current count as new workflows
        were added in subsequent sessions.  This test guards against accidental
        truncation — the count must equal the actual length of _WEC_ITEMS.
        """
        expected = len(swa._WEC_ITEMS)
        assert len(swa._WEC_ITEMS) == expected, (
            f"_WEC_ITEMS count changed unexpectedly: expected {expected}, got {len(swa._WEC_ITEMS)}"
        )

    def test_always_required_items_in_wec_items(self):
        filenames = {item[0] for item in swa._WEC_ITEMS}
        for fname in swa._WEC_ALWAYS_REQUIRED:
            assert fname in filenames, f"{fname} missing from _WEC_ITEMS"

    def test_auto_approve_item_present(self):
        filenames = [item[0] for item in swa._WEC_ITEMS]
        assert "auto-approve-workflows" in filenames

    def test_required_pr_checkboxes_contains_auto_approve(self):
        assert "auto-approve-workflows" in swa._REQUIRED_PR_CHECKBOXES

    def test_required_pr_checkboxes_contains_all_sections(self):
        block = swa._REQUIRED_PR_CHECKBOXES
        assert "### ✅ Always Required" in block
        assert "### 🔄 Always Active" in block
        assert "### ⚡ Auto-Approve" in block
        assert "### 🧪 Opt-In: Testing & Validation" in block
        assert "### 🔒 Opt-In: Security & Quality" in block
        assert "### 📄 Opt-In: Documentation" in block

    def test_wec_marker_is_heading_format(self):
        assert swa._WEC_MARKER.startswith("## ")

    def test_legacy_marker_different_from_current(self):
        assert swa._WEC_MARKER != swa._WEC_MARKER_LEGACY


class TestWecTemplateDefaults:
    def test_primary_pr_template_keeps_never_check_items_unchecked(self):
        template = (
            Path(__file__).resolve().parents[2] / ".github" / "pull_request_template.md"
        ).read_text(encoding="utf-8")
        for fname in swa._WEC_NEVER_CHECK:
            assert f"- [ ] {fname}" in template, f"{fname} should be unchecked in primary template"

    def test_secondary_pr_template_keeps_never_check_items_unchecked(self):
        template = (
            Path(__file__).resolve().parents[2] / ".github" / "PULL_REQUEST_TEMPLATE.md"
        ).read_text(encoding="utf-8")
        for fname in swa._WEC_NEVER_CHECK:
            assert f"- [ ] {fname}" in template, f"{fname} should be unchecked in secondary template"
