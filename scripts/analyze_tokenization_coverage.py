#!/usr/bin/env python3
"""Analyze coverage gaps in tokenization module and generate detailed report."""
import json
from typing import Any


def analyze_coverage_gaps(coverage_file: str = 'coverage_reports/coverage_tokenization.json') -> list[dict[str, Any]]:
    """Analyze coverage gaps and generate detailed report."""
    with open(coverage_file) as f:
        data = json.load(f)

    gaps = []
    for filepath, filedata in data['files'].items():
        if 'src/tokenization/' in filepath:
            missing_lines = filedata.get('missing_lines', [])
            covered = filedata['summary']['covered_lines']
            total = filedata['summary']['num_statements']
            percent = filedata['summary']['percent_covered']

            gaps.append({
                'file': filepath,
                'filename': filepath.split('/')[-1],
                'coverage': percent,
                'covered': covered,
                'total': total,
                'missing_lines': missing_lines,
                'gap': 70.0 - percent,
                'lines_needed': int((70.0 * total / 100.0) - covered)
            })

    # Sort by gap size (largest first)
    gaps.sort(key=lambda x: x['gap'], reverse=True)

    return gaps


def main():
    """Generate coverage gap analysis report."""
    gaps = analyze_coverage_gaps()

    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print("TOKENIZATION COVERAGE GAP ANALYSIS")  # codeql[py/clear-text-logging-sensitive-data]
    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    # Overall summary
    total_stmts = sum(g['total'] for g in gaps)
    total_covered = sum(g['covered'] for g in gaps)
    overall_pct = (total_covered / total_stmts * 100) if total_stmts > 0 else 0

    print(f"Overall Coverage: {overall_pct:.2f}%")  # codeql[py/clear-text-logging-sensitive-data]
    print("Target Coverage: 70.00%")  # codeql[py/clear-text-logging-sensitive-data]
    print(f"Gap to Target: {70.0 - overall_pct:.2f} percentage points")  # codeql[py/clear-text-logging-sensitive-data]
    print(f"Lines Covered: {total_covered}/{total_stmts}")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    # Per-file breakdown
    print("-" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print("PER-FILE COVERAGE GAPS (Highest Priority First)")  # codeql[py/clear-text-logging-sensitive-data]
    print("-" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    for i, gap in enumerate(gaps, 1):
        print(f"{i}. 📄 {gap['filename']}")  # codeql[py/clear-text-logging-sensitive-data]
        print(f"   Path: {gap['file']}")  # codeql[py/clear-text-logging-sensitive-data]
        print(f"   Current Coverage: {gap['coverage']:.2f}% ({gap['covered']}/{gap['total']} lines)")  # codeql[py/clear-text-logging-sensitive-data]
        print(f"   Gap to 70% Target: {gap['gap']:.2f} percentage points")  # codeql[py/clear-text-logging-sensitive-data]
        print(f"   Lines Needed: ~{gap['lines_needed']} additional lines")  # codeql[py/clear-text-logging-sensitive-data]

        if gap['missing_lines']:
            # Show sample of missing lines
            if len(gap['missing_lines']) <= 10:
                print(f"   Missing Lines: {gap['missing_lines']}")  # codeql[py/clear-text-logging-sensitive-data]
            else:
                sample = gap['missing_lines'][:5] + ['...'] + gap['missing_lines'][-5:]
                print(f"   Missing Lines (sample): {sample}")  # codeql[py/clear-text-logging-sensitive-data]

        # Priority classification
        if gap['gap'] > 50:
            priority = "🔴 CRITICAL"
        elif gap['gap'] > 20:
            priority = "🟡 HIGH"
        elif gap['gap'] > 0:
            priority = "🟢 MEDIUM"
        else:
            priority = "✅ COMPLETE"
        print(f"   Priority: {priority}")  # codeql[py/clear-text-logging-sensitive-data]
        print()  # codeql[py/clear-text-logging-sensitive-data]

    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print("SUMMARY RECOMMENDATIONS")  # codeql[py/clear-text-logging-sensitive-data]
    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    critical_files = [g for g in gaps if g['gap'] > 50]
    high_files = [g for g in gaps if 20 < g['gap'] <= 50]
    medium_files = [g for g in gaps if 0 < g['gap'] <= 20]
    complete_files = [g for g in gaps if g['gap'] <= 0]

    print(f"🔴 CRITICAL Priority Files: {len(critical_files)}")  # codeql[py/clear-text-logging-sensitive-data]
    for g in critical_files:
        print(f"   - {g['filename']}: {g['coverage']:.2f}% (need {g['lines_needed']} lines)")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    print(f"🟡 HIGH Priority Files: {len(high_files)}")  # codeql[py/clear-text-logging-sensitive-data]
    for g in high_files:
        print(f"   - {g['filename']}: {g['coverage']:.2f}% (need {g['lines_needed']} lines)")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    print(f"🟢 MEDIUM Priority Files: {len(medium_files)}")  # codeql[py/clear-text-logging-sensitive-data]
    for g in medium_files:
        print(f"   - {g['filename']}: {g['coverage']:.2f}% (need {g['lines_needed']} lines)")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    print(f"✅ COMPLETE Files (≥70%): {len(complete_files)}")  # codeql[py/clear-text-logging-sensitive-data]
    for g in complete_files:
        print(f"   - {g['filename']}: {g['coverage']:.2f}%")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print("NEXT STEPS")  # codeql[py/clear-text-logging-sensitive-data]
    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]
    print("1. Focus test implementation on CRITICAL priority files first")  # codeql[py/clear-text-logging-sensitive-data]
    print("2. Implement 10+ comprehensive tests per plan in Pre-commit 5-8")  # codeql[py/clear-text-logging-sensitive-data]
    print("3. Target high-impact functions with low/no coverage")  # codeql[py/clear-text-logging-sensitive-data]
    print("4. Use test patterns from .codex/docs/TEST_DEVELOPMENT_PATTERNS.md")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]
    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]


if __name__ == '__main__':
    main()
