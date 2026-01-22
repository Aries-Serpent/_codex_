#!/usr/bin/env python3
"""
Cargo.toml Feature Validation Script

Validates that Rust Cargo.toml features are properly configured to prevent
regressions like the January 19, 2026 incident where the 'python' feature
was missing, causing 10 CI failures.

This script should be run in CI/CD pipelines and by Dependabot PRs.
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple


def validate_cargo_features(cargo_toml_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate Cargo.toml features configuration.
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if not cargo_toml_path.exists():
        return False, [f"Cargo.toml not found at {cargo_toml_path}"]
    
    content = cargo_toml_path.read_text()
    
    # Check 1: Features section exists
    if '[features]' not in content:
        errors.append("❌ [features] section not found in Cargo.toml")
        return False, errors
    
    # Check 2: Extract features section
    features_match = re.search(r'\[features\](.*?)(\n\[|\Z)', content, re.DOTALL)
    if not features_match:
        errors.append("❌ Could not parse [features] section")
        return False, errors
    
    features_section = features_match.group(1)
    
    # Check 3: Required features for PyO3
    required_features = {
        'python': r'python\s*=\s*\[',
        'extension-module': r'extension-module\s*=\s*\[.*pyo3/extension-module.*\]',
    }
    
    for feature_name, pattern in required_features.items():
        if not re.search(pattern, features_section):
            errors.append(
                f"❌ Required feature '{feature_name}' not properly configured in Cargo.toml"
            )
    
    # Check 4: Verify python feature enables extension-module
    python_feature_match = re.search(r'python\s*=\s*\[(.*?)\]', features_section)
    if python_feature_match:
        python_deps = python_feature_match.group(1).strip()
        if 'extension-module' not in python_deps:
            errors.append(
                "⚠️ WARNING: 'python' feature should depend on 'extension-module'"
            )
    
    # Check 5: Validate against src/lib.rs usage
    lib_rs_path = cargo_toml_path.parent / 'src' / 'lib.rs'
    if lib_rs_path.exists():
        lib_content = lib_rs_path.read_text()
        cfg_features = re.findall(r'#\[cfg\(feature\s*=\s*"(\w+)"\)\]', lib_content)
        
        for feature in cfg_features:
            if feature not in ['python', 'extension-module', 'default']:
                # Check if this feature exists in Cargo.toml
                feature_pattern = rf'{feature}\s*='
                if not re.search(feature_pattern, features_section):
                    errors.append(
                        f"❌ Feature '{feature}' used in src/lib.rs but not declared in Cargo.toml"
                    )
    
    return len(errors) == 0, errors


def main():
    """Main validation function."""
    repo_root = Path(__file__).parent.parent.parent
    cargo_toml = repo_root / 'Cargo.toml'
    
    print("🔍 Validating Cargo.toml features configuration...")
    print(f"   Location: {cargo_toml}")
    print()
    
    is_valid, errors = validate_cargo_features(cargo_toml)
    
    if is_valid:
        print("✅ All Cargo.toml feature validations passed!")
        print()
        print("Validated:")
        print("  ✓ [features] section exists")
        print("  ✓ 'python' feature declared")
        print("  ✓ 'extension-module' feature declared with pyo3 dependency")
        print("  ✓ Features match usage in src/lib.rs")
        return 0
    else:
        print("❌ Cargo.toml feature validation FAILED!")
        print()
        print("Errors found:")
        for error in errors:
            print(f"  {error}")
        print()
        print("This validation prevents regressions like the January 19, 2026 incident")
        print("where missing features caused 10 CI failures.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
