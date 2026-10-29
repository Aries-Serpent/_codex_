import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.ci import session_wrapup_autofix as swa


def test_accountability_report_targets_active_report():
    assert swa.ACCOUNTABILITY_REPORT == (
        _REPO_ROOT / "docs" / "accountability" / "AGENT_ACCOUNTABILITY_REPORT.md"
    )


def test_accountability_report_is_current_when_recent_entry_is_at_top(tmp_path, monkeypatch):
    report = tmp_path / "AGENT_ACCOUNTABILITY_REPORT.md"
    today = swa.datetime.now(tz=swa.timezone.utc).strftime("%Y-%m-%d")
    report.write_text(f"## Session: {today} — current session\n" + "older\n" * 200)
    monkeypatch.setattr(swa, "ACCOUNTABILITY_REPORT", report)

    assert swa._accountability_report_is_current()


def test_accountability_report_requires_recent_date_on_session_heading(
    tmp_path, monkeypatch
):
    report = tmp_path / "AGENT_ACCOUNTABILITY_REPORT.md"
    today = swa.datetime.now(tz=swa.timezone.utc).strftime("%Y-%m-%d")
    report.write_text(f"## Session: 2020-01-01 — old session\nToday is {today}.\n")
    monkeypatch.setattr(swa, "ACCOUNTABILITY_REPORT", report)

    assert not swa._accountability_report_is_current()


def test_direct_execution_is_valid_without_registry_or_delegates(monkeypatch):
    monkeypatch.setattr(swa, "_load_registered_agent_ids", lambda: frozenset())
    declaration = swa._DIRECT_EXECUTION_DECLARATION
    assert swa.check_pr_body_agents_used(f"## 🤖 Agents Used\n{declaration}\n") == (True, "")


@pytest.mark.parametrize(
    "declaration",
    [
        "Delegation: not recorded.",
        "- [ ] `real-agent`",
        "- `unknown-agent`",
        "- `real-agent`\n- `made-up-agent`",
        f"{swa._DIRECT_EXECUTION_DECLARATION}\n- `real-agent`",
    ],
)
def test_templates_unknown_agents_and_conflicting_claims_are_not_evidence(
    monkeypatch, declaration
):
    monkeypatch.setattr(swa, "_load_registered_agent_ids", lambda: frozenset({"real-agent"}))
    assert not swa.check_pr_body_agents_used(f"## 🤖 Agents Used\n{declaration}\n")[0]


def test_checked_actual_agent_ids_are_valid(monkeypatch):
    monkeypatch.setattr(swa, "_load_registered_agent_ids", lambda: frozenset({"real-agent"}))
    assert swa.check_pr_body_agents_used("## 🤖 Agents Used\n- [x] `real-agent`\n")[0]


def test_missing_registry_does_not_validate_arbitrary_agent_ids(monkeypatch):
    monkeypatch.setattr(swa, "_load_registered_agent_ids", lambda: frozenset())
    assert not swa.check_pr_body_agents_used("## 🤖 Agents Used\n- `made-up-agent`\n")[0]


def test_req14_does_not_invent_fallback_agents(tmp_path, monkeypatch):
    report = tmp_path / "report.md"
    content = "# Session\nNo delegation recorded.\n"
    report.write_text(content)
    monkeypatch.setattr(swa, "ACCOUNTABILITY_REPORT", report)
    assert not swa.fix_req14_agents_used()
    assert report.read_text() == content
    assert "session-analysis-agent" not in report.read_text()


def test_explicit_direct_fix_replaces_invalid_section_and_preserves_other_content(
    tmp_path, monkeypatch
):
    report = tmp_path / "report.md"
    report.write_text("# Session\n### Agents Used\n- `unknown-agent`\n### Checks\nKept.\n")
    monkeypatch.setattr(swa, "ACCOUNTABILITY_REPORT", report)
    assert swa.fix_req14_agents_used(direct_execution=True)
    assert swa.check_req14_agents_used()
    assert "### Checks\nKept." in report.read_text()
    assert "unknown-agent" not in report.read_text()
    assert not swa.fix_req14_agents_used(direct_execution=True)


