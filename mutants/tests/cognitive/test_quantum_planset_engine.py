import pytest

#         assert math.isclose(, "Condition must be true"
#             step.effective_amplitude(),
#             step.physics.amplitude(),
#             rel_tol=1e-9,
#         )
# * QuantumPlansetEngine.generate — all 6 built-in templates (incl. QI_TESTING)
# * QuantumPlansetEngine.collapse — ordering, entanglement promotion
# * QuantumPlansetEngine.apply_decoherence — amplitude decay
# * QuantumPlansetEngine.interference — constructive merging
# * QuantumPlansetEngine.save / load — round-trip JSON
# * Context-driven momentum boosts
# * Edge cases: empty plansets, zero energy, all-dead steps
#     """
#     Tests for the QI_TESTING improvement area that drives the
#     quantum-compliance-tuning-agent iterative tuning loop via QuantumPlansetEngine.
# from __future__ import annotations
#         assert math.isclose(, "Condition must be true"
#             step.effective_amplitude(),
#             step.physics.amplitude(),
#             rel_tol=1e-9,
#         )
# from codex.cognitive.quantum_planset_engine import (
#     EntanglementBond,
#     ImprovementArea,
#     PhysicsParams,
#     PlanStep,
#     QuantumPlanset,
#     QuantumPlansetEngine,
#     StepStatus,
# )
#         step = _make_step(decoherence_sessions=0)
#         assert math.isclose(, "Condition must be true"
#             step.effective_amplitude(),
#             step.physics.amplitude(),
#             rel_tol=1e-9,
#         )
# def _make_step(
#     step_id: str = "S-01",
#     agent: str = "test-agent",
#     action: str = "do something",
#     impact: float = 0.8,
#     confidence: float = 0.9,
#     momentum: float = 5.0,
#     energy: float = 10.0,
#     risk: float = 0.1,
#     friction: float = 0.1,
#     decoherence_sessions: int = 0,
#     status: StepStatus = StepStatus.PENDING,
#     entangled_with: list | None = None,
# ) -> PlanStep:
#     return PlanStep(
#         step_id=step_id,
#         agent=agent,
#         action=action,
#         description="test step",
#         physics=PhysicsParams(
#             impact=impact,
#             confidence=confidence,
#             momentum=momentum,
#             energy=energy,
#             risk=risk,
#             friction=friction,
#         ),
#         decoherence_sessions=decoherence_sessions,
#         status=status,
#         entangled_with=entangled_with or [],
#     )
#         step = _make_step(decoherence_sessions=0)
#         assert math.isclose(, "Condition must be true"
#             step.effective_amplitude(),
#             step.physics.amplitude(),
#             rel_tol=1e-9,
#         )
# 
#         step = _make_step(decoherence_sessions=0)
#         assert math.isclose(, "Condition must be true"
#             step.effective_amplitude(),
#             step.physics.amplitude(),
#             rel_tol=1e-9,
#         )
#         expected = (0.9 * 0.9 * 9.0) / (5.0 * 1.1 * 1.1)
#         assert math.isclose(p.score(), expected, rel_tol=1e-9)
# 
#     def test_score_zero_energy(self):
#         p = PhysicsParams(energy=0.0)
#         assert p.score() == 0.0, "Condition must be true"
# 
#     def test_score_negative_energy_guarded(self):
#         p = PhysicsParams(energy=-1.0)
#         assert p.score() == 0.0, "Condition must be true"
# 
#     def test_amplitude_is_sqrt_of_score(self):
#         p = PhysicsParams(
#             impact=1.0, confidence=1.0, momentum=4.0, energy=4.0, risk=0.0, friction=0.0
#         )
#         assert math.isclose(p.amplitude(), math.sqrt(p.score()), rel_tol=1e-9)
# 
#     def test_amplitude_non_negative(self):
#         p = PhysicsParams(impact=0.0)
#         assert p.amplitude() == 0.0, "Condition must be true"
#         step = _make_step(decoherence_sessions=0)
#         assert math.isclose(, "Condition must be true"
#             step.effective_amplitude(),
#             step.physics.amplitude(),
#             rel_tol=1e-9,
#         )
# 
#         step = _make_step(decoherence_sessions=0)
#         assert math.isclose(, "Condition must be true"
#             step.effective_amplitude(),
#             step.physics.amplitude(),
#             rel_tol=1e-9,
#         )
#             step.physics.amplitude(),
#             rel_tol=1e-9,
#         )
# 
#     def test_effective_amplitude_decays(self):
#         step_fresh = _make_step(decoherence_sessions=0)
#         step_aged = _make_step(decoherence_sessions=5)  # one half-life
#         assert step_aged.effective_amplitude() < step_fresh.effective_amplitude(), "Condition must be true"
#         assert math.isclose(, "Condition must be true"
#             step_aged.effective_amplitude(),
#             step_fresh.effective_amplitude() * 0.5,
#             rel_tol=1e-6,
#         )
# 
#     def test_is_viable_fresh(self):
#         step = _make_step()
#         assert step.is_viable(), "Condition must be true"
# 
#     def test_is_viable_over_decohered(self):
#         # After 100 half-lives amplitude → 0
#         step = _make_step(decoherence_sessions=500)
#         assert not step.is_viable(), "Condition must be true"
# 
#     def test_serialise_round_trip(self):
#         step = _make_step(step_id="ROUND-01", entangled_with=["ROUND-02"])
#         restored = PlanStep.from_dict(step.to_dict())
#         assert restored.step_id == step.step_id, "step_id is not valid"
#         assert restored.agent == step.agent, "agent is not valid"
#         assert restored.status == step.status, "status is not valid"
#         assert math.isclose(restored.physics.impact, step.physics.impact, rel_tol=1e-9)
#         assert restored.entangled_with == ["ROUND-02"], "entangled_with is not valid"
# 
#     def test_to_dict_contains_amplitude_and_score(self):
#         step = _make_step()
#         d = step.to_dict()
#         assert "effective_amplitude" in d, "Condition must be true"
#         assert "physics_score" in d, "Condition must be true"
#         assert d["effective_amplitude"] >= 0.0, "Value must be greater than zero"
# 
#     def test_status_roundtrip(self):
#         step = _make_step(status=StepStatus.COMPLETE)
#         restored = PlanStep.from_dict(step.to_dict())
#         assert restored.status == StepStatus.COMPLETE, "status is not valid"
#         ps = self._planset_with_steps(s1, s2)
#         assert math.isclose(, "Condition must be true"
#             ps.total_amplitude(),
#             s1.effective_amplitude() + s2.effective_amplitude(),
#         )
# 
#         ps = self._planset_with_steps(s1, s2)
#         assert math.isclose(, "Condition must be true"
#             ps.total_amplitude(),
#             s1.effective_amplitude() + s2.effective_amplitude(),
#         )
#             planset_id="TEST-001",
#             area="CUSTOM",
#             steps=list(steps),
#         )
# 
#     def test_viable_steps_excludes_dead(self):
#         live = _make_step("A")
#         dead = _make_step("B", decoherence_sessions=500)
#         ps = self._planset_with_steps(live, dead)
#         assert ps.viable_steps() == [live], "Condition must be true"
# 
#     def test_total_amplitude(self):
#         s1 = _make_step(
#         s1 = _make_step(
#             "A", momentum=4.0, energy=4.0, risk=0.0, friction=0.0, impact=1.0, confidence=1.0
#         )
#         s2 = _make_step(
#             "B", momentum=4.0, energy=4.0, risk=0.0, friction=0.0, impact=1.0, confidence=1.0
#         )
#         ps = self._planset_with_steps(s1, s2)
#         assert math.isclose(, "Condition must be true"
#             ps.total_amplitude(),
#             s1.effective_amplitude() + s2.effective_amplitude(),
#         )
#     def test_probability_sums_to_one(self):
#         steps = [_make_step(f"S{i}") for i in range(4)]
#         ps = self._planset_with_steps(*steps)
#         total_prob = sum(ps.probability(s) for s in ps.viable_steps())
#         assert math.isclose(total_prob, 1.0, rel_tol=1e-9)
# 
#     def test_probability_zero_when_no_viable(self):
#         dead = _make_step("X", decoherence_sessions=500)
#         ps = self._planset_with_steps(dead)
#         assert ps.probability(dead) == 0.0, "Condition must be true"
# 
#     def test_serialise_round_trip(self):
#         step = _make_step("RT-01", entangled_with=["RT-02"])
#         bond = EntanglementBond("RT-01", "RT-02", 0.9)
#         ps = QuantumPlanset(
#             planset_id="RT-PS",
#             area="CUSTOM",
#             steps=[step],
#             entanglement_bonds=[bond],
#             context={"key": "val"},
#         )
#         restored = QuantumPlanset.from_dict(ps.to_dict())
#         assert restored.planset_id == ps.planset_id, "planset_id is not valid"
#         assert len(restored.steps) == 1, "Collection must not be empty"
#         assert len(restored.entanglement_bonds) == 1, "Collection must not be empty"
#         assert restored.context == {"key": "val"}, "context is not valid"


