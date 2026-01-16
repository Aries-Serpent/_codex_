#!/usr/bin/env python
"""
Verify Conflicts

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/remediation/verify_conflicts.py [options]
    
    Examples:
    $ python scripts/remediation/verify_conflicts.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""


"""
import logging
logger = logging.getLogger(__name__)
[Verification]: Import Conflict Checker
Purpose: Verifies if local directories are shadowing standard libraries or
causing ambiguous imports between root and src/.

Usage:
  python scripts/remediation/verify_conflicts.py
Flags:
  --expect-site-packages  : Enforce that 'hydra' resolves from site-packages
  --allow-shadow          : Do not exit non-zero on hydra shadowing (logs warning only)
  --mode strict           : Fail on any non-whitelisted duplicates (uses SHIM_INVENTORY.yaml)
  --mode shim-aware       : Warn only for whitelisted duplicates from inventory
  --output FILE           : Write JSON findings to FILE
"""
import sys
import argparse
import importlib.util
import json
from pathlib import Path

# Add repo root to sys.path to simulate how Python sees the repo context
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

try:
    import yaml

    HAS_YAML = True
except ImportError as e:
    logger.debug(f"ImportError: {e}")
    HAS_YAML = False


def load_inventory():
    """Load shim inventory if available."""
    inv_path = ROOT / ".github" / "SHIM_INVENTORY.yaml"
    if not inv_path.exists() or not HAS_YAML:
        return {"inventory": [], "policy": {}}
    try:
        return yaml.safe_load(inv_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.debug(f"Exception: {e}")
        print(f"[WARN] Failed to load inventory: {e}")
        return {"inventory": [], "policy": {}}


def check_import(
    module_name: str, expected_location_substr: str = None, quiet: bool = False
) -> tuple[bool, str]:
    """Check import resolution. Returns (success, origin_path)."""
    if not quiet:
        print(f"[*] Testing import resolution: '{module_name}'")
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            if not quiet:
                print(f"  [FAIL] Module not found.")
            return False, ""
        origin = spec.origin or "namespace"
        if not quiet:
            print(f"  [OK] Resolved to: {origin}")
        if expected_location_substr:
            # Accept both site-packages and dist-packages
            if "site-packages" in str(origin) or "dist-packages" in str(origin):
                return True, origin
            else:
                if not quiet:
                    print(f"  [RISK] Unexpected location!")
                    print(
                        f"         Expected path containing: '{expected_location_substr}' or 'dist-packages'"
                    )
                    print(f"         Actual path:              '{origin}'")
                return False, origin
        return True, origin
    except Exception as e:
        logger.debug(f"Exception: {e}")
        if not quiet:
            print(f"  [CRITICAL] Import crashed: {e}")
        return False, str(e)


def check_split_brain_strict(inventory):
    """Check for split-brain duplicates using inventory whitelist."""
    findings = {"duplicates": [], "whitelisted": [], "violations": [], "mode": "strict"}

    # Build whitelist from inventory
    # Map module to set of whitelisted paths for that module
    whitelist = {}
    for item in inventory.get("inventory", []):
        module = item.get("module", "")
        whitelist_paths = item.get("whitelist_duplicates", [])
        if module and whitelist_paths:
            whitelist[module] = set(whitelist_paths)

    # Check for duplicates
    for item in inventory.get("inventory", []):
        module = item.get("module", "")
        legacy = item.get("legacy_path", "")
        canonical = item.get("canonical_path", "")

        if not legacy or not canonical:
            continue

        # Check if both paths exist
        legacy_exists = (ROOT / legacy).exists() if legacy else False
        canonical_exists = (ROOT / canonical).exists() if canonical else False

        if legacy_exists and canonical_exists:
            findings["duplicates"].append(
                {"module": module, "legacy_path": legacy, "canonical_path": canonical}
            )

            # Check if this module has any whitelisted paths
            # If the legacy path or canonical path is in the whitelist for this module,
            # then the entire duplicate is whitelisted
            module_whitelist = whitelist.get(module, set())
            if legacy in module_whitelist or canonical in module_whitelist:
                findings["whitelisted"].append(
                    {
                        "module": module,
                        "legacy_path": legacy,
                        "canonical_path": canonical,
                        "reason": "whitelisted in inventory",
                    }
                )
            else:
                findings["violations"].append(
                    {
                        "module": module,
                        "legacy_path": legacy,
                        "canonical_path": canonical,
                        "severity": "error",
                        "message": "Non-whitelisted duplicate module paths",
                    }
                )

    return findings


def main():
    parser = argparse.ArgumentParser(description="Verify import conflicts and shadowing.")
    parser.add_argument(
        "--expect-site-packages",
        action="store_true",
        help="Require 'hydra' and 'yaml' to resolve from site-packages.",
    )
    parser.add_argument(
        "--allow-shadow", action="store_true", help="Allow shadowing without non-zero exit."
    )
    parser.add_argument(
        "--mode",
        choices=["strict", "shim-aware", "legacy"],
        default="legacy",
        help="Verification mode: strict (fail on non-whitelisted), shim-aware (warn only), legacy (original behavior)",
    )
    parser.add_argument("--output", default="", help="Write JSON findings to specified file")
    args = parser.parse_args()

    # For strict/shim-aware modes, use inventory-based checking
    if args.mode in ["strict", "shim-aware"]:
        inventory = load_inventory()
        findings = check_split_brain_strict(inventory)
        findings["mode"] = args.mode

        # Add library shadowing checks to findings
        yaml_ok, yaml_origin = check_import(
            "yaml",
            expected_location_substr="site-packages" if args.expect_site_packages else None,
            quiet=True,
        )
        hydra_ok, hydra_origin = check_import(
            "hydra",
            expected_location_substr="site-packages" if args.expect_site_packages else None,
            quiet=True,
        )

        findings["library_shadowing"] = {
            "yaml": {"ok": yaml_ok, "origin": yaml_origin},
            "hydra": {"ok": hydra_ok, "origin": hydra_origin},
        }

        # Output JSON if requested
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(findings, indent=2), encoding="utf-8")
            print(f"[*] Findings written to {args.output}")

        # Print summary
        print(json.dumps(findings, indent=2))

        # Determine exit code
        if args.mode == "strict" and findings["violations"]:
            print(
                f"\n[FAIL] {len(findings['violations'])} non-whitelisted duplicate(s) found in strict mode.",
                file=sys.stderr,
            )
            sys.exit(1)
        elif findings["duplicates"]:
            print(
                f"\n[WARN] {len(findings['duplicates'])} duplicate(s) found ({len(findings['whitelisted'])} whitelisted)."
            )
        else:
            print("\n[PASS] No violations found.")

        sys.exit(0)

    # Legacy mode (original behavior)
    print("--- Structural Integrity Verification ---")
    print(f"Context Root: {ROOT}\n")

    failures = 0

    # 0. Check YAML Shadowing (Critical)
    print(">>> Case 0: Library Shadowing (yaml)")
    yaml_ok, _ = check_import(
        "yaml", expected_location_substr="site-packages" if args.expect_site_packages else None
    )
    if args.expect_site_packages and not yaml_ok:
        print("  [!] CRITICAL: Local 'yaml/' directory is shadowing the installed PyYAML library.")
        print(
            "      Remediation: Rename root 'yaml/' → 'yaml_legacy/' OR remove local shim to allow PyYAML usage."
        )
        print("      Commands:")
        print("        git mv yaml yaml_legacy || true")
        print("        # Ensure site-packages PyYAML imports are used")
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
        print(
            f"      Remediation: Rename 'hydra/' → 'config_legacy/' OR move under 'src/codex_conf/'."
        )
        print(f"      Commands:")
        print(f"        git mv hydra config_legacy || true")
        print(
            f"        # Update imports to hydra-core or src.codex_conf; add DeprecationWarning in config_legacy/__init__.py"
        )
        if not args.allow_shadow:
            failures += 1
            hydra_ok = False
    elif legacy_config.exists():
        print(f"  [OK] Legacy 'hydra/' has been renamed to 'config_legacy/'")
        print(f"       Imports should now use 'import hydra' (from site-packages)")

    # Verify hydra resolves to site-packages
    hydra_ok, _ = check_import(
        "hydra", expected_location_substr="site-packages" if args.expect_site_packages else None
    )
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
    root_train, _ = check_import("training", expected_location_substr=str(ROOT / "training"))
    src_train, _ = check_import(
        "src.training", expected_location_substr=str(ROOT / "src" / "training")
    )
    if root_train and src_train:
        print(
            "  [!] WARNING: Both 'training' and 'src.training' are importable. Ambiguous usage possible."
        )
        failures += 1

    print("\n  -- 'tokenization' vs 'src.tokenization'")
    root_tok, _ = check_import("tokenization", expected_location_substr=str(ROOT / "tokenization"))
    src_tok, _ = check_import(
        "src.tokenization", expected_location_substr=str(ROOT / "src" / "tokenization")
    )
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
