#!/usr/bin/env python3
import json
import os
import platform
import shutil
import subprocess
import sys
import time


def log_warn(message: str) -> None:
    print(f"[WARN] {message}", file=sys.stderr)


def which(cmd):
    return shutil.which(cmd) or ""


def main():
    info = {
        "timestamp_utc": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "python": sys.version.replace("\n", " "),
        "platform": platform.platform(),
        "exe_paths": {"python": sys.executable, "pip": which("pip"), "git": which("git")},
        "env_flags": {
            "ACCELERATE_TEST": os.getenv("ACCELERATE_TEST", ""),
            "RUN_LORA_TESTS": os.getenv("RUN_LORA_TESTS", ""),
            "RUN_PERF_SMOKE": os.getenv("RUN_PERF_SMOKE", ""),
            "SKIP_OPTIONAL": os.getenv("SKIP_OPTIONAL", ""),
            "FAIL_ON_MISSING": os.getenv("FAIL_ON_MISSING", ""),
        },
        "limits": {},
        "pkgs_head": [],
    }
    try:
        import pkgutil

        info["top_level_modules"] = sorted({m.name for m in pkgutil.iter_modules()})[:50]
    except Exception as exc:
        log_warn(f"Failed to enumerate top-level modules: {exc}")
        info["top_level_modules"] = []

    # pip freeze head
    try:
        out = subprocess.check_output(
            [sys.executable, "-m", "pip", "freeze"], text=True, timeout=20
        )
        info["pkgs_head"] = out.strip().splitlines()[:50]
    except Exception as exc:
        log_warn(f"pip freeze snapshot failed: {exc}")

    # ulimit (platform-aware)
    if platform.system() != "Windows" and which("bash"):
        try:
            out = subprocess.check_output(["bash", "-lc", "ulimit -a"], text=True, timeout=5)
            info["limits"]["ulimit"] = out.strip()
        except Exception as e:
            log_warn(f"ulimit probe failed: {e}")
    else:
        print("[INFO] Skipping ulimit on non-Unix platform", file=sys.stderr)

    # write
    out_path = os.path.join("audit_artifacts", "agent_env.json")
    os.makedirs("audit_artifacts", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)
    print(f"[INFO] Agent env written to {out_path}")


if __name__ == "__main__":
    main()