@pytest.mark.parametrize("arguments", [[], ["--check"], ["--check", "--no-pr", "--direct-execution"]])
def test_local_no_pr_mode_does_not_require_or_mutate_pr_bookkeeping(
    tmp_path, monkeypatch, arguments
):
    monkeypatch.setattr(swa, "_short_sha", lambda: "local")

    def unexpected(*args, **kwargs):
        pytest.fail("Local/no-PR mode must not invoke PR bookkeeping or remote operations")

    for name in (
        "_accountability_report_is_current", "_changelog_is_current",
        "check_req14_agents_used", "fix_req14_agents_used",
        "fix_manifest_baseline", "fix_pr_body_checkboxes",
    ):
        monkeypatch.setattr(swa, name, unexpected)
    monkeypatch.setattr(swa.subprocess, "run", unexpected)
    assert swa.main(arguments) == 0


def test_no_pr_rejects_remote_mutation_mode_before_calling_it(monkeypatch):
    with pytest.raises(SystemExit) as error:
        swa.main(["--no-pr", "--fix-pr-body"])
    assert error.value.code == 2


def test_wec_template_does_not_claim_any_delegated_agent():
    assert not swa.check_pr_body_agents_used(swa._REQUIRED_PR_CHECKBOXES)[0]
    assert "- [ ] `ci-testing-agent`" not in swa._REQUIRED_PR_CHECKBOXES


def test_wec_repair_preserves_existing_actual_agent_attestation(monkeypatch):
    body = "## Work\nPrepared patch.\n\n## 🤖 Agents Used\n- `real-agent`\n"
    edited = []

    def fake_run(command, **kwargs):
        if command[:3] == ["gh", "pr", "view"]:
            return swa.subprocess.CompletedProcess(command, 0, stdout=body)
        assert command[:3] == ["gh", "pr", "edit"]
        edited.append(command[command.index("--body") + 1])
        return swa.subprocess.CompletedProcess(command, 0, stdout="")

    monkeypatch.setattr(swa.subprocess, "run", fake_run)
    monkeypatch.setattr(swa, "_detect_human_grants", lambda *args: {})
    monkeypatch.setattr(swa, "_record_agent_wec_write", lambda *args, **kwargs: None)
    monkeypatch.setattr(swa, "_load_registered_agent_ids", lambda: frozenset({"real-agent"}))
    assert swa.fix_pr_body_checkboxes("42")
    assert edited and swa.check_pr_body_agents_used(edited[0])[0]
    assert edited[0].count("- `real-agent`") == 1


@pytest.mark.parametrize("ok", [True, False])
def test_generated_handoff_does_not_ping_or_invent_workflow_tasks(ok):
    handoff = swa._build_followup_prompt_md({"dimensions": [("local lint", 1, "result", ok)]})
    assert "@copilot" not in handoff
    assert "--fix-all" not in handoff
    assert "--activate-workflows" not in handoff
    assert "create .github/workflows" not in handoff
    assert ("local lint" in handoff) is not ok


def test_pr_generator_keeps_recorded_direct_execution(monkeypatch):
    monkeypatch.setattr(swa, "_compute_merge_readiness_score", lambda: {"dimensions": []})
    monkeypatch.setattr(swa, "_build_recent_changes_md", lambda: "Local patch")
    monkeypatch.setattr(swa, "_build_scorecard_md", lambda data: "Diagnostic only")
    body = f"## 🤖 Agents Used\n{swa._DIRECT_EXECUTION_DECLARATION}\n"
    generated = swa._build_meaningful_pr_body("42", {}, body)
    assert swa.check_pr_body_agents_used(generated)[0]


@pytest.mark.parametrize(
    "suffix",
    ["", "\n---", "\n \t--- \t\n\n---", "\n---" + "\n\n---" * 10000],
)
def test_agent_attestation_strips_only_trailing_separator_lines(suffix):
    attestation = "## 🤖 Agents Used\n- `real-agent`"
    body = attestation + suffix + "\n\n" + swa._WEC_MARKER
    generated = swa._preserve_agent_attestation(swa._REQUIRED_PR_CHECKBOXES, body)
    assert attestation + "\n\n---\n\n" + swa._WEC_MARKER in generated
    assert generated.count("- `real-agent`") == 1


@pytest.mark.parametrize(
    "suffix",
    ["inline---", "\n---" + "\n\n---" * 10000 + "\nnot-a-separator"],
)
def test_agent_attestation_preserves_non_separator_content(suffix):
    attestation = "## 🤖 Agents Used\n- `real-agent`\n" + suffix
    generated = swa._preserve_agent_attestation(swa._REQUIRED_PR_CHECKBOXES, attestation)
    assert attestation + "\n\n---\n\n" + swa._WEC_MARKER in generated
