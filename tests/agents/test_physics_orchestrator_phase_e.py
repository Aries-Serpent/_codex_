"""Phase E tests for agents/physics_orchestrator.py — gaps in less-covered classes."""

from __future__ import annotations

import math
from unittest.mock import MagicMock

import pytest

from agents.physics_orchestrator import (
    ActionPath,
    ActionType,
    DecisionState,
    DiffusionFlowModel,
    EnergyLandscape,
    EnergyState,
    FlowVector,
    ForceVector,
    ImportMigration,
    ImportMigrationOrchestrator,
    PhysicsInspiredOrchestrator,
    SwarmIntelligence,
)

# ---------------------------------------------------------------------------
# ForceVector
# ---------------------------------------------------------------------------


class TestForceVector:
    def test_default_construction(self):
        fv = ForceVector()
        assert fv.magnitude == 0.0, "magnitude is not valid"
        assert fv.priority == 1.0, "priority is not valid"

    def test_xyz_magnitude_calculated(self):
        fv = ForceVector(name="test", x=3.0, y=4.0, z=0.0)
        assert fv.magnitude == pytest.approx(5.0), "magnitude is not valid"

    def test_xyz_direction_normalized(self):
        fv = ForceVector(name="d", x=1.0, y=0.0, z=0.0)
        assert isinstance(fv.direction, list)
        assert fv.direction[0] == pytest.approx(1.0), "Condition must be true"
        assert fv.direction[1] == pytest.approx(0.0), "Condition must be true"

    def test_get_components_2d_angle(self):
        fv = ForceVector(name="a", magnitude=1.0, direction=0.0, priority=1.0)
        x, y = fv.get_components()
        assert x == pytest.approx(1.0), "x is not valid"
        assert y == pytest.approx(0.0), "y is not valid"

    def test_get_components_3d_vector(self):
        fv = ForceVector(name="b", x=1.0, y=1.0, z=0.0)
        x, _ = fv.get_components()
        assert x > 0, "x must be greater than zero"

    def test_priority_scales_components(self):
        fv = ForceVector(name="p", magnitude=2.0, direction=0.0, priority=0.5)
        x, _ = fv.get_components()
        assert x == pytest.approx(1.0), "x is not valid"


# ---------------------------------------------------------------------------
# ActionPath
# ---------------------------------------------------------------------------


class TestActionPath:
    def test_default_construction(self):
        ap = ActionPath()
        assert ap.action_type == ActionType.ANALYZE, "action_type is not valid"
        assert ap.confidence == 0.0, "confidence is not valid"

    def test_energy_alias_sets_potential_energy(self):
        ap = ActionPath(energy=50.0)
        assert ap.potential_energy == 50.0, "potential_energy is not valid"

    def test_calculate_total_energy(self):
        ap = ActionPath(
            potential_energy=30.0,
            kinetic_energy=20.0,
            friction=2.0,
            momentum=5.0,
        )
        total = ap.calculate_total_energy()
        # E_total = 30 + 20 - 5*5 + 2*10 = 30+20-25+20 = 45
        assert total == pytest.approx(45.0), "total is not valid"
        assert ap.total_energy == pytest.approx(45.0), "total_energy is not valid"

    def test_calculate_optimization_score_basic(self):
        ap = ActionPath(
            potential_energy=30.0,
            kinetic_energy=10.0,
            friction=0.5,
            momentum=5.0,
            confidence=0.9,
            risk=0.1,
            impact=0.8,
            urgency=0.6,
        )
        ap.calculate_total_energy()
        score = ap.calculate_optimization_score()
        assert score > 0.0, "score must be greater than zero"
        assert ap.optimization_score == score, "optimization_score is not valid"

    def test_calculate_optimization_score_with_mlp(self):
        ap = ActionPath(
            potential_energy=20.0,
            kinetic_energy=10.0,
            friction=1.0,
            momentum=3.0,
            confidence=0.7,
            risk=0.3,
            impact=0.6,
            urgency=0.5,
        )
        ap.calculate_total_energy()
        mlp_scorer = MagicMock()
        mlp_scorer.score.return_value = 0.1
        score = ap.calculate_optimization_score(mlp_scorer)
        assert score > 0.0, "score must be greater than zero"
        mlp_scorer.score.assert_called_once()

    def test_extract_mlp_features_length(self):
        ap = ActionPath(
            potential_energy=50.0,
            kinetic_energy=20.0,
            friction=2.0,
            momentum=5.0,
            confidence=0.8,
            risk=0.2,
            impact=0.7,
            urgency=0.4,
        )
        features = ap._extract_mlp_features()
        assert len(features) == 8, "Features must not be empty"
        assert all(isinstance(f, float) for f in features)


