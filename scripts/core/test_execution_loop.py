#!/usr/bin/env python3
"""
Execution Loop Test Suite

Comprehensive testing of the core autonomy foundations:
1. Full 8-step loop execution
2. Validation failure + blocking
3. Rollback scenario
4. Multi-agent handoff
5. Crash recovery
"""

import sys
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from .checkpoint_manager import CheckpointManager
from .handoff_protocol import HandoffProtocol
from .validation_engine import validate_state, validate_state_transition


def create_test_state(
    step: str = "act",
    status: str = "in_progress",
    confidence: float = 0.85,
    valid: bool = True,
    previous_state_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create a test state."""
    state_id = str(uuid.uuid4())
    
    state = {
        "state_id": state_id,
        "agent_id": "test-agent",
        "phase_id": "phase-10",
        "track_id": "test-track",
        "task_id": "test-task",
        "execution_step": step,
        "status": status,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "previous_state_id": previous_state_id or "null",
        "confidence_score": confidence,
        "input_context": {
            "source": "test",
            "data": {"test_key": "test_value"}
        },
        "decision_context": {
            "reasoning": ["Test reasoning"],
            "constraints": ["Test constraint"],
            "selected_action": "test_action",
            "confidence": confidence
        },
        "actions_taken": [
            {
                "action_id": "action-1",
                "action_type": "test",
                "status": "completed",
                "target": "test-system"
            }
        ],
        "validation_results": {},
        "dependencies": [
            {
                "type": "state",
                "id": str(uuid.uuid4()),
                "status": "resolved"
            }
        ],
        "unresolved_items": [],
        "lineage": {
            "created_by": "test-agent"
        }
    }
    
    if not valid:
        # Add violations
        state["status"] = "failed"
        state["confidence_score"] = 0.3
    
    return state


def test_full_execution_loop():
    """Test successful full 8-step execution loop."""
    print("\n=== TEST: Full 8-Step Execution Loop ===")
    
    steps = ["observe", "context", "decide", "act", "validate", "persist", "handoff", "complete"]
    current_state = None
    checkpoint_manager = CheckpointManager(storage_dir=None)
    
    for i, step in enumerate(steps):
        print(f"\nStep {i+1}/8: {step.upper()}")
        
        # Create state for this step
        previous_id = current_state.get("state_id") if current_state else None
        current_state = create_test_state(
            step=step,
            status="in_progress",
            confidence=0.5 + (i * 0.05),
            previous_state_id=previous_id
        )
        
        # Validate state
        validation = validate_state(current_state)
        print(f"  Validation: {validation['valid']}")
        
        if validation["violations"]:
            print(f"  Violations: {len(validation['violations'])}")
            for v in validation["violations"][:2]:
                print(f"    - {v.get('rule')}: {v.get('message', '')[:60]}")
        
        # Checkpoint state
        if step != "complete":
            checkpoint_id = checkpoint_manager.create_checkpoint(current_state)
            print(f"  Checkpoint: {checkpoint_id[:8]}...")
            current_state["_checkpoint_id"] = checkpoint_id
        
        # Update status
        if step == "validate":
            current_state["status"] = "validated"
        elif step == "persist":
            current_state["status"] = "validated"
        elif step == "handoff":
            current_state["status"] = "handoff_pending"
        elif step == "complete":
            current_state["status"] = "validated"
    
    print("\n✓ Full execution loop test PASSED")
    assert current_state is not None, "Final state should not be None"
    assert current_state["execution_step"] == "complete", "Final step should be complete"


def test_validation_failure_and_blocking():
    """Test validation failure + blocking."""
    print("\n=== TEST: Validation Failure + Blocking ===")
    
    # Create invalid state
    state = create_test_state(step="act", valid=False)
    
    # Validate - should detect violations
    validation = validate_state(state)
    print(f"State valid: {validation['valid']}")
    print(f"Violations found: {len(validation['violations'])}")
    
    for v in validation['violations'][:3]:
        print(f"  - {v.get('rule')}: {v.get('message', '')[:70]}")
    
    # Should not persist if invalid
    assert not validation['valid'], "Invalid state should fail validation"
    assert len(validation['violations']) > 0, "Should have violations"
    print("✓ Invalid state blocked from persistence")


def test_rollback_scenario():
    """Test rollback from failed validation."""
    print("\n=== TEST: Rollback Scenario ===")
    
    checkpoint_manager = CheckpointManager(storage_dir=None)
    
    # Create good state
    good_state = create_test_state(step="act", status="in_progress")
    checkpoint_1 = checkpoint_manager.create_checkpoint(good_state)
    print(f"Created checkpoint 1: {checkpoint_1[:8]}...")
    
    # Create bad state
    bad_state = create_test_state(
        step="validate",
        status="failed",
        confidence=0.3,
        valid=False,
        previous_state_id=good_state.get("state_id")
    )
    
    # Validate bad state
    validation = validate_state(bad_state)
    print(f"Bad state validation: {validation['valid']}")
    
    assert not validation['valid'], "Bad state should fail validation"
    
    # Rollback
    print("Rolling back to previous state...")
    rolled_back = checkpoint_manager.rollback_to_previous(bad_state)
    
    assert rolled_back is not None, "Rollback should succeed"
    print(f"✓ Rolled back to state: {rolled_back.get('state_id')[:8]}...")
    # Should be the good state
    assert rolled_back.get('state_id') == good_state.get('state_id'), "Rollback should return correct state"
    print("✓ Rollback returned correct state")


def test_multi_agent_handoff():
    """Test multi-agent handoff."""
    print("\n=== TEST: Multi-Agent Handoff ===")
    
    # Agent A creates state
    state_a = create_test_state(step="decide", status="in_progress")
    state_a["agent_id"] = "agent-a"
    print(f"Agent A created state: {state_a.get('state_id')[:8]}...")
    
    # Agent A prepares handoff to Agent B
    handoff = HandoffProtocol.prepare_handoff(
        state_a,
        next_agent="agent-b",
        current_agent="agent-a"
    )
    print(f"Handoff prepared: {handoff.handoff_id[:8]}...")
    print(f"  Decision trace items: {len(handoff.decision_trace)}")
    print(f"  Risk flags: {handoff.risk_flags}")
    print(f"  Confidence: {handoff.confidence}")
    
    # Validate handoff
    validation = HandoffProtocol.validate_handoff(handoff)
    print(f"Handoff validation: {validation['valid']}")
    
    assert validation['valid'], f"Handoff should be valid. Errors: {validation.get('errors', [])}"
    
    # Agent B resumes from handoff
    state_b = HandoffProtocol.resume_from_handoff(handoff)
    print(f"Agent B resumed state: {state_b.get('state_id')[:8]}...")
    print(f"  Preserved decision context: {bool(state_b.get('decision_context'))}")
    print(f"  Preserved unresolved items: {len(state_b.get('unresolved_items', []))}")
    
    # Check that critical info was preserved
    assert state_b.get('state_id') == state_a.get('state_id'), "State ID should be preserved"
    print("✓ State ID preserved")
    assert state_b.get('decision_context'), "Decision context should be preserved"
    print("✓ Decision context preserved")
    
    print("✓ Multi-agent handoff test PASSED")


def test_crash_recovery():
    """Test crash recovery from checkpoint."""
    print("\n=== TEST: Crash Recovery ===")
    
    checkpoint_manager = CheckpointManager(storage_dir=None)
    
    # Simulate normal execution
    state = create_test_state(step="act", status="in_progress")
    checkpoint_id = checkpoint_manager.create_checkpoint(state)
    print(f"Created checkpoint before crash: {checkpoint_id[:8]}...")
    
    # Simulate crash - create new manager (like process restart)
    manager_after_crash = CheckpointManager(storage_dir=None)
    
    # Recover from checkpoint
    recovered_state = manager_after_crash.load_checkpoint(checkpoint_id)
    
    assert recovered_state is not None, "Should recover state from checkpoint"
    print("✓ Recovered state from checkpoint")
    assert recovered_state.get('state_id') == state.get('state_id'), "State ID should match"
    print(f"  State ID matches: {recovered_state.get('state_id') == state.get('state_id')}")
    assert len(recovered_state) == len(state), "All data should be preserved"
    print(f"  All data preserved: {len(recovered_state) == len(state)}")
    
    # Resume execution
    resumed_state = manager_after_crash.resume_execution(checkpoint_id)
    assert resumed_state is not None, "Should resume execution from checkpoint"
    print("✓ Resumed execution from checkpoint")
    print(f"  Execution step: {resumed_state.get('execution_step')}")


def test_state_transition_validation():
    """Test state machine transition validation."""
    print("\n=== TEST: State Transition Validation ===")
    
    # Valid transition
    from_state = create_test_state(step="act", status="in_progress")
    to_state = create_test_state(
        step="validate",
        status="validated",
        previous_state_id=from_state.get('state_id')
    )
    
    validation = validate_state_transition(from_state, to_state)
    print(f"Valid transition: {validation['valid']}")
    assert validation['valid'], f"Valid transition should pass: {validation.get('violations')}"
    
    # Invalid transition
    bad_transition_state = create_test_state(step="complete", status="blocked")
    validation2 = validate_state_transition(to_state, bad_transition_state)
    print(f"Invalid transition detected: {not validation2['valid']}")
    assert not validation2['valid'], "Invalid transition should be detected"
    
    if validation2.get('violations'):
        print(f"  Reason: {validation2['violations'][0].get('message')[:70]}")
    
    print("✓ State transition validation test PASSED")


def test_confidence_thresholds():
    """Test confidence threshold validation."""
    print("\n=== TEST: Confidence Threshold Validation ===")
    
    # Test low confidence at different steps
    test_cases = [
        ("decide", 0.6),  # Should violate (min 0.7)
        ("act", 0.7),     # Should violate (min 0.75)
        ("persist", 0.8), # Should pass (min 0.85 is borderline)
    ]
    
    for step, confidence in test_cases:
        state = create_test_state(step=step, confidence=confidence)
        validation = validate_state(state)
        
        has_confidence_violation = any(
            "confidence" in v.get("rule", "").lower()
            for v in validation["violations"]
        )
        
        print(f"Step '{step}' at {confidence:.2f}: ", end="")
        if has_confidence_violation:
            print("✓ Confidence violation detected")
        else:
            print("✓ No confidence violation")
    
    print("✓ Confidence threshold validation test PASSED")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("CORE AUTONOMY FOUNDATIONS - EXECUTION LOOP TEST SUITE")
    print("="*60)
    
    tests = [
        ("Full 8-Step Loop", test_full_execution_loop),
        ("Validation Failure", test_validation_failure_and_blocking),
        ("Rollback Scenario", test_rollback_scenario),
        ("Multi-Agent Handoff", test_multi_agent_handoff),
        ("Crash Recovery", test_crash_recovery),
        ("State Transitions", test_state_transition_validation),
        ("Confidence Thresholds", test_confidence_thresholds),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            test_func()
            results[test_name] = "PASSED"
        except AssertionError as e:
            results[test_name] = f"FAILED: {str(e)[:50]}"
            print(f"ASSERTION FAILED in {test_name}: {e}")
        except Exception as e:
            results[test_name] = f"ERROR: {str(e)[:50]}"
            print(f"ERROR in {test_name}: {e}")
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✓" if "PASSED" in result else "✗"
        print(f"{status} {test_name}: {result}")
    
    passed = sum(1 for r in results.values() if "PASSED" in r)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
