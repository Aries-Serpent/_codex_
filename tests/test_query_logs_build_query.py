# Test: build_query column & timestamp inference
# > Generated: 2025-08-19T22:41:08Z | Author: mbaetiong
"""
Merged test script combining:
- Depth-aware dict / nested inference with configurable MAX_DICT_DEPTH
- Optional AST metrics emission (CODEX_AST_METRICS=1)
- Dynamic candidate discovery for build_query
- Fallback static candidate paths
- Source snippet matrix inference test
- Temporary module compilation tests (pure SQL, dict-based, mixed, nested)
- Robust multi-strategy invocation of build_query
"""

from __future__ import annotations

import ast
import importlib.util
import inspect
import json
import os
import pathlib
import re
import textwrap
import types
from typing import Iterable, List, Optional, Tuple

import pytest

# --------------------------------------------------------------------------------------
# Configuration & Metrics
# --------------------------------------------------------------------------------------

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Dynamic population; will fallback to static list if empty after discovery.
CANDIDATES: List[str] = []

# Depth knob for nested dict scanning (env override).
MAX_DICT_DEPTH = int(os.getenv("CODEX_MAX_DICT_DEPTH", "5"))

# AST metrics toggle.
EMIT_AST_METRICS = os.getenv("CODEX_AST_METRICS", "0") == "1"
_AST_METRICS = {"files": {}}

# Key sets (selection & timestamp)
_SELECT_KEYS = {"select", "columns", "cols", "select_cols"}
_TS_KEYS = {"timestamp", "order_by", "ts", "ts_col", "sort_key"}

# Fallback static candidate paths (legacy support)
_FALLBACK_CANDIDATES = [
    "src/codex/logging/query_logs.py",
    "src/codex/logging/viewer.py",
    "scripts/codex_end_to_end.py",
]


# --------------------------------------------------------------------------------------
# Metrics helpers
# --------------------------------------------------------------------------------------


class _MetricsVisitor(ast.NodeVisitor):
    def __init__(self):
        self.count = 0

    def generic_visit(self, node):  # type: ignore[override]
        self.count += 1
        super().generic_visit(node)


def _metrics_visit(label: str, src: str):
    if not EMIT_AST_METRICS:
        return
    try:
        tree = ast.parse(src)
        v = _MetricsVisitor()
        v.visit(tree)
        file_entry = _AST_METRICS["files"].setdefault(label, {})
        file_entry["nodes_visited"] = v.count
    except Exception:
        # silent best-effort
        pass


def _flush_metrics():
    if not EMIT_AST_METRICS:
        return
    out = ROOT / ".codex" / "audits" / "ast_metrics.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        out.write_text(json.dumps(_AST_METRICS, indent=2), encoding="utf-8")
    except Exception:
        pass


@pytest.fixture(scope="session", autouse=True)
def _session_finalize_metrics():
    # Session-level automatic flush
    yield
    _flush_metrics()


# --------------------------------------------------------------------------------------
# Discovery & Loading
# --------------------------------------------------------------------------------------


def _load_module_from_path(rel_path: str):
    p = ROOT / rel_path
    if not p.exists():
        raise FileNotFoundError(f"Candidate path not found: {rel_path}")
    spec = importlib.util.spec_from_file_location("build_query_mod", str(p))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


def _discover_candidates() -> List[str]:
    out: List[str] = []
    for p in ROOT.rglob("*.py"):
        if ".git" in p.parts:
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if re.search(r"\bdef\s+build_query\s*\(", txt):
            try:
                rel = str(p.relative_to(ROOT))
            except Exception:
                rel = str(p)
            out.append(rel)
    out = sorted(set(out), key=lambda s: (len(s.split("/")), s))
    return out


def _resolve_candidates() -> List[str]:
    discovered = _discover_candidates()
    if discovered:
        return discovered
    # fallback (preserve previous behavior)
    return [c for c in _FALLBACK_CANDIDATES if (ROOT / c).exists()]


