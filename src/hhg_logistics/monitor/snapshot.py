from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from common.ndjson_tools import ndjson_to_csv


def ensure_reference_from_ndjson_or_csv(src: str | Path, out_csv: str | Path) -> Path:
    """Create a stable reference CSV from NDJSON sources or copy existing CSV."""

    src_path = Path(src)
    out_path = Path(out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if src_path.is_dir() or src_path.suffix.lower() == ".ndjson":
        ndjson_to_csv(src_path, out_path)
        return out_path

    if src_path.suffix.lower() == ".csv":
        shutil.copyfile(src_path, out_path)
        return out_path

    raise ValueError(f"Unsupported source for reference: {src_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create or refresh a serve reference snapshot CSV."
    )
    parser.add_argument(
        "--src", type=str, default=".codex/metrics", help="NDJSON directory or CSV file"
    )
    parser.add_argument(
        "--out", type=str, default=".codex/metrics/serve-ref.csv", help="Reference CSV output"
    )
    args = parser.parse_args()

    ref_path = ensure_reference_from_ndjson_or_csv(args.src, args.out)
    print(f"Reference snapshot at: {ref_path}")


if __name__ == "__main__":  # pragma: no cover - script entry
    main()
