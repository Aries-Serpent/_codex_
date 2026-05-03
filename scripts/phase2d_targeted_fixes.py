#!/usr/bin/env python3
"""
Phase 2D - Targeted Link Fixes
Fix high-priority relocated file references and actual broken links
"""

import logging
import os
import re
from pathlib import Path
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class TargetedLinkFixer:
    """Fix high-priority broken links"""

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.fixes_applied = 0
        self.files_modified = 0

        # Known relocated files with correct paths
        self.relocations = {
            # From Phase 2 relocations
            'CODEBASE_DASHBOARD.md': 'docs/system/CODEBASE_DASHBOARD.md',
            'CODEBASE_COGNITIVE_MAP.md': 'docs/system/CODEBASE_COGNITIVE_MAP.md',
            'CODEBASE_AGENCY_POLICY.md': '.codex/CODEBASE_AGENCY_POLICY.md',
            'ROADMAP.md': 'docs/ROADMAP.md',
            'GENESIS_SETUP_GUIDE.md': 'docs/admin/GENESIS_SETUP_GUIDE.md',
            'OPERATIONAL_GUIDELINES.md': 'docs/agent/OPERATIONAL_GUIDELINES.md',
            'AGENTS.md': '.github/AGENTS.md',
            'ARCHITECTURE.md': 'docs/ARCHITECTURE.md',
            'COGNITIVE_ARCHITECTURE.md': '.github/agents/ARCHITECTURE.md',

            # Common index files
            'docs/README.md': 'docs/README.md',
            'agents/README.md': 'agents/README.md',
            '.github/agents/README.md': '.github/agents/README.md',
        }

    def _calculate_relative_path(self, source_file: Path, target_path: str) -> str:
        """Calculate correct relative path from source to target"""
        source_dir = source_file.parent
        target = self.repo_root / target_path

        try:
            rel_path = os.path.relpath(target, source_dir)
            rel_path = rel_path.replace('\\', '/')
            if not rel_path.startswith('..'):
                rel_path = './' + rel_path
            return rel_path
        except ValueError:
            # Fallback to GitHub URL
            return f"https://github.com/Aries-Serpent/_codex_/blob/main/{target_path}"

    def _fix_link(self, source_file: Path, link_url: str) -> Tuple[str, bool]:
        """Attempt to fix a broken link, return (new_url, was_fixed)"""
        # Check if link references a relocated file
        for filename, correct_path in self.relocations.items():
            if filename in link_url:
                # Extract anchor if present
                anchor = ''
                if '#' in link_url:
                    anchor = '#' + link_url.split('#', 1)[1]

                # Calculate correct relative path
                new_url = self._calculate_relative_path(source_file, correct_path) + anchor
                return new_url, True

        # Check for common broken patterns
        # Pattern: Wrong relative path to docs/
        if link_url.startswith('docs/') and not (self.repo_root / link_url).exists():
            # Try to find correct path
            filename = Path(link_url).name
            for relocation_key, correct_path in self.relocations.items():
                if correct_path.endswith(filename):
                    anchor = '#' + link_url.split('#', 1)[1] if '#' in link_url else ''
                    new_url = self._calculate_relative_path(source_file, correct_path) + anchor
                    return new_url, True

        # Pattern: Wrong relative path to .codex/
        if link_url.startswith('.codex/') and not (source_file.parent / link_url).resolve().exists():
            # Try to fix
            try:
                filename = Path(link_url).name
                for relocation_key, correct_path in self.relocations.items():
                    if correct_path.endswith(filename):
                        anchor = '#' + link_url.split('#', 1)[1] if '#' in link_url else ''
                        new_url = self._calculate_relative_path(source_file, correct_path) + anchor
                        return new_url, True
            except Exception:
                # Best-effort heuristic: if anything goes wrong, leave link unchanged
                logger.debug("Suppressed exception in handler", exc_info=True)
        # Pattern: Wrong relative path to .github/
        if link_url.startswith('.github/') or link_url.startswith('../.github/'):
            link_clean = link_url.replace('../', '').split('#')[0]
            if not (self.repo_root / link_clean).exists():
                filename = Path(link_clean).name
                for relocation_key, correct_path in self.relocations.items():
                    if correct_path.endswith(filename):
                        anchor = '#' + link_url.split('#', 1)[1] if '#' in link_url else ''
                        new_url = self._calculate_relative_path(source_file, correct_path) + anchor
                        return new_url, True

        return link_url, False

    def _should_skip_link(self, link_url: str, link_text: str) -> bool:
        """Determine if a link should be skipped (template, placeholder, etc)"""
        # Skip template placeholders
        placeholder_patterns = [
            r'\{[^}]+\}',  # {variable}
            r'\(.+?\)',     # Regex patterns in links
            r'\[\^',        # Character class patterns
            r'blob:https', # Blob URLs (artifacts from copy-paste)
            r'^path$',      # Generic 'path' placeholder
            r'^link$',      # Generic 'link' placeholder
        ]

        for pattern in placeholder_patterns:
            if re.search(pattern, link_url):
                return True

        # Skip if link text indicates it's an example
        example_indicators = ['example', 'placeholder', 'your-', 'sample']
        return bool(any(indicator in link_text.lower() for indicator in example_indicators))

    def fix_file(self, file_path: Path) -> Dict:
        """Fix broken links in a single file"""
        result = {
            'file': str(file_path.relative_to(self.repo_root)),
            'fixes_applied': 0,
            'fixes': []
        }

        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content

            # Extract all markdown links
            pattern = r'\[([^\]]+)\]\(([^)]+)\)'

            for match in re.finditer(pattern, content):
                full_match = match.group(0)
                link_text = match.group(1)
                link_url = match.group(2)

                # Skip certain links
                if self._should_skip_link(link_url, link_text):
                    continue

                # Skip anchors and external links
                if link_url.startswith('#') or (link_url.startswith('http') and 'github.com/Aries-Serpent/_codex_' not in link_url):
                    continue

                # Try to fix the link
                new_url, was_fixed = self._fix_link(file_path, link_url)

                if was_fixed:
                    new_full_match = f"[{link_text}]({new_url})"
                    content = content.replace(full_match, new_full_match, 1)
                    result['fixes_applied'] += 1
                    result['fixes'].append({
                        'old': full_match,
                        'new': new_full_match
                    })

            # Write back if modified
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                self.files_modified += 1
                self.fixes_applied += result['fixes_applied']

        except Exception as e:
            result['error'] = str(e)

        return result

    def fix_repository(self) -> Dict:
        """Fix broken links across repository"""
        results = []

        priority_dirs = ['docs', '.github', '.codex', 'agents']

        for directory in priority_dirs:
            dir_path = self.repo_root / directory
            if not dir_path.exists():
                continue

            for md_file in dir_path.rglob('*.md'):
                # Skip excluded directories
                if any(excluded in md_file.parts for excluded in ['.git', 'node_modules', '__pycache__']):
                    continue

                # Skip files that are known to have template content
                if any(skip in str(md_file) for skip in ['template', 'example', 'skeleton']):
                    continue

                result = self.fix_file(md_file)

                if result['fixes_applied'] > 0:
                    results.append(result)

        return {
            'files_modified': self.files_modified,
            'fixes_applied': self.fixes_applied,
            'results': results
        }

def main():
    """Main execution"""
    repo_root = os.getcwd()

    print("=" * 80)
    print("Phase 2D: Targeted Link Fixes")
    print("=" * 80)
    print()

    fixer = TargetedLinkFixer(repo_root)

    print("Fixing broken links...")
    output = fixer.fix_repository()

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Files modified: {output['files_modified']}")
    print(f"Total fixes applied: {output['fixes_applied']}")
    print()

    if output['results']:
        print("Files modified:")
        print("-" * 80)
        for result in output['results']:
            print(f"\n{result['file']} - {result['fixes_applied']} fixes")
            for fix in result['fixes'][:5]:  # Show first 5
                print(f"  ✓ {fix['old']}")
                print(f"    → {fix['new']}")
            if len(result['fixes']) > 5:
                print(f"  ... and {len(result['fixes']) - 5} more")

    # Save report
    import json
    output_file = repo_root + '/PHASE_2D_TARGETED_FIXES.json'
    with open(output_file, 'w') as f:
        json.dump(output, indent=2, fp=f)

    print()
    print(f"Full report saved to: {output_file}")
    print()
    print("=" * 80)
    print("Phase 2D: Targeted Fixes COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
