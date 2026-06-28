"""
Command-Line Interface for Quantum Orchestrator.

Provides intuitive commands for:
- Running orchestration with test tasks
- Performance benchmarking
- Quantum state inspection
- Metrics export (Prometheus format)
- QFT operations (spawn, entangle, optimize)

Examples:
    $ python -m codex.quantum_orchestrator.cli run --tasks 10
    $ python -m codex.quantum_orchestrator.cli benchmark --iterations 100
    $ python -m codex.quantum_orchestrator.cli inspect task_1
    $ python -m codex.quantum_orchestrator.cli qft spawn --count 5
    $ python -m codex.quantum_orchestrator.cli qft entangle task_1 task_2
"""

import json
import logging

logger = logging.getLogger(__name__)
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Optional  # noqa: E402

import click  # noqa: E402
import numpy as np  # noqa: E402

# Import orchestrator components
try:
    from codex.quantum_orchestrator import (
        DiracSpinor,
        OrchestratorState,
        TaskState,
        TaskVector,
        create_observable_orchestrator,
    )

    # QFT extensions
    try:
        from codex.quantum_orchestrator.qft import (
            BellState,
            EntanglementManager,
            PathIntegralOptimizer,
            TaskSpawner,
        )

        QFT_AVAILABLE = True
    except ImportError as e:
        error_type = type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")
        logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
        QFT_AVAILABLE = False
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    click.echo(f"Error importing quantum orchestrator: {e}", err=True)
    click.echo("Make sure numpy is installed: pip install numpy", err=True)
    sys.exit(1)


# ============================================================================
# Helper Functions
# ============================================================================


def create_test_tasks(count: int) -> dict[str, TaskState]:
    """
    Create a set of test tasks for demonstration.

    Args:
        count: Number of tasks to create
    Returns:
        Dictionary of task_id -> TaskState
    """
    tasks = {}
    for i in range(count):
        # Create normalized spinor
        spinor = DiracSpinor(components=np.array([0.8 + 0j, 0.6 + 0j, 0j, 0j]))
        spinor.normalize()

        # Create task with varying properties
        task = TaskState(
            task_id=f"task_{i}",
            name=f"Test Task {i}",
            position=TaskVector(
                priority=0.1 * (i + 1),
                complexity=1.0 + 0.5 * i,
                resource_demand=0.3,
                time_sensitivity=0.5,
                dependency_depth=0,
            ),
            spinor=spinor,
            velocity=np.array([0.1 * i, 0.0, 0.0, 0.0, 0.0]),
            rest_mass=1.0 + 0.1 * i,
        )

        tasks[task.task_id] = task

    return tasks


def format_task_state(task: TaskState) -> str:
    """Format task state for display."""
    return f"""Task: {task.task_id}
  Name: {task.name}
  Position: priority={task.position.priority:.3f}, complexity={task.position.complexity:.3f}
  Probability: {task.probability:.4f}
  Velocity: {np.linalg.norm(task.velocity):.4f}
  Mass: {task.rest_mass:.3f}
  Energy: {task.total_energy:.2f}
"""


def export_metrics_prometheus(state: OrchestratorState) -> str:
    """
    Export metrics in Prometheus format.

    Args:
        state: Current orchestrator state

    Returns:
        Prometheus-formatted metrics string
    """
    lines = []

    # Add metadata
    lines.append("# HELP quantum_orchestrator_tasks Total number of tasks")
    lines.append("# TYPE quantum_orchestrator_tasks gauge")
    lines.append(f"quantum_orchestrator_tasks {len(state.tasks)}")

    lines.append("# HELP quantum_orchestrator_total_probability Total probability across all tasks")
    lines.append("# TYPE quantum_orchestrator_total_probability gauge")
    lines.append(f"quantum_orchestrator_total_probability {state.total_probability()}")

    lines.append("# HELP quantum_orchestrator_coherence System coherence")
    lines.append("# TYPE quantum_orchestrator_coherence gauge")
    lines.append(f"quantum_orchestrator_coherence {state.coherence}")

    # Per-task metrics
    for task_id, task in state.tasks.items():
        lines.append(f"# HELP quantum_orchestrator_task_probability Probability for task {task_id}")
        lines.append("# TYPE quantum_orchestrator_task_probability gauge")
        lines.append(
            f'quantum_orchestrator_task_probability{{task_id="{task_id}"}} {task.probability}'
        )

        lines.append(f'quantum_orchestrator_task_energy{{task_id="{task_id}"}} {task.total_energy}')

        speed = np.linalg.norm(task.velocity)
        lines.append(f'quantum_orchestrator_task_speed{{task_id="{task_id}"}} {speed}')

    return "\n".join(lines)


# ============================================================================
# Main CLI Group
# ============================================================================


