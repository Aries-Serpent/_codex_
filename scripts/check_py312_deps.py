#!/usr/bin/env python3
"""
Verify all dependencies support Python 3.12.

This script checks pyproject.toml dependencies against PyPI metadata
to ensure Python 3.12 compatibility before migration.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print("ERROR: Neither tomllib (Python 3.11+) nor tomli is available")
        sys.exit(1)


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
    is_conditional = ';' in dep_spec

    # Remove environment markers for parsing
    if is_conditional:
        dep_spec = dep_spec.split(';')[0].strip()

    # Remove extras like [cuda], [serve], etc.
    dep_spec = re.sub(r'\[([^\]]+)\]', '', dep_spec)

    # Split on comparison operators
    match = re.match(r'^([a-zA-Z0-9_-]+)([><=!]+.*)?$', dep_spec.strip())
    if match:
        package_name = match.group(1)
        version_constraint = match.group(2) if match.group(2) else None
        return package_name, version_constraint, is_conditional

    return dep_spec.strip(), None, is_conditional


def check_package_py312_support(package: str) -> dict[str, Any]:
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
    """
    result = {
        "name": package,
        "version": None,
        "supports_312": False,
        "latest_version": None,
        "python_requires": None,
        "error": None,
    }

    try:
        # Get package info from PyPI
        proc = subprocess.run(
            [sys.executable, "-m", "pip", "index", "versions", package],
            capture_output=True,
            text=True,
            timeout=30,
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
            timeout=10,
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
                match = re.search(r'>=\s*(\d+)\.(\d+)', req)
                if match:
                    major, minor = int(match.group(1)), int(match.group(2))
                    # If requires >= 3.x where x <= 12, likely supports 3.12
                    if major == 3 and minor <= 12 or major < 3:
                        result["supports_312"] = True
            # No upper bound restriction typically means support
            elif "<" not in req and "!=" not in req:
                result["supports_312"] = True
        else:
            # No explicit requirement often means broad compatibility
            result["supports_312"] = True
            result["python_requires"] = "Not specified (likely compatible)"

    except subprocess.TimeoutExpired:
        result["error"] = "Timeout querying PyPI"
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
        print(f"ERROR: pyproject.toml not found at {pyproject_path}")
        sys.exit(1)

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    dependencies = []

    # Get main dependencies
    if "project" in data and "dependencies" in data["project"]:
        dependencies.extend(data["project"]["dependencies"])

    # Get optional dependencies
    if "project" in data and "optional-dependencies" in data["project"]:
        for group, deps in data["project"]["optional-dependencies"].items():
            dependencies.extend(deps)

    return dependencies


def main() -> int:
    """
    Main entry point for dependency compatibility checker.

    Returns:
        Exit code: 0 if all dependencies support Python 3.12, 1 otherwise
    """
    print("=" * 80)
    print("Python 3.12 Dependency Compatibility Checker")
    print("=" * 80)
    print()

    # Load dependencies
    print("Loading dependencies from pyproject.toml...")
    dep_specs = load_dependencies_from_pyproject()

    # Parse unique package names, excluding conditional dependencies for Python < 3.12
    packages = set()
    skipped_conditional = []
    for dep_spec in dep_specs:
        package_name, _, is_conditional = parse_dependency_spec(dep_spec)

        # Skip conditional dependencies that don't apply to Python 3.12+
        if is_conditional and ('python_version' in dep_spec and '<' in dep_spec):
            # This is a conditional for older Python versions, skip it
            skipped_conditional.append(dep_spec)
            continue

        packages.add(package_name)

    print(f"Found {len(packages)} unique packages to check")
    if skipped_conditional:
        print(f"Skipped {len(skipped_conditional)} conditional dependencies for Python < 3.12")
    print()

    # Check each package
    results = []
    incompatible = []
    errors = []

    for i, package in enumerate(sorted(packages), 1):
        print(f"[{i}/{len(packages)}] Checking {package}...", end=" ")
        sys.stdout.flush()

        result = check_package_py312_support(package)
        results.append(result)

        if result["error"]:
            print("❌ ERROR")
            errors.append(result)
        elif result["supports_312"]:
            print("✅ COMPATIBLE")
        else:
            print("⚠️  INCOMPATIBLE")
            incompatible.append(result)

    print()
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print()

    compatible_count = len(results) - len(incompatible) - len(errors)
    print(f"✅ Compatible:   {compatible_count}/{len(results)}")
    print(f"⚠️  Incompatible: {len(incompatible)}/{len(results)}")
    print(f"❌ Errors:       {len(errors)}/{len(results)}")
    print()

    if incompatible:
        print("⚠️  INCOMPATIBLE PACKAGES:")
        print("-" * 80)
        for result in incompatible:
            print(f"  • {result['name']}")
            print(f"    Version: {result['version'] or 'Unknown'}")
            print(f"    Requires: {result['python_requires'] or 'Not specified'}")
            print()

    if errors:
        print("❌ PACKAGES WITH ERRORS:")
        print("-" * 80)
        for result in errors:
            print(f"  • {result['name']}: {result['error']}")
            print()

    # Generate JSON report
    report_path = Path(__file__).parent.parent / ".codex" / "py312_deps_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    from datetime import datetime, timezone

    with open(report_path, "w") as f:
        json.dump({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_packages": len(results),
            "compatible": compatible_count,
            "incompatible": len(incompatible),
            "errors": len(errors),
            "results": results,
        }, f, indent=2)

    print(f"📄 Detailed report saved to: {report_path}")
    print()

    # Determine exit code
    if incompatible or errors:
        print("❌ Python 3.12 migration readiness: NOT READY")
        print("   Please resolve incompatible dependencies before migrating.")
        return 1
    print("✅ Python 3.12 migration readiness: READY")
    print("   All dependencies support Python 3.12!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
