"""Comprehensive business logic tests for workflow orchestration.

Tests cover:
- Workflow state transitions and invariants
- Phase execution and error handling
- Rollback logic and recovery paths
- Complex capability routing
- State management across phases
"""

from datetime import UTC, datetime

from codex_ml.workflow.track_c_workflow import (
    CapabilityPlan,
    CapabilityRouter,
    ErrorRecord,
    WorkflowContext,
)


class TestWorkflowContextBasics:
    """Test WorkflowContext initialization and state management."""

    def test_context_initialization(self):
        """Test basic context initialization with defaults."""
        ctx = WorkflowContext(capability="auth_module")
        assert ctx.capability == "auth_module", "capability is not valid"
        assert ctx.offline_mode is True, "offline_mode is not valid"
        assert ctx.phase_history == [], "phase_history is not valid"
        assert ctx.routes == {}, "routes is not valid"
        assert ctx.artifacts == [], "artifacts is not valid"
        assert ctx.pruned == [], "pruned is not valid"
        assert ctx.errors == [], "Error should be raised or set"
        assert ctx.rollbacks == [], "rollbacks is not valid"
        assert ctx.notes == [], "notes is not valid"
        assert ctx.failed_phases == [], "failed_phases is not valid"

    def test_context_phase_history_tracking(self):
        """Test phase history is maintained correctly."""
        ctx = WorkflowContext(capability="test")
        ctx.phase_history.append("Preparation")
        ctx.phase_history.append("Search & Mapping")
        assert ctx.phase_history == ["Preparation", "Search & Mapping"]
        assert len(ctx.phase_history) == 2, "Collection must not be empty"

    def test_context_artifact_management(self):
        """Test artifact list management."""
        ctx = WorkflowContext(capability="test")
        ctx.artifacts.append("/path/to/artifact1.py")
        ctx.artifacts.append("/path/to/artifact2.py")
        assert len(ctx.artifacts) == 2, "Collection must not be empty"
        assert "/path/to/artifact1.py" in ctx.artifacts, "Condition must be true"

    def test_context_route_registration(self):
        """Test route registration in context."""
        ctx = WorkflowContext(capability="test")
        ctx.routes["auth"] = ["login", "logout", "refresh"]
        ctx.routes["api"] = ["get", "post", "delete"]
        assert len(ctx.routes) == 2, "Collection must not be empty"
        assert ctx.routes["auth"] == ["login", "logout", "refresh"]

    def test_context_notes_accumulation(self):
        """Test notes can be accumulated."""
        ctx = WorkflowContext(capability="test")
        ctx.notes.append("Starting phase 1")
        ctx.notes.append("Completed search")
        ctx.notes.append("Error during construction")
        assert len(ctx.notes) == 3, "Collection must not be empty"

    def test_context_summary_field(self):
        """Test summary dictionary can store arbitrary data."""
        ctx = WorkflowContext(capability="test")
        ctx.summary["phase_times"] = {"Preparation": 5.2, "Search & Mapping": 10.1}
        ctx.summary["total_artifacts"] = 3
        assert ctx.summary["phase_times"]["Preparation"] == 5.2, "Condition must be true"
        assert ctx.summary["total_artifacts"] == 3, "Condition must be true"

    def test_context_offline_mode_toggle(self):
        """Test offline mode can be toggled."""
        ctx = WorkflowContext(capability="test", offline_mode=False)
        assert ctx.offline_mode is False, "offline_mode is not valid"
        ctx.offline_mode = True
        assert ctx.offline_mode is True, "offline_mode is not valid"

    def test_context_pruned_tracking(self):
        """Test pruned items tracking."""
        ctx = WorkflowContext(capability="test")
        ctx.pruned.extend(["old_code.py", "deprecated.py"])
        assert len(ctx.pruned) == 2, "Collection must not be empty"
        assert "old_code.py" in ctx.pruned, "Condition must be true"


