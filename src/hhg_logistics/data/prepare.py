from __future__ import annotations

import csv
import sys
from pathlib import Path


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _split_rows(rows, split: float) -> tuple[list, list]:
    n = len(rows)
    k = max(1, int(n * (1 - split)))
    return rows[:k], rows[k:]


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: python -m hhg_logistics.data.prepare <input_csv> <out_dir>", file=sys.stderr)
        return 2
    in_csv = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
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
        rows = list(r)

    train, valid = _split_rows(rows, split=0.2)

    train_out = out_dir / "train.csv"
    valid_out = out_dir / "valid.csv"
    for pth in (train_out, valid_out):
        _ensure_dir(pth.parent)

    with train_out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "value"])
        w.writeheader()
        w.writerows(train)
    with valid_out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "value"])
        w.writeheader()
        w.writerows(valid)

    print(f"Wrote {len(train)} train and {len(valid)} valid rows to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
