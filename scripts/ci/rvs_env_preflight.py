#!/usr/bin/env python3
"""
RVS Environment Pre-Flight Validator
=====================================
Validates that the Python environment contains every package required by the
Resilient Validation Suite before tests run.

Usage
-----
  # Report-only (no installs) — used by setup-python-cached action step 8
  python scripts/ci/rvs_env_preflight.py --report

  # Check and auto-install any missing packages
  python scripts/ci/rvs_env_preflight.py --install

  # Given a CI failure report JSON, start the correct env patch
  python scripts/ci/rvs_env_preflight.py --from-failure /tmp/rvs_report.json

  # Write machine-readable env manifest for checkpoint/resume
  python scripts/ci/rvs_env_preflight.py --report --json /tmp/env_manifest.json

Exit codes
----------
  0  All required packages present (or installed successfully with --install)
  1  One or more packages missing (without --install)
  2  Install attempted but failed for at least one package
"""

from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import logging
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Package inventory — every group required for a green RVS run
# ---------------------------------------------------------------------------
PACKAGE_GROUPS: dict[str, list[tuple[str, str]]] = {
    # (import_name, pypi_name) pairs
    "pytest_plugins": [
        ("pytest", "pytest>=9.0.3,<10.0.0"),
        ("pytest_timeout", "pytest-timeout>=2.2.0,<3.0.0"),
        ("pytest_xdist", "pytest-xdist>=3.5.0,<4.0.0"),
        ("pytest_cov", "pytest-cov>=4.1.0,<8.0.0"),
        ("pytest_asyncio", "pytest-asyncio>=1.4.0,<2.0.0"),
        ("pytest_mock", "pytest-mock>=3.15.1,<4.0.0"),
        ("pytest_randomly", "pytest-randomly>=3.15"),
        ("pytest_rerunfailures", "pytest-rerunfailures>=16.6"),
    ],
    "core": [
        ("pydantic", "pydantic>=2.4"),
        ("pydantic_settings", "pydantic-settings>=2.2"),
        ("yaml", "PyYAML>=6.0"),
        ("omegaconf", "omegaconf>=2.3"),
        ("jsonschema", "jsonschema>=4.0"),
    ],
    "ml": [
        ("torch", "torch>=2.6.0"),
        ("transformers", "transformers>=5.16.1,<6"),
        ("datasets", "datasets>=5.0.0,<6"),
        ("peft", "peft>=0.20.0,<1"),
        ("accelerate", "accelerate>=1.14.0,<2"),
        ("sentencepiece", "sentencepiece>=0.2.2"),
    ],
    "analysis": [
        ("libcst", "libcst>=1.0"),
        ("sqlparse", "sqlparse>=0.5.0"),
    ],
    "numeric": [
        ("numpy", "numpy>=2.5.2,<3"),
        ("scipy", "scipy>=1.18.1,<2"),
        ("mlflow", "mlflow>=2.22.4"),
    ],
    "infra": [
        ("psutil", "psutil>=5.9"),
        ("hydra", "hydra-core>=1.3"),
    ],
}

# Packages that are optional (informational only, not failures)
OPTIONAL_PACKAGES: frozenset[str] = frozenset(
    {
        "pynvml",   # GPU monitoring — not available on CPU-only runners
        "wandb",    # Experiment tracking — optional telemetry
        "mlflow",   # Large package — optional perf extra
        "scipy",    # Only needed by a subset of tests
        "hydra",    # Only needed by Hydra-backed CLI tests
        "sentencepiece",  # Only needed by tokenizer tests
    }
)


@dataclass
class PackageStatus:
    import_name: str
    pypi_spec: str
    installed: bool
    version: str | None
    optional: bool

    @property
    def status_icon(self) -> str:
        if self.installed:
            return "✅"
        return "⚠️ " if self.optional else "❌"

    def to_dict(self) -> dict[str, Any]:
        return {
            "import_name": self.import_name,
            "pypi_spec": self.pypi_spec,
            "installed": self.installed,
            "version": self.version,
            "optional": self.optional,
        }


@dataclass
class EnvManifest:
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    python_version: str = field(
        default_factory=lambda: sys.version.split()[0]
    )
    python_executable: str = field(default_factory=lambda: sys.executable)
    platform: str = field(default_factory=lambda: sys.platform)
    groups: dict[str, list[PackageStatus]] = field(default_factory=dict)
    missing_required: list[str] = field(default_factory=list)
    missing_optional: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "python_version": self.python_version,
            "python_executable": self.python_executable,
            "platform": self.platform,
            "groups": {
                g: [s.to_dict() for s in statuses]
                for g, statuses in self.groups.items()
            },
            "missing_required": self.missing_required,
            "missing_optional": self.missing_optional,
            "summary": {
                "total_required": sum(
                    1
                    for ss in self.groups.values()
                    for s in ss
                    if not s.optional
                ),
                "installed_required": sum(
                    1
                    for ss in self.groups.values()
                    for s in ss
                    if not s.optional and s.installed
                ),
                "missing_required_count": len(self.missing_required),
                "missing_optional_count": len(self.missing_optional),
            },
        }


def _get_version(import_name: str) -> str | None:
    """Return installed version or None."""
    try:
        return importlib.metadata.version(import_name.replace("_", "-"))
    except importlib.metadata.PackageNotFoundError:
        logger.debug("Suppressed exception in handler", exc_info=True)
    try:
        return importlib.metadata.version(import_name)
    except importlib.metadata.PackageNotFoundError:
        logger.debug("Suppressed exception in handler", exc_info=True)
    # Fall back to checking importability (for namespace packages)
    if importlib.util.find_spec(import_name) is not None:
        return "installed (no metadata)"
    return None


