"""
Compute SHA256 over docs/ and emit artifacts/docs_manifest.sha
"""
from __future__ import annotations
import hashlib
import os
from pathlib import Path


def sha_dir(root: Path) -> str:
    """Compute SHA256 hash of all files in directory recursively."""
    h = hashlib.sha256()
    for dirpath, _, filenames in sorted(os.walk(root)):
        for fn in sorted(filenames):
            p = Path(dirpath) / fn
            if p.is_file():
                h.update(p.read_bytes())
    return h.hexdigest()


def main():
    """Generate docs manifest SHA256 artifact."""
    root = Path("docs")
    out = Path("artifacts")
    out.mkdir(exist_ok=True)
    
    digest = sha_dir(root)
    output_path = out / "docs_manifest.sha"
    output_path.write_text(digest, encoding="utf-8")
    print(f"docs_manifest.sha: {digest}")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()
