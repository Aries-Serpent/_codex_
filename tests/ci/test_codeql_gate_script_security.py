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


def _parse_sarif(tmp_path, run):
    workflow = yaml.safe_load(_WORKFLOW.read_text())
    script = next(
        step["run"]
        for step in workflow["jobs"]["codeql-analysis"]["steps"]
        if step["name"] == "Parse CodeQL Results"
    )
    results = tmp_path / "results"
    results.mkdir()
    (results / "test.sarif").write_text(json.dumps({"runs": [run]}))
    output = tmp_path / "outputs"
    result = subprocess.run(
        ["bash"],
        input=script,
        text=True,
        capture_output=True,
        cwd=tmp_path,
        env={
            **os.environ,
            "GITHUB_OUTPUT": str(output),
            "GITHUB_STEP_SUMMARY": str(tmp_path / "summary"),
        },
        timeout=10,
    )
    return result, output


def test_parser_counts_inherited_driver_and_extension_rule_levels(tmp_path):
    result, output = _parse_sarif(
        tmp_path,
        {
            "tool": {
                "driver": {"rules": [{"id": "shared", "defaultConfiguration": {"level": "note"}}]},
                "extensions": [
                    {"rules": [{"id": "shared", "defaultConfiguration": {"level": "error"}}]}
                ],
            },
            "results": [
                {"ruleId": "shared", "ruleIndex": 0},
                {
                    "ruleId": "shared",
                    "rule": {"id": "shared", "index": 0, "toolComponent": {"index": 0}},
                },
                {"ruleId": "no-descriptor"},
                {"ruleId": "shared", "level": "warning"},
            ],
        },
    )
    assert result.returncode == 0, result.stderr
    assert output.read_text().splitlines() == [
        "critical_count=1",
        "high_count=2",
        "medium_count=1",
        "quality_count=0",
    ]


def test_parser_ranks_security_rules_by_security_severity(tmp_path):
    def rule(rule_id, level, tags, score=None):
        properties = {"tags": tags}
        if score is not None:
            properties["security-severity"] = score
        return {
            "id": rule_id,
            "defaultConfiguration": {"level": level},
            "properties": properties,
        }

    result, output = _parse_sarif(
        tmp_path,
        {
            "tool": {
                "driver": {
                    "rules": [
                        rule("sec-critical", "note", ["security"], "9.8"),
                        rule("sec-high", "warning", ["security", "external/cwe/cwe-020"], "7.8"),
                        rule("sec-medium", "error", ["security"], "5.0"),
                        rule("sec-unscored", "error", ["security"]),
                        rule("quality-error", "error", ["reliability", "correctness"]),
                        {"id": "untagged", "defaultConfiguration": {"level": "warning"}},
                    ]
                }
            },
            "results": [
                {"ruleId": "sec-critical"},
                {"ruleId": "sec-high"},
                {"ruleId": "sec-medium"},
                {"ruleId": "sec-unscored"},
                {"ruleId": "quality-error"},
                {"ruleId": "quality-error", "level": "error"},
                {"ruleId": "untagged"},
            ],
        },
    )
    assert result.returncode == 0, result.stderr
    assert output.read_text().splitlines() == [
        "critical_count=2",
        "high_count=2",
        "medium_count=1",
        "quality_count=2",
    ]


def test_parser_rejects_invalid_rule_component_without_zero_counts(tmp_path):
    result, output = _parse_sarif(
        tmp_path,
        {
            "tool": {"driver": {}},
            "results": [{"rule": {"toolComponent": {"index": 9}}}],
        },
    )
    assert result.returncode != 0
    assert "Invalid SARIF rule toolComponent index" in result.stderr
    assert not output.exists()


@pytest.mark.parametrize("score", ["NaN", "Infinity", -1, 0, 11, True, "invalid", None])
def test_parser_rejects_invalid_security_scores(tmp_path, score):
    result, output = _parse_sarif(
        tmp_path,
        {
            "tool": {
                "driver": {
                    "rules": [
                        {
                            "id": "security",
                            "properties": {"tags": ["correctness"], "security-severity": score},
                        }
                    ]
                }
            },
            "results": [{"ruleId": "security"}],
        },
    )
    assert result.returncode != 0
    assert "Invalid SARIF security-severity" in result.stderr
    assert not output.exists()


@pytest.mark.parametrize(
    ("score", "bucket"),
    [(9, "critical"), (7, "high"), (4, "medium"), (3.9, None)],
)
def test_parser_security_score_overrides_quality_tags_in_extensions(tmp_path, score, bucket):
    result, output = _parse_sarif(
        tmp_path,
        {
            "tool": {
                "driver": {},
                "extensions": [
                    {
                        "rules": [
                            {
                                "id": "security",
                                "defaultConfiguration": {"level": "error"},
                                "properties": {"tags": ["correctness"], "security-severity": score},
                            }
                        ]
                    }
                ],
            },
            "results": [
                {
                    "rule": {"id": "security", "index": 0, "toolComponent": {"index": 0}},
                }
            ],
        },
    )
    assert result.returncode == 0, result.stderr
    counts = dict(line.split("=") for line in output.read_text().splitlines())
    assert counts == {
        "critical_count": str(int(bucket == "critical")),
        "high_count": str(int(bucket == "high")),
        "medium_count": str(int(bucket == "medium")),
        "quality_count": "0",
    }


@pytest.mark.parametrize(
    "result_properties",
    [
        {"tags": ["security"]},
        {"tags": ["external/cwe/cwe-020"]},
        {"security-severity": "9.8"},
        {"tags": "security"},
        {"tags": "external/cwe/cwe-020"},
        {"tags": [123]},
        {"tags": None},
    ],
)
def test_parser_conflicting_result_metadata_is_not_quality(tmp_path, result_properties):
    result, output = _parse_sarif(
        tmp_path,
        {
            "tool": {
                "driver": {
                    "rules": [
                        {
                            "id": "conflicting",
                            "defaultConfiguration": {"level": "error"},
                            "properties": {"tags": ["correctness"]},
                        }
                    ]
                }
            },
            "results": [{"ruleId": "conflicting", "properties": result_properties}],
        },
    )
    assert result.returncode == 0, result.stderr
    assert "critical_count=1" in output.read_text()
    assert "quality_count=0" in output.read_text()


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
