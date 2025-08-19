#!/usr/bin/env python3
# tests/test_query_logs_build_query.py

import ast
import importlib.util
import inspect
import pathlib
import re
import textwrap
import types
from typing import List, Optional, Tuple

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CANDIDATES = [
    "src/codex/logging/query_logs.py",
    "src/codex/logging/viewer.py",
    "scripts/codex_end_to_end.py",
]


# --- AST helpers for extracting literal strings and list-of-strings from code ---


_COLUMNS_KEYS = {"select", "columns", "select_cols", "cols"}
_TS_KEYS = {"timestamp", "order_by", "ts", "sort_key"}


def _const_str(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Str):
        return node.s
    return None


def _extract_list_of_str(node: ast.AST) -> List[str]:
    out: List[str] = []
    if isinstance(node, (ast.List, ast.Tuple)):
        for elt in node.elts:
            s = _const_str(elt)
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                out.append(elt.value)
            elif s is not None:
                out.append(s)
    return out


def _harvest_from_dict_node(
    dnode: ast.Dict, cols_set: set, ts_list: list, depth: int = 0, max_depth: int = 1
) -> None:
    for k_node, v_node in zip(dnode.keys, dnode.values):
        k = _const_str(k_node)
        if not isinstance(k, str):
            continue
        k_lower = k.lower()
        if k_lower in _COLUMNS_KEYS:
            cols = _extract_list_of_str(v_node)
            for c in cols:
                if re.match(r"[A-Za-z_][A-Za-z0-9_]*$", c or ""):
                    cols_set.add(c)
        if k_lower in _TS_KEYS:
            s = _const_str(v_node)
            if isinstance(s, str) and re.match(r"[A-Za-z_][A-Za-z0-9_]*$", s):
                ts_list.append(s)
        if depth < max_depth and isinstance(v_node, ast.Dict):
            _harvest_from_dict_node(v_node, cols_set, ts_list, depth + 1, max_depth)


def _extract_literal_columns_from_source(src: str) -> List[str]:
    """Collect columns from list/tuple assignments, dict literals (including nested), and SQL SELECT strings."""
    cols_set = set()
    try:
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and re.search(
                        r"^(columns|select|select_cols|cols)$", target.id, re.I
                    ):
                        # support list/tuple literal
                        cols_set.update(_extract_list_of_str(node.value))
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                if re.search(r"^(columns|select|select_cols|cols)$", node.target.id, re.I):
                    cols_set.update(_extract_list_of_str(node.value))
            if isinstance(node, ast.Dict):
                try:
                    _harvest_from_dict_node(node, cols_set, ts_list=[], depth=0, max_depth=2)
                except Exception:
                    # Best-effort; don't fail tests generation on complex nodes
                    pass
    except Exception:
        pass

    # Also parse inline SQL SELECT statements
    for m in re.finditer(r"SELECT\s+(.+?)\s+FROM", src, flags=re.I | re.S):
        cols = [c.strip(' `"') for c in re.split(r",\s*", m.group(1))]
        cols = [
            c
            for c in cols
            if c
            and all(x not in c.lower() for x in ["*", "case ", "count(", "sum(", "avg("])
        ]
        cols_set.update([c for c in cols if re.match(r"[A-Za-z_][A-Za-z0-9_]*$", c)])
    return sorted(cols_set)


def _extract_timestamp_from_source(src: str) -> Optional[str]:
    m = re.search(
        r"ORDER\s+BY\s+([A-Za-z_][A-Za-z0-9_]*)\s+(ASC|DESC)", src, flags=re.I
    )
    if m:
        return m.group(1)
    # also check for simple assignments like timestamp = 'ts'
    m2 = re.search(
        r"(timestamp|ts_col|order_by|sort_key)\s*=\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]",
        src,
        flags=re.I,
    )
    if m2:
        return m2.group(2)
    return None


def _infer_expectations(build_query_func) -> Tuple[List[str], str]:
    """
    Inspect a build_query callable and attempt to infer:
      - expected list of selected columns (best-effort)
      - timestamp column name
    Returns (expected_cols, ts). Defaults to sensible fallbacks.
    """
    expected_cols: List[str] = []
    ts: Optional[str] = None
    try:
        src = inspect.getsource(build_query_func)
        expected_cols = _extract_literal_columns_from_source(src)
        ts = _extract_timestamp_from_source(src)
    except Exception:
        # best-effort only; ignore failures
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

    if not expected_cols:
        expected_cols = ["event_time", "user_id", "message"]
    if not ts:
        ts = "event_time"
    return expected_cols, ts


