"""
Performance-optimized quantum orchestrator using vectorized operations.

This module provides batch evolution capabilities for processing multiple
tasks simultaneously using numpy broadcasting and einsum operations.
"""

from dataclasses import dataclass

import numpy as np

from .constants import PhysicsConstants
from .orchestrator import DiracMatrices, TaskState


@dataclass
class BatchState:
    """Batched state for vectorized operations."""

    spinors: np.ndarray  # Shape: (N, 4) - N task spinors
    positions: np.ndarray  # Shape: (N, 5) - N task positions
    velocities: np.ndarray  # Shape: (N, 5) - N task velocities
    masses: np.ndarray  # Shape: (N,) - N task masses
    task_ids: list[str]  # Length N - task identifiers

    def __len__(self) -> int:
        return len(self.task_ids)


class VectorizedEvolution:
    """
    Vectorized evolution engine for quantum orchestrator.

    Key optimizations:
    1. Batch spinor evolution using einsum
    2. Vectorized gradient computation
    3. SIMD-friendly normalization
    4. Spatial indexing for neighbor queries
    """

    def __init__(self, constants: PhysicsConstants):
        self.constants = constants
        self.hbar = constants.hbar
        self.c = constants.c  # type: ignore[attr-defined]

        # Pre-compute Dirac matrices
        self.dirac = DiracMatrices()
        self.alpha = np.array([self.dirac.alpha_x(), self.dirac.alpha_y(), self.dirac.alpha_z()])
        self.beta = self.dirac.beta()

    def batch_evolve_spinors(
        self,
        spinors: np.ndarray,
        gradients: np.ndarray,
        masses: np.ndarray,
        dt: float,
    ) -> np.ndarray:
        """
        Evolve all spinors in one vectorized operation.

        Args:
            spinors: Shape (N, 4) - N task spinors
            gradients: Shape (N, 5) - Spatial gradients for each task
            masses: Shape (N,) - Rest masses
            dt: Time step

        Returns:
            Evolved spinors of shape (N, 4)
        """
        N = spinors.shape[0]

        # Dirac Hamiltonian: H = -iℏα·∇ + βmc²
        # We'll compute this for all tasks at once

        # Step 1: -iℏα·∇ψ term
        # For each task, we need α·∇ = α₁∂/∂x₁ + α₂∂/∂x₂ + α₃∂/∂x₃
        # Use first 3 gradient components for spatial derivatives
        spatial_grads = gradients[:, :3]  # Shape: (N, 3)

        # Compute α·∇ψ for all tasks: einsum over alpha matrices and gradients
        # alpha: (3, 4, 4) - three 4x4 matrices
        # spatial_grads: (N, 3) - N tasks, 3 spatial components
        # spinors: (N, 4) - N spinors

        # First apply alpha matrices to spinors
        alpha_psi = np.einsum("ijk,nk->nij", self.alpha, spinors)  # (N, 3, 4)

        # Then contract with gradients
        kinetic_term = np.einsum("nij,ni->nj", alpha_psi, spatial_grads)  # (N, 4)
        kinetic_term = -1j * self.hbar * kinetic_term

        # Step 2: βmc²ψ term
        mass_term = np.einsum("ij,nj->ni", self.beta, spinors)  # (N, 4)
        mass_term = np.outer(masses * self.c**2, np.ones(4)).reshape(N, 4) * mass_term

        # Total Hamiltonian
        H_psi = kinetic_term + mass_term

        # Evolve: ψ(t+dt) = ψ(t) - (i/ℏ)Hψ dt
        return spinors - (1j / self.hbar) * H_psi * dt

    def batch_normalize(self, spinors: np.ndarray) -> np.ndarray:
        """
        Normalize all spinors simultaneously.

        Args:
            spinors: Shape (N, 4)

        Returns:
            Normalized spinors of shape (N, 4)
        """
        # Compute norms: ψ†ψ for each spinor
        norms = np.sqrt(np.sum(np.abs(spinors) ** 2, axis=1, keepdims=True))  # (N, 1)

        # Avoid division by zero
        norms = np.where(norms > 1e-10, norms, 1.0)

        return spinors / norms

    def batch_compute_dirac_current(
        self,
        spinors: np.ndarray,
    ) -> np.ndarray:
        """
        Compute Dirac current for all tasks.

        j = c ψ† α ψ

        Args:
            spinors: Shape (N, 4)

        Returns:
            Currents of shape (N, 3) for 3D current vectors
        """
        # ψ† (conjugate transpose)
        psi_dagger = np.conj(spinors)  # (N, 4)

        # Compute ψ†α for all three alpha matrices
        # alpha: (3, 4, 4)
        # psi_dagger: (N, 4)
        psi_dag_alpha = np.einsum("ni,jik->njk", psi_dagger, self.alpha)  # (N, 3, 4)

        # Contract with ψ to get j = ψ†αψ
        currents = np.einsum("nji,ni->nj", psi_dag_alpha, spinors)  # (N, 3)

        # Multiply by c and take real part (current is real)
        return self.c * np.real(currents)

    def batch_compute_probabilities(self, spinors: np.ndarray) -> dict[str, np.ndarray]:
        """
        Compute probability distributions for all spinors.

        Args:
            spinors: Shape (N, 4)

        Returns:
            Dictionary with probability arrays
        """
        # Total probability for each task
        total_prob = np.sum(np.abs(spinors) ** 2, axis=1)  # (N,)

        # Positive energy (components 0, 1)
        positive_prob = np.sum(np.abs(spinors[:, :2]) ** 2, axis=1)  # (N,)

        # Negative energy (components 2, 3)
        negative_prob = np.sum(np.abs(spinors[:, 2:]) ** 2, axis=1)  # (N,)

        # Spin up (components 0, 2)
        spin_up_prob = np.sum(np.abs(spinors[:, [0, 2]]) ** 2, axis=1)  # (N,)

        # Spin down (components 1, 3)
        spin_down_prob = np.sum(np.abs(spinors[:, [1, 3]]) ** 2, axis=1)  # (N,)

        return {
            "total": total_prob,
            "positive_energy": positive_prob,
            "negative_energy": negative_prob,
            "spin_up": spin_up_prob,
            "spin_down": spin_down_prob,
        }

    def batch_compute_helicity(
        self,
        spinors: np.ndarray,
        velocities: np.ndarray,
    ) -> np.ndarray:
        """
        Compute helicity for all tasks.

        Helicity = (spin · momentum) / |momentum|

        Args:
            spinors: Shape (N, 4)
            velocities: Shape (N, 5) - only first 3 used for momentum direction

        Returns:
            Helicity values of shape (N,)
        """
        # Compute spin expectation values
        # For Dirac spinors, spin = (ℏ/2) Σ where Σ = diag(σ, σ)
        # with σ = Pauli matrices

        # Simplified: use spin-up vs spin-down probability difference
        spin_up = np.abs(spinors[:, 0]) ** 2 + np.abs(spinors[:, 2]) ** 2
        spin_down = np.abs(spinors[:, 1]) ** 2 + np.abs(spinors[:, 3]) ** 2
        spin_z = spin_up - spin_down  # Projection along z

        # Momentum direction (use first 3 velocity components)
        momentum_dir = velocities[:, :3]

        # Helicity (simplified as spin-z for now)
        return spin_z * np.sign(momentum_dir[:, 2])  # Use z-component sign

    def batch_compute_zitterbewegung(self, spinors: np.ndarray) -> np.ndarray:
        """
        Compute zitterbewegung amplitude for all tasks.

        Amplitude = 2√(P₊ · P₋)

        Args:
            spinors: Shape (N, 4)

        Returns:
            Amplitudes of shape (N,)
        """
        # Positive energy probability
        P_plus = np.sum(np.abs(spinors[:, :2]) ** 2, axis=1)

        # Negative energy probability
        P_minus = np.sum(np.abs(spinors[:, 2:]) ** 2, axis=1)

        # Amplitude
        return 2 * np.sqrt(P_plus * P_minus)


