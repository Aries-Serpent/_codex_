from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.security.offline_zip_keymaster import (  # noqa: E402
    MAX_MEMBER_BYTES,
    _common_word_variants,
    encrypt_directory,
    generate_local_key,
    generate_password_candidates,
    main,
    normalize_directory,
    recover_archive_password,
    reconstruct_normalized_directory,
    rezip_clean_directory,
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


def _xor_bytes(payload: bytes, password: str) -> bytes:
    if not password:
        return payload
    key = password.encode("utf-8")
    return bytes(byte ^ key[index % len(key)] for index, byte in enumerate(payload))


def _write_local_password_archive(zip_path: Path, password: str, *, files: dict[str, bytes]) -> None:
    plaintext = b"\n".join([b"[" + name.encode("utf-8") + b"]" + content for name, content in files.items()])
    encrypted_bytes = _xor_bytes(plaintext, password)
    manifest = {
        "version": 1,
        "cipher": "xor-password",
        "archive_name": zip_path.name,
        "payload_name": "encrypted_payload.bin",
        "payload_sha256": __import__("hashlib").sha256(plaintext).hexdigest(),
        "member_names": list(files.keys()),
    }
    with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, sort_keys=True))
        zf.writestr("encrypted_payload.bin", encrypted_bytes)


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


def test_common_word_variants_cover_known_password_patterns():
    variants = _common_word_variants("password")
    assert "P@$$w0rd" in variants
    assert "p@$$w0rd" in variants
    assert "P@ssw0rd" in variants
    assert "Password" in variants


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


