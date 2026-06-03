#!/usr/bin/env python3
"""
Patch script: replaces the || { } flow scalar session preload with block scalar form.
Safe to run multiple times (idempotent).

Canonical baseline: commit 12f7a861 / blob 8c84a8c1
See: docs/agent/COPILOT_SETUP_STEPS_GUARD.md
"""
import re
import sys

path = ".github/workflows/copilot-setup-steps.yml"
content = open(path).read()

GUARD_COMMENT = """\
      # ⚠️ DO NOT REFACTOR THIS STEP — See docs/agent/COPILOT_SETUP_STEPS_GUARD.md
      # Canonical form: block scalar run: | with if ! ...; then syntax.
      # This step has been broken 4+ times by agents converting it to flow scalar
      # (|| { } syntax) or orphaning the run: key. yamllint 1.38.0 crashes on
      # flow scalar brace syntax. Canonical baseline: commit 12f7a861 / blob 8c84a8c1.
      # RULE: if you are fixing a CI failure, fix the failing file — NOT this step.
"""

CANONICAL_STEP = """\
      - name: "🧠 Session Context Pre-load (memory + policy + accountability + PDA)"
        continue-on-error: true   # non-blocking: agent must start even if preload fails
        run: |
          if ! python3 .github/scripts/session_preload.py; then
            echo "⚠️ session_preload.py failed (non-blocking) — agent will operate without preloaded context"
          fi
"""

# Check if already patched with guard comment
if "DO NOT REFACTOR THIS STEP" in content:
    if 'run: |\n          if ! python3 .github/scripts/session_preload.py' in content:
        print("✅ File already has guard comment + block scalar form — no change needed")
        sys.exit(0)

# Pattern: matches the flow scalar form (|| { })
FULL_PATTERN = re.compile(
    r'( *- name: "🧠 Session Context Pre-load \(memory \+ policy \+ accountability \+ PDA\)"\n'
    r' +continue-on-error: true[^\n]*\n'
    r' +run: python3 \.github/scripts/session_preload\.py \|\| \{\n'
    r'[^\}]*\}\n)',
    re.MULTILINE
)

match = FULL_PATTERN.search(content)
if match:
    replacement = GUARD_COMMENT + CANONICAL_STEP
    new_content = content[: match.start()] + replacement + content[match.end() :]
    open(path, "w").write(new_content)
    print("✅ Patched: replaced || { } flow scalar with block scalar form")
    sys.exit(0)

# Already block scalar — check if guard comment needs adding
if 'run: |\n          if ! python3 .github/scripts/session_preload.py' in content:
    if "DO NOT REFACTOR THIS STEP" not in content:
        STEP_PATTERN = re.compile(
            r'( *- name: "🧠 Session Context Pre-load \(memory \+ policy \+ accountability \+ PDA\)")'
        )
        new_content = STEP_PATTERN.sub(GUARD_COMMENT.rstrip("\n") + "\n" + r"\1", content)
        open(path, "w").write(new_content)
        print("✅ Added guard comment to already-correct block scalar step")
    else:
        print("✅ File already correct — no changes needed")
    sys.exit(0)

print("❌ Could not find session preload step to patch — manual intervention required")
print("   Look for the '🧠 Session Context Pre-load' step and apply the block scalar form manually")
sys.exit(1)
