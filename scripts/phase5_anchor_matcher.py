#!/usr/bin/env python3
"""
Phase 5: Complex Anchor Mismatches - Processor
Fixes anchor links that don't match actual section headers.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Repository root
REPO_ROOT = Path(__file__).parent.parent

def extract_headers(content: str) -> Dict[str, str]:
    """Extract all headers and their anchors from content."""
    headers = {}
    lines = content.split('\n')

    for line in lines:
        if line.startswith('#'):
            # Extract header text
            header_text = line.lstrip('#').strip()
            # Create anchor
            anchor = header_text.lower()
            anchor = re.sub(r'[^\w\s-]', '', anchor)
            anchor = re.sub(r'[\s_]+', '-', anchor)
            anchor = anchor.strip('-')
            headers[f'#{anchor}'] = header_text

    return headers

def find_anchor_links(content: str) -> List[Tuple[str, str, str]]:
    """Find all anchor links in content. Returns (full_match, text, anchor)."""
    pattern = r'\[([^\]]+)\]\((#[^\)]+)\)'
    matches = re.finditer(pattern, content)
    return [(m.group(0), m.group(1), m.group(2)) for m in matches]

def find_best_match(anchor: str, available_anchors: List[str]) -> Optional[str]:
    """Find the best matching anchor from available options."""
    # Remove # for comparison
    anchor_clean = anchor.lstrip('#').lower()

    # Exact match
    for avail in available_anchors:
        if avail.lower() == anchor.lower():
            return avail

    # Partial match (contains)
    for avail in available_anchors:
        if anchor_clean in avail.lower().lstrip('#'):
            return avail

    # Reverse partial match
    for avail in available_anchors:
        if avail.lower().lstrip('#') in anchor_clean:
            return avail

    return None

def fix_anchor_mismatches(file_path: Path) -> Tuple[int, List[dict]]:
    """
    Fix anchor mismatches in a file.
    Returns (fixes_applied, fix_details).
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return 0, []

    original_content = content
    fixes = []

    # Extract available headers
    available_headers = extract_headers(content)
    available_anchors = list(available_headers.keys())

    if not available_anchors:
        return 0, []

    # Find all anchor links
    anchor_links = find_anchor_links(content)

    for full_match, link_text, anchor in anchor_links:
        # Check if anchor exists
        if anchor not in available_headers:
            # Try to find best match
            best_match = find_best_match(anchor, available_anchors)

            if best_match:
                # Replace with best match
                new_link = f'[{link_text}]({best_match})'
                content = content.replace(full_match, new_link, 1)
                fixes.append({
                    'text': link_text,
                    'old_anchor': anchor,
                    'new_anchor': best_match,
                    'action': 'corrected'
                })
            else:
                # No good match - comment for manual review
                commented = f'<!-- BROKEN ANCHOR: {full_match} -->'
                content = content.replace(full_match, commented, 1)
                fixes.append({
                    'text': link_text,
                    'old_anchor': anchor,
                    'action': 'commented',
                    'reason': 'no_match_found'
                })

    # Write back if changed
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return len(fixes), fixes
        except Exception:
            return 0, []

    return 0, []

def main():
    """Main execution."""
    print("=" * 80)
    print("🔧 Phase 5: Complex Anchor Mismatches")
    print("=" * 80)
    print()

    print("📂 Scanning for files with anchor links...")

    # Find all markdown files
    md_files = list(REPO_ROOT.rglob('*.md'))
    md_files = [f for f in md_files if '.git' not in str(f) and 'node_modules' not in str(f)]

    stats = {
        'files_scanned': 0,
        'files_with_issues': 0,
        'files_modified': 0,
        'anchors_corrected': 0,
        'anchors_commented': 0
    }

    fixes_log = []

    print(f"   Found {len(md_files)} markdown files")
    print()
    print("🔧 Processing files with anchor mismatches...")
    print()

    for md_file in md_files:
        stats['files_scanned'] += 1

        fixes_count, fix_details = fix_anchor_mismatches(md_file)

        if fixes_count > 0:
            stats['files_with_issues'] += 1
            stats['files_modified'] += 1

            rel_path = md_file.relative_to(REPO_ROOT)

            for fix in fix_details:
                if fix['action'] == 'corrected':
                    stats['anchors_corrected'] += 1
                elif fix['action'] == 'commented':
                    stats['anchors_commented'] += 1

            fixes_log.append({
                'file': str(rel_path),
                'fixes_count': fixes_count,
                'details': fix_details
            })

            print(f"📄 {rel_path}")
            print(f"   ✅ Fixed {fixes_count} anchor mismatch(es)")

            for fix in fix_details:
                if fix['action'] == 'corrected':
                    print(f"      - Corrected: {fix['old_anchor']} → {fix['new_anchor']}")
                elif fix['action'] == 'commented':
                    print(f"      - Commented: {fix['old_anchor']} (no match)")

    print()
    print("=" * 80)
    print("📊 Phase 5 Summary")
    print("=" * 80)
    print(f"Files scanned: {stats['files_scanned']}")
    print(f"Files with anchor issues: {stats['files_with_issues']}")
    print(f"Files modified: {stats['files_modified']}")
    print(f"Anchors corrected: {stats['anchors_corrected']}")
    print(f"Anchors commented (for review): {stats['anchors_commented']}")
    print()

    # Save log
    log_file = REPO_ROOT / "PHASE_5_ANCHOR_FIXES.json"
    with open(log_file, 'w') as f:
        json.dump({
            'stats': stats,
            'fixes': fixes_log
        }, f, indent=2)

    print(f"📄 Fixes log saved to: {log_file.name}")
    print()
    print("✅ Phase 5 Complete!")
    print()

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
