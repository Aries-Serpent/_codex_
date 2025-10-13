"""High level archive orchestration utilities."""

from __future__ import annotations

import mimetypes
import os
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from .backend import ArchiveConfig, ArchiveDAL
from .util import append_evidence, compression_codec, sha256_hex, zstd_compress, zstd_decompress


@dataclass(frozen=True)
class ArchiveResult:
    """Metadata returned after storing an item."""

    tombstone_id: str
    sha256: str
    size_bytes: int
    compressed_size: int
    repo: str
    path: str


class ArchiveService:
    """Service façade encapsulating archival workflows."""

    def __init__(
        self,
        config: ArchiveConfig | None = None,
        *,
        apply_schema: bool = True,
    ) -> None:
        self.config = config or ArchiveConfig.from_env()
        self.dal = ArchiveDAL(self.config, apply_schema=apply_schema)

    # ------------------------------------------------------------------
    # entry points
    # ------------------------------------------------------------------
    def archive_path(
        self,
        *,
        repo: str,
        path: Path,
        reason: str,
        archived_by: str,
        commit_sha: str,
        kind: str = "code",
        language: str | None = None,
        mime_type: str | None = None,
        tags: Sequence[str] | None = None,
        extra_metadata: dict[str, object] | None = None,
    ) -> ArchiveResult:
        """Archive *path* and return archival metadata."""

        bytes_in = path.read_bytes()
        sha = sha256_hex(bytes_in)
        compressed = zstd_compress(bytes_in)
        codec = compression_codec()
        mime = mime_type or (mimetypes.guess_type(path.as_posix())[0] or "application/octet-stream")
        metadata = {
            "sha256": sha,
            "size_bytes": len(bytes_in),
            "compressed_size": len(compressed),
            "compression": codec,
            "mime_type": mime,
            "language": language,
        }
        if extra_metadata:
            metadata.update(extra_metadata)
        context = {
            "commit": commit_sha,
            "repo": repo,
            "path": path.as_posix(),
            "python": os.getenv("PYTHON_VERSION") or _python_version(),
        }
        artifact_payload = {
            "content_sha256": sha,
            "size_bytes": len(bytes_in),
            "compression": codec,
            "mime_type": mime,
            "storage_driver": "db",
            "blob_bytes": compressed,
            "object_url": None,
        }
        result = self.dal.record_archive(
            repo=repo,
            path=path.as_posix(),
            commit_sha=commit_sha,
            language=language,
            reason=reason,
            kind=kind,
            artifact_payload=artifact_payload,
            archived_by=archived_by,
            metadata=metadata,
            context=context,
            tags=list(tags or ()),
        )
        append_evidence(
            {
                "action": "ARCHIVE",
                "actor": archived_by,
                "repo": repo,
                "path": path.as_posix(),
                "tombstone": result["tombstone_id"],
                "sha256": sha,
                "size": len(bytes_in),
                "compressed_size": len(compressed),
                "reason": reason,
            }
        )
        return ArchiveResult(
            tombstone_id=result["tombstone_id"],
            sha256=sha,
            size_bytes=len(bytes_in),
            compressed_size=len(compressed),
            repo=repo,
            path=path.as_posix(),
        )

    def restore_to_path(
        self,
        tombstone_id: str,
        *,
        output_path: Path,
        actor: str,
    ) -> Path:
        """Restore an archived item to *output_path*."""

        payload = self.dal.record_restore(tombstone_id, actor=actor)
        artifact = payload["artifact"]
        blob = artifact.get("blob_bytes")
        if blob is None:
            raise RuntimeError("Artifact payload has been purged; bytes unavailable")
        restored = zstd_decompress(blob)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(restored)
        append_evidence(
            {
                "action": "RESTORE",
                "actor": actor,
                "tombstone": tombstone_id,
                "path": output_path.as_posix(),
                "repo": payload["item"].get("repo"),
            }
        )
        return output_path

    def list_items(
        self, *, repo: str | None = None, since: str | None = None, limit: int = 100
    ) -> list[dict[str, object]]:
        return self.dal.list_items(repo=repo, since=since, limit=limit)

    def show_item(self, tombstone_id: str) -> dict[str, object]:
        return self.dal.show_item(tombstone_id)

    def request_prune(self, tombstone_id: str, *, actor: str, reason: str) -> None:
        self.dal.record_prune_request(tombstone_id, actor=actor, reason=reason)
        append_evidence(
            {
                "action": "PRUNE_REQUEST",
                "actor": actor,
                "tombstone": tombstone_id,
                "reason": reason,
            }
        )

    def approve_delete(
        self,
        tombstone_id: str,
        *,
        primary_actor: str,
        secondary_actor: str,
        reason: str,
        apply: bool = False,
    ) -> None:
        self.dal.record_delete_approval(
            tombstone_id,
            primary_actor=primary_actor,
            secondary_actor=secondary_actor,
            reason=reason,
            apply=apply,
        )
        append_evidence(
            {
                "action": "DELETE_APPROVED",
                "tombstone": tombstone_id,
                "primary": primary_actor,
                "secondary": secondary_actor,
                "reason": reason,
                "apply": apply,
            }
        )

    def ensure_schema(self) -> None:
        self.dal.ensure_schema()


# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------


def _python_version() -> str:
    try:
        result = subprocess.run(
            ["python", "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip() or result.stderr.strip()
    except Exception:  # pragma: no cover - best effort fallback
        return os.getenv("PYTHON_VERSION", "unknown")
