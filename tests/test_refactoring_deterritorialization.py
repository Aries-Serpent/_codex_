"""
Comprehensive test suite for refactoring deterritorialization engine.

Tests cover:
- Code rigidity detection (deep nesting, long methods, god classes)
- Line of flight proposal
- Statistics / report export
- Edge case handling (empty and invalid sources)

The engine operates on files/directories (``detect_rigidity``) and proposes
lines of flight from detected rigidities (``propose_lines_of_flight``).
"""

from pathlib import Path

import pytest
from codex.refactoring.deterritorialization_engine import (
    DeterritorializationEngine,
    LineOfFlight,
    RigidityDetection,
    RigidityDetector,
    RigidityType,  # pragma: allowlist secret
)

DEEP_NESTING_CODE = """
def outer():
    if True:
        if True:
            if True:
                if True:
                    if True:
                        if True:
                            pass
"""

SIMPLE_CODE = """
def simple():
    return 1
"""


def _long_method_code(num_statements: int = 60) -> str:
    body = "\n".join(f"    v{i} = {i}" for i in range(num_statements))
    return f"def long_method():\n{body}\n    return v0\n"


def _god_class_code(num_methods: int = 30) -> str:
    methods = "\n".join(f"    def method{i}(self):\n        pass" for i in range(num_methods))
    return f"class GodClass:\n{methods}\n"


def _write(tmp_path: Path, name: str, code: str) -> Path:
    path = tmp_path / name
    path.write_text(code, encoding="utf-8")
    return path


class TestRigidityType:
    """Test RigidityType enum values."""

    @pytest.mark.parametrize(
        ("member", "value"),
        [
            (RigidityType.DEEP_NESTING, "deep_nesting"),
            (RigidityType.LONG_METHOD, "long_method"),
            (RigidityType.GOD_CLASS, "god_class"),
            (RigidityType.TIGHT_COUPLING, "tight_coupling"),
            (RigidityType.HARDCODED_VALUES, "hardcoded_values"),
            (RigidityType.REPEATED_PATTERNS, "repeated_patterns"),
            (RigidityType.OVERLY_COMPLEX, "overly_complex"),
        ],
    )
    def test_rigidity_type_values(self, member, value):
        assert member.value == value
        assert RigidityType(value) is member


class TestDeterritorializationEngine:
    """Test DeterritorializationEngine detection."""

    def test_engine_initialization(self):
        engine = DeterritorializationEngine()
        assert engine.rigidities == []
        assert engine.lines_of_flight == []
        assert isinstance(engine.detector, RigidityDetector)

    def test_detect_deep_nesting(self, tmp_path):
        path = _write(tmp_path, "nested.py", DEEP_NESTING_CODE)
        rigidities = DeterritorializationEngine().detect_rigidity(path)
        nesting = [r for r in rigidities if r.rigidity_type == RigidityType.DEEP_NESTING]
        assert len(nesting) == 1
        assert nesting[0].metadata["method_name"] == "outer"
        assert nesting[0].metadata["max_depth"] == 6

    def test_detect_long_method(self, tmp_path):
        path = _write(tmp_path, "long.py", _long_method_code())
        rigidities = DeterritorializationEngine().detect_rigidity(path)
        long_methods = [r for r in rigidities if r.rigidity_type == RigidityType.LONG_METHOD]
        assert len(long_methods) == 1
        assert long_methods[0].metadata["method_name"] == "long_method"
        assert long_methods[0].metadata["num_lines"] > 50

    def test_detect_god_class(self, tmp_path):
        path = _write(tmp_path, "god.py", _god_class_code())
        rigidities = DeterritorializationEngine().detect_rigidity(path)
        god = [r for r in rigidities if r.rigidity_type == RigidityType.GOD_CLASS]
        assert len(god) == 1
        assert god[0].metadata == {"num_methods": 30, "class_name": "GodClass"}

    def test_small_class_is_not_god_class(self, tmp_path):
        path = _write(tmp_path, "small.py", _god_class_code(5))
        rigidities = DeterritorializationEngine().detect_rigidity(path)
        assert not any(r.rigidity_type == RigidityType.GOD_CLASS for r in rigidities)

    def test_simple_code_has_no_rigidity(self, tmp_path):
        path = _write(tmp_path, "simple.py", SIMPLE_CODE)
        assert DeterritorializationEngine().detect_rigidity(path) == []

    def test_custom_thresholds(self, tmp_path):
        path = _write(tmp_path, "nested.py", DEEP_NESTING_CODE)
        detector = RigidityDetector(max_nesting=10)
        assert detector.analyze_file(path) == []

    def test_empty_code_handling(self, tmp_path):
        path = _write(tmp_path, "empty.py", "")
        assert DeterritorializationEngine().detect_rigidity(path) == []

    def test_invalid_code_handling(self, tmp_path):
        path = _write(tmp_path, "broken.py", "this is not valid python {")
        # Syntax errors are logged, not raised
        assert DeterritorializationEngine().detect_rigidity(path) == []

    def test_non_python_file_ignored(self, tmp_path):
        path = _write(tmp_path, "notes.txt", DEEP_NESTING_CODE)
        assert DeterritorializationEngine().detect_rigidity(path) == []

    def test_directory_scan_does_not_duplicate(self, tmp_path):
        _write(tmp_path, "a.py", DEEP_NESTING_CODE)
        _write(tmp_path, "b.py", _god_class_code())
        _write(tmp_path, "c.py", SIMPLE_CODE)
        rigidities = DeterritorializationEngine().detect_rigidity(tmp_path)
        assert len(rigidities) == 2
        assert {Path(r.file_path).name for r in rigidities} == {"a.py", "b.py"}


