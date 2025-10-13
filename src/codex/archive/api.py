from __future__ import annotations

import os
import uuid
from pathlib import Path

from .dal import ArchiveDAL
from .util import json_dumps, sha256_hex, utcnow_iso, zlib_compress

EVIDENCE_DIR = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence")).resolve()
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
EVIDENCE_FILE = EVIDENCE_DIR / "archive_ops.jsonl"


def _evidence_append(rec: dict[str, object]) -> None:
    EVIDENCE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with EVIDENCE_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json_dumps(rec) + "\n")


def store(
    *,
    repo: str,
    path: str,
    by: str,
    reason: str,
    commit_sha: str,
    bytes_in: bytes,
    mime: str,
    lang: str | None = None,
) -> dict[str, str]:
    tomb = str(uuid.uuid4())
    sha = sha256_hex(bytes_in)
    blob = zlib_compress(bytes_in, level=9)
    dal = ArchiveDAL.from_env()
    art = dal.ensure_artifact(
        sha=sha,
        size=len(bytes_in),
        mime=mime,
        blob=blob,
        compression="zlib",
    )
    item = dal.insert_item(
        repo=repo,
        path=path,
        commit_sha=commit_sha,
        language=lang or "",
        reason=reason,
        artifact_id=art["id"],
        tombstone_id=tomb,
        kind="code",
        metadata={"mime": mime},
        archived_by=by,
    )
    dal.insert_event(
        item_id=item["id"],
        action="ARCHIVE",
        actor=by,
        context={"commit": commit_sha},
    )
    _evidence_append(
        {
            "ts": utcnow_iso(),
            "action": "ARCHIVE",
            "actor": by,
            "repo": repo,
            "path": path,
            "tombstone": tomb,
            "sha256": sha,
            "size": len(bytes_in),
            "commit": commit_sha,
        }
    )
    return {"tombstone": tomb, "sha256": sha}


def restore(tombstone: str) -> dict[str, object]:
    dal = ArchiveDAL.from_env()
    item, artifact = dal.fetch_by_tombstone(tombstone)
    actor = os.getenv("CODEX_ACTOR", os.getenv("USER", "codex"))
    dal.insert_event(item_id=item.id, action="RESTORE", actor=actor, context={})
    _evidence_append(
        {
            "ts": utcnow_iso(),
            "action": "RESTORE",
            "actor": actor,
            "repo": item.repo,
            "path": item.path,
            "tombstone": item.tombstone_id,
            "sha256": artifact.content_sha256,
            "size": artifact.size_bytes,
        }
    )
    if artifact.storage_driver == "db" and artifact.blob_bytes is not None:
        import zlib

        data = zlib.decompress(artifact.blob_bytes)
        return {"path": item.path, "bytes": data}
    raise RuntimeError("Non-db storage_driver restore not implemented in this scaffold.")
