"""Print CLI flags for file_integrity_audit from allowlists.yml."""
from __future__ import annotations

from pathlib import Path

import yaml

POLICY = Path(".codex/policies/allowlists.yml")


def main() -> None:
    cfg = yaml.safe_load(POLICY.read_text()) if POLICY.exists() else {}
    parts: list[str] = []
    for key, flag in [("added", "--allow-added"), ("removed", "--allow-removed"), ("changed", "--allow-changed")]:
        for pattern in cfg.get(key, []) or []:
            parts.append(f"{flag} {pattern}")
    print(" ".join(parts))


if __name__ == "__main__":  # pragma: no cover
    main()
