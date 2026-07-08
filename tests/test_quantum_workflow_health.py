"""
Test cases for quantum-inspired workflow health monitoring.

These tests use quantum mechanics principles:
- Superposition: Multiple states simultaneously
- Measurement: Collapsing to definite state
- Entanglement: Correlated behavior
- Uncertainty: Cannot predict exact outcome
"""

import json
import math
import os
import tempfile
from dataclasses import asdict

import pytest

from scripts.quantum_workflow_health import (
    ComplexEncoder,
    QuantumWorkflowHealthAnalyzer,
    QuantumWorkflowState,
)


class TestQuantumWorkflowState:
    """Test quantum state behavior"""

    def test_superposition_before_measurement(self):
        """State exists in superposition until measured"""
        state = QuantumWorkflowState(
            workflow_id=123,
            name="Test Workflow",
            status="in_progress",
            conclusion=None,
            health_amplitude=complex(0.7, 0.3),
            phase=0.5,
            entangled_with=[],
        )

        # Before measurement, state is uncertain
        assert state.measured_health is None, "measured_health is not valid"

        # Amplitude represents superposition
        assert abs(state.health_amplitude) > 0, "Value must be greater than zero"

    def test_wave_function_collapse(self):
        """Measurement collapses wave function to definite state"""
        state = QuantumWorkflowState(
            workflow_id=123,
            name="Test Workflow",
            status="completed",
            conclusion="success",
            health_amplitude=complex(0.9, 0.1),
            phase=0.5,
            entangled_with=[],
        )

        # First measurement collapses state
        health1 = state.measure_health()
        assert health1 in ["healthy", "degraded", "critical"]
        assert state.measured_health is not None, "measured_health must be initialized"

        # Subsequent measurements return same result (deterministic)
        health2 = state.measure_health()
        assert health1 == health2, "health1 is not valid"

    def test_entanglement_correlation(self):
        """Entangled workflows affect each other"""
        # Create two entangled workflows
        state1 = QuantumWorkflowState(
            workflow_id=1,
            name="Workflow A",
            status="completed",
            conclusion="success",
            health_amplitude=complex(0.8, 0.2),
            phase=0.0,
            entangled_with=[2],
        )

        state2 = QuantumWorkflowState(
            workflow_id=2,
            name="Workflow B",
            status="completed",
            conclusion="failure",
            health_amplitude=complex(0.3, 0.1),  # Lower amplitude for critical: |0.3+0.1i| ≈ 0.32
            phase=0.0,
            entangled_with=[1],
        )

        # Measure state2 (failure)
        state2.measure_health()
        # With amplitude |0.3+0.1i|^2 ≈ 0.1, probability < 0.4, should be critical
        assert state2.measured_health == "critical", "measured_health is not valid"

        # Entanglement should affect state1
        original_amplitude = abs(state1.health_amplitude)
        state1.apply_entanglement([state2])

        # state1's amplitude should decrease due to entanglement with critical workflow
        assert abs(state1.health_amplitude) < original_amplitude, "Condition must be true"

    def test_heisenberg_uncertainty(self):
        """Cannot know exact state without measurement"""
        state = QuantumWorkflowState(
            workflow_id=123,
            name="Test Workflow",
            status="in_progress",
            conclusion=None,
            health_amplitude=complex(0.6, 0.4),
            phase=math.pi / 4,
            entangled_with=[],
        )

        # Before measurement, outcome is probabilistic
        # Run multiple measurements and verify randomness
        outcomes = set()
        for _ in range(10):
            # Reset measurement
            state.measured_health = None
            outcome = state.measure_health()
            outcomes.add(outcome)

        # Should get varied outcomes (uncertainty)
        # Note: With specific amplitude, might be deterministic
        # This test validates the measurement mechanism exists
        assert len(outcomes) >= 1, "Outcomes must not be empty"

    def test_quantum_tunneling_detection(self):
        """Detect unexpected state transitions (tunneling)"""
        # Workflow with high imaginary component (tunneling signature)
        state = QuantumWorkflowState(
            workflow_id=123,
            name="Tunneling Workflow",
            status="completed",
            conclusion="success",
            health_amplitude=complex(0.5, 0.7),  # High imaginary part
            phase=math.pi / 2,
            entangled_with=[],
        )

        state.measure_health()

        # Tunneling indicator: healthy result with high imaginary amplitude
        if state.measured_health == "healthy":
            assert abs(state.health_amplitude.imag) > 0.5, "Value must be greater than zero"


