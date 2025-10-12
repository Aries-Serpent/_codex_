from __future__ import annotations

import csv
from collections.abc import Sequence
from pathlib import Path


def _coerce_row(row: dict, required: Sequence[str]) -> dict:
    coerced: dict = {}
    for key in required:
        coerced[key] = row.get(key)
    if coerced.get("id") is not None:
        coerced["id"] = int(coerced["id"])
    if coerced.get("value") is not None:
        coerced["value"] = int(coerced["value"])
    return coerced


def clean_rows(
    rows: list[dict],
    required_columns: Sequence[str],
    value_minmax: tuple[int, int] = (0, 2),
    drop_na: bool = True,
) -> list[dict]:
    vmin, vmax = value_minmax
    cleaned: list[dict] = []
    for row in rows:
        coerced = _coerce_row(row, required_columns)
        if drop_na and any(coerced.get(col) is None for col in required_columns):
            continue
        if coerced.get("value") is None:
            continue
        if not (vmin <= int(coerced["value"]) <= vmax):
            continue
        cleaned.append(coerced)

    seen_ids = set()
    unique_rows: list[dict] = []
    for row in cleaned:
        if row["id"] in seen_ids:
            continue
        seen_ids.add(row["id"])
        unique_rows.append(row)
    return unique_rows


def write_clean_csv(rows: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "value"])
        writer.writeheader()
        writer.writerows(rows)
