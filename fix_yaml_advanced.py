#!/usr/bin/env python3
"""Advanced YAML fixer handling all edge cases"""
import re
from pathlib import Path
import yaml

def advanced_fix(filepath):
    """Advanced fixing with better pattern handling"""
    with open(filepath) as f:
        lines = f.readlines()
    
    output = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Pattern: Fix indentation under "with:" or "env:"
        if re.match(r'^(\s+)(with|env):\s*$', line):
            indent_str = re.match(r'^(\s+)', line).group(1)
            indent = len(indent_str)
            keyword = re.match(r'^(\s+)(with|env):\s*$', line).group(2)
            
            output.append(line)
            i += 1
            
            # Process children
            while i < len(lines):
                next_line = lines[i]
                
                # Empty lines
                if not next_line.strip():
                    output.append(next_line)
                    i += 1
                    continue
                
                next_indent = len(next_line) - len(next_line.lstrip())
                
                # If at parent indent and is a key, add 2 spaces
                if next_indent == indent and re.match(r'^\s+\w+:', next_line):
                    output.append('  ' + next_line)
                    i += 1
                # If properly indented (indent+2) or less, stop
                elif next_indent <= indent:
                    break
                elif next_indent == indent + 2:
                    output.append(next_line)
                    i += 1
                else:
                    output.append(next_line)
                    i += 1
        
        # Pattern: Multiline run/script blocks starting with quote
        elif re.match(r'^\s+(run|script):\s+"', line):
            indent_str = re.match(r'^(\s+)', line).group(1)
            indent = len(indent_str)
            keyword = re.match(r'^\s+(run|script):', line).group(1)
            
            # Collect the entire multiline block
            block_text = line
            i += 1
            
            # Keep collecting until end quote
            while i < len(lines):
                next_line = lines[i]
                block_text += next_line
                
                if next_line.rstrip().endswith('"'):
                    i += 1
                    break
                i += 1
            
            # Extract content between quotes
            match = re.search(rf'^\s+{keyword}:\s*"((?:\\.|[^"])*?)"', block_text, re.DOTALL)
            if not match:
                # Maybe the closing quote is separate
                match = re.search(rf'^\s+{keyword}:\s*"(.*)', block_text, re.DOTALL)
                if match:
                    content = match.group(1)
                    # Find and remove closing quote
                    last_quote = content.rfind('"')
                    if last_quote >= 0:
                        content = content[:last_quote]
                else:
                    output.append(line)
                    continue
            else:
                content = match.group(1)
            
            # Decode escape sequences
            content = content.replace('\\"', '"')
            content = content.replace('\\\\', '\\')
            # Handle line continuations with backslash
            content = re.sub(r'\\\s*\n\s*\\?\s*', '', content)
            content = content.replace('\\n', '\n')
            
            # Normalize spacing
            lines_list = content.split('\n')
            # Filter out empty lines from the original
            lines_list = [l for l in lines_list if l.strip() or len(lines_list) > 1]
            
            # Output as literal block
            output.append(f'{indent_str}{keyword}: |\n')
            for code_line in lines_list:
                if code_line.strip():
                    output.append(f'{indent_str}  {code_line.lstrip()}\n')
        
        else:
            output.append(line)
            i += 1
    
    # Join and validate
    result = ''.join(output)
    
    try:
        yaml.safe_load(result)
        with open(filepath, 'w') as f:
            f.write(result)
        return True
    except:
        return False

files = [
    '.github/workflows/correlation-engine-monitor.yml',
    '.github/workflows/ensemble-predictor-monitor.yml',
]

for f in files:
    result = advanced_fix(f)
    print(f"{'✓' if result else '✗'} {Path(f).name}")

