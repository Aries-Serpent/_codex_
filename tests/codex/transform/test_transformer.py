"""
Tests for codex.transform.transformer module.

This module contains tests for code transformation and patch generation.
"""

import pytest
from pathlib import Path


class TestTier:
    """Tests for Tier enum."""

    def test_tier_a_value(self):
        """Test Tier A value."""
        from codex.transform.transformer import Tier
        
        assert Tier.A.value == "safe_auto_apply"

    def test_tier_b_value(self):
        """Test Tier B value."""
        from codex.transform.transformer import Tier
        
        assert Tier.B.value == "apply_with_tests"

    def test_tier_c_value(self):
        """Test Tier C value."""
        from codex.transform.transformer import Tier
        
        assert Tier.C.value == "suggest_only"


class TestPatch:
    """Tests for Patch dataclass."""

    def test_basic_creation(self):
        """Test Patch basic creation."""
        from codex.transform.transformer import Patch, Tier
        
        patch = Patch(
            file_path="src/module.py",
            original="def foo(): pass",
            modified="def foo():\n    pass",
            diff="@@ -1 +1,2 @@",
            rule_id="FORMAT001",
            tier=Tier.A,
            description="Format function"
        )
        
        assert patch.file_path == "src/module.py"
        assert patch.original == "def foo(): pass"
        assert patch.modified == "def foo():\n    pass"
        assert patch.rule_id == "FORMAT001"
        assert patch.tier == Tier.A
        assert patch.description == "Format function"

    def test_to_dict(self):
        """Test Patch to_dict method."""
        from codex.transform.transformer import Patch, Tier
        
        patch = Patch(
            file_path="test.py",
            original="x=1",
            modified="x = 1",
            diff="--- a/test.py\n+++ b/test.py",
            rule_id="WHITESPACE001",
            tier=Tier.A,
            description="Add spaces around assignment"
        )
        
        result = patch.to_dict()
        
        assert result["file_path"] == "test.py"
        assert result["rule_id"] == "WHITESPACE001"
        assert result["tier"] == "A"
        assert result["description"] == "Add spaces around assignment"
        assert "diff" in result


class TestTransformResult:
    """Tests for TransformResult dataclass."""

    def test_basic_creation(self):
        """Test TransformResult basic creation."""
        from codex.transform.transformer import TransformResult
        from datetime import datetime, timezone
        
        result = TransformResult(
            snapshot_id="snap_123",
            timestamp=datetime.now(timezone.utc)
        )
        
        assert result.snapshot_id == "snap_123"
        assert result.tier_a_patches == []
        assert result.tier_b_patches == []
        assert result.tier_c_suggestions == []
        assert result.applied is False
        assert result.errors == []

    def test_to_dict(self):
        """Test TransformResult to_dict method."""
        from codex.transform.transformer import TransformResult
        from datetime import datetime, timezone
        
        result = TransformResult(
            snapshot_id="snap_456",
            timestamp=datetime.now(timezone.utc),
            applied=True
        )
        
        d = result.to_dict()
        
        assert d["snapshot_id"] == "snap_456"
        assert d["applied"] is True
        assert "timestamp" in d


class TestModuleLevel:
    """Tests for module-level elements."""

    def test_logger_exists(self):
        """Test logger is configured."""
        from codex.transform.transformer import logger
        
        assert logger is not None
        assert logger.name == "codex.transform.transformer"
