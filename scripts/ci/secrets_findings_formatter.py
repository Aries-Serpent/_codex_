#!/usr/bin/env python3
"""
Secrets Detection Categorizer Module - Phase 8C Security Findings Integration.

Categorizes secret findings from detect-secrets, truffleHog, gitLeaks analysis:
- Groups by secret type (API keys, tokens, credentials, DB passwords, etc.)
- Calculates rotation requirements and urgency deadlines
- Generates remediation steps and markdown reports
- Provides comprehensive metadata and statistics

Stdlib only, zero external dependencies.
"""

import json
import sys
from argparse import ArgumentParser
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List


# Secret Type Classification Database
SECRET_TYPES: Dict[str, Dict[str, Any]] = {
    "AWS_API_KEY": {
        "description": "Amazon Web Services API Key",
        "urgency": "CRITICAL",
        "rotation_hours": 6,
        "patterns": ["AKIA", "aws_access_key_id"],
    },
    "GITHUB_PAT": {
        "description": "GitHub Personal Access Token",
        "urgency": "CRITICAL",
        "rotation_hours": 6,
        "patterns": ["ghp_", "github_token"],
    },
    "OPENAI_KEY": {
        "description": "OpenAI API Key",
        "urgency": "CRITICAL",
        "rotation_hours": 6,
        "patterns": ["sk-", "openai"],
    },
    "PRIVATE_KEY": {
        "description": "Private Key (RSA/ED25519)",
        "urgency": "CRITICAL",
        "rotation_hours": 6,
        "patterns": ["BEGIN PRIVATE KEY", "BEGIN RSA PRIVATE KEY"],
    },
    "DB_PASSWORD": {
        "description": "Database Password or Connection String",
        "urgency": "CRITICAL",
        "rotation_hours": 6,
        "patterns": ["postgresql://", "mongodb+srv://", "mysql://"],
    },
    "STRIPE_KEY": {
        "description": "Stripe API Key",
        "urgency": "CRITICAL",
        "rotation_hours": 6,
        "patterns": ["sk_live_", "pk_live_", "rk_live_"],
    },
    "SLACK_TOKEN": {
        "description": "Slack Bot or User Token",
        "urgency": "HIGH",
        "rotation_hours": 24,
        "patterns": ["xoxb-", "xoxp-"],
    },
    "JWT_TOKEN": {
        "description": "JSON Web Token",
        "urgency": "HIGH",
        "rotation_hours": 24,
        "patterns": ["eyJ"],
    },
    "API_KEY": {
        "description": "Generic API Key",
        "urgency": "HIGH",
        "rotation_hours": 24,
        "patterns": ["api_key", "apikey"],
    },
    "ENV_CREDENTIAL": {
        "description": "Environment Variable Credential",
        "urgency": "MEDIUM",
        "rotation_hours": 168,
        "patterns": ["password", "secret", "token"],
    },
}

# Urgency to severity mapping
URGENCY_ORDER: Dict[str, int] = {
    "CRITICAL": 4,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1,
}


def _parse_secret_type(finding: Dict[str, Any]) -> str:
    """
    Determine secret type from finding data.

    Args:
        finding: Individual finding dictionary

    Returns:
        Secret type string (e.g., "AWS_API_KEY")
    """
    description = finding.get("description", "").lower()
    cwe = finding.get("cwe", "").lower()
    tool = finding.get("tool", "").lower()

    # Pattern matching on description and CWE
    if "aws" in description or "akia" in description:
        return "AWS_API_KEY"
    if "github" in description or "ghp_" in description:
        return "GITHUB_PAT"
    if "openai" in description or "sk-" in description:
        return "OPENAI_KEY"
    if "private key" in description or "private" in description and "key" in description:
        return "PRIVATE_KEY"
    if (
        "database" in description
        or "connection" in description
        or "postgresql" in description
        or "mongodb" in description
    ):
        return "DB_PASSWORD"
    if "stripe" in description:
        return "STRIPE_KEY"
    if "slack" in description:
        return "SLACK_TOKEN"
    if "jwt" in description or "eyj" in description:
        return "JWT_TOKEN"
    if "api" in description and "key" in description:
        return "API_KEY"
    if "env" in description or "environment" in description:
        return "ENV_CREDENTIAL"

    # Fallback to generic API_KEY
    return "API_KEY"


def _calculate_rotation_deadline(urgency: str) -> str:
    """
    Calculate rotation deadline based on urgency level.

    Args:
        urgency: Urgency level (CRITICAL, HIGH, MEDIUM, LOW)

    Returns:
        ISO 8601 datetime string for rotation deadline
    """
    secret_info = SECRET_TYPES.get("AWS_API_KEY")  # Get default
    for stype, info in SECRET_TYPES.items():
        if info["urgency"] == urgency:
            secret_info = info
            break

    hours = secret_info.get("rotation_hours", 168)
    deadline = datetime.now(timezone.utc) + timedelta(hours=hours)
    return deadline.strftime("%Y-%m-%dT%H:%M:%SZ")


