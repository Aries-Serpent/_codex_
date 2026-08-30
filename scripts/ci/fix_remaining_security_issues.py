#!/usr/bin/env python3
"""Fix remaining security issues in agent.yaml files"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
import re

def fix_file(filepath: Path):
    """Fix a single file"""
    content = filepath.read_text()
    original = content

    # Fix indentation issue: "- name:" should not have extra indentation before "env:"
    content = re.sub(
        r'(\s+- name: Comment on PR)\n(\s+)env:',
        r'\1\n      env:',
        content
    )

    # Fix process.env references - remove quotes
    content = content.replace("'process.env.COVERAGE'", "process.env.COVERAGE")
    content = content.replace("'process.env.PASSED'", "process.env.PASSED")
    content = content.replace("'process.env.THRESHOLD'", "process.env.THRESHOLD")

    # Fix file read to use environment variable
    content = re.sub(
        r"fs\.readFileSync\('\$\{\{ inputs\.output-file \}\}', 'utf8'\)",
        "fs.readFileSync(process.env.OUTPUT_FILE, 'utf8')",
        content
    )

    # Add OUTPUT_FILE to env section if not present
    if "OUTPUT_FILE: ${{ inputs.output-file }}" not in content and "inputs.output-file" in content:
        content = re.sub(
            r'(\s+env:\n(?:\s+\w+: \$\{\{[^}]+\}\}\n)+)',
            lambda m: m.group(1) + "        OUTPUT_FILE: ${{ inputs.output-file }}\n",
            content
        )

    if content != original:
        filepath.write_text(content)
        return True
    return False

def main():
    files_to_fix = [
        ".github/agents/service-integration-tester/agent.yaml",
        ".github/agents/dependency-conflict-resolver/agent.yaml",
        ".github/agents/security-vulnerability-patcher/agent.yaml",
    ]

    repo_root = REPO_ROOT

    for file_path in files_to_fix:
        full_path = repo_root / file_path
        if not full_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue

        print(f"🔧 Fixing {file_path}...")
        if fix_file(full_path):
            print(f"✅ Fixed {file_path}")
        else:
            print(f"ℹ️  No changes needed for {file_path}")

    print("\n✅ All remaining security issues fixed!")

if __name__ == "__main__":
    main()