# ---------------------------------------------------------------------------
# QuantumPlansetEngine — generate
# ---------------------------------------------------------------------------


class TestGenerate:

    @pytest.fixture
    def engine(self):
        return QuantumPlansetEngine()

    @pytest.mark.parametrize("area", [a.value for a in ImprovementArea])
    def test_generate_all_templates(self, engine, area):
        ps = engine.generate(area)
        assert ps.area == area, "area is not valid"
        assert len(ps.steps) > 0, "Collection must not be empty"
        assert all(s.is_viable() for s in ps.steps), "Condition must be true"

    def test_generate_planset_id_contains_area(self, engine):
        ps = engine.generate(ImprovementArea.CI_SELF_HEALING)
        assert ImprovementArea.CI_SELF_HEALING.value in ps.planset_id, "Value must be initialized"

    def test_generate_with_extra_steps(self, engine):
        extra = _make_step("EXTRA-01")
        ps = engine.generate(ImprovementArea.COVERAGE_IMPROVEMENT, extra_steps=[extra])
        ids = [s.step_id for s in ps.steps]
        assert "EXTRA-01" in ids, "Condition must be true"

    def test_generate_builds_entanglement_bonds(self, engine):
        ps = engine.generate(ImprovementArea.SECURITY_REMEDIATION)
        bond_pairs = {(b.step_a, b.step_b) for b in ps.entanglement_bonds}
        # SEC-02 is entangled with SEC-01
        assert any("SEC-01" in pair and "SEC-02" in pair for pair in bond_pairs), "Condition must be true"

    def test_context_momentum_boost_security(self, engine):
        ps_low = engine.generate(ImprovementArea.SECURITY_REMEDIATION, context={"open_alerts": 10})
        ps_high = engine.generate(ImprovementArea.SECURITY_REMEDIATION, context={"open_alerts": 60})
        sec01_low = next(s for s in ps_low.steps if s.step_id == "SEC-01")
        sec01_high = next(s for s in ps_high.steps if s.step_id == "SEC-01")
        assert sec01_high.physics.momentum > sec01_low.physics.momentum, "momentum must be greater than zero"

    def test_context_momentum_boost_coverage(self, engine):
        ps_high_cov = engine.generate(
            ImprovementArea.COVERAGE_IMPROVEMENT, context={"coverage_pct": 85}
        )
        ps_low_cov = engine.generate(
            ImprovementArea.COVERAGE_IMPROVEMENT, context={"coverage_pct": 55}
        )
        cov01_high = next(s for s in ps_high_cov.steps if s.step_id == "COV-01")
        cov01_low = next(s for s in ps_low_cov.steps if s.step_id == "COV-01")
        assert cov01_low.physics.momentum >= cov01_high.physics.momentum, "momentum must be greater than zero"

    def test_generate_custom_area(self, engine):
        extra = _make_step("CUSTOM-01")
        ps = engine.generate("CUSTOM_BESPOKE", extra_steps=[extra])
        assert ps.area == "CUSTOM_BESPOKE", "area is not valid"
        assert len(ps.steps) == 1, "Collection must not be empty"


