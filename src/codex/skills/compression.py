"""Compression utilities for Cognitive Brain Skill archives.

Packages a skill directory into a ``.7z`` archive (via the ``7z`` CLI if
available) and falls back to ``zipfile`` when ``7z`` is not installed.

Archive layout::

    <skill_id>-<version>/
    ├── manifest.yaml
    ├── handler.py
    ├── schema/
    │   ├── input.json
    │   └── output.json
    ├── docs/          (optional – source or chunk pointers)
    └── tests/         (optional)

The ``CompressionMeta`` fields ``size_before`` and ``size_after`` are updated
in-place and written back to the manifest file.

Usage::

    from codex.skills.compression import compress_skill, install_skill

    metrics = compress_skill("doc.retriever.core", out_dir=Path("dist"))
    install_skill(Path("dist/doc.retriever.core-1.0.0.7z"))
"""

from __future__ import annotations

import logging
import shutil
import subprocess  # nosec B404 - 7z is only called with a validated, controlled arg list
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

yaml: ModuleType | None
try:
    import yaml as _yaml_module

    yaml = _yaml_module
except (IOError, OSError):  # pragma: no cover
    yaml = None

logger = logging.getLogger(__name__)

_7Z_BIN = shutil.which("7z") or shutil.which("7za") or shutil.which("7zz")


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class CompressionResult:
    """Metrics captured after compressing a skill directory."""

    skill_id: str
    version: str
    archive_path: str
    size_before: int
    size_after: int
    compression_ratio: float
    method: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _dir_size(path: Path) -> int:
    """Return total byte count of all files under *path*."""
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def _find_skill_dir(skill_id: str) -> Path | None:
    """Locate the skill directory for *skill_id* under src/codex/skills/."""
    base = Path(__file__).parent
    # Convert dotted id to path fragment: "doc.retriever.core" → check subdirs
    # Registry-based lookup if available
    slug = skill_id.replace(".", "_").lower()
    for candidate in base.iterdir():
        if not candidate.is_dir():
            continue
        manifest = candidate / "manifest.yaml"
        if not manifest.exists():
            continue
        if yaml is None:  # pragma: no cover
            continue
        try:
            data = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
            if data.get("id") == skill_id:
                return candidate
        except (IOError, OSError):  # nosec B112 — intentional: skip unreadable manifest candidates
            continue
    candidates = [d for d in base.iterdir() if d.is_dir() and d.name == slug]
    return candidates[0] if candidates else None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def compress_skill(
    skill_id: str,
    *,
    out_dir: Path | str = Path("dist"),
    format: str = "7z",
    level: str = "max",
    record_metrics: bool = True,
) -> CompressionResult:
    """Compress a skill directory into a distributable archive.

    Parameters
    ----------
    skill_id:
        Dotted skill identifier (must match ``id`` in its ``manifest.yaml``).
    out_dir:
        Output directory for the archive.
    format:
        Archive format: ``"7z"`` or ``"zip"``.
    level:
        Compression level: ``"max"`` or ``"fast"``.
    record_metrics:
        If True, update ``size_before``/``size_after`` in the manifest file.

    Returns
    -------
    CompressionResult
    """
    skill_dir = _find_skill_dir(skill_id)
    if skill_dir is None:
        raise FileNotFoundError(f"Skill directory not found for skill id '{skill_id}'")

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # Read manifest for version
    version = "1.0.0"
    manifest_file = skill_dir / "manifest.yaml"
    if manifest_file.exists() and yaml is not None:
        try:
            data = yaml.safe_load(manifest_file.read_text(encoding="utf-8")) or {}
            version = data.get("version", "1.0.0")
        except (IOError, OSError):
            logger.debug("Suppressed exception in handler", exc_info=True)
    size_before = _dir_size(skill_dir)
    archive_name = f"{skill_id.replace('.', '-')}-{version}"

    if format == "7z" and _7Z_BIN:
        archive_path = out_path / f"{archive_name}.7z"
        level_flag = "-mx=9" if level == "max" else "-mx=5"
        cmd = [_7Z_BIN, "a", level_flag, str(archive_path), str(skill_dir)]
        result = subprocess.run(  # nosec B603 - controlled path list, shell disabled
            cmd, capture_output=True, text=True
        )
        if result.returncode != 0:
            logger.warning("7z compression failed: %s — falling back to zip", result.stderr)
            archive_path = _compress_zip(skill_dir, out_path / f"{archive_name}.zip")
    else:
        archive_path = _compress_zip(skill_dir, out_path / f"{archive_name}.zip")

    size_after = archive_path.stat().st_size if archive_path.exists() else 0
    ratio = size_after / size_before if size_before > 0 else 0.0

    if record_metrics and manifest_file.exists() and yaml is not None:
        _update_manifest_compression(manifest_file, size_before, size_after)

    logger.info(
        "Compressed '%s' → %s (%.1f%% of original)",
        skill_id,
        archive_path,
        ratio * 100,
    )

    return CompressionResult(
        skill_id=skill_id,
        version=version,
        archive_path=str(archive_path),
        size_before=size_before,
        size_after=size_after,
        compression_ratio=ratio,
        method="7z" if str(archive_path).endswith(".7z") else "zip",
    )


