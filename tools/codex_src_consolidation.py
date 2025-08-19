#!/usr/bin/env python3
# tools/codex_src_consolidation.py
# Purpose: Unify SOT at src/codex, update imports/tests/tooling,
# log changes & errors, and finalize results.
# Constraint: DO NOT ACTIVATE ANY GitHub Actions files.

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# --------------------------- Utilities & Logging ---------------------------


def repo_root() -> Path:
    try:
        p = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True
        ).strip()
        return Path(p)
    except Exception:
        return Path.cwd()


R = repo_root()
COD = R / ".codex"
COD.mkdir(exist_ok=True, parents=True)
CHANGE_LOG = COD / "change_log.md"
ERRORS = COD / "errors.ndjson"
RESULTS = COD / "results.md"
INVENTORY = COD / "inventory.json"

# Never touch actions
DO_NOT_ACTIVATE_GHA = True
os.environ["DO_NOT_ACTIVATE_GITHUB_ACTIONS"] = "true"


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def log_change(
    path: Path,
    action: str,
    rationale: str,
    before: Optional[str] = None,
    after: Optional[str] = None,
):
    CHANGE_LOG.parent.mkdir(parents=True, exist_ok=True)
    if not CHANGE_LOG.exists():
        CHANGE_LOG.write_text("# .codex/change_log.md\n\n", encoding="utf-8")
    entry = (
        f"## {now_iso()} — {action}\n"
        f"**File:** {path.as_posix()}\n"
        f"**Why:** {rationale}\n"
    )
    if before or after:
        entry += "```diff\n"
        if before:
            entry += f"- {before}\n"
        if after:
            entry += f"+ {after}\n"
        entry += "```\n"
    entry += "\n"
    with CHANGE_LOG.open("a", encoding="utf-8") as f:
        f.write(entry)


def log_error(step: str, err: str, ctx: str):
    line = {
        "ts": now_iso(),
        "step": step,
        "error": err,
        "context": ctx,
        "research_question": (
            "Question for ChatGPT-5:\n"
            f"While performing [{step}], encountered the following error:\n{err}\n"
            f"Context: {ctx}\n"
            "What are the possible causes, and how can this be resolved while "
            "preserving intended functionality?"
        ),
    }
    with ERRORS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")
    print(line["research_question"], file=sys.stderr)


def run(cmd: List[str]) -> Tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, cwd=R, text=True, capture_output=True)
        return (p.returncode, p.stdout, p.stderr)
    except Exception as e:
        return (1, "", str(e))


def clean_state_best_effort():
    code, out, err = run(["git", "status", "--porcelain"])
    if code == 0 and out.strip():
        log_error("1.1 CLEAN", "Working tree not clean", out.strip())
    elif code != 0:
        log_error("1.1 CLEAN", f"git status failed ({code})", err.strip())


# --------------------------- Inventory ---------------------------

SKIP_DIRS = {".git", ".venv", "venv", ".mypy_cache", ".ruff_cache", "__pycache__"}


