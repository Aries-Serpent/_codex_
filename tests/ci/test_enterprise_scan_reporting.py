"""Enterprise reports retain actual scan outputs, not success-shaped summaries."""

import json
import os
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/enterprise-compliance.yml"


def workflow():
    return yaml.safe_load(WORKFLOW.read_text())


def test_codeql_retains_sarif_separately_from_source_metadata():
    document = workflow()
    assert "0D_base_" in document["on"]["pull_request"]["branches"]
    assert document["permissions"] == {"contents": "read", "security-events": "write"}
    steps = document["jobs"]["codeql"]["steps"]
    analyze = next(step for step in steps if step["name"] == "Analyze code")
    assert analyze["with"]["upload"] == "never"
    assert analyze["with"]["output"] == "codeql-results"
    uploads = [
        step for step in steps if step.get("uses", "").startswith("actions/upload-artifact@")
    ]
    assert len(uploads) == 2
    assert {step["with"]["path"].strip() for step in uploads} == {
        "codeql-results/*.sarif",
        "scan-source.json",
    }
    assert all(step["if"] == "always()" for step in uploads)
    assert all(step["with"]["if-no-files-found"] == "error" for step in uploads)


@pytest.mark.parametrize("scanner", ["bandit", "semgrep"])
def test_informational_scan_exits_are_exposed_not_called_clean(scanner):
    job = workflow()["jobs"][scanner]
    scan = next(step for step in job["steps"] if step.get("id") == "scan")
    assert "|| true" not in scan["run"]
    assert 'echo "exit_code=$status" >> "$GITHUB_OUTPUT"' in scan["run"]
    assert "informational" in scan["run"]
    assert job["outputs"]["scan-exit-code"] == "${{ steps.scan.outputs.exit_code }}"
    reports = [
        step for step in job["steps"] if step.get("uses", "").startswith("actions/upload-artifact@")
    ]
    assert reports
    assert all(step["with"]["if-no-files-found"] == "error" for step in reports)
    dashboard = workflow()["jobs"]["compliance-report"]
    summary = next(step for step in dashboard["steps"] if "env" in step)
    assert "COMPLETE" not in summary["run"]
    assert summary["env"][scanner.upper() + "_RESULT"] == f"${{{{ needs.{scanner}.result }}}}"


def test_source_metadata_distinguishes_head_base_merge_and_attempt(tmp_path):
    steps = workflow()["jobs"]["codeql"]["steps"]
    script = next(
        step["run"] for step in steps if step["name"] == "Retain analyzed source identity"
    )
    event = tmp_path / "event.json"
    event.write_text(
        json.dumps(
            {
                "pull_request": {
                    "number": 123,
                    "head": {"sha": "a" * 40},
                    "base": {"sha": "b" * 40},
                    "body": "Sensitive unrelated metadata must not be copied",
                }
            }
        )
    )
    subprocess.run(
        ["bash", "-eu", "-c", script],
        cwd=tmp_path,
        env={
            **os.environ,
            "GIT_DIR": str(ROOT / ".git"),
            "GIT_WORK_TREE": str(ROOT),
            "GITHUB_EVENT_PATH": str(event),
            "GITHUB_SHA": "c" * 40,
            "GITHUB_REF": "refs/pull/123/merge",
            "GITHUB_EVENT_NAME": "pull_request",
            "GITHUB_RUN_ID": "456",
            "GITHUB_RUN_ATTEMPT": "2",
        },
        check=True,
        timeout=15,
        capture_output=True,
    )
    report = json.loads((tmp_path / "scan-source.json").read_text())
    assert report["pr_head_sha"] == "a" * 40
    assert report["pr_base_sha"] == "b" * 40
    assert report["event_sha"] == "c" * 40
    assert report["run_attempt"] == "2"
    assert len(report["checkout_sha"]) == 40
    assert "body" not in report
    assert "Sensitive" not in json.dumps(report)