def test_unpack_auto_resolves_key_from_local_key_store(sample_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    key_dir = tmp_path / "keys"
    key_dir.mkdir()
    key_file = key_dir / "archive.key"
    generate_local_key(key_file)
    archive_path = tmp_path / "payloads" / "audit_logs.zip"
    encrypt_directory(sample_dir, archive_path, key_file)

    monkeypatch.chdir(tmp_path)
    extracted = unpack_archive(archive_path, output_dir=tmp_path / "output")

    assert extracted.name == "audit_logs"
    assert (extracted / "hello.txt").read_text(encoding="utf-8") == "hello offline\n"
    assert (extracted / "nested" / "hello2.txt").read_text(encoding="utf-8") == "second file\n"


def test_unpack_uses_master_seed_contract_without_explicit_key(sample_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    key_dir = tmp_path / "keys"
    key_dir.mkdir()
    key_file = key_dir / "archive.key"
    result = generate_local_key(key_file)
    assert (key_dir / "master_seed.json").exists()
    archive_path = tmp_path / "payloads" / "deterministic.zip"
    encrypt_directory(sample_dir, archive_path, key_file)

    monkeypatch.chdir(tmp_path)
    extracted = unpack_archive(archive_path, output_dir=tmp_path / "output")

    assert extracted.name == "deterministic"
    assert result["fingerprint"]
    assert (extracted / "hello.txt").read_text(encoding="utf-8") == "hello offline\n"


def test_unpack_password_protected_zip_uses_bounded_candidates(sample_dir: Path, tmp_path: Path):
    zip_path = tmp_path / "passworded.zip"
    zip_password = f"{zip_path.stem}:0"
    files = {
        "hello.txt": b"hello offline\n",
        "nested/hello2.txt": b"second file\n",
    }
    _write_local_password_archive(zip_path, zip_password, files=files)

    (tmp_path / "passwords.txt").write_text(f"{zip_password}\n", encoding="utf-8")
    extracted = unpack_archive(zip_path, output_dir=tmp_path / "output", wordlist=tmp_path / "passwords.txt")

    assert extracted.name == "passworded"
    assert (extracted / "hello.txt").read_text(encoding="utf-8") == "hello offline\n"
    assert (extracted / "nested" / "hello2.txt").read_text(encoding="utf-8") == "second file\n"


def test_standard_zipfile_password_protected_archive_recovers_and_unpacks(tmp_path: Path):
    archive_path = tmp_path / "standard_passworded.zip"
    password = "audit-42"
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    source_file = source_dir / "hello.txt"
    source_file.write_text("secret data\n", encoding="utf-8")

    if not shutil.which("zip"):
        pytest.skip("zip CLI is required to generate a real encrypted ZIP archive")
    subprocess.run(["zip", "-j", "-P", password, str(archive_path), str(source_file)], check=True, capture_output=True)

    wordlist = tmp_path / "passwords.txt"
    wordlist.write_text(f"{password}\n", encoding="utf-8")

    recovered = recover_archive_password(archive_path, wordlist=wordlist)
    assert recovered == password

    extracted = unpack_archive(archive_path, output_dir=tmp_path / "output", wordlist=wordlist)
    assert extracted.name == "standard_passworded"
    assert (extracted / "hello.txt").read_text(encoding="utf-8") == "secret data\n"


def test_recover_requires_candidate_inputs_for_archive_only_attempt(tmp_path: Path):
    archive_path = tmp_path / "standard_passworded.zip"
    password = "audit-42"
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    source_file = source_dir / "hello.txt"
    source_file.write_text("secret data\n", encoding="utf-8")

    if not shutil.which("zip"):
        pytest.skip("zip CLI is required to generate a real encrypted ZIP archive")
    subprocess.run(["zip", "-j", "-P", password, str(archive_path), str(source_file)], check=True, capture_output=True)

    with pytest.raises(ValueError, match="candidate-driven|wordlist|mask|seed|brute-force|archive-only"):
        recover_archive_password(archive_path)


def test_unpack_requires_resolved_key_without_matching_store(sample_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    key_file = tmp_path / "archive.key"
    generate_local_key(key_file)
    archive_path = tmp_path / "payloads" / "audit_logs.zip"
    encrypt_directory(sample_dir, archive_path, key_file)
    monkeypatch.chdir(tmp_path)
    key_file.unlink()
    generate_local_key(tmp_path / "other.key")

    with pytest.raises(ValueError, match="Unable to resolve matching key for archive"):
        unpack_archive(archive_path, output_dir=tmp_path / "output")


def test_unpack_handles_plain_zip_containing_nested_encrypted_bundle(sample_dir: Path, tmp_path: Path):
    key_file = tmp_path / "nested.key"
    generate_local_key(key_file)
    encrypted_bundle = tmp_path / "nested_bundle.zip"
    encrypt_directory(sample_dir, encrypted_bundle, key_file)

    outer_zip = tmp_path / "outer_container.zip"
    with zipfile.ZipFile(outer_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(encrypted_bundle, arcname="packets/nested_bundle.zip")

    extracted = unpack_archive(outer_zip, key_file, output_dir=tmp_path / "outer_output")
    assert extracted.name == "outer_container"
    assert (extracted / "packets" / "nested_bundle" / "hello.txt").read_text(encoding="utf-8") == "hello offline\n"
    assert (extracted / "packets" / "nested_bundle" / "nested" / "hello2.txt").read_text(encoding="utf-8") == "second file\n"


def test_unpack_recurses_through_plain_zip_layers_until_bundle_is_normalized(sample_dir: Path, tmp_path: Path):
    key_file = tmp_path / "recursive.key"
    generate_local_key(key_file)

    inner_encrypted = tmp_path / "inner_encrypted.zip"
    encrypt_directory(sample_dir, inner_encrypted, key_file)

    middle_zip = tmp_path / "middle.zip"
    with zipfile.ZipFile(middle_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(inner_encrypted, arcname="payloads/inner_encrypted.zip")

    outer_zip = tmp_path / "outer_container.zip"
    with zipfile.ZipFile(outer_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(middle_zip, arcname="nested/middle.zip")

    extracted = unpack_archive(outer_zip, key_file, output_dir=tmp_path / "recursive_output")

    assert extracted.name == "outer_container"
    assert (extracted / "nested" / "middle" / "payloads" / "inner_encrypted" / "hello.txt").read_text(encoding="utf-8") == "hello offline\n"
    assert (extracted / "nested" / "middle" / "payloads" / "inner_encrypted" / "nested" / "hello2.txt").read_text(encoding="utf-8") == "second file\n"


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


def test_unpack_rejects_malformed_manifest_fields(tmp_path: Path):
    key_path = tmp_path / "manifest.key"
    generate_local_key(key_path)
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "payload.txt").write_text("still valid\n", encoding="utf-8")
    archive_path = tmp_path / "tampered.zip"
    encrypt_directory(source_dir, archive_path, key_path)

    with zipfile.ZipFile(archive_path, "r") as zf:
        manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
    manifest["hmac"] = "deadbeef"
    manifest["member_names"] = ["../../escape.txt"]
    with zipfile.ZipFile(tmp_path / "tampered-bad.zip", mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, sort_keys=True))
        with zipfile.ZipFile(archive_path, "r") as src:
            zf.writestr("encrypted_payload.bin", src.read("encrypted_payload.bin"))

    with pytest.raises(ValueError, match="traversal|member names|manifest"):
        unpack_archive(tmp_path / "tampered-bad.zip", key_path, output_dir=tmp_path / "tampered_out")


def test_unpack_rejects_windows_path_variants(tmp_path: Path):
    key_path = tmp_path / "windows.key"
    generate_local_key(key_path)
    source_dir = tmp_path / "windows_source"
    source_dir.mkdir()
    (source_dir / "safe.txt").write_text("safe\n", encoding="utf-8")
    archive_path = tmp_path / "windows.zip"
    encrypt_directory(source_dir, archive_path, key_path)

    with zipfile.ZipFile(archive_path, "r") as zf:
        manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
    manifest["member_names"] = ["nested\\..\\escape.txt", "C:/Windows/System32/drivers/etc/hosts"]
    with zipfile.ZipFile(tmp_path / "windows_bad.zip", mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, sort_keys=True))
        with zipfile.ZipFile(archive_path, "r") as src:
            zf.writestr("encrypted_payload.bin", src.read("encrypted_payload.bin"))

    with pytest.raises(ValueError, match="traversal|absolute path|Windows drive"):
        unpack_archive(tmp_path / "windows_bad.zip", key_path, output_dir=tmp_path / "windows_out")


def test_unpack_rejects_oversized_archive_member(tmp_path: Path):
    key_path = tmp_path / "oversize.key"
    generate_local_key(key_path)
    source_dir = tmp_path / "oversize_source"
    source_dir.mkdir()
    oversized = source_dir / "too_big.bin"
    oversized.write_bytes(b"x" * (MAX_MEMBER_BYTES + 1))

    archive_path = tmp_path / "oversize.zip"
    encrypt_directory(source_dir, archive_path, key_path)

    with pytest.raises(ValueError, match="size cap|oversize|per-file size cap"):
        unpack_archive(archive_path, key_path, output_dir=tmp_path / "oversize_out")


def test_normalize_and_reconstruct_preserves_directory_fidelity(tmp_path: Path):
    source_dir = tmp_path / "normalized_source"
    nested = source_dir / "nested"
    nested.mkdir(parents=True)
    (source_dir / "top.txt").write_text("first\n", encoding="utf-8")
    (nested / "deep.bin").write_bytes(b"\x00\x01\x02\x03")

    manifest = normalize_directory(source_dir, include_content=True)
    assert manifest["root_name"] == source_dir.name
    paths = [entry["relative_path"] for entry in manifest["entries"]]
    assert paths == ["nested/deep.bin", "top.txt"] or paths == ["top.txt", "nested/deep.bin"]

    output_dir = tmp_path / "reconstructed"
    reconstruct_normalized_directory(manifest, output_dir)
    assert (output_dir / "top.txt").read_text(encoding="utf-8") == "first\n"
    assert (output_dir / "nested" / "deep.bin").read_bytes() == b"\x00\x01\x02\x03"


def test_rezip_clean_directory_keeps_members_relative_and_safe(tmp_path: Path):
    source_dir = tmp_path / "rezip_source"
    nested = source_dir / "nested"
    nested.mkdir(parents=True)
    (nested / "keep.txt").write_text("clean\n", encoding="utf-8")

    archive_path = tmp_path / "clean.zip"
    rezip_clean_directory(source_dir, archive_path)

    with zipfile.ZipFile(archive_path, "r") as zf:
        names = zf.namelist()
        assert names == ["rezip_source/nested/keep.txt"]
        assert not any(name.startswith("/") for name in names)
        assert not any(".." in Path(name).parts for name in names)


def test_unpack_raises_when_nested_zip_recursion_exceeds_limit(tmp_path: Path):
    key_path = tmp_path / "depth.key"
    generate_local_key(key_path)
    source_dir = tmp_path / "depth_source"
    source_dir.mkdir()
    (source_dir / "leaf.txt").write_text("depth\n", encoding="utf-8")

    inner_zip = tmp_path / "inner.zip"
    encrypt_directory(source_dir, inner_zip, key_path)
    for idx in range(9):
        payload_zip = tmp_path / f"layer_{idx}.zip"
        if idx == 0:
            payload = inner_zip.read_bytes()
        else:
            payload = previous.read_bytes()
        with zipfile.ZipFile(payload_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(f"layer_{idx}.zip", payload)
        previous = payload_zip

    with pytest.raises(ValueError, match="recursion depth exceeded"):
        unpack_archive(previous, key_path, output_dir=tmp_path / "depth_output")


def test_generate_password_candidates_supports_dictionary_mask_and_seed():
    wordlist = Path("/tmp/test_wordlist.txt")
    wordlist.write_text("alpha\nBeta\n", encoding="utf-8")
    candidates = generate_password_candidates(
        wordlist=wordlist,
        mask="?d?d",
        seed="seed",
        archive_name="audit_logs.zip",
        rules=["upper"],
        max_candidates=64,
    )

    assert "alpha" in candidates
    assert "Beta" in candidates
    assert "seed" in candidates
    assert "audit_logs" in candidates
    assert "00" in candidates


def test_recover_archive_password_uses_dictionary_candidates(tmp_path: Path):
    zip_path = tmp_path / "recovery.zip"
    password = "winter2026!"
    _write_local_password_archive(zip_path, password, files={"payload.txt": b"encrypted content"})

    wordlist = tmp_path / "passwords.txt"
    wordlist.write_text("spring123\nwinter2026!\n", encoding="utf-8")
    recovered = recover_archive_password(zip_path, wordlist=wordlist)

    assert recovered == password


def test_recover_archive_password_requires_candidate_clues(tmp_path: Path):
    zip_path = tmp_path / "candidate_required.zip"
    password = "mask42"
    _write_local_password_archive(zip_path, password, files={"secret.txt": b"value"})

    with pytest.raises(ValueError, match=r"candidate-driven.*archive-only recovery is not supported"):
        recover_archive_password(zip_path)


def test_cli_recover_help_mentions_candidate_only_recovery_limitation(
    capsys: pytest.CaptureFixture[str],
):
    with pytest.raises(SystemExit) as exc_info:
        main(["recover", "--help"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    help_text = captured.out.lower()
    assert "candidate-driven" in help_text
    assert "archive-only recovery is not supported" in help_text


def test_cli_recover_passwords_from_wordlist(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    zip_path = tmp_path / "cli_recover.zip"
    password = "mask42"
    _write_local_password_archive(zip_path, password, files={"secret.txt": b"value"})

    wordlist = tmp_path / "candidate.txt"
    wordlist.write_text("fallback\nmask42\n", encoding="utf-8")
    code = main(["recover", "--zip-path", str(zip_path), "--wordlist", str(wordlist)])
    captured = capsys.readouterr()

    assert code == 0
    assert "Recovered ZIP password" in captured.out
    assert "mask42" not in captured.out
    assert "sha256:" in captured.out


def test_cli_recover_and_unpack_writes_sanitized_report(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    zip_path = tmp_path / "cli_report.zip"
    password = "mask42"
    _write_local_password_archive(zip_path, password, files={"secret.txt": b"value"})

    wordlist = tmp_path / "report_candidates.txt"
    wordlist.write_text("fallback\nmask42\n", encoding="utf-8")
    report_path = tmp_path / "audit_report.json"

    code = main([
        "recover-and-unpack",
        "--zip-path", str(zip_path),
        "--output-dir", str(tmp_path / "out"),
        "--wordlist", str(wordlist),
        "--report-path", str(report_path),
    ])
    captured = capsys.readouterr()

    assert code == 0
    assert "mask42" not in captured.out
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert "mask42" not in json.dumps(report, sort_keys=True)
    assert report["password_masked"].startswith("sha256:")


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


def test_default_workspace_uses_env_override_for_packaged_runtime(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    from offline_zip_keymaster import cli

    workspace = tmp_path / "runtime_workspace"
    monkeypatch.setenv("OFFLINE_ZIP_KEYMASTER_WORKSPACE", str(workspace))

    assert cli._default_app_workspace() == workspace.resolve()