# ---------------------------------------------------------------------------
# QuantumPlansetEngine — collapse
# ---------------------------------------------------------------------------


class TestCollapse:

    @pytest.fixture
    def engine(self):
        return QuantumPlansetEngine()

    def test_collapse_returns_viable_steps_only(self, engine):
        live = _make_step("L-01")
        dead = _make_step("D-01", decoherence_sessions=500)
        ps = QuantumPlanset("TEST", "CUSTOM", steps=[live, dead])
        path = engine.collapse(ps)
        assert all(s.step_id != "D-01" for s in path), "step_id is not valid"

    def test_collapse_ordered_by_amplitude(self, engine):
        high = _make_step("HIGH", momentum=9.0, energy=5.0)
        low = _make_step("LOW", momentum=1.0, energy=20.0)
        ps = QuantumPlanset("TEST", "CUSTOM", steps=[low, high])
        path = engine.collapse(ps)
        assert path[0].step_id == "HIGH", "step_id is not valid"

    def test_collapse_promotes_entangled_partner(self, engine):
        anchor = _make_step("ANCHOR", entangled_with=["PARTNER"])
        partner = _make_step("PARTNER", momentum=0.5, energy=30.0)  # low amplitude
        weak_other = _make_step("WEAK", momentum=0.6, energy=28.0)
        ps = QuantumPlanset("TEST", "CUSTOM", steps=[anchor, weak_other, partner])
        path = engine.collapse(ps)
        ids = [s.step_id for s in path]
        # PARTNER must appear immediately after ANCHOR
        anchor_idx = ids.index("ANCHOR")
        partner_idx = ids.index("PARTNER")
        assert partner_idx == anchor_idx + 1, "partner_idx is not valid"

    def test_collapse_empty_planset(self, engine):
        ps = QuantumPlanset("EMPTY", "CUSTOM", steps=[])
        path = engine.collapse(ps)
        assert path == [], "path is not valid"

    def test_collapse_all_complete(self, engine):
        done = _make_step("D", status=StepStatus.COMPLETE)
        ps = QuantumPlanset("TEST", "CUSTOM", steps=[done])
        assert engine.collapse(ps) == [], "Condition must be true"

    def test_collapse_updates_collapsed_at(self, engine):
        ps = QuantumPlanset("TEST", "CUSTOM", steps=[_make_step("S")])
        assert ps.collapsed_at is None, "collapsed_at is not valid"
        engine.collapse(ps)
        assert ps.collapsed_at is not None, "collapsed_at must be initialized"

    def test_collapse_security_template(self, engine):
        ps = engine.generate(ImprovementArea.SECURITY_REMEDIATION)
        path = engine.collapse(ps)
        assert len(path) >= 3, "Path must not be empty"
        assert path[0].step_id == "SEC-01", "step_id is not valid"

    def test_collapse_no_duplicates(self, engine):
        steps = [_make_step(f"S{i}", entangled_with=[f"S{i-1}"] if i > 0 else []) for i in range(5)]
        ps = QuantumPlanset("TEST", "CUSTOM", steps=steps)
        path = engine.collapse(ps)
        ids = [s.step_id for s in path]
        assert len(ids) == len(set(ids)), "Ids must not be empty"


