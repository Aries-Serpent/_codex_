#!/usr/bin/env python3
"""
Documentation Template Validator

Validates documentation files against the 6-section template standard.
Can be used as a pre-commit hook or CI check.

Template Sections:
1. Mission Overview
2. Verification Checklist
3. Success Metrics
4. Physics Alignment
5. Energy Distribution
6. Redundancy Patterns

Author: Codex Documentation System
Generated: 2026-01-23T10:50:00Z
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ISO 8601 date format patterns
ISO_8601_PATTERNS = [
    r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',
    r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
    r'\d{4}-\d{2}-\d{2}',
]

# Calendar-based language to flag
CALENDAR_TERMS = [
    r'\b(week|weeks|weekly)\b',
    r'\b(month|months|monthly)\b',
    r'\b(day|days|daily)\b',
    r'\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',
]

# Required template sections
REQUIRED_SECTIONS = [
    "Mission Overview",
    "Verification Checklist",
    "Success Metrics",
    "Physics Alignment",
    "Energy Distribution",
    "Redundancy Patterns",
]

# Section patterns for flexible matching
SECTION_PATTERNS = {
    "Mission Overview": [r"##\s+🎯\s+Mission\s+Overview", r"##\s+Mission\s+Overview", r"##\s+Overview"],
    "Verification Checklist": [r"##\s+⚖️\s+Verification\s+Checklist", r"##\s+Verification\s+Checklist"],
    "Success Metrics": [r"##\s+📈\s+Success\s+Metrics", r"##\s+Success\s+Metrics", r"##\s+Metrics"],
    "Physics Alignment": [r"##\s+⚛️\s+Physics\s+Alignment", r"##\s+Physics\s+Alignment"],
    "Energy Distribution": [r"##\s+⚡\s+Energy\s+Distribution", r"##\s+Energy\s+Distribution"],
    "Redundancy Patterns": [r"##\s+🧠\s+Redundancy\s+Patterns", r"##\s+Redundancy\s+Patterns"],
}


class ValidationResult:
    """Validation result for a single file"""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.missing_sections: list[str] = []
        self.found_sections: list[str] = []
        self.date_issues: list[dict] = []
        self.calendar_language: list[dict] = []

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    @property
    def severity_score(self) -> int:
        return len(self.errors) * 3 + len(self.warnings) * 2


class DocTemplateValidator:
    """Validates documentation against template standards"""

    def __init__(self, strict: bool = False, check_calendar: bool = True):
        self.strict = strict
        self.check_calendar = check_calendar

    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate a single file"""
        result = ValidationResult(file_path)

        if not file_path.exists():
            result.errors.append(f"File does not exist: {file_path}")
            return result

        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            result.errors.append(f"Failed to read file: {e}")
            return result

        self._check_sections(content, result)
        self._check_dates(content, result)
        if self.check_calendar:
            self._check_calendar_language(content, result)

        return result

    def _check_sections(self, content: str, result: ValidationResult):
        """Check for required template sections"""
        for section in REQUIRED_SECTIONS:
            found = False
            patterns = SECTION_PATTERNS.get(section, [])

            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    found = True
                    result.found_sections.append(section)
                    break

            if not found:
                result.missing_sections.append(section)
                if self.strict:
                    result.errors.append(f"Missing required section: {section}")
                else:
                    result.warnings.append(f"Missing recommended section: {section}")

    def _check_dates(self, content: str, result: ValidationResult):
        """Check date format compliance"""
        lines = content.split('\n')

        date_patterns = [
            r'(Last\s+Updated|Generated|Date|Updated):\s*(.+)',
            r'\*\*(?:Last\s+Updated|Generated|Date|Updated)\*\*:\s*(.+)',
        ]

        for line_num, line in enumerate(lines, 1):
            for pattern in date_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    # Get the last group (the date string)
                    date_str = match.groups()[-1].strip() if match.groups() else ""
                    is_iso = any(re.match(p, date_str) for p in ISO_8601_PATTERNS)

                    if not is_iso and date_str:
                        result.date_issues.append({
                            'line': line_num,
                            'text': line.strip(),
                            'date_str': date_str,
                        })
                        if self.strict:
                            result.errors.append(f"Non-ISO 8601 date on line {line_num}: {date_str}")
                        else:
                            result.warnings.append(f"Non-ISO 8601 date on line {line_num}: {date_str}")

    def _check_calendar_language(self, content: str, result: ValidationResult):
        """Check for calendar-based language"""
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            for term_pattern in CALENDAR_TERMS:
                matches = re.finditer(term_pattern, line, re.IGNORECASE)
                for match in matches:
                    if '```' in line or 'cron:' in line.lower():
                        continue

                    result.calendar_language.append({
                        'line': line_num,
                        'text': line.strip(),
                        'term': match.group(0),
                    })

        if result.calendar_language:
            count = len(result.calendar_language)
            result.warnings.append(f"Found {count} calendar-based terms")


def main():
    parser = argparse.ArgumentParser(description="Validate documentation against template standards")
    parser.add_argument('--path', type=Path, required=True, help='File or directory to validate')
    parser.add_argument('--strict', action='store_true', help='Strict mode')
    parser.add_argument('--recursive', action='store_true', default=True, help='Recursive validation')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--json', action='store_true', help='JSON output')

    args = parser.parse_args()

    validator = DocTemplateValidator(strict=args.strict)

    results = []
    if args.path.is_file():
        results = [validator.validate_file(args.path)]
    elif args.path.is_dir():
        pattern = "**/*.md" if args.recursive else "*.md"
        for md_file in args.path.glob(pattern):
            if md_file.is_file():
                results.append(validator.validate_file(md_file))

    # Print results
    if args.json:
        output = [{'file': str(r.file_path), 'valid': r.is_valid, 'errors': r.errors,
                   'warnings': r.warnings, 'missing_sections': r.missing_sections}
                  for r in results]
        print(json.dumps(output, indent=2))
    else:
        total = len(results)
        valid = sum(1 for r in results if r.is_valid)
        print(f"\nValidation Report - Generated: {datetime.now(timezone.utc).isoformat()}Z")
        print(f"Total: {total} | Valid: {valid} | Invalid: {total-valid}")

        for result in sorted(results, key=lambda r: r.severity_score, reverse=True):
            if not result.is_valid or args.verbose:
                print(f"\n{result.file_path}")
                print(f"Status: {'✅ VALID' if result.is_valid else '❌ INVALID'}")
                if result.errors:
                    print(f"Errors: {len(result.errors)}")
                    for e in result.errors:
                        print(f"  - {e}")
                if result.warnings:
                    print(f"Warnings: {len(result.warnings)}")
                    for w in result.warnings[:3]:
                        print(f"  - {w}")
                if result.missing_sections:
                    print(f"Missing: {', '.join(result.missing_sections)}")

    return 1 if any(not r.is_valid for r in results) else 0


if __name__ == '__main__':
    sys.exit(main())
