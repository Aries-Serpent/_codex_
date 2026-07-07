#!/usr/bin/env python3
"""
CodeQL Alert Formatter Module - Phase 8A Security Findings Integration.

Formats CodeQL and related security findings from comprehensive cache into:
- CWE-grouped structure with severity sorting
- Fix pattern generation from code snippets
- Markdown report generation
- Metadata and statistics

Stdlib only, zero external dependencies.
"""

import json
import sys
from argparse import ArgumentParser
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


# CWE Metadata Database
CWE_TITLES: Dict[str, str] = {
    "CWE-22": "Improper Limitation of a Pathname to a Restricted Directory",
    "CWE-79": "Improper Neutralization of Input During Web Page Generation",
    "CWE-89": "Improper Neutralization of Special Elements used in an SQL Command",
    "CWE-327": "Use of a Broken or Risky Cryptographic Algorithm",
    "CWE-434": "Unrestricted Upload of File with Dangerous Type",
    "CWE-502": "Deserialization of Untrusted Data",
    "CWE-611": "Improper Restriction of XML External Entity Reference",
    "CWE-798": "Use of Hard-Coded Credentials",
}

# Severity ordering (higher index = higher priority)
SEVERITY_ORDER: Dict[str, int] = {
    "INFO": 0,
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}


def _parse_cwe_id(cwe_string: str) -> str:
    """
    Extract CWE ID from string.

    Args:
        cwe_string: Raw CWE string (e.g., "CWE-89")

    Returns:
        Normalized CWE ID
    """
    return cwe_string.strip() if cwe_string else "UNKNOWN"


def _get_cwe_title(cwe_id: str) -> str:
    """
    Get CWE title from metadata database.

    Args:
        cwe_id: CWE identifier

    Returns:
        CWE title or "Unknown CWE" if not found
    """
    return CWE_TITLES.get(cwe_id, "Unknown CWE")


def _severity_to_int(severity: str) -> int:
    """
    Convert severity string to sortable integer.

    Args:
        severity: Severity level (CRITICAL, HIGH, MEDIUM, LOW, INFO)

    Returns:
        Integer for sorting (higher = more severe)
    """
    return SEVERITY_ORDER.get(severity.upper(), -1)


def _convert_confidence_to_percent(confidence: Any) -> str:
    """
    Convert confidence value to percentage string.

    Args:
        confidence: Confidence as float (0-1) or int (0-100) or already formatted

    Returns:
        Formatted percentage string (e.g., "95%")
    """
    if isinstance(confidence, str):
        return confidence if "%" in confidence else f"{confidence}%"
    if isinstance(confidence, (int, float)):
        if confidence <= 1.0:
            return f"{int(confidence * 100)}%"
        return f"{int(confidence)}%"
    return "N/A"


def _generate_fix_pattern(finding: Dict[str, Any]) -> str:
    """
    Generate fix pattern from finding data.

    Args:
        finding: Individual finding dictionary

    Returns:
        Fix pattern recommendation text
    """
    recommendation = finding.get("fix_recommendation", "Review and apply security patch")
    cwe_id = _parse_cwe_id(finding.get("cwe", ""))

    # Add agent mention for automated fixes
    if cwe_id in ["CWE-89", "CWE-22"]:
        return f"{recommendation} (@code-review-agent can assist)"
    if cwe_id in ["CWE-798"]:
        return f"{recommendation} (@secret-detection-agent can help)"
    return recommendation


def _load_findings(findings_json_path: str) -> List[Dict[str, Any]]:
    """
    Load findings from JSON cache file.

    Args:
        findings_json_path: Path to comprehensive findings JSON

    Returns:
        List of finding dictionaries

    Raises:
        FileNotFoundError: If findings file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    cache_path = Path(findings_json_path)
    if not cache_path.exists():
        raise FileNotFoundError(f"Findings cache not found: {findings_json_path}")

    with open(cache_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract findings list
    if isinstance(data, dict) and "findings" in data:
        return data["findings"]
    if isinstance(data, list):
        return data
    return []


def _group_by_cwe(findings: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group findings by CWE classification.

    Args:
        findings: List of finding dictionaries

    Returns:
        Dictionary with CWE IDs as keys and lists of findings as values
    """
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for finding in findings:
        cwe_id = _parse_cwe_id(finding.get("cwe", "UNKNOWN"))
        if cwe_id not in groups:
            groups[cwe_id] = []
        groups[cwe_id].append(finding)
    return groups