class SpatialIndex:
    """
    Spatial indexing for efficient neighbor queries.

    Uses a simple grid-based approach for fast neighbor lookups.
    """

    def __init__(self, cell_size: float = 2.0):
        self.cell_size = cell_size
        self.grid: dict[tuple[int, ...], list[int]] = {}

    def _get_cell(self, position: np.ndarray) -> tuple[int, ...]:
        """Get grid cell for a position."""
        return tuple((position / self.cell_size).astype(int))

    def build_index(self, positions: np.ndarray) -> None:
        """
        Build spatial index from positions.

        Args:
            positions: Shape (N, 5) - task positions
        """
        self.grid.clear()

        for i, pos in enumerate(positions):
            cell = self._get_cell(pos)
            if cell not in self.grid:
                self.grid[cell] = []
            self.grid[cell].append(i)

    def query_neighbors(
        self,
        position: np.ndarray,
        positions: np.ndarray,
        radius: float,
    ) -> list[int]:
        """
        Find all neighbors within radius of position.

        Args:
            position: Query position (5D)
            positions: All positions, shape (N, 5)
            radius: Search radius

        Returns:
            list of neighbor indices
        """
        # Get cells to check (current + adjacent)
        center_cell = self._get_cell(position)
        cells_to_check = self._get_adjacent_cells(center_cell)

        # Collect candidates
        candidates = []
        for cell in cells_to_check:
            if cell in self.grid:
                candidates.extend(self.grid[cell])

        # Filter by actual distance
        neighbors = []
        for idx in candidates:
            dist = np.linalg.norm(positions[idx] - position)
            if dist <= radius:
                neighbors.append(idx)

        return neighbors

    def _get_adjacent_cells(self, cell: tuple[int, ...]) -> list[tuple[int, ...]]:
        """Get current cell and all adjacent cells."""
        cells = [cell]

        # Add neighboring cells (in 5D, this is 3^5 = 243 cells, but we'll use a subset)
        for dim in range(len(cell)):
            new_cells = []
            for c in cells:
                c_list = list(c)
                for offset in [-1, 0, 1]:
                    c_list[dim] = cell[dim] + offset
                    new_cells.append(tuple(c_list))
            cells = new_cells

        return cells


