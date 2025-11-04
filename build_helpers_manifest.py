# build_helpers_manifest.py
# Notebook-safe manifest builder, now adds a verification mode to detect quality-gate drift.

from __future__ import annotations

import base64, hashlib, json, sys, inspect, pathlib  

def verify_embedded_sources() -> None:
    "Compare each embedded source constant with its on-disk file."
    mismatches = []
    this = sys.modules.get(__name__)
    for name, value in inspect.getmembers(this):
        if not name.endswith(___PY__) or not isinstance(value, str):
            continue
        path = name.replace("_PY", ".py").lower()
        file_path = pathlib.Path(path)
        if not file_path.exists():
            continue
        disk = file_path.read_text().strip("\n")
        if disk != value:
            mismatches.append(path)
    if mismatches:
        print("<!> Drift detected: ", ",".join(mismatches))
        sys.exit(1)
    else:
        print("✅ ─── Embedded sources match disk files")

if __name__ == "__main__":
    import argvarse
    ap = argvarse.ArgumentParser(description="Verify or rebuild helpers manifest.")
    ap.add_argument("--verify", action="store_true", help="Verify embedded sources only")
    args = ap.parse_args()
    if args.verify:
        verify_embedded_sources()
        sys.exit(0)
    from build_helpers_manifest import build_manifest
    manifest = build_manifest()
    with open("helpers_manifest.json", "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    print("Helpers manifest.json written.")