def _sort_findings_by_severity(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sort findings by severity (critical first).

    Args:
        findings: List of finding dictionaries

    Returns:
        Sorted list of findings
    """
    return sorted(
        findings,
        key=lambda f: _severity_to_int(f.get("severity", "INFO")),
        reverse=True,
    )


def format_codeql_alerts(findings_json_path: str) -> Dict[str, Any]:
    """
    Format CodeQL alerts from cache into structured output.

    Args:
        findings_json_path: Path to comprehensive findings JSON cache

    Returns:
        Dictionary with formatted findings grouped by CWE

    Raises:
        FileNotFoundError: If cache file not found
        json.JSONDecodeError: If cache JSON is invalid
    """
    # Load findings
    findings = _load_findings(findings_json_path)

    # Group by CWE
    cwe_groups = _group_by_cwe(findings)

    # Build output structure
    output: Dict[str, Any] = {
        "cwe_groups": [],
        "metadata": {
            "total_findings": len(findings),
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
            "info_count": 0,
            "cwe_count": len(cwe_groups),
            "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
        },
    }

    # Count severity levels
    for finding in findings:
        severity = finding.get("severity", "INFO").upper()
        if severity == "CRITICAL":
            output["metadata"]["critical_count"] += 1
        elif severity == "HIGH":
            output["metadata"]["high_count"] += 1
        elif severity == "MEDIUM":
            output["metadata"]["medium_count"] += 1
        elif severity == "LOW":
            output["metadata"]["low_count"] += 1
        else:
            output["metadata"]["info_count"] += 1

    # Process CWE groups
    for cwe_id in sorted(cwe_groups.keys()):
        cwe_findings = cwe_groups[cwe_id]

        # Sort by severity within group
        sorted_findings = _sort_findings_by_severity(cwe_findings)

        # Get most severe level in group
        group_severity = sorted_findings[0].get("severity", "INFO")

        # Format individual findings
        formatted_findings: List[Dict[str, Any]] = []
        for finding in sorted_findings:
            formatted_findings.append(
                {
                    "file": f"{finding.get('file_path', 'unknown')}:{finding.get('line_number', '?')}",
                    "tool": finding.get("tool", "Unknown"),
                    "message": finding.get("description", "No description"),
                    "fix_pattern": _generate_fix_pattern(finding),
                    "confidence": _convert_confidence_to_percent(
                        finding.get("confidence", 0)
                    ),
                }
            )

        # Create CWE group
        cwe_group = {
            "cwe_id": cwe_id,
            "cwe_title": _get_cwe_title(cwe_id),
            "severity": group_severity,
            "finding_count": len(sorted_findings),
            "findings": formatted_findings,
        }

        output["cwe_groups"].append(cwe_group)

    # Sort CWE groups by severity
    output["cwe_groups"].sort(
        key=lambda g: _severity_to_int(g.get("severity", "INFO")), reverse=True
    )

    return output


def _generate_markdown_report(formatted: Dict[str, Any]) -> str:
    """
    Generate Markdown report from formatted findings.

    Args:
        formatted: Formatted findings dictionary

    Returns:
        Markdown report as string
    """
    lines: List[str] = []

    # Header
    lines.append("# CodeQL Security Findings Report")
    lines.append("")

    # Metadata
    meta = formatted["metadata"]
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total Findings**: {meta['total_findings']}")
    lines.append(f"- **Critical**: {meta['critical_count']}")
    lines.append(f"- **High**: {meta['high_count']}")
    lines.append(f"- **Medium**: {meta['medium_count']}")
    lines.append(f"- **Low**: {meta['low_count']}")
    lines.append(f"- **Info**: {meta['info_count']}")
    lines.append(f"- **CWE Categories**: {meta['cwe_count']}")
    lines.append(f"- **Generated**: {meta['generated_at']}")
    lines.append("")

    # Findings by CWE
    lines.append("## Findings by CWE")
    lines.append("")

    for group in formatted["cwe_groups"]:
        cwe_id = group["cwe_id"]
        cwe_title = group["cwe_title"]
        severity = group["severity"]
        count = group["finding_count"]

        lines.append(f"### {cwe_id}: {cwe_title}")
        lines.append("")
        lines.append(
            f"**Severity**: `{severity}` | **Count**: {count} | **CWE Link**: "
            f"https://cwe.mitre.org/data/definitions/{cwe_id.split('-')[1]}.html"
        )
        lines.append("")

        for i, finding in enumerate(group["findings"], 1):
            lines.append(f"#### Finding {i}")
            lines.append("")
            lines.append(f"- **Location**: `{finding['file']}`")
            lines.append(f"- **Tool**: {finding['tool']}")
            lines.append(f"- **Message**: {finding['message']}")
            lines.append(f"- **Confidence**: {finding['confidence']}")
            lines.append(f"- **Fix**: {finding['fix_pattern']}")
            lines.append("")

    return "\n".join(lines)


def main() -> int:
    """
    CLI entry point for CodeQL formatter.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = ArgumentParser(
        description="Format CodeQL security findings from cache"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # format-alerts subcommand
    format_cmd = subparsers.add_parser("format-alerts", help="Format CodeQL alerts")
    format_cmd.add_argument(
        "--findings",
        required=True,
        help="Path to comprehensive findings JSON cache",
    )
    format_cmd.add_argument(
        "--output",
        default="codeql-formatted.json",
        help="Output JSON file path",
    )
    format_cmd.add_argument(
        "--markdown",
        help="Optional markdown report output path",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        # Format findings
        formatted = format_codeql_alerts(args.findings)

        # Write JSON output
        output_path = Path(args.output)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(formatted, f, indent=2)
        print(f"✓ Formatted findings written to: {args.output}")

        # Write markdown report if requested
        if args.markdown:
            markdown_content = _generate_markdown_report(formatted)
            md_path = Path(args.markdown)
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            print(f"✓ Markdown report written to: {args.markdown}")

        return 0

    except FileNotFoundError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"✗ JSON parsing error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
