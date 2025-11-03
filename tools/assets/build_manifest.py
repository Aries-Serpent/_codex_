#!/usr/bin/env python3
import json
from pathlib import Path

def sha256_of(p: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

INCLUDE_DIRS = ["docs","reports","src","tools","tokenization"]

def main():
    files = {}
    for d in INCLUDE_DIRS:
        p_dir = Path(d)
        if not p_dir.exists():
            continue
        for p in p_dir.rglob("*"):
            if p.is_file():
                try:
                    files[str(p)] = sha256_of(p)
                except Exception:
                    pass
    from datetime import datetime, timezone
    out = {"generated_utc": datetime.now(timezone.utc).isoformat()+"Z", "files": files}
    Path("assets").mkdir(exist_ok=True)
    Path("assets/manifest.json").write_text(json.dumps(out, indent=2))
    print("assets/manifest.json")

if __name__ == "__main__":
    main()
