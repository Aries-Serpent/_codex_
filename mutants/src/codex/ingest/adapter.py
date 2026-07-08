"""
Ingest Adapter - Handles artifact ingestion from multiple sources.

Accepts file paths, ZIP archives, or Git URLs and creates immutable snapshots
in the artifacts directory with full provenance tracking.

Author: mbaetiong
Generated: 2025-12-17

Safeguards:
- Input validation on source paths
- Path traversal prevention
- Content hash verification
- Size bounds checking
- Deterministic operations
"""

from __future__ import annotations

import hashlib
import json
import logging
import shutil
import tarfile
import tempfile
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .manifest import IngestManifest, parse_manifest

logger = logging.getLogger(__name__)

# Safeguards: Configuration bounds
MAX_FILE_SIZE_MB = 100
MAX_TOTAL_SIZE_MB = 500
MAX_FILES_COUNT = 10000
ARTIFACTS_DIR = Path("artifacts")


@dataclass
class Snapshot:
    """Immutable snapshot of ingested code.

    Attributes:
        snapshot_id: Unique identifier (timestamp-hash format)
        source_path: Original source location
        snapshot_dir: Path to snapshot directory
        content_hash: SHA256 hash of source content
        created_at: Creation timestamp (UTC)
        manifest: Parsed ingestion manifest
        metadata: Additional metadata
    """

    snapshot_id: str
    source_path: str
    snapshot_dir: Path
    content_hash: str
    created_at: datetime
    manifest: Optional[IngestManifest] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_source_dir(self) -> Path:
        """Get path to source directory within snapshot."""
        return self.snapshot_dir / "source"

    def get_artifact_path(self, name: str) -> Path:
        """Get path to a named artifact within snapshot."""
        return self.snapshot_dir / name

    def to_dict(self) -> dict[str, Any]:
        """Convert snapshot to dictionary for serialization."""
        return {
            "snapshot_id": self.snapshot_id,
            "source_path": self.source_path,
            "snapshot_dir": str(self.snapshot_dir),
            "content_hash": self.content_hash,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


def _compute_content_hash(path: Path) -> str:
    """Compute SHA256 hash of file or directory content.

    Safeguard: Deterministic hashing with sorted file order.

    Args:
        path: File or directory to hash

    Returns:
        Hex-encoded SHA256 hash
    """
    hasher = hashlib.sha256()

    if path.is_file():
        # Hash single file
        content = path.read_bytes()
        hasher.update(content)
    elif path.is_dir():
        # Hash directory contents deterministically
        files = sorted(path.rglob("*"))
        for file_path in files:
            if file_path.is_file():
                # Include relative path in hash for structure
                rel_path = file_path.relative_to(path)
                hasher.update(str(rel_path).encode("utf-8"))
                hasher.update(file_path.read_bytes())

    return hasher.hexdigest()


def _validate_path(path: Path, base_dir: Optional[Path] = None) -> None:
    """Validate path for security issues.

    Safeguard: Path traversal prevention.

    Args:
        path: Path to validate
        base_dir: Optional base directory for containment check

    Raises:
        ValueError: If path is invalid or attempts traversal
    """
    # Check for path traversal attempts
    try:
        resolved = path.resolve()
        if base_dir:
            base_resolved = base_dir.resolve()
            if not str(resolved).startswith(str(base_resolved)):
                raise ValueError(f"Path traversal detected: {path}")
    except (IOError, OSError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        raise ValueError(f"Invalid path: {path} - {e}") from e


def _check_size_bounds(path: Path) -> None:
    """Check file/directory size against bounds.

    Safeguard: Size bounds checking.

    Args:
        path: Path to check

    Raises:
        ValueError: If size exceeds limits
    """
    if path.is_file():
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            raise ValueError(f"File size {size_mb:.2f}MB exceeds limit {MAX_FILE_SIZE_MB}MB")
    elif path.is_dir():
        total_size = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
        size_mb = total_size / (1024 * 1024)
        if size_mb > MAX_TOTAL_SIZE_MB:
            raise ValueError(f"Total size {size_mb:.2f}MB exceeds limit {MAX_TOTAL_SIZE_MB}MB")

        file_count = sum(1 for f in path.rglob("*") if f.is_file())
        if file_count > MAX_FILES_COUNT:
            raise ValueError(f"File count {file_count} exceeds limit {MAX_FILES_COUNT}")


def _extract_zip(zip_path: Path, dest_dir: Path) -> None:
    """Extract ZIP archive safely.

    Safeguard: Path traversal prevention in ZIP extraction.

    Args:
        zip_path: Path to ZIP file
        dest_dir: Destination directory
    """
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            member_path = dest_dir / member.filename
            _validate_path(member_path, dest_dir)

            if member.is_dir():
                member_path.mkdir(parents=True, exist_ok=True)
                continue

            member_path.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(member, "r") as src, open(member_path, "wb") as dst:
                shutil.copyfileobj(src, dst)


def _extract_tar(tar_path: Path, dest_dir: Path) -> None:
    """Extract TAR archive safely.

    Safeguard: Path traversal prevention in TAR extraction.

    Args:
        tar_path: Path to TAR file
        dest_dir: Destination directory
    """

    def is_safe_member(member_name: str) -> bool:
        member_path = Path(member_name)
        if member_path.is_absolute():
            return False
        return ".." not in member_path.parts

    with tarfile.open(tar_path, "r:*") as tf:
        for member in tf.getmembers():
            # Validate each member path
            if not is_safe_member(member.name):
                raise ValueError(f"Unsafe tar member path: {member.name}")
            member_path = dest_dir / member.name
            _validate_path(member_path, dest_dir)

            if member.isdir():
                member_path.mkdir(parents=True, exist_ok=True)
                continue

            if member.issym() or member.islnk():
                raise ValueError(f"Refusing to extract symlinked member: {member.name}")

            member_path.parent.mkdir(parents=True, exist_ok=True)
            extracted = tf.extractfile(member)
            if extracted is None:
                continue
            with extracted as src, open(member_path, "wb") as dst:
                shutil.copyfileobj(src, dst)


def _clone_git_repo(url: str, ref: Optional[str], dest_dir: Path) -> None:
    """Clone Git repository.

    Args:
        url: Git repository URL
        ref: Optional Git reference (branch, tag, commit)
        dest_dir: Destination directory
    """
    import subprocess  # nosec B404: subprocess is required for git invocation
    from urllib.parse import urlparse

    parsed_url = urlparse(url)
    if parsed_url.scheme not in {"", "http", "https", "ssh", "git"}:
        raise ValueError(f"Unsupported git URL scheme: {parsed_url.scheme}")
    if parsed_url.scheme and not parsed_url.netloc:
        raise ValueError(f"Invalid git URL: {url}")

    git_path = shutil.which("git")
    if not git_path:
        raise RuntimeError("git not found in PATH")
    git_path = str(Path(git_path).resolve())

    if ref and any(ch.isspace() for ch in ref):
        raise ValueError("Invalid git ref: whitespace is not allowed")

    # Clone repository
    cmd = [git_path, "clone", "--depth", "1"]
    if ref:
        cmd.extend(["--branch", ref])
    cmd.extend([url, str(dest_dir)])

    # Security: Using 'git' from PATH - assumes it's a trusted version control tool.
    # The url and ref parameters should be validated by the caller. Arguments are passed
    # as a list to prevent shell injection. The dest_dir is a controlled Path object.
    try:
        subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            check=True,
        )  # nosec B603: command arguments are controlled and validated above
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Git clone failed: {exc.stderr}") from exc


def ingest(
    source: str | Path,
    manifest_path: Optional[str | Path] = None,
    snapshot_id: Optional[str] = None,
    artifacts_dir: Optional[Path] = None,
) -> Snapshot:
    """Ingest source code and create immutable snapshot.

    Accepts file paths, ZIP archives, or Git URLs and creates an immutable
    snapshot in the artifacts directory with full provenance tracking.

    Args:
        source: File path, ZIP archive path, or Git URL
        manifest_path: Optional path to ingestion manifest
        snapshot_id: Optional custom snapshot ID
        artifacts_dir: Optional custom artifacts directory

    Returns:
        Snapshot object with metadata

    Raises:
        FileNotFoundError: If source file doesn't exist
        ValueError: If source is invalid or exceeds limits

    Example:
        >>> snapshot = ingest("./my_script.py", manifest_path="manifest.yaml")
        >>> logger.info(f"Created snapshot: {snapshot.snapshot_id}")
    """
    source_str = str(source)
    artifacts_base = artifacts_dir or ARTIFACTS_DIR

    # Parse manifest if provided
    manifest = None
    if manifest_path:
        manifest = parse_manifest(Path(manifest_path))

    # Create timestamp for snapshot
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y%m%d-%H%M%S")

    # Create temporary workspace
    with tempfile.TemporaryDirectory() as tmpdir:
        work_dir = Path(tmpdir) / "workspace"
        work_dir.mkdir()

        # Determine source type and process
        if source_str.startswith(("http://", "https://", "git@")):
            # Git URL
            logger.info("Cloning Git repository: %s", source_str)
            ref = manifest.source.ref if manifest and manifest.source else None
            _clone_git_repo(source_str, ref, work_dir)
        elif Path(source_str).exists():
            source_path = Path(source_str)
            _validate_path(source_path)

            if source_path.suffix.lower() == ".zip":
                # ZIP archive
                logger.info("Extracting ZIP archive: %s", source_str)
                _check_size_bounds(source_path)
                _extract_zip(source_path, work_dir)
            elif source_path.suffix.lower() in (".tar", ".tgz", ".tar.gz"):
                # TAR archive
                logger.info("Extracting TAR archive: %s", source_str)
                _check_size_bounds(source_path)
                _extract_tar(source_path, work_dir)
            elif source_path.is_file():
                # Single file
                logger.info("Copying file: %s", source_str)
                _check_size_bounds(source_path)
                shutil.copy2(source_path, work_dir / source_path.name)
            elif source_path.is_dir():
                # Directory
                logger.info("Copying directory: %s", source_str)
                _check_size_bounds(source_path)
                shutil.copytree(source_path, work_dir, dirs_exist_ok=True)
            else:
                raise ValueError(f"Unknown source type: {source_str}")
        else:
            raise FileNotFoundError(f"Source not found: {source_str}")

        # Compute content hash
        content_hash = _compute_content_hash(work_dir)
        short_hash = content_hash[:8]

        # Generate snapshot ID
        if not snapshot_id:
            snapshot_id = f"{timestamp}-{short_hash}"

        # Create snapshot directory
        snapshot_dir = artifacts_base / snapshot_id
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        # Copy source to snapshot
        source_dir = snapshot_dir / "source"
        shutil.copytree(work_dir, source_dir)

        # Copy manifest if provided
        if manifest_path:
            shutil.copy2(manifest_path, snapshot_dir / "manifest.yaml")

        # Create snapshot metadata
        snapshot_meta = {
            "snapshot_id": snapshot_id,
            "source": source_str,
            "content_hash": content_hash,
            "created_at": now.isoformat(),
            "file_count": sum(1 for _ in source_dir.rglob("*") if _.is_file()),
        }

        meta_path = snapshot_dir / "snapshot-meta.json"
        with meta_path.open("w", encoding="utf-8") as f:
            json.dump(snapshot_meta, f, indent=2)

        # Create empty artifact directories
        (snapshot_dir / "patches").mkdir(exist_ok=True)
        (snapshot_dir / "tests" / "codex_generated").mkdir(parents=True, exist_ok=True)
        (snapshot_dir / "llm_provenance").mkdir(exist_ok=True)

        logger.info("Created snapshot: %s at %s", snapshot_id, snapshot_dir)

        return Snapshot(
            snapshot_id=snapshot_id,
            source_path=source_str,
            snapshot_dir=snapshot_dir,
            content_hash=content_hash,
            created_at=now,
            manifest=manifest,
            metadata=snapshot_meta,
        )
