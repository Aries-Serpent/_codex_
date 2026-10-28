"""Exercise bounded native output and environment trust independently of Git size."""

from __future__ import annotations

import builtins
import os
import subprocess
import sys

import pytest

from codex.institutional import core, git_capture, storage


def command(script):
    return [sys.executable, "-I", "-c", script]


def test_capture_exact_budget_and_stderr_accounting(monkeypatch):
    monkeypatch.setattr(git_capture, "MAX_GIT_BYTES", 128)
    output = git_capture.capture(command("import os; os.write(1,b'x'*64); os.write(2,b'e'*64)"), {})
    assert output == b"x" * 64
    with pytest.raises(git_capture.CaptureLimit, match="OUTPUT_LIMIT"):
        git_capture.capture(command("import os; os.write(2,b'e'*129)"), {})


def test_capture_terminates_output_flood_and_timeout(monkeypatch):
    monkeypatch.setattr(git_capture, "MAX_GIT_BYTES", 1024)
    with pytest.raises(git_capture.CaptureLimit, match="OUTPUT_LIMIT"):
        git_capture.capture(command("import os\nwhile True: os.write(1,b'x'*4096)"), {})
    monkeypatch.setattr(git_capture, "GIT_TIMEOUT", 0.05)
    with pytest.raises(git_capture.CaptureLimit, match="TIMEOUT"):
        git_capture.capture(command("import time; time.sleep(5)"), {})


def test_nonzero_and_missing_executable():
    with pytest.raises(subprocess.CalledProcessError):
        git_capture.capture(command("raise SystemExit(1)"), {})
    with pytest.raises(OSError):
        git_capture.capture(["/nonexistent/institutional-git"], {})


def test_resource_failures_never_fallback_to_filesystem(tmp_path, monkeypatch):
    def blocked(*args, **kwargs):
        raise git_capture.CaptureLimit("GIT_OUTPUT_LIMIT")

    monkeypatch.setattr(core, "capture", blocked)
    with pytest.raises(core.Rejected, match="BLOCKED_RESOURCE_LIMIT") as error:
        core.inventory(tmp_path)
    assert error.value.code == 4


def test_environment_does_not_adopt_target_config_or_loader_hooks(tmp_path, monkeypatch):
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "core.fsmonitor")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", "/untrusted")
    monkeypatch.setenv("GIT_DIR", "/other")
    monkeypatch.setenv("LD_PRELOAD", "/untrusted")

    def observe(command, env):
        assert (
            not {
                "GIT_CONFIG_COUNT",
                "GIT_CONFIG_KEY_0",
                "GIT_CONFIG_VALUE_0",
                "GIT_DIR",
                "LD_PRELOAD",
            }
            & env.keys()
        )
        assert env["GIT_CONFIG_NOSYSTEM"] == "1"
        assert env["GIT_CONFIG_GLOBAL"] == os.devnull
        return b" path with trailing space \n"

    monkeypatch.setattr(core, "capture", observe)
    assert core.git(tmp_path, "anything") == " path with trailing space "


def test_unsupported_locking_rejects_before_namespace_mutation(tmp_path, monkeypatch):
    value = core.candidate(tmp_path, "fixture")
    preview = storage.plan(tmp_path, value)
    original = builtins.__import__

    def without_locking(name, *args, **kwargs):
        if name == "fcntl":
            raise ImportError("simulated unsupported locking")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", without_locking)
    with pytest.raises(core.Rejected, match="LOCKING_UNSUPPORTED") as error:
        storage.apply(tmp_path, value, preview)
    assert error.value.code == 6
    assert not (tmp_path / core.NAMESPACE).exists()
