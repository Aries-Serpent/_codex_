#!/usr/bin/env python3
"""Read-only probe for Copilot agent sandbox prerequisites."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

COPILOT_SETTING = "github.copilot.chat.cli.sandbox.enabled"


def _strip_json_comments(text: str) -> str:
    text = "".join(
        line if not line.lstrip().startswith("//") else ""
        for line in text.splitlines(keepends=True)
    )
    return text


def read_workspace_sandbox_setting(repo_root: Path) -> str:
    settings_path = repo_root / ".vscode" / "settings.json"
    try:
        text = _strip_json_comments(settings_path.read_text(encoding="utf-8"))
        settings = json.loads(text)
        value = settings.get(COPILOT_SETTING)
        if value in {"off", "on", "allowNetwork"}:
            return value
    except (OSError, json.JSONDecodeError):
        pass
    return "unknown"


def probe_bwrap() -> dict[str, Any]:
    executable = shutil.which("bwrap")
    if executable is None:
        return {"available": False, "namespace_capable": False, "reason": "bwrap-missing"}

    try:
        proc = subprocess.run(
            [executable, "--ro-bind", "/", "/", "sh", "-c", "echo sandbox-smoke-ok"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "available": True,
            "namespace_capable": False,
            "reason": type(exc).__name__.lower(),
        }

    return {
        "available": True,
        "namespace_capable": proc.returncode == 0,
        "reason": "namespace-capable" if proc.returncode == 0 else "namespace-denied",
    }


def _read_proc_status() -> dict[str, Any]:
    status: dict[str, Any] = {}
    status_path = Path("/proc/self/status")
    try:
        for line in status_path.read_text(encoding="utf-8").splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            if key in {"CapEff", "NoNewPrivs", "Seccomp", "Seccomp_filters"}:
                status[key] = value.strip()
    except OSError:
        pass

    apparmor_path = Path("/proc/self/attr/current")
    try:
        status["AppArmor"] = apparmor_path.read_text(encoding="utf-8").strip()
    except OSError:
        status["AppArmor"] = "unknown"

    return status


def _read_namespace_sysctls() -> dict[str, Any]:
    sysctls: dict[str, Any] = {}
    for name in ("unprivileged_userns_clone", "max_user_namespaces"):
        path = Path("/proc/sys/kernel") / name
        try:
            sysctls[name] = int(path.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            sysctls[name] = None
    return sysctls


def probe_unshare() -> dict[str, Any]:
    executable = shutil.which("unshare")
    if executable is None:
        return {"available": False, "namespace_capable": False, "reason": "unshare-missing"}

    try:
        proc = subprocess.run(
            [executable, "-Ur", "sh", "-c", "echo userns-smoke-ok"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "available": True,
            "namespace_capable": False,
            "reason": type(exc).__name__.lower(),
        }

    return {
        "available": True,
        "namespace_capable": proc.returncode == 0,
        "reason": "namespace-capable" if proc.returncode == 0 else "namespace-denied",
    }


def build_probe(repo_root: Path) -> dict[str, Any]:
    setting = read_workspace_sandbox_setting(repo_root)
    bwrap = probe_bwrap()
    unshare = probe_unshare()
    sandbox_capable = bool(bwrap["namespace_capable"] or unshare["namespace_capable"])

    if not sandbox_capable:
        recommended = "off"
    elif setting == "allowNetwork":
        recommended = "allowNetwork"
    else:
        recommended = "on"

    return {
        "sandbox_capable": sandbox_capable,
        "configured_setting": setting,
        "recommended_setting": recommended,
        "bwrap": bwrap,
        "unshare": unshare,
        "kernel_container": {
            **_read_proc_status(),
            "sysctls": _read_namespace_sysctls(),
            "containerized": os.path.exists("/.dockerenv"),
        },
    }


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    print(json.dumps(build_probe(repo_root), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
