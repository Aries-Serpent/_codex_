import subprocess
from pathlib import Path

from scripts.archive.git_patch_bundle import apply_bundle, bundle_changes, verify_bundle
import pytest


def test_git_patch_bundle_round_trip(tmp_path: Path) -> None:
    source = tmp_path / "source_repo"
    source.mkdir()
    subprocess.run(["git", "init"], cwd=source, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=source, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=source, check=True)

    initial = source / "tracked.txt"
    initial.write_text("before\n", encoding="utf-8")
    subprocess.run(["git", "add", "tracked.txt"], cwd=source, check=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=source,
        check=True,
        capture_output=True,
        text=True,
    )

    target = tmp_path / "target_repo"
    subprocess.run(["git", "clone", str(source), str(target)], check=True, capture_output=True, text=True)

    initial.write_text("after\n", encoding="utf-8")
    new_file = source / "new.txt"
    new_file.write_text("brand-new\n", encoding="utf-8")

    bundle = bundle_changes(source, tmp_path / "bundles", "sandbox-example")
    assert bundle.exists(), "Condition must be true"
    bundle_hash = bundle.with_name(f"{bundle.name}.sha256")
    assert bundle_hash.exists(), "Condition must be true"
    assert bundle_hash.read_text(encoding="utf-8").strip(), "Condition must be true"
    verify_bundle(bundle)

    apply_bundle(bundle, target)

    assert (target / "tracked.txt").read_text(encoding="utf-8") == "after\n", "Condition must be true"
    assert (target / "new.txt").read_text(encoding="utf-8") == "brand-new\n", "Condition must be true"

    subprocess.run(["git", "-C", str(target), "status", "--short"], check=True)


def test_bundle_refuses_deleted_sensitive_file(tmp_path: Path) -> None:
    source = tmp_path / "source_repo"
    source.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=source, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=source, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=source, check=True)
    secret = source / ".env"
    secret.write_text("SECRET=value\n", encoding="utf-8")
    subprocess.run(["git", "add", ".env"], cwd=source, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "add secret"], cwd=source, check=True)
    secret.unlink()

    with pytest.raises(ValueError, match="Sensitive"):
        bundle_changes(source, tmp_path / "bundles", "sensitive-deleted")


def test_bundle_refuses_ssh_private_key_basename(tmp_path: Path) -> None:
    source = tmp_path / "source_repo"
    source.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=source, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=source, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=source, check=True)
    key = source / "id_ed25519"
    key.write_text("PRIVATE KEY\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Sensitive"):
        bundle_changes(source, tmp_path / "bundles", "private-key")


def test_bundle_refuses_symlink_snapshot(tmp_path: Path) -> None:
    source = tmp_path / "source_repo"
    source.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=source, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=source, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=source, check=True)
    outside = tmp_path / "outside.txt"
    outside.write_text("outside\n", encoding="utf-8")
    (source / "notes.txt").symlink_to(outside)

    with pytest.raises(ValueError, match="Symlink|escapes"):
        bundle_changes(source, tmp_path / "bundles", "symlink")


def test_bundle_decodes_quoted_porcelain_paths(tmp_path: Path) -> None:
    source = tmp_path / "source_repo"
    source.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=source, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=source, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=source, check=True)
    initial = source / "README.md"
    initial.write_text("before\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=source, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "initial"], cwd=source, check=True)

    spaced = source / "my config"
    spaced.mkdir()
    (spaced / "notes.txt").write_text("safe\n", encoding="utf-8")

    bundle = bundle_changes(source, tmp_path / "bundles", "quoted-path")

    assert bundle.exists()
    verify_bundle(bundle)
