"""
Physical constants for the Quantum-Relativistic-Dirac Orchestrator.

Defines fundamental constants that govern the behavior of the orchestrator:
- ℏ (hbar): Planck's reduced constant - minimum meaningful work unit
- c: Speed of light - maximum throughput rate
- m: Rest mass - base task complexity
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PhysicsConstants:
    """
    Basic quantum mechanics constants.

    Attributes:
        hbar: Reduced Planck constant (ℏ) - granularity of work
        default_mass: Default task mass (complexity)
    """

    hbar: float = 1.0  # Minimum meaningful work unit
    default_mass: float = 1.0  # Default task complexity

    @property
    def hbar_squared(self) -> float:
        """ℏ² - appears in kinetic energy operator."""
        return self.hbar**2


@dataclass
class RelativisticConstants(PhysicsConstants):
    """
    Relativistic constants extending basic quantum mechanics.

    Adds the speed of light (c) which defines the maximum throughput
    rate that the system can sustain.

    Attributes:
        c: Speed of light - maximum throughput rate
        hbar: Reduced Planck constant (inherited)
        default_mass: Default task mass (inherited)
    """

    c: float = 100.0  # Maximum throughput (tasks per unit time)

    @property
    def c_squared(self) -> float:
        """c² - appears in energy calculations."""
        return self.c**2

    @property
    def c_fourth(self) -> float:
        """c⁴ - appears in relativistic energy equation."""
        return self.c**4

    def rest_energy(self, mass: Optional[float] = None) -> float:
        """
        Compute rest energy: E₀ = mc².

        Args:
            mass: Task mass (complexity). Uses default if None.

        Returns:
            Rest energy (idle cost)
        """
        m = mass if mass is not None else self.default_mass
        return m * self.c_squared

    def compton_wavelength(self, mass: Optional[float] = None) -> float:
        """
        Compute Compton wavelength: λ = ℏ/(mc).

        This is the characteristic length scale for a task.

        Args:
            mass: Task mass (complexity). Uses default if None.

        Returns:
            Compton wavelength
        """
        m = mass if mass is not None else self.default_mass
        if m == 0:
            return float("inf")
        return self.hbar / (m * self.c)

    def classical_electron_radius(self, mass: Optional[float] = None) -> float:
        """
        Compute classical radius: r = ℏ/(mc).

        Same as Compton wavelength for our purposes.

        Args:
            mass: Task mass

        Returns:
            Classical radius
        """
        return self.compton_wavelength(mass)


# Default constants instance
DEFAULT_CONSTANTS = RelativisticConstants()
