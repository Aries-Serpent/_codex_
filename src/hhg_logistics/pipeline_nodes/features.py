from __future__ import annotations

import csv
from collections.abc import Sequence
from pathlib import Path


def build_features(
    rows: list[dict],
    even_flag: bool = True,
    passthrough: Sequence[str] = ("id", "value"),
) -> list[dict]:
    features: list[dict] = []
    for row in rows:
        feat_row = {key: row[key] for key in passthrough if key in row}
        if even_flag and "value" in row:
            feat_row["value_is_even"] = int(row["value"]) % 2 == 0
        features.append(feat_row)
    return features


def write_features_csv(rows: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    headers = list(rows[0].keys()) if rows else ["id", "value", "value_is_even"]
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
