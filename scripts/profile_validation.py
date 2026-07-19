#!/usr/bin/env python3
"""
Profile Validation Script
Phase 3 Lane 1 - Cognitive Brain Profile Packaging & Validation

This script validates the profile definitions without requiring pytest.
It checks:
1. Profile definition completeness
2. Dependency isolation (core vs runtime)
3. Entry points configuration
4. Profile size estimates
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set


def extract_profiles_from_pyproject() -> Dict[str, Dict]:
    """Extract profile definitions from pyproject.toml."""
    import tomllib
    
    pyproject_path = Path("pyproject.toml")
    
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
    
    return data.get("project", {}).get("optional-dependencies", {})


def validate_core_profile_isolation(profiles: Dict[str, List[str]]) -> Dict:
    """Validate that core profile has no torch/transformers."""
    core_deps = set(profiles.get("core", []))
    
    forbidden_in_core = {
        "torch",
        "transformers",
        "datasets",
        "accelerate",
        "peft",
        "fastapi",
        "litestar",
        "ray",
        "pandas",
        "numpy",
        "scikit-learn",
        "pytest",
        "black",
        "mypy",
    }
    
    found_forbidden = []
    for dep in core_deps:
        dep_name = dep.split(">=")[0].split("==")[0].split("<")[0].split(";")[0].strip()
        if dep_name in forbidden_in_core:
            found_forbidden.append(dep)
    
    return {
        "status": "PASS" if not found_forbidden else "FAIL",
        "total_packages": len(core_deps),
        "forbidden_found": found_forbidden,
        "isolation_verified": len(found_forbidden) == 0,
    }


def validate_runtime_profile_completeness(profiles: Dict[str, List[str]]) -> Dict:
    """Validate that runtime profile includes expected ML packages."""
    runtime_deps = set(profiles.get("runtime", []))
    
    required_ml_packages = {
        "torch",
        "transformers",
        "datasets",
        "pandas",
        "numpy",
        "scikit-learn",
        "fastapi",
    }
    
    dep_names = set()
    for dep in runtime_deps:
        dep_name = dep.split(">=")[0].split("==")[0].split("<")[0].split(";")[0].strip()
        dep_names.add(dep_name)
    
    found_required = required_ml_packages & dep_names
    missing_required = required_ml_packages - dep_names
    
    return {
        "status": "PASS" if not missing_required else "FAIL",
        "total_packages": len(runtime_deps),
        "required_packages": len(required_ml_packages),
        "found_required": len(found_required),
        "missing_required": list(missing_required),
        "completeness_verified": len(missing_required) == 0,
    }


def validate_full_profile_completeness(profiles: Dict[str, List[str]]) -> Dict:
    """Validate that full profile includes everything."""
    full_deps = set(profiles.get("full", []))
    
    required_categories = {
        "config": {"hydra-core", "omegaconf", "pydantic"},
        "ml": {"torch", "transformers", "datasets"},
        "web": {"fastapi", "litestar"},
        "dev": {"pytest", "black", "mypy"},
    }
    
    dep_names = set()
    for dep in full_deps:
        dep_name = dep.split(">=")[0].split("==")[0].split("<")[0].split(";")[0].strip()
        # Handle packages with hyphens vs underscores
        dep_name = dep_name.replace("-", "_")
        dep_names.add(dep_name)
    
    category_results = {}
    all_found = True
    
    for category, required_packages in required_categories.items():
        found = len(required_packages & {p.replace("-", "_") for p in dep_names})
        total = len(required_packages)
        status = "PASS" if found == total else "FAIL"
        
        if status == "FAIL":
            all_found = False
        
        category_results[category] = {
            "status": status,
            "found": found,
            "total": total,
        }
    
    return {
        "status": "PASS" if all_found else "FAIL",
        "total_packages": len(full_deps),
        "categories": category_results,
        "completeness_verified": all_found,
    }


def validate_entry_points(pyproject_data: Dict) -> Dict:
    """Validate entry points configuration."""
    entry_points = pyproject_data.get("project", {}).get("entry-points", {})
    scripts = pyproject_data.get("project", {}).get("scripts", {})
    
    required_scripts = {"codex-ml", "codex-cli"}
    found_scripts = set(scripts.keys()) if scripts else set()
    
    required_entry_point_groups = {
        "codex_ml.tokenizers",
        "codex_ml.models",
        "codex_ml.metrics",
    }
    found_entry_point_groups = set(entry_points.keys()) if entry_points else set()
    
    return {
        "scripts": {
            "required": list(required_scripts),
            "found": list(found_scripts),
            "missing": list(required_scripts - found_scripts),
            "status": "PASS" if required_scripts <= found_scripts else "FAIL",
        },
        "entry_point_groups": {
            "required": list(required_entry_point_groups),
            "found": list(found_entry_point_groups),
            "missing": list(required_entry_point_groups - found_entry_point_groups),
            "status": "PASS" if required_entry_point_groups <= found_entry_point_groups else "FAIL",
        },
    }


def estimate_profile_sizes(profiles: Dict[str, List[str]]) -> Dict:
    """Estimate profile sizes based on package counts and typical sizes."""
    # Rough estimates: core pkg ~10MB, runtime pkg ~30MB, dev pkg ~20MB
    
    estimates = {}
    
    for profile_name in ["core", "runtime", "full"]:
        deps = profiles.get(profile_name, [])
        
        if profile_name == "core":
            # Small packages: ~1-2MB each
            estimated_size_mb = len(deps) * 1.5
            target_mb = 15
        elif profile_name == "runtime":
            # Medium packages: ~2-3MB each, but some huge (torch ~2GB compressed, ~600MB wheel)
            # torch is ~600MB, transformers ~500MB, others smaller
            estimated_size_mb = 600 + 500 + (len(deps) - 2) * 2
            target_mb = 35
        else:  # full
            estimated_size_mb = 600 + 500 + (len(deps) - 2) * 2
            target_mb = 100
        
        estimates[profile_name] = {
            "package_count": len(deps),
            "estimated_size_mb": estimated_size_mb,
            "target_size_mb": target_mb,
            "status": "PASS" if estimated_size_mb <= target_mb else "WARN",
            "note": "Estimates are rough; actual sizes vary by platform and installation method",
        }
    
    return estimates


def main():
    """Run comprehensive profile validation."""
    print("=" * 80)
    print("Phase 3 Lane 1: Profile Definition Validation")
    print("=" * 80)
    
    # Load pyproject.toml
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib
    
    pyproject_path = Path("pyproject.toml")
    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)
    
    profiles = pyproject_data.get("project", {}).get("optional-dependencies", {})
    
    print(f"\n✅ Loaded pyproject.toml")
    print(f"   Profiles found: {list(profiles.keys())}")
    
    # Run validations
    validations = {}
    
    print(f"\n{'=' * 80}")
    print("1️⃣  Core Profile Isolation Validation")
    print(f"{'=' * 80}")
    
    core_validation = validate_core_profile_isolation(profiles)
    validations["core_isolation"] = core_validation
    
    print(f"Status: {core_validation['status']}")
    print(f"Packages in core profile: {core_validation['total_packages']}")
    if core_validation["forbidden_found"]:
        print(f"❌ Forbidden packages found: {core_validation['forbidden_found']}")
    else:
        print(f"✅ No forbidden runtime packages in core profile")
    
    print(f"\n{'=' * 80}")
    print("2️⃣  Runtime Profile Completeness Validation")
    print(f"{'=' * 80}")
    
    runtime_validation = validate_runtime_profile_completeness(profiles)
    validations["runtime_completeness"] = runtime_validation
    
    print(f"Status: {runtime_validation['status']}")
    print(f"Packages in runtime profile: {runtime_validation['total_packages']}")
    print(f"Required ML packages: {runtime_validation['required_packages']}")
    print(f"Found required: {runtime_validation['found_required']}")
    if runtime_validation["missing_required"]:
        print(f"❌ Missing required: {runtime_validation['missing_required']}")
    else:
        print(f"✅ All required packages present")
    
    print(f"\n{'=' * 80}")
    print("3️⃣  Full Profile Completeness Validation")
    print(f"{'=' * 80}")
    
    full_validation = validate_full_profile_completeness(profiles)
    validations["full_completeness"] = full_validation
    
    print(f"Status: {full_validation['status']}")
    print(f"Total packages in full profile: {full_validation['total_packages']}")
    print(f"\nCategory breakdown:")
    for category, result in full_validation["categories"].items():
        print(f"  {category:10s}: {result['found']}/{result['total']} ✅" if result['status'] == "PASS" else f"  {category:10s}: {result['found']}/{result['total']} ❌")
    
    print(f"\n{'=' * 80}")
    print("4️⃣  Entry Points & CLI Validation")
    print(f"{'=' * 80}")
    
    entry_points_validation = validate_entry_points(pyproject_data)
    validations["entry_points"] = entry_points_validation
    
    print(f"\nConsole Scripts:")
    print(f"  Required: {entry_points_validation['scripts']['required']}")
    print(f"  Found: {entry_points_validation['scripts']['found']}")
    if entry_points_validation['scripts']['missing']:
        print(f"  Missing: {entry_points_validation['scripts']['missing']}")
    print(f"  Status: {entry_points_validation['scripts']['status']}")
    
    print(f"\nEntry Point Groups:")
    print(f"  Required: {len(entry_points_validation['entry_point_groups']['required'])}")
    print(f"  Found: {len(entry_points_validation['entry_point_groups']['found'])}")
    if entry_points_validation['entry_point_groups']['missing']:
        print(f"  Missing: {entry_points_validation['entry_point_groups']['missing']}")
    print(f"  Status: {entry_points_validation['entry_point_groups']['status']}")
    
    print(f"\n{'=' * 80}")
    print("5️⃣  Profile Size Estimation")
    print(f"{'=' * 80}")
    
    size_estimates = estimate_profile_sizes(profiles)
    validations["size_estimates"] = size_estimates
    
    for profile_name, estimate in size_estimates.items():
        status = "✅" if estimate["status"] == "PASS" else "⚠️"
        print(f"\n{profile_name.upper()} Profile:")
        print(f"  Packages: {estimate['package_count']}")
        print(f"  Estimated size: {estimate['estimated_size_mb']:.1f} MB")
        print(f"  Target size: {estimate['target_size_mb']} MB")
        print(f"  Status: {status}")
        if estimate["status"] == "WARN":
            ratio = estimate["estimated_size_mb"] / estimate["target_size_mb"]
            print(f"  ⚠️  Estimated to exceed target by {(ratio - 1) * 100:.1f}%")
    
    # Summary
    print(f"\n{'=' * 80}")
    print("📊 VALIDATION SUMMARY")
    print(f"{'=' * 80}")
    
    all_pass = all(
        v.get("status") == "PASS" or v.get("status") == "WARN"
        for k, v in validations.items()
        if k != "size_estimates"
    )
    
    print(f"\nCore isolation: {core_validation['status']}")
    print(f"Runtime completeness: {runtime_validation['status']}")
    print(f"Full completeness: {full_validation['status']}")
    print(f"Entry points: {entry_points_validation['scripts']['status']} / {entry_points_validation['entry_point_groups']['status']}")
    
    print(f"\n{'Overall Status:':30s} {'✅ PASS' if all_pass else '❌ FAIL'}")
    
    # Save validation report
    report_path = Path(".codex") / "profile_validation_results.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, "w") as f:
        json.dump(validations, f, indent=2)
    
    print(f"\n📄 Validation report saved to: {report_path}")
    
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
