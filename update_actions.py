#!/usr/bin/env python3
"""
Delegate action version updates to enforce_actions_versions.py.
This ensures:
1. SHA-pinned actions are preserved (not rewritten)
2. Only versions below policy are upgraded
3. No downgrades occur
"""

import subprocess
import sys

result = subprocess.run(
    [sys.executable, "scripts/ci/enforce_actions_versions.py", "--fix"],
    cwd="."
)
sys.exit(result.returncode)
