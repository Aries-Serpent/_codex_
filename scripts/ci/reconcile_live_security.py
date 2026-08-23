#!/usr/bin/env python3
"""Reconcile GitHub Security live alerts against generated artifact findings."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib import error, request

SEVERITY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
SOURCE_ORDER = ["code_scanning", "dependabot", "secret_scanning"]
SEVERITY_ALIASES = {
    "CRITICAL": "CRITICAL",
    "ERROR": "CRITICAL",
    "HIGH": "HIGH",
    "WARNING": "MEDIUM",
    "WARNING_LEVEL": "MEDIUM",
    "MODERATE": "MEDIUM",
    "MEDIUM": "MEDIUM",
    "LOW": "LOW",
    "NOTE": "LOW",
    "INFO": "INFO",
    "UNKNOWN": "INFO",
}


def _token() -> str | None:
    return (
        os.environ.get("GH_TOKEN")
        or os.environ.get("CODEX_MASTER_KEY")
        or os.environ.get("CODEX_BACKUP_KEY")
        or os.environ.get("GITHUB_TOKEN")
    )


def _headers() -> dict[str, str]:
    token = _token()
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"******"
    return headers


def _api_get(url: str) -> object:
    req = request.Request(url, headers=_headers())
    with request.urlopen(req, timeout=30) as response:
        body = response.read().decode("utf-8")
        if not body:
            return []
        return json.loads(body)


def _coerce_severity(raw: object) -> str:
    if raw is None:
        return "INFO"
    value = str(raw).strip().upper()
    if value.startswith("CWE-"):
        return "INFO"
    return SEVERITY_ALIASES.get(value, "INFO")


def _paginate(endpoint: str) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    page = 1
    while True:
        separator = "&" if "?" in endpoint else "?"
        url = f"https://api.github.com{endpoint}{separator}page={page}&per_page=100"
        try:
            payload = _api_get(url)
        except (error.HTTPError, error.URLError, TimeoutError, ValueError, OSError):
            return results
        if not isinstance(payload, list):
            return results
        if not payload:
            return results
        results.extend(payload)
        if len(payload) < 100:
            return results
        page += 1


def _normalize_severity(alert: dict[str, object], source: str) -> str:
    if source == "dependabot":
        severity = str((alert.get("security_vulnerability") or {}).get("severity") or "unknown")
        return _coerce_severity(severity)

    if source == "secret_scanning":
        return "CRITICAL" if alert.get("state") == "open" else "LOW"

    rule = alert.get("rule") or {}
    candidates = [
        rule.get("security_severity_level"),
        rule.get("severity"),
        (alert.get("most_recent_instance") or {}).get("state"),
        alert.get("state"),
        alert.get("severity"),
        alert.get("level"),
    ]
    for candidate in candidates:
        if candidate is not None:
            severity = _coerce_severity(candidate)
            if severity != "INFO":
                return severity
    return "INFO"


def _severity_counts_from_mapping(raw: object) -> dict[str, int]:
    counts = {sev: 0 for sev in SEVERITY_ORDER}
    if not isinstance(raw, dict):
        return counts
    for key, value in raw.items():
        key_name = str(key).strip().upper().replace("-", "_")
        int_value = int(value or 0)
        if "CRITICAL" in key_name:
            counts["CRITICAL"] = int_value
        elif "HIGH" in key_name:
            counts["HIGH"] = int_value
        elif "MODERATE" in key_name or "MEDIUM" in key_name:
            counts["MEDIUM"] = int_value
        elif "LOW" in key_name:
            counts["LOW"] = int_value
        elif "INFO" in key_name:
            counts["INFO"] = int_value
    return counts


def _artifact_summary(path: Path) -> dict[str, object]:
    zero = {"total_findings": 0, "by_severity": {sev: 0 for sev in SEVERITY_ORDER}}
    if not path.exists():
        return zero

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return zero

    if not isinstance(payload, dict):
        return zero

    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    severity = _severity_counts_from_mapping(summary.get("by_severity") or metadata.get("by_severity"))
    if not any(severity.values()):
        severity = _severity_counts_from_mapping(summary) if summary else _severity_counts_from_mapping(metadata)

    total = int((summary or metadata).get("total_findings", 0) or 0)
    findings = payload.get("findings") or payload.get("finding_index") or []
    if isinstance(findings, list) and findings:
        total = len(findings)
        counts = {sev: 0 for sev in SEVERITY_ORDER}
        for finding in findings:
            if not isinstance(finding, dict):
                continue
            sev = _coerce_severity(
                finding.get("severity")
                or finding.get("level")
                or finding.get("security_severity_level")
                or (finding.get("security_vulnerability") or {}).get("severity")
                or (finding.get("rule") or {}).get("severity")
                or (finding.get("rule") or {}).get("security_severity_level")
            )
            counts[sev] = counts.get(sev, 0) + 1
        if any(counts.values()):
            severity = counts
        total = sum(severity.values())

    if not total:
        total = sum(severity.values())

    return {"total_findings": int(total), "by_severity": severity}


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    lines = [
        "# 🔐 Live GitHub Security Reconciliation",
        "",
        f"- Repository: `{payload['repo_url']}`",
        f"- Default branch: `{payload['default_branch']}`",
        f"- Default branch only: `{payload['default_branch_only']}`",
        f"- Last synced: `{payload['last_synced_at']}`",
        "",
        "## Live open alerts",
        "",
        f"- Total: **{payload['total_open_alerts']}**",
        "",
        "| Severity | Count |",
        "|----------|-------|",
    ]
    for severity in SEVERITY_ORDER:
        lines.append(f"| {severity} | {payload['by_severity'].get(severity, 0)} |")

    lines.extend(["", "## By source", "", "| Source | Count |", "|--------|-------|"])
    for source in SOURCE_ORDER:
        lines.append(f"| {source} | {payload['by_source'].get(source, 0)} |")

    artifact_summary = payload.get("artifact_generated_findings", {})
    lines.extend(["", "## Artifact-generated findings", "", f"- Total: **{artifact_summary.get('total_findings', 0)}**", ""])
    lines.append("| Severity | Count |")
    lines.append("|----------|-------|")
    for severity in SEVERITY_ORDER:
        lines.append(f"| {severity} | {artifact_summary.get('by_severity', {}).get(severity, 0)} |")

    delta_total = payload.get("delta", {}).get("total_findings", 0)
    lines.extend(["", "## Delta", "", f"- Total delta: **{delta_total}**", f"- Needs triage: **{payload.get('needs_triage', False)}**", ""])
    lines.append("| Severity | Live | Artifact | Delta |")
    lines.append("|----------|------|----------|-------|")
    for severity in SEVERITY_ORDER:
        live = payload["by_severity"].get(severity, 0)
        artifact = artifact_summary.get("by_severity", {}).get(severity, 0)
        delta = live - artifact
        lines.append(f"| {severity} | {live} | {artifact} | {delta} |")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _build_payload(repo: str, artifact_path: str) -> dict[str, object]:
    repo_url = f"https://github.com/{repo}"
    default_branch = "main"
    artifact_summary = _artifact_summary(Path(artifact_path))

    if not _token():
        artifact_total = int(artifact_summary.get("total_findings", 0) or 0)
        return {
            "repo_url": repo_url,
            "default_branch": default_branch,
            "default_branch_only": True,
            "last_synced_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_open_alerts": artifact_total,
            "by_severity": {sev: artifact_summary.get("by_severity", {}).get(sev, 0) for sev in SEVERITY_ORDER},
            "by_source": {src: 0 for src in SOURCE_ORDER},
            "artifact_generated_findings": artifact_summary,
            "delta": {"total_findings": 0, "needs_triage": artifact_total > 0},
            "needs_triage": artifact_total > 0,
            "source_of_truth": "artifact",
            "source_urls": {
                "code_scanning": f"{repo_url}/security/code-scanning",
                "dependabot": f"{repo_url}/security/dependabot",
                "secret_scanning": f"{repo_url}/security/secret-scanning",
            },
        }

    try:
        repo_meta = _api_get(f"https://api.github.com/repos/{repo}")
        if isinstance(repo_meta, dict):
            default_branch = str(repo_meta.get("default_branch") or default_branch)
    except (error.HTTPError, error.URLError, TimeoutError, ValueError, OSError):
        artifact_total = int(artifact_summary.get("total_findings", 0) or 0)
        return {
            "repo_url": repo_url,
            "default_branch": default_branch,
            "default_branch_only": bool(default_branch),
            "last_synced_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_open_alerts": artifact_total,
            "by_severity": {sev: artifact_summary.get("by_severity", {}).get(sev, 0) for sev in SEVERITY_ORDER},
            "by_source": {src: 0 for src in SOURCE_ORDER},
            "artifact_generated_findings": artifact_summary,
            "delta": {"total_findings": 0, "needs_triage": artifact_total > 0},
            "needs_triage": artifact_total > 0,
            "source_of_truth": "artifact",
            "source_urls": {
                "code_scanning": f"{repo_url}/security/code-scanning",
                "dependabot": f"{repo_url}/security/dependabot",
                "secret_scanning": f"{repo_url}/security/secret-scanning",
            },
        }

    by_source: dict[str, list[dict[str, object]]] = {
        "code_scanning": [],
        "dependabot": [],
        "secret_scanning": [],
    }
    for source, endpoint in (
        ("code_scanning", f"/repos/{repo}/code-scanning/alerts?state=open"),
        ("dependabot", f"/repos/{repo}/dependabot/alerts?state=open"),
        ("secret_scanning", f"/repos/{repo}/secret-scanning/alerts?state=open"),
    ):
        try:
            by_source[source] = _paginate(endpoint)
        except Exception:
            by_source[source] = []

    totals: Counter[str] = Counter()
    for source, alerts in by_source.items():
        for alert in alerts:
            totals[_normalize_severity(alert, source)] += 1

    live_total = sum(totals.values())
    artifact_total = int(artifact_summary.get("total_findings", 0) or 0)
    delta_total = live_total - artifact_total
    source_of_truth = "live" if live_total or any(by_source.values()) else "artifact"
    if source_of_truth == "artifact":
        live_total = artifact_total
        totals = Counter({sev: artifact_summary.get("by_severity", {}).get(sev, 0) for sev in SEVERITY_ORDER})
        delta_total = 0
    return {
        "repo_url": repo_url,
        "default_branch": default_branch,
        "default_branch_only": bool(default_branch),
        "last_synced_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_open_alerts": live_total,
        "by_severity": {sev: totals.get(sev, 0) for sev in SEVERITY_ORDER},
        "by_source": {src: len(by_source.get(src, [])) for src in SOURCE_ORDER},
        "artifact_generated_findings": artifact_summary,
        "delta": {"total_findings": delta_total, "needs_triage": delta_total != 0},
        "needs_triage": delta_total != 0,
        "source_of_truth": source_of_truth,
        "source_urls": {
            "code_scanning": f"{repo_url}/security/code-scanning",
            "dependabot": f"{repo_url}/security/dependabot",
            "secret_scanning": f"{repo_url}/security/secret-scanning",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "Aries-Serpent/_codex_"))
    parser.add_argument("--artifact", default=".codex/security-findings-comprehensive.json")
    parser.add_argument("--output", default=".codex/live-security-reconciliation.json")
    parser.add_argument("--markdown", default=".codex/live-security-reconciliation.md")
    args = parser.parse_args()

    payload = _build_payload(args.repo, args.artifact)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _write_markdown(Path(args.markdown), payload)

    print(json.dumps({
        "repo": args.repo,
        "total_open_alerts": payload["total_open_alerts"],
        "by_severity": payload["by_severity"],
        "by_source": payload["by_source"],
        "delta": payload["delta"]["total_findings"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
