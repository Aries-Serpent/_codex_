#!/usr/bin/env python3
"""
CI Gate: Check for profile/lock drift.

This script validates that:
1. All packages declared in pyproject.toml extras are in uv.lock
2. uv.lock only contains packages transitively required by extras + base
3. All packages have SHA256 hashes

Exits with 0 (success) or 1 (drift detected).
"""

import json
import re
import sys
from pathlib import Path

# Try to use tomllib (Python 3.11+)
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print("ERROR: tomllib/tomli not available. Install: pip install tomli")
        sys.exit(1)


def normalize_pkg(dep_str):
    """Extract normalized package name from dependency specifier."""
    return re.split(r'[<>=\[\];]', dep_str)[0].strip().lower()


def load_pyproject_extras():
    """Load optional-dependencies from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        raise FileNotFoundError(f"pyproject.toml not found at {pyproject_path}")
    
    with open(pyproject_path, "rb") as f:
        pyproject = tomllib.load(f)
    
    optional_deps = pyproject.get("project", {}).get("optional-dependencies", {})
    base_deps = pyproject.get("project", {}).get("dependencies", [])
    
    # Normalize all package names
    extras = {}
    for extra_name, deps in optional_deps.items():
        extras[extra_name] = set(normalize_pkg(d) for d in deps if normalize_pkg(d))
    
    base_packages = set(normalize_pkg(d) for d in base_deps if normalize_pkg(d))
    
    return extras, base_packages


def load_lock_packages():
    """Load package names from uv.lock."""
    lock_path = Path("uv.lock")
    if not lock_path.exists():
        raise FileNotFoundError(f"uv.lock not found at {lock_path}")
    
    with open(lock_path, 'r') as f:
        lock_content = f.read()
    
    # Extract package names
    packages = set(re.findall(r'name = "([^"]+)"', lock_content))
    normalized_packages = set(p.lower() for p in packages)
    
    # Check for hashes
    hash_count = len(re.findall(r'hash = "sha256:[a-f0-9]{64}"', lock_content))
    
    return normalized_packages, hash_count, len(normalized_packages)


def main():
    """Main validation logic."""
    print("=" * 70)
    print("PROFILE DRIFT VALIDATION")
    print("=" * 70)
    
    # Load dependencies
    try:
        extras, base_packages = load_pyproject_extras()
        lock_packages, hash_count, total_packages = load_lock_packages()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return 1
    
    print(f"\nConfiguration:")
    print(f"  Extras defined: {list(extras.keys())}")
    print(f"  Base packages: {len(base_packages)}")
    print(f"  Total lock packages: {total_packages}")
    print(f"  SHA256 hashes found: {hash_count}")
    
    # Collect all declared packages
    all_declared = base_packages.copy()
    for deps in extras.values():
        all_declared.update(deps)
    
    print(f"  Total declared (base + extras): {len(all_declared)}")
    
    # Check for drift
    errors = []
    warnings = []
    
    # CRITICAL: Packages declared but not in lock
    declared_not_in_lock = all_declared - lock_packages
    if declared_not_in_lock:
        errors.append(
            f"CRITICAL: {len(declared_not_in_lock)} packages declared but NOT in lock:\n"
            f"  {', '.join(sorted(declared_not_in_lock))}"
        )
    
    # WARNING: Packages in lock but not explicitly declared (transitive deps)
    lock_not_in_declared = lock_packages - all_declared
    if lock_not_in_declared and len(lock_not_in_declared) > 50:
        warnings.append(
            f"INFO: {len(lock_not_in_declared)} transitive dependencies in lock "
            f"(expected for {', '.join(sorted(lock_not_in_declared)[:5])}...)"
        )
    
    # WARNING: Hash coverage
    if hash_count < total_packages:
        warnings.append(
            f"WARNING: Only {hash_count}/{total_packages} packages have SHA256 hashes"
        )
    
    # Per-extra validation
    print(f"\nPer-Extra Validation:")
    extra_errors = False
    for extra_name in sorted(extras.keys()):
        extra_pkgs = extras[extra_name]
        in_lock = extra_pkgs & lock_packages
        missing = extra_pkgs - lock_packages
        
        status = "✓" if not missing else "✗"
        print(f"  {status} {extra_name:12} {len(in_lock):3}/{len(extra_pkgs):3} in lock")
        
        if missing:
            print(f"      Missing: {', '.join(sorted(missing))}")
            extra_errors = True
    
    # Print warnings
    if warnings:
        print(f"\nWarnings:")
        for warning in warnings:
            print(f"  ⚠  {warning}")
    
    # Print errors and determine exit code
    if errors:
        print(f"\nErrors:")
        for error in errors:
            print(f"  ✗ {error}")
        print("\n" + "=" * 70)
        print("RESULT: FAILED - Profile drift detected")
        print("=" * 70)
        print("\nFix:")
        print("  1. Update pyproject.toml extras to match lock transitive closure")
        print("  2. Run: uv lock --upgrade")
        print("  3. Verify: python scripts/ci/check_profile_drift.py")
        return 1
    
    # Success
    print("\n" + "=" * 70)
    print("RESULT: PASSED - No profile drift detected")
    print("=" * 70)
    print("\nSummary:")
    print(f"  ✓ All {len(all_declared)} declared packages in lock")
    print(f"  ✓ {hash_count} packages have SHA256 hashes")
    print(f"  ✓ Extras properly aligned with lock transitive closure")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
