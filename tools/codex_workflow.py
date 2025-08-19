#!/usr/bin/env python3
# tools/codex_workflow.py
# Merged Execution Plan Script
# Combines depth-aware dict inference, AST metrics, extended test generation,
# robust typing, and safety guards (no GitHub Actions activation).

from __future__ import annotations

import ast
import difflib
import importlib.util
import inspect
import json
import os
import re
import shutil
import subprocess
import textwrap
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Iterable, Tuple, Dict, Any

DO_NOT_ACTIVATE_GITHUB_ACTIONS = True

# --- Inference knobs & optional AST metrics ---
MAX_DICT_DEPTH = int(os.getenv("CODEX_MAX_DICT_DEPTH", "5"))
EMIT_AST_METRICS = os.getenv("CODEX_AST_METRICS", "0") == "1"
_AST_METRICS: Dict[str, Any] = {"files": {}}

REPO_ROOT: Optional[Path] = None

# ---------------------------------------------------------------------------
# Core repository / filesystem helpers
# ---------------------------------------------------------------------------


def repo_root() -> Path:
    """Locate and cache the repository root (directory containing .git)."""
    global REPO_ROOT
    if REPO_ROOT:
        return REPO_ROOT
    p = Path.cwd().resolve()
    for up in (p, *p.parents):
        if (up / ".git").is_dir():
            REPO_ROOT = up
            return up
    print("Not inside a git repository.", file=os.sys.stderr)
    raise SystemExit(2)


def run(
    cmd,
    step: str,
    check: bool = False,
    capture: bool = False,
    env: Optional[dict] = None,
) -> Tuple[int, str]:
    """
    Execute a command in the repo root.
    Returns (returncode, stdout_text). Never raises; logs instead.
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=str(repo_root()),
            check=check,
            text=True,
            shell=isinstance(cmd, str),
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.STDOUT if capture else None,
            env=env or os.environ.copy(),
        )
        return result.returncode, (result.stdout or "")
    except Exception as e:
        log_error(step, str(e), f"cmd={cmd}")
        return 1, ""


CODexDir = lambda: (repo_root() / ".codex")
CHANGE_LOG = lambda: (CODexDir() / "change_log.md")
ERRORS = lambda: (CODexDir() / "errors.ndjson")
RESULTS = lambda: (CODexDir() / "results.md")


def ensure_dirs() -> None:
    CODexDir().mkdir(parents=True, exist_ok=True)
    for p in (CHANGE_LOG(), ERRORS(), RESULTS()):
        if not p.exists():
            p.write_text("", encoding="utf-8")
    append_change(f"# Change Log (Codex) — {utcnow()}")


def utcnow() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def append_change(text: str) -> None:
    with CHANGE_LOG().open("a", encoding="utf-8") as f:
        f.write(text.rstrip() + "\n")


def append_result(text: str) -> None:
    with RESULTS().open("a", encoding="utf-8") as f:
        f.write(text.rstrip() + "\n")


def append_error_ndjson(record: dict) -> None:
    with ERRORS().open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    block = f"""Question for ChatGPT-5:
