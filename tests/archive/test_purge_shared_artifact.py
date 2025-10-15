from __future__ import annotations

import hashlib
import json
from pathlib import Path

from codex.archive.backend import ArchiveConfig, ArchiveDAL


def _dal(tmp_path: Path) -> ArchiveDAL:
    db_path = tmp_path / "archive.sqlite"
    config = ArchiveConfig(url=f"sqlite:///{db_path.as_posix()}", backend="sqlite")
    return ArchiveDAL(config=config)


def _artifact_payload(content: bytes) -> dict[str, object]:
    return {
        "content_sha256": hashlib.sha256(content).hexdigest(),
        "size_bytes": len(content),
        "compression": "raw",
        "mime_type": "text/plain",
        "storage_driver": "db",
        "blob_bytes": content,
        "object_url": None,
    }


def _record(
    dal: ArchiveDAL,
    *,
    repo: str,
    path: str,
    tombstone_reason: str,
    artifact_content: bytes,
) -> dict[str, str]:
    payload = dal.record_archive(
        repo=repo,
        path=path,
        commit_sha="0" * 40,
        language="python",
        reason=tombstone_reason,
        kind="code",
        artifact_payload=_artifact_payload(artifact_content),
        archived_by="tester",
        metadata={},
        context={},
    )
    return {
        "tombstone": payload["tombstone_id"],
        "artifact": payload["artifact_id"],
        "item": payload["item_id"],
    }


def test_purge_skips_shared_artifact(tmp_path: Path) -> None:
    dal = _dal(tmp_path)
    first = _record(
        dal,
        repo="example",
        path="src/foo.py",
        tombstone_reason="dead",
        artifact_content=b"print('hello')\n",
    )
    second = _record(
        dal,
        repo="example",
        path="src/bar.py",
        tombstone_reason="dead",
        artifact_content=b"print('hello')\n",
    )

    scrubbed = dal.record_delete_approval(
        first["tombstone"],
        primary_actor="alice",
        secondary_actor="bob",
        reason="redundant",
        apply=True,
    )

    assert not scrubbed

    restore_payload = dal.get_restore_payload(second["tombstone"])
    artifact = restore_payload["artifact"]
    assert artifact["blob_bytes"] is not None

    with dal._transaction() as execute:  # type: ignore[attr-defined]
        events = execute(
            """
            SELECT context
            FROM event
            WHERE item_id = :item_id AND action = 'DELETE_APPROVED'
            ORDER BY created_at
            """,
            {"item_id": first["item"]},
            fetchall=True,
        )
    contexts = [json.loads(row["context"]) for row in events]
    assert all(ctx.get("blob_scrubbed") is False for ctx in contexts)
    assert any(ctx.get("shared_references") == 1 for ctx in contexts)


def test_purge_scrubs_single_reference(tmp_path: Path) -> None:
    dal = _dal(tmp_path)
    record = _record(
        dal,
        repo="example",
        path="src/single.py",
        tombstone_reason="dead",
        artifact_content=b"print('bye')\n",
    )

    scrubbed = dal.record_delete_approval(
        record["tombstone"],
        primary_actor="alice",
        secondary_actor="bob",
        reason="retired",
        apply=True,
    )

    assert scrubbed

    restore_payload = dal.get_restore_payload(record["tombstone"])
    artifact = restore_payload["artifact"]
    assert artifact["blob_bytes"] is None
    assert artifact["storage_driver"] == "object"
