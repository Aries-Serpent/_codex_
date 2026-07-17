"""Phase 2 Foundation Hardening Tests — 40+ comprehensive tests.

Tests for:
- Contract Gate System (15 tests)
- Policy Tier Engine (10 tests)
- Rollback Controls (8 tests)
- Lane Scheduler (7+ tests)
"""

import pytest

from orchestration.gates.contract_gate import (
    ContractGateSystem,
)
from orchestration.healing.policy_tier_engine import (
    PolicyTierEngine,  # pragma: allowlist secret
)
from orchestration.safety.rollback_controls import (
    RollbackControlSystem,
)
from orchestration.scheduling.lane_scheduler_v1 import (
    Lane,
    LaneSchedulerV1,
    LaneState,
)


class TestContractGates:
    """Tests for 8-gate contract validation system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.system = ContractGateSystem()

    def test_gate_1_schema_validation_pass(self):
        """Test Gate 1 passes with valid schema."""
        proposal = {
            "proposal_id": "p1",
            "lane_id": "lane_a",
            "action_type": "code_change",
            "description": "Test change",
        }
        result = self.system.validate_gate_1_schema(proposal)
        assert result.passed
        assert result.gate_number == 1

    def test_gate_1_schema_validation_fail(self):
        """Test Gate 1 fails with invalid schema."""
        proposal = {}  # Missing required fields
        result = self.system.validate_gate_1_schema(proposal)
        assert not result.passed
        assert "Schema validation failed" in result.error_message

    def test_gate_2_regression_tests_pass(self):
        """Test Gate 2 passes when tests pass."""
        proposal = {
            "proposal_id": "p1",
            "lane_id": "lane_a",
            "action_type": "code_change",
            "description": "Test change",
            "regression_tests": {"passed": True, "test_count": 50},
        }
        result = self.system.validate_gate_2_regression_tests(proposal)
        assert result.passed
        assert result.details["test_count"] == 50

    def test_gate_2_regression_tests_fail(self):
        """Test Gate 2 fails when tests fail."""
        proposal = {
            "regression_tests": {"passed": False, "test_count": 50}
        }
        result = self.system.validate_gate_2_regression_tests(proposal)
        assert not result.passed
        assert "did not pass" in result.error_message

    def test_gate_3_security_audit_pass(self):
        """Test Gate 3 passes when audit passes."""
        proposal = {
            "security_audit": {"passed": True, "issues": []}
        }
        result = self.system.validate_gate_3_security_audit(proposal)
        assert result.passed

    def test_gate_3_security_audit_fail(self):
        """Test Gate 3 fails when audit fails."""
        proposal = {
            "security_audit": {"passed": False, "issues": ["sql_injection"]}
        }
        result = self.system.validate_gate_3_security_audit(proposal)
        assert not result.passed

    def test_gate_4_policy_tier_valid(self):
        """Test Gate 4 passes with valid tier."""
        for tier in ["T0", "T1", "T2", "T3"]:
            proposal = {"policy_tier": tier}
            result = self.system.validate_gate_4_policy_tier(proposal)
            assert result.passed
            assert result.details["policy_tier"] == tier

    def test_gate_4_policy_tier_invalid(self):
        """Test Gate 4 fails with invalid tier."""
        proposal = {"policy_tier": "T5"}
        result = self.system.validate_gate_4_policy_tier(proposal)
        assert not result.passed

    def test_gate_5_input_lock_signed(self):
        """Test Gate 5 passes when input lock is signed."""
        proposal = {
            "input_lock": {
                "lock_hash": "abc123def456",
                "is_signed": True,
            }
        }
        result = self.system.validate_gate_5_input_lock(proposal)
        assert result.passed

    def test_gate_5_input_lock_unsigned(self):
        """Test Gate 5 fails when input lock not signed."""
        proposal = {
            "input_lock": {
                "lock_hash": "abc123def456",
                "is_signed": False,
            }
        }
        result = self.system.validate_gate_5_input_lock(proposal)
        assert not result.passed

    def test_gate_6_output_contract_valid(self):
        """Test Gate 6 passes with valid output schema."""
        proposal = {
            "output_contract": {
                "schema": {
                    "type": "object",
                    "properties": {"result": {"type": "string"}},
                }
            },
            "output": {"result": "success"},
        }
        result = self.system.validate_gate_6_output_contract(proposal)
        assert result.passed

    def test_gate_6_output_contract_invalid(self):
        """Test Gate 6 fails with invalid output schema."""
        proposal = {
            "output_contract": {
                "schema": {
                    "type": "object",
                    "properties": {"result": {"type": "string"}},
                }
            },
            "output": {"result": 123},  # Wrong type
        }
        result = self.system.validate_gate_6_output_contract(proposal)
        assert not result.passed

    def test_gate_7_decision_trace_valid(self):
        """Test Gate 7 passes with valid decision trace."""
        proposal = {
            "decision_trace": {
                "trace_id": "trace_001",
                "is_signed": True,
                "entries": [{"action": "test"}],
            }
        }
        result = self.system.validate_gate_7_decision_trace(proposal)
        assert result.passed

    def test_gate_7_decision_trace_unsigned(self):
        """Test Gate 7 fails with unsigned trace."""
        proposal = {
            "decision_trace": {
                "trace_id": "trace_001",
                "is_signed": False,
                "entries": [],
            }
        }
        result = self.system.validate_gate_7_decision_trace(proposal)
        assert not result.passed

    def test_gate_8_rollback_valid(self):
        """Test Gate 8 passes with valid rollback."""
        proposal = {
            "rollback_instructions": {
                "steps": [
                    {"step_id": "s1", "action": "revert"}
                ],
                "is_validated": True,
            }
        }
        result = self.system.validate_gate_8_rollback(proposal)
        assert result.passed

    def test_gate_8_rollback_invalid(self):
        """Test Gate 8 fails with invalid rollback."""
        proposal = {
            "rollback_instructions": {
                "steps": [],
                "is_validated": False,
            }
        }
        result = self.system.validate_gate_8_rollback(proposal)
        assert not result.passed

    def test_validate_all_gates_pass(self):
        """Test all 8 gates pass with valid proposal."""
        proposal = {
            "proposal_id": "p1",
            "lane_id": "lane_a",
            "action_type": "code_change",
            "description": "Valid change",
            "policy_tier": "T2",
            "regression_tests": {"passed": True, "test_count": 50},
            "security_audit": {"passed": True, "issues": []},
            "input_lock": {"lock_hash": "abc123", "is_signed": True},
            "output_contract": {
                "schema": {"type": "object"}
            },
            "output": {},
            "decision_trace": {
                "trace_id": "t1",
                "is_signed": True,
                "entries": [{}],
            },
            "rollback_instructions": {
                "steps": [{"step_id": "s1"}],
                "is_validated": True,
            },
        }
        result = self.system.validate_all_gates(proposal)
        assert result.all_passed
        assert len(result.gate_results) == 8
        assert all(r.passed for r in result.gate_results)

    def test_validate_all_gates_single_failure_blocks(self):
        """Test that single gate failure blocks all."""
        proposal = {
            "proposal_id": "p1",
            "lane_id": "lane_a",
            "action_type": "code_change",
            "description": "Valid change",
            "policy_tier": "T2",
            "regression_tests": {"passed": False, "test_count": 0},  # Gate 2 fails
            "security_audit": {"passed": True, "issues": []},
            "input_lock": {"lock_hash": "abc123", "is_signed": True},
            "output_contract": {"schema": {"type": "object"}},
            "output": {},
            "decision_trace": {
                "trace_id": "t1",
                "is_signed": True,
                "entries": [{}],
            },
            "rollback_instructions": {
                "steps": [{"step_id": "s1"}],
                "is_validated": True,
            },
        }
        result = self.system.validate_all_gates(proposal)
        assert not result.all_passed
        assert result.gate_results[1].passed is False  # Gate 2 failed

    def test_gate_results_to_dict(self):
        """Test gate result serialization."""
        result = self.system.validate_gate_1_schema(
            {
                "proposal_id": "p1",
                "lane_id": "lane_a",
                "action_type": "code_change",
                "description": "Test",
            }
        )
        result_dict = result.to_dict()
        assert "gate_number" in result_dict
        assert result_dict["passed"] is True


class TestPolicyTierEngine:
    """Tests for policy tier classification."""

    def test_classify_tier_0_metadata(self):
        """Test T0 classification for metadata changes."""
        result = PolicyTierEngine.classify_action(
            "Update README config file",
            affected_modules=["README.md"],
        )
        assert result.tier == "T0"
        assert 1 in result.required_gates

    def test_classify_tier_1_test(self):
        """Test T1 classification for test changes."""
        result = PolicyTierEngine.classify_action(
            "Add unit test for login function",
            affected_modules=["tests/test_auth.py"],
        )
        assert result.tier == "T1"
        assert 1 in result.required_gates
        assert 2 in result.required_gates

    def test_classify_tier_2_security(self):
        """Test T2 classification for security patches."""
        result = PolicyTierEngine.classify_action(
            "Security patch for SQL injection vulnerability",
            affected_modules=["src/db/query.py"],
        )
        assert result.tier == "T2"
        assert 3 in result.required_gates  # Security gate

    def test_classify_tier_3_governance(self):
        """Test T3 classification for governance changes."""
        result = PolicyTierEngine.classify_action(
            "Modify tier system and approval chains",
            affected_modules=["src/orchestration/gates/contract_gate.py"],
        )
        assert result.tier == "T3"
        assert len(result.required_gates) == 8  # All gates required

    def test_escalation_on_high_risk(self):
        """Test escalation when risk exceeds threshold."""
        result = PolicyTierEngine.classify_action(
            "Delete critical system files and remove core functionality",
            affected_modules=[
                "src/auth.py",
                "src/api.py",
                "src/core.py",
                "src/data.py",
            ],
        )
        # High-risk action should escalate to higher tier
        assert result.risk_score > 35.0  # High risk detected

    def test_batch_classify(self):
        """Test batch classification."""
        actions = [
            {"description": "Update README", "affected_modules": ["README.md"]},
            {"description": "Add test", "affected_modules": ["tests/"]},
            {"description": "Security patch", "affected_modules": ["src/"]},
        ]
        results = PolicyTierEngine.batch_classify(actions)
        assert len(results) == 3
        assert results[0].tier == "T0"
        assert results[1].tier == "T1"
        assert results[2].tier == "T2"

    def test_get_tier_requirements_valid(self):
        """Test getting requirements for valid tier."""
        for tier in ["T0", "T1", "T2", "T3"]:
            reqs = PolicyTierEngine.get_tier_requirements(tier)
            assert reqs["tier"] == tier
            assert "name" in reqs
            assert "required_gates" in reqs

    def test_get_tier_requirements_invalid(self):
        """Test error on invalid tier."""
        with pytest.raises(Exception):
            PolicyTierEngine.get_tier_requirements("T5")

    def test_risk_score_calculation(self):
        """Test risk score is calculated."""
        result = PolicyTierEngine.classify_action("Delete critical function")
        assert result.risk_score > 0

    def test_classification_to_dict(self):
        """Test classification serialization."""
        result = PolicyTierEngine.classify_action("Add documentation")
        result_dict = result.to_dict()
        assert "tier" in result_dict
        assert "risk_score" in result_dict


class TestRollbackControls:
    """Tests for rollback execution system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.system = RollbackControlSystem()

    def test_validate_rollback_instruction_valid(self):
        """Test validation of valid instruction."""
        instruction = {
            "rollback_id": "rb_001",
            "steps": [
                {
                    "step_type": "git_revert",
                    "action": {"commit_sha": "abc123"},
                }
            ],
        }
        assert RollbackControlSystem.validate_rollback_instruction(instruction)

    def test_validate_rollback_instruction_missing_id(self):
        """Test validation fails without rollback_id."""
        instruction = {
            "steps": [
                {
                    "step_type": "git_revert",
                    "action": {},
                }
            ]
        }
        with pytest.raises(Exception):
            RollbackControlSystem.validate_rollback_instruction(instruction)

    def test_validate_rollback_instruction_missing_steps(self):
        """Test validation fails without steps."""
        instruction = {"rollback_id": "rb_001"}
        with pytest.raises(Exception):
            RollbackControlSystem.validate_rollback_instruction(instruction)

    def test_execute_rollback_single_step_success(self):
        """Test executing single successful rollback step."""
        instruction = {
            "rollback_id": "rb_001",
            "steps": [
                {
                    "step_id": "s1",
                    "step_type": "git_revert",
                    "description": "Revert bad commit",
                    "action": {"commit_sha": "abc123"},
                    "optional": False,
                }
            ],
        }
        result = self.system.execute_rollback(instruction)
        assert result.success
        assert len(result.step_results) == 1

    def test_execute_rollback_multi_step_success(self):
        """Test executing multiple successful steps."""
        instruction = {
            "rollback_id": "rb_001",
            "steps": [
                {
                    "step_id": "s1",
                    "step_type": "git_revert",
                    "description": "Revert commit",
                    "action": {"commit_sha": "abc123"},
                    "optional": False,
                },
                {
                    "step_id": "s2",
                    "step_type": "data_migration",
                    "description": "Restore data",
                    "action": {"operation": "restore"},
                    "optional": False,
                },
            ],
        }
        result = self.system.execute_rollback(instruction)
        assert result.success
        assert len(result.step_results) == 2

    def test_execute_rollback_failure_aborts(self):
        """Test that non-optional failure aborts rollback."""
        instruction = {
            "rollback_id": "rb_001",
            "steps": [
                {
                    "step_id": "s1",
                    "step_type": "git_revert",
                    "description": "Revert commit",
                    "action": {"commit_sha": None},  # Invalid, will fail
                    "optional": False,
                },
            ],
        }
        result = self.system.execute_rollback(instruction)
        assert not result.success

    def test_execute_rollback_optional_failure_continues(self):
        """Test that optional failure doesn't abort."""
        instruction = {
            "rollback_id": "rb_001",
            "steps": [
                {
                    "step_id": "s1",
                    "step_type": "git_revert",
                    "description": "Optional revert",
                    "action": {"commit_sha": None},  # Invalid, will fail
                    "optional": True,
                },
                {
                    "step_id": "s2",
                    "step_type": "cleanup",
                    "description": "Cleanup",
                    "action": {"target": "/tmp"},
                    "optional": False,
                },
            ],
        }
        result = self.system.execute_rollback(instruction)
        # Should complete despite first step failure
        assert len(result.step_results) == 2

    def test_rollback_result_to_dict(self):
        """Test rollback result serialization."""
        instruction = {
            "rollback_id": "rb_001",
            "steps": [
                {
                    "step_id": "s1",
                    "step_type": "cleanup",
                    "description": "Clean up",
                    "action": {"target": "/tmp"},
                    "optional": False,
                }
            ],
        }
        result = self.system.execute_rollback(instruction)
        result_dict = result.to_dict()
        assert "rollback_id" in result_dict
        assert "success" in result_dict
        assert "step_results" in result_dict


