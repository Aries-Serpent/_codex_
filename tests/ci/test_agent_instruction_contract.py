"""Regressions for scoped preparation, not claims about hosted permissions."""

import re
from pathlib import Path

import pytest
import yaml

from scripts.ci import check_no_deferral_security as security_evidence

ROOT = Path(__file__).resolve().parents[2]

CURRENT_GUIDANCE = (
    ".codex/CODEBASE_AGENCY_POLICY.md",
    ".github/copilot-instructions.md",
    ".github/AGENTS.md",
    ".github/agents/COPILOT_HARDENED_PLANNING_PROTOCOL.md",
    ".github/agents/policy-coach-agent.md",
    ".github/agents/docs/AGENTS.md",
    ".codex/docs/COPILOT_AGENT_PROMPT_GUIDE.md",
    ".github/copilot-prompts/active/SESSION-DIAGNOSTIC-PROTOCOL.md",
)


@pytest.mark.parametrize("path", CURRENT_GUIDANCE)
def test_current_guidance_does_not_reimpose_superseded_global_rituals(path):
    text = (ROOT / path).read_text()
    forbidden = (
        r"(?i)you MUST resolve ALL issues",
        r"(?i)minimum 5 (?:self-review|iteration|attempt)",
        r"(?i)every session MUST launch",
        r"(?i)dispatch ALL independent agents.*FIRST response",
        r"(?i)manual shell scripting.*prohibited",
        r"(?i)first line MUST start with.*@copilot",
        r"(?i)LOAD all stored session memories.*store_memory",
    )
    assert not any(re.search(pattern, text) for pattern in forbidden)


@pytest.mark.parametrize(
    "path",
    (
        "docs/guides/AGENTS.md",
        "prompts/AGENTS.md",
        "scripts/AGENTS.md",
        "src/mcp/AGENTS.md",
    ),
)
def test_scoped_guides_link_current_policy_not_archived_main(path):
    text = (ROOT / path).read_text()
    assert "archive/deprecated/AGENTS.md" not in text
    assert "CODEBASE_AGENCY_POLICY.md" in text


def test_profile_integrations_do_not_require_public_or_shared_state_writes():
    injector = (ROOT / ".github/agents/cognitive-brain-session-injector.md").read_text()
    assert "Public continuation\\nexplicitly authorized?" in injector
    assert "local/read-only completion does not require a public comment" in injector
    qa = (ROOT / ".github/agents/qa-walkthrough-agent.md").read_text()
    assert "The agent **must** collect CI artifacts from the last 5" not in qa
    assert "The agent **must** call `TopologyManager.register_scan_result()`" not in qa
    assert "For read-only work," in qa


@pytest.mark.parametrize(
    "path",
    (
        ".codex/AGENTIC_REPO_STATE.md",
        "docs/ci/GITHUB_API_COPILOT_AGENT_REFERENCE.md",
        "docs/reference/GITHUB_VARIABLES_SECRETS_REFERENCE.md",
        ".codex/docs/GITHUB_API_AND_MCP_REFERENCE.md",
        ".codex/docs/COPILOT_MCP_TOOL_REFERENCE.md",
    ),
)
def test_authority_references_do_not_assert_unqualified_admin_or_ttl_grants(path):
    # Narrow negative regression; not an authorization audit or profile-load test.
    # Dates/historical snapshots and explicit denials are not affirmative grants.
    text = (ROOT / path).read_text()
    claims = (
        r"(?im)^\s*(?:[-*>]\s*)*(?:\*\*)?(?:Authority|Authorization)"
        r"(?: level)?(?:\*\*)?\s*:\s*(?:\*\*)?"
        r"(?:full.admin|all.branches|unrestricted)",
        r"(?im)^\s*(?:[-*]\s*)?(?:A |The )?(?:session )?TTL "
        r"(?:grants|waives|bypasses) (?:all )?(?:approval|permission|admin)",
    )
    assert not any(re.search(pattern, text) for pattern in claims)


@pytest.mark.parametrize(
    "path",
    (
        ".github/workflows/deferral-language-gate.yml",
        ".github/workflows/strict-no-deferral-security.yml",
    ),
)
def test_existing_workflow_wording_scans_are_advisory(path):
    workflow = yaml.safe_load((ROOT / path).read_text())
    runs = [
        step.get("run", "") for job in workflow["jobs"].values() for step in job.get("steps", [])
    ]
    scanner_lines = [
        line
        for run in runs
        for line in re.sub(r"\\\n\s*", " ", run).splitlines()
        if "python scripts/ci/check_deferral_language.py" in line
    ]
    assert scanner_lines
    assert all("--warn-only" in line for line in scanner_lines)


def test_security_owner_reason_checks_remain_blocking_with_scoped_handoff(tmp_path):
    path = tmp_path / "security-exceptions.md"
    path.write_text(
        "### Exception ID: SEC-1\n**Status**: OPEN\n"
        "**Owner**: security-team\n**Reason**: Fix is out of scope for read-only "
        "analysis; execution awaits owner approval. Mitigation is documented.\n"
    )
    assert security_evidence.validate_exceptions(path) == []
    path.write_text("### Exception ID: SEC-1\n**Status**: OPEN\n")
    errors = security_evidence.validate_exceptions(path)
    assert any("Owner" in error for error in errors)
    assert any("Reason" in error for error in errors)


def test_security_matrix_classification_requirement_is_not_removed(tmp_path):
    path = tmp_path / "security-open-findings-matrix.md"
    path.write_text("No owner/reason contract.\n")
    assert security_evidence.validate_matrix(path)


def test_healing_engine_approver_contract_is_unchanged():
    # JSON-like AST literals avoid importing the execution engine or invoking actions.
    import ast

    source = ROOT / "src/orchestration/healing/policy_tier_engine.py"
    tree = ast.parse(source.read_text())
    definitions = next(
        ast.literal_eval(node.value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "TIER_DEFINITIONS"
            for target in node.targets
        )
    )
    assert definitions["T2"]["required_approvers"] == ["security-reviewer", "code-owner"]
    assert definitions["T3"]["required_approvers"] == [
        "@mbaetiong",
        "stakeholder_1",
        "stakeholder_2",
    ]


def test_scope_advice_does_not_make_cli_security_classification_optional(tmp_path, monkeypatch):
    missing = tmp_path / "security-exceptions.md"
    missing.write_text("### Exception ID: SEC-1\n**Status**: OPEN\n")
    monkeypatch.setattr(
        "sys.argv",
        ["check", "--paths", str(missing), "--text", "This fix is out of scope."],
    )
    assert security_evidence.main() == 1
