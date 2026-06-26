"""
Tests for codex.archive.stub module.

This module contains tests for stub generation functionality.
"""

from unittest.mock import patch


class TestMakeStubText:
    """Tests for make_stub_text function."""

    @patch("codex.archive.stub.utcnow_iso")
    def test_basic_stub(self, mock_utcnow):
        """Test basic stub generation."""
        from codex.archive.stub import make_stub_text

        mock_utcnow.return_value = "2024-01-01T00:00:00Z" # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret

        result = make_stub_text(
            path="src/old_module.py",
            actor="user@example.com",
            reason="dead",
            tombstone="ts_abc123",
            sha256="sha256_hash_value",
            commit="abc123def456",
        )

        assert isinstance(result, str)

    @patch("codex.archive.stub.utcnow_iso")
    def test_contains_header(self, mock_utcnow):
        """Test stub contains header."""
        from codex.archive.stub import make_stub_text

        mock_utcnow.return_value = "2024-01-01T00:00:00Z"

        result = make_stub_text(
            path="test.py",
            actor="actor",
            reason="legacy",
            tombstone="ts_1",
            sha256="hash",
            commit="commit",
        )

        assert "TOMBSTONE ARCHIVE STUB" in result, "Result must not be empty"

    @patch("codex.archive.stub.utcnow_iso")
    def test_contains_path(self, mock_utcnow):
        """Test stub contains file path."""
        from codex.archive.stub import make_stub_text

        mock_utcnow.return_value = "2024-01-01T00:00:00Z"

        result = make_stub_text(
            path="src/modules/module.py",
            actor="user",
            reason="dead",
            tombstone="ts",
            sha256="hash",
            commit="commit",
        )

        assert "src/modules/module.py" in result, "Result must not be empty"

    @patch("codex.archive.stub.utcnow_iso")
    def test_contains_actor(self, mock_utcnow):
        """Test stub contains actor."""
        from codex.archive.stub import make_stub_text

        mock_utcnow.return_value = "2024-01-01T00:00:00Z"

        result = make_stub_text(
            path="test.py",
            actor="test_user@company.com",
            reason="dead",
            tombstone="ts",
            sha256="hash",
            commit="commit",
        )

        assert "test_user@company.com" in result, "Result must not be empty"

    @patch("codex.archive.stub.utcnow_iso")
    def test_contains_reason(self, mock_utcnow):
        """Test stub contains reason."""
        from codex.archive.stub import make_stub_text

        mock_utcnow.return_value = "2024-01-01T00:00:00Z"

        result = make_stub_text(
            path="test.py",
            actor="user",
            reason="deprecated",
            tombstone="ts",
            sha256="hash",
            commit="commit",
        )

        assert "deprecated" in result, "Result must not be empty"

    @patch("codex.archive.stub.utcnow_iso")
    def test_contains_tombstone(self, mock_utcnow):
        """Test stub contains tombstone ID."""
        from codex.archive.stub import make_stub_text

        mock_utcnow.return_value = "2024-01-01T00:00:00Z"

        result = make_stub_text(
            path="test.py",
            actor="user",
            reason="dead",
            tombstone="ts_unique_123",
            sha256="hash",
            commit="commit",
        )

        assert "ts_unique_123" in result, "Result must not be empty"

    @patch("codex.archive.stub.utcnow_iso")
    def test_contains_restore_instructions(self, mock_utcnow):
        """Test stub contains restore instructions."""
        from codex.archive.stub import make_stub_text

        mock_utcnow.return_value = "2024-01-01T00:00:00Z"

        result = make_stub_text(
            path="test.py",
            actor="user",
            reason="dead",
            tombstone="ts_123",
            sha256="hash",
            commit="commit",
        )

        assert "restore" in result.lower(), "Result must not be empty"
        assert "codex.cli archive restore" in result, "Result must not be empty"

    @patch("codex.archive.stub.utcnow_iso")
    def test_contains_sha256(self, mock_utcnow):
        """Test stub contains SHA256 hash."""
        from codex.archive.stub import make_stub_text

        mock_utcnow.return_value = "2024-01-01T00:00:00Z"

        result = make_stub_text(
            path="test.py",
            actor="user",
            reason="dead",
            tombstone="ts",
            sha256="abc123def456789hash",
            commit="commit",
        )

        assert "abc123def456789hash" in result, "Result must not be empty"

    @patch("codex.archive.stub.utcnow_iso")
    def test_contains_commit(self, mock_utcnow):
        """Test stub contains commit SHA."""
        from codex.archive.stub import make_stub_text

        mock_utcnow.return_value = "2024-01-01T00:00:00Z"

        result = make_stub_text(
            path="test.py",
            actor="user",
            reason="dead",
            tombstone="ts",
            sha256="hash",
            commit="f1e2d3c4b5a6",
        )

        assert "f1e2d3c4b5a6" in result, "Result must not be empty"

    @patch("codex.archive.stub.utcnow_iso")
    def test_uses_utcnow(self, mock_utcnow):
        """Test stub uses utcnow_iso for timestamp."""
        from codex.archive.stub import make_stub_text

        mock_utcnow.return_value = "2025-06-15T12:30:45Z"

        result = make_stub_text(
            path="test.py",
            actor="user",
            reason="dead",
            tombstone="ts",
            sha256="hash",
            commit="commit",
        )

        mock_utcnow.assert_called_once()
        assert "2025-06-15T12:30:45Z" in result, "Result must not be empty"
