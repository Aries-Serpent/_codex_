"""
Shared exception hierarchy for agents package.

Provides consistent exception handling across all agent modules,
especially for optional dependency imports (numpy, scipy, etc.).
"""

from typing import Optional


# Package name constant - single source of truth for pip install instructions
PACKAGE_NAME = "codex-ml"


class AgentError(Exception):
    """Base exception for all agent-related errors."""
    pass


class AgentImportError(AgentError, ImportError):
    """
    Raised when an optional dependency is missing.
    
    Provides actionable remediation hints for users.
    """
    
    def __init__(
        self, 
        module_name: str, 
        package_name: Optional[str] = None, 
        extra: Optional[str] = None
    ) -> None:
        """
        Initialize import error with helpful message.
        
        Args:
            module_name: Name of the missing module (e.g., 'numpy')
            package_name: Optional package name if different (e.g., 'numpy' for 'np')
            extra: Optional extra requirement group (e.g., 'perf', 'ml')
        """
        self.module_name = module_name
        self.package_name = package_name or module_name
        self.extra = extra
        
        msg = f"Optional dependency '{self.module_name}' is not installed."
        
        if extra:
            msg += f"\nInstall with: pip install {PACKAGE_NAME}[{extra}]"
        else:
            msg += f"\nInstall with: pip install {self.package_name}"
        
        super().__init__(msg)


class AgentConfigError(AgentError, ValueError):
    """Raised when agent configuration is invalid."""
    pass


class AgentValidationError(AgentError, ValueError):
    """Raised when validation fails (e.g., invariants violated)."""
    pass


class AgentExecutionError(AgentError, RuntimeError):
    """Raised when agent execution encounters an error."""
    pass


class EntanglementError(AgentError):
    """Raised when entanglement operations fail."""
    pass


class GaugeError(AgentError):
    """Raised when gauge symmetry or conservation checks fail."""
    pass


class ContinuityError(AgentValidationError):
    """Raised when continuity equation is violated."""
    pass


class BoundCheckError(AgentValidationError):
    """Raised when physical bounds are violated (e.g., |j| > c)."""
    pass


# Physics-specific exceptions for test compatibility
class PhysicsError(AgentError):
    """Base exception for physics-related errors."""
    pass


class ValidationError(AgentValidationError):
    """Raised when validation fails - alias for backward compatibility."""
    pass


class ConvergenceError(PhysicsError):
    """Raised when iterative physics calculations fail to converge."""
    pass


class InvariantViolationError(PhysicsError):
    """Raised when physical invariants are violated."""
    pass


class CausalityViolationError(PhysicsError):
    """Raised when causality constraints are violated (e.g., v > c)."""
    pass
