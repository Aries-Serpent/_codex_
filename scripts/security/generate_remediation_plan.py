"""
Generate Semgrep Remediation Plan.

Creates a prioritized, batched remediation plan from scored alerts.

Author: Copilot Agent
Generated: 2025-12-24

Safeguards:
- Input validation on file paths
- Bounds checking on batch sizes
- Defensive error handling
"""

from __future__ import annotations

import csv
import logging
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Configure logging
logger = logging.getLogger(__name__)

# Safeguards: Bounds
MAX_BATCH_SIZE = 250
MIN_BATCH_SIZE = 10
DEFAULT_BATCH_SIZE = 200


def load_scored_alerts(csv_path: Path) -> list[dict[str, Any]]:
    """Load scored alerts from CSV file."""
    if not csv_path.exists():
        logger.error("Scored alerts file not found: %s", csv_path)
        return []

    alerts = []
    try:
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                alerts.append(row)
    except Exception as e:
        logger.error("Error loading alerts: %s", e)
        return []

    logger.info("Loaded %d scored alerts", len(alerts))
    return alerts


def group_by_pattern(alerts: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group alerts by fix pattern for batch processing."""
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)

    pattern_keywords = {
        "sql_injection": ["sql-injection", "sqli"],
        "command_injection": ["subprocess", "command-injection", "shell-true"],
        "xss": ["xss", "html-injection", "reflected"],
        "secrets": ["hardcoded", "secret", "password", "credential", "api-key"],
        "path_traversal": ["path-traversal", "directory-traversal"],
        "deserialization": ["deserialization", "pickle", "yaml-load"],
        "cryptography": ["crypto", "weak-hash", "md5", "sha1"],
        "logging": ["log-injection", "sensitive-log"],
    }

    for alert in alerts:
        rule_id = alert.get("rule_id", "").lower()
        assigned = False

        for pattern, keywords in pattern_keywords.items():
            if any(kw in rule_id for kw in keywords):
                groups[pattern].append(alert)
                assigned = True
                break

        if not assigned:
            groups["other"].append(alert)

    return groups


def generate_batches(
    alerts: list[dict[str, Any]], batch_size: int = DEFAULT_BATCH_SIZE
) -> list[list[dict[str, Any]]]:
    """Generate batches for iterative fixing."""
    # Bounds check (safeguard)
    batch_size = max(MIN_BATCH_SIZE, min(MAX_BATCH_SIZE, batch_size))
    return [alerts[i : i + batch_size] for i in range(0, len(alerts), batch_size)]


def generate_markdown_plan(
    alerts: list[dict[str, Any]],
    groups: dict[str, list[dict[str, Any]]],
) -> str:
    """Generate markdown remediation plan."""
    timestamp = datetime.now(timezone.utc).isoformat()

    # Count by priority
    priority_counts: dict[str, int] = defaultdict(int)
    for alert in alerts:
        priority_counts[alert.get("priority_bucket", "P3")] += 1

    plan = f"""# Semgrep Remediation Plan

> Generated: {timestamp}
> Total Alerts: {len(alerts)}

## Executive Summary

| Priority | Count | Target |
|----------|-------|--------|
| P0 (Critical) | {priority_counts.get('P0', 0)} | Immediate |
| P1 (High) | {priority_counts.get('P1', 0)} | This Sprint |
| P2 (Medium) | {priority_counts.get('P2', 0)} | Backlog |
| P3 (Low) | {priority_counts.get('P3', 0)} | Defer |

## Remediation Strategy

1. **Automated Codemods**: Apply existing codemods from `scripts/security/codemods/`
2. **Manual Review**: Address complex patterns requiring human judgment
3. **Suppress False Positives**: Document and suppress confirmed false positives
4. **Enable Baseline**: After remediation, enable baseline mode

## Pattern-Based Batches

"""

    for pattern, group_alerts in sorted(groups.items(), key=lambda x: len(x[1]), reverse=True):
        batches = generate_batches(group_alerts)
        p0_count = sum(1 for a in group_alerts if a.get("priority_bucket") == "P0")
        p1_count = sum(1 for a in group_alerts if a.get("priority_bucket") == "P1")

        plan += f"""### Pattern: `{pattern}` ({len(group_alerts)} alerts)

**Priority Breakdown**: P0={p0_count}, P1={p1_count}
**Batches**: {len(batches)}

| Batch | Alerts | P0 | P1 | Status |
|-------|--------|----|----|--------|
"""
        for i, batch in enumerate(batches, 1):
            bp0 = sum(1 for a in batch if a.get("priority_bucket") == "P0")
            bp1 = sum(1 for a in batch if a.get("priority_bucket") == "P1")
            plan += f"| {i} | {len(batch)} | {bp0} | {bp1} | ⏳ Pending |\n"

        plan += "\n"

    plan += """## Available Codemods

The following automated fixes are available in `scripts/security/codemods/`:

| Codemod | Pattern | Description |
|---------|---------|-------------|
| `fix_sql_injection.py` | SQL Injection | Converts to parameterized queries |
| `fix_subprocess.py` | Command Injection | Removes shell=True |
| `fix_subprocess_libcst.py` | Command Injection | LibCST-based AST transform |
| `fix_hardcoded_secrets.py` | Secrets | Moves to environment variables |

## Execution Commands

```bash
# Run all codemods
python scripts/security/run_codemods.py

# Run specific codemod
python scripts/security/codemods/fix_sql_injection.py

# Validate fixes
python scripts/security/validate_security.py
```

## Post-Remediation

After all alerts are resolved:

1. Update `semgrep/semgrep.yml` with baseline configuration
2. Document any remaining suppressions in `.security-exceptions.md`
3. Enable baseline mode to catch only new alerts

---

*This plan is auto-generated. Update by re-running `generate_remediation_plan.py`*
"""

    return plan


def main() -> None:
    """Main entry point."""
    logging.basicConfig(level=logging.INFO)

    base_dir = Path(".github/security")
    output_dir = Path(".github/security-reports/semgrep")

    # Load scored alerts
    scored_file = base_dir / "prioritized-alerts.csv"
    alerts = load_scored_alerts(scored_file)

    if not alerts:
        # Generate from export if scored file doesn't exist
        logger.warning("No scored alerts found. Run score_alerts.py first.")
        logger.info("Generating sample plan for demonstration...")

        # Create sample alerts for demonstration
        alerts = [
            {
                "alert_id": "1",
                "rule_id": "python.lang.security.audit.subprocess-shell-true",
                "severity": "high",
                "file": "src/utils/shell.py",
                "priority_bucket": "P0",
            },
            {
                "alert_id": "2",
                "rule_id": "python.lang.security.audit.hardcoded-password",
                "severity": "critical",
                "file": "src/config/settings.py",
                "priority_bucket": "P0",
            },
        ]

    # Group by pattern
    groups = group_by_pattern(alerts)

    # Generate plan
    plan = generate_markdown_plan(alerts, groups)

    # Save plan
    output_dir.mkdir(parents=True, exist_ok=True)
    plan_file = output_dir / "remediation-plan.md"
    plan_file.write_text(plan)

    logger.info("✅ Remediation plan saved to %s", plan_file)

    # Print summary
    logger.info("\n📊 Pattern Distribution:")
    for pattern, group_alerts in sorted(groups.items(), key=lambda x: len(x[1]), reverse=True):
        logger.info("  %s: %d alerts", pattern, len(group_alerts))


if __name__ == "__main__":
    main()
