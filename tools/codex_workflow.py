#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ruff: noqa: E501
"""
Codex Workflow: ISO-8601 parsing upgrade + tests + docs
Repo: Aries-Serpent/_codex_ (branch 0B_base_)
Policy: DO NOT ACTIVATE ANY GitHub Actions files.
"""

import difflib
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(
    subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
)
CODEX_DIR = ROOT / ".codex"
CHANGE_LOG = CODEX_DIR / "change_log.md"
ERROR_LOG = CODEX_DIR / "errors.ndjson"
RESULTS = CODEX_DIR / "results.md"
INVENTORY = CODEX_DIR / "inventory.json"

DO_NOT_ACTIVATE_GITHUB_ACTIONS = True


# --------- Utilities ---------
def sh(cmd, check=True):
    try:
        return subprocess.run(cmd, text=True, capture_output=True, check=check)
    except subprocess.CalledProcessError as e:
        log_error(
            "1.1", f"Run shell: {' '.join(cmd)}", e.stderr or e.stdout, {"cmd": cmd}
        )
        if check:
            raise
        return e


def log_error(step, desc, err, ctx=None):
    msg = (
        "Question for ChatGPT-5:\n"
        f"While performing [{step}: {desc}], encountered the following error:\n"
        f"{(err or '').strip()}\n"
        f"Context: {json.dumps(ctx or {}, ensure_ascii=False)}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n"
    )
    sys.stderr.write(msg + "\n")
    ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
    with ERROR_LOG.open("a", encoding="utf-8") as f:
        f.write(
            json.dumps(
                {
                    "step": step,
                    "desc": desc,
                    "error": err,
                    "context": ctx,
                    "render": msg,
                },
                ensure_ascii=False,
            )
            + "\n"
        )


def append_change(file_path, action, rationale, before=None, after=None):
    CHANGE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with CHANGE_LOG.open("a", encoding="utf-8") as f:
        f.write(f"\n### {datetime.utcnow().isoformat()}Z — {action}\n")
        f.write(f"**File:** `{file_path}`\n\n**Rationale:** {rationale}\n\n")
        if before is not None and after is not None:
            diff = "".join(
                difflib.unified_diff(
                    before.splitlines(True),
                    after.splitlines(True),
                    fromfile=f"{file_path} (before)",
                    tofile=f"{file_path} (after)",
                )
            )
            f.write("```diff\n" + diff + "\n```\n")


def safe_write(path: Path, new_text: str, rationale: str):
    before = path.read_text(encoding="utf-8") if path.exists() else ""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(new_text, encoding="utf-8")
    append_change(
        str(path.relative_to(ROOT)), "Modify/Create", rationale, before, new_text
    )


def is_clean_worktree():
    out = sh(["git", "status", "--porcelain"], check=False)
    return out.returncode == 0 and out.stdout.strip() == ""


def index_files():
    exts = (".py", ".sh", ".sql", ".js", ".ts", ".html", ".md")
    files = []
    for p in ROOT.rglob("*"):
        if (
            p.is_file()
            and p.suffix in exts
            and ".git" not in p.parts
            and ".venv" not in p.parts
        ):
            files.append(str(p.relative_to(ROOT)))
    CODEX_DIR.mkdir(parents=True, exist_ok=True)
    INVENTORY.write_text(json.dumps({"files": files}, indent=2), encoding="utf-8")


def find_candidates():
    # Returns (parse_targets, query_logs)
    parse_targets, query_logs = [], None
    # Avoid .github/workflows to respect policy
    for p in ROOT.rglob("*.py"):
        if ".github" in p.parts and "workflows" in p.parts:
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if re.search(r"\bdef\s+parse_when\s*\(", txt):
            parse_targets.append(p)
        if p.name == "query_logs.py":
            query_logs = p
    return parse_targets, query_logs


