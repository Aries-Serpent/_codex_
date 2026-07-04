import os
import subprocess
import sys
import tokenize
from io import StringIO
from pathlib import Path

BANNED_PATTERNS = [
    "type: ignore",
    "noqa",
    "pylint: disable",
]

# Deletion policy: deleting these paths in PR requires explicit human override label/flow
CRITICAL_DELETE_HINTS = (
    "tests/",
    ".github/workflows/",
    "validation",
    "security",
    "auth",
    "manifest",
)

def sh(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()

def get_base_head() -> tuple[str, str]:
    base = os.getenv("GITHUB_BASE_SHA")
    head = os.getenv("GITHUB_SHA")
    if base and head:
        return base, head
    base = sh(["git", "merge-base", "HEAD", "origin/main"])
    head = sh(["git", "rev-parse", "HEAD"])
    return base, head

def changed_name_status(base: str, head: str) -> list[tuple[str, str]]:
    # format: <STATUS>\t<PATH>
    out = sh(["git", "diff", "--name-status", base, head])
    rows: list[tuple[str, str]] = []
    for line in out.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t", 1)
        if len(parts) != 2:
            continue
        rows.append((parts[0].strip(), parts[1].strip()))
    return rows

def comment_has_banned(content: str) -> list[str]:
    hits: list[str] = []
    reader = StringIO(content).readline
    for tok in tokenize.generate_tokens(reader):
        if tok.type == tokenize.COMMENT:
            c = tok.string.lower()
            for pat in BANNED_PATTERNS:
                if pat in c:
                    hits.append(f"line {tok.start[0]}: banned suppression in comment: {pat}")
    return hits

def main() -> int:
    base, head = get_base_head()
    rows = changed_name_status(base, head)

    violations: list[str] = []

    # 1) Deleted-file bypass guard
    for status, path in rows:
        if status.upper().startswith("D"):
            low = path.lower()
            is_py_or_test = low.endswith(".py") or low.startswith("tests/")
            is_critical = any(h in low for h in CRITICAL_DELETE_HINTS)
            if is_py_or_test and is_critical:
                violations.append(
                    f"{path}: deletion of critical python/test/workflow file is blocked by guard"
                )

    # 2) Syntax + suppression pragma checks for existing changed python files
    changed_existing_py = [
        path
        for status, path in rows
        if not status.upper().startswith("D") and path.endswith(".py") and Path(path).exists()
    ]

    for path in changed_existing_py:
        raw = Path(path).read_text(encoding="utf-8", errors="ignore")

        # COMMENT-token scoped suppression check (prevents docstring/string false positives)
        for h in comment_has_banned(raw):
            violations.append(f"{path}: {h}")

        # Syntax check (deterministic)
        try:
            compile(raw, path, "exec")
        except SyntaxError as e:
            violations.append(f"{path}: syntax error: {e}")

    if violations:
        for v in violations:
            print(f"::error::{v}")
        return 1

    print("Deterministic diff guard passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())