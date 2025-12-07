"""Tests for checkpoint management."""

import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[2] / "scripts"))
from list_checkpoints import list_checkpoints, apply_retention_policy


class TestCheckpointListing:
    """Test checkpoint listing functionality."""
    
    def test_list_empty_dir(self, tmp_path):
        """Test listing empty directory."""
        result = list_checkpoints(tmp_path)
        assert result == []
    
    def test_list_checkpoints(self, tmp_path):
        """Test listing checkpoints."""
        # Create test checkpoints
        (tmp_path / "checkpoint_1.pt").touch()
        (tmp_path / "checkpoint_2.pt").touch()
        
        result = list_checkpoints(tmp_path)
        assert len(result) == 2
    
    def test_retention_policy(self):
        """Test retention policy logic."""
        checkpoints = [
            {"path": "ckpt1.pt", "age_days": 1},
            {"path": "ckpt2.pt", "age_days": 10},
            {"path": "ckpt3.pt", "age_days": 50},
        ]
        
        keep, delete = apply_retention_policy(
            checkpoints,
            keep_last_n=2,
            keep_days=30,
        )
        
        assert len(keep) == 2
        assert len(delete) == 1