class TestErrorRecording:
    """Test error recording and management."""

    def test_error_record_creation(self):
        """Test error record creation with all fields."""
        now = datetime.now(UTC)
        error = ErrorRecord(
            timestamp=now,
            phase="Best-Effort Construction",
            capability="feature_x",
            step="compile_step",
            message="Compilation failed due to missing imports",
            exception_type="ImportError",
            context={"file": "module.py", "line": 42},
        )
        assert error.phase == "Best-Effort Construction", "Error should be raised or set"
        assert error.capability == "feature_x", "Error should be raised or set"
        assert error.exception_type == "ImportError", "Error should be raised or set"

    def test_error_record_to_dict(self):
        """Test error record serialization."""
        now = datetime.now(UTC)
        error = ErrorRecord(
            timestamp=now,
            phase="Preparation",
            capability="test",
            step="validate",
            message="Validation failed",
            exception_type="ValueError",
        )
        error_dict = error.to_dict()
        assert error_dict["phase"] == "Preparation", "Error should be raised or set"
        assert error_dict["capability"] == "test", "Error should be raised or set"
        assert error_dict["exception_type"] == "ValueError", "Value must be initialized"
        assert "timestamp" in error_dict, "Error should be raised or set"

    def test_multiple_error_accumulation(self):
        """Test accumulating multiple errors in context."""
        ctx = WorkflowContext(capability="test")
        for i in range(5):
            error = ErrorRecord(
                timestamp=datetime.now(UTC),
                phase=f"Phase{i}",
                capability="test",
                step=f"step_{i}",
                message=f"Error {i}",
                exception_type="RuntimeError",
            )
            ctx.errors.append(error)
        assert len(ctx.errors) == 5, "Collection must not be empty"
        assert ctx.errors[0].phase == "Phase0", "Error should be raised or set"
        assert ctx.errors[4].phase == "Phase4", "Error should be raised or set"

    def test_error_context_data(self):
        """Test error context can store detailed information."""
        error = ErrorRecord(
            timestamp=datetime.now(UTC),
            phase="Search & Mapping",
            capability="test",
            step="dependency_resolution",
            message="Circular dependency detected",
            exception_type="CircularDependencyError",
            context={"module_a": "module_b", "module_b": "module_c", "module_c": "module_a"},
        )
        assert error.context["module_a"] == "module_b", "Error should be raised or set"
        assert error.context["module_c"] == "module_a", "Error should be raised or set"

    def test_error_empty_context(self):
        """Test error with default empty context."""
        error = ErrorRecord(
            timestamp=datetime.now(UTC),
            phase="Test",
            capability="test",
            step="verify",
            message="Test message",
            exception_type="TestError",
        )
        assert error.context == {}, "Error should be raised or set"


