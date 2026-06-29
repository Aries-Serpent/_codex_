#!/usr/bin/env python3
"""Analyze all Python scripts for token usage patterns (PHASE 4.1)."""

import json
import os
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

def find_all_python_scripts(root: str) -> List[Path]:
    """Find all Python scripts in the repository."""
    scripts = []
    exclude_dirs = {
        '__pycache__', '.git', '.venv', 'venv', 'node_modules',
        '.pytest_cache', '.mypy_cache', 'build', 'dist', 'eggs'
    }
    
    for root_dir, dirs, files in os.walk(root):
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                scripts.append(Path(root_dir) / file)
    
    return sorted(scripts)

def analyze_token_patterns(script_path: Path) -> Dict:
    """Analyze a single script for token usage patterns."""
    try:
        with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return {
            'file': str(script_path),
            'status': 'error',
            'error': str(e),
            'current_pattern': 'error'
        }
    
    lines = content.split('\n')
    
    # Define token patterns to detect
    patterns = {
        'direct_env_vars': r'os\.environ\.get\([\'"]([A-Z_]*TOKEN[A-Z_]*)[\'"]',
        'getenv_calls': r'os\.getenv\([\'"]([A-Z_]*TOKEN[A-Z_]*)[\'"]',
        'inline_fallbacks': r'os\.(environ|getenv).*or\s+(os\.(environ|getenv)|.*TOKEN)',
        'hardcoded_github': r'[\'"]github\.token[\'"]|GITHUB_TOKEN.*=.*github\.token',
        'codex_master_key': r'CODEX_MASTER_KEY|CODEX_BACKUP_KEY',
        'existing_import': r'from scripts\.ci\._token_resolver import',
    }
    
    findings = {
        'file': str(script_path),
        'status': 'analyzed',
        'patterns_found': {},
        'current_pattern': 'none',
        'refactoring_type': 'none',
        'lines_with_patterns': [],
        'needs_token_utility': False,
        'elevation_required': False,
        'lines_changed': 0,
        'effort_estimate': 'none'
    }
    
    # Search for patterns
    for pattern_name, pattern_regex in patterns.items():
        matches = []
        for line_num, line in enumerate(lines, 1):
            if re.search(pattern_regex, line):
                matches.append(line_num)
        
        if matches:
            findings['patterns_found'][pattern_name] = matches
    
    # Determine if already has import
    has_utility_import = 'existing_import' in findings['patterns_found']
    
    # Determine current pattern and refactoring type
    if has_utility_import:
        findings['status'] = 'already_refactored'
        findings['current_pattern'] = 'utility_library'
        findings['refactoring_type'] = 'none'
    elif 'inline_fallbacks' in findings['patterns_found']:
        findings['current_pattern'] = 'inline_fallback_chains'
        findings['refactoring_type'] = 'replace_inline_chains'
        findings['needs_token_utility'] = True
        findings['lines_changed'] = len(findings['patterns_found'].get('inline_fallbacks', []))
        findings['effort_estimate'] = 'low'
    elif 'hardcoded_github' in findings['patterns_found']:
        findings['current_pattern'] = 'hardcoded_github_token'
        findings['refactoring_type'] = 'replace_hardcoded'
        findings['needs_token_utility'] = True
        findings['lines_changed'] = len(findings['patterns_found'].get('hardcoded_github', []))
        findings['effort_estimate'] = 'low'
    elif 'direct_env_vars' in findings['patterns_found'] or 'getenv_calls' in findings['patterns_found']:
        env_matches = findings['patterns_found'].get('direct_env_vars', []) + findings['patterns_found'].get('getenv_calls', [])
        
        # Check if it's elevated operations
        for line_num in env_matches:
            if line_num - 1 < len(lines):
                line = lines[line_num - 1]
                if any(keyword in line for keyword in ['actions', 'workflow', 'security', 'admin', 'org_hook']):
                    findings['elevation_required'] = True
        
        if findings['elevation_required']:
            findings['current_pattern'] = 'direct_env_elevated_ops'
            findings['refactoring_type'] = 'add_utility_elevated'
            findings['effort_estimate'] = 'medium'
        else:
            findings['current_pattern'] = 'direct_env_calls'
            findings['refactoring_type'] = 'add_utility_basic'
            findings['effort_estimate'] = 'low'
        
        findings['needs_token_utility'] = True
        findings['lines_changed'] = len(env_matches)
    
    # Also check for patterns that imply elevated operations
    if not findings['elevation_required']:
        elevated_keywords = ['actions:write', 'workflow', 'security_events', 'admin:', 'org_hook']
        for keyword in elevated_keywords:
            if keyword in content:
                findings['elevation_required'] = True
                break
    
    return findings

