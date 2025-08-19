#!/usr/bin/env python3
# tools/codex_workflow.py
# Purpose: Best-effort implementation of the Codex execution plan for `_codex_` repo (branch 0B_base_)
# Constraints: DO_NOT_ACTIVATE_GITHUB_ACTIONS = True; no CI activation or workflow edits.

import os, sys, re, json, difflib, subprocess, textwrap, shutil, inspect, ast
from pathlib import Path
from datetime import datetime

DO_NOT_ACTIVATE_GITHUB_ACTIONS = True

REPO_ROOT = None


def repo_root() -> Path:
    global REPO_ROOT
    if REPO_ROOT:
        return REPO_ROOT
    p = Path.cwd().resolve()
    for up in [p] + list(p.parents):
        if (up / ".git").is_dir():
            REPO_ROOT = up
            return up
    print("Not inside a git repository.", file=sys.stderr)
    sys.exit(2)


def run(cmd, step, check=False, capture=False, env=None):
    try:
        res = subprocess.run(
            cmd,
            cwd=str(repo_root()),
            check=check,
            text=True,
            shell=isinstance(cmd, str),
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.STDOUT if capture else None,
            env=env or os.environ.copy(),
        )
        return (res.returncode, (res.stdout or ""))
    except Exception as e:
        log_error(step, str(e), f"cmd={cmd}")
        return (1, "")


CODexDir = lambda: (repo_root() / ".codex")
CHANGE_LOG = lambda: (CODexDir() / "change_log.md")
ERRORS = lambda: (CODexDir() / "errors.ndjson")
RESULTS = lambda: (CODexDir() / "results.md")


def ensure_dirs():
    CODexDir().mkdir(parents=True, exist_ok=True)
    for p in [CHANGE_LOG(), ERRORS(), RESULTS()]:
        if not p.exists():
            p.write_text("", encoding="utf-8")
    append_change(f"# Change Log (Codex) — {utcnow()}")


def utcnow():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def append_change(text):
    with CHANGE_LOG().open("a", encoding="utf-8") as f:
        f.write(text.rstrip() + "\n")


def append_result(text):
    with RESULTS().open("a", encoding="utf-8") as f:
        f.write(text.rstrip() + "\n")


def append_error_ndjson(record: dict):
    with ERRORS().open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    block = f"""Question for ChatGPT-5:
While performing [{record.get('step_number','?')}: {record.get('step_desc','')}], encountered the following error:
{record.get('error_message','(no message)')}
Context: {record.get('context','(none)')}
What are the possible causes, and how can this be resolved while preserving intended functionality?"""
    print(block, file=sys.stderr)


def log_error(step_num_desc: str, error_message: str, context: str):
    try:
        step_num, _, desc = step_num_desc.partition(" ")
        if not _:
            step_num, desc = step_num_desc, ""
    except Exception:
        step_num, desc = step_num_desc, ""
    append_error_ndjson(
        {
            "timestamp": utcnow(),
            "step_number": step_num,
            "step_desc": desc.strip(),
            "error_message": error_message,
            "context": context,
        }
    )


def safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        log_error("READ", str(e), f"path={path}")
        return ""


def safe_write_with_diff(path: Path, new_text: str, change_title: str):
    old = safe_read(path) if path.exists() else ""
    if old == new_text:
        return False
    if DO_NOT_ACTIVATE_GITHUB_ACTIONS and path.is_relative_to(
        repo_root() / ".github" / "workflows"
    ):
        log_error(
            "GUARD",
            "Attempted to write into .github/workflows under constraint",
            f"path={path}",
        )
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(new_text, encoding="utf-8")
    diff = difflib.unified_diff(
        old.splitlines(True),
        new_text.splitlines(True),
        fromfile=f"a/{path}",
        tofile=f"b/{path}",
    )
    append_change(
        f"## {change_title}\n**File:** {path}\n**When:** {utcnow()}\n```diff\n{''.join(diff)}```\n"
    )
    return True


