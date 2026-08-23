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
from typing import Any, Iterable
from urllib import error, request

SEVERITY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
SOURCE_ORDER = ["code_scanning", "dependabot", "secret_scanning"]


def _token() -> str | None:
    return (
        os.environ.get("GH_TOKEN")
        or os.environ.get("CODEX_MASTER_KEY")
        or os.environ.get("CODEX_BACKUP_KEY")
        or os.environ.get("GITHUB_TOKEN")
    )


def _headers() -> dict[str, str]:
    token = _token()
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"******"
    return headers


def _api_get(url: str) -> Any:
    req = request.Request(url, headers=_headers())
    with request.urlopen(req, timeout=30) as response:
        body = response.read().decode("utf-8")
        if not body:
            return []
        return json.loads(body)


def _paginate(endpoint: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    page = 1
    while True:
        separator = "&" if "?" in endpoint else "?"
        url = f"https://api.github.com{endpoint}{separator}page={page}&per_page=100"
        try:
            payload = _api_get(url)
        except error.HTTPError as exc:  # pragma: no cover - network safety
            if exc.code in (401, 403, 404):
                return results
            raise
        if not isinstance(payload, list):
            return results
        if not payload:
            return results
        results.extend(payload)
        if len(payload) < 100:
            return results
        page += 1


def _normalize_severity(alert: dict[str, Any], source: str) -> str:
    if source == "dependabot":
        severity = str(
            (alert.get("security_vulnerability") or {}).get("severity") or "unknown"
        ).upper()
        return {"CRITICAL": "CRITICAL", "HIGH": "HIGH", "MODERATE": "MEDIUM", "LOW": "LOW"}.get(severity, "INFO")

    if source == "secret_scanning":
        return "CRITICAL" if alert.get("state") == "open" else "LOW"

    rule = alert.get("rule") or {}
    severity = str(
        rule.get("security_severity_level")
        or rule.get("severity")
        or alert.get("most_recent_instance", {}).get("state")
        or "info"
    ).lower()
    mapping = {
        "critical": "CRITICAL",
        "error": "CRITICAL",
        "high": "HIGH",
        "warning": "MEDIUM",
        "warning_level": "MEDIUM",
        "moderate": "MEDIUM",
        "medium": "MEDIUM",
        "low": "LOW",
        "note": "LOW",
        "info": "INFO",
    }
    return mapping.get(severity, "INFO")


def _artifact_summary(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"total_findings": 0, "by_severity": {sev: 0 for sev in SEVERITY_ORDER}}

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"total_findings": 0, "by_severity": {sev: 0 for sev in SEVERITY_ORDER}}

    summary = payload.get("summary", {})
    severity = {
        "CRITICAL": int(summary.get("critical_count", 0) or 0),
        "HIGH": int(summary.get("high_count", 0) or 0),
        "MEDIUM": int(summary.get("medium_count", 0) or 0),
        "LOW": int(summary.get("low_count", 0) or 0),
        "INFO": int(summary.get("info_count", 0) or 0),
    }
    total = int(summary.get("total_findings", sum(severity.values())) or 0)
    return {"total_findings": total, "by_severity": severity}


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
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

    lines.extend(["", "## Artifact-generated findings", "", f"- Total: **{payload['artifact_generated_findings']['total_findings']}**", ""])
    lines.append("| Severity | Count |")
    lines.append("|----------|-------|")
    for severity in SEVERITY_ORDER:
        lines.append(f"| {severity} | {payload['artifact_generated_findings']['by_severity'].get(severity, 0)} |")

    lines.extend(["", "## Delta", "", f"- Total delta: **{payload['delta']['total_findings']}**", f"- Needs triage: **{payload['delta']['needs_triage']}**", ""])
    lines.append("| Severity | Live | Artifact | Delta |")
    lines.append("|----------|------|----------|-------|")
    for severity in SEVERITY_ORDER:
        live = payload["by_severity"].get(severity, 0)
        artifact = payload["artifact_generated_findings"]["by_severity"].get(severity, 0)
        delta = live - artifact
        lines.append(f"| {severity} | {live} | {artifact} | {delta} |")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _build_payload(repo: str, artifact_path: str) -> dict[str, Any]:
    repo_url = f"https://github.com/{repo}"
    repository = repo.split("/", 1)
    default_branch = "main"
    repo_endpoint = f"https://api.github.com/repos/{'/'.join(repository)}"
    by_source: dict[str, list[dict[str, Any]]] = {
        "code_scanning": [],
        "dependabot": [],
        "secret_scanning": [],
    }

    if not _token():
        return {
            "repo_url": repo_url,
            "default_branch": default_branch,
            "default_branch_only": True,
            "last_synced_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_open_alerts": 0,
            "by_severity": {sev: 0 for sev in SEVERITY_ORDER},
            "by_source": {src: 0 for src in SOURCE_ORDER},
            "artifact_generated_findings": _artifact_summary(Path(artifact_path)),
            "delta": {"total_findings": 0, "needs_triage": False},
            "needs_triage": False,
            "source_urls": {
                "code_scanning": f"{repo_url}/security/code-scanning",
                "dependabot": f"{repo_url}/security/dependabot",
                "secret_scanning": f"{repo_url}/security/secret-scanning",
            },
        }

    try:
        repo_meta = _api_get(repo_endpoint)
        default_branch = str(repo_meta.get("default_branch") or default_branch)
    except Exception:  # pragma: no cover - best effort fallback
        default_branch = "main"

    for source, endpoint in (
        ("code_scanning", f"/repos/{repo}/code-scanning/alerts?state=open"),
        ("dependabot", f"/repos/{repo}/dependabot/alerts?state=open"),
        ("secret_scanning", f"/repos/{repo}/secret-scanning/alerts?state=open"),
    ):
        by_source[source] = _paginate(endpoint)

    totals = Counter()
    for source, alerts in by_source.items():
        for alert in alerts:
            totals[_normalize_severity(alert, source)] += 1

    artifact_summary = _artifact_summary(Path(artifact_path))
    live_total = sum(totals.values())
    artifact_total = artifact_summary["total_findings"]
    delta_total = live_total - artifact_total
    result = {
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
        "source_urls": {
            "code_scanning": f"{repo_url}/security/code-scanning",
            "dependabot": f"{repo_url}/security/dependabot",
            "secret_scanning": f"{repo_url}/security/secret-scanning",
        },
    }
    return result


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
