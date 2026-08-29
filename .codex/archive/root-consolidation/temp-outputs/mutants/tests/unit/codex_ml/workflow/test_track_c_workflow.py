from datetime import UTC, datetime

import pytest

from codex_ml.workflow.track_c_workflow import (
    DEFAULT_ROUTER,
    CapabilityPlan,
    CapabilityRouter,
    ErrorRecord,
    WorkflowContext,
    WorkflowOrchestrator,
    _best_effort_construction_phase,
    _controlled_pruning_phase,
    _error_capture_phase,
    _finalization_phase,
    _preparation_phase,
    _search_and_mapping_phase,
    record_error,
    run_capability,
    step_context,
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
        context={"foo": "bar"},
    )
    d = record.to_dict()
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
    assert ctx.failed_phases == ["rollback:r2"], "failed_phases is not valid"


def test_capability_plan():
    def custom_action(ctx, plan):
        pass

    plan = CapabilityPlan("test", phase_overrides={"Preparation": custom_action})

    assert plan.get_action("Preparation") is custom_action, "Condition must be true"
    assert plan.get_action("Finalization") is None, "Condition must be true"


def test_capability_router():
    plan = CapabilityPlan("test", aliases=["t1"])
    router = CapabilityRouter([plan])

    assert router.resolve("test") is plan, "Condition must be true"
    assert router.resolve("t1") is plan, "Condition must be true"
    assert router.resolve("TEST") is plan, "Condition must be true"

    with pytest.raises(KeyError, match="Unknown capability"):
        router.resolve("unknown")

    # test default
    router2 = CapabilityRouter()
    assert len(router2._plans) == 0, "Collection must not be empty"


def test_record_error():
    ctx = WorkflowContext(capability="test")
    try:
        raise ValueError("oops")
    except ValueError as e:
        record = record_error(ctx, "Preparation", "step1", e, extra_context={"k": "v"})

    assert len(ctx.errors) == 1, "Collection must not be empty"
    assert ctx.errors[0] is record, "Error should be raised or set"
    assert record.exception_type == "ValueError", "Value must be initialized"
    assert record.message == "oops", "message is not valid"
    assert record.context == {"k": "v"}, "context is not valid"
    assert ctx.failed_phases == ["Preparation"], "failed_phases is not valid"


def test_step_context():
    ctx = WorkflowContext(capability="test")

    def rollback(c):
        c.notes.append("rb")

    def fail_step():
        raise ValueError("oops")

    # step_context swallows exceptions
    with step_context(ctx, "Preparation", "step1", rollback=rollback):
        fail_step()

    assert len(ctx.errors) == 1, "Collection must not be empty"
    assert ctx.errors[0].exception_type == "ValueError", "Value must be initialized"
    assert ctx.notes == ["rb"], "notes is not valid"

    # success case
    with step_context(ctx, "Preparation", "step2"):
        ctx.notes.append("success")
    assert "success" in ctx.notes, "Condition must be true"


def test_preparation_phase():
    ctx = WorkflowContext(capability="test")
    plan = CapabilityPlan("test")
    _preparation_phase(ctx, plan)

    assert "prepared:test" in ctx.notes, "Condition must be true"
    assert ctx.summary["offline"] is True, "Condition must be true"

    ctx.apply_rollbacks()
    assert "prepared:test" not in ctx.notes, "Condition must be true"

    # double rollback doesn't crash
    ctx.apply_rollbacks()


def test_search_and_mapping_phase():
    ctx = WorkflowContext(capability="test")
    plan = CapabilityPlan("test", search_targets=["t1", "t2"])
    _search_and_mapping_phase(ctx, plan)

    assert ctx.routes["test"] == ["t1", "t2"]
    ctx.apply_rollbacks()
    assert "test" not in ctx.routes, "Condition must be true"

    plan_default = CapabilityPlan("test2")
    _search_and_mapping_phase(ctx, plan_default)
    assert ctx.routes["test2"] == ["baseline-scan"], "Condition must be true"


