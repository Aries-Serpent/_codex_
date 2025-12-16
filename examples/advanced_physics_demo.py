"""
Demonstration of Advanced Physics Paradigms for AI Orchestration.

This example showcases all emerging physics paradigms:
1. Chaos Theory - Adaptive exploration
2. Fractal Geometry - Multi-scale analysis
3. Fluid Dynamics - Workflow optimization
4. Electromagnetic Fields - Influence routing
5. Wave Propagation - Signal consensus
6. Relativistic Effects - Latency-aware scheduling

Run with: python examples/advanced_physics_demo.py
"""

import numpy as np


def demo_chaos_theory():
    """
    Demonstrate chaos theory for adaptive exploration.

    Use case: Generate diverse test parameters for code review.
    """
    print("\n" + "=" * 60)
    print("CHAOS THEORY: Adaptive Exploration")
    print("=" * 60)

    try:
        from agents.advanced_physics_calculators import ChaoticNeuralNetwork
    except ImportError:
        print("⚠ Chaos theory module not available. Install with: pip install numpy")
        return

    # Create chaotic neural network
    cnn = ChaoticNeuralNetwork(num_neurons=5, attractor_type="logistic")

    # Generate test parameters for code review
    # Parameters: [complexity, priority, risk]
    param_ranges = [
        (1.0, 10.0),  # Complexity (1-10)
        (0.0, 1.0),  # Priority (0-1)
        (0.0, 1.0),  # Risk (0-1)
    ]

    print("\nGenerating 10 chaotic test cases:")
    test_cases = cnn.generate_test_parameters(param_ranges, num_tests=10)

    for i, params in enumerate(test_cases[:10]):
        print(
            f"  Test {i+1}: complexity={params[0]:.2f}, "
            f"priority={params[1]:.2f}, risk={params[2]:.2f}"
        )

    # Calculate Lyapunov exponent (measure of chaos)
    lyapunov = cnn.neurons[0].lyapunov_exponent()
    print(f"\nLyapunov exponent: {lyapunov:.4f}")
    print(f"  → {'Chaotic' if lyapunov > 0 else 'Stable'} regime")

    # Inject chaos into a decision
    base_decision = 0.5
    perturbed = cnn.inject_chaos(base_decision, chaos_strength=0.2)
    print(f"\nChaos injection: {base_decision:.3f} → {perturbed:.3f}")
    print("  → Helps escape local optima in decision space")


def demo_fractal_geometry():
    """
    Demonstrate fractal analysis for code structure.

    Use case: Detect anomalous complexity in code trees.
    """
    print("\n" + "=" * 60)
    print("FRACTAL GEOMETRY: Multi-Scale Code Analysis")
    print("=" * 60)

    try:
        from agents.advanced_physics_calculators import FractalAnalyzer
    except ImportError:
        print("⚠ Fractal geometry module not available. Install with: pip install numpy")
        return

    # Create fractal analyzer
    analyzer = FractalAnalyzer()

    # Example code structure (nested dictionary)
    code_tree = {
        "api": {
            "routes": {
                "users": {"get": {}, "post": {}, "delete": {}},
                "auth": {"login": {}, "logout": {}},
            },
            "middleware": {"auth": {}, "logging": {}},
        },
        "models": {"user": {}, "session": {}},
    }

    print("\nAnalyzing code tree structure:")
    analysis = analyzer.analyze_code_tree(code_tree)

    print(f"  Depth: {analysis['depth']}")
    print(f"  Total nodes: {analysis['nodes']}")
    print(f"  Fractal dimension: {analysis['fractal_dimension']:.3f}")
    print(f"  Self-similarity: {analysis.get('self_similarity', 0):.3f}")

    # Demonstrate anomaly detection
    print("\nDetecting anomalous structures:")

    # Create normal and anomalous structures
    normal_structure = {
        "module": {
            "class1": {"method1": {}, "method2": {}},
            "class2": {"method3": {}, "method4": {}},
        }
    }

    deep_structure = {"a": {"b": {"c": {"d": {"e": {"f": {"g": {}}}}}}}}

    structures = [normal_structure, normal_structure, deep_structure, normal_structure]
    anomalies = analyzer.detect_anomalies(structures, threshold=1.5)

    print(f"  Found {len(anomalies)} anomalous structures")
    for anomaly in anomalies:
        print(
            f"    Structure {anomaly['index']}: dimension={anomaly['fractal_dimension']:.2f}, "
            f"z-score={anomaly['z_score']:.2f}"
        )


