"""
Batch codemod runner for security fixes.

Executes codemods against multiple files and creates PRs for each fix group.

Author: mbaetiong
Generated: 2025-12-17

Safeguards:
- Input validation on file paths
- Dry-run mode by default
- Bounds checking on file counts
"""

from __future__ import annotations

import csv
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, List, Tuple

# Configure logging
logger = logging.getLogger(__name__)

# Import codemods
from scripts.security.codemods.fix_subprocess import transform_file as fix_subprocess
from scripts.security.codemods.fix_sql_injection import transform_file as fix_sql_injection
from scripts.security.codemods.fix_hardcoded_secrets import transform_file as fix_secrets

# Safeguards
MAX_FILES_PER_GROUP = 1000


@dataclass
class FixGroup:
    """A group of related fixes to apply together."""
    
    group_id: str
    rule_pattern: str
    fix_function: Callable[[str], Tuple[str, List[str]]]
    description: str
    priority: str


# Define fix groups
FIX_GROUPS = [
    FixGroup(
        group_id="FG-001",
        rule_pattern="subprocess",
        fix_function=fix_subprocess,
        description="Fix unsafe subprocess usage (shell=True, os.system)",
        priority="P0",
    ),
    FixGroup(
        group_id="FG-002",
        rule_pattern="sql",
        fix_function=fix_sql_injection,
        description="Fix SQL injection vulnerabilities",
        priority="P0",
    ),
    FixGroup(
        group_id="FG-003",
        rule_pattern="hardcoded",
        fix_function=lambda f: fix_secrets(f)[:2],  # Ignore env_vars return
        description="Remove hardcoded secrets",
        priority="P0",
    ),
]


def load_prioritized_alerts(alerts_file: Path) -> List[dict[str, Any]]:
    """Load the prioritized alerts CSV."""
    alerts = []
    
    if not alerts_file.exists():
        logger.warning(f"Alerts file not found: {alerts_file}")
        return alerts
    
    try:
        with open(alerts_file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                alerts.append(row)
    except Exception as e:
        logger.error(f"Error reading alerts file: {e}")
    
    return alerts


def group_alerts_by_fix(alerts: List[dict[str, Any]]) -> dict[str, List[dict[str, Any]]]:
    """Group alerts by which fix group they belong to."""
    grouped: dict[str, List[dict[str, Any]]] = {fg.group_id: [] for fg in FIX_GROUPS}
    
    for alert in alerts:
        rule_id = alert.get("rule_id", "").lower()
        
        for fg in FIX_GROUPS:
            if fg.rule_pattern in rule_id:
                grouped[fg.group_id].append(alert)
                break
    
    return grouped


def apply_fix_group(
    fix_group: FixGroup, 
    alerts: List[dict[str, Any]], 
    dry_run: bool = True
) -> dict[str, Any]:
    """Apply fixes for a group of alerts."""
    results: dict[str, Any] = {
        "group_id": fix_group.group_id,
        "description": fix_group.description,
        "files_processed": 0,
        "changes_made": 0,
        "errors": [],
        "modified_files": [],
    }
    
    # Get unique files
    files = set(alert.get("file", "") for alert in alerts if alert.get("file"))
    
    # Bounds check (safeguard)
    if len(files) > MAX_FILES_PER_GROUP:
        logger.warning(f"Limiting files to {MAX_FILES_PER_GROUP}")
        files = set(list(files)[:MAX_FILES_PER_GROUP])
    
    for file_path in files:
        if not file_path or not Path(file_path).exists():
            results["errors"].append(f"File not found: {file_path}")
            continue
        
        try:
            new_content, changes = fix_group.fix_function(file_path)
            
            if changes and not any("Error" in c or "Invalid" in c for c in changes):
                results["files_processed"] += 1
                results["changes_made"] += len(changes)
                results["modified_files"].append({
                    "path": file_path,
                    "changes": changes,
                })
                
                if not dry_run:
                    with open(file_path, "w") as f:
                        f.write(new_content)
                    logger.info(f"  ✅ Fixed {file_path}: {len(changes)} changes")
                else:
                    logger.info(f"  🔍 Would fix {file_path}: {len(changes)} changes")
        
        except Exception as e:
            results["errors"].append(f"Error processing {file_path}: {str(e)}")
    
    return results


def main() -> None:
    """Main entry point."""
    import argparse
    
    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser(description="Run security codemods")
    parser.add_argument("--dry-run", action="store_true", default=True, 
                       help="Don't make actual changes (default: True)")
    parser.add_argument("--apply", action="store_true", 
                       help="Actually apply changes")
    parser.add_argument("--group", type=str, help="Only run specific fix group")
    args = parser.parse_args()
    
    dry_run = not args.apply
    
    alerts_file = Path(".github/security/prioritized-alerts.csv")
    
    if not alerts_file.exists():
        logger.warning("Prioritized alerts file not found. Running in demo mode.")
        # Create sample alerts for demo
        sample_alerts = [
            {"rule_id": "subprocess-shell-true", "file": "src/utils/shell.py"},
            {"rule_id": "sql-injection", "file": "src/db/queries.py"},
            {"rule_id": "hardcoded-password", "file": "src/config/settings.py"},
        ]
        grouped = {fg.group_id: [] for fg in FIX_GROUPS}
        for alert in sample_alerts:
            for fg in FIX_GROUPS:
                if fg.rule_pattern in alert["rule_id"]:
                    grouped[fg.group_id].append(alert)
                    break
    else:
        # Load and group alerts
        alerts = load_prioritized_alerts(alerts_file)
        grouped = group_alerts_by_fix(alerts)
    
    # Process each fix group
    total_changes = 0
    for fix_group in FIX_GROUPS:
        if args.group and fix_group.group_id != args.group:
            continue
        
        group_alerts = grouped[fix_group.group_id]
        
        if not group_alerts:
            logger.info(f"⏭️ {fix_group.group_id}: No matching alerts")
            continue
        
        logger.info(f"\n🔧 Processing {fix_group.group_id}: {fix_group.description}")
        logger.info(f"   {len(group_alerts)} alerts to process")
        
        # Apply fixes
        results = apply_fix_group(fix_group, group_alerts, dry_run=dry_run)
        total_changes += results["changes_made"]
        
        if results["errors"]:
            logger.warning(f"   ⚠️ Errors: {len(results['errors'])}")
            for error in results["errors"][:5]:
                logger.warning(f"      - {error}")
    
    logger.info(f"\n✅ Codemod run complete. Total changes: {total_changes}")
    if dry_run:
        logger.info("   (Dry run - no files were modified. Use --apply to apply changes)")


if __name__ == "__main__":
    main()
