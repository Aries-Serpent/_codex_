"""Tests for SHIM inventory integration."""

import tempfile
from pathlib import Path

import pytest
import yaml

from tools.dupinv.shim_integration import (
    CrossReference,
    ShimEntry,
    ShimInventoryReader,
)


def test_load_shim_inventory():
    """Test loading SHIM inventory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        github_dir = repo_root / ".github"
        github_dir.mkdir()

        # Create test SHIM inventory
        inventory = {
            "inventory": [
                {
                    "module": "training.engine",
                    "legacy_path": "training/engine.py",
                    "canonical_path": "src/training/engine.py",
                    "owner": "ml-team",
                    "status": "shim",
                    "rationale": "Compatibility layer",
                    "deprecation_date": None,
                    "whitelist_duplicates": ["training/engine.py"],
                    "notes": "Test entry",
                }
            ]
        }

        shim_path = github_dir / "SHIM_INVENTORY.yaml"
        with open(shim_path, "w") as f:
            yaml.dump(inventory, f)

        # Load inventory
        reader = ShimInventoryReader(repo_root)
        entries = reader.load()

        assert len(entries) == 1, "Entries must not be empty"
        assert entries[0].module == "training.engine", "module is not valid"
        assert entries[0].status == "shim", "status is not valid"
        assert "training/engine.py" in entries[0].whitelist_duplicates, "Condition must be true"


def test_extract_whitelist():
    """Test extracting whitelisted paths."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        github_dir = repo_root / ".github"
        github_dir.mkdir()

        inventory = {
            "inventory": [
                {
                    "module": "training.engine",
                    "legacy_path": "training/engine.py",
                    "canonical_path": "src/training/engine.py",
                    "owner": "ml-team",
                    "status": "shim",
                    "rationale": "Test",
                    "deprecation_date": None,
                    "whitelist_duplicates": ["training/engine.py"],
                    "notes": "",
                }
            ]
        }

        shim_path = github_dir / "SHIM_INVENTORY.yaml"
        with open(shim_path, "w") as f:
            yaml.dump(inventory, f)

        reader = ShimInventoryReader(repo_root)
        whitelisted = reader.get_whitelisted_paths()

        # Should include both whitelist_duplicates and the paths themselves
        assert ("training.engine", "training/engine.py") in whitelisted
        assert ("training.engine", "src/training/engine.py") in whitelisted


def test_missing_shim_file():
    """Test handling missing SHIM inventory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        reader = ShimInventoryReader(repo_root)

        with pytest.raises(FileNotFoundError):
            reader.load()


def test_invalid_yaml():
    """Test handling malformed YAML."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        github_dir = repo_root / ".github"
        github_dir.mkdir()

        shim_path = github_dir / "SHIM_INVENTORY.yaml"
        with open(shim_path, "w") as f:
            f.write("invalid: yaml: syntax: [[[")

        reader = ShimInventoryReader(repo_root)

        with pytest.raises(yaml.YAMLError):
            reader.load()


def test_whitelisted_duplicate():
    """Test identifying whitelisted duplicates."""
    entries = [
        ShimEntry(
            module="training.engine",
            legacy_path="training/engine.py",
            canonical_path="src/training/engine.py",
            owner="ml-team",
            status="shim",
            rationale="Test",
            deprecation_date=None,
            whitelist_duplicates=["training/engine.py"],
            notes="",
        )
    ]

    cross_ref = CrossReference(entries)

    assert cross_ref.is_whitelisted("training.engine", "training/engine.py")
    assert cross_ref.is_whitelisted("training.engine", "src/training/engine.py")
    assert not cross_ref.is_whitelisted("training.engine", "other/path.py")


def test_non_whitelisted():
    """Test identifying non-whitelisted duplicates."""
    entries = [
        ShimEntry(
            module="training.engine",
            legacy_path="training/engine.py",
            canonical_path="src/training/engine.py",
            owner="ml-team",
            status="shim",
            rationale="Test",
            deprecation_date=None,
            whitelist_duplicates=["training/engine.py"],
            notes="",
        )
    ]

    cross_ref = CrossReference(entries)

    result = cross_ref.check_paths(["unknown/file.py"])

    assert not result.in_shim_inventory, "Result must not be empty"
    assert not result.is_whitelisted, "Result must not be empty"
    assert result.shim_status is None, "Result must not be empty"
    assert any("Add to .github/SHIM_INVENTORY.yaml" in rec for rec in result.recommendations)


def test_not_in_inventory():
    """Test flagging duplicates not in inventory."""
    entries = [
        ShimEntry(
            module="training.engine",
            legacy_path="training/engine.py",
            canonical_path="src/training/engine.py",
            owner="ml-team",
            status="shim",
            rationale="Test",
            deprecation_date=None,
            whitelist_duplicates=["training/engine.py"],
            notes="",
        )
    ]

    cross_ref = CrossReference(entries)

    # Check a path not in inventory
    result = cross_ref.check_paths(["scripts/util/helper.py"])

    assert not result.in_shim_inventory, "Result must not be empty"
    assert "Add to .github/SHIM_INVENTORY.yaml" in result.recommendations[0], "Result must not be empty"


def test_recommendations():
    """Test generating appropriate recommendations."""
    entries = [
        ShimEntry(
            module="training.engine",
            legacy_path="training/engine.py",
            canonical_path="src/training/engine.py",
            owner="ml-team",
            status="shim",
            rationale="Test",
            deprecation_date=None,
            whitelist_duplicates=["training/engine.py"],
            notes="",
        )
    ]

    cross_ref = CrossReference(entries)

    # Whitelisted duplicate
    result1 = cross_ref.check_paths(["training/engine.py"])
    assert result1.in_shim_inventory, "Result must not be empty"
    assert result1.is_whitelisted, "Result must not be empty"
    assert any("Already tracked" in rec for rec in result1.recommendations), "Result must not be empty"

    # Not in inventory
    result2 = cross_ref.check_paths(["new/duplicate.py"])
    assert not result2.in_shim_inventory, "Result must not be empty"
    assert any("Add to .github/SHIM_INVENTORY.yaml" in rec for rec in result2.recommendations)
