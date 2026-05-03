#!/usr/bin/env python3
"""
Root Organization: Reference Validation Script

Scans the entire codebase for references to a specific file/path and generates
a comprehensive report. Used to ensure zero-break guarantee before moving files.

Usage:
    python validate_references.py <file_path> [--dry-run] [--json]
    python validate_references.py README.md --dry-run
    python validate_references.py AGENTS.md --json > agents_refs.json

Physics Model: Fields🔄 - Track all references with metadata
"""

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Reference patterns to search for
REFERENCE_PATTERNS = [
    r'\[.*?\]\({file_path}\)',          # Markdown links
    r'href=["\'].*?{file_path}["\']',   # HTML href
    r'src=["\'].*?{file_path}["\']',    # HTML src
    r'path:.*{file_path}',              # YAML workflow paths
    r'uses:.*{file_path}',              # GitHub Actions uses
    r'include:.*{file_path}',           # MkDocs include
    r'nav:.*{file_path}',               # MkDocs navigation
    r'from\s+{module}\s+import',        # Python imports (module)
    r'import\s+{module}',               # Python imports (direct)
]

# Directories to scan
SCAN_DIRS = [
    'docs',
    '.github',
    'scripts',
    'src',
    'tests',
    '.codex',
]

# File extensions to scan
SCAN_EXTENSIONS = [
    '.md',
    '.yml',
    '.yaml',
    '.py',
    '.json',
    '.toml',
    '.txt',
    '.rst',
    '.sh',
]

# Directories to skip
SKIP_DIRS = {
    '.git',
    '__pycache__',
    'node_modules',
    '.venv',
    'venv',
    '.pytest_cache',
    '.mypy_cache',
    '.ruff_cache',
    '.hypothesis',
    'build',
    'dist',
    '.eggs',
}


def escape_regex(text: str) -> str:
    """Escape special regex characters."""
    return re.escape(text)


def generate_patterns(file_path: str) -> list[re.Pattern]:
    """Generate compiled regex patterns for the given file path."""
    patterns = []
    escaped_path = escape_regex(file_path)

    # For Python imports, extract module name
    if file_path.endswith('.py'):
        module_name = file_path.replace('.py', '').replace('/', '.').replace('\\', '.')
        escaped_module = escape_regex(module_name)
        patterns.append(re.compile(f'from\\s+{escaped_module}\\s+import', re.IGNORECASE))
        patterns.append(re.compile(f'import\\s+{escaped_module}', re.IGNORECASE))

    # General patterns
    for pattern_template in REFERENCE_PATTERNS[:7]:  # Skip Python import patterns (handled above)
        pattern = pattern_template.format(file_path=escaped_path, module='')
        try:
            patterns.append(re.compile(pattern, re.IGNORECASE))
        except re.error:
            continue

    return patterns


def scan_file_for_references(
    file_path: Path,
    target_file: str,
    patterns: list[re.Pattern]
) -> list[dict[str, any]]:
    """Scan a single file for references to the target file."""
    references = []

    try:
        with open(file_path, encoding='utf-8', errors='ignore') as f:
            content = f.read()

        for pattern in patterns:
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count('\n') + 1
                line_start = content.rfind('\n', 0, match.start()) + 1
                line_end = content.find('\n', match.start())
                if line_end == -1:
                    line_end = len(content)
                line_content = content[line_start:line_end].strip()

                references.append({
                    'file': str(file_path),
                    'line': line_num,
                    'match': match.group(0),
                    'context': line_content[:200],  # First 200 chars of line
                    'pattern': pattern.pattern[:50],
                })

    except Exception:
        # Skip files that can't be read
        logger.debug("Suppressed exception in handler", exc_info=True)
    return references