def main():
    """Execute Phase 4.1 analysis."""
    repo_root = '/home/runner/work/_codex_/_codex_'
    
    print("🔍 PHASE 4.1: Analyzing Python scripts for token utility refactoring...")
    print(f"Repository root: {repo_root}")
    
    # Find all Python scripts
    print("\n📝 Finding all Python scripts...")
    scripts = find_all_python_scripts(repo_root)
    print(f"Found {len(scripts)} Python scripts")
    
    # Analyze each script
    print("\n🔬 Analyzing token patterns...")
    analysis_results = []
    
    for i, script in enumerate(scripts, 1):
        if i % 100 == 0:
            print(f"  Progress: {i}/{len(scripts)} scripts analyzed")
        
        result = analyze_token_patterns(script)
        analysis_results.append(result)
    
    # Categorize results
    print("\n📊 Categorizing results...")
    categories = defaultdict(list)
    status_counts = defaultdict(int)
    pattern_counts = defaultdict(int)
    refactoring_counts = defaultdict(int)
    
    for result in analysis_results:
        status_counts[result['status']] += 1
        pattern_counts[result['current_pattern']] += 1
        refactoring_counts[result['refactoring_type']] += 1
        categories[result['refactoring_type']].append(result)
    
    # Calculate statistics
    scripts_needing_refactoring = sum(1 for r in analysis_results if r['needs_token_utility'])
    already_refactored = sum(1 for r in analysis_results if r['status'] == 'already_refactored')
    total_lines_changed = sum(r.get('lines_changed', 0) for r in analysis_results)
    
    # Generate summary
    summary = {
        'phase': 'PHASE_4.1',
        'timestamp': '2026-01-24T00:00:00Z',
        'total_scripts': len(scripts),
        'scripts_analyzed': len([r for r in analysis_results if r['status'] != 'error']),
        'scripts_needing_refactoring': scripts_needing_refactoring,
        'already_refactored': already_refactored,
        'scripts_with_errors': status_counts['error'],
        'total_lines_to_change': total_lines_changed,
        'status_breakdown': dict(status_counts),
        'current_pattern_breakdown': dict(pattern_counts),
        'refactoring_type_breakdown': dict(refactoring_counts),
        'scripts_by_refactoring_type': {
            k: len(v) for k, v in categories.items()
        }
    }
    
    # Prepare for output
    print("\n✅ Analysis complete!")
    print(f"\n📈 Summary Statistics:")
    print(f"  Total scripts: {summary['total_scripts']}")
    print(f"  Scripts analyzed: {summary['scripts_analyzed']}")
    print(f"  Scripts needing refactoring: {summary['scripts_needing_refactoring']}")
    print(f"  Already refactored: {summary['already_refactored']}")
    print(f"  Total lines to change: {summary['total_lines_to_change']}")
    
    print(f"\n📋 Refactoring Type Breakdown:")
    for rtype, count in summary['scripts_by_refactoring_type'].items():
        if count > 0:
            print(f"  {rtype}: {count}")
    
    # Return for JSON output
    return {
        'summary': summary,
        'categories': {k: v for k, v in categories.items() if v},
        'detailed_results': analysis_results
    }

if __name__ == '__main__':
    results = main()
    print("\n✅ Analysis complete. Results ready for export.")