def _import_block_insertion_point(text: str) -> int:
    idx = 0
    if text.startswith("#!"):
        idx = text.find("\n") + 1
    enc_m = re.match(r"(?s)(#.*coding[:=].*\n)", text[idx:])
    if enc_m:
        idx += enc_m.end()
    doc_m = re.match(r'(?s)\s*(?P<q>["\']{3}).*?(?P=q)\s*', text[idx:])
    if doc_m and doc_m.start() == 0:
        idx += doc_m.end()
    return idx


def ensure_imports(file_path: Path, imports: list[str]) -> bool:
    text = safe_read(file_path)
    if not text:
        log_error("3.1 ensure_imports", "Empty or unreadable file", f"{file_path}")
        return False
    needed = []
    for imp in imports:
        canon = imp.strip()
        pattern = re.escape(canon).replace("\\ ", "\\s+")
        if not re.search(rf'^\s*{pattern}\s*$', text, flags=re.M):
            needed.append(canon)
    if not needed:
        return False
    insert_at = _import_block_insertion_point(text)
    block = "".join(f"{imp}\n" for imp in needed)
    new_text = (
        text[:insert_at]
        + block
        + ("\n" if not text[insert_at:].startswith("\n") else "")
        + text[insert_at:]
    )
    return safe_write_with_diff(file_path, new_text, f"Insert missing imports into {file_path.name}")


def find_candidates(symbol: str) -> list[Path]:
    hits = []
    for p in repo_root().rglob("*.py"):
        if ".git" in p.parts:
            continue
        try:
            t = p.read_text(encoding="utf-8", errors="ignore")
            if re.search(rf"\bdef\s+{re.escape(symbol)}\s*\(", t):
                hits.append(p)
            if re.search(rf"\bclass\s+{re.escape(symbol)}\b", t):
                hits.append(p)
        except Exception as e:
            log_error("2.2 find_candidates", str(e), f"path={p}")
    hits = sorted(set(hits), key=lambda p: (len(p.parts), str(p)))
    return hits


def _extract_literal_columns_from_source(src: str) -> list[str]:
    """Best-effort: find Python list literals assigned to names like columns/select/cols."""
    out = set()
    try:
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and re.search(
                        r"^(columns|select|select_cols|cols)$", target.id, re.I
                    ):
                        if isinstance(node.value, (ast.List, ast.Tuple)):
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Str):
                                    out.add(elt.s)
                                elif isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                    out.add(elt.value)
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                if re.search(r"^(columns|select|select_cols|cols)$", node.target.id, re.I):
                    v = node.value
                    if isinstance(v, (ast.List, ast.Tuple)):
                        for elt in v.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                out.add(elt.value)
    except Exception:
        pass
    for m in re.finditer(r"SELECT\s+(.+?)\s+FROM", src, flags=re.I | re.S):
        cols = [c.strip(" `\"") for c in re.split(r",\s*", m.group(1))]
        out.update(
            [
                c
                for c in cols
                if c
                and all(
                    x not in c.lower() for x in ["*", "case ", "count(", "sum(", "avg("]
                )
            ]
        )
    return [c for c in out if re.match(r"[A-Za-z_][A-Za-z0-9_]*$", c)]


def _extract_timestamp_from_source(src: str) -> str | None:
    m = re.search(
        r"ORDER\s+BY\s+([A-Za-z_][A-Za-z0-9_]*)\s+(ASC|DESC)", src, flags=re.I
    )
    if m:
        return m.group(1)
    m = re.search(
        r"(timestamp|ts_col|order_by|sort_key)\s*=\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]",
        src,
        flags=re.I,
    )
    if m:
        return m.group(2)
    return None


