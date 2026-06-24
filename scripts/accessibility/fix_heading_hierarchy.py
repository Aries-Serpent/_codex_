#!/usr/bin/env python3
"""
Fix heading hierarchy issues in markdown files.

Ensures proper heading progression (H1 -> H2 -> H3, no skips)
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple


class HeadingHierarchyFixer:
    """Fix improper heading levels in markdown files."""

    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        self.issues_found: List[Dict] = []
        self.files_fixed: int = 0

    def find_heading_issues(self, content: str, file_path: str) -> List[Tuple[int, str, int]]:
        """Find heading hierarchy issues."""
        issues = []
        lines = content.split('\n')
        previous_level = 0

        for i, line in enumerate(lines, 1):
            match = re.match(r'^(#+)\s+', line)
            if not match:
                continue

            level = len(match.group(1))

            # Check for improper jumps (e.g., H1 to H3)
            if previous_level > 0:
                jump = level - previous_level
                if jump > 1:
                    issues.append((i, line.strip(), level))

            previous_level = level

        return issues

    def fix_heading_hierarchy(self, content: str) -> str:
        """Fix heading hierarchy issues."""
        lines = content.split('\n')
        fixed_lines = []
        previous_level = 0
        level_map = {}  # Map of old level to new level

        for line in lines:
            match = re.match(r'^(#+)\s+', line)
            if not match:
                fixed_lines.append(line)
                continue

            old_level = len(match.group(1))
            title = line[old_level:].strip()

            if previous_level == 0:
                # First heading should be H1
                new_level = 1
            else:
                # Calculate proper level
                if old_level > previous_level:
                    new_level = previous_level + 1
                else:
                    new_level = old_level

            level_map[old_level] = new_level
            new_heading = '#' * new_level + ' ' + title
            fixed_lines.append(new_heading)
            previous_level = new_level

        return '\n'.join(fixed_lines)

    def process_file(self, file_path: Path) -> bool:
        """Process a single markdown file."""
        if not file_path.is_file() or file_path.suffix != '.md':
            return False

        try:
            content = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            return False

        issues = self.find_heading_issues(content, str(file_path))

        if not issues:
            return False

        # Fix and save
        fixed_content = self.fix_heading_hierarchy(content)
        try:
            file_path.write_text(fixed_content, encoding='utf-8')
            self.files_fixed += 1
            self.issues_found.append({
                'file': str(file_path.relative_to(self.docs_dir)),
                'issues_count': len(issues),
                'issues': issues
            })
            return True
        except OSError:
            return False

    def process_all(self) -> Dict:
        """Process all markdown files."""
        for file_path in self.docs_dir.rglob('*.md'):
            self.process_file(file_path)

        return {
            'files_fixed': self.files_fixed,
            'total_issues': sum(item['issues_count'] for item in self.issues_found),
            'issues_by_file': self.issues_found
        }

    def generate_report(self) -> str:
        """Generate heading hierarchy report."""
        stats = self.process_all()

        report = f"""# Heading Hierarchy Consistency Report

## Summary
- **Files with Issues:** {stats['files_fixed']}
- **Total Issues Fixed:** {stats['total_issues']}

## Details
"""
        for item in stats['issues_by_file']:
            report += f"\n### {item['file']}\n"
            report += f"Issues fixed: {item['issues_count']}\n"
            for line_num, heading, level in item['issues'][:3]:
                report += f"  - Line {line_num}: H{level} - {heading[:50]}\n"
            if len(item['issues']) > 3:
                report += f"  - ... and {len(item['issues']) - 3} more\n"

        return report


if __name__ == '__main__':
    import sys
    docs_dir = sys.argv[1] if len(sys.argv) > 1 else 'docs'
    fixer = HeadingHierarchyFixer(docs_dir)
    stats = fixer.process_all()

    print(fixer.generate_report())
    print(f"\n✅ Fixed {stats['files_fixed']} files with {stats['total_issues']} heading issues")