def _generate_remediation_steps(secret_type: str, file_path: str) -> str:
    """
    Generate remediation steps for a specific secret type.

    Args:
        secret_type: Type of secret (AWS_API_KEY, GITHUB_PAT, etc.)
        file_path: Path where secret was found

    Returns:
        Formatted remediation steps
    """
    steps: Dict[str, List[str]] = {
        "AWS_API_KEY": [
            "1. Revoke the exposed AWS key in IAM console immediately",
            "2. Delete from local config/.env",
            "3. Regenerate new key in AWS",
            "4. Update .env and config files with new key",
            "5. Commit with MESSAGE: 'Fix(sec): Rotated AWS API key'",
            "6. Force push to remove from history",
        ],
        "GITHUB_PAT": [
            "1. Delete PAT in GitHub settings → Developer settings",
            "2. Remove from .env and source code",
            "3. Generate new PAT with minimal required scopes",
            "4. Update config with new token",
            "5. Commit with MESSAGE: 'Fix(sec): Rotated GitHub PAT'",
            "6. Review all recent API calls to token",
        ],
        "PRIVATE_KEY": [
            "1. Backup current key for transition period",
            "2. Generate new RSA-2048 or ED25519 key pair",
            "3. Deploy new public key everywhere",
            "4. Remove private key from repository",
            "5. Update deployment systems with new key",
            "6. Revoke old key after verification period",
        ],
        "DB_PASSWORD": [
            "1. Change password in database immediately",
            "2. Update connection string in .env",
            "3. Remove hardcoded password from config",
            "4. Use secrets manager (AWS Secrets Manager, etc.)",
            "5. Restart database client connections",
            "6. Audit database access logs for unauthorized access",
        ],
        "OPENAI_KEY": [
            "1. Revoke key in OpenAI dashboard",
            "2. Remove from .env and source files",
            "3. Generate new API key",
            "4. Update app configuration",
            "5. Commit with MESSAGE: 'Fix(sec): Rotated OpenAI key'",
            "6. Monitor API usage for suspicious activity",
        ],
    }

    default_steps = [
        "1. Identify the secret type and location",
        "2. Revoke the exposed secret in the issuing system",
        "3. Remove secret from source code",
        "4. Generate replacement credentials",
        "5. Update all configuration files",
        "6. Commit with MESSAGE: 'Fix(sec): Rotated credentials'",
    ]

    return " | ".join(steps.get(secret_type, default_steps))


def _convert_confidence_to_percent(confidence: Any) -> str:
    """
    Convert confidence value to percentage string.

    Args:
        confidence: Confidence as float (0-1), int (0-100), or string

    Returns:
        Formatted percentage string (e.g., "95%")
    """
    if isinstance(confidence, str):
        return confidence if "%" in confidence else f"{confidence}%"
    if isinstance(confidence, (int, float)):
        if confidence <= 1.0:
            return f"{int(confidence * 100)}%"
        return f"{int(confidence)}%"
    return "100%"


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