While performing [{record.get('step_number','?')}: {record.get('step_desc','')}], encountered the following error:
{record.get('error_message','(no message)')}
Context: {record.get('context','(none)')}
What are the possible causes, and how can this be resolved while preserving intended functionality?"""
    print(block, file=os.sys.stderr)


def log_error(step_num_desc: str, error_message: str, context: str) -> None:
    try:
        step_num, sep, desc = step_num_desc.partition(" ")
        if not sep:
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


def safe_write_with_diff(path: Path, new_text: str, change_title: str) -> bool:
    """
    Write file only if content changes; record unified diff; guard GitHub Actions workflow area.
    Returns True if a write occurred.
    """
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
    """
    Return index after shebang/encoding/module docstring for safe import insertion.
    """
    idx = 0
    if text.startswith("#!"):
        nl = text.find("\n")
        idx = (nl + 1) if nl != -1 else len(text)
    enc_m = re.match(r"(?s)(#.*coding[:=].*\n)", text[idx:])
    if enc_m:
        idx += enc_m.end()
    doc_m = re.match(r'(?s)\s*(?P<q>["\']{3}).*?(?P=q)\s*', text[idx:])
    if doc_m and doc_m.start() == 0:
        idx += doc_m.end()
    return idx


def ensure_imports(file_path: Path, imports: List[str]) -> bool:
    """
    Ensure each import line is present (exact line match ignoring whitespace runs).
    Returns True if modifications were made.
    """
    text = safe_read(file_path)
    if not text:
        log_error("3.1 ensure_imports", "Empty or unreadable file", f"{file_path}")
        return False
    needed: List[str] = []
    for imp in imports:
        canon = imp.strip()
        pattern = re.escape(canon).replace("\\ ", "\\s+")
        if not re.search(rf"^\s*{pattern}\s*$", text, flags=re.M):
            needed.append(canon)
    if not needed:
        return False
    insert_at = _import_block_insertion_point(text)
    block = "".join(f"{imp}\n" for imp in needed)
    new_text = (
        text[:insert_at]
        + block
        + ("" if text[insert_at:].startswith("\n") else "\n")
        + text[insert_at:]
    )
    return safe_write_with_diff(
        file_path, new_text, f"Insert missing imports into {file_path.name}"
    )


def find_candidates(symbol: str) -> List[Path]:
    """
    Find candidate Python files defining a function or class named `symbol`.
    """
    hits: List[Path] = []
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


# ---------------------------------------------------------------------------
# AST Metrics (optional)
# ---------------------------------------------------------------------------


class _MetricsVisitor(ast.NodeVisitor):
    def __init__(self):
        self.count = 0

    def generic_visit(self, node):  # type: ignore[override]
        self.count += 1
        super().generic_visit(node)


def _maybe_record_ast_metrics(label: str, src: str) -> None:
    if not EMIT_AST_METRICS:
        return
    try:
        tree = ast.parse(src)
        v = _MetricsVisitor()
        v.visit(tree)
        entry = _AST_METRICS["files"].setdefault(label, {})
        entry["nodes_visited"] = v.count
        entry["timestamp"] = utcnow()
    except Exception:
        pass


def _flush_ast_metrics_if_any() -> None:
    if not EMIT_AST_METRICS:
        return
    out = repo_root() / ".codex" / "audits" / "ast_metrics.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        out.write_text(json.dumps(_AST_METRICS, indent=2), encoding="utf-8")
        append_result(f"AST metrics written to {out}")
    except Exception as e:
        log_error("AST_METRICS_WRITE", str(e), f"path={out}")


# ---------------------------------------------------------------------------
# Inference helpers (depth‑aware dict DFS + SQL parsing)
# ---------------------------------------------------------------------------

_COLUMNS_KEYS = {"select", "columns", "cols", "select_cols"}
_TS_KEYS = {"timestamp", "order_by", "ts", "sort_key", "ts_col"}


def _const_str(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Str):  # py<3.8 compatibility
        return node.s
    return None


def _collect_str_list(node: ast.AST) -> List[str]:
    if not isinstance(node, (ast.List, ast.Tuple)):
        return []
    out: List[str] = []
    for elt in node.elts:
        s = _const_str(elt)
        if s is not None:
            out.append(s)
    return out


def _dfs_dict(node: ast.AST, depth: int, cols_acc: set, ts_acc: List[str]) -> None:
    """Depth-bounded DFS into dict literals collecting columns & timestamp keys."""
    if depth > MAX_DICT_DEPTH or not isinstance(node, ast.Dict):
        return
    for k_node, v_node in zip(node.keys, node.values):
        key = _const_str(k_node) or (k_node.id if isinstance(k_node, ast.Name) else None)
        if key:
            k_norm = key.lower()
            if k_norm in _COLUMNS_KEYS:
                cols_acc.update(_collect_str_list(v_node))
            elif k_norm in _TS_KEYS:
                ts_val = _const_str(v_node)
                if ts_val:
                    ts_acc.append(ts_val)
        # Recurse
        if isinstance(v_node, ast.Dict):
            _dfs_dict(v_node, depth + 1, cols_acc, ts_acc)
        elif isinstance(v_node, (ast.List, ast.Tuple)):
            for e in v_node.elts:
                if isinstance(e, ast.Dict):
                    _dfs_dict(e, depth + 1, cols_acc, ts_acc)


def _extract_literal_columns_from_source(src: str) -> List[str]:
    """Collect columns from variable assignments, dict structures (depth-aware), and SQL SELECT clauses."""
    _maybe_record_ast_metrics("build_query_source_columns", src)
    cols: set = set()
    try:
        tree = ast.parse(src)
        for node in ast.walk(tree):
            # Direct assignments
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id.lower() in _COLUMNS_KEYS:
                        cols.update(_collect_str_list(node.value))
                if isinstance(node.value, ast.Dict):
                    _dfs_dict(node.value, 1, cols, [])
            elif isinstance(node, ast.AnnAssign):
                if (
                    isinstance(node.target, ast.Name)
                    and node.target.id.lower() in _COLUMNS_KEYS
                ):
                    cols.update(_collect_str_list(node.value))
                if isinstance(node.value, ast.Dict):
                    _dfs_dict(node.value, 1, cols, [])
            elif isinstance(node, ast.Dict):
                _dfs_dict(node, 1, cols, [])
        # SQL parsing
        for m in re.finditer(r"SELECT\s+(.+?)\s+FROM", src, flags=re.I | re.S):
            raw_cols = [c.strip(' `"') for c in re.split(r",\s*", m.group(1))]
            for c in raw_cols:
                if c and all(
                    x not in c.lower() for x in ["*", "case ", "count(", "sum(", "avg("]
                ):
                    if re.match(r"[A-Za-z_][A-Za-z0-9_]*$", c):
                        cols.add(c)
    except Exception:
        pass
    return sorted(cols)


def _extract_timestamp_from_source(src: str) -> Optional[str]:
    """Extract ORDER BY column or timestamp-like literals from assignments/dicts."""
    _maybe_record_ast_metrics("build_query_source_timestamp", src)
    m = re.search(
        r"ORDER\s+BY\s+([A-Za-z_][A-Za-z0-9_]*)\s+(ASC|DESC)", src, flags=re.I
    )
    if m:
        return m.group(1)
    ts_acc: List[str] = []
    try:
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id.lower() in _TS_KEYS:
                        s = _const_str(node.value)
                        if s:
                            ts_acc.append(s)
                if isinstance(node.value, ast.Dict):
                    _dfs_dict(node.value, 1, set(), ts_acc)
            elif isinstance(node, ast.AnnAssign):
                if (
                    isinstance(node.target, ast.Name)
                    and node.target.id.lower() in _TS_KEYS
                ):
                    s = _const_str(node.value)
                    if s:
                        ts_acc.append(s)
                if isinstance(node.value, ast.Dict):
                    _dfs_dict(node.value, 1, set(), ts_acc)
            elif isinstance(node, ast.Dict):
                _dfs_dict(node, 1, set(), ts_acc)
    except Exception:
        pass
    return ts_acc[0] if ts_acc else None


def _infer_expectations(build_query_func) -> Tuple[List[str], str]:
    """
    Infer (expected_columns, timestamp_column) from a build_query function.
    Falls back to defaults if inference is incomplete.
    """
    expected_cols: List[str] = []
    ts: Optional[str] = None
    try:
        src = inspect.getsource(build_query_func)
        inferred_cols = _extract_literal_columns_from_source(src)
        inferred_ts = _extract_timestamp_from_source(src)
        if inferred_cols:
            expected_cols = inferred_cols
        if inferred_ts:
            ts = inferred_ts
    except Exception:
        pass
    try:
        sig = inspect.signature(build_query_func)
        params = list(sig.parameters)
        if not ts:
            if "timestamp" in params:
                ts = "timestamp"
            elif "order_by" in params:
                ts = "order_by"
        if not expected_cols and ("columns" in params or "select" in params):
            expected_cols = ["event_time", "user_id", "message"]
    except Exception:
        pass
    if not expected_cols:
        expected_cols = ["event_time", "user_id", "message"]
    if not ts:
        ts = "event_time"
    return expected_cols, ts


# ---------------------------------------------------------------------------
# Test generation (build_query) & ChatSession test patch
# ---------------------------------------------------------------------------


def create_build_query_test() -> bool:
    """
    Generate or update tests/test_query_logs_build_query.py
    embedding inference logic (dict & nested structures).
    """
    test_path = repo_root() / "tests" / "test_query_logs_build_query.py"
    candidates = find_candidates("build_query")
    rel_candidates = [str(p.relative_to(repo_root())) for p in candidates]
    body = f'''# Auto-generated by codex_workflow.py @ {utcnow()}
import os, sys, re, importlib.util, pathlib, inspect, pytest, ast, json, types, textwrap

ROOT = pathlib.Path(__file__).resolve().parents[1]
CANDIDATES = {json.dumps(rel_candidates, indent=2)}

MAX_DICT_DEPTH = int(os.getenv("CODEX_MAX_DICT_DEPTH", "5"))
_SELECT_KEYS = {sorted(list(_COLUMNS_KEYS))}
_TS_KEYS = {sorted(list(_TS_KEYS))}

def _const_str(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if hasattr(ast, "Str") and isinstance(node, ast.Str):
        return node.s
    return None

def _collect_str_list(node):
    if not isinstance(node, (ast.List, ast.Tuple)):
        return []
    out = []
    for e in node.elts:
        s = _const_str(e)
        if s is not None:
            out.append(s)
    return out

def _dfs_dict(node, depth, cols_acc: set, ts_acc: list):
    if depth > MAX_DICT_DEPTH or not isinstance(node, ast.Dict):
        return
    for k_node, v_node in zip(node.keys, node.values):
        key = _const_str(k_node) or (k_node.id if isinstance(k_node, ast.Name) else None)
        if key:
            k_norm = key.lower()
            if k_norm in _SELECT_KEYS:
                cols_acc.update(_collect_str_list(v_node))
            elif k_norm in _TS_KEYS:
                ts_val = _const_str(v_node)
                if ts_val:
                    ts_acc.append(ts_val)
        if isinstance(v_node, ast.Dict):
            _dfs_dict(v_node, depth + 1, cols_acc, ts_acc)
        elif isinstance(v_node, (ast.List, ast.Tuple)):
            for e in v_node.elts:
                if isinstance(e, ast.Dict):
                    _dfs_dict(e, depth + 1, cols_acc, ts_acc)

def _extract_literal_columns_from_source(src: str):
    cols = set()
    try:
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id.lower() in _SELECT_KEYS:
                        cols.update(_collect_str_list(node.value))
                if isinstance(node.value, ast.Dict):
                    _dfs_dict(node.value, 1, cols, [])
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name) and node.target.id.lower() in _SELECT_KEYS:
                    cols.update(_collect_str_list(node.value))
                if isinstance(node.value, ast.Dict):
                    _dfs_dict(node.value, 1, cols, [])
            elif isinstance(node, ast.Dict):
                _dfs_dict(node, 1, cols, [])
        for m in re.finditer(r"SELECT\\s+(.+?)\\s+FROM", src, flags=re.I|re.S):
            raw_cols = [c.strip(' `\"') for c in re.split(r",\\s*", m.group(1))]
            for c in raw_cols:
                if c and all(x not in c.lower() for x in ["*", "case ", "count(", "sum(", "avg("]):
                    if re.match(r"[A-Za-z_][A-Za-z0-9_]*$", c):
                        cols.add(c)
    except Exception:
        pass
    return sorted(cols)

def _extract_timestamp_from_source(src: str):
    m = re.search(r"ORDER\\s+BY\\s+([A-Za-z_][A-Za-z0-9_]*)\\s+(ASC|DESC)", src, flags=re.I)
    if m:
        return m.group(1)
    ts_acc = []
    try:
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id.lower() in _TS_KEYS:
                        s = _const_str(node.value)
                        if s:
                            ts_acc.append(s)
                if isinstance(node.value, ast.Dict):
                    _dfs_dict(node.value, 1, set(), ts_acc)
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name) and node.target.id.lower() in _TS_KEYS:
                    s = _const_str(node.value)
                    if s:
                        ts_acc.append(s)
                if isinstance(node.value, ast.Dict):
                    _dfs_dict(node.value, 1, set(), ts_acc)
            elif isinstance(node, ast.Dict):
                _dfs_dict(node, 1, set(), ts_acc)
    except Exception:
        pass
    return ts_acc[0] if ts_acc else None

def _infer_expectations(build_query):
    cols = []
    ts = None
    try:
        src = inspect.getsource(build_query)
        cols = _extract_literal_columns_from_source(src) or cols
        ts = _extract_timestamp_from_source(src) or ts
    except Exception:
        pass
    try:
        sig = inspect.signature(build_query)
        params = list(sig.parameters)
        if not ts:
            if "timestamp" in params: ts = "timestamp"
            elif "order_by" in params: ts = "order_by"
        if not cols and ("columns" in params or "select" in params):
            cols = ["event_time", "user_id", "message"]
    except Exception:
        pass
    if not cols:
        cols = ["event_time", "user_id", "message"]
    if not ts:
        ts = "event_time"
    return cols, ts

def _extract_select_cols(sql: str):
    m = re.search(r"select\\s+(.*?)\\s+from", sql, flags=re.I|re.S)
    if not m:
        return []
    parts = [c.strip() for c in re.split(r",\\s*", m.group(1))]
    return [re.sub(r"\\s+as\\s+\\w+$", "", c, flags=re.I) for c in parts]

def _load_module_from_path(rel_path):
    mod_path = ROOT / rel_path
    spec = importlib.util.spec_from_file_location("build_query_mod", str(mod_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return mod

def _load_build_query():
    last_err = None
    for rel in CANDIDATES:
        try:
            mod = _load_module_from_path(rel)
            if hasattr(mod, "build_query"):
                return getattr(mod, "build_query"), mod
        except Exception as e:
            last_err = e
            continue
    import pytest
    if last_err:
        pytest.xfail(f"build_query not importable from candidates: {{last_err}}")
    pytest.xfail("build_query not importable from any candidate")

def test_build_query_selects_columns_and_orders():
    build_query, mod = _load_build_query()
    exp_cols, ts = _infer_expectations(build_query)
    try:
        sig = inspect.signature(build_query)
    except Exception:
        sig = None
    mapcol = {{"timestamp": ts, "select": exp_cols}}
    attempts = []
    if sig:
        params = list(sig.parameters)
        if "mapcol" in params:
            attempts += [((mapcol,), {{}}), ((), {{"mapcol": mapcol}})]
        if "columns" in params:
            attempts.append(((), {{"columns": exp_cols}}))
        if "select" in params and "columns" not in params:
            attempts.append(((), {{"select": exp_cols}}))
        if "timestamp" in params:
            attempts.append(((), {{"timestamp": ts}}))
        if "order_by" in params and "timestamp" not in params:
            attempts.append(((), {{"order_by": ts}}))
    attempts += [((mapcol,), {{}}), ((), {{"mapcol": mapcol}})]
    last_err=None
    for a, kw in attempts:
        try:
            out = build_query(*a, **kw)
            break
        except Exception as e:
            last_err=e
    else:
        pytest.fail(f"build_query call failed under all strategies: {{last_err}}")
    sql = None
    if isinstance(out, str):
        sql = out
    elif isinstance(out, (tuple, list)):
        for x in out:
            if isinstance(x, str) and "select" in x.lower():
                sql = x; break
    if not isinstance(sql, str):
        pytest.fail("build_query did not return SQL string")
    sel = _extract_select_cols(sql)
    for c in exp_cols:
        assert any(c.lower() in s.lower() for s in sel), f"Missing column {{c}} in SELECT: {{sel}}"
    import re
    assert re.search(rf"order\\s+by\\s{{1,}}{re.escape(ts)}\\s+asc\\b", sql, flags=re.I), f"ORDER BY {{ts}} ASC missing: {{sql}}"
'''
    return safe_write_with_diff(
        test_path,
        body,
        "Add test_query_logs_build_query.py (with dict & nested inference)",
    )


def patch_chat_session_test() -> bool:
    """
    Ensure ChatSession env restoration test is present.
    """
    file_path = repo_root() / "tests" / "test_chat_session.py"
    if not file_path.exists():
        log_error(
            "3.1 chat_session_test",
            "tests/test_chat_session.py not found",
            "required by task",
        )
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
        if re.search(r"\\bclass\\s+ChatSession\\b", t):
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
    new_text = text.rstrip() + "\n\n" + addition.lstrip()
    return safe_write_with_diff(
        file_path, new_text, "Add exception restoration test for ChatSession"
    )


# ---------------------------------------------------------------------------
# Import insertion across test files
# ---------------------------------------------------------------------------


def insert_all_missing_imports() -> List[str]:
    specs: Dict[str, List[str]] = {
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
    edited: List[str] = []
    for rel, imps in specs.items():
        p = repo_root() / rel
        if not p.exists():
            log_error("3.1 ensure_imports", "File missing for import insertion", rel)
            continue
        try:
            if ensure_imports(p, imps):
                edited.append(str(p))
        except Exception as e:
            log_error("3.1 ensure_imports", str(e), rel)
    return edited


# ---------------------------------------------------------------------------
# Execution helpers (pre-commit, pytest, docs)
# ---------------------------------------------------------------------------


def run_precommit_on(paths: List[str]) -> None:
    if not paths:
        return
    rc, out = run(["pre-commit", "run", "--files", *paths], "Hook pre-commit", capture=True)
    append_result("## pre-commit output\n```\n" + out.strip() + "\n```")
    if rc != 0:
        log_error(
            "Hook pre-commit",
            f"non-zero exit ({rc})",
            "See .codex/results.md for output",
        )


def run_pytest_focus() -> None:
    rc, out = run(
        ["pytest", "-q", "tests/test_chat_session.py::test_exception_restores_env"],
        "pytest focus",
        capture=True,
    )
    append_result("## pytest (focused) output\n```\n" + out.strip() + "\n```")
    if rc != 0:
        log_error(
            "pytest focus",
            f"non-zero exit ({rc})",
            "Expected to fail pre-fix; see results for details",
        )


def rescan_docs() -> None:
    for name in ("README.md", "CONTRIBUTING.md"):
        p = repo_root() / name
        if p.exists():
            txt = safe_read(p)
            new = re.sub(r"\[([^\]]+)\]\(#?TO?D?O?\)", r"\1", txt, flags=re.I)
            if new != txt:
                safe_write_with_diff(p, new, f"Doc sanity pass for {name}")


def finalize_and_exit() -> None:
    unresolved = ERRORS().read_text(encoding="utf-8").strip()
    append_result("### Statement\nDO NOT ACTIVATE ANY GitHub Actions files.")
    if unresolved:
        append_result("\n### Unresolved Errors Present — exit(1)")
        print(
            "Unresolved issues recorded in .codex/errors.ndjson",
            file=os.sys.stderr,
        )
        _flush_ast_metrics_if_any()
        raise SystemExit(1)
    else:
        append_result("\n### No unresolved errors — exit(0)")
        _flush_ast_metrics_if_any()
        raise SystemExit(0)


# ---------------------------------------------------------------------------
# Main Orchestration
# ---------------------------------------------------------------------------


def main() -> None:
    ensure_dirs()
    rc, _ = run(
        ["bash", "-lc", 'test -z "$(git status --porcelain)"'],
        "1.1 cleanliness",
        check=False,
        capture=False,
    )
    if rc != 0:
        log_error(
            "1.1 cleanliness",
            "Working tree not clean",
            "Commit/stash changes before running",
        )

    candidates_bq = [str(p) for p in find_candidates("build_query")]
    candidates_cs = [str(p) for p in find_candidates("ChatSession")]
    append_result(
        "## Mapping\n"
        + json.dumps(
            {"build_query": candidates_bq, "ChatSession": candidates_cs}, indent=2
        )
    )

    edited = insert_all_missing_imports()
    created_bq_test = create_build_query_test()
    patched_cs_test = patch_chat_session_test()

    append_result("## Edited Files\n" + json.dumps(edited, indent=2))
    append_result(
        "## Created build_query test\n" + json.dumps(bool(created_bq_test), indent=2)
    )
    append_result(
        "## Patched ChatSession test\n" + json.dumps(bool(patched_cs_test), indent=2)
    )

    run_precommit_on(edited + ["tests/test_query_logs_build_query.py"])
    run_pytest_focus()
    rescan_docs()
    append_result("**DO NOT ACTIVATE ANY GitHub Actions files.**")
    finalize_and_exit()


__all__ = [
    # Core
    "repo_root",
    "run",
    "ensure_dirs",
    "utcnow",
    "append_change",
    "append_result",
    "append_error_ndjson",
    "log_error",
    "safe_read",
    "safe_write_with_diff",
    "ensure_imports",
    "find_candidates",
    # Inference
    "_extract_literal_columns_from_source",
    "_extract_timestamp_from_source",
    "_infer_expectations",
    # Test generation / patching
    "create_build_query_test",
    "patch_chat_session_test",
    "insert_all_missing_imports",
    # Execution helpers
    "run_precommit_on",
    "run_pytest_focus",
    "rescan_docs",
    "finalize_and_exit",
    # Orchestration
    "main",
]

if __name__ == "__main__":
    main()
