#!/usr/bin/env python3
"""Fix all corrupted YAML files"""
import re
from pathlib import Path

def fix_file(filepath):
    """Fix a single YAML file"""
    content = Path(filepath).read_text()
    original = content
    
    # Fix 1: with: or env: followed by non-indented fields
    # Pattern: "with:" on one line, then fields at same or less indentation
    # Fix by adding 2 spaces to lines that should be under with/env
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a "with:" or "env:" line
        if re.search(r'^\s+(with|env):\s*$', line):
            fixed_lines.append(line)
            i += 1
            
            # Get the indent level of the with:/env: line
            indent = len(line) - len(line.lstrip())
            expected_child_indent = indent + 2
            
            # Next lines should be indented properly under with/env
            while i < len(lines):
                next_line = lines[i]
                
                # Stop if we hit a line at same or lower indentation that's not under with/env
                if next_line.strip() and not next_line.startswith(' ' * (indent + 2)):
                    if next_line.strip() and len(next_line) - len(next_line.lstrip()) <= indent:
                        break
                
                # If line is at wrong indentation for with/env child
                if next_line.strip() and not next_line.startswith(' ' * (indent + 2)):
                    curr_indent = len(next_line) - len(next_line.lstrip())
                    if curr_indent == indent:
                        # This should be a child of with/env, add 2 spaces
                        fixed_lines.append('  ' + next_line)
                    else:
                        fixed_lines.append(next_line)
                else:
                    fixed_lines.append(next_line)
                
                i += 1
                
                # Stop at next step or job-level keyword
                if i < len(lines):
                    look_ahead = lines[i]
                    if look_ahead.strip().startswith('-') and (len(look_ahead) - len(look_ahead.lstrip())) <= indent:
                        break
                    if re.search(r'^\s{0,4}(steps|jobs|name|uses|run|if|shell):', look_ahead):
                        break
        else:
            fixed_lines.append(line)
            i += 1
    
    fixed_content = '\n'.join(fixed_lines)
    
    # Fix 2: run: lines with escaped newlines
    # Convert: run: "line1\nline2" to run: |
    fixed_content = re.sub(
        r'run: "(.*?)(?<!\\)"',
        lambda m: fix_run_block(m.group(1)),
        fixed_content,
        flags=re.DOTALL
    )
    
    return fixed_content

def fix_run_block(escaped_content):
    """Convert escaped run content to multiline literal block"""
    # Decode the escaped string
    decoded = escaped_content.encode('utf-8').decode('unicode_escape')
    
    # If it's still a single line, keep it as quoted
    if '\n' not in decoded:
        return f'run: "{escaped_content}"'
    
    # Convert to multiline
    lines = decoded.split('\n')
    result = ['run: |']
    for line in lines:
        if line.strip():
            result.append('  ' + line)
    
    return '\n'.join(result)

if __name__ == '__main__':
    test_file = '.github/workflows/trigger-on-approval.yml'
    fixed = fix_file(test_file)
    print(fixed[:1500])
    
