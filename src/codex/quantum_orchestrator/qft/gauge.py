"""
Gauge Symmetries and Conservation Laws for Quantum Orchestrator.

Implements fundamental symmetries and their associated conserved quantities
via Noether's theorem:
- U(1) gauge symmetry → probability conservation
- Translation symmetry → momentum conservation
- Time translation symmetry → energy conservation
- Noether currents for probability and momentum flow

These symmetries provide a framework for verifying and enforcing
conservation laws in the quantum orchestration framework.

Mathematical Background:
- U(1) gauge: ψ → e^{iθ}ψ leaves |ψ|² invariant
- Noether current: j^μ = (ρ, j) where ∂_μ j^μ = 0 (continuity equation)
- Probability current: j = (iℏ/2m)(ψ*∇ψ - ψ∇ψ*)
"""

import copy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import numpy as np

from ..orchestrator import (
    OrchestratorState,
    PhysicsConstants,
    TaskState,
    TaskVector,
)


class SymmetryType(Enum):
    """Types of gauge symmetries."""

    U1_PHASE = "u1_phase"  # Global phase transformation
    TRANSLATION = "translation"  # Spatial translation
    TIME_TRANSLATION = "time_translation"  # Temporal translation


@dataclass
class TransformationResult:
    """Result of applying a gauge transformation."""

    transformed_state: OrchestratorState
    is_invariant: bool
    deviation: float
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "is_invariant": self.is_invariant,
            "deviation": self.deviation,
            "details": self.details,
        }


class U1GaugeTransform:
    """
    U(1) gauge transformation: ψ → e^{iθ}ψ

    This is the fundamental symmetry of quantum mechanics. The phase θ can be:
    - Global (same for all tasks) → global U(1)
    - Local (different per task) → local U(1) gauge symmetry

    The probability |ψ|² is invariant under this transformation.
    """

    def __init__(self, constants: Optional[PhysicsConstants] = None):
        """
        Initialize U(1) gauge transform.

        Args:
            constants: Physical constants (optional)
        """
        self.constants = constants or PhysicsConstants()

    def apply_global(self, state: OrchestratorState, theta: float) -> OrchestratorState:
        """
        Apply global U(1) transformation: ψ → e^{iθ}ψ for all tasks.

        Args:
            state: Current orchestrator state
            theta: Global phase angle (radians)

        Returns:
            Transformed state
        """
        phase_factor = np.exp(1j * theta)
        transformed_state = copy.deepcopy(state)

        for _, task in transformed_state.tasks.items():
            # Transform spinor components
            task.spinor.components = task.spinor.components * phase_factor

        return transformed_state

    def apply_local(
        self, state: OrchestratorState, phase_map: dict[str, float]
    ) -> OrchestratorState:
        """
        Apply local U(1) transformation: ψ_i → e^{iθ_i}ψ_i.

        Each task gets its own phase transformation.

        Args:
            state: Current orchestrator state
            phase_map: Map of task_id → phase angle

        Returns:
            Transformed state
        """
        transformed_state = copy.deepcopy(state)

        for task_id, theta in phase_map.items():
            if task_id in transformed_state.tasks:
                phase_factor = np.exp(1j * theta)
                task = transformed_state.tasks[task_id]
                task.spinor.components = task.spinor.components * phase_factor

        return transformed_state

    def verify_invariance(
        self,
        original_state: OrchestratorState,
        theta: float = np.pi / 4,
        tolerance: float = 1e-10,
    ) -> TransformationResult:
        """
        Verify that probabilities are invariant under U(1) transformation.

        Checks that |ψ'|² = |ψ|² after transformation.

        Args:
            original_state: State to test
            theta: Test phase angle
            tolerance: Acceptable deviation

        Returns:
            TransformationResult with invariance check
        """
        transformed_state = self.apply_global(original_state, theta)

        max_deviation = 0.0
        deviations = {}

        for task_id in original_state.tasks:
            if task_id not in transformed_state.tasks:
                continue

            orig_prob = original_state.tasks[task_id].spinor.total_probability
            trans_prob = transformed_state.tasks[task_id].spinor.total_probability

            deviation = abs(trans_prob - orig_prob)
            deviations[task_id] = deviation
            max_deviation = max(max_deviation, deviation)

        is_invariant = max_deviation < tolerance

        return TransformationResult(
            transformed_state=transformed_state,
            is_invariant=is_invariant,
            deviation=max_deviation,
            details={
                "theta": theta,
                "max_deviation": max_deviation,
                "task_deviations": deviations,
                "tolerance": tolerance,
            },
        )


