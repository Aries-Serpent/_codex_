#!/usr/bin/env python3
"""
Comprehensive Freshness Audit for Admin Documentation
Scans all markdown files in docs/admin/ and generates detailed audit report
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ISO 8601 date pattern
ISO_8601_PATTERN = r'\d{4}-\d{2}-\d{2}'

# Calendar-based language patterns
CALENDAR_PATTERNS = [
    r'\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',
    r'\b(January|February|March|April|June|July|August|September|October|November|December)\b',
    r'\b(Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b',
    r'\b(week|weeks|month|months)\s+(ago|old|since)\b',
    r'\b(last|next|this)\s+(week|month|day|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',
    r'\b(yesterday|tomorrow)\b',
]

def extract_last_updated_date(content: str, file_path: str) -> Optional[Tuple[str, bool, int]]:
    """
    Extract last updated date from file content.
    Returns: (date_string, is_iso_8601, line_number) or None
    """
    lines = content.split('\n')

    # Common patterns for "Last Updated" metadata
    patterns = [
        r'\*\*Last\s+Updated\*\*:\s*(.+)',
        r'Last\s+Updated:\s*(.+)',
        r'\*\*Date\*\*:\s*(.+)',
        r'Date:\s*(.+)',
        r'last_updated:\s*(.+)',
        r'date:\s*(.+)',
    ]

    for line_num, line in enumerate(lines[:50], 1):  # Check first 50 lines
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                date_str = match.group(1).strip()
                # Remove markdown formatting
                date_str = re.sub(r'[*_`]', '', date_str)
                # Clean up common prefixes
                date_str = date_str.lstrip(':').strip()

                # Check if this looks like a valid date (not just text)
                if len(date_str) < 8 or not any(c.isdigit() for c in date_str):
                    continue

                is_iso = bool(re.match(ISO_8601_PATTERN, date_str))
                return (date_str, is_iso, line_num)

    return None

def parse_date(date_str: str) -> Optional[datetime]:
    """Try to parse date string in various formats."""
    # Clean up the date string
    date_str = date_str.strip()

    formats = [
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%d-%m-%Y',
        '%d/%m/%Y',
        '%B %d, %Y',
        '%b %d, %Y',
        '%m/%d/%Y',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%d %H:%M:%S',
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    return None

def check_calendar_language(content: str) -> List[Dict]:
    """Check for calendar-based language in content."""
    findings = []
    lines = content.split('\n')

    for pattern in CALENDAR_PATTERNS:
        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                findings.append({
                    'line_number': line_num,
                    'text': match.group(0),
                    'context': line.strip()[:100]
                })

    return findings

def get_staleness_level(date_obj: datetime) -> str:
    """Determine staleness level based on age."""
    now = datetime.now()
    age_days = (now - date_obj).days

    if age_days < 30:
        return 'Fresh'
    if age_days < 90:
        return 'Aging'
    return 'Stale'

def audit_file(file_path: Path, repo_root: Path) -> Dict:
    """Audit a single markdown file.

    Args:
        file_path: Path to the file to audit
        repo_root: Repository root path for relative path calculation
    """
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {
            'file': str(file_path),
            'error': f"Could not read file: {e!s}"
        }

    result = {
        'file': str(file_path.relative_to(repo_root)),
        'size_bytes': len(content),
        'line_count': content.count('\n') + 1,
    }

    # Extract last updated date
    date_info = extract_last_updated_date(content, str(file_path))

    if date_info:
        date_str, is_iso, line_num = date_info
        result['last_updated_raw'] = date_str
        result['last_updated_line'] = line_num
        result['is_iso_8601'] = is_iso

        # Try to parse the date
        parsed_date = parse_date(date_str)
        if parsed_date:
            result['last_updated_parsed'] = parsed_date.isoformat()
            result['age_days'] = (datetime.now() - parsed_date).days
            result['staleness_level'] = get_staleness_level(parsed_date)
        else:
            result['last_updated_parsed'] = None
            result['parse_error'] = 'Could not parse date'
    else:
        result['last_updated_raw'] = None
        result['missing_date_metadata'] = True

    # Check for calendar language
    calendar_findings = check_calendar_language(content)
    if calendar_findings:
        result['calendar_language_count'] = len(calendar_findings)
        result['calendar_language_samples'] = calendar_findings[:5]  # First 5 samples
    else:
        result['calendar_language_count'] = 0

    # File modification time (fallback)
    stat = os.stat(file_path)
    result['file_mtime'] = datetime.fromtimestamp(stat.st_mtime).isoformat()

    return result

def generate_audit_report(docs_dir: Path) -> Dict:
    """Generate comprehensive audit report."""
    # Get repo root for relative paths - scripts/maintenance/ is 2 levels deep
    repo_root = Path(__file__).resolve().parent.parent.parent

    # Find all markdown files
    md_files = sorted(docs_dir.rglob('*.md'))

    print(f"Found {len(md_files)} markdown files to audit...")

    audit_results = []
    for file_path in md_files:
        print(f"Auditing: {file_path.relative_to(repo_root)}")
        result = audit_file(file_path, repo_root)
        audit_results.append(result)

    # Generate statistics
    now = datetime.now()

    total_files = len(audit_results)
    files_with_dates = sum(1 for r in audit_results if r.get('last_updated_raw'))
    files_missing_dates = sum(1 for r in audit_results if r.get('missing_date_metadata'))
    files_iso_8601 = sum(1 for r in audit_results if r.get('is_iso_8601'))
    files_non_iso = sum(1 for r in audit_results if r.get('last_updated_raw') and not r.get('is_iso_8601'))

    fresh_files = sum(1 for r in audit_results if r.get('staleness_level') == 'Fresh')
    aging_files = sum(1 for r in audit_results if r.get('staleness_level') == 'Aging')
    stale_files = sum(1 for r in audit_results if r.get('staleness_level') == 'Stale')

    files_with_calendar_lang = sum(1 for r in audit_results if r.get('calendar_language_count', 0) > 0)
    total_calendar_instances = sum(r.get('calendar_language_count', 0) for r in audit_results)

    statistics = {
        'audit_timestamp': now.isoformat(),
        'total_files': total_files,
        'files_with_date_metadata': files_with_dates,
        'files_missing_date_metadata': files_missing_dates,
        'files_iso_8601_compliant': files_iso_8601,
        'files_non_iso_8601': files_non_iso,
        'staleness_breakdown': {
            'fresh_under_30_days': fresh_files,
            'aging_30_90_days': aging_files,
            'stale_over_90_days': stale_files,
            'unknown_no_date': files_missing_dates
        },
        'calendar_language': {
            'files_with_calendar_language': files_with_calendar_lang,
            'total_calendar_instances': total_calendar_instances
        }
    }

    # Categorize files
    categorized = {
        'fresh': [r for r in audit_results if r.get('staleness_level') == 'Fresh'],
        'aging': [r for r in audit_results if r.get('staleness_level') == 'Aging'],
        'stale': [r for r in audit_results if r.get('staleness_level') == 'Stale'],
        'missing_dates': [r for r in audit_results if r.get('missing_date_metadata')],
        'needs_iso_conversion': [r for r in audit_results if r.get('last_updated_raw') and not r.get('is_iso_8601')],
        'has_calendar_language': [r for r in audit_results if r.get('calendar_language_count', 0) > 0]
    }

    return {
        'statistics': statistics,
        'categorized_files': categorized,
        'all_files': audit_results
    }

def main():
    """Main execution function."""
    # Get repository root dynamically - scripts/maintenance/ is 2 levels deep
    repo_root = Path(__file__).resolve().parent.parent.parent
    docs_dir = repo_root / 'docs' / 'admin'

    if not docs_dir.exists():
        print(f"Error: Directory {docs_dir} does not exist!")
        return

    print("=" * 80)
    print("ADMIN DOCUMENTATION FRESHNESS AUDIT")
    print("=" * 80)
    print()

    # Generate audit report
    report = generate_audit_report(docs_dir)

    # Save to JSON file
    output_dir = repo_root / '.codex'
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / 'admin_docs_audit.json'

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print()
    print("=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)
    print(f"\nFull report saved to: {output_file}")
    print()

    # Print summary
    stats = report['statistics']
    print("SUMMARY STATISTICS")
    print("-" * 80)
    print(f"Total Files Audited:           {stats['total_files']}")
    print(f"Files with Date Metadata:      {stats['files_with_date_metadata']}")
    print(f"Files Missing Dates:           {stats['files_missing_date_metadata']}")
    print(f"Files ISO 8601 Compliant:      {stats['files_iso_8601_compliant']}")
    print(f"Files Needing ISO Conversion:  {stats['files_non_iso_8601']}")
    print()
    print("STALENESS LEVELS")
    print("-" * 80)
    sb = stats['staleness_breakdown']
    print(f"✅ Fresh (<30 days):           {sb['fresh_under_30_days']}")
    print(f"⚠️  Aging (30-90 days):         {sb['aging_30_90_days']}")
    print(f"🔴 Stale (>90 days):           {sb['stale_over_90_days']}")
    print(f"❓ Unknown (no date):          {sb['unknown_no_date']}")
    print()
    print("CALENDAR LANGUAGE DETECTION")
    print("-" * 80)
    cl = stats['calendar_language']
    print(f"Files with Calendar Language:  {cl['files_with_calendar_language']}")
    print(f"Total Calendar Instances:      {cl['total_calendar_instances']}")
    print()

    # Print files needing attention
    if report['categorized_files']['stale']:
        print("🔴 STALE FILES (>90 days old)")
        print("-" * 80)
        for file_info in report['categorized_files']['stale']:
            age = file_info.get('age_days', '?')
            print(f"  • {file_info['file']} ({age} days old)")
        print()

    if report['categorized_files']['missing_dates']:
        print("❓ FILES MISSING DATE METADATA")
        print("-" * 80)
        for file_info in report['categorized_files']['missing_dates']:
            print(f"  • {file_info['file']}")
        print()

    if report['categorized_files']['needs_iso_conversion']:
        print("📅 FILES NEEDING ISO 8601 CONVERSION")
        print("-" * 80)
        for file_info in report['categorized_files']['needs_iso_conversion']:
            date = file_info.get('last_updated_raw', '?')
            print(f"  • {file_info['file']} (currently: {date})")
        print()

    if report['categorized_files']['has_calendar_language']:
        print("📆 FILES WITH CALENDAR LANGUAGE (Top 10)")
        print("-" * 80)
        calendar_files = sorted(
            report['categorized_files']['has_calendar_language'],
            key=lambda x: x.get('calendar_language_count', 0),
            reverse=True
        )[:10]
        for file_info in calendar_files:
            count = file_info.get('calendar_language_count', 0)
            print(f"  • {file_info['file']} ({count} instances)")
        print()

if __name__ == '__main__':
    main()
