#!/usr/bin/env python3
"""Fix all corrupted YAML workflow files"""
import re
import yaml
from pathlib import Path
import subprocess
import sys

def fix_yaml_indentation(filepath):
    """Fix YAML indentation issues"""
    content = Path(filepath).read_text()
    original = content
    
    # Problem 1: "      env:" appearing at wrong indentation after "id: "
    pattern1 = r'(\n        id: \w+)\n      env:'
    content = re.sub(pattern1, r'\1\n        env:', content)
    
    # Problem 2: "      run:" appearing at wrong indentation
    pattern2 = r'(\n        \w+: .+)\n      run:'
    content = re.sub(pattern2, r'\1\n        run:', content)
    
    # Problem 3: with: or env: followed by non-indented fields
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        fixed_lines.append(line)
        
        # If this line ends with "with:" or "env:" 
        if re.search(r'^\s+(with|env):\s*$', line):
            # Get the indent level
            indent = len(line) - len(line.lstrip())
            expected_child_indent = indent + 2
            
            # Look ahead and fix following lines until we hit a different level
            i += 1
            while i < len(lines):
                next_line = lines[i]
                
                # Skip empty lines
                if not next_line.strip():
                    fixed_lines.append(next_line)
                    i += 1
                    continue
                
                # Check indentation
                next_indent = len(next_line) - len(next_line.lstrip())
                
                # If this is a child (at indent+2), keep it
                if next_indent == expected_child_indent:
                    fixed_lines.append(next_line)
                    i += 1
                    continue
                
                # If this is a sibling or parent, stop
                if next_indent <= indent:
                    break
                
                # If this is at wrong indentation (indent instead of indent+2), fix it
                if next_indent == indent:
                    # Add 2 spaces
                    fixed_lines.append('  ' + next_line)
                    i += 1
                    continue
                
                # Otherwise just add it
                fixed_lines.append(next_line)
                i += 1
        else:
            i += 1
    
    content = '\n'.join(fixed_lines)
    
    # Validate the result
    try:
        yaml.safe_load(content)
        if content != original:
            Path(filepath).write_text(content)
            return True, "Fixed and validated"
        else:
            return False, "No changes needed"
    except yaml.YAMLError as e:
        return False, f"YAML validation failed: {str(e)[:100]}"

def main():
    files_to_fix = [
        '.github/workflows/correlation-engine-monitor.yml',
        '.github/workflows/ensemble-predictor-monitor.yml',
        '.github/workflows/docker-build-push.yml',
        '.github/workflows/adaptive-agent-delegation.yml',
        '.github/workflows/health-dashboard-update.yml',
        '.github/workflows/admin-action-notifier.yml',
        '.github/workflows/progressive-validation.yml',
        '.github/workflows/security-scan-phase-16.yml',
        '.github/workflows/data-quality-suite.yml',
        '.github/workflows/batch-ci-triage.yml',
        '.github/workflows/rust_swarm_ci.yml',
        '.github/workflows/release-to-pypi.yml',
        '.github/workflows/copilot-session-chain.yml',
        '.github/workflows/workflow-execution-gate.yml',
    ]
    
    fixed_count = 0
    failed_count = 0
    
    for filepath in files_to_fix:
        success, msg = fix_yaml_indentation(filepath)
        if success:
            print(f"✓ {Path(filepath).name}: {msg}")
            fixed_count += 1
        else:
            print(f"✗ {Path(filepath).name}: {msg}")
            failed_count += 1
    
    print(f"\nSummary: {fixed_count} fixed, {failed_count} failed")
    return 0 if failed_count == 0 else 1

if __name__ == '__main__':
    sys.exit(main())

