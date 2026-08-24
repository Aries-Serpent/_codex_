#!/usr/bin/env python3
"""Reconcile GitHub Security live alerts against generated artifact findings."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
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


def _compact_count(value: int) -> str:
    if value < 1000:
        return str(value)
    if value < 10000:
        return f"{value / 1000:.1f}k+"
    return f"{value / 1000:.0f}k+"


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
        headers["Authorization"] = "Bearer " + token
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


def _normalize_branch_name(branch_name: str) -> str:
    value = str(branch_name or "").strip()
    if not value:
        return ""
    value = value.replace("refs/heads/", "")
    value = value.replace("refs/tags/", "")
    value = value.replace("origin/", "")
    return value.strip("/")


def _discover_default_branch(repo: str) -> str:
    candidate = _normalize_branch_name(os.environ.get("GITHUB_DEFAULT_BRANCH", ""))
    if candidate:
        return candidate

    try:
        repo_meta = _api_get(f"https://api.github.com/repos/{repo}")
        if isinstance(repo_meta, dict):
            candidate = _normalize_branch_name(str(repo_meta.get("default_branch") or ""))
            if candidate:
                return candidate
    except (error.HTTPError, error.URLError, TimeoutError, ValueError, OSError):
        # Fall back to git metadata when GitHub API access is unavailable in CI or private runners.
        pass

    git_commands = [
        ["git", "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"],
        ["git", "symbolic-ref", "--quiet", "--short", "HEAD"],
        ["git", "rev-parse", "--abbrev-ref", "origin/HEAD"],
    ]
    for cmd in git_commands:
        try:
            proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
        except (FileNotFoundError, OSError):
            continue
        value = (proc.stdout or "").strip()
        if not value:
            continue
        value = value.replace("origin/HEAD -> ", "")
        candidate = _normalize_branch_name(value)
        if candidate:
            return candidate

    return "main"


def _with_default_branch_ref(endpoint: str, default_branch: str) -> str:
    if not default_branch:
        return endpoint
    if "ref=" in endpoint:
        return endpoint
    delimiter = "&" if "?" in endpoint else "?"
    branch_ref = f"refs/heads/{_normalize_branch_name(default_branch)}"
    return f"{endpoint}{delimiter}ref={branch_ref}"


def _alert_ref_matches_default(alert: dict[str, object], default_branch: str) -> bool:
    if not default_branch:
        return True
    default_name = _normalize_branch_name(default_branch)
    if not default_name:
        return True
    for candidate in (
        alert.get("ref"),
        (alert.get("most_recent_instance") or {}).get("ref"),
        (alert.get("most_recent_instance") or {}).get("branch"),
        (alert.get("most_recent_instance") or {}).get("analysis_key"),
        alert.get("branch"),
    ):
        if candidate is None:
            continue
        branch_name = _normalize_branch_name(str(candidate))
        if not branch_name:
            continue
        if branch_name == default_name or branch_name.endswith(f"/{default_name}"):
            return True
    return False


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
        try:
            int_value = int(value or 0)
        except (TypeError, ValueError):
            continue
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


def _artifact_is_valid(path: Path) -> bool:
    if not path.exists() or not path.is_file():
        return False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    if not isinstance(payload, dict):
        return False
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else None
    metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else None
    if summary is not None and summary.get("total_findings") is not None:
        return True
    if metadata is not None and metadata.get("total_findings") is not None:
        return True
    if isinstance(payload.get("findings"), list):
        return True
    if isinstance(payload.get("finding_index"), list):
        return True
    return isinstance(payload.get("findings_by_severity"), dict)


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


def _failure_classification(by_severity: dict[str, int]) -> str:
    critical = int(by_severity.get("CRITICAL", 0) or 0)
    high = int(by_severity.get("HIGH", 0) or 0)
    medium = int(by_severity.get("MEDIUM", 0) or 0)
    low = int(by_severity.get("LOW", 0) or 0)
    if critical or high:
        return "blocked_by_critical_or_high_vulnerabilities"
    if medium or low:
        return "warning_only"
    return "clean"


def _raw_evidence_artifacts(*paths: str | Path) -> list[str]:
    evidence: list[str] = []
    for path in paths:
        if not path:
            continue
        candidate = Path(path)
        if candidate.exists() and candidate.is_file():
            evidence.append(str(candidate))
    return evidence


def _final_recommendation(payload: dict[str, object]) -> str:
    status = str(payload.get("status", "clean")).lower()
    source_of_truth = str(payload.get("source_of_truth", "")).lower()
    if status in {"compliance-unknown", "unknown"}:
        return "advisory-only"
    live_total = int(payload.get("total_open_alerts", 0) or 0)
    artifact_total = int((payload.get("artifact_generated_findings") or {}).get("total_findings", 0) or 0)
    if source_of_truth == "artifact":
        return "advisory-only" if artifact_total > 0 else "compliant"
    if live_total > 0:
        return "action required"
    if artifact_total > 0:
        return "advisory-only"
    return "compliant"


def _classify_alert_balance(live_total: int, artifact_total: int, source_of_truth: str = "live") -> str:
    if source_of_truth == "artifact":
        return "historical_artifact_backlog" if artifact_total > 0 else "no_findings"
    if live_total > 0 and artifact_total > 0:
        if live_total > artifact_total:
            return "live_alerts_exceed_artifact_backlog"
        if live_total < artifact_total:
            return "artifact_backlog_exceeds_live_alerts"
        return "live_alerts_match_artifact_backlog"
    if live_total > 0:
        return "live_alerts_active"
    if artifact_total > 0:
        return "historical_artifact_backlog"
    return "no_findings"


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    security_overview = payload.get("security_overview", {}) if isinstance(payload.get("security_overview"), dict) else {}
    lines = [
        "# 🔐 Live GitHub Security Reconciliation",
        "",
        f"- Repository: `{payload['repo_url']}`",
        f"- Default branch: `{payload['default_branch']}`",
        f"- Default branch only: `{payload['default_branch_only']}`",
        f"- Source of truth: `{payload.get('source_of_truth', 'artifact')}`",
        f"- Last synced: `{payload['last_synced_at']}`",
        "",
        "## GitHub Security views",
        "",
    ]
    for label, url in (payload.get("source_urls") or {}).items():
        lines.append(f"- {label}: `{url}`")
    lines.extend([
        "",
        "## Live open alerts",
        "",
        f"- Total: **{payload['total_open_alerts']}** ({_compact_count(int(payload['total_open_alerts']))})",
        "",
        "| Severity | Count |",
        "|----------|-------|",
    ])
    for severity in SEVERITY_ORDER:
        lines.append(f"| {severity} | {payload['by_severity'].get(severity, 0)} |")

    lines.extend(["", "## By source", "", "| Source | Count |", "|--------|-------|"])
    for source in SOURCE_ORDER:
        lines.append(f"| {source} | {payload['by_source'].get(source, 0)} |")

    artifact_summary = payload.get("artifact_generated_findings", {})
    artifact_total = int(artifact_summary.get("total_findings", 0) or 0)
    lines.extend([
        "",
        "## Artifact-generated findings",
        "",
        f"- Total: **{artifact_total}** ({_compact_count(artifact_total)})",
        "",
    ])
    lines.append("| Severity | Count |")
    lines.append("|----------|-------|")
    for severity in SEVERITY_ORDER:
        lines.append(f"| {severity} | {artifact_summary.get('by_severity', {}).get(severity, 0)} |")

    live_total = int(payload.get("total_open_alerts", 0) or 0)
    stale_total = artifact_total if payload.get("source_of_truth") == "artifact" else max(artifact_total - live_total, 0)
    default_branch_matched = int(security_overview.get("default_branch_matched_active_items", 0) or 0)
    delta_total = payload.get("delta", {}).get("total_findings", 0)
    delta_display = _compact_count(abs(int(delta_total))) if int(delta_total) != 0 else "0"
    evidence_artifacts = payload.get("raw_evidence_artifacts", []) or []
    evidence_text = ", ".join(str(item) for item in evidence_artifacts) if evidence_artifacts else "none"
    lines.extend([
        "",
        "## Evidence package",
        "",
        f"- Source of truth: **{payload.get('source_of_truth', 'artifact')}**",
        f"- Default branch: **{payload.get('default_branch', 'unknown')}**",
        f"- Default branch only: **{payload.get('default_branch_only', False)}**",
        f"- Evidence artifacts: **{evidence_text}**",
        "",
        "## Evidence classification",
        "",
        f"- Live active alerts: **{live_total}**",
        f"- Historical artifact backlog: **{artifact_total}**",
        f"- Default-branch-matched active items: **{default_branch_matched}**",
        f"- Stale or archived findings: **{stale_total}**",
        f"- Pending triage: **{payload.get('needs_triage', False)}**",
        f"- Final recommendation: **{payload.get('final_recommendation', _final_recommendation(payload))}**",
        "",
        "## Delta",
        "",
        f"- Total delta: **{delta_total}** ({delta_display})",
        f"- Needs triage: **{payload.get('needs_triage', False)}**",
        "",
    ])
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
    default_branch = _discover_default_branch(repo)
    artifact_summary = _artifact_summary(Path(artifact_path))
    source_urls = {
        "code_scanning": f"{repo_url}/security/code-scanning",
        "dependabot": f"{repo_url}/security/dependabot",
        "secret_scanning": f"{repo_url}/security/secret-scanning",
    }

    if not _token():
        artifact_total = int(artifact_summary.get("total_findings", 0) or 0)
        severity_summary = {sev: int(artifact_summary.get("by_severity", {}).get(sev, 0) or 0) for sev in SEVERITY_ORDER}
        failure_classification = _failure_classification(severity_summary)
        status = "artifact-only" if artifact_total else "clean"
        final_recommendation = _final_recommendation({
            "status": status,
            "source_of_truth": "artifact",
            "total_open_alerts": artifact_total,
            "artifact_generated_findings": artifact_summary,
        })
        classification = _classify_alert_balance(artifact_total, artifact_total, "artifact")
        return {
            "repo_url": repo_url,
            "default_branch": default_branch,
            "default_branch_only": False,
            "last_synced_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_open_alerts": artifact_total,
            "total_open_alerts_display": _compact_count(artifact_total),
            "by_severity": severity_summary,
            "severity_summary": severity_summary,
            "by_source": {src: 0 for src in SOURCE_ORDER},
            "artifact_generated_findings": artifact_summary,
            "artifact_generated_findings_display": _compact_count(artifact_total),
            "delta": {"total_findings": 0, "needs_triage": artifact_total > 0},
            "needs_triage": artifact_total > 0,
            "source_of_truth": "artifact",
            "status": status,
            "failure_classification": failure_classification,
            "raw_evidence_artifacts": _raw_evidence_artifacts(artifact_path),
            "source_urls": source_urls,
            "classification": classification,
            "final_recommendation": final_recommendation,
            "security_overview": {
                "default_branch": default_branch,
                "default_branch_only": False,
                "repo_url": repo_url,
                "live_active_alerts": artifact_total,
                "historical_artifact_backlog": artifact_total,
                "stale_or_archived_findings": artifact_total,
                "pending_triage": artifact_total > 0,
                "live_open_alerts": artifact_total,
                "artifact_total": artifact_total,
                "classification": classification,
                "severity_summary": severity_summary,
                "source_of_truth": "artifact",
                "status": status,
                "final_recommendation": final_recommendation,
            },
        }

    try:
        repo_meta = _api_get(f"https://api.github.com/repos/{repo}")
        if isinstance(repo_meta, dict):
            default_branch = str(repo_meta.get("default_branch") or default_branch)
    except (error.HTTPError, error.URLError, TimeoutError, ValueError, OSError):
        artifact_total = int(artifact_summary.get("total_findings", 0) or 0)
        severity_summary = {sev: int(artifact_summary.get("by_severity", {}).get(sev, 0) or 0) for sev in SEVERITY_ORDER}
        failure_classification = _failure_classification(severity_summary)
        status = "artifact-only" if artifact_total else "clean"
        final_recommendation = _final_recommendation({
            "status": status,
            "source_of_truth": "artifact",
            "total_open_alerts": artifact_total,
            "artifact_generated_findings": artifact_summary,
        })
        classification = _classify_alert_balance(artifact_total, artifact_total, "artifact")
        return {
            "repo_url": repo_url,
            "default_branch": default_branch,
            "default_branch_only": False,
            "last_synced_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_open_alerts": artifact_total,
            "total_open_alerts_display": _compact_count(artifact_total),
            "by_severity": severity_summary,
            "severity_summary": severity_summary,
            "by_source": {src: 0 for src in SOURCE_ORDER},
            "artifact_generated_findings": artifact_summary,
            "artifact_generated_findings_display": _compact_count(artifact_total),
            "delta": {"total_findings": 0, "needs_triage": artifact_total > 0},
            "needs_triage": artifact_total > 0,
            "source_of_truth": "artifact",
            "status": status,
            "failure_classification": failure_classification,
            "raw_evidence_artifacts": _raw_evidence_artifacts(artifact_path),
            "source_urls": source_urls,
            "classification": classification,
            "final_recommendation": final_recommendation,
            "security_overview": {
                "default_branch": default_branch,
                "default_branch_only": False,
                "repo_url": repo_url,
                "live_active_alerts": artifact_total,
                "historical_artifact_backlog": artifact_total,
                "stale_or_archived_findings": artifact_total,
                "pending_triage": artifact_total > 0,
                "live_open_alerts": artifact_total,
                "artifact_total": artifact_total,
                "classification": classification,
                "severity_summary": severity_summary,
                "source_of_truth": "artifact",
                "status": status,
                "final_recommendation": final_recommendation,
            },
        }

    by_source: dict[str, list[dict[str, object]]] = {
        "code_scanning": [],
        "dependabot": [],
        "secret_scanning": [],
    }
    for source, endpoint in (
        ("code_scanning", _with_default_branch_ref(f"/repos/{repo}/code-scanning/alerts?state=open", default_branch)),
        ("dependabot", f"/repos/{repo}/dependabot/alerts?state=open"),
        ("secret_scanning", _with_default_branch_ref(f"/repos/{repo}/secret-scanning/alerts?state=open", default_branch)),
    ):
        try:
            by_source[source] = _paginate(endpoint)
        except Exception as exc:  # Network/API failures should degrade to artifact fallback rather than fail silently.
            print(f"::warning::Unable to load {source} alerts for {repo}: {exc}", file=sys.stderr)
            by_source[source] = []

    totals: Counter[str] = Counter()
    filtered_source_counts = {source: 0 for source in SOURCE_ORDER}
    for source, alerts in by_source.items():
        filtered_source_counts[source] = len(alerts)
        for alert in alerts:
            totals[_normalize_severity(alert, source)] += 1

    live_total = sum(totals.values())
    artifact_total = int(artifact_summary.get("total_findings", 0) or 0)
    delta_total = live_total - artifact_total
    source_of_truth = "live" if live_total or any(by_source.values()) else "artifact"
    branch_filtered_sources = []
    default_branch_matched_active_items = 0
    for source in ("code_scanning", "secret_scanning"):
        alerts = by_source.get(source, [])
        if not alerts:
            continue
        default_branch_matches = [alert for alert in alerts if _alert_ref_matches_default(alert, default_branch)]
        default_branch_matched_active_items += len(default_branch_matches)
        branch_filtered_sources.append(all(_alert_ref_matches_default(alert, default_branch) for alert in alerts))
    default_branch_only = bool(default_branch) and not by_source.get("dependabot") and (
        not branch_filtered_sources or all(branch_filtered_sources)
    )

    if source_of_truth == "artifact":
        live_total = artifact_total
        totals = Counter({sev: artifact_summary.get("by_severity", {}).get(sev, 0) for sev in SEVERITY_ORDER})
        delta_total = 0
        default_branch_only = False
        default_branch_matched_active_items = 0

    by_severity = {sev: totals.get(sev, 0) for sev in SEVERITY_ORDER}
    severity_summary = {sev: int(by_severity.get(sev, 0) or 0) for sev in SEVERITY_ORDER}
    failure_classification = _failure_classification(severity_summary)

    classification = _classify_alert_balance(live_total, artifact_total, source_of_truth)

    status = "triage-required" if delta_total != 0 else "clean"
    if source_of_truth == "artifact":
        status = "artifact-only" if artifact_total else "clean"
    stale_or_archived_findings = artifact_total if source_of_truth == "artifact" else max(artifact_total - live_total, 0) if artifact_total > 0 else 0
    final_recommendation = "action required" if live_total > 0 and source_of_truth != "artifact" else "advisory-only" if artifact_total > 0 else "compliant"

    return {
        "repo_url": repo_url,
        "default_branch": default_branch,
        "default_branch_only": default_branch_only,
        "last_synced_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_open_alerts": live_total,
        "total_open_alerts_display": _compact_count(live_total),
        "by_severity": by_severity,
        "severity_summary": severity_summary,
        "by_source": {src: filtered_source_counts.get(src, 0) for src in SOURCE_ORDER},
        "artifact_generated_findings": artifact_summary,
        "artifact_generated_findings_display": _compact_count(artifact_total),
        "delta": {"total_findings": delta_total, "needs_triage": delta_total != 0},
        "needs_triage": delta_total != 0 or artifact_total > 0,
        "source_of_truth": source_of_truth,
        "status": status,
        "failure_classification": failure_classification,
        "raw_evidence_artifacts": _raw_evidence_artifacts(artifact_path),
        "source_urls": source_urls,
        "classification": classification,
        "final_recommendation": final_recommendation,
        "security_overview": {
            "default_branch": default_branch,
            "default_branch_only": default_branch_only,
            "repo_url": repo_url,
            "live_active_alerts": live_total,
            "historical_artifact_backlog": artifact_total,
            "stale_or_archived_findings": stale_or_archived_findings,
            "default_branch_matched_active_items": default_branch_matched_active_items,
            "pending_triage": delta_total != 0 or artifact_total > 0,
            "live_open_alerts": live_total,
            "artifact_total": artifact_total,
            "classification": classification,
            "severity_summary": severity_summary,
            "source_of_truth": source_of_truth,
            "status": status,
            "final_recommendation": final_recommendation,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "Aries-Serpent/_codex_"))
    parser.add_argument("--artifact", default=".codex/security-findings-comprehensive.json")
    parser.add_argument("--output", default=".codex/live-security-reconciliation.json")
    parser.add_argument("--markdown", default=".codex/live-security-reconciliation.md")
    parser.add_argument("--strict-artifact", action="store_true", help="Fail when the security artifact is missing or invalid.")
    parser.add_argument("--require-live-source", action="store_true", help="Fail when live security data is unavailable and artifact fallback must not be treated as authoritative.")
    parser.add_argument("--fail-on-delta", action="store_true", help="Fail when live alerts and artifact totals disagree.")
    args = parser.parse_args()

    payload = _build_payload(args.repo, args.artifact)
    artifact_path = Path(args.artifact)
    if args.strict_artifact and not _artifact_is_valid(artifact_path):
        print(f"::error::Missing or invalid security artifact at {args.artifact}", file=sys.stderr)
        return 2
    if args.require_live_source and payload.get("source_of_truth") == "artifact":
        print("::error::Live GitHub security data is unavailable; refusing to treat the generated artifact as the source of truth.", file=sys.stderr)
        return 2
    if args.fail_on_delta and payload.get("delta", {}).get("total_findings", 0) != 0:
        print("::error::Live GitHub security totals differ from the generated artifact by %s; workflow should stop and reconcile before continuing." % payload["delta"]["total_findings"], file=sys.stderr)
        return 2

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _write_markdown(Path(args.markdown), payload)

    print(json.dumps({
        "repo": args.repo,
        "total_open_alerts": payload["total_open_alerts"],
        "total_open_alerts_display": payload.get("total_open_alerts_display", _compact_count(int(payload["total_open_alerts"]))),
        "artifact_generated_findings": payload["artifact_generated_findings"]["total_findings"],
        "artifact_generated_findings_display": payload.get("artifact_generated_findings_display", _compact_count(int(payload["artifact_generated_findings"]["total_findings"]))),
        "by_severity": payload["by_severity"],
        "severity_summary": payload.get("severity_summary", payload.get("by_severity", {})),
        "by_source": payload["by_source"],
        "delta": payload["delta"]["total_findings"],
        "source_of_truth": payload.get("source_of_truth", "artifact"),
        "status": payload.get("status", "clean"),
        "failure_classification": payload.get("failure_classification", _failure_classification(payload.get("by_severity", {}))),
        "raw_evidence_artifacts": payload.get("raw_evidence_artifacts", []),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
