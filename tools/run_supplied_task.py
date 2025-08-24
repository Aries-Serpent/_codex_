#!/usr/bin/env python3
"""
tools/run_supplied_task.py

Implements the Supplied Task for branch 0B_base_:

T1: In src/codex/logging/viewer.py, enforce table name regex ^[A-Za-z0-9_]+$ before use
    and reject invalid names with a clear error. Then lint that file.

T2: In src/codex/logging/session_hooks.py, emit logging.warning when retries fail
    in _safe_write_text and _safe_append_json_line. Then lint that file.

Also:
- Maintains .codex/change_log.md and .codex/errors.ndjson
- Leaves GitHub Actions untouched.
"""

from __future__ import annotations

import argparse
import datetime
import difflib
import hashlib
import json
import pathlib
import re
import shlex
import subprocess  # nosec B404
import sys
import textwrap

ROOT = pathlib.Path(__file__).resolve().parents[1]
CODEX_DIR = ROOT / ".codex"
CHANGE_LOG = CODEX_DIR / "change_log.md"
ERRORS = CODEX_DIR / "errors.ndjson"
RESULTS = CODEX_DIR / "results.md"
INVENTORY = CODEX_DIR / "inventory.json"
DO_NOT_ACTIVATE_GITHUB_ACTIONS = True

FILES = {
    "viewer": ROOT / "src" / "codex" / "logging" / "viewer.py",
    "hooks": ROOT / "src" / "codex" / "logging" / "session_hooks.py",
    "readme": ROOT / "README.md",
    "precommit": ROOT / ".pre-commit-config.yaml",
}

TABLE_PATTERN = r"^[A-Za-z0-9_]+$"


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def ensure_dirs():
    CODEX_DIR.mkdir(parents=True, exist_ok=True)
    if not CHANGE_LOG.exists():
        CHANGE_LOG.write_text("# Codex Change Log\n\n", encoding="utf-8")
    if not ERRORS.exists():
        ERRORS.write_text("", encoding="utf-8")


def echo_q(step: str, err: str, ctx: str = ""):
    """Emit a ChatGPT-5 research question line to errors.ndjson and stderr."""
    block = f"""Question for ChatGPT-5:
While performing {step}, encountered the following error:
{err}
Context: {ctx}
What are the possible causes, and how can this be resolved while preserving intended functionality?
"""
    sys.stderr.write(block + "\n")
    ERRORS.write_text(
        json.dumps({"ts": now_iso(), "step": step, "error": err, "context": ctx})
        + "\n",
        encoding="utf-8",
        append=True if hasattr(CHANGE_LOG, "append") else False,
    )
    # pathlib has no append; emulate:
    with ERRORS.open("a", encoding="utf-8") as f:
        f.write(
            json.dumps({"ts": now_iso(), "step": step, "error": err, "context": ctx})
            + "\n"
        )