def _filter_secret_findings(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter findings to only secrets (CWE-798).

    Args:
        findings: List of all finding dictionaries

    Returns:
        Filtered list of secret findings
    """
    secret_tools = {"detect-secrets", "truffleHog", "gitLeaks"}
    secret_cwes = {"CWE-798"}

    filtered: List[Dict[str, Any]] = []
    for finding in findings:
        tool = finding.get("tool", "").lower()
        cwe = finding.get("cwe", "")

        if tool in secret_tools or cwe in secret_cwes:
            filtered.append(finding)

    return filtered


def categorize_secret_findings(findings_json_path: str) -> Dict[str, Any]:
    """
    Categorize secret findings from comprehensive cache.

    Args:
        findings_json_path: Path to comprehensive findings JSON cache

    Returns:
        Dictionary with categorized secrets, rotation requirements, and metadata

    Raises:
        FileNotFoundError: If cache file not found
        json.JSONDecodeError: If cache JSON is invalid
    """
    # Load and filter findings
    all_findings = _load_findings(findings_json_path)
    secret_findings = _filter_secret_findings(all_findings)

    # Group by secret type
    secret_categories: Dict[str, Dict[str, Any]] = {}

    for finding in secret_findings:
        secret_type = _parse_secret_type(finding)
        if secret_type not in secret_categories:
            secret_info = SECRET_TYPES.get(secret_type, SECRET_TYPES["API_KEY"])
            secret_categories[secret_type] = {
                "type": secret_type,
                "count": 0,
                "rotation_urgency": secret_info["urgency"],
                "rotation_deadline": _calculate_rotation_deadline(
                    secret_info["urgency"]
                ),
                "findings": [],
            }

        # Add finding to category
        secret_categories[secret_type]["count"] += 1
        secret_categories[secret_type]["findings"].append(
            {
                "secret_type": secret_type,
                "file": f"{finding.get('file_path', 'unknown')}:{finding.get('line_number', '?')}",
                "tool": finding.get("tool", "Unknown"),
                "confidence": _convert_confidence_to_percent(
                    finding.get("confidence", 1.0)
                ),
                "remediation": _generate_remediation_steps(
                    secret_type, finding.get("file_path", "")
                ),
                "allowlist": False,
            }
        )

    # Calculate metadata
    total_secrets = len(secret_findings)
    critical_count = sum(
        1
        for cat in secret_categories.values()
        if cat["rotation_urgency"] == "CRITICAL"
    )
    high_count = sum(
        1 for cat in secret_categories.values() if cat["rotation_urgency"] == "HIGH"
    )
    medium_count = sum(
        1 for cat in secret_categories.values() if cat["rotation_urgency"] == "MEDIUM"
    )

    # Build output structure
    output: Dict[str, Any] = {
        "secret_categories": sorted(
            secret_categories.values(),
            key=lambda x: URGENCY_ORDER.get(x["rotation_urgency"], 0),
            reverse=True,
        ),
        "metadata": {
            "total_secrets": total_secrets,
            "critical_count": critical_count,
            "high_count": high_count,
            "medium_count": medium_count,
            "secret_types": len(secret_categories),
            "rotation_status": f"{critical_count} expired, {high_count} due soon, {medium_count} ok",
            "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
        },
    }

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
    lines.append("# Secrets Detection Report")
    lines.append("")

    # Metadata
    meta = formatted["metadata"]
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total Secrets Found**: {meta['total_secrets']}")
    lines.append(f"- **Critical**: {meta['critical_count']}")
    lines.append(f"- **High**: {meta['high_count']}")
    lines.append(f"- **Medium**: {meta['medium_count']}")
    lines.append(f"- **Secret Types**: {meta['secret_types']}")
    lines.append(f"- **Status**: {meta['rotation_status']}")
    lines.append(f"- **Generated**: {meta['generated_at']}")
    lines.append("")
    lines.append("⚠️ **ACTION REQUIRED**: Rotate exposed secrets immediately!")
    lines.append("")

    # Secrets by category
    lines.append("## Secrets by Category")
    lines.append("")

    for category in formatted["secret_categories"]:
        secret_type = category["type"]
        count = category["count"]
        urgency = category["rotation_urgency"]
        deadline = category["rotation_deadline"]

        lines.append(f"### {secret_type}")
        lines.append("")
        lines.append(
            f"**Urgency**: `{urgency}` | **Count**: {count} | "
            f"**Deadline**: {deadline}"
        )
        lines.append("")

        for i, finding in enumerate(category["findings"], 1):
            lines.append(f"#### Secret {i}")
            lines.append("")
            lines.append(f"- **Location**: `{finding['file']}`")
            lines.append(f"- **Tool**: {finding['tool']}")
            lines.append(f"- **Confidence**: {finding['confidence']}")
            lines.append(f"- **Remediation**: {finding['remediation']}")
            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(
        "**Generated by Phase 8C Secrets Categorizer** | "
        "Contact @secret-detection-agent for rotation assistance"
    )

    return "\n".join(lines)


def main() -> int:
    """
    CLI entry point for secrets formatter.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = ArgumentParser(description="Categorize secrets detection findings")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # categorize-secrets subcommand
    cat_cmd = subparsers.add_parser(
        "categorize-secrets", help="Categorize secret findings"
    )
    cat_cmd.add_argument(
        "--findings",
        required=True,
        help="Path to comprehensive findings JSON cache",
    )
    cat_cmd.add_argument(
        "--output",
        default="secrets-formatted.json",
        help="Output JSON file path",
    )
    cat_cmd.add_argument(
        "--markdown",
        help="Optional markdown report output path",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        # Categorize findings
        # lgtm[py/clear-text-storage]: Processing secret metadata only (types, locations),
        # not actual secret values. Secret hashes never stored/written in output.
        formatted = categorize_secret_findings(args.findings)

        # Write JSON output
        # lgtm[py/clear-text-storage]: Output contains only finding metadata (file, type,
        # remediation steps), not actual secret values or hashes
        output_path = Path(args.output)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(formatted, f, indent=2)
        print(f"✓ Categorized secrets written to: {args.output}")

        # Write markdown report if requested
        if args.markdown:
            # lgtm[py/clear-text-storage]: Markdown report contains only finding metadata
            # (file paths, secret types, rotation urgency), not actual secret values
            markdown_content = _generate_markdown_report(formatted)
            md_path = Path(args.markdown)
            with open(md_path, "w", encoding="utf-8") as f:
                # lgtm[py/clear-text-storage]: Metadata-only report for agent handoff
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
