"""
Tests for AST storage.
"""

import tempfile
from pathlib import Path

import pytest

from codex_ml.ast.core.node import Finding, SourceLocation
from codex_ml.ast.storage.sqlite_storage import ASTStorage


class TestASTStorage:
    """Tests for ASTStorage class."""

    @pytest.fixture
    def storage(self) -> None:
        """Create temporary storage for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            yield ASTStorage(db_path)

    def test_create_storage(self, storage) -> None:
        """Test creating storage."""
        assert storage.db_path.exists()

    def test_save_analysis(self, storage) -> None:
        """Test saving an analysis."""
        findings = [
            Finding(
                type="high_complexity",
                severity="warning",
                message="Function too complex",
                analyzer="complexity",
            )
        ]
        storage.save_analysis(
            analysis_id="test-001",
            file_path="test.py",
            findings=findings,
            language="python",
        )

        analysis = storage.get_analysis("test-001")
        assert analysis is not None
        assert analysis["analysis_id"] == "test-001"
        assert analysis["file_path"] == "test.py"
        assert analysis["finding_count"] == 1

    def test_get_analysis_not_found(self, storage) -> None:
        """Test getting non-existent analysis."""
        result = storage.get_analysis("nonexistent")
        assert result is None

    def test_get_findings(self, storage) -> None:
        """Test getting findings."""
        findings = [
            Finding(
                type="high_complexity",
                severity="warning",
                message="Msg 1",
                analyzer="complexity",
            ),
            Finding(
                type="unused_import",
                severity="info",
                message="Msg 2",
                analyzer="unused",
            ),
        ]
        storage.save_analysis("test-001", "test.py", findings)

        retrieved = storage.get_findings(analysis_id="test-001")
        assert len(retrieved) == 2

    def test_get_findings_filtered(self, storage) -> None:
        """Test getting filtered findings."""
        findings = [
            Finding(type="a", severity="warning", message="", analyzer="x"),
            Finding(type="b", severity="error", message="", analyzer="y"),
        ]
        storage.save_analysis("test-001", "test.py", findings)

        # Filter by severity
        warnings = storage.get_findings(severity="warning")
        assert len(warnings) == 1
        assert warnings[0].severity == "warning"

    def test_list_analyses(self, storage) -> None:
        """Test listing analyses."""
        for i in range(3):
            storage.save_analysis(f"test-{i:03d}", f"file{i}.py", [])

        analyses = storage.list_analyses()
        assert len(analyses) == 3

    def test_delete_analysis(self, storage) -> None:
        """Test deleting an analysis."""
        storage.save_analysis("test-001", "test.py", [])
        assert storage.get_analysis("test-001") is not None

        result = storage.delete_analysis("test-001")
        assert result is True
        assert storage.get_analysis("test-001") is None

    def test_delete_analysis_not_found(self, storage) -> None:
        """Test deleting non-existent analysis."""
        result = storage.delete_analysis("nonexistent")
        assert result is False

    def test_get_statistics(self, storage) -> None:
        """Test getting statistics."""
        findings = [
            Finding(type="a", severity="warning", message="", analyzer="x"),
            Finding(type="b", severity="error", message="", analyzer="y"),
        ]
        storage.save_analysis("test-001", "test.py", findings)

        stats = storage.get_statistics()
        assert stats["total_analyses"] == 1
        assert stats["total_findings"] == 2
        assert "warning" in stats["findings_by_severity"]
        assert "error" in stats["findings_by_severity"]

    def test_save_metric(self, storage) -> None:
        """Test saving metrics."""
        storage.save_analysis("test-001", "test.py", [])
        storage.save_metric("test-001", "complexity_avg", 5.5)
        storage.save_metric("test-001", "loc", 100.0)

        metrics = storage.get_metrics("test-001")
        assert len(metrics) == 2

    def test_get_metrics_filtered(self, storage) -> None:
        """Test getting filtered metrics."""
        storage.save_analysis("test-001", "test.py", [])
        storage.save_metric("test-001", "complexity_avg", 5.5)
        storage.save_metric("test-001", "loc", 100.0)

        metrics = storage.get_metrics("test-001", metric_name="complexity_avg")
        assert len(metrics) == 1
        assert metrics[0]["metric_name"] == "complexity_avg"
        assert metrics[0]["metric_value"] == 5.5

    def test_findings_with_location(self, storage) -> None:
        """Test findings with source location."""
        location = SourceLocation(
            file_path=Path("test.py"),
            line_start=10,
            line_end=20,
            column_start=0,
            column_end=50,
        )
        findings = [
            Finding(
                type="issue",
                severity="warning",
                message="Test",
                location=location,
                analyzer="test",
            )
        ]
        storage.save_analysis("test-001", "test.py", findings)

        retrieved = storage.get_findings(analysis_id="test-001")
        assert len(retrieved) == 1
        assert retrieved[0].location is not None
        assert retrieved[0].location.line_start == 10