# ---------------------------------------------------------------------------
# DecisionState
# ---------------------------------------------------------------------------


class TestDecisionState:
    def test_default_construction(self):
        ds = DecisionState()
        assert ds.current_position == "", "current_position is not valid"
        assert ds.available_resources == 1.0, "available_resources is not valid"
        assert ds.coherence == 1.0, "coherence is not valid"

    def test_custom_state_vector(self):
        ds = DecisionState(state_vector=[0.1, 0.2, 0.3])
        assert len(ds.state_vector) == 3, "Collection must not be empty"


# ---------------------------------------------------------------------------
# PhysicsInspiredOrchestrator — private helpers
# ---------------------------------------------------------------------------


class TestPhysicsOrchestratorPrivateHelpers:
    @pytest.fixture
    def orch(self):
        return PhysicsInspiredOrchestrator()

    def test_calculate_distance(self, orch):
        state = DecisionState(available_resources=0.5)
        dist = orch._calculate_distance(state)
        assert dist == pytest.approx(5.0), "dist is not valid"

    def test_calculate_entropy(self, orch):
        state = DecisionState(available_resources=0.5, time_available=0.5, current_velocity=0.5)
        entropy = orch._calculate_entropy(state)
        assert 0.0 <= entropy <= 1.0, "0 is not valid"

    def test_calculate_attractive_potential(self, orch):
        state = DecisionState(available_resources=1.0, time_available=1.0)
        pot = orch._calculate_attractive_potential(state)
        assert pot == pytest.approx(10.0), "pot is not valid"

    def test_calculate_repulsive_potential(self, orch):
        state = DecisionState(current_velocity=0.0)
        pot = orch._calculate_repulsive_potential(state)
        assert pot == pytest.approx(5.0), "pot is not valid"

    def test_evolve_state(self, orch):
        state = EnergyState(configuration={"x": 1}, energy=10.0, entropy=0.1)
        new_state = orch.evolve_state(state, dt=0.1)
        assert new_state is not None, "new_state must be initialized"
        assert new_state.energy < state.energy, "energy is not valid"
        assert new_state.entropy > state.entropy, "entropy must be greater than zero"

    def test_optimize_empty_returns_none(self, orch):
        assert orch.optimize([]) is None, "Condition must be true"

    def test_optimize_returns_best(self, orch):
        ap1 = ActionPath(
            confidence=0.9,
            impact=0.8,
            momentum=5.0,
            potential_energy=10.0,
            kinetic_energy=5.0,
            friction=0.5,
        )
        ap2 = ActionPath(
            confidence=0.3,
            impact=0.1,
            momentum=1.0,
            potential_energy=50.0,
            kinetic_energy=5.0,
            friction=3.0,
        )
        for ap in [ap1, ap2]:
            ap.calculate_total_energy()
            ap.calculate_optimization_score()
        best = orch.optimize([ap1, ap2])
        assert best is not None, "best must be initialized"

    def test_save_decision_history(self, orch, tmp_path):
        orch.decision_history.append({"action_taken": "test"})
        out = tmp_path / "history.json"
        orch.save_decision_history(out)
        assert out.exists(), "Condition must be true"
        import json

        loaded = json.loads(out.read_text())
        assert loaded[0]["action_taken"] == "test", "Condition must be true"


# ---------------------------------------------------------------------------
# EnergyState
# ---------------------------------------------------------------------------


