#!/usr/bin/env python3
"""
Dependency Security Findings Formatter

Purpose:
    Format dependency vulnerabilities from security findings cache into
    agent-ready format with upgrade recommendations and risk assessment.
    Targets the dependency-security-review-agent for autonomous remediation.

Usage:
    python scripts/ci/dependency_findings_formatter.py format-deps \
      --findings .codex/security-findings-comprehensive.json \
      --output dependency-formatted.json \
      --markdown dependency-report.md

Exit Codes:
    0: Success
    1: Error (file I/O, validation, etc.)
    2: No dependency findings found
"""

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DEFAULT_FINDINGS_FILE = Path(".codex/security-findings-comprehensive.json")
DEPENDENCY_TOOLS = {"pip-audit", "safety", "requirements-analysis"}
SEVERITY_LEVELS = {"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"}


def load_findings(findings_path: str) -> List[Dict[str, Any]]:
    """
    Load security findings from JSON file.
    
    Args:
        findings_path: Path to comprehensive findings JSON.
        
    Returns:
        List of security findings.
        
    Raises:
        FileNotFoundError: If findings file does not exist.
        json.JSONDecodeError: If JSON is invalid.
    """
    path = Path(findings_path)
    if not path.exists():
        raise FileNotFoundError(f"Findings file not found: {findings_path}")
    
    with open(path, 'r') as f:
        data = json.load(f)
        return data.get("findings", [])


