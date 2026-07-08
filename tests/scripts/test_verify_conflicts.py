"""
Test Verify Conflicts

Test module for verify conflicts.
"""

#!/usr/bin/env python
"""
Tests for scripts/remediation/verify_conflicts.py

Validates that the whitelist parsing logic correctly handles
duplicate module paths according to SHIM_INVENTORY.yaml.
"""
import importlib.util
from contextlib import contextmanager
from pathlib import Path

import pytest

# Constants
SHIM_INVENTORY_FILENAME = "SHIM_INVENTORY.yaml"


@contextmanager
def _load_verify_conflicts_with_root(test_root):
    """
    Context manager to load verify_conflicts module with temporary ROOT override.

    Note: This function manipulates module-level global state (ROOT variable)
    which is necessary because the verify_conflicts module uses ROOT as a
    global. The original ROOT is restored on exit.

    Args:
        test_root: Path to use as temporary ROOT directory for testing

    Yields:
        verify_conflicts module with ROOT set to test_root
    """
    script_path = (
        Path(__file__).resolve().parents[2] / "scripts" / "remediation" / "verify_conflicts.py"
    )
    spec = importlib.util.spec_from_file_location("verify_conflicts", script_path)
    verify_conflicts = importlib.util.module_from_spec(spec)

    # Load the module first
    spec.loader.exec_module(verify_conflicts)

    # Save original ROOT and set test ROOT
    original_root = verify_conflicts.ROOT if hasattr(verify_conflicts, "ROOT") else None
    verify_conflicts.ROOT = test_root

    try:
        yield verify_conflicts
    finally:
        # Restore original ROOT
        if original_root is not None:
            verify_conflicts.ROOT = original_root


def test_verify_conflicts_whitelist_parsing(tmp_path):
    """Test that whitelisted duplicates are correctly excluded from violations."""
    # Create a temporary inventory file
    inventory_content = """
inventory:
  - module: training.engine_hf_trainer
    legacy_path: "training/engine_hf_trainer.py"
    canonical_path: src/training/engine_hf_trainer.py
    owner: core-ml-platform
    status: shim
    rationale: "Test shim"
    deprecation_date: null
    whitelist_duplicates: ["training/engine_hf_trainer.py"]
    notes: "Test notes"

  - module: training.config
    legacy_path: "training/config.py"
    canonical_path: src/training/config.py
    owner: core-ml-platform
    status: shim
    rationale: "Test shim"
    deprecation_date: null
    whitelist_duplicates: ["training/config.py"]
    notes: "Test notes"

  - module: tokenization.api
    legacy_path: "tokenization/api.py"
    canonical_path: src/tokenization/api.py
    owner: nlp-team
    status: shim
    rationale: "Test shim"
    deprecation_date: null
    whitelist_duplicates: ["tokenization/api.py"]
    notes: "Test notes"

policy:
  strict_conflicts:
    enabled: true
    whitelist_source: ".github/SHIM_INVENTORY.yaml"
"""

    # Create test directory structure
    root = tmp_path / "test_repo"
    root.mkdir()

    # Create .github directory and inventory
    github_dir = root / ".github"
    github_dir.mkdir()
    inventory_path = github_dir / SHIM_INVENTORY_FILENAME
    inventory_path.write_text(inventory_content)

    # Create duplicate files (both legacy and canonical paths)
    training_dir = root / "training"
    training_dir.mkdir()
    (training_dir / "engine_hf_trainer.py").write_text("# Legacy file")
    (training_dir / "config.py").write_text("# Legacy file")

    src_training_dir = root / "src" / "training"
    src_training_dir.mkdir(parents=True)
    (src_training_dir / "engine_hf_trainer.py").write_text("# Canonical file")
    (src_training_dir / "config.py").write_text("# Canonical file")

    tokenization_dir = root / "tokenization"
    tokenization_dir.mkdir()
    (tokenization_dir / "api.py").write_text("# Legacy file")

    src_tokenization_dir = root / "src" / "tokenization"
    src_tokenization_dir.mkdir(parents=True)
    (src_tokenization_dir / "api.py").write_text("# Canonical file")

    # Test using context manager
    with _load_verify_conflicts_with_root(root) as verify_conflicts:
        # Load inventory and check
        inventory = verify_conflicts.load_inventory()
        findings = verify_conflicts.check_split_brain_strict(inventory)

        # Verify results
        assert (len(findings["duplicates"]) == 3), f"Expected 3 duplicates, got {len(findings['duplicates'])}"
        assert (len(findings["whitelisted"]) == 3), f"Expected 3 whitelisted, got {len(findings['whitelisted'])}"
        assert (len(findings["violations"]) == 0), f"Expected 0 violations, got {len(findings['violations'])}: {findings['violations']}"

        # Verify specific entries
        whitelisted_modules = {entry["module"] for entry in findings["whitelisted"]}
        assert "training.engine_hf_trainer" in whitelisted_modules, "Condition must be true"
        assert "training.config" in whitelisted_modules, "Condition must be true"
        assert "tokenization.api" in whitelisted_modules, "Condition must be true"


