#!/usr/bin/env python
"""
[Verification]: Import Conflict Checker
Purpose: Verifies if local directories are shadowing standard libraries or 
causing ambiguous imports between root and src/.

Usage:
  python scripts/remediation/verify_conflicts.py
Flags:
  --expect-site-packages  : Enforce that 'hydra' resolves from site-packages
  --allow-shadow          : Do not exit non-zero on hydra shadowing (logs warning only)
"""
import sys
import argparse
import importlib.util
from pathlib import Path

# Add repo root to sys.path to simulate how Python sees the repo context
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

def check_import(module_name: str, expected_location_substr: str = None) -> bool:
    print(f"[*] Testing import resolution: '{module_name}'")
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            print(f"  [FAIL] Module not found.")
            return False
        origin = spec.origin or "namespace"
        print(f"  [OK] Resolved to: {origin}")
        if expected_location_substr:
            # Accept both site-packages and dist-packages
            if ("site-packages" in str(origin) or "dist-packages" in str(origin)):
                return True
            else:
                print(f"  [RISK] Unexpected location!")
                print(f"         Expected path containing: '{expected_location_substr}' or 'dist-packages'")
                print(f"         Actual path:              '{origin}'")
                return False
        return True
    except Exception as e:
        print(f"  [CRITICAL] Import crashed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Verify import conflicts and shadowing.")
    parser.add_argument("--expect-site-packages", action="store_true", help="Require 'hydra' and 'yaml' to resolve from site-packages.")
    parser.add_argument("--allow-shadow", action="store_true", help="Allow shadowing without non-zero exit.")
    args = parser.parse_args()

    print("--- Structural Integrity Verification ---")
    print(f"Context Root: {ROOT}\n")

    failures = 0

    # 0. Check YAML Shadowing (Critical)
    print(">>> Case 0: Library Shadowing (yaml)")
    yaml_ok = check_import("yaml", expected_location_substr="site-packages" if args.expect_site_packages else None)
    if args.expect_site_packages and not yaml_ok:
        print("  [!] CRITICAL: Local 'yaml/' or 'yaml_legacy/' directory may be shadowing PyYAML.")
        print("      Remediation: Ensure 'yaml/' renamed to 'yaml_legacy/' or removed.")
        print("      Quick fix: run `git mv yaml yaml_legacy || true` to avoid shadowing.")
        if not args.allow_shadow:
            failures += 1

    # 1. Check Hydra Shadowing (Critical)
    print("\n>>> Case 1: Library Shadowing (hydra)")
    
    # Check if legacy directories exist
    legacy_hydra = ROOT / "hydra"
    legacy_config = ROOT / "config_legacy"
    if legacy_hydra.exists():
        print(f"  [!] CRITICAL: Local 'hydra/' directory still exists at repository root.")
        print(f"      This WILL shadow the installed hydra-core package.")
        print(f"      Remediation: Rename 'hydra/' to 'config_legacy/' immediately:")
        print(f"                   git mv hydra config_legacy")
        print(f"      Quick fix: run `git mv hydra config_legacy || true` and update imports to `src.codex_conf` or add deprecation shims.")
        if not args.allow_shadow:
            failures += 1
            hydra_ok = False
    elif legacy_config.exists():
        print(f"  [OK] Legacy 'hydra/' has been renamed to 'config_legacy/'")
        print(f"       Imports should now use 'import hydra' (from site-packages)")
    
    # Verify hydra resolves to site-packages
    hydra_ok = check_import("hydra", expected_location_substr="site-packages" if args.expect_site_packages else None)
    if args.expect_site_packages and not hydra_ok:
        print("  [!] CRITICAL: 'hydra' import does not resolve to site-packages.")
        print("      Remediation: Ensure no local 'hydra/' directory exists.")
        print("                   Verify hydra-core is installed: pip install hydra-core")
        print("      Quick fix: run `git mv hydra config_legacy || true` and update imports.")
        if not args.allow_shadow:
            failures += 1

    # 2. Check Split Brain Resolution
    print("\n>>> Case 2: Split Brain Ambiguity")
    print("  -- 'training' vs 'src.training'")
    root_train = check_import("training", expected_location_substr=str(ROOT / "training"))
    src_train = check_import("src.training", expected_location_substr=str(ROOT / "src" / "training"))
    if root_train and src_train:
        print("  [!] WARNING: Both 'training' and 'src.training' are importable. Ambiguous usage possible.")
        failures += 1

    print("\n  -- 'tokenization' vs 'src.tokenization'")
    root_tok = check_import("tokenization", expected_location_substr=str(ROOT / "tokenization"))
    src_tok = check_import("src.tokenization", expected_location_substr=str(ROOT / "src" / "tokenization"))
    if root_tok and src_tok:
        print("  [!] WARNING: Both 'tokenization' and 'src.tokenization' are importable.")
        failures += 1

    print("\n  -- 'models' vs 'src.modeling'")
    check_import("models")
    check_import("src.modeling")

    print("\n--- Verification Summary ---")
    if failures > 0:
        print(f"[FAIL] {failures} structural risks detected.")
        print("Recommendation: Execute 'Codebase_Convergence_Validation' plan.")
        sys.exit(1)
    else:
        print("[PASS] No structural conflicts detected.")
        sys.exit(0)

if __name__ == "__main__":
    main()