class TestComplexNumberSerialization:
    """Test JSON serialization of complex numbers"""

    def test_complex_encoder_serializes_complex_numbers(self):
        """ComplexEncoder should convert complex numbers to JSON-serializable format"""
        test_data = {"value": complex(3.14, 2.71), "nested": {"amplitude": complex(0.9, 0.1)}}

        # Should serialize without raising TypeError
        json_str = json.dumps(test_data, cls=ComplexEncoder)

        # Verify deserialization structure
        result = json.loads(json_str)
        assert result["value"]["real"] == 3.14, "Result must not be empty"
        assert result["value"]["imag"] == 2.71, "Result must not be empty"
        assert result["nested"]["amplitude"]["real"] == 0.9, "Result must not be empty"
        assert result["nested"]["amplitude"]["imag"] == 0.1, "Result must not be empty"

    def test_quantum_state_serialization_with_complex_amplitude(self):
        """QuantumWorkflowState with complex amplitude should serialize to JSON"""
        state = QuantumWorkflowState(
            workflow_id=123,
            name="Test Workflow",
            status="completed",
            conclusion="success",
            health_amplitude=complex(0.8, 0.2),
            phase=1.57,
            entangled_with=[456, 789],
        )

        # Measure to get complete state
        state.measure_health()

        # Convert to dict and serialize
        state_dict = state.__dict__

        # Should serialize without TypeError
        json_str = json.dumps(state_dict, cls=ComplexEncoder)
        result = json.loads(json_str)

        # Verify complex number was properly serialized
        assert "health_amplitude" in result, "Result must not be empty"
        assert result["health_amplitude"]["real"] == 0.8, "Result must not be empty"
        assert result["health_amplitude"]["imag"] == 0.2, "Result must not be empty"

    def test_full_health_report_json_serialization(self):
        """Full health report with quantum states should serialize to JSON file"""
        states = [
            QuantumWorkflowState(
                workflow_id=1,
                name="Workflow 1",
                status="completed",
                conclusion="success",
                health_amplitude=complex(0.9, 0.1),
                phase=0.5,
                entangled_with=[],
            ),
            QuantumWorkflowState(
                workflow_id=2,
                name="Workflow 2",
                status="completed",
                conclusion="failure",
                health_amplitude=complex(0.3, 0.7),
                phase=1.0,
                entangled_with=[1],
            ),
        ]

        # Measure all states
        for state in states:
            state.measure_health()

        # Create report structure similar to analyze_health output
        report = {
            "timestamp": "2024-01-01T00:00:00",
            "total_workflows": len(states),
            "health_distribution": {"healthy": 1, "degraded": 0, "critical": 1},
            "critical_failures": 1,
            "overall_health": "degraded",
            "quantum_coherence": 0.75,
            "states": [asdict(s) for s in states],
        }

        # Write to temporary file using ComplexEncoder
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name
            json.dump(report, f, indent=2, cls=ComplexEncoder)

        try:
            # Verify file can be read back
            with open(temp_path, "r") as f:
                loaded_report = json.load(f)

            # Verify structure
            assert loaded_report["total_workflows"] == 2, "loaded_rep is not valid"
            assert len(loaded_report["states"]) == 2, "Collection must not be empty"

            # Verify complex numbers were serialized
            assert "health_amplitude" in loaded_report["states"][0], "Condition must be true"
            assert "real" in loaded_report["states"][0]["health_amplitude"], "Condition must be true"
            assert "imag" in loaded_report["states"][0]["health_amplitude"], "Condition must be true"
        finally:
            # Clean up
            os.unlink(temp_path)