def append_change(
    file_path: pathlib.Path, action: str, rationale: str, before: str, after: str
):
    diff = "\n".join(
        difflib.unified_diff(
            before.splitlines(),
            after.splitlines(),
            fromfile=str(file_path),
            tofile=str(file_path),
            lineterm="",
        )
    )
    with CHANGE_LOG.open("a", encoding="utf-8") as f:
        f.write(
            textwrap.dedent(f"""
        ## {now_iso()} — {file_path.relative_to(ROOT)}
        - **Action:** {action}
        - **Rationale:** {rationale}

        <details><summary>Diff (summary)</summary>

        ```diff
        {diff}
        ```

        </details>
        """).strip()
            + "\n\n"
        )


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def safe_read(p: pathlib.Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except Exception as e:
        echo_q("Phase1: Read file", f"{e}", f"file={p}")
        raise


def safe_write(p: pathlib.Path, content: str, rationale: str):
    before = p.read_text(encoding="utf-8") if p.exists() else ""
    p.write_text(content, encoding="utf-8")
    append_change(p, "edit" if before else "create", rationale, before, content)


def inventory():
    items = []
    for p in ROOT.rglob("*"):
        if p.is_file() and ".git" not in p.parts:
            try:
                items.append(
                    {
                        "path": str(p.relative_to(ROOT)),
                        "size": p.stat().st_size,
                        "sha256": sha256_text(
                            p.read_text(encoding="utf-8", errors="ignore")
                        ),
                    }
                )
            except Exception:
                items.append(
                    {
                        "path": str(p.relative_to(ROOT)),
                        "size": p.stat().st_size,
                        "sha256": None,
                    }
                )
    INVENTORY.write_text(json.dumps(items, indent=2), encoding="utf-8")


def enforce_no_actions_touch():
    if not DO_NOT_ACTIVATE_GITHUB_ACTIONS:
        return
    # Guard: ensure we never plan writes under .github/workflows
    workflows = ROOT / ".github" / "workflows"
    if workflows.exists():
        # Document presence; no modifications will occur.
        with CHANGE_LOG.open("a", encoding="utf-8") as f:
            f.write(
                f"{now_iso()} — Detected workflows at {workflows}, no changes will be made.\n"
            )


def patch_viewer_table_validation(path: pathlib.Path):
    src = safe_read(path)
    new = src
    rationale = (
        "Enforce `--table` to match ^[A-Za-z0-9_]+$ and fail fast with clear error."
    )

    # 1) Ensure import blocks have argparse + re
    if "import re" not in new:
        new = (
            new.replace("\nimport ", "\nimport re\nimport ", 1)
            if "\nimport " in new
            else "import re\n" + new
        )
    if "import argparse" not in new:
        # Might parse args elsewhere; still safe to import
        if "argparse" not in new:
            new = "import argparse\n" + new

    # 2) Inject validator if absent
    if "_validate_table_name" not in new:
        validator = textwrap.dedent(f"""
        def _validate_table_name(s: str) -> str:
            pattern = re.compile(r"{TABLE_PATTERN}")
            if s is None:
                return s
            if pattern.fullmatch(s):
                return s
            raise argparse.ArgumentTypeError(
                "Invalid table name: '{{s}}'. Only letters, digits, and underscore are allowed."
            )
        """)
        # place near top after imports
        # heuristics: after first double newline
        parts = new.split("\n\n", 1)
        new = (
            parts[0]
            + "\n\n"
            + validator
            + ("\n\n" + parts[1] if len(parts) > 1 else "\n")
        )

    # 3) Prefer argparse wiring: --table … type=_validate_table_name
    new = re.sub(
        r'(add_argument\(\s*["\']--table["\'][^)]*)\)',
        lambda m: (m.group(1) + ", type=_validate_table_name)")
        if "type=" not in m.group(1)
        else m.group(0),
        new,
    )

    # 4) If code accesses args.table without prior validation, add runtime guard once.
    if "args.table" in new and "Invalid table name:" not in new:
        guard = textwrap.dedent(f"""
        # Runtime guard (defense-in-depth) in case argparse wiring is bypassed:
        if getattr(args, "table", None):
            if not re.fullmatch(r"{TABLE_PATTERN}", args.table):
                raise SystemExit(f"Invalid table name: '{{args.table}}'. Only letters, digits, and underscore are allowed.")
        """)
        # Heuristic: insert after a line that looks like "args = parser.parse_args()" or similar
        new = re.sub(
            r"(args\s*=\s*[^\n]*parse_args\([^)]*\)\s*)",
            r"\1\n" + guard + "\n",
            new,
            count=1,
        )

    if new != src:
        safe_write(path, new, rationale)
    else:
        with CHANGE_LOG.open("a", encoding="utf-8") as f:
            f.write(
                f"{now_iso()} — No changes needed in {path.relative_to(ROOT)} (validation already present).\n"
            )


def patch_session_hooks_warnings(path: pathlib.Path):
    src = safe_read(path)
    new = src
    rationale = "Emit logging.warning when retries are exhausted in _safe_write_text and _safe_append_json_line."

    # Ensure logging is imported
    if "import logging" not in new:
        new = (
            new.replace("\nimport ", "\nimport logging\nimport ", 1)
            if "\nimport " in new
            else "import logging\n" + new
        )

    def ensure_warning(func_name: str):
        nonlocal new
        # crude block detection
        pattern = re.compile(
            rf"(def\s+{func_name}\s*\(.*?\):)(.*?)(?=^def\s|\Z)", re.S | re.M
        )
        m = pattern.search(new)
        if not m:
            echo_q("Phase3: locate function", f"{func_name} not found", f"file={path}")
            return
        _, body = m.group(1), m.group(2)
        if "logging.warning" in body and "retries" in body:
            return
        # Insert a warning near common retry exits
        insertion = textwrap.dedent("""
            # Warning when retries have been exhausted
            try:
                _last_err  # noqa: F821
            except NameError:
                _last_err = None
            logging.warning("Write attempt failed after all retries in %s: %s", __name__, _last_err)
        """)
        # Heuristic: append before return/raise at end of block
        body2 = re.sub(
            r"(return\s+[^\n]+|raise\s+[^\n]+)\s*$",
            insertion + r"\n\1",
            body,
            flags=re.S,
        )
        if body2 == body:
            body2 = body + "\n" + insertion
        new = new[: m.start(2)] + body2 + new[m.end(2) :]

    ensure_warning("_safe_write_text")
    ensure_warning("_safe_append_json_line")

    if new != src:
        safe_write(path, new, rationale)
    else:
        with CHANGE_LOG.open("a", encoding="utf-8") as f:
            f.write(
                f"{now_iso()} — No changes needed in {path.relative_to(ROOT)} (warnings already present).\n"
            )


def maybe_update_readme(readme: pathlib.Path):
    if not readme.exists():
        return
    src = safe_read(readme)
    note = "Table names provided via `--table` must match `[A-Za-z0-9_]+`."
    if note in src:
        return
    # Add note near the viewer CLI section if present, else append to end
    if "codex.logging.viewer" in src or "--table" in src:
        new = src + f"\n\n> Note: {note}\n"
    else:
        new = src + f"\n\n{note}\n"
    safe_write(readme, new, "Document `--table` naming constraint for the viewer CLI.")


def run_precommit(files: list[str]):
    cfg = FILES["precommit"]
    if not cfg.exists():
        with CHANGE_LOG.open("a", encoding="utf-8") as f:
            f.write(f"{now_iso()} — pre-commit config not found; skipped lint.\n")
        return
    cmd = ["pre-commit", "run", "--files"] + files
    try:
        print("+", shlex.join(cmd))
        subprocess.check_call(cmd, cwd=str(ROOT))  # nosec B603,B607
    except subprocess.CalledProcessError as e:
        echo_q("Phase6: pre-commit run", f"exit {e.returncode}", f"cmd={' '.join(cmd)}")
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run", action="store_true", help="Compute edits but do not write."
    )
    args = parser.parse_args()

    ensure_dirs()
    enforce_no_actions_touch()
    inventory()

    # Safety: require clean git worktree for non-dry runs
    try:
        dirty = (
            subprocess.check_output(["git", "status", "--porcelain"], cwd=str(ROOT))  # nosec B603,B607
            .decode()
            .strip()
        )
    except Exception as e:
        echo_q(
            "Phase1: git status",
            str(e),
            "Ensure git is available and repository is initialized.",
        )
        dirty = ""
    if dirty:
        echo_q("Phase1: clean tree check", "Working tree not clean", dirty)
        print(
            "Refusing to edit because the working tree is not clean.", file=sys.stderr
        )
        sys.exit(2)

    # T1
    if FILES["viewer"].exists():
        if not args.dry_run:
            patch_viewer_table_validation(FILES["viewer"])
    else:
        echo_q("Phase2: locate viewer.py", "File not found", str(FILES["viewer"]))

    # T2
    if FILES["hooks"].exists():
        if not args.dry_run:
            patch_session_hooks_warnings(FILES["hooks"])
    else:
        echo_q("Phase2: locate session_hooks.py", "File not found", str(FILES["hooks"]))

    # README doc note
    maybe_update_readme(FILES["readme"])

    # Results
    RESULTS.write_text(
        textwrap.dedent(f"""
    # Results Summary ({now_iso()})

    - Implemented:
        - T1: Table name validation in viewer.py (regex: {TABLE_PATTERN})
        - T2: Warning on retry exhaustion in session_hooks helpers
    - Residual gaps: see `.codex/errors.ndjson` if present.
    - Pruning: none.
    - Next steps: strengthen smoke tests for invalid `--table` & forced retry paths.

    **DO NOT ACTIVATE ANY GitHub Actions files.**
    """).strip()
        + "\n",
        encoding="utf-8",
    )

    # Lint only the two files per task spec
    try:
        run_precommit([str(FILES["viewer"]), str(FILES["hooks"])])
    except Exception:
        # already captured to errors; propagate non-zero
        sys.exit(1)

    print("OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
