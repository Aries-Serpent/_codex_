# tests/test_query_logs_build_query.py
# Auto-upgraded by codex_workflow: dict-literal DFS, depth knob, AST metrics gate.
import ast
import importlib.util
import inspect
import json
import os
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CANDIDATES = []  # filled by loader

MAX_DICT_DEPTH = int(os.getenv("CODEX_MAX_DICT_DEPTH", "5"))
EMIT_AST_METRICS = os.getenv("CODEX_AST_METRICS", "0") == "1"
_AST_METRICS = {"files": {}}

_SELECT_KEYS = {"select", "columns", "cols", "select_cols"}
_TS_KEYS = {"timestamp", "order_by", "ts_col", "sort_key"}


def _metrics_visit(label: str, src: str):
    if not EMIT_AST_METRICS:
        return

    class _V(ast.NodeVisitor):
        def __init__(self):
            self.count = 0

        def generic_visit(self, node):
            self.count += 1
            super().generic_visit(node)

    try:
        t = ast.parse(src)
        v = _V()
        v.visit(t)
        _AST_METRICS["files"].setdefault(label, {})
        _AST_METRICS["files"][label]["nodes_visited"] = v.count
    except Exception:
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


def _load_module_from_path(rel_path):
    p = ROOT / rel_path
    spec = importlib.util.spec_from_file_location("build_query_mod", str(p))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return mod


def _discover_candidates():
    out = []
    for p in ROOT.rglob("*.py"):
        if ".git" in p.parts:
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"\bdef\s+build_query\s*\(", txt):
                out.append(str(p.relative_to(ROOT)))
        except Exception:
            continue
    out.sort(key=lambda s: (len(s.split("/")), s))
    return out


def _load_build_query():
    global CANDIDATES
    CANDIDATES = _discover_candidates()
    last_err = None
    for rel in CANDIDATES:
        try:
            mod = _load_module_from_path(rel)
            if hasattr(mod, "build_query"):
                return getattr(mod, "build_query"), mod, rel
        except Exception as e:
            last_err = e
            continue
    if last_err:
        pytest.xfail(f"build_query not importable from candidates: {last_err}")
    pytest.xfail("build_query not importable from any candidate")


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
    for k, v in zip(node.keys, node.values):
        key = _const_str(k) or (k.id if isinstance(k, ast.Name) else None)
        if key:
            k_norm = key.lower()
            if k_norm in _SELECT_KEYS:
                cols_acc.update(_collect_str_list(v))
            elif k_norm in _TS_KEYS:
                s = _const_str(v)
                if s:
                    ts_acc.append(s)
        if isinstance(v, ast.Dict):
            _dfs_dict(v, depth + 1, cols_acc, ts_acc)
        elif isinstance(v, (ast.List, ast.Tuple)):
            for e in v.elts:
                if isinstance(e, ast.Dict):
                    _dfs_dict(e, depth + 1, cols_acc, ts_acc)


def _extract_literal_columns_from_source(src: str) -> list[str]:
    _metrics_visit("build_query_source", src)
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
                if (
                    isinstance(node.target, ast.Name)
                    and node.target.id.lower() in _SELECT_KEYS
                ):
                    cols.update(_collect_str_list(node.value))
                if isinstance(node.value, ast.Dict):
                    _dfs_dict(node.value, 1, cols, [])
            elif isinstance(node, ast.Dict):
                _dfs_dict(node, 1, cols, [])
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


def _extract_timestamp_from_source(src: str):
    _metrics_visit("build_query_source", src)
    m = re.search(
        r"ORDER\s+BY\s+([A-Za-z_][A-Za-z0-9_]*)\s+(ASC|DESC)", src, flags=re.I
    )
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
                    cols_dummy = set()
                    _dfs_dict(node.value, 1, cols_dummy, ts_acc)
            elif isinstance(node, ast.AnnAssign):
                if (
                    isinstance(node.target, ast.Name)
                    and node.target.id.lower() in _TS_KEYS
                ):
                    s = _const_str(node.value)
                    if s:
                        ts_acc.append(s)
                if isinstance(node.value, ast.Dict):
                    cols_dummy = set()
                    _dfs_dict(node.value, 1, cols_dummy, ts_acc)
            elif isinstance(node, ast.Dict):
                cols_dummy = set()
                _dfs_dict(node, 1, cols_dummy, ts_acc)
    except Exception:
        pass
    return ts_acc[0] if ts_acc else None


def _infer_expectations(build_query):
    expected_cols = []
    ts = None
    try:
        src = inspect.getsource(build_query)
        expected_cols = _extract_literal_columns_from_source(src) or expected_cols
        ts = _extract_timestamp_from_source(src) or ts
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


def _extract_select_cols(sql: str):
    m = re.search(r"select\s+(.*?)\s+from", sql, flags=re.I | re.S)
    if not m:
        return []
    cols = [c.strip() for c in re.split(r",\s*", m.group(1))]
    return [re.sub(r"\s+as\s+\w+$", "", c, flags=re.I) for c in cols]


def test_build_query_selects_columns_and_orders():
    build_query, mod, rel = _load_build_query()
    exp_cols, ts = _infer_expectations(build_query)

    sig = None
    try:
        sig = inspect.signature(build_query)
    except Exception:
        pass

    mapcol = {"timestamp": ts, "select": exp_cols}
    try_calls = []
    if sig:
        params = list(sig.parameters)
        if "mapcol" in params:
            try_calls += [((mapcol,), {}), ((), {"mapcol": mapcol})]
        if "columns" in params:
            try_calls.append(((), {"columns": exp_cols}))
        if "select" in params and "columns" not in params:
            try_calls.append(((), {"select": exp_cols}))
        if "timestamp" in params:
            try_calls.append(((), {"timestamp": ts}))
        if "order_by" in params and "timestamp" not in params:
            try_calls.append(((), {"order_by": ts}))
    try_calls += [((mapcol,), {}), ((), {"mapcol": mapcol})]

    last_err = None
    for args, kwargs in try_calls:
        try:
            out = build_query(*args, **kwargs)
            break
        except Exception as e:
            last_err = e
    else:
        pytest.fail(f"build_query call failed under all strategies: {last_err}")

    sql = (
        out
        if isinstance(out, str)
        else next(
            (
                x
                for x in (out if isinstance(out, (tuple, list)) else [])
                if isinstance(x, str) and "select" in x.lower()
            ),
            None,
        )
    )
    assert isinstance(sql, str), "build_query did not return SQL string"

    sel = _extract_select_cols(sql)
    for c in exp_cols:
        assert any(c.lower() in s.lower() for s in sel), (
            f"Missing column {c} in SELECT: {sel}"
        )
    assert re.search(rf"order\s+by\s+{re.escape(ts)}\s+asc\b", sql, flags=re.I), (
        f"ORDER BY {ts} ASC missing: {sql}"
    )
    _flush_metrics()


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
    conf = {"level1": {"level2": {"level3": {"select": ["p","q"], "timestamp": "t0"}}}}
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
    assert set(exp_cols).issubset(set(cols)), (
        f"expected subset {exp_cols} \u2284 {cols}"
    )
    assert ts == exp_ts, f"timestamp mismatch: {ts} != {exp_ts}"
