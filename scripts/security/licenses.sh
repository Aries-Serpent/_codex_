#!/usr/bin/env bash
# Generate THIRD_PARTY_NOTICES.md using pip-licenses (local)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT_DIR="${ROOT}/artifacts/licenses"
OUT_FILE="${OUT_DIR}/THIRD_PARTY_NOTICES.md"

mkdir -p "${OUT_DIR}"

export OUT_FILE
python - <<'PY'
import os
import pathlib
import subprocess

out = pathlib.Path(os.environ["OUT_FILE"])
# Install tool locally into the active environment
subprocess.run(["python", "-m", "pip", "install", "pip-licenses"], check=True)
with out.open("w", encoding="utf-8") as fh:
    subprocess.run(
        [
            "pip-licenses",
            "--format=markdown",
            "--with-urls",
            "--with-license-file",
        ],
        check=True,
        stdout=fh,
    )
print(f"[LICENSES] Wrote {out.as_posix()}")
PY
