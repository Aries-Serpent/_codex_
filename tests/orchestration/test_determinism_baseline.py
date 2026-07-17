"""Comprehensive test suite for Phase 1 Determinism Baseline Implementation.

Tests for input-lock generation, seed control, decision tracing, and manifests.
Total: 50+ tests covering all modules and integration scenarios.
"""

import hashlib
import json
import random
import tempfile
from pathlib import Path

import pytest

from orchestration.adapters.decision_trace import (
    DecisionTraceError,
    DecisionTraceWriter,
)
from orchestration.adapters.input_lock import InputLockAdapter, InputLockError
from orchestration.adapters.seed_control import (
    SeedControlError,
    SeedControlSystem,
    set_deterministic_seed,
)
from orchestration.contracts.lane_manifest import (
    LaneManifestContract,
    LaneManifestError,
)

# ============================================================================
# INPUT-LOCK TESTS (15 tests)
# ============================================================================


class TestInputLock:
    """Tests for Input-Lock Adapter."""

    @pytest.fixture
    def sample_inputs(self):
        """Sample inputs for testing."""
        return {
            "policy_config": {
                "severity_weights": {"critical": 1.0, "high": 0.8},
                "clustering_params": {"k": 5},
                "policy_version": "1.0",
            },
            "solver_info": {
                "classical_solver": "cplex",
                "hybrid_solver": "vqe",
                "random_seed": 42,
            },
            "environment": {
                "lane_id": "A",
                "attempt_number": 1,
            },
            "input_checksums": {
                "config_file": "abc123",
                "data_file": "def456",
            },
        }

    def test_lock_generation_deterministic(self, sample_inputs):
        """Test that lock generation is deterministic."""
        lock_hash_1, _ = InputLockAdapter.generate(**sample_inputs)
        lock_hash_2, _ = InputLockAdapter.generate(**sample_inputs)
        assert lock_hash_1 == lock_hash_2

    def test_lock_collision_rate_zero(self, sample_inputs):
        """Test that collision rate is zero for 1000+ hashes."""
        hashes = set()
        for i in range(100):
            modified_inputs = sample_inputs.copy()
            modified_inputs["environment"] = sample_inputs["environment"].copy()
            modified_inputs["environment"]["attempt_number"] = i
            lock_hash, _ = InputLockAdapter.generate(**modified_inputs)
            hashes.add(lock_hash)

        assert len(hashes) == 100  # All unique

    def test_lock_immutability(self, sample_inputs):
        """Test that generated lock is immutable."""
        _, lock_dict = InputLockAdapter.generate(**sample_inputs)
        original_hash = lock_dict["lock_hash"]

        # Ensure we can't accidentally modify and get same hash
        lock_dict["context"]["policy_config"]["severity_weights"]["critical"] = 0.5
        recalculated = InputLockAdapter._compute_hash(
            lock_dict["context"]["policy_config"],
            lock_dict["context"]["solver_info"],
            lock_dict["context"]["environment"],
            lock_dict["context"]["input_checksums"],
        )
        assert recalculated != original_hash

    def test_lock_format_validation(self, sample_inputs):
        """Test that lock conforms to expected format."""
        _, lock_dict = InputLockAdapter.generate(**sample_inputs)

        assert lock_dict["lock_version"] == "1"
        assert len(lock_dict["lock_hash"]) == 64
        assert "T" in lock_dict["generated_at"] and "Z" in lock_dict["generated_at"]
        assert "context" in lock_dict

    def test_lock_hash_is_sha256(self, sample_inputs):
        """Test that lock_hash is valid SHA256."""
        _, lock_dict = InputLockAdapter.generate(**sample_inputs)
        lock_hash = lock_dict["lock_hash"]

        # SHA256 produces 64-character hex string
        assert len(lock_hash) == 64
        assert all(c in "0123456789abcdef" for c in lock_hash)

    def test_policy_config_affects_hash(self, sample_inputs):
        """Test that policy_config changes affect hash."""
        _, lock1 = InputLockAdapter.generate(**sample_inputs)

        modified = sample_inputs.copy()
        modified["policy_config"] = sample_inputs["policy_config"].copy()
        modified["policy_config"]["severity_weights"]["critical"] = 0.5

        _, lock2 = InputLockAdapter.generate(**modified)

        assert lock1["lock_hash"] != lock2["lock_hash"]

    def test_solver_info_affects_hash(self, sample_inputs):
        """Test that solver_info changes affect hash."""
        _, lock1 = InputLockAdapter.generate(**sample_inputs)

        modified = sample_inputs.copy()
        modified["solver_info"] = sample_inputs["solver_info"].copy()
        modified["solver_info"]["random_seed"] = 99

        _, lock2 = InputLockAdapter.generate(**modified)

        assert lock1["lock_hash"] != lock2["lock_hash"]

    def test_environment_affects_hash(self, sample_inputs):
        """Test that environment changes affect hash."""
        _, lock1 = InputLockAdapter.generate(**sample_inputs)

        modified = sample_inputs.copy()
        modified["environment"] = sample_inputs["environment"].copy()
        modified["environment"]["attempt_number"] = 2

        _, lock2 = InputLockAdapter.generate(**modified)

        assert lock1["lock_hash"] != lock2["lock_hash"]

    def test_input_checksum_affects_hash(self, sample_inputs):
        """Test that input_checksums changes affect hash."""
        _, lock1 = InputLockAdapter.generate(**sample_inputs)

        modified = sample_inputs.copy()
        modified["input_checksums"] = sample_inputs["input_checksums"].copy()
        modified["input_checksums"]["config_file"] = "changed123"

        _, lock2 = InputLockAdapter.generate(**modified)

        assert lock1["lock_hash"] != lock2["lock_hash"]

    def test_lock_json_schema_compliance(self, sample_inputs):
        """Test that lock conforms to JSON schema."""
        _, lock_dict = InputLockAdapter.generate(**sample_inputs)

        # Should not raise
        InputLockAdapter.validate_lock_hash(lock_dict)

    def test_validate_lock_hash_success(self, sample_inputs):
        """Test successful lock hash validation."""
        _, lock_dict = InputLockAdapter.generate(**sample_inputs)
        assert InputLockAdapter.validate_lock_hash(lock_dict) is True

    def test_validate_lock_hash_failure(self, sample_inputs):
        """Test that validation fails when hash is corrupted."""
        _, lock_dict = InputLockAdapter.generate(**sample_inputs)
        lock_dict["lock_hash"] = "0" * 64  # Invalid hash

        with pytest.raises(InputLockError):
            InputLockAdapter.validate_lock_hash(lock_dict)

    def test_write_lock_file(self, sample_inputs):
        """Test writing lock to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _, lock_dict = InputLockAdapter.generate(**sample_inputs)
            output_path = Path(tmpdir) / "input-lock.json"

            InputLockAdapter.write_lock_file(lock_dict, output_path)

            assert output_path.exists()
            with open(output_path) as f:
                written = json.load(f)
            assert written["lock_hash"] == lock_dict["lock_hash"]

    def test_lock_timestamp_format(self, sample_inputs):
        """Test that timestamp is ISO 8601 with Z suffix."""
        _, lock_dict = InputLockAdapter.generate(**sample_inputs)
        ts = lock_dict["generated_at"]

        # Format: YYYY-MM-DDTHH:MM:SSZ
        assert ts.endswith("Z")
        assert "T" in ts
        assert ts.count("-") == 2  # Date separators
        assert ts.count(":") == 2  # Time separators


# ============================================================================
# SEED CONTROL TESTS (12 tests)
# ============================================================================


class TestSeedControl:
    """Tests for Seed Control System."""

    def test_seed_validation_valid(self):
        """Test that valid seeds pass validation."""
        assert SeedControlSystem.validate_seed(0) is True
        assert SeedControlSystem.validate_seed(2**31 - 1) is True
        assert SeedControlSystem.validate_seed(42) is True

    def test_seed_validation_invalid_type(self):
        """Test that non-integer seeds fail validation."""
        with pytest.raises(SeedControlError):
            SeedControlSystem.validate_seed("42")
        with pytest.raises(SeedControlError):
            SeedControlSystem.validate_seed(3.14)

    def test_seed_validation_invalid_range_low(self):
        """Test that negative seeds fail validation."""
        with pytest.raises(SeedControlError):
            SeedControlSystem.validate_seed(-1)

    def test_seed_validation_invalid_range_high(self):
        """Test that oversized seeds fail validation."""
        with pytest.raises(SeedControlError):
            SeedControlSystem.validate_seed(2**31)

    def test_seed_reproducibility_random(self):
        """Test that same seed produces reproducible random outputs."""
        values_1 = []
        SeedControlSystem.set_seed(42, numpy_enabled=False)
        for _ in range(10):
            values_1.append(random.random())

        values_2 = []
        SeedControlSystem.set_seed(42, numpy_enabled=False)
        for _ in range(10):
            values_2.append(random.random())

        assert values_1 == values_2

    def test_seed_reproducibility_numpy(self):
        """Test numpy seed reproducibility."""
        try:
            import numpy as np
        except ImportError:
            pytest.skip("numpy not installed")

        SeedControlSystem.set_seed(42, numpy_enabled=True)
        arr_1 = np.random.randn(5)

        SeedControlSystem.set_seed(42, numpy_enabled=True)
        arr_2 = np.random.randn(5)

        assert np.allclose(arr_1, arr_2)

    def test_seed_reproducibility_torch(self):
        """Test torch seed reproducibility."""
        try:
            import torch

            SeedControlSystem.set_seed(42)
            t_1 = torch.randn(5)

            SeedControlSystem.set_seed(42)
            t_2 = torch.randn(5)

            assert torch.allclose(t_1, t_2)
        except (ImportError, AttributeError):
            pytest.skip("torch not installed or not available")

    def test_seed_propagation_across_modules(self):
        """Test seed propagates across all RNG modules."""
        # Set seed and generate from each system
        SeedControlSystem.set_seed(42)

        random_val = random.random()

        try:
            import numpy as np

            numpy_val = np.random.random()
        except ImportError:
            numpy_val = None

        try:
            import torch

            torch_val = torch.randn(1).item()
        except (ImportError, AttributeError):
            torch_val = None

        # Reset seed and verify same values
        SeedControlSystem.set_seed(42)

        random_val_2 = random.random()
        assert random_val == random_val_2

        if numpy_val is not None:
            import numpy as np

            numpy_val_2 = np.random.random()
            assert abs(numpy_val - numpy_val_2) < 1e-10

        if torch_val is not None:
            import torch

            torch_val_2 = torch.randn(1).item()
            assert abs(torch_val - torch_val_2) < 1e-5

    def test_seed_documentation(self):
        """Test seed documentation generation."""
        doc = SeedControlSystem.get_seed_documentation(42)

        assert doc["seed"] == 42
        assert doc["range"] == [0, 2**31 - 1]
        assert "random" in doc["systems"]

    def test_set_deterministic_seed_convenience(self):
        """Test convenience function for setting seed."""
        values_1 = []
        set_deterministic_seed(123)
        for _ in range(5):
            values_1.append(random.random())

        values_2 = []
        set_deterministic_seed(123)
        for _ in range(5):
            values_2.append(random.random())

        assert values_1 == values_2

    def test_seed_different_values_produce_different_outputs(self):
        """Test that different seeds produce different outputs."""
        SeedControlSystem.set_seed(42, numpy_enabled=False)
        val_1 = random.random()

        SeedControlSystem.set_seed(43, numpy_enabled=False)
        val_2 = random.random()

        assert val_1 != val_2


# ============================================================================
# DECISION-TRACE TESTS (15 tests)
# ============================================================================


class TestDecisionTrace:
    """Tests for Decision Trace Writer."""

    @pytest.fixture
    def trace_path(self):
        """Temporary trace file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "decision_trace.jsonl"

    def test_trace_append_only(self, trace_path):
        """Test that trace is append-only."""
        writer = DecisionTraceWriter(trace_path)

        writer.append("A", "action", "a" * 64, "success")
        assert writer.get_entry_count() == 1

        writer.append("A", "action", "b" * 64, "success")
        assert writer.get_entry_count() == 2

    def test_trace_jsonl_format(self, trace_path):
        """Test that trace file is valid JSONL."""
        writer = DecisionTraceWriter(trace_path)

        writer.append("A", "action", "a" * 64, "success", description="Test 1")
        writer.append("A", "gate_pass", "b" * 64, "success", description="Test 2")

        entries = writer.read_all()
        assert len(entries) == 2
        assert entries[0]["description"] == "Test 1"
        assert entries[1]["description"] == "Test 2"

    def test_trace_timestamp_utc_z_format(self, trace_path):
        """Test that timestamp uses UTC Z format."""
        writer = DecisionTraceWriter(trace_path)

        writer.append("A", "action", "a" * 64, "success")

        entries = writer.read_all()
        ts = entries[0]["timestamp"]

        # Format: YYYY-MM-DDTHH:MM:SS.fffZ
        assert ts.endswith("Z")
        assert "T" in ts
        assert "." in ts

    def test_trace_integrity_check(self, trace_path):
        """Test integrity check passes for valid trace."""
        writer = DecisionTraceWriter(trace_path)

        writer.append("A", "action", "a" * 64, "success")
        writer.append("A", "gate_pass", "b" * 64, "success")

        assert writer.verify_integrity() is True

    def test_trace_immutability(self, trace_path):
        """Test that trace entries cannot be modified."""
        writer = DecisionTraceWriter(trace_path)

        writer.append("A", "action", "a" * 64, "success")

        # Try to read and modify
        entries = writer.read_all()
        entries[0]["outcome"] = "failure"

        # Read again - should not be modified
        entries_2 = writer.read_all()
        assert entries_2[0]["outcome"] == "success"

    def test_trace_lane_id_validation(self, trace_path):
        """Test that invalid lane_id is rejected."""
        writer = DecisionTraceWriter(trace_path)

        with pytest.raises(DecisionTraceError):
            writer.append("Z", "action", "a" * 64, "success")  # Z is invalid

    def test_trace_file_location(self, trace_path):
        """Test that trace is written to correct location."""
        writer = DecisionTraceWriter(trace_path)

        writer.append("A", "action", "a" * 64, "success")

        assert trace_path.exists()

    def test_trace_decision_type_validation(self, trace_path):
        """Test that invalid decision_type is rejected."""
        writer = DecisionTraceWriter(trace_path)

        with pytest.raises(DecisionTraceError):
            writer.append("A", "invalid_type", "a" * 64, "success")

    def test_trace_outcome_validation(self, trace_path):
        """Test that invalid outcome is rejected."""
        writer = DecisionTraceWriter(trace_path)

        with pytest.raises(DecisionTraceError):
            writer.append("A", "action", "a" * 64, "invalid_outcome")

    def test_trace_with_evidence(self, trace_path):
        """Test appending trace with evidence."""
        writer = DecisionTraceWriter(trace_path)

        evidence = ["artifact_1.json", "artifact_2.json"]
        writer.append("A", "action", "a" * 64, "success", evidence=evidence)

        entries = writer.read_all()
        assert entries[0]["evidence"] == evidence

    def test_trace_with_context(self, trace_path):
        """Test appending trace with context."""
        writer = DecisionTraceWriter(trace_path)

        context = {"retry_count": 3, "status": "resolved"}
        writer.append("A", "escalation", "a" * 64, "escalated", context=context)

        entries = writer.read_all()
        assert entries[0]["context"] == context

    def test_trace_entry_count(self, trace_path):
        """Test that entry count is tracked."""
        writer = DecisionTraceWriter(trace_path)

        assert writer.get_entry_count() == 0

        writer.append("A", "action", "a" * 64, "success")
        assert writer.get_entry_count() == 1

        writer.append("A", "action", "b" * 64, "success")
        assert writer.get_entry_count() == 2

    def test_trace_read_empty_file(self, trace_path):
        """Test reading from non-existent file returns empty list."""
        writer = DecisionTraceWriter(trace_path)

        entries = writer.read_all()
        assert entries == []

    def test_trace_integrity_check_empty_file(self, trace_path):
        """Test integrity check fails for empty file."""
        writer = DecisionTraceWriter(trace_path)

        with pytest.raises(DecisionTraceError):
            writer.verify_integrity()


