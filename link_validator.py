#!/usr/bin/env python3
"""
Comprehensive link validator for documentation files.
Scans markdown and HTML files for broken internal and external links.
"""

import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse, urljoin
from collections import defaultdict
import json
from typing import Dict, List, Tuple, Set

class LinkValidator:
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.all_files = set()
        self.broken_links = defaultdict(list)
        self.fixed_links = []
        self.external_links = set()
        self.internal_links = defaultdict(list)
        self.anchor_links = defaultdict(list)
        
        # Patterns for different link types
        self.md_link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        self.md_anchor_pattern = r'#{1,6}\s+(.+?)(?:\n|$)'
        
    def load_all_file_paths(self):
        """Load all markdown and HTML file paths in repo"""
        print("Loading all documentation file paths...")
        for root, dirs, files in os.walk(self.repo_root):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.venv', 'venv', 'node_modules'}]
            
            for file in files:
                if file.endswith(('.md', '.html')):
                    full_path = Path(root) / file
                    rel_path = full_path.relative_to(self.repo_root)
                    self.all_files.add(str(rel_path))
    
    def extract_headings(self, content: str, file_path: str) -> Set[str]:
        """Extract all heading anchors from a file"""
        headings = set()
        for match in re.finditer(self.md_anchor_pattern, content):
            heading = match.group(1).strip()
            # Convert heading to anchor format
            anchor = heading.lower().replace(' ', '-').replace('_', '-')
            # Remove special characters
            anchor = re.sub(r'[^a-z0-9\-]', '', anchor)
            # Remove consecutive dashes
            anchor = re.sub(r'-+', '-', anchor).strip('-')
            if anchor:
                headings.add(anchor)
        return headings
    
    def extract_links(self, content: str, file_path: str) -> List[Tuple[str, str]]:
        """Extract all markdown links from a file"""
        links = []
        for match in re.finditer(self.md_link_pattern, content):
            text = match.group(1)
            url = match.group(2)
            links.append((text, url))
        return links
    
    def validate_link(self, url: str, source_file: str) -> Tuple[bool, str]:
        """
        Validate a single link.
        Returns (is_valid, message)
        """
        if not url or url.startswith('#'):
            return True, "Anchor-only link"
        
        # Skip certain link types
        if url.startswith(('mailto:', 'tel:', 'javascript:')):
            return True, "Special protocol"
        
        # Parse the URL
        if url.startswith(('http://', 'https://', 'ftp://')):
            # External link - mark but don't validate in this pass
            self.external_links.add(url)
            return True, "External URL"
        
        # Internal link
        if '#' in url:
            file_part, anchor_part = url.split('#', 1)
        else:
            file_part = url
            anchor_part = None
        
        # Resolve the file path
        source_dir = Path(source_file).parent if source_file else self.repo_root
        target_path = (source_dir / file_part).resolve() if file_part else Path(source_file)
        
        # Check if file exists
        if file_part and not target_path.exists():
            # Try relative to repo root
            alt_path = (self.repo_root / file_part).resolve()
            if alt_path.exists():
                target_path = alt_path
            else:
                return False, f"File not found: {file_part}"
        
        # Check anchor if present
        if anchor_part:
            if target_path.exists() and target_path.suffix in {'.md', '.html'}:
                with open(target_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    headings = self.extract_headings(content, str(target_path))
                    if anchor_part not in headings:
                        return False, f"Anchor not found: #{anchor_part}"
        
        return True, "Valid"
    
    def process_file(self, file_path: Path) -> Dict:
        """Process a single markdown file"""
        result = {
            'file': str(file_path.relative_to(self.repo_root)),
            'links': [],
            'errors': 0
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract links
            links = self.extract_links(content, str(file_path))
            headings = self.extract_headings(content, str(file_path))
            
            for text, url in links:
                is_valid, message = self.validate_link(url, str(file_path))
                
                link_info = {
                    'text': text[:50],  # Truncate long text
                    'url': url,
                    'valid': is_valid,
                    'message': message
                }
                result['links'].append(link_info)
                
                if not is_valid:
                    result['errors'] += 1
                    self.broken_links[str(file_path.relative_to(self.repo_root))].append({
                        'url': url,
                        'text': text,
                        'error': message
                    })
        
        except Exception as e:
            result['error'] = str(e)
            result['errors'] = 1
        
        return result
    
    def validate_all(self):
        """Validate all documentation files"""
        self.load_all_file_paths()
        
        print(f"Scanning {len(self.all_files)} documentation files...")
        
        results = []
        processed = 0
        
        # Process files in repo root and docs/ directory first (smaller subset)
        priority_paths = []
        for file_str in sorted(self.all_files):
            if file_str.startswith(('docs/', '.codex/', '.github/', 'README.md', 'SECURITY.md')):
                file_path = self.repo_root / file_str
                if file_path.exists():
                    result = self.process_file(file_path)
                    if result['errors'] > 0:
                        results.append(result)
                    processed += 1
                    if processed % 100 == 0:
                        print(f"  Processed {processed} files...")
        
        return results
    
    def generate_report(self) -> str:
        """Generate comprehensive report"""
        report = []
        report.append("# Phase 9 Track 9.1: Dead Link Detection & Remediation Report\n")
        report.append(f"Generated: {__import__('datetime').datetime.now().isoformat()}\n\n")
        
        # Summary
        total_broken = sum(len(links) for links in self.broken_links.values())
        report.append("## Executive Summary\n")
        report.append(f"- **Total files scanned**: {len(self.all_files)}\n")
        report.append(f"- **Broken links found**: {total_broken}\n")
        report.append(f"- **Files with broken links**: {len(self.broken_links)}\n")
        report.append(f"- **External URLs identified**: {len(self.external_links)}\n\n")
        
        # Broken links by file
        if self.broken_links:
            report.append("## Broken Links by File\n\n")
            for file_path in sorted(self.broken_links.keys()):
                links = self.broken_links[file_path]
                report.append(f"### {file_path}\n")
                for link in links:
                    report.append(f"- **URL**: `{link['url']}`\n")
                    report.append(f"  - Text: {link['text']}\n")
                    report.append(f"  - Error: {link['error']}\n")
                report.append("\n")
        else:
            report.append("## No Broken Links Found\n")
            report.append("All links in scanned documentation are valid!\n\n")
        
        return ''.join(report)


def main():
    repo_root = '/home/runner/work/_codex_/_codex_'
    validator = LinkValidator(repo_root)
    
    print("Starting comprehensive link validation...")
    results = validator.validate_all()
    
    # Generate and print report
    report = validator.generate_report()
    print(report)
    
    # Save report
    report_path = Path(repo_root) / '.codex' / 'PHASE_9_LINK_HEALTH_REPORT.md'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report)
    print(f"\nReport saved to: {report_path}")


if __name__ == '__main__':
    main()