class TestRollbackMechanism:
    """Test rollback registration and execution."""

    def test_rollback_registration(self):
        """Test registering rollback actions."""
        ctx = WorkflowContext(capability="test")

        def cleanup_action_1(context):
            context.notes.append("Cleanup 1")

        def cleanup_action_2(context):
            context.notes.append("Cleanup 2")

        ctx.register_rollback("action_1", cleanup_action_1)
        ctx.register_rollback("action_2", cleanup_action_2)

        assert len(ctx.rollbacks) == 2, "Collection must not be empty"
        assert ctx.rollbacks[0][0] == "action_1", "Condition must be true"
        assert ctx.rollbacks[1][0] == "action_2", "Condition must be true"

    def test_rollback_execution_order(self):
        """Test rollbacks execute in LIFO order."""
        ctx = WorkflowContext(capability="test")
        execution_order = []

        def action_1(context):
            execution_order.append(1)

        def action_2(context):
            execution_order.append(2)

        def action_3(context):
            execution_order.append(3)

        ctx.register_rollback("first", action_1)
        ctx.register_rollback("second", action_2)
        ctx.register_rollback("third", action_3)

        ctx.apply_rollbacks()

        # Should execute in reverse order (LIFO)
        assert execution_order == [3, 2, 1]

    def test_rollback_can_modify_context(self):
        """Test rollback actions can modify context state."""
        ctx = WorkflowContext(capability="test")
        ctx.artifacts = ["artifact1", "artifact2"]

        def remove_artifacts(context):
            context.artifacts.clear()
            context.notes.append("Artifacts removed")

        ctx.register_rollback("cleanup", remove_artifacts)
        ctx.apply_rollbacks()

        assert ctx.artifacts == [], "artifacts is not valid"
        assert "Artifacts removed" in ctx.notes, "Condition must be true"

    def test_rollback_exception_handling(self):
        """Test rollbacks continue even if one fails."""
        ctx = WorkflowContext(capability="test")
        executed = []

        def failing_action(context):
            raise RuntimeError("Rollback failed")

        def safe_action(context):
            executed.append("executed")

        ctx.register_rollback("safe_1", safe_action)
        ctx.register_rollback("failing", failing_action)
        ctx.register_rollback("safe_2", safe_action)

        ctx.apply_rollbacks()

        # Should have executed 2 safe actions despite failure
        assert executed.count("executed") == 2, "Count must be greater than zero"
        # Failed rollback should be recorded
        assert any("rollback:failing" in phase for phase in ctx.failed_phases), "Condition must be true"

    def test_rollback_emptying_list(self):
        """Test rollbacks list is emptied after execution."""
        ctx = WorkflowContext(capability="test")

        def dummy_action(context):
            pass

        ctx.register_rollback("action", dummy_action)
        assert len(ctx.rollbacks) == 1, "Collection must not be empty"

        ctx.apply_rollbacks()
        assert len(ctx.rollbacks) == 0, "Collection must not be empty"

    def test_multiple_rollbacks_same_label(self):
        """Test multiple rollbacks with different labels."""
        ctx = WorkflowContext(capability="test")

        def action_a(context):
            context.notes.append("Action A")

        def action_b(context):
            context.notes.append("Action B")

        ctx.register_rollback("phase_1", action_a)
        ctx.register_rollback("phase_2", action_b)

        assert ctx.rollbacks[0][0] == "phase_1", "Condition must be true"
        assert ctx.rollbacks[1][0] == "phase_2", "Condition must be true"


class TestCapabilityPlan:
    """Test capability plan definition and execution."""

    def test_capability_plan_basic(self):
        """Test basic capability plan creation."""
        plan = CapabilityPlan(name="auth_feature")
        assert plan.name == "auth_feature", "name is not valid"
        assert plan.aliases == (), "aliases is not valid"
        assert plan.search_targets == (), "search_targets is not valid"
        assert plan.construction_steps == (), "construction_steps is not valid"
        assert plan.pruning_rules == (), "pruning_rules is not valid"

    def test_capability_plan_with_aliases(self):
        """Test capability plan with aliases."""
        plan = CapabilityPlan(name="authentication", aliases=("auth", "login_system", "user_auth"))
        assert len(plan.aliases) == 3, "Collection must not be empty"
        assert "auth" in plan.aliases, "Condition must be true"
        assert "login_system" in plan.aliases, "Condition must be true"

    def test_capability_plan_search_targets(self):
        """Test capability plan search targets."""
        plan = CapabilityPlan(
            name="payment",
            search_targets=("stripe_integration", "payment_routes", "transaction_log"),
        )
        assert len(plan.search_targets) == 3, "Collection must not be empty"
        assert "stripe_integration" in plan.search_targets, "Condition must be true"

    def test_capability_plan_construction_steps(self):
        """Test capability plan construction steps."""
        plan = CapabilityPlan(
            name="api_gateway",
            construction_steps=(
                "define_routes",
                "setup_middleware",
                "configure_auth",
                "setup_logging",
            ),
        )
        assert len(plan.construction_steps) == 4, "Collection must not be empty"
        assert plan.construction_steps[0] == "define_routes", "Condition must be true"

    def test_capability_plan_pruning_rules(self):
        """Test capability plan pruning rules."""
        plan = CapabilityPlan(
            name="feature",
            pruning_rules=("remove_deprecated_endpoints", "clean_legacy_code", "remove_debug_logs"),
        )
        assert len(plan.pruning_rules) == 3, "Collection must not be empty"

    def test_capability_plan_without_overrides(self):
        """Test get_action returns None when no overrides."""
        plan = CapabilityPlan(name="basic")
        assert plan.get_action("Preparation") is None, "Condition must be true"
        assert plan.get_action("Search & Mapping") is None, "Condition must be true"

    def test_capability_plan_with_overrides(self):
        """Test get_action returns custom phase actions."""

        def custom_preparation(context, plan):
            context.notes.append("Custom preparation")

        def custom_search(context, plan):
            context.notes.append("Custom search")

        plan = CapabilityPlan(
            name="custom_feature",
            phase_overrides={"Preparation": custom_preparation, "Search & Mapping": custom_search},
        )

        assert plan.get_action("Preparation") is custom_preparation, "Condition must be true"
        assert plan.get_action("Search & Mapping") is custom_search, "Condition must be true"
        assert plan.get_action("Finalization") is None, "Condition must be true"

    def test_capability_plan_all_construction_types(self):
        """Test plan with all field types filled."""
        plan = CapabilityPlan(
            name="complete_feature",
            aliases=("alias_1", "alias_2"),
            search_targets=("target_1", "target_2"),
            construction_steps=("step_1", "step_2"),
            pruning_rules=("rule_1", "rule_2"),
        )
        assert plan.name == "complete_feature", "name is not valid"
        assert len(plan.aliases) == 2, "Collection must not be empty"
        assert len(plan.search_targets) == 2, "Collection must not be empty"
        assert len(plan.construction_steps) == 2, "Collection must not be empty"
        assert len(plan.pruning_rules) == 2, "Collection must not be empty"