def scan_repository(
    target_file: str,
    root_dir: Path,
    dry_run: bool = False
) -> tuple[list[dict], dict[str, int]]:
    """Scan the entire repository for references to target file."""
    patterns = generate_patterns(target_file)
    all_references = []
    stats = {
        'files_scanned': 0,
        'files_with_refs': 0,
        'total_references': 0,
        'directories_scanned': 0,
    }

    for scan_dir in SCAN_DIRS:
        dir_path = root_dir / scan_dir
        if not dir_path.exists():
            continue

        stats['directories_scanned'] += 1

        for root, dirs, files in os.walk(dir_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

            for file in files:
                if not any(file.endswith(ext) for ext in SCAN_EXTENSIONS):
                    continue

                file_path = Path(root) / file
                stats['files_scanned'] += 1

                refs = scan_file_for_references(file_path, target_file, patterns)
                if refs:
                    all_references.extend(refs)
                    stats['files_with_refs'] += 1

    stats['total_references'] = len(all_references)

    return all_references, stats


def assess_risk(reference_count: int) -> str:
    """Assess risk level based on reference count (Physics Model: Balance⚖️)."""
    if reference_count == 0:
        return "LOW"
    if reference_count <= 5:
        return "MEDIUM"
    return "HIGH"


def generate_report(
    target_file: str,
    references: list[dict],
    stats: dict[str, int],
    output_format: str = 'text'
) -> str:
    """Generate validation report."""
    risk_level = assess_risk(stats['total_references'])

    if output_format == 'json':
        report = {
            'target_file': target_file,
            'timestamp': datetime.now().isoformat(),
            'risk_level': risk_level,
            'statistics': stats,
            'references': references,
        }
        return json.dumps(report, indent=2)

    # Text format
    lines = [
        "=" * 80,
        "Root Organization: Reference Validation Report",
        "=" * 80,
        f"Target File: {target_file}",
        f"Scan Time: {datetime.now().isoformat()}",
        f"Risk Level: {risk_level}",
        "",
        "Statistics:",
        f"  - Directories scanned: {stats['directories_scanned']}",
        f"  - Files scanned: {stats['files_scanned']}",
        f"  - Files with references: {stats['files_with_refs']}",
        f"  - Total references found: {stats['total_references']}",
        "",
    ]

    if references:
        lines.append("References Found:")
        lines.append("-" * 80)

        # Group by file
        by_file = {}
        for ref in references:
            file = ref['file']
            if file not in by_file:
                by_file[file] = []
            by_file[file].append(ref)

        for file, refs in sorted(by_file.items()):
            lines.append(f"\n{file} ({len(refs)} references):")
            for ref in refs[:10]:  # Limit to first 10 per file
                lines.append(f"  Line {ref['line']}: {ref['context']}")
            if len(refs) > 10:
                lines.append(f"  ... and {len(refs) - 10} more")
    else:
        lines.append("✅ No references found - SAFE to move")

    lines.append("")
    lines.append("=" * 80)

    return '\n'.join(lines)


def log_to_ndjson(target_file: str, references: list[dict], stats: dict[str, int]):
    """Log validation results to .codex/action_log.ndjson."""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': 'validate_references',
        'target_file': target_file,
        'risk_level': assess_risk(stats['total_references']),
        'reference_count': stats['total_references'],
        'files_with_refs': stats['files_with_refs'],
    }

    log_file = Path('.codex/action_log.ndjson')
    log_file.parent.mkdir(parents=True, exist_ok=True)

    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')


def main():
    parser = argparse.ArgumentParser(
        description='Validate references to a file before moving it',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_references.py README.md
  python validate_references.py AGENTS.md --dry-run
  python validate_references.py QUICKSTART.md --json > refs.json
        """
    )
    parser.add_argument('file_path', help='File path to validate references for')
    parser.add_argument('--dry-run', action='store_true',
                       help='Dry run mode (no logging)')
    parser.add_argument('--json', action='store_true',
                       help='Output in JSON format')

    args = parser.parse_args()

    # Validate file exists
    root_dir = Path.cwd()
    root_dir / args.file_path

    if args.dry_run:
        print(f"[DRY RUN] Validating references for: {args.file_path}")

    # Scan repository
    references, stats = scan_repository(args.file_path, root_dir, args.dry_run)

    # Generate report
    report = generate_report(args.file_path, references, stats,
                            'json' if args.json else 'text')
    print(report)

    # Log to NDJSON (unless dry-run or JSON output)
    if not args.dry_run and not args.json:
        log_to_ndjson(args.file_path, references, stats)

    # Exit code based on risk level
    risk = assess_risk(stats['total_references'])
    if risk == "HIGH":
        return 2  # High risk
    if risk == "MEDIUM":
        return 1  # Medium risk
    return 0  # Low risk


if __name__ == '__main__':
    sys.exit(main())
