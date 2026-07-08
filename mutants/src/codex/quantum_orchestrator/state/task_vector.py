"""
TaskVector - Position representation in multi-dimensional task space.

Defines the position of a task across multiple dimensions:
- Priority axis
- Complexity axis
- Resource demand axis
- Time sensitivity axis
- Dependency depth axis
"""

from dataclasses import dataclass
from typing import Union

import numpy as np


@dataclass
class TaskVector:
    """
    Represents a task's position in multi-dimensional task space.

    This is the "x" in quantum mechanics — the position operator.

    Dimensions:
        priority: Priority level (0.0 = lowest, 1.0 = highest)
        complexity: Computational complexity (arbitrary units)
        resource_demand: Resource requirements (normalized 0-1)
        time_sensitivity: Urgency level (0 = flexible, 1 = critical)
        dependency_depth: Number of dependency levels (integer)
    """

    priority: float = 0.0
    complexity: float = 1.0
    resource_demand: float = 0.0
    time_sensitivity: float = 0.0
    dependency_depth: int = 0

    def to_array(self) -> np.ndarray:
        """
        Convert to numpy array for vector operations.

        Returns:
            5-element numpy array [priority, complexity, resource, time, depth]
        """
        return np.array(
            [
                self.priority,
                self.complexity,
                self.resource_demand,
                self.time_sensitivity,
                float(self.dependency_depth),
            ],
            dtype=np.float64,
        )

    @classmethod
    def from_array(cls, arr: np.ndarray) -> "TaskVector":
        """
        Create TaskVector from numpy array.

        Args:
            arr: 5-element array [priority, complexity, resource, time, depth]

        Returns:
            TaskVector instance
        """
        return cls(
            priority=float(arr[0]),
            complexity=float(arr[1]),
            resource_demand=float(arr[2]),
            time_sensitivity=float(arr[3]),
            dependency_depth=int(arr[4]),
        )

    def distance_to(self, other: "TaskVector") -> float:
        """
        Compute Euclidean distance to another task vector.

        Args:
            other: Another task vector

        Returns:
            Distance in task space
        """
        return np.linalg.norm(self.to_array() - other.to_array())

    def __add__(self, other: Union["TaskVector", np.ndarray]) -> "TaskVector":
        """Vector addition."""
        if isinstance(other, TaskVector):
            return TaskVector.from_array(self.to_array() + other.to_array())
        if isinstance(other, np.ndarray):
            return TaskVector.from_array(self.to_array() + other)
        return NotImplemented

    def __sub__(self, other: Union["TaskVector", np.ndarray]) -> Union["TaskVector", np.ndarray]:
        """Vector subtraction."""
        if isinstance(other, TaskVector):
            return self.to_array() - other.to_array()
        if isinstance(other, np.ndarray):
            return self.to_array() - other
        return NotImplemented

    def __mul__(self, scalar: float) -> "TaskVector":
        """Scalar multiplication."""
        return TaskVector.from_array(self.to_array() * scalar)

    def __rmul__(self, scalar: float) -> "TaskVector":
        """Right scalar multiplication."""
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> "TaskVector":
        """Scalar division."""
        return TaskVector.from_array(self.to_array() / scalar)

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"TaskVector(priority={self.priority:.3f}, "
            f"complexity={self.complexity:.3f}, "
            f"resource_demand={self.resource_demand:.3f}, "
            f"time_sensitivity={self.time_sensitivity:.3f}, "
            f"dependency_depth={self.dependency_depth})"
        )


# Dimension names for reference
DIMENSION_NAMES = [
    "priority",
    "complexity",
    "resource_demand",
    "time_sensitivity",
    "dependency_depth",
]
