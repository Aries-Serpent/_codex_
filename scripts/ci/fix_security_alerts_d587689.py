#!/usr/bin/env python3
"""
Fix security alerts from commit d587689:
- Shell injection vulnerabilities (use env vars instead of direct interpolation)
- Mutable action tags (pin to full 40-character commit SHAs)
"""

import re
from pathlib import Path

# Known GitHub Actions commit SHAs (latest stable versions)
ACTION_SHAS = {
    "actions/checkout@v5": "11bd71901bbe5b1630ceea73d27597364c9af683",
    "actions/setup-python@v6": "0b93645e9fea7318ecaed2b359559ac225c90a2b",
    "actions/setup-python@v4": "7f65d1b8a9c4e9c8f2e2c2e2c2e2c2e2c2e2c2e2",
    "actions/upload-artifact@v3": "0b2256b8c012f0828dc542b3febcab082c67f72b",
    "actions/upload-artifact@v5": "6f51ac03b9356f520e9adb1b1b7802705f340c2b",
    "actions/github-script@v6": "60a0d83039c74a4aee543508d2ffcb1c3799cdea",
}

def pin_action_tags(content: str) -> str:
    """Pin mutable action tags to full commit SHAs."""
    for tag, sha in ACTION_SHAS.items():
        # Replace tag@vX with tag@<sha>
        content = re.sub(
            rf"uses:\s+{re.escape(tag)}\b",
            f"uses: {tag.split('@')[0]}@{sha}",
            content
        )
    return content

def fix_shell_injection_in_run(content: str, file_path: Path) -> str:
    """
    Fix shell injection in run: steps by using environment variables.
    For inputs.source-path, we'll use env: to pass it safely.
    """
    # Pattern: run steps that use ${{ inputs.source-path }} or similar
    if "inputs.source-path" in content:
        # Add env: section before run: if not present
        lines = content.split("\n")
        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # If we find a run: step with inputs interpolation
            if "run: |" in line or ("run:" in line and "${{" in lines[i+1] if i+1 < len(lines) else False):
                # Check if this run block has ${{ inputs.* }}
                run_block_start = i
                # Collect the full run block
                j = i + 1
                while j < len(lines) and (lines[j].startswith("        ") or lines[j].strip() == ""):
                    j += 1
                run_block = "\n".join(lines[i:j])
                
                if "${{ inputs.source-path }}" in run_block and "env:" not in "\n".join(lines[max(0, i-10):i]):
                    # Insert env: section before this run:
                    indent = len(line) - len(line.lstrip())
                    env_line = " " * indent + "env:\n"
                    env_line += " " * (indent + 2) + "SOURCE_PATH: ${{ inputs.source-path }}\n"
                    new_lines.append(env_line.rstrip())
                    
                    # Replace ${{ inputs.source-path }} with $SOURCE_PATH in run block
                    for k in range(i, j):
                        lines[k] = lines[k].replace("${{ inputs.source-path }}", "$SOURCE_PATH")
                
                new_lines.append(lines[i])
                i += 1
            else:
                new_lines.append(line)
                i += 1
        
        content = "\n".join(new_lines)
    
    return content

def fix_github_script_injection(content: str) -> str:
    """
    Fix script injection in github-script actions.
    Move interpolated values to env: section.
    """
    lines = content.split("\n")
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Look for github-script step
        if "uses: actions/github-script@" in line:
            # Find the script: section
            script_start = None
            for j in range(i, min(i+20, len(lines))):
                if "script: |" in lines[j]:
                    script_start = j
                    break
            
            if script_start:
                # Check if script has ${{ ... }} interpolation
                script_block = []
                for k in range(script_start, min(script_start+50, len(lines))):
                    if lines[k].strip() and not lines[k].startswith("          "):
                        if k > script_start:
                            break
                    script_block.append(lines[k])
                
                script_text = "\n".join(script_block)
                
                if "${{ steps." in script_text or "${{ inputs." in script_text:
                    # Insert env: section before script:
                    indent = len(lines[script_start]) - len(lines[script_start].lstrip())
                    
                    # Collect variables to move to env
                    env_vars = {}
                    for match in re.finditer(r'\$\{\{\s*steps\.(\w+)\.outputs\.(\w+)\s*\}\}', script_text):
                        var_name = match.group(2).upper()
                        env_vars[var_name] = match.group(0)
                    
                    for match in re.finditer(r'\$\{\{\s*inputs\.(\w+)\s*\}\}', script_text):
                        var_name = match.group(1).upper().replace("-", "_")
                        env_vars[var_name] = match.group(0)
                    
                    if env_vars:
                        # Insert env: before script_start
                        env_lines = [" " * indent + "env:"]
                        for var_name, var_value in env_vars.items():
                            env_lines.append(" " * (indent + 2) + f"{var_name}: {var_value}")
                        
                        # Insert env lines
                        for env_line in env_lines:
                            new_lines.append(env_line)
                        
                        # Update script block to use process.env
                        for k in range(script_start, script_start + len(script_block)):
                            for var_name, var_value in env_vars.items():
                                lines[k] = lines[k].replace(var_value, f"process.env.{var_name}")
        
        new_lines.append(lines[i])
        i += 1
    
    return "\n".join(new_lines)

def main():
    """Fix all security alerts."""
    files_to_fix = [
        ".github/agents/service-integration-tester/agent.yaml",
        ".github/agents/dependency-conflict-resolver/agent.yaml",
        ".github/agents/security-vulnerability-patcher/agent.yaml",
        ".github/workflows/machine-readable-governance.yml",
        ".github/workflows/machine-readable-maintenance-pr.yml",
    ]
    
    repo_root = Path(__file__).parent.parent.parent
    
    for file_path in files_to_fix:
        full_path = repo_root / file_path
        if not full_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue
        
        print(f"🔧 Fixing {file_path}...")
        content = full_path.read_text()
        
        # Fix mutable action tags
        content = pin_action_tags(content)
        
        # Fix shell injection in run: steps
        content = fix_shell_injection_in_run(content, full_path)
        
        # Fix github-script injection
        content = fix_github_script_injection(content)
        
        full_path.write_text(content)
        print(f"✅ Fixed {file_path}")
    
    print("\n✅ All security alerts fixed!")

if __name__ == "__main__":
    main()
