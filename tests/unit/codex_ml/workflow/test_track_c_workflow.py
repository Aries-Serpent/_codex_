import pytest
from datetime import datetime, UTC
from codex_ml.workflow.track_c_workflow import (
    ErrorRecord, WorkflowContext, CapabilityPlan, CapabilityRouter,
    record_error, step_context, _preparation_phase, _search_and_mapping_phase,
    _best_effort_construction_phase, _controlled_pruning_phase,
    _error_capture_phase, _finalization_phase, WorkflowOrchestrator,
    run_capability, DEFAULT_ROUTER
)

def test_error_record_to_dict():
    dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)
    record = ErrorRecord(
        timestamp=dt,
        phase="Preparation",
        capability="test",
        step="test_step",
        message="test error",
        exception_type="ValueError",
        context={"foo": "bar"}
    )
    d = record.to_dict()
    assert d == {
        "timestamp": "2023-01-01T12:00:00+00:00",
        "phase": "Preparation",
        "capability": "test",
        "step": "test_step",
        "message": "test error",
        "exception_type": "ValueError",
        "context": {"foo": "bar"},
    }

def test_workflow_context_rollbacks():
    ctx = WorkflowContext(capability="test")
    def r1(c):
        c.notes.append("r1")
    def r2(c):
        raise ValueError("r2 error")
    def r3(c):
        c.notes.append("r3")
    
    ctx.register_rollback("r1", r1)
    ctx.register_rollback("r2", r2)
    ctx.register_rollback("r3", r3)
    
    ctx.apply_rollbacks()
    assert ctx.notes == ["r3", "r1"]
    assert ctx.failed_phases == ["rollback:r2"]

def test_capability_plan():
    def custom_action(ctx, plan): pass
    plan = CapabilityPlan("test", phase_overrides={"Preparation": custom_action})
    
    assert plan.get_action("Preparation") is custom_action
    assert plan.get_action("Finalization") is None

def test_capability_router():
    plan = CapabilityPlan("test", aliases=["t1"])
    router = CapabilityRouter([plan])
    
    assert router.resolve("test") is plan
    assert router.resolve("t1") is plan
    assert router.resolve("TEST") is plan
    
    with pytest.raises(KeyError, match="Unknown capability"):
        router.resolve("unknown")
        
    # test default
    router2 = CapabilityRouter()
    assert len(router2._plans) == 0

def test_record_error():
    ctx = WorkflowContext(capability="test")
    try:
        raise ValueError("oops")
    except ValueError as e:
        record = record_error(ctx, "Preparation", "step1", e, extra_context={"k": "v"})
    
    assert len(ctx.errors) == 1
    assert ctx.errors[0] is record
    assert record.exception_type == "ValueError"
    assert record.message == "oops"
    assert record.context == {"k": "v"}
    assert ctx.failed_phases == ["Preparation"]

def test_step_context():
    ctx = WorkflowContext(capability="test")
    def rollback(c): c.notes.append("rb")
    def fail_step():
        raise ValueError("oops")
    
    # step_context swallows exceptions
    with step_context(ctx, "Preparation", "step1", rollback=rollback):
        fail_step()
    
    assert len(ctx.errors) == 1
    assert ctx.errors[0].exception_type == "ValueError"
    assert ctx.notes == ["rb"]

    # success case
    with step_context(ctx, "Preparation", "step2"):
        ctx.notes.append("success")
    assert "success" in ctx.notes

def test_preparation_phase():
    ctx = WorkflowContext(capability="test")
    plan = CapabilityPlan("test")
    _preparation_phase(ctx, plan)
    
    assert "prepared:test" in ctx.notes
    assert ctx.summary["offline"] is True
    
    ctx.apply_rollbacks()
    assert "prepared:test" not in ctx.notes
    
    # double rollback doesn't crash
    ctx.apply_rollbacks()