def test_verify_conflicts_non_whitelisted_violation(tmp_path):
    """Test that non-whitelisted duplicates are reported as violations."""
    # Create a temporary inventory file without whitelist entries
    inventory_content = """
inventory:
  - module: models.test_model
    legacy_path: "models/test_model.py"
    canonical_path: src/models/test_model.py
    owner: test-team
    status: shim
    rationale: "Test shim"
    deprecation_date: null
    whitelist_duplicates: []
    notes: "Test notes"

policy:
  strict_conflicts:
    enabled: true
    whitelist_source: ".github/SHIM_INVENTORY.yaml"
"""

    # Create test directory structure
    root = tmp_path / "test_repo2"
    root.mkdir()

    # Create .github directory and inventory
    github_dir = root / ".github"
    github_dir.mkdir()
    inventory_path = github_dir / SHIM_INVENTORY_FILENAME
    inventory_path.write_text(inventory_content)

    # Create duplicate files
    models_dir = root / "models"
    models_dir.mkdir()
    (models_dir / "test_model.py").write_text("# Legacy file")

    src_models_dir = root / "src" / "models"
    src_models_dir.mkdir(parents=True)
    (src_models_dir / "test_model.py").write_text("# Canonical file")

    # Test using context manager
    with _load_verify_conflicts_with_root(root) as verify_conflicts:
        inventory = verify_conflicts.load_inventory()
        findings = verify_conflicts.check_split_brain_strict(inventory)

        # Verify results
        assert (len(findings["duplicates"]) == 1), f"Expected 1 duplicate, got {len(findings['duplicates'])}"
        assert (len(findings["whitelisted"]) == 0), f"Expected 0 whitelisted, got {len(findings['whitelisted'])}"
        assert (len(findings["violations"]) == 1), f"Expected 1 violation, got {len(findings['violations'])}"

        # Verify violation details
        violation = findings["violations"][0]
        assert violation["module"] == "models.test_model", "Condition must be true"
        assert violation["severity"] == "error", "Error should be raised or set"


def test_verify_conflicts_empty_whitelist(tmp_path):
    """Test that modules with empty whitelist_duplicates are treated as non-whitelisted."""
    inventory_content = """
inventory:
  - module: training.new_module
    legacy_path: "training/new_module.py"
    canonical_path: src/training/new_module.py
    owner: test-team
    status: active
    rationale: "Test module"
    deprecation_date: null
    whitelist_duplicates: []
    notes: "No whitelist"

policy:
  strict_conflicts:
    enabled: true
    whitelist_source: ".github/SHIM_INVENTORY.yaml"
"""

    # Create test directory structure
    root = tmp_path / "test_repo3"
    root.mkdir()

    # Create .github directory and inventory
    github_dir = root / ".github"
    github_dir.mkdir()
    inventory_path = github_dir / SHIM_INVENTORY_FILENAME
    inventory_path.write_text(inventory_content)

    # Create duplicate files
    training_dir = root / "training"
    training_dir.mkdir()
    (training_dir / "new_module.py").write_text("# Legacy file")

    src_training_dir = root / "src" / "training"
    src_training_dir.mkdir(parents=True)
    (src_training_dir / "new_module.py").write_text("# Canonical file")

    # Test using context manager
    with _load_verify_conflicts_with_root(root) as verify_conflicts:
        inventory = verify_conflicts.load_inventory()
        findings = verify_conflicts.check_split_brain_strict(inventory)

        # Verify results - empty whitelist should be treated as non-whitelisted
        assert len(findings["duplicates"]) == 1, "Collection must not be empty"
        assert len(findings["whitelisted"]) == 0, "Collection must not be empty"
        assert len(findings["violations"]) == 1, "Collection must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
