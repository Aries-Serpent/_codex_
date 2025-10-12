from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Iterable

import yaml


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _iter_rows(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    return list(rows)


def _split_rows(
    rows: list[dict[str, str]], split: float, seed: int | None
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    if not 0 < split < 1:
        raise ValueError("split must be between 0 and 1 (exclusive)")

    if seed is not None:
        import random

        rng = random.Random(seed)
        rows = rows.copy()
        rng.shuffle(rows)

    n = len(rows)
    if n == 0:
        return [], []

    k = max(1, int(round(n * (1 - split))))
    if n > 1:
        k = min(k, n - 1)
    else:
        k = min(k, n)
    return rows[:k], rows[k:]


def _load_prepare_params(params_path: Path | None) -> tuple[int | None, float | None]:
    if params_path is None:
        params_path = Path("params.yaml")

    if params_path.exists():
        with params_path.open() as f:
            data = yaml.safe_load(f) or {}
        prepare_cfg = data.get("prepare") or {}
        seed = prepare_cfg.get("seed")
        split = prepare_cfg.get("split")
        return seed, split

    return None, None


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="hhg_logistics.data.prepare",
        description="Prepare train/valid splits for the HHG logistics dataset.",
    )
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("out_dir", type=Path)
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for shuffling before splitting.",
    )
    parser.add_argument(
        "--split",
        type=float,
        default=None,
        help="Validation split ratio (0-1).",
    )
    parser.add_argument(
        "--params",
        type=Path,
        default=None,
        help="Optional path to params.yaml file for defaults.",
    )
    return parser.parse_args(argv)


def main() -> int:
    args = _parse_args(sys.argv[1:])
    in_csv = args.input_csv
    out_dir = args.out_dir
    seed = args.seed
    split = args.split

    params_seed, params_split = _load_prepare_params(args.params)
    if seed is None:
        seed = params_seed
    if split is None:
        split = params_split if params_split is not None else 0.2

    if split is None:
        raise ValueError("Split ratio must be provided either via CLI or params.yaml")
    _ensure_dir(out_dir)

    if not in_csv.exists():
        # create placeholder for reproducibility
        _ensure_dir(in_csv.parent)
        with in_csv.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["id", "value"])
            for i in range(10):
                w.writerow([i, i % 3])

    with in_csv.open() as f:
        r = csv.DictReader(f)
        rows = _iter_rows(r)
        fieldnames = list(r.fieldnames or [])

    if not fieldnames:
        # Fallback for headerless CSVs: preserve key order from the first row.
        for row in rows:
            fieldnames.extend(k for k in row.keys() if k not in fieldnames)
            if fieldnames:
                break

    if not fieldnames:
        fieldnames = ["id", "value"]

    train, valid = _split_rows(rows, split=split, seed=seed)

    train_out = out_dir / "train.csv"
    valid_out = out_dir / "valid.csv"
    for pth in (train_out, valid_out):
        _ensure_dir(pth.parent)

    with train_out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(train)
    with valid_out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(valid)

    print(f"Wrote {len(train)} train and {len(valid)} valid rows to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
