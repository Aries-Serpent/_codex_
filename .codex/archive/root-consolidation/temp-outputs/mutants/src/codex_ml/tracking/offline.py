"""
Offline Module

This module provides functionality for offline.

Usage:
    from tracking.offline import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import json  # noqa: E402
import os  # noqa: E402
import shutil  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Optional  # noqa: E402
from urllib.parse import urlparse  # noqa: E402


def _file_uri(p: Path) -> str:
    """Convert path to a RFC 8089-compliant file URI."""
    p = p.resolve()
    return p.as_uri()


@dataclass
class OfflineDecision:
    offline: bool
    reason: str
    mlflow_tracking_uri: str
    wandb_env: dict[str, str]


def decide_offline(
    *,
    prefer_offline: bool = True,
    allow_remote: bool = False,
    mlruns_dir: Optional[str | Path] = None,
) -> OfflineDecision:
    """
    Decide on offline posture for MLflow and W&B.

    If ``prefer_offline`` and remote URIs are not allowed, enforce a local ``file://``
    MLflow tracking URI and configure W&B to operate in offline mode.
    """

    env = os.environ
    default_store = Path(mlruns_dir) if mlruns_dir else (Path.cwd() / "mlruns")

    current_uri = env.get("MLFLOW_TRACKING_URI") or ""
    canonical_current = current_uri
    if current_uri.startswith("file:"):
        remainder = current_uri[len("file:") :]
        if remainder.startswith("///"):
            canonical_current = current_uri
        elif remainder.startswith("//"):
            # file://relative/path -- treat the remainder as a path.
            canonical_current = _file_uri(Path(remainder.lstrip("/")))
        else:
            canonical_current = _file_uri(Path(remainder))

    current_uri = canonical_current

    def _is_remote_mlflow_uri(uri: str) -> bool:
        if not uri:
            return False

        lowered = uri.lower()
        if lowered.startswith("databricks"):
            return True

        parsed = urlparse(uri)
        scheme = parsed.scheme.lower()

        if scheme in {"", "file", "sqlite"}:
            return False

        remote_schemes = {"http", "https", "postgresql", "mysql"}
        if scheme in remote_schemes:
            return True

        return bool(parsed.netloc)

    is_remote = _is_remote_mlflow_uri(current_uri)

    if prefer_offline and not allow_remote and (is_remote or not current_uri):
        mlflow_tracking_uri = _file_uri(default_store)
        offline = True
        reason = "prefer_offline=True and remote URIs are disallowed; forcing file:// store"
    else:
        mlflow_tracking_uri = current_uri or _file_uri(default_store)
        offline = prefer_offline
        reason = "respecting existing MLFLOW_TRACKING_URI"

    wandb_env: dict[str, str] = {}
    if prefer_offline and not allow_remote:
        wandb_mode = env.get("WANDB_MODE", "").lower()
        wandb_disabled = env.get("WANDB_DISABLED", "").lower()
        if wandb_mode != "offline" and wandb_disabled not in {"true", "1"}:
            wandb_env["WANDB_MODE"] = "offline"

    return OfflineDecision(
        offline=offline,
        reason=reason,
        mlflow_tracking_uri=mlflow_tracking_uri,
        wandb_env=wandb_env,
    )


def export_env_lines(decision: OfflineDecision) -> str:
    """Return shell ``export`` lines for the offline decision."""

    lines = [f'export MLFLOW_TRACKING_URI="{decision.mlflow_tracking_uri}"']
    for key, value in decision.wandb_env.items():
        lines.append(f'export {key}="{value}"')
    return "\n".join(lines) + "\n"


class NDJSONLogger:
    """Append JSON records to disk with optional size-based rotation."""

    def __init__(
        self,
        path: str | Path,
        *,
        max_bytes: int = 50_000_000,
        backup_count: int = 3,
        enable_rotation: bool = True,
    ) -> None:
        self.path = Path(path)
        self.max_bytes = int(max_bytes)
        self.backup_count = int(backup_count)
        self.enable_rotation = bool(enable_rotation)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _backup_path(self, index: int) -> Path:
        """Return the backup path for ``index`` where ``0`` is the active file."""

        if index <= 0:
            return self.path

        return self.path.with_name(f"{self.path.name}.{index}")

    def _rotate(self) -> None:
        if not self.path.exists() or self.backup_count <= 0:
            return

        for index in range(self.backup_count, 0, -1):
            src = self._backup_path(index - 1)
            dst = self._backup_path(index)
            if src.exists():
                try:
                    shutil.move(str(src), str(dst))
                except (IOError, OSError) as e:
                    type(e).__name__
                    logger.debug("Exception: <ERROR_TYPE>")
                    logger.warning("Exception: <ERROR_TYPE>", exc_info=True)

    def write(self, record: dict[str, object]) -> None:
        line = json.dumps(record, ensure_ascii=False)
        try:
            if (
                self.enable_rotation
                and self.max_bytes > 0
                and self.path.exists()
                and self.path.stat().st_size + len(line) + 1 > self.max_bytes
            ):
                self._rotate()
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning("Exception: <ERROR_TYPE>", exc_info=True)
