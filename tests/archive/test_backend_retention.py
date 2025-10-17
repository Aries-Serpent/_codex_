"""Regression coverage for archive retention semantics."""

from __future__ import annotations

import hashlib
from collections.abc import Iterator
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from codex.archive.backend import ArchiveConfig
from codex.archive.backend import ArchiveDAL as ArchiveBackend


@pytest.fixture
def archive_backend(tmp_path: Path) -> Iterator[ArchiveBackend]:
    """Provide a fresh SQLite-backed ``ArchiveBackend`` instance."""

    db_path = tmp_path / "archive.sqlite"
    config = ArchiveConfig(url=f"sqlite:///{db_path}", backend="sqlite")
    backend = ArchiveBackend(config=config)
    try:
        yield backend
    finally:
        connection = getattr(backend, "_conn", None)
        if connection is not None:
            connection.close()


def _archive_sample(
    backend: ArchiveBackend,
    *,
    repo: str,
    path: str,
    content: bytes,
    reason: str = "legacy",
    commit_sha: str = "deadbeef",
    legal_hold: bool | int = False,
    delete_after: str | None = None,
) -> dict[str, Any]:
    sha = hashlib.sha256(content).hexdigest()
    artifact_payload = {
        "content_sha256": sha,
        "size_bytes": len(content),
        "compression": "none",
        "mime_type": "text/plain",
        "storage_driver": "db",
        "blob_bytes": content,
        "object_url": None,
    }
    metadata = {
        "sha256": sha,
        "size_bytes": len(content),
        "legal_hold": legal_hold,
    }
    if delete_after is not None:
        metadata["delete_after"] = delete_after
    result = backend.record_archive(
        repo=repo,
        path=path,
        commit_sha=commit_sha,
        language="python",
        reason=reason,
        kind="code",
        artifact_payload=artifact_payload,
        archived_by="pytest",
        metadata=metadata,
        context={"trigger": "unit-test"},
        tags=["retention"],
    )
    return result


def test_delete_approval_blocked_by_legal_hold(archive_backend: ArchiveBackend) -> None:
    """``record_delete_approval`` should not allow deletion under legal hold."""

    tombstone = _archive_sample(
        archive_backend,
        repo="acme/example",
        path="src/example.py",
        content=b"print('under hold')\n",
        legal_hold=True,
        delete_after=(datetime.now(timezone.utc) + timedelta(days=90)).isoformat(),
    )["tombstone_id"]

    with pytest.raises(PermissionError):
        archive_backend.record_delete_approval(
            tombstone,
            primary_actor="alice",
            secondary_actor="bob",
            reason="retention review",
            apply=False,
        )


def test_delete_apply_scrubs_only_single_reference(archive_backend: ArchiveBackend) -> None:
    """Blob bytes are only scrubbed when the artifact has a single reference."""

    first = _archive_sample(
        archive_backend,
        repo="acme/example",
        path="src/single.py",
        content=b"print('single')\n",
    )

    scrubbed = archive_backend.record_delete_approval(
        first["tombstone_id"],
        primary_actor="alice",
        secondary_actor="bob",
        reason="retention cleanup",
        apply=True,
    )
    assert scrubbed is True

    payload = archive_backend.get_restore_payload(first["tombstone_id"])
    assert payload["artifact"]["blob_bytes"] is None
    assert payload["artifact"]["storage_driver"] == "object"

    shared_one = _archive_sample(
        archive_backend,
        repo="acme/example",
        path="src/shared_one.py",
        content=b"print('shared')\n",
    )
    shared_two = _archive_sample(
        archive_backend,
        repo="acme/example",
        path="src/shared_two.py",
        content=b"print('shared')\n",
    )

    scrubbed_shared = archive_backend.record_delete_approval(
        shared_one["tombstone_id"],
        primary_actor="alice",
        secondary_actor="bob",
        reason="shared cleanup",
        apply=True,
    )
    assert scrubbed_shared is False

    shared_payload = archive_backend.get_restore_payload(shared_one["tombstone_id"])
    assert shared_payload["artifact"]["blob_bytes"] is not None
    assert shared_payload["artifact"]["id"] == shared_two["artifact_id"]


def test_delete_after_metadata_persisted_and_list_respects_retention(
    archive_backend: ArchiveBackend,
) -> None:
    """Ensure ``delete_after`` is stored and list ordering supports retention windows."""

    repo = "acme/policy"
    older_delete_after = (datetime.now(timezone.utc) - timedelta(days=45)).isoformat()
    newer_delete_after = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()

    older = _archive_sample(
        archive_backend,
        repo=repo,
        path="src/old.py",
        content=b"print('old')\n",
        delete_after=older_delete_after,
    )
    newer = _archive_sample(
        archive_backend,
        repo=repo,
        path="src/new.py",
        content=b"print('new')\n",
        delete_after=newer_delete_after,
    )

    older_item = archive_backend.show_item(older["tombstone_id"])
    newer_item = archive_backend.show_item(newer["tombstone_id"])
    assert older_item["delete_after"] == older_delete_after
    assert newer_item["delete_after"] == newer_delete_after
    assert older_item["metadata"]["delete_after"] == older_delete_after
    assert newer_item["metadata"]["delete_after"] == newer_delete_after

    listed = archive_backend.list_items(repo=repo, limit=2)
    listed_tombstones = [row["tombstone_id"] for row in listed]
    assert listed_tombstones == [newer["tombstone_id"], older["tombstone_id"]]

    truncated = archive_backend.list_items(repo=repo, limit=1)
    assert truncated[0]["tombstone_id"] == newer["tombstone_id"]