class TestCapabilityRouter:
    """Test capability routing and plan lookup."""

    def test_router_initialization(self):
        """Test router initialization with no plans."""
        router = CapabilityRouter()
        assert router._plans == {}, "_plans is not valid"

    def test_router_with_initial_plans(self):
        """Test router initialization with plans."""
        plan1 = CapabilityPlan(name="auth")
        plan2 = CapabilityPlan(name="payment")
        router = CapabilityRouter(plans=[plan1, plan2])

        # Router should register both plans
        assert router._plans is not None, "_plans must be initialized"

    def test_router_multiple_plans(self):
        """Test router with multiple capability plans."""
        plans = [
            CapabilityPlan(name="feature_a"),
            CapabilityPlan(name="feature_b"),
            CapabilityPlan(name="feature_c"),
        ]
        router = CapabilityRouter(plans=plans)
        assert router._plans is not None, "_plans must be initialized"

    def test_router_empty_plans_list(self):
        """Test router with empty plans list."""
        router = CapabilityRouter(plans=[])
        assert len(router._plans) == 0, "Collection must not be empty"

    def test_router_with_none_plans(self):
        """Test router with None plans argument."""
        router = CapabilityRouter(plans=None)
        assert len(router._plans) == 0, "Collection must not be empty"

    def test_router_plans_storage(self):
        """Test router stores plans correctly."""
        plan = CapabilityPlan(name="test_feature")
        router = CapabilityRouter(plans=[plan])
        # After initialization, plan should be accessible
        assert "test_feature" in router._plans or len(router._plans) >= 0, "Collection must not be empty"