def demo_fluid_dynamics():
    """
    Demonstrate fluid dynamics for workflow optimization.

    Use case: Balance load across parallel execution channels.
    """
    print("\n" + "=" * 60)
    print("FLUID DYNAMICS: Workflow Flow Optimization")
    print("=" * 60)

    try:
        from agents.advanced_physics_calculators import FluidFlowScheduler
    except ImportError:
        print("⚠ Fluid dynamics module not available. Install with: pip install numpy")
        return

    # Create scheduler with multiple channels
    scheduler = FluidFlowScheduler(num_channels=5)

    print("\nSimulating task workflow as fluid flow:")

    # Inject tasks into channels (create imbalance)
    channels = list(scheduler.channels.keys())
    scheduler.inject_flow(channels[0], 80.0)  # Overloaded
    scheduler.inject_flow(channels[1], 30.0)
    scheduler.inject_flow(channels[2], 20.0)
    scheduler.inject_flow(channels[3], 40.0)
    scheduler.inject_flow(channels[4], 10.0)  # Underutilized

    print("\nInitial state:")
    for ch_id, channel in scheduler.channels.items():
        print(
            f"  {ch_id}: flow={channel.current_flow:.1f}, "
            f"pressure={channel.pressure:.2f}, "
            f"Re={channel.reynolds_number():.0f} "
            f"({'turbulent' if channel.is_turbulent() else 'laminar'})"
        )

    # Detect bottlenecks
    bottlenecks = scheduler.detect_bottlenecks(threshold=0.75)
    print(f"\nBottlenecks detected: {bottlenecks}")

    # Optimize flow distribution
    print("\nOptimizing flow distribution...")
    result = scheduler.optimize_flow(iterations=10)

    print(f"  Bottlenecks before: {result['initial']['bottlenecks']}")
    print(f"  Bottlenecks after: {result['final']['bottlenecks']}")
    print(
        f"  Pressure variance: {result['initial']['pressure_variance']:.3f} → "
        f"{result['final']['pressure_variance']:.3f}"
    )
    print(f"  Improvement: {result['improvement']['bottleneck_reduction']} bottlenecks removed")


def demo_electromagnetic_fields():
    """
    Demonstrate EM field routing for code review prioritization.

    Use case: Guide reviewer attention to code hotspots.
    """
    print("\n" + "=" * 60)
    print("ELECTROMAGNETIC FIELDS: Influence-Based Routing")
    print("=" * 60)

    try:
        from agents.advanced_physics_calculators import EMFieldRouter
    except ImportError:
        print("⚠ EM field module not available. Install with: pip install numpy")
        return

    # Create EM field router
    router = EMFieldRouter(grid_resolution=30)

    print("\nSetting up code hotspots as charges:")

    # Add hotspots (high-risk code areas)
    hotspots = [
        (np.array([0.3, 0.7]), 5.0, "Auth module"),
        (np.array([0.7, 0.3]), 3.0, "Payment API"),
        (np.array([0.5, 0.5]), 2.0, "Database layer"),
    ]

    for pos, charge, label in hotspots:
        router.add_charge(pos, charge)
        print(f"  {label}: position={pos}, charge={charge}")

    # Route a reviewer agent
    print("\nRouting reviewer from corner to hotspots:")
    start = np.array([0.1, 0.1])
    trajectory = router.route_agent(start, steps=40, step_size=0.02)

    print(f"  Start: {trajectory[0]}")
    print(f"  End: {trajectory[-1]}")
    print(f"  Steps taken: {len(trajectory)}")

    # Identify priority regions
    print("\nPriority regions for review:")
    regions = router.prioritize_regions(num_regions=3)

    for i, region in enumerate(regions):
        print(
            f"  Region {i+1}: position={region['position']}, " f"priority={region['priority']:.2f}"
        )


