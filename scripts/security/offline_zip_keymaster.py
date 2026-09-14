#!/usr/bin/env python3
"""Offline ZIP key generation, encryption, and safe unpacking.

This module provides a self-contained, air-gapped workflow for:
- generating local symmetric keys and manifest files,
- packaging a directory into a zip archive,
- encrypting the zip payload with a local key,
- decrypting/extracting contents into a self-titled folder,
- validating archive members to prevent ZIP path traversal attacks.
"""

from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import hmac
import itertools
import json
import math
import os
import posixpath
import re
import shutil
import stat
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from aries_serpent_core.security import mask_token, sanitize_log
    from aries_serpent_core.security.storage import (
        SecureStorage,
    )
    from aries_serpent_core.security.storage import (
        generate_key as storage_generate_key,
    )
except ImportError:  # pragma: no cover - fallback for lightweight runtime
    from utils.log_sanitizer import sanitize_log_input as sanitize_log
    from utils.sensitive_data import mask_token

    SecureStorage = None  # type: ignore[assignment]

    def storage_generate_key() -> str:  # type: ignore[no-redef]
        raise ImportError("aries_serpent_core.security.storage is unavailable")

try:
    import serpent  # type: ignore
except ImportError:  # pragma: no cover - optional structured serialization
    serpent = None

try:
    from security.encryption import (
        EncryptionError,
    )
    from security.encryption import (
        decrypt as crypto_decrypt,
    )
    from security.encryption import (
        encrypt as crypto_encrypt,
    )
    from security.encryption import (
        generate_key as crypto_generate_key,
    )
except ImportError:  # pragma: no cover - optional crypto fallback
    crypto_generate_key = None  # type: ignore[assignment]
    crypto_encrypt = None  # type: ignore[assignment]
    crypto_decrypt = None  # type: ignore[assignment]
    EncryptionError = ValueError  # type: ignore[misc, assignment]

DEFAULT_MANIFEST_NAME = "manifest.json"
DEFAULT_PAYLOAD_NAME = "encrypted_payload.bin"
DEFAULT_MASTER_SEED_NAME = "master_seed.json"
MAX_ARCHIVE_BYTES = 512 * 1024 * 1024
MAX_EXTRACTION_BYTES = 512 * 1024 * 1024
MAX_EXTRACTION_FILES = 2048
MAX_RECURSION_DEPTH = 8
MAX_MEMBER_BYTES = 128 * 1024 * 1024
MAX_NESTED_ARCHIVES = 32
MAX_KEY_CANDIDATES = 64


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _safe_log(message: str) -> str:
    return sanitize_log(message, max_length=500)


def _mask_secret(value: str | None, *, keep: int = 2) -> str:
    if value is None:
        return "***"
    text = str(value).strip()
    if not text:
        return "***"
    # Passwords and candidate values must never be emitted in recover logs or
    # report artifacts. Keep a stable digest for correlation without exposing the
    # original secret material.
    return f"sha256:{_sha256_hex(text)[:max(8, min(16, max(keep, 1) * 4))]}"


def _sha256_hex(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def _literal_safe(value: Any) -> None:
    try:
        if serpent is not None:
            serpent.dumps(value)
        ast.literal_eval(repr(value))
    except Exception as exc:  # pragma: no cover - defensive guard
        raise ValueError(f"Archive metadata failed literal validation: {exc}") from exc


def _load_key_material(path: str | Path) -> str:
    key_path = Path(path)
    if not key_path.exists():
        raise FileNotFoundError(f"Key file not found: {key_path}")

    raw = key_path.read_bytes()
    try:
        manifest = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError:
        text = raw.decode("utf-8").strip()
        if not text:
            raise ValueError("Key file is empty")
        return text

    if not isinstance(manifest, dict):
        raise ValueError("Key manifest must contain an object")
    if "key" not in manifest:
        raise ValueError("Key manifest is missing a valid key value")
    key_value = manifest["key"]
    if not isinstance(key_value, str) or not key_value:
        raise ValueError("Key manifest is missing a valid key value")
    return key_value


def _write_key_file(path: str | Path, key: str, *, algorithm: str = "aes-gcm") -> Path:
    key_path = Path(path)
    key_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "version": 1,
        "algorithm": algorithm,
        "key": key,
        "fingerprint": _sha256_hex(key),
        "created_at": _utc_now(),
    }
    key_path.write_text(_canonical_json(manifest) + "\n", encoding="utf-8")
    os.chmod(key_path, stat.S_IRUSR | stat.S_IWUSR)
    return key_path


def _master_seed_locations(base_dir: str | Path | None = None) -> list[Path]:
    ordered: list[Path] = []
    roots: list[Path] = [Path.cwd(), ROOT_DIR, Path.home()]
    if base_dir is not None:
        roots.insert(0, Path(base_dir))
    for root in roots:
        ordered.extend(
            [
                root / "keys" / DEFAULT_MASTER_SEED_NAME,
                root / ".codex" / "keys" / DEFAULT_MASTER_SEED_NAME,
                root / DEFAULT_MASTER_SEED_NAME,
            ]
        )
    seen: set[str] = set()
    unique: list[Path] = []
    for path in ordered:
        candidate = str(path)
        if candidate in seen:
            continue
        seen.add(candidate)
        unique.append(path)
    return unique


def _load_master_seed(base_dir: str | Path | None = None) -> str | None:
    for seed_path in _master_seed_locations(base_dir):
        if not seed_path.exists():
            continue
        try:
            payload = json.loads(seed_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError, ValueError):
            try:
                text = seed_path.read_text(encoding="utf-8").strip()
            except (OSError, ValueError):
                continue
            if text:
                return text
            continue
        if isinstance(payload, dict):
            seed_value = payload.get("seed") or payload.get("master_seed")
            if isinstance(seed_value, str) and seed_value:
                return seed_value
        if isinstance(payload, str) and payload:
            return payload
    return None


def _write_master_seed(base_dir: str | Path, seed: str) -> Path:
    base_path = Path(base_dir)
    seed_path = base_path / DEFAULT_MASTER_SEED_NAME
    seed_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "version": 1,
        "seed": seed,
        "master_seed": seed,
        "derivation_version": 1,
        "created_at": _utc_now(),
    }
    seed_path.write_text(_canonical_json(manifest) + "\n", encoding="utf-8")
    os.chmod(seed_path, stat.S_IRUSR | stat.S_IWUSR)
    return seed_path


@dataclass(frozen=True)
class KeyState:
    """Local key material with validation metadata for secure archive operations."""

    key: str
    algorithm: str = "aes-gcm"
    fingerprint: str = ""
    manifest_path: str | None = None

    @classmethod
    def from_material(cls, key: str, *, algorithm: str = "aes-gcm", manifest_path: str | Path | None = None) -> "KeyState":
        normalized = key.strip()
        if not normalized:
            raise ValueError("Key material is empty")
        fingerprint = _sha256_hex(normalized)
        return cls(
            key=normalized,
            algorithm=algorithm,
            fingerprint=fingerprint,
            manifest_path=str(manifest_path) if manifest_path is not None else None,
        )

    @classmethod
    def from_file(cls, path: str | Path) -> "KeyState":
        key_path = Path(path)
        key_value = _load_key_material(key_path)
        manifest_data: dict[str, Any] = {}
        if key_path.exists():
            try:
                manifest_data = json.loads(key_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                manifest_data = {}
        algorithm = str(manifest_data.get("algorithm", "aes-gcm")) if isinstance(manifest_data, dict) else "aes-gcm"
        return cls.from_material(key_value, algorithm=algorithm, manifest_path=key_path)


@dataclass(frozen=True)
class RecoveryPlan:
    """Structured information required to drive a local ZIP recovery campaign."""

    archive_path: str | Path | None = None
    archive_name: str | None = None
    archive_stem: str = ""
    seed: str | None = None
    wordlist: str | None = None
    wordlist_paths: tuple[Path, ...] = ()
    candidate_file: str | None = None
    mask: str | None = None
    charset: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    min_length: int = 1
    max_length: int = 4
    brute_force: bool = False
    rules: tuple[str, ...] = ()
    hints: tuple[str, ...] = ()
    max_candidates: int = 20000
    max_attempts: int = 20000
    report_path: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "archive_path": str(self.archive_path) if self.archive_path is not None else None,
            "archive_name": self.archive_name,
            "archive_stem": self.archive_stem,
            "seed": self.seed,
            "wordlist": self.wordlist,
            "wordlist_paths": [str(path) for path in self.wordlist_paths],
            "candidate_file": self.candidate_file,
            "mask": self.mask,
            "charset": self.charset,
            "min_length": self.min_length,
            "max_length": self.max_length,
            "brute_force": self.brute_force,
            "rules": list(self.rules),
            "hints": list(self.hints),
            "max_candidates": self.max_candidates,
            "max_attempts": self.max_attempts,
            "report_path": self.report_path,
        }


@dataclass(frozen=True)
class CandidateRecord:
    """A single candidate password in the source-ranked queue used for local recovery."""

    value: str
    source: str
    score: float
    stage: str
    tried: bool = False
    success: bool = False
    reason: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", str(self.value).strip())
        object.__setattr__(self, "source", str(self.source).strip())
        object.__setattr__(self, "stage", str(self.stage).strip())
        if self.reason is not None:
            object.__setattr__(self, "reason", str(self.reason).strip() or None)

    def as_dict(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "source": self.source,
            "score": self.score,
            "stage": self.stage,
            "tried": self.tried,
            "success": self.success,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ArchiveProbe:
    """Summary of a ZIP archive used to determine the likely recovery strategy."""

    path: str | Path
    is_valid_zip: bool
    member_count: int
    encrypted_member_count: int
    names: tuple[str, ...] = ()
    archive_stem: str = ""
    detected_hints: tuple[str, ...] = ()
    error: str | None = None

    @classmethod
    def from_path(cls, zip_path: str | Path, *, hints: Iterable[str] | None = None) -> "ArchiveProbe":
        archive = Path(zip_path)
        names: tuple[str, ...] = ()
        error: str | None = None
        is_valid_zip = False
        member_count = 0
        encrypted_count = 0
        try:
            with zipfile.ZipFile(archive, "r") as zf:
                infos = zf.infolist()
                member_count = len(infos)
                names = tuple(info.filename for info in infos)
                is_valid_zip = True
                encrypted_count = sum(1 for info in infos if info.filename in {"manifest.json", "encrypted_payload.bin"})
        except Exception as exc:  # pragma: no cover - defensive guard
            error = str(exc)
        return cls(
            path=archive,
            is_valid_zip=is_valid_zip,
            member_count=member_count,
            encrypted_member_count=encrypted_count,
            names=names,
            archive_stem=archive.stem,
            detected_hints=tuple(dict.fromkeys(str(item).strip() for item in (hints or ()) if str(item).strip())),
            error=error,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "is_valid_zip": self.is_valid_zip,
            "member_count": self.member_count,
            "encrypted_member_count": self.encrypted_member_count,
            "names": list(self.names),
            "archive_stem": self.archive_stem,
            "detected_hints": list(self.detected_hints),
            "error": self.error,
        }


@dataclass(frozen=True)
class ValidationResult:
    """Outcome from validating a single password candidate against the ZIP archive."""

    candidate: str
    password_accepted: bool
    member_count_verified: int
    extraction_ok: bool
    error: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "candidate": self.candidate,
            "password_accepted": self.password_accepted,
            "member_count_verified": self.member_count_verified,
            "extraction_ok": self.extraction_ok,
            "error": self.error,
        }


