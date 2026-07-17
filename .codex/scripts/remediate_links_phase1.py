#!/usr/bin/env python3
"""
Automated Link Fix Script for GitHub Pages v0.2.0
Applies high-confidence fixes to broken documentation links.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

class LinkRemediator:
    """Automatically fix broken documentation links."""
    
    def __init__(self, repo_root: Path = Path.cwd()):
        self.repo_root = repo_root
        self.docs_root = repo_root / "docs"
        self.fixed_count = 0
        self.skipped_count = 0
        self.fixes_log = []
    
    def create_stub_files(self, targets: List[str]) -> int:
        """Create stub files for referenced but missing targets."""
        created = 0
        stub_template = """# {title}

> **Status**: Stub file - To be populated

## Overview
This documentation file is referenced in the knowledge base but content is pending.

## References
- See related documentation for context
- To contribute content to this file, submit a pull request

## TODOs
- [ ] Add introductory content
- [ ] Add usage examples
- [ ] Add cross-references
- [ ] Link to related topics

---
**Created**: {date}  
**Status**: Draft - Awaiting content population
"""
        
        for target_path in targets:
            file_path = self.repo_root / target_path
            if not file_path.exists():
                try:
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    title = target_path.split('/')[-1].replace('.md', '').replace('_', ' ')
                    content = stub_template.format(
                        title=title,
                        date='2026-07-17'
                    )
                    file_path.write_text(content)
                    self.fixes_log.append(f"✓ Created stub: {target_path}")
                    created += 1
                except Exception as e:
                    self.fixes_log.append(f"✗ Failed to create {target_path}: {e}")
        
        return created
    
    def fix_relative_paths(self, md_file: Path, fixes: List[Tuple[str, str]]) -> bool:
        """Apply relative path fixes to a markdown file."""
        try:
            content = md_file.read_text(encoding='utf-8')
            original_content = content
            
            for old_pattern, new_pattern in fixes:
                # Use word boundaries to avoid partial replacements
                pattern = re.compile(re.escape(old_pattern) + r'(?=[\)\]`])')
                content = pattern.sub(new_pattern, content)
            
            if content != original_content:
                md_file.write_text(content, encoding='utf-8')
                self.fixes_log.append(f"✓ Fixed paths in: {md_file.relative_to(self.repo_root)}")
                self.fixed_count += 1
                return True
            else:
                self.skipped_count += 1
                return False
        except Exception as e:
            self.fixes_log.append(f"✗ Error fixing {md_file}: {e}")
            return False
    
    def remove_placeholder_links(self, md_file: Path) -> bool:
        """Remove placeholder and template links from documentation."""
        try:
            content = md_file.read_text(encoding='utf-8')
            original_content = content
            
            # Pattern 1: [text](./file.md) - placeholder template
            content = re.sub(
                r'\[([^\]]+)\]\(\./file\.md(?:#anchor)?\)',
                r'<!-- TODO: Add real link: \1 -->',
                content
            )
            
            # Pattern 2: [text](../new/path.md) - example path
            content = re.sub(
                r'\[([^\]]+)\]\(\.\./new/path\.md\)',
                r'<!-- TODO: Update link: \1 -->',
                content
            )
            
            # Pattern 3: [text](url) where url is a placeholder
            content = re.sub(
                r'\[text\]\(([^)]*example|test|todo|placeholder)[^)]*\)',
                r'<!-- TODO: Replace placeholder link -->',
                content,
                flags=re.IGNORECASE
            )
            
            if content != original_content:
                md_file.write_text(content, encoding='utf-8')
                self.fixes_log.append(f"✓ Removed placeholders from: {md_file.relative_to(self.repo_root)}")
                self.fixed_count += 1
                return True
            else:
                self.skipped_count += 1
                return False
        except Exception as e:
            self.fixes_log.append(f"✗ Error removing placeholders from {md_file}: {e}")
            return False
    
    def fix_github_url_references(self, md_file: Path) -> bool:
        """Convert root-level references to GitHub URLs."""
        try:
            content = md_file.read_text(encoding='utf-8')
            original_content = content
            
            # Root-level file references
            replacements = {
                r'\]\(\.\./(pyproject\.toml)\)': r'](https://github.com/Aries-Serpent/_codex_/blob/main/\1)',
                r'\]\(\.\./(README\.md)\)': r'](https://github.com/Aries-Serpent/_codex_/blob/main/\1)',
                r'\]\(\.\./(LICENSE)\)': r'](https://github.com/Aries-Serpent/_codex_/blob/main/\1)',
                r'\]\(\.\./src/([^)]+)\)': r'](https://github.com/Aries-Serpent/_codex_/blob/main/src/\1)',
                r'\]\(\.\./tests/([^)]+)\)': r'](https://github.com/Aries-Serpent/_codex_/blob/main/tests/\1)',
            }
            
            for pattern, replacement in replacements.items():
                content = re.sub(pattern, replacement, content)
            
            if content != original_content:
                md_file.write_text(content, encoding='utf-8')
                self.fixes_log.append(f"✓ Converted GitHub URLs in: {md_file.relative_to(self.repo_root)}")
                self.fixed_count += 1
                return True
            else:
                self.skipped_count += 1
                return False
        except Exception as e:
            self.fixes_log.append(f"✗ Error updating GitHub URLs in {md_file}: {e}")
            return False
    
    def execute_remediation_plan(self) -> Dict:
        """Execute the full remediation plan."""
        
        print("=" * 80)
        print("LINK REMEDIATION EXECUTION - Phase 1 (Quick Wins)")
        print("=" * 80)
        
        # Step 1: Create stub files
        print("\n[1/4] Creating stub files for high-priority missing targets...")
        stub_targets = [
            'docs/CODE_OF_CONDUCT.md',
            'docs/cognitive_brain/index.md',
            'docs/architecture.md',
            'docs/agents/ORCHESTRATION.md',
            'docs/rag/RAG_QUICKSTART.md',
            'docs/rag/RAG_API_REFERENCE.md',
            'docs/integration/webhook_guide.md',
            'docs/authentication/auth_guide.md',
            'docs/api/INDEX.md',
            'docs/evaluation/index.md',
        ]
        
        stubs_created = self.create_stub_files(stub_targets)
        print(f"  ✓ Created {stubs_created} stub files")
        
        # Step 2: Remove placeholder content
        print("\n[2/4] Removing placeholder and template content...")
        placeholder_files = [
            'docs/CONSISTENCY_CHECKS_SETUP.md',
            'docs/DOC_OPERATIONAL_RUNBOOK.md',
            'docs/templates/README.md',
        ]
        
        placeholders_fixed = 0
        for file_path_str in placeholder_files:
            file_path = self.repo_root / file_path_str
            if file_path.exists():
                if self.remove_placeholder_links(file_path):
                    placeholders_fixed += 1
        print(f"  ✓ Cleaned {placeholders_fixed} files with placeholder content")
        
        # Step 3: Fix relative paths in critical hub files
        print("\n[3/4] Correcting relative paths in critical hub files...")
        hub_fixes = {
            'docs/DOCUMENTATION_INDEX.md': [
                ('../docs/', 'docs/'),  # Fix docs references from outside docs/
                ('docs/agents/', 'agents/'),  # Agent docs relative path
            ],
            'docs/DOC_CROSSREFERENCE_MAP.md': [
                ('integration/webhook_guide.md', 'integration/webhook_guide.md'),  # Already exists in stub
            ],
        }
        
        hub_fixed = 0
        for file_path_str, fixes in hub_fixes.items():
            file_path = self.repo_root / file_path_str
            if file_path.exists():
                if self.fix_relative_paths(file_path, fixes):
                    hub_fixed += 1
        print(f"  ✓ Fixed paths in {hub_fixed} hub files")
        
        # Step 4: Convert GitHub URL references
        print("\n[4/4] Converting root-level references to GitHub URLs...")
        github_url_files = list(self.docs_root.rglob('*.md'))[:10]  # Sample
        
        github_urls_fixed = 0
        for file_path in github_url_files:
            if self.fix_github_url_references(file_path):
                github_urls_fixed += 1
        print(f"  ✓ Updated {github_urls_fixed} files with GitHub URLs")
        
        # Summary
        print("\n" + "=" * 80)
        print("REMEDIATION SUMMARY")
        print("=" * 80)
        print(f"✓ Stub files created: {stubs_created}")
        print(f"✓ Placeholder content removed: {placeholders_fixed}")
        print(f"✓ Hub files corrected: {hub_fixed}")
        print(f"✓ GitHub URL references updated: {github_urls_fixed}")
        print(f"✓ Total files modified: {self.fixed_count}")
        print(f"ℹ Files skipped (no changes): {self.skipped_count}")
        
        return {
            'stubs_created': stubs_created,
            'placeholders_removed': placeholders_fixed,
            'hub_files_fixed': hub_fixed,
            'github_urls_updated': github_urls_fixed,
            'total_fixed': self.fixed_count,
            'skipped': self.skipped_count,
            'log': self.fixes_log
        }

def main():
    """Main execution."""
    repo_root = Path('/home/runner/work/_codex_/_codex_')
    remediator = LinkRemediator(repo_root)
    
    # Execute remediation
    results = remediator.execute_remediation_plan()
    
    # Save results
    results_file = repo_root / '.codex' / 'reports' / 'REMEDIATION_PHASE1_RESULTS.json'
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Results saved to: {results_file}")
    print("\n💡 Next: Run `python scripts/analyze_broken_links.py` to verify improvements")

if __name__ == '__main__':
    main()
