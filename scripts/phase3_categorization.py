#!/usr/bin/env python3
"""
Phase 3: Deleted File References - Categorization & Analysis
Analyzes COMPREHENSIVE_LINK_AUDIT.json to categorize and prioritize fixes.
"""

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict

# Repository root
REPO_ROOT = Path(__file__).parent.parent

def load_audit_data() -> dict:
    """Load comprehensive link audit data."""
    audit_file = REPO_ROOT / "COMPREHENSIVE_LINK_AUDIT.json"
    with open(audit_file) as f:
        return json.load(f)

def categorize_broken_link(url: str, reason: str) -> str:
    """Categorize a broken link by type."""

    # Pattern matching for categorization
    if reason.startswith("github_broken"):
        return "github_reference"
    if reason.startswith("relative_broken"):
        # Check if it's a likely file reference
        if any(ext in url for ext in ['.md', '.py', '.yml', '.yaml', '.json', '.txt']):
            return "deleted_file"
        if url.startswith('http') or url.startswith('blob:'):
            return "malformed_url"
        if '[' in url or ']' in url or '{' in url:
            return "code_snippet"  # Likely code, not a real link
        return "broken_relative"
    if reason.startswith("external"):
        return "external_broken"
    return "other"

def analyze_broken_links(data: dict) -> Dict[str, Any]:
    """Analyze and categorize all broken links."""

    categorized = defaultdict(list)
    file_priorities = {}

    for result in data['results']:
        file_path = result['file']
        broken_links = result['broken_links']

        if not broken_links:
            continue

        # Categorize each broken link
        file_categories = defaultdict(int)
        for link in broken_links:
            url = link.get('url', '')
            reason = link.get('reason', '')
            category = categorize_broken_link(url, reason)

            categorized[category].append({
                'file': file_path,
                'url': url,
                'text': link.get('text', ''),
                'reason': reason
            })
            file_categories[category] += 1

        # Determine file priority
        # High: Documentation roots, READMEs, main guides
        # Medium: Secondary documentation
        # Low: Archive, templates, old reports

        if 'archive' in file_path.lower() or 'deprecated' in file_path.lower():
            priority = 'low'
        elif any(x in file_path.lower() for x in ['readme', 'index', 'guide', 'docs/']):
            priority = 'high' if 'template' not in file_path.lower() else 'medium'
        else:
            priority = 'medium'

        file_priorities[file_path] = {
            'priority': priority,
            'broken_count': len(broken_links),
            'categories': dict(file_categories)
        }

    return {
        'by_category': {k: len(v) for k, v in categorized.items()},
        'detailed': dict(categorized),
        'file_priorities': file_priorities
    }

def generate_phase3_plan(analysis: dict) -> dict:
    """Generate execution plan for Phase 3."""

    # Count by priority
    priority_counts = defaultdict(lambda: {'files': 0, 'links': 0})
    for file_path, info in analysis['file_priorities'].items():
        priority = info['priority']
        priority_counts[priority]['files'] += 1
        priority_counts[priority]['links'] += info['broken_count']

    # Categorize into actionable vs non-actionable
    actionable_categories = ['deleted_file', 'broken_relative', 'github_reference']
    non_actionable_categories = ['code_snippet', 'malformed_url']

    actionable_count = sum(analysis['by_category'].get(cat, 0) for cat in actionable_categories)
    non_actionable_count = sum(analysis['by_category'].get(cat, 0) for cat in non_actionable_categories)

    return {
        'total_broken': sum(analysis['by_category'].values()),
        'actionable': actionable_count,
        'non_actionable': non_actionable_count,
        'by_priority': dict(priority_counts),
        'by_category': analysis['by_category'],
        'execution_stages': [
            {
                'stage': 1,
                'name': 'High-Priority Deleted Files',
                'scope': 'High-priority files with deleted file references',
                'estimated_fixes': priority_counts['high']['links'] // 2  # Rough estimate
            },
            {
                'stage': 2,
                'name': 'Medium-Priority Deleted Files',
                'scope': 'Medium-priority files with deleted file references',
                'estimated_fixes': priority_counts['medium']['links'] // 2
            },
            {
                'stage': 3,
                'name': 'GitHub References',
                'scope': 'Broken GitHub URLs (deleted files on main)',
                'estimated_fixes': analysis['by_category'].get('github_reference', 0)
            },
            {
                'stage': 4,
                'name': 'Low-Priority and Archive',
                'scope': 'Archive files and low-priority documentation',
                'estimated_fixes': priority_counts['low']['links']
            },
            {
                'stage': 5,
                'name': 'Code Snippets Review',
                'scope': 'Review code snippets that look like links',
                'estimated_fixes': 0,  # Manual review only
                'note': 'Many are false positives - code examples, not real links'
            }
        ]
    }