# ---------------------------------------------------------------------------
# QuantumPlansetEngine — apply_decoherence
# ---------------------------------------------------------------------------


class TestDecoherence:

    def test_decoherence_increments_sessions(self):
        engine = QuantumPlansetEngine()
        step = _make_step("D-01")
        ps = QuantumPlanset("TEST", "CUSTOM", steps=[step])
        engine.apply_decoherence(ps, sessions=3)
        assert step.decoherence_sessions == 3, "decoherence_sessions is not valid"

    def test_decoherence_reduces_amplitude(self):
        engine = QuantumPlansetEngine()
        step = _make_step("D-02")
        original = step.effective_amplitude()
        ps = QuantumPlanset("TEST", "CUSTOM", steps=[step])
        engine.apply_decoherence(ps, sessions=5)
        assert step.effective_amplitude() < original, "Condition must be true"

    def test_decoherence_skips_complete_steps(self):
        engine = QuantumPlansetEngine()
        step = _make_step("DONE", status=StepStatus.COMPLETE)
        ps = QuantumPlanset("TEST", "CUSTOM", steps=[step])
        engine.apply_decoherence(ps, sessions=10)
        assert step.decoherence_sessions == 0, "decoherence_sessions is not valid"


# ---------------------------------------------------------------------------
# QuantumPlansetEngine — interference
# ---------------------------------------------------------------------------