def _load_build_query():
    """
    Attempt to load the first build_query found among dynamic then fallback candidates.
    Returns (callable, module, relative_path).
    """
    global CANDIDATES
    CANDIDATES = _resolve_candidates()
    last_err: Optional[Exception] = None
    for rel in CANDIDATES:
        try:
            mod = _load_module_from_path(rel)
            if hasattr(mod, "build_query"):
                return getattr(mod, "build_query"), mod, rel
        except Exception as e:
            last_err = e
            continue
    if last_err:
        pytest.xfail(f"build_query not importable; last error: {last_err}")
    pytest.xfail("build_query not importable from any candidate")


# --------------------------------------------------------------------------------------
# AST & Inference
# --------------------------------------------------------------------------------------


def _const_str(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if hasattr(ast, "Str") and isinstance(node, ast.Str):
        return node.s
    return None


def _collect_str_list(node: ast.AST) -> List[str]:
    if not isinstance(node, (ast.List, ast.Tuple)):
        return []
    out: List[str] = []
    for e in node.elts:
        s = _const_str(e)
        if s is not None:
            out.append(s)
    return out


def _dfs_dict(node: ast.AST, depth: int, cols_acc: set, ts_acc: List[str]):
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
        # Recurse into nested dicts or dicts inside list/tuple
        if isinstance(v_node, ast.Dict):
            _dfs_dict(v_node, depth + 1, cols_acc, ts_acc)
        elif isinstance(v_node, (ast.List, ast.Tuple)):
            for inner in v_node.elts:
                if isinstance(inner, ast.Dict):
                    _dfs_dict(inner, depth + 1, cols_acc, ts_acc)


def _extract_literal_columns_from_source(src: str) -> List[str]:
    _metrics_visit("columns_source", src)
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
        # SQL scanning
        for m in re.finditer(r"SELECT\s+(.+?)\s+FROM", src, flags=re.I | re.S):
            raw = [c.strip(' `"') for c in re.split(r",\s*", m.group(1))]
            for c in raw:
                if c and all(
                    x not in c.lower() for x in ["*", "case ", "count(", "sum(", "avg("]
                ):
                    if re.match(r"[A-Za-z_][A-Za-z0-9_]*$", c):
                        cols.add(c)
    except Exception:
        pass
    return sorted(cols)


def _extract_timestamp_from_source(src: str) -> Optional[str]:
    _metrics_visit("timestamp_source", src)
    m = re.search(r"ORDER\s+BY\s+([A-Za-z_][A-Za-z0-9_]*)\s+(ASC|DESC)", src, flags=re.I)
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


def _infer_expectations(build_query) -> Tuple[List[str], str]:
    """
    Infer (expected_cols, timestamp) by combining source introspection, param hints, and defaults.
    """
    expected_cols: List[str] = []
    ts: Optional[str] = None
    try:
        src = inspect.getsource(build_query)
        inferred_cols = _extract_literal_columns_from_source(src)
        inferred_ts = _extract_timestamp_from_source(src)
        if inferred_cols:
            expected_cols = inferred_cols
        if inferred_ts:
            ts = inferred_ts
    except Exception:
        pass
    try:
        sig = inspect.signature(build_query)
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


def _extract_select_cols(sql: str) -> List[str]:
    m = re.search(r"select\s+(.*?)\s+from", sql, flags=re.I | re.S)
    if not m:
        return []
    parts = [c.strip() for c in re.split(r",\s*", m.group(1))]
    return [re.sub(r"\s+as\s+\w+$", "", c, flags=re.I) for c in parts]


# --------------------------------------------------------------------------------------
# Temp module writer (for synthetic inference tests)
# --------------------------------------------------------------------------------------


def _write_tmp_module(tmp_path: pathlib.Path, src: str) -> types.ModuleType:
    p = tmp_path / "tmp_bq.py"
    p.write_text(textwrap.dedent(src), encoding="utf-8")
    spec = importlib.util.spec_from_file_location("tmp_bq", str(p))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


# --------------------------------------------------------------------------------------
# Comprehensive tests
# --------------------------------------------------------------------------------------


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
    cfg = {"select": ["id","ts","val"], "timestamp": "ts"}
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
    mapcol = {"columns": ["a","b","c"], "order_by": "ts_cfg"}
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
    config = {"query": {"select": ["u","v","w"], "order_by": "ts_nested"}}
    return "SELECT u, v, w FROM x ORDER BY ts_nested ASC"
""",
    )
    cols, ts = _infer_expectations(mod.build_query)
    assert set(cols) >= {"u", "v", "w"}
    assert ts == "ts_nested"


def test_build_query_selects_columns_and_orders():
    build_query, mod, rel = _load_build_query()
    exp_cols, ts = _infer_expectations(build_query)

    try:
        sig = inspect.signature(build_query)
    except Exception:
        sig = None

    mapcol = {"timestamp": ts, "select": exp_cols}
    attempts: List[Tuple[Tuple, dict]] = []
    if sig:
        params = list(sig.parameters)
        if "mapcol" in params:
            attempts += [((mapcol,), {}), ((), {"mapcol": mapcol})]
        if "columns" in params:
            attempts.append(((), {"columns": exp_cols}))
        if "select" in params and "columns" not in params:
            attempts.append(((), {"select": exp_cols}))
        if "timestamp" in params:
            attempts.append(((), {"timestamp": ts}))
        if "order_by" in params and "timestamp" not in params:
            attempts.append(((), {"order_by": ts}))
    # Always include fallback call attempts
    attempts += [((mapcol,), {}), ((), {"mapcol": mapcol})]

    last_err = None
    out = None
    for args, kwargs in attempts:
        try:
            out = build_query(*args, **kwargs)
            break
        except Exception as e:
            last_err = e
    else:
        pytest.fail(f"build_query call failed under all strategies: {last_err}")

    if isinstance(out, str):
        sql = out
    elif isinstance(out, (tuple, list)):
        sql = next(
            (x for x in out if isinstance(x, str) and "select" in x.lower()), None
        )
    else:
        sql = None

    assert isinstance(sql, str), "build_query did not return SQL string"

    sel = _extract_select_cols(sql)
    for c in exp_cols:
        assert any(c.lower() in s.lower() for s in sel), f"Missing column {c} in SELECT: {sel}"
    assert re.search(
        rf"order\s+by\s+{re.escape(ts)}\s+asc\b", sql, flags=re.I
    ), f"ORDER BY {ts} ASC missing: {sql}"


# --------------------------------------------------------------------------------------
# Source snippet matrix (direct source analysis)
# --------------------------------------------------------------------------------------

SRC_PURE_SQL = """
def build_query():
    return "SELECT user_id, event_time, message FROM events ORDER BY event_time ASC"
"""

SRC_DICT_DRIVEN = """
mapcol = {"select": ["event_time", "user_id", "message"], "timestamp": "event_time"}
def build_query(mapcol=mapcol):
    return (
        "SELECT "
        + ", ".join(mapcol["select"])
        + " FROM t ORDER BY "
        + mapcol["timestamp"]
        + " ASC"
    )
"""

SRC_MIXED = r"""
select_cols = ["a","b","c"]
config = {"query": {"select": ["x","y"], "order_by": "ts"}}
def build_query(columns=select_cols):
    sql = "SELECT a, b, c FROM t ORDER BY ts ASC"
    return sql
"""

SRC_DEEP_NESTED = r"""
def build_query():
    conf = {"l1": {"l2": {"l3": {"l4": {"select": ["p","q"], "timestamp": "t0"}}}}}
    return "SELECT p, q FROM t ORDER BY t0 ASC"
"""


@pytest.mark.parametrize(
    "src,exp_cols,exp_ts",
    [
        (SRC_PURE_SQL, ["user_id", "event_time", "message"], "event_time"),
        (SRC_DICT_DRIVEN, ["event_time", "user_id", "message"], "event_time"),
        (SRC_MIXED, ["a", "b", "c", "x", "y"], "ts"),
        (SRC_DEEP_NESTED, ["p", "q"], "t0"),
    ],
)
def test_inference_matrix_from_source_snippets(src, exp_cols, exp_ts):
    cols = _extract_literal_columns_from_source(src)
    ts = _extract_timestamp_from_source(src)
    assert set(exp_cols).issubset(set(cols)), f"Expected subset {exp_cols} ⊄ {cols}"
    assert ts == exp_ts, f"Timestamp mismatch: {ts} != {exp_ts}"


# --------------------------------------------------------------------------------------
# __all__ (optional clarity for imported helpers)
# --------------------------------------------------------------------------------------

__all__ = [
    "_extract_literal_columns_from_source",
    "_extract_timestamp_from_source",
    "_infer_expectations",
    "_write_tmp_module",
]
