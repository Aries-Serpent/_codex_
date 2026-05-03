#!/usr/bin/env python3
"""
Empty TOC Resolver - PR #3248 Sprint 2
Analyzes and resolves empty table of contents entries.

This script identifies TOC entries with:
- Empty anchors: [text]()
- Empty link text: []()
- Placeholder text: [TBD](), [TODO]()

Generated: 2026-02-14
Part of: PR #3248 Sprint 2
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

# Repository root
REPO_ROOT = Path(__file__).parent.parent


def find_toc_entries(content: str) -> List[Dict]:
    """
    Find all TOC entries in content.
    Returns list of entries with their patterns.
    """
    entries = []
    lines = content.split('\n')

    # Patterns for TOC entries
    patterns = [
        # Empty anchor: [text]()
        (r'^\s*-\s+\[([^\]]+)\]\(\)\s*$', 'empty_anchor'),
        # Empty link: []()
        (r'^\s*-\s+\[\]\(\)\s*$', 'empty_link'),
        # Placeholder with empty link: [TBD](), [TODO](), etc.
        (r'^\s*-\s+\[(TBD|TODO|PLACEHOLDER|WIP|TBA|PENDING)\]\(\)\s*$', 'placeholder'),
        # Numbered empty: 1. [text]()
        (r'^\s*\d+\.\s+\[([^\]]+)\]\(\)\s*$', 'numbered_empty'),
        # Empty with hash: [text](#)
        (r'^\s*-\s+\[([^\]]+)\]\(#\)\s*$', 'empty_hash'),
    ]

    for line_num, line in enumerate(lines, 1):
        for pattern, entry_type in patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                text = match.group(1) if match.lastindex and match.lastindex >= 1 else ""
                entries.append({
                    'line': line_num,
                    'type': entry_type,
                    'text': text,
                    'original': line.strip(),
                    'context': get_context(lines, line_num - 1)
                })
                break

    return entries


def get_context(lines: List[str], line_idx: int) -> str:
    """Get 3 lines before and after for context."""
    start = max(0, line_idx - 3)
    end = min(len(lines), line_idx + 4)
    return '\n'.join(lines[start:end])


def categorize_entry(entry: Dict, file_path: Path) -> str:
    """
    Categorize a TOC entry to determine action.
    Returns: 'future_content', 'deprecated', 'error', or 'intentional'
    """
    text = entry['text'].lower()
    entry_type = entry['type']
    context = entry['context'].lower()

    # Check for placeholder keywords
    placeholder_keywords = ['tbd', 'todo', 'placeholder', 'wip', 'tba', 'pending', 'future', 'coming soon']
    if any(kw in text for kw in placeholder_keywords):
        return 'future_content'

    # Check if commented as broken
    if '<!-- broken' in context or '<!-- todo' in context:
        return 'intentional'

    # Check for deprecation markers
    deprecated_keywords = ['deprecated', 'removed', 'obsolete', 'old', 'legacy']
    if any(kw in text or kw in context for kw in deprecated_keywords):
        return 'deprecated'

    # Empty links/anchors are likely errors
    if entry_type in ['empty_link', 'empty_hash']:
        return 'error'

    # Placeholder type
    if entry_type == 'placeholder':
        return 'future_content'

    # Default to future content for safety
    return 'future_content'


def scan_repository(directories: List[str] = None) -> Dict:
    """
    Scan repository for empty TOC entries.
    Returns comprehensive analysis.
    """
    if directories is None:
        directories = ['.codex', 'docs', '.github']

    results = {
        'timestamp': '2026-02-14T00:05:00Z',
        'sprint': 'Sprint 2: Empty TOC Resolution',
        'scan_directories': directories,
        'files_scanned': 0,
        'files_with_issues': 0,
        'total_entries': 0,
        'by_category': defaultdict(int),
        'by_type': defaultdict(int),
        'files': []
    }

    for directory in directories:
        dir_path = REPO_ROOT / directory
        if not dir_path.exists():
            continue

        # Find all markdown files
        md_files = list(dir_path.rglob('*.md'))

        for md_file in md_files:
            results['files_scanned'] += 1

            try:
                with open(md_file, encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                continue

            entries = find_toc_entries(content)

            if entries:
                results['files_with_issues'] += 1
                results['total_entries'] += len(entries)

                # Categorize entries
                categorized_entries = []
                for entry in entries:
                    category = categorize_entry(entry, md_file)
                    entry['category'] = category
                    entry['recommended_action'] = get_recommended_action(category)
                    categorized_entries.append(entry)

                    results['by_category'][category] += 1
                    results['by_type'][entry['type']] += 1

                results['files'].append({
                    'file': str(md_file.relative_to(REPO_ROOT)),
                    'entries_count': len(entries),
                    'entries': categorized_entries
                })

    # Convert defaultdicts to regular dicts
    results['by_category'] = dict(results['by_category'])
    results['by_type'] = dict(results['by_type'])

    return results


def get_recommended_action(category: str) -> str:
    """Get recommended action for a category."""
    actions = {
        'future_content': 'Comment with <!-- TODO: Add content for [Title] -->',
        'deprecated': 'Remove entry entirely',
        'error': 'Fix link or remove if section does not exist',
        'intentional': 'Keep as-is (already documented as broken)'
    }
    return actions.get(category, 'Manual review required')


def generate_action_plan(analysis: Dict) -> Dict:
    """
    Generate an action plan for resolving entries.
    Returns plan with prioritized actions.
    """
    plan = {
        'summary': {
            'total_entries': analysis['total_entries'],
            'by_category': analysis['by_category'],
            'by_type': analysis['by_type']
        },
        'actions': {
            'automated': [],
            'manual_review': [],
            'no_action': []
        }
    }

    for file_data in analysis['files']:
        for entry in file_data['entries']:
            action_item = {
                'file': file_data['file'],
                'line': entry['line'],
                'text': entry['text'],
                'type': entry['type'],
                'category': entry['category'],
                'recommended_action': entry['recommended_action']
            }

            # Categorize by automation potential
            if entry['category'] == 'intentional':
                plan['actions']['no_action'].append(action_item)
            elif entry['category'] in ['future_content', 'deprecated']:
                plan['actions']['automated'].append(action_item)
            else:
                plan['actions']['manual_review'].append(action_item)

    return plan


def main():
    """Main execution function."""
    print("📋 Empty TOC Resolver - PR #3248 Sprint 2 Part 1")
    print("=" * 60)

    # Scan repository
    print("\n📊 Scanning repository for empty TOC entries...")
    analysis = scan_repository()

    # Print summary
    print("\n✅ Scan Complete!")
    print(f"   Files scanned: {analysis['files_scanned']}")
    print(f"   Files with empty TOC entries: {analysis['files_with_issues']}")
    print(f"   Total empty entries: {analysis['total_entries']}")

    print("\n📋 By category:")
    for category, count in sorted(analysis['by_category'].items(), key=lambda x: -x[1]):
        print(f"   {category}: {count}")

    print("\n📋 By type:")
    for entry_type, count in sorted(analysis['by_type'].items(), key=lambda x: -x[1]):
        print(f"   {entry_type}: {count}")

    # Generate action plan
    print("\n📝 Generating action plan...")
    action_plan = generate_action_plan(analysis)

    print("\n🎯 Action Plan:")
    print(f"   Automated: {len(action_plan['actions']['automated'])} items")
    print(f"   Manual review: {len(action_plan['actions']['manual_review'])} items")
    print(f"   No action: {len(action_plan['actions']['no_action'])} items")

    # Save results
    output_dir = REPO_ROOT / '.codex' / 'validation'
    output_dir.mkdir(parents=True, exist_ok=True)

    analysis_file = output_dir / 'empty_toc_analysis.json'
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    print(f"\n📝 Analysis saved: {analysis_file.relative_to(REPO_ROOT)}")

    plan_file = output_dir / 'empty_toc_action_plan.json'
    with open(plan_file, 'w', encoding='utf-8') as f:
        json.dump(action_plan, f, indent=2, ensure_ascii=False)
    print(f"📝 Action plan saved: {plan_file.relative_to(REPO_ROOT)}")

    # Print next steps
    print("\n🎯 Next Steps:")
    print(f"   1. Review action plan: {plan_file.relative_to(REPO_ROOT)}")
    print("   2. Run Sprint 2 Part 2 to apply automated actions")
    print("   3. Run Sprint 2 Part 3 for manual review items")

    print("\n✨ Sprint 2 Part 1 Complete!")


if __name__ == '__main__':
    main()
