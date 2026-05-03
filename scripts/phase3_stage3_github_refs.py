#!/usr/bin/env python3
"""
Phase 3 Stage 3: GitHub References - Processor
Fixes or removes broken GitHub URLs to deleted files.
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

def get_github_references(cat_data: dict) -> list[dict]:
    """Get list of broken GitHub references."""
    detailed = cat_data['analysis']['detailed']
    return detailed.get('github_reference', [])

def fix_github_reference(file_path: Path, link_url: str, link_text: str) -> tuple[bool, str]:
    """
    Fix a broken GitHub reference.
    Returns (success, action_taken).
    """
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return False, 'read_error'

    original_content = content

    # Pattern to find the link
    pattern = re.escape(link_url)

    # Strategy: Remove broken GitHub URLs since they're external refs to deleted files
    # Replace [text](url) with just text
    content = re.sub(f'\\[([^\\]]+)\\]\\({pattern}\\)', r'\1', content)

    # If link is in a list item, remove the entire item
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        if link_url in line and (line.strip().startswith('-') or line.strip().startswith('*')):
            # Skip this list item
            continue
        new_lines.append(line)

    content = '\n'.join(new_lines)

    # Write back if changed
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, 'removed'
        except Exception:
            return False, 'write_error'

    return False, 'no_change'

def main():
    """Main execution."""
    print("=" * 80)
    print("🔧 Phase 3 Stage 3: GitHub References")
    print("=" * 80)
    print()

    # Load data
    print("📂 Loading categorization data...")
    cat_data = load_categorization()

    # Get GitHub references
    github_refs = get_github_references(cat_data)
    print(f"   Found {len(github_refs)} broken GitHub references")
    print()

    if not github_refs:
        print("✅ No GitHub references to fix!")
        return 0

    # Group by file
    refs_by_file = {}
    for ref in github_refs:
        file_path = ref['file']
        if file_path not in refs_by_file:
            refs_by_file[file_path] = []
        refs_by_file[file_path].append(ref)

    print(f"📊 References span {len(refs_by_file)} files")
    print()

    # Process files
    stats = {
        'files_processed': 0,
        'files_modified': 0,
        'refs_removed': 0,
        'refs_failed': 0
    }

    fixes_log = []

    print("🔧 Processing files with broken GitHub references...")
    print()

    for file_rel_path, refs in refs_by_file.items():
        file_path = REPO_ROOT / file_rel_path
        if not file_path.exists():
            continue

        stats['files_processed'] += 1
        print(f"📄 {file_rel_path}")

        file_modified = False
        for ref_data in refs:
            link_url = ref_data['url']
            link_text = ref_data.get('text', '')

            success, action = fix_github_reference(file_path, link_url, link_text)

            if success:
                file_modified = True
                stats['refs_removed'] += 1
                fixes_log.append({
                    'file': file_rel_path,
                    'url': link_url,
                    'action': action
                })
                print(f"   ✅ Removed: {link_url[:60]}...")
            else:
                stats['refs_failed'] += 1
                print(f"   ⏭️  Skipped: {link_url[:60]}...")

        if file_modified:
            stats['files_modified'] += 1

        print()

    print("=" * 80)
    print("📊 Stage 3 Summary")
    print("=" * 80)
    print(f"Files processed: {stats['files_processed']}")
    print(f"Files modified: {stats['files_modified']}")
    print(f"GitHub refs removed: {stats['refs_removed']}")
    print(f"Refs failed/skipped: {stats['refs_failed']}")
    print()

    # Save log
    log_file = REPO_ROOT / "PHASE_3_STAGE3_FIXES.json"
    with open(log_file, 'w') as f:
        json.dump({
            'stats': stats,
            'fixes': fixes_log
        }, f, indent=2)

    print(f"📄 Fixes log saved to: {log_file.name}")
    print()
    print("✅ Stage 3 Complete!")
    print()

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
