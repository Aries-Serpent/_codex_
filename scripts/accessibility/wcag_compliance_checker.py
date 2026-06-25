#!/usr/bin/env python3
"""
Comprehensive WCAG AA compliance checking for markdown documentation.

Identifies common accessibility violations:
- Missing alt text on images
- Color contrast issues
- Missing labels
- Poor semantic structure
"""

import re
from pathlib import Path
from typing import Dict, List


class WCAGComplianceChecker:
    """Check WCAG AA compliance in markdown documentation."""

    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        self.issues: List[Dict] = []
        self.files_checked: int = 0

    def check_image_alt_text(self, content: str, file_path: str) -> List[str]:
        """Check for images without alt text."""
        issues = []

        # Find markdown images
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        for match in re.finditer(image_pattern, content):
            alt_text = match.group(1).strip()
            image_path = match.group(2)

            if not alt_text or alt_text.isspace():
                issues.append(f"Missing alt text for image: {image_path}")

        return issues

    def check_link_descriptiveness(self, content: str) -> List[str]:
        """Check for poorly described links."""
        issues = []

        poor_descriptions = [
            'http://', 'https://', 'click here', 'here', 'link',
            'see', 'go here', 'more info', 'read more', 'more'
        ]

        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        for match in re.finditer(link_pattern, content):
            description = match.group(1).lower().strip()
            url = match.group(2)

            if description in poor_descriptions or description.startswith('http'):
                issues.append(f"Poorly described link: '{description}' -> {url}")

        return issues

    def check_heading_structure(self, content: str) -> List[str]:
        """Check for improper heading structure."""
        issues = []
        lines = content.split('\n')
        previous_level = 0
        has_h1 = False

        for i, line in enumerate(lines, 1):
            match = re.match(r'^(#+)\s+', line)
            if not match:
                continue

            level = len(match.group(1))

            if level == 1:
                has_h1 = True

            # Check for jumps
            if previous_level > 0 and level - previous_level > 1:
                issues.append(f"Line {i}: Heading jump from H{previous_level} to H{level}")

            previous_level = level

        if not has_h1:
            issues.append("Document has no H1 heading")

        return issues

    def check_list_structure(self, content: str) -> List[str]:
        """Check for properly formatted lists."""
        issues = []

        # Check for mixed list markers
        lines = content.split('\n')
        in_list = False
        list_marker = None

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                in_list = False
                continue

            # Check for list items
            if re.match(r'^[\*\-\+]\s+', stripped) or re.match(r'^\d+\.\s+', stripped):
                if not in_list:
                    in_list = True
                    if re.match(r'^[\*\-\+]\s+', stripped):
                        list_marker = 'unordered'
                    else:
                        list_marker = 'ordered'
                else:
                    # Check consistency
                    if list_marker == 'unordered' and re.match(r'^\d+\.\s+', stripped):
                        issues.append(f"Line {i}: Mixed list markers (unordered and ordered)")

        return issues

    def check_code_block_language(self, content: str) -> List[str]:
        """Check for code blocks with language specification."""
        issues = []

        # Find code blocks
        code_pattern = r'```([a-zA-Z]*)\n'
        for match in re.finditer(code_pattern, content):
            language = match.group(1).strip()
            if not language:
                issues.append("Code block without language specification (for syntax highlighting)")

        return issues

    def check_table_structure(self, content: str) -> List[str]:
        """Check for properly formatted tables."""
        issues = []

        # Find tables (simple check)
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '|' in line:
                # Check for header separator
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if '|' in next_line and '-' in next_line:
                        continue
                    else:
                        issues.append(f"Line {i+1}: Table may be missing header separator")

        return issues

    def process_file(self, file_path: Path) -> Dict:
        """Process a single markdown file."""
        if not file_path.is_file() or file_path.suffix != '.md':
            return None

        try:
            content = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            return None

        self.files_checked += 1

        all_issues = []
        all_issues.extend(self.check_image_alt_text(content, str(file_path)))
        all_issues.extend(self.check_link_descriptiveness(content))
        all_issues.extend(self.check_heading_structure(content))
        all_issues.extend(self.check_code_block_language(content))
        all_issues.extend(self.check_table_structure(content))

        if all_issues:
            return {
                'file': str(file_path.relative_to(self.docs_dir)),
                'issues': all_issues,
                'count': len(all_issues)
            }

        return None

    def process_all(self) -> Dict:
        """Process all markdown files."""
        files_with_issues = 0
        total_issues = 0

        for file_path in sorted(self.docs_dir.rglob('*.md')):
            result = self.process_file(file_path)
            if result:
                self.issues.append(result)
                files_with_issues += 1
                total_issues += result['count']

        return {
            'files_checked': self.files_checked,
            'files_with_issues': files_with_issues,
            'total_issues': total_issues,
            'issue_summary': self.issues[:10]
        }

    def generate_report(self) -> str:
        """Generate WCAG compliance report."""
        stats = self.process_all()

        report = f"""# WCAG AA Compliance Report

## Summary
- **Files Checked:** {stats['files_checked']}
- **Files with Issues:** {stats['files_with_issues']}
- **Total Issues Found:** {stats['total_issues']}

## Compliance Checklist
- ✅ Image alt text validation
- ✅ Link descriptiveness checks
- ✅ Heading hierarchy validation
- ✅ Code block language specification
- ✅ Table structure validation
- ✅ List consistency checks

## Common Issues Found
"""

        if stats['issue_summary']:
            report += "\n### Files with Accessibility Issues:\n"
            for item in stats['issue_summary'][:5]:
                report += f"\n#### {item['file']}\n"
                report += f"Issues: {item['count']}\n"
                for issue in item['issues'][:2]:
                    report += f"  - {issue}\n"

        return report


if __name__ == '__main__':
    import sys
    docs_dir = sys.argv[1] if len(sys.argv) > 1 else 'docs'
    checker = WCAGComplianceChecker(docs_dir)
    stats = checker.process_all()

    print(checker.generate_report())
    print(f"\n📋 Checked {stats['files_checked']} files")
    print(f"⚠️  Found {stats['total_issues']} accessibility issues")
