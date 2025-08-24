#!/usr/bin/env python3
# codex_repo_scout.py
# End-to-end workflow implementing the phased block for `_codex_` / 0B_base_
# Writes outputs under ./.codex/ only. No CI activation, no external calls.

import json
import re
import shutil
import subprocess
import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path.cwd()
CODEX_DIR = ROOT / ".codex"
CHANGE_LOG = CODEX_DIR / "change_log.md"
ERROR_LOG = CODEX_DIR / "errors.ndjson"
RESULTS = CODEX_DIR / "results.md"
INVENTORY = CODEX_DIR / "inventory.json"
SMOKE = CODEX_DIR / "smoke_checks.json"
MAPPING_MD = CODEX_DIR / "mapping_table.md"


@dataclass
class UnfinishedItem:
    """Represents an unfinished marker detected in a source file."""

    line: int
    kind: str
    text: str


@dataclass
class ScanResult:
    """Outcome of scanning a file for unfinished code."""

    path: str
    unfinished: List[UnfinishedItem] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


# -------- utilities --------
def now_iso() -> str:
    """Return the current UTC time in ISO 8601 format."""
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def ensure_codex_dir() -> None:
    """Create required `.codex` files if they do not already exist."""

    CODEX_DIR.mkdir(exist_ok=True)
    if not CHANGE_LOG.exists():
        CHANGE_LOG.write_text(
            f"# .codex/change_log.md\n\nCreated {now_iso()}\n\n", encoding="utf-8"
        )
    if not ERROR_LOG.exists():
        ERROR_LOG.write_text("", encoding="utf-8")
    if not RESULTS.exists():
        RESULTS.write_text("# .codex/results.md\n\n(placeholder)\n", encoding="utf-8")


def append_change(
    file: Path, action: str, rationale: str, before: str = "", after: str = ""
) -> None:
    """Append an entry to `.codex/change_log.md` describing a modification."""

    with CHANGE_LOG.open("a", encoding="utf-8") as f:
        f.write(f"## {now_iso()} — {action}\n")
        f.write(f"- **file**: {file}\n- **rationale**: {rationale}\n")
        if before or after:
            f.write("```diff\n")
            f.write(
                f"- BEFORE: {before.strip()[:600]}\n+ AFTER : {after.strip()[:600]}\n"
            )
            f.write("```\n")
        f.write("\n")


def emit_error(
    step_num: str, step_desc: str, err_msg: str, context: str, path: str = ""
):
    # Console echo per template
    print(
        "Question for ChatGPT-5:\n"
        f"While performing [{step_num}: {step_desc}], encountered the following error:\n"
        f"{err_msg}\n"
        f"Context: {context}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n",
        file=sys.stderr,
    )
    payload = {
        "timestamp": now_iso(),
        "step": {"id": step_num, "desc": step_desc},
        "error": err_msg,
        "context": context,
        "path": path,
    }
    with ERROR_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def run(cmd: List[str], step: str, check: bool = False) -> Tuple[int, str, str]:
    """Run a subprocess, capturing output and optionally raising on failure."""

    try:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        if check and proc.returncode != 0:
            raise RuntimeError(
                f"exit={proc.returncode}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
            )
        return proc.returncode, proc.stdout, proc.stderr
    except Exception as e:  # pragma: no cover - defensive
        emit_error(step, f"run {' '.join(cmd)}", str(e), "subprocess invocation")
        return 127, "", str(e)


