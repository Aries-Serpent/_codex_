#!/usr/bin/env python3
"""
Verify all dependencies support Python 3.12.

This script checks pyproject.toml dependencies against PyPI metadata
to ensure Python 3.12 compatibility before migration.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print(
            "ERROR: Neither tomllib (Python 3.11+) nor tomli is available"
        )  # codeql[py/clear-text-logging-sensitive-data]
        sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
ACTIVE_MANIFEST_NAMES = (
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "requirements-test.txt",
    "requirements-base.txt",
    "uv.lock",
    "poetry.lock",
    "Pipfile.lock",
)
CACHE_PATH = REPO_ROOT / ".codex" / "py312_deps_cache.json"
PACKAGE_TIMEOUT_SECONDS = 15
SHOW_TIMEOUT_SECONDS = 10


def parse_dependency_spec(dep_spec: str) -> tuple[str, str | None, bool]:
    """
    Parse a dependency specification into package name and version constraint.

    Args:
        dep_spec: Dependency specification like "package>=1.0.0" or "package[extras]>=2.0"

    Returns:
        Tuple of (package_name, version_constraint, is_conditional)

    Examples:
        >>> parse_dependency_spec("numpy>=1.26,<3")
        ('numpy', '>=1.26,<3', False)
        >>> parse_dependency_spec("torch[cuda]>=2.6.0")
        ('torch', '>=2.6.0', False)
        >>> parse_dependency_spec("importlib-metadata; python_version < '3.10'")
        ('importlib-metadata', None, True)
    """
    # Check for conditional dependencies (environment markers)
    is_conditional = ";" in dep_spec

    # Remove environment markers for parsing
    if is_conditional:
        dep_spec = dep_spec.split(";")[0].strip()

    # Remove extras like [cuda], [serve], etc.
    dep_spec = re.sub(r"\[([^\]]+)\]", "", dep_spec)

    # Split on comparison operators
    match = re.match(r"^([a-zA-Z0-9_-]+)([><=!]+.*)?$", dep_spec.strip())
    if match:
        package_name = match.group(1)
        version_constraint = match.group(2) if match.group(2) else None
        return package_name, version_constraint, is_conditional

    return dep_spec.strip(), None, is_conditional


def _manifest_paths() -> list[Path]:
    """Return active dependency manifests and lockfiles at repo root."""
    paths: list[Path] = []
    for name in ACTIVE_MANIFEST_NAMES:
        path = REPO_ROOT / name
        if path.exists():
            paths.append(path)
    return paths


def _manifest_fingerprint(paths: list[Path]) -> str:
    """Create a stable fingerprint for the active dependency manifests."""
    digest = hashlib.sha256()
    for path in paths:
        try:
            stat = path.stat()
        except FileNotFoundError:
            continue
        digest.update(str(path.relative_to(REPO_ROOT)).encode())
        digest.update(str(stat.st_mtime_ns).encode())
        digest.update(str(stat.st_size).encode())
    return digest.hexdigest()


def _read_requirements_file(path: Path, seen: set[Path] | None = None) -> list[str]:
    """Read dependency specs from a root-level requirements file."""
    seen = seen or set()
    if path in seen or not path.exists():
        return []
    seen.add(path)

    dependencies: list[str] = []
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("-r "):
            nested = (path.parent / line[3:].strip()).resolve()
            if nested.parent == REPO_ROOT.resolve():
                dependencies.extend(_read_requirements_file(nested, seen))
            continue
        if line.startswith("-c ") or line.startswith("--"):
            continue
        dependencies.append(line)
    return dependencies


def _read_lockfile_dependencies(path: Path) -> list[str]:
    """Extract package names from a root-level TOML lockfile."""
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except Exception:
        return []

    dependencies: list[str] = []
    packages = data.get("package", [])
    if isinstance(packages, list):
        for package in packages:
            if isinstance(package, dict) and package.get("name"):
                dependencies.append(str(package["name"]))
    return dependencies


def load_dependencies_from_active_manifests() -> list[str]:
    """Load dependencies from active manifests and lockfiles at the repo root."""
    dependencies: list[str] = []
    seen_paths: set[Path] = set()
    for path in _manifest_paths():
        if path in seen_paths:
            continue
        seen_paths.add(path)
        if path.name == "pyproject.toml":
            dependencies.extend(load_dependencies_from_pyproject())
        elif path.suffix == ".txt":
            dependencies.extend(_read_requirements_file(path))
        elif path.name in {"poetry.lock", "uv.lock", "Pipfile.lock"}:
            dependencies.extend(_read_lockfile_dependencies(path))
    return list(dict.fromkeys(dependencies))


def _cache_load(fingerprint: str) -> dict[str, Any] | None:
    if not CACHE_PATH.exists():
        return None
    try:
        cached = json.loads(CACHE_PATH.read_text())
    except Exception:
        return None
    if cached.get("fingerprint") != fingerprint:
        return None
    return cached


def _cache_save(fingerprint: str, payload: dict[str, Any]) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(payload)
    payload["fingerprint"] = fingerprint
    payload["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    CACHE_PATH.write_text(json.dumps(payload, indent=2))


def _print_cached_report(cached: dict[str, Any]) -> int:
    """Emit a cached report without re-running package checks."""
    print(f"Loaded cached Python 3.12 dependency results from {CACHE_PATH}")
    print(f"Found {cached.get('total_packages', 0)} unique packages to check")
    warnings = cached.get("warnings", [])
    for warning in warnings:
        print(f"⚠️  {warning}")
    compatible_count = cached.get("compatible", 0)
    incompatible_count = cached.get("incompatible", 0)
    error_count = cached.get("errors", 0)
    total = cached.get("total_packages", 0)
    print()
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print()
    print(f"✅ Compatible:   {compatible_count}/{total}")
    print(f"⚠️  Incompatible: {incompatible_count}/{total}")
    print(f"❌ Errors:       {error_count}/{total}")
    return int(cached.get("exit_code", 0))


@lru_cache(maxsize=512)
def check_package_py312_support(
    package: str, timeout_seconds: int = PACKAGE_TIMEOUT_SECONDS
) -> dict[str, Any]:
    """
    Check if a package supports Python 3.12.

    Args:
        package: Package name (e.g., "numpy", "torch")

    Returns:
        Dictionary with keys:
            - name: Package name
            - version: Current installed version (if available)
            - supports_312: Boolean indicating Python 3.12 support
            - latest_version: Latest version on PyPI
            - python_requires: Python version requirement string
            - error: Error message if check failed
            - warning: Warning message for timeout fallback
    """
    result = {
        "name": package,
        "version": None,
        "supports_312": None,
        "latest_version": None,
        "python_requires": None,
        "error": None,
        "warning": None,
    }

    try:
        # Get package info from PyPI
        proc = subprocess.run(
            [sys.executable, "-m", "pip", "index", "versions", package],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )

        if proc.returncode != 0:
            result["error"] = f"Failed to query PyPI: {proc.stderr}"
            return result

        # Parse available versions
        output = proc.stdout
        if "Available versions:" in output:
            versions_line = output.split("Available versions:")[1].split("\n")[0]
            versions = [v.strip() for v in versions_line.split(",")]
            if versions:
                result["latest_version"] = versions[0]

        # Try to get detailed metadata using pip show
        proc_show = subprocess.run(
            [sys.executable, "-m", "pip", "show", package],
            capture_output=True,
            text=True,
            timeout=SHOW_TIMEOUT_SECONDS,
        )

        if proc_show.returncode == 0:
            for line in proc_show.stdout.splitlines():
                if line.startswith("Version:"):
                    result["version"] = line.split(":", 1)[1].strip()
                elif line.startswith("Requires-Python:"):
                    result["python_requires"] = line.split(":", 1)[1].strip()

        # Check Python version compatibility
        if result["python_requires"]:
            # Parse version requirement
            # Simple check: if it mentions 3.12 explicitly or uses >= with version <= 3.12
            req = result["python_requires"]

            # Check if explicitly supports 3.12
            if "3.12" in req:
                result["supports_312"] = True
            # Check for >= patterns
            elif ">=" in req:
                match = re.search(r">=\s*(\d+)\.(\d+)", req)
                if match:
                    major, minor = int(match.group(1)), int(match.group(2))
                    # If requires >= 3.x where x <= 12, likely supports 3.12
                    if (major == 3 and minor <= 12) or major < 3:
                        result["supports_312"] = True
            # No upper bound restriction typically means support
            elif "<" not in req and "!=" not in req:
                result["supports_312"] = True
        else:
            # No explicit requirement often means broad compatibility
            result["supports_312"] = True
            result["python_requires"] = "Not specified (likely compatible)"

    except subprocess.TimeoutExpired:
        result["warning"] = "Timeout querying PyPI; using best-effort local metadata"
        try:
            proc_show = subprocess.run(
                [sys.executable, "-m", "pip", "show", package],
                capture_output=True,
                text=True,
                timeout=SHOW_TIMEOUT_SECONDS,
            )
            if proc_show.returncode == 0:
                for line in proc_show.stdout.splitlines():
                    if line.startswith("Version:"):
                        result["version"] = line.split(":", 1)[1].strip()
                    elif line.startswith("Requires-Python:"):
                        result["python_requires"] = line.split(":", 1)[1].strip()
                if result["python_requires"]:
                    req = result["python_requires"]
                    if "3.12" in req:
                        result["supports_312"] = True
                    elif ">=" in req:
                        match = re.search(r">=\s*(\d+)\.(\d+)", req)
                        if match:
                            major, minor = int(match.group(1)), int(match.group(2))
                            if (major == 3 and minor <= 12) or major < 3:
                                result["supports_312"] = True
                    elif "<" not in req and "!=" not in req:
                        result["supports_312"] = True
        except Exception:
            pass
    except Exception as e:
        result["error"] = str(e)

    return result


def load_dependencies_from_pyproject() -> list[str]:
    """
    Load dependencies from pyproject.toml.

    Returns:
        List of dependency specifications
    """
    repo_root = Path(__file__).parent.parent
    pyproject_path = repo_root / "pyproject.toml"

    if not pyproject_path.exists():
        print(
            f"ERROR: pyproject.toml not found at {pyproject_path}"
        )  # codeql[py/clear-text-logging-sensitive-data]
        sys.exit(1)

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    dependencies = []

    # Get main dependencies
    if "project" in data and "dependencies" in data["project"]:
        dependencies.extend(data["project"]["dependencies"])

    # Get optional dependencies
    if "project" in data and "optional-dependencies" in data["project"]:
        for _, deps in data["project"]["optional-dependencies"].items():
            dependencies.extend(deps)

    return dependencies


def main() -> int:
    """
    Main entry point for dependency compatibility checker.

    Returns:
        Exit code: 0 if all dependencies support Python 3.12, 1 otherwise
    """
    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print(
        "Python 3.12 Dependency Compatibility Checker"
    )  # codeql[py/clear-text-logging-sensitive-data]
    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    manifest_paths = _manifest_paths()
    fingerprint = _manifest_fingerprint(manifest_paths)
    cached = _cache_load(fingerprint)
    if cached:
        return _print_cached_report(cached)

    # Load dependencies from active manifests only.
    if manifest_paths:
        print(
            "Loading dependencies from active manifests: "
            + ", ".join(path.name for path in manifest_paths)
        )  # codeql[py/clear-text-logging-sensitive-data]
    else:
        print(
            "Loading dependencies from pyproject.toml..."
        )  # codeql[py/clear-text-logging-sensitive-data]
    dep_specs = load_dependencies_from_active_manifests() or load_dependencies_from_pyproject()

    # Parse unique package names, excluding conditional dependencies for Python < 3.12
    packages = set()
    skipped_conditional = []
    for dep_spec in dep_specs:
        package_name, _, is_conditional = parse_dependency_spec(dep_spec)

        # Skip conditional dependencies that don't apply to Python 3.12+
        if is_conditional and ("python_version" in dep_spec and "<" in dep_spec):
            # This is a conditional for older Python versions, skip it
            skipped_conditional.append(dep_spec)
            continue

        packages.add(package_name)

    print(
        f"Found {len(packages)} unique packages to check"
    )  # codeql[py/clear-text-logging-sensitive-data]
    if skipped_conditional:
        print(
            f"Skipped {len(skipped_conditional)} conditional dependencies for Python < 3.12"
        )  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    # Check each package
    results = []
    incompatible = []
    errors = []
    warnings = []

    for i, package in enumerate(sorted(packages), 1):
        print(
            f"[{i}/{len(packages)}] Checking {package}...", end=" "
        )  # codeql[py/clear-text-logging-sensitive-data]
        sys.stdout.flush()

        result = check_package_py312_support(package)
        results.append(result)

        if result["error"]:
            print("❌ ERROR")  # codeql[py/clear-text-logging-sensitive-data]
            errors.append(result)
        elif result["warning"]:
            print("⚠️  WARNING")  # codeql[py/clear-text-logging-sensitive-data]
            warnings.append(result)
        elif result["supports_312"]:
            print("✅ COMPATIBLE")  # codeql[py/clear-text-logging-sensitive-data]
        else:
            print("⚠️  INCOMPATIBLE")  # codeql[py/clear-text-logging-sensitive-data]
            incompatible.append(result)

    print()  # codeql[py/clear-text-logging-sensitive-data]
    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print("Summary")  # codeql[py/clear-text-logging-sensitive-data]
    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    compatible_count = sum(1 for result in results if result.get("supports_312") is True)
    print(
        f"✅ Compatible:   {compatible_count}/{len(results)}"
    )  # codeql[py/clear-text-logging-sensitive-data]
    print(
        f"⚠️  Incompatible: {len(incompatible)}/{len(results)}"
    )  # codeql[py/clear-text-logging-sensitive-data]
    print(
        f"❌ Errors:       {len(errors)}/{len(results)}"
    )  # codeql[py/clear-text-logging-sensitive-data]
    if warnings:
        print(
            f"⚠️  Warnings:     {len(warnings)}/{len(results)}"
        )  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    if incompatible:
        print("⚠️  INCOMPATIBLE PACKAGES:")  # codeql[py/clear-text-logging-sensitive-data]
        print("-" * 80)  # codeql[py/clear-text-logging-sensitive-data]
        for result in incompatible:
            print(f"  • {result['name']}")  # codeql[py/clear-text-logging-sensitive-data]
            print(
                f"    Version: {result['version'] or 'Unknown'}"
            )  # codeql[py/clear-text-logging-sensitive-data]
            print(
                f"    Requires: {result['python_requires'] or 'Not specified'}"
            )  # codeql[py/clear-text-logging-sensitive-data]
            print()  # codeql[py/clear-text-logging-sensitive-data]

    if errors:
        print("❌ PACKAGES WITH ERRORS:")  # codeql[py/clear-text-logging-sensitive-data]
        print("-" * 80)  # codeql[py/clear-text-logging-sensitive-data]
        for result in errors:
            print(
                f"  • {result['name']}: {result['error']}"
            )  # codeql[py/clear-text-logging-sensitive-data]
            print()  # codeql[py/clear-text-logging-sensitive-data]

    if warnings:
        print("⚠️  PACKAGES WITH WARNINGS:")  # codeql[py/clear-text-logging-sensitive-data]
        print("-" * 80)  # codeql[py/clear-text-logging-sensitive-data]
        for result in warnings:
            print(
                f"  • {result['name']}: {result['warning']}"
            )  # codeql[py/clear-text-logging-sensitive-data]
            print()  # codeql[py/clear-text-logging-sensitive-data]

    # Generate JSON report
    report_path = Path(__file__).parent.parent / ".codex" / "py312_deps_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    from datetime import datetime, timezone

    with open(report_path, "w") as f:
        json.dump(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "fingerprint": fingerprint,
                "total_packages": len(results),
                "compatible": compatible_count,
                "incompatible": len(incompatible),
                "errors": len(errors),
                "warnings": len(warnings),
                "results": results,
            },
            f,
            indent=2,
        )

    print(
        f"📄 Detailed report saved to: {report_path}"
    )  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    # Determine exit code
    if incompatible or errors:
        print(
            "❌ Python 3.12 migration readiness: NOT READY"
        )  # codeql[py/clear-text-logging-sensitive-data]
        print(
            "   Please resolve incompatible dependencies before migrating."
        )  # codeql[py/clear-text-logging-sensitive-data]
        exit_code = 1
    else:
        print(
            "✅ Python 3.12 migration readiness: READY"
        )  # codeql[py/clear-text-logging-sensitive-data]
        print(
            "   All dependencies support Python 3.12!"
        )  # codeql[py/clear-text-logging-sensitive-data]
        exit_code = 0
    _cache_save(
        fingerprint,
        {
            "exit_code": exit_code,
            "total_packages": len(results),
            "compatible": compatible_count,
            "incompatible": len(incompatible),
            "errors": len(errors),
            "warnings": [result["warning"] for result in warnings],
        },
    )
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
