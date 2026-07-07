#!/usr/bin/env python3
"""
Documentation Link Validator
Checks for broken internal links in Tier 1 user-facing documentation.
Can be run locally or in CI/CD pipeline.
"""

import re
import sys
import json
from pathlib import Path
from typing import List, Tuple, Dict

# Tier 1 documentation paths to validate
TIER1_DOCS = [
    'README.md',
    'CONTRIBUTING.md',
    'SECURITY.md',
    'CHANGELOG.md',
    'AGENTS.md',
    'CODE_OF_CONDUCT.md',
    'docs/index.md',
    'docs/README.md',
    'docs/MASTER_INDEX.md',
    'docs/NEWCOMER_GUIDE.md',
]

def find_markdown_files(tier1_only: bool = True) -> List[Path]:
    """Find all markdown files to validate."""
    if tier1_only:
        return [Path(p) for p in TIER1_DOCS if Path(p).exists()]
    return list(Path('.').glob('**/*.md'))

def extract_links(content: str) -> List[Tuple[str, str]]:
    """Extract markdown links from content."""
    # Match [text](url) pattern
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    return re.findall(pattern, content)

def validate_link(link: str) -> Tuple[bool, str]:
    """Validate a single link."""
    # Skip external links
    if link.startswith('http'):
        return True, "external"
    
    # Remove anchor
    file_path = link.split('#')[0]
    
    if not file_path:  # Just an anchor
        return True, "anchor_only"
    
    # Check if file exists
    if Path(file_path).exists():
        return True, "ok"
    
    return False, f"missing_file: {file_path}"

def validate_docs(fail_on_errors: bool = False) -> int:
    """Validate all Tier 1 documentation."""
    broken_count = 0
    
    for doc_path in find_markdown_files(tier1_only=True):
        with open(doc_path) as f:
            content = f.read()
        
        links = extract_links(content)
        
        for text, link in links:
            valid, reason = validate_link(link)
            if not valid:
                broken_count += 1
                print(f"❌ {doc_path}: {link}")
                print(f"   Reason: {reason}")
    
    if broken_count == 0:
        print("✅ All Tier 1 documentation links are valid!")
        return 0
    else:
        print(f"\n⚠️  Found {broken_count} broken links")
        return 1 if fail_on_errors else 0

if __name__ == '__main__':
    fail_on_errors = '--fail-on-errors' in sys.argv
    exit_code = validate_docs(fail_on_errors=fail_on_errors)
    sys.exit(exit_code)
