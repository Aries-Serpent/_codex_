"""Ensure canonical JSON codec rejects non-finite numbers."""

from __future__ import annotations

import importlib
import math

import pytest

schema_v2 = importlib.import_module("codex_ml.checkpointing.schema_v2")
to_bytes = getattr(schema_v2, "to_canonical_bytes", None)


@pytest.mark.skipif(to_bytes is None, reason="to_canonical_bytes not available")
@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_canonicalization_rejects_nonfinite_numbers(bad):
    """The canonicalisation helper should refuse NaN/Inf payloads."""

    assert to_bytes is not None
    with pytest.raises(ValueError):
        to_bytes({"x": bad})
