from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    requested = os.environ.get("LINT_POLICY")
    if requested not in (None, "", "ruff", "hybrid"):
        raise SystemExit(f"Unknown LINT_POLICY={requested}")
    policy = requested or (
        json.loads((ROOT / ".codex/lint-policy.json").read_text()).get("policy", "hybrid")
        if (ROOT / ".codex/lint-policy.json").exists()
        else "hybrid"
    )
    shutil.copyfile(ROOT / f".pre-commit-{policy}.yaml", ROOT / ".pre-commit-config.yaml")
    print(f"[pre-commit] selected policy: {policy}")


if __name__ == "__main__":
    main()