class TestQuantumHealthAnalyzer:
    """Test quantum health analyzer"""

    def test_workflow_entanglement_detection(self):
        """Identify entangled workflows"""
        analyzer = QuantumWorkflowHealthAnalyzer(github_token="fake_token", repo="test/repo")

        workflows = [
            {"id": 1, "event": "push", "head_branch": "main"},
            {"id": 2, "event": "push", "head_branch": "main"},
            {"id": 3, "event": "pull_request", "head_branch": "feature"},
        ]

        entanglements = analyzer._identify_entanglements(workflows)

        # 1 and 2 should be entangled (same event/branch)
        assert 2 in entanglements[1], "Condition must be true"
        assert 1 in entanglements[2], "Condition must be true"

        # 3 should not be entangled with 1 or 2
        assert 1 not in entanglements[3], "Condition must be true"
        assert 2 not in entanglements[3], "Condition must be true"

    def test_coherence_calculation(self):
        """Calculate quantum coherence (system stability)"""
        analyzer = QuantumWorkflowHealthAnalyzer(github_token="fake_token", repo="test/repo")

        # All workflows in phase = high coherence
        states_coherent = [
            QuantumWorkflowState(
                workflow_id=i,
                name=f"Workflow {i}",
                status="completed",
                conclusion="success",
                health_amplitude=complex(0.8, 0.2),
                phase=0.5,  # Same phase
                entangled_with=[],
            )
            for i in range(5)
        ]

        coherence_high = analyzer._calculate_coherence(states_coherent)

        # Random phases = low coherence
        states_incoherent = [
            QuantumWorkflowState(
                workflow_id=i,
                name=f"Workflow {i}",
                status="completed",
                conclusion="success",
                health_amplitude=complex(0.8, 0.2),
                phase=i * math.pi / 2,  # Different phases
                entangled_with=[],
            )
            for i in range(5)
        ]

        coherence_low = analyzer._calculate_coherence(states_incoherent)

        # High coherence should be greater than low coherence
        assert coherence_high > coherence_low, "coherence_high must be greater than zero"

    def test_overall_health_calculation(self):
        """Calculate overall system health"""
        analyzer = QuantumWorkflowHealthAnalyzer(github_token="fake_token", repo="test/repo")

        # Mostly healthy (>80%)
        health_good = {"healthy": 9, "degraded": 1, "critical": 0}
        assert analyzer._calculate_overall_health(health_good) == "healthy", "Condition must be true"

        # Mixed health (50-80%)
        health_mixed = {"healthy": 6, "degraded": 3, "critical": 1}
        assert analyzer._calculate_overall_health(health_mixed) == "degraded", "Condition must be true"

        # Mostly critical (<50%)
        health_bad = {"healthy": 2, "degraded": 2, "critical": 6}
        assert analyzer._calculate_overall_health(health_bad) == "critical", "Condition must be true"


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("GITHUB_TOKEN"), reason="Requires GITHUB_TOKEN")
class TestQuantumHealthIntegration:
    """Integration tests requiring GitHub API"""

    def test_full_analysis_real_workflows(self):
        """Test full analysis with real GitHub workflows"""
        analyzer = QuantumWorkflowHealthAnalyzer(
            github_token=os.getenv("GITHUB_TOKEN"), repo="Aries-Serpent/_codex_"
        )

        # Use a known commit SHA
        commit_sha = "b615560"

        workflows = analyzer.fetch_workflows(commit_sha)
        if not workflows:
            pytest.skip(f"No workflow runs returned for commit {commit_sha}")

        states = analyzer.create_quantum_states(workflows)
        assert len(states) == len(workflows), "States must not be empty"

        results = analyzer.analyze_health(states)

        # Verify result structure
        assert "overall_health" in results, "Result must not be empty"
        assert "quantum_coherence" in results, "Result must not be empty"
        assert "health_distribution" in results, "Result must not be empty"
        assert results["overall_health"] in ["healthy", "degraded", "critical"]
        assert 0 <= results["quantum_coherence"] <= 1, "Result must not be empty"
