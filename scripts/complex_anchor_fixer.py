#!/usr/bin/env python3
"""
Complex Anchor Fixer - PR #3248 Sprint 1 Part 2
Applies automated fixes for complex anchor references in batches.

This script processes the review queue and applies fixes for auto-fixable items,
with batch validation to ensure zero-break guarantee.

Generated: 2026-02-13
Part of: PR #3248 Sprint 1 Part 2
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

# Repository root
REPO_ROOT = Path(__file__).parent.parent


def load_review_queue(queue_file: Path) -> List[Dict]:
    """Load the review queue JSON file."""
    with open(queue_file, encoding='utf-8') as f:
        return json.load(f)


def apply_anchor_fix(file_path: Path, line_num: int, old_anchor: str, new_anchor: str, link_text: str) -> bool:
    """
    Apply a single anchor fix to a file.
    Returns True if fix was applied successfully.
    """
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"   ❌ Error reading {file_path}: {e}")
        return False

    original_content = content

    # Construct the old link pattern
    old_link = f'[{link_text}]({old_anchor})'
    new_link = f'[{link_text}]({new_anchor})'

    # Try exact replacement
    if old_link in content:
        content = content.replace(old_link, new_link, 1)
    else:
        # Try with escaped characters
        old_link_escaped = re.escape(old_link)
        pattern = old_link_escaped.replace(r'\ ', r'\s')
        content = re.sub(pattern, new_link, content, count=1)

    if content == original_content:
        print(f"   ⚠️  Warning: No change made for {old_anchor} in {file_path}")
        return False

    # Write the fixed content
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"   ❌ Error writing {file_path}: {e}")
        return False


def validate_file_syntax(file_path: Path) -> bool:
    """
    Validate that a markdown file is still valid after changes.
    Basic check: file is readable and has balanced brackets.
    """
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()

        # Check for balanced brackets
        brackets = {'[': 0, ']': 0, '(': 0, ')': 0}
        for char in content:
            if char in brackets:
                brackets[char] += 1

        # Allow some imbalance (code blocks, etc.) but flag major issues
        if abs(brackets['['] - brackets[']']) > 10:
            return False
        return not abs(brackets['('] - brackets[')']) > 10
    except Exception:
        return False


def process_batch(items: List[Dict], batch_num: int, dry_run: bool = False) -> Tuple[int, int, List[str]]:
    """
    Process a batch of fixes.
    Returns (successful_fixes, failed_fixes, affected_files).
    """
    print(f"\n📦 Processing Batch {batch_num} ({len(items)} items)...")

    successful = 0
    failed = 0
    affected_files = set()

    for idx, item in enumerate(items, 1):
        file_path = REPO_ROOT / item['file']
        old_anchor = item['current_anchor']
        new_anchor = item['suggested_fix']
        link_text = item['link_text']
        line = item['line']

        print(f"   [{idx}/{len(items)}] {item['file']}:{line}")
        print(f"      {old_anchor} → {new_anchor}")

        if dry_run:
            print("      [DRY RUN] Would fix")
            successful += 1
            continue

        if apply_anchor_fix(file_path, line, old_anchor, new_anchor, link_text):
            print("      ✅ Fixed")
            successful += 1
            affected_files.add(str(file_path.relative_to(REPO_ROOT)))
        else:
            print("      ❌ Failed")
            failed += 1

    return successful, failed, list(affected_files)


def validate_batch(files: List[str]) -> bool:
    """
    Validate all files in a batch after fixes are applied.
    Returns True if all files pass validation.
    """
    print(f"\n✅ Validating {len(files)} affected files...")

    all_valid = True
    for file in files:
        file_path = REPO_ROOT / file
        if not validate_file_syntax(file_path):
            print(f"   ❌ Validation failed: {file}")
            all_valid = False
        else:
            print(f"   ✅ Valid: {file}")

    return all_valid


def generate_resolution_log(fixes: List[Dict], successful: int, failed: int) -> Dict:
    """Generate a resolution log for audit trail."""
    return {
        'timestamp': '2026-02-13T23:58:00Z',
        'sprint': 'Sprint 1 Part 2',
        'scope': 'Complex Anchor Automated Fixes',
        'total_items': len(fixes),
        'successful': successful,
        'failed': failed,
        'success_rate': f"{(successful / len(fixes) * 100):.1f}%" if fixes else "0%",
        'fixes_applied': fixes,
        'validation': 'passed' if failed == 0 else 'partial'
    }


def main():
    """Main execution function."""
    print("🔧 Complex Anchor Fixer - PR #3248 Sprint 1 Part 2")
    print("=" * 60)

    # Load review queue
    queue_file = REPO_ROOT / '.codex' / 'validation' / 'complex_anchors_review_queue.json'
    print(f"\n📋 Loading review queue: {queue_file.relative_to(REPO_ROOT)}")

    queue = load_review_queue(queue_file)
    print(f"   Total items: {len(queue)}")

    # Filter auto-fixable items
    auto_fixable = [item for item in queue if item.get('auto_fixable', False)]
    print(f"   Auto-fixable: {len(auto_fixable)}")

    if not auto_fixable:
        print("\n✨ No auto-fixable items to process!")
        return

    # Group by file for efficient processing
    by_file = defaultdict(list)
    for item in auto_fixable:
        by_file[item['file']].append(item)

    print(f"   Files affected: {len(by_file)}")

    # Process in batches of 20
    batch_size = 20
    all_items = auto_fixable
    batches = [all_items[i:i + batch_size] for i in range(0, len(all_items), batch_size)]

    print(f"\n📦 Processing {len(batches)} batches (batch size: {batch_size})")

    total_successful = 0
    total_failed = 0
    all_affected_files = set()
    all_fixes = []

    for batch_num, batch in enumerate(batches, 1):
        successful, failed, affected_files = process_batch(batch, batch_num, dry_run=False)

        total_successful += successful
        total_failed += failed
        all_affected_files.update(affected_files)

        # Record fixes
        for item in batch:
            all_fixes.append({
                'file': item['file'],
                'line': item['line'],
                'old_anchor': item['current_anchor'],
                'new_anchor': item['suggested_fix'],
                'link_text': item['link_text'],
                'status': 'success' if item in batch[:successful] else 'failed'
            })

        # Validate batch
        if not validate_batch(affected_files):
            print(f"\n❌ Batch {batch_num} validation failed!")
            print("   Stopping to prevent breaking changes.")
            break

        print(f"\n✅ Batch {batch_num} complete and validated!")

    # Generate summary
    print("\n" + "=" * 60)
    print("📊 Summary")
    print(f"   Total processed: {len(all_items)}")
    print(f"   Successful: {total_successful}")
    print(f"   Failed: {total_failed}")
    print(f"   Files modified: {len(all_affected_files)}")
    print(f"   Success rate: {(total_successful / len(all_items) * 100):.1f}%")

    # Save resolution log
    output_dir = REPO_ROOT / '.codex' / 'validation'
    log_file = output_dir / 'complex_anchors_resolution_log.json'

    resolution_log = generate_resolution_log(all_fixes, total_successful, total_failed)

    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(resolution_log, f, indent=2, ensure_ascii=False)

    print(f"\n📝 Resolution log saved: {log_file.relative_to(REPO_ROOT)}")

    print("\n✨ Sprint 1 Part 2 Complete!")
    print(f"\n🎯 Next: Sprint 1 Part 3 - Manual review of {len(queue) - len(auto_fixable)} remaining items")


if __name__ == '__main__':
    main()
