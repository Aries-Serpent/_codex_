"""Tests for thermodynamic orchestration system."""

from __future__ import annotations

import pytest

from quantum import (
    TaskPriority,
    ThermodynamicOrchestrator,
    ThermodynamicTask,
    calculate_thermodynamic_load_priority,
)


class TestThermodynamicTask:
    """Test ThermodynamicTask class."""

    def test_task_creation(self):
        """Test creating a thermodynamic task."""
        task = ThermodynamicTask(
            name="test_task", task_func=lambda: "result", energy=1.5, priority=TaskPriority.HIGH
        )
        assert task.name == "test_task", "name is not valid"
        assert task.energy == 1.5, "energy is not valid"
        assert task.priority == TaskPriority.HIGH, "priority is not valid"

    def test_calculate_free_energy(self):
        """Test Gibbs free energy calculation."""
        task = ThermodynamicTask(
            name="task", task_func=lambda: None, energy=5.0, temperature=2.0, entropy=1.0
        )
        # G = E - TS = 5.0 - 2.0 * 1.0 = 3.0
        assert task.calculate_free_energy() == pytest.approx(3.0), "Condition must be true"

    def test_task_comparison(self):
        """Test task comparison by free energy."""
        task1 = ThermodynamicTask(
            name="high_priority", task_func=lambda: None, energy=1.0, temperature=1.0, entropy=0.1
        )
        task2 = ThermodynamicTask(
            name="low_priority", task_func=lambda: None, energy=5.0, temperature=1.0, entropy=0.1
        )
        # Lower free energy = higher priority
        assert task1 < task2, "task1 is not valid"


class TestThermodynamicOrchestrator:
    """Test ThermodynamicOrchestrator class."""

    def test_orchestrator_creation(self):
        """Test creating an orchestrator."""
        orch = ThermodynamicOrchestrator(global_temperature=1.5, max_energy_per_cycle=10.0)
        assert orch.global_temperature == 1.5, "global_temperature is not valid"
        assert orch.max_energy_per_cycle == 10.0, "max_energy_per_cycle is not valid"
        assert orch.tasks == [], "tasks is not valid"

    def test_register_task(self):
        """Test registering a task."""
        orch = ThermodynamicOrchestrator()
        task = ThermodynamicTask(name="task1", task_func=lambda: None)
        orch.register_task(task)
        assert len(orch.tasks) == 1, "Collection must not be empty"
        assert orch.tasks[0] is task, "Condition must be true"

    def test_execute_thermodynamic_cycle_simple(self):
        """Test executing a simple task cycle."""
        orch = ThermodynamicOrchestrator(max_energy_per_cycle=10.0)

        executed = []

        def make_task_func(name):
            def func():
                executed.append(name)
                return f"result_{name}"

            return func

        task = ThermodynamicTask(name="task1", task_func=make_task_func("task1"), energy=2.0)
        orch.register_task(task)

        results = orch.execute_thermodynamic_cycle()

        assert len(results["executed"]) == 1, "Collection must not be empty"
        assert results["executed"][0]["name"] == "task1", "Result must not be empty"
        assert results["total_energy_used"] == 2.0, "Result must not be empty"
        assert "task1" in executed, "Condition must be true"

    def test_execute_multiple_tasks(self):
        """Test executing multiple tasks."""
        orch = ThermodynamicOrchestrator(max_energy_per_cycle=10.0)

        for i in range(3):
            task = ThermodynamicTask(name=f"task{i}", task_func=lambda: None, energy=2.0)
            orch.register_task(task)

        results = orch.execute_thermodynamic_cycle()

        assert len(results["executed"]) == 3, "Collection must not be empty"
        assert results["total_energy_used"] == 6.0, "Result must not be empty"

    def test_energy_budget_enforcement(self):
        """Test that energy budget is enforced."""
        orch = ThermodynamicOrchestrator(max_energy_per_cycle=5.0)

        # Register tasks totaling more than budget
        for i in range(3):
            task = ThermodynamicTask(name=f"task{i}", task_func=lambda: None, energy=3.0)
            orch.register_task(task)

        results = orch.execute_thermodynamic_cycle()

        # Should only execute tasks within budget
        assert results["total_energy_used"] <= 5.0, "Result must not be empty"
        assert len(results["skipped"]) > 0, "Collection must not be empty"

    def test_task_priority_ordering(self):
        """Test that tasks execute in priority order."""
        orch = ThermodynamicOrchestrator(max_energy_per_cycle=10.0)

        execution_order = []

        def make_func(name):
            def func():
                execution_order.append(name)

            return func

        # Add tasks with different priorities (lower free energy = higher priority)
        orch.register_task(
            ThermodynamicTask(
                name="low_priority",
                task_func=make_func("low"),
                energy=5.0,  # High energy
                temperature=1.0,
                entropy=0.0,
            )
        )
        orch.register_task(
            ThermodynamicTask(
                name="high_priority",
                task_func=make_func("high"),
                energy=0.5,  # Low energy
                temperature=1.0,
                entropy=0.0,
            )
        )
        orch.register_task(
            ThermodynamicTask(
                name="medium_priority",
                task_func=make_func("medium"),
                energy=2.0,
                temperature=1.0,
                entropy=0.0,
            )
        )

        orch.execute_thermodynamic_cycle()

        # Should execute in order: high, medium, low
        assert execution_order[0] == "high", "execution_ is not valid"

    def test_task_failure_handling(self):
        """Test handling of task failures."""
        orch = ThermodynamicOrchestrator()

        def failing_func():
            raise ValueError("Task failed")

        task = ThermodynamicTask(name="failing_task", task_func=failing_func, energy=1.0)
        orch.register_task(task)

        results = orch.execute_thermodynamic_cycle()

        assert len(results["failed"]) == 1, "Collection must not be empty"
        assert results["failed"][0]["name"] == "failing_task", "Result must not be empty"

    def test_optimize_task_order(self):
        """Test task order optimization using simulated annealing."""
        orch = ThermodynamicOrchestrator()

        # Add tasks with dependencies
        orch.register_task(
            ThermodynamicTask(
                name="task_a", task_func=lambda: None, energy=1.0, dependencies=["task_b"]
            )
        )
        orch.register_task(ThermodynamicTask(name="task_b", task_func=lambda: None, energy=1.0))

        optimal_order = orch.optimize_task_order()

        # task_b should come before task_a (dependency)
        assert optimal_order.index("task_b") < optimal_order.index("task_a"), "optimal_ is not valid"

    def test_temperature_cooling(self):
        """Test system temperature cooling after work."""
        orch = ThermodynamicOrchestrator(global_temperature=2.0, max_energy_per_cycle=10.0)

        task = ThermodynamicTask(name="task", task_func=lambda: None, energy=5.0)
        orch.register_task(task)

        results = orch.execute_thermodynamic_cycle()

        # Temperature should decrease after energy expenditure
        assert results["final_temperature"] < orch.global_temperature, "Result must not be empty"


