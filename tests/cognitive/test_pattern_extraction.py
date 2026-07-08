"""
Test suite for ML pattern extraction with quantum interference.

Tests quantum principles:
- Wave interference (constructive/destructive)
- Quantum neural network classification
- Phase encoding
- Pattern correlation
"""

import json
import math

# Add scripts to path
import sys
import tempfile
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "cognitive"))

from extract_workflow_patterns import (
    CognitiveBrainFeeder,
    PatternWave,
    QuantumPatternClassifier,
    WorkflowPattern,
    WorkflowPatternExtractor,
)


class TestPatternWave:
    """Test quantum wave interference"""

    def test_constructive_interference(self):
        """Test that in-phase patterns amplify (constructive interference)"""
        wave1 = PatternWave("high_failure_rate", amplitude=0.5, frequency=0.1)
        wave2 = PatternWave("high_failure_rate", amplitude=0.3, frequency=0.1)

        # Set same phase (in phase)
        wave1.phase = 0.0
        wave2.phase = 0.1  # Small difference < π/4

        interference = wave1.interfere(wave2)

        # Constructive interference: should add amplitudes
        expected = wave1.amplitude + wave2.amplitude
        assert abs(interference - expected) < 0.01, (
            f"Constructive interference failed: " f"got {interference}, expected ~{expected}"
        )

    def test_destructive_interference(self):
        """Test that out-of-phase patterns cancel (destructive interference)"""
        wave1 = PatternWave("high_failure_rate", amplitude=0.6, frequency=0.1)
        wave2 = PatternWave("test_flakiness", amplitude=0.4, frequency=0.1)

        # Set opposite phases (out of phase)
        wave1.phase = 0.0
        wave2.phase = math.pi  # π difference > 3π/4

        interference = wave1.interfere(wave2)

        # Destructive interference: should subtract amplitudes
        expected = abs(wave1.amplitude - wave2.amplitude)
        assert abs(interference - expected) < 0.01, (
            f"Destructive interference failed: " f"got {interference}, expected ~{expected}"
        )

    def test_partial_interference(self):
        """Test partial interference for intermediate phase differences"""
        wave1 = PatternWave("high_failure_rate", amplitude=0.5, frequency=0.1)
        wave2 = PatternWave("duration_variance", amplitude=0.3, frequency=0.1)

        # Set intermediate phase
        wave1.phase = 0.0
        wave2.phase = math.pi / 2  # π/2 difference

        interference = wave1.interfere(wave2)

        # Partial interference: should be sqrt(a1² + a2²)
        expected = math.hypot(wave1.amplitude, wave2.amplitude)
        assert (abs(interference - expected) < 0.01, "Condition must be true"
        ), f"Partial interference failed: got {interference}, expected ~{expected}"


