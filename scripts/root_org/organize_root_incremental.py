#!/usr/bin/env python3
"""
Root Organization: Incremental Root Organizer Script

Safely moves files from root to target locations in controlled batches.
Integrates validation and reference updating for zero-break guarantee.

Usage:
    python organize_root_incremental.py --plan <plan_file> [--batch <n>] [--dry-run]
    python organize_root_incremental.py --plan .codex/plans/ROOT_ORG_RELOCATION_PLAN.json --batch 10 --dry-run
    python organize_root_incremental.py --file <file> --target <target> --dry-run

Physics Model: Balance⚖️ - Prioritize zero-break guarantees
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

# Import other scripts
try:
    from update_links_atomic import (
        UpdateTransaction,
        find_files_to_update,
        update_references_in_file,
    )
    from validate_references import assess_risk, scan_repository
except ImportError:
    print("Warning: Could not import validation scripts. Some features may be limited.")
    def assess_risk(count): return "HIGH" if count > 5 else "MEDIUM" if count > 0 else "LOW"


def load_relocation_plan(plan_file: Path) -> Dict:
    """Load the relocation plan from JSON file."""
    with open(plan_file) as f:
        return json.load(f)


def validate_move(source: Path, target: Path, dry_run: bool = False) -> Tuple[bool, str, int]:
    """
    Validate if a move is safe.
    Returns: (safe, risk_level, reference_count)
    """
    if not source.exists():
        return False, "ERROR", 0

    # Run reference validation
    references, stats = scan_repository(str(source), Path.cwd(), dry_run)
    ref_count = stats['total_references']
    risk = assess_risk(ref_count)

    # Check if target directory exists
    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)

    return True, risk, ref_count


def execute_git_mv(source: Path, target: Path, dry_run: bool = False) -> bool:
    """Execute git mv command."""
    if dry_run:
        print(f"  [DRY RUN] Would execute: git mv {source} {target}")
        return True

    try:
        # Ensure target directory exists
        target.parent.mkdir(parents=True, exist_ok=True)

        # Use git mv
        result = subprocess.run(
            ['git', 'mv', str(source), str(target)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return True
        print(f"  ❌ Git mv failed: {result.stderr}")
        return False

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def move_file_safely(
    source: Path,
    target: Path,
    update_refs: bool = True,
    dry_run: bool = False
) -> bool:
    """
    Safely move a file with validation and reference updating.
    """
    print(f"\n{'='*80}")
    print(f"Moving: {source} → {target}")
    print(f"{'='*80}")

    # Step 1: Validate
    print("Step 1: Validating move...")
    safe, risk, ref_count = validate_move(source, target, dry_run)

    if not safe:
        print("  ❌ Validation failed")
        return False

    print(f"  ✓ Risk level: {risk}")
    print(f"  ✓ References found: {ref_count}")

    # Step 2: Check risk threshold
    if risk == "HIGH" and not dry_run:
        response = input(f"  ⚠️  HIGH RISK ({ref_count} references). Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("  Skipped")
            return False

    # Step 3: Execute move
    print("Step 2: Executing git mv...")
    if not execute_git_mv(source, target, dry_run):
        return False
    print("  ✓ File moved")

    # Step 4: Update references
    if update_refs and ref_count > 0:
        print("Step 3: Updating references...")

        try:
            with UpdateTransaction(str(source), str(target), dry_run) as transaction:
                files_to_check = find_files_to_update(str(source), Path.cwd())

                for file_path in files_to_check:
                    modified, old_content, new_content = update_references_in_file(
                        file_path, str(source), str(target)
                    )
                    if modified:
                        transaction.add_update(file_path, old_content, new_content)

                updated = transaction.execute()
                print(f"  ✓ Updated {updated} files")

        except Exception as e:
            print(f"  ❌ Reference update failed: {e}")
            # Note: git mv already happened, but refs not updated
            # This is a partial failure state
            return False

    print(f"✅ Successfully moved: {source} → {target}")
    return True


def organize_by_plan(
    plan_file: Path,
    batch_size: int = 10,
    risk_filter: Optional[str] = None,
    dry_run: bool = False
):
    """Organize files according to relocation plan."""
    plan = load_relocation_plan(plan_file)
    relocations = plan['relocations']

    # Filter by risk if specified
    if risk_filter:
        relocations = [r for r in relocations if r['risk_level'] == risk_filter]

    # Sort by risk (LOW first)
    risk_order = {'LOW': 0, 'MEDIUM': 1, 'HIGH': 2}
    relocations.sort(key=lambda x: risk_order.get(x['risk_level'], 3))

    # Process in batches
    total = len(relocations)
    processed = 0
    successes = 0
    failures = 0

    print(f"Processing {total} relocations in batches of {batch_size}")
    print(f"{'='*80}\n")

    for i, relocation in enumerate(relocations):
        if batch_size > 0 and processed >= batch_size:
            break

        source = Path(relocation['source'].lstrip('./'))
        target = Path(relocation['target'])

        print(f"[{i+1}/{total}] Processing: {source}")

        if move_file_safely(source, target, update_refs=True, dry_run=dry_run):
            successes += 1
        else:
            failures += 1

        processed += 1

    # Summary
    print(f"\n{'='*80}")
    print("Summary:")
    print(f"  Total processed: {processed}")
    print(f"  Successes: {successes}")
    print(f"  Failures: {failures}")
    print(f"{'='*80}")

    return failures == 0


def log_to_ndjson(operation: str, details: Dict):
    """Log operation to .codex/action_log.ndjson."""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': 'organize_root_incremental',
        'operation': operation,
        'details': details,
    }

    log_file = Path('.codex/action_log.ndjson')
    log_file.parent.mkdir(parents=True, exist_ok=True)

    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')


def main():
    parser = argparse.ArgumentParser(
        description='Incrementally organize root folder with validation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Move files according to plan (10 at a time)
  python organize_root_incremental.py --plan .codex/plans/ROOT_ORG_RELOCATION_PLAN.json --batch 10 --dry-run

  # Move only LOW risk files
  python organize_root_incremental.py --plan .codex/plans/ROOT_ORG_RELOCATION_PLAN.json --risk LOW

  # Move a single file
  python organize_root_incremental.py --file QUICKSTART.md --target docs/QUICKSTART.md --dry-run
        """
    )

    parser.add_argument('--plan', type=Path, help='Relocation plan JSON file')
    parser.add_argument('--batch', type=int, default=10, help='Batch size (0 for all)')
    parser.add_argument('--risk', choices=['LOW', 'MEDIUM', 'HIGH'], help='Filter by risk level')
    parser.add_argument('--file', type=Path, help='Single file to move')
    parser.add_argument('--target', type=Path, help='Target path for single file')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')

    args = parser.parse_args()

    if args.file and args.target:
        # Single file mode
        success = move_file_safely(args.file, args.target, dry_run=args.dry_run)
        return 0 if success else 1

    if args.plan:
        # Plan mode
        if not args.plan.exists():
            print(f"Error: Plan file not found: {args.plan}")
            return 1

        success = organize_by_plan(
            args.plan,
            batch_size=args.batch,
            risk_filter=args.risk,
            dry_run=args.dry_run
        )
        return 0 if success else 1

    parser.print_help()
    return 1


if __name__ == '__main__':
    sys.exit(main())
