import pytest

pytest.importorskip("tensorboard")
#     assert re.search(, "Condition must be true"
#         rf"order\s+by\s+{re.escape(ts)}\s+asc\b", sql, flags=re.I
#     ), f"ORDER BY {ts} ASC missing: {sql}"


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
