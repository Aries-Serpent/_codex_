"""
Test: Archival Tombstone Required (P6 Atomic Patchset)

- Simulates a deleted path by creating a "removed file" record and ensuring the compliance
  checker fails when no tombstone exists, and passes when the tombstone stub with ADR is
  present and an evidence entry exists.

This test is lightweight and uses local file system operations; it avoids modifying git history.
"""

import json
import subprocess
import sys
import uuid
from pathlib import Path


# Find repository root
def find_repo_root():
    """Find the repository root by looking for pyproject.toml"""
    current = Path(__file__).parent
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise RuntimeError("Cannot find repository root")


REPO_ROOT = find_repo_root()
CHECK = REPO_ROOT / "scripts/archival/check_archival_compliance.py"
EVIDENCE_DIR = REPO_ROOT / ".codex/evidence"
EVIDENCE_FILE = EVIDENCE_DIR / "archive_ops.jsonl"


def setup_removed_list(paths, test_id):
    p = REPO_ROOT / "tests/archival"
    p.mkdir(parents=True, exist_ok=True)
    rf = p / f"removed_paths_{test_id}.txt"
    rf.write_text("\n".join(paths), encoding="utf-8")
    # Ensure file is written to disk
    assert rf.exists(), f"Failed to create {rf}"
    return rf


def test_missing_tombstone_fails():
    # Use UUID to avoid conflicts with parallel test execution or pytest-randomly
    test_id = str(uuid.uuid4())[:8]
    # create fake removed path with unique name
    removed = [f"some/removed_file_{test_id}.py"]
    rf = setup_removed_list(removed, test_id)

    # ensure no tombstone present
    stub_path = REPO_ROOT / removed[0]
    if stub_path.exists():
        stub_path.unlink()

    # ensure evidence clean (backup existing)
    if EVIDENCE_FILE.exists():
        backup = EVIDENCE_FILE.read_text()
    else:
        backup = None

    r = subprocess.run(
        [sys.executable, str(CHECK), "--removed-file", str(rf)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )

    # cleanup
    rf.unlink()
    if backup:
        EVIDENCE_FILE.write_text(backup)

    assert r.returncode != 0, f"Expected failure but got {r.returncode}"


def test_tombstone_and_evidence_pass():
    # Use UUID to avoid conflicts with parallel test execution or pytest-randomly
    test_id = str(uuid.uuid4())[:8]
    removed = [f"some/removed_file_{test_id}.py"]
    rf = setup_removed_list(removed, test_id)

    # Create tombstone stub at the expected path (relative to repo root)
    stub = REPO_ROOT / removed[0]
    stub.parent.mkdir(parents=True, exist_ok=True)

    # create tombstone stub with ADR ref
    stub.write_text("# TOMBSTONE\nadr_ref: docs/arch/ADR-test.md\n", encoding="utf-8")

    # append evidence entry (backup existing)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    if EVIDENCE_FILE.exists():
        backup = EVIDENCE_FILE.read_text()
    else:
        backup = None

    entry = {"path": removed[0], "tombstone": True}
    with EVIDENCE_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")

    # Run the check from the repository root
    r = subprocess.run(
        [sys.executable, str(CHECK), "--removed-file", str(rf)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )

    # cleanup
    stub.unlink()
    if stub.parent.exists():
        try:
            stub.parent.rmdir()
        except OSError:
            pass  # directory not empty
    rf.unlink()

    # restore evidence
    if backup:
        EVIDENCE_FILE.write_text(backup)
    else:
        if EVIDENCE_FILE.exists():
            EVIDENCE_FILE.unlink()

    assert r.returncode == 0, f"Expected success but got {r.returncode}. stderr: {r.stderr}"