def audit_environment() -> EnvManifest:
    """Scan the current environment and return a full manifest."""
    manifest = EnvManifest()

    for group_name, packages in PACKAGE_GROUPS.items():
        statuses: list[PackageStatus] = []
        for import_name, pypi_spec in packages:
            version = _get_version(import_name)
            optional = import_name in OPTIONAL_PACKAGES
            status = PackageStatus(
                import_name=import_name,
                pypi_spec=pypi_spec,
                installed=version is not None,
                version=version,
                optional=optional,
            )
            statuses.append(status)
            if not status.installed:
                if optional:
                    manifest.missing_optional.append(import_name)
                else:
                    manifest.missing_required.append(import_name)
        manifest.groups[group_name] = statuses

    return manifest


def print_report(manifest: EnvManifest) -> None:
    """Print a human-readable env report."""
    sep = "─" * 72
    print(sep)
    print("  RVS Environment Pre-Flight Report")
    print(f"  Python {manifest.python_version}  |  {manifest.platform}")
    print(f"  {manifest.timestamp}")
    print(sep)

    for group_name, statuses in manifest.groups.items():
        print(f"\n  [{group_name.upper()}]")
        for s in statuses:
            ver_str = f"  ({s.version})" if s.version else ""
            print(f"    {s.status_icon}  {s.import_name:<28} {ver_str}")

    m = manifest.to_dict()["summary"]
    print(f"\n  Summary: {m['installed_required']}/{m['total_required']} required packages installed")
    if manifest.missing_required:
        print(f"  ❌ MISSING REQUIRED : {', '.join(manifest.missing_required)}")
    if manifest.missing_optional:
        print(f"  ⚠️  Missing optional : {', '.join(manifest.missing_optional)}")
    if not manifest.missing_required:
        print("  ✅ All required packages present — RVS env is READY")
    print(sep)


def install_missing(manifest: EnvManifest, pip_cache: str | None = None) -> int:
    """
    Install missing required packages.

    Returns the number of packages that failed to install.
    """
    if not manifest.missing_required:
        print("Nothing to install — all required packages present.")
        return 0

    # Build the pip install spec list
    specs: list[str] = []
    for statuses in manifest.groups.values():
        for s in statuses:
            if not s.installed and not s.optional:
                specs.append(s.pypi_spec)

    print(f"Installing {len(specs)} missing required package(s)...")
    cmd = [sys.executable, "-m", "pip", "install"]
    if pip_cache:
        cmd += ["--cache-dir", pip_cache]
    cmd += ["--quiet"] + specs

    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"❌ pip install failed (exit {result.returncode})")
        return len(specs)

    print("✅ Installation complete")
    return 0


def from_failure_report(report_path: str) -> int:
    """
    Parse a structured RVS failure report (JSON produced by rvs_preflight.py)
    and install any packages that were missing at test time.

    Returns 0 if the env is fixed, non-zero otherwise.
    """
    path = Path(report_path)
    if not path.exists():
        print(f"❌ Failure report not found: {report_path}", file=sys.stderr)
        return 1

    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"❌ Cannot parse failure report: {exc}", file=sys.stderr)
        return 1

    print(f"Loaded failure report: {report_path}")
    print(f"  status       : {report.get('status', 'unknown')}")
    print(f"  total issues : {report.get('total_issues', '?')}")
    print(f"  auto-fixable : {report.get('auto_fixable', '?')}")

    # Run a fresh env audit and install anything missing
    manifest = audit_environment()
    if manifest.missing_required:
        print(f"\nInstalling missing required packages: {manifest.missing_required}")
        failures = install_missing(manifest)
        if failures:
            return 2
    else:
        print("✅ All required packages already present")

    # Re-audit and write refreshed manifest alongside the failure report
    refreshed = audit_environment()
    out_path = path.parent / "env_manifest_post_fix.json"
    out_path.write_text(
        json.dumps(refreshed.to_dict(), indent=2), encoding="utf-8"
    )
    print(f"Refreshed env manifest written to: {out_path}")
    return 0 if not refreshed.missing_required else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="RVS environment pre-flight validator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Print human-readable env report (default when no action given)",
    )
    parser.add_argument(
        "--json",
        metavar="PATH",
        help="Write machine-readable JSON env manifest to PATH",
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Auto-install any missing required packages",
    )
    parser.add_argument(
        "--from-failure",
        metavar="REPORT_JSON",
        help="Parse an RVS failure report JSON and patch the env",
    )
    parser.add_argument(
        "--pip-cache",
        metavar="DIR",
        default=None,
        help="pip download cache directory (passed as --cache-dir to pip)",
    )
    args = parser.parse_args(argv)

    # -- from-failure mode supersedes everything else ---------------------
    if args.from_failure:
        return from_failure_report(args.from_failure)

    # -- standard audit ---------------------------------------------------
    manifest = audit_environment()

    if args.report or not (args.install or args.json):
        print_report(manifest)

    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(manifest.to_dict(), indent=2), encoding="utf-8")
        print(f"Env manifest written to: {out}")

    if args.install and manifest.missing_required:
        failures = install_missing(manifest, pip_cache=args.pip_cache)
        if failures:
            return 2
        # Re-audit after install
        manifest = audit_environment()
        if args.report:
            print("\n=== Post-install state ===")
            print_report(manifest)

    # Exit 1 when required packages are still missing
    return 1 if manifest.missing_required else 0


if __name__ == "__main__":
    sys.exit(main())