class TestInterference:

    def test_interference_merges_steps(self):
        engine = QuantumPlansetEngine()
        s1 = _make_step("A", action="fix lints")
        s2 = _make_step("B", action="fix types")
        s3 = _make_step("C", action="fix lints")  # overlaps with s1 by action
        ps_a = QuantumPlanset("PA", "AREA_A", steps=[s1])
        ps_b = QuantumPlanset("PB", "AREA_B", steps=[s2, s3])
        merged = engine.interference(ps_a, ps_b)
        actions = [s.action for s in merged.steps]
        # "fix lints" should appear once (merged), "fix types" once
        assert actions.count("fix lints") == 1, "Count must be greater than zero"
        assert "fix types" in actions, "Condition must be true"

    def test_interference_boosts_overlapping_momentum(self):
        engine = QuantumPlansetEngine()
        s_a = _make_step("A", action="scan", momentum=3.0)
        s_b = _make_step("B", action="scan", momentum=4.0)
        ps_a = QuantumPlanset("PA", "A", steps=[s_a])
        ps_b = QuantumPlanset("PB", "B", steps=[s_b])
        merged = engine.interference(ps_a, ps_b)
        merged_step = next(s for s in merged.steps if s.action == "scan")
        # Constructive interference: momentum = 3.0 + 4.0 = 7.0
        assert math.isclose(merged_step.physics.momentum, 7.0, rel_tol=1e-9)

    def test_interference_area_combines(self):
        engine = QuantumPlansetEngine()
        ps_a = QuantumPlanset("PA", "AREA_X", steps=[_make_step("A")])
        ps_b = QuantumPlanset("PB", "AREA_Y", steps=[_make_step("B")])
        merged = engine.interference(ps_a, ps_b)
        assert "AREA_X" in merged.area and "AREA_Y" in merged.area, "Condition must be true"


# ---------------------------------------------------------------------------
# QuantumPlansetEngine — persistence
# ---------------------------------------------------------------------------


class TestPersistence:

    def test_save_and_load_round_trip(self, tmp_path):
        engine = QuantumPlansetEngine(planset_dir=tmp_path)
        ps = engine.generate(ImprovementArea.CI_SELF_HEALING, context={"failing_checks": 7})
        saved_path = engine.save(ps)
        assert saved_path.exists(), "Condition must be true"

        restored = engine.load(saved_path)
        assert restored.planset_id == ps.planset_id, "planset_id is not valid"
        assert restored.area == ps.area, "area is not valid"
        assert len(restored.steps) == len(ps.steps), "Collection must not be empty"
        assert restored.context == ps.context, "context is not valid"

    def test_save_custom_path(self, tmp_path):
        engine = QuantumPlansetEngine()
        ps = engine.generate(ImprovementArea.DOCUMENTATION_HYGIENE)
        target = tmp_path / "custom" / "planset.json"
        engine.save(ps, path=target)
        assert target.exists(), "Condition must be true"
        data = json.loads(target.read_text())
        assert data["area"] == ImprovementArea.DOCUMENTATION_HYGIENE.value, "Data must not be empty"

    def test_load_preserves_entanglement_bonds(self, tmp_path):
        engine = QuantumPlansetEngine(planset_dir=tmp_path)
        ps = engine.generate(ImprovementArea.SECURITY_REMEDIATION)
        saved = engine.save(ps)
        restored = engine.load(saved)
        assert len(restored.entanglement_bonds) == len(ps.entanglement_bonds), "Collection must not be empty"


# ---------------------------------------------------------------------------
# QuantumPlansetEngine — summary
# ---------------------------------------------------------------------------


class TestSummary:

    def test_summary_contains_planset_id(self):
        engine = QuantumPlansetEngine()
        ps = engine.generate(ImprovementArea.COVERAGE_IMPROVEMENT)
        s = engine.summary(ps)
        assert ps.planset_id in s, "Condition must be true"

    def test_summary_contains_area(self):
        engine = QuantumPlansetEngine()
        ps = engine.generate(ImprovementArea.DEPENDENCY_MODERNISATION)
        s = engine.summary(ps)
        assert ImprovementArea.DEPENDENCY_MODERNISATION.value in s, "Value must be initialized"


