"""
Tests for codex.transform.transformer module.

This module contains tests for code transformation and patch generation.
"""


class TestTier:
    """Tests for Tier enum."""

    def test_tier_a_value(self):
        """Test Tier A value."""
        from codex.transform.transformer import Tier

        assert Tier.A.value == "safe_auto_apply", "Value must be initialized"

    def test_tier_b_value(self):
        """Test Tier B value."""
        from codex.transform.transformer import Tier

        assert Tier.B.value == "apply_with_tests", "Value must be initialized"

    def test_tier_c_value(self):
        """Test Tier C value."""
        from codex.transform.transformer import Tier

        assert Tier.C.value == "suggest_only", "Value must be initialized"


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
            description="Format function",
        )

        assert patch.file_path == "src/module.py", "file_path is not valid"
        assert patch.original == "def foo(): pass", "original is not valid"
        assert patch.modified == "def foo():\n    pass", "modified is not valid"
        assert patch.rule_id == "FORMAT001", "rule_id is not valid"
        assert patch.tier == Tier.A, "tier is not valid"
        assert patch.description == "Format function", "description is not valid"

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
            description="Add spaces around assignment",
        )

        result = patch.to_dict()

        assert result["file_path"] == "test.py", "Result must not be empty"
        assert result["rule_id"] == "WHITESPACE001", "Result must not be empty"
        assert result["tier"] == "A", "Result must not be empty"
        assert result["description"] == "Add spaces around assignment", "Result must not be empty"
        assert "diff" in result, "Result must not be empty"


class TestTransformResult:
    """Tests for TransformResult dataclass."""

    def test_basic_creation(self):
        """Test TransformResult basic creation."""
        from datetime import datetime, timezone

        from codex.transform.transformer import TransformResult

        result = TransformResult(snapshot_id="snap_123", timestamp=datetime.now(timezone.utc))

        assert result.snapshot_id == "snap_123", "Result must not be empty"
        assert result.tier_a_patches == [], "Result must not be empty"
        assert result.tier_b_patches == [], "Result must not be empty"
        assert result.tier_c_suggestions == [], "Result must not be empty"
        assert result.applied is False, "Result must not be empty"
        assert result.errors == [], "Result must not be empty"

    def test_to_dict(self):
        """Test TransformResult to_dict method."""
        from datetime import datetime, timezone

        from codex.transform.transformer import TransformResult

        result = TransformResult(
            snapshot_id="snap_456", timestamp=datetime.now(timezone.utc), applied=True
        )

        d = result.to_dict()

        assert d["snapshot_id"] == "snap_456", "Condition must be true"
        assert d["applied"] is True, "Condition must be true"
        assert "timestamp" in d, "Condition must be true"


class TestModuleLevel:
    """Tests for module-level elements."""

    def test_logger_exists(self):
        """Test logger is configured."""
        from codex.transform.transformer import logger

        assert logger is not None, "logger must be initialized"
        assert logger.name == "codex.transform.transformer", "name is not valid"