def install_skill(
    archive_path: Path | str,
    *,
    install_root: Path | None = None,
) -> Path:
    """Extract and install a skill archive into the skills directory.

    Parameters
    ----------
    archive_path:
        Path to a ``.7z`` or ``.zip`` archive produced by :func:`compress_skill`.
    install_root:
        Target directory (defaults to ``src/codex/skills/``).

    Returns
    -------
    Path
        The directory the skill was extracted into.
    """
    archive_path = Path(archive_path)
    if not archive_path.exists():
        raise FileNotFoundError(f"Archive not found: {archive_path}")

    target_root = install_root or Path(__file__).parent

    suffix = archive_path.suffix.lower()
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        if suffix == ".7z":
            if _7Z_BIN is None:
                raise RuntimeError("7z binary not found; cannot extract .7z archive")
            subprocess.run(  # nosec B603
                [_7Z_BIN, "x", str(archive_path), f"-o{tmp}", "-y"],
                check=True,
                capture_output=True,
            )
        elif suffix == ".zip":
            with zipfile.ZipFile(archive_path) as zf:
                # Guard against Zip Slip: verify every member resolves inside tmp
                for member in zf.infolist():
                    member_path = (tmp / member.filename).resolve()
                    if not str(member_path).startswith(str(tmp.resolve())):
                        raise ValueError(
                            f"Zip Slip detected: '{member.filename}' "
                            "would extract outside target dir"
                        )
                zf.extractall(tmp)
        else:
            raise ValueError(f"Unsupported archive format: {suffix}")

        # Find extracted skill directory (first top-level directory)
        extracted_dirs = [d for d in tmp.iterdir() if d.is_dir()]
        if not extracted_dirs:
            raise RuntimeError("Archive contains no directories")
        extracted = extracted_dirs[0]

        dest = target_root / extracted.name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(extracted, dest)

    logger.info("Installed skill archive '%s' to '%s'", archive_path, dest)
    return dest


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _compress_zip(skill_dir: Path, out_path: Path) -> Path:
    """Create a zip archive of *skill_dir* at *out_path*."""
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for file in skill_dir.rglob("*"):
            if file.is_file():
                zf.write(file, file.relative_to(skill_dir.parent))
    return out_path


def _update_manifest_compression(manifest_file: Path, size_before: int, size_after: int) -> None:
    """Update compression size fields in an existing manifest.yaml in-place."""
    if yaml is None:  # pragma: no cover
        return
    try:
        data = yaml.safe_load(manifest_file.read_text(encoding="utf-8")) or {}
        compression = data.setdefault("compression", {})
        compression["size_before"] = size_before
        compression["size_after"] = size_after
        manifest_file.write_text(yaml.safe_dump(data, default_flow_style=False), encoding="utf-8")
    except (IOError, OSError) as exc:
        logger.warning("Could not update manifest compression fields: %s", exc)


__all__ = ["CompressionResult", "compress_skill", "install_skill"]
