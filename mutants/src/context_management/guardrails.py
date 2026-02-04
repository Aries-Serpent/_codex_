"""
Loop Guardrails

Implements loop detection, recovery, and guardrails for agent execution.
Prevents infinite loops and repeated action patterns.
"""

from typing import Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
import hashlib
import json
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


@dataclass
class ActionRecord:
    """Record of an agent action."""

    action_type: str
    action_hash: str
    timestamp: datetime = field(default_factory=datetime.now)
    tool_name: Optional[str] = None
    parameters_hash: Optional[str] = None
    produced_artifacts: bool = False
    result_hash: Optional[str] = None

    def matches(self, other: "ActionRecord") -> bool:
        """Check if this action matches another (potential repeat)."""
        return (
            self.action_type == other.action_type
            and self.action_hash == other.action_hash
            and self.parameters_hash == other.parameters_hash
        )


@dataclass
class GuardrailViolation:
    """Record of a guardrail violation."""

    violation_type: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    action_history: list[str] = field(default_factory=list)
    recommended_action: str = ""


class LoopGuardrail:
    """
    Detect and prevent infinite loops in agent execution.

    Features:
    - Consecutive repeat detection (≥3 without new artifacts)
    - Pattern-based loop detection
    - Automatic recovery injection
    - Configurable thresholds
    """

    def xǁLoopGuardrailǁ__init____mutmut_orig(
        self,
        max_consecutive_repeats: int = 3,
        history_size: int = 100,
        pattern_window: int = 10,
        recovery_callback: Optional[Callable[[GuardrailViolation], str]] = None,
    ):
        """
        Initialize guardrail.

        Args:
            max_consecutive_repeats: Max same action without new artifacts
            history_size: Number of actions to keep in history
            pattern_window: Window size for pattern detection
            recovery_callback: Function to generate recovery message
        """
        self.max_consecutive_repeats = max_consecutive_repeats
        self.history_size = history_size
        self.pattern_window = pattern_window
        self._recovery_callback = recovery_callback or self._default_recovery

        # Action history
        self._history: deque = deque(maxlen=history_size)
        self._violations: list[GuardrailViolation] = []

        # Counters
        self._consecutive_count = 0
        self._last_action_hash: Optional[str] = None

    def xǁLoopGuardrailǁ__init____mutmut_1(
        self,
        max_consecutive_repeats: int = 4,
        history_size: int = 100,
        pattern_window: int = 10,
        recovery_callback: Optional[Callable[[GuardrailViolation], str]] = None,
    ):
        """
        Initialize guardrail.

        Args:
            max_consecutive_repeats: Max same action without new artifacts
            history_size: Number of actions to keep in history
            pattern_window: Window size for pattern detection
            recovery_callback: Function to generate recovery message
        """
        self.max_consecutive_repeats = max_consecutive_repeats
        self.history_size = history_size
        self.pattern_window = pattern_window
        self._recovery_callback = recovery_callback or self._default_recovery

        # Action history
        self._history: deque = deque(maxlen=history_size)
        self._violations: list[GuardrailViolation] = []

        # Counters
        self._consecutive_count = 0
        self._last_action_hash: Optional[str] = None

    def xǁLoopGuardrailǁ__init____mutmut_2(
        self,
        max_consecutive_repeats: int = 3,
        history_size: int = 101,
        pattern_window: int = 10,
        recovery_callback: Optional[Callable[[GuardrailViolation], str]] = None,
    ):
        """
        Initialize guardrail.

        Args:
            max_consecutive_repeats: Max same action without new artifacts
            history_size: Number of actions to keep in history
            pattern_window: Window size for pattern detection
            recovery_callback: Function to generate recovery message
        """
        self.max_consecutive_repeats = max_consecutive_repeats
        self.history_size = history_size
        self.pattern_window = pattern_window
        self._recovery_callback = recovery_callback or self._default_recovery

        # Action history
        self._history: deque = deque(maxlen=history_size)
        self._violations: list[GuardrailViolation] = []

        # Counters
        self._consecutive_count = 0
        self._last_action_hash: Optional[str] = None

    def xǁLoopGuardrailǁ__init____mutmut_3(
        self,
        max_consecutive_repeats: int = 3,
        history_size: int = 100,
        pattern_window: int = 11,
        recovery_callback: Optional[Callable[[GuardrailViolation], str]] = None,
    ):
        """
        Initialize guardrail.

        Args:
            max_consecutive_repeats: Max same action without new artifacts
            history_size: Number of actions to keep in history
            pattern_window: Window size for pattern detection
            recovery_callback: Function to generate recovery message
        """
        self.max_consecutive_repeats = max_consecutive_repeats
        self.history_size = history_size
        self.pattern_window = pattern_window
        self._recovery_callback = recovery_callback or self._default_recovery

        # Action history
        self._history: deque = deque(maxlen=history_size)
        self._violations: list[GuardrailViolation] = []

        # Counters
        self._consecutive_count = 0
        self._last_action_hash: Optional[str] = None

    def xǁLoopGuardrailǁ__init____mutmut_4(
        self,
        max_consecutive_repeats: int = 3,
        history_size: int = 100,
        pattern_window: int = 10,
        recovery_callback: Optional[Callable[[GuardrailViolation], str]] = None,
    ):
        """
        Initialize guardrail.

        Args:
            max_consecutive_repeats: Max same action without new artifacts
            history_size: Number of actions to keep in history
            pattern_window: Window size for pattern detection
            recovery_callback: Function to generate recovery message
        """
        self.max_consecutive_repeats = None
        self.history_size = history_size
        self.pattern_window = pattern_window
        self._recovery_callback = recovery_callback or self._default_recovery

        # Action history
        self._history: deque = deque(maxlen=history_size)
        self._violations: list[GuardrailViolation] = []

        # Counters
        self._consecutive_count = 0
        self._last_action_hash: Optional[str] = None

    def xǁLoopGuardrailǁ__init____mutmut_5(
        self,
        max_consecutive_repeats: int = 3,
        history_size: int = 100,
        pattern_window: int = 10,
        recovery_callback: Optional[Callable[[GuardrailViolation], str]] = None,
    ):
        """
        Initialize guardrail.

        Args:
            max_consecutive_repeats: Max same action without new artifacts
            history_size: Number of actions to keep in history
            pattern_window: Window size for pattern detection
            recovery_callback: Function to generate recovery message
        """
        self.max_consecutive_repeats = max_consecutive_repeats
        self.history_size = None
        self.pattern_window = pattern_window
        self._recovery_callback = recovery_callback or self._default_recovery

        # Action history
        self._history: deque = deque(maxlen=history_size)
        self._violations: list[GuardrailViolation] = []

        # Counters
        self._consecutive_count = 0
        self._last_action_hash: Optional[str] = None

    def xǁLoopGuardrailǁ__init____mutmut_6(
        self,
        max_consecutive_repeats: int = 3,
        history_size: int = 100,
        pattern_window: int = 10,
        recovery_callback: Optional[Callable[[GuardrailViolation], str]] = None,
    ):
        """
        Initialize guardrail.

        Args:
            max_consecutive_repeats: Max same action without new artifacts
            history_size: Number of actions to keep in history
            pattern_window: Window size for pattern detection
            recovery_callback: Function to generate recovery message
        """
        self.max_consecutive_repeats = max_consecutive_repeats
        self.history_size = history_size
        self.pattern_window = None
        self._recovery_callback = recovery_callback or self._default_recovery

        # Action history
        self._history: deque = deque(maxlen=history_size)
        self._violations: list[GuardrailViolation] = []

        # Counters
        self._consecutive_count = 0
        self._last_action_hash: Optional[str] = None

    def xǁLoopGuardrailǁ__init____mutmut_7(
        self,
        max_consecutive_repeats: int = 3,
        history_size: int = 100,
        pattern_window: int = 10,
        recovery_callback: Optional[Callable[[GuardrailViolation], str]] = None,
    ):
        """
        Initialize guardrail.

        Args:
            max_consecutive_repeats: Max same action without new artifacts
            history_size: Number of actions to keep in history
            pattern_window: Window size for pattern detection
            recovery_callback: Function to generate recovery message
        """
        self.max_consecutive_repeats = max_consecutive_repeats
        self.history_size = history_size
        self.pattern_window = pattern_window
        self._recovery_callback = None

        # Action history
        self._history: deque = deque(maxlen=history_size)
        self._violations: list[GuardrailViolation] = []

        # Counters
        self._consecutive_count = 0
        self._last_action_hash: Optional[str] = None

    def xǁLoopGuardrailǁ__init____mutmut_8(
        self,
        max_consecutive_repeats: int = 3,
        history_size: int = 100,
        pattern_window: int = 10,
        recovery_callback: Optional[Callable[[GuardrailViolation], str]] = None,
    ):
        """
        Initialize guardrail.

        Args:
            max_consecutive_repeats: Max same action without new artifacts
            history_size: Number of actions to keep in history
            pattern_window: Window size for pattern detection
            recovery_callback: Function to generate recovery message
        """
        self.max_consecutive_repeats = max_consecutive_repeats
        self.history_size = history_size
        self.pattern_window = pattern_window
        self._recovery_callback = recovery_callback and self._default_recovery

        # Action history
        self._history: deque = deque(maxlen=history_size)
        self._violations: list[GuardrailViolation] = []

        # Counters
        self._consecutive_count = 0
        self._last_action_hash: Optional[str] = None

    def xǁLoopGuardrailǁ__init____mutmut_9(
        self,
        max_consecutive_repeats: int = 3,
        history_size: int = 100,
        pattern_window: int = 10,
        recovery_callback: Optional[Callable[[GuardrailViolation], str]] = None,
    ):
        """
        Initialize guardrail.

        Args:
            max_consecutive_repeats: Max same action without new artifacts
            history_size: Number of actions to keep in history
            pattern_window: Window size for pattern detection
            recovery_callback: Function to generate recovery message
        """
        self.max_consecutive_repeats = max_consecutive_repeats
        self.history_size = history_size
        self.pattern_window = pattern_window
        self._recovery_callback = recovery_callback or self._default_recovery

        # Action history
        self._history: deque = None
        self._violations: list[GuardrailViolation] = []

        # Counters
        self._consecutive_count = 0
        self._last_action_hash: Optional[str] = None

    def xǁLoopGuardrailǁ__init____mutmut_10(
        self,
        max_consecutive_repeats: int = 3,
        history_size: int = 100,
        pattern_window: int = 10,
        recovery_callback: Optional[Callable[[GuardrailViolation], str]] = None,
    ):
        """
        Initialize guardrail.

        Args:
            max_consecutive_repeats: Max same action without new artifacts
            history_size: Number of actions to keep in history
            pattern_window: Window size for pattern detection
            recovery_callback: Function to generate recovery message
        """
        self.max_consecutive_repeats = max_consecutive_repeats
        self.history_size = history_size
        self.pattern_window = pattern_window
        self._recovery_callback = recovery_callback or self._default_recovery

        # Action history
        self._history: deque = deque(maxlen=None)
        self._violations: list[GuardrailViolation] = []

        # Counters
        self._consecutive_count = 0
        self._last_action_hash: Optional[str] = None

    def xǁLoopGuardrailǁ__init____mutmut_11(
        self,
        max_consecutive_repeats: int = 3,
        history_size: int = 100,
        pattern_window: int = 10,
        recovery_callback: Optional[Callable[[GuardrailViolation], str]] = None,
    ):
        """
        Initialize guardrail.

        Args:
            max_consecutive_repeats: Max same action without new artifacts
            history_size: Number of actions to keep in history
            pattern_window: Window size for pattern detection
            recovery_callback: Function to generate recovery message
        """
        self.max_consecutive_repeats = max_consecutive_repeats
        self.history_size = history_size
        self.pattern_window = pattern_window
        self._recovery_callback = recovery_callback or self._default_recovery

        # Action history
        self._history: deque = deque(maxlen=history_size)
        self._violations: list[GuardrailViolation] = None

        # Counters
        self._consecutive_count = 0
        self._last_action_hash: Optional[str] = None

    def xǁLoopGuardrailǁ__init____mutmut_12(
        self,
        max_consecutive_repeats: int = 3,
        history_size: int = 100,
        pattern_window: int = 10,
        recovery_callback: Optional[Callable[[GuardrailViolation], str]] = None,
    ):
        """
        Initialize guardrail.

        Args:
            max_consecutive_repeats: Max same action without new artifacts
            history_size: Number of actions to keep in history
            pattern_window: Window size for pattern detection
            recovery_callback: Function to generate recovery message
        """
        self.max_consecutive_repeats = max_consecutive_repeats
        self.history_size = history_size
        self.pattern_window = pattern_window
        self._recovery_callback = recovery_callback or self._default_recovery

        # Action history
        self._history: deque = deque(maxlen=history_size)
        self._violations: list[GuardrailViolation] = []

        # Counters
        self._consecutive_count = None
        self._last_action_hash: Optional[str] = None

    def xǁLoopGuardrailǁ__init____mutmut_13(
        self,
        max_consecutive_repeats: int = 3,
        history_size: int = 100,
        pattern_window: int = 10,
        recovery_callback: Optional[Callable[[GuardrailViolation], str]] = None,
    ):
        """
        Initialize guardrail.

        Args:
            max_consecutive_repeats: Max same action without new artifacts
            history_size: Number of actions to keep in history
            pattern_window: Window size for pattern detection
            recovery_callback: Function to generate recovery message
        """
        self.max_consecutive_repeats = max_consecutive_repeats
        self.history_size = history_size
        self.pattern_window = pattern_window
        self._recovery_callback = recovery_callback or self._default_recovery

        # Action history
        self._history: deque = deque(maxlen=history_size)
        self._violations: list[GuardrailViolation] = []

        # Counters
        self._consecutive_count = 1
        self._last_action_hash: Optional[str] = None

    def xǁLoopGuardrailǁ__init____mutmut_14(
        self,
        max_consecutive_repeats: int = 3,
        history_size: int = 100,
        pattern_window: int = 10,
        recovery_callback: Optional[Callable[[GuardrailViolation], str]] = None,
    ):
        """
        Initialize guardrail.

        Args:
            max_consecutive_repeats: Max same action without new artifacts
            history_size: Number of actions to keep in history
            pattern_window: Window size for pattern detection
            recovery_callback: Function to generate recovery message
        """
        self.max_consecutive_repeats = max_consecutive_repeats
        self.history_size = history_size
        self.pattern_window = pattern_window
        self._recovery_callback = recovery_callback or self._default_recovery

        # Action history
        self._history: deque = deque(maxlen=history_size)
        self._violations: list[GuardrailViolation] = []

        # Counters
        self._consecutive_count = 0
        self._last_action_hash: Optional[str] = ""
    
    xǁLoopGuardrailǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLoopGuardrailǁ__init____mutmut_1': xǁLoopGuardrailǁ__init____mutmut_1, 
        'xǁLoopGuardrailǁ__init____mutmut_2': xǁLoopGuardrailǁ__init____mutmut_2, 
        'xǁLoopGuardrailǁ__init____mutmut_3': xǁLoopGuardrailǁ__init____mutmut_3, 
        'xǁLoopGuardrailǁ__init____mutmut_4': xǁLoopGuardrailǁ__init____mutmut_4, 
        'xǁLoopGuardrailǁ__init____mutmut_5': xǁLoopGuardrailǁ__init____mutmut_5, 
        'xǁLoopGuardrailǁ__init____mutmut_6': xǁLoopGuardrailǁ__init____mutmut_6, 
        'xǁLoopGuardrailǁ__init____mutmut_7': xǁLoopGuardrailǁ__init____mutmut_7, 
        'xǁLoopGuardrailǁ__init____mutmut_8': xǁLoopGuardrailǁ__init____mutmut_8, 
        'xǁLoopGuardrailǁ__init____mutmut_9': xǁLoopGuardrailǁ__init____mutmut_9, 
        'xǁLoopGuardrailǁ__init____mutmut_10': xǁLoopGuardrailǁ__init____mutmut_10, 
        'xǁLoopGuardrailǁ__init____mutmut_11': xǁLoopGuardrailǁ__init____mutmut_11, 
        'xǁLoopGuardrailǁ__init____mutmut_12': xǁLoopGuardrailǁ__init____mutmut_12, 
        'xǁLoopGuardrailǁ__init____mutmut_13': xǁLoopGuardrailǁ__init____mutmut_13, 
        'xǁLoopGuardrailǁ__init____mutmut_14': xǁLoopGuardrailǁ__init____mutmut_14
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLoopGuardrailǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁLoopGuardrailǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁLoopGuardrailǁ__init____mutmut_orig)
    xǁLoopGuardrailǁ__init____mutmut_orig.__name__ = 'xǁLoopGuardrailǁ__init__'

    def xǁLoopGuardrailǁrecord_action__mutmut_orig(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_1(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = True,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_2(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = None
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_3(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(None, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_4(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, None, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_5(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, None)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_6(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_7(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_8(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, )
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_9(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_10(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(None) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_11(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_12(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(None) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_13(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = None

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_14(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=None,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_15(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=None,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_16(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=None,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_17(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=None,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_18(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=None,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_19(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=None,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_20(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_21(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_22(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_23(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_24(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_25(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_26(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(None)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_27(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash or not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_28(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash != self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_29(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_30(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count = 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_31(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count -= 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_32(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 2
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_33(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = None
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_34(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 2 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_35(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_36(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 1
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_37(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = None

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_38(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count > self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_39(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = None
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_40(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type=None,
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_41(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=None,
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_42(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=None,
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_43(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=None,
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_44(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_45(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_46(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_47(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_48(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="XXconsecutive_repeatXX",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_49(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="CONSECUTIVE_REPEAT",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_50(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(None)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_51(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[+5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_52(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-6:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_53(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(None)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_54(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = None  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_55(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 1  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_56(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = None
        if pattern_violation:
            self._violations.append(pattern_violation)
            return pattern_violation

        return None

    def xǁLoopGuardrailǁrecord_action__mutmut_57(
        self,
        action_type: str,
        tool_name: Optional[str] = None,
        parameters: Optional[dict] = None,
        produced_artifacts: bool = False,
        result: Optional[Any] = None,
    ) -> Optional[GuardrailViolation]:
        """
        Record an agent action and check for violations.

        Args:
            action_type: Type of action taken
            tool_name: Name of tool if tool call
            parameters: Action parameters
            produced_artifacts: Whether action produced new artifacts
            result: Action result for hashing

        Returns:
            GuardrailViolation if violated, None otherwise
        """
        # Create action record
        action_hash = self._hash_action(action_type, tool_name, parameters)
        params_hash = self._hash_dict(parameters) if parameters else None
        result_hash = self._hash_result(result) if result else None

        record = ActionRecord(
            action_type=action_type,
            action_hash=action_hash,
            tool_name=tool_name,
            parameters_hash=params_hash,
            produced_artifacts=produced_artifacts,
            result_hash=result_hash,
        )

        self._history.append(record)

        # Check for consecutive repeats without artifacts
        if action_hash == self._last_action_hash and not produced_artifacts:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 1 if not produced_artifacts else 0
            self._last_action_hash = action_hash

        # Check violation
        if self._consecutive_count >= self.max_consecutive_repeats:
            violation = GuardrailViolation(
                violation_type="consecutive_repeat",
                message=f"Action repeated {self._consecutive_count} times without new artifacts",
                action_history=[r.action_type for r in list(self._history)[-5:]],
                recommended_action=self._recovery_callback(None),
            )
            self._violations.append(violation)
            self._consecutive_count = 0  # Reset after violation
            return violation

        # Check for pattern loops
        pattern_violation = self._check_pattern_loop()
        if pattern_violation:
            self._violations.append(None)
            return pattern_violation

        return None
    
    xǁLoopGuardrailǁrecord_action__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLoopGuardrailǁrecord_action__mutmut_1': xǁLoopGuardrailǁrecord_action__mutmut_1, 
        'xǁLoopGuardrailǁrecord_action__mutmut_2': xǁLoopGuardrailǁrecord_action__mutmut_2, 
        'xǁLoopGuardrailǁrecord_action__mutmut_3': xǁLoopGuardrailǁrecord_action__mutmut_3, 
        'xǁLoopGuardrailǁrecord_action__mutmut_4': xǁLoopGuardrailǁrecord_action__mutmut_4, 
        'xǁLoopGuardrailǁrecord_action__mutmut_5': xǁLoopGuardrailǁrecord_action__mutmut_5, 
        'xǁLoopGuardrailǁrecord_action__mutmut_6': xǁLoopGuardrailǁrecord_action__mutmut_6, 
        'xǁLoopGuardrailǁrecord_action__mutmut_7': xǁLoopGuardrailǁrecord_action__mutmut_7, 
        'xǁLoopGuardrailǁrecord_action__mutmut_8': xǁLoopGuardrailǁrecord_action__mutmut_8, 
        'xǁLoopGuardrailǁrecord_action__mutmut_9': xǁLoopGuardrailǁrecord_action__mutmut_9, 
        'xǁLoopGuardrailǁrecord_action__mutmut_10': xǁLoopGuardrailǁrecord_action__mutmut_10, 
        'xǁLoopGuardrailǁrecord_action__mutmut_11': xǁLoopGuardrailǁrecord_action__mutmut_11, 
        'xǁLoopGuardrailǁrecord_action__mutmut_12': xǁLoopGuardrailǁrecord_action__mutmut_12, 
        'xǁLoopGuardrailǁrecord_action__mutmut_13': xǁLoopGuardrailǁrecord_action__mutmut_13, 
        'xǁLoopGuardrailǁrecord_action__mutmut_14': xǁLoopGuardrailǁrecord_action__mutmut_14, 
        'xǁLoopGuardrailǁrecord_action__mutmut_15': xǁLoopGuardrailǁrecord_action__mutmut_15, 
        'xǁLoopGuardrailǁrecord_action__mutmut_16': xǁLoopGuardrailǁrecord_action__mutmut_16, 
        'xǁLoopGuardrailǁrecord_action__mutmut_17': xǁLoopGuardrailǁrecord_action__mutmut_17, 
        'xǁLoopGuardrailǁrecord_action__mutmut_18': xǁLoopGuardrailǁrecord_action__mutmut_18, 
        'xǁLoopGuardrailǁrecord_action__mutmut_19': xǁLoopGuardrailǁrecord_action__mutmut_19, 
        'xǁLoopGuardrailǁrecord_action__mutmut_20': xǁLoopGuardrailǁrecord_action__mutmut_20, 
        'xǁLoopGuardrailǁrecord_action__mutmut_21': xǁLoopGuardrailǁrecord_action__mutmut_21, 
        'xǁLoopGuardrailǁrecord_action__mutmut_22': xǁLoopGuardrailǁrecord_action__mutmut_22, 
        'xǁLoopGuardrailǁrecord_action__mutmut_23': xǁLoopGuardrailǁrecord_action__mutmut_23, 
        'xǁLoopGuardrailǁrecord_action__mutmut_24': xǁLoopGuardrailǁrecord_action__mutmut_24, 
        'xǁLoopGuardrailǁrecord_action__mutmut_25': xǁLoopGuardrailǁrecord_action__mutmut_25, 
        'xǁLoopGuardrailǁrecord_action__mutmut_26': xǁLoopGuardrailǁrecord_action__mutmut_26, 
        'xǁLoopGuardrailǁrecord_action__mutmut_27': xǁLoopGuardrailǁrecord_action__mutmut_27, 
        'xǁLoopGuardrailǁrecord_action__mutmut_28': xǁLoopGuardrailǁrecord_action__mutmut_28, 
        'xǁLoopGuardrailǁrecord_action__mutmut_29': xǁLoopGuardrailǁrecord_action__mutmut_29, 
        'xǁLoopGuardrailǁrecord_action__mutmut_30': xǁLoopGuardrailǁrecord_action__mutmut_30, 
        'xǁLoopGuardrailǁrecord_action__mutmut_31': xǁLoopGuardrailǁrecord_action__mutmut_31, 
        'xǁLoopGuardrailǁrecord_action__mutmut_32': xǁLoopGuardrailǁrecord_action__mutmut_32, 
        'xǁLoopGuardrailǁrecord_action__mutmut_33': xǁLoopGuardrailǁrecord_action__mutmut_33, 
        'xǁLoopGuardrailǁrecord_action__mutmut_34': xǁLoopGuardrailǁrecord_action__mutmut_34, 
        'xǁLoopGuardrailǁrecord_action__mutmut_35': xǁLoopGuardrailǁrecord_action__mutmut_35, 
        'xǁLoopGuardrailǁrecord_action__mutmut_36': xǁLoopGuardrailǁrecord_action__mutmut_36, 
        'xǁLoopGuardrailǁrecord_action__mutmut_37': xǁLoopGuardrailǁrecord_action__mutmut_37, 
        'xǁLoopGuardrailǁrecord_action__mutmut_38': xǁLoopGuardrailǁrecord_action__mutmut_38, 
        'xǁLoopGuardrailǁrecord_action__mutmut_39': xǁLoopGuardrailǁrecord_action__mutmut_39, 
        'xǁLoopGuardrailǁrecord_action__mutmut_40': xǁLoopGuardrailǁrecord_action__mutmut_40, 
        'xǁLoopGuardrailǁrecord_action__mutmut_41': xǁLoopGuardrailǁrecord_action__mutmut_41, 
        'xǁLoopGuardrailǁrecord_action__mutmut_42': xǁLoopGuardrailǁrecord_action__mutmut_42, 
        'xǁLoopGuardrailǁrecord_action__mutmut_43': xǁLoopGuardrailǁrecord_action__mutmut_43, 
        'xǁLoopGuardrailǁrecord_action__mutmut_44': xǁLoopGuardrailǁrecord_action__mutmut_44, 
        'xǁLoopGuardrailǁrecord_action__mutmut_45': xǁLoopGuardrailǁrecord_action__mutmut_45, 
        'xǁLoopGuardrailǁrecord_action__mutmut_46': xǁLoopGuardrailǁrecord_action__mutmut_46, 
        'xǁLoopGuardrailǁrecord_action__mutmut_47': xǁLoopGuardrailǁrecord_action__mutmut_47, 
        'xǁLoopGuardrailǁrecord_action__mutmut_48': xǁLoopGuardrailǁrecord_action__mutmut_48, 
        'xǁLoopGuardrailǁrecord_action__mutmut_49': xǁLoopGuardrailǁrecord_action__mutmut_49, 
        'xǁLoopGuardrailǁrecord_action__mutmut_50': xǁLoopGuardrailǁrecord_action__mutmut_50, 
        'xǁLoopGuardrailǁrecord_action__mutmut_51': xǁLoopGuardrailǁrecord_action__mutmut_51, 
        'xǁLoopGuardrailǁrecord_action__mutmut_52': xǁLoopGuardrailǁrecord_action__mutmut_52, 
        'xǁLoopGuardrailǁrecord_action__mutmut_53': xǁLoopGuardrailǁrecord_action__mutmut_53, 
        'xǁLoopGuardrailǁrecord_action__mutmut_54': xǁLoopGuardrailǁrecord_action__mutmut_54, 
        'xǁLoopGuardrailǁrecord_action__mutmut_55': xǁLoopGuardrailǁrecord_action__mutmut_55, 
        'xǁLoopGuardrailǁrecord_action__mutmut_56': xǁLoopGuardrailǁrecord_action__mutmut_56, 
        'xǁLoopGuardrailǁrecord_action__mutmut_57': xǁLoopGuardrailǁrecord_action__mutmut_57
    }
    
    def record_action(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLoopGuardrailǁrecord_action__mutmut_orig"), object.__getattribute__(self, "xǁLoopGuardrailǁrecord_action__mutmut_mutants"), args, kwargs, self)
        return result 
    
    record_action.__signature__ = _mutmut_signature(xǁLoopGuardrailǁrecord_action__mutmut_orig)
    xǁLoopGuardrailǁrecord_action__mutmut_orig.__name__ = 'xǁLoopGuardrailǁrecord_action'

    def xǁLoopGuardrailǁcheck_before_action__mutmut_orig(
        self, action_type: str, tool_name: Optional[str] = None, parameters: Optional[dict] = None
    ) -> Optional[str]:
        """
        Pre-check if action would violate guardrails.

        Returns recovery message if would violate, None if safe.
        """
        action_hash = self._hash_action(action_type, tool_name, parameters)

        # Check if this would be a repeat
        if action_hash == self._last_action_hash:
            predicted_count = self._consecutive_count + 1
            if predicted_count >= self.max_consecutive_repeats:
                # Preemptively suggest alternative
                return self._generate_alternative_suggestion(action_type, tool_name)

        return None

    def xǁLoopGuardrailǁcheck_before_action__mutmut_1(
        self, action_type: str, tool_name: Optional[str] = None, parameters: Optional[dict] = None
    ) -> Optional[str]:
        """
        Pre-check if action would violate guardrails.

        Returns recovery message if would violate, None if safe.
        """
        action_hash = None

        # Check if this would be a repeat
        if action_hash == self._last_action_hash:
            predicted_count = self._consecutive_count + 1
            if predicted_count >= self.max_consecutive_repeats:
                # Preemptively suggest alternative
                return self._generate_alternative_suggestion(action_type, tool_name)

        return None

    def xǁLoopGuardrailǁcheck_before_action__mutmut_2(
        self, action_type: str, tool_name: Optional[str] = None, parameters: Optional[dict] = None
    ) -> Optional[str]:
        """
        Pre-check if action would violate guardrails.

        Returns recovery message if would violate, None if safe.
        """
        action_hash = self._hash_action(None, tool_name, parameters)

        # Check if this would be a repeat
        if action_hash == self._last_action_hash:
            predicted_count = self._consecutive_count + 1
            if predicted_count >= self.max_consecutive_repeats:
                # Preemptively suggest alternative
                return self._generate_alternative_suggestion(action_type, tool_name)

        return None

    def xǁLoopGuardrailǁcheck_before_action__mutmut_3(
        self, action_type: str, tool_name: Optional[str] = None, parameters: Optional[dict] = None
    ) -> Optional[str]:
        """
        Pre-check if action would violate guardrails.

        Returns recovery message if would violate, None if safe.
        """
        action_hash = self._hash_action(action_type, None, parameters)

        # Check if this would be a repeat
        if action_hash == self._last_action_hash:
            predicted_count = self._consecutive_count + 1
            if predicted_count >= self.max_consecutive_repeats:
                # Preemptively suggest alternative
                return self._generate_alternative_suggestion(action_type, tool_name)

        return None

    def xǁLoopGuardrailǁcheck_before_action__mutmut_4(
        self, action_type: str, tool_name: Optional[str] = None, parameters: Optional[dict] = None
    ) -> Optional[str]:
        """
        Pre-check if action would violate guardrails.

        Returns recovery message if would violate, None if safe.
        """
        action_hash = self._hash_action(action_type, tool_name, None)

        # Check if this would be a repeat
        if action_hash == self._last_action_hash:
            predicted_count = self._consecutive_count + 1
            if predicted_count >= self.max_consecutive_repeats:
                # Preemptively suggest alternative
                return self._generate_alternative_suggestion(action_type, tool_name)

        return None

    def xǁLoopGuardrailǁcheck_before_action__mutmut_5(
        self, action_type: str, tool_name: Optional[str] = None, parameters: Optional[dict] = None
    ) -> Optional[str]:
        """
        Pre-check if action would violate guardrails.

        Returns recovery message if would violate, None if safe.
        """
        action_hash = self._hash_action(tool_name, parameters)

        # Check if this would be a repeat
        if action_hash == self._last_action_hash:
            predicted_count = self._consecutive_count + 1
            if predicted_count >= self.max_consecutive_repeats:
                # Preemptively suggest alternative
                return self._generate_alternative_suggestion(action_type, tool_name)

        return None

    def xǁLoopGuardrailǁcheck_before_action__mutmut_6(
        self, action_type: str, tool_name: Optional[str] = None, parameters: Optional[dict] = None
    ) -> Optional[str]:
        """
        Pre-check if action would violate guardrails.

        Returns recovery message if would violate, None if safe.
        """
        action_hash = self._hash_action(action_type, parameters)

        # Check if this would be a repeat
        if action_hash == self._last_action_hash:
            predicted_count = self._consecutive_count + 1
            if predicted_count >= self.max_consecutive_repeats:
                # Preemptively suggest alternative
                return self._generate_alternative_suggestion(action_type, tool_name)

        return None

    def xǁLoopGuardrailǁcheck_before_action__mutmut_7(
        self, action_type: str, tool_name: Optional[str] = None, parameters: Optional[dict] = None
    ) -> Optional[str]:
        """
        Pre-check if action would violate guardrails.

        Returns recovery message if would violate, None if safe.
        """
        action_hash = self._hash_action(action_type, tool_name, )

        # Check if this would be a repeat
        if action_hash == self._last_action_hash:
            predicted_count = self._consecutive_count + 1
            if predicted_count >= self.max_consecutive_repeats:
                # Preemptively suggest alternative
                return self._generate_alternative_suggestion(action_type, tool_name)

        return None

    def xǁLoopGuardrailǁcheck_before_action__mutmut_8(
        self, action_type: str, tool_name: Optional[str] = None, parameters: Optional[dict] = None
    ) -> Optional[str]:
        """
        Pre-check if action would violate guardrails.

        Returns recovery message if would violate, None if safe.
        """
        action_hash = self._hash_action(action_type, tool_name, parameters)

        # Check if this would be a repeat
        if action_hash != self._last_action_hash:
            predicted_count = self._consecutive_count + 1
            if predicted_count >= self.max_consecutive_repeats:
                # Preemptively suggest alternative
                return self._generate_alternative_suggestion(action_type, tool_name)

        return None

    def xǁLoopGuardrailǁcheck_before_action__mutmut_9(
        self, action_type: str, tool_name: Optional[str] = None, parameters: Optional[dict] = None
    ) -> Optional[str]:
        """
        Pre-check if action would violate guardrails.

        Returns recovery message if would violate, None if safe.
        """
        action_hash = self._hash_action(action_type, tool_name, parameters)

        # Check if this would be a repeat
        if action_hash == self._last_action_hash:
            predicted_count = None
            if predicted_count >= self.max_consecutive_repeats:
                # Preemptively suggest alternative
                return self._generate_alternative_suggestion(action_type, tool_name)

        return None

    def xǁLoopGuardrailǁcheck_before_action__mutmut_10(
        self, action_type: str, tool_name: Optional[str] = None, parameters: Optional[dict] = None
    ) -> Optional[str]:
        """
        Pre-check if action would violate guardrails.

        Returns recovery message if would violate, None if safe.
        """
        action_hash = self._hash_action(action_type, tool_name, parameters)

        # Check if this would be a repeat
        if action_hash == self._last_action_hash:
            predicted_count = self._consecutive_count - 1
            if predicted_count >= self.max_consecutive_repeats:
                # Preemptively suggest alternative
                return self._generate_alternative_suggestion(action_type, tool_name)

        return None

    def xǁLoopGuardrailǁcheck_before_action__mutmut_11(
        self, action_type: str, tool_name: Optional[str] = None, parameters: Optional[dict] = None
    ) -> Optional[str]:
        """
        Pre-check if action would violate guardrails.

        Returns recovery message if would violate, None if safe.
        """
        action_hash = self._hash_action(action_type, tool_name, parameters)

        # Check if this would be a repeat
        if action_hash == self._last_action_hash:
            predicted_count = self._consecutive_count + 2
            if predicted_count >= self.max_consecutive_repeats:
                # Preemptively suggest alternative
                return self._generate_alternative_suggestion(action_type, tool_name)

        return None

    def xǁLoopGuardrailǁcheck_before_action__mutmut_12(
        self, action_type: str, tool_name: Optional[str] = None, parameters: Optional[dict] = None
    ) -> Optional[str]:
        """
        Pre-check if action would violate guardrails.

        Returns recovery message if would violate, None if safe.
        """
        action_hash = self._hash_action(action_type, tool_name, parameters)

        # Check if this would be a repeat
        if action_hash == self._last_action_hash:
            predicted_count = self._consecutive_count + 1
            if predicted_count > self.max_consecutive_repeats:
                # Preemptively suggest alternative
                return self._generate_alternative_suggestion(action_type, tool_name)

        return None

    def xǁLoopGuardrailǁcheck_before_action__mutmut_13(
        self, action_type: str, tool_name: Optional[str] = None, parameters: Optional[dict] = None
    ) -> Optional[str]:
        """
        Pre-check if action would violate guardrails.

        Returns recovery message if would violate, None if safe.
        """
        action_hash = self._hash_action(action_type, tool_name, parameters)

        # Check if this would be a repeat
        if action_hash == self._last_action_hash:
            predicted_count = self._consecutive_count + 1
            if predicted_count >= self.max_consecutive_repeats:
                # Preemptively suggest alternative
                return self._generate_alternative_suggestion(None, tool_name)

        return None

    def xǁLoopGuardrailǁcheck_before_action__mutmut_14(
        self, action_type: str, tool_name: Optional[str] = None, parameters: Optional[dict] = None
    ) -> Optional[str]:
        """
        Pre-check if action would violate guardrails.

        Returns recovery message if would violate, None if safe.
        """
        action_hash = self._hash_action(action_type, tool_name, parameters)

        # Check if this would be a repeat
        if action_hash == self._last_action_hash:
            predicted_count = self._consecutive_count + 1
            if predicted_count >= self.max_consecutive_repeats:
                # Preemptively suggest alternative
                return self._generate_alternative_suggestion(action_type, None)

        return None

    def xǁLoopGuardrailǁcheck_before_action__mutmut_15(
        self, action_type: str, tool_name: Optional[str] = None, parameters: Optional[dict] = None
    ) -> Optional[str]:
        """
        Pre-check if action would violate guardrails.

        Returns recovery message if would violate, None if safe.
        """
        action_hash = self._hash_action(action_type, tool_name, parameters)

        # Check if this would be a repeat
        if action_hash == self._last_action_hash:
            predicted_count = self._consecutive_count + 1
            if predicted_count >= self.max_consecutive_repeats:
                # Preemptively suggest alternative
                return self._generate_alternative_suggestion(tool_name)

        return None

    def xǁLoopGuardrailǁcheck_before_action__mutmut_16(
        self, action_type: str, tool_name: Optional[str] = None, parameters: Optional[dict] = None
    ) -> Optional[str]:
        """
        Pre-check if action would violate guardrails.

        Returns recovery message if would violate, None if safe.
        """
        action_hash = self._hash_action(action_type, tool_name, parameters)

        # Check if this would be a repeat
        if action_hash == self._last_action_hash:
            predicted_count = self._consecutive_count + 1
            if predicted_count >= self.max_consecutive_repeats:
                # Preemptively suggest alternative
                return self._generate_alternative_suggestion(action_type, )

        return None
    
    xǁLoopGuardrailǁcheck_before_action__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLoopGuardrailǁcheck_before_action__mutmut_1': xǁLoopGuardrailǁcheck_before_action__mutmut_1, 
        'xǁLoopGuardrailǁcheck_before_action__mutmut_2': xǁLoopGuardrailǁcheck_before_action__mutmut_2, 
        'xǁLoopGuardrailǁcheck_before_action__mutmut_3': xǁLoopGuardrailǁcheck_before_action__mutmut_3, 
        'xǁLoopGuardrailǁcheck_before_action__mutmut_4': xǁLoopGuardrailǁcheck_before_action__mutmut_4, 
        'xǁLoopGuardrailǁcheck_before_action__mutmut_5': xǁLoopGuardrailǁcheck_before_action__mutmut_5, 
        'xǁLoopGuardrailǁcheck_before_action__mutmut_6': xǁLoopGuardrailǁcheck_before_action__mutmut_6, 
        'xǁLoopGuardrailǁcheck_before_action__mutmut_7': xǁLoopGuardrailǁcheck_before_action__mutmut_7, 
        'xǁLoopGuardrailǁcheck_before_action__mutmut_8': xǁLoopGuardrailǁcheck_before_action__mutmut_8, 
        'xǁLoopGuardrailǁcheck_before_action__mutmut_9': xǁLoopGuardrailǁcheck_before_action__mutmut_9, 
        'xǁLoopGuardrailǁcheck_before_action__mutmut_10': xǁLoopGuardrailǁcheck_before_action__mutmut_10, 
        'xǁLoopGuardrailǁcheck_before_action__mutmut_11': xǁLoopGuardrailǁcheck_before_action__mutmut_11, 
        'xǁLoopGuardrailǁcheck_before_action__mutmut_12': xǁLoopGuardrailǁcheck_before_action__mutmut_12, 
        'xǁLoopGuardrailǁcheck_before_action__mutmut_13': xǁLoopGuardrailǁcheck_before_action__mutmut_13, 
        'xǁLoopGuardrailǁcheck_before_action__mutmut_14': xǁLoopGuardrailǁcheck_before_action__mutmut_14, 
        'xǁLoopGuardrailǁcheck_before_action__mutmut_15': xǁLoopGuardrailǁcheck_before_action__mutmut_15, 
        'xǁLoopGuardrailǁcheck_before_action__mutmut_16': xǁLoopGuardrailǁcheck_before_action__mutmut_16
    }
    
    def check_before_action(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLoopGuardrailǁcheck_before_action__mutmut_orig"), object.__getattribute__(self, "xǁLoopGuardrailǁcheck_before_action__mutmut_mutants"), args, kwargs, self)
        return result 
    
    check_before_action.__signature__ = _mutmut_signature(xǁLoopGuardrailǁcheck_before_action__mutmut_orig)
    xǁLoopGuardrailǁcheck_before_action__mutmut_orig.__name__ = 'xǁLoopGuardrailǁcheck_before_action'

    def xǁLoopGuardrailǁget_recovery_message__mutmut_orig(self) -> str:
        """Get recovery message for current state."""
        if self._violations:
            return self._recovery_callback(self._violations[-1])
        return self._default_recovery(None)

    def xǁLoopGuardrailǁget_recovery_message__mutmut_1(self) -> str:
        """Get recovery message for current state."""
        if self._violations:
            return self._recovery_callback(None)
        return self._default_recovery(None)

    def xǁLoopGuardrailǁget_recovery_message__mutmut_2(self) -> str:
        """Get recovery message for current state."""
        if self._violations:
            return self._recovery_callback(self._violations[+1])
        return self._default_recovery(None)

    def xǁLoopGuardrailǁget_recovery_message__mutmut_3(self) -> str:
        """Get recovery message for current state."""
        if self._violations:
            return self._recovery_callback(self._violations[-2])
        return self._default_recovery(None)
    
    xǁLoopGuardrailǁget_recovery_message__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLoopGuardrailǁget_recovery_message__mutmut_1': xǁLoopGuardrailǁget_recovery_message__mutmut_1, 
        'xǁLoopGuardrailǁget_recovery_message__mutmut_2': xǁLoopGuardrailǁget_recovery_message__mutmut_2, 
        'xǁLoopGuardrailǁget_recovery_message__mutmut_3': xǁLoopGuardrailǁget_recovery_message__mutmut_3
    }
    
    def get_recovery_message(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLoopGuardrailǁget_recovery_message__mutmut_orig"), object.__getattribute__(self, "xǁLoopGuardrailǁget_recovery_message__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_recovery_message.__signature__ = _mutmut_signature(xǁLoopGuardrailǁget_recovery_message__mutmut_orig)
    xǁLoopGuardrailǁget_recovery_message__mutmut_orig.__name__ = 'xǁLoopGuardrailǁget_recovery_message'

    def xǁLoopGuardrailǁget_metrics__mutmut_orig(self) -> dict:
        """Get guardrail metrics."""
        return {
            "actions_recorded": len(self._history),
            "violations_count": len(self._violations),
            "current_consecutive": self._consecutive_count,
            "violation_types": self._count_violation_types(),
        }

    def xǁLoopGuardrailǁget_metrics__mutmut_1(self) -> dict:
        """Get guardrail metrics."""
        return {
            "XXactions_recordedXX": len(self._history),
            "violations_count": len(self._violations),
            "current_consecutive": self._consecutive_count,
            "violation_types": self._count_violation_types(),
        }

    def xǁLoopGuardrailǁget_metrics__mutmut_2(self) -> dict:
        """Get guardrail metrics."""
        return {
            "ACTIONS_RECORDED": len(self._history),
            "violations_count": len(self._violations),
            "current_consecutive": self._consecutive_count,
            "violation_types": self._count_violation_types(),
        }

    def xǁLoopGuardrailǁget_metrics__mutmut_3(self) -> dict:
        """Get guardrail metrics."""
        return {
            "actions_recorded": len(self._history),
            "XXviolations_countXX": len(self._violations),
            "current_consecutive": self._consecutive_count,
            "violation_types": self._count_violation_types(),
        }

    def xǁLoopGuardrailǁget_metrics__mutmut_4(self) -> dict:
        """Get guardrail metrics."""
        return {
            "actions_recorded": len(self._history),
            "VIOLATIONS_COUNT": len(self._violations),
            "current_consecutive": self._consecutive_count,
            "violation_types": self._count_violation_types(),
        }

    def xǁLoopGuardrailǁget_metrics__mutmut_5(self) -> dict:
        """Get guardrail metrics."""
        return {
            "actions_recorded": len(self._history),
            "violations_count": len(self._violations),
            "XXcurrent_consecutiveXX": self._consecutive_count,
            "violation_types": self._count_violation_types(),
        }

    def xǁLoopGuardrailǁget_metrics__mutmut_6(self) -> dict:
        """Get guardrail metrics."""
        return {
            "actions_recorded": len(self._history),
            "violations_count": len(self._violations),
            "CURRENT_CONSECUTIVE": self._consecutive_count,
            "violation_types": self._count_violation_types(),
        }

    def xǁLoopGuardrailǁget_metrics__mutmut_7(self) -> dict:
        """Get guardrail metrics."""
        return {
            "actions_recorded": len(self._history),
            "violations_count": len(self._violations),
            "current_consecutive": self._consecutive_count,
            "XXviolation_typesXX": self._count_violation_types(),
        }

    def xǁLoopGuardrailǁget_metrics__mutmut_8(self) -> dict:
        """Get guardrail metrics."""
        return {
            "actions_recorded": len(self._history),
            "violations_count": len(self._violations),
            "current_consecutive": self._consecutive_count,
            "VIOLATION_TYPES": self._count_violation_types(),
        }
    
    xǁLoopGuardrailǁget_metrics__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLoopGuardrailǁget_metrics__mutmut_1': xǁLoopGuardrailǁget_metrics__mutmut_1, 
        'xǁLoopGuardrailǁget_metrics__mutmut_2': xǁLoopGuardrailǁget_metrics__mutmut_2, 
        'xǁLoopGuardrailǁget_metrics__mutmut_3': xǁLoopGuardrailǁget_metrics__mutmut_3, 
        'xǁLoopGuardrailǁget_metrics__mutmut_4': xǁLoopGuardrailǁget_metrics__mutmut_4, 
        'xǁLoopGuardrailǁget_metrics__mutmut_5': xǁLoopGuardrailǁget_metrics__mutmut_5, 
        'xǁLoopGuardrailǁget_metrics__mutmut_6': xǁLoopGuardrailǁget_metrics__mutmut_6, 
        'xǁLoopGuardrailǁget_metrics__mutmut_7': xǁLoopGuardrailǁget_metrics__mutmut_7, 
        'xǁLoopGuardrailǁget_metrics__mutmut_8': xǁLoopGuardrailǁget_metrics__mutmut_8
    }
    
    def get_metrics(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLoopGuardrailǁget_metrics__mutmut_orig"), object.__getattribute__(self, "xǁLoopGuardrailǁget_metrics__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_metrics.__signature__ = _mutmut_signature(xǁLoopGuardrailǁget_metrics__mutmut_orig)
    xǁLoopGuardrailǁget_metrics__mutmut_orig.__name__ = 'xǁLoopGuardrailǁget_metrics'

    def xǁLoopGuardrailǁreset__mutmut_orig(self):
        """Reset guardrail state."""
        self._history.clear()
        self._violations.clear()
        self._consecutive_count = 0
        self._last_action_hash = None

    def xǁLoopGuardrailǁreset__mutmut_1(self):
        """Reset guardrail state."""
        self._history.clear()
        self._violations.clear()
        self._consecutive_count = None
        self._last_action_hash = None

    def xǁLoopGuardrailǁreset__mutmut_2(self):
        """Reset guardrail state."""
        self._history.clear()
        self._violations.clear()
        self._consecutive_count = 1
        self._last_action_hash = None

    def xǁLoopGuardrailǁreset__mutmut_3(self):
        """Reset guardrail state."""
        self._history.clear()
        self._violations.clear()
        self._consecutive_count = 0
        self._last_action_hash = ""
    
    xǁLoopGuardrailǁreset__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLoopGuardrailǁreset__mutmut_1': xǁLoopGuardrailǁreset__mutmut_1, 
        'xǁLoopGuardrailǁreset__mutmut_2': xǁLoopGuardrailǁreset__mutmut_2, 
        'xǁLoopGuardrailǁreset__mutmut_3': xǁLoopGuardrailǁreset__mutmut_3
    }
    
    def reset(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLoopGuardrailǁreset__mutmut_orig"), object.__getattribute__(self, "xǁLoopGuardrailǁreset__mutmut_mutants"), args, kwargs, self)
        return result 
    
    reset.__signature__ = _mutmut_signature(xǁLoopGuardrailǁreset__mutmut_orig)
    xǁLoopGuardrailǁreset__mutmut_orig.__name__ = 'xǁLoopGuardrailǁreset'

    def xǁLoopGuardrailǁ_hash_action__mutmut_orig(
        self, action_type: str, tool_name: Optional[str], parameters: Optional[dict]
    ) -> str:
        """Generate hash for action identification."""
        content = f"{action_type}:{tool_name or ''}"
        if parameters:
            # Sort keys for consistent hashing
            content += ":" + json.dumps(parameters, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_action__mutmut_1(
        self, action_type: str, tool_name: Optional[str], parameters: Optional[dict]
    ) -> str:
        """Generate hash for action identification."""
        content = None
        if parameters:
            # Sort keys for consistent hashing
            content += ":" + json.dumps(parameters, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_action__mutmut_2(
        self, action_type: str, tool_name: Optional[str], parameters: Optional[dict]
    ) -> str:
        """Generate hash for action identification."""
        content = f"{action_type}:{tool_name and ''}"
        if parameters:
            # Sort keys for consistent hashing
            content += ":" + json.dumps(parameters, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_action__mutmut_3(
        self, action_type: str, tool_name: Optional[str], parameters: Optional[dict]
    ) -> str:
        """Generate hash for action identification."""
        content = f"{action_type}:{tool_name or 'XXXX'}"
        if parameters:
            # Sort keys for consistent hashing
            content += ":" + json.dumps(parameters, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_action__mutmut_4(
        self, action_type: str, tool_name: Optional[str], parameters: Optional[dict]
    ) -> str:
        """Generate hash for action identification."""
        content = f"{action_type}:{tool_name or ''}"
        if parameters:
            # Sort keys for consistent hashing
            content = ":" + json.dumps(parameters, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_action__mutmut_5(
        self, action_type: str, tool_name: Optional[str], parameters: Optional[dict]
    ) -> str:
        """Generate hash for action identification."""
        content = f"{action_type}:{tool_name or ''}"
        if parameters:
            # Sort keys for consistent hashing
            content -= ":" + json.dumps(parameters, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_action__mutmut_6(
        self, action_type: str, tool_name: Optional[str], parameters: Optional[dict]
    ) -> str:
        """Generate hash for action identification."""
        content = f"{action_type}:{tool_name or ''}"
        if parameters:
            # Sort keys for consistent hashing
            content += ":" - json.dumps(parameters, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_action__mutmut_7(
        self, action_type: str, tool_name: Optional[str], parameters: Optional[dict]
    ) -> str:
        """Generate hash for action identification."""
        content = f"{action_type}:{tool_name or ''}"
        if parameters:
            # Sort keys for consistent hashing
            content += "XX:XX" + json.dumps(parameters, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_action__mutmut_8(
        self, action_type: str, tool_name: Optional[str], parameters: Optional[dict]
    ) -> str:
        """Generate hash for action identification."""
        content = f"{action_type}:{tool_name or ''}"
        if parameters:
            # Sort keys for consistent hashing
            content += ":" + json.dumps(None, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_action__mutmut_9(
        self, action_type: str, tool_name: Optional[str], parameters: Optional[dict]
    ) -> str:
        """Generate hash for action identification."""
        content = f"{action_type}:{tool_name or ''}"
        if parameters:
            # Sort keys for consistent hashing
            content += ":" + json.dumps(parameters, sort_keys=None, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_action__mutmut_10(
        self, action_type: str, tool_name: Optional[str], parameters: Optional[dict]
    ) -> str:
        """Generate hash for action identification."""
        content = f"{action_type}:{tool_name or ''}"
        if parameters:
            # Sort keys for consistent hashing
            content += ":" + json.dumps(parameters, sort_keys=True, default=None)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_action__mutmut_11(
        self, action_type: str, tool_name: Optional[str], parameters: Optional[dict]
    ) -> str:
        """Generate hash for action identification."""
        content = f"{action_type}:{tool_name or ''}"
        if parameters:
            # Sort keys for consistent hashing
            content += ":" + json.dumps(sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_action__mutmut_12(
        self, action_type: str, tool_name: Optional[str], parameters: Optional[dict]
    ) -> str:
        """Generate hash for action identification."""
        content = f"{action_type}:{tool_name or ''}"
        if parameters:
            # Sort keys for consistent hashing
            content += ":" + json.dumps(parameters, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_action__mutmut_13(
        self, action_type: str, tool_name: Optional[str], parameters: Optional[dict]
    ) -> str:
        """Generate hash for action identification."""
        content = f"{action_type}:{tool_name or ''}"
        if parameters:
            # Sort keys for consistent hashing
            content += ":" + json.dumps(parameters, sort_keys=True, )
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_action__mutmut_14(
        self, action_type: str, tool_name: Optional[str], parameters: Optional[dict]
    ) -> str:
        """Generate hash for action identification."""
        content = f"{action_type}:{tool_name or ''}"
        if parameters:
            # Sort keys for consistent hashing
            content += ":" + json.dumps(parameters, sort_keys=False, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_action__mutmut_15(
        self, action_type: str, tool_name: Optional[str], parameters: Optional[dict]
    ) -> str:
        """Generate hash for action identification."""
        content = f"{action_type}:{tool_name or ''}"
        if parameters:
            # Sort keys for consistent hashing
            content += ":" + json.dumps(parameters, sort_keys=True, default=str)
        return hashlib.sha256(None).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_action__mutmut_16(
        self, action_type: str, tool_name: Optional[str], parameters: Optional[dict]
    ) -> str:
        """Generate hash for action identification."""
        content = f"{action_type}:{tool_name or ''}"
        if parameters:
            # Sort keys for consistent hashing
            content += ":" + json.dumps(parameters, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:13]
    
    xǁLoopGuardrailǁ_hash_action__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLoopGuardrailǁ_hash_action__mutmut_1': xǁLoopGuardrailǁ_hash_action__mutmut_1, 
        'xǁLoopGuardrailǁ_hash_action__mutmut_2': xǁLoopGuardrailǁ_hash_action__mutmut_2, 
        'xǁLoopGuardrailǁ_hash_action__mutmut_3': xǁLoopGuardrailǁ_hash_action__mutmut_3, 
        'xǁLoopGuardrailǁ_hash_action__mutmut_4': xǁLoopGuardrailǁ_hash_action__mutmut_4, 
        'xǁLoopGuardrailǁ_hash_action__mutmut_5': xǁLoopGuardrailǁ_hash_action__mutmut_5, 
        'xǁLoopGuardrailǁ_hash_action__mutmut_6': xǁLoopGuardrailǁ_hash_action__mutmut_6, 
        'xǁLoopGuardrailǁ_hash_action__mutmut_7': xǁLoopGuardrailǁ_hash_action__mutmut_7, 
        'xǁLoopGuardrailǁ_hash_action__mutmut_8': xǁLoopGuardrailǁ_hash_action__mutmut_8, 
        'xǁLoopGuardrailǁ_hash_action__mutmut_9': xǁLoopGuardrailǁ_hash_action__mutmut_9, 
        'xǁLoopGuardrailǁ_hash_action__mutmut_10': xǁLoopGuardrailǁ_hash_action__mutmut_10, 
        'xǁLoopGuardrailǁ_hash_action__mutmut_11': xǁLoopGuardrailǁ_hash_action__mutmut_11, 
        'xǁLoopGuardrailǁ_hash_action__mutmut_12': xǁLoopGuardrailǁ_hash_action__mutmut_12, 
        'xǁLoopGuardrailǁ_hash_action__mutmut_13': xǁLoopGuardrailǁ_hash_action__mutmut_13, 
        'xǁLoopGuardrailǁ_hash_action__mutmut_14': xǁLoopGuardrailǁ_hash_action__mutmut_14, 
        'xǁLoopGuardrailǁ_hash_action__mutmut_15': xǁLoopGuardrailǁ_hash_action__mutmut_15, 
        'xǁLoopGuardrailǁ_hash_action__mutmut_16': xǁLoopGuardrailǁ_hash_action__mutmut_16
    }
    
    def _hash_action(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLoopGuardrailǁ_hash_action__mutmut_orig"), object.__getattribute__(self, "xǁLoopGuardrailǁ_hash_action__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _hash_action.__signature__ = _mutmut_signature(xǁLoopGuardrailǁ_hash_action__mutmut_orig)
    xǁLoopGuardrailǁ_hash_action__mutmut_orig.__name__ = 'xǁLoopGuardrailǁ_hash_action'

    def xǁLoopGuardrailǁ_hash_dict__mutmut_orig(self, d: dict) -> str:
        """Hash a dictionary."""
        return hashlib.sha256(json.dumps(d, sort_keys=True, default=str).encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_dict__mutmut_1(self, d: dict) -> str:
        """Hash a dictionary."""
        return hashlib.sha256(None).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_dict__mutmut_2(self, d: dict) -> str:
        """Hash a dictionary."""
        return hashlib.sha256(json.dumps(None, sort_keys=True, default=str).encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_dict__mutmut_3(self, d: dict) -> str:
        """Hash a dictionary."""
        return hashlib.sha256(json.dumps(d, sort_keys=None, default=str).encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_dict__mutmut_4(self, d: dict) -> str:
        """Hash a dictionary."""
        return hashlib.sha256(json.dumps(d, sort_keys=True, default=None).encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_dict__mutmut_5(self, d: dict) -> str:
        """Hash a dictionary."""
        return hashlib.sha256(json.dumps(sort_keys=True, default=str).encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_dict__mutmut_6(self, d: dict) -> str:
        """Hash a dictionary."""
        return hashlib.sha256(json.dumps(d, default=str).encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_dict__mutmut_7(self, d: dict) -> str:
        """Hash a dictionary."""
        return hashlib.sha256(json.dumps(d, sort_keys=True, ).encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_dict__mutmut_8(self, d: dict) -> str:
        """Hash a dictionary."""
        return hashlib.sha256(json.dumps(d, sort_keys=False, default=str).encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_dict__mutmut_9(self, d: dict) -> str:
        """Hash a dictionary."""
        return hashlib.sha256(json.dumps(d, sort_keys=True, default=str).encode()).hexdigest()[:13]
    
    xǁLoopGuardrailǁ_hash_dict__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLoopGuardrailǁ_hash_dict__mutmut_1': xǁLoopGuardrailǁ_hash_dict__mutmut_1, 
        'xǁLoopGuardrailǁ_hash_dict__mutmut_2': xǁLoopGuardrailǁ_hash_dict__mutmut_2, 
        'xǁLoopGuardrailǁ_hash_dict__mutmut_3': xǁLoopGuardrailǁ_hash_dict__mutmut_3, 
        'xǁLoopGuardrailǁ_hash_dict__mutmut_4': xǁLoopGuardrailǁ_hash_dict__mutmut_4, 
        'xǁLoopGuardrailǁ_hash_dict__mutmut_5': xǁLoopGuardrailǁ_hash_dict__mutmut_5, 
        'xǁLoopGuardrailǁ_hash_dict__mutmut_6': xǁLoopGuardrailǁ_hash_dict__mutmut_6, 
        'xǁLoopGuardrailǁ_hash_dict__mutmut_7': xǁLoopGuardrailǁ_hash_dict__mutmut_7, 
        'xǁLoopGuardrailǁ_hash_dict__mutmut_8': xǁLoopGuardrailǁ_hash_dict__mutmut_8, 
        'xǁLoopGuardrailǁ_hash_dict__mutmut_9': xǁLoopGuardrailǁ_hash_dict__mutmut_9
    }
    
    def _hash_dict(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLoopGuardrailǁ_hash_dict__mutmut_orig"), object.__getattribute__(self, "xǁLoopGuardrailǁ_hash_dict__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _hash_dict.__signature__ = _mutmut_signature(xǁLoopGuardrailǁ_hash_dict__mutmut_orig)
    xǁLoopGuardrailǁ_hash_dict__mutmut_orig.__name__ = 'xǁLoopGuardrailǁ_hash_dict'

    def xǁLoopGuardrailǁ_hash_result__mutmut_orig(self, result: Any) -> str:
        """Hash a result value."""
        if isinstance(result, (dict, list)):
            content = json.dumps(result, sort_keys=True, default=str)
        else:
            content = str(result)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_result__mutmut_1(self, result: Any) -> str:
        """Hash a result value."""
        if isinstance(result, (dict, list)):
            content = None
        else:
            content = str(result)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_result__mutmut_2(self, result: Any) -> str:
        """Hash a result value."""
        if isinstance(result, (dict, list)):
            content = json.dumps(None, sort_keys=True, default=str)
        else:
            content = str(result)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_result__mutmut_3(self, result: Any) -> str:
        """Hash a result value."""
        if isinstance(result, (dict, list)):
            content = json.dumps(result, sort_keys=None, default=str)
        else:
            content = str(result)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_result__mutmut_4(self, result: Any) -> str:
        """Hash a result value."""
        if isinstance(result, (dict, list)):
            content = json.dumps(result, sort_keys=True, default=None)
        else:
            content = str(result)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_result__mutmut_5(self, result: Any) -> str:
        """Hash a result value."""
        if isinstance(result, (dict, list)):
            content = json.dumps(sort_keys=True, default=str)
        else:
            content = str(result)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_result__mutmut_6(self, result: Any) -> str:
        """Hash a result value."""
        if isinstance(result, (dict, list)):
            content = json.dumps(result, default=str)
        else:
            content = str(result)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_result__mutmut_7(self, result: Any) -> str:
        """Hash a result value."""
        if isinstance(result, (dict, list)):
            content = json.dumps(result, sort_keys=True, )
        else:
            content = str(result)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_result__mutmut_8(self, result: Any) -> str:
        """Hash a result value."""
        if isinstance(result, (dict, list)):
            content = json.dumps(result, sort_keys=False, default=str)
        else:
            content = str(result)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_result__mutmut_9(self, result: Any) -> str:
        """Hash a result value."""
        if isinstance(result, (dict, list)):
            content = json.dumps(result, sort_keys=True, default=str)
        else:
            content = None
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_result__mutmut_10(self, result: Any) -> str:
        """Hash a result value."""
        if isinstance(result, (dict, list)):
            content = json.dumps(result, sort_keys=True, default=str)
        else:
            content = str(None)
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_result__mutmut_11(self, result: Any) -> str:
        """Hash a result value."""
        if isinstance(result, (dict, list)):
            content = json.dumps(result, sort_keys=True, default=str)
        else:
            content = str(result)
        return hashlib.sha256(None).hexdigest()[:12]

    def xǁLoopGuardrailǁ_hash_result__mutmut_12(self, result: Any) -> str:
        """Hash a result value."""
        if isinstance(result, (dict, list)):
            content = json.dumps(result, sort_keys=True, default=str)
        else:
            content = str(result)
        return hashlib.sha256(content.encode()).hexdigest()[:13]
    
    xǁLoopGuardrailǁ_hash_result__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLoopGuardrailǁ_hash_result__mutmut_1': xǁLoopGuardrailǁ_hash_result__mutmut_1, 
        'xǁLoopGuardrailǁ_hash_result__mutmut_2': xǁLoopGuardrailǁ_hash_result__mutmut_2, 
        'xǁLoopGuardrailǁ_hash_result__mutmut_3': xǁLoopGuardrailǁ_hash_result__mutmut_3, 
        'xǁLoopGuardrailǁ_hash_result__mutmut_4': xǁLoopGuardrailǁ_hash_result__mutmut_4, 
        'xǁLoopGuardrailǁ_hash_result__mutmut_5': xǁLoopGuardrailǁ_hash_result__mutmut_5, 
        'xǁLoopGuardrailǁ_hash_result__mutmut_6': xǁLoopGuardrailǁ_hash_result__mutmut_6, 
        'xǁLoopGuardrailǁ_hash_result__mutmut_7': xǁLoopGuardrailǁ_hash_result__mutmut_7, 
        'xǁLoopGuardrailǁ_hash_result__mutmut_8': xǁLoopGuardrailǁ_hash_result__mutmut_8, 
        'xǁLoopGuardrailǁ_hash_result__mutmut_9': xǁLoopGuardrailǁ_hash_result__mutmut_9, 
        'xǁLoopGuardrailǁ_hash_result__mutmut_10': xǁLoopGuardrailǁ_hash_result__mutmut_10, 
        'xǁLoopGuardrailǁ_hash_result__mutmut_11': xǁLoopGuardrailǁ_hash_result__mutmut_11, 
        'xǁLoopGuardrailǁ_hash_result__mutmut_12': xǁLoopGuardrailǁ_hash_result__mutmut_12
    }
    
    def _hash_result(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLoopGuardrailǁ_hash_result__mutmut_orig"), object.__getattribute__(self, "xǁLoopGuardrailǁ_hash_result__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _hash_result.__signature__ = _mutmut_signature(xǁLoopGuardrailǁ_hash_result__mutmut_orig)
    xǁLoopGuardrailǁ_hash_result__mutmut_orig.__name__ = 'xǁLoopGuardrailǁ_hash_result'

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_orig(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_1(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) <= self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_2(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = None
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_3(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(None)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_4(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[+self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_5(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = None

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_6(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(None, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_7(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, None):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_8(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_9(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, ):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_10(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(3, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_11(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 7):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_12(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) > pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_13(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len / 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_14(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 3:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_15(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = None
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_16(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[+pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_17(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = None

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_18(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len / 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_19(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[+pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_20(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 3 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_21(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : +pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_22(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern != preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_23(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type=None,
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_24(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=None,
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_25(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=None,
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_26(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action=None,
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_27(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_28(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_29(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_30(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_31(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="XXpattern_loopXX",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_32(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="PATTERN_LOOP",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="Break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_33(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="XXBreak loop by trying alternative approachXX",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_34(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="break loop by trying alternative approach",
                    )

        return None

    def xǁLoopGuardrailǁ_check_pattern_loop__mutmut_35(self) -> Optional[GuardrailViolation]:
        """Detect cyclic patterns in action history."""
        if len(self._history) < self.pattern_window:
            return None

        recent = list(self._history)[-self.pattern_window :]
        hashes = [r.action_hash for r in recent]

        # Check for repeating patterns of length 2-5
        for pattern_len in range(2, 6):
            if len(hashes) >= pattern_len * 2:
                pattern = hashes[-pattern_len:]
                preceding = hashes[-pattern_len * 2 : -pattern_len]

                if pattern == preceding:
                    # Found repeating pattern
                    return GuardrailViolation(
                        violation_type="pattern_loop",
                        message=f"Detected repeating pattern of {pattern_len} actions",
                        action_history=[r.action_type for r in recent],
                        recommended_action="BREAK LOOP BY TRYING ALTERNATIVE APPROACH",
                    )

        return None
    
    xǁLoopGuardrailǁ_check_pattern_loop__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_1': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_1, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_2': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_2, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_3': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_3, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_4': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_4, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_5': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_5, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_6': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_6, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_7': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_7, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_8': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_8, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_9': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_9, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_10': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_10, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_11': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_11, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_12': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_12, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_13': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_13, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_14': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_14, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_15': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_15, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_16': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_16, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_17': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_17, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_18': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_18, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_19': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_19, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_20': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_20, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_21': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_21, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_22': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_22, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_23': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_23, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_24': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_24, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_25': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_25, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_26': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_26, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_27': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_27, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_28': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_28, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_29': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_29, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_30': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_30, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_31': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_31, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_32': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_32, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_33': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_33, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_34': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_34, 
        'xǁLoopGuardrailǁ_check_pattern_loop__mutmut_35': xǁLoopGuardrailǁ_check_pattern_loop__mutmut_35
    }
    
    def _check_pattern_loop(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLoopGuardrailǁ_check_pattern_loop__mutmut_orig"), object.__getattribute__(self, "xǁLoopGuardrailǁ_check_pattern_loop__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _check_pattern_loop.__signature__ = _mutmut_signature(xǁLoopGuardrailǁ_check_pattern_loop__mutmut_orig)
    xǁLoopGuardrailǁ_check_pattern_loop__mutmut_orig.__name__ = 'xǁLoopGuardrailǁ_check_pattern_loop'

    def xǁLoopGuardrailǁ_count_violation_types__mutmut_orig(self) -> dict[str, int]:
        """Count violations by type."""
        counts = {}
        for v in self._violations:
            counts[v.violation_type] = counts.get(v.violation_type, 0) + 1
        return counts

    def xǁLoopGuardrailǁ_count_violation_types__mutmut_1(self) -> dict[str, int]:
        """Count violations by type."""
        counts = None
        for v in self._violations:
            counts[v.violation_type] = counts.get(v.violation_type, 0) + 1
        return counts

    def xǁLoopGuardrailǁ_count_violation_types__mutmut_2(self) -> dict[str, int]:
        """Count violations by type."""
        counts = {}
        for v in self._violations:
            counts[v.violation_type] = None
        return counts

    def xǁLoopGuardrailǁ_count_violation_types__mutmut_3(self) -> dict[str, int]:
        """Count violations by type."""
        counts = {}
        for v in self._violations:
            counts[v.violation_type] = counts.get(v.violation_type, 0) - 1
        return counts

    def xǁLoopGuardrailǁ_count_violation_types__mutmut_4(self) -> dict[str, int]:
        """Count violations by type."""
        counts = {}
        for v in self._violations:
            counts[v.violation_type] = counts.get(None, 0) + 1
        return counts

    def xǁLoopGuardrailǁ_count_violation_types__mutmut_5(self) -> dict[str, int]:
        """Count violations by type."""
        counts = {}
        for v in self._violations:
            counts[v.violation_type] = counts.get(v.violation_type, None) + 1
        return counts

    def xǁLoopGuardrailǁ_count_violation_types__mutmut_6(self) -> dict[str, int]:
        """Count violations by type."""
        counts = {}
        for v in self._violations:
            counts[v.violation_type] = counts.get(0) + 1
        return counts

    def xǁLoopGuardrailǁ_count_violation_types__mutmut_7(self) -> dict[str, int]:
        """Count violations by type."""
        counts = {}
        for v in self._violations:
            counts[v.violation_type] = counts.get(v.violation_type, ) + 1
        return counts

    def xǁLoopGuardrailǁ_count_violation_types__mutmut_8(self) -> dict[str, int]:
        """Count violations by type."""
        counts = {}
        for v in self._violations:
            counts[v.violation_type] = counts.get(v.violation_type, 1) + 1
        return counts

    def xǁLoopGuardrailǁ_count_violation_types__mutmut_9(self) -> dict[str, int]:
        """Count violations by type."""
        counts = {}
        for v in self._violations:
            counts[v.violation_type] = counts.get(v.violation_type, 0) + 2
        return counts
    
    xǁLoopGuardrailǁ_count_violation_types__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLoopGuardrailǁ_count_violation_types__mutmut_1': xǁLoopGuardrailǁ_count_violation_types__mutmut_1, 
        'xǁLoopGuardrailǁ_count_violation_types__mutmut_2': xǁLoopGuardrailǁ_count_violation_types__mutmut_2, 
        'xǁLoopGuardrailǁ_count_violation_types__mutmut_3': xǁLoopGuardrailǁ_count_violation_types__mutmut_3, 
        'xǁLoopGuardrailǁ_count_violation_types__mutmut_4': xǁLoopGuardrailǁ_count_violation_types__mutmut_4, 
        'xǁLoopGuardrailǁ_count_violation_types__mutmut_5': xǁLoopGuardrailǁ_count_violation_types__mutmut_5, 
        'xǁLoopGuardrailǁ_count_violation_types__mutmut_6': xǁLoopGuardrailǁ_count_violation_types__mutmut_6, 
        'xǁLoopGuardrailǁ_count_violation_types__mutmut_7': xǁLoopGuardrailǁ_count_violation_types__mutmut_7, 
        'xǁLoopGuardrailǁ_count_violation_types__mutmut_8': xǁLoopGuardrailǁ_count_violation_types__mutmut_8, 
        'xǁLoopGuardrailǁ_count_violation_types__mutmut_9': xǁLoopGuardrailǁ_count_violation_types__mutmut_9
    }
    
    def _count_violation_types(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLoopGuardrailǁ_count_violation_types__mutmut_orig"), object.__getattribute__(self, "xǁLoopGuardrailǁ_count_violation_types__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _count_violation_types.__signature__ = _mutmut_signature(xǁLoopGuardrailǁ_count_violation_types__mutmut_orig)
    xǁLoopGuardrailǁ_count_violation_types__mutmut_orig.__name__ = 'xǁLoopGuardrailǁ_count_violation_types'

    def xǁLoopGuardrailǁ_default_recovery__mutmut_orig(self, violation: Optional[GuardrailViolation]) -> str:
        """Generate default recovery message."""
        return (
            "LOOP DETECTED: The same action has been repeated multiple times "
            "without producing new results. Please:\n"
            "1. Stop and analyze the current state\n"
            "2. Try a different approach or tool\n"
            "3. If stuck, summarize findings and request guidance\n"
            "4. Consider if the goal has already been achieved"
        )

    def xǁLoopGuardrailǁ_default_recovery__mutmut_1(self, violation: Optional[GuardrailViolation]) -> str:
        """Generate default recovery message."""
        return (
            "XXLOOP DETECTED: The same action has been repeated multiple times XX"
            "without producing new results. Please:\n"
            "1. Stop and analyze the current state\n"
            "2. Try a different approach or tool\n"
            "3. If stuck, summarize findings and request guidance\n"
            "4. Consider if the goal has already been achieved"
        )

    def xǁLoopGuardrailǁ_default_recovery__mutmut_2(self, violation: Optional[GuardrailViolation]) -> str:
        """Generate default recovery message."""
        return (
            "loop detected: the same action has been repeated multiple times "
            "without producing new results. Please:\n"
            "1. Stop and analyze the current state\n"
            "2. Try a different approach or tool\n"
            "3. If stuck, summarize findings and request guidance\n"
            "4. Consider if the goal has already been achieved"
        )

    def xǁLoopGuardrailǁ_default_recovery__mutmut_3(self, violation: Optional[GuardrailViolation]) -> str:
        """Generate default recovery message."""
        return (
            "LOOP DETECTED: THE SAME ACTION HAS BEEN REPEATED MULTIPLE TIMES "
            "without producing new results. Please:\n"
            "1. Stop and analyze the current state\n"
            "2. Try a different approach or tool\n"
            "3. If stuck, summarize findings and request guidance\n"
            "4. Consider if the goal has already been achieved"
        )

    def xǁLoopGuardrailǁ_default_recovery__mutmut_4(self, violation: Optional[GuardrailViolation]) -> str:
        """Generate default recovery message."""
        return (
            "LOOP DETECTED: The same action has been repeated multiple times "
            "XXwithout producing new results. Please:\nXX"
            "1. Stop and analyze the current state\n"
            "2. Try a different approach or tool\n"
            "3. If stuck, summarize findings and request guidance\n"
            "4. Consider if the goal has already been achieved"
        )

    def xǁLoopGuardrailǁ_default_recovery__mutmut_5(self, violation: Optional[GuardrailViolation]) -> str:
        """Generate default recovery message."""
        return (
            "LOOP DETECTED: The same action has been repeated multiple times "
            "without producing new results. please:\n"
            "1. Stop and analyze the current state\n"
            "2. Try a different approach or tool\n"
            "3. If stuck, summarize findings and request guidance\n"
            "4. Consider if the goal has already been achieved"
        )

    def xǁLoopGuardrailǁ_default_recovery__mutmut_6(self, violation: Optional[GuardrailViolation]) -> str:
        """Generate default recovery message."""
        return (
            "LOOP DETECTED: The same action has been repeated multiple times "
            "WITHOUT PRODUCING NEW RESULTS. PLEASE:\n"
            "1. Stop and analyze the current state\n"
            "2. Try a different approach or tool\n"
            "3. If stuck, summarize findings and request guidance\n"
            "4. Consider if the goal has already been achieved"
        )

    def xǁLoopGuardrailǁ_default_recovery__mutmut_7(self, violation: Optional[GuardrailViolation]) -> str:
        """Generate default recovery message."""
        return (
            "LOOP DETECTED: The same action has been repeated multiple times "
            "without producing new results. Please:\n"
            "XX1. Stop and analyze the current state\nXX"
            "2. Try a different approach or tool\n"
            "3. If stuck, summarize findings and request guidance\n"
            "4. Consider if the goal has already been achieved"
        )

    def xǁLoopGuardrailǁ_default_recovery__mutmut_8(self, violation: Optional[GuardrailViolation]) -> str:
        """Generate default recovery message."""
        return (
            "LOOP DETECTED: The same action has been repeated multiple times "
            "without producing new results. Please:\n"
            "1. stop and analyze the current state\n"
            "2. Try a different approach or tool\n"
            "3. If stuck, summarize findings and request guidance\n"
            "4. Consider if the goal has already been achieved"
        )

    def xǁLoopGuardrailǁ_default_recovery__mutmut_9(self, violation: Optional[GuardrailViolation]) -> str:
        """Generate default recovery message."""
        return (
            "LOOP DETECTED: The same action has been repeated multiple times "
            "without producing new results. Please:\n"
            "1. STOP AND ANALYZE THE CURRENT STATE\n"
            "2. Try a different approach or tool\n"
            "3. If stuck, summarize findings and request guidance\n"
            "4. Consider if the goal has already been achieved"
        )

    def xǁLoopGuardrailǁ_default_recovery__mutmut_10(self, violation: Optional[GuardrailViolation]) -> str:
        """Generate default recovery message."""
        return (
            "LOOP DETECTED: The same action has been repeated multiple times "
            "without producing new results. Please:\n"
            "1. Stop and analyze the current state\n"
            "XX2. Try a different approach or tool\nXX"
            "3. If stuck, summarize findings and request guidance\n"
            "4. Consider if the goal has already been achieved"
        )

    def xǁLoopGuardrailǁ_default_recovery__mutmut_11(self, violation: Optional[GuardrailViolation]) -> str:
        """Generate default recovery message."""
        return (
            "LOOP DETECTED: The same action has been repeated multiple times "
            "without producing new results. Please:\n"
            "1. Stop and analyze the current state\n"
            "2. try a different approach or tool\n"
            "3. If stuck, summarize findings and request guidance\n"
            "4. Consider if the goal has already been achieved"
        )

    def xǁLoopGuardrailǁ_default_recovery__mutmut_12(self, violation: Optional[GuardrailViolation]) -> str:
        """Generate default recovery message."""
        return (
            "LOOP DETECTED: The same action has been repeated multiple times "
            "without producing new results. Please:\n"
            "1. Stop and analyze the current state\n"
            "2. TRY A DIFFERENT APPROACH OR TOOL\n"
            "3. If stuck, summarize findings and request guidance\n"
            "4. Consider if the goal has already been achieved"
        )

    def xǁLoopGuardrailǁ_default_recovery__mutmut_13(self, violation: Optional[GuardrailViolation]) -> str:
        """Generate default recovery message."""
        return (
            "LOOP DETECTED: The same action has been repeated multiple times "
            "without producing new results. Please:\n"
            "1. Stop and analyze the current state\n"
            "2. Try a different approach or tool\n"
            "XX3. If stuck, summarize findings and request guidance\nXX"
            "4. Consider if the goal has already been achieved"
        )

    def xǁLoopGuardrailǁ_default_recovery__mutmut_14(self, violation: Optional[GuardrailViolation]) -> str:
        """Generate default recovery message."""
        return (
            "LOOP DETECTED: The same action has been repeated multiple times "
            "without producing new results. Please:\n"
            "1. Stop and analyze the current state\n"
            "2. Try a different approach or tool\n"
            "3. if stuck, summarize findings and request guidance\n"
            "4. Consider if the goal has already been achieved"
        )

    def xǁLoopGuardrailǁ_default_recovery__mutmut_15(self, violation: Optional[GuardrailViolation]) -> str:
        """Generate default recovery message."""
        return (
            "LOOP DETECTED: The same action has been repeated multiple times "
            "without producing new results. Please:\n"
            "1. Stop and analyze the current state\n"
            "2. Try a different approach or tool\n"
            "3. IF STUCK, SUMMARIZE FINDINGS AND REQUEST GUIDANCE\n"
            "4. Consider if the goal has already been achieved"
        )

    def xǁLoopGuardrailǁ_default_recovery__mutmut_16(self, violation: Optional[GuardrailViolation]) -> str:
        """Generate default recovery message."""
        return (
            "LOOP DETECTED: The same action has been repeated multiple times "
            "without producing new results. Please:\n"
            "1. Stop and analyze the current state\n"
            "2. Try a different approach or tool\n"
            "3. If stuck, summarize findings and request guidance\n"
            "XX4. Consider if the goal has already been achievedXX"
        )

    def xǁLoopGuardrailǁ_default_recovery__mutmut_17(self, violation: Optional[GuardrailViolation]) -> str:
        """Generate default recovery message."""
        return (
            "LOOP DETECTED: The same action has been repeated multiple times "
            "without producing new results. Please:\n"
            "1. Stop and analyze the current state\n"
            "2. Try a different approach or tool\n"
            "3. If stuck, summarize findings and request guidance\n"
            "4. consider if the goal has already been achieved"
        )

    def xǁLoopGuardrailǁ_default_recovery__mutmut_18(self, violation: Optional[GuardrailViolation]) -> str:
        """Generate default recovery message."""
        return (
            "LOOP DETECTED: The same action has been repeated multiple times "
            "without producing new results. Please:\n"
            "1. Stop and analyze the current state\n"
            "2. Try a different approach or tool\n"
            "3. If stuck, summarize findings and request guidance\n"
            "4. CONSIDER IF THE GOAL HAS ALREADY BEEN ACHIEVED"
        )
    
    xǁLoopGuardrailǁ_default_recovery__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLoopGuardrailǁ_default_recovery__mutmut_1': xǁLoopGuardrailǁ_default_recovery__mutmut_1, 
        'xǁLoopGuardrailǁ_default_recovery__mutmut_2': xǁLoopGuardrailǁ_default_recovery__mutmut_2, 
        'xǁLoopGuardrailǁ_default_recovery__mutmut_3': xǁLoopGuardrailǁ_default_recovery__mutmut_3, 
        'xǁLoopGuardrailǁ_default_recovery__mutmut_4': xǁLoopGuardrailǁ_default_recovery__mutmut_4, 
        'xǁLoopGuardrailǁ_default_recovery__mutmut_5': xǁLoopGuardrailǁ_default_recovery__mutmut_5, 
        'xǁLoopGuardrailǁ_default_recovery__mutmut_6': xǁLoopGuardrailǁ_default_recovery__mutmut_6, 
        'xǁLoopGuardrailǁ_default_recovery__mutmut_7': xǁLoopGuardrailǁ_default_recovery__mutmut_7, 
        'xǁLoopGuardrailǁ_default_recovery__mutmut_8': xǁLoopGuardrailǁ_default_recovery__mutmut_8, 
        'xǁLoopGuardrailǁ_default_recovery__mutmut_9': xǁLoopGuardrailǁ_default_recovery__mutmut_9, 
        'xǁLoopGuardrailǁ_default_recovery__mutmut_10': xǁLoopGuardrailǁ_default_recovery__mutmut_10, 
        'xǁLoopGuardrailǁ_default_recovery__mutmut_11': xǁLoopGuardrailǁ_default_recovery__mutmut_11, 
        'xǁLoopGuardrailǁ_default_recovery__mutmut_12': xǁLoopGuardrailǁ_default_recovery__mutmut_12, 
        'xǁLoopGuardrailǁ_default_recovery__mutmut_13': xǁLoopGuardrailǁ_default_recovery__mutmut_13, 
        'xǁLoopGuardrailǁ_default_recovery__mutmut_14': xǁLoopGuardrailǁ_default_recovery__mutmut_14, 
        'xǁLoopGuardrailǁ_default_recovery__mutmut_15': xǁLoopGuardrailǁ_default_recovery__mutmut_15, 
        'xǁLoopGuardrailǁ_default_recovery__mutmut_16': xǁLoopGuardrailǁ_default_recovery__mutmut_16, 
        'xǁLoopGuardrailǁ_default_recovery__mutmut_17': xǁLoopGuardrailǁ_default_recovery__mutmut_17, 
        'xǁLoopGuardrailǁ_default_recovery__mutmut_18': xǁLoopGuardrailǁ_default_recovery__mutmut_18
    }
    
    def _default_recovery(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLoopGuardrailǁ_default_recovery__mutmut_orig"), object.__getattribute__(self, "xǁLoopGuardrailǁ_default_recovery__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _default_recovery.__signature__ = _mutmut_signature(xǁLoopGuardrailǁ_default_recovery__mutmut_orig)
    xǁLoopGuardrailǁ_default_recovery__mutmut_orig.__name__ = 'xǁLoopGuardrailǁ_default_recovery'

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_orig(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_1(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = None

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_2(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "XXsearchXX": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_3(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "SEARCH": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_4(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "XXConsider using grep or glob with different patternsXX",
            "read": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_5(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_6(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "CONSIDER USING GREP OR GLOB WITH DIFFERENT PATTERNS",
            "read": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_7(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "XXreadXX": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_8(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "READ": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_9(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "XXTry reading a different file or sectionXX",
            "edit": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_10(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_11(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "TRY READING A DIFFERENT FILE OR SECTION",
            "edit": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_12(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "XXeditXX": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_13(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "EDIT": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_14(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "XXVerify changes were applied before editing againXX",
            "run": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_15(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_16(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "VERIFY CHANGES WERE APPLIED BEFORE EDITING AGAIN",
            "run": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_17(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "XXrunXX": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_18(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "RUN": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_19(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "XXCheck command output before re-runningXX",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_20(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_21(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "CHECK COMMAND OUTPUT BEFORE RE-RUNNING",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_22(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "XXtestXX": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_23(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "TEST": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_24(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "XXReview test results before re-running testsXX",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_25(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_26(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "REVIEW TEST RESULTS BEFORE RE-RUNNING TESTS",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_27(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() and (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_28(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key not in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_29(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.upper() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_30(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name or key in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_31(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key not in tool_name.lower()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_32(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.upper()):
                return suggestion

        return "Consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_33(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "XXConsider trying a different approach to avoid repetitionXX"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_34(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "consider trying a different approach to avoid repetition"

    def xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_35(self, action_type: str, tool_name: Optional[str]) -> str:
        """Generate suggestion for alternative action."""
        suggestions = {
            "search": "Consider using grep or glob with different patterns",
            "read": "Try reading a different file or section",
            "edit": "Verify changes were applied before editing again",
            "run": "Check command output before re-running",
            "test": "Review test results before re-running tests",
        }

        for key, suggestion in suggestions.items():
            if key in action_type.lower() or (tool_name and key in tool_name.lower()):
                return suggestion

        return "CONSIDER TRYING A DIFFERENT APPROACH TO AVOID REPETITION"
    
    xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_1': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_1, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_2': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_2, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_3': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_3, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_4': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_4, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_5': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_5, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_6': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_6, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_7': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_7, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_8': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_8, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_9': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_9, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_10': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_10, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_11': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_11, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_12': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_12, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_13': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_13, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_14': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_14, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_15': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_15, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_16': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_16, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_17': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_17, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_18': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_18, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_19': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_19, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_20': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_20, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_21': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_21, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_22': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_22, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_23': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_23, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_24': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_24, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_25': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_25, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_26': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_26, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_27': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_27, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_28': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_28, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_29': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_29, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_30': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_30, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_31': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_31, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_32': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_32, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_33': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_33, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_34': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_34, 
        'xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_35': xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_35
    }
    
    def _generate_alternative_suggestion(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_orig"), object.__getattribute__(self, "xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _generate_alternative_suggestion.__signature__ = _mutmut_signature(xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_orig)
    xǁLoopGuardrailǁ_generate_alternative_suggestion__mutmut_orig.__name__ = 'xǁLoopGuardrailǁ_generate_alternative_suggestion'