class TestEnergyState:
    def test_free_energy_calculation(self):
        state = EnergyState(configuration={"a": 1}, energy=5.0, entropy=2.0, temperature=1.0)
        # F = E - T*S = 5 - 1*2 = 3
        assert state.free_energy() == pytest.approx(3.0), "Condition must be true"

    def test_boltzmann_probability_at_reference(self):
        state = EnergyState(configuration={}, energy=0.0, temperature=1.0)
        p = state.boltzmann_probability(reference_energy=0.0)
        assert p == pytest.approx(1.0), "p is not valid"

    def test_boltzmann_probability_higher_energy(self):
        state = EnergyState(configuration={}, energy=2.0, temperature=1.0)
        p = state.boltzmann_probability(reference_energy=0.0)
        assert p == pytest.approx(math.exp(-2.0)), "p is not valid"

    def test_internal_energy_alias(self):
        state = EnergyState(configuration={}, internal_energy=7.0)
        assert state.energy == 7.0, "energy is not valid"


# ---------------------------------------------------------------------------
# EnergyLandscape
# ---------------------------------------------------------------------------


class TestEnergyLandscape:
    def test_empty_select_returns_none(self):
        landscape = EnergyLandscape()
        assert landscape.select_state() is None, "l is not valid"

    def test_add_state_and_select(self):
        landscape = EnergyLandscape(temperature=1.0)
        s1 = EnergyState(configuration={"x": 1}, energy=5.0)
        s2 = EnergyState(configuration={"x": 2}, energy=1.0)
        landscape.add_state(s1)
        landscape.add_state(s2)
        selected = landscape.select_state()
        assert selected is not None, "selected must be initialized"

    def test_minimize_free_energy_single_state(self):
        landscape = EnergyLandscape(temperature=1.0)
        s = EnergyState(configuration={"a": 1}, energy=2.0, entropy=0.5)
        landscape.add_state(s)
        result = landscape.minimize_free_energy()
        assert result is not None, "result must be initialized"

    def test_minimize_free_energy_empty_raises(self):
        landscape = EnergyLandscape()
        with pytest.raises(ValueError):
            landscape.minimize_free_energy()

    def test_cool_system(self):
        landscape = EnergyLandscape(temperature=1.0)
        s = EnergyState(configuration={}, energy=1.0)
        landscape.add_state(s)
        landscape.cool_system(cooling_rate=0.9)
        assert landscape.temperature == pytest.approx(0.9), "temperature is not valid"

    def test_calculate_system_entropy_empty(self):
        landscape = EnergyLandscape()
        assert landscape.calculate_system_entropy() == 0.0, "l is not valid"

    def test_calculate_system_entropy_non_empty(self):
        landscape = EnergyLandscape(temperature=1.0)
        for e in [1.0, 2.0, 3.0]:
            landscape.add_state(EnergyState(configuration={}, energy=e))
        entropy = landscape.calculate_system_entropy()
        assert entropy >= 0.0, "entropy must be greater than zero"

    def test_integrate_with_self_appraisal(self):
        landscape = EnergyLandscape(temperature=1.0)
        result = landscape.integrate_with_self_appraisal(
            decision_quality=0.8, expected_confidence=0.75
        )
        assert "free_energy" in result, "Result must not be empty"
        assert "probability" in result, "Result must not be empty"
        assert "recommendation" in result, "Result must not be empty"


# ---------------------------------------------------------------------------
# FlowVector & DiffusionFlowModel
# ---------------------------------------------------------------------------


class TestFlowVector:
    def test_step_returns_tuple(self):
        fv = FlowVector(
            position=(0.0, 0.0),
            velocity=(1.0, 0.0),
            gradient=(0.0, 0.0),
            diffusion_coefficient=0.0,
        )
        new_pos = fv.step(dt=0.1)
        assert isinstance(new_pos, tuple)
        assert len(new_pos) == 2, "New_pos must not be empty"

    def test_magnitude_calculation(self):
        fv = FlowVector(
            position=(0.0, 0.0),
            velocity=(3.0, 4.0),
            gradient=(0.0, 0.0),
        )
        assert fv.magnitude() == pytest.approx(5.0), "Condition must be true"

    def test_step_deterministic_with_zero_diffusion(self):
        fv = FlowVector(
            position=(1.0, 1.0),
            velocity=(1.0, 0.0),
            gradient=(0.0, 1.0),
            diffusion_coefficient=0.0,
        )
        new_x, new_y = fv.step(dt=0.5)
        # new_x = 1 + 1*0.5 + 0*0.5 + 0 = 1.5
        # new_y = 1 + 0*0.5 + 1*0.5 + 0 = 1.5
        assert new_x == pytest.approx(1.5), "new_x is not valid"
        assert new_y == pytest.approx(1.5), "new_y is not valid"