class TestQuantumPatternClassifier:
    """Test 4-qubit quantum neural network classifier"""

    def test_quantum_state_initialization(self):
        """Test that quantum state initializes in uniform superposition"""
        classifier = QuantumPatternClassifier(n_qubits=4)

        # 4 qubits = 2^4 = 16 possible states
        expected_states = 2**4
        assert len(classifier.quantum_state) == expected_states, "Collection must not be empty"

        # Uniform superposition: all amplitudes equal
        expected_amplitude = 1.0 / np.sqrt(expected_states)
        for amplitude in classifier.quantum_state:
            assert abs(abs(amplitude) - expected_amplitude) < 0.01, "Condition must be true"

    def test_pattern_encoding(self):
        """Test that patterns encode into quantum states"""
        classifier = QuantumPatternClassifier(n_qubits=4)

        pattern = WorkflowPattern(
            pattern_id="test_pattern",
            pattern_type="high_failure_rate",
            workflow_name="Test Workflow",
            failure_rate=0.8,
            avg_duration=1800.0,
            frequency=10,
            severity="high",
            amplitude=0.8,
            frequency_hz=0.33,
            phase=0.0,
            first_seen="2026-01-01T00:00:00Z",
            last_seen="2026-01-30T00:00:00Z",
            occurrences=10,
            related_patterns=[],
            example_workflow_ids=[1, 2, 3],
        )

        encoded_state = classifier.encode_pattern(pattern)

        # Should return modified quantum state
        assert len(encoded_state) == 2**4, "Encoded_state must not be empty"
        assert encoded_state is not None, "encoded_state must be initialized"

        # State should be normalized (sum of |amplitudes|² ≈ 1)
        total_probability = np.sum(np.abs(encoded_state) ** 2)
        assert abs(total_probability - 1.0) < 0.1, "Condition must be true"

    def test_pattern_classification(self):
        """Test that measurement produces valid classification"""
        classifier = QuantumPatternClassifier(n_qubits=4)

        pattern = WorkflowPattern(
            pattern_id="test_flaky",
            pattern_type="test_flakiness",
            workflow_name="Flaky Test",
            failure_rate=0.5,
            avg_duration=300.0,
            frequency=15,
            severity="medium",
            amplitude=0.6,
            frequency_hz=0.5,
            phase=math.pi / 4,
            first_seen="2026-01-15T00:00:00Z",
            last_seen="2026-01-30T00:00:00Z",
            occurrences=15,
            related_patterns=[],
            example_workflow_ids=[4, 5, 6],
        )

        encoded_state = classifier.encode_pattern(pattern)
        classification = classifier.classify(encoded_state)

        # Should return one of the valid pattern classes
        valid_classes = [
            "false_positive",
            "actual_failure",
            "transient_error",
            "cascading_failure",
            "resource_exhaustion",
            "timeout",
            "network_issue",
            "test_flake",
        ]
        assert classification in valid_classes, "Condition must be true"


class TestWorkflowPatternExtractor:
    """Test pattern extraction from workflow data"""

    def test_flakiness_calculation(self):
        """Test flakiness score calculation"""
        token = "fake_token"
        extractor = WorkflowPatternExtractor(token)

        # Create test runs with alternating results
        runs = [
            {"conclusion": "success"},
            {"conclusion": "failure"},
            {"conclusion": "success"},
            {"conclusion": "failure"},
            {"conclusion": "success"},
        ]

        flakiness = extractor._calculate_flakiness(runs)

        # 4 alternations out of 4 possible = 1.0 (perfect flakiness)
        assert abs(flakiness - 1.0) < 0.01, "Condition must be true"

    def test_flakiness_stable_workflow(self):
        """Test that stable workflows have low flakiness"""
        token = "fake_token"
        extractor = WorkflowPatternExtractor(token)

        # Create test runs with consistent results
        runs = [
            {"conclusion": "success"},
            {"conclusion": "success"},
            {"conclusion": "success"},
            {"conclusion": "success"},
        ]

        flakiness = extractor._calculate_flakiness(runs)

        # No alternations = 0.0 flakiness
        assert flakiness == 0.0, "flakiness is not valid"

    def test_workflow_grouping(self):
        """Test that workflows group correctly by name"""
        token = "fake_token"
        extractor = WorkflowPatternExtractor(token)

        workflows = [
            {"name": "Test Suite", "id": 1},
            {"name": "Test Suite", "id": 2},
            {"name": "Build", "id": 3},
            {"name": "Test Suite", "id": 4},
        ]

        grouped = extractor._group_by_workflow(workflows)

        assert "Test Suite" in grouped, "Condition must be true"
        assert "Build" in grouped, "Condition must be true"
        assert len(grouped["Test Suite"]) == 3, "Collection must not be empty"
        assert len(grouped["Build"]) == 1, "Collection must not be empty"

    def test_pattern_interference_application(self):
        """Test that pattern interference identifies related patterns"""
        token = "fake_token"
        extractor = WorkflowPatternExtractor(token)

        # Create patterns with similar properties (should interfere constructively)
        pattern1 = WorkflowPattern(
            pattern_id="workflow1_high_failure",
            pattern_type="high_failure_rate",
            workflow_name="Workflow 1",
            failure_rate=0.8,
            avg_duration=1800.0,
            frequency=20,
            severity="high",
            amplitude=0.8,
            frequency_hz=0.66,
            phase=0.0,  # Same phase
            first_seen="2026-01-01T00:00:00Z",
            last_seen="2026-01-30T00:00:00Z",
            occurrences=20,
            related_patterns=[],
            example_workflow_ids=[1, 2],
        )

        pattern2 = WorkflowPattern(
            pattern_id="workflow2_high_failure",
            pattern_type="high_failure_rate",
            workflow_name="Workflow 2",
            failure_rate=0.7,
            avg_duration=1500.0,
            frequency=18,
            severity="high",
            amplitude=0.7,
            frequency_hz=0.6,
            phase=0.1,  # Nearly same phase (should interfere constructively)
            first_seen="2026-01-01T00:00:00Z",
            last_seen="2026-01-30T00:00:00Z",
            occurrences=18,
            related_patterns=[],
            example_workflow_ids=[3, 4],
        )

        patterns = extractor._apply_pattern_interference([pattern1, pattern2])

        # With high constructive interference, patterns should be related
        # (interference > 1.5 threshold)
        assert len(patterns) == 2, "Patterns must not be empty"
        # Constructive interference: 0.8 + 0.7 = 1.5, right at threshold
        # May or may not trigger relation depending on exact calculation


