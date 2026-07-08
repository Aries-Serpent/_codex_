"""Unit tests for codex_ml.workflow.track_c_workflow."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest

from codex_ml.workflow.track_c_workflow import (
    CAPABILITY_ROUTING,
    PHASE_IMPLEMENTATIONS,
    SIX_PHASES,
    CapabilityPlan,
    CapabilityRouter,
    ErrorRecord,
    WorkflowContext,
    record_error,
    run_capability,
    step_context,
)

# ---------------------------------------------------------------------------
# SIX_PHASES constant
# ---------------------------------------------------------------------------


def test_six_phases_length():
    assert len(SIX_PHASES) == 6, "Six_phases must not be empty"


def test_six_phases_names():
    assert SIX_PHASES[0] == "Preparation", "Condition must be true"
    assert SIX_PHASES[-1] == "Finalization", "Condition must be true"


# ---------------------------------------------------------------------------
# ErrorRecord
# ---------------------------------------------------------------------------


def _make_error_record(**kwargs: Any) -> ErrorRecord:
    defaults: dict[str, Any] = {
        "timestamp": datetime.now(UTC),
        "phase": "Preparation",
        "capability": "tokenization",
        "step": "some_step",
        "message": "something failed",
        "exception_type": "ValueError",
    }
    defaults.update(kwargs)
    return ErrorRecord(**defaults)


def test_error_record_to_dict_keys():
    rec = _make_error_record()
    d = rec.to_dict()
    rec = _make_error_record()
    d = rec.to_dict()
    # Should be parseable ISO string
    parsed = datetime.fromisoformat(d["timestamp"])
    assert isinstance(parsed, datetime)


def test_error_record_to_dict_context_default_empty():
    rec = _make_error_record()
    assert rec.to_dict()["context"] == {}, "Condition must be true"


def test_error_record_to_dict_with_context():
    rec = _make_error_record(context={"key": "value"})
    assert rec.to_dict()["context"] == {"key": "value"}, "Value must be initialized"


# ---------------------------------------------------------------------------
# WorkflowContext
# ---------------------------------------------------------------------------


def test_workflow_context_defaults():
    ctx = WorkflowContext(capability="training")
    assert ctx.capability == "training", "capability is not valid"
    assert ctx.offline_mode is True, "offline_mode is not valid"
    assert ctx.phase_history == [], "phase_history is not valid"
    assert ctx.routes == {}, "routes is not valid"
    assert ctx.artifacts == [], "artifacts is not valid"
    assert ctx.pruned == [], "pruned is not valid"
    assert ctx.errors == [], "Error should be raised or set"
    assert ctx.rollbacks == [], "rollbacks is not valid"
    assert ctx.notes == [], "notes is not valid"
    assert ctx.failed_phases == [], "failed_phases is not valid"
    assert ctx.summary == {}, "summary is not valid"


def test_workflow_context_offline_mode_false():
    ctx = WorkflowContext(capability="eval", offline_mode=False)
    assert ctx.offline_mode is False, "offline_mode is not valid"


def test_register_rollback_appends():
    ctx = WorkflowContext(capability="test")
    ctx.register_rollback("rb1", lambda c: None)
    assert len(ctx.rollbacks) == 1, "Collection must not be empty"
    assert ctx.rollbacks[0][0] == "rb1", "Condition must be true"


def test_apply_rollbacks_executes_in_reverse():
    ctx = WorkflowContext(capability="test")
    calls: list[str] = []
    ctx.register_rollback("first", lambda c: calls.append("first"))
    ctx.register_rollback("second", lambda c: calls.append("second"))
    ctx.apply_rollbacks()
    assert calls == ["second", "first"]
    assert ctx.rollbacks == [], "rollbacks is not valid"


def test_apply_rollbacks_swallows_exceptions():
    ctx = WorkflowContext(capability="test")

    def bad_rollback(c: WorkflowContext) -> None:
        raise RuntimeError("rollback_boom")

    ctx.register_rollback("bad", bad_rollback)
    ctx.apply_rollbacks()  # should not raise
    assert "rollback:bad" in ctx.failed_phases, "Condition must be true"


def test_apply_rollbacks_empty_is_noop():
    ctx = WorkflowContext(capability="test")
    ctx.apply_rollbacks()  # no error


# ---------------------------------------------------------------------------
# CapabilityPlan
# ---------------------------------------------------------------------------


def test_capability_plan_defaults():
    plan = CapabilityPlan(name="myplan")
    assert plan.aliases == (), "aliases is not valid"
    assert plan.search_targets == (), "search_targets is not valid"
    assert plan.construction_steps == (), "construction_steps is not valid"
    assert plan.pruning_rules == (), "pruning_rules is not valid"
    assert plan.phase_overrides is None, "phase_overrides is not valid"


def test_capability_plan_get_action_none_when_no_overrides():
    plan = CapabilityPlan(name="myplan")
    assert plan.get_action("Preparation") is None, "Condition must be true"


def test_capability_plan_get_action_returns_override():
    called: list[str] = []

    def my_action(ctx: WorkflowContext, plan: CapabilityPlan) -> None:
        called.append("ok")

    plan = CapabilityPlan(name="myplan", phase_overrides={"Preparation": my_action})
    action = plan.get_action("Preparation")
    assert action is my_action, "action is not valid"


def test_capability_plan_get_action_unknown_phase_returns_none():
    plan = CapabilityPlan(name="myplan", phase_overrides={"Preparation": lambda c, p: None})
    assert plan.get_action("Unknown") is None, "Condition must be true"


# ---------------------------------------------------------------------------
# CapabilityRouter
# ---------------------------------------------------------------------------


def test_capability_router_register_and_resolve():
    router = CapabilityRouter()
    plan = CapabilityPlan(name="Tokenization", aliases=("token", "bpe"))
    router.register(plan)
    assert router.resolve("tokenization") is plan, "Condition must be true"
    assert router.resolve("TOKEN") is plan, "Condition must be true"
    assert router.resolve("BPE") is plan, "Condition must be true"


def test_capability_router_resolve_unknown_raises():
    router = CapabilityRouter()
    with pytest.raises(KeyError, match="unknown_cap"):
        router.resolve("unknown_cap")


def test_capability_router_init_with_plans():
    plan_a = CapabilityPlan(name="alpha")
    plan_b = CapabilityPlan(name="beta")
    router = CapabilityRouter(plans=[plan_a, plan_b])
    assert router.resolve("alpha") is plan_a, "Condition must be true"
    assert router.resolve("beta") is plan_b, "Condition must be true"


# ---------------------------------------------------------------------------
# record_error
# ---------------------------------------------------------------------------


def test_record_error_appends_to_ctx():
    ctx = WorkflowContext(capability="eval")
    exc = ValueError("something_bad")
    rec = record_error(ctx, "Preparation", "step_x", exc)
    assert rec in ctx.errors, "Error should be raised or set"
    assert "Preparation" in ctx.failed_phases, "Condition must be true"


def test_record_error_exception_type():
    ctx = WorkflowContext(capability="eval")
    exc = TypeError("type_error_msg")
    rec = record_error(ctx, "Finalization", "step_y", exc)
    assert rec.exception_type == "TypeError", "Error should be raised or set"
    assert rec.message == "type_error_msg", "Error should be raised or set"


def test_record_error_extra_context():
    ctx = WorkflowContext(capability="eval")
    exc = RuntimeError("extra_context_test")
    rec = record_error(ctx, "Preparation", "step", exc, extra_context={"k": "v"})
    assert rec.context == {"k": "v"}, "context is not valid"


# ---------------------------------------------------------------------------
# Step Context
# ---------------------------------------------------------------------------


def test_step_context_no_exception():
    ctx = WorkflowContext(capability="eval")
    with step_context(ctx, "Preparation", "step"):
        pass
    assert ctx.errors == [], "Error should be raised or set"


def test_step_context_captures_exception():
    ctx = WorkflowContext(capability="eval")
    with step_context(ctx, "Preparation", "step"):
        raise ValueError("step_context_error_captured")
    assert len(ctx.errors) == 1, "Collection must not be empty"
    assert ctx.errors[0].message == "step_context_error_captured", "Error should be raised or set"


def test_step_context_calls_rollback_on_exception():
    ctx = WorkflowContext(capability="eval")
    rolled_back: list[bool] = []
    with step_context(ctx, "Preparation", "step", rollback=lambda c: rolled_back.append(True)):
        raise RuntimeError("trigger_rollback")
    assert rolled_back == [True], "rolled_back is not valid"


def test_step_context_no_rollback_on_success():
    ctx = WorkflowContext(capability="eval")
    rolled_back: list[bool] = []
    with step_context(ctx, "Preparation", "step", rollback=lambda c: rolled_back.append(True)):
        pass
    assert rolled_back == [], "rolled_back is not valid"


# ---------------------------------------------------------------------------
# Phase implementations (direct)
# ---------------------------------------------------------------------------


def _make_plan(**kwargs: Any) -> CapabilityPlan:
    defaults: dict[str, Any] = {
        "name": "test_cap",
        "search_targets": ("data", "models"),
        "construction_steps": ("build", "package"),
        "pruning_rules": ("stale",),
    }
    defaults.update(kwargs)
    return CapabilityPlan(**defaults)


def test_preparation_phase_adds_note():
    ctx = WorkflowContext(capability="test_cap")
    plan = _make_plan()
    PHASE_IMPLEMENTATIONS["Preparation"](ctx, plan)
    assert "prepared:test_cap" in ctx.notes, "Condition must be true"
    assert ctx.summary.get("offline") is True, "Condition must be true"


def test_preparation_phase_rollback():
    ctx = WorkflowContext(capability="test_cap")
    plan = _make_plan()
    PHASE_IMPLEMENTATIONS["Preparation"](ctx, plan)
    ctx.apply_rollbacks()
    assert "prepared:test_cap" not in ctx.notes, "Condition must be true"


def test_search_and_mapping_phase_populates_routes():
    ctx = WorkflowContext(capability="test_cap")
    plan = _make_plan()
    PHASE_IMPLEMENTATIONS["Search & Mapping"](ctx, plan)
    assert "test_cap" in ctx.routes, "Condition must be true"
    assert ctx.routes["test_cap"] == ["data", "models"]


def test_search_and_mapping_phase_default_targets():
    ctx = WorkflowContext(capability="test_cap")
    plan = CapabilityPlan(name="test_cap")
    PHASE_IMPLEMENTATIONS["Search & Mapping"](ctx, plan)
    assert ctx.routes["test_cap"] == ["baseline-scan"], "Condition must be true"


def test_best_effort_construction_phase_adds_artifacts():
    ctx = WorkflowContext(capability="test_cap")
    plan = _make_plan()
    PHASE_IMPLEMENTATIONS["Best-Effort Construction"](ctx, plan)
    assert "test_cap:build" in ctx.artifacts, "Condition must be true"
    assert "test_cap:package" in ctx.artifacts, "Condition must be true"


def test_best_effort_construction_phase_default_step():
    ctx = WorkflowContext(capability="test_cap")
    plan = CapabilityPlan(name="test_cap")
    PHASE_IMPLEMENTATIONS["Best-Effort Construction"](ctx, plan)
    assert "test_cap:prototype" in ctx.artifacts, "Condition must be true"


def test_controlled_pruning_phase_removes_matching():
    ctx = WorkflowContext(capability="test_cap")
    ctx.artifacts = ["test_cap:stale_item", "test_cap:good_item"]
    plan = _make_plan(pruning_rules=("stale",))
    PHASE_IMPLEMENTATIONS["Controlled Pruning"](ctx, plan)
    assert "test_cap:stale_item" not in ctx.artifacts, "Item must not be empty"
    assert "test_cap:stale_item" in ctx.pruned, "Item must not be empty"
    assert "test_cap:good_item" in ctx.artifacts, "Item must not be empty"


def test_controlled_pruning_phase_no_matches():
    ctx = WorkflowContext(capability="test_cap")
    ctx.artifacts = ["test_cap:good_item"]
    plan = _make_plan(pruning_rules=("stale",))
    PHASE_IMPLEMENTATIONS["Controlled Pruning"](ctx, plan)
    assert ctx.pruned == [], "pruned is not valid"
    assert "test_cap:good_item" in ctx.artifacts, "Item must not be empty"


def test_error_capture_phase_triggers_rollbacks_when_errors():
    ctx = WorkflowContext(capability="test_cap")
    exc = ValueError("err_capture_test")
    record_error(ctx, "Preparation", "step", exc)
    rolled: list[bool] = []
    ctx.register_rollback("test_rb", lambda c: rolled.append(True))
    plan = _make_plan()
    PHASE_IMPLEMENTATIONS["Error Capture"](ctx, plan)
    assert rolled == [True], "rolled is not valid"
    assert "errors-reviewed" in ctx.notes, "Error should be raised or set"


def test_error_capture_phase_no_rollbacks_when_no_errors():
    ctx = WorkflowContext(capability="test_cap")
    rolled: list[bool] = []
    ctx.register_rollback("test_rb", lambda c: rolled.append(True))
    plan = _make_plan()
    PHASE_IMPLEMENTATIONS["Error Capture"](ctx, plan)
    # No errors → rollbacks not consumed
    assert rolled == [], "rolled is not valid"


def test_finalization_phase_populates_summary():
    ctx = WorkflowContext(capability="test_cap")
    ctx.artifacts = ["a1"]
    ctx.phase_history = ["Preparation"]
    plan = _make_plan()
    PHASE_IMPLEMENTATIONS["Finalization"](ctx, plan)
    assert ctx.summary["capability"] == "test_cap", "Condition must be true"
    assert ctx.summary["artifacts"] == ["a1"], "Condition must be true"
    assert ctx.summary["phases"] == ["Preparation"], "Condition must be true"


# ---------------------------------------------------------------------------
# CAPABILITY_ROUTING / DEFAULT_ROUTER
# ---------------------------------------------------------------------------


def test_default_router_resolves_tokenization():
    ctx = run_capability("tokenization")
    assert ctx.capability == "tokenization", "capability is not valid"


def test_default_router_resolves_alias_token():
    ctx = run_capability("token")
    assert ctx.capability == "tokenization", "capability is not valid"


def test_default_router_resolves_training():
    ctx = run_capability("training")
    assert ctx.capability == "training", "capability is not valid"


def test_default_router_resolves_evaluation():
    ctx = run_capability("evaluation")
    assert ctx.capability == "evaluation", "capability is not valid"


def test_capability_routing_has_expected_keys():
    assert "tokenization" in CAPABILITY_ROUTING, "Condition must be true"
    assert "training" in CAPABILITY_ROUTING, "Condition must be true"
    assert "evaluation" in CAPABILITY_ROUTING, "Condition must be true"


# ---------------------------------------------------------------------------
# WorkflowOrchestrator / run_capability end-to-end
# ---------------------------------------------------------------------------


def test_run_capability_all_phases_in_history():
    ctx = run_capability("training")
    assert list(ctx.phase_history) == list(SIX_PHASES), "Condition must be true"


def test_run_capability_offline_mode_default():
    ctx = run_capability("evaluation")
    assert ctx.offline_mode is True, "offline_mode is not valid"


def test_run_capability_offline_mode_false():
    ctx = run_capability("evaluation", offline_mode=False)
    assert ctx.offline_mode is False, "offline_mode is not valid"


def test_run_capability_summary_populated():
    ctx = run_capability("tokenization")
    assert ctx.summary.get("capability") == "tokenization", "Condition must be true"


def test_run_capability_custom_router():
    plan = CapabilityPlan(name="custom_cap", construction_steps=("step_a",))
    router = CapabilityRouter(plans=[plan])
    ctx = run_capability("custom_cap", router=router)
    assert ctx.capability == "custom_cap", "capability is not valid"
    assert any("custom_cap:step_a" in a for a in ctx.artifacts), "Condition must be true"


def test_orchestrator_phase_override_is_called():
    called: list[str] = []

    def custom_prep(ctx: WorkflowContext, plan: CapabilityPlan) -> None:
        called.append("custom_prep_called")

    plan = CapabilityPlan(
        name="override_cap",
        phase_overrides={"Preparation": custom_prep},
    )
    router = CapabilityRouter(plans=[plan])
    run_capability("override_cap", router=router)
    assert "custom_prep_called" in called, "Condition must be true"


def test_run_capability_unknown_raises_key_error():
    with pytest.raises(KeyError):
        run_capability("nonexistent_capability_xyz")
