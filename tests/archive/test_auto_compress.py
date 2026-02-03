"""
P2 Test: Auto Compression Pointer Style Variants

Cases:
- both (default)
- sidecar only
- embedded only (degraded scenario)

Uses small threshold to force compression.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

RAW_ROOT = Path("audit_artifacts/raw")
BUNDLE_ROOT = Path("audit_artifacts/bundles")


def setup_files():
    if RAW_ROOT.exists():
        shutil.rmtree(RAW_ROOT)
    if BUNDLE_ROOT.exists():
        shutil.rmtree(BUNDLE_ROOT)
    RAW_ROOT.mkdir(parents=True)
    BUNDLE_ROOT.mkdir(parents=True, exist_ok=True)
    # create ~1MB total
    (RAW_ROOT / "a.txt").write_text("x" * 400_000)
    (RAW_ROOT / "b.txt").write_text("y" * 400_000)
    (RAW_ROOT / "c.txt").write_text("z" * 400_000)


def run_env(env):
    subprocess.run(
        [
            sys.executable,
            "scripts/archive/select_and_compress.py",
            "--root",
            str(RAW_ROOT),
        ],
        check=True,
        env=env,
    )


def pointer_files():
    return list(BUNDLE_ROOT.glob("*.pointer.json"))


def sidecars():
    return list(BUNDLE_ROOT.glob("*.sha256"))


def test_pointer_both():
    setup_files()
    env = os.environ.copy()
    env["MAX_BUNDLE_MB"] = "1"
    env["ARCHIVE_POINTER_STYLE"] = "both"
    run_env(env)
    assert pointer_files(), "Pointer missing"
    assert sidecars(), "Sidecar missing for 'both' style"


def test_pointer_sidecar_only():
    setup_files()
    env = os.environ.copy()
    env["MAX_BUNDLE_MB"] = "1"
    env["ARCHIVE_POINTER_STYLE"] = "sidecar"
    run_env(env)
    assert pointer_files(), "Pointer missing"
    assert sidecars(), "Sidecar missing for 'sidecar' style"


def test_pointer_embedded_only():
    setup_files()
    env = os.environ.copy()
    env["MAX_BUNDLE_MB"] = "1"
    env["ARCHIVE_POINTER_STYLE"] = "embedded"
    run_env(env)
    assert pointer_files(), "Pointer missing"
    assert not sidecars(), "Sidecar should not exist for 'embedded'"
