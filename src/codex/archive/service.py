"""High level archive orchestration utilities."""

# ruff: noqa: I001  # import-order handled by isort configuration

from __future__ import annotations

import logging
import mimetypes
import os
import subprocess
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import backend as backend_module, config as config_module, retry as retry_module
from .logging_config import log_restore, setup_logging
from .perf import timer
from .util import (
    append_evidence,
    compression_codec,
    decompress_payload,
    redact_text_credentials,
    redact_url_credentials,
    sha256_hex,
    zstd_compress,
)

BackendArchiveConfig = backend_module.ArchiveConfig
ArchiveDAL = backend_module.ArchiveDAL
SettingsArchiveConfig = config_module.ArchiveAppConfig
SettingsBackendConfig = config_module.BackendConfig
RetryPolicyConfig = retry_module.RetryConfig
retry_with_backoff = retry_module.retry_with_backoff


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
        config: SettingsArchiveConfig | BackendArchiveConfig | None = None,
        *,
        apply_schema: bool = True,
        logger: logging.Logger | None = None,
    ) -> None:
        settings = self._coerce_settings(config)
        self.config = settings
        backend_config = BackendArchiveConfig.from_settings(settings)
        self.dal = ArchiveDAL(backend_config, apply_schema=apply_schema)
        self.logger = logger or setup_logging(settings.logging)
        self._retry_policy: RetryPolicyConfig | None = None
        retry_config = settings.retry.to_retry_config()
        if retry_config.enabled:
            self._retry_policy = retry_config
        self._get_restore_payload: Callable[[str], dict[str, Any]] = (
            retry_with_backoff(self._retry_policy)(self.dal.get_restore_payload)
            if self._retry_policy
            else self.dal.get_restore_payload
        )

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

        backend = getattr(self.dal, "backend", None)
        raw_url = getattr(self.dal, "url", None)
        metrics: dict[str, float] = {}
        decompress_duration: float | None = None
        write_duration: float | None = None

        with timer("restore") as restore_timer:
            try:
                payload = self._get_restore_payload(tombstone_id)
            except LookupError as exc:
                self._record_restore_failure(
                    tombstone_id=tombstone_id,
                    actor=actor,
                    backend=backend,
                    url=raw_url,
                    reason=f"Tombstone not found: {exc}",
                )
                raise
            except Exception as exc:  # pragma: no cover - defensive guard
                sanitized = redact_text_credentials(str(exc)).strip()
                detail = f"{type(exc).__name__}" + (f": {sanitized}" if sanitized else "")
                self._record_restore_failure(
                    tombstone_id=tombstone_id,
                    actor=actor,
                    backend=backend,
                    url=raw_url,
                    reason=f"Backend access error: {detail}",
                    error=exc,
                )
                raise RuntimeError(
                    f"Failed to retrieve restore payload for tombstone {tombstone_id}: {detail}"
                ) from exc

            artifact = payload["artifact"]
            blob = artifact.get("blob_bytes")
            if blob is None:
                self._record_restore_failure(
                    tombstone_id=tombstone_id,
                    actor=actor,
                    backend=backend,
                    url=raw_url,
                    reason="Artifact payload has been purged; bytes unavailable",
                )
                raise RuntimeError("Artifact payload has been purged; bytes unavailable")

            codec = artifact.get("compression") or compression_codec()
            try:
                with timer("decompress") as decompress_timer:
                    restored = decompress_payload(blob, codec)
            except (RuntimeError, ValueError) as exc:
                self._record_restore_failure(
                    tombstone_id=tombstone_id,
                    actor=actor,
                    backend=backend,
                    url=raw_url,
                    reason=f"Decompression failed with codec '{codec}'",
                    error=exc,
                )
                raise RuntimeError(f"Unable to decompress artifact using codec '{codec}'") from exc
            else:
                decompress_duration = decompress_timer.duration_ms

            with timer("write") as write_timer:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(restored)
            write_duration = write_timer.duration_ms

            self.dal.record_restore(tombstone_id, actor=actor)

        if self.config.performance.enabled:
            if restore_timer.duration_ms is not None:
                metrics["duration_ms"] = restore_timer.duration_ms
            if decompress_duration is not None:
                metrics["decompression_ms"] = decompress_duration
            if write_duration is not None:
                metrics["write_ms"] = write_duration

        evidence_payload: dict[str, Any] = {
            "action": "RESTORE",
            "actor": actor,
            "tombstone": tombstone_id,
            "path": output_path.as_posix(),
            "repo": payload["item"].get("repo"),
        }
        evidence_payload.update(metrics)
        append_evidence(evidence_payload)

        log_restore(
            self.logger,
            actor=actor,
            tombstone=tombstone_id,
            status="SUCCESS",
            metrics=metrics or None,
            logging_config=self.config.logging,
            performance_config=self.config.performance,
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
    ) -> bool:
        scrubbed = self.dal.record_delete_approval(
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
                "blob_scrubbed": scrubbed,
            }
        )
        return scrubbed

    def ensure_schema(self) -> None:
        self.dal.ensure_schema()

    @staticmethod
    def _coerce_settings(
        config: SettingsArchiveConfig | BackendArchiveConfig | None,
    ) -> SettingsArchiveConfig:
        if config is None:
            return SettingsArchiveConfig.load()
        if isinstance(config, SettingsArchiveConfig):
            return config
        return SettingsArchiveConfig(
            backend=SettingsBackendConfig(backend=config.backend, url=config.url)
        )

    def _record_restore_failure(
        self,
        *,
        tombstone_id: str,
        actor: str,
        backend: str | None,
        url: str | None,
        reason: str,
        error: Exception | None = None,
    ) -> None:
        sanitized_reason = redact_text_credentials(reason).strip() or reason
        append_evidence(
            {
                "action": "RESTORE_FAIL",
                "actor": actor,
                "tombstone": tombstone_id,
                "reason": sanitized_reason,
                "backend": backend,
                "url": redact_url_credentials(url) or None,
            }
        )
        sanitized_error: str | None = None
        if error is not None:
            redacted_error = redact_text_credentials(str(error)).strip()
            sanitized_error = redacted_error or error.__class__.__name__

        detail = sanitized_reason
        if sanitized_error:
            detail = f"{sanitized_reason}: {sanitized_error}"

        log_restore(
            self.logger,
            actor=actor,
            tombstone=tombstone_id,
            status="FAILED",
            detail=detail,
            logging_config=self.config.logging,
            performance_config=self.config.performance,
        )


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
