from __future__ import annotations

import json
import math

import pytest

from codex_ml.io.atomic import canonical_json_dumps


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_canonical_json_forbids_nan_inf(bad: float) -> None:
    with pytest.raises(ValueError):
        canonical_json_dumps({"x": bad})


def test_canonical_json_is_deterministic() -> None:
    a = {"b": 1, "a": 2, "nested": {"z": 1, "y": 2}}
    x = canonical_json_dumps(a)
    y = canonical_json_dumps(dict(reversed(list(a.items()))))
    assert x == y
    # Round-trip ensures canonical form parses back to same structure.
    assert json.loads(x) == a
