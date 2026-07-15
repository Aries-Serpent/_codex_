#!/usr/bin/env python3
"""Repair all YAML files by reconstructing them properly"""
import yaml
from pathlib import Path

def reconstruct_trigger_on_approval():
    """Read current file and reconstruct it properly"""
    content = Path('.github/workflows/trigger-on-approval.yml').read_text()
    
    # Replace the broken section with correct YAML
    fixed = content.replace(
        '''      - name: Resolve PR context
        id: ctx
      env:
        PR_HEAD_REF: ${{ github.event.pull_request.head.ref }}
        REVIEWER_LOGIN: ${{ github.event.review.user.login }}
        run: "PR_SHA=\\"${{ github.event.pull_request.head.sha }}\\"\\nPR_NUM=\\"${{ github.event.pull_request.number\\
        \\ }}\\"\\nPR_REF=\\"$PR_HEAD_REF\\"\\nREVIEWER=\\"$REVIEWER_LOGIN\\"\\necho \\"pr_sha=${PR_SHA}\\"\
        \\   >> \\"$GITHUB_OUTPUT\\"\\necho \\"pr_num=${PR_NUM}\\"   >> \\"$GITHUB_OUTPUT\\"\\
        \\necho \\"pr_ref=${PR_REF}\\"   >> \\"$GITHUB_OUTPUT\\"\\necho \\"reviewer=${REVIEWER}\\"\
        \\ >> \\"$GITHUB_OUTPUT\\"\\nif [ -z \\"${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY }}\\" ]; then\\n\
        \\  echo \\"::warning::CODEX_MASTER_KEY not set — workflow dispatch and\\
        \\ auto-approve will use github.token fallback (may 403)\\"\\n  echo \\"token_tier=fallback\\"\
        \\ >> \\"$GITHUB_OUTPUT\\"\\nelse\\n  echo \\"token_tier=master\\"  >> \\"$GITHUB_OUTPUT\\"\\
        \\nfi\\necho \\"Approval by ${REVIEWER} on PR  #${PR_NUM} @ ${PR_SHA} (${PR_REF})\\"\\
        \\n"''',
        '''      - name: Resolve PR context
        id: ctx
        env:
          PR_HEAD_REF: ${{ github.event.pull_request.head.ref }}
          REVIEWER_LOGIN: ${{ github.event.review.user.login }}
        run: |
          PR_SHA="${{ github.event.pull_request.head.sha }}"
          PR_NUM="${{ github.event.pull_request.number }}"
          PR_REF="$PR_HEAD_REF"
          REVIEWER="$REVIEWER_LOGIN"
          echo "pr_sha=${PR_SHA}" >> "$GITHUB_OUTPUT"
          echo "pr_num=${PR_NUM}" >> "$GITHUB_OUTPUT"
          echo "pr_ref=${PR_REF}" >> "$GITHUB_OUTPUT"
          echo "reviewer=${REVIEWER}" >> "$GITHUB_OUTPUT"
          if [ -z "${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY }}" ]; then
            echo "::warning::CODEX_MASTER_KEY not set — workflow dispatch and auto-approve will use github.token fallback (may 403)"
            echo "token_tier=fallback" >> "$GITHUB_OUTPUT"
          else
            echo "token_tier=master" >> "$GITHUB_OUTPUT"
          fi
          echo "Approval by ${REVIEWER} on PR  #${PR_NUM} @ ${PR_SHA} (${PR_REF})"'''
    )
    
    # Fix checkout step indentation
    fixed = fixed.replace(
        '''      - name: Checkout
        uses: actions/checkout@v5
        with:
        persist-credentials: false
        fetch-depth: 1
        token: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY || github.token
          }}
        ref: ${{ github.event.pull_request.head.ref }}''',
        '''      - name: Checkout
        uses: actions/checkout@v5
        with:
          persist-credentials: false
          fetch-depth: 1
          token: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY || github.token }}
          ref: ${{ github.event.pull_request.head.ref }}'''
    )
    
    # Fix setup-python step indentation
    fixed = fixed.replace(
        '''      - name: Set up Python (for approve_pending_runs.py)
        uses: actions/setup-python@v6
        with:
        cache: pip
        python-version: 3.12.13''',
        '''      - name: Set up Python (for approve_pending_runs.py)
        uses: actions/setup-python@v6
        with:
          cache: pip
          python-version: 3.12.13'''
    )
    
    return fixed

if __name__ == '__main__':
    fixed_content = reconstruct_trigger_on_approval()
    
    # Validate
    try:
        yaml.safe_load(fixed_content)
        print("✓ YAML is valid")
        # Write it back
        Path('.github/workflows/trigger-on-approval.yml').write_text(fixed_content)
        print("✓ File written")
    except yaml.YAMLError as e:
        print(f"✗ YAML validation failed: {e}")