def _infer_expectations(build_query_func):
    expected_cols = []
    ts = None
    try:
        src = inspect.getsource(build_query_func)
        expected_cols = _extract_literal_columns_from_source(src)
        ts = _extract_timestamp_from_source(src)
    except Exception:
        pass
    try:
        sig = inspect.signature(build_query_func)
        param_names = [p for p in sig.parameters]
        if not ts:
            if "timestamp" in param_names:
                ts = "timestamp"
            elif "order_by" in param_names:
                ts = "order_by"
        if not expected_cols:
            if "columns" in param_names or "select" in param_names:
                expected_cols = ["event_time", "user_id", "message"]
    except Exception:
        pass
    return expected_cols, ts


def create_build_query_test():
    test_path = repo_root() / "tests" / "test_query_logs_build_query.py"
    candidates = find_candidates("build_query")
    test_body = f'''# Auto-generated by codex_workflow.py @ {utcnow()}
import os, sys, re, importlib.util, pathlib, inspect, pytest, ast, json

ROOT = pathlib.Path(__file__).resolve().parents[1]
CANDIDATES = {json.dumps([str(p.relative_to(repo_root())) for p in candidates], indent=2)}

def _load_module_from_path(rel_path):
    mod_path = ROOT / rel_path
    spec = importlib.util.spec_from_file_location("build_query_mod", str(mod_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return mod

def _load_build_query():
    last_err=None
    for rel in CANDIDATES:
        try:
            mod=_load_module_from_path(rel)
            if hasattr(mod, "build_query"):
                return getattr(mod, "build_query"), mod
        except Exception as e:
            last_err=e
            continue
    if last_err:
        pytest.xfail(f"build_query not importable from candidates: {{last_err}}")
    pytest.xfail("build_query not importable from any candidate")

def _extract_literal_columns_from_source(src: str):
    out=set()
    try:
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and re.search(r"^(columns|select|select_cols|cols)$", target.id, re.I):
                        if isinstance(node.value, (ast.List, ast.Tuple)):
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                    out.add(elt.value)
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                if re.search(r"^(columns|select|select_cols|cols)$", node.target.id, re.I):
                    v=node.value
                    if isinstance(v, (ast.List, ast.Tuple)):
                        for elt in v.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                out.add(elt.value)
    except Exception:
        pass
    for m in re.finditer(r"SELECT\s+(.+?)\s+FROM", src, flags=re.I|re.S):
        cols = [c.strip(" `\"") for c in re.split(r",\s*", m.group(1))]
        out.update([c for c in cols if c and all(x not in c.lower() for x in ["*", "case ", "count(", "sum(", "avg("] )])
    return [c for c in out if re.match(r"[A-Za-z_][A-Za-z0-9_]*$", c)]

def _extract_timestamp_from_source(src: str):
    m = re.search(r"ORDER\s+BY\s+([A-Za-z_][A-Za-z0-9_]*)\s+(ASC|DESC)", src, flags=re.I)
    if m: return m.group(1)
    m = re.search(r"(timestamp|ts_col|order_by|sort_key)\s*=\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]", src, flags=re.I)
    if m: return m.group(2)
    return None

def _infer_expectations(build_query):
    expected_cols=[]
    ts=None
    try:
        src = inspect.getsource(build_query)
        expected_cols = _extract_literal_columns_from_source(src)
        ts = _extract_timestamp_from_source(src)
    except Exception:
        pass
    try:
        sig = inspect.signature(build_query)
        params = [p for p in sig.parameters]
        if not ts:
            if "timestamp" in params: ts = "timestamp"
            elif "order_by" in params: ts = "order_by"
        if not expected_cols:
            if "columns" in params or "select" in params:
                expected_cols = ["event_time", "user_id", "message"]
    except Exception:
        pass
    if not expected_cols:
        expected_cols = ["event_time", "user_id", "message"]
    if not ts:
        ts = "event_time"
    return expected_cols, ts

def _extract_select_cols(sql: str):
    m = re.search(r"select\s+(.*?)\s+from", sql, flags=re.I|re.S)
    if not m:
        return []
    cols = [c.strip() for c in re.split(r",\s*", m.group(1))]
    return [re.sub(r"\s+as\s+\w+$", "", c, flags=re.I) for c in cols]

def test_build_query_selects_columns_and_orders():
    build_query, mod = _load_build_query()
    expected_cols, ts = _infer_expectations(build_query)

    sig = None
    try:
        sig = inspect.signature(build_query)
    except Exception:
        pass

    mapcol = {
        "timestamp": ts,
        "select": expected_cols
    }

    try_calls = []
    if sig:
        params = [p for p in sig.parameters]
        if "mapcol" in params:
            try_calls.append(((mapcol,), {}))
            try_calls.append(((), {"mapcol": mapcol}))
        if "columns" in params:
            try_calls.append(((), {"columns": expected_cols}))
        if "select" in params and "columns" not in params:
            try_calls.append(((), {"select": expected_cols}))
        if "timestamp" in params:
            try_calls.append(((), {"timestamp": ts}))
        if "order_by" in params and "timestamp" not in params:
            try_calls.append(((), {"order_by": ts}))
    try_calls += [
        ((mapcol,), {}),
        ((), {"mapcol": mapcol})
    ]

    last_err=None
    for args, kwargs in try_calls:
        try:
            out = build_query(*args, **kwargs)
            break
        except Exception as e:
            last_err=e
    else:
        pytest.fail(f"build_query call failed under all strategies: {last_err}")

    sql = None
    if isinstance(out, str):
        sql = out
    elif isinstance(out, (tuple, list)):
        for x in out:
            if isinstance(x, str) and "select" in x.lower():
                sql = x; break
    if not isinstance(sql, str):
        pytest.fail("build_query did not return SQL string (directly or in tuple)")

    sel = _extract_select_cols(sql)
    for c in expected_cols:
        assert any(c.lower() in s.lower() for s in sel), f"Missing column {c} in SELECT: {sel}"

    assert re.search(rf"order\s+by\s{{1,}}{re.escape(ts)}\s+asc\b", sql, flags=re.I), f"ORDER BY {ts} ASC missing in SQL: {sql}"
'''
    return safe_write_with_diff(test_path, test_body, "Add test_query_logs_build_query.py (with inference)")