class TranslationSymmetry:
    """
    Spatial translation symmetry: x → x + a

    Symmetry under spatial translations implies momentum conservation.
    This is Noether's theorem in action.

    For tasks: shifting all priorities/complexities by a constant
    should preserve the dynamics.
    """

    def __init__(self, constants: Optional[PhysicsConstants] = None):
        """
        Initialize translation symmetry checker.

        Args:
            constants: Physical constants (optional)
        """
        self.constants = constants or PhysicsConstants()

    def apply_translation(
        self, state: OrchestratorState, displacement: np.ndarray
    ) -> OrchestratorState:
        """
        Apply spatial translation to all tasks: x → x + a.

        Args:
            state: Current orchestrator state
            displacement: 5D displacement vector

        Returns:
            Translated state
        """
        transformed_state = copy.deepcopy(state)

        for _, task in transformed_state.tasks.items():
            # Translate position
            task.position = TaskVector.from_array(task.position.to_array() + displacement)

        return transformed_state

    def compute_total_momentum(self, state: OrchestratorState) -> np.ndarray:
        """
        Compute total momentum: P = Σᵢ mᵢvᵢ

        This is the conserved quantity under translation symmetry.

        Args:
            state: Current orchestrator state

        Returns:
            Total momentum vector (5D)
        """
        total_momentum = np.zeros(5)

        for task in state.tasks.values():
            momentum = task.rest_mass * task.velocity
            total_momentum += momentum

        return total_momentum

    def verify_momentum_conservation(
        self,
        state_before: OrchestratorState,
        state_after: OrchestratorState,
        tolerance: float = 1e-6,
    ) -> TransformationResult:
        """
        Verify momentum conservation between two states.

        Args:
            state_before: Initial state
            state_after: Final state
            tolerance: Acceptable deviation

        Returns:
            TransformationResult with conservation check
        """
        p_before = self.compute_total_momentum(state_before)
        p_after = self.compute_total_momentum(state_after)

        deviation = np.linalg.norm(p_after - p_before)
        is_conserved = deviation < tolerance

        return TransformationResult(
            transformed_state=state_after,
            is_invariant=is_conserved,
            deviation=deviation,
            details={
                "momentum_before": p_before.tolist(),
                "momentum_after": p_after.tolist(),
                "deviation": deviation,
                "tolerance": tolerance,
            },
        )


class TimeTranslationSymmetry:
    """
    Time translation symmetry: t → t + τ

    Symmetry under time translations implies energy conservation.

    For autonomous systems (no explicit time dependence),
    the Hamiltonian commutes with the time evolution operator,
    leading to energy conservation.
    """

    def __init__(self, constants: Optional[PhysicsConstants] = None):
        """
        Initialize time translation symmetry checker.

        Args:
            constants: Physical constants (optional)
        """
        self.constants = constants or PhysicsConstants()

    def compute_total_energy(self, state: OrchestratorState) -> float:
        """
        Compute total energy: E = Σᵢ (½mᵢvᵢ² + Vᵢ)

        This is the conserved quantity under time translation symmetry.

        Args:
            state: Current orchestrator state

        Returns:
            Total energy
        """
        total_energy = 0.0

        for task in state.tasks.values():
            # Kinetic energy: T = ½mv²
            kinetic = 0.5 * task.rest_mass * np.dot(task.velocity, task.velocity)

            # Potential energy (use task priority as potential)
            potential = task.position.priority

            # Rest energy: E₀ = mc²
            rest_energy = task.rest_mass * self.constants.c_squared

            total_energy += kinetic + potential + rest_energy

        return total_energy

    def verify_energy_conservation(
        self,
        state_before: OrchestratorState,
        state_after: OrchestratorState,
        tolerance: float = 1e-6,
    ) -> TransformationResult:
        """
        Verify energy conservation between two states.

        Args:
            state_before: Initial state
            state_after: Final state
            tolerance: Acceptable deviation

        Returns:
            TransformationResult with conservation check
        """
        e_before = self.compute_total_energy(state_before)
        e_after = self.compute_total_energy(state_after)

        deviation = abs(e_after - e_before)
        is_conserved = deviation < tolerance

        return TransformationResult(
            transformed_state=state_after,
            is_invariant=is_conserved,
            deviation=deviation,
            details={
                "energy_before": e_before,
                "energy_after": e_after,
                "deviation": deviation,
                "tolerance": tolerance,
            },
        )


