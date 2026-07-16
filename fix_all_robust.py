#!/usr/bin/env python3
"""Robust YAML fixer for all corrupted workflow files"""
import re
from pathlib import Path
import yaml
import sys

def smartly_fix_yaml(content):
    """Smartly fix YAML content"""
    lines = content.split('\n')
    output = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Pattern 1: Fix "        with:" followed by non-indented children
        if re.match(r'^(\s+)(with|env):\s*$', line):
            indent_match = re.match(r'^(\s+)', line)
            parent_indent = len(indent_match.group(1))
            keyword = re.match(r'^(\s+)(with|env):\s*$', line).group(2)
            
            output.append(line)
            i += 1
            
            # Collect children
            while i < len(lines):
                child_line = lines[i]
                if not child_line.strip():
                    output.append(child_line)
                    i += 1
                    continue
                
                child_indent = len(child_line) - len(child_line.lstrip())
                
                # If this line is at the same indentation as parent, it needs 2 more spaces
                if child_indent == parent_indent and re.match(r'^' + ' ' * child_indent + r'\w+:', child_line):
                    # Add 2 spaces
                    output.append('  ' + child_line)
                    i += 1
                # If it's at parent_indent + 2, it's correct
                elif child_indent == parent_indent + 2:
                    output.append(child_line)
                    i += 1
                # If it's lower, we're done with this block
                elif child_indent < parent_indent:
                    break
                else:
                    output.append(child_line)
                    i += 1
        
        # Pattern 2: Convert multiline quoted strings to literal blocks
        elif re.match(r'^(\s+)run:\s*"', line):
            indent_match = re.match(r'^(\s+)', line)
            indent = len(indent_match.group(1))
            
            # Collect all lines of this multiline string
            run_content = line[indent+4:]  # Skip "run: "
            if run_content.startswith('"'):
                run_content = run_content[1:]  # Remove opening quote
            
            i += 1
            # Collect until closing quote
            while i < len(lines) and not lines[i].rstrip().endswith('"'):
                run_content += '\n' + lines[i]
                i += 1
            
            if i < len(lines):
                # Get the last line and remove closing quote
                last_line = lines[i].rstrip()
                if last_line.endswith('"'):
                    last_line = last_line[:-1]
                run_content += '\n' + last_line
                i += 1
            
            # Now convert to literal block
            output.append(' ' * indent + 'run: |')
            
            # Try to decode escape sequences
            try:
                # Replace \\n with newlines, \\ with \, \" with "
                decoded = run_content.replace('\\"', '"').replace('\\\\', '\\')
                # Handle the pattern "text\<newline><spaces>\<newline>more text"
                decoded = re.sub(r'\\\s+', '', decoded)  # Remove line continuations
                # Handle \n sequences
                decoded = decoded.replace('\\n', '\n')
                
                for code_line in decoded.split('\n'):
                    if code_line.strip():
                        output.append(' ' * (indent + 2) + code_line.lstrip())
            except:
                # Fallback: just output as-is with proper indentation
                output.append(' ' * (indent + 2) + run_content.strip())
        
        # Pattern 3: Fix broken multiline in other cases
        elif re.match(r'^(\s+)script:\s*"', line):
            # Similar to run block
            indent_match = re.match(r'^(\s+)', line)
            indent = len(indent_match.group(1))
            
            script_content = line[indent+8:]  # Skip "script: "
            if script_content.startswith('"'):
                script_content = script_content[1:]
            
            i += 1
            while i < len(lines) and not lines[i].rstrip().endswith('"'):
                script_content += '\n' + lines[i]
                i += 1
            
            if i < len(lines):
                last_line = lines[i].rstrip()
                if last_line.endswith('"'):
                    last_line = last_line[:-1]
                script_content += '\n' + last_line
                i += 1
            
            output.append(' ' * indent + 'script: |')
            
            try:
                decoded = script_content.replace('\\"', '"').replace('\\\\', '\\')
                decoded = re.sub(r'\\\s+', '', decoded)
                decoded = decoded.replace('\\n', '\n')
                
                for code_line in decoded.split('\n'):
                    if code_line.strip():
                        output.append(' ' * (indent + 2) + code_line.lstrip())
            except:
                output.append(' ' * (indent + 2) + script_content.strip())
        
        else:
            output.append(line)
            i += 1
    
    return '\n'.join(output)

def fix_file(filepath):
    """Fix a single YAML file"""
    content = Path(filepath).read_text()
    original = content
    
    fixed = smartly_fix_yaml(content)
    
    # Validate
    try:
        yaml.safe_load(fixed)
        if fixed != original:
            Path(filepath).write_text(fixed)
            return True, "Fixed and validated"
        else:
            return False, "No changes"
    except yaml.YAMLError as e:
        err_msg = str(e).split('\n')[0][:80]
        return False, f"Validation error: {err_msg}"

def main():
    files = [
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
    failed_list = []
    
    for filepath in files:
        success, msg = fix_file(filepath)
        fname = Path(filepath).name
        if success:
            print(f"✓ {fname}")
            fixed_count += 1
        else:
            print(f"✗ {fname}: {msg}")
            failed_list.append(fname)
    
    print(f"\nSummary: {fixed_count} fixed, {len(failed_list)} failed")
    if failed_list:
        print(f"Failed: {', '.join(failed_list)}")
    
    return 0 if not failed_list else 1

if __name__ == '__main__':
    sys.exit(main())

