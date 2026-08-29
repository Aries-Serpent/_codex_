import shutil
import subprocess
from pathlib import Path

from scripts.archive.git_patch_bundle import apply_bundle, bundle_changes, verify_bundle


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
    assert bundle.exists()
    bundle_hash = bundle.with_name(f"{bundle.name}.sha256")
    assert bundle_hash.exists()
    assert bundle_hash.read_text(encoding="utf-8").strip()
    verify_bundle(bundle)

    apply_bundle(bundle, target)

    assert (target / "tracked.txt").read_text(encoding="utf-8") == "after\n"
    assert (target / "new.txt").read_text(encoding="utf-8") == "brand-new\n"

    subprocess.run(["git", "-C", str(target), "status", "--short"], check=True)