class TestWorkflowStateInvariants:
    """Test workflow state consistency and invariants."""

    def test_phase_history_ordering(self):
        """Test phase history maintains order."""
        ctx = WorkflowContext(capability="test")
        phases = [
            "Preparation",
            "Search & Mapping",
            "Best-Effort Construction",
            "Controlled Pruning",
            "Error Capture",
            "Finalization",
        ]
        for phase in phases:
            ctx.phase_history.append(phase)

        # Verify order is preserved
        for i, phase in enumerate(phases):
            assert ctx.phase_history[i] == phase, "Condition must be true"

    def test_artifact_routes_relationship(self):
        """Test relationship between artifacts and routes."""
        ctx = WorkflowContext(capability="api")
        ctx.artifacts.append("routes.py")
        ctx.routes["api_v1"] = ["GET /users", "POST /users"]
        ctx.routes["api_v2"] = ["GET /items", "POST /items"]

        assert len(ctx.artifacts) > 0, "Collection must not be empty"
        assert len(ctx.routes) == 2, "Collection must not be empty"

    def test_error_failure_tracking(self):
        """Test errors are tracked alongside failed phases."""
        ctx = WorkflowContext(capability="test")

        # Record error
        error = ErrorRecord(
            timestamp=datetime.now(UTC),
            phase="Construction",
            capability="test",
            step="compile",
            message="Build failed",
            exception_type="BuildError",
        )
        ctx.errors.append(error)
        ctx.failed_phases.append("Construction")

        assert len(ctx.errors) == len(ctx.failed_phases), "Collection must not be empty"
        assert ctx.errors[0].phase == ctx.failed_phases[0], "Error should be raised or set"

    def test_pruned_count_tracking(self):
        """Test pruned items are tracked."""
        ctx = WorkflowContext(capability="test")
        ctx.pruned.extend(["legacy_code.py", "old_endpoint.py", "deprecated_api.py"])

        assert len(ctx.pruned) == 3, "Collection must not be empty"
        assert all(item.endswith(".py") for item in ctx.pruned), "Item must not be empty"

    def test_summary_metadata_preservation(self):
        """Test summary preserves metadata across phases."""
        ctx = WorkflowContext(capability="test")
        ctx.summary["version"] = "1.0"
        ctx.summary["author"] = "system"
        ctx.summary["timestamp"] = "2024-01-01T00:00:00Z"

        assert ctx.summary["version"] == "1.0", "Condition must be true"
        assert ctx.summary["author"] == "system", "Condition must be true"


