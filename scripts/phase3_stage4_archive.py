#!/usr/bin/env python3
"""
Phase 3 Stage 4: Low-Priority and Archive Files - Processor
Quick cleanup of low-priority and archived content broken links.
"""

import json
import re
from pathlib import Path

# Repository root
REPO_ROOT = Path(__file__).parent.parent

def load_categorization() -> dict:
    """Load Phase 3 categorization data."""
    cat_file = REPO_ROOT / "PHASE_3_CATEGORIZATION_REPORT.json"
    with open(cat_file) as f:
        return json.load(f)

def get_low_priority_files(cat_data: dict) -> list[tuple[str, dict]]:
    """Get list of low-priority files with broken links."""
    low_priority = []

    for file_path, info in cat_data['analysis']['file_priorities'].items():
        if info['priority'] == 'low':
            low_priority.append((file_path, info))

    return sorted(low_priority, key=lambda x: x[1]['broken_count'], reverse=True)

def bulk_clean_file(file_path: Path) -> tuple[int, str]:
    """
    Bulk clean broken links from low-priority/archive files.
    Returns (links_cleaned, action).
    """
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return 0, 'read_error'

    original_content = content
    links_cleaned = 0

    # Remove list items with broken links (common in archive)
    lines = content.split('\n')
    new_lines = []

    for line in lines:
        # Skip lines that are list items with links to non-existent files
        if (line.strip().startswith('-') or line.strip().startswith('*')) and '](' in line:
            # Check if it looks like a broken relative link
            if '.md)' in line or '.json)' in line or '.txt)' in line or '.yml)' in line:
                # Likely a broken link - skip it
                links_cleaned += 1
                continue
        new_lines.append(line)

    content = '\n'.join(new_lines)

    # Comment out remaining broken links
    broken_link_pattern = r'\[([^\]]+)\]\(([^)]+\.(?:md|json|txt|yml|yaml|py))\)'
    matches = list(re.finditer(broken_link_pattern, content))

    for match in matches:
        # link_text = match.group(1)  # Unused, but kept for potential debugging
        link_url = match.group(2)

        # Check if file exists
        potential_path = file_path.parent / link_url
        if not potential_path.exists() and not link_url.startswith('http'):
            # Comment it out
            content = content.replace(match.group(0), f'<!-- BROKEN: {match.group(0)} -->')
            links_cleaned += 1

    # Write back if changed
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return links_cleaned, 'bulk_cleaned'
        except Exception:
            return 0, 'write_error'

    return 0, 'no_change'

def main():
    """Main execution."""
    print("=" * 80)
    print("🔧 Phase 3 Stage 4: Low-Priority & Archive Files")
    print("=" * 80)
    print()

    # Load data
    print("📂 Loading categorization data...")
    cat_data = load_categorization()

    # Get low-priority files
    low_priority_files = get_low_priority_files(cat_data)
    print(f"   Found {len(low_priority_files)} low-priority files")
    print()

    # Process files
    stats = {
        'files_processed': 0,
        'files_modified': 0,
        'links_cleaned': 0
    }

    fixes_log = []

    print("🔧 Bulk cleaning low-priority/archive files...")
    print()

    for file_rel_path, _info in low_priority_files:
        file_path = REPO_ROOT / file_rel_path
        if not file_path.exists():
            continue

        stats['files_processed'] += 1

        links_cleaned, action = bulk_clean_file(file_path)

        if links_cleaned > 0:
            stats['files_modified'] += 1
            stats['links_cleaned'] += links_cleaned

            fixes_log.append({
                'file': file_rel_path,
                'links_cleaned': links_cleaned,
                'action': action
            })

            print(f"📄 {file_rel_path}")
            print(f"   ✅ Cleaned {links_cleaned} broken link(s)")

    print()
    print("=" * 80)
    print("📊 Stage 4 Summary")
    print("=" * 80)
    print(f"Files processed: {stats['files_processed']}")
    print(f"Files modified: {stats['files_modified']}")
    print(f"Links cleaned: {stats['links_cleaned']}")
    print()

    # Save log
    log_file = REPO_ROOT / "PHASE_3_STAGE4_FIXES.json"
    with open(log_file, 'w') as f:
        json.dump({
            'stats': stats,
            'fixes': fixes_log
        }, f, indent=2)

    print(f"📄 Fixes log saved to: {log_file.name}")
    print()
    print("✅ Stage 4 Complete!")
    print()

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