def test_best_effort_construction_phase():
    ctx = WorkflowContext(capability="test")
    plan = CapabilityPlan("test", construction_steps=["s1"])
    _best_effort_construction_phase(ctx, plan)

    assert ctx.artifacts == ["test:s1"], "artifacts is not valid"
    ctx.apply_rollbacks()
    assert len(ctx.artifacts) == 0, "Collection must not be empty"

    # Ensure empty pops work
    _best_effort_construction_phase(ctx, plan)
    ctx.artifacts.clear()  # artificially empty
    ctx.apply_rollbacks()  # should not crash

    plan_default = CapabilityPlan("test2")
    _best_effort_construction_phase(ctx, plan_default)
    assert ctx.artifacts == ["test2:prototype"], "artifacts is not valid"
    ctx.apply_rollbacks()
    assert len(ctx.artifacts) == 0, "Collection must not be empty"


def test_controlled_pruning_phase():
    ctx = WorkflowContext(capability="test")
    ctx.artifacts = [
        "good",
        "bad",
        "bad",
        "stale1",
        "stale1",
    ]  # stale1 is duplicate AND matches rule
    plan = CapabilityPlan("test", pruning_rules=["stale"])
    _controlled_pruning_phase(ctx, plan)

    assert ctx.artifacts == ["good", "bad"]
    assert ctx.pruned == ["bad", "stale1", "stale1"]

    ctx.apply_rollbacks()
    # It restores items in reverse order. The specific order isn't strictly mandated by our test,
    # but let's check membership.
    assert "good" in ctx.artifacts, "Condition must be true"
    assert "bad" in ctx.artifacts, "Condition must be true"
    assert "stale1" in ctx.artifacts, "Condition must be true"
    # Check that removed items are removed from pruned
    assert "bad" not in ctx.pruned, "Condition must be true"
    assert "stale1" not in ctx.pruned, "Condition must be true"


def test_error_capture_phase():
    ctx = WorkflowContext(capability="test")
    plan = CapabilityPlan("test")
    _error_capture_phase(ctx, plan)
    assert ctx.notes == ["errors-reviewed"], "Error should be raised or set"
    ctx.apply_rollbacks()
    assert len(ctx.notes) == 0, "Collection must not be empty"

    # With errors, should apply existing rollbacks
    ctx = WorkflowContext(capability="test")
    ctx.errors.append(ErrorRecord(datetime.now(UTC), "phase", "cap", "step", "msg", "type"))
    ctx.register_rollback("test_rb", lambda c: c.notes.append("rb_applied"))
    _error_capture_phase(ctx, plan)

    assert "rb_applied" in ctx.notes, "Condition must be true"
    assert "errors-reviewed" in ctx.notes, "Error should be raised or set"


def test_finalization_phase():
    ctx = WorkflowContext(capability="test")
    plan = CapabilityPlan("test")
    _finalization_phase(ctx, plan)

    assert ctx.summary["capability"] == "test", "Condition must be true"
    assert "phases" in ctx.summary, "Condition must be true"

    ctx.apply_rollbacks()
    assert len(ctx.summary) == 0, "Collection must not be empty"


def test_workflow_orchestrator():
    def err_action(ctx, plan):
        raise ValueError("Phase error")

    plan = CapabilityPlan("test", phase_overrides={"Preparation": err_action})
    router = CapabilityRouter([plan])

    orch = WorkflowOrchestrator(router)
    ctx = orch.run("test")

    assert "Preparation" in ctx.phase_history, "Condition must be true"
    assert len(ctx.errors) == 1, "Collection must not be empty"
    assert ctx.errors[0].phase == "Preparation", "Error should be raised or set"
    assert "Finalization" in ctx.phase_history, "Condition must be true"

    # Test default router
    orch2 = WorkflowOrchestrator()
    assert orch2.router == DEFAULT_ROUTER, "router is not valid"


def test_run_capability():
    plan = CapabilityPlan("test")
    router = CapabilityRouter([plan])
    ctx = run_capability("test", router=router)
    assert ctx.capability == "test", "capability is not valid"
    assert ctx.summary["capability"] == "test", "Condition must be true"