@click.group()
@click.version_option(version="0.3.0")
def cli() -> None:
    """
    Quantum Orchestrator CLI.

    A physics-inspired task orchestration framework with quantum mechanics,
    relativity, and QFT extensions.
    """


# ============================================================================
# Core Commands
# ============================================================================


@cli.command()
@click.option("--tasks", default=5, help="Number of test tasks to create")
@click.option("--steps", default=10, help="Number of evolution steps")
@click.option("--dt", default=0.1, help="Time step size")
@click.option("--output", type=click.Path(), help="Output file for results (JSON)")
@click.option("--verbose", is_flag=True, help="Verbose output")
def run(tasks: int, steps: int, dt: float, output: Optional[str], verbose: bool) -> None:
    """
    Run orchestration with test tasks.

    Creates test tasks and evolves them through the quantum orchestrator,
    demonstrating the core physics-inspired dynamics.

    Examples:
        $ quantum-orchestrator run --tasks 10 --steps 20
        $ quantum-orchestrator run --tasks 5 --output results.json
    """
    click.echo(f"🌌 Quantum Orchestrator - Running with {tasks} tasks")
    click.echo(f"   Steps: {steps}, dt: {dt}")

    # Create orchestrator
    orchestrator = create_observable_orchestrator(
        max_throughput=100.0,
        work_granularity=1.0,
        time_step=dt,
    )

    # Create test tasks
    test_tasks = create_test_tasks(tasks)

    # Initialize state (set orchestrator's internal state)
    orchestrator.orchestrator.state = OrchestratorState(
        tasks=test_tasks,
        constants=orchestrator.orchestrator.constants,
    )

    if verbose:
        click.echo("\n📊 Initial State:")
        for task in orchestrator.orchestrator.state.tasks.values():
            click.echo(f"  {task.task_id}: probability={task.probability:.4f}")

    # Evolution
    click.echo("\n⚛️  Evolving system...")
    results = []

    for step in range(steps):
        orchestrator.evolve()
        state = orchestrator.orchestrator.state

        total_prob = state.total_probability()
        results.append(
            {
                "step": step,
                "time": state.timestamp,
                "total_probability": total_prob,
                "coherence": state.coherence,
            }
        )

        if verbose or step % max(1, steps // 5) == 0:
            click.echo(
                f"  Step {step:3d}: t={state.timestamp:.2f}, "
                f"P_total={total_prob:.4f}, coherence={state.coherence:.4f}"
            )

    # Final state
    click.echo("\n✅ Final State:")
    for task in orchestrator.orchestrator.state.tasks.values():
        click.echo(
            f"  {task.task_id}: probability={task.probability:.4f}, energy={task.total_energy:.2f}"
        )

    # Save results if requested
    if output:
        output_data = {
            "config": {"tasks": tasks, "steps": steps, "dt": dt},
            "results": results,
            "final_state": {
                task_id: {
                    "probability": task.probability,
                    "energy": task.total_energy,
                    "position": task.position.to_array().tolist(),
                }
                for task_id, task in orchestrator.orchestrator.state.tasks.items()
            },
        }

        Path(output).write_text(json.dumps(output_data, indent=2))
        click.echo(f"\n💾 Results saved to {output}")


@cli.command()
@click.option("--tasks", default=10, help="Number of tasks to benchmark")
@click.option("--iterations", default=100, help="Number of iterations")
@click.option("--warmup", default=10, help="Warmup iterations")
def benchmark(tasks: int, iterations: int, warmup: int) -> None:
    """
    Performance benchmark.

    Measures evolution speed and throughput for the orchestrator.
    Useful for performance tuning and regression testing.

    Examples:
        $ quantum-orchestrator benchmark --tasks 100 --iterations 1000
    """
    click.echo("⚡ Benchmarking Quantum Orchestrator")
    click.echo(f"   Tasks: {tasks}, Iterations: {iterations}")

    # Create orchestrator
    orchestrator = create_observable_orchestrator()
    test_tasks = create_test_tasks(tasks)

    orchestrator.orchestrator.state = OrchestratorState(
        tasks=test_tasks, constants=orchestrator.orchestrator.constants
    )

    # Warmup
    click.echo(f"\n🔥 Warming up ({warmup} iterations)...")
    for _ in range(warmup):
        orchestrator.evolve()

    # Benchmark
    click.echo("\n📊 Running benchmark...")
    start_time = time.perf_counter()

    for i in range(iterations):
        orchestrator.evolve()
        if i % max(1, iterations // 10) == 0:
            progress_pct = 100 * i // iterations
            click.echo(f"  Progress: {progress_pct:3d}%   ", nl=False)  # Extra spaces to clear line
            click.echo("\r", nl=False)

    elapsed = time.perf_counter() - start_time

    # Results
    click.echo("\n\n✅ Benchmark Results:")
    click.echo(f"   Total time: {elapsed:.3f} seconds")
    click.echo(f"   Iterations: {iterations}")
    click.echo(f"   Time per iteration: {1000 * elapsed / iterations:.3f} ms")
    click.echo(f"   Throughput: {iterations / elapsed:.1f} iterations/sec")
    click.echo(f"   Tasks per second: {tasks * iterations / elapsed:.1f}")


@cli.command()
@click.argument("task_id")
@click.option("--format", type=click.Choice(["text", "json"]), default="text")
def inspect(task_id: str, format: str) -> None:
    """
    Inspect quantum state of a task.

    Shows detailed information about a specific task's quantum state,
    including spinor components, position, velocity, and energy.

    Examples:
        $ quantum-orchestrator inspect task_0
        $ quantum-orchestrator inspect task_1 --format json
    """
    # Create test system
    create_observable_orchestrator()
    test_tasks = create_test_tasks(5)

    if task_id not in test_tasks:
        click.echo(f"❌ Task '{task_id}' not found. Available tasks:", err=True)
        for tid in test_tasks:
            click.echo(f"   - {tid}", err=True)
        sys.exit(1)

    task = test_tasks[task_id]

    if format == "json":
        data = {
            "task_id": task.task_id,
            "name": task.name,
            "position": {
                "priority": task.position.priority,
                "complexity": task.position.complexity,
                "resource_demand": task.position.resource_demand,
                "time_sensitivity": task.position.time_sensitivity,
                "dependency_depth": task.position.dependency_depth,
            },
            "spinor": {
                "psi_1": {
                    "real": float(task.spinor.psi_1.real),
                    "imag": float(task.spinor.psi_1.imag),
                },
                "psi_2": {
                    "real": float(task.spinor.psi_2.real),
                    "imag": float(task.spinor.psi_2.imag),
                },
                "psi_3": {
                    "real": float(task.spinor.psi_3.real),
                    "imag": float(task.spinor.psi_3.imag),
                },
                "psi_4": {
                    "real": float(task.spinor.psi_4.real),
                    "imag": float(task.spinor.psi_4.imag),
                },
                "total_probability": task.spinor.total_probability,
            },
            "probability": task.probability,
            "velocity": task.velocity.tolist(),
            "rest_mass": task.rest_mass,
            "energy": task.total_energy,
        }
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo("\n🔍 Quantum State Inspection")
        click.echo(format_task_state(task))
        click.echo("Spinor Components:")
        click.echo(f"  ψ₁ (pos energy, spin ↑): {task.spinor.psi_1:.4f}")
        click.echo(f"  ψ₂ (pos energy, spin ↓): {task.spinor.psi_2:.4f}")
        click.echo(f"  ψ₃ (neg energy, spin ↑): {task.spinor.psi_3:.4f}")
        click.echo(f"  ψ₄ (neg energy, spin ↓): {task.spinor.psi_4:.4f}")


@cli.command()
@click.option("--tasks", default=5, help="Number of tasks")
@click.option("--output", type=click.Path(), help="Output file for metrics")
def metrics(tasks: int, output: Optional[str]) -> None:
    """
    Export Prometheus metrics.

    Generates Prometheus-formatted metrics for the current orchestrator state.
    Useful for monitoring and integration with observability tools.

    Examples:
        $ quantum-orchestrator metrics --tasks 10
        $ quantum-orchestrator metrics --output metrics.txt
    """
    # Create orchestrator with test tasks
    orchestrator = create_observable_orchestrator()
    test_tasks = create_test_tasks(tasks)
    state = OrchestratorState(tasks=test_tasks, constants=orchestrator.orchestrator.constants)

    # Generate metrics
    metrics_text = export_metrics_prometheus(state)

    if output:
        Path(output).write_text(metrics_text)
        click.echo(f"✅ Metrics exported to {output}")
    else:
        click.echo(metrics_text)


# ============================================================================
# QFT Commands
# ============================================================================


@cli.group()
def qft() -> None:
    """
    Quantum Field Theory operations.

    Commands for advanced QFT features including task spawning,
    entanglement, and path integral optimization.
    """
    if not QFT_AVAILABLE:
        click.echo("❌ QFT extensions not available", err=True)
        click.echo("   Install dependencies or check imports", err=True)
        sys.exit(1)


@qft.command()
@click.option("--count", default=3, help="Number of tasks to spawn")
@click.option("--mode", default="default", help="Spawning mode")
def spawn(count: int, mode: str) -> None:
    """
    Spawn tasks using creation operator.

    Uses second quantization (creation operator) to dynamically
    spawn new tasks in the orchestrator.

    Examples:
        $ quantum-orchestrator qft spawn --count 5
        $ quantum-orchestrator qft spawn --count 10 --mode parallel
    """
    if not QFT_AVAILABLE:
        return

    click.echo(f"✨ Spawning {count} tasks using creation operator")

    # Create orchestrator and spawner
    orchestrator = create_observable_orchestrator()
    initial_tasks = create_test_tasks(2)
    state = OrchestratorState(tasks=initial_tasks, constants=orchestrator.orchestrator.constants)
    spawner = TaskSpawner(state)

    click.echo(f"\n📊 Initial state: {len(state.tasks)} tasks")

    # Spawn tasks
    for i in range(count):
        template = TaskState(
            task_id=f"spawned_{i}",
            name=f"Spawned Task {i}",
            position=TaskVector(priority=0.5, complexity=1.0),
            spinor=DiracSpinor(),
            velocity=np.zeros(5),
            rest_mass=1.0,
        )

        success, new_state = spawner.spawn_task(state, template, mode)

        if success:
            state = new_state
            click.echo(f"  ✅ Spawned {template.task_id}")
        else:
            click.echo(f"  ❌ Failed to spawn task {i}")

    click.echo(f"\n✅ Final state: {len(state.tasks)} tasks")
    click.echo(f"   Spawner metrics: {spawner.metrics.total_spawned} spawned")


@qft.command()
@click.argument("task_a")
@click.argument("task_b")
@click.option(
    "--bell-state",
    type=click.Choice(["phi_plus", "phi_minus", "psi_plus", "psi_minus"]),
    default="phi_plus",
    help="Type of Bell state",
)
def entangle(task_a: str, task_b: str, bell_state: str) -> None:
    """
    Create Bell state entanglement between two tasks.

    Entangles two tasks using quantum entanglement, creating
    correlated or anti-correlated execution states.

    Examples:
        $ quantum-orchestrator qft entangle task_0 task_1
        $ quantum-orchestrator qft entangle task_0 task_1 --bell-state psi_minus
    """
    if not QFT_AVAILABLE:
        return

    click.echo(f"🔗 Creating entanglement: {task_a} ↔ {task_b}")
    click.echo(f"   Bell state: {bell_state}")

    # Create orchestrator
    orchestrator = create_observable_orchestrator()
    test_tasks = create_test_tasks(5)

    if task_a not in test_tasks or task_b not in test_tasks:
        click.echo("❌ Tasks not found. Available:", err=True)
        for tid in test_tasks:
            click.echo(f"   - {tid}", err=True)
        sys.exit(1)

    state = OrchestratorState(tasks=test_tasks, constants=orchestrator.orchestrator.constants)

    # Create entanglement
    manager = EntanglementManager()
    bell = BellState[bell_state.upper()]

    success = manager.entangle(state, task_a, task_b, bell)

    if success:
        click.echo("✅ Tasks entangled successfully!")
        click.echo(f"   Pair count: {len(manager.entangled_pairs)}")
        click.echo(
            f"   Correlation: {manager.entangled_pairs[manager._canonical_key(task_a, task_b)].correlation_type}"  # noqa: E501
        )
    else:
        click.echo("❌ Entanglement failed", err=True)


@qft.command()
@click.option("--paths", default=100, help="Number of paths to sample")
@click.option("--temperature", default=1.0, help="Annealing temperature")
@click.option("--task-count", default=5, help="Number of tasks in system")
def optimize(paths: int, temperature: float, task_count: int) -> None:
    """
    Find optimal execution path via path integral.

    Uses Feynman path integral formulation to find the optimal
    execution strategy by sampling multiple possible paths.

    Examples:
        $ quantum-orchestrator qft optimize --paths 1000
        $ quantum-orchestrator qft optimize --paths 500 --temperature 0.5
    """
    if not QFT_AVAILABLE:
        return

    click.echo("🛤️  Path Integral Optimization")
    click.echo(f"   Sampling {paths} paths at T={temperature}")

    # Create orchestrator
    orchestrator = create_observable_orchestrator()
    test_tasks = create_test_tasks(task_count)
    initial_state = OrchestratorState(
        tasks=test_tasks, constants=orchestrator.orchestrator.constants
    )

    # Create optimizer — temperature scales perturbation_scale = _BASE_PERTURBATION_SCALE * T
    optimizer = PathIntegralOptimizer(
        orchestrator.orchestrator,
        n_paths=paths,
        temperature=temperature,
    )

    # Find optimal path
    click.echo("\n🔍 Searching for optimal path...")
    optimal = optimizer.find_optimal_path(
        initial_state,
        temperature=temperature,
    )

    click.echo("\n✅ Optimization complete!")
    click.echo(f"   Action: {optimal.action:.4f}")
    click.echo(f"   Time: {optimal.total_time:.2f}")
    click.echo(f"   Steps: {len(optimal.states)}")


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    cli()