# -------- Phase 1 --------
def phase1_prepare():
    ensure_codex_dir()

    # 1.1 Repo root & clean state
    step = "1.1"
    try:
        rc, _, _ = run(["git", "rev-parse", "--show-toplevel"], step)
        # cleanliness
        rc, out, _ = run(["git", "status", "--porcelain"], step)
        if rc == 0 and out.strip():
            emit_error(
                step,
                "Verify clean working state",
                "Working tree not clean",
                out.strip(),
            )
    except Exception as e:
        emit_error(step, "Detect repo root", str(e), "fallback to CWD")

    # 1.2 Load README/constraints
    step = "1.2"
    readmes = []
    for name in ("README.md", "README_UPDATED.md"):
        p = ROOT / name
        if p.exists():
            readmes.append(p.read_text(encoding="utf-8", errors="ignore"))
    combined = "\n\n".join(readmes)
    if "DO NOT ACTIVATE ANY GitHub Actions files" not in combined:
        # enforce anyway; log notice
        emit_error(
            step,
            "Enforce Actions constraint",
            "Constraint not found in README text; enforcing locally.",
            "Set DO_NOT_ACTIVATE_GITHUB_ACTIONS=True",
        )
    append_change(
        CODEX_DIR, "Initialize .codex and constraints", "Prepare logs and guardrails"
    )

    # 1.3 Inventory
    step = "1.3"
    ignore_dirs = {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules"}
    inv = []
    for path in ROOT.rglob("*"):
        try:
            if any(part in ignore_dirs for part in path.parts):
                continue
            if path.is_dir():
                continue
            rel = path.relative_to(ROOT).as_posix()
            st = path.stat()
            # classify
            ext = path.suffix.lower()
            lang = (
                "python"
                if ext == ".py"
                else "bash"
                if ext in {".sh", ".bash", ".zsh"}
                else "javascript"
                if ext in {".js", ".jsx", ".mjs"}
                else "typescript"
                if ext in {".ts", ".tsx"}
                else "sql"
                if ext == ".sql"
                else "html"
                if ext == ".html"
                else "dockerfile"
                if path.name.lower() == "dockerfile" or ext == ".dockerfile"
                else "yaml"
                if ext in {".yml", ".yaml"}
                else "markdown"
                if ext in {".md", ".markdown"}
                else "other"
            )
            inv.append(
                {
                    "path": rel,
                    "size": st.st_size,
                    "mtime": int(st.st_mtime),
                    "lang": lang,
                }
            )
        except Exception as e:
            emit_error(step, "Inventory walk error", str(e), f"path={path}")
    INVENTORY.write_text(json.dumps(inv, indent=2), encoding="utf-8")
    append_change(
        INVENTORY, "Create inventory.json", "Repo file inventory written under .codex"
    )


# -------- Phase 2 --------
def phase2_search_mapping():
    # 2.1 Intent captured in this function docstring
    # 2.2 Related components (by conventional dirs)
    candidates = []
    for c in ["src/codex", "src", "tests", "scripts", "tools", "codex"]:
        p = ROOT / c
        if p.exists():
            candidates.append(c)

    # 2.3 Rank (simple heuristic as per symbolic equation)
    def path_score(path: str) -> float:
        p = ROOT / path
        files = list(p.rglob("*")) if p.exists() else []
        code_files = [
            f
            for f in files
            if f.suffix.lower() in {".py", ".js", ".ts", ".sh", ".sql", ".html"}
        ]
        txt = ""
        for f in code_files[:200]:  # cap reads
            try:
                txt += f.read_text(encoding="utf-8", errors="ignore") + "\n"
            except Exception:
                pass
        hints = len(
            re.findall(
                r"\b(TODO|FIXME|WIP|TBD|XXX|NotImplemented)\b", txt, flags=re.IGNORECASE
            )
        )
        present_tests = 1 if "tests" in path.split("/") else 0
        risk = 0.3 if "scripts" in path.split("/") else 0.1
        return 0.5 * len(code_files) + 0.3 * hints + 0.4 * present_tests - 0.2 * risk

    ranked = sorted(
        ([c, path_score(c)] for c in candidates), key=lambda x: x[1], reverse=True
    )
    # 2.4 mapping table (markdown)
    lines = [
        "# Mapping Table",
        "",
        "| Task | Candidate Assets | Rationale |",
        "|---|---|---|",
    ]
    rationale = "Primary locations for source/tests/scripts with highest likelihood of unfinished markers."
    cand_list = ", ".join([c for c, _ in ranked]) if ranked else "(none)"
    lines.append(f"| unfinished-code-harvest | {cand_list} | {rationale} |")
    MAPPING_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    append_change(
        MAPPING_MD, "Create mapping_table.md", "Ranked candidate asset locations"
    )


# -------- Phase 3 scanning --------
UNFINISHED_PAT = re.compile(
    r"\b(TODO|FIXME|WIP|TBD|XXX|NOT\s*IMPLEMENTED|NotImplemented)\b", re.IGNORECASE
)
PY_NOTIMPL_PAT = re.compile(r"raise\s+NotImplementedError\b")
PY_PASS_OR_ELLIPSIS = re.compile(r"^\s*(pass|\.{3})\s*$")


def scan_file(relpath: str) -> ScanResult:
    """Scan a file for unfinished code markers and return a structured result."""

    path = ROOT / relpath
    result = ScanResult(path=relpath)
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        emit_error("3.2", "Read file", str(e), f"path={relpath}", relpath)
        return result

    # common markers
    for i, line in enumerate(text.splitlines(), start=1):
        if UNFINISHED_PAT.search(line):
            result.unfinished.append(
                UnfinishedItem(line=i, kind="marker", text=line.strip())
            )

    # language specifics
    if relpath.endswith(".py"):
        try:
            import ast

            tree = ast.parse(text)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    body_src = [
                        text.splitlines()[b.lineno - 1]
                        for b in node.body
                        if hasattr(b, "lineno")
                    ]
                    if body_src and all(
                        PY_PASS_OR_ELLIPSIS.match(x or "") for x in body_src
                    ):
                        result.unfinished.append(
                            UnfinishedItem(
                                line=node.lineno,
                                kind="stub_fn",
                                text=f"function {node.name} appears stubbed",
                            )
                        )
            if PY_NOTIMPL_PAT.search(text):
                for i, line in enumerate(text.splitlines(), start=1):
                    if "NotImplementedError" in line:
                        result.unfinished.append(
                            UnfinishedItem(
                                line=i,
                                kind="not_implemented",
                                text=line.strip(),
                            )
                        )
        except Exception as e:  # pragma: no cover - defensive
            emit_error("3.2", "Python AST parse", str(e), f"path={relpath}", relpath)

    if relpath.endswith((".js", ".ts", ".tsx", ".jsx")):
        for i, line in enumerate(text.splitlines(), start=1):
            if "throw new Error" in line and "Not Implemented" in line:
                result.unfinished.append(
                    UnfinishedItem(line=i, kind="not_implemented", text=line.strip())
                )

    if relpath.endswith((".sh", ".bash", ".zsh")):
        for i, line in enumerate(text.splitlines(), start=1):
            if "exit 1" in line and ("TODO" in line or "TBD" in line):
                result.unfinished.append(
                    UnfinishedItem(line=i, kind="bash_todo_exit", text=line.strip())
                )

    if relpath.endswith(".sql"):
        for i, line in enumerate(text.splitlines(), start=1):
            if "--" in line and UNFINISHED_PAT.search(line):
                result.unfinished.append(
                    UnfinishedItem(line=i, kind="sql_marker", text=line.strip())
                )

    if relpath.endswith(".html"):
        for i, line in enumerate(text.splitlines(), start=1):
            if "<!--" in line and UNFINISHED_PAT.search(line):
                result.unfinished.append(
                    UnfinishedItem(line=i, kind="html_marker", text=line.strip())
                )

    return result


def collect_code_paths() -> List[str]:
    """Return repository paths for files considered source code."""

    ignore_dirs = {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules"}
    code_exts = {
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".sh",
        ".bash",
        ".zsh",
        ".sql",
        ".html",
    }
    paths: List[str] = []
    for p in ROOT.rglob("*"):
        if p.is_dir() or any(part in ignore_dirs for part in p.parts):
            continue
        if p.suffix.lower() in code_exts or p.name.lower() == "dockerfile":
            try:
                paths.append(p.relative_to(ROOT).as_posix())
            except Exception:
                pass
    return paths


def optional_compile_python(py_paths: List[str]) -> Dict[str, Dict[str, Any]]:
    results: Dict[str, Dict[str, Any]] = {}
    for rel in py_paths:
        step = "3.4"
        try:
            src = (ROOT / rel).read_text(encoding="utf-8", errors="ignore")
            compile(src, rel, "exec")
            results[rel] = {"compiled": True}
        except Exception as e:
            results[rel] = {"compiled": False, "error": str(e)}
            emit_error(step, "Python compile", str(e), f"path={rel}", rel)
    return results


def optional_run_pytest():
    # run pytest if available
    step = "3.4"
    try:
        rc, out, err = run(["pytest", "-q"], step)
        return {"ran": (rc != 127), "returncode": rc, "stdout": out, "stderr": err}
    except Exception as e:
        emit_error(step, "pytest run", str(e), "pytest invocation")
        return {"ran": False}


def optional_run_ruff():
    step = "3.4"
    exe = shutil.which("ruff")
    if not exe:
        return {"ran": False}
    rc, out, err = run([exe, "check", "--format", "json", "."], step)
    try:
        data = json.loads(out or "[]")
    except Exception:
        data = []
    if rc not in (0, 1):  # 0=clean, 1=lint findings
        emit_error(step, "ruff check", f"exit={rc}", err[:500])
    return {"ran": True, "exit": rc, "findings": data}


def phase3_execute() -> None:
    code_paths = collect_code_paths()
    unfinished: List[ScanResult] = []
    for rel in code_paths:
        res = scan_file(rel)
        if res.unfinished:
            unfinished.append(res)
    # Optional compile / tests / ruff
    py_paths = [p for p in code_paths if p.endswith(".py")]
    compile_res = optional_compile_python(py_paths)
    smoke = {"python_compile": compile_res}

    pytest_res = optional_run_pytest()
    if pytest_res.get("ran"):
        smoke["pytest"] = {
            "returncode": pytest_res.get("returncode"),
            "stdout": pytest_res.get("stdout", "")[-10000:],
            "stderr": pytest_res.get("stderr", "")[-5000:],
        }

    ruff_res = optional_run_ruff()
    if ruff_res.get("ran"):
        smoke["ruff"] = {
            "exit": ruff_res.get("exit"),
            "count": len(ruff_res.get("findings", [])),
        }

    SMOKE.write_text(json.dumps(smoke, indent=2), encoding="utf-8")
    append_change(SMOKE, "Write smoke_checks.json", "Compile/test/lint snapshot")

    # Aggregate results.md
    unfinished_count = sum(len(entry.unfinished) for entry in unfinished)
    RESULTS.write_text("# .codex/results.md\n\n", encoding="utf-8")
    with RESULTS.open("a", encoding="utf-8") as f:
        f.write("## Implemented Artifacts\n")
        f.write(
            "- inventory.json\n- mapping_table.md\n- smoke_checks.json\n- errors.ndjson\n\n"
        )
        f.write("## Unfinished Code Index\n")
        f.write(f"- Files with unfinished markers: **{len(unfinished)}**\n")
        f.write(f"- Total unfinished signals: **{unfinished_count}**\n\n")
        if unfinished:
            f.write("| File | Line | Kind | Snippet |\n|---|---:|---|---|\n")
            for entry in unfinished:
                for item in entry.unfinished:
                    snip = item.text.replace("|", "\\|")
                    f.write(
                        f"| {entry.path} | {item.line} | {item.kind} | `{snip[:160]}` |\n"
                    )
        f.write("\n## Errors Captured as Research Questions\n")
        try:
            lines = ERROR_LOG.read_text(encoding="utf-8").strip().splitlines()
        except Exception:
            lines = []
        f.write(f"- Total: **{len(lines)}**\n\n")
        f.write("## Pruning Decisions\n- None (detection rules retained)\n\n")
        f.write(
            "## Next Steps\n- Review unfinished index; prioritize high-signal files\n"
        )
        f.write("- Address compile/test failures recorded in smoke_checks.json\n")
        f.write(
            "- Update README references only after fixes are in-place (no CI activation)\n"
        )
        f.write("\n**Constraint:** DO NOT ACTIVATE ANY GitHub Actions files.\n")
    append_change(RESULTS, "Update results.md", "Summarize scan results")


# -------- Main --------
def main():
    exit_code = 0
    try:
        phase1_prepare()
        phase2_search_mapping()
        phase3_execute()
        # Determine exit code: non-zero if we logged compile errors or pytest failed
        smoke = json.loads(SMOKE.read_text(encoding="utf-8"))
        pyc = smoke.get("python_compile", {})
        if any(not v.get("compiled", False) for v in pyc.values()):
            exit_code = 2
        pytest = smoke.get("pytest", {})
        if pytest and pytest.get("returncode", 0) != 0:
            exit_code = max(exit_code, 3)
    except Exception as e:
        emit_error("X", "Top-level failure", repr(e), traceback.format_exc())
        exit_code = max(exit_code, 10)

    # Final banner
    print("\n=== Codex Repo Scout Complete ===")
    print(f"Results: {RESULTS}")
    print(f"Change Log: {CHANGE_LOG}")
    print(f"Errors (ChatGPT-5): {ERROR_LOG}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
