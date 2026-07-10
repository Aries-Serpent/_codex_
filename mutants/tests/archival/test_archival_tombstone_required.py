"""
Test: Archival Tombstone Required (P6 Atomic Patchset)

- Simulates a deleted path by creating a "removed file" record and ensuring the compliance
  checker fails when no tombstone exists, and passes when the tombstone stub with ADR is
  present and an evidence entry exists.

This test is lightweight and uses local file system operations; it avoids modifying git history.

Test artifacts are stored in `.codex/test_artifacts/archival/` and cleaned up in finally blocks.
Per repository policy (.codex/archive/deprecated/AGENTS.md), `.codex/` directory contents follow 30-day retention.
Tests attempt to remove empty directories after cleanup to minimize artifact accumulation.
"""

import json
import os
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
TEST_ARTIFACTS_DIR = REPO_ROOT / ".codex/test_artifacts/archival"


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
    # Use test-specific directory to avoid polluting repository root
    removed = [f".codex/test_artifacts/archival/removed_file_{test_id}.py"]
    rf = setup_removed_list(removed, test_id)

    # ensure no tombstone present
    stub_path = REPO_ROOT / removed[0]
    if stub_path.exists():
        stub_path.unlink()

    # ensure evidence clean (backup existing)
    backup = EVIDENCE_FILE.read_text() if EVIDENCE_FILE.exists() else None

    try:
        r = subprocess.run(
            [sys.executable, str(CHECK), "--removed-file", str(rf)],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        assert r.returncode != 0, f"Expected failure but got {r.returncode}"
    finally:
        # cleanup: remove test file list
        rf.unlink()
        # cleanup: remove test artifacts directory if empty
        if stub_path.parent.exists():
            try:
                stub_path.parent.rmdir()  # Only succeeds if directory is empty
            except OSError:
                _ = None  # directory not empty or doesn't exist
        if backup:
            EVIDENCE_FILE.write_text(backup)


def test_tombstone_and_evidence_pass():
    # Use UUID to avoid conflicts with parallel test execution or pytest-randomly
    test_id = str(uuid.uuid4())[:8]
    # Use test-specific directory to avoid polluting repository root
    removed = [f".codex/test_artifacts/archival/removed_file_{test_id}.py"]
    rf = setup_removed_list(removed, test_id)

    # Create tombstone stub at the expected path (relative to repo root)
    stub = REPO_ROOT / removed[0]
    stub.parent.mkdir(parents=True, exist_ok=True)

    # create tombstone stub with ADR ref
    stub.write_text("# TOMBSTONE\nadr_ref: docs/arch/ADR-test.md\n", encoding="utf-8")

    # append evidence entry (backup existing)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    backup = EVIDENCE_FILE.read_text() if EVIDENCE_FILE.exists() else None

    entry = {"path": removed[0], "tombstone": True}
    with EVIDENCE_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")

    try:
        # Run the check from the repository root
        r = subprocess.run(
            [sys.executable, str(CHECK), "--removed-file", str(rf)],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        assert r.returncode == 0, f"Expected success but got {r.returncode}. stderr: {r.stderr}"
    finally:
        # cleanup: remove tombstone stub
        if stub.exists():
            stub.unlink()
        # cleanup: remove test artifacts directory if empty (try parent directories up to test_artifacts)
        current = stub.parent
        test_artifacts_root = REPO_ROOT / ".codex/test_artifacts"
        while current != test_artifacts_root and current.exists():
            try:
                current.rmdir()  # Only succeeds if directory is empty
                current = current.parent
            except OSError:
                break  # directory not empty, stop trying
        # cleanup: remove test file list
        rf.unlink()

        # restore evidence
        if backup:
            EVIDENCE_FILE.write_text(backup)
        else:
            if EVIDENCE_FILE.exists():
                EVIDENCE_FILE.unlink()


def test_rename_without_adr_is_flagged():
    """Ensure rename entries require ADR/evidence like deletions."""

    # Import inside test to allow monkeypatching the evidence path safely.
    from scripts.archival import check_archival_compliance as compliance

    test_id = str(uuid.uuid4())[:8]
    original_relative = f".codex/test_artifacts/archival/renamed_original_{test_id}.py"
    destination_relative = f".codex/test_artifacts/archival/renamed_destination_{test_id}.py"

    stub_path = REPO_ROOT / original_relative
    stub_path.parent.mkdir(parents=True, exist_ok=True)
    stub_path.write_text("# TOMBSTONE\n", encoding="utf-8")

    # Point compliance checker to an isolated evidence file for this test.
    previous_evidence = compliance.EVIDENCE
    compliance.EVIDENCE = REPO_ROOT / f".codex/test_artifacts/archival/evidence_{test_id}.jsonl"
    if compliance.EVIDENCE.exists():
        compliance.EVIDENCE.unlink()

    entry = compliance.DiffEntry(
        status="R100", path=destination_relative, original_path=original_relative
    )

    try:
        previous_cwd = Path.cwd()
        os.chdir(REPO_ROOT)
        try:
            result = compliance.evaluate_entries([entry])
        finally:
            os.chdir(previous_cwd)
        assert original_relative in result.missing_adr, "Rename without ADR should be flagged"
        assert (original_relative in result.missing_evidence, "Result must not be empty"
        ), "Rename without evidence should be flagged"
        assert result.return_code == 2, "Missing ADR should cause failure return code"
    finally:
        compliance.EVIDENCE = previous_evidence
        if stub_path.exists():
            stub_path.unlink()
        current = stub_path.parent
        test_artifacts_root = REPO_ROOT / ".codex/test_artifacts"
        while current != test_artifacts_root and current.exists():
            try:
                current.rmdir()
                current = current.parent
            except OSError:
                break


def test_copy_does_not_require_tombstone():
    """
    Ensure copy entries (C status) do not require tombstone/ADR/evidence.

    A git copy leaves the original file intact and creates a new file at the destination.
    This is not a removal operation and should not trigger archival compliance checks.
    """
    from scripts.archival import check_archival_compliance as compliance

    test_id = str(uuid.uuid4())[:8]
    original_relative = f".codex/test_artifacts/archival/copied_original_{test_id}.py"
    destination_relative = f".codex/test_artifacts/archival/copied_destination_{test_id}.py"

    # Create the original file (it stays intact in a copy)
    original_path = REPO_ROOT / original_relative
    original_path.parent.mkdir(parents=True, exist_ok=True)
    original_path.write_text("# Original file content\n", encoding="utf-8")

    # Point compliance checker to an isolated evidence file for this test
    previous_evidence = compliance.EVIDENCE
    compliance.EVIDENCE = REPO_ROOT / f".codex/test_artifacts/archival/evidence_{test_id}.jsonl"
    if compliance.EVIDENCE.exists():
        compliance.EVIDENCE.unlink()

    entry = compliance.DiffEntry(
        status="C100", path=destination_relative, original_path=original_relative
    )

    try:
        previous_cwd = Path.cwd()
        os.chdir(REPO_ROOT)
        try:
            result = compliance.evaluate_entries([entry])
        finally:
            os.chdir(previous_cwd)

        # Copy operations should NOT be flagged for missing tombstone, ADR, or evidence
        assert (original_relative not in result.missing_stub, "Result must not be empty"
        ), "Copy should not require tombstone stub"
        assert original_relative not in result.missing_adr, "Copy should not require ADR"
        assert original_relative not in result.missing_evidence, "Copy should not require evidence"
        assert result.return_code == 0, "Copy operations should pass compliance check"
    finally:
        compliance.EVIDENCE = previous_evidence
        if original_path.exists():
            original_path.unlink()
        current = original_path.parent
        test_artifacts_root = REPO_ROOT / ".codex/test_artifacts"
        while current != test_artifacts_root and current.exists():
            try:
                current.rmdir()
                current = current.parent
            except OSError:
                break
