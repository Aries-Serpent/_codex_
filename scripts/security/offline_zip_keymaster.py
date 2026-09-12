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
import stat
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from aries_serpent_core.security import mask_token, sanitize_log
    from aries_serpent_core.security.storage import SecureStorage, generate_key as storage_generate_key
except ImportError:  # pragma: no cover - fallback for lightweight runtime
    from utils.sensitive_data import mask_token
    from utils.log_sanitizer import sanitize_log_input as sanitize_log
    SecureStorage = None  # type: ignore[assignment]
    def storage_generate_key() -> str:  # type: ignore[no-redef]
        raise ImportError("aries_serpent_core.security.storage is unavailable")

try:
    import serpent  # type: ignore
except ImportError:  # pragma: no cover - optional structured serialization
    serpent = None

try:
    from security.encryption import EncryptionError, decrypt as crypto_decrypt, encrypt as crypto_encrypt, generate_key as crypto_generate_key
except ImportError:  # pragma: no cover - optional crypto fallback
    crypto_generate_key = None  # type: ignore[assignment]
    crypto_encrypt = None  # type: ignore[assignment]
    crypto_decrypt = None  # type: ignore[assignment]
    EncryptionError = ValueError  # type: ignore[misc, assignment]

DEFAULT_MANIFEST_NAME = "manifest.json"
DEFAULT_PAYLOAD_NAME = "encrypted_payload.bin"


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


def _safe_member_name(name: str) -> str:
    if not name:
        raise ValueError("Archive member name is empty")
    candidate = PurePosixPath(name)
    if candidate.is_absolute() or name.startswith(("/", "\\")):
        raise ValueError(f"Archive member uses an absolute path: {name!r}")
    if ".." in candidate.parts:
        raise ValueError(f"Archive member attempts traversal: {name!r}")
    normalized = name.replace("\\", "/")
    return normalized


def _build_plain_zip(source: str | Path, zip_out: str | Path) -> list[str]:
    source_path = Path(source).resolve()
    zip_path = Path(zip_out)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    members: list[str] = []
    with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in _iter_source_files(source_path):
            relative_name = file_path.relative_to(source_path if source_path.is_dir() else source_path.parent).as_posix()
            member_name = _safe_member_name(relative_name)
            zf.write(file_path, arcname=member_name)
            members.append(member_name)
    return members


def encrypt_directory(input_dir: str | Path, zip_out: str | Path, key_file: str | Path) -> dict[str, Any]:
    """Package a directory into an encrypted ZIP archive."""
    key = _load_key_material(key_file)
    key_bytes = base64.urlsafe_b64decode(key.encode("ascii"))
    zip_output = Path(zip_out)
    zip_output.parent.mkdir(parents=True, exist_ok=True)
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
        manifest = ast.literal_eval(manifest_data.decode("utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("Archive manifest must decode to a dictionary")
    _literal_safe(manifest)
    return manifest


def _safe_extract_members(zip_bytes: bytes, destination_dir: Path) -> None:
    destination_root = destination_dir.resolve()
    destination_root.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
        tmp_file.write(zip_bytes)
        temp_path = Path(tmp_file.name)
    try:
        with zipfile.ZipFile(temp_path, "r") as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                member_name = info.filename
                if not member_name or member_name.startswith(("/", "\\")):
                    raise ValueError(f"Unsafe archive member path: {member_name!r}")
                if ".." in PurePosixPath(member_name).parts:
                    raise ValueError(f"ZIP traversal attempt detected: {member_name!r}")
                target = (destination_root / member_name).resolve()
                try:
                    target.relative_to(destination_root)
                except ValueError as exc:
                    raise ValueError(f"ZIP path escapes destination: {member_name!r}") from exc
                mode = info.external_attr >> 16
                if stat.S_ISLNK(mode):
                    raise ValueError(f"ZIP contains a symbolic link entry: {member_name!r}")
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(info, "r") as src, open(target, "wb") as dest:
                    while True:
                        chunk = src.read(65536)
                        if not chunk:
                            break
                        dest.write(chunk)
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except TypeError:
            if temp_path.exists():
                temp_path.unlink()


def unpack_archive(zip_path: str | Path, key_file: str | Path, output_dir: str | Path | None = None) -> Path:
    """Decrypt an encrypted ZIP archive and extract it into a self-titled folder."""
    archive_path = Path(zip_path)
    if not archive_path.exists():
        raise FileNotFoundError(f"Encrypted ZIP archive not found: {archive_path}")

    key = _load_key_material(key_file)
    manifest = _read_encrypted_manifest(archive_path)
    expected_hmac = manifest.get("hmac")
    if expected_hmac is None:
        raise ValueError("Encrypted archive is missing a manifest signature")
    canonical_manifest = {name: value for name, value in manifest.items() if name != "hmac"}
    actual_hmac = hmac.new(key.encode("ascii"), _canonical_json(canonical_manifest).encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(actual_hmac, expected_hmac):
        raise ValueError("Encrypted archive manifest signature mismatch")

    with zipfile.ZipFile(archive_path, "r") as zf:
        try:
            payload_text = zf.read(DEFAULT_PAYLOAD_NAME).decode("utf-8")
        except KeyError as exc:
            raise ValueError("Encrypted archive payload is missing") from exc

    key_bytes = base64.urlsafe_b64decode(key.encode("ascii"))
    decrypted_zip = crypto_decrypt(payload_text.encode("ascii"), key_bytes)
    destination_root = Path(output_dir).resolve() if output_dir is not None else archive_path.parent.resolve()
    destination_root.mkdir(parents=True, exist_ok=True)
    extracted_dir = destination_root / archive_path.stem
    _safe_extract_members(decrypted_zip, extracted_dir)
    return extracted_dir


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

        if args.command == "unpack":
            extracted_path = unpack_archive(args.zip_path, args.key_file, output_dir=args.output_dir)
            print(_safe_log(f"Decrypted archive unpacked into {extracted_path}"))
            return 0

        parser.error(f"Unsupported command: {args.command}")
        return 2
    except Exception as exc:  # pragma: no cover - CLI safety path
        print(_safe_log(f"Offline ZIP keymaster error: {exc}"), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
