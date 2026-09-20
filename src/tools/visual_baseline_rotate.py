#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def rotate(dir_path: Path, keep: int) -> list[str]:
    files = sorted([p for p in dir_path.glob("*.png") if p.is_file()])
    to_delete = files[:-keep] if keep > 0 else files
    for p in to_delete:
        p.unlink(missing_ok=True)
    # Remaining files after deletion
    remaining_files = sorted([p for p in dir_path.glob("*.png") if p.is_file()])
    # Update/refresh LATEST.png symlink/copy
    latest = remaining_files[-1] if remaining_files else None
    if latest:
        dst = dir_path / "LATEST.png"
        try:
            if dst.exists() or dst.is_symlink():
                dst.unlink()
            dst.symlink_to(latest.name)
        except Exception:
            # Fallback to copy
            dst.write_bytes(latest.read_bytes())
    return [str(p) for p in remaining_files]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Rotate baseline PNG artifacts (keep last N) per template directory"
    )
    ap.add_argument("--root", default="visual_baseline", help="Baseline root directory")
    ap.add_argument("--template", required=True, help="Template name (subdirectory under root)")
    ap.add_argument("--keep", type=int, default=5, help="How many to keep")
    args = ap.parse_args(argv)

    dir_path = Path(args.root) / args.template
    dir_path.mkdir(parents=True, exist_ok=True)

    kept = rotate(dir_path, args.keep)
    print(f"[OK] Kept {len(kept)} baseline(s) for {args.template}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