def test_search_and_mapping_phase():
    ctx = WorkflowContext(capability="test")
    plan = CapabilityPlan("test", search_targets=["t1", "t2"])
    _search_and_mapping_phase(ctx, plan)
    
    assert ctx.routes["test"] == ["t1", "t2"]
    ctx.apply_rollbacks()
    assert "test" not in ctx.routes

    plan_default = CapabilityPlan("test2")
    _search_and_mapping_phase(ctx, plan_default)
    assert ctx.routes["test2"] == ["baseline-scan"]

def test_best_effort_construction_phase():
    ctx = WorkflowContext(capability="test")
    plan = CapabilityPlan("test", construction_steps=["s1"])
    _best_effort_construction_phase(ctx, plan)
    
    assert ctx.artifacts == ["test:s1"]
    ctx.apply_rollbacks()
    assert len(ctx.artifacts) == 0

    # Ensure empty pops work
    _best_effort_construction_phase(ctx, plan)
    ctx.artifacts.clear() # artificially empty
    ctx.apply_rollbacks() # should not crash

    plan_default = CapabilityPlan("test2")
    _best_effort_construction_phase(ctx, plan_default)
    assert ctx.artifacts == ["test2:prototype"]
    ctx.apply_rollbacks()
    assert len(ctx.artifacts) == 0

def test_controlled_pruning_phase():
    ctx = WorkflowContext(capability="test")
    ctx.artifacts = ["good", "bad", "bad", "stale1", "stale1"] # stale1 is duplicate AND matches rule
    plan = CapabilityPlan("test", pruning_rules=["stale"])
    _controlled_pruning_phase(ctx, plan)
    
    assert ctx.artifacts == ["good", "bad"]
    assert ctx.pruned == ["bad", "stale1", "stale1"]
    
    ctx.apply_rollbacks()
    # It restores items in reverse order. The specific order isn't strictly mandated by our test,
    # but let's check membership.
    assert "good" in ctx.artifacts
    assert "bad" in ctx.artifacts
    assert "stale1" in ctx.artifacts
    # Check that removed items are removed from pruned
    assert "bad" not in ctx.pruned
    assert "stale1" not in ctx.pruned

def test_error_capture_phase():
    ctx = WorkflowContext(capability="test")
    plan = CapabilityPlan("test")
    _error_capture_phase(ctx, plan)
    assert ctx.notes == ["errors-reviewed"]
    ctx.apply_rollbacks()
    assert len(ctx.notes) == 0

    # With errors, should apply existing rollbacks
    ctx = WorkflowContext(capability="test")
    ctx.errors.append(ErrorRecord(datetime.now(UTC), "phase", "cap", "step", "msg", "type"))
    ctx.register_rollback("test_rb", lambda c: c.notes.append("rb_applied"))
    _error_capture_phase(ctx, plan)
    
    assert "rb_applied" in ctx.notes
    assert "errors-reviewed" in ctx.notes

def test_finalization_phase():
    ctx = WorkflowContext(capability="test")
    plan = CapabilityPlan("test")
    _finalization_phase(ctx, plan)
    
    assert ctx.summary["capability"] == "test"
    assert "phases" in ctx.summary
    
    ctx.apply_rollbacks()
    assert len(ctx.summary) == 0

def test_workflow_orchestrator():
    def err_action(ctx, plan):
        raise ValueError("Phase error")

    plan = CapabilityPlan("test", phase_overrides={"Preparation": err_action})
    router = CapabilityRouter([plan])
    
    orch = WorkflowOrchestrator(router)
    ctx = orch.run("test")
    
    assert "Preparation" in ctx.phase_history
    assert len(ctx.errors) == 1
    assert ctx.errors[0].phase == "Preparation"
    assert "Finalization" in ctx.phase_history
    
    # Test default router
    orch2 = WorkflowOrchestrator()
    assert orch2.router == DEFAULT_ROUTER

def test_run_capability():
    plan = CapabilityPlan("test")
    router = CapabilityRouter([plan])
    ctx = run_capability("test", router=router)
    assert ctx.capability == "test"
    assert ctx.summary["capability"] == "test"
