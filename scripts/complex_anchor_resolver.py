#!/usr/bin/env python3
"""
Complex Anchor Resolver - PR #3248 Phase 4 Session 1
Analyzes complex anchor references that require manual review or automated fixing.

This script identifies anchor links in documentation that may be:
1. Using non-standard anchor formatting
2. Referencing sections with special characters
3. Ambiguous due to similar heading names
4. Potentially broken but need context to verify

Generated: 2026-02-13
Part of: PR #3248 Remaining Items Resolution
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Optional

# Repository root
REPO_ROOT = Path(__file__).parent.parent


def generate_github_anchor(heading_text: str) -> str:
    """
    Generate GitHub-style anchor ID from heading text.

    Rules:
    - Convert to lowercase
    - Replace spaces with hyphens
    - Remove special characters (keep alphanumeric and hyphens)
    - Collapse multiple hyphens to single hyphen
    - Strip leading/trailing hyphens

    Examples:
        "Phase 1: Setup" -> "phase-1-setup"
        "What's Next?" -> "whats-next"
        "API Reference (v2.0)" -> "api-reference-v20"
    """
    # Convert to lowercase
    anchor = heading_text.lower()

    # Replace special chars except space and hyphen
    anchor = re.sub(r'[^\w\s-]', '', anchor)

    # Replace spaces/underscores with hyphen
    anchor = re.sub(r'[\s_]+', '-', anchor)

    # Collapse multiple hyphens
    anchor = re.sub(r'-+', '-', anchor)

    # Strip leading/trailing hyphens
    return anchor.strip('-')



def extract_headers_with_line_numbers(content: str) -> list[tuple[str, str, int]]:
    """
    Extract all headers from content with their line numbers.
    Returns list of (header_text, anchor_id, line_number).
    """
    headers = []
    lines = content.split('\n')

    for line_num, line in enumerate(lines, 1):
        if line.startswith('#'):
            # Extract header text (remove # symbols)
            header_text = line.lstrip('#').strip()

            # Skip empty headers
            if not header_text:
                continue

            # Generate anchor
            anchor = generate_github_anchor(header_text)

            headers.append((header_text, anchor, line_num))

    return headers


def find_anchor_links_with_context(content: str) -> list[dict]:
    """
    Find all anchor links in content with surrounding context.
    Returns list of dicts with link details and context.
    """
    links = []
    lines = content.split('\n')

    # Pattern for markdown links with anchors
    pattern = r'\[([^\]]+)\]\((#[^\)]+)\)'

    for line_num, line in enumerate(lines, 1):
        matches = re.finditer(pattern, line)
        for match in matches:
            link_text = match.group(1)
            anchor = match.group(2)

            # Get context (3 lines before and after)
            context_start = max(0, line_num - 4)
            context_end = min(len(lines), line_num + 3)
            context = '\n'.join(lines[context_start:context_end])

            links.append({
                'line': line_num,
                'link_text': link_text,
                'anchor': anchor,
                'full_match': match.group(0),
                'context': context,
                'column': match.start()
            })

    return links


def analyze_file_anchors(file_path: Path) -> dict:
    """
    Analyze a file for complex anchor references.
    Returns analysis results.
    """
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {
            'file': str(file_path),
            'error': str(e),
            'headers': [],
            'links': [],
            'issues': []
        }

    # Extract headers and links
    headers = extract_headers_with_line_numbers(content)
    links = find_anchor_links_with_context(content)

    # Create header anchor lookup
    valid_anchors = {f'#{anchor}': text for text, anchor, _ in headers}

    # Identify issues
    issues = []

    for link in links:
        anchor = link['anchor']

        # Check if anchor exists
        if anchor not in valid_anchors:
            # Categorize issue
            issue_type = categorize_anchor_issue(anchor, valid_anchors, link['link_text'])

            issues.append({
                'type': issue_type,
                'line': link['line'],
                'link_text': link['link_text'],
                'anchor': anchor,
                'suggested_fix': find_best_match(anchor, list(valid_anchors.keys())),
                'context': link['context'][:200],  # Limit context size
                'auto_fixable': issue_type in ['simple_mismatch', 'case_difference']
            })

    return {
        'file': str(file_path.relative_to(REPO_ROOT)),
        'headers_count': len(headers),
        'links_count': len(links),
        'issues_count': len(issues),
        'headers': [{'text': text, 'anchor': f'#{anchor}', 'line': line} for text, anchor, line in headers],
        'links': links,
        'issues': issues
    }


def categorize_anchor_issue(anchor: str, valid_anchors: dict[str, str], link_text: str) -> str:
    """
    Categorize the type of anchor issue.
    Returns issue type string.
    """
    anchor_clean = anchor.lstrip('#').lower()

    # Check for exact match with different case
    for valid in valid_anchors:
        if valid.lower() == anchor.lower():
            return 'case_difference'

    # Check for simple mismatches (extra/missing hyphens, etc.)
    for valid in valid_anchors:
        valid_clean = valid.lstrip('#').lower()

        # Remove all hyphens and compare
        if anchor_clean.replace('-', '') == valid_clean.replace('-', ''):
            return 'simple_mismatch'

        # Check if words are same but order different
        anchor_words = set(anchor_clean.split('-'))
        valid_words = set(valid_clean.split('-'))
        if anchor_words == valid_words and len(anchor_words) > 1:
            return 'word_order'

    # Check for partial matches
    for valid in valid_anchors:
        valid_clean = valid.lstrip('#').lower()
        if anchor_clean in valid_clean or valid_clean in anchor_clean:
            return 'partial_match'

    # Check for special characters
    if re.search(r'[^a-z0-9-]', anchor_clean):
        return 'special_characters'

    # Check if link text might indicate section moved/deleted
    deprecated_keywords = ['old', 'deprecated', 'removed', 'todo', 'tbd']
    if any(kw in link_text.lower() for kw in deprecated_keywords):
        return 'deprecated_section'

    return 'no_match_found'


def find_best_match(anchor: str, valid_anchors: list[str]) -> Optional[str]:
    """
    Find the best matching anchor from valid options.
    Returns best match or None.
    """
    anchor_clean = anchor.lstrip('#').lower()

    # Exact match (case insensitive)
    for valid in valid_anchors:
        if valid.lower() == anchor.lower():
            return valid

    # Match without hyphens
    anchor_no_hyphen = anchor_clean.replace('-', '')
    for valid in valid_anchors:
        if valid.lstrip('#').lower().replace('-', '') == anchor_no_hyphen:
            return valid

    # Partial match (anchor in valid)
    best_match = None
    best_score = 0

    for valid in valid_anchors:
        valid_clean = valid.lstrip('#').lower()

        # Calculate similarity score
        if anchor_clean in valid_clean:
            score = len(anchor_clean) / len(valid_clean)
            if score > best_score:
                best_score = score
                best_match = valid
        elif valid_clean in anchor_clean:
            score = len(valid_clean) / len(anchor_clean)
            if score > best_score:
                best_score = score
                best_match = valid

    return best_match if best_score > 0.5 else None


def scan_repository(directories: list[str] = None) -> dict:
    """
    Scan repository for complex anchor issues.
    Returns comprehensive analysis.
    """
    if directories is None:
        directories = ['.codex', 'docs', '.github']

    results = {
        'timestamp': '2026-02-13T23:30:00Z',
        'scan_directories': directories,
        'files_scanned': 0,
        'files_with_issues': 0,
        'total_issues': 0,
        'issues_by_type': defaultdict(int),
        'auto_fixable_count': 0,
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

            analysis = analyze_file_anchors(md_file)

            if analysis.get('issues'):
                results['files_with_issues'] += 1
                results['total_issues'] += len(analysis['issues'])

                for issue in analysis['issues']:
                    results['issues_by_type'][issue['type']] += 1
                    if issue['auto_fixable']:
                        results['auto_fixable_count'] += 1

                results['files'].append(analysis)

    # Convert defaultdict to regular dict for JSON serialization
    results['issues_by_type'] = dict(results['issues_by_type'])

    return results


def generate_review_queue(analysis: dict) -> list[dict]:
    """
    Generate a review queue for manual inspection.
    Returns list of items needing review, sorted by priority.
    """
    queue = []

    for file_data in analysis['files']:
        for issue in file_data['issues']:
            queue_item = {
                'priority': calculate_priority(issue),
                'file': file_data['file'],
                'line': issue['line'],
                'issue_type': issue['type'],
                'link_text': issue['link_text'],
                'current_anchor': issue['anchor'],
                'suggested_fix': issue['suggested_fix'],
                'auto_fixable': issue['auto_fixable'],
                'action': 'review',  # Will be updated during manual review
                'notes': ''
            }
            queue.append(queue_item)

    # Sort by priority (high to low), then by file
    queue.sort(key=lambda x: (-x['priority'], x['file'], x['line']))

    return queue


def calculate_priority(issue: dict) -> int:
    """
    Calculate priority score for an issue (0-10).
    Higher score = higher priority.
    """
    base_priority = {
        'case_difference': 10,  # Easy fix
        'simple_mismatch': 9,   # Easy fix
        'partial_match': 7,     # Likely fixable
        'word_order': 6,        # Needs review
        'special_characters': 5, # Needs review
        'deprecated_section': 3, # May need removal
        'no_match_found': 2     # Hard to fix
    }

    priority = base_priority.get(issue['type'], 1)

    # Boost priority if auto-fixable
    if issue['auto_fixable']:
        priority += 2

    # Boost if suggested fix available
    if issue['suggested_fix']:
        priority += 1

    return min(priority, 10)


def main():
    """Main execution function."""
    print("🔍 Complex Anchor Resolver - PR #3248 Phase 4 Session 1")
    print("=" * 60)

    # Scan repository
    print("\n📊 Scanning repository for complex anchor issues...")
    analysis = scan_repository()

    # Print summary
    print("\n✅ Scan Complete!")
    print(f"   Files scanned: {analysis['files_scanned']}")
    print(f"   Files with issues: {analysis['files_with_issues']}")
    print(f"   Total issues: {analysis['total_issues']}")
    print(f"   Auto-fixable: {analysis['auto_fixable_count']}")

    print("\n📋 Issues by type:")
    for issue_type, count in sorted(analysis['issues_by_type'].items(), key=lambda x: -x[1]):
        print(f"   {issue_type}: {count}")

    # Generate review queue
    print("\n📝 Generating review queue...")
    review_queue = generate_review_queue(analysis)

    # Save results
    output_dir = REPO_ROOT / '.codex' / 'validation'
    output_dir.mkdir(parents=True, exist_ok=True)

    analysis_file = output_dir / 'complex_anchors_analysis.json'
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    print(f"   Saved analysis: {analysis_file.relative_to(REPO_ROOT)}")

    queue_file = output_dir / 'complex_anchors_review_queue.json'
    with open(queue_file, 'w', encoding='utf-8') as f:
        json.dump(review_queue, f, indent=2, ensure_ascii=False)
    print(f"   Saved review queue: {queue_file.relative_to(REPO_ROOT)}")

    # Print next steps
    print("\n🎯 Next Steps:")
    print(f"   1. Review queue file: {queue_file.relative_to(REPO_ROOT)}")
    print(f"   2. For auto-fixable items ({analysis['auto_fixable_count']}), run with --fix flag")
    print("   3. For manual review items, update 'action' field in queue")
    print("   4. Run Phase 4 Session 2 to apply fixes")

    print("\n✨ Phase 4 Session 1 Complete!")


if __name__ == '__main__':
    main()