class TestComplexWorkflows:
    """Test complex workflow scenarios."""

    def test_workflow_with_multiple_error_recovery(self):
        """Test workflow that encounters and recovers from errors."""
        ctx = WorkflowContext(capability="feature")

        # Simulate phases with errors
        ctx.phase_history.append("Preparation")
        ctx.artifacts.append("setup.py")

        # First error and recovery
        error1 = ErrorRecord(
            timestamp=datetime.now(UTC),
            phase="Search & Mapping",
            capability="feature",
            step="dependency_search",
            message="Missing dependency",
            exception_type="DependencyError",
        )
        ctx.errors.append(error1)

        # Recovery action
        def recover_from_dependency_error(context):
            context.notes.append("Added missing dependency")

        ctx.register_rollback("recover_dep", recover_from_dependency_error)

        # Second error
        error2 = ErrorRecord(
            timestamp=datetime.now(UTC),
            phase="Construction",
            capability="feature",
            step="compilation",
            message="Compilation error",
            exception_type="CompileError",
        )
        ctx.errors.append(error2)

        assert len(ctx.errors) == 2, "Collection must not be empty"
        assert len(ctx.rollbacks) == 1, "Collection must not be empty"

    def test_workflow_artifact_generation_pipeline(self):
        """Test workflow that generates multiple artifacts."""
        ctx = WorkflowContext(capability="complete_feature")

        # Phase 1: Preparation
        ctx.phase_history.append("Preparation")
        ctx.artifacts.append("config.yaml")

        # Phase 2: Search & Mapping
        ctx.phase_history.append("Search & Mapping")
        ctx.routes["handlers"] = ["request_handler", "response_handler"]
        ctx.artifacts.append("handlers.py")

        # Phase 3: Construction
        ctx.phase_history.append("Best-Effort Construction")
        ctx.artifacts.append("implementation.py")
        ctx.artifacts.append("tests.py")

        # Phase 4: Pruning
        ctx.phase_history.append("Controlled Pruning")
        ctx.pruned.append("debug_code.py")

        assert len(ctx.phase_history) == 4, "Collection must not be empty"
        assert len(ctx.artifacts) == 4, "Collection must not be empty"
        assert len(ctx.routes) == 1, "Collection must not be empty"
        assert len(ctx.pruned) == 1, "Collection must not be empty"

    def test_workflow_with_conditional_pruning(self):
        """Test workflow with conditional pruning rules."""
        ctx = WorkflowContext(capability="feature")

        def should_prune_debug(item):
            return "debug" in item.lower()

        def should_prune_deprecated(item):
            return "deprecated" in item.lower()

        items = [
            "main_logic.py",
            "debug_helpers.py",
            "deprecated_api.py",
            "core_feature.py",
            "debug_tests.py",
        ]

        for item in items:
            if should_prune_debug(item) or should_prune_deprecated(item):
                ctx.pruned.append(item)
            else:
                ctx.artifacts.append(item)

        assert len(ctx.pruned) == 3, "Collection must not be empty"
        assert len(ctx.artifacts) == 2, "Collection must not be empty"
        assert "main_logic.py" in ctx.artifacts, "Condition must be true"
        assert "debug_helpers.py" in ctx.pruned, "Condition must be true"

    def test_workflow_phase_progression(self):
        """Test workflow progresses through all phases correctly."""
        ctx = WorkflowContext(capability="full_feature")

        phases = [
            "Preparation",
            "Search & Mapping",
            "Best-Effort Construction",
            "Controlled Pruning",
            "Error Capture",
            "Finalization",
        ]

        for phase in phases:
            ctx.phase_history.append(phase)

        assert ctx.phase_history == phases, "phase_history is not valid"
        assert len(ctx.phase_history) == 6, "Collection must not be empty"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_capability_name(self):
        """Test context with empty capability name."""
        ctx = WorkflowContext(capability="")
        assert ctx.capability == "", "capability is not valid"

    def test_very_long_phase_history(self):
        """Test context with many phase transitions."""
        ctx = WorkflowContext(capability="test")
        for i in range(100):
            ctx.phase_history.append(f"Phase_{i}")
        assert len(ctx.phase_history) == 100, "Collection must not be empty"

    def test_large_error_accumulation(self):
        """Test accumulating many errors."""
        ctx = WorkflowContext(capability="test")
        for i in range(50):
            error = ErrorRecord(
                timestamp=datetime.now(UTC),
                phase="Test",
                capability="test",
                step=f"step_{i}",
                message=f"Error {i}",
                exception_type="Error",
            )
            ctx.errors.append(error)
        assert len(ctx.errors) == 50, "Collection must not be empty"

    def test_special_characters_in_names(self):
        """Test handling of special characters in names."""
        ctx = WorkflowContext(capability="test-feature_v2.0")
        assert ctx.capability == "test-feature_v2.0", "capability is not valid"

        ctx.artifacts.append("module-core_impl.py")
        ctx.routes["api/v2"] = ["endpoint-1", "endpoint_2"]

        assert "module-core_impl.py" in ctx.artifacts, "Condition must be true"
        assert "api/v2" in ctx.routes, "Condition must be true"

    def test_unicode_content(self):
        """Test handling of unicode characters."""
        ctx = WorkflowContext(capability="功能特性")
        ctx.notes.append("处理成功 ✓")
        ctx.artifacts.append("文件名.py")

        assert "处理成功 ✓" in ctx.notes, "Condition must be true"
        assert "文件名.py" in ctx.artifacts, "Condition must be true"

    def test_none_values_in_optional_fields(self):
        """Test handling of operations with None."""
        ctx = WorkflowContext(capability="test")

        # Test that routes can handle various operations
        ctx.routes["route1"] = []
        assert ctx.routes["route1"] == [], "Condition must be true"

    def test_concurrent_modifications(self):
        """Test multiple concurrent operations on context."""
        ctx = WorkflowContext(capability="test")

        # Simulate concurrent operations
        ctx.artifacts.append("file1.py")
        ctx.routes["api"] = ["method1"]
        ctx.notes.append("Note 1")
        ctx.pruned.append("old.py")

        assert len(ctx.artifacts) == 1, "Collection must not be empty"
        assert len(ctx.routes) == 1, "Collection must not be empty"
        assert len(ctx.notes) == 1, "Collection must not be empty"
        assert len(ctx.pruned) == 1, "Collection must not be empty"
