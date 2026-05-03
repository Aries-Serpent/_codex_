#!/usr/bin/env python3
"""
GitHub Reference Validator - PR #3248 Sprint 3
Validates GitHub URLs to issues, PRs, commits, and workflow runs.

This script checks GitHub references without making API calls (offline mode),
categorizing them for potential issues.

Generated: 2026-02-14
Part of: PR #3248 Sprint 3
"""

import json
import re
from collections import defaultdict
from pathlib import Path

# Repository root
REPO_ROOT = Path(__file__).parent.parent


def extract_github_refs(content: str, file_path: Path) -> list[dict]:
    """
    Extract all GitHub references from content.
    Returns list of references with context.
    """
    refs = []
    lines = content.split('\n')

    # Patterns for GitHub references
    patterns = [
        (r'github\.com/([^/]+)/([^/]+)/issues/(\d+)', 'issue'),
        (r'github\.com/([^/]+)/([^/]+)/pull/(\d+)', 'pr'),
        (r'github\.com/([^/]+)/([^/]+)/commit/([a-f0-9]{7,40})', 'commit'),
        (r'github\.com/([^/]+)/([^/]+)/actions/runs/(\d+)', 'workflow_run'),
        (r'#(\d+)', 'short_ref'),  # #123 style references
    ]

    for line_num, line in enumerate(lines, 1):
        # Skip if already marked as broken
        if '<!-- BROKEN' in line.upper():
            continue

        for pattern, ref_type in patterns:
            matches = re.finditer(pattern, line)
            for match in matches:
                ref = {
                    'file': str(file_path.relative_to(REPO_ROOT)),
                    'line': line_num,
                    'type': ref_type,
                    'url': match.group(0),
                    'context': line.strip()[:100]
                }

                if ref_type == 'short_ref':
                    ref['number'] = match.group(1)
                elif ref_type in ['issue', 'pr', 'workflow_run']:
                    ref['owner'] = match.group(1)
                    ref['repo'] = match.group(2)
                    ref['number'] = match.group(3)
                elif ref_type == 'commit':
                    ref['owner'] = match.group(1)
                    ref['repo'] = match.group(2)
                    ref['sha'] = match.group(3)

                refs.append(ref)

    return refs


def categorize_reference(ref: dict) -> str:
    """
    Categorize a reference based on patterns.
    Returns: 'likely_valid', 'uncertain', or 'needs_check'
    """
    ref_type = ref['type']
    context = ref['context'].lower()

    # Check if in a comment or example
    if any(marker in context for marker in ['example', 'e.g.', 'template', 'sample']):
        return 'likely_valid'

    # Check if marked as TODO or pending
    if any(marker in context for marker in ['todo', 'pending', 'future', 'tbd']):
        return 'uncertain'

    # Short refs without context are uncertain
    if ref_type == 'short_ref' and 'PR' not in context and 'issue' not in context:
        return 'uncertain'

    # Workflow runs are time-sensitive (may expire)
    if ref_type == 'workflow_run':
        return 'needs_check'

    # Default to needs check for safety
    return 'needs_check'