def main():
    """Main execution."""
    print("=" * 80)
    print("🔍 Phase 3: Deleted File References - Analysis & Categorization")
    print("=" * 80)
    print()

    # Load data
    print("📂 Loading audit data...")
    data = load_audit_data()
    print(f"   Total broken links: {data['total_broken']}")
    print(f"   Total valid links: {data['total_valid']}")
    print(f"   Files with issues: {data['files_with_broken_links']}")
    print()

    # Analyze
    print("📊 Analyzing and categorizing...")
    analysis = analyze_broken_links(data)
    print()

    print("📋 Categorization Results:")
    print()
    for category, count in sorted(analysis['by_category'].items(), key=lambda x: x[1], reverse=True):
        print(f"   {category:20s}: {count:4d} links")
    print()

    # Generate plan
    print("📝 Generating execution plan...")
    plan = generate_phase3_plan(analysis)
    print()

    print("=" * 80)
    print("📊 Phase 3 Execution Plan")
    print("=" * 80)
    print()
    print(f"Total Broken Links: {plan['total_broken']}")
    print(f"Actionable:         {plan['actionable']} ({plan['actionable']/plan['total_broken']*100:.1f}%)")
    print(f"Non-Actionable:     {plan['non_actionable']} ({plan['non_actionable']/plan['total_broken']*100:.1f}%)")
    print()

    print("By Priority:")
    for priority in ['high', 'medium', 'low']:
        info = plan['by_priority'][priority]
        print(f"   {priority.upper():8s}: {info['files']:3d} files, {info['links']:4d} links")
    print()

    print("Execution Stages:")
    for stage_info in plan['execution_stages']:
        print(f"\n   Stage {stage_info['stage']}: {stage_info['name']}")
        print(f"   Scope: {stage_info['scope']}")
        print(f"   Estimated fixes: {stage_info['estimated_fixes']}")
        if 'note' in stage_info:
            print(f"   Note: {stage_info['note']}")
    print()

    # Save detailed analysis
    output_file = REPO_ROOT / "PHASE_3_CATEGORIZATION_REPORT.json"
    with open(output_file, 'w') as f:
        json.dump({
            'analysis': analysis,
            'plan': plan
        }, f, indent=2)

    print(f"📄 Detailed analysis saved to: {output_file.name}")
    print()

    # Save human-readable report
    md_file = REPO_ROOT / "PHASE_3_CATEGORIZATION_REPORT.md"
    with open(md_file, 'w') as f:
        f.write("# Phase 3: Deleted File References - Analysis Report\n\n")
        f.write("**Generated:** 2026-02-13\n\n")
        f.write("---\n\n")
        f.write("## Summary\n\n")
        f.write(f"- **Total Broken Links:** {plan['total_broken']}\n")
        f.write(f"- **Actionable:** {plan['actionable']} ({plan['actionable']/plan['total_broken']*100:.1f}%)\n")
        f.write(f"- **Non-Actionable:** {plan['non_actionable']} ({plan['non_actionable']/plan['total_broken']*100:.1f}%)\n\n")

        f.write("## Categorization\n\n")
        f.write("| Category | Count |\n")
        f.write("|----------|-------|\n")
        for category, count in sorted(analysis['by_category'].items(), key=lambda x: x[1], reverse=True):
            f.write(f"| {category} | {count} |\n")
        f.write("\n")

        f.write("## Priority Breakdown\n\n")
        f.write("| Priority | Files | Links |\n")
        f.write("|----------|-------|-------|\n")
        for priority in ['high', 'medium', 'low']:
            info = plan['by_priority'][priority]
            f.write(f"| {priority.upper()} | {info['files']} | {info['links']} |\n")
        f.write("\n")

        f.write("## Execution Stages\n\n")
        for stage_info in plan['execution_stages']:
            f.write(f"### Stage {stage_info['stage']}: {stage_info['name']}\n\n")
            f.write(f"**Scope:** {stage_info['scope']}\n\n")
            f.write(f"**Estimated Fixes:** {stage_info['estimated_fixes']}\n\n")
            if 'note' in stage_info:
                f.write(f"**Note:** {stage_info['note']}\n\n")

        f.write("---\n\n")
        f.write("**Next Steps:**\n\n")
        f.write("1. Review this categorization\n")
        f.write("2. Execute Stage 1 (High-Priority Deleted Files)\n")
        f.write("3. Validate and commit changes\n")
        f.write("4. Proceed to subsequent stages\n")

    print(f"📄 Human-readable report saved to: {md_file.name}")
    print()
    print("✅ Analysis Complete!")
    print()

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
