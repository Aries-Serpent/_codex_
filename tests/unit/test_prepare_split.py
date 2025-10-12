from __future__ import annotations

from hhg_logistics.data.prepare import _split_rows


def test_split_rows_keeps_validation_non_empty_for_small_inputs() -> None:
    rows = [{"id": "1"}, {"id": "2"}]

    train, valid = _split_rows(rows, split=0.2, seed=None)

    assert len(train) == 1
    assert len(valid) == 1