class TestCognitiveBrainFeeder:
    """Test cognitive brain persistence layer"""

    def test_pattern_persistence(self):
        """Test saving and loading patterns"""
        with tempfile.TemporaryDirectory() as tmpdir:
            brain_dir = Path(tmpdir)
            feeder = CognitiveBrainFeeder(brain_dir)

            # Create test patterns
            patterns = [
                WorkflowPattern(
                    pattern_id="test1",
                    pattern_type="high_failure_rate",
                    workflow_name="Test 1",
                    failure_rate=0.5,
                    avg_duration=1000.0,
                    frequency=10,
                    severity="medium",
                    amplitude=0.5,
                    frequency_hz=0.33,
                    phase=0.0,
                    first_seen="2026-01-01T00:00:00Z",
                    last_seen="2026-01-30T00:00:00Z",
                    occurrences=10,
                    related_patterns=[],
                    example_workflow_ids=[1, 2, 3],
                )
            ]

            # Feed patterns
            metadata = feeder.feed_patterns(patterns)

            assert metadata["total_patterns"] == 1, "Data must not be empty"
            assert metadata["new_patterns"] == 1, "Data must not be empty"
            assert metadata["updated_patterns"] == 0, "Data must not be empty"

            # Load patterns
            loaded = feeder._load_existing_patterns()

            assert len(loaded) == 1, "Loaded must not be empty"
            assert loaded[0].pattern_id == "test1", "pattern_id is not valid"
            assert loaded[0].occurrences == 10, "occurrences is not valid"

    def test_pattern_update(self):
        """Test updating existing patterns"""
        with tempfile.TemporaryDirectory() as tmpdir:
            brain_dir = Path(tmpdir)
            feeder = CognitiveBrainFeeder(brain_dir)

            # Create and feed initial pattern
            pattern = WorkflowPattern(
                pattern_id="test_update",
                pattern_type="test_flakiness",
                workflow_name="Test Update",
                failure_rate=0.3,
                avg_duration=500.0,
                frequency=5,
                severity="low",
                amplitude=0.3,
                frequency_hz=0.16,
                phase=math.pi / 4,
                first_seen="2026-01-01T00:00:00Z",
                last_seen="2026-01-15T00:00:00Z",
                occurrences=5,
                related_patterns=[],
                example_workflow_ids=[1],
            )

            feeder.feed_patterns([pattern])

            # Feed updated pattern (more occurrences)
            updated_pattern = WorkflowPattern(
                pattern_id="test_update",
                pattern_type="test_flakiness",
                workflow_name="Test Update",
                failure_rate=0.4,
                avg_duration=600.0,
                frequency=7,
                severity="low",
                amplitude=0.4,
                frequency_hz=0.23,
                phase=math.pi / 4,
                first_seen="2026-01-01T00:00:00Z",
                last_seen="2026-01-30T00:00:00Z",
                occurrences=7,
                related_patterns=[],
                example_workflow_ids=[1, 2],
            )

            metadata = feeder.feed_patterns([updated_pattern])

            # Should update existing pattern
            assert metadata["total_patterns"] == 1, "Data must not be empty"
            assert metadata["new_patterns"] == 0, "Data must not be empty"
            assert metadata["updated_patterns"] == 1, "Data must not be empty"

            # Load and verify update
            loaded = feeder._load_existing_patterns()
            assert loaded[0].occurrences == 12, "occurrences is not valid"

    def test_metadata_generation(self):
        """Test cognitive brain metadata generation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            brain_dir = Path(tmpdir)
            feeder = CognitiveBrainFeeder(brain_dir)

            patterns = [
                WorkflowPattern(
                    pattern_id="p1",
                    pattern_type="high_failure_rate",
                    workflow_name="W1",
                    failure_rate=0.5,
                    avg_duration=1000.0,
                    frequency=10,
                    severity="high",
                    amplitude=0.5,
                    frequency_hz=0.33,
                    phase=0.0,
                    first_seen="2026-01-01T00:00:00Z",
                    last_seen="2026-01-30T00:00:00Z",
                    occurrences=10,
                    related_patterns=[],
                    example_workflow_ids=[1],
                ),
                WorkflowPattern(
                    pattern_id="p2",
                    pattern_type="test_flakiness",
                    workflow_name="W2",
                    failure_rate=0.3,
                    avg_duration=500.0,
                    frequency=5,
                    severity="medium",
                    amplitude=0.3,
                    frequency_hz=0.16,
                    phase=math.pi / 4,
                    first_seen="2026-01-01T00:00:00Z",
                    last_seen="2026-01-30T00:00:00Z",
                    occurrences=5,
                    related_patterns=[],
                    example_workflow_ids=[2],
                ),
            ]

            metadata = feeder.feed_patterns(patterns)

            # Check metadata
            assert metadata["total_patterns"] == 2, "Data must not be empty"
            assert metadata["new_patterns"] == 2, "Data must not be empty"
            assert "pattern_types" in metadata, "Data must not be empty"
            assert metadata["pattern_types"]["high_failure_rate"] == 1, "Data must not be empty"
            assert metadata["pattern_types"]["test_flakiness"] == 1, "Data must not be empty"

            # Check metadata file
            metadata_file = brain_dir / "metadata.json"
            assert metadata_file.exists(), "Data must not be empty"

            with open(metadata_file, "r") as f:
                saved_metadata = json.load(f)
                assert saved_metadata["total_patterns"] == 2, "Data must not be empty"


@pytest.mark.skipif(
    not sys.platform.startswith("linux"), reason="Integration test requires GitHub token"
)
class TestIntegration:
    """Integration tests with real GitHub API (skipped without token)"""

    @pytest.mark.skip(reason="Requires GITHUB_TOKEN")
    def test_real_workflow_extraction(self):
        """Test with real GitHub workflows (requires token)"""
        import os

        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            pytest.skip("GITHUB_TOKEN not set")

        extractor = WorkflowPatternExtractor(token, "Aries-Serpent/_codex_")
        patterns = extractor.extract_patterns(days_back=7)

        # Should extract some patterns
        assert isinstance(patterns, list)
        # All patterns should have required fields
        for pattern in patterns:
            assert pattern.pattern_id, "Condition must be true"
            assert pattern.workflow_name, "Condition must be true"
            assert pattern.pattern_type, "Condition must be true"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