def extract_package_name(description: str) -> Optional[str]:
    """
    Extract package name from finding description.
    
    Args:
        description: Vulnerability description text.
        
    Returns:
        Extracted package name or None.
    """
    # Match patterns like "numpy 1.21.0", "requests >= 2.25.0", etc.
    patterns = [
        r"(?:vulnerability in|update|upgrade)\s+(\w+)",
        r"^(\w+)\s+(?:\d+\.\d+|[><]=?)",
        r"package\s+(\w+)",
        r"^(\w+)$",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            return match.group(1).lower()
    return None


def parse_version(version_str: str) -> Tuple[int, int, int]:
    """
    Parse semantic version string to tuple for comparison.
    
    Args:
        version_str: Version string like "1.2.3" or "1.2".
        
    Returns:
        Tuple of (major, minor, patch) integers.
    """
    parts = version_str.split('.')
    try:
        major = int(parts[0]) if len(parts) > 0 else 0
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        return (major, minor, patch)
    except (ValueError, IndexError):
        return (0, 0, 0)


def calculate_upgrade_path(
    package: str,
    current_version: str,
    findings: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate safe upgrade path for vulnerable package.
    
    Args:
        package: Package name.
        current_version: Current installed version.
        findings: List of findings for this package.
        
    Returns:
        Dict with upgrade recommendation and risk assessment.
    """
    # Find minimum fixed version from all vulnerabilities
    min_fixed = None
    has_breaking_changes = False
    
    for finding in findings:
        fix_rec = finding.get("fix_recommendation", "")
        # Extract version if mentioned in fix recommendation
        version_match = re.search(r"(?:>= |>= v|update to |to )(\d+\.\d+(?:\.\d+)?)", fix_rec)
        if version_match:
            fixed_version = version_match.group(1)
            if min_fixed is None:
                min_fixed = fixed_version
            else:
                # Compare versions (simple semantic versioning)
                if parse_version(fixed_version) > parse_version(min_fixed):
                    min_fixed = fixed_version
        
        # Check for breaking changes indicators
        if any(word in fix_rec.lower() for word in ["major", "breaking", "incompatible"]):
            has_breaking_changes = True
    
    if not min_fixed:
        min_fixed = current_version
    
    current_parsed = parse_version(current_version)
    fixed_parsed = parse_version(min_fixed)
    
    # Detect major version change
    major_bump = fixed_parsed[0] > current_parsed[0]
    risk_level = "HIGH" if major_bump or has_breaking_changes else "LOW"
    
    return {
        "target_version": min_fixed,
        "breaking_changes": major_bump or has_breaking_changes,
        "risk_level": risk_level,
        "is_major_upgrade": major_bump,
    }


def filter_dependency_findings(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter findings to only dependency/package vulnerabilities.
    
    Args:
        findings: All security findings.
        
    Returns:
        Filtered findings from pip-audit, Safety, etc.
    """
    dependency_findings = []
    for finding in findings:
        tool = finding.get("tool", "").lower()
        # Match against known dependency analysis tools
        if any(dep_tool in tool for dep_tool in ["pip-audit", "safety", "requirements"]):
            dependency_findings.append(finding)
        # Also include findings with "package" in description
        elif "package" in finding.get("description", "").lower():
            dependency_findings.append(finding)
    
    return dependency_findings


def group_by_package(
    findings: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group findings by package name.
    
    Args:
        findings: List of dependency findings.
        
    Returns:
        Dict mapping package name to list of findings.
    """
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    
    for finding in findings:
        # Try to extract package name from various fields
        package = None
        
        # First try explicit package field
        if "package" in finding:
            package = finding["package"].lower()
        # Then try description
        elif "description" in finding:
            package = extract_package_name(finding["description"])
        # Fall back to file path package indicator
        elif "file_path" in finding:
            file_match = re.search(r"requirements[.-]([a-z0-9]+)", finding["file_path"])
            if file_match:
                package = file_match.group(1)
        
        if package:
            if package not in grouped:
                grouped[package] = []
            grouped[package].append(finding)
    
    return grouped


def format_dependency_vulnerabilities(findings_json_path: str) -> Dict[str, Any]:
    """
    Format dependency vulnerabilities for agent consumption.
    
    Args:
        findings_json_path: Path to security findings JSON.
        
    Returns:
        Formatted output with package grouping and upgrade recommendations.
    """
    # Load and filter findings
    all_findings = load_findings(findings_json_path)
    dep_findings = filter_dependency_findings(all_findings)
    
    if not dep_findings:
        logger.warning("No dependency findings detected")
        return {
            "vulnerable_packages": [],
            "metadata": {
                "total_vulnerabilities": 0,
                "critical_count": 0,
                "safe_upgrades": 0,
                "risky_upgrades": 0,
                "packages_affected": 0,
                "generated_at": datetime.now(timezone.utc).isoformat() + "Z"
            }
        }
    
    # Group by package
    grouped = group_by_package(dep_findings)
    
    # Format output
    vulnerable_packages = []
    critical_count = 0
    safe_upgrades = 0
    risky_upgrades = 0
    
    for package, package_findings in grouped.items():
        for finding in package_findings:
            severity = finding.get("severity", "MEDIUM")
            if severity == "CRITICAL":
                critical_count += 1
            
            # Extract version if available
            current_version = extract_version_from_finding(finding)
            
            # Calculate upgrade path
            upgrade_info = calculate_upgrade_path(package, current_version, package_findings)
            
            if upgrade_info["risk_level"] == "LOW":
                safe_upgrades += 1
            else:
                risky_upgrades += 1
            
            vulnerable_packages.append({
                "package": package,
                "current_version": current_version,
                "vulnerability": finding.get("description", "Unknown vulnerability"),
                "severity": severity,
                "cve_id": extract_cve_id(finding),
                "safe_upgrade": upgrade_info,
                "tool": finding.get("tool", "unknown"),
                "confidence": f"{int(finding.get('confidence', 0.8) * 100)}%"
            })
    
    return {
        "vulnerable_packages": vulnerable_packages,
        "metadata": {
            "total_vulnerabilities": len(vulnerable_packages),
            "critical_count": critical_count,
            "safe_upgrades": safe_upgrades,
            "risky_upgrades": risky_upgrades,
            "packages_affected": len(grouped),
            "generated_at": datetime.now(timezone.utc).isoformat() + "Z"
        }
    }


def extract_version_from_finding(finding: Dict[str, Any]) -> str:
    """
    Extract version information from finding.
    
    Args:
        finding: Security finding dictionary.
        
    Returns:
        Version string or "unknown".
    """
    if "version" in finding:
        return finding["version"]
    
    # Try to extract from description
    match = re.search(r"(\d+\.\d+(?:\.\d+)?)", finding.get("description", ""))
    if match:
        return match.group(1)
    
    return "unknown"


def extract_cve_id(finding: Dict[str, Any]) -> str:
    """
    Extract CVE ID from finding.
    
    Args:
        finding: Security finding dictionary.
        
    Returns:
        CVE ID string or empty string.
    """
    if "cve_id" in finding:
        return finding["cve_id"]
    
    # Try to extract from description
    match = re.search(r"(CVE-\d{4}-\d{4,})", finding.get("description", ""))
    if match:
        return match.group(1)
    
    return ""


def generate_markdown_report(formatted_data: Dict[str, Any]) -> str:
    """
    Generate markdown report from formatted findings.
    
    Args:
        formatted_data: Output from format_dependency_vulnerabilities.
        
    Returns:
        Markdown formatted report.
    """
    lines = [
        "# Dependency Security Report",
        "",
        f"Generated: {formatted_data['metadata']['generated_at']}",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Total Vulnerabilities | {formatted_data['metadata']['total_vulnerabilities']} |",
        f"| Critical | {formatted_data['metadata']['critical_count']} |",
        f"| Safe Upgrades | {formatted_data['metadata']['safe_upgrades']} |",
        f"| Risky Upgrades | {formatted_data['metadata']['risky_upgrades']} |",
        f"| Packages Affected | {formatted_data['metadata']['packages_affected']} |",
        "",
    ]
    
    if formatted_data["vulnerable_packages"]:
        lines.extend([
            "## Vulnerable Packages",
            "",
        ])
        
        for pkg in formatted_data["vulnerable_packages"]:
            lines.extend([
                f"### {pkg['package']} (current: {pkg['current_version']})",
                "",
                f"- **Severity**: {pkg['severity']}",
                f"- **CVE**: {pkg['cve_id'] or 'N/A'}",
                f"- **Description**: {pkg['vulnerability']}",
                f"- **Tool**: {pkg['tool']}",
                f"- **Confidence**: {pkg['confidence']}",
                "",
                f"**Recommended Upgrade**: {pkg['safe_upgrade']['target_version']}",
                f"- Breaking Changes: {pkg['safe_upgrade']['breaking_changes']}",
                f"- Risk Level: {pkg['safe_upgrade']['risk_level']}",
                "",
            ])
    
    return "\n".join(lines)


def main() -> int:
    """Main entry point with CLI interface."""
    parser = argparse.ArgumentParser(
        description="Format dependency vulnerabilities for agent consumption"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # format-deps command
    format_parser = subparsers.add_parser(
        "format-deps",
        help="Format dependency findings"
    )
    format_parser.add_argument(
        "--findings",
        default=str(DEFAULT_FINDINGS_FILE),
        help="Path to comprehensive findings JSON"
    )
    format_parser.add_argument(
        "--output",
        default="dependency-formatted.json",
        help="Output JSON file path"
    )
    format_parser.add_argument(
        "--markdown",
        help="Optional markdown report output path"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Format findings
        formatted = format_dependency_vulnerabilities(args.findings)
        
        if not formatted["vulnerable_packages"]:
            logger.info("No vulnerable packages found")
            return 2
        
        # Write JSON output
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(formatted, f, indent=2)
        logger.info(f"Formatted output written to {output_path}")
        
        # Write markdown report if requested
        if args.markdown:
            markdown_path = Path(args.markdown)
            markdown_path.parent.mkdir(parents=True, exist_ok=True)
            
            report = generate_markdown_report(formatted)
            with open(markdown_path, 'w') as f:
                f.write(report)
            logger.info(f"Markdown report written to {markdown_path}")
        
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
