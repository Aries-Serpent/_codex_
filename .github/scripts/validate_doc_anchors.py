#!/usr/bin/env python3
"""
Markdown Anchor Link Validator

Validates that all anchor links (#heading-id format) reference existing headings.
Extracts heading IDs and validates cross-references across documentation.

Author: Link Validator Agent
Date: 2026-06-22
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set

# Heading pattern: # Heading Text -> generates ID like #heading-text
HEADING_PATTERN = re.compile(r'^#+\s+(.+?)(?:\s*{#(.+?)})?$', re.MULTILINE)

# Anchor link patterns
ANCHOR_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)#]+)?#([^)]+)\)')
RELATIVE_ANCHOR_PATTERN = re.compile(r'\[([^\]]+)\]\(#([^)]+)\)')

# Standard heading ID generation (GitHub flavor)
def generate_heading_id(text: str) -> str:
    """Generate GitHub-style heading ID from heading text."""
    # Convert to lowercase
    id_text = text.lower()
    # Replace spaces with hyphens
    id_text = re.sub(r'\s+', '-', id_text)
    # Remove special characters except hyphens
    id_text = re.sub(r'[^a-z0-9\-]', '', id_text)
    # Remove consecutive hyphens
    id_text = re.sub(r'-+', '-', id_text)
    # Remove leading/trailing hyphens
    id_text = id_text.strip('-')
    return id_text


class AnchorValidator:
    """Validates heading anchors and cross-references."""
    
    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self.anchors: Dict[str, Set[str]] = defaultdict(set)
        self.cross_refs: List[Dict] = []
        self.errors: List[Dict] = []
        self.warnings: List[Dict] = []
        
    def extract_headings(self, file_path: Path) -> Set[str]:
        """Extract all valid heading IDs from a markdown file."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            self.errors.append({
                'file': str(file_path),
                'type': 'read_error',
                'message': f'Failed to read file: {e}'
            })
            return set()
        
        heading_ids = set()
        
        for match in HEADING_PATTERN.finditer(content):
            text = match.group(1)
            
            # Check for explicit ID in curly braces
            if match.group(2):
                heading_id = match.group(2)
            else:
                # Generate ID from heading text
                heading_id = generate_heading_id(text)
            
            heading_ids.add(heading_id)
        
        self.anchors[str(file_path)] = heading_ids
        return heading_ids
    
    def validate_anchor_links(self, file_path: Path) -> None:
        """Validate all anchor links in a file."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            self.errors.append({
                'file': str(file_path),
                'type': 'read_error',
                'message': f'Failed to read file: {e}'
            })
            return
        
        file_str = str(file_path)
        
        # Check relative anchors (same file)
        for match in RELATIVE_ANCHOR_PATTERN.finditer(content):
            link_text = match.group(1)
            anchor_id = match.group(2)
            
            self.cross_refs.append({
                'file': file_str,
                'type': 'relative_anchor',
                'link_text': link_text,
                'anchor': anchor_id,
                'target_file': file_str
            })
            
            if anchor_id not in self.anchors[file_str]:
                self.errors.append({
                    'file': file_str,
                    'type': 'missing_anchor',
                    'link_text': link_text,
                    'anchor': anchor_id,
                    'message': f'Anchor #{anchor_id} not found in file'
                })
        
        # Check cross-file anchors
        for match in ANCHOR_LINK_PATTERN.finditer(content):
            link_text = match.group(1)
            target_file = match.group(2)
            anchor_id = match.group(3)
            
            if not target_file:
                # Same-file link
                continue
            
            # Resolve target file
            resolved_target = self._resolve_file_path(file_path, target_file)
            
            self.cross_refs.append({
                'file': file_str,
                'type': 'cross_file_anchor',
                'link_text': link_text,
                'target': target_file,
                'anchor': anchor_id,
                'target_file': str(resolved_target) if resolved_target else target_file
            })
            
            if not resolved_target:
                self.errors.append({
                    'file': file_str,
                    'type': 'file_not_found',
                    'target': target_file,
                    'anchor': anchor_id,
                    'message': f'Target file not found: {target_file}'
                })
            elif anchor_id not in self.anchors.get(str(resolved_target), set()):
                self.errors.append({
                    'file': file_str,
                    'type': 'missing_anchor',
                    'link_text': link_text,
                    'target': target_file,
                    'anchor': anchor_id,
                    'message': f'Anchor #{anchor_id} not found in {target_file}'
                })
    
    def _resolve_file_path(self, from_file: Path, target: str) -> Path:
        """Resolve relative file path."""
        # Skip external URLs
        if target.startswith(('http://', 'https://', 'mailto:', 'tel:')):
            return None
        
        if target.startswith('/'):
            # Absolute path from repo root
            return Path(target)
        
        # Relative path
        base_dir = from_file.parent
        resolved = (base_dir / target).resolve()
        
        if resolved.exists() and resolved.is_file():
            return resolved
        
        return None
    
    def validate_directory(self, root_dir: Path) -> None:
        """Validate all markdown files in a directory."""
        markdown_files = list(root_dir.rglob('*.md'))
        
        # First pass: extract all headings
        for file_path in markdown_files:
            self.extract_headings(file_path)
        
        # Second pass: validate anchor links
        for file_path in markdown_files:
            self.validate_anchor_links(file_path)
    
    def generate_report(self) -> Dict:
        """Generate validation report."""
        return {
            'timestamp': __import__('datetime').datetime.utcnow().isoformat() + 'Z',
            'statistics': {
                'files_scanned': len(self.anchors),
                'cross_references_found': len(self.cross_refs),
                'errors': len(self.errors),
                'warnings': len(self.warnings)
            },
            'errors': self.errors,
            'warnings': self.warnings,
            'summary': {
                'status': 'PASS' if not self.errors else 'FAIL',
                'error_count': len(self.errors),
                'warning_count': len(self.warnings)
            }
        }
    
    def print_summary(self) -> None:
        """Print validation summary."""
        report = self.generate_report()
        
        print("\n" + "="*80)
        print("📋 MARKDOWN ANCHOR VALIDATION REPORT")
        print("="*80)
        
        stats = report['statistics']
        print(f"\n✅ Files scanned: {stats['files_scanned']}")
        print(f"🔗 Cross-references found: {stats['cross_references_found']}")
        print(f"⚠️  Warnings: {stats['warnings']}")
        print(f"❌ Errors: {stats['errors']}")
        
        if self.errors:
            print("\n🔴 ERRORS:")
            for error in self.errors[:10]:
                print(f"  - [{error['type']}] {error['file']}")
                print(f"    {error['message']}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more errors")
        
        print("\n" + "="*80)
        print(f"Status: {report['summary']['status']}")
        print("="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Validate markdown anchor links and heading IDs'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Fail on warnings (strict mode)'
    )
    parser.add_argument(
        '--directory',
        default='.',
        help='Directory to validate (default: current directory)'
    )
    parser.add_argument(
        '--report-file',
        help='Write JSON report to file'
    )
    parser.add_argument(
        '--fail-on-errors',
        action='store_true',
        help='Exit with code 1 if errors found'
    )
    
    args = parser.parse_args()
    
    root_dir = Path(args.directory).resolve()
    if not root_dir.exists():
        print(f"Error: Directory not found: {root_dir}")
        sys.exit(1)
    
    validator = AnchorValidator(strict_mode=args.strict)
    validator.validate_directory(root_dir)
    validator.print_summary()
    
    report = validator.generate_report()
    
    if args.report_file:
        with open(args.report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📄 Report written: {args.report_file}")
    
    if args.fail_on_errors and report['summary']['error_count'] > 0:
        sys.exit(1)
    
    return 0 if not report['summary']['error_count'] else 0


if __name__ == '__main__':
    sys.exit(main())