class BatchGradientComputer:
    """
    Compute gradients for all tasks using spatial indexing.
    """

    def __init__(self, constants: PhysicsConstants):
        self.constants = constants
        self.spatial_index = SpatialIndex(cell_size=2.0)

    def compute_batch_gradients(
        self,
        spinors: np.ndarray,
        positions: np.ndarray,
        radius: float = 2.0,
    ) -> np.ndarray:
        """
        Compute spatial gradients for all tasks.

        Args:
            spinors: Shape (N, 4)
            positions: Shape (N, 5)
            radius: Neighbor search radius

        Returns:
            Gradients of shape (N, 5)
        """
        N = positions.shape[0]
        gradients = np.zeros((N, 5))

        # Build spatial index
        self.spatial_index.build_index(positions)

        # Compute gradient for each task
        for i in range(N):
            neighbors = self.spatial_index.query_neighbors(positions[i], positions, radius)

            if len(neighbors) == 0:
                continue

            # Compute finite difference gradient
            for j in neighbors:
                if i == j:
                    continue

                # Position difference
                delta_pos = positions[j] - positions[i]
                distance = np.linalg.norm(delta_pos)

                if distance < 1e-10:
                    continue

                # Amplitude difference (use total probability)
                amplitude_i = np.sqrt(np.sum(np.abs(spinors[i]) ** 2))
                amplitude_j = np.sqrt(np.sum(np.abs(spinors[j]) ** 2))
                delta_amp = amplitude_j - amplitude_i

                # Gradient contribution
                gradients[i] += (delta_amp / distance) * (delta_pos / distance)

            # Average over neighbors
            if len(neighbors) > 1:
                gradients[i] /= len(neighbors) - 1  # Exclude self

        return gradients


def extract_batch_state(tasks: dict[str, TaskState]) -> BatchState:
    """
    Extract batch state from task dictionary.

    Args:
        tasks: Dictionary of TaskState objects

    Returns:
        BatchState for vectorized operations
    """
    task_ids = list(tasks.keys())
    N = len(task_ids)

    spinors = np.zeros((N, 4), dtype=complex)
    positions = np.zeros((N, 5))
    velocities = np.zeros((N, 5))
    masses = np.zeros(N)

    for i, task_id in enumerate(task_ids):
        task = tasks[task_id]
        spinors[i] = task.spinor.components
        positions[i] = task.position.to_array()
        velocities[i] = task.velocity
        masses[i] = task.rest_mass

    return BatchState(
        spinors=spinors,
        positions=positions,
        velocities=velocities,
        masses=masses,
        task_ids=task_ids,
    )


def apply_batch_state(batch: BatchState, tasks: dict[str, TaskState]) -> None:
    """
    Apply batch state back to task dictionary.

    Args:
        batch: BatchState with updated values
        tasks: Dictionary of TaskState objects to update
    """
    for i, task_id in enumerate(batch.task_ids):
        if task_id in tasks:
            tasks[task_id].spinor.components = batch.spinors[i]
            tasks[task_id].velocity = batch.velocities[i]
