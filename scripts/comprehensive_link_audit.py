#!/usr/bin/env python3
"""
Comprehensive Link Audit - Find ALL broken internal links
Focus on relocated files from Phase 2
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple


class ComprehensiveLinkAuditor:
    """Audit all internal markdown links"""

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.broken_links = []
        self.valid_links = []

        # Known relocated files from Phase 2
        self.relocated_files = {
            'CODEBASE_DASHBOARD.md': 'docs/system/CODEBASE_DASHBOARD.md',
            'CODEBASE_COGNITIVE_MAP.md': 'docs/system/CODEBASE_COGNITIVE_MAP.md',
            'CODEBASE_AGENCY_POLICY.md': '.codex/CODEBASE_AGENCY_POLICY.md',
            'ROADMAP.md': 'docs/ROADMAP.md',
            'GENESIS_SETUP_GUIDE.md': 'docs/admin/GENESIS_SETUP_GUIDE.md',
            'OPERATIONAL_GUIDELINES.md': 'docs/agent/OPERATIONAL_GUIDELINES.md',
        }

    def _is_link_valid(self, source_file: Path, link_url: str) -> Tuple[bool, str]:
        """Check if a link is valid, return (is_valid, reason)"""
        # Skip anchors
        if link_url.startswith('#'):
            return True, "anchor"

        # Skip external links (except GitHub repo)
        if link_url.startswith('http'):
            if 'github.com/Aries-Serpent/_codex_/blob/main/' in link_url:
                # Extract path and verify
                rel_path = link_url.split('/blob/main/')[-1].split('#')[0]
                target = self.repo_root / rel_path
                if target.exists():
                    return True, "github_valid"
                return False, f"github_broken:{rel_path}"
            return True, "external"

        # Handle relative paths
        link_path = link_url.split('#')[0]
        source_dir = source_file.parent

        try:
            target = (source_dir / link_path).resolve()
            # Check if within repo
            target.relative_to(self.repo_root)

            if target.exists():
                return True, "relative_valid"
            return False, f"relative_broken:{link_path}"
        except (ValueError, OSError):
            return False, f"path_error:{link_path}"

    def _extract_links(self, content: str) -> List[Tuple[str, str, str]]:
        """Extract markdown links"""
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = []
        for match in re.finditer(pattern, content):
            full_match = match.group(0)
            link_text = match.group(1)
            link_url = match.group(2)
            links.append((full_match, link_text, link_url))
        return links

    def audit_file(self, file_path: Path) -> Dict:
        """Audit a single markdown file"""
        result = {
            'file': str(file_path.relative_to(self.repo_root)),
            'total_links': 0,
            'broken_links': [],
            'valid_links': 0
        }

        try:
            content = file_path.read_text(encoding='utf-8')
            links = self._extract_links(content)
            result['total_links'] = len(links)

            for full_match, link_text, link_url in links:
                is_valid, reason = self._is_link_valid(file_path, link_url)

                if not is_valid:
                    result['broken_links'].append({
                        'text': link_text,
                        'url': link_url,
                        'full': full_match,
                        'reason': reason
                    })
                else:
                    result['valid_links'] += 1

        except Exception as e:
            result['error'] = str(e)

        return result

    def audit_repository(self, directories: List[str] = None) -> Dict:
        """Audit all markdown files"""
        if directories is None:
            directories = ['docs', '.github', '.codex', 'agents']

        results = []
        total_broken = 0
        total_valid = 0

        for directory in directories:
            dir_path = self.repo_root / directory
            if not dir_path.exists():
                continue

            for md_file in dir_path.rglob('*.md'):
                # Skip excluded directories
                if any(excluded in md_file.parts for excluded in ['.git', 'node_modules', '__pycache__']):
                    continue

                result = self.audit_file(md_file)

                if result['broken_links']:
                    results.append(result)
                    total_broken += len(result['broken_links'])

                total_valid += result['valid_links']

        return {
            'total_broken': total_broken,
            'total_valid': total_valid,
            'files_with_broken_links': len(results),
            'results': sorted(results, key=lambda x: len(x['broken_links']), reverse=True)
        }

def main():
    """Main execution"""
    repo_root = os.getcwd()

    print("=" * 80)
    print("Comprehensive Link Audit")
    print("=" * 80)
    print()

    auditor = ComprehensiveLinkAuditor(repo_root)

    print("Auditing markdown files...")
    output = auditor.audit_repository()

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total broken links: {output['total_broken']}")
    print(f"Total valid links: {output['total_valid']}")
    print(f"Files with broken links: {output['files_with_broken_links']}")
    print()

    # Show top files with most broken links
    print("Top 20 files with broken links:")
    print("-" * 80)
    for i, result in enumerate(output['results'][:20], 1):
        print(f"{i}. {result['file']} - {len(result['broken_links'])} broken links")
        for broken in result['broken_links'][:3]:
            print(f"   • [{broken['text']}]({broken['url']})")
            print(f"     Reason: {broken['reason']}")
        if len(result['broken_links']) > 3:
            print(f"   ... and {len(result['broken_links']) - 3} more")
        print()

    # Save full report
    import json
    output_file = repo_root + '/COMPREHENSIVE_LINK_AUDIT.json'
    with open(output_file, 'w') as f:
        json.dump(output, indent=2, fp=f)

    print(f"Full report saved to: {output_file}")
    print()

if __name__ == '__main__':
    main()
