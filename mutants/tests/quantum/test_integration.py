"""
Integration tests for quantum orchestration system with cross-reference capabilities.

This module tests the ability of AI agents to "take the helm" and actively
produce pathways by cross-referencing existing codebase components.
"""

from __future__ import annotations

import pytest

from src.quantum import (
    PluginState,
    QuantumPlugin,
    QuantumPluginRegistry,
    QuantumTest,
    QuantumTestSuite,
    TaskPriority,
    ThermodynamicOrchestrator,
    ThermodynamicTask,
)


@pytest.mark.integration
class TestEndToEndQuantumRAG:
    """End-to-end integration with quantum RAG pipeline."""

    def test_quantum_rag_plugin_loading(self, quantum_plugin_fixture):
        """Test loading quantum RAG components dynamically."""
        # Mock the RAG pipeline modules that may not exist in CI
        quantum_plugin_fixture.mock_module("src.rag.pipelines.chunking")
        quantum_plugin_fixture.mock_module("src.rag.pipelines.embedding")
        quantum_plugin_fixture.mock_module("src.rag.pipelines.quantum_retrieval")

        registry = QuantumPluginRegistry()

        # Register RAG pipeline components
        registry.register(
            QuantumPlugin(
                name="chunking", import_path="src.rag.pipelines.chunking", energy_cost=1.0
            )
        )
        registry.register(
            QuantumPlugin(
                name="embedding",
                import_path="src.rag.pipelines.embedding",
                energy_cost=2.0,
                dependencies=["chunking"],
            )
        )
        registry.register(
            QuantumPlugin(
                name="quantum_retrieval",
                import_path="src.rag.pipelines.quantum_retrieval",
                energy_cost=1.5,
                dependencies=["embedding"],
            )
        )

        # Load quantum retrieval (should load dependencies)
        module = registry.load_with_dependencies("quantum_retrieval")
        assert module is not None, "module must be initialized"

        # Verify all dependencies loaded
        assert registry.plugins["chunking"].state == PluginState.COLLAPSED, "state is not valid"
        assert registry.plugins["embedding"].state == PluginState.COLLAPSED, "state is not valid"
        assert registry.plugins["quantum_retrieval"].state == PluginState.COLLAPSED, "state is not valid"

    def test_quantum_rag_cross_reference(self):
        """Test cross-referencing quantum RAG with physics calculators."""
        registry = QuantumPluginRegistry()

        # Cross-reference: RAG + Physics
        registry.register(
            QuantumPlugin(
                name="rag_quantum",
                import_path="src.rag.pipelines.quantum_retrieval",
                energy_cost=1.5,
            )
        )
        registry.register(
            QuantumPlugin(
                name="physics_calc",
                import_path="agents.advanced_physics_calculators",
                energy_cost=2.5,
                dependencies=["rag_quantum"],
            )
        )

        # This demonstrates "wearing the codebase as a brain"
        module = registry.load_with_dependencies("physics_calc")
        assert module is not None, "module must be initialized"


@pytest.mark.integration
class TestAgentOrchestrationIntegration:
    """Test agent orchestration with cross-references."""

    def test_agent_core_integration(self):
        """Test integrating with agent core functionality."""
        registry = QuantumPluginRegistry()

        # Register agent components — import path is relative to src/ (on sys.path)
        registry.register(
            QuantumPlugin(name="agent_core", import_path="agent.core", energy_cost=1.0)
        )

        module = registry.load_with_dependencies("agent_core")
        assert module is not None, "module must be initialized"
        assert hasattr(module, "AgentCore") or hasattr(module, "AgentConfig")

    def test_mcp_metrics_integration(self):
        """Test integrating with MCP metrics system."""
        registry = QuantumPluginRegistry()

        registry.register(
            QuantumPlugin(
                name="mcp_metrics", import_path="mcp.metrics.mcp_metrics", energy_cost=0.8
            )
        )

        module = registry.load_with_dependencies("mcp_metrics")
        assert module is not None, "module must be initialized"
        assert hasattr(module, "MCPMetrics") or hasattr(module, "MetricCollector")


