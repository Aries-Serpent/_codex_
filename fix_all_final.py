#!/usr/bin/env python3
"""Final comprehensive fix for all YAML files"""
import re
from pathlib import Path
import yaml

def fix_yaml_file(filepath):
    """Fix a YAML file by handling common corruption patterns"""
    try:
        with open(filepath) as f:
            content = f.read()
        
        original = content
        lines = content.split('\n')
        output = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Pattern 1: Fix "with:" or "env:" indentation
            if re.match(r'^\s+(with|env):\s*$', line):
                indent = len(line) - len(line.lstrip())
                output.append(line)
                i += 1
                
                # Fix children indentation
                while i < len(lines):
                    next_line = lines[i]
                    if not next_line.strip():
                        output.append(next_line)
                        i += 1
                        continue
                    
                    next_indent = len(next_line) - len(next_line.lstrip())
                    
                    # If at same level and is a key, indent it
                    if next_indent == indent and re.match(r'^\s+\w+:', next_line):
                        output.append('  ' + next_line)
                        i += 1
                    # If properly indented already or less, stop
                    elif next_indent <= indent or next_indent == indent + 2:
                        break
                    else:
                        output.append(next_line)
                        i += 1
            
            # Pattern 2: Fix multiline run: or script: blocks
            elif re.match(r'^\s+(run|script):\s+"', line):
                indent_match = re.match(r'^(\s+)', line)
                indent = len(indent_match.group(1))
                keyword = re.match(r'^\s+(run|script)', line).group(1)
                
                # Collect all lines of this multiline block
                i += 1
                block_lines = [line]
                
                while i < len(lines) and not lines[i].rstrip().endswith('"'):
                    block_lines.append(lines[i])
                    i += 1
                
                if i < len(lines):
                    block_lines.append(lines[i])
                    i += 1
                
                # Extract and decode content
                full_block = '\n'.join(block_lines)
                
                # Try to extract the quoted content
                match = re.search(rf'^\s+{keyword}:\s*"(.*)', full_block, re.DOTALL)
                if match:
                    content_text = match.group(1)
                    
                    # Remove the closing quote if it exists
                    if content_text.endswith('"'):
                        content_text = content_text[:-1]
                    
                    # Decode escape sequences
                    decoded = content_text.replace('\\"', '"')
                    decoded = decoded.replace('\\\\', '\\')
                    decoded = re.sub(r'\\\s*\n\s*\\?\s*', '', decoded)
                    decoded = decoded.replace('\\n', '\n')
                    
                    # Output as literal block
                    output.append(f'{" " * indent}{keyword}: |')
                    for code_line in decoded.split('\n'):
                        if code_line.strip():
                            output.append(f'{" " * (indent + 2)}{code_line.lstrip()}')
                else:
                    output.extend(block_lines)
            
            else:
                output.append(line)
                i += 1
        
        fixed = '\n'.join(output)
        
        # Validate
        yaml.safe_load(fixed)
        
        # Write if changed
        if fixed != original:
            with open(filepath, 'w') as f:
                f.write(fixed)
            return True, "Fixed"
        else:
            return False, "No changes"
    
    except yaml.YAMLError as e:
        return False, f"YAML error: {str(e)[:60]}"
    except Exception as e:
        return False, f"Error: {str(e)[:60]}"

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
    failed = []
    
    for filepath in files:
        success, msg = fix_yaml_file(filepath)
        fname = Path(filepath).name
        if success:
            print(f"✓ {fname}")
            fixed_count += 1
        else:
            print(f"✗ {fname}: {msg}")
            failed.append(fname)
    
    print(f"\n{fixed_count}/{len(files)} files fixed")
    return 0 if not failed else 1

if __name__ == '__main__':
    import sys
    sys.exit(main())