def build_inventory() -> Dict:
    items = []
    for p in R.rglob("*"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.is_file():
            role = (
                "code"
                if p.suffix in {".py", ".sh", ".js", ".ts", ".sql", ".html", ".css"}
                else "other"
            )
            items.append(
                {"path": str(p.relative_to(R)), "role": role, "size": p.stat().st_size}
            )
    inv = {"root": str(R), "count": len(items), "items": items}
    INVENTORY.write_text(json.dumps(inv, indent=2), encoding="utf-8")
    return inv


# --------------------------- Core Paths ---------------------------

D_TOP = R / "codex"
S_SRC = R / "src" / "codex"
TESTS = R / "tests"


def exists_summary() -> Dict[str, bool]:
    return {
        "codex_dir": D_TOP.exists(),
        "src_codex_dir": S_SRC.exists(),
        "tests_dir": TESTS.exists(),
    }


# --------------------------- Import Rewrite (Python) ---------------------------

IMPORT_RE = re.compile(r"^(?P<indent>\s*)(from|import)\s+codex(\b|\.)(?P<rest>.*)$")


def rewrite_python_imports_to_src_codex(path: Path) -> bool:
    """Best-effort line-by-line transform.

    Avoids comments/strings by limiting to import lines.
    """
    changed = False
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception as e:
        log_error("3.2 REWRITE_READ", str(e), f"{path}")
        return False
    new_lines = []
    for line in lines:
        m = IMPORT_RE.match(line)
        if m:
            indent = m.group("indent")
            if line.strip().startswith("import codex"):  # e.g., "import codex as c"
                # import src.codex as codex  (preserve alias if present)
                alias = ""
                if " as " in line:
                    alias = line.split(" as ", 1)[1].strip()
                else:
                    alias = "codex"
                newline = f"{indent}import src.codex as {alias}"
            else:
                # from codex[.x] import Y => from src.codex[.x] import Y
                newline = re.sub(r"from\s+codex", "from src.codex", line, count=1)
            new_lines.append(newline)
            changed = True
        else:
            new_lines.append(line)
    if changed:
        try:
            path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            log_change(
                path,
                "rewrite-imports",
                "Normalize imports to src.codex",
                before="from/import codex …",
                after="from/import src.codex …",
            )
        except Exception as e:
            log_error("3.2 REWRITE_WRITE", str(e), f"{path}")
            return False
    return changed


def rewrite_tree_py_to_src_codex(root: Path) -> int:
    count = 0
    for p in root.rglob("*.py"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.parts[0] in (".codex", ".github"):
            continue
        if p.is_file():
            if rewrite_python_imports_to_src_codex(p):
                count += 1
    return count


# --------------------------- Tooling & Docs ---------------------------


def ensure_pytest_src_pythonpath():
    # Prefer pytest.ini if exists; else create minimal file.
    ini = R / "pytest.ini"
    if ini.exists():
        txt = ini.read_text(encoding="utf-8")
        if "pythonpath = src" not in txt:
            txt2 = txt.rstrip() + "\n\n[pytest]\npythonpath = src\ntestpaths = tests\n"
            ini.write_text(txt2, encoding="utf-8")
            log_change(
                ini,
                "update",
                "Ensure pytest discovers src layout",
                after="pythonpath = src, testpaths = tests",
            )
    else:
        content = "[pytest]\npythonpath = src\ntestpaths = tests\n"
        ini.write_text(content, encoding="utf-8")
        log_change(
            ini,
            "create",
            "Introduce pytest config for src layout",
            after=content.strip(),
        )


def update_docs_paths():
    # Replace " codex/" path references in docs with " src/codex/"
    candidates = (
        [R / "README.md"] + list((R / "documentation").rglob("*.md"))
        if (R / "documentation").exists()
        else [R / "README.md"]
    )
    for md in candidates:
        if not md.exists():
            continue
        try:
            txt = md.read_text(encoding="utf-8")
            new = txt.replace(" codex/", " src/codex/").replace(
                "`codex/`", "`src/codex/`"
            )
            if new != txt:
                md.write_text(new, encoding="utf-8")
                log_change(
                    md,
                    "update-docs",
                    "Align doc paths to src/codex",
                    before="… codex/ …",
                    after="… src/codex/ …",
                )
        except Exception as e:
            log_error("3.3 DOCS", str(e), f"{md}")


def add_smoke_test():
    if not TESTS.exists():
        TESTS.mkdir(parents=True, exist_ok=True)
    t = TESTS / "test_import_codex.py"
    if not t.exists():
        content = """# smoke: import from src layout
def test_import_src_codex():
    import importlib
    m = importlib.import_module("src.codex")
    assert m is not None
"""
        t.write_text(content, encoding="utf-8")
        log_change(
            t,
            "create",
            "Add smoke test for src.codex import",
            after="test_import_src_codex()",
        )


# --------------------------- Symlink / Proxy / Removal ---------------------------


def safe_rename_legacy_codex():
    ts = time.strftime("%Y%m%d_%H%M%S")
    new = R / f"codex_legacy_{ts}"
    try:
        D_TOP.rename(new)
        log_change(
            D_TOP, "rename", "Preserve legacy top-level codex directory", after=new.name
        )
        return new
    except Exception as e:
        log_error("3.2 RENAME", str(e), "Preserving legacy codex before symlink/proxy")
        return None


def create_symlink_codex_to_src() -> bool:
    try:
        if D_TOP.exists():
            renamed = safe_rename_legacy_codex()
            if renamed is None:
                return False
        os.symlink(S_SRC.as_posix(), D_TOP.as_posix(), target_is_directory=True)
        log_change(
            D_TOP,
            "symlink",
            "codex → src/codex to unify SOT",
            after=f"{D_TOP} -> {S_SRC}",
        )
        return True
    except Exception as e:
        log_error("3.2 SYMLINK", str(e), f"Attempted symlink {D_TOP} -> {S_SRC}")
        return False


def proxy_codex_package() -> bool:
    """
    Windows fallback if symlink fails: remove/rename legacy and create an empty
    'codex' pkg that forwards imports by modifying sys.path to include src at
    runtime and re-importing.
    """
    try:
        if D_TOP.exists():
            renamed = safe_rename_legacy_codex()
            if renamed is None:
                return False
        D_TOP.mkdir(parents=True, exist_ok=True)
        init = D_TOP / "__init__.py"
        init.write_text(
            '"""Proxy package forwarding to src.codex (runtime path injection)."""\n'
            "import os, sys, pathlib, importlib\n"
            "ROOT = pathlib.Path(__file__).resolve().parent.parent\n"
            "SRC = ROOT / 'src'\n"
            "if SRC.as_posix() not in sys.path:\n"
            "    sys.path.insert(0, SRC.as_posix())\n"
            "mod = importlib.import_module('codex')\n"
            "# resolves to src/codex after path injection\n"
            "globals().update(mod.__dict__)\n",
            encoding="utf-8",
        )
        log_change(
            init,
            "create",
            "Proxy package for src layout fallback",
            after="codex/__init__.py forwarding",
        )
        return True
    except Exception as e:
        log_error("3.2 PROXY", str(e), "Create proxy package")
        return False


# --------------------------- Main Routine ---------------------------


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--mode",
        choices=["auto", "symlink", "rewrite", "proxy"],
        default="auto",
        help="How to align codex with src/codex",
    )
    args = ap.parse_args()

    print("== Phase 1: Prep ==")
    clean_state_best_effort()
    inv = build_inventory()

    # Guard: never touch GHA workflows
    gha = R / ".github" / "workflows"
    if gha.exists():
        print(
            "NOTE: .github/workflows present; this script does not modify it "
            "and will not activate anything."
        )

    print("== Phase 2: Mapping ==")
    summary = exists_summary()
    print("Paths:", summary)

    print("== Phase 3: Construction ==")
    constructed = {"symlink": False, "proxy": False, "rewrites": 0}

    # Ensure src/codex exists
    if not S_SRC.exists():
        log_error("3.1 SOT", "src/codex not found", str(S_SRC))
        # Best-effort: if top-level D exists, keep it and let tests rely on it
    else:
        # Normalize: handle D_TOP
        chosen = args.mode
        if chosen == "auto":
            # Try symlink first; if fails, proxy; then do rewrites
            if create_symlink_codex_to_src():
                constructed["symlink"] = True
            elif proxy_codex_package():
                constructed["proxy"] = True
        elif chosen == "symlink":
            constructed["symlink"] = create_symlink_codex_to_src()
        elif chosen == "proxy":
            constructed["proxy"] = proxy_codex_package()

    # Tooling alignment and import rewrites (tests + code) if asked or needed
    ensure_pytest_src_pythonpath()
    update_docs_paths()
    add_smoke_test()

    # Always attempt safe rewrites to src.codex if repository policy requires
    # direct src.codex references
    rewrites = 0
    for root in [
        R / "tests",
        R / "tools",
        R / "scripts",
        R / "src",
        R / "documentation",
        R,
    ]:
        if root.exists():
            rewrites += rewrite_tree_py_to_src_codex(root)
    constructed["rewrites"] = rewrites

    print("== Phase 4: Pruning ==")
    # Evidence-based pruning: if symlink/proxy created, we already renamed legacy
    # folder.
    # Additional duplication pruning would be done here if a diff or equality
    # pass proves duplication.

    print("== Phase 5: Errors Recorded ==")
    # Errors already appended to ERRORS as they occur.

    print("== Phase 6: Finalization ==")
    # Results
    results = {
        "timestamp": now_iso(),
        "paths": summary,
        "constructed": constructed,
        "inventory_count": inv.get("count", 0),
        "explicit_warning": "DO NOT ACTIVATE ANY GitHub Actions files.",
        "next_steps": [
            "Run pytest to validate imports/tests: `pytest -q`",
            "If Windows with no symlink support, use --mode proxy "
            "(already attempted in auto).",
            "Review .codex/change_log.md and .codex/errors.ndjson",
        ],
    }
    RESULTS.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))

    # Exit non-zero if unresolved errors exist
    err_count = (
        sum(1 for _ in ERRORS.open("r", encoding="utf-8"))
        if ERRORS.exists() and ERRORS.stat().st_size
        else 0
    )
    sys.exit(1 if err_count else 0)


if __name__ == "__main__":
    main()
