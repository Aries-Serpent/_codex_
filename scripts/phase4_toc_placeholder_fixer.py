#!/usr/bin/env python3
"""
Phase 4: Empty TOC Placeholders - Processor
Fixes empty TOC links by either creating anchor targets or removing entries.
"""

import json
import re
from pathlib import Path
from typing import List, Tuple

# Repository root
REPO_ROOT = Path(__file__).parent.parent

def load_audit_data() -> dict:
    """Load comprehensive link audit data."""
    audit_file = REPO_ROOT / "COMPREHENSIVE_LINK_AUDIT.json"
    with open(audit_file) as f:
        return json.load(f)

def find_empty_toc_links(content: str) -> List[Tuple[str, str]]:
    """Find empty TOC links like [Text]()."""
    # Pattern: [text]() - link with empty URL
    pattern = r'\[([^\]]+)\]\(\)'
    matches = re.finditer(pattern, content)
    return [(m.group(0), m.group(1)) for m in matches]

def create_anchor_from_text(text: str) -> str:
    """Create a markdown anchor from text."""
    # Convert to lowercase, replace spaces with hyphens, remove special chars
    anchor = text.lower()
    anchor = re.sub(r'[^\w\s-]', '', anchor)
    anchor = re.sub(r'[\s_]+', '-', anchor)
    anchor = anchor.strip('-')
    return f'#{anchor}'

def check_if_section_exists(content: str, text: str) -> str:
    """Check if a section with matching header exists."""
    # Look for header that matches the TOC text
    lines = content.split('\n')
    for line in lines:
        if line.startswith('#'):
            # Remove # symbols and clean up
            header_text = line.lstrip('#').strip()
            if header_text.lower() == text.lower():
                return create_anchor_from_text(header_text)
    return None

def fix_empty_toc_placeholder(file_path: Path) -> Tuple[int, List[dict]]:
    """
    Fix empty TOC placeholders in a file.
    Returns (fixes_applied, fix_details).
    """
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return 0, []

    original_content = content
    fixes = []

    # Find all empty TOC links
    empty_links = find_empty_toc_links(content)

    if not empty_links:
        return 0, []

    for full_match, link_text in empty_links:
        # Check if corresponding section exists
        existing_anchor = check_if_section_exists(content, link_text)

        if existing_anchor:
            # Section exists - add anchor
            new_link = f'[{link_text}]({existing_anchor})'
            content = content.replace(full_match, new_link, 1)
            fixes.append({
                'text': link_text,
                'action': 'added_anchor',
                'anchor': existing_anchor
            })
        else:
            # Section doesn't exist - comment it out for manual review
            commented = f'<!-- TODO: Add section or remove TOC entry - {full_match} -->'
            content = content.replace(full_match, commented, 1)
            fixes.append({
                'text': link_text,
                'action': 'commented',
                'reason': 'no_matching_section'
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
    print("🔧 Phase 4: Empty TOC Placeholders")
    print("=" * 80)
    print()

    print("📂 Scanning for files with empty TOC links...")

    # Find all markdown files
    md_files = list(REPO_ROOT.rglob('*.md'))
    md_files = [f for f in md_files if '.git' not in str(f) and 'node_modules' not in str(f)]

    stats = {
        'files_scanned': 0,
        'files_with_empty_toc': 0,
        'files_modified': 0,
        'anchors_added': 0,
        'entries_commented': 0
    }

    fixes_log = []

    print(f"   Found {len(md_files)} markdown files")
    print()
    print("🔧 Processing files with empty TOC placeholders...")
    print()

    for md_file in md_files:
        stats['files_scanned'] += 1

        fixes_count, fix_details = fix_empty_toc_placeholder(md_file)

        if fixes_count > 0:
            stats['files_with_empty_toc'] += 1
            stats['files_modified'] += 1

            rel_path = md_file.relative_to(REPO_ROOT)

            for fix in fix_details:
                if fix['action'] == 'added_anchor':
                    stats['anchors_added'] += 1
                elif fix['action'] == 'commented':
                    stats['entries_commented'] += 1

            fixes_log.append({
                'file': str(rel_path),
                'fixes_count': fixes_count,
                'details': fix_details
            })

            print(f"📄 {rel_path}")
            print(f"   ✅ Fixed {fixes_count} empty TOC placeholder(s)")

            for fix in fix_details:
                if fix['action'] == 'added_anchor':
                    print(f"      - Added anchor: [{fix['text']}]({fix['anchor']})")
                elif fix['action'] == 'commented':
                    print(f"      - Commented: [{fix['text']}]() (no section found)")

    print()
    print("=" * 80)
    print("📊 Phase 4 Summary")
    print("=" * 80)
    print(f"Files scanned: {stats['files_scanned']}")
    print(f"Files with empty TOC: {stats['files_with_empty_toc']}")
    print(f"Files modified: {stats['files_modified']}")
    print(f"Anchors added: {stats['anchors_added']}")
    print(f"Entries commented (for review): {stats['entries_commented']}")
    print()

    # Save log
    log_file = REPO_ROOT / "PHASE_4_TOC_FIXES.json"
    with open(log_file, 'w') as f:
        json.dump({
            'stats': stats,
            'fixes': fixes_log
        }, f, indent=2)

    print(f"📄 Fixes log saved to: {log_file.name}")
    print()
    print("✅ Phase 4 Complete!")
    print()

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