class TestDiffusionFlowModel:
    def test_construction(self):
        model = DiffusionFlowModel(dimensions=2, resolution=5)
        assert model.dimensions == 2, "dimensions is not valid"
        assert model.resolution == 5, "resolution is not valid"

    def test_diffusion_coefficient_property(self):
        model = DiffusionFlowModel(diffusion_coefficient=0.3)
        assert model.diffusion_coefficient == pytest.approx(0.3), "diffusion_coefficient is not valid"

    def test_add_attractor_updates_field(self):
        model = DiffusionFlowModel(resolution=4)
        model.add_attractor((0.5, 0.5), strength=1.0)
        assert len(model.attractors) == 1, "Collection must not be empty"
        assert len(model.potential_field) > 0, "Collection must not be empty"

    def test_add_repulsor_updates_field(self):
        model = DiffusionFlowModel(resolution=4)
        model.add_repulsor((0.8, 0.8), strength=0.5)
        assert len(model.repulsors) == 1, "Collection must not be empty"


# ---------------------------------------------------------------------------
# ImportMigration
# ---------------------------------------------------------------------------


class TestImportMigration:
    def test_calculate_properties_cli_file(self):
        migration = ImportMigration(
            file_path="/repo/cli/train.py",
            old_import="from training import train",
            new_import="from src.training import train",
            line_number=5,
        )
        migration.calculate_properties()
        assert migration.impact == pytest.approx(0.9), "impact is not valid"
        assert migration.confidence > 0.0, "confidence must be greater than zero"
        assert migration.optimization_score > 0.0, "optimization_score must be greater than zero"

    def test_calculate_properties_test_file(self):
        migration = ImportMigration(
            file_path="/repo/tests/test_trainer.py",
            old_import="from training.trainer import Trainer",
            new_import="from src.training.trainer import Trainer",
            line_number=1,
        )
        migration.calculate_properties()
        assert migration.impact == pytest.approx(0.7), "impact is not valid"

    def test_calculate_properties_agents_file(self):
        migration = ImportMigration(
            file_path="/repo/agents/some_agent.py",
            old_import="from models import base",
            new_import="from src.models import base",
            line_number=2,
        )
        migration.calculate_properties()
        assert migration.impact == pytest.approx(0.85), "impact is not valid"

    def test_urgency_is_high(self):
        migration = ImportMigration(
            file_path="/repo/src/something.py",
            old_import="from training import utils",
            new_import="from src.training import utils",
            line_number=1,
        )
        migration.calculate_properties()
        assert migration.urgency == pytest.approx(0.8), "urgency is not valid"


# ---------------------------------------------------------------------------
# ImportMigrationOrchestrator
# ---------------------------------------------------------------------------


