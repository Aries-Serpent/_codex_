"""Ensure CodeQL gate messages treat GitHub metadata as data, not source."""

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

_WORKFLOW = Path(__file__).resolve().parents[2] / ".github/workflows/codeql-ga-gate.yml"


def test_github_script_does_not_interpolate_github_context():
    workflow = yaml.safe_load(_WORKFLOW.read_text())
    for job in workflow["jobs"].values():
        for step in job.get("steps", []):
            if step.get("uses", "").startswith("actions/github-script@"):
                assert not re.search(r"\$\{\{\s*github\.", step["with"]["script"])


@pytest.mark.parametrize(
    "ref",
    [
        "refs/heads/main",
        "refs/heads/${(globalThis.injected=true)}",
        "refs/heads/`;globalThis.injected=true;//",
    ],
)
def test_security_issue_keeps_hostile_ref_as_data(ref):
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is required to exercise github-script")
    workflow = yaml.safe_load(_WORKFLOW.read_text())
    step = next(
        step
        for step in workflow["jobs"]["create-issue-on-alert"]["steps"]
        if step["name"] == "Create Security Alert Issue"
    )
    script = re.sub(r"\$\{\{[^}]+\}\}", "0", step["with"]["script"])
    context = {
        "ref": ref,
        "sha": "abc123",
        "actor": "test-actor",
        "repo": {"owner": "test-owner", "repo": "test-repo"},
    }
    harness = (
        """
        (async () => {
            const context = JSON.parse(process.env.TEST_CONTEXT);
            let body;
            const github = {rest: {issues: {create: async (issue) => {
                body = issue.body;
                return {data: {html_url: 'https://example.com/issue'}};
            }}}};
    """
        + script
        + """
            process.stdout.write(JSON.stringify({
                body, injected: globalThis.injected === true
            }));
        })().catch(error => { console.error(error); process.exitCode = 1; });
    """
    )
    result = subprocess.run(
        [node],
        input=harness,
        text=True,
        capture_output=True,
        check=True,
        env={**os.environ, "TEST_CONTEXT": json.dumps(context)},
        timeout=10,
    )
    output = json.loads(result.stdout.splitlines()[-1])
    assert ref in output["body"]
    assert "@test-actor" in output["body"]
    assert output["injected"] is False


@pytest.mark.parametrize(
    "ref",
    [
        "refs/heads/release/$(touch${IFS}injected)",
        "refs/heads/release/`touch${IFS}injected`",
        'refs/heads/quotes"and\\backslashes\n',
    ],
)
@pytest.mark.parametrize("blocked", ["true", "false"])
def test_audit_values_remain_json_data(tmp_path, ref, blocked):
    workflow = yaml.safe_load(_WORKFLOW.read_text())
    step = next(
        step
        for step in workflow["jobs"]["codeql-analysis"]["steps"]
        if step["name"] == "Log Gate Decision to Audit Trail"
    )
    assert "${{" not in step["run"]
    reason = 'reason with "quotes", \\slashes and\nnewlines'
    env = {
        **os.environ,
        "GITHUB_EVENT_NAME": "push",
        "GITHUB_REPOSITORY": "owner/repo",
        "GITHUB_REF": ref,
        "GITHUB_SHA": "abc123",
        "GITHUB_ACTOR": "test-actor",
        "GATE_PR_NUMBER": "-1",
        "GATE_STATUS": "FAIL",
        "GATE_BLOCKED": blocked,
        "GATE_REASON": reason,
        "GATE_CRITICAL": "1",
        "GATE_HIGH": "2",
        "GATE_MEDIUM": "3",
        "CODEQL_SEVERITY_THRESHOLD": "high",
        "GATE_DRY_RUN": "false",
    }
    subprocess.run(
        ["bash"],
        input=step["run"],
        text=True,
        capture_output=True,
        check=True,
        cwd=tmp_path,
        env=env,
        timeout=10,
    )
    audit_file = next((tmp_path / ".codex/security/gate_audit").glob("gate_*.json"))
    audit = json.loads(audit_file.read_text())
    assert audit["branch"] == ref
    assert audit["reason"] == reason
    assert audit["blocked"] is (blocked == "true")
    assert audit["dry_run"] is False
    assert audit["critical_alerts"] == 1
    assert audit["pr_number"] == -1
    assert not (tmp_path / "injected").exists()
