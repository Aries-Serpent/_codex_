import json

from scripts.ci import reconcile_live_security as rls


def test_artifact_summary_reads_current_repo_schema(tmp_path):
    artifact = tmp_path / "security-findings-comprehensive.json"
    artifact.write_text(
        json.dumps(
            {
                "metadata": {
                    "total_findings": 10,
                    "by_severity": {"CRITICAL": 4, "HIGH": 4, "MEDIUM": 2, "LOW": 0, "INFO": 0},
                },
                "findings": [
                    {"severity": "CRITICAL"},
                    {"severity": "CRITICAL"},
                    {"severity": "CRITICAL"},
                    {"severity": "CRITICAL"},
                    {"severity": "HIGH"},
                    {"severity": "HIGH"},
                    {"severity": "HIGH"},
                    {"severity": "HIGH"},
                    {"severity": "MEDIUM"},
                    {"severity": "MEDIUM"},
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    summary = rls._artifact_summary(artifact)

    assert summary["total_findings"] == 10
    assert summary["by_severity"]["CRITICAL"] == 4
    assert summary["by_severity"]["HIGH"] == 4
    assert summary["by_severity"]["MEDIUM"] == 2


def test_build_payload_falls_back_to_artifact_evidence(monkeypatch, tmp_path):
    for env_name in ("GH_TOKEN", "CODEX_MASTER_KEY", "CODEX_BACKUP_KEY", "GITHUB_TOKEN"):
        monkeypatch.delenv(env_name, raising=False)

    artifact = tmp_path / "security-findings-comprehensive.json"
    artifact.write_text(
        json.dumps(
            {
                "metadata": {
                    "total_findings": 3,
                    "by_severity": {"CRITICAL": 1, "HIGH": 1, "MEDIUM": 1, "LOW": 0, "INFO": 0},
                },
                "findings": [
                    {"severity": "CRITICAL"},
                    {"severity": "HIGH"},
                    {"severity": "MEDIUM"},
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    payload = rls._build_payload("Aries-Serpent/_codex_", str(artifact))

    assert payload["source_of_truth"] == "artifact"
    assert payload["total_open_alerts"] == 3
    assert payload["needs_triage"] is True
    assert payload["delta"]["total_findings"] == 0
    assert payload["artifact_generated_findings"]["total_findings"] == 3


def test_default_branch_ref_filtering_handles_branch_matches():
    alert = {"ref": "refs/heads/main", "most_recent_instance": {"ref": "refs/heads/main"}}
    assert rls._alert_ref_matches_default(alert, "main") is True
    assert rls._alert_ref_matches_default({"ref": "refs/heads/feature/demo"}, "main") is False
    assert rls._with_default_branch_ref("/repos/test/repo/code-scanning/alerts?state=open", "main") == "/repos/test/repo/code-scanning/alerts?state=open&ref=refs/heads/main"


def test_failure_classification_and_raw_evidence_are_exposed(tmp_path):
    artifact = tmp_path / "security-findings-comprehensive.json"
    artifact.write_text(
        json.dumps(
            {
                "metadata": {
                    "total_findings": 2,
                    "by_severity": {"CRITICAL": 1, "HIGH": 1, "MEDIUM": 0, "LOW": 0, "INFO": 0},
                },
                "findings": [{"severity": "CRITICAL"}, {"severity": "HIGH"}],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    payload = rls._build_payload("Aries-Serpent/_codex_", str(artifact))

    assert payload["failure_classification"] == "blocked_by_critical_or_high_vulnerabilities"
    assert payload["raw_evidence_artifacts"] == [str(artifact)]
    assert payload["severity_summary"]["CRITICAL"] == 1
    assert payload["severity_summary"]["HIGH"] == 1
    assert payload["security_overview"]["severity_summary"] == payload["severity_summary"]


def test_paginate_handles_network_errors(monkeypatch):
    def fake_api_get(_url):
        raise OSError("broken socket")

    monkeypatch.setattr(rls, "_api_get", fake_api_get)

    assert rls._paginate("/repos/test/repo/code-scanning/alerts?state=open") == []