def demo_wave_propagation():
    """
    Demonstrate wave propagation for consensus building.

    Use case: Broadcast decisions through agent hierarchy.
    """
    print("\n" + "=" * 60)
    print("WAVE PROPAGATION: Signal Broadcasting")
    print("=" * 60)

    try:
        from agents.advanced_physics_calculators import WavePropagator
    except ImportError:
        print("⚠ Wave propagation module not available. Install with: pip install numpy")
        return

    # Create wave propagator
    wave = WavePropagator(grid_size=40, wave_speed=1.0, damping=0.05)

    print("\nSetting up signal sources:")

    # Add multiple signal sources (agents broadcasting decisions)
    sources = [
        {"position": (15, 15), "amplitude": 1.0, "frequency": 1.0, "phase": 0.0},
        {"position": (25, 25), "amplitude": 1.0, "frequency": 1.0, "phase": 0.0},
    ]

    for i, source in enumerate(sources):
        wave.add_source(**source)
        print(f"  Source {i+1}: position={source['position']}, " f"amplitude={source['amplitude']}")

    # Propagate signals
    print("\nPropagating signals through network...")
    history = wave.propagate(dt=0.1, steps=80)

    print(f"  Propagation steps: {len(history)}")

    # Measure interference
    midpoint = (20, 20)
    interference = wave.measure_interference(midpoint)

    print(f"\nInterference at midpoint {midpoint}:")
    print(f"  Constructive: {interference['constructive']:.3f}")
    print(f"  Destructive: {interference['destructive']:.3f}")
    print(f"  Net effect: {interference['net']:.3f}")

    if interference["constructive"] > 0:
        print("  → Signals reinforce (agreement)")
    elif interference["destructive"] > 0:
        print("  → Signals cancel (conflict)")


def demo_relativistic_effects():
    """
    Demonstrate relativistic scheduling for distributed systems.

    Use case: Synchronize clocks across microservices.
    """
    print("\n" + "=" * 60)
    print("RELATIVISTIC EFFECTS: Latency-Aware Scheduling")
    print("=" * 60)

    try:
        from agents.advanced_physics_calculators import RelativityScheduler
    except ImportError:
        print("⚠ Relativity module not available. Install with: pip install numpy")
        return

    # Create scheduler with communication speed limit
    scheduler = RelativityScheduler(speed_of_light=100.0)

    print("\nSetting up distributed agents:")

    # Add agents in different locations with different velocities
    agents = [
        {
            "agent_id": "service_a",
            "position": np.array([0.0, 0.0]),
            "velocity": np.array([10.0, 0.0]),  # Slow
        },
        {
            "agent_id": "service_b",
            "position": np.array([50.0, 0.0]),
            "velocity": np.array([50.0, 0.0]),  # Fast
        },
        {
            "agent_id": "service_c",
            "position": np.array([100.0, 0.0]),
            "velocity": np.array([20.0, 0.0]),  # Medium
        },
    ]

    for agent in agents:
        scheduler.add_agent(**agent)
        gamma = scheduler.lorentz_factor(agent["velocity"])
        print(
            f"  {agent['agent_id']}: position={agent['position']}, "
            f"velocity_mag={np.linalg.norm(agent['velocity']):.1f}, "
            f"γ={gamma:.3f}"
        )

    # Calculate communication delays
    print("\nCommunication delays:")
    delay_ab = scheduler.communication_delay("service_a", "service_b")
    delay_bc = scheduler.communication_delay("service_b", "service_c")
    delay_ac = scheduler.communication_delay("service_a", "service_c")

    print(f"  A ↔ B: {delay_ab:.3f} time units")
    print(f"  B ↔ C: {delay_bc:.3f} time units")
    print(f"  A ↔ C: {delay_ac:.3f} time units")

    # Synchronize clocks
    print("\nSynchronizing clocks (Einstein synchronization):")
    corrections = scheduler.synchronize_clocks()

    for agent_id, correction in corrections.items():
        print(f"  {agent_id}: correction={correction:.3f}")

    # Schedule tasks with relativistic corrections
    print("\nScheduling tasks with time dilation:")

    task_result = scheduler.schedule_task(
        task_id="critical_task",
        agent_id="service_b",  # Fast-moving service
        deadline=10.0,
        priority=1.0,
    )

    print(f"  Task: {task_result['task_id']}")
    print(f"  Coordinate deadline: {task_result['coordinate_deadline']:.2f}")
    print(f"  Proper deadline: {task_result['proper_deadline']:.2f}")
    print(f"  Time dilation factor (γ): {task_result['lorentz_factor']:.3f}")
    print("  → Fast-moving service experiences less proper time")