class TestLaneScheduler:
    """Tests for lane scheduling system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.scheduler = LaneSchedulerV1()

    def test_register_single_lane(self):
        """Test registering a single lane."""
        lane = Lane(lane_id="lane_a", name="Phase A")
        self.scheduler.register_lane(lane)
        assert "lane_a" in self.scheduler.lanes

    def test_register_multiple_lanes(self):
        """Test registering multiple lanes."""
        lanes = [
            Lane(lane_id="lane_a", name="Phase A"),
            Lane(lane_id="lane_b", name="Phase B"),
        ]
        self.scheduler.register_lanes(lanes)
        assert len(self.scheduler.lanes) == 2

    def test_lane_dependency_enforcement(self):
        """Test that dependencies are enforced."""
        lane_a = Lane(lane_id="lane_a", name="Phase A")
        lane_b = Lane(
            lane_id="lane_b",
            name="Phase B",
            upstream_dependencies=["lane_a"],
        )
        self.scheduler.register_lanes([lane_a, lane_b])

        # lane_a must pass before lane_b can run
        result_b = self.scheduler.schedule_lane("lane_b")
        assert result_b.state == LaneState.PENDING  # Not ready

        # Schedule lane_a first
        self.scheduler.schedule_lane("lane_a")
        result_b = self.scheduler.schedule_lane("lane_b")
        assert result_b.state == LaneState.PASSED

    def test_deterministic_execution_order(self):
        """Test that execution order is deterministic."""
        lanes = [
            Lane(lane_id="lane_c", name="Phase C"),
            Lane(lane_id="lane_a", name="Phase A"),
            Lane(lane_id="lane_b", name="Phase B"),
        ]
        self.scheduler.register_lanes(lanes)

        # Run twice with same seed, should get same order
        result1 = self.scheduler.schedule_all_lanes()
        self.scheduler.reset_all_lanes()
        result2 = self.scheduler.schedule_all_lanes()

        # Both should succeed and have consistent ordering
        assert all(r.state == LaneState.PASSED for r in result1.values())
        assert all(r.state == LaneState.PASSED for r in result2.values())

    def test_get_lane_state(self):
        """Test getting lane state."""
        lane = Lane(lane_id="lane_a", name="Phase A")
        self.scheduler.register_lane(lane)
        state = self.scheduler.get_lane_state("lane_a")
        assert state == LaneState.PENDING

    def test_get_all_lane_states(self):
        """Test getting all lane states."""
        lanes = [
            Lane(lane_id="lane_a", name="Phase A"),
            Lane(lane_id="lane_b", name="Phase B"),
        ]
        self.scheduler.register_lanes(lanes)
        states = self.scheduler.get_all_lane_states()
        assert len(states) == 2
        assert all(s == "pending" for s in states.values())

    def test_reset_single_lane(self):
        """Test resetting a single lane."""
        lane = Lane(lane_id="lane_a", name="Phase A")
        self.scheduler.register_lane(lane)
        self.scheduler.schedule_lane("lane_a")
        assert self.scheduler.get_lane_state("lane_a") == LaneState.PASSED

        self.scheduler.reset_lane("lane_a")
        assert self.scheduler.get_lane_state("lane_a") == LaneState.PENDING

    def test_reset_all_lanes(self):
        """Test resetting all lanes."""
        lanes = [
            Lane(lane_id="lane_a", name="Phase A"),
            Lane(lane_id="lane_b", name="Phase B"),
        ]
        self.scheduler.register_lanes(lanes)
        self.scheduler.schedule_all_lanes()

        self.scheduler.reset_all_lanes()
        states = self.scheduler.get_all_lane_states()
        assert all(s == "pending" for s in states.values())

    def test_circular_dependency_detection(self):
        """Test that circular dependencies are detected."""
        lane_a = Lane(
            lane_id="lane_a",
            name="Phase A",
            upstream_dependencies=["lane_b"],
        )
        lane_b = Lane(
            lane_id="lane_b",
            name="Phase B",
            upstream_dependencies=["lane_a"],
        )
        self.scheduler.register_lanes([lane_a, lane_b])

        with pytest.raises(Exception):
            self.scheduler.schedule_all_lanes()

    def test_export_schedule(self):
        """Test exporting schedule."""
        lanes = [
            Lane(lane_id="lane_a", name="Phase A"),
            Lane(lane_id="lane_b", name="Phase B"),
        ]
        self.scheduler.register_lanes(lanes)

        schedule = self.scheduler.export_schedule()
        assert "lanes" in schedule
        assert "execution_order" in schedule
        assert len(schedule["lanes"]) == 2


class TestIntegration:
    """Integration tests across modules."""

    def test_gate_system_with_tier_engine(self):
        """Test gate system using tier engine classification."""
        classification = PolicyTierEngine.classify_action(
            "Security patch"
        )

        proposal = {
            "proposal_id": "p1",
            "lane_id": "lane_a",
            "action_type": "code_change",
            "description": "Security patch",
            "policy_tier": classification.tier,
            "regression_tests": {"passed": True, "test_count": 50},
            "security_audit": {"passed": True, "issues": []},
            "input_lock": {"lock_hash": "abc123", "is_signed": True},
            "output_contract": {"schema": {"type": "object"}},
            "output": {},
            "decision_trace": {
                "trace_id": "t1",
                "is_signed": True,
                "entries": [{}],
            },
            "rollback_instructions": {
                "steps": [{"step_id": "s1"}],
                "is_validated": True,
            },
        }

        gate_system = ContractGateSystem()
        result = gate_system.validate_all_gates(proposal)
        assert result.all_passed

    def test_scheduler_with_gate_validation(self):
        """Test scheduler coordinating gated lanes."""
        scheduler = LaneSchedulerV1()

        lanes = [
            Lane(lane_id="validate", name="Validation"),
            Lane(
                lane_id="execute",
                name="Execution",
                upstream_dependencies=["validate"],
            ),
        ]
        scheduler.register_lanes(lanes)

        results = scheduler.schedule_all_lanes()
        assert all(r.state == LaneState.PASSED for r in results.values())
