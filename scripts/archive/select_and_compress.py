#!/usr/bin/env python
"""
Archive & Pointer (P2) with Knob Normalization

- Honors ARCHIVE_POINTER_STYLE: embedded | sidecar | both
- Skips already compressed files (.gz/.zip/.tar) in raw aggregation
- Respects AUTO_ARCHIVE_DISABLE
- Uses scripts.config.parse_knobs for normalization
"""
from __future__ import annotations
import json, os, sys, hashlib, tarfile, zipfile, time
from pathlib import Path
from typing import List

try:
    from scripts.config.parse_knobs import normalize_from_env
except Exception:
    def normalize_from_env():
        import os as _os
        return dict(_os.environ), []

SKIP_SUFFIXES = {".gz",".zip",".tar"}
BUNDLES_DIR = Path("audit_artifacts/bundles")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1<<16), b""):
            h.update(chunk)
    return h.hexdigest()


def aggregate_sha(paths: List[Path]) -> str:
    h = hashlib.sha256()
    for p in sorted(paths):
        h.update(sha256_file(p).encode())
    return h.hexdigest()


def collect_candidates(root: Path) -> List[Path]:
    return [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() not in SKIP_SUFFIXES]


def compress(root: Path, out: Path, members: List[Path], fmt: str):
    if fmt == "zip":
        with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for m in members:
                zf.write(m, arcname=m.relative_to(root))
    else:
        with tarfile.open(out, "w:gz") as tf:
            for m in members:
                tf.add(m, arcname=m.relative_to(root))


def human_size(b: int) -> str:
    return f"{b/1024/1024:.2f}MB"


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    
    root_arg = None
    if "--root" in argv:
        i = argv.index("--root")
        if i+1 < len(argv):
            root_arg = argv[i+1]
    
    root = Path(root_arg or "audit_artifacts/raw")
    if not root.exists():
        print("[INFO] Raw path missing; nothing to archive.")
        return 0
    
    knobs, knob_warnings = normalize_from_env()
    
    if knobs.get("AUTO_ARCHIVE_DISABLE", False) is True or str(knobs.get("AUTO_ARCHIVE_DISABLE")) == "1":
        print("[INFO] Auto archive disabled.")
        return 0
    
    fmt = knobs.get("ARCHIVE_FORMAT","tar.gz")
    pointer_style = knobs.get("ARCHIVE_POINTER_STYLE","both")
    threshold_mb = float(knobs.get("MAX_BUNDLE_MB", 25.0))
    
    candidates = collect_candidates(root)
    total = sum(p.stat().st_size for p in candidates)
    total_mb = total/1024/1024
    
    print(f"[INFO] Raw size: {human_size(total)} threshold={threshold_mb}MB")
    
    if total_mb < threshold_mb:
        print("[INFO] Below threshold; skipping compression.")
        return 0
    
    BUNDLES_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    ext = "tar.gz" if fmt=="tar.gz" else "zip"
    archive_path = BUNDLES_DIR / f"bundle_{stamp}.{ext}"
    
    print(f"[INFO] Compressing -> {archive_path}")
    compress(root, archive_path, candidates, fmt)
    
    original_sha = aggregate_sha(candidates)
    compressed_sha = sha256_file(archive_path)
    
    pointer = {
        "original_paths_count": len(candidates),
        "original_root": root.as_posix(),
        "compressed_file": archive_path.as_posix(),
        "archive_format": fmt,
        "total_original_size_bytes": total,
        "compressed_size_bytes": archive_path.stat().st_size,
        "original_sha_aggregate": original_sha,
        "compressed_sha": compressed_sha,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "warnings": list(knob_warnings),
    }
    
    # Write pointer and optional sidecar
    pointer_json = BUNDLES_DIR / f"bundle_{stamp}.pointer.json"
    pointer_json.write_text(json.dumps(pointer, indent=2), encoding="utf-8")
    
    if pointer_style in ("both","sidecar"):
        try:
            (BUNDLES_DIR / f"bundle_{stamp}.sha256").write_text(compressed_sha+"\n", encoding="utf-8")
        except Exception as e:
            # degrade to embedded-only
            data = json.loads(pointer_json.read_text())
            data.setdefault("warnings", []).append(f"sidecar_write_fail:{e}")
            data["warnings"].append("pointer_style_degraded:embedded")
            pointer_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    print(f"[INFO] Pointer written: {pointer_json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
