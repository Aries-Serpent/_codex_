"""
Example usage of the Quantum-Relativistic-Dirac Orchestrator.

Demonstrates:
1. Creating an orchestrator
2. Adding tasks with dependencies
3. Running the orchestration loop
4. Monitoring task status
5. Self-healing behavior
"""

from codex.quantum_orchestrator.orchestrator import create_orchestrator
import numpy as np


def example_basic_orchestration():
    """Basic orchestration example with 5 tasks."""
    print("=" * 70)
    print("EXAMPLE 1: Basic Quantum Orchestration")
    print("=" * 70)

    # Create orchestrator
    orchestrator = create_orchestrator(
        max_throughput=100.0,  # c = 100 tasks/sec max
        work_granularity=1.0,  # ℏ = 1.0
        time_step=0.1,  # dt = 0.1 sec
    )

    # Add tasks
    orchestrator.add_task(
        task_id="task_1", name="Initialize System", priority=0.9, complexity=2.0, rest_mass=2.0
    )

    orchestrator.add_task(
        task_id="task_2",
        name="Load Data",
        priority=0.7,
        complexity=3.0,
        rest_mass=3.0,
        dependencies=["task_1"],
    )

    orchestrator.add_task(
        task_id="task_3",
        name="Process Data",
        priority=0.8,
        complexity=5.0,
        rest_mass=5.0,
        dependencies=["task_2"],
    )

    orchestrator.add_task(
        task_id="task_4",
        name="Generate Report",
        priority=0.6,
        complexity=2.0,
        rest_mass=2.0,
        dependencies=["task_3"],
    )

    orchestrator.add_task(
        task_id="task_5",
        name="Send Notification",
        priority=0.5,
        complexity=1.0,
        rest_mass=1.0,
        dependencies=["task_4"],
    )

    print(f"\nInitial state: {len(orchestrator.state.tasks)} tasks added")
    print(f"Total probability: {orchestrator.state.total_probability():.3f}")

    # Run orchestration
    print("\nRunning orchestration...")
    results = orchestrator.run(max_iterations=100)

    print(f"\nResults:")
    print(f"  Iterations: {results['iterations']}")
    print(f"  Completed tasks: {len(results['completed_tasks'])}/{results['total_tasks']}")
    print(f"  Completion rate: {results['completion_rate']:.1%}")
    print(f"  Final timestamp: {results['final_timestamp']:.2f}")

    # Show final status
    print("\nFinal task status:")
    status = orchestrator.get_task_status()
    for task_id, info in status.items():
        print(f"  {task_id}:")
        print(f"    Probability: {info['probability']:.3f}")
        print(f"    Energy: {info['energy']:.2f}")
        print(f"    Stable: {info['stable']}")
        print(f"    Zitterbewegung: {info['zitterbewegung']:.3f}")