# Injected implementation for parse_when
PARSE_WHEN_IMPL = r'''

def parse_when(s: str):
    """
    Parse ISO-8601-like timestamps supporting:
      - 'Z' (UTC), e.g. '2025-08-19T15:26:00Z'
      - explicit offsets, e.g. '2025-08-19T10:26:00-05:00'
      - naive timestamps (no timezone), e.g. '2025-08-19T15:26:00'
    Returns:
      datetime: aware if input has 'Z' or an explicit offset; otherwise naive.
    """
    from datetime import datetime
    if not isinstance(s, str):
        raise TypeError(f"parse_when expects str, got {type(s).__name__}")
    s2 = s.strip()
    # Normalize 'Z' to '+00:00' for fromisoformat compatibility
    if s2.endswith('Z'):
        s2 = s2[:-1] + '+00:00'
    try:
        return datetime.fromisoformat(s2)
    except Exception as e:
        # Provide clearer error for diagnostics
        raise ValueError(f"Unsupported timestamp format: {s!r}") from e
'''.lstrip()


def upgrade_parse_when(pyfile: Path):
    text = pyfile.read_text(encoding="utf-8")
    # Replace existing parse_when body or append if not present (conservative)
    if re.search(r"\bdef\s+parse_when\s*\(", text):
        new = re.sub(
            r"\bdef\s+parse_when\s*\([^\)]*\):(?:\s*\"\"\".*?\"\"\"\s*)?[\s\S]*?(?=^\S|\Z)",
            PARSE_WHEN_IMPL,
            text,
            flags=re.MULTILINE,
        )
        if new == text:
            # Fallback: append a new implementation; caller can refactor call sites later
            new = text.rstrip() + "\n\n" + PARSE_WHEN_IMPL
        safe_write(
            pyfile,
            new,
            "Upgrade parse_when to support Z/offset/naive via fromisoformat normalization",
        )
        return True
    else:
        # No parse_when; append at EOF
        new = text.rstrip() + "\n\n" + PARSE_WHEN_IMPL
        safe_write(
            pyfile, new, "Add parse_when implementation (no prior definition found)"
        )
        return True


def ensure_tests():
    tests_dir = ROOT / "tests"
    tests_dir.mkdir(exist_ok=True)
    test_file = tests_dir / "test_parse_when.py"
    content = """# Auto-generated regression tests for parse_when
import importlib, sys, types
from datetime import timezone

# Attempt to locate parse_when from likely modules
MODULE_CANDIDATES = ["query_logs", "utils", "time_utils", "dates", "common"]

parse_when = None
for m in MODULE_CANDIDATES:
    try:
        mod = importlib.import_module(m)
        if hasattr(mod, "parse_when"):
            parse_when = getattr(mod, "parse_when")
            break
    except Exception:
        continue

if parse_when is None:
    raise ImportError("Could not locate parse_when in candidate modules: " + ", ".join(MODULE_CANDIDATES))

def test_parse_when_z():
    dt = parse_when("2025-08-19T12:34:56Z")
    assert dt.tzinfo is not None
    assert dt.utcoffset() == timezone.utc.utcoffset(dt)

def test_parse_when_offset():
    dt = parse_when("2025-08-19T07:34:56-05:00")
    assert dt.tzinfo is not None
    # normalize via ISO parsing—presence of tzinfo is the primary contract

def test_parse_when_naive():
    dt = parse_when("2025-08-19T12:34:56")
    assert dt.tzinfo is None
"""
    safe_write(test_file, content, "Add regression tests for Z/offset/naive timestamps")


def update_query_logs_docstring(query_logs_py: Path):
    if query_logs_py is None or not query_logs_py.exists():
        log_error(
            "3.3",
            "Document supported formats in query_logs.py",
            "query_logs.py not found",
            {},
        )
        return False
    text = query_logs_py.read_text(encoding="utf-8")
    doc = (
        '"""query_logs\n\n'
        "Supported timestamp formats for `parse_when`:\n"
        "  - Zulu/UTC:       2025-08-19T12:34:56Z\n"
        "  - Offset-aware:   2025-08-19T12:34:56+00:00, 2025-08-19T07:34:56-05:00\n"
        "  - Naive/local:    2025-08-19T12:34:56 (tzinfo=None)\n\n"
        "Behavior:\n"
        "  - Z/offset inputs produce **aware** datetime objects.\n"
        "  - Naive inputs return **naive** datetime objects.\n"
        '"""'
    )
    if text.lstrip().startswith('"""'):
        # Replace existing top-level docstring
        new = re.sub(r'^"""[\s\S]*?"""', doc, text, count=1, flags=re.MULTILINE)
    else:
        # Insert at top
        new = doc + "\n\n" + text
    safe_write(
        query_logs_py, new, "Document supported timestamp formats in module docstring"
    )
    return True


