import json
import sys

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


def test_artifact_backlog_reports_4k_plus_findings_in_summary(tmp_path):
    artifact = tmp_path / "security-findings-comprehensive.json"
    artifact.write_text(
        json.dumps(
            {
                "metadata": {
                    "total_findings": 4100,
                    "by_severity": {"CRITICAL": 1100, "HIGH": 1600, "MEDIUM": 900, "LOW": 300, "INFO": 200},
                },
                "findings": [{"severity": "CRITICAL"} for _ in range(1100)]
                + [{"severity": "HIGH"} for _ in range(1600)]
                + [{"severity": "MEDIUM"} for _ in range(900)]
                + [{"severity": "LOW"} for _ in range(300)]
                + [{"severity": "INFO"} for _ in range(200)],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    payload = rls._build_payload("Aries-Serpent/_codex_", str(artifact))
    markdown_path = tmp_path / "report.md"
    rls._write_markdown(markdown_path, payload)
    text = markdown_path.read_text(encoding="utf-8")

    assert rls._compact_count(4100) == "4.1k+"
    assert "Historical artifact backlog: **4100**" in text
    assert "Stale or archived findings: **4100**" in text
    assert "Final recommendation: **advisory-only**" in text


def test_artifact_only_classification_and_markdown_evidence_are_explicit(monkeypatch, tmp_path):
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
                "findings": [{"severity": "CRITICAL"}, {"severity": "HIGH"}, {"severity": "MEDIUM"}],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    payload = rls._build_payload("Aries-Serpent/_codex_", str(artifact))
    assert payload["classification"] == "historical_artifact_backlog"
    assert payload["source_of_truth"] == "artifact"

    markdown_path = tmp_path / "report.md"
    rls._write_markdown(markdown_path, payload)
    text = markdown_path.read_text(encoding="utf-8")
    assert "Source of truth: **artifact**" in text
    assert "Evidence artifacts:" in text
    assert str(artifact) in text


def test_paginate_handles_network_errors(monkeypatch):
    def fake_api_get(_url):
        raise OSError("broken socket")

    monkeypatch.setattr(rls, "_api_get", fake_api_get)

    assert rls._paginate("/repos/test/repo/code-scanning/alerts?state=open") == []


def test_artifact_validation_rejects_invalid_payload(tmp_path):
    artifact = tmp_path / "invalid.json"
    artifact.write_text("[]", encoding="utf-8")

    assert rls._artifact_is_valid(artifact) is False


def test_default_branch_detection_uses_git_remote_when_api_unavailable(monkeypatch):
    for env_name in (
        "GH_TOKEN",
        "CODEX_MASTER_KEY",
        "CODEX_BACKUP_KEY",
        "GITHUB_TOKEN",
        "GITHUB_DEFAULT_BRANCH",
        "GITHUB_REF_NAME",
        "GITHUB_HEAD_REF",
        "GITHUB_BASE_REF",
    ):
        monkeypatch.delenv(env_name, raising=False)
    monkeypatch.setenv("GITHUB_REF_NAME", "copilot/understanding-security-alerts")

    monkeypatch.setattr(rls, "_api_get", lambda _url: (_ for _ in ()).throw(OSError("offline")))

    class FakeProc:
        def __init__(self, stdout: str):
            self.stdout = stdout

    def fake_run(args, check=False, capture_output=False, text=False):
        if args[:4] == ["git", "symbolic-ref", "--quiet", "--short"] and args[4] == "refs/remotes/origin/HEAD":
            return FakeProc("origin/HEAD -> origin/0D_base_")
        if args[:4] == ["git", "symbolic-ref", "--quiet", "--short"] and args[4] == "HEAD":
            return FakeProc("main")
        return FakeProc("")

    monkeypatch.setattr(rls.subprocess, "run", fake_run)

    assert rls._discover_default_branch("Aries-Serpent/_codex_") == "0D_base_"


def test_main_rejects_invalid_artifact_under_strict_validation(monkeypatch, tmp_path):
    artifact = tmp_path / "invalid-security-artifact.json"
    artifact.write_text("[]", encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["reconcile_live_security.py", "--artifact", str(artifact), "--strict-artifact"])
    monkeypatch.delenv("GITHUB_DEFAULT_BRANCH", raising=False)
    monkeypatch.setattr(rls, "_token", lambda: None)

    assert rls.main() == 2
