from pathlib import Path

OFFLINE_BLOCK_TITLE = "## Offline CI & Local Parity"

def ensure_offline_block(md: str) -> str:
    if OFFLINE_BLOCK_TITLE in md:
        return md
    block = f"""
{OFFLINE_BLOCK_TITLE}

This repository enforces **offline-only** validation in the Codex environment.
- No remote CI/CD or network I/O during tests.
- GitHub Actions are **manual-only** and must not run automatically.
- Use `scripts/codex_local_gates.sh` for local gates (lint, tests, coverage).
""".strip()
    sep = "\n\n" if not md.endswith("\n") else "\n"
    return md + sep + block + "\n"