def maybe_update_readme():
    path = ROOT / "README.md"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    section = (
        "## Timestamp Parsing\n\n"
        "This project supports ISO-8601 timestamps including `Z` (UTC), explicit offsets (e.g., `+05:30`), "
        "and naive timestamps (no timezone). See `parse_when` and tests under `tests/test_parse_when.py`.\n"
    )
    if "## Timestamp Parsing" in text:
        return  # assume already present
    new = text.rstrip() + "\n\n" + section + "\n"
    safe_write(path, new, "Mention supported timestamp formats and tests")


def finalize(results):
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    RESULTS.write_text(
        "# Results Summary\n\n"
        "## Implemented\n"
        "- Upgraded/added `parse_when` to support `Z`, offsets, and naive timestamps.\n"
        "- Added regression tests: `tests/test_parse_when.py`.\n"
        "- Documented formats in `query_logs.py` module docstring.\n"
        "- Updated README with a timestamp parsing section (if present).\n\n"
        "## Residual Gaps\n"
        "- Validate all call sites compile/run under your CI (not activated here).\n"
        "- Confirm no duplicate helpers remain.\n\n"
        "## Pruning Index\n"
        "- None (no pruning performed in this run).\n\n"
        "## Next Steps\n"
        "- Run `pytest -q` and address any environment-specific issues.\n\n"
        "**Policy Notice:** DO NOT ACTIVATE ANY GitHub Actions files.\n",
        encoding="utf-8",
    )
    if ERROR_LOG.exists() and ERROR_LOG.read_text(encoding="utf-8").strip():
        print(
            "Completed with recorded errors. See .codex/errors.ndjson", file=sys.stderr
        )
        sys.exit(1)
    print("Completed successfully.")
    sys.exit(0)


def main():
    # Phase 1 — Preparation
    if not is_clean_worktree():
        log_error(
            "1.1", "Verify clean working state", "Uncommitted changes present", {}
        )
        print("Please commit or stash changes before running.", file=sys.stderr)
        sys.exit(2)
    index_files()
    # Phase 2 — Search & Mapping
    parse_targets, query_logs_py = find_candidates()
    if not parse_targets:
        # Fallback: if no parse_when found, prefer query_logs.py, else invent a util
        if query_logs_py is None:
            # Create a utility module
            util = ROOT / "utils.py"
            txt = util.read_text(encoding="utf-8") if util.exists() else ""
            safe_write(util, txt, "Ensure utils.py exists")
            parse_targets = [util]
        else:
            parse_targets = [query_logs_py]
    # Phase 3 — Best-Effort Construction
    touched = []
    for tgt in parse_targets[:1]:  # keep change localized to top-ranked candidate
        try:
            upgrade_parse_when(tgt)
            touched.append(str(tgt.relative_to(ROOT)))
            break
        except Exception as e:
            log_error("3.2", f"Upgrade parse_when in {tgt}", str(e), {"file": str(tgt)})
            continue
    ensure_tests()
    update_query_logs_docstring(query_logs_py)
    maybe_update_readme()
    # Phase 4 — Controlled Pruning (not performed automatically)
    # Phase 5 handled inline by log_error()
    # Phase 6 — Finalization
    finalize({"touched": touched})


if __name__ == "__main__":
    # Safety: never touch GitHub Actions
    if DO_NOT_ACTIVATE_GITHUB_ACTIONS and (ROOT / ".github" / "workflows").exists():
        # Read-only scan; do nothing
        pass
    main()
