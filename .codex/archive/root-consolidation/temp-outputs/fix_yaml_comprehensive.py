#!/usr/bin/env python3
"""Comprehensive YAML fixer for corrupted workflow files"""
import re
import yaml
from pathlib import Path
import sys

def fix_yaml_comprehensive(filepath):
    """Comprehensively fix YAML corruption"""
    content = Path(filepath).read_text()
    original = content
    
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Handle step containers - detect "- name:" and ensure proper structure
        if re.match(r'^\s*- name:', line):
            fixed_lines.append(line)
            i += 1
            
            # Collect all fields of this step
            step_indent = len(line) - len(line.lstrip())
            
            while i < len(lines):
                next_line = lines[i]
                
                # Stop at next step or job
                if next_line.strip().startswith('- ') or (next_line.strip() and len(next_line) - len(next_line.lstrip()) <= step_indent):
                    if not re.match(r'^\s+\w+:', next_line):
                        break
                
                # Empty lines
                if not next_line.strip():
                    fixed_lines.append(next_line)
                    i += 1
                    continue
                
                curr_indent = len(next_line) - len(next_line.lstrip())
                
                # Key-value pairs at step level (uses, id, env, run, if, with, etc.)
                if curr_indent == step_indent + 2:
                    # Check for "with:" or "env:"
                    if re.match(r'^\s+(with|env):\s*$', next_line):
                        fixed_lines.append(next_line)
                        i += 1
                        
                        # Handle children of with/env
                        with_indent = curr_indent
                        while i < len(lines):
                            child_line = lines[i]
                            
                            if not child_line.strip():
                                fixed_lines.append(child_line)
                                i += 1
                                continue
                            
                            child_indent = len(child_line) - len(child_line.lstrip())
                            
                            # If at same level as with/env, need to indent it
                            if child_indent == with_indent:
                                fixed_lines.append('  ' + child_line)
                                i += 1
                            # If at with_indent + 2, it's already correctly indented
                            elif child_indent == with_indent + 2:
                                fixed_lines.append(child_line)
                                i += 1
                            # If lower than with_indent, we're done with this block
                            elif child_indent < with_indent:
                                break
                            else:
                                fixed_lines.append(child_line)
                                i += 1
                        continue
                    
                    # Handle multiline run: blocks
                    elif next_line.strip().startswith('run:'):
                        # Collect the run content
                        run_match = re.match(r'(\s*)run:\s*(.*)$', next_line)
                        if run_match:
                            run_indent = len(run_match.group(1))
                            run_content = run_match.group(2)
                            
                            # If it's a string that continues
                            if run_content.startswith('"'):
                                # Collect all continuation lines
                                i += 1
                                while i < len(lines) and lines[i].strip() and not re.match(r'^\s+\w+:', lines[i]):
                                    run_content += '\n' + lines[i]
                                    i += 1
                                
                                # Convert to literal block
                                fixed_lines.append(f"{' ' * run_indent}run: |")
                                
                                # Decode and output
                                try:
                                    # Remove outer quotes
                                    if run_content.endswith('"'):
                                        run_content = run_content[:-1]
                                    if run_content.startswith('"'):
                                        run_content = run_content[1:]
                                    
                                    # Decode escape sequences
                                    decoded = run_content.encode('utf-8').decode('unicode_escape')
                                    
                                    # Output lines
                                    for code_line in decoded.split('\n'):
                                        if code_line.strip():
                                            fixed_lines.append(f"{' ' * (run_indent + 2)}{code_line}")
                                except:
                                    # If decode fails, just output as-is
                                    fixed_lines.append(f"{' ' * (run_indent + 2)}{run_content}")
                                continue
                            else:
                                fixed_lines.append(next_line)
                                i += 1
                                continue
                        else:
                            fixed_lines.append(next_line)
                            i += 1
                            continue
                    else:
                        fixed_lines.append(next_line)
                        i += 1
                        continue
                else:
                    fixed_lines.append(next_line)
                    i += 1
        else:
            fixed_lines.append(line)
            i += 1
    
    content = '\n'.join(fixed_lines)
    
    # Validate
    try:
        yaml.safe_load(content)
        if content != original:
            Path(filepath).write_text(content)
            return True, "Fixed"
        else:
            return False, "No changes"
    except yaml.YAMLError as e:
        return False, f"Validation failed: {str(e)[:80]}"

def main():
    files = [
        '.github/workflows/correlation-engine-monitor.yml',
    ]
    
    for filepath in files:
        success, msg = fix_yaml_comprehensive(filepath)
        if success:
            print(f"✓ {Path(filepath).name}: {msg}")
        else:
            print(f"✗ {Path(filepath).name}: {msg}")

if __name__ == '__main__':
    main()