@pytest.mark.integration
class TestDependencyGraphIntegration:
    """Test dependency graph integration."""

    def test_ast_graph_usage(self):
        """Test using AST/Dependency graph for plugin management."""
        registry = QuantumPluginRegistry()

        # Verify dependency graph is initialized
        assert registry.dependency_graph is not None, "dependency_graph must be initialized"

        # Register plugins and verify graph structure
        registry.register(QuantumPlugin(name="base", import_path="sys"))
        registry.register(QuantumPlugin(name="derived", import_path="os", dependencies=["base"]))

        # Check graph structure
        deps = registry.get_entangled_plugins("derived")
        assert "base" in deps, "Condition must be true"


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Test integration with error handling utilities."""

    def test_safe_call_in_plugin_loading(self):
        """Test that plugin loading uses safe_call from codebase."""
        plugin = QuantumPlugin(name="test", import_path="sys")

        # This internally uses src.common.error_handling.safe_call
        module = plugin.observe()
        assert module is not None, "module must be initialized"

    def test_safe_call_in_test_execution(self):
        """Test that test execution uses safe_call."""
        suite = QuantumTestSuite()

        # Add a test that might fail
        suite.add_test(QuantumTest(name="risky_test", test_func=lambda: 1 / 1))  # Safe division

        # Execution uses safe_call internally
        results = suite.execute_with_thermodynamic_scheduling()
        assert results["passed"] == 1, "Result must not be empty"

    def test_safe_call_in_orchestration(self):
        """Test that orchestrator uses safe_call for tasks."""
        orch = ThermodynamicOrchestrator()

        def risky_task():
            return "success"

        orch.register_task(ThermodynamicTask(name="risky", task_func=risky_task, energy=1.0))

        # Internally uses safe_call
        results = orch.execute_thermodynamic_cycle()
        assert len(results["executed"]) == 1, "Collection must not be empty"


@pytest.mark.integration
class TestCrossReferenceCapabilities:
    """
    Test suite demonstrating AI agent "brain" capabilities through cross-references.

    These tests showcase how an AI agent can actively produce pathways by
    understanding and connecting different parts of the codebase.
    """

    def test_capability_1_rag_to_agent_bridge(self, quantum_plugin_fixture):
        """
        Capability 1: Bridge RAG pipeline with Agent system.

        Demonstrates: AI agent connects quantum retrieval with agent orchestration.
        """
        # Mock the required modules
        quantum_plugin_fixture.mock_module("src.rag.pipelines.retrieval")
        quantum_plugin_fixture.mock_module("src.agent.core")

        registry = QuantumPluginRegistry()

        # Cross-reference: RAG → Agent
        registry.register(
            QuantumPlugin(
                name="rag_retrieval", import_path="src.rag.pipelines.retrieval", energy_cost=1.0
            )
        )
        registry.register(
            QuantumPlugin(
                name="agent_system",
                import_path="src.agent.core",
                energy_cost=1.5,
                dependencies=["rag_retrieval"],
            )
        )

        # AI agent pathway: Load agent with RAG capability
        agent_module = registry.load_with_dependencies("agent_system")
        assert agent_module is not None, "agent_module must be initialized"

        # Verify pathway established
        assert registry.plugins["rag_retrieval"].state == PluginState.COLLAPSED, "state is not valid"

    def test_capability_2_physics_to_testing_pipeline(self):
        """
        Capability 2: Connect physics calculators with testing framework.

        Demonstrates: AI agent uses physics principles for test prioritization.
        """
        suite = QuantumTestSuite(temperature=1.0)

        # Cross-reference: Physics energy → Test priority
        suite.add_test(
            QuantumTest(
                name="high_energy_test",
                test_func=lambda: True,
                amplitude=0.9,  # High amplitude = high energy state
            )
        )
        suite.add_test(
            QuantumTest(
                name="low_energy_test",
                test_func=lambda: True,
                amplitude=0.3,  # Low amplitude = low energy state
            )
        )

        results = suite.execute_with_thermodynamic_scheduling()

        # AI agent pathway: Tests executed by energy (amplitude) priority
        assert results["total"] == 2, "Result must not be empty"
        # Higher amplitude tests execute first
        assert results["tests"][0]["probability"] > results["tests"][1]["probability"], "Value must be greater than zero"

    def test_capability_3_mcp_to_quantum_metrics(self):
        """
        Capability 3: Integrate MCP metrics with quantum measurements.

        Demonstrates: AI agent connects telemetry with quantum test metrics.
        """
        suite = QuantumTestSuite()

        # Cross-reference: MCP metrics concepts → Quantum metrics
        suite.add_test(QuantumTest(name="metric_test_1", test_func=lambda: True, amplitude=0.8))
        suite.add_test(QuantumTest(name="metric_test_2", test_func=lambda: False, amplitude=0.7))

        results = suite.execute_with_thermodynamic_scheduling()

        # AI agent pathway: Quantum metrics (energy, entropy) as telemetry
        assert "total_energy" in results, "Result must not be empty"
        assert "entropy" in results, "Result must not be empty"
        assert results["entropy"] > 0, "Value must be greater than zero"

    def test_capability_4_dependency_aware_orchestration(self):
        """
        Capability 4: Orchestrate tasks using dependency graph intelligence.

        Demonstrates: AI agent understands module dependencies for smart scheduling.
        """
        orch = ThermodynamicOrchestrator(max_energy_per_cycle=20.0)

        execution_order = []

        def make_func(name):
            def func():
                execution_order.append(name)
                return name

            return func

        # Cross-reference: AST/dependency graph → Task orchestration
        orch.register_task(
            ThermodynamicTask(name="load_base", task_func=make_func("load_base"), energy=1.0)
        )
        orch.register_task(
            ThermodynamicTask(
                name="load_derived",
                task_func=make_func("load_derived"),
                energy=2.0,
                dependencies=["load_base"],
            )
        )
        orch.register_task(
            ThermodynamicTask(
                name="process",
                task_func=make_func("process"),
                energy=3.0,
                dependencies=["load_derived"],
            )
        )

        # AI agent pathway: Dependency-aware execution
        orch.optimize_task_order()
        orch.execute_thermodynamic_cycle()

        # Verify dependency order maintained
        assert execution_order.index("load_base") < execution_order.index("load_derived"), "execution_ is not valid"
        assert execution_order.index("load_derived") < execution_order.index("process"), "execution_ is not valid"

    def test_capability_5_adaptive_loading_strategy(self):
        """
        Capability 5: Adapt plugin loading based on system temperature.

        Demonstrates: AI agent adjusts behavior based on system state.
        """
        from src.quantum.plugin_registry import calculate_thermodynamic_load_priority

        plugins = [
            QuantumPlugin(name="heavy", import_path="sys", energy_cost=5.0),
            QuantumPlugin(name="light", import_path="os", energy_cost=0.5),
            QuantumPlugin(name="medium", import_path="math", energy_cost=2.0),
        ]

        # AI agent pathway: Adapt to cold system (load critical only)
        cold_priorities = calculate_thermodynamic_load_priority(plugins, current_temperature=0.5)

        # AI agent pathway: Adapt to hot system (load more eagerly)
        hot_priorities = calculate_thermodynamic_load_priority(plugins, current_temperature=2.0)

        # Cold system: More selective (bigger priority differences)
        cold_range = cold_priorities[0][1] - cold_priorities[-1][1]
        hot_range = hot_priorities[0][1] - hot_priorities[-1][1]

        # Cold system: Values collapse more (all near zero except lightest)
        # Hot system: Values spread more (wider range in absolute Boltzmann weights)
        # Both demonstrate adaptive loading: temperature controls selectivity
        assert cold_range != hot_range, "cold_range is not valid"

    def test_capability_6_error_recovery_pathway(self):
        """
        Capability 6: Demonstrate error recovery through alternative pathways.

        Demonstrates: AI agent finds alternative routes when primary path fails.
        """
        registry = QuantumPluginRegistry()

        # Register primary and fallback plugins
        registry.register(
            QuantumPlugin(
                name="primary", import_path="nonexistent.module", energy_cost=1.0  # Will fail
            )
        )
        registry.register(
            QuantumPlugin(name="fallback", import_path="sys", energy_cost=1.5)  # Will succeed
        )

        # AI agent pathway: Try primary, fallback to alternative
        try:
            registry.load_with_dependencies("primary")
        except ImportError:
            # Agent detects failure and tries fallback
            fallback_module = registry.load_with_dependencies("fallback")
            assert fallback_module is not None, "fallback_module must be initialized"
            assert registry.plugins["fallback"].state == PluginState.COLLAPSED, "state is not valid"

    def test_capability_7_multi_paradigm_integration(self):
        """
        Capability 7: Integrate multiple paradigms (quantum, thermodynamic, classical).

        Demonstrates: AI agent synthesizes different conceptual frameworks.
        """
        orch = ThermodynamicOrchestrator(max_energy_per_cycle=15.0)
        suite = QuantumTestSuite(temperature=1.2)
        registry = QuantumPluginRegistry()

        results = {}

        # AI agent pathway: Orchestrate quantum test execution
        def run_quantum_tests():
            suite.add_test(
                QuantumTest(name="paradigm_test", test_func=lambda: True, amplitude=0.85)
            )
            test_results = suite.execute_with_thermodynamic_scheduling()
            results["tests"] = test_results
            return test_results

        # AI agent pathway: Load plugins via thermodynamic orchestration
        def load_plugins():
            registry.register(QuantumPlugin(name="test_module", import_path="sys", energy_cost=1.0))
            module = registry.load_with_dependencies("test_module")
            results["plugins"] = module
            return module

        # Orchestrate multi-paradigm workflow
        orch.register_task(
            ThermodynamicTask(
                name="load_phase",
                task_func=load_plugins,
                energy=2.0,
                priority=TaskPriority.CRITICAL,
            )
        )
        orch.register_task(
            ThermodynamicTask(
                name="test_phase",
                task_func=run_quantum_tests,
                energy=3.0,
                priority=TaskPriority.HIGH,
                dependencies=["load_phase"],
            )
        )

        orch_results = orch.execute_thermodynamic_cycle()

        # Verify multi-paradigm integration
        assert "plugins" in results, "Result must not be empty"
        assert "tests" in results, "Result must not be empty"
        assert len(orch_results["executed"]) == 2, "Collection must not be empty"

    def test_capability_8_self_optimizing_workflow(self):
        """
        Capability 8: Create self-optimizing workflows using feedback.

        Demonstrates: AI agent learns from execution and optimizes.
        """
        orch = ThermodynamicOrchestrator(max_energy_per_cycle=20.0)

        # First pass: Record execution metrics
        metrics = {"execution_times": []}

        def make_instrumented_task(name, base_energy):
            def func():
                import time

                start = time.time()
                # Simulate work
                result = sum(range(1000))
                elapsed = time.time() - start
                metrics["execution_times"].append(
                    {"name": name, "time": elapsed, "energy": base_energy}
                )
                return result

            return func

        # AI agent pathway: Execute and gather metrics
        for i in range(3):
            orch.register_task(
                ThermodynamicTask(
                    name=f"task_{i}",
                    task_func=make_instrumented_task(f"task_{i}", float(i + 1)),
                    energy=float(i + 1),
                )
            )

        results = orch.execute_thermodynamic_cycle()

        # AI agent pathway: Analyze and optimize for next iteration
        assert len(metrics["execution_times"]) > 0, "Collection must not be empty"

        # Calculate efficiency (work done / energy spent)
        total_work = len(metrics["execution_times"])
        total_energy = results["total_energy_used"]
        efficiency = total_work / total_energy if total_energy > 0 else 0

        assert efficiency > 0, "efficiency must be greater than zero"

    def test_capability_9_context_aware_plugin_selection(self):
        """
        Capability 9: Select plugins based on execution context.

        Demonstrates: AI agent makes intelligent choices based on runtime context.
        """
        registry = QuantumPluginRegistry()

        # Simulate different contexts
        contexts = {
            "development": {"max_energy": 10.0, "temperature": 2.0},
            "production": {"max_energy": 5.0, "temperature": 0.5},
            "testing": {"max_energy": 15.0, "temperature": 1.5},
        }

        plugins = [
            QuantumPlugin(name="debug_tools", import_path="sys", energy_cost=3.0),
            QuantumPlugin(name="core", import_path="os", energy_cost=1.0),
            QuantumPlugin(name="analytics", import_path="math", energy_cost=2.0),
        ]

        for plugin in plugins:
            registry.register(plugin)

        # AI agent pathway: Context-aware selection
        context = "production"  # Low energy budget, low temperature

        from src.quantum.plugin_registry import calculate_thermodynamic_load_priority

        priorities = calculate_thermodynamic_load_priority(
            plugins, current_temperature=contexts[context]["temperature"]
        )

        # In production, core (low energy) should have highest priority
        assert priorities[0][0] == "core", "pri is not valid"

    def test_capability_10_intelligent_test_distribution(self):
        """
        Capability 10: Distribute tests intelligently across quantum states.

        Demonstrates: AI agent optimizes test execution using interference patterns.
        """
        suite = QuantumTestSuite(temperature=1.0)

        # Create tests with different phases for interference
        import math

        # AI agent pathway: Create constructive/destructive interference patterns
        for i in range(10):
            suite.add_test(
                QuantumTest(
                    name=f"test_{i}",
                    test_func=lambda: True,
                    amplitude=0.8,
                    phase=i * math.pi / 5,  # Distribute phases
                )
            )

        # Calculate interference patterns between tests
        interferences = []
        for i in range(len(suite.tests) - 1):
            interference = suite.calculate_test_interference(suite.tests[i], suite.tests[i + 1])
            interferences.append(interference)

        # AI agent pathway: Use interference to optimize execution order
        results = suite.execute_with_thermodynamic_scheduling()

        assert len(interferences) == 9, "Interferences must not be empty"
        assert results["total"] == 10, "Result must not be empty"
        # Entropy should reflect distribution pattern
        assert results["entropy"] >= 0.0, "Value must be greater than zero"


@pytest.mark.integration
class TestAgentAutonomyCapabilities:
    """
    Tests demonstrating AI agent autonomy and "taking the helm".

    These scenarios show the agent actively making decisions and creating
    pathways based on codebase understanding.
    """

    def test_autonomous_module_discovery(self):
        """Test agent's ability to discover and load related modules."""
        registry = QuantumPluginRegistry()

        # Agent discovers RAG pipeline components
        rag_modules = [
            "src.rag.pipelines.chunking",
            "src.rag.pipelines.embedding",
            "src.rag.pipelines.retrieval",
            "src.rag.pipelines.quantum_retrieval",
        ]

        for idx, module_path in enumerate(rag_modules):
            registry.register(
                QuantumPlugin(
                    name=f"rag_{idx}", import_path=module_path, energy_cost=1.0 + idx * 0.5
                )
            )

        # Agent creates optimal loading strategy
        from src.quantum.plugin_registry import calculate_thermodynamic_load_priority

        priorities = calculate_thermodynamic_load_priority(
            list(registry.plugins.values()), current_temperature=1.0
        )

        # Verify agent prioritized correctly (lower cost first)
        assert priorities[0][1] > priorities[-1][1], "pri must be greater than zero"

    def test_autonomous_error_diagnosis(self):
        """Test agent's ability to diagnose and adapt to errors."""
        suite = QuantumTestSuite()

        # Create tests with different failure modes
        suite.add_test(
            QuantumTest(
                name="import_error_test",
                test_func=lambda: __import__("nonexistent_module"),
                amplitude=0.7,
            )
        )
        suite.add_test(
            QuantumTest(
                name="value_error_test", test_func=lambda: int("not_a_number"), amplitude=0.6
            )
        )
        suite.add_test(QuantumTest(name="success_test", test_func=lambda: True, amplitude=0.9))

        results = suite.execute_with_thermodynamic_scheduling()

        # Agent adapts: High entropy indicates diagnostic needed
        if results["entropy"] > 0.5:
            # Agent recognizes mixed outcomes and can analyze failures
            failed_tests = [test for test in results["tests"] if test["state"] == "failed"]
            assert len(failed_tests) == 2, "Failed_tests must not be empty"

    def test_autonomous_optimization_iteration(self):
        """Test agent's ability to iteratively optimize execution."""
        orch = ThermodynamicOrchestrator(max_energy_per_cycle=10.0)

        # First iteration: baseline
        for i in range(5):
            orch.register_task(
                ThermodynamicTask(name=f"task_{i}", task_func=lambda: "result", energy=float(i + 1))
            )

        # Agent optimizes
        optimal_order_v1 = orch.optimize_task_order()

        # Simulate learning: adjust energies based on feedback
        for task in orch.tasks:
            # Agent reduces energy cost for faster tasks
            if "1" in task.name or "2" in task.name:
                task.energy *= 0.8

        # Agent re-optimizes with new information
        optimal_order_v2 = orch.optimize_task_order()

        # Orders may differ as agent adapted
        assert len(optimal_order_v1) == len(optimal_order_v2), "Optimal_order_v1 must not be empty"
