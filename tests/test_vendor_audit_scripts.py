"""Tests for vendor audit shell wrappers."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_uv_lock(repo_root: Path, package_names: list[str]) -> None:
    entries = ",\n".join(
        f'    {{"name": "{name}", "version": "0.{idx}.0"}}'
        for idx, name in enumerate(package_names)
    )
    content = '{\n  "package": [\n' + entries + "\n  ]\n}\n"
    (repo_root / "uv.lock").write_text(content, encoding="utf-8")


def _run_audit(script_name: str, tmp_path: Path, extra_env: dict[str, str]) -> None:
    env = os.environ.copy()
    env.update(
        {
            "REPO_ROOT": str(tmp_path),
            "CODEX_VENDOR_MAX_PACKAGES": extra_env.get("CODEX_VENDOR_MAX_PACKAGES", "0"),
            "CODEX_VENDOR_MAX_SIZE_KB": extra_env.get("CODEX_VENDOR_MAX_SIZE_KB", "0"),
            "CODEX_FAIL_ON_VIOLATION": extra_env.get("CODEX_FAIL_ON_VIOLATION", "0"),
        }
    )
    env.update(extra_env)
    result = subprocess.run(
        ["bash", str(REPO_ROOT / "scripts" / script_name)],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"{script_name} failed with code {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def _load_cached_json(tmp_path: Path, filename: str) -> dict:
    cache_path = tmp_path / ".codex" / "cache" / filename
    return json.loads(cache_path.read_text(encoding="utf-8"))


@pytest.mark.usefixtures("tmp_path")
def test_vendor_audit_setup_sanitizes_policy_values(tmp_path: Path) -> None:
    """Setup audit should honour comment-stripped tunables and persist GPU lock matches."""

    _write_uv_lock(tmp_path, ["torch", "nvidia-cublas-cu12"])

    _run_audit(
        "vendor_audit_setup.sh",
        tmp_path,
        {
            "CODEX_OFFLINE": "1",
            "CODEX_AUDIT_BOOTSTRAP": "0",
            "CODEX_CPU_TRIALS": "1",
            "CODEX_CPU_TARGET_SECONDS": "0.05  # keep run fast",
            "CODEX_DISK_TRIALS": "1",
            "CODEX_DISK_BENCH_BYTES": "65536",
            "CODEX_NET_TRIALS": "1",
            "CODEX_NET_TEST_URLS": "https://speed.hetzner.de/100KB.bin  # inline note",
        },
    )

    data = _load_cached_json(tmp_path, "vendor_audit.setup.json")
    assert data["phase"] == "setup"
    assert data["policy"]["cpu_trials"] == 1
    assert data["policy"]["disk_trials"] == 1
    assert data["policy"]["disk_bytes"] == 65536
    assert data["policy"]["net_trials"] == 1
    assert data["policy"]["net_urls"] == ["https://speed.hetzner.de/100KB.bin"]
    assert data["policy"]["cpu_target_s"] == pytest.approx(0.05, rel=1e-3)
    assert "nvidia-cublas-cu12" in data["lock_scan_names"]
    assert data["system_caps"]["network"]["notes"] == "offline mode"


def test_vendor_audit_setup_respects_vendor_overrides(tmp_path: Path) -> None:
    """CODEX_VENDOR_AUDIT_* overrides should drive runtime tunables for setup audits."""

    _write_uv_lock(tmp_path, ["torch", "triton"])

    _run_audit(
        "vendor_audit_setup.sh",
        tmp_path,
        {
            "CODEX_OFFLINE": "0",
            "CODEX_AUDIT_BOOTSTRAP": "1",
            "CODEX_CPU_TRIALS": "5",
            "CODEX_CPU_BENCH_BUF_KB": "4096",
            "CODEX_DISK_TRIALS": "4",
            "CODEX_DISK_BENCH_BYTES": "262144",
            "CODEX_NET_TRIALS": "3",
            "CODEX_VENDOR_AUDIT_OFFLINE": "1",
            "CODEX_VENDOR_AUDIT_BOOTSTRAP": "0",
            "CODEX_VENDOR_AUDIT_CPU_TRIALS": "2",
            "CODEX_VENDOR_AUDIT_CPU_TARGET_SECONDS": "0.02",
            "CODEX_VENDOR_AUDIT_CPU_BUFFER_KB": "128",
            "CODEX_VENDOR_AUDIT_DISK_TRIALS": "1",
            "CODEX_VENDOR_AUDIT_DISK_BYTES": "65536",
            "CODEX_VENDOR_AUDIT_NET_TRIALS": "1",
            "CODEX_VENDOR_AUDIT_NET_URLS": "https://example.invalid/blob.bin",
        },
    )

    data = _load_cached_json(tmp_path, "vendor_audit.setup.json")
    assert data["policy"]["cpu_trials"] == 2
    assert data["policy"]["cpu_target_s"] == pytest.approx(0.02, rel=1e-3)
    assert data["policy"]["cpu_buf_kb"] == 128
    assert data["policy"]["disk_trials"] == 1
    assert data["policy"]["disk_bytes"] == 65536
    assert data["policy"]["net_trials"] == 1
    assert data["policy"]["net_urls"] == ["https://example.invalid/blob.bin"]
    assert data["system_caps"]["network"]["notes"] == "offline mode"
    assert not data["bootstrap_status"]["attempted"]


def test_vendor_audit_maintenance_overrides(tmp_path: Path) -> None:
    """Maintenance audit should also respect the integration override variables."""

    _write_uv_lock(tmp_path, ["torch", "nvidia-cufft-cu12"])

    _run_audit(
        "vendor_audit_maint.sh",
        tmp_path,
        {
            "CODEX_OFFLINE": "0",
            "CODEX_AUDIT_BOOTSTRAP": "1",
            "CODEX_CPU_TRIALS": "4",
            "CODEX_CPU_BENCH_BUF_KB": "4096",
            "CODEX_DISK_TRIALS": "3",
            "CODEX_DISK_BENCH_BYTES": "262144",
            "CODEX_NET_TRIALS": "2",
            "CODEX_VENDOR_AUDIT_OFFLINE": "1",
            "CODEX_VENDOR_AUDIT_BOOTSTRAP": "0",
            "CODEX_VENDOR_AUDIT_CPU_TRIALS": "3",
            "CODEX_VENDOR_AUDIT_CPU_TARGET_SECONDS": "0.015",
            "CODEX_VENDOR_AUDIT_CPU_BUFFER_KB": "192",
            "CODEX_VENDOR_AUDIT_DISK_TRIALS": "2",
            "CODEX_VENDOR_AUDIT_DISK_BYTES": "98304",
            "CODEX_VENDOR_AUDIT_NET_TRIALS": "1",
            "CODEX_VENDOR_AUDIT_NET_URLS": "https://example.invalid/maint.bin",
        },
    )

    data = _load_cached_json(tmp_path, "vendor_audit.maintenance.json")
    assert data["phase"] == "maintenance"
    assert data["policy"]["cpu_trials"] == 3
    assert data["policy"]["cpu_target_s"] == pytest.approx(0.015, rel=1e-3)
    assert data["policy"]["cpu_buf_kb"] == 192
    assert data["policy"]["disk_trials"] == 2
    assert data["policy"]["disk_bytes"] == 98304
    assert data["policy"]["net_trials"] == 1
    assert data["policy"]["net_urls"] == ["https://example.invalid/maint.bin"]
    assert data["system_caps"]["network"]["notes"] == "offline mode"
    assert not data["bootstrap_status"]["attempted"]
    assert "nvidia-cufft-cu12" in data["lock_scan_names"]
