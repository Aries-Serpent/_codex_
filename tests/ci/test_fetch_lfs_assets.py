"""Bounded LFS tests: only tiny local objects and stubbed failures, no network."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.ci import fetch_lfs_assets as mod


def git(root: Path, *args: str) -> str:
    env = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1", GIT_TERMINAL_PROMPT="0")
    return subprocess.run(
        ["git", *args],
        cwd=root,
        env=env,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=20,
    ).stdout


@pytest.fixture
def lfs_repo(tmp_path):
    if not shutil.which("git-lfs"):
        pytest.skip("real fixture requires git-lfs")
    remote = tmp_path / "origin.git"
    source = tmp_path / "source"
    clone = tmp_path / "clone"
    git(tmp_path, "init", "--bare", str(remote))
    git(tmp_path, "init", str(source))
    git(source, "config", "user.email", "fixture@example.invalid")
    git(source, "config", "user.name", "Local fixture")
    git(source, "lfs", "install", "--local", "--skip-smudge")
    git(source, "lfs", "track", "*.bin")
    payloads = {
        "data/model with space.bin": b"tiny required model\n" * 4,
        "artifacts/other.bin": b"tiny second asset\n" * 4,
        "unrequested/third.bin": b"not requested\n" * 4,
    }
    for name, content in payloads.items():
        path = source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    git(source, "add", ".")
    git(source, "commit", "-m", "tiny local LFS fixture")
    git(source, "remote", "add", "origin", str(remote))
    git(source, "push", "origin", "HEAD")
    git(tmp_path, "clone", str(remote), str(clone))
    git(clone, "lfs", "install", "--local", "--skip-smudge")
    return clone, remote, payloads


def test_real_local_lfs_materializes_only_required_paths(lfs_repo):
    root, _, payloads = lfs_repo
    selected = ["data/model with space.bin", "artifacts/*.bin"]
    assets = mod.Fetcher(root, mod.Limits(bytes=4096, seconds=20)).fetch(selected)
    assert len(assets) == 2
    for asset in assets:
        assert (root / asset.path).read_bytes() == payloads[asset.path]
    assert (root / "unrequested/third.bin").read_text().startswith("version https://git-lfs")
    mod.Fetcher(root, mod.Limits(bytes=4096)).fetch(selected, verify_only=True)


def test_real_full_current_head_is_still_bounded(lfs_repo):
    root, _, payloads = lfs_repo
    assets = mod.Fetcher(root, mod.Limits(bytes=4096)).fetch([], full=True)
    assert {asset.path for asset in assets} == set(payloads)
    for asset in assets:
        assert (root / asset.path).read_bytes() == payloads[asset.path]


@pytest.mark.parametrize("limits", [mod.Limits(objects=1), mod.Limits(bytes=1)])
def test_real_fixture_budget_rejected_before_fetch(lfs_repo, limits, monkeypatch):
    root, _, _ = lfs_repo
    fetcher = mod.Fetcher(root, limits)
    calls = []
    original = fetcher.run

    def record(*args, **kwargs):
        calls.append(args)
        return original(*args, **kwargs)

    monkeypatch.setattr(fetcher, "run", record)
    with pytest.raises(mod.AssetError, match="budget"):
        fetcher.fetch(["data/*.bin", "artifacts/*.bin"])
    assert not any("fetch" in args for args in calls)


def test_real_fixture_required_missing_object_is_failure(lfs_repo):
    root, remote, _ = lfs_repo
    shutil.rmtree(remote / "lfs" / "objects")
    with pytest.raises(mod.AssetError, match="Git/LFS command failed"):
        mod.Fetcher(root, mod.Limits(seconds=15)).fetch(["data/*.bin"])


def test_verify_rejects_pointer_and_modified_materialization(lfs_repo):
    root, _, _ = lfs_repo
    with pytest.raises(mod.AssetError, match="pointer|size"):
        mod.Fetcher(root, mod.Limits()).fetch(["data/*.bin"], verify_only=True)
    mod.Fetcher(root, mod.Limits()).fetch(["data/*.bin"])
    path = root / "data/model with space.bin"
    path.write_bytes(b"x" * path.stat().st_size)
    with pytest.raises(mod.AssetError, match="hash mismatch"):
        mod.Fetcher(root, mod.Limits()).fetch(["data/*.bin"], verify_only=True)


@pytest.mark.parametrize(
    "pattern", ["*", "../data/*", "/data/*", "data/../*", "*.bin", "data/\nfile"]
)
def test_invalid_or_overbroad_intent_is_rejected(tmp_path, pattern):
    with pytest.raises(mod.AssetError):
        mod.Fetcher(tmp_path, mod.Limits()).safe_path(pattern, pattern=True)


def test_symlink_escape_is_rejected(tmp_path):
    (tmp_path / "data").symlink_to(tmp_path.parent)
    with pytest.raises(mod.AssetError, match="escape|symlink"):
        mod.Fetcher(tmp_path, mod.Limits()).safe_path("data/file")


def test_no_matching_required_asset_is_failure(lfs_repo):
    root, _, _ = lfs_repo
    with pytest.raises(mod.AssetError, match="matched no"):
        mod.Fetcher(root, mod.Limits()).fetch(["data/missing.bin"])


def test_retry_exhaustion_never_falls_back_or_checks_out(tmp_path, monkeypatch):
    fetcher = mod.Fetcher(tmp_path, mod.Limits(retries=2))
    monkeypatch.setattr(
        fetcher, "select", lambda *_: ("a" * 40, [mod.Asset("data/a", "b" * 64, 1)])
    )
    monkeypatch.setattr(fetcher, "auth_env", lambda: {})
    calls = []

    def fail(*args, **kwargs):
        calls.append(args)
        raise mod.AssetError("fake transport failure")

    monkeypatch.setattr(fetcher, "run", fail)
    with pytest.raises(mod.AssetError, match="fake transport"):
        fetcher.fetch(["data/a"])
    assert len(calls) == 2
    assert all("fetch" in call and "--all" not in call and "checkout" not in call for call in calls)
    assert all(call[-1] == "a" * 40 for call in calls)
    assert all("lfs.fetchrecentalways=false" in call for call in calls)


@pytest.mark.parametrize("seconds", [float("nan"), float("inf"), 0, -1, 601])
def test_nonfinite_or_unbounded_timeout_rejected(tmp_path, seconds):
    with pytest.raises(mod.AssetError, match="timeout"):
        mod.Fetcher(tmp_path, mod.Limits(seconds=seconds))


def test_total_timeout_terminates_subprocess(tmp_path, monkeypatch):
    original = subprocess.Popen

    def sleep_process(*args, **kwargs):
        return original([sys.executable, "-c", "import time; time.sleep(5)"], **kwargs)

    monkeypatch.setattr(mod.subprocess, "Popen", sleep_process)
    with pytest.raises(mod.AssetError, match="timeout"):
        mod.Fetcher(tmp_path, mod.Limits(seconds=0.05)).run("lfs", "version")


def test_cli_failure_writes_not_ready_and_full_needs_opt_in(tmp_path, monkeypatch, capsys):
    status = tmp_path / "status.json"
    monkeypatch.setattr(sys, "argv", ["fetch", "--mode", "full", "--status", str(status)])
    assert mod.main() == 1
    assert json.loads(status.read_text())["status"] == "not-ready"
    assert "explicit --allow-full" in capsys.readouterr().out


def test_none_mode_never_invokes_git(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["fetch", "--mode", "none"])
    monkeypatch.setattr(
        mod.subprocess, "Popen", lambda *_a, **_k: pytest.fail("no fetch authorized")
    )
    assert mod.main() == 0


def test_auth_token_rejected_for_untrusted_origin(tmp_path, monkeypatch):
    fetcher = mod.Fetcher(tmp_path, mod.Limits())
    monkeypatch.setenv("LFS_AUTH_TOKEN", "test-only-not-a-credential")
    monkeypatch.setattr(fetcher, "run", lambda *_: "https://example.invalid/repo.git")
    with pytest.raises(mod.AssetError, match="github.com"):
        fetcher.auth_env()