def demo_unified_orchestration():
    """
    Demonstrate unified orchestration using all paradigms.

    Use case: Comprehensive decision analysis for complex scenarios.
    """
    print("\n" + "=" * 60)
    print("UNIFIED ORCHESTRATION: All Paradigms Combined")
    print("=" * 60)

    try:
        from agents.advanced_physics_calculators import AdvancedPhysicsOrchestrator
    except ImportError:
        print("⚠ Advanced physics not available. Install with: pip install numpy")
        return

    # Create unified orchestrator
    orchestrator = AdvancedPhysicsOrchestrator()

    print("\nRunning multi-paradigm analysis:")

    # Define complex decision space
    decision_space = {
        "exploration": True,
        "param_ranges": [(0, 1), (0, 10), (-5, 5)],
        "structure": {
            "root": {"branch1": {"leaf1": {}, "leaf2": {}}, "branch2": {"leaf3": {}, "leaf4": {}}}
        },
        "workflow": True,
        "hotspots": [(np.array([0.3, 0.3]), 2.0), (np.array([0.7, 0.7]), 3.0)],
        "signals": [{"position": (20, 20), "amplitude": 1.0, "frequency": 1.0}],
        "agents": [
            {"agent_id": "a1", "position": np.array([0.0, 0.0])},
            {"agent_id": "a2", "position": np.array([50.0, 0.0])},
        ],
    }

    # Run comprehensive analysis
    results = orchestrator.full_analysis(decision_space)

    print("\nParadigms applied:")
    for paradigm in results.get("paradigms", {}).keys():
        print(f"  ✓ {paradigm}")

    # Get system status
    status = orchestrator.get_status()
    print("\nSystem status:")
    for component, state in status.items():
        print(f"  {component}: {state}")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 60)
    print("ADVANCED PHYSICS PARADIGMS FOR AI ORCHESTRATION")
    print("=" * 60)
    print("\nDemonstrating emerging physics principles:")
    print("  1. Chaos Theory")
    print("  2. Fractal Geometry")
    print("  3. Fluid Dynamics")
    print("  4. Electromagnetic Fields")
    print("  5. Wave Propagation")
    print("  6. Relativistic Effects")
    print("  7. Unified Orchestration")

    # Run individual demonstrations
    demo_chaos_theory()
    demo_fractal_geometry()
    demo_fluid_dynamics()
    demo_electromagnetic_fields()
    demo_wave_propagation()
    demo_relativistic_effects()
    demo_unified_orchestration()

    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\nAll paradigms are now integrated and ready for use.")
    print("See agents/advanced_physics_calculators.py for full API.")


if __name__ == "__main__":
    main()