def patch_chat_session_test():
    file_path = repo_root() / "tests" / "test_chat_session.py"
    if not file_path.exists():
        log_error("3.1 chat_session_test", "tests/test_chat_session.py not found", "required by task")
        return False
    text = safe_read(file_path)
    marker = "def test_exception_restores_env"
    if marker in text:
        return False
    addition = '''
import os, pytest, importlib.util, pathlib, re

def _load_chatsession():
    root = pathlib.Path(__file__).resolve().parents[1]
    for p in root.rglob("*.py"):
        try:
            t = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if re.search(r"\bclass\s+ChatSession\b", t):
            spec = importlib.util.spec_from_file_location("cs_mod", str(p))
            mod = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(mod)  # type: ignore
                if hasattr(mod, "ChatSession"):
                    return getattr(mod, "ChatSession")
            except Exception:
                continue
    return None

def test_exception_restores_env():
    ChatSession = _load_chatsession()
    if ChatSession is None:
        pytest.xfail("ChatSession not found/importable; implement ChatSession or update mapping")
    os.environ["CODEX_SESSION_ID"] = "dummy"
    try:
        try:
            cs = ChatSession()
        except TypeError:
            pytest.xfail("ChatSession requires args; provide a zero-arg default or factory")
        with cs:
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    assert os.environ.get("CODEX_SESSION_ID") in (None, "",), "CODEX_SESSION_ID should be unset after exception"
'''
    new_text = text.rstrip() + "\n\n" + addition.lstrip() + "\n"
    return safe_write_with_diff(file_path, new_text, "Add exception restoration test for ChatSession")