def scan_repository(directories: list[str] = None) -> dict:
    """
    Scan repository for GitHub references.
    Returns comprehensive analysis.
    """
    if directories is None:
        directories = ['.codex', 'docs', '.github']

    results = {
        'timestamp': '2026-02-14T00:10:00Z',
        'sprint': 'Sprint 3: GitHub Reference Validation',
        'scan_directories': directories,
        'files_scanned': 0,
        'files_with_refs': 0,
        'total_refs': 0,
        'by_type': defaultdict(int),
        'by_category': defaultdict(int),
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

            refs = extract_github_refs(content, md_file)

            if refs:
                results['files_with_refs'] += 1
                results['total_refs'] += len(refs)

                # Categorize references
                categorized_refs = []
                for ref in refs:
                    category = categorize_reference(ref)
                    ref['category'] = category
                    categorized_refs.append(ref)

                    results['by_type'][ref['type']] += 1
                    results['by_category'][category] += 1

                results['files'].append({
                    'file': str(md_file.relative_to(REPO_ROOT)),
                    'refs_count': len(refs),
                    'refs': categorized_refs
                })

    # Convert defaultdicts to regular dicts
    results['by_type'] = dict(results['by_type'])
    results['by_category'] = dict(results['by_category'])

    return results


def generate_validation_plan(analysis: dict) -> dict:
    """
    Generate a validation plan for GitHub references.
    Returns plan with recommendations.
    """
    plan = {
        'summary': {
            'total_refs': analysis['total_refs'],
            'by_type': analysis['by_type'],
            'by_category': analysis['by_category']
        },
        'actions': {
            'keep_as_is': [],
            'needs_validation': [],
            'manual_review': []
        },
        'recommendations': []
    }

    for file_data in analysis['files']:
        for ref in file_data['refs']:
            action_item = {
                'file': file_data['file'],
                'line': ref['line'],
                'type': ref['type'],
                'url': ref['url'],
                'category': ref['category'],
                'context': ref['context']
            }

            if ref['category'] == 'likely_valid':
                plan['actions']['keep_as_is'].append(action_item)
            elif ref['category'] == 'uncertain':
                plan['actions']['manual_review'].append(action_item)
            else:  # needs_check
                plan['actions']['needs_validation'].append(action_item)

    # Add recommendations
    if plan['actions']['needs_validation']:
        plan['recommendations'].append(
            f"Validate {len(plan['actions']['needs_validation'])} references using GitHub API or manual inspection"
        )

    if plan['actions']['manual_review']:
        plan['recommendations'].append(
            f"Manually review {len(plan['actions']['manual_review'])} uncertain references for context"
        )

    return plan


def main():
    """Main execution function."""
    print("🔗 GitHub Reference Validator - PR #3248 Sprint 3")
    print("=" * 60)
    print("\n📝 Note: Operating in offline mode (no API calls)")
    print("   Categorizing references based on patterns and context")

    # Scan repository
    print("\n📊 Scanning repository for GitHub references...")
    analysis = scan_repository()

    # Print summary
    print("\n✅ Scan Complete!")
    print(f"   Files scanned: {analysis['files_scanned']}")
    print(f"   Files with GitHub refs: {analysis['files_with_refs']}")
    print(f"   Total references: {analysis['total_refs']}")

    print("\n📋 By type:")
    for ref_type, count in sorted(analysis['by_type'].items(), key=lambda x: -x[1]):
        print(f"   {ref_type}: {count}")

    print("\n📋 By category:")
    for category, count in sorted(analysis['by_category'].items(), key=lambda x: -x[1]):
        print(f"   {category}: {count}")

    # Generate validation plan
    print("\n📝 Generating validation plan...")
    validation_plan = generate_validation_plan(analysis)

    print("\n🎯 Validation Plan:")
    print(f"   Keep as-is (likely valid): {len(validation_plan['actions']['keep_as_is'])} refs")
    print(f"   Needs validation: {len(validation_plan['actions']['needs_validation'])} refs")
    print(f"   Manual review: {len(validation_plan['actions']['manual_review'])} refs")

    if validation_plan['recommendations']:
        print("\n💡 Recommendations:")
        for i, rec in enumerate(validation_plan['recommendations'], 1):
            print(f"   {i}. {rec}")

    # Save results
    output_dir = REPO_ROOT / '.codex' / 'validation'
    output_dir.mkdir(parents=True, exist_ok=True)

    analysis_file = output_dir / 'github_refs_analysis.json'
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    print(f"\n📝 Analysis saved: {analysis_file.relative_to(REPO_ROOT)}")

    plan_file = output_dir / 'github_refs_validation_plan.json'
    with open(plan_file, 'w', encoding='utf-8') as f:
        json.dump(validation_plan, f, indent=2, ensure_ascii=False)
    print(f"📝 Validation plan saved: {plan_file.relative_to(REPO_ROOT)}")

    print("\n✨ Sprint 3 Complete!")
    print("\n📊 Summary:")
    print("   - All GitHub references cataloged and categorized")
    print(f"   - {len(validation_plan['actions']['keep_as_is'])} references appear valid")
    print(f"   - {len(validation_plan['actions']['needs_validation'])} need validation (if API available)")
    print(f"   - {len(validation_plan['actions']['manual_review'])} need manual review")
    print("\n   Note: All references logged for future validation if needed")


if __name__ == '__main__':
    main()
