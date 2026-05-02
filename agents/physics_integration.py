"""
Integration module connecting advanced physics calculators with existing systems.

This module provides integration points between:
- Advanced physics calculators (chaos, fractal, fluid, EM, wave, relativity)
- Existing quantum orchestrator
- Physics-inspired orchestrator
- Existing physics calculators (PINN, energy landscape, etc.)
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

try:
    from agents.advanced_physics_calculators import AdvancedPhysicsOrchestrator

    ADVANCED_PHYSICS_AVAILABLE = True
except ImportError as e:
    logger.debug(f"ImportError: {e}")
    logger.warning(f"ImportError: {e}", exc_info=True)
    ADVANCED_PHYSICS_AVAILABLE = False

try:
    from agents.physics_orchestrator import (
        DecisionState,
        PhysicsInspiredOrchestrator,
    )

    PHYSICS_ORCHESTRATOR_AVAILABLE = True
except ImportError as e:
    logger.debug(f"ImportError: {e}")
    logger.warning(f"ImportError: {e}", exc_info=True)
    PHYSICS_ORCHESTRATOR_AVAILABLE = False

# Import logging utilities
try:
    from codex.logging.session_logger import log_message

    LOGGING_AVAILABLE = True
except ImportError as e:
    logger.debug(f"ImportError: {e}")
    logger.warning(f"ImportError: {e}", exc_info=True)
    LOGGING_AVAILABLE = False

    # Fallback to print if logging not available
    def log_message(session_id, role, message, **kwargs):  # type: ignore
        print(f"[{role}] {message}")


class HybridPhysicsOrchestrator:
    """
    Hybrid orchestrator combining classical and emerging physics paradigms.

    Integrates:
    - Classical mechanics (energy, momentum)
    - Quantum mechanics (superposition, entanglement)
    - Chaos theory (unpredictable exploration)
    - Fractal geometry (multi-scale analysis)
    - Fluid dynamics (flow optimization)
    - Electromagnetic fields (influence propagation)
    - Wave mechanics (interference patterns)
    - Relativistic effects (latency awareness)
    """

    def __init__(self, session_id: Optional[str] = None):
        self.classical_orchestrator = None
        self.advanced_orchestrator = None
        self.session_id = session_id or "hybrid_physics"

        if PHYSICS_ORCHESTRATOR_AVAILABLE:
            self.classical_orchestrator = PhysicsInspiredOrchestrator()

        if ADVANCED_PHYSICS_AVAILABLE:
            self.advanced_orchestrator = AdvancedPhysicsOrchestrator()

        self.decision_history: list[dict[str, Any]] = []

    def _log(self, role: str, message: str) -> None:
        """Log a message using session logger."""
        log_message(self.session_id, role, message)

    def orchestrate_with_all_paradigms(
        self, decision_space: dict[str, Any], action_paths: Optional[list] = None
    ) -> dict[str, Any]:
        """
        Orchestrate decision using all available physics paradigms.

        Args:
            decision_space: Complete description of decision context
            action_paths: list of ActionPath objects (if classical available)

        Returns:
            Comprehensive orchestration results
        """
        results = {
            "paradigms_used": [],
            "classical_physics": None,
            "advanced_physics": None,
            "recommendations": [],
        }

        # Classical physics analysis
        if self.classical_orchestrator and action_paths:
            results["paradigms_used"].append("classical_mechanics")

            # Create decision state
            state = DecisionState(
                current_position=decision_space.get("current_position", "initial"),
                goal_position=decision_space.get("goal_position", "target"),
                available_resources=decision_space.get("resources", 1.0),
                time_available=decision_space.get("time", 1.0),
                current_velocity=decision_space.get("velocity", 0.5),
            )

            # Run classical orchestration
            classical_result = self.classical_orchestrator.orchestrate(state, action_paths)
            results["classical_physics"] = classical_result

        # Advanced physics analysis
        if self.advanced_orchestrator:
            results["paradigms_used"].extend(
                [
                    "chaos_theory",
                    "fractal_geometry",
                    "fluid_dynamics",
                    "electromagnetic_fields",
                    "wave_propagation",
                    "relativistic_effects",
                ]
            )

            advanced_result = self.advanced_orchestrator.full_analysis(decision_space)
            results["advanced_physics"] = advanced_result

        # Synthesize recommendations
        results["recommendations"] = self._synthesize_recommendations(results)

        self.decision_history.append(results)
        return results

    def _synthesize_recommendations(self, results: dict[str, Any]) -> list[str]:
        """
        Synthesize recommendations from all physics analyses.
        """
        recommendations = []

        # Classical physics recommendations
        if results.get("classical_physics"):
            action = results["classical_physics"].get("action_taken", "unknown")
            recommendations.append(f"Classical physics suggests: {action}")

        # Advanced physics recommendations
        if results.get("advanced_physics"):
            adv = results["advanced_physics"].get("paradigms", {})

            if "chaos" in adv:
                lyap = adv["chaos"].get("lyapunov_exponent", 0)
                if lyap > 0:
                    recommendations.append("Chaos detected: Use adaptive exploration")

            if "fractal" in adv:
                dim = adv["fractal"].get("fractal_dimension", 1.0)
                if dim > 2.0:
                    recommendations.append(
                        f"High fractal dimension ({dim:.2f}): Complex structure detected"
                    )

            if "fluid" in adv:
                bottlenecks = adv["fluid"].get("improvement", {}).get("bottleneck_reduction", 0)
                if bottlenecks > 0:
                    recommendations.append(f"Fluid optimization reduced {bottlenecks} bottlenecks")

        return recommendations

    def inject_chaos_into_decision(self, base_value: float, strength: float = 0.1) -> float:
        """
        Inject chaos into a decision value for exploration.

        Uses chaotic neural network if available.
        """
        if not ADVANCED_PHYSICS_AVAILABLE or not self.advanced_orchestrator:
            return base_value

        return self.advanced_orchestrator.chaos.inject_chaos(base_value, strength)

    def analyze_code_structure_fractal(self, code_tree: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze code structure using fractal geometry.
        """
        if not ADVANCED_PHYSICS_AVAILABLE or not self.advanced_orchestrator:
            return {"error": "Fractal analysis not available"}

        return self.advanced_orchestrator.fractal.analyze_code_tree(code_tree)

    def optimize_workflow_flow(self, workflow_description: dict[str, Any]) -> dict[str, Any]:
        """
        Optimize workflow using fluid dynamics.
        """
        if not ADVANCED_PHYSICS_AVAILABLE or not self.advanced_orchestrator:
            return {"error": "Fluid dynamics not available"}

        # Inject flows based on workflow
        for channel_id, flow_rate in workflow_description.items():
            if channel_id in self.advanced_orchestrator.fluid.channels:
                self.advanced_orchestrator.fluid.inject_flow(channel_id, flow_rate)

        return self.advanced_orchestrator.fluid.optimize_flow()

    def route_agent_with_em_field(
        self, start_position: Any, hotspots: list[tuple]  # np.ndarray when numpy available
    ) -> list[Any]:  # list[np.ndarray] when numpy available
        """
        Route agent using electromagnetic field.

        Args:
            start_position: Starting position [x, y]
            hotspots: list of (position, charge) tuples
        """
        if not ADVANCED_PHYSICS_AVAILABLE or not self.advanced_orchestrator:
            return [start_position]

        # Add hotspots as charges
        for pos, charge in hotspots:
            self.advanced_orchestrator.em_field.add_charge(pos, charge)

        # Route agent
        return self.advanced_orchestrator.em_field.route_agent(start_position)

    def propagate_signal_with_waves(self, sources: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Propagate signals using wave mechanics.

        Args:
            sources: list of signal sources with position, amplitude, frequency
        """
        if not ADVANCED_PHYSICS_AVAILABLE or not self.advanced_orchestrator:
            return {"error": "Wave propagation not available"}

        # Add sources
        for source in sources:
            self.advanced_orchestrator.wave.add_source(**source)

        # Propagate
        self.advanced_orchestrator.wave.propagate(steps=100)

        return {
            "propagation_complete": True,
            "history_length": len(self.advanced_orchestrator.wave.history),
        }

    def schedule_with_relativity(
        self, agents: list[dict[str, Any]], tasks: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Schedule tasks with relativistic corrections.

        Args:
            agents: list of agent descriptions
            tasks: list of task descriptions
        """
        if not ADVANCED_PHYSICS_AVAILABLE or not self.advanced_orchestrator:
            return {"error": "Relativistic scheduling not available"}

        # Add agents
        for agent in agents:
            self.advanced_orchestrator.relativity.add_agent(**agent)

        # Synchronize clocks
        sync_result = self.advanced_orchestrator.relativity.synchronize_clocks()

        # Schedule tasks
        scheduled = []
        for task in tasks:
            result = self.advanced_orchestrator.relativity.schedule_task(**task)
            scheduled.append(result)

        return {
            "clock_synchronization": sync_result,
            "scheduled_tasks": scheduled,
            "total_tasks": len(scheduled),
        }

    def get_capabilities(self) -> dict[str, bool]:
        """Get available physics paradigms."""
        return {
            "classical_physics": PHYSICS_ORCHESTRATOR_AVAILABLE,
            "chaos_theory": ADVANCED_PHYSICS_AVAILABLE,
            "fractal_geometry": ADVANCED_PHYSICS_AVAILABLE,
            "fluid_dynamics": ADVANCED_PHYSICS_AVAILABLE,
            "electromagnetic_fields": ADVANCED_PHYSICS_AVAILABLE,
            "wave_propagation": ADVANCED_PHYSICS_AVAILABLE,
            "relativistic_effects": ADVANCED_PHYSICS_AVAILABLE,
        }


def create_hybrid_orchestrator(session_id: Optional[str] = None) -> HybridPhysicsOrchestrator:
    """
    Factory function to create hybrid orchestrator.

    Args:
        session_id: Optional session ID for logging

    Returns:
        Configured HybridPhysicsOrchestrator instance
    """
    orchestrator = HybridPhysicsOrchestrator(session_id=session_id)

    # Log capabilities
    capabilities = orchestrator.get_capabilities()
    active_paradigms = [k for k, v in capabilities.items() if v]

    orchestrator._log(
        "system", f"Hybrid Physics Orchestrator initialized with {len(active_paradigms)} paradigms"
    )
    for paradigm in active_paradigms:
        orchestrator._log("system", f"  ✓ {paradigm}")

    return orchestrator


# Export main classes
__all__ = [
    "HybridPhysicsOrchestrator",
    "PhysicsIntegration",
    "create_hybrid_orchestrator",
    "ADVANCED_PHYSICS_AVAILABLE",
    "PHYSICS_ORCHESTRATOR_AVAILABLE",
]


# Create PhysicsIntegration as an alias for backward compatibility
# Many tests expect PhysicsIntegration class name
PhysicsIntegration = HybridPhysicsOrchestrator