# ---------------------------------------------------------------------------
# Integration: full generate → collapse → save → load cycle
# ---------------------------------------------------------------------------


class TestIntegration:

    def test_full_cycle_security(self, tmp_path):
        engine = QuantumPlansetEngine(planset_dir=tmp_path)
        ps = engine.generate(
            ImprovementArea.SECURITY_REMEDIATION,
            context={"open_alerts": 100},
        )
        path = engine.collapse(ps)
        assert path[0].step_id == "SEC-01", "step_id is not valid"

        saved = engine.save(ps)
        restored = engine.load(saved)
        path2 = engine.collapse(restored)
        assert [s.step_id for s in path2] == [s.step_id for s in path], "Condition must be true"

    def test_decoherence_then_collapse_shrinks_path(self):
        engine = QuantumPlansetEngine()
        ps = engine.generate(ImprovementArea.DOCUMENTATION_HYGIENE)
        full_path = engine.collapse(ps)

        engine.apply_decoherence(ps, sessions=100)  # extreme ageing
        short_path = engine.collapse(ps)
        assert len(short_path) <= len(full_path), "Short_path must not be empty"

    def test_interference_then_collapse(self):
        engine = QuantumPlansetEngine()
        ps_a = engine.generate(ImprovementArea.SECURITY_REMEDIATION)
        ps_b = engine.generate(ImprovementArea.CI_SELF_HEALING)
        merged = engine.interference(ps_a, ps_b)
        path = engine.collapse(merged)
        assert len(path) > 0, "Path must not be empty"


# ---------------------------------------------------------------------------
# QI_TESTING: Quantum-Inspired Testing via quantum-compliance-tuning-agent
# ---------------------------------------------------------------------------


