#!/usr/bin/env python3
"""
Phase 3 Stage 2: Medium-Priority Deleted Files - Processor
Removes or updates references to deleted files in medium-priority documentation.
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

def get_medium_priority_files(cat_data: dict) -> list[tuple[str, dict]]:
    """Get list of medium-priority files with broken links."""
    medium_priority = []

    for file_path, info in cat_data['analysis']['file_priorities'].items():
        if info['priority'] == 'medium':
            medium_priority.append((file_path, info))

    return sorted(medium_priority, key=lambda x: x[1]['broken_count'], reverse=True)

def analyze_link_context(file_path: Path, link_url: str) -> dict:
    """Analyze context around a broken link to determine best action."""
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {'action': 'skip', 'reason': f'Cannot read file: {e}'}

    # Find the link in context
    pattern = re.escape(link_url)
    matches = list(re.finditer(f'\\[([^\\]]+)\\]\\({pattern}\\)', content))

    if not matches:
        return {'action': 'skip', 'reason': 'Link not found in file'}

    # Analyze link text and surrounding context
    for match in matches:
        link_text = match.group(1)
        start = max(0, match.start() - 200)
        end = min(len(content), match.end() + 200)
        context = content[start:end]

        # Decision rules
        if any(word in link_text.lower() for word in ['deprecated', 'old', 'legacy', 'archive']):
            return {'action': 'remove', 'reason': 'Link text indicates obsolete content'}

        if 'TODO' in context or 'FIXME' in context:
            return {'action': 'remove', 'reason': 'Part of TODO/FIXME section'}

        # Check if it's in a list of links
        lines_before = content[start:match.start()].split('\n')[-3:]
        if any(line.strip().startswith('-') or line.strip().startswith('*') for line in lines_before):
            return {'action': 'remove_item', 'reason': 'List item with broken link'}

        # Default: comment out for medium priority
        return {'action': 'comment', 'reason': 'Medium priority - comment for review'}

    return {'action': 'skip', 'reason': 'No matches found'}

def fix_deleted_file_reference(file_path: Path, link_url: str, action: str) -> bool:
    """Apply fix to a file based on determined action."""
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return False

    original_content = content
    pattern = re.escape(link_url)

    if action == 'remove':
        # Remove the entire link, keep just the text
        content = re.sub(f'\\[([^\\]]+)\\]\\({pattern}\\)', r'\1', content)

    elif action == 'remove_item':
        # Remove the entire list item containing the link
        lines = content.split('\n')
        new_lines = []

        for line in lines:
            if f']({link_url})' in line and (line.strip().startswith('-') or line.strip().startswith('*')):
                # Skip this list item
                continue
            new_lines.append(line)

        content = '\n'.join(new_lines)

    elif action == 'comment':
        # Comment out the link
        content = re.sub(
            f'(\\[([^\\]]+)\\]\\({pattern}\\))',
            r'<!-- BROKEN LINK: \1 -->',
            content
        )

    # Write back if changed
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception:
            return False

    return False

def main():
    """Main execution."""
    print("=" * 80)
    print("🔧 Phase 3 Stage 2: Medium-Priority Deleted Files")
    print("=" * 80)
    print()

    # Load data
    print("📂 Loading categorization data...")
    cat_data = load_categorization()

    # Get medium-priority files
    medium_priority_files = get_medium_priority_files(cat_data)
    print(f"   Found {len(medium_priority_files)} medium-priority files")
    print()

    # Get detailed broken links
    detailed_links = cat_data['analysis']['detailed']

    # Process files
    stats = {
        'files_processed': 0,
        'files_modified': 0,
        'links_fixed': 0,
        'links_commented': 0,
        'links_skipped': 0,
        'actions': {'remove': 0, 'remove_item': 0, 'comment': 0, 'skip': 0}
    }

    fixes_log = []

    print("🔧 Processing medium-priority files (top 30)...")
    print()

    for file_rel_path, info in medium_priority_files[:30]:
        file_path = REPO_ROOT / file_rel_path
        if not file_path.exists():
            continue

        stats['files_processed'] += 1
        print(f"📄 {file_rel_path}")

        # Find broken links for this file
        file_links = []
        for category, links in detailed_links.items():
            if category in ['deleted_file', 'broken_relative']:
                file_links.extend([line_item for line_item in links if line_item['file'] == file_rel_path])

        if not file_links:
            continue

        file_modified = False
        fixes_in_file = 0

        for link_data in file_links[:10]:  # Limit per file
            link_url = link_data['url']

            # Analyze and fix
            analysis = analyze_link_context(file_path, link_url)
            action = analysis['action']

            if action != 'skip':
                if fix_deleted_file_reference(file_path, link_url, action):
                    file_modified = True
                    fixes_in_file += 1
                    stats['actions'][action] += 1

                    if action == 'remove' or action == 'remove_item':
                        stats['links_fixed'] += 1
                    elif action == 'comment':
                        stats['links_commented'] += 1

                    fixes_log.append({
                        'file': file_rel_path,
                        'link': link_url,
                        'action': action,
                        'reason': analysis['reason']
                    })
            else:
                stats['links_skipped'] += 1

        if file_modified:
            stats['files_modified'] += 1
            print(f"   ✅ Fixed {fixes_in_file} link(s)")
        else:
            print("   ⏭️  Skipped (no fixes applied)")

    print()
    print("=" * 80)
    print("📊 Stage 2 Summary")
    print("=" * 80)
    print(f"Files processed: {stats['files_processed']}")
    print(f"Files modified: {stats['files_modified']}")
    print(f"Links fixed (removed): {stats['links_fixed']}")
    print(f"Links commented: {stats['links_commented']}")
    print(f"Links skipped: {stats['links_skipped']}")
    print()
    print("Actions breakdown:")
    for action, count in stats['actions'].items():
        if count > 0:
            print(f"   {action}: {count}")
    print()

    # Save log
    log_file = REPO_ROOT / "PHASE_3_STAGE2_FIXES.json"
    with open(log_file, 'w') as f:
        json.dump({
            'stats': stats,
            'fixes': fixes_log
        }, f, indent=2)

    print(f"📄 Fixes log saved to: {log_file.name}")
    print()
    print("✅ Stage 2 Complete!")
    print()

    return 0 if stats['files_modified'] >= 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