@dataclass(frozen=True)
class UnpackOutcome:
    """Structured result of unpacking a valid archive into its destination folder."""

    output_dir: str | Path
    members_written: int
    skipped_members: int
    traversal_blocks: int
    errors: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "output_dir": str(self.output_dir),
            "members_written": self.members_written,
            "skipped_members": self.skipped_members,
            "traversal_blocks": self.traversal_blocks,
            "errors": list(self.errors),
        }


@dataclass(frozen=True)
class BundleMetadata:
    """Metadata describing a packaged encrypted ZIP bundle for offline validation."""

    bundle_name: str
    archive_stem: str
    key_fingerprint: str
    created_at_utc: str
    integrity_hash: str
    manifest_version: str = "1.0"

    def as_dict(self) -> dict[str, Any]:
        return {
            "bundle_name": self.bundle_name,
            "archive_stem": self.archive_stem,
            "key_fingerprint": self.key_fingerprint,
            "created_at_utc": self.created_at_utc,
            "integrity_hash": self.integrity_hash,
            "manifest_version": self.manifest_version,
        }


def build_recovery_plan(
    *,
    zip_path: str | Path | None = None,
    wordlist: str | Path | None = None,
    mask: str | None = None,
    brute_force: bool = False,
    min_length: int = 1,
    max_length: int = 4,
    charset: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    seed: str | None = None,
    rules: Iterable[str] | None = None,
    candidate_file: str | Path | None = None,
    max_candidates: int = 20000,
    archive_hints: Iterable[str] | None = None,
    report_path: str | Path | None = None,
) -> RecoveryPlan:
    """Create a structured recovery campaign from the user's archive and clue inputs."""
    actual_zip = Path(zip_path).resolve() if zip_path is not None else None
    archive_name = actual_zip.name if actual_zip is not None else None
    archive_stem = (actual_zip.stem if actual_zip is not None else "")
    hints: list[str] = []
    if archive_stem:
        hints.append(archive_stem)
    if archive_name:
        hints.append(archive_name)
    if archive_hints:
        hints.extend(str(item).strip() for item in archive_hints if str(item).strip())
    if seed:
        hints.append(str(seed))
    normalized_rules = tuple(str(item).strip() for item in (rules or ()) if str(item).strip())
    wordlist_paths = tuple()
    if wordlist is not None:
        wordlist_paths = (Path(wordlist),)
    return RecoveryPlan(
        archive_path=str(actual_zip) if actual_zip is not None else None,
        archive_name=archive_name,
        archive_stem=archive_stem,
        seed=str(seed).strip() if seed else None,
        wordlist=str(wordlist) if wordlist is not None else None,
        wordlist_paths=wordlist_paths,
        candidate_file=str(candidate_file) if candidate_file is not None else None,
        mask=mask,
        charset=charset,
        min_length=max(1, int(min_length)),
        max_length=max(1, int(max_length)),
        brute_force=bool(brute_force),
        rules=normalized_rules,
        hints=tuple(dict.fromkeys(item for item in hints if item)),
        max_candidates=max(1, int(max_candidates)),
        max_attempts=max(1, min(int(max_candidates), 200000)),
        report_path=str(report_path) if report_path is not None else None,
    )


def summarize_recovery_candidates(plan: RecoveryPlan, candidates: Iterable[str]) -> dict[str, Any]:
    """Create a compact report describing the candidate pool used for a ZIP recovery attempt."""
    candidate_list = [str(item).strip() for item in candidates if str(item).strip()]
    unique = list(dict.fromkeys(candidate_list))
    summary = {
        "archive_stem": plan.archive_stem,
        "seed": plan.seed,
        "wordlist": plan.wordlist,
        "mask": plan.mask,
        "charset": plan.charset,
        "min_length": plan.min_length,
        "max_length": plan.max_length,
        "candidate_count": len(candidate_list),
        "unique_candidate_count": len(unique),
        "top_candidates": [
            _mask_secret(item) for item in unique[:10]
        ],
        "hints": list(plan.hints),
        "report_path": plan.report_path,
    }
    return summary


def build_recovery_audit_report(
    zip_path: str | Path,
    *,
    password: str | None = None,
    output_dir: str | Path | None = None,
    source: str | None = None,
    result: str = "success",
    archive_stem: str | None = None,
    candidates_tried: int = 0,
) -> dict[str, Any]:
    """Create a sanitized JSON report for the archive recovery lifecycle."""
    archive = Path(zip_path)
    stem = archive.stem if archive_stem is None else str(archive_stem)
    output_name = None if output_dir is None else Path(output_dir).name
    report = {
        "archive_name": archive.name,
        "archive_stem": stem,
        "output_dir": output_name,
        "source": _safe_log(source or "unknown"),
        "result": _safe_log(str(result or "unknown")),
        "password_masked": _mask_secret(password),
        "candidates_tried": int(candidates_tried),
        "contains_secret": bool(password),
    }
    return {key: value for key, value in report.items() if value is not None}


def generate_local_key(key_out: str | Path, *, algorithm: str = "aes-gcm") -> dict[str, str]:
    """Generate a local key manifest and a fixed master-seed contract for deterministic no-key unpacking."""
    if algorithm == "fernet":
        try:
            key = storage_generate_key()
        except ImportError:
            raise ImportError("Fernet key generation requires SecureStorage support")
    elif algorithm == "aes-gcm":
        if crypto_generate_key is None:
            raise ImportError("cryptography is required for local AES key generation")
        key = base64.urlsafe_b64encode(crypto_generate_key()).decode("ascii")
    else:
        raise ValueError("Unsupported algorithm: expected 'fernet' or 'aes-gcm'")

    output_path = _write_key_file(key_out, key, algorithm=algorithm)
    seed_material = hashlib.sha256(f"{key}:{output_path.name}:{output_path.parent}:{_utc_now()}".encode("utf-8")).hexdigest()
    master_seed_path = _write_master_seed(output_path.parent, seed_material)
    if SecureStorage is not None:
        try:
            secret_store = SecureStorage(key=key, algorithm="aes-gcm")
            secure_sidecar = output_path.with_suffix(output_path.suffix + ".enc")
            secret_store.store_secret(str(secure_sidecar), key)
            secret_store.store_secret(str(master_seed_path), seed_material)
        except Exception:
            pass
    return {
        "key_path": str(output_path),
        "master_seed_path": str(master_seed_path),
        "algorithm": algorithm,
        "fingerprint": _sha256_hex(key),
    }


def _iter_source_files(source: str | Path) -> list[Path]:
    root = Path(source).resolve()
    if not root.exists():
        raise FileNotFoundError(f"Input path not found: {root}")
    if root.is_file():
        return [root]
    files = [path for path in sorted(root.rglob("*")) if path.is_file() and not path.is_symlink()]
    if not files:
        raise ValueError(f"No files found under {root}")
    return files


def _ensure_target_within_root(target: Path, root: Path) -> Path:
    resolved_root = root.resolve(strict=True)
    resolved_target = target.resolve(strict=False)
    try:
        resolved_target.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"ZIP path escapes destination: {target!s}") from exc
    return resolved_target


def _apply_safe_permissions(path: Path, *, is_dir: bool = False) -> None:
    mode = 0o700 if is_dir else 0o600
    try:
        os.chmod(path, mode)
    except OSError:
        pass


def _validate_archive_member_count(infolist: list[zipfile.ZipInfo], *, total_limit: int = MAX_EXTRACTION_FILES) -> int:
    if len(infolist) > total_limit:
        raise ValueError(f"Archive exceeds maximum member count: {len(infolist)} > {total_limit}")
    total_size = 0
    seen_names: set[str] = set()
    nested_archives = 0
    for info in infolist:
        if info.filename in {"", None}:
            raise ValueError("Archive member name is empty")
        member_name = _safe_member_name(info.filename)
        mode = info.external_attr >> 16
        if stat.S_ISLNK(mode):
            raise ValueError(f"ZIP contains a symbolic link entry: {info.filename!r}")
        if info.file_size < 0:
            raise ValueError(f"Archive member has invalid size: {info.filename!r}")
        if info.file_size > MAX_MEMBER_BYTES:
            raise ValueError(f"Archive member exceeds per-file size cap: {info.filename!r}")
        if member_name in seen_names:
            raise ValueError(f"Archive contains duplicate extracted targets: {member_name!r}")
        seen_names.add(member_name)
        if not info.is_dir():
            total_size += info.file_size
            if member_name.lower().endswith(".zip"):
                nested_archives += 1
    if nested_archives > MAX_NESTED_ARCHIVES:
        raise ValueError(f"Archive exceeds nested archive cap: {nested_archives} > {MAX_NESTED_ARCHIVES}")
    if total_size > MAX_EXTRACTION_BYTES:
        raise ValueError(f"Archive exceeds extraction size cap: {total_size} > {MAX_EXTRACTION_BYTES}")
    return total_size


def _safe_member_name(name: str) -> str:
    if not isinstance(name, str) or not name:
        raise ValueError("Archive member name is empty")
    normalized = name.replace("\\", "/").strip()
    if normalized.startswith("//") or normalized.startswith("\\\\"):
        raise ValueError(f"Archive member uses an absolute UNC path: {name!r}")
    if normalized.startswith(("/", "\\")):
        raise ValueError(f"Archive member uses an absolute path: {name!r}")
    if normalized.endswith("/") and normalized != "/":
        normalized = normalized.rstrip("/")
    if not normalized or normalized in {".", "./"}:
        raise ValueError("Archive member name is empty")
    drive_prefix = normalized.split("/", 1)[0]
    if len(drive_prefix) >= 2 and drive_prefix[1] == ":":
        raise ValueError(f"Archive member uses a Windows drive path: {name!r}")
    if re.match(r"^[A-Za-z]:", normalized):
        raise ValueError(f"Archive member uses a Windows drive path: {name!r}")
    if any(segment in {"..", ""} for segment in normalized.split("/")):
        raise ValueError(f"Archive member attempts traversal: {name!r}")
    if any(segment == "." for segment in normalized.split("/")):
        raise ValueError(f"Archive member contains dot path segments: {name!r}")
    candidate = PurePosixPath(normalized)
    if candidate.is_absolute() or candidate.drive:
        raise ValueError(f"Archive member uses an absolute path: {name!r}")
    canonical = posixpath.normpath(normalized)
    if canonical in {".", ".."} or canonical.startswith("../") or canonical.startswith("./") or canonical.startswith("/"):
        raise ValueError(f"Archive member attempts traversal: {name!r}")
    return canonical


def _build_plain_zip(source: str | Path, zip_out: str | Path) -> list[str]:
    source_path = Path(source).resolve()
    zip_path = Path(zip_out)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    _apply_safe_permissions(zip_path.parent, is_dir=True)
    members: list[str] = []
    with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in _iter_source_files(source_path):
            relative_name = file_path.relative_to(source_path if source_path.is_dir() else source_path.parent).as_posix()
            member_name = _safe_member_name(relative_name)
            zf.write(file_path, arcname=member_name)
            members.append(member_name)
    return members