class TestDetectedRigidities:
    """Test rigidity detection result structure."""

    @pytest.fixture
    def detection(self, tmp_path) -> RigidityDetection:
        path = _write(tmp_path, "nested.py", DEEP_NESTING_CODE)
        (detection,) = DeterritorializationEngine().detect_rigidity(path)
        return detection

    def test_rigidity_result_has_type(self, detection):
        assert detection.rigidity_type is RigidityType.DEEP_NESTING

    def test_rigidity_result_has_location(self, detection):
        assert detection.file_path.endswith("nested.py")
        assert detection.line_number == 2
        assert "def outer" in detection.context

    def test_rigidity_result_has_severity(self, detection):
        # depth 6 with threshold 4 -> (6 - 4) / 4
        assert detection.severity == pytest.approx(0.5)

    def test_str_representation(self, detection):
        text = str(detection)
        assert text.startswith("deep_nesting at ")
        assert "severity: 0.50" in text


class TestLineOfFlight:
    """Test line of flight proposal."""

    def test_identify_line_of_flight(self, tmp_path):
        engine = DeterritorializationEngine()
        engine.detect_rigidity(_write(tmp_path, "nested.py", DEEP_NESTING_CODE))
        flights = engine.propose_lines_of_flight(min_severity=0.0)
        assert len(flights) == 1
        flight = flights[0]
        assert isinstance(flight, LineOfFlight)
        assert flight.rigidity.rigidity_type is RigidityType.DEEP_NESTING
        assert "Flatten nesting" in flight.proposed_action
        assert 0.0 <= flight.risk_level <= 1.0
        assert 0.0 <= flight.innovation_potential <= 1.0

    def test_min_severity_filters(self, tmp_path):
        engine = DeterritorializationEngine()
        engine.detect_rigidity(_write(tmp_path, "nested.py", DEEP_NESTING_CODE))
        assert engine.propose_lines_of_flight(min_severity=0.9) == []

    def test_no_rigidity_no_flights(self, tmp_path):
        engine = DeterritorializationEngine()
        engine.detect_rigidity(_write(tmp_path, "simple.py", SIMPLE_CODE))
        assert engine.propose_lines_of_flight(min_severity=0.0) == []

    @pytest.mark.parametrize("rigidity_type", list(RigidityType))
    def test_every_rigidity_type_has_strategy(self, rigidity_type):
        """Deterritorialization is purposeful: each rigidity maps to an action."""
        rigidity = RigidityDetection(
            rigidity_type=rigidity_type,
            file_path="x.py",
            line_number=1,
            severity=1.0,
            description="synthetic",
            context="",
        )
        flight = DeterritorializationEngine()._create_line_of_flight(rigidity)
        assert flight is not None
        assert flight.proposed_action
        assert flight.expected_outcome
        assert str(flight).startswith(f"Line of flight from {rigidity_type.value}")


class TestPhilosophicalFramework:
    """Test deterritorialization force calculation."""

    def test_force_positive_when_innovation_dominates(self):
        engine = DeterritorializationEngine()
        assert engine.calculate_deterritorialization_force(0.2, 0.7) == pytest.approx(0.5)

    def test_force_negative_when_rigidity_dominates(self):
        engine = DeterritorializationEngine()
        assert engine.calculate_deterritorialization_force(0.8, 0.3) == pytest.approx(-0.5)

    def test_force_equilibrium(self):
        engine = DeterritorializationEngine()
        assert engine.calculate_deterritorialization_force(0.4, 0.4) == pytest.approx(0.0)


class TestIntegration:
    """Test full analysis workflow."""

    def test_full_analysis_workflow(self, tmp_path):
        _write(tmp_path, "nested.py", DEEP_NESTING_CODE)
        _write(tmp_path, "god.py", _god_class_code())
        engine = DeterritorializationEngine()

        rigidities = engine.detect_rigidity(tmp_path)
        assert len(rigidities) == 2

        flights = engine.propose_lines_of_flight(min_severity=0.0)
        assert len(flights) == 2

        stats = engine.get_stats()
        assert stats["total_rigidities"] == 2
        assert stats["rigidity_by_type"] == {"deep_nesting": 1, "god_class": 1}
        assert stats["lines_of_flight"] == 2
        assert 0.0 < stats["average_severity"] <= 1.0

        report = engine.export_report()
        assert {r["type"] for r in report["rigidities"]} == {"deep_nesting", "god_class"}
        assert len(report["lines_of_flight"]) == 2
        assert report["stats"] == stats
        assert "timestamp" in report

    def test_empty_stats(self):
        stats = DeterritorializationEngine().get_stats()
        assert stats == {
            "total_rigidities": 0,
            "rigidity_by_type": {},
            "average_severity": 0.0,
            "lines_of_flight": 0,
            "high_priority_rigidities": 0,
        }
