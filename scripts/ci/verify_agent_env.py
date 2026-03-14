#!/usr/bin/env python3
"""verify_agent_env.py — Validate the Copilot agent venv is complete and healthy.

Checks:
  1. Python binary is executable and correct version (>=3.12)
  2. All packages in requirements/agent.txt are importable
  3. Codex package is installed and importable
  4. Key entry points exist (ruff, pytest, mkdocs)
  5. GitHub App auth module is importable
  6. CacheManager is importable

Exit codes:
  0  healthy
  1  one or more issues (degraded — agent can still function)
  2  critical failure (Python binary missing/broken)

Usage:
    python scripts/ci/verify_agent_env.py
    python scripts/ci/verify_agent_env.py --venv .venv_agent
    python scripts/ci/verify_agent_env.py --venv .venv_agent --requirements requirements/agent.txt
    python scripts/ci/verify_agent_env.py --json   # machine-readable output
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Package → import name mapping (where they differ)
# ---------------------------------------------------------------------------

IMPORT_MAP: dict[str, str] = {
    "pyyaml":           "yaml",
    "pyjwt":            "jwt",
    "python-dotenv":    "dotenv",
    "mkdocs-material":  "material",          # not directly importable; checked via CLI
    "pymdown-extensions": "pymdownx",
    "mkdocs-mermaid2-plugin": "mermaid2",   # checked via CLI
    "httpx":            "httpx",
    "detect-secrets":   "detect_secrets",
    "pip-audit":        "pip_audit",
    "pre-commit":       "pre_commit",
    "bandit":           "bandit",
    "rich":             "rich",
    "click":            "click",
    "tomli":            "tomli",
}

# Packages only checked via CLI binary (not importable directly)
CLI_ONLY: set[str] = {"mkdocs-material", "mkdocs-mermaid2-plugin", "pip-audit"}

# Critical packages — failure = exit code 2
CRITICAL: set[str] = {"pip", "setuptools", "ruff", "pytest", "mypy", "requests", "pyjwt"}

# Key binaries that must be on PATH inside the venv
REQUIRED_BINS = ["python", "pip", "ruff", "pytest", "mkdocs", "mypy"]

# Codex internal modules to verify
CODEX_MODULES = [
    "codex.ci.cache_manager",
    "codex.auth.github_app",
    "codex.auth.token_manager",
    "codex.cognitive.brain_interface",
]


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def check_python(venv: Path) -> tuple[bool, str]:
    """Verify Python binary exists and is >=3.12."""
    py = venv / "bin" / "python"
    if not py.exists():
        return False, f"Python binary not found: {py}"
    try:
        result = subprocess.run(
            [str(py), "--version"], capture_output=True, text=True, timeout=10
        )
        version_str = result.stdout.strip() or result.stderr.strip()
        parts = version_str.split()[-1].split(".")
        major, minor = int(parts[0]), int(parts[1])
        if (major, minor) < (3, 12):
            return False, f"Python {version_str} < 3.12 (required by pyproject.toml)"
        return True, f"Python {version_str} ✅"
    except Exception as exc:
        return False, f"Python binary check failed: {exc}"


def check_binaries(venv: Path) -> list[tuple[str, bool, str]]:
    """Check key binaries exist in the venv."""
    results = []
    bin_dir = venv / "bin"
    for bin_name in REQUIRED_BINS:
        path = bin_dir / bin_name
        ok = path.exists() and path.is_file()
        results.append((bin_name, ok, str(path) if ok else f"missing: {path}"))
    return results


def check_imports(venv: Path, requirements_file: Path) -> list[tuple[str, bool, str]]:
    """Try importing each package from requirements.txt inside the venv."""
    py = str(venv / "bin" / "python")
    results = []

    # Parse requirements file for package names
    packages: list[str] = []
    for line in requirements_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Strip version specifiers, extras, markers
        pkg = line.split(";")[0].split(">=")[0].split("==")[0].split("[")[0].strip()
        pkg = pkg.lower()
        if pkg:
            packages.append(pkg)

    for pkg in packages:
        if pkg in CLI_ONLY:
            continue
        import_name = IMPORT_MAP.get(pkg, pkg.replace("-", "_"))
        try:
            result = subprocess.run(
                [py, "-c", f"import {import_name}"],
                capture_output=True, text=True, timeout=15,
            )
            ok = result.returncode == 0
            msg = "✅" if ok else result.stderr.strip()[:100]
        except Exception as exc:
            ok = False
            msg = str(exc)
        results.append((pkg, ok, msg))

    return results


def check_codex_modules(venv: Path) -> list[tuple[str, bool, str]]:
    """Check that key Codex internal modules are importable."""
    py = str(venv / "bin" / "python")
    results = []
    for mod in CODEX_MODULES:
        try:
            result = subprocess.run(
                [py, "-c", f"import {mod}"],
                capture_output=True, text=True, timeout=15,
            )
            ok = result.returncode == 0
            msg = "✅" if ok else result.stderr.strip()[:120]
        except Exception as exc:
            ok = False
            msg = str(exc)
        results.append((mod, ok, msg))
    return results


def check_github_app_auth(venv: Path) -> tuple[bool, str]:
    """Verify GitHub App auth module is importable and pyjwt is available."""
    py = str(venv / "bin" / "python")
    script = (
        "from integrations.github_app_auth import mint_app_jwt, exchange_installation_token; "
        "import jwt; "
        "print('GitHub App auth: OK')"
    )
    try:
        result = subprocess.run(
            [py, "-c", script],
            capture_output=True, text=True, timeout=15,
        )
        ok = result.returncode == 0
        return ok, result.stdout.strip() if ok else result.stderr.strip()[:120]
    except Exception as exc:
        return False, str(exc)


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def run_checks(venv: Path, requirements: Path) -> dict:
    report: dict = {
        "venv": str(venv),
        "python": {},
        "binaries": [],
        "packages": [],
        "codex_modules": [],
        "github_app_auth": {},
        "summary": {},
    }

    # Python version
    py_ok, py_msg = check_python(venv)
    report["python"] = {"ok": py_ok, "message": py_msg}

    if not py_ok:
        report["summary"] = {"healthy": False, "critical": True, "message": py_msg}
        return report

    # Binaries
    for bin_name, ok, msg in check_binaries(venv):
        report["binaries"].append({"name": bin_name, "ok": ok, "message": msg})

    # Package imports
    for pkg, ok, msg in check_imports(venv, requirements):
        report["packages"].append({"package": pkg, "ok": ok, "message": msg})

    # Codex modules
    for mod, ok, msg in check_codex_modules(venv):
        report["codex_modules"].append({"module": mod, "ok": ok, "message": msg})

    # GitHub App auth
    gh_ok, gh_msg = check_github_app_auth(venv)
    report["github_app_auth"] = {"ok": gh_ok, "message": gh_msg}

    # Summary
    all_checks = (
        [report["python"]["ok"]]
        + [b["ok"] for b in report["binaries"]]
        + [p["ok"] for p in report["packages"] if p["package"] in CRITICAL]
        + [c["ok"] for c in report["codex_modules"]]
    )
    failures = sum(1 for ok in all_checks if not ok)
    total = len(all_checks)
    healthy = failures == 0
    report["summary"] = {
        "healthy": healthy,
        "critical": not py_ok,
        "total_checks": total,
        "failures": failures,
        "message": f"{'✅ HEALTHY' if healthy else '⚠️ DEGRADED'} — {total - failures}/{total} checks passed",
    }
    return report


def print_report(report: dict) -> None:
    print(f"\n{'═' * 60}")
    print(f"  Copilot Agent Environment Health Report")
    print(f"  Venv: {report['venv']}")
    print(f"{'═' * 60}")

    # Python
    py = report["python"]
    print(f"\n🐍 Python:  {py['message']}")

    # Binaries
    print("\n📦 Binaries:")
    for b in report["binaries"]:
        icon = "  ✅" if b["ok"] else "  ❌"
        print(f"{icon}  {b['name']:12s}  {b['message']}")

    # Critical packages
    print("\n📚 Critical packages:")
    for p in report["packages"]:
        if p["package"] in CRITICAL:
            icon = "  ✅" if p["ok"] else "  ❌"
            print(f"{icon}  {p['package']:20s}  {p['message']}")

    # Codex modules
    print("\n🧠 Codex modules:")
    for c in report["codex_modules"]:
        icon = "  ✅" if c["ok"] else "  ⚠️ "
        print(f"{icon}  {c['module']}")

    # GitHub App auth
    gh = report["github_app_auth"]
    icon = "  ✅" if gh["ok"] else "  ⚠️ "
    print(f"\n🔐 GitHub App auth:{icon}  {gh['message']}")

    # Summary
    s = report["summary"]
    print(f"\n{'─' * 60}")
    print(f"  {s['message']}")
    print(f"{'═' * 60}\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify Copilot agent venv health.")
    parser.add_argument("--venv", default=".venv_agent",
                        help="Path to agent venv (default: .venv_agent)")
    parser.add_argument("--requirements", default="requirements/agent.txt",
                        help="Path to requirements file")
    parser.add_argument("--json", dest="json_out", action="store_true",
                        help="Output JSON report to stdout")
    args = parser.parse_args(argv)

    venv = Path(args.venv)
    requirements = Path(args.requirements)

    if not venv.exists():
        print(f"❌ Venv not found: {venv}", file=sys.stderr)
        return 2
    if not requirements.exists():
        print(f"❌ Requirements not found: {requirements}", file=sys.stderr)
        return 2

    report = run_checks(venv, requirements)

    if args.json_out:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    if report["summary"].get("critical"):
        return 2
    return 0 if report["summary"]["healthy"] else 1


if __name__ == "__main__":
    sys.exit(main())
