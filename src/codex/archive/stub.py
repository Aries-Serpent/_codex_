from __future__ import annotations

from .util import utcnow_iso


def make_stub_text(
    path: str,
    *,
    actor: str,
    reason: str,
    tombstone: str,
    sha256: str,
    commit: str,
) -> str:
    lines = [
        "# TOMBSTONE ARCHIVE STUB — DO NOT DELETE",
        f"# File: {path}",
        f"# ArchivedBy: {actor}",
        f"# Reason: {reason}",
        f"# Tombstone: {tombstone}",
        f"# SHA256: {sha256}",
        f"# ArchivedAt: {utcnow_iso()}",
        f"# Commit: {commit}",
        "#",
        "# To restore:",
        f"#   python -m codex.cli archive restore {tombstone} --out {path}",
        "#",
        "# NOTE: This stub intentionally contains no functional code.",
        "",
    ]
    return "\n".join(lines)