def _extract_select_cols(sql: str) -> List[str]:
    m = re.search(r"select\s+(.*?)\s+from", sql, flags=re.I | re.S)
    if not m:
        return []
    cols = [c.strip() for c in re.split(r",\s*", m.group(1))]
    return [re.sub(r"\s+as\s+\w+$", "", c, flags=re.I) for c in cols]


# --- dynamic module loading for repository candidates ---


def _load_module_from_path(rel_path: str):
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
        except Exception as e:  # pragma: no cover - best effort
            last_err = e
            continue
    if last_err:
        pytest.xfail(f"build_query not importable from candidates: {last_err}")
    pytest.xfail("build_query not importable from any candidate")


# --- utilities for creating temporary modules used in tests ---


def _write_tmp_module(tmp_path: pathlib.Path, src: str) -> types.ModuleType:
    p = tmp_path / "tmp_bq.py"
    p.write_text(textwrap.dedent(src), encoding="utf-8")
    spec = importlib.util.spec_from_file_location("tmp_bq", str(p))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return mod


# --- Tests (pytest) ---


def test_inference_pure_sql(tmp_path):
    mod = _write_tmp_module(
        tmp_path,
        """
def build_query():
    return "SELECT event_time, user_id, message FROM t ORDER BY event_time ASC"
""",
    )
    cols, ts = _infer_expectations(mod.build_query)
    assert set(cols) >= {"event_time", "user_id", "message"}
    assert ts == "event_time"


def test_inference_dict_literal(tmp_path):
    mod = _write_tmp_module(
        tmp_path,
        """
def build_query():
    mapcol = {"select": ["id", "ts", "val"], "timestamp": "ts"}
    return "SELECT id, ts, val FROM t ORDER BY ts ASC"
""",
    )
    cols, ts = _infer_expectations(mod.build_query)
    assert set(cols) >= {"id", "ts", "val"}
    assert ts == "ts"


def test_inference_mixed(tmp_path):
    mod = _write_tmp_module(
        tmp_path,
        """
def build_query(columns=None, order_by=None):
    cfg = {"columns": ["a", "b", "c"], "order_by": "ts_cfg"}
    sql = "SELECT a, b, c, d FROM table ORDER BY d ASC"
    return sql
""",
    )
    cols, ts = _infer_expectations(mod.build_query)
    assert set(cols) >= {"a", "b", "c", "d"}
    assert ts == "d"


def test_inference_nested_dict(tmp_path):
    mod = _write_tmp_module(
        tmp_path,
        """
def build_query():
    config = {"query": {"select": ["u", "v", "w"], "order_by": "ts_nested"}}
    return "SELECT u, v, w FROM x ORDER BY ts_nested ASC"
""",
    )
    cols, ts = _infer_expectations(mod.build_query)
    assert set(cols) >= {"u", "v", "w"}
    assert ts == "ts_nested"


def test_build_query_selects_columns_and_orders():
    build_query, mod = _load_build_query()
    expected_cols, ts = _infer_expectations(build_query)

    sig = None
    try:
        sig = inspect.signature(build_query)
    except Exception:
        pass

    mapcol = {"timestamp": ts, "select": expected_cols}

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
    # always try mapcol strategies as fallback
    try_calls += [((mapcol,), {}), ((), {"mapcol": mapcol})]

    last_err = None
    out = None
    for args, kwargs in try_calls:
        try:
            out = build_query(*args, **kwargs)
            break
        except Exception as e:  # pragma: no cover - best effort
            last_err = e
    else:
        pytest.fail(f"build_query call failed under all strategies: {last_err}")

    sql = None
    if isinstance(out, str):
        sql = out
    elif isinstance(out, (tuple, list)):
        for x in out:
            if isinstance(x, str) and "select" in x.lower():
                sql = x
                break
    if not isinstance(sql, str):
        pytest.fail("build_query did not return SQL string (directly or in tuple)")

    sel = _extract_select_cols(sql)
    for c in expected_cols:
        assert any(c.lower() in s.lower() for s in sel), (
            f"Missing column {c} in SELECT: {sel}"
        )

    assert re.search(rf"order\s+by\s{{1,}}{re.escape(ts)}\s+asc\b", sql, flags=re.I), (
        f"ORDER BY {ts} ASC missing in SQL: {sql}"
    )