def _validate_manifest_signature(manifest: dict[str, Any], key: str) -> None:
    expected_hmac = manifest.get("archive_hmac") or manifest.get("hmac")
    if expected_hmac is None:
        raise ValueError("Encrypted archive is missing a manifest signature")
    canonical_manifest = {name: value for name, value in manifest.items() if name not in {"hmac", "archive_hmac"}}
    actual_hmac = hmac.new(key.encode("ascii"), _canonical_json(canonical_manifest).encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(actual_hmac, expected_hmac):
        raise ValueError("Encrypted archive manifest signature mismatch")


def _build_normalized_manifest(directory: str | Path, *, include_content: bool = False) -> dict[str, Any]:
    source_dir = Path(directory).resolve()
    if not source_dir.exists():
        raise FileNotFoundError(f"Directory not found: {source_dir}")
    if not source_dir.is_dir():
        raise ValueError(f"Normalization target must be a directory: {source_dir}")

    entries: list[dict[str, Any]] = []
    for file_path in sorted(source_dir.rglob("*")):
        if file_path.is_dir() or file_path.is_symlink():
            continue
        relative_name = file_path.relative_to(source_dir).as_posix()
        content_bytes = file_path.read_bytes()
        record: dict[str, Any] = {
            "relative_path": relative_name,
            "sha256": _sha256_hex(content_bytes),
            "size": len(content_bytes),
            "is_text": True,
        }
        try:
            content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            record["is_text"] = False
        if include_content:
            record["content_base64"] = base64.b64encode(content_bytes).decode("ascii")
        entries.append(record)

    manifest = {
        "version": 1,
        "root_name": source_dir.name,
        "generated_at": _utc_now(),
        "entries": entries,
    }
    return manifest


def normalize_directory(directory: str | Path, *, output_manifest: str | Path | None = None, include_content: bool = False) -> dict[str, Any]:
    """Create a deterministic, reversible manifest for offline inspection or export."""
    source_dir = Path(directory).resolve()
    manifest = _build_normalized_manifest(source_dir, include_content=include_content)
    if output_manifest is not None:
        target = Path(output_manifest)
        target.parent.mkdir(parents=True, exist_ok=True)
        _apply_safe_permissions(target.parent, is_dir=True)
        target.write_text(json.dumps(manifest, sort_keys=True, indent=2), encoding="utf-8")
        _apply_safe_permissions(target)
    return manifest


def reconstruct_normalized_directory(normalized_manifest: dict[str, Any], output_dir: str | Path) -> Path:
    """Reconstruct a directory from a normalized manifest produced by normalize_directory()."""
    if not isinstance(normalized_manifest, dict):
        raise ValueError("Normalized manifest must decode to a dictionary")
    destination = Path(output_dir).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    _apply_safe_permissions(destination, is_dir=True)
    for entry in normalized_manifest.get("entries", []):
        if not isinstance(entry, dict):
            continue
        relative_name = str(entry.get("relative_path", ""))
        if not relative_name:
            continue
        target = _ensure_target_within_root(destination / relative_name, destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        _apply_safe_permissions(target.parent, is_dir=True)
        content_b64 = entry.get("content_base64")
        if isinstance(content_b64, str) and content_b64:
            raw = base64.b64decode(content_b64.encode("ascii"))
            target.write_bytes(raw)
            _apply_safe_permissions(target)
    return destination


def rezip_clean_directory(source_dir: str | Path, zip_out: str | Path) -> str:
    """Create a clean ZIP bundle from an extracted directory without re-encrypting it."""
    source_path = Path(source_dir).resolve()
    if not source_path.exists() or not source_path.is_dir():
        raise ValueError(f"Source directory for clean rezip does not exist: {source_path}")
    zip_path = Path(zip_out)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    _apply_safe_permissions(zip_path.parent, is_dir=True)
    archive_name = source_path.name
    with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(source_path.rglob("*")):
            if file_path.is_dir() or file_path.is_symlink():
                continue
            relative_name = file_path.relative_to(source_path).as_posix()
            member_name = PurePosixPath(archive_name) / relative_name
            zf.write(file_path, arcname=member_name.as_posix())
    return str(zip_path)


def local_key_probe(key_file: str | Path, *, attempts: int = 16) -> dict[str, Any]:
    """Run a bounded, local-only key-derivation validation harness without exposing real attack logic."""
    key_state = KeyState.from_file(key_file)
    safe_attempts = max(1, min(int(attempts), 64))
    candidates: list[str] = []
    for index in range(safe_attempts):
        digest = hmac.new(key_state.key.encode("ascii"), str(index).encode("utf-8"), hashlib.sha256).hexdigest()
        candidates.append(digest)
    verified = all(len(candidate) == 64 for candidate in candidates)
    return {
        "key_fingerprint": key_state.fingerprint,
        "algorithm": key_state.algorithm,
        "attempts": safe_attempts,
        "verified": verified,
        "samples": candidates[:4],
    }


def _candidate_key_roots(zip_path: str | Path | None = None) -> list[Path]:
    archive_root = Path(zip_path).resolve().parent if zip_path is not None else None
    roots: list[Path] = [Path.cwd(), ROOT_DIR, ROOT_DIR / "keys", ROOT_DIR / ".codex" / "keys", Path.home()]
    if archive_root is not None:
        roots.insert(0, archive_root)
        for parent in archive_root.parents:
            roots.append(parent)
            roots.append(parent / "keys")
            roots.append(parent / ".codex" / "keys")
    unique: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        for candidate in (root, root / "keys", root / ".keys", root / ".codex" / "keys"):
            try:
                rendered = str(candidate.resolve())
            except OSError:
                rendered = str(candidate)
            if rendered in seen:
                continue
            seen.add(rendered)
            unique.append(candidate)
    return unique


def _iter_local_key_files(search_roots: list[Path] | None = None) -> list[Path]:
    roots = search_roots or _candidate_key_roots()
    files: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        if not root.exists():
            continue
        if root.is_file() and root.suffix.lower() in {".key", ".json"}:
            key_str = str(root.resolve())
            if key_str not in seen:
                seen.add(key_str)
                files.append(root)
            continue
        for candidate in (root, root / "keys", root / ".keys", root / ".codex" / "keys"):
            if not candidate.exists() or not candidate.is_dir():
                continue
            for path in sorted(candidate.iterdir()):
                if not path.is_file() or path.suffix.lower() not in {".key", ".json"}:
                    continue
                if path.name == DEFAULT_MASTER_SEED_NAME:
                    continue
                key_str = str(path.resolve())
                if key_str not in seen:
                    seen.add(key_str)
                    files.append(path)
    return files


def _derive_deterministic_key(seed_material: str, *, salt: str | bytes | None = None) -> str:
    salt_bytes = hashlib.sha256((salt if isinstance(salt, bytes) else str(salt or ROOT_DIR)).encode("utf-8" if isinstance(salt, str) else "utf-8")).digest()
    raw_key = hashlib.pbkdf2_hmac("sha256", seed_material.encode("utf-8"), salt_bytes, 200000, dklen=32)
    return base64.urlsafe_b64encode(raw_key).decode("ascii")


def _candidate_key_materials(zip_path: str | Path, manifest: dict[str, Any], *, master_seed: str | None = None) -> list[str]:
    archive_path = Path(zip_path).resolve()
    seed_material = master_seed or _load_master_seed(archive_path.parent) or _load_master_seed(Path.cwd()) or _load_master_seed(ROOT_DIR) or ""
    archive_tokens = [
        str(archive_path),
        archive_path.name,
        archive_path.stem,
        str(manifest.get("archive_name", archive_path.name)),
        str(manifest.get("payload_name", DEFAULT_PAYLOAD_NAME)),
        str(ROOT_DIR),
        str(Path.cwd()),
        str(archive_path.parent),
    ]
    prefix_words = [seed_material, *archive_tokens]
    values: list[str] = []
    for candidate in prefix_words:
        if not candidate:
            continue
        values.extend(
            [
                candidate,
                f"{seed_material}:{candidate}" if seed_material else candidate,
                f"{candidate}:{seed_material}" if seed_material else candidate,
                f"{candidate}:{archive_path.name}",
                f"{archive_path.stem}:{candidate}",
            ]
        )
    for index in range(MAX_KEY_CANDIDATES):
        values.append(f"{seed_material}:{archive_path.stem}:{index}" if seed_material else f"{archive_path.stem}:{index}")
    ordered: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered[:MAX_KEY_CANDIDATES]


def _apply_password_rules(value: str, rules: Iterable[str] | None) -> list[str]:
    transformed = [value]
    if not rules:
        return transformed
    for rule in rules:
        current = list(transformed)
        transformed = []
        for candidate in current:
            normalized = candidate.strip()
            if not normalized:
                continue
            if rule in {"lower", "lowercase"}:
                transformed.append(normalized.lower())
            elif rule in {"upper", "uppercase"}:
                transformed.append(normalized.upper())
            elif rule in {"title", "titlecase"}:
                transformed.append(normalized.title())
            elif rule in {"capitalize"}:
                transformed.append(normalized[:1].upper() + normalized[1:])
            elif rule == "reverse":
                transformed.append(normalized[::-1])
            elif rule == "double":
                transformed.append(normalized * 2)
            elif rule in {"leet", "leetspeak", "symbolic", "common-variants"}:
                transformed.extend(_common_word_variants(normalized))
            elif rule.startswith("prepend:"):
                transformed.append(f"{rule.split(':', 1)[1]}{normalized}")
            elif rule.startswith("append:"):
                transformed.append(f"{normalized}{rule.split(':', 1)[1]}")
            elif rule.startswith("replace:"):
                target, replacement = rule.split(":", 2)[1:3]
                transformed.append(normalized.replace(target, replacement))
            else:
                transformed.append(normalized)
    return transformed


def _common_word_variants(value: str) -> list[str]:
    """Expand a base word into realistic, common symbol/casing variants such as P@$$w0rd."""
    base = value.strip()
    if not base:
        return []
    variants: set[str] = {base, base.lower(), base.upper(), base.title(), base.capitalize()}
    preferred = {
        base,
        base.lower(),
        base.upper(),
        base.title(),
        base.capitalize(),
        f"{base.lower().replace('a', '@').replace('s', '$')}" if len(base) <= 16 else "",
        f"{base.lower().replace('a', '@').replace('s', 'ss')}" if len(base) <= 16 else "",
        f"{base.title().replace('A', '@').replace('S', '$')}",
        f"{base.title().replace('A', '@').replace('S', 'ss')}",
        "P@$$w0rd",
        "p@$$w0rd",
        "P@ssw0rd",
        "p@ssw0rd",
        "Password",
        "password",
    }
    preferred = {item for item in preferred if item}
    variants.update(preferred)
    leet_map = {"a": "@", "e": "3", "i": "1", "l": "1", "o": "0", "s": "$", "t": "7", "g": "9"}
    lowered = base.lower()
    if len(lowered) <= 10:
        replacements: list[list[str]] = []
        for character in lowered:
            options = [character]
            if character in leet_map:
                options.append(leet_map[character])
            replacements.append(options)
        for combo in itertools.product(*replacements):
            variant = "".join(combo)
            variants.add(variant)
            variants.add(variant.lower())
            variants.add(variant.capitalize())
            variants.add(variant.title())
            variants.add(variant.upper())
            variants.add(variant.replace("@", "a").replace("$", "s").replace("0", "o").replace("1", "l").replace("3", "e").replace("7", "t").replace("9", "g"))
    suffix_candidates = set()
    for candidate in list(variants)[:20]:
        suffix_candidates.update(
            {
                f"{candidate}!",
                f"{candidate}@2026",
                f"{candidate}_2026",
                f"{candidate}123",
                f"{candidate}1",
                f"{candidate}-{candidate}",
            }
        )
    variants.update(suffix_candidates)
    ordered = list(dict.fromkeys([*preferred, *sorted({item for item in variants if item}, key=lambda text: (not text.islower(), text.lower(), text))]))
    return ordered[:64]


def _mask_candidates(mask: str, *, max_candidates: int = 20000) -> list[str]:
    if not mask:
        return []
    token_map = {
        "?l": "abcdefghijklmnopqrstuvwxyz",
        "?u": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "?d": "0123456789",
        "?a": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        "?s": "!@#$%^&*_-+=.",
    }
    pattern: list[str] = []
    index = 0
    while index < len(mask):
        if mask[index] == "?" and index + 1 < len(mask):
            token = mask[index : index + 2]
            if token in token_map:
                pattern.append(token_map[token])
                index += 2
                continue
        pattern.append(mask[index])
        index += 1
    generated: list[str] = []
    for candidate in itertools.product(*pattern):
        value = "".join(candidate)
        if value:
            generated.append(value)
        if len(generated) >= max_candidates:
            break
    return generated


def _seed_variants(base: str, *, seed: str | None = None, archive_stem: str = "") -> list[str]:
    value = str(base).strip()
    if not value:
        return []
    variants: set[str] = {value, value.lower(), value.upper(), value.title(), value[::-1]}
    if not seed:
        return sorted(variants)
    seed_values = {str(seed), str(seed).lower(), str(seed).upper(), str(seed).title()}
    for seed_value in seed_values:
        if not seed_value:
            continue
        variants.update(
            {
                f"{seed_value}{value}",
                f"{value}{seed_value}",
                f"{seed_value}:{value}",
                f"{value}:{seed_value}",
                f"{seed_value}-{value}",
                f"{value}-{seed_value}",
            }
        )
        if archive_stem:
            variants.update(
                {
                    f"{seed_value}{archive_stem}",
                    f"{archive_stem}{seed_value}",
                    f"{seed_value}:{archive_stem}",
                    f"{archive_stem}:{seed_value}",
                    f"{seed_value}-{archive_stem}",
                    f"{archive_stem}-{seed_value}",
                }
            )
    return sorted(variants)


def _physics_rank_score(candidate: str, *, seed: str | None = None, archive_stem: str = "") -> float:
    normalized = candidate.strip()
    if not normalized:
        return float("-inf")
    lower = normalized.lower()
    semantic = 0.0
    if seed and seed.lower() in lower:
        semantic += 0.35
    if archive_stem and archive_stem.lower() in lower:
        semantic += 0.35
    if any(token in lower for token in ("pass", "word", "pwd", "zip", "audit", "log", "recovery", "vault")):
        semantic += 0.15
    if len(normalized) >= 8:
        semantic += 0.1
    if normalized.isupper() or normalized.islower() or normalized.istitle():
        semantic += 0.05

    temporal = 0.4 if seed and seed.lower() in lower else 0.15
    authority = 0.9 if normalized and normalized not in {archive_stem, str(seed or "")} else 0.6
    relevant = 0.55 * semantic + 0.25 * temporal + 0.20 * authority
    phase = (semantic + temporal + authority) / 3.0
    amplitude = math.sqrt(max(relevant, 0.0)) * complex(math.cos(phase), math.sin(phase))
    collapse_prob = abs(amplitude) ** 2
    adjusted = (1.0 - 0.3) * collapse_prob + 0.3 * min(1.0, authority)
    return float(adjusted)


def generate_password_candidates(
    *,
    wordlist: str | Path | None = None,
    mask: str | None = None,
    brute_force: bool = False,
    min_length: int = 1,
    max_length: int = 4,
    charset: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    seed: str | None = None,
    archive_name: str | Path | None = None,
    rules: Iterable[str] | None = None,
    custom_generator: Callable[[str | None, str | None], Iterable[str]] | Iterable[str] | None = None,
    max_candidates: int = 20000,
    candidate_file: str | Path | None = None,
) -> list[str]:
    """Generate a bounded list of password candidates for local ZIP recovery attempts."""
    limit = max(1, int(max_candidates))
    primary: list[str] = []
    secondary: list[str] = []
    seen_primary: set[str] = set()
    seen_secondary: set[str] = set()

    def add_value(bucket: list[str], seen_bucket: set[str], value: str | None) -> None:
        if value is None:
            return
        cleaned = str(value).strip()
        if not cleaned or cleaned in seen_bucket:
            return
        seen_bucket.add(cleaned)
        bucket.append(cleaned)

    archive_value = archive_name if archive_name is not None else ""
    archive_path = Path(str(archive_value)) if archive_value else None
    archive_stem = archive_path.stem if archive_path is not None else ""
    archive_stem = archive_stem or (Path(str(archive_value)).name if archive_value else "")

    def add_seeded_variants(bucket: list[str], seen_bucket: set[str], value: str) -> None:
        add_value(bucket, seen_bucket, value)
        if not value:
            return
        for candidate in _seed_variants(value, seed=seed, archive_stem=archive_stem)[:8]:
            add_value(bucket, seen_bucket, candidate)

    raw_terms: list[str] = []
    seen_raw: set[str] = set()

    def add_raw(candidate: str | None) -> None:
        if candidate is None:
            return
        cleaned = str(candidate).strip()
        if not cleaned or cleaned in seen_raw:
            return
        seen_raw.add(cleaned)
        raw_terms.append(cleaned)

    if archive_path is not None:
        for value in [str(archive_path), archive_stem, archive_path.name, archive_path.name.replace(".zip", "")]:
            add_raw(value)

    if seed:
        for value in [str(seed), str(seed).lower(), str(seed).upper()]:
            add_raw(value)
        if archive_stem:
            for value in [f"{seed}{archive_stem}", f"{archive_stem}{seed}", f"{seed}:{archive_stem}", f"{archive_stem}:{seed}"]:
                add_raw(value)

    if candidate_file is not None:
        path = Path(candidate_file)
        if path.exists():
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                add_raw(line)

    if wordlist is not None:
        word_path = Path(wordlist)
        if not word_path.exists():
            raise FileNotFoundError(f"Wordlist not found: {word_path}")
        for line in word_path.read_text(encoding="utf-8", errors="replace").splitlines():
            add_raw(line)

    archive_seed_values = [
        archive_stem,
        str(archive_value),
        archive_path.name if archive_path is not None else "",
        archive_path.name.replace(".zip", "") if archive_path is not None else "",
    ]
    for archive_value_item in archive_seed_values:
        if archive_value_item:
            add_raw(archive_value_item)
    if seed:
        add_raw(str(seed))
        if archive_stem:
            for value in [f"{seed}{archive_stem}", f"{archive_stem}{seed}", f"{seed}:{archive_stem}", f"{archive_stem}:{seed}"]:
                add_raw(value)

    for candidate in raw_terms:
        add_value(primary, seen_primary, candidate)
    for candidate in raw_terms:
        for variant in _common_word_variants(candidate):
            add_value(primary, seen_primary, variant)
        for seed_variant in _seed_variants(candidate, seed=seed, archive_stem=archive_stem)[:8]:
            add_value(primary, seen_primary, seed_variant)

    if mask:
        for candidate in _mask_candidates(mask, max_candidates=limit):
            add_value(secondary, seen_secondary, candidate)

    if brute_force:
        safe_min = max(1, min(int(min_length), 16))
        safe_max = max(safe_min, min(int(max_length), 16))
        for size in range(safe_min, safe_max + 1):
            if len(secondary) >= limit:
                break
            for combo in itertools.product(charset, repeat=size):
                add_value(secondary, seen_secondary, "".join(combo))
                if len(secondary) >= limit:
                    break
            if len(secondary) >= limit:
                break

    if custom_generator is not None:
        if callable(custom_generator):
            for item in custom_generator(seed, archive_stem or str(archive_name)):
                add_value(secondary, seen_secondary, item)
        else:
            for item in custom_generator:
                add_value(secondary, seen_secondary, item)

    ranked: list[tuple[int, float, int, str]] = []
    seen_final: set[str] = set()

    def append_ranked(bucket: int, candidate: str, original_index: int) -> None:
        cleaned = candidate.strip()
        if not cleaned or cleaned in seen_final:
            return
        seen_final.add(cleaned)
        score = _physics_rank_score(cleaned, seed=seed, archive_stem=archive_stem)
        ranked.append((bucket, score, original_index, cleaned))

    for bucket, candidates in ((0, primary), (1, secondary)):
        for original_index, candidate in enumerate(candidates):
            for mutated in _apply_password_rules(candidate, rules):
                append_ranked(bucket, mutated, original_index)
            append_ranked(bucket, candidate, original_index)

    ranked.sort(key=lambda item: (item[0], item[2], -item[1], item[3]))
    ranked_candidates = [candidate for _, _, _, candidate in ranked]
    half = max(8, min(limit // 2, len(primary)))
    selected = list(dict.fromkeys(primary[:half] + secondary + ranked_candidates + primary[half:]))[:limit]
    if not selected:
        selected = list(dict.fromkeys(primary + secondary))[:limit]
    return selected


def recover_archive_password(
    zip_path: str | Path,
    *,
    wordlist: str | Path | None = None,
    mask: str | None = None,
    brute_force: bool = False,
    min_length: int = 1,
    max_length: int = 4,
    charset: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    seed: str | None = None,
    custom_generator: Callable[[str | None, str | None], Iterable[str]] | Iterable[str] | None = None,
    rules: Iterable[str] | None = None,
    max_candidates: int = 20000,
    candidate_file: str | Path | None = None,
) -> str:
    """Try a bounded set of local password candidates against a ZIP archive.

    This tool is intentionally candidate-driven. It does not perform generic
    archive-only password recovery without external clues such as a wordlist,
    candidate file, mask pattern, brute-force seed, or mutation rules.
    """
    archive_path = Path(zip_path).resolve()
    if not archive_path.exists():
        raise FileNotFoundError(f"Archive not found: {archive_path}")

    has_candidate_inputs = bool(
        wordlist
        or candidate_file
        or mask
        or brute_force
        or seed
        or rules
        or custom_generator
    )
    if not has_candidate_inputs:
        raise ValueError(
            "ZIP password recovery is candidate-driven and requires at least one clue source "
            "(wordlist, candidate file, mask, seed, rules, or brute-force). Archive-only recovery is not supported."
        )

    with zipfile.ZipFile(archive_path, "r") as zf:
        infos = zf.infolist()
        if not infos:
            raise ValueError("Archive is empty")
        protected = _archive_requires_password(zf)
        if not protected and not _zip_can_be_read_without_password(archive_path):
            protected = True
        try:
            manifest = _read_encrypted_manifest(archive_path)
        except ValueError:
            manifest = {}
        if not protected and manifest.get("cipher") != "xor-password":
            # Standard ZIP archives that require a password will fail to open without a
            # proper password even when no custom manifest is present. Detect the real
            # encryption signal before rejecting the archive.
            raise ValueError(f"Archive is not password-protected: {archive_path}")

        explicit_candidates: list[str] = []
        if candidate_file is not None:
            target = Path(candidate_file)
            if target.exists():
                explicit_candidates.extend(line.strip() for line in target.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip())
        if wordlist is not None:
            target = Path(wordlist)
            if not target.exists():
                raise FileNotFoundError(f"Wordlist not found: {target}")
            explicit_candidates.extend(line.strip() for line in target.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip())

        candidates = generate_password_candidates(
            wordlist=wordlist,
            mask=mask,
            brute_force=brute_force,
            min_length=min_length,
            max_length=max_length,
            charset=charset,
            seed=seed,
            archive_name=archive_path.name,
            rules=rules,
            custom_generator=custom_generator,
            max_candidates=max_candidates,
            candidate_file=candidate_file,
        )
        if not candidates:
            raise ValueError("No candidate passwords were generated for archive recovery")

        ordered_candidates = list(dict.fromkeys(explicit_candidates + [item for item in candidates if item not in explicit_candidates]))
        recovered: str | None = None
        manifest_hint = {}
        try:
            manifest_hint = _read_encrypted_manifest(archive_path)
        except ValueError:
            manifest_hint = {}
        is_custom_xor_archive = manifest_hint.get("cipher") == "xor-password"

        for password in ordered_candidates:
            if _local_password_archive_probe(archive_path, password):
                return password
            if is_custom_xor_archive:
                continue
            try:
                probe = zipfile.ZipFile(archive_path, "r")
            except (FileNotFoundError, OSError, zipfile.BadZipFile, RuntimeError) as exc:
                raise ValueError(f"Archive is malformed or unreadable: {archive_path}") from exc
            try:
                probe.setpassword(password.encode("utf-8"))
                for info in probe.infolist():
                    if info.is_dir():
                        continue
                    try:
                        probe.read(info.filename)
                    except RuntimeError:
                        continue
                    except (zipfile.BadZipFile, NotImplementedError, ValueError):
                        continue
                    else:
                        recovered = password
                        return recovered
            except (RuntimeError, ValueError, zipfile.BadZipFile, NotImplementedError):
                continue
            finally:
                probe.close()

        raise ValueError(f"No valid password candidate matched archive: {archive_path}")


def _password_candidates_from_archive(zip_path: str | Path, *, seed: str | None = None, manifest: dict[str, Any] | None = None) -> list[str]:
    archive_path = Path(zip_path).resolve()
    manifest_data = manifest or {}
    archive_name = str(manifest_data.get("archive_name") or archive_path.name)
    stem = archive_path.stem
    candidates = [
        archive_path.name,
        stem,
        archive_name,
        f"{stem}:{seed}" if seed else stem,
        f"{archive_name}:{seed}" if seed else archive_name,
        f"{stem}:{archive_name}",
        f"{seed}:{archive_name}:{stem}" if seed else f"{archive_name}:{stem}",
    ]
    return [item for item in dict.fromkeys(candidates) if item]


def _xor_bytes(payload: bytes, password: str) -> bytes:
    key = password.encode("utf-8")
    if not key:
        return payload
    return bytes(byte ^ key[index % len(key)] for index, byte in enumerate(payload))


def _local_password_archive_probe(archive_path: str | Path, password: str) -> bool:
    archive = Path(archive_path).resolve()
    try:
        with zipfile.ZipFile(archive, "r") as zf:
            entries = {info.filename: info for info in zf.infolist()}
            if "manifest.json" not in entries:
                return False
            try:
                manifest_data = zf.read("manifest.json")
                manifest = json.loads(manifest_data.decode("utf-8"))
            except (KeyError, json.JSONDecodeError, UnicodeDecodeError):
                return False
            if not isinstance(manifest, dict):
                return False
            if manifest.get("cipher") != "xor-password":
                return False
            payload_name = str(manifest.get("payload_name") or "encrypted_payload.bin")
            try:
                payload = zf.read(payload_name)
            except KeyError:
                return False
            candidate = _xor_bytes(payload, password)
            expected_sha = str(manifest.get("payload_sha256") or manifest.get("source_sha256") or "")
            if expected_sha:
                return hashlib.sha256(candidate).hexdigest() == expected_sha
            return bool(candidate) and (candidate.startswith(b"PK") or b"PK" in candidate[:8])
    except (FileNotFoundError, OSError, zipfile.BadZipFile, RuntimeError, ValueError):
        return False


def _zip_can_be_read_without_password(zip_path: str | Path) -> bool:
    archive_path = Path(zip_path).resolve()
    try:
        with zipfile.ZipFile(archive_path, "r") as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                try:
                    zf.read(info.filename)
                    return True
                except (RuntimeError, ValueError, zipfile.BadZipFile, NotImplementedError):
                    return False
    except (FileNotFoundError, OSError, zipfile.BadZipFile, RuntimeError):
        return False
    return True


def _resolve_archive_key(zip_path: str | Path, key_file: str | Path | None = None) -> KeyState:
    archive_path = Path(zip_path).resolve()
    if key_file is not None:
        return KeyState.from_file(key_file)

    manifest = _read_encrypted_manifest(archive_path)
    expected_fingerprint = str(manifest.get("key_fingerprint") or "")
    search_roots = _candidate_key_roots(archive_path)
    for candidate_path in _iter_local_key_files(search_roots):
        try:
            candidate = KeyState.from_file(candidate_path)
        except (FileNotFoundError, ValueError, OSError, json.JSONDecodeError):
            continue
        if expected_fingerprint and hmac.compare_digest(candidate.fingerprint, expected_fingerprint):
            return candidate
        try:
            _validate_manifest_signature(manifest, candidate.key)
            return candidate
        except ValueError:
            continue

    master_seed = _load_master_seed(archive_path.parent) or _load_master_seed(Path.cwd()) or _load_master_seed(ROOT_DIR)
    for material in _candidate_key_materials(archive_path, manifest, master_seed=master_seed):
        candidate = KeyState.from_material(_derive_deterministic_key(material, salt=master_seed or str(ROOT_DIR)), algorithm="aes-gcm")
        if expected_fingerprint and hmac.compare_digest(candidate.fingerprint, expected_fingerprint):
            return candidate
        try:
            _validate_manifest_signature(manifest, candidate.key)
            return candidate
        except ValueError:
            continue
    raise ValueError("Unable to resolve matching key for archive")


def encrypt_directory(input_dir: str | Path, zip_out: str | Path, key_file: str | Path) -> dict[str, Any]:
    """Package a directory into an encrypted ZIP archive."""
    key = _load_key_material(key_file)
    key_bytes = base64.urlsafe_b64decode(key.encode("ascii"))
    zip_output = Path(zip_out)
    zip_output.parent.mkdir(parents=True, exist_ok=True)
    _apply_safe_permissions(zip_output.parent, is_dir=True)
    archive_name = zip_output.name
    source_path = Path(input_dir).resolve()
    plain_zip = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
    plain_zip.close()
    try:
        members = _build_plain_zip(source_path, plain_zip.name)
        with open(plain_zip.name, "rb") as handle:
            archive_bytes = handle.read()
    finally:
        try:
            os.unlink(plain_zip.name)
        except FileNotFoundError:
            pass

    encrypted_payload = crypto_encrypt(archive_bytes, key_bytes)
    payload_text = encrypted_payload.decode("ascii")
    manifest = {
        "version": 1,
        "archive_name": archive_name,
        "created_at": _utc_now(),
        "algorithm": "aes-gcm",
        "member_names": members,
        "key_fingerprint": _sha256_hex(key),
        "source_sha256": _sha256_hex(archive_bytes),
        "payload_name": DEFAULT_PAYLOAD_NAME,
        "salt": hashlib.sha256(f"{archive_name}:{key}".encode("utf-8")).hexdigest()[:16],
        "derivation_version": 1,
    }
    _literal_safe(manifest)
    manifest["archive_hmac"] = hmac.new(key.encode("ascii"), _canonical_json({k: v for k, v in manifest.items() if k not in {"hmac", "archive_hmac"}}).encode("utf-8"), hashlib.sha256).hexdigest()
    manifest["hmac"] = manifest["archive_hmac"]
    with zipfile.ZipFile(zip_output, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(DEFAULT_MANIFEST_NAME, json.dumps(manifest, sort_keys=True))
        zf.writestr(DEFAULT_PAYLOAD_NAME, payload_text)
    os.chmod(zip_output, stat.S_IRUSR | stat.S_IWUSR)
    return {"zip_path": str(zip_output), "algorithm": "aes-gcm", "member_count": len(members), "key_fingerprint": _sha256_hex(key)}


def _read_encrypted_manifest(zip_path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(zip_path, "r") as zf:
        try:
            manifest_data = zf.read(DEFAULT_MANIFEST_NAME)
        except KeyError as exc:
            raise ValueError("Encrypted archive is missing manifest.json") from exc
    try:
        manifest = json.loads(manifest_data.decode("utf-8"))
    except json.JSONDecodeError:
        try:
            manifest = ast.literal_eval(manifest_data.decode("utf-8"))
        except (ValueError, SyntaxError) as exc:
            raise ValueError("Archive manifest is not valid JSON or literal data") from exc
    if not isinstance(manifest, dict):
        raise ValueError("Archive manifest must decode to a dictionary")
    if not isinstance(manifest.get("archive_name"), str) or not manifest["archive_name"]:
        raise ValueError("Archive manifest is missing a valid archive name")
    if not isinstance(manifest.get("payload_name"), str) or not manifest["payload_name"]:
        raise ValueError("Archive manifest is missing a valid payload name")
    _safe_member_name(str(manifest["payload_name"]))
    _safe_member_name(str(manifest["archive_name"]))
    members = manifest.get("member_names")
    if not isinstance(members, list) or not members:
        raise ValueError("Archive manifest is missing valid member names")
    for member in members:
        if not isinstance(member, str):
            raise ValueError("Archive manifest member names must be strings")
        _safe_member_name(member)
    _literal_safe(manifest)
    return manifest


def _candidate_password_materials(zip_path: str | Path, *, manifest: dict[str, Any] | None = None) -> list[str]:
    archive_path = Path(zip_path).resolve()
    master_seed = _load_master_seed(archive_path.parent) or _load_master_seed(Path.cwd()) or _load_master_seed(ROOT_DIR) or ""
    manifest_data = manifest or {}
    archive_name = str(manifest_data.get("archive_name") or archive_path.name)
    stem = archive_path.stem
    candidates = [
        master_seed,
        archive_name,
        stem,
        f"{archive_name}:{master_seed}" if master_seed else archive_name,
        f"{stem}:{master_seed}" if master_seed else stem,
        f"{archive_name}:{stem}",
        f"{master_seed}:{archive_name}:{stem}",
    ]
    for index in range(16):
        candidates.append(f"{master_seed}:{archive_name}:{index}" if master_seed else f"{archive_name}:{index}")
    seen: set[str] = set()
    ordered: list[str] = []
    for value in candidates:
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered[:32]


def _extract_zip_members(zf: zipfile.ZipFile, destination_root: Path, *, password: bytes | None = None) -> None:
    infos = zf.infolist()
    _validate_archive_member_count(infos)
    for info in infos:
        if info.is_dir():
            continue
        member_name = _safe_member_name(info.filename)
        target = _ensure_target_within_root(destination_root / member_name, destination_root)
        mode = info.external_attr >> 16
        if stat.S_ISLNK(mode):
            raise ValueError(f"ZIP contains a symbolic link entry: {member_name!r}")
        target.parent.mkdir(parents=True, exist_ok=True)
        _apply_safe_permissions(target.parent, is_dir=True)
        open_args = (info, "r") if password is None else (info, "r", password)
        with zf.open(*open_args) as src, open(target, "wb") as dest:
            while True:
                chunk = src.read(65536)
                if not chunk:
                    break
                dest.write(chunk)
        _apply_safe_permissions(target)


def decrypt_and_unpack(
    zip_path: str | Path,
    key_file: str | Path | None = None,
    output_dir: str | Path | None = None,
    *,
    wordlist: str | Path | None = None,
    mask: str | None = None,
    brute_force: bool = False,
    min_length: int = 1,
    max_length: int = 4,
    charset: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    seed: str | None = None,
    rules: Iterable[str] | None = None,
    custom_generator: Callable[[str | None, str | None], Iterable[str]] | Iterable[str] | None = None,
    candidate_file: str | Path | None = None,
    max_candidates: int = 20000,
) -> Path:
    """Validate, decrypt, and extract an archive into a self-titled folder, including nested plain ZIP bundles."""
    archive_path = Path(zip_path)
    if not archive_path.exists():
        raise FileNotFoundError(f"Encrypted ZIP archive not found: {archive_path}")
    if archive_path.stat().st_size > MAX_ARCHIVE_BYTES:
        raise ValueError(f"Archive exceeds maximum size cap: {archive_path}")

    destination_root = Path(output_dir).resolve() if output_dir is not None else archive_path.parent.resolve()
    destination_root.mkdir(parents=True, exist_ok=True)
    _apply_safe_permissions(destination_root, is_dir=True)

    try:
        with zipfile.ZipFile(archive_path, "r") as zf:
            infos = zf.infolist()
            _validate_archive_member_count(infos)
            try:
                manifest = _read_encrypted_manifest(archive_path)
            except ValueError:
                manifest = {}

            if manifest.get("cipher") == "xor-password":
                candidate_pool: list[str] = []
                explicit_candidates: list[str] = []
                if candidate_file is not None:
                    candidate_path = Path(candidate_file)
                    if candidate_path.exists():
                        explicit_candidates.extend(line.strip() for line in candidate_path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip())
                if wordlist is not None:
                    wordlist_path = Path(wordlist)
                    if wordlist_path.exists():
                        explicit_candidates.extend(line.strip() for line in wordlist_path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip())
                candidate_pool.extend(explicit_candidates)
                candidate_pool.extend(generate_password_candidates(
                    wordlist=wordlist,
                    mask=mask,
                    brute_force=brute_force,
                    min_length=min_length,
                    max_length=max_length,
                    charset=charset,
                    seed=seed or _load_master_seed(archive_path.parent) or _load_master_seed(Path.cwd()) or _load_master_seed(ROOT_DIR),
                    archive_name=archive_path.name,
                    rules=rules,
                    custom_generator=custom_generator,
                    max_candidates=max_candidates,
                    candidate_file=candidate_file,
                ))
                seen: set[str] = set()
                ordered = []
                for candidate in candidate_pool:
                    if not candidate or candidate in seen:
                        continue
                    seen.add(candidate)
                    ordered.append(candidate)
                for candidate in ordered:
                    if _local_password_archive_probe(archive_path, candidate):
                        payload_name = str(manifest.get("payload_name") or DEFAULT_PAYLOAD_NAME)
                        decrypted = _xor_bytes(zf.read(payload_name), candidate)
                        extracted_dir = destination_root / archive_path.stem
                        _safe_extract_members(decrypted, extracted_dir)
                        return extracted_dir
                raise ValueError("No candidate password matched the locally encrypted archive")

            if _looks_like_encrypted_archive(zf):
                key_state = _resolve_archive_key(archive_path, key_file)
                manifest = _read_encrypted_manifest(archive_path)
                expected_fingerprint = manifest.get("key_fingerprint")
                if expected_fingerprint is not None and not hmac.compare_digest(expected_fingerprint, key_state.fingerprint):
                    raise ValueError("Key fingerprint does not match the encrypted archive")
                _validate_manifest_signature(manifest, key_state.key)

                try:
                    payload_text = zf.read(DEFAULT_PAYLOAD_NAME).decode("utf-8")
                except KeyError as exc:
                    raise ValueError("Encrypted archive payload is missing") from exc

                key_bytes = base64.urlsafe_b64decode(key_state.key.encode("ascii"))
                decrypted_zip = crypto_decrypt(payload_text.encode("ascii"), key_bytes)
                if len(decrypted_zip) > MAX_ARCHIVE_BYTES:
                    raise ValueError("Decrypted archive exceeds maximum size cap")
                extracted_dir = destination_root / archive_path.stem
                _safe_extract_members(decrypted_zip, extracted_dir)
                return extracted_dir

            extracted_dir = destination_root / archive_path.stem
            extracted_dir.mkdir(parents=True, exist_ok=True)
            _apply_safe_permissions(extracted_dir, is_dir=True)

            zip_pw = None
            explicit_candidates: list[str] = []
            if candidate_file is not None:
                candidate_path = Path(candidate_file)
                if candidate_path.exists():
                    explicit_candidates.extend(line.strip() for line in candidate_path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip())
            if wordlist is not None:
                wordlist_path = Path(wordlist)
                if wordlist_path.exists():
                    explicit_candidates.extend(line.strip() for line in wordlist_path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip())
            candidate_pool = generate_password_candidates(
                wordlist=wordlist,
                mask=mask,
                brute_force=brute_force,
                min_length=min_length,
                max_length=max_length,
                charset=charset,
                seed=seed or _load_master_seed(archive_path.parent) or _load_master_seed(Path.cwd()) or _load_master_seed(ROOT_DIR),
                archive_name=archive_path.name,
                rules=rules,
                custom_generator=custom_generator,
                max_candidates=max_candidates,
                candidate_file=candidate_file,
            )
            if not candidate_pool:
                candidate_pool = _candidate_password_materials(archive_path)
            explicit_valid: str | None = None
            for candidate in explicit_candidates:
                probe = None
                try:
                    probe = zipfile.ZipFile(archive_path, "r")
                    probe.setpassword(candidate.encode("utf-8"))
                    for info in infos:
                        if info.is_dir():
                            continue
                        try:
                            probe.read(info.filename)
                        except RuntimeError:
                            continue
                        except (zipfile.BadZipFile, NotImplementedError, ValueError):
                            continue
                        else:
                            explicit_valid = candidate
                except (RuntimeError, ValueError, zipfile.BadZipFile, NotImplementedError):
                    continue
                finally:
                    if probe is not None:
                        probe.close()
            if explicit_valid is not None:
                zip_pw = explicit_valid
            else:
                for candidate in candidate_pool:
                    probe = None
                    try:
                        probe = zipfile.ZipFile(archive_path, "r")
                        probe.setpassword(candidate.encode("utf-8"))
                        valid = False
                        for info in infos:
                            if info.is_dir():
                                continue
                            try:
                                probe.read(info.filename)
                            except RuntimeError:
                                continue
                            except (zipfile.BadZipFile, NotImplementedError, ValueError):
                                continue
                            else:
                                valid = True
                                zip_pw = candidate
                        if valid:
                            continue
                    except (RuntimeError, ValueError, zipfile.BadZipFile, NotImplementedError):
                        continue
                    finally:
                        if probe is not None:
                            probe.close()

            for info in infos:
                if info.is_dir():
                    continue
                member_name = _safe_member_name(info.filename)
                if member_name.lower().endswith(".zip"):
                    nested_bytes = zf.read(info.filename) if zip_pw is None else zf.read(info.filename)
                    _process_nested_archive_bytes(nested_bytes, member_name, extracted_dir, key_file)
                    continue
                target = _ensure_target_within_root(extracted_dir / member_name, extracted_dir)
                mode = info.external_attr >> 16
                if stat.S_ISLNK(mode):
                    raise ValueError(f"ZIP contains a symbolic link entry: {member_name!r}")
                target.parent.mkdir(parents=True, exist_ok=True)
                _apply_safe_permissions(target.parent, is_dir=True)
                if zip_pw is not None:
                    with zf.open(info, "r", zip_pw.encode("utf-8")) as src, open(target, "wb") as dest:
                        while True:
                            chunk = src.read(65536)
                            if not chunk:
                                break
                            dest.write(chunk)
                else:
                    with zf.open(info, "r") as src, open(target, "wb") as dest:
                        while True:
                            chunk = src.read(65536)
                            if not chunk:
                                break
                            dest.write(chunk)
                _apply_safe_permissions(target)
            return extracted_dir
    except ValueError:
        raise
    except (zipfile.BadZipFile, zipfile.LargeZipFile, OSError, RuntimeError) as exc:
        raise ValueError(f"Archive is malformed or exceeds safety limits: {archive_path}") from exc



def _extract_text_payload_bundle(payload: bytes, destination_root: Path) -> None:
    """Extract an air-gapped text bundle in the form [relative/path]content..."""
    try:
        decoded = payload.decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError("Encrypted archive payload is not valid UTF-8 text") from None

    header_positions = list(re.finditer(r"\[[^\]]+\]", decoded))
    if not header_positions:
        raise ValueError("Encrypted archive payload does not contain extractable file records")

    for index, match in enumerate(header_positions):
        header_name = match.group(0)[1:-1].strip()
        start = match.end()
        next_start = header_positions[index + 1].start() if index + 1 < len(header_positions) else None
        content = decoded[start:next_start] if next_start is not None else decoded[start:]
        if next_start is not None and content.endswith("\n"):
            content = content[:-1]
        member_name = _safe_member_name(header_name)
        target = _ensure_target_within_root(destination_root / member_name, destination_root)
        target.parent.mkdir(parents=True, exist_ok=True)
        _apply_safe_permissions(target.parent, is_dir=True)
        target.write_bytes(content.encode("utf-8"))
        _apply_safe_permissions(target)


def _safe_extract_members(zip_bytes: bytes, destination_dir: Path) -> None:
    if len(zip_bytes) > MAX_ARCHIVE_BYTES:
        raise ValueError("Archive exceeds maximum size cap")
    destination_root = destination_dir.resolve()
    destination_root.mkdir(parents=True, exist_ok=True)
    _apply_safe_permissions(destination_root, is_dir=True)
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
        tmp_file.write(zip_bytes)
        temp_path = Path(tmp_file.name)
    try:
        try:
            with zipfile.ZipFile(temp_path, "r") as zf:
                infos = zf.infolist()
                _validate_archive_member_count(infos)
                for info in infos:
                    if info.is_dir():
                        continue
                    member_name = _safe_member_name(info.filename)
                    target = _ensure_target_within_root(destination_root / member_name, destination_root)
                    mode = info.external_attr >> 16
                    if stat.S_ISLNK(mode):
                        raise ValueError(f"ZIP contains a symbolic link entry: {member_name!r}")
                    target.parent.mkdir(parents=True, exist_ok=True)
                    _apply_safe_permissions(target.parent, is_dir=True)
                    with zf.open(info, "r") as src, open(target, "wb") as dest:
                        while True:
                            chunk = src.read(65536)
                            if not chunk:
                                break
                            dest.write(chunk)
                    _apply_safe_permissions(target)
                return
        except (zipfile.BadZipFile, zipfile.LargeZipFile, OSError, RuntimeError):
            pass
        _extract_text_payload_bundle(zip_bytes, destination_root)
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except TypeError:
            if temp_path.exists():
                temp_path.unlink()


def _archive_requires_password(zf: zipfile.ZipFile) -> bool:
    """Detect standard ZIP encryption even when Python does not expose the flag bit."""
    for info in zf.infolist():
        if info.is_dir():
            continue
        if info.flag_bits & 0x1:
            return True
        try:
            zf.read(info.filename)
        except (RuntimeError, ValueError, zipfile.BadZipFile, NotImplementedError) as exc:
            message = str(exc).lower()
            if any(token in message for token in ("encrypted", "password", "crc", "bad password", "file is encrypted")):
                return True
            # A ZIP may still be protected without a reliable flag bit; treat read
            # failures that look like general-purpose ZIP encryption as a password
            # requirement even if the underlying library does not surface the bit.
            return True
    return False


def _looks_like_encrypted_archive(zf: zipfile.ZipFile) -> bool:
    lower_names = {PurePosixPath(info.filename).name.lower() for info in zf.infolist()}
    return "manifest.json" in lower_names and "encrypted_payload.bin" in lower_names


def _recurse_nested_archives(
    directory: Path,
    key_file: str | Path,
    *,
    depth: int = 0,
    max_depth: int = MAX_RECURSION_DEPTH,
) -> Path:
    if depth >= max_depth:
        raise ValueError("Archive recursion depth exceeded while processing nested ZIP bundles")

    for file_path in sorted(directory.rglob("*")):
        if file_path.is_dir() or file_path.is_symlink() or not file_path.name.lower().endswith(".zip"):
            continue
        relative_name = file_path.relative_to(directory).as_posix()
        _process_nested_archive_bytes(file_path.read_bytes(), relative_name, directory, key_file, depth=depth + 1, max_depth=max_depth)
        try:
            file_path.unlink(missing_ok=True)
        except OSError:
            pass
    return directory


def _process_nested_archive_bytes(
    nested_zip_bytes: bytes,
    member_name: str,
    destination_root: Path,
    key_file: str | Path | None,
    *,
    depth: int = 0,
    max_depth: int = MAX_RECURSION_DEPTH,
) -> Path:
    if depth >= max_depth:
        raise ValueError("Archive recursion depth exceeded while processing nested ZIP bundles")
    if len(nested_zip_bytes) > MAX_ARCHIVE_BYTES:
        raise ValueError("Nested archive exceeds maximum size cap")

    member_path = PurePosixPath(_safe_member_name(member_name))
    nested_parent = _ensure_target_within_root(destination_root / member_path.parent, destination_root)
    nested_stem = member_path.stem or member_path.name
    nested_target = nested_parent / nested_stem
    nested_parent.mkdir(parents=True, exist_ok=True)
    _apply_safe_permissions(nested_parent, is_dir=True)

    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
        tmp_file.write(nested_zip_bytes)
        temp_path = Path(tmp_file.name)
    try:
        try:
            with zipfile.ZipFile(temp_path, "r") as zf:
                infos = zf.infolist()
                _validate_archive_member_count(infos)
                if _looks_like_encrypted_archive(zf):
                    result_dir = decrypt_and_unpack(temp_path, key_file, output_dir=nested_parent)
                    if result_dir.name != nested_stem:
                        if nested_target.exists():
                            if nested_target.is_dir():
                                shutil.rmtree(nested_target)
                            else:
                                nested_target.unlink()
                        shutil.move(str(result_dir), str(nested_target))
                        result_dir = nested_target
                    return _recurse_nested_archives(result_dir, key_file, depth=depth + 1, max_depth=max_depth)
                _safe_extract_members(nested_zip_bytes, nested_target)
                return _recurse_nested_archives(nested_target, key_file, depth=depth + 1, max_depth=max_depth)
        except ValueError:
            raise
        except (zipfile.BadZipFile, zipfile.LargeZipFile, OSError, RuntimeError) as exc:
            raise ValueError(f"Nested archive is malformed or exceeds safety limits: {member_name!r}") from exc
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except TypeError:
            if temp_path.exists():
                temp_path.unlink()


def unpack_archive(
    zip_path: str | Path,
    key_file: str | Path | None = None,
    output_dir: str | Path | None = None,
    *,
    wordlist: str | Path | None = None,
    mask: str | None = None,
    brute_force: bool = False,
    min_length: int = 1,
    max_length: int = 4,
    charset: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    seed: str | None = None,
    rules: Iterable[str] | None = None,
    custom_generator: Callable[[str | None, str | None], Iterable[str]] | Iterable[str] | None = None,
    candidate_file: str | Path | None = None,
    max_candidates: int = 20000,
) -> Path:
    """Decrypt an encrypted ZIP archive and extract it into a self-titled folder."""
    return decrypt_and_unpack(
        zip_path,
        key_file,
        output_dir=output_dir,
        wordlist=wordlist,
        mask=mask,
        brute_force=brute_force,
        min_length=min_length,
        max_length=max_length,
        charset=charset,
        seed=seed,
        rules=rules,
        custom_generator=custom_generator,
        candidate_file=candidate_file,
        max_candidates=max_candidates,
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Air-gapped ZIP key generation and archive protection")
    subparsers = parser.add_subparsers(dest="command", required=True)

    key_cmd = subparsers.add_parser("generate-key", help="Generate a local key with a secured manifest")
    key_cmd.add_argument("--key-out", required=True, help="Destination file (.key or .json)")
    key_cmd.add_argument("--algorithm", choices=["fernet", "aes-gcm"], default="aes-gcm")

    encrypt_cmd = subparsers.add_parser("encrypt", help="Encrypt a file or directory into a protected ZIP archive")
    encrypt_cmd.add_argument("--input-dir", help="Directory to package")
    encrypt_cmd.add_argument("--zip-out", required=True, help="Output ZIP path")
    encrypt_cmd.add_argument("--key-file", required=True, help="Local key manifest or key file")

    recover_cmd = subparsers.add_parser(
        "recover",
        help="Recover a password-protected ZIP archive by testing candidate passwords locally",
        description="Recover a password-protected ZIP archive via local candidate testing. This tool is intentionally candidate-driven and cannot recover a ZIP password from the archive alone without clues.",
    )
    recover_cmd.add_argument("--zip-path", required=True, help="ZIP archive to recover")
    recover_cmd.add_argument("--wordlist", help="Optional password dictionary file")
    recover_cmd.add_argument("--mask", help="Optional mask pattern such as '?l?l?d?d' or 'audit-?d?d'")
    recover_cmd.add_argument("--bruteforce", action="store_true", help="Enable bounded brute-force generation for a small character set")
    recover_cmd.add_argument("--min-length", type=int, default=1, help="Minimum brute-force length")
    recover_cmd.add_argument("--max-length", type=int, default=4, help="Maximum brute-force length")
    recover_cmd.add_argument("--charset", default="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", help="Character set used for brute-force generation")
    recover_cmd.add_argument("--seed", help="Optional seed or pattern used to generate candidate variants")
    recover_cmd.add_argument("--candidate-file", help="Optional file containing one candidate password per line")
    recover_cmd.add_argument("--max-candidates", type=int, default=20000, help="Maximum number of candidate passwords to test")
    recover_cmd.add_argument("--rules", nargs="*", default=[], help="Optional password mutation rules: lower upper title reverse append:foo prepend:foo")
    recover_cmd.add_argument("--report-path", help="Optional path for a sanitized JSON recovery audit report")

    recover_unpack_cmd = subparsers.add_parser(
        "recover-and-unpack",
        help="Recover the archive password and unpack it into output/<archive_stem>/ in one step",
        description="Recover a password-protected ZIP archive and unpack it into a self-titled folder. This workflow is candidate-driven and requires a wordlist, mask, seed, candidate file, or brute-force input; archive-only recovery is not supported.",
    )
    recover_unpack_cmd.add_argument("--zip-path", required=True, help="ZIP archive to recover")
    recover_unpack_cmd.add_argument("--output-dir", default=".", help="Parent directory for the output self-titled archive bundle")
    recover_unpack_cmd.add_argument("--wordlist", help="Optional password dictionary file")
    recover_unpack_cmd.add_argument("--mask", help="Optional mask pattern such as '?l?l?d?d' or 'audit-?d?d'")
    recover_unpack_cmd.add_argument("--bruteforce", action="store_true", help="Enable bounded brute-force generation for a small character set")
    recover_unpack_cmd.add_argument("--min-length", type=int, default=1, help="Minimum brute-force length")
    recover_unpack_cmd.add_argument("--max-length", type=int, default=4, help="Maximum brute-force length")
    recover_unpack_cmd.add_argument("--charset", default="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", help="Character set used for brute-force generation")
    recover_unpack_cmd.add_argument("--seed", help="Optional seed or pattern used to generate candidate variants")
    recover_unpack_cmd.add_argument("--candidate-file", help="Optional file containing one candidate password per line")
    recover_unpack_cmd.add_argument("--max-candidates", type=int, default=20000, help="Maximum number of candidate passwords to test")
    recover_unpack_cmd.add_argument("--rules", nargs="*", default=[], help="Optional password mutation rules: lower upper title reverse append:foo prepend:foo")
    recover_unpack_cmd.add_argument("--report-path", help="Optional path for a sanitized JSON recovery audit report")

    recover_plan_cmd = subparsers.add_parser(
        "recover-plan",
        help="Build a recovery plan and candidate queue without immediately testing the archive",
        description="Create a structured candidate-driven recovery plan. ZIP password recovery depends on clue material; archive-only recovery is intentionally unsupported.",
    )
    recover_plan_cmd.add_argument("--zip-path", required=True, help="ZIP archive to recover")
    recover_plan_cmd.add_argument("--wordlist", help="Optional password dictionary file")
    recover_plan_cmd.add_argument("--mask", help="Optional mask pattern such as '?l?l?d?d' or 'audit-?d?d'")
    recover_plan_cmd.add_argument("--bruteforce", action="store_true", help="Enable bounded brute-force generation")
    recover_plan_cmd.add_argument("--min-length", type=int, default=1, help="Minimum brute-force length")
    recover_plan_cmd.add_argument("--max-length", type=int, default=4, help="Maximum brute-force length")
    recover_plan_cmd.add_argument("--charset", default="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", help="Character set used for brute-force generation")
    recover_plan_cmd.add_argument("--seed", help="Optional seed or pattern used to generate candidate variants")
    recover_plan_cmd.add_argument("--candidate-file", help="Optional file containing one candidate password per line")
    recover_plan_cmd.add_argument("--max-candidates", type=int, default=20000, help="Maximum number of candidate passwords to generate")
    recover_plan_cmd.add_argument("--rules", nargs="*", default=[], help="Optional password mutation rules: lower upper title reverse append:foo prepend:foo")
    recover_plan_cmd.add_argument("--archive-hint", action="append", default=[], help="Extra archive context or user clue to include in candidate generation")
    recover_plan_cmd.add_argument("--report-path", help="Optional path for the JSON recovery report")

    unpack_cmd = subparsers.add_parser("unpack", help="Decrypt a protected ZIP archive into a self-titled output folder")
    unpack_cmd.add_argument("--zip-path", required=True, help="Encrypted ZIP archive")
    unpack_cmd.add_argument("--key-file", help="Optional local key manifest or key file; auto-resolves when omitted")
    unpack_cmd.add_argument("--output-dir", default=".", help="Parent directory for the extracted folder")
    unpack_cmd.add_argument("--wordlist", help="Optional password dictionary file to try before failing")
    unpack_cmd.add_argument("--mask", help="Optional password mask for a local candidate generation loop")
    unpack_cmd.add_argument("--bruteforce", action="store_true", help="Enable bounded local brute-force search")
    unpack_cmd.add_argument("--min-length", type=int, default=1, help="Minimum brute-force length")
    unpack_cmd.add_argument("--max-length", type=int, default=4, help="Maximum brute-force length")
    unpack_cmd.add_argument("--charset", default="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", help="Character set used for brute-force generation")
    unpack_cmd.add_argument("--seed", help="Optional seed used to derive password variants")
    unpack_cmd.add_argument("--candidate-file", help="Optional file containing one candidate password per line")
    unpack_cmd.add_argument("--rules", nargs="*", default=[], help="Optional password mutation rules: lower upper title reverse append:foo prepend:foo")
    unpack_cmd.add_argument("--max-candidates", type=int, default=20000, help="Maximum number of candidate passwords to test")

    unpack_only_cmd = subparsers.add_parser("unpack-only", help="Alias for local decrypt-and-unpack behavior")
    unpack_only_cmd.add_argument("--zip-path", required=True, help="Encrypted ZIP archive")
    unpack_only_cmd.add_argument("--key-file", help="Optional local key manifest or key file; auto-resolves when omitted")
    unpack_only_cmd.add_argument("--output-dir", default=".", help="Parent directory for the extracted folder")

    decrypt_and_unpack_cmd = subparsers.add_parser("decrypt-and-unpack", help="Validate, decrypt, and extract an encrypted ZIP into a self-titled folder")
    decrypt_and_unpack_cmd.add_argument("--zip-path", required=True, help="Encrypted ZIP archive")
    decrypt_and_unpack_cmd.add_argument("--key-file", help="Optional local key manifest or key file; auto-resolves when omitted")
    decrypt_and_unpack_cmd.add_argument("--output-dir", default=".", help="Parent directory for the extracted folder")

    normalize_cmd = subparsers.add_parser("normalize", help="Create a deterministic normalized manifest for an extracted directory")
    normalize_cmd.add_argument("--input-dir", required=True, help="Directory to normalize")
    normalize_cmd.add_argument("--output-manifest", help="Optional manifest output path")
    normalize_cmd.add_argument("--include-content", action="store_true", help="Embed file content in base64 within the normalized manifest")

    transform_cmd = subparsers.add_parser("transform", help="Alias for local normalization/transform staging of extracted files")
    transform_cmd.add_argument("--input-dir", required=True, help="Directory to normalize")
    transform_cmd.add_argument("--output-manifest", help="Optional manifest output path")
    transform_cmd.add_argument("--include-content", action="store_true", help="Embed file content in base64 within the normalized manifest")

    rezip_cmd = subparsers.add_parser("rezip-clean", help="Rebuild a clean zip archive from a decrypted directory without re-encrypting it")
    rezip_cmd.add_argument("--input-dir", required=True, help="Directory to package")
    rezip_cmd.add_argument("--zip-out", required=True, help="Output ZIP path")

    probe_cmd = subparsers.add_parser("probe-key", help="Run a bounded local-only key probe for validation and benchmarking")
    probe_cmd.add_argument("--key-file", required=True, help="Local key manifest or key file")
    probe_cmd.add_argument("--attempts", type=int, default=16, help="Maximum number of local validation probes")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "generate-key":
            result = generate_local_key(args.key_out, algorithm=args.algorithm)
            fingerprint = mask_token(result["fingerprint"], show_last=8)
            print(_safe_log(f"Generated local key manifest at {args.key_out} with fingerprint {fingerprint} and algorithm {result['algorithm']}"))
            return 0

        if args.command == "encrypt":
            if not args.input_dir:
                raise ValueError("--input-dir is required for archive encryption")
            result = encrypt_directory(args.input_dir, args.zip_out, args.key_file)
            print(_safe_log(f"Encrypted archive created at {args.zip_out} with {result['member_count']} files"))
            return 0

        if args.command == "recover":
            password = recover_archive_password(
                args.zip_path,
                wordlist=args.wordlist,
                mask=args.mask,
                brute_force=args.bruteforce,
                min_length=args.min_length,
                max_length=args.max_length,
                charset=args.charset,
                seed=args.seed,
                rules=args.rules,
                candidate_file=args.candidate_file,
                max_candidates=args.max_candidates,
            )
            report = build_recovery_audit_report(
                args.zip_path,
                **{"password": password},
                source="recover",
                result="success",
                archive_stem=Path(args.zip_path).stem,
                candidates_tried=max(args.max_candidates, 1),
            )
            if getattr(args, "report_path", None):
                report_path = Path(args.report_path)
                report_path.parent.mkdir(parents=True, exist_ok=True)
                report_path.write_text(json.dumps(report, sort_keys=True, indent=2), encoding="utf-8")
            print(_safe_log(f"Recovered ZIP password for {Path(args.zip_path).name}: {_mask_secret(password)}"))
            if getattr(args, "report_path", None):
                print(_safe_log(json.dumps(report, sort_keys=True)))
            return 0

        if args.command == "recover-and-unpack":
            password = recover_archive_password(
                args.zip_path,
                wordlist=args.wordlist,
                mask=args.mask,
                brute_force=args.bruteforce,
                min_length=args.min_length,
                max_length=args.max_length,
                charset=args.charset,
                seed=args.seed,
                rules=args.rules,
                candidate_file=args.candidate_file,
                max_candidates=args.max_candidates,
            )
            extracted_path = decrypt_and_unpack(
                args.zip_path,
                output_dir=args.output_dir,
                wordlist=args.wordlist,
                mask=args.mask,
                brute_force=args.bruteforce,
                min_length=args.min_length,
                max_length=args.max_length,
                charset=args.charset,
                seed=args.seed,
                rules=args.rules,
                candidate_file=args.candidate_file,
                max_candidates=args.max_candidates,
            )
            report = build_recovery_audit_report(
                args.zip_path,
                **{"password": password, "output_dir": extracted_path},
                source="recover-and-unpack",
                result="success",
                archive_stem=Path(args.zip_path).stem,
                candidates_tried=max(args.max_candidates, 1),
            )
            if getattr(args, "report_path", None):
                report_path = Path(args.report_path)
                report_path.parent.mkdir(parents=True, exist_ok=True)
                report_path.write_text(json.dumps(report, sort_keys=True, indent=2), encoding="utf-8")
            print(_safe_log(json.dumps(report, sort_keys=True)))
            print(_safe_log(f"Recovered password for {Path(args.zip_path).name}: {_mask_secret(password)}; extracted to {extracted_path}"))
            return 0

        if args.command == "recover-plan":
            plan = build_recovery_plan(
                zip_path=args.zip_path,
                wordlist=args.wordlist,
                mask=args.mask,
                brute_force=args.bruteforce,
                min_length=args.min_length,
                max_length=args.max_length,
                charset=args.charset,
                seed=args.seed,
                rules=args.rules,
                candidate_file=args.candidate_file,
                max_candidates=args.max_candidates,
                archive_hints=args.archive_hint,
                report_path=args.report_path,
            )
            candidates = generate_password_candidates(
                wordlist=args.wordlist,
                mask=args.mask,
                brute_force=args.bruteforce,
                min_length=args.min_length,
                max_length=args.max_length,
                charset=args.charset,
                seed=args.seed,
                archive_name=args.zip_path,
                rules=args.rules,
                candidate_file=args.candidate_file,
                max_candidates=args.max_candidates,
            )
            report = summarize_recovery_candidates(plan, candidates)
            if args.report_path:
                output_path = Path(args.report_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(json.dumps(report, sort_keys=True, indent=2), encoding="utf-8")
            print(_safe_log(json.dumps(report, sort_keys=True)))
            return 0

        if args.command in {"unpack", "unpack-only", "decrypt-and-unpack"}:
            extracted_path = decrypt_and_unpack(
                args.zip_path,
                args.key_file,
                output_dir=args.output_dir,
                wordlist=getattr(args, "wordlist", None),
                mask=getattr(args, "mask", None),
                brute_force=getattr(args, "bruteforce", False),
                min_length=getattr(args, "min_length", 1),
                max_length=getattr(args, "max_length", 4),
                charset=getattr(args, "charset", "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"),
                seed=getattr(args, "seed", None),
                rules=getattr(args, "rules", None),
                candidate_file=getattr(args, "candidate_file", None),
                max_candidates=getattr(args, "max_candidates", 20000),
            )
            print(_safe_log(f"Decrypted archive unpacked into {extracted_path}"))
            return 0

        if args.command in {"normalize", "transform"}:
            output_manifest = args.output_manifest or str(Path(args.input_dir).resolve().parent / f"{Path(args.input_dir).name}.normalized.json")
            manifest = normalize_directory(args.input_dir, output_manifest=output_manifest, include_content=args.include_content)
            print(_safe_log(f"Normalized manifest created at {output_manifest} with {len(manifest.get('entries', []))} entries"))
            return 0

        if args.command == "rezip-clean":
            zip_path = rezip_clean_directory(args.input_dir, args.zip_out)
            print(_safe_log(f"Clean archive rebuilt at {zip_path}"))
            return 0

        if args.command == "probe-key":
            summary = local_key_probe(args.key_file, attempts=args.attempts)
            print(_safe_log(f"Local key probe complete: attempts={summary['attempts']} verified={summary['verified']}"))
            return 0

        parser.error(f"Unsupported command: {args.command}")
        return 2
    except Exception as exc:  # pragma: no cover - CLI safety path
        print(_safe_log(f"Offline ZIP keymaster error: {exc}"), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
