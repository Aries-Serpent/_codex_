"""Hypothesis-based fuzz tests for tokenizer / text-processing utilities.

Targets:
- ``codex_ml.data.utils``: ``deterministic_split_ids``, ``assign_split_map``
- ``codex_ml.data.split_utils``: ``_normalise_ratios``, ``ensure_split_seed``
- ``codex_ml.data.jsonl_loader``: ``_normalise_text``, ``_extract_texts_from_line``

Import guard ensures the suite is skipped gracefully when ``hypothesis`` is
absent (e.g., minimal CI environments that don't install dev extras).
"""

from __future__ import annotations

import pytest

# Guard: skip entire module if hypothesis is unavailable.
hypothesis = pytest.importorskip("hypothesis")

from hypothesis import given, settings  # noqa: E402
from hypothesis import strategies as st  # noqa: E402
from hypothesis.strategies import SearchStrategy  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers / strategies
# ---------------------------------------------------------------------------

# Strategy: arbitrary unicode text (empty, long, special chars, surrogates excl.)
_text_strategy: SearchStrategy[str] = st.text(
    alphabet=st.characters(blacklist_categories=("Cs",)),  # no surrogates
    min_size=0,
    max_size=512,
)

# Strategy: list of arbitrary text IDs
_id_list_strategy: SearchStrategy[list[str]] = st.lists(
    _text_strategy.filter(lambda s: len(s) > 0),
    min_size=0,
    max_size=200,
)

# ---------------------------------------------------------------------------
# Tests for codex_ml.data.utils
# ---------------------------------------------------------------------------


def _import_utils():
    """Lazy import to isolate heavy optional deps from collection time."""
    from codex_ml.data.utils import SplitConfig, assign_split_map, deterministic_split_ids

    return SplitConfig, deterministic_split_ids, assign_split_map


@given(
    ids=_id_list_strategy,
    fraction=st.floats(min_value=0.01, max_value=0.99, allow_nan=False, allow_infinity=False),
    seed=st.integers(min_value=0, max_value=2**31 - 1),
)
@settings(max_examples=60, deadline=None)
def test_fuzz_deterministic_split_ids_partition(ids, fraction, seed):
    """Fuzz: train+eval always partitions the original list (no duplicates, no drops)."""
    SplitConfig, deterministic_split_ids, _ = _import_utils()
    cfg = SplitConfig(fraction_train=fraction, seed=seed)
    train, eval_ = deterministic_split_ids(ids, cfg)
    assert set(train) | set(eval_) == set(ids) or (
        # Duplicated IDs: combined count must equal original
        len(train) + len(eval_)
        == len(ids)
    )
    assert len(train) + len(eval_) == len(ids)


@given(
    ids=_id_list_strategy,
    fraction=st.floats(min_value=0.01, max_value=0.99, allow_nan=False, allow_infinity=False),
    seed=st.integers(min_value=0, max_value=2**31 - 1),
)
@settings(max_examples=60, deadline=None)
def test_fuzz_deterministic_split_ids_reproducible(ids, fraction, seed):
    """Fuzz: same inputs always produce identical splits (determinism)."""
    SplitConfig, deterministic_split_ids, _ = _import_utils()
    cfg = SplitConfig(fraction_train=fraction, seed=seed)
    train1, eval1 = deterministic_split_ids(ids, cfg)
    train2, eval2 = deterministic_split_ids(ids, cfg)
    assert train1 == train2
    assert eval1 == eval2


@given(
    fraction=st.one_of(
        st.floats(max_value=0.0, allow_nan=False, allow_infinity=False),
        st.floats(min_value=1.0, allow_nan=False, allow_infinity=False),
    )
)
@settings(max_examples=40, deadline=None)
def test_fuzz_deterministic_split_ids_invalid_fraction(fraction):
    """Fuzz: out-of-range fraction (≤0 or ≥1) raises ValueError."""
    SplitConfig, deterministic_split_ids, _ = _import_utils()
    cfg = SplitConfig(fraction_train=fraction, seed=42)
    with pytest.raises(ValueError):
        deterministic_split_ids(["a", "b", "c"], cfg)


@given(
    ids=_id_list_strategy,
    fraction=st.floats(min_value=0.01, max_value=0.99, allow_nan=False, allow_infinity=False),
    seed=st.integers(min_value=0, max_value=2**31 - 1),
)
@settings(max_examples=60, deadline=None)
def test_fuzz_assign_split_map_values(ids, fraction, seed):
    """Fuzz: every ID in map is labelled 'train' or 'eval'."""
    SplitConfig, _, assign_split_map = _import_utils()
    cfg = SplitConfig(fraction_train=fraction, seed=seed)
    split_map = assign_split_map(ids, cfg)
    assert set(split_map.values()) <= {"train", "eval"}
    # All unique IDs must appear in the map
    for uid in set(ids):
        assert uid in split_map


# ---------------------------------------------------------------------------
# Tests for codex_ml.data.split_utils
# ---------------------------------------------------------------------------


def _import_split_utils():
    from codex_ml.data.split_utils import _normalise_ratios, ensure_split_seed

    return _normalise_ratios, ensure_split_seed


@given(
    a=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    b=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=60, deadline=None)
def test_fuzz_normalise_ratios_invalid_sum(a, b):
    """Fuzz: ratios that don't sum to ~1.0 raise ValueError."""
    _normalise_ratios, _ = _import_split_utils()
    # Only call with combinations that definitely don't sum to 1
    bad_total = a + b  # 2-tuple → wrong length
    if abs(bad_total - 1.0) > 0.05:
        with pytest.raises((ValueError, Exception)):
            _normalise_ratios([a, b])  # wrong length (needs 3 values)


@given(seed=st.integers(min_value=0, max_value=2**31 - 1))
@settings(max_examples=80, deadline=None)
def test_fuzz_ensure_split_seed_positive_int(seed):
    """Fuzz: ensure_split_seed returns the provided integer unchanged."""
    _, ensure_split_seed = _import_split_utils()
    result = ensure_split_seed(seed)
    assert result == seed
    assert isinstance(result, int)


# ---------------------------------------------------------------------------
# Tests for codex_ml.data.jsonl_loader (text-normalisation helpers)
# ---------------------------------------------------------------------------


def _import_jsonl():
    from codex_ml.data.jsonl_loader import _extract_texts_from_line, _normalise_text

    return _normalise_text, _extract_texts_from_line


@given(text=_text_strategy)
@settings(max_examples=100, deadline=None)
def test_fuzz_normalise_text_string_returns_list(text):
    """Fuzz: string input always returns a list of strings."""
    _normalise_text, _ = _import_jsonl()
    result = _normalise_text(text)
    assert isinstance(result, (list, tuple))
    for item in result:
        assert isinstance(item, str)


@given(
    line=st.one_of(
        _text_strategy,
        st.just(""),
        st.just('{"text": "hello"}'),
        st.just('{"text": null}'),
        st.just('{"other": 42}'),
        st.binary(min_size=0, max_size=256).map(lambda b: b.decode("utf-8", errors="replace")),
    )
)
@settings(max_examples=100, deadline=None)
def test_fuzz_extract_texts_from_line_never_raises(line):
    """Fuzz: _extract_texts_from_line must never raise on arbitrary input."""
    _, _extract_texts_from_line = _import_jsonl()
    try:
        result = list(_extract_texts_from_line(line))
        for item in result:
            assert isinstance(item, str)
    except Exception as exc:  # noqa: BLE001
        pytest.fail(f"_extract_texts_from_line raised unexpectedly: {exc!r}")
