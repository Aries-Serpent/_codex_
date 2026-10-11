import csv
import json

from scripts.ci.aggregate_security_findings import FindingsAggregator


def _artifact(root, name, contract=None):
    artifact = root / name
    artifact.mkdir(parents=True)
    contract_path = artifact / ".codex" / "contracts" / "output-contract-test.json"
    contract_path.parent.mkdir(parents=True)
    contract_path.write_text(
        json.dumps(contract or {"status": "success"}), encoding="utf-8"
    )
    return artifact


def _sarif_result(rule_id, fingerprint, path="src/app.py", line=8):
    return {
        "ruleId": rule_id,
        "message": {"text": f"Finding for {rule_id}"},
        "level": "error",
        "fingerprints": {"primary": fingerprint},
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": path},
                    "region": {"startLine": line},
                }
            }
        ],
    }


def _write_sarif(path, results):
    path.write_text(
        json.dumps(
            {
                "version": "2.1.0",
                "runs": [
                    {
                        "tool": {"driver": {"name": "fixture", "rules": []}},
                        "results": results,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def _aggregator(root, selected_scans=None):
    return FindingsAggregator(
        artifacts_dir=str(root),
        repo_url="https://github.com/example/repo",
        run_id="123",
        commit_sha="abc123",
        repository="example/repo",
        selected_scans=selected_scans,
    )


def test_aggregates_each_successful_scanner_format(tmp_path):
    codeql_python = _artifact(tmp_path, "security-suite-codeql-python")
    _write_sarif(
        codeql_python / "results.sarif",
        [_sarif_result("py-rule", "py-1")],
    )
    codeql_javascript = _artifact(tmp_path, "security-suite-codeql-javascript")
    _write_sarif(codeql_javascript / "results.sarif", [])

    semgrep = _artifact(tmp_path, "security-suite-semgrep")
    (semgrep / "semgrep-results.json").write_text(
        json.dumps(
            {
                "results": [
                    {
                        "check_id": "python.lang.security.audit",
                        "extra": {
                            "message": "Semgrep finding",
                            "severity": "WARNING",
                        },
                        "path": "src/app.py",
                        "start": {"line": 8},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    container = _artifact(tmp_path, "security-suite-container-0")
    _write_sarif(container / "trivy-results.sarif", [_sarif_result("trivy-rule", "t-1")])
    for index in (1, 2):
        _artifact(tmp_path, f"security-suite-container-{index}")

    cve_python = _artifact(tmp_path, "security-suite-cve-python")
    (cve_python / "python-cve-audit.json").write_text(
        json.dumps(
            {
                "dependencies": [
                    {
                        "name": "package-a",
                        "installed_version": "1.0",
                        "vulns": [{"id": "PYSEC-1", "description": "Python issue"}],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    cve_javascript = _artifact(tmp_path, "security-suite-cve-javascript")
    (cve_javascript / "javascript-cve-audit.json").write_text(
        json.dumps(
            {
                "vulnerabilities": {
                    "package-b": {
                        "severity": "high",
                        "range": "<2.0",
                        "via": [
                            {"source": 101, "title": "First npm issue"},
                            {"source": 102, "title": "Second npm issue"},
                        ],
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    cve_rust = _artifact(tmp_path, "security-suite-cve-rust")
    (cve_rust / "rust-cve-audit.json").write_text(
        json.dumps({"vulnerabilities": {"list": []}}), encoding="utf-8"
    )

    dependency = _artifact(tmp_path, "security-suite-dependency")
    (dependency / "pip-audit.json").write_text(
        json.dumps(
            {
                "dependencies": [
                    {
                        "name": "package-c",
                        "installed_version": "1.0",
                        "vulns": [{"id": "PYSEC-2", "description": "Dependency issue"}],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (dependency / "safety.json").write_text(
        json.dumps(
            {
                "vulnerabilities": [
                    {
                        "package_name": "package-d",
                        "vulnerability_id": "SAFETY-1",
                        "severity": "medium",
                        "advisory": "Safety issue",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    secrets = _artifact(tmp_path, "security-suite-secrets")
    (secrets / ".secrets.baseline").write_text(
        json.dumps(
            {
                "results": {
                    "src/config.py": [
                        {"type": "FixtureSecretDetector", "line_number": 12}
                    ]
                }
            }
        ),
        encoding="utf-8",
    )

    report = _aggregator(
        tmp_path,
        ["codeql", "semgrep", "containers", "cve", "dependency", "secrets"],
    ).run()

    assert report["summary"]["total_findings"] == 9
    assert {finding["tool"] for finding in report["finding_index"]} == {
        "codeql",
        "semgrep",
        "trivy",
        "pip-audit",
        "npm-audit",
        "safety",
        "detect-secrets",
    }
    assert report["scan_status"]["sbom"]["status"] == "skipped"
    assert report["scan_status"]["secrets"]["status"] == "success"


def test_failed_contract_is_incomplete_and_not_aggregated(tmp_path):
    artifact = _artifact(
        tmp_path,
        "security-suite-secrets",
        {"status": "success", "scan_outcome": "failure"},
    )
    (artifact / ".secrets.baseline").write_text(
        json.dumps({"results": {"secret.py": [{"type": "Example", "line_number": 1}]}}),
        encoding="utf-8",
    )

    report = _aggregator(tmp_path, ["secrets"]).run()

    assert report["summary"]["total_findings"] == 0
    assert report["scan_status"]["secrets"]["status"] == "incomplete"


def test_sarif_findings_from_different_artifacts_keep_unique_ids(tmp_path):
    for name in ("security-suite-codeql-python", "security-suite-codeql-javascript"):
        artifact = _artifact(tmp_path, name)
        _write_sarif(
            artifact / "results.sarif",
            [_sarif_result("shared-rule", "same-fingerprint")],
        )

    report = _aggregator(tmp_path, ["codeql"]).run()
    findings = report["finding_index"]

    assert len(findings) == 2
    assert len({finding["id"] for finding in findings}) == 2


def test_csv_exports_include_all_findings(tmp_path):
    report = {
        "finding_index": [
            {
                "id": f"ALERT-{index}",
                "tool": "codeql",
                "rule_id": "rule-a",
                "severity": "HIGH",
            }
            for index in range(3510)
        ],
        "scan_metadata": {"commit": "abc123", "run_id": "123"},
    }
    inventory = tmp_path / "inventory.csv"
    priority = tmp_path / "priority.csv"
    family = tmp_path / "family.csv"

    FindingsAggregator.write_csv_exports(
        report, str(inventory), str(priority), str(family)
    )

    with inventory.open(encoding="utf-8", newline="") as handle:
        assert sum(1 for _ in csv.DictReader(handle)) == 3510
    with priority.open(encoding="utf-8", newline="") as handle:
        assert sum(1 for _ in csv.DictReader(handle)) == 3510
    with family.open(encoding="utf-8", newline="") as handle:
        families = list(csv.DictReader(handle))
    assert families == [{"family_id": "codeql:rule-a", "rule_id": "rule-a", "count": "3510"}]
