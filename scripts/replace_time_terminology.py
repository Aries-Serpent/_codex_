#!/usr/bin/env python3
"""
Replace time-based terminology with iteration-based workflow terminology.

Context-aware replacements:
- "N days" → "N iterations" (development work)
- "N weeks" → "N phases" (longer periods)
- "daily" → "per-iteration"
- "weekly" → "per-phase"
- "Hours" → "Commits" (metrics context)
- "Minutes" → "Pre-commits" (metrics context)

PRESERVES:
- ISO 8601 timestamps (YYYY-MM-DD, HH:MM:SS)
- CI/CD technical metrics (<3 minutes build time)
- Cache/artifact retention periods (30 days retention)
- Cron schedules and timeouts
- UTC time references
"""

import json
import re
import sys
from pathlib import Path
from typing import List, Tuple


class TimeTerminologyReplacer:
    def __init__(self):
        self.changes_log = []
        self.files_processed = 0
        self.total_replacements = 0

        # Patterns to PRESERVE (must not be replaced)
        self.preserve_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # ISO dates
            r'\d{2}:\d{2}:\d{2}',  # Time stamps
            r'<\s*\d+\s*minutes?\s*',  # "<3 minutes" build time
            r'\d+\s*days?\s+retention',  # "30 days retention"
            r'\d+\s*days?\s+cache',  # "90 days cache"
            r'cron:\s*["\']?[\d\s\*\/]+["\']?',  # Cron schedules
            r'timeout:\s*\d+',  # Timeout values
            r'UTC',  # UTC references
            r'Z$',  # ISO timestamp suffix
            r'\d+\s*days?\s+ago',  # Git log relative dates
            r'retention[-_]days',  # retention_days variable
            r'cache[-_]ttl',  # cache TTL
            r'expir(e|es|ed|ation)',  # expiration contexts
        ]

        # Replacement patterns (order matters!)
        self.replacements = [
            # Days patterns
            (r'\b(\d+)[-\s]+day(s?)\b(?!\s+(retention|cache|ago|expir))', r'\1 iteration\2', 'N days → N iterations'),
            (r'\bday-by-day\b', r'iteration-by-iteration', 'day-by-day → iteration-by-iteration'),
            (r'\bper[- ]day\b', r'per-iteration', 'per-day → per-iteration'),
            (r'\bdaily\b(?!\.yml)', r'per-iteration', 'daily → per-iteration'),
            (r'\beach day\b', r'each iteration', 'each day → each iteration'),
            (r'\bevery day\b', r'every iteration', 'every day → every iteration'),

            # Weeks patterns
            (r'\b(\d+)[-\s]+week(s?)\b', r'\1 phase\2', 'N weeks → N phases'),
            (r'\bweek-by-week\b', r'phase-by-phase', 'week-by-week → phase-by-phase'),
            (r'\bper[- ]week\b', r'per-phase', 'per-week → per-phase'),
            (r'\bweekly\b', r'per-phase', 'weekly → per-phase'),
            (r'\beach week\b', r'each phase', 'each week → each phase'),
            (r'\bevery week\b', r'every phase', 'every week → every phase'),

            # Metrics context - Hours/Minutes
            (r'\bHours\b(?=\s*\|)', r'Commits', 'Hours → Commits (metrics)'),
            (r'\bMinutes\b(?=\s*\|)', r'Pre-commits', 'Minutes → Pre-commits (metrics)'),

            # Generic time references in development context
            (r'\bin\s+\d+\s+days?\b(?!\s+(retention|cache|ago))', lambda m: m.group(0).replace('day', 'iteration').replace('days', 'iterations'), 'in N days → in N iterations'),
            (r'\bwithin\s+\d+\s+days?\b(?!\s+(retention|cache))', lambda m: m.group(0).replace('day', 'iteration').replace('days', 'iterations'), 'within N days → within N iterations'),
            (r'\bover\s+\d+\s+days?\b(?!\s+(retention|cache))', lambda m: m.group(0).replace('day', 'iteration').replace('days', 'iterations'), 'over N days → over N iterations'),
            (r'\bafter\s+\d+\s+days?\b(?!\s+(retention|cache|ago))', lambda m: m.group(0).replace('day', 'iteration').replace('days', 'iterations'), 'after N days → after N iterations'),

            # Week variants
            (r'\bin\s+\d+\s+weeks?\b', lambda m: m.group(0).replace('week', 'phase').replace('weeks', 'phases'), 'in N weeks → in N phases'),
            (r'\bwithin\s+\d+\s+weeks?\b', lambda m: m.group(0).replace('week', 'phase').replace('weeks', 'phases'), 'within N weeks → within N phases'),
            (r'\bover\s+\d+\s+weeks?\b', lambda m: m.group(0).replace('week', 'phase').replace('weeks', 'phases'), 'over N weeks → over N phases'),
        ]

    def should_preserve_line(self, line: str) -> bool:
        """Check if line contains patterns that should be preserved."""
        return any(re.search(pattern, line, re.IGNORECASE) for pattern in self.preserve_patterns)

    def process_file(self, filepath: Path) -> Tuple[bool, List[str]]:
        """Process a single file and return (changed, change_descriptions)."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return False, [f"Error reading file: {e}"]

        original_content = content
        changes_made = []
        lines = content.split('\n')
        new_lines = []

        for line_num, line in enumerate(lines, 1):
            original_line = line

            # Skip lines with preserve patterns
            if self.should_preserve_line(line):
                new_lines.append(line)
                continue

            # Apply replacements
            for pattern, replacement, description in self.replacements:
                if callable(replacement):
                    new_line = re.sub(pattern, replacement, line, flags=re.IGNORECASE)
                else:
                    new_line = re.sub(pattern, replacement, line, flags=re.IGNORECASE)

                if new_line != line:
                    changes_made.append(f"Line {line_num}: {description}")
                    changes_made.append(f"  Old: {original_line.strip()}")
                    changes_made.append(f"  New: {new_line.strip()}")
                    line = new_line

            new_lines.append(line)

        new_content = '\n'.join(new_lines)

        if new_content != original_content:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True, changes_made
            except Exception as e:
                return False, [f"Error writing file: {e}"]

        return False, []

    def process_files(self, file_list_path: str):
        """Process all files from the list."""
        with open(file_list_path, 'r') as f:
            files = [line.strip() for line in f if line.strip()]

        print(f"Processing {len(files)} files...")

        for filepath_str in files:
            filepath = Path(filepath_str)

            if not filepath.exists():
                print(f"⚠️  File not found: {filepath}")
                continue

            if not filepath.is_file():
                print(f"⚠️  Not a file: {filepath}")
                continue

            changed, changes = self.process_file(filepath)

            if changed:
                self.files_processed += 1
                self.total_replacements += len([c for c in changes if c.startswith('Line')])
                self.changes_log.append({
                    'file': str(filepath),
                    'changes': changes
                })
                print(f"✅ {filepath.relative_to(Path.cwd())} ({len([c for c in changes if c.startswith('Line')])} replacements)")
            else:
                print(f"⏭️  {filepath.relative_to(Path.cwd())} (no changes)")

    def generate_report(self, output_path: str):
        """Generate detailed change report."""
        report = []
        report.append("=" * 80)
        report.append("TIME TERMINOLOGY REPLACEMENT REPORT")
        report.append("=" * 80)
        report.append(f"Files processed: {self.files_processed}")
        report.append(f"Total replacements: {self.total_replacements}")
        report.append("")
        report.append("=" * 80)
        report.append("DETAILED CHANGES")
        report.append("=" * 80)
        report.append("")

        for entry in self.changes_log:
            report.append(f"\n{'=' * 80}")
            report.append(f"File: {entry['file']}")
            report.append(f"{'=' * 80}")
            for change in entry['changes']:
                report.append(change)

        report_content = '\n'.join(report)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"\n📊 Report saved to: {output_path}")

        # Also save JSON version
        json_path = output_path.replace('.txt', '.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'files_processed': self.files_processed,
                    'total_replacements': self.total_replacements
                },
                'changes': self.changes_log
            }, f, indent=2)
        print(f"📊 JSON report saved to: {json_path}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python replace_time_terminology.py <file_list.txt>")
        sys.exit(1)

    file_list = sys.argv[1]

    replacer = TimeTerminologyReplacer()
    replacer.process_files(file_list)
    replacer.generate_report('/tmp/time_terminology_replacement_report.txt')

    print("\n✅ Processing complete!")
    print(f"   Files changed: {replacer.files_processed}")
    print(f"   Total replacements: {replacer.total_replacements}")

if __name__ == '__main__':
    main()
