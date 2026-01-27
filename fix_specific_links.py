#!/usr/bin/env python3
"""
Final pass to fix remaining specific broken links
"""

import re
from pathlib import Path

REPO_ROOT = Path("/home/runner/work/_codex_/_codex_")

# Specific files and their broken links to fix
fixes = [
    # docs/archive/phases/PHASE_11_0_EXECUTIVE_SUMMARY.md
    {
        'file': 'docs/archive/phases/PHASE_11_0_EXECUTIVE_SUMMARY.md',
        'replacements': [
            ('(./COGNITIVE_BRAIN_STATUS_V11_WORKFLOW_CI_FIXES.md)', '(https://github.com/Aries-Serpent/_codex_/tree/main/docs/cognitive_brain/status)'),
            ('(./COGNITIVE_BRAIN_ARCHITECTURE_PHASE_11.md)', '(https://github.com/Aries-Serpent/_codex_/blob/main/docs/cognitive_brain/ARCHITECTURE.md)'),
        ]
    },
    # docs/quality/LINK_VALIDATION_SUMMARY_2026-01-26.md
    {
        'file': 'docs/quality/LINK_VALIDATION_SUMMARY_2026-01-26.md',
        'replacements': [
            ('(.codex/agents/link-validator-agent.md)', '(../agents/link-validator-agent.md)'),
        ]
    },
]

def apply_fixes():
    """Apply all specific fixes"""
    for fix in fixes:
        file_path = REPO_ROOT / fix['file']
        
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue
        
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            for old, new in fix['replacements']:
                if old in content:
                    content = content.replace(old, new)
                    print(f"✅ {fix['file']}: {old} → {new}")
                else:
                    print(f"⚠️  {fix['file']}: Pattern not found: {old}")
            
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                print(f"💾 Saved {fix['file']}")
        
        except Exception as e:
            print(f"❌ Error processing {fix['file']}: {e}")

if __name__ == "__main__":
    print("🔧 Applying final specific link fixes...\n")
    apply_fixes()
    print("\n✨ Done!")
