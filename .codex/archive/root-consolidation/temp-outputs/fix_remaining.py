#!/usr/bin/env python3
"""Fix remaining YAML files using line-based approach"""
import re
from pathlib import Path
import yaml

def comprehensive_fix(filepath):
    """Comprehensive fix that handles all patterns seen so far"""
    with open(filepath) as f:
        content = f.read()
    
    original = content
    lines = content.split('\n')
    output = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Fix 1: with: or env: indentation - collect mis-indented children
        if re.match(r'^\s+(with|env):\s*$', line):
            indent_level = len(line) - len(line.lstrip())
            output.append(line)
            i += 1
            
            while i < len(lines):
                child = lines[i]
                
                if not child.strip():
                    output.append(child)
                    i += 1
                    continue
                
                child_level = len(child) - len(child.lstrip())
                
                # If this looks like a field at the wrong indent, fix it
                if child_level == indent_level and re.match(r'^\s+\w+:\s*', child):
                    output.append('  ' + child)
                    i += 1
                elif child_level == indent_level + 2:
                    # Already correct
                    output.append(child)
                    i += 1
                elif child_level < indent_level:
                    # Next section started
                    break
                else:
                    output.append(child)
                    i += 1
        
        # Fix 2: Collect all multiline run/script blocks and convert to literal
        elif re.match(r'^\s+(run|script):\s*"', line):
            indent_level = len(line) - len(line.lstrip())
            keyword_match = re.match(r'^\s+(run|script):', line)
            keyword = keyword_match.group(1)
            
            # Collect entire block
            full_block = line
            i += 1
            start_i = i
            
            # Find end of block (line ending with ")
            while i < len(lines):
                full_block += '\n' + lines[i]
                if lines[i].rstrip().endswith('"'):
                    i += 1
                    break
                i += 1
            
            # Extract text between first " and last "
            first_quote = full_block.find('"')
            last_quote = full_block.rfind('"')
            
            if first_quote < last_quote:
                inner_text = full_block[first_quote+1:last_quote]
                
                # Decode
                inner_text = inner_text.replace('\\"', '"')
                inner_text = inner_text.replace('\\\\', '\\')
                # Remove line continuations
                inner_text = re.sub(r'\\\s*\n\s*', '', inner_text)
                inner_text = inner_text.replace('\\n', '\n')
                
                # Output literal block
                indent_str = ' ' * indent_level
                output.append(f'{indent_str}{keyword}: |')
                
                for code_line in inner_text.split('\n'):
                    # Skip completely empty lines but preserve structure
                    if code_line or len(inner_text.split('\n')) == 1:
                        output.append(f'{indent_str}  {code_line}')
            else:
                output.append(line)
        
        else:
            output.append(line)
            i += 1
    
    result = '\n'.join(output)
    
    # Validate and write
    try:
        yaml.safe_load(result)
        if result != original:
            with open(filepath, 'w') as f:
                f.write(result)
            return True, "Fixed"
        return False, "No changes"
    except yaml.YAMLError as e:
        return False, f"YAML error: {str(e)[:50]}"
    except Exception as e:
        return False, f"Error: {str(e)[:50]}"

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

fixed = 0
failed = []

for filepath in files_to_fix:
    success, msg = comprehensive_fix(filepath)
    fname = Path(filepath).name
    if success:
        print(f"✓ {fname}")
        fixed += 1
    else:
        print(f"✗ {fname}: {msg}")
        failed.append(fname)

print(f"\n{fixed}/{len(files_to_fix)} fixed")
if failed:
    print(f"Failed: {', '.join(failed[:5])}")