class TestQITesting:
    """
    Tests for the QI_TESTING improvement area that drives the
    quantum-compliance-tuning-agent iterative tuning loop via QuantumPlansetEngine.
    """

    @pytest.fixture
    def engine(self) -> QuantumPlansetEngine:
        return QuantumPlansetEngine()

    def test_generate_qi_testing_planset(self, engine):
        ps = engine.generate(ImprovementArea.QI_TESTING)
        assert ps.area == ImprovementArea.QI_TESTING, "area is not valid"
        assert len(ps.steps) == 7, "Collection must not be empty"
        ids = [s.step_id for s in ps.steps]
        assert ids == ["QI-01", "QI-02", "QI-03", "QI-04", "QI-05", "QI-06", "QI-07"]

    def test_all_qi_steps_target_qi_agent(self, engine):
        ps = engine.generate(ImprovementArea.QI_TESTING)
        for step in ps.steps:
            assert step.agent == "quantum-compliance-tuning-agent", "agent is not valid"

    def test_qi_01_is_highest_amplitude(self, engine):
        """QI-01 (baseline run) should have the highest base amplitude — confidence=0.99."""
        ps = engine.generate(ImprovementArea.QI_TESTING)
        qi01 = next(s for s in ps.steps if s.step_id == "QI-01")
        qi07 = next(s for s in ps.steps if s.step_id == "QI-07")
        assert qi01.physics.confidence > qi07.physics.confidence, "confidence must be greater than zero"

    def test_qi_06_regression_guard_boosted_on_failing_patterns(self, engine):
        ps_low = engine.generate(ImprovementArea.QI_TESTING, context={"failing_patterns": 0})
        ps_high = engine.generate(ImprovementArea.QI_TESTING, context={"failing_patterns": 3})
        qi06_low = next(s for s in ps_low.steps if s.step_id == "QI-06")
        qi06_high = next(s for s in ps_high.steps if s.step_id == "QI-06")
        assert qi06_high.physics.momentum > qi06_low.physics.momentum, "momentum must be greater than zero"

    def test_qi_06_extra_boost_when_k1_near_limit(self, engine):
        ps_safe = engine.generate(
            ImprovementArea.QI_TESTING, context={"failing_patterns": 2, "k1": 0.20}
        )
        ps_risky = engine.generate(
            ImprovementArea.QI_TESTING, context={"failing_patterns": 2, "k1": 0.34}
        )
        qi06_safe = next(s for s in ps_safe.steps if s.step_id == "QI-06")
        qi06_risky = next(s for s in ps_risky.steps if s.step_id == "QI-06")
        assert qi06_risky.physics.momentum >= qi06_safe.physics.momentum, "momentum must be greater than zero"

    def test_qi_entanglement_chain(self, engine):
        """Each QI step (02-07) must be entangled with its predecessor."""
        ps = engine.generate(ImprovementArea.QI_TESTING)
        step_by_id = {s.step_id: s for s in ps.steps}
        pairs = [
            ("QI-02", "QI-01"),
            ("QI-03", "QI-02"),
            ("QI-04", "QI-03"),
            ("QI-05", "QI-04"),
            ("QI-06", "QI-05"),
            ("QI-07", "QI-06"),
        ]
        for child_id, parent_id in pairs:
            child = step_by_id[child_id]
            assert (parent_id in child.entangled_with, "Condition must be true"
            ), f"{child_id} should be entangled with {parent_id}"

    def test_collapse_starts_with_highest_amplitude_step(self, engine):
        """Without context, QI-02 leads (energy=5 < QI-01 energy=8 → higher score).
        With failing_patterns=2, QI-06 gets ×1.6 boost → leads instead."""
        # No context: QI-02 leads
        ps_plain = engine.generate(ImprovementArea.QI_TESTING)
        path_plain = engine.collapse(ps_plain)
        assert path_plain[0].step_id == "QI-02", "step_id is not valid"
        # With context: QI-06 momentum boosted → leads
        ps_ctx = engine.generate(ImprovementArea.QI_TESTING, context={"failing_patterns": 2})
        path_ctx = engine.collapse(ps_ctx)
        assert path_ctx[0].step_id == "QI-06", "step_id is not valid"

    def test_collapse_promotes_entangled_chain(self, engine):
        """QI-02 is entangled with QI-01 → QI-01 promoted to position immediately after QI-02."""
        ps = engine.generate(ImprovementArea.QI_TESTING)
        path = engine.collapse(ps)
        ids = [s.step_id for s in path]
        qi02_idx = ids.index("QI-02")
        assert (ids[qi02_idx + 1] == "QI-01", "Condition must be true"
        ), f"Expected QI-01 after QI-02 (entanglement promotion), got {ids[qi02_idx + 1]}"

    def test_qi_planset_serialise_round_trip(self, tmp_path, engine):
        ps = engine.generate(
            ImprovementArea.QI_TESTING, context={"failing_patterns": 1, "k1": 0.33}
        )
        saved = engine.save(ps, path=tmp_path / "qi_planset.json")
        restored = engine.load(saved)
        assert restored.area == ImprovementArea.QI_TESTING, "area is not valid"
        assert len(restored.steps) == 7, "Collection must not be empty"
        assert restored.context["failing_patterns"] == 1, "rest is not valid"

    def test_qi_decoherence_reduces_all_steps(self, engine):
        ps = engine.generate(ImprovementArea.QI_TESTING)
        orig_amplitudes = [s.effective_amplitude() for s in ps.steps]
        engine.apply_decoherence(ps, sessions=10)
        decayed = [s.effective_amplitude() for s in ps.steps]
        assert all(d < o for d, o in zip(decayed, orig_amplitudes))

    def test_qi_summary_contains_area(self, engine):
        ps = engine.generate(ImprovementArea.QI_TESTING)
        s = engine.summary(ps)
        assert ImprovementArea.QI_TESTING.value in s, "Value must be initialized"

    def test_qi_interference_with_security_remediation(self, engine):
        """QI_TESTING + SECURITY_REMEDIATION interference should yield a merged planset."""
        ps_qi = engine.generate(ImprovementArea.QI_TESTING)
        ps_sec = engine.generate(ImprovementArea.SECURITY_REMEDIATION)
        merged = engine.interference(ps_qi, ps_sec)
        assert ImprovementArea.QI_TESTING.value in merged.area, "Value must be initialized"
        path = engine.collapse(merged)
        assert len(path) > 0, "Path must not be empty"