class TestThermodynamicLoadPriority:
    """Test thermodynamic load priority calculation."""

    def test_calculate_priority(self):
        """Test priority calculation."""
        tasks = [
            ThermodynamicTask(name="high", task_func=lambda: None, energy=0.5),
            ThermodynamicTask(name="low", task_func=lambda: None, energy=5.0),
            ThermodynamicTask(name="medium", task_func=lambda: None, energy=2.0),
        ]

        priorities = calculate_thermodynamic_load_priority(tasks, 1.0)

        # Should be sorted by priority
        names = [name for name, _ in priorities]
        assert names[0] == "high", "Condition must be true"
        assert names[-1] == "low", "Condition must be true"

    def test_temperature_effect(self):
        """Test temperature effect on priorities."""
        task = ThermodynamicTask(name="task", task_func=lambda: None, energy=2.0)

        # Higher temperature = more uniform priorities
        priorities_hot = calculate_thermodynamic_load_priority([task], 10.0)
        priorities_cold = calculate_thermodynamic_load_priority([task], 0.1)

        # Cold system has more extreme priorities
        assert priorities_cold[0][1] < priorities_hot[0][1], "pri is not valid"


@pytest.mark.integration
class TestOrchestrationIntegration:
    """Integration tests for orchestration system."""

    def test_real_world_task_execution(self):
        """Test executing real-world tasks."""
        orch = ThermodynamicOrchestrator(max_energy_per_cycle=20.0)

        results_store = {}

        # Simulate plugin loading
        def load_plugin():
            results_store["plugin_loaded"] = True
            return "plugin_module"

        # Simulate data processing
        def process_data():
            results_store["data_processed"] = True
            return "processed_data"

        # Simulate cleanup
        def cleanup():
            results_store["cleanup_done"] = True

        orch.register_task(
            ThermodynamicTask(
                name="load_plugin",
                task_func=load_plugin,
                energy=2.0,
                priority=TaskPriority.CRITICAL,
            )
        )
        orch.register_task(
            ThermodynamicTask(
                name="process_data",
                task_func=process_data,
                energy=5.0,
                priority=TaskPriority.HIGH,
                dependencies=["load_plugin"],
            )
        )
        orch.register_task(
            ThermodynamicTask(
                name="cleanup", task_func=cleanup, energy=1.0, priority=TaskPriority.LOW
            )
        )

        results = orch.execute_thermodynamic_cycle()

        assert results_store["plugin_loaded"], "Result must not be empty"
        assert results_store["data_processed"], "Result must not be empty"
        assert results_store["cleanup_done"], "Result must not be empty"
        assert len(results["executed"]) == 3, "Collection must not be empty"

    def test_complex_dependency_management(self):
        """Test managing complex task dependencies."""
        orch = ThermodynamicOrchestrator(max_energy_per_cycle=50.0)

        execution_log = []

        def make_func(name):
            def func():
                execution_log.append(name)

            return func

        # Create complex dependency graph
        orch.register_task(ThermodynamicTask(name="init", task_func=make_func("init"), energy=1.0))
        orch.register_task(
            ThermodynamicTask(
                name="load_config",
                task_func=make_func("load_config"),
                energy=2.0,
                dependencies=["init"],
            )
        )
        orch.register_task(
            ThermodynamicTask(
                name="load_plugins",
                task_func=make_func("load_plugins"),
                energy=3.0,
                dependencies=["load_config"],
            )
        )
        orch.register_task(
            ThermodynamicTask(
                name="start_service",
                task_func=make_func("start_service"),
                energy=2.0,
                dependencies=["load_plugins"],
            )
        )

        # Optimize and execute
        orch.optimize_task_order()
        orch.execute_thermodynamic_cycle()

        # Verify dependency order
        assert execution_log.index("init") < execution_log.index("load_config"), "Condition must be true"
        assert execution_log.index("load_config") < execution_log.index("load_plugins"), "Condition must be true"
        assert execution_log.index("load_plugins") < execution_log.index("start_service"), "Condition must be true"