class NoetherCurrent:
    """
    Noether currents associated with continuous symmetries.

    For each continuous symmetry, there exists a conserved current j^μ:
    - Probability current: j = (ρ, j) where ∂ρ/∂t + ∇·j = 0
    - Momentum current (stress-energy tensor)

    The continuity equation ∂_μ j^μ = 0 expresses conservation.
    """

    def __init__(self, constants: Optional[PhysicsConstants] = None):
        """
        Initialize Noether current calculator.

        Args:
            constants: Physical constants (optional)
        """
        self.constants = constants or PhysicsConstants()

    def probability_current(
        self, task: TaskState, gradient_psi: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Compute probability current: j = (ℏ/2mi)(ψ*∇ψ - ψ∇ψ*)

        This is the current associated with U(1) symmetry.

        Args:
            task: Task state
            gradient_psi: Gradient of spinor (if known)

        Returns:
            Probability current vector (5D)
        """
        if gradient_psi is None:
            # Approximate gradient using velocity
            gradient_psi = task.velocity

        # For Dirac spinors, use upper components
        psi = task.spinor.components[:2]  # Positive energy components
        psi_star = np.conj(psi)

        # j = (ℏ/2mi)(ψ*∇ψ - ψ∇ψ*)
        # Simplified for discrete representation
        return (
            self.constants.hbar
            / (2.0 * task.rest_mass)
            * np.real(np.sum(psi_star) * gradient_psi - np.sum(psi) * np.conj(gradient_psi))
        )

    def momentum_current(self, task: TaskState) -> np.ndarray:
        """
        Compute momentum current (momentum density).

        This is related to the stress-energy tensor.

        Args:
            task: Task state

        Returns:
            Momentum current (5D)
        """
        # Momentum density: g = ρv where ρ = |ψ|²
        probability_density = task.spinor.total_probability
        return probability_density * task.velocity

    def verify_continuity(
        self,
        state_before: OrchestratorState,
        state_after: OrchestratorState,
        dt: float,
        tolerance: float = 1e-6,
    ) -> dict[str, Any]:
        """
        Verify continuity equation: ∂ρ/∂t + ∇·j = 0

        Args:
            state_before: State at time t
            state_after: State at time t + dt
            dt: Time step
            tolerance: Acceptable deviation

        Returns:
            Dictionary with continuity check results
        """
        results = {}
        max_violation = 0.0

        for task_id in state_before.tasks:
            if task_id not in state_after.tasks:
                continue

            task_before = state_before.tasks[task_id]
            task_after = state_after.tasks[task_id]

            # ∂ρ/∂t
            rho_before = task_before.spinor.total_probability
            rho_after = task_after.spinor.total_probability
            drho_dt = (rho_after - rho_before) / dt

            # Approximate ∇·j using velocity divergence
            j_before = self.probability_current(task_before)
            div_j = np.sum(j_before)  # Simplified divergence

            # Check continuity: ∂ρ/∂t + ∇·j ≈ 0
            violation = abs(drho_dt + div_j)
            results[task_id] = {
                "drho_dt": drho_dt,
                "div_j": div_j,
                "violation": violation,
            }
            max_violation = max(max_violation, violation)

        return {
            "max_violation": max_violation,
            "is_conserved": max_violation < tolerance,
            "task_results": results,
        }


class GaugeChecker:
    """
    Comprehensive gauge symmetry and conservation law checker.

    Combines all symmetry checks into a single interface:
    - U(1) gauge invariance
    - Translation symmetry (momentum conservation)
    - Time translation symmetry (energy conservation)
    - Continuity equations
    """

    def __init__(self, constants: Optional[PhysicsConstants] = None):
        """
        Initialize gauge checker.

        Args:
            constants: Physical constants (optional)
        """
        self.constants = constants or PhysicsConstants()
        self.u1_gauge = U1GaugeTransform(constants)
        self.translation = TranslationSymmetry(constants)
        self.time_translation = TimeTranslationSymmetry(constants)
        self.noether = NoetherCurrent(constants)

    def check_all(self, state: OrchestratorState, tolerance: float = 1e-6) -> dict[str, Any]:
        """
        Run all symmetry checks on a state.

        Args:
            state: State to check
            tolerance: Acceptable deviation

        Returns:
            Dictionary with all check results
        """
        results = {}

        # U(1) gauge invariance
        u1_result = self.u1_gauge.verify_invariance(state, tolerance=tolerance)
        results["u1_invariance"] = u1_result.to_dict()

        # Momentum (requires evolution, use snapshot)
        total_momentum = self.translation.compute_total_momentum(state)
        results["total_momentum"] = total_momentum.tolist()

        # Energy
        total_energy = self.time_translation.compute_total_energy(state)
        results["total_energy"] = total_energy  # type: ignore[assignment]

        # Summary
        results["all_passed"] = u1_result.is_invariant  # type: ignore[assignment]
        results["tolerance"] = tolerance  # type: ignore[assignment]

        return results

    def verify_all(
        self,
        state_before: OrchestratorState,
        state_after: OrchestratorState,
        dt: float,
        tolerance: float = 1e-6,
    ) -> dict[str, Any]:
        """
        Verify all conservation laws between two states.

        Args:
            state_before: Initial state
            state_after: Final state
            dt: Time step
            tolerance: Acceptable deviation

        Returns:
            Dictionary with all verification results
        """
        results = {}

        # Momentum conservation
        momentum_result = self.translation.verify_momentum_conservation(
            state_before, state_after, tolerance
        )
        results["momentum_conservation"] = momentum_result.to_dict()

        # Energy conservation
        energy_result = self.time_translation.verify_energy_conservation(
            state_before, state_after, tolerance
        )
        results["energy_conservation"] = energy_result.to_dict()

        # Continuity equation
        continuity_result = self.noether.verify_continuity(state_before, state_after, dt, tolerance)
        results["continuity"] = continuity_result

        # Summary
        all_passed = (
            momentum_result.is_invariant
            and energy_result.is_invariant
            and continuity_result["is_conserved"]
        )
        results["all_passed"] = all_passed  # type: ignore[assignment]
        results["tolerance"] = tolerance  # type: ignore[assignment]

        return results


class ConservationEnforcer:
    """
    Enforce conservation laws by detecting and repairing violations.

    When conservation laws are violated (due to numerical errors,
    discretization, or approximations), this class can:
    - Detect violations
    - Apply corrective transformations
    - Renormalize states
    - Log violations for debugging
    """

    def __init__(self, constants: Optional[PhysicsConstants] = None, auto_repair: bool = True):
        """
        Initialize conservation enforcer.

        Args:
            constants: Physical constants (optional)
            auto_repair: Automatically repair violations
        """
        self.constants = constants or PhysicsConstants()
        self.checker = GaugeChecker(constants)
        self.auto_repair = auto_repair
        self.violations_log: list[dict[str, Any]] = []

    def enforce_probability_conservation(
        self, state: OrchestratorState, tolerance: float = 1e-10
    ) -> tuple[OrchestratorState, bool]:
        """
        Enforce probability conservation: Σᵢ |ψᵢ|² = 1 for each task.

        Args:
            state: State to check/repair
            tolerance: Acceptable deviation from 1.0

        Returns:
            (repaired_state, was_repaired)
        """
        repaired_state = copy.deepcopy(state)
        was_repaired = False

        for task_id, task in repaired_state.tasks.items():
            total_prob = task.spinor.total_probability
            deviation = abs(total_prob - 1.0)

            if deviation > tolerance:
                # Log violation
                self.violations_log.append(
                    {
                        "type": "probability_violation",
                        "task_id": task_id,
                        "total_probability": total_prob,
                        "deviation": deviation,
                    }
                )

                # Repair if enabled
                if self.auto_repair:
                    task.spinor.normalize()
                    was_repaired = True

        return repaired_state, was_repaired

    def get_violations(self) -> list[dict[str, Any]]:
        """Get log of all detected violations."""
        return self.violations_log

    def clear_violations(self) -> None:
        """Clear violation log."""
        self.violations_log.clear()