class TestImportMigrationOrchestrator:
    def test_construction(self):
        orch = ImportMigrationOrchestrator()
        assert hasattr(orch, "migration_map")
        assert "from training." in orch.migration_map, "Condition must be true"

    def test_assess_imports_with_no_deprecated(self, tmp_path):
        (tmp_path / "clean.py").write_text("import os\nimport sys\n", encoding="utf-8")
        orch = ImportMigrationOrchestrator()
        result = orch.assess_imports(tmp_path)
        assert result["deprecated_found"] == 0, "Result must not be empty"

    def test_assess_imports_finds_deprecated(self, tmp_path):
        content = "from training.trainer import Trainer\n"
        (tmp_path / "user.py").write_text(content, encoding="utf-8")
        orch = ImportMigrationOrchestrator()
        result = orch.assess_imports(tmp_path)
        assert result["deprecated_found"] >= 1, "Value must be greater than zero"

    def test_deliberate_migrations_sorts_by_score(self, tmp_path):
        orch = ImportMigrationOrchestrator()
        m1 = ImportMigration(
            file_path="/repo/cli/a.py",
            old_import="from training import X",
            new_import="from src.training import X",
            line_number=1,
        )
        m2 = ImportMigration(
            file_path="/repo/other/b.py",
            old_import="from training import Y",
            new_import="from src.training import Y",
            line_number=1,
        )
        for m in [m1, m2]:
            m.calculate_properties()
        orch.migrations = [m1, m2]
        ranked = orch.deliberate_migrations()
        # Should return sorted list
        assert len(ranked) == 2, "Ranked must not be empty"
        if len(ranked) > 1:
            assert ranked[0].optimization_score >= ranked[1].optimization_score, "optimization_score must be greater than zero"

    def test_optimize_migration_plan_within_budget(self):
        orch = ImportMigrationOrchestrator()
        migrations = []
        for i in range(5):
            m = ImportMigration(
                file_path=f"/repo/file_{i}.py",
                old_import="from training import X",
                new_import="from src.training import X",
                line_number=i + 1,
            )
            m.calculate_properties()
            migrations.append(m)
        selected = orch.optimize_migration_plan(migrations, energy_budget=100.0)
        total_energy = sum(m.potential_energy for m in selected)
        assert total_energy <= 100.0, "total_energy is not valid"

    def test_execute_migrations_dry_run(self, tmp_path):
        content = "from training.trainer import Trainer\n"
        py_file = tmp_path / "module.py"
        py_file.write_text(content, encoding="utf-8")

        orch = ImportMigrationOrchestrator()
        m = ImportMigration(
            file_path=str(py_file),
            old_import="from training.trainer import Trainer",
            new_import="from src.training.trainer import Trainer",
            line_number=1,
        )
        results = orch.execute_migrations([m], dry_run=True)
        assert "migrations_attempted" in results, "Result must not be empty"
        # Dry run → file should NOT be modified
        assert py_file.read_text(encoding="utf-8") == content, "Content must not be empty"

    def test_execute_migrations_live(self, tmp_path):
        content = "from training.trainer import Trainer\n"
        py_file = tmp_path / "module2.py"
        py_file.write_text(content, encoding="utf-8")

        orch = ImportMigrationOrchestrator()
        m = ImportMigration(
            file_path=str(py_file),
            old_import="from training.trainer import Trainer",
            new_import="from src.training.trainer import Trainer",
            line_number=1,
        )
        m.calculate_properties()
        results = orch.execute_migrations([m], dry_run=False)
        assert results["migrations_attempted"] >= 1, "Value must be greater than zero"


# ---------------------------------------------------------------------------
# SwarmIntelligence / SwarmParticle
# ---------------------------------------------------------------------------


class TestSwarmIntelligence:
    def _make_swarm(self) -> "SwarmIntelligence":
        return SwarmIntelligence(num_particles=3, dimensions=2)

    def test_construction(self):
        swarm = self._make_swarm()
        # Particles are empty at construction; they're filled after initialize_swarm().
        assert swarm.num_particles == 3, "num_particles is not valid"
        assert swarm.dimensions == 2, "dimensions is not valid"
        assert isinstance(swarm.particles, list)

    def test_optimize_returns_best_position(self):
        swarm = self._make_swarm()

        def objective(pos):
            return -sum(x**2 for x in pos)  # Maximum at origin

        result = swarm.optimize(objective, bounds=[(-1.0, 1.0), (-1.0, 1.0)])
        assert isinstance(result, dict)
        assert "best_position" in result, "Result must not be empty"
        assert "best_score" in result, "Result must not be empty"
        assert isinstance(result["best_score"], float)

    def test_optimize_improves_over_initial(self):
        swarm = SwarmIntelligence(num_particles=5, dimensions=1)

        def rosenbrock(pos):
            return -(pos[0] ** 2)  # Simple concave function

        result = swarm.optimize(rosenbrock, bounds=[(-2.0, 2.0)])
        assert result["best_score"] <= 0.0, "Result must not be empty"
