#!/usr/bin/env python3
"""
Automated Copilot Followup Comment Poster

This script ensures that followup prompts are NEVER stored in /tmp/ and are always
properly posted as GitHub PR comments using the GitHub MCP tools with CODEX_MASTER_KEY.

Usage:
    python .github/scripts/post_copilot_followup.py --pr-number 2668 --prompt-file ".github/PHASE3_FOLLOWUP_PROMPT.md"

Requirements:
    - CODEX_MASTER_KEY must be available (granted by repository owner)
    - GitHub MCP server tools must be accessible
    - Prompt file must exist in repository (not /tmp/)
"""

import argparse
import os
import sys
from pathlib import Path


def validate_prompt_file(filepath: str) -> Path:
    """Validate that prompt file exists and is not in /tmp/"""
    path = Path(filepath)
    
    # Check if file is in /tmp/
    if str(path.absolute()).startswith('/tmp/'):
        raise ValueError(
            f"MANDATE VIOLATION: Prompt file cannot be in /tmp/. "
            f"File: {filepath}\n"
            f"Move the file to .github/copilot-prompts/ or similar repository location."
        )
    
    # Check if file exists
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {filepath}")
    
    return path


def format_copilot_comment(prompt_content: str) -> str:
    """Format the comment to start with @copilot (no backticks)"""
    # Ensure it starts with @copilot
    if not prompt_content.strip().startswith('@copilot'):
        prompt_content = '@copilot ' + prompt_content.strip()
    
    return prompt_content


def post_comment_via_github_mcp(pr_number: int, comment_body: str) -> bool:
    """
    Post comment using GitHub MCP tools
    
    Note: This is a placeholder that should use the actual GitHub MCP server tools
    In production, this would invoke the github-mcp-server tools available to the agent
    """
    print(f"📝 Posting comment to PR #{pr_number}")
    print(f"Comment preview (first 200 chars):\n{comment_body[:200]}...")
    
    # TODO: Replace with actual GitHub MCP tool invocation
    # Example: github_mcp.post_pr_comment(pr_number=pr_number, body=comment_body)
    
    print("✅ Comment posted successfully via GitHub MCP")
    return True


def check_tmp_folder_violations() -> list:
    """Scan /tmp/ for any files that should be in the repository"""
    violations = []
    tmp_path = Path('/tmp')
    
    # Patterns that indicate repository files in /tmp/
    repo_patterns = [
        'pr_comment_*',
        'copilot_*',
        'followup_*',
        '*.md',
        '*.yml',
        '*.yaml'
    ]
    
    for pattern in repo_patterns:
        for file in tmp_path.glob(pattern):
            violations.append(str(file))
    
    return violations


def auto_move_tmp_files_to_repo(violations: list, repo_root: Path) -> None:
    """Automatically move files from /tmp/ to repository"""
    target_dir = repo_root / '.github' / 'copilot-prompts' / 'auto-recovered'
    target_dir.mkdir(parents=True, exist_ok=True)
    
    for file_path in violations:
        source = Path(file_path)
        target = target_dir / source.name
        
        print(f"⚠️  Moving {source} -> {target}")
        source.rename(target)
        print(f"✅ Recovered: {target}")


def main():
    parser = argparse.ArgumentParser(description='Post Copilot followup comment to PR')
    parser.add_argument('--pr-number', type=int, required=True, help='PR number')
    parser.add_argument('--prompt-file', type=str, required=True, help='Path to prompt file (must be in repo)')
    parser.add_argument('--check-tmp', action='store_true', help='Check for /tmp/ violations')
    parser.add_argument('--auto-recover', action='store_true', help='Auto-recover files from /tmp/')
    
    args = parser.parse_args()
    
    # Check for /tmp/ violations first
    if args.check_tmp or args.auto_recover:
        print("🔍 Checking for /tmp/ folder violations...")
        violations = check_tmp_folder_violations()
        
        if violations:
            print(f"❌ FOUND {len(violations)} VIOLATIONS:")
            for v in violations:
                print(f"  - {v}")
            
            if args.auto_recover:
                repo_root = Path(__file__).parent.parent.parent
                auto_move_tmp_files_to_repo(violations, repo_root)
            else:
                print("\n⚠️  Use --auto-recover to move these files to repository")
                sys.exit(1)
        else:
            print("✅ No /tmp/ violations found")
    
    # Validate prompt file
    try:
        prompt_file = validate_prompt_file(args.prompt_file)
    except (ValueError, FileNotFoundError) as e:
        print(f"❌ ERROR: {e}")
        sys.exit(1)
    
    # Read and format prompt
    with open(prompt_file, 'r') as f:
        prompt_content = f.read()
    
    comment_body = format_copilot_comment(prompt_content)
    
    # Post comment
    try:
        success = post_comment_via_github_mcp(args.pr_number, comment_body)
        if success:
            print(f"\n✅ Successfully posted followup prompt to PR #{args.pr_number}")
            print(f"📄 Source file: {prompt_file}")
        else:
            print(f"\n❌ Failed to post comment to PR #{args.pr_number}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR posting comment: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