def example_with_deadlines():
    """Example with SLA deadlines."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Orchestration with SLA Deadlines")
    print("=" * 70)

    orchestrator = create_orchestrator()

    # Add tasks with deadlines
    orchestrator.add_task(
        task_id="urgent_task",
        name="Urgent Processing",
        priority=0.9,
        complexity=3.0,
        rest_mass=3.0,
        deadline=5.0,  # Must complete by t=5.0
    )

    orchestrator.add_task(
        task_id="normal_task",
        name="Normal Processing",
        priority=0.5,
        complexity=2.0,
        rest_mass=2.0,
        deadline=20.0,  # Must complete by t=20.0
    )

    orchestrator.add_task(
        task_id="flexible_task",
        name="Flexible Processing",
        priority=0.3,
        complexity=1.0,
        rest_mass=1.0,
        deadline=50.0,  # Flexible deadline
    )

    print(f"\nTasks with deadlines:")
    for task_id, task in orchestrator.state.tasks.items():
        print(f"  {task.name}: deadline at t={task.deadline}")

    # Run and monitor
    results = orchestrator.run(max_iterations=200)

    print(f"\nResults:")
    print(f"  Completed: {len(results['completed_tasks'])}/{results['total_tasks']}")
    print(f"  Final time: {results['final_timestamp']:.2f}")

    # Check SLA compliance
    print(f"\nSLA Compliance:")
    for task_id, task in orchestrator.state.tasks.items():
        completed = task_id in results["completed_tasks"]
        on_time = completed and results["final_timestamp"] <= task.deadline
        print(
            f"  {task.name}: {'✓ On-time' if on_time else '✗ Missed' if not completed else '✗ Late'}"
        )


def example_resource_constraints():
    """Example with resource constraints."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Resource-Constrained Orchestration")
    print("=" * 70)

    orchestrator = create_orchestrator()

    # Set available resources
    orchestrator.state.resources = {"cpu": 10.0, "memory": 16.0, "gpu": 2.0}

    # Add resource-intensive tasks
    orchestrator.add_task(
        task_id="ml_training",
        name="ML Model Training",
        priority=0.9,
        complexity=10.0,
        rest_mass=10.0,
        required_resources={"cpu": 8.0, "memory": 12.0, "gpu": 1.0},
    )

    orchestrator.add_task(
        task_id="data_processing",
        name="Data Processing",
        priority=0.7,
        complexity=5.0,
        rest_mass=5.0,
        required_resources={"cpu": 4.0, "memory": 8.0},
    )

    orchestrator.add_task(
        task_id="inference",
        name="Model Inference",
        priority=0.6,
        complexity=3.0,
        rest_mass=3.0,
        required_resources={"gpu": 1.0, "memory": 4.0},
        dependencies=["ml_training"],
    )

    print(f"\nAvailable resources:")
    for resource, amount in orchestrator.state.resources.items():
        print(f"  {resource}: {amount}")

    print(f"\nTask resource requirements:")
    for task_id, task in orchestrator.state.tasks.items():
        if task.required_resources:
            print(f"  {task.name}: {task.required_resources}")

    # Run
    results = orchestrator.run(max_iterations=150)

    print(f"\nResults:")
    print(f"  Completed: {len(results['completed_tasks'])}/{results['total_tasks']}")

    # Show bottlenecks if any
    if len(orchestrator.history) > 0:
        bottlenecks = orchestrator.flow_analyzer.identify_bottlenecks(
            orchestrator.state, orchestrator.history[-1], orchestrator.dt
        )
        if bottlenecks:
            print(f"\nIdentified bottlenecks:")
            for bn in bottlenecks:
                print(f"  {bn['task_id']}: severity={bn['severity']:.2f}")


def example_spinor_analysis():
    """Example analyzing spinor states and physics properties."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Spinor State Analysis")
    print("=" * 70)

    orchestrator = create_orchestrator()

    # Add a task
    orchestrator.add_task(
        task_id="test_task", name="Test Task", priority=0.8, complexity=3.0, rest_mass=3.0
    )

    task = orchestrator.state.tasks["test_task"]

    print(f"\nInitial spinor state:")
    print(f"  ψ₁ (pos energy, spin up): {task.spinor.psi_1}")
    print(f"  ψ₂ (pos energy, spin down): {task.spinor.psi_2}")
    print(f"  ψ₃ (neg energy, spin up): {task.spinor.psi_3}")
    print(f"  ψ₄ (neg energy, spin down): {task.spinor.psi_4}")
    print(f"  Total probability: {task.spinor.total_probability:.3f}")
    print(f"  Positive energy prob: {task.spinor.positive_energy_prob:.3f}")
    print(f"  Negative energy prob: {task.spinor.negative_energy_prob:.3f}")

    # Evolve for a few steps
    print(f"\nEvolving for 10 steps...")
    for _ in range(10):
        orchestrator.evolve()

    print(f"\nAfter evolution:")
    print(f"  ψ₁: {task.spinor.psi_1:.4f}")
    print(f"  ψ₂: {task.spinor.psi_2:.4f}")
    print(f"  ψ₃: {task.spinor.psi_3:.4f}")
    print(f"  ψ₄: {task.spinor.psi_4:.4f}")
    print(f"  Total probability: {task.spinor.total_probability:.3f}")

    # Physics properties
    current = orchestrator.dirac.compute_current(task)
    helicity = orchestrator.dirac.helicity(task, orchestrator.state)
    zitter = orchestrator.dirac.zitterbewegung_amplitude(task)

    print(f"\nPhysics properties:")
    print(f"  Dirac current: {current}")
    print(f"  Current magnitude: {np.linalg.norm(current):.3f} (max={orchestrator.constants.c})")
    print(f"  Helicity: {helicity:.3f}")
    print(f"  Zitterbewegung amplitude: {zitter:.3f}")
    print(f"  Stable: {zitter < 0.5}")
    print(f"  Lorentz factor γ: {task.lorentz_factor:.3f}")
    print(f"  Relativistic mass: {task.relativistic_mass:.3f}")
    print(f"  Total energy: {task.total_energy:.3f}")


def main():
    """Run all examples."""
    example_basic_orchestration()
    example_with_deadlines()
    example_resource_constraints()
    example_spinor_analysis()

    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