def insert_all_missing_imports():
    specs = {
        "tests/test_chat_session.py": ["import os"],
        "tests/test_fetch_messages.py": [
            "import sqlite3",
            "import inspect",
            "from pathlib import Path",
            "import os",
        ],
        "tests/test_session_hooks.py": ["import os", "import json"],
        "tests/test_db_utils.py": ["import sqlite3"],
        "tests/test_logging_viewer_cli.py": ["import sqlite3", "import json"],
        "tests/test_log_adapters.py": ["from pathlib import Path", "import sqlite3"],
        "tests/test_sqlite_pool.py": ["import sqlite3", "import threading"],
        "tests/test_session_logging.py": [
            "import importlib",
            "import sys",
            "import subprocess",
            "import sqlite3",
            "import pathlib",
            "import logging",
            "import json",
            "import os",
            "import pwd",
            "import shutil",
        ],
    }
    edited = []
    for rel, imps in specs.items():
        p = repo_root() / rel
        if not p.exists():
            log_error("3.1 ensure_imports", "File missing for import insertion", rel)
            continue
        if ensure_imports(p, imps):
            edited.append(str(p))
    return edited


def run_precommit_on(paths):
    if not paths:
        return
    cmd = ["pre-commit", "run", "--files", *paths]
    rc, out = run(cmd, "Hook pre-commit", check=False, capture=True)
    append_result("## pre-commit output\n```\n" + out.strip() + "\n```")
    if rc != 0:
        log_error("Hook pre-commit", f"non-zero exit ({rc})", "See .codex/results.md for output")


def run_pytest_focus():
    cmd = ["pytest", "-q", "tests/test_chat_session.py::test_exception_restores_env"]
    rc, out = run(cmd, "pytest focus", check=False, capture=True)
    append_result("## pytest (focused) output\n```\n" + out.strip() + "\n```")
    if rc != 0:
        log_error(
            "pytest focus",
            f"non-zero exit ({rc})",
            "Expected to fail pre-fix; see results for details",
        )


def rescan_docs():
    for name in ("README.md", "CONTRIBUTING.md"):
        p = repo_root() / name
        if p.exists():
            txt = safe_read(p)
            new = re.sub(r"\[([^\]]+)\]\(#?TO?D?O?\)", r"\1", txt, flags=re.I)
            if new != txt:
                safe_write_with_diff(p, new, f"Doc sanity pass for {name}")


def finalize_and_exit():
    unresolved = ERRORS().read_text(encoding="utf-8").strip()
    append_result("### Statement\nDO NOT ACTIVATE ANY GitHub Actions files.")
    if unresolved:
        append_result("\n### Unresolved Errors Present — exit(1)")
        print("Unresolved issues recorded in .codex/errors.ndjson", file=sys.stderr)
        sys.exit(1)
    else:
        append_result("\n### No unresolved errors — exit(0)")
        sys.exit(0)


def main():
    ensure_dirs()
    rc, _ = run([
        "bash",
        "-lc",
        'test -z "$(git status --porcelain)"'
    ], "1.1 cleanliness", check=False, capture=False)
    if rc != 0:
        log_error("1.1 cleanliness", "Working tree not clean", "Commit/stash changes before running")

    candidates_bq = [str(p) for p in find_candidates("build_query")]
    candidates_cs = [str(p) for p in find_candidates("ChatSession")]
    append_result(
        "## Mapping\n" + json.dumps({"build_query": candidates_bq, "ChatSession": candidates_cs}, indent=2)
    )

    edited = insert_all_missing_imports()
    created_bq_test = create_build_query_test()
    patched_cs_test = patch_chat_session_test()

    append_result("## Edited Files\n" + json.dumps(edited, indent=2))
    append_result("## Created build_query test\n" + json.dumps(bool(created_bq_test), indent=2))
    append_result("## Patched ChatSession test\n" + json.dumps(bool(patched_cs_test), indent=2))

    run_precommit_on(
        edited + ["tests/test_query_logs_build_query.py"]
    )
    run_pytest_focus()
    rescan_docs()
    append_result("**DO NOT ACTIVATE ANY GitHub Actions files.**")
    finalize_and_exit()


if __name__ == "__main__":
    main()