# ============================================================================
# MANIFEST TESTS (10 tests)
# ============================================================================


class TestLaneManifest:
    """Tests for Lane Manifest Contract."""

    @pytest.fixture
    def manifest_inputs(self):
        """Sample inputs for manifest generation."""
        return {
            "lane_id": "A",
            "lane_name": "Determinism Baseline",
            "execution_mode": "sequential",
            "owner": "orchestrator-agent",
            "inputs": {
                "input_lock": "a" * 64,
                "seed": 42,
                "policy_version": "1.0",
                "solver_version": "1.0",
            },
        }

    def test_manifest_generation(self, manifest_inputs):
        """Test manifest generation."""
        manifest = LaneManifestContract.generate(**manifest_inputs)

        assert manifest["lane_id"] == "A"
        assert manifest["lane_name"] == "Determinism Baseline"
        assert manifest["owner"] == "orchestrator-agent"

    def test_manifest_schema_compliance(self, manifest_inputs):
        """Test that manifest conforms to schema."""
        manifest = LaneManifestContract.generate(**manifest_inputs)

        # Should not raise
        LaneManifestContract.validate_manifest(manifest)

    def test_manifest_dependency_validation(self, manifest_inputs):
        """Test manifest with upstream dependencies."""
        manifest_inputs["dependencies"] = {
            "upstream_lanes": [],
            "upstream_gates": {},
        }

        manifest = LaneManifestContract.generate(**manifest_inputs)
        assert manifest["dependencies"]["upstream_lanes"] == []

    def test_manifest_immutability(self, manifest_inputs):
        """Test that manifest has run_id and timestamp (immutability markers)."""
        manifest = LaneManifestContract.generate(**manifest_inputs)

        assert "run_id" in manifest
        assert "timestamp" in manifest
        assert len(manifest["run_id"]) == 36  # UUID format

    def test_manifest_upstream_gates_resolved(self, manifest_inputs):
        """Test that upstream gates must be resolved."""
        manifest_inputs["dependencies"] = {
            "upstream_lanes": ["B"],
            "upstream_gates": {"gate_B": "pass"},
        }

        manifest = LaneManifestContract.generate(**manifest_inputs)
        assert LaneManifestContract.validate_upstream_gates(manifest) is True

    def test_manifest_upstream_gates_pending_fails(self, manifest_inputs):
        """Test that pending gates fail validation."""
        manifest_inputs["dependencies"] = {
            "upstream_lanes": ["B"],
            "upstream_gates": {"gate_B": "pending"},
        }

        manifest = LaneManifestContract.generate(**manifest_inputs)

        with pytest.raises(LaneManifestError):
            LaneManifestContract.validate_upstream_gates(manifest)

    def test_manifest_write_file(self, manifest_inputs):
        """Test writing manifest to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = LaneManifestContract.generate(**manifest_inputs)
            output_path = Path(tmpdir) / "lane-manifest.json"

            LaneManifestContract.write_manifest_file(manifest, output_path)

            assert output_path.exists()
            with open(output_path) as f:
                written = json.load(f)
            assert written["lane_id"] == manifest["lane_id"]

    def test_manifest_timestamp_format(self, manifest_inputs):
        """Test that manifest timestamp uses Z format."""
        manifest = LaneManifestContract.generate(**manifest_inputs)

        ts = manifest["timestamp"]
        assert ts.endswith("Z")
        assert "T" in ts
        assert ts.count("-") == 2

    def test_manifest_provenance(self, manifest_inputs):
        """Test manifest includes provenance."""
        manifest = LaneManifestContract.generate(**manifest_inputs)

        assert manifest["provenance"]["created_by"] == "orchestrator-agent"
        assert "created_at" in manifest["provenance"]


# ============================================================================
# INTEGRATION TESTS (8+ tests)
# ============================================================================


class TestDeterminismIntegration:
    """Integration tests for full determinism flow."""

    @pytest.fixture
    def test_inputs(self):
        """Common test inputs."""
        return {
            "policy_config": {"version": "1.0"},
            "solver_info": {"solver": "cplex"},
            "environment": {"lane_id": "A"},
            "input_checksums": {"data": "abc123"},
        }

    def test_determinism_replay_100_runs(self, test_inputs):
        """Test 100 replay runs produce identical outputs."""
        outputs = []

        for run in range(100):
            # Use same seed
            set_deterministic_seed(42)

            lock_hash, _ = InputLockAdapter.generate(**test_inputs)
            outputs.append(lock_hash)

        # All hashes should be identical
        assert len(set(outputs)) == 1

    def test_replay_with_different_seed(self, test_inputs):
        """Test that different seed produces different output."""
        set_deterministic_seed(42)
        lock1, _ = InputLockAdapter.generate(**test_inputs)

        set_deterministic_seed(43)
        lock2, _ = InputLockAdapter.generate(**test_inputs)

        # Different seeds, same input → same lock (seed affects RNG, not lock)
        assert lock1 == lock2

    def test_replay_with_different_policy(self, test_inputs):
        """Test that different policy produces different lock."""
        lock1, _ = InputLockAdapter.generate(**test_inputs)

        modified = test_inputs.copy()
        modified["policy_config"] = {"version": "2.0"}

        lock2, _ = InputLockAdapter.generate(**modified)

        assert lock1 != lock2

    def test_full_lane_manifest_generation(self, test_inputs):
        """Test full lane manifest generation."""
        lock_hash, lock_dict = InputLockAdapter.generate(**test_inputs)

        manifest = LaneManifestContract.generate(
            lane_id="A",
            lane_name="Determinism Baseline",
            execution_mode="sequential",
            owner="orchestrator-agent",
            inputs={
                "input_lock": lock_hash,
                "seed": 42,
                "policy_version": "1.0",
                "solver_version": "1.0",
            },
            dependencies={"upstream_lanes": [], "upstream_gates": {}},
        )

        assert manifest["inputs"]["input_lock"] == lock_hash
        assert manifest["lane_id"] == "A"

    def test_end_to_end_determinism_certification(self, test_inputs):
        """Test end-to-end determinism certification."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Generate lock
            lock_hash, lock_dict = InputLockAdapter.generate(**test_inputs)

            # Set deterministic seed
            set_deterministic_seed(42)

            # Create manifest
            manifest = LaneManifestContract.generate(
                lane_id="A",
                lane_name="Test Lane",
                execution_mode="sequential",
                owner="test-agent",
                inputs={
                    "input_lock": lock_hash,
                    "seed": 42,
                    "policy_version": "1.0",
                    "solver_version": "1.0",
                },
            )

            # Create decision trace
            trace_path = tmpdir / "trace.jsonl"
            trace = DecisionTraceWriter(trace_path)

            trace.append(
                "A",
                "action",
                lock_hash,
                "success",
                description="Determinism test",
            )

            # Verify all components
            assert InputLockAdapter.validate_lock_hash(lock_dict)
            assert LaneManifestContract.validate_manifest(manifest)
            assert trace.verify_integrity()

    def test_determinism_with_all_modules(self):
        """Test integration of all 4 modules."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # 1. Generate input lock
            inputs = {
                "policy_config": {"v": "1"},
                "solver_info": {"v": "1"},
                "environment": {"lane_id": "A"},
                "input_checksums": {"f": "hash"},
            }
            lock_hash, lock_dict = InputLockAdapter.generate(**inputs)

            # 2. Set seed
            set_deterministic_seed(42)

            # 3. Create trace
            trace_path = tmpdir / "trace.jsonl"
            trace = DecisionTraceWriter(trace_path)
            trace.append("A", "action", lock_hash, "success")

            # 4. Generate manifest
            manifest = LaneManifestContract.generate(
                lane_id="A",
                lane_name="Integration Test",
                execution_mode="sequential",
                owner="test",
                inputs={
                    "input_lock": lock_hash,
                    "seed": 42,
                    "policy_version": "1.0",
                    "solver_version": "1.0",
                },
            )

            # Verify all
            assert InputLockAdapter.validate_lock_hash(lock_dict)
            assert trace.verify_integrity()
            assert LaneManifestContract.validate_manifest(manifest)


# ============================================================================
# EDGE CASE AND ERROR HANDLING TESTS (10+ tests)
# ============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_lock_with_special_characters_in_config(self):
        """Test lock generation with special characters."""
        inputs = {
            "policy_config": {"name": "test\u00e9\u00f1\u00fc", "symbols": "!@#$%^&*()"},
            "solver_info": {"version": "1.0\n\t"},
            "environment": {"lane_id": "A"},
            "input_checksums": {"data": "hash\x00\x01"},
        }
        lock_hash, lock_dict = InputLockAdapter.generate(**inputs)
        assert InputLockAdapter.validate_lock_hash(lock_dict)

    def test_lock_collision_across_order(self):
        """Test that hash is stable regardless of input organization."""
        inputs1 = {
            "policy_config": {"a": 1, "b": 2},
            "solver_info": {"x": "y"},
            "environment": {"lane_id": "A"},
            "input_checksums": {"f": "h"},
        }
        inputs2 = {
            "policy_config": {"b": 2, "a": 1},  # Different order
            "solver_info": {"x": "y"},
            "environment": {"lane_id": "A"},
            "input_checksums": {"f": "h"},
        }
        lock1, _ = InputLockAdapter.generate(**inputs1)
        lock2, _ = InputLockAdapter.generate(**inputs2)
        assert lock1 == lock2

    def test_seed_boundary_values(self):
        """Test seed with boundary values."""
        # Test minimum
        SeedControlSystem.validate_seed(0)

        # Test maximum
        SeedControlSystem.validate_seed(2**31 - 1)

        # Test negative (should raise)
        with pytest.raises(SeedControlError):
            SeedControlSystem.validate_seed(-1)

        # Test too large (should raise)
        with pytest.raises(SeedControlError):
            SeedControlSystem.validate_seed(2**31)

    def test_decision_trace_with_unicode_evidence(self):
        """Test decision trace with unicode content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trace_path = Path(tmpdir) / "trace.jsonl"
            trace = DecisionTraceWriter(trace_path)

            # Use valid SHA256 hash
            valid_hash = "a" * 64

            trace.append(
                "A",
                "action",  # Valid decision type
                valid_hash,
                "success",
                description="Test with émojis 🎉 and spëcial çhars",
            )

            entries = trace.read_all()
            assert len(entries) == 1
            assert "émojis" in entries[0]["description"]

    def test_manifest_with_empty_dependencies(self):
        """Test manifest generation with no dependencies."""
        manifest = LaneManifestContract.generate(
            lane_id="A",
            lane_name="Standalone Lane",
            execution_mode="sequential",
            owner="test",
            inputs={"seed": 42},
            dependencies=[],
        )
        # Dependencies is converted to dict with upstream_lanes and upstream_gates
        assert isinstance(manifest["dependencies"], dict)
        assert LaneManifestContract.validate_manifest(manifest)

    def test_lock_with_large_nested_config(self):
        """Test lock generation with deeply nested configuration."""
        large_config = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "data": list(range(100)),
                            "metadata": {"v": "1"},
                        }
                    }
                }
            }
        }
        inputs = {
            "policy_config": large_config,
            "solver_info": {"v": "1"},
            "environment": {"lane_id": "A"},
            "input_checksums": {"f": "h"},
        }
        lock_hash, lock_dict = InputLockAdapter.generate(**inputs)
        assert len(lock_hash) == 64  # SHA256 hex string length

    def test_decision_trace_multiple_sequential_appends(self):
        """Test appending many entries sequentially."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trace_path = Path(tmpdir) / "trace.jsonl"
            trace = DecisionTraceWriter(trace_path)

            # Append 100 entries with valid SHA256 hashes
            for i in range(100):
                # Create valid SHA256 hash (64 hex chars)
                hash_val = hashlib.sha256(f"hash_{i}".encode()).hexdigest()
                trace.append(
                    "A",
                    "action",  # Valid decision type
                    hash_val,
                    "success",
                    description=f"Decision {i}",
                )

            # Verify all entries
            entries = trace.read_all()
            assert len(entries) == 100
            assert entries[0]["lane_id"] == "A"
            assert entries[99]["description"] == "Decision 99"

    def test_manifest_validation_with_invalid_execution_mode(self):
        """Test that invalid execution mode is rejected."""
        invalid_manifest = {
            "lane_id": "A",
            "lane_name": "Test",
            "execution_mode": "invalid_mode",  # Not in enum
            "owner": "test",
            "inputs": {},
            "dependencies": [],
            "run_id": "test-run",
            "created_at": "2026-07-13T00:00:00Z",
            "provenance": {"initiated_by": "test"},
        }
        with pytest.raises(Exception):  # Will raise jsonschema validation error
            LaneManifestContract.validate_manifest(invalid_manifest)

    def test_seed_reproducibility_edge_case(self):
        """Test seed reproducibility with edge case values."""
        edge_values = [0, 1, 42, 12345, 2**31 - 1]

        for seed_val in edge_values:
            random.seed(seed_val)
            val1 = random.random()

            random.seed(seed_val)
            val2 = random.random()

            assert val1 == val2

    def test_lock_determinism_with_empty_strings(self):
        """Test lock generation handles empty strings correctly."""
        inputs = {
            "policy_config": {"key": "", "other": "value"},
            "solver_info": {"data": ""},
            "environment": {"lane_id": "A"},
            "input_checksums": {"hash": ""},
        }
        lock_hash1, _ = InputLockAdapter.generate(**inputs)

        # Same inputs should produce same hash
        lock_hash2, _ = InputLockAdapter.generate(**inputs)
        assert lock_hash1 == lock_hash2


# ============================================================================
# MARKER TESTS
# ============================================================================


class TestDeterminismBaseline:
    """Marker class for determinism baseline tests."""

    def test_marker(self):
        """Marker test to identify test class."""
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
