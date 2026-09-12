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
import json
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
from typing import Any

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
MAX_ARCHIVE_BYTES = 512 * 1024 * 1024
MAX_EXTRACTION_BYTES = 512 * 1024 * 1024
MAX_EXTRACTION_FILES = 2048
MAX_RECURSION_DEPTH = 8
MAX_MEMBER_BYTES = 128 * 1024 * 1024
MAX_NESTED_ARCHIVES = 32


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _safe_log(message: str) -> str:
    return sanitize_log(message, max_length=500)


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


def generate_local_key(key_out: str | Path, *, algorithm: str = "aes-gcm") -> dict[str, str]:
    """Generate a local key manifest and write it to disk with 0600 permissions."""
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
    if SecureStorage is not None:
        try:
            secret_store = SecureStorage(key=key, algorithm="aes-gcm")
            secure_sidecar = output_path.with_suffix(output_path.suffix + ".enc")
            secret_store.store_secret(str(secure_sidecar), key)
        except Exception:
            pass
    return {
        "key_path": str(output_path),
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
    expected_hmac = manifest.get("hmac")
    if expected_hmac is None:
        raise ValueError("Encrypted archive is missing a manifest signature")
    canonical_manifest = {name: value for name, value in manifest.items() if name != "hmac"}
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
    }
    _literal_safe(manifest)
    manifest["hmac"] = hmac.new(key.encode("ascii"), _canonical_json({k: v for k, v in manifest.items() if k != "hmac"}).encode("utf-8"), hashlib.sha256).hexdigest()
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


def decrypt_and_unpack(zip_path: str | Path, key_file: str | Path, output_dir: str | Path | None = None) -> Path:
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
            if _looks_like_encrypted_archive(zf):
                key_state = KeyState.from_file(key_file)
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
            for info in infos:
                if info.is_dir():
                    continue
                member_name = _safe_member_name(info.filename)
                if member_name.lower().endswith(".zip"):
                    nested_bytes = zf.read(info.filename)
                    _process_nested_archive_bytes(nested_bytes, member_name, extracted_dir, key_file)
                    continue
                target = _ensure_target_within_root(extracted_dir / member_name, extracted_dir)
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
            return extracted_dir
    except ValueError:
        raise
    except (zipfile.BadZipFile, zipfile.LargeZipFile, OSError, RuntimeError) as exc:
        raise ValueError(f"Archive is malformed or exceeds safety limits: {archive_path}") from exc


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
        except ValueError:
            raise
        except (zipfile.BadZipFile, zipfile.LargeZipFile, OSError, RuntimeError) as exc:
            raise ValueError("Archive is malformed or exceeds safety limits") from exc
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except TypeError:
            if temp_path.exists():
                temp_path.unlink()


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
    key_file: str | Path,
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


def unpack_archive(zip_path: str | Path, key_file: str | Path, output_dir: str | Path | None = None) -> Path:
    """Decrypt an encrypted ZIP archive and extract it into a self-titled folder."""
    return decrypt_and_unpack(zip_path, key_file, output_dir=output_dir)


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

    unpack_cmd = subparsers.add_parser("unpack", help="Decrypt a protected ZIP archive into a self-titled output folder")
    unpack_cmd.add_argument("--zip-path", required=True, help="Encrypted ZIP archive")
    unpack_cmd.add_argument("--key-file", required=True, help="Local key manifest or key file")
    unpack_cmd.add_argument("--output-dir", default=".", help="Parent directory for the extracted folder")

    unpack_only_cmd = subparsers.add_parser("unpack-only", help="Alias for local decrypt-and-unpack behavior")
    unpack_only_cmd.add_argument("--zip-path", required=True, help="Encrypted ZIP archive")
    unpack_only_cmd.add_argument("--key-file", required=True, help="Local key manifest or key file")
    unpack_only_cmd.add_argument("--output-dir", default=".", help="Parent directory for the extracted folder")

    decrypt_and_unpack_cmd = subparsers.add_parser("decrypt-and-unpack", help="Validate, decrypt, and extract an encrypted ZIP into a self-titled folder")
    decrypt_and_unpack_cmd.add_argument("--zip-path", required=True, help="Encrypted ZIP archive")
    decrypt_and_unpack_cmd.add_argument("--key-file", required=True, help="Local key manifest or key file")
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

        if args.command in {"unpack", "unpack-only", "decrypt-and-unpack"}:
            extracted_path = decrypt_and_unpack(args.zip_path, args.key_file, output_dir=args.output_dir)
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
