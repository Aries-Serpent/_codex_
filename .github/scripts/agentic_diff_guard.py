import os
import re
import subprocess
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

def comment_has_banned(content: str, added_lines: set[int]) -> list[str]:
    """Check for banned suppression patterns, but allow noqa on imports."""
    hits: list[str] = []
    lines = content.split('\n')
    reader = StringIO(content).readline
    for tok in tokenize.generate_tokens(reader):
        if tok.type == tokenize.COMMENT and tok.start[0] in added_lines:
            c = tok.string.lower()
            line_num = tok.start[0]
            line_text = lines[line_num - 1] if line_num <= len(lines) else ""
            
            # Allow noqa on import statements (common and valid use case)
            is_import_line = "import " in line_text
            
            for pat in BANNED_PATTERNS:
                if pat in c:
                    # Skip noqa on imports
                    if pat == "noqa" and is_import_line:
                        continue
                    hits.append(f"line {line_num}: banned suppression in comment: {pat}")
    return hits


def added_line_numbers(base: str, head: str, path: str) -> set[int]:
    """Return the destination line numbers added for a path in the base..head diff."""
    diff = subprocess.check_output(
        ["git", "diff", "--unified=0", base, head, "--", path],
        text=True,
    )
    lines: set[int] = set()
    for match in re.finditer(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", diff, re.MULTILINE):
        start = int(match.group(1))
        count = int(match.group(2) or "1")
        if count <= 0:
            continue
        lines.update(range(start, start + count))
    return lines

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
        added_lines = added_line_numbers(base, head, path)

        # COMMENT-token scoped suppression check (prevents docstring/string false positives)
        for h in comment_has_banned(raw, added_lines):
            match = re.search(r"line (\d+):", h)
            if not match or int(match.group(1)) not in added_lines:
                continue
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
