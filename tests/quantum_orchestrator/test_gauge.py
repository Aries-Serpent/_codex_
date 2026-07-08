#     assert np.allclose(, "Condition must be true"
#         momentum_curr, simple_task.spinor.total_probability * simple_task.velocity, rtol=1e-6
#     )


def test_noether_continuity_equation(multi_task_state):
    """Test continuity equation verification."""
    noether = NoetherCurrent()

    # Create slightly evolved state
    state_after = OrchestratorState(
        tasks=multi_task_state.tasks.copy(),
        timestamp=0.01,
        constants=multi_task_state.constants,
    )

    result = noether.verify_continuity(multi_task_state, state_after, dt=0.01, tolerance=1e-3)

    assert "max_violation" in result, "Result must not be empty"
    assert "is_conserved" in result, "Result must not be empty"
    assert "task_results" in result, "Result must not be empty"


# ============================================================================
# GaugeChecker Tests
# ============================================================================


def test_gauge_checker_check_all(multi_task_state):
    """Test comprehensive gauge check."""
    checker = GaugeChecker()

    results = checker.check_all(multi_task_state, tolerance=1e-6)

    assert "u1_invariance" in results, "Result must not be empty"
    assert "total_momentum" in results, "Result must not be empty"
    assert "total_energy" in results, "Result must not be empty"
    assert "all_passed" in results, "Result must not be empty"
    assert results["all_passed"], "Result must not be empty"


def test_gauge_checker_verify_all(multi_task_state):
    """Test comprehensive conservation verification."""
    checker = GaugeChecker()

    # Create evolved state
    state_after = OrchestratorState(
        tasks=multi_task_state.tasks.copy(),
        timestamp=0.1,
        constants=multi_task_state.constants,
    )

    results = checker.verify_all(multi_task_state, state_after, dt=0.1, tolerance=1e-3)

    assert "momentum_conservation" in results, "Result must not be empty"
    assert "energy_conservation" in results, "Result must not be empty"
    assert "continuity" in results, "Result must not be empty"
    assert "all_passed" in results, "Result must not be empty"


# ============================================================================
# ConservationEnforcer Tests
# ============================================================================


def test_conservation_enforcer_probability(simple_state):
    """Test probability conservation enforcement."""
    enforcer = ConservationEnforcer(auto_repair=True)

    # Violate probability conservation
    simple_state.tasks["task_1"].spinor.components *= 2.0

    repaired, was_repaired = enforcer.enforce_probability_conservation(
        simple_state, tolerance=1e-10
    )

    assert was_repaired, "was_repaired is not valid"
    assert abs(repaired.tasks["task_1"].spinor.total_probability - 1.0) < 1e-10, "Condition must be true"


def test_conservation_enforcer_no_repair_needed(simple_state):
    """Test enforcer when no repair is needed."""
    enforcer = ConservationEnforcer(auto_repair=True)

    # Normalize first
    simple_state.tasks["task_1"].spinor.normalize()

    _repaired, was_repaired = enforcer.enforce_probability_conservation(
        simple_state, tolerance=1e-10
    )

    assert not was_repaired, "Condition must be true"


def test_conservation_enforcer_logging(simple_state):
    """Test violation logging."""
    enforcer = ConservationEnforcer(auto_repair=True)

    # Violate conservation
    simple_state.tasks["task_1"].spinor.components *= 3.0

    enforcer.enforce_probability_conservation(simple_state)

    violations = enforcer.get_violations()
    assert len(violations) > 0, "Violations must not be empty"
    assert violations[0]["type"] == "probability_violation", "Condition must be true"
    assert violations[0]["task_id"] == "task_1", "Condition must be true"


def test_conservation_enforcer_clear_log(simple_state):
    """Test clearing violation log."""
    enforcer = ConservationEnforcer(auto_repair=True)

    # Create violation
    simple_state.tasks["task_1"].spinor.components *= 2.0
    enforcer.enforce_probability_conservation(simple_state)

    assert len(enforcer.get_violations()) > 0, "Collection must not be empty"

    enforcer.clear_violations()
    assert len(enforcer.get_violations()) == 0, "Collection must not be empty"


def test_conservation_enforcer_no_auto_repair(simple_state):
    """Test enforcer with auto_repair disabled."""
    enforcer = ConservationEnforcer(auto_repair=False)

    # Violate conservation
    simple_state.tasks["task_1"].spinor.components *= 2.0

    repaired, was_repaired = enforcer.enforce_probability_conservation(
        simple_state, tolerance=1e-10
    )

    # Should detect but not repair
    assert not was_repaired, "Condition must be true"
    assert len(enforcer.get_violations()) > 0, "Collection must not be empty"
    # Probability still violated
    assert abs(repaired.tasks["task_1"].spinor.total_probability - 1.0) > 0.1, "Value must be greater than zero"


# ============================================================================
# Integration Tests
# ============================================================================


def test_full_symmetry_workflow(multi_task_state):
    """Test complete symmetry checking workflow."""
    # Initialize all components
    gauge = U1GaugeTransform()
    trans = TranslationSymmetry()
    TimeTranslationSymmetry()
    checker = GaugeChecker()
    enforcer = ConservationEnforcer()

    # 1. Check initial state
    initial_check = checker.check_all(multi_task_state)
    assert initial_check["all_passed"], "Condition must be true"

    # 2. Apply U(1) transformation
    gauge.apply_global(multi_task_state, np.pi / 4)
    u1_result = gauge.verify_invariance(multi_task_state)
    assert u1_result.is_invariant, "Result must not be empty"

    # 3. Apply translation
    displacement = np.array([0.1, 0.0, 0.0, 0.0, 0.0])
    trans.apply_translation(multi_task_state, displacement)

    # 4. Enforce conservation
    repaired, _was_repaired = enforcer.enforce_probability_conservation(multi_task_state)

    # 5. Final verification
    final_check = checker.check_all(repaired)
    assert final_check["all_passed"], "Condition must be true"


def test_symmetry_type_enum():
    """Test SymmetryType enum."""
    assert SymmetryType.U1_PHASE.value == "u1_phase", "Value must be initialized"
    assert SymmetryType.TRANSLATION.value == "translation", "Value must be initialized"
    assert SymmetryType.TIME_TRANSLATION.value == "time_translation", "Value must be initialized"


def test_transformation_result_serialization():
    """Test TransformationResult to_dict."""
    result = TransformationResult(
        transformed_state=Mock(),
        is_invariant=True,
        deviation=1e-10,
        details={"test": "value"},
    )

    data = result.to_dict()
    assert data["is_invariant"] is True, "Data must not be empty"
    assert data["deviation"] == 1e-10, "Data must not be empty"
    assert data["details"]["test"] == "value", "Data must not be empty"
