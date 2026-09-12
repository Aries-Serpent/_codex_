from __future__ import annotations

import json
import os
import stat
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.security.offline_zip_keymaster import (  # noqa: E402
    encrypt_directory,
    generate_local_key,
    main,
    unpack_archive,
)


@pytest.fixture
def sample_dir(tmp_path: Path) -> Path:
    source = tmp_path / "source_data"
    nested = source / "nested"
    nested.mkdir(parents=True)
    (source / "hello.txt").write_text("hello offline\n", encoding="utf-8")
    (nested / "hello2.txt").write_text("second file\n", encoding="utf-8")
    return source


def test_generate_key_creates_secure_manifest(tmp_path: Path):
    key_path = tmp_path / "archive.key"
    result = generate_local_key(key_path)

    assert key_path.exists()
    assert key_path.stat().st_mode & 0o777 == 0o600
    manifest = json.loads(key_path.read_text(encoding="utf-8"))
    assert manifest["algorithm"] == "aes-gcm"
    assert manifest["key"]
    assert result["fingerprint"] == manifest["fingerprint"]
    assert "key" in manifest


def test_encrypt_and_unpack_round_trip(sample_dir: Path, tmp_path: Path):
    key_file = tmp_path / "archive.key"
    key_result = generate_local_key(key_file)
    archive_path = tmp_path / "payloads" / "audit_logs.zip"

    encrypted = encrypt_directory(sample_dir, archive_path, key_file)
    assert encrypted["member_count"] == 2
    assert archive_path.exists()

    extracted = unpack_archive(archive_path, key_file, output_dir=tmp_path / "output")
    assert extracted.name == "audit_logs"
    assert (extracted / "hello.txt").read_text(encoding="utf-8") == "hello offline\n"
    assert (extracted / "nested" / "hello2.txt").read_text(encoding="utf-8") == "second file\n"


def test_unpack_rejects_zip_traversal(tmp_path: Path):
    key_path = tmp_path / "archive.key"
    generate_local_key(key_path)
    malicious_zip = tmp_path / "malicious.zip"
    with zipfile.ZipFile(malicious_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("../escape.txt", "boom")

    payload = malicious_zip.read_bytes()
    from scripts.security.offline_zip_keymaster import _read_encrypted_manifest
    from scripts.security.offline_zip_keymaster import _sha256_hex
    import base64
    from security.encryption import encrypt

    key = json.loads(key_path.read_text(encoding="utf-8"))["key"]
    key_bytes = base64.urlsafe_b64decode(key.encode("ascii"))
    encrypted = encrypt(payload, key_bytes).decode("ascii")
    manifest = {
        "version": 1,
        "archive_name": "malicious.zip",
        "created_at": "2026-01-01T00:00:00Z",
        "algorithm": "aes-gcm",
        "member_names": ["../escape.txt"],
        "key_fingerprint": _sha256_hex(key),
        "source_sha256": _sha256_hex(payload),
        "payload_name": "encrypted_payload.bin",
    }
    manifest["hmac"] = __import__("hmac").new(key.encode("ascii"), json.dumps({k: v for k, v in manifest.items() if k != "hmac"}, sort_keys=True, separators=(",", ":")).encode("utf-8"), __import__("hashlib").sha256).hexdigest()

    with zipfile.ZipFile(tmp_path / "encrypted-malicious.zip", mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, sort_keys=True))
        zf.writestr("encrypted_payload.bin", encrypted)

    with pytest.raises(ValueError, match="traversal|escapes destination|Unsafe archive"):
        unpack_archive(tmp_path / "encrypted-malicious.zip", key_path, output_dir=tmp_path / "out")


def test_cli_generate_key_is_sanitized_and_successful(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    key_path = tmp_path / "cli.key"
    code = main(["generate-key", "--key-out", str(key_path)])
    captured = capsys.readouterr()

    assert code == 0
    assert "Generated local key manifest" in captured.out
    assert str(key_path) in captured.out
    assert key_path.exists()
    assert "eyJ" not in captured.out
    assert "key" not in captured.out.lower() or "manifest" in captured.out.lower()
