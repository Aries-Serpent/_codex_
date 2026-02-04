"""MCP lifecycle management for server state transitions.

This module provides server lifecycle management including:
- Server initialization and shutdown
- Health checks and readiness probes
- Graceful shutdown handling
- State transitions with validation
"""

import asyncio
import logging
import signal
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional, Any

logger = logging.getLogger(__name__)
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


class ServerState(Enum):
    """Server state enumeration."""
    
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    DRAINING = "draining"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


# Valid state transitions
VALID_TRANSITIONS: dict[ServerState, list[ServerState]] = {
    ServerState.UNINITIALIZED: [ServerState.INITIALIZING],
    ServerState.INITIALIZING: [ServerState.READY, ServerState.ERROR],
    ServerState.READY: [ServerState.RUNNING, ServerState.STOPPING],
    ServerState.RUNNING: [ServerState.DRAINING, ServerState.STOPPING, ServerState.ERROR],
    ServerState.DRAINING: [ServerState.STOPPING],
    ServerState.STOPPING: [ServerState.STOPPED],
    ServerState.STOPPED: [ServerState.INITIALIZING],
    ServerState.ERROR: [ServerState.STOPPING, ServerState.INITIALIZING],
}


class InvalidStateTransition(Exception):
    """Raised when an invalid state transition is attempted."""
    
    def xǁInvalidStateTransitionǁ__init____mutmut_orig(self, current: ServerState, target: ServerState) -> None:
        """Initialize the exception.
        
        Args:
            current: Current server state.
            target: Target state that was attempted.
        """
        self.current = current
        self.target = target
        super().__init__(
            f"Invalid state transition from {current.value} to {target.value}"
        )
    
    def xǁInvalidStateTransitionǁ__init____mutmut_1(self, current: ServerState, target: ServerState) -> None:
        """Initialize the exception.
        
        Args:
            current: Current server state.
            target: Target state that was attempted.
        """
        self.current = None
        self.target = target
        super().__init__(
            f"Invalid state transition from {current.value} to {target.value}"
        )
    
    def xǁInvalidStateTransitionǁ__init____mutmut_2(self, current: ServerState, target: ServerState) -> None:
        """Initialize the exception.
        
        Args:
            current: Current server state.
            target: Target state that was attempted.
        """
        self.current = current
        self.target = None
        super().__init__(
            f"Invalid state transition from {current.value} to {target.value}"
        )
    
    def xǁInvalidStateTransitionǁ__init____mutmut_3(self, current: ServerState, target: ServerState) -> None:
        """Initialize the exception.
        
        Args:
            current: Current server state.
            target: Target state that was attempted.
        """
        self.current = current
        self.target = target
        super().__init__(
            None
        )
    
    xǁInvalidStateTransitionǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁInvalidStateTransitionǁ__init____mutmut_1': xǁInvalidStateTransitionǁ__init____mutmut_1, 
        'xǁInvalidStateTransitionǁ__init____mutmut_2': xǁInvalidStateTransitionǁ__init____mutmut_2, 
        'xǁInvalidStateTransitionǁ__init____mutmut_3': xǁInvalidStateTransitionǁ__init____mutmut_3
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁInvalidStateTransitionǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁInvalidStateTransitionǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁInvalidStateTransitionǁ__init____mutmut_orig)
    xǁInvalidStateTransitionǁ__init____mutmut_orig.__name__ = 'xǁInvalidStateTransitionǁ__init__'


@dataclass
class HealthStatus:
    """Health check result."""
    
    healthy: bool
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class LifecycleConfig:
    """Lifecycle configuration."""
    
    shutdown_timeout_seconds: float = 30.0
    health_check_interval_seconds: float = 10.0
    drain_timeout_seconds: float = 60.0
    max_concurrent_requests: int = 100


class LifecycleManager:
    """Manages MCP server lifecycle."""
    
    def xǁLifecycleManagerǁ__init____mutmut_orig(self, config: Optional[LifecycleConfig] = None) -> None:
        """Initialize the lifecycle manager.
        
        Args:
            config: Lifecycle configuration. Uses defaults if not provided.
        """
        self._config = config or LifecycleConfig()
        self._state = ServerState.UNINITIALIZED
        self._state_lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()
        self._active_requests = 0
        self._requests_lock = asyncio.Lock()
        self._health_checks: list[Callable[[], HealthStatus]] = []
        self._startup_hooks: list[Callable[[], None]] = []
        self._shutdown_hooks: list[Callable[[], None]] = []
        self._logger = logging.getLogger(__name__)
        
    
    def xǁLifecycleManagerǁ__init____mutmut_1(self, config: Optional[LifecycleConfig] = None) -> None:
        """Initialize the lifecycle manager.
        
        Args:
            config: Lifecycle configuration. Uses defaults if not provided.
        """
        self._config = None
        self._state = ServerState.UNINITIALIZED
        self._state_lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()
        self._active_requests = 0
        self._requests_lock = asyncio.Lock()
        self._health_checks: list[Callable[[], HealthStatus]] = []
        self._startup_hooks: list[Callable[[], None]] = []
        self._shutdown_hooks: list[Callable[[], None]] = []
        self._logger = logging.getLogger(__name__)
        
    
    def xǁLifecycleManagerǁ__init____mutmut_2(self, config: Optional[LifecycleConfig] = None) -> None:
        """Initialize the lifecycle manager.
        
        Args:
            config: Lifecycle configuration. Uses defaults if not provided.
        """
        self._config = config and LifecycleConfig()
        self._state = ServerState.UNINITIALIZED
        self._state_lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()
        self._active_requests = 0
        self._requests_lock = asyncio.Lock()
        self._health_checks: list[Callable[[], HealthStatus]] = []
        self._startup_hooks: list[Callable[[], None]] = []
        self._shutdown_hooks: list[Callable[[], None]] = []
        self._logger = logging.getLogger(__name__)
        
    
    def xǁLifecycleManagerǁ__init____mutmut_3(self, config: Optional[LifecycleConfig] = None) -> None:
        """Initialize the lifecycle manager.
        
        Args:
            config: Lifecycle configuration. Uses defaults if not provided.
        """
        self._config = config or LifecycleConfig()
        self._state = None
        self._state_lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()
        self._active_requests = 0
        self._requests_lock = asyncio.Lock()
        self._health_checks: list[Callable[[], HealthStatus]] = []
        self._startup_hooks: list[Callable[[], None]] = []
        self._shutdown_hooks: list[Callable[[], None]] = []
        self._logger = logging.getLogger(__name__)
        
    
    def xǁLifecycleManagerǁ__init____mutmut_4(self, config: Optional[LifecycleConfig] = None) -> None:
        """Initialize the lifecycle manager.
        
        Args:
            config: Lifecycle configuration. Uses defaults if not provided.
        """
        self._config = config or LifecycleConfig()
        self._state = ServerState.UNINITIALIZED
        self._state_lock = None
        self._shutdown_event = asyncio.Event()
        self._active_requests = 0
        self._requests_lock = asyncio.Lock()
        self._health_checks: list[Callable[[], HealthStatus]] = []
        self._startup_hooks: list[Callable[[], None]] = []
        self._shutdown_hooks: list[Callable[[], None]] = []
        self._logger = logging.getLogger(__name__)
        
    
    def xǁLifecycleManagerǁ__init____mutmut_5(self, config: Optional[LifecycleConfig] = None) -> None:
        """Initialize the lifecycle manager.
        
        Args:
            config: Lifecycle configuration. Uses defaults if not provided.
        """
        self._config = config or LifecycleConfig()
        self._state = ServerState.UNINITIALIZED
        self._state_lock = asyncio.Lock()
        self._shutdown_event = None
        self._active_requests = 0
        self._requests_lock = asyncio.Lock()
        self._health_checks: list[Callable[[], HealthStatus]] = []
        self._startup_hooks: list[Callable[[], None]] = []
        self._shutdown_hooks: list[Callable[[], None]] = []
        self._logger = logging.getLogger(__name__)
        
    
    def xǁLifecycleManagerǁ__init____mutmut_6(self, config: Optional[LifecycleConfig] = None) -> None:
        """Initialize the lifecycle manager.
        
        Args:
            config: Lifecycle configuration. Uses defaults if not provided.
        """
        self._config = config or LifecycleConfig()
        self._state = ServerState.UNINITIALIZED
        self._state_lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()
        self._active_requests = None
        self._requests_lock = asyncio.Lock()
        self._health_checks: list[Callable[[], HealthStatus]] = []
        self._startup_hooks: list[Callable[[], None]] = []
        self._shutdown_hooks: list[Callable[[], None]] = []
        self._logger = logging.getLogger(__name__)
        
    
    def xǁLifecycleManagerǁ__init____mutmut_7(self, config: Optional[LifecycleConfig] = None) -> None:
        """Initialize the lifecycle manager.
        
        Args:
            config: Lifecycle configuration. Uses defaults if not provided.
        """
        self._config = config or LifecycleConfig()
        self._state = ServerState.UNINITIALIZED
        self._state_lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()
        self._active_requests = 1
        self._requests_lock = asyncio.Lock()
        self._health_checks: list[Callable[[], HealthStatus]] = []
        self._startup_hooks: list[Callable[[], None]] = []
        self._shutdown_hooks: list[Callable[[], None]] = []
        self._logger = logging.getLogger(__name__)
        
    
    def xǁLifecycleManagerǁ__init____mutmut_8(self, config: Optional[LifecycleConfig] = None) -> None:
        """Initialize the lifecycle manager.
        
        Args:
            config: Lifecycle configuration. Uses defaults if not provided.
        """
        self._config = config or LifecycleConfig()
        self._state = ServerState.UNINITIALIZED
        self._state_lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()
        self._active_requests = 0
        self._requests_lock = None
        self._health_checks: list[Callable[[], HealthStatus]] = []
        self._startup_hooks: list[Callable[[], None]] = []
        self._shutdown_hooks: list[Callable[[], None]] = []
        self._logger = logging.getLogger(__name__)
        
    
    def xǁLifecycleManagerǁ__init____mutmut_9(self, config: Optional[LifecycleConfig] = None) -> None:
        """Initialize the lifecycle manager.
        
        Args:
            config: Lifecycle configuration. Uses defaults if not provided.
        """
        self._config = config or LifecycleConfig()
        self._state = ServerState.UNINITIALIZED
        self._state_lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()
        self._active_requests = 0
        self._requests_lock = asyncio.Lock()
        self._health_checks: list[Callable[[], HealthStatus]] = None
        self._startup_hooks: list[Callable[[], None]] = []
        self._shutdown_hooks: list[Callable[[], None]] = []
        self._logger = logging.getLogger(__name__)
        
    
    def xǁLifecycleManagerǁ__init____mutmut_10(self, config: Optional[LifecycleConfig] = None) -> None:
        """Initialize the lifecycle manager.
        
        Args:
            config: Lifecycle configuration. Uses defaults if not provided.
        """
        self._config = config or LifecycleConfig()
        self._state = ServerState.UNINITIALIZED
        self._state_lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()
        self._active_requests = 0
        self._requests_lock = asyncio.Lock()
        self._health_checks: list[Callable[[], HealthStatus]] = []
        self._startup_hooks: list[Callable[[], None]] = None
        self._shutdown_hooks: list[Callable[[], None]] = []
        self._logger = logging.getLogger(__name__)
        
    
    def xǁLifecycleManagerǁ__init____mutmut_11(self, config: Optional[LifecycleConfig] = None) -> None:
        """Initialize the lifecycle manager.
        
        Args:
            config: Lifecycle configuration. Uses defaults if not provided.
        """
        self._config = config or LifecycleConfig()
        self._state = ServerState.UNINITIALIZED
        self._state_lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()
        self._active_requests = 0
        self._requests_lock = asyncio.Lock()
        self._health_checks: list[Callable[[], HealthStatus]] = []
        self._startup_hooks: list[Callable[[], None]] = []
        self._shutdown_hooks: list[Callable[[], None]] = None
        self._logger = logging.getLogger(__name__)
        
    
    def xǁLifecycleManagerǁ__init____mutmut_12(self, config: Optional[LifecycleConfig] = None) -> None:
        """Initialize the lifecycle manager.
        
        Args:
            config: Lifecycle configuration. Uses defaults if not provided.
        """
        self._config = config or LifecycleConfig()
        self._state = ServerState.UNINITIALIZED
        self._state_lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()
        self._active_requests = 0
        self._requests_lock = asyncio.Lock()
        self._health_checks: list[Callable[[], HealthStatus]] = []
        self._startup_hooks: list[Callable[[], None]] = []
        self._shutdown_hooks: list[Callable[[], None]] = []
        self._logger = None
        
    
    def xǁLifecycleManagerǁ__init____mutmut_13(self, config: Optional[LifecycleConfig] = None) -> None:
        """Initialize the lifecycle manager.
        
        Args:
            config: Lifecycle configuration. Uses defaults if not provided.
        """
        self._config = config or LifecycleConfig()
        self._state = ServerState.UNINITIALIZED
        self._state_lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()
        self._active_requests = 0
        self._requests_lock = asyncio.Lock()
        self._health_checks: list[Callable[[], HealthStatus]] = []
        self._startup_hooks: list[Callable[[], None]] = []
        self._shutdown_hooks: list[Callable[[], None]] = []
        self._logger = logging.getLogger(None)
        
    
    xǁLifecycleManagerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLifecycleManagerǁ__init____mutmut_1': xǁLifecycleManagerǁ__init____mutmut_1, 
        'xǁLifecycleManagerǁ__init____mutmut_2': xǁLifecycleManagerǁ__init____mutmut_2, 
        'xǁLifecycleManagerǁ__init____mutmut_3': xǁLifecycleManagerǁ__init____mutmut_3, 
        'xǁLifecycleManagerǁ__init____mutmut_4': xǁLifecycleManagerǁ__init____mutmut_4, 
        'xǁLifecycleManagerǁ__init____mutmut_5': xǁLifecycleManagerǁ__init____mutmut_5, 
        'xǁLifecycleManagerǁ__init____mutmut_6': xǁLifecycleManagerǁ__init____mutmut_6, 
        'xǁLifecycleManagerǁ__init____mutmut_7': xǁLifecycleManagerǁ__init____mutmut_7, 
        'xǁLifecycleManagerǁ__init____mutmut_8': xǁLifecycleManagerǁ__init____mutmut_8, 
        'xǁLifecycleManagerǁ__init____mutmut_9': xǁLifecycleManagerǁ__init____mutmut_9, 
        'xǁLifecycleManagerǁ__init____mutmut_10': xǁLifecycleManagerǁ__init____mutmut_10, 
        'xǁLifecycleManagerǁ__init____mutmut_11': xǁLifecycleManagerǁ__init____mutmut_11, 
        'xǁLifecycleManagerǁ__init____mutmut_12': xǁLifecycleManagerǁ__init____mutmut_12, 
        'xǁLifecycleManagerǁ__init____mutmut_13': xǁLifecycleManagerǁ__init____mutmut_13
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLifecycleManagerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁLifecycleManagerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁLifecycleManagerǁ__init____mutmut_orig)
    xǁLifecycleManagerǁ__init____mutmut_orig.__name__ = 'xǁLifecycleManagerǁ__init__'
    @property
    def state(self) -> ServerState:
        """Get current server state."""
        return self._state
    
    @property
    def is_healthy(self) -> bool:
        """Check if server is in a healthy state."""
        return self._state in (ServerState.READY, ServerState.RUNNING)
    
    @property
    def is_accepting_requests(self) -> bool:
        """Check if server is accepting new requests."""
        return self._state == ServerState.RUNNING
    
    async def xǁLifecycleManagerǁtransition_to__mutmut_orig(self, target: ServerState) -> None:
        """Transition to a new state with validation.
        
        Args:
            target: Target state to transition to.
            
        Raises:
            InvalidStateTransition: If the transition is not valid.
        """
        async with self._state_lock:
            if target not in VALID_TRANSITIONS.get(self._state, []):
                raise InvalidStateTransition(self._state, target)
            
            old_state = self._state
            self._state = target
            self._logger.info(
                "State transition: %s -> %s",
                old_state.value,
                target.value
            )
    
    async def xǁLifecycleManagerǁtransition_to__mutmut_1(self, target: ServerState) -> None:
        """Transition to a new state with validation.
        
        Args:
            target: Target state to transition to.
            
        Raises:
            InvalidStateTransition: If the transition is not valid.
        """
        async with self._state_lock:
            if target in VALID_TRANSITIONS.get(self._state, []):
                raise InvalidStateTransition(self._state, target)
            
            old_state = self._state
            self._state = target
            self._logger.info(
                "State transition: %s -> %s",
                old_state.value,
                target.value
            )
    
    async def xǁLifecycleManagerǁtransition_to__mutmut_2(self, target: ServerState) -> None:
        """Transition to a new state with validation.
        
        Args:
            target: Target state to transition to.
            
        Raises:
            InvalidStateTransition: If the transition is not valid.
        """
        async with self._state_lock:
            if target not in VALID_TRANSITIONS.get(None, []):
                raise InvalidStateTransition(self._state, target)
            
            old_state = self._state
            self._state = target
            self._logger.info(
                "State transition: %s -> %s",
                old_state.value,
                target.value
            )
    
    async def xǁLifecycleManagerǁtransition_to__mutmut_3(self, target: ServerState) -> None:
        """Transition to a new state with validation.
        
        Args:
            target: Target state to transition to.
            
        Raises:
            InvalidStateTransition: If the transition is not valid.
        """
        async with self._state_lock:
            if target not in VALID_TRANSITIONS.get(self._state, None):
                raise InvalidStateTransition(self._state, target)
            
            old_state = self._state
            self._state = target
            self._logger.info(
                "State transition: %s -> %s",
                old_state.value,
                target.value
            )
    
    async def xǁLifecycleManagerǁtransition_to__mutmut_4(self, target: ServerState) -> None:
        """Transition to a new state with validation.
        
        Args:
            target: Target state to transition to.
            
        Raises:
            InvalidStateTransition: If the transition is not valid.
        """
        async with self._state_lock:
            if target not in VALID_TRANSITIONS.get([]):
                raise InvalidStateTransition(self._state, target)
            
            old_state = self._state
            self._state = target
            self._logger.info(
                "State transition: %s -> %s",
                old_state.value,
                target.value
            )
    
    async def xǁLifecycleManagerǁtransition_to__mutmut_5(self, target: ServerState) -> None:
        """Transition to a new state with validation.
        
        Args:
            target: Target state to transition to.
            
        Raises:
            InvalidStateTransition: If the transition is not valid.
        """
        async with self._state_lock:
            if target not in VALID_TRANSITIONS.get(self._state, ):
                raise InvalidStateTransition(self._state, target)
            
            old_state = self._state
            self._state = target
            self._logger.info(
                "State transition: %s -> %s",
                old_state.value,
                target.value
            )
    
    async def xǁLifecycleManagerǁtransition_to__mutmut_6(self, target: ServerState) -> None:
        """Transition to a new state with validation.
        
        Args:
            target: Target state to transition to.
            
        Raises:
            InvalidStateTransition: If the transition is not valid.
        """
        async with self._state_lock:
            if target not in VALID_TRANSITIONS.get(self._state, []):
                raise InvalidStateTransition(None, target)
            
            old_state = self._state
            self._state = target
            self._logger.info(
                "State transition: %s -> %s",
                old_state.value,
                target.value
            )
    
    async def xǁLifecycleManagerǁtransition_to__mutmut_7(self, target: ServerState) -> None:
        """Transition to a new state with validation.
        
        Args:
            target: Target state to transition to.
            
        Raises:
            InvalidStateTransition: If the transition is not valid.
        """
        async with self._state_lock:
            if target not in VALID_TRANSITIONS.get(self._state, []):
                raise InvalidStateTransition(self._state, None)
            
            old_state = self._state
            self._state = target
            self._logger.info(
                "State transition: %s -> %s",
                old_state.value,
                target.value
            )
    
    async def xǁLifecycleManagerǁtransition_to__mutmut_8(self, target: ServerState) -> None:
        """Transition to a new state with validation.
        
        Args:
            target: Target state to transition to.
            
        Raises:
            InvalidStateTransition: If the transition is not valid.
        """
        async with self._state_lock:
            if target not in VALID_TRANSITIONS.get(self._state, []):
                raise InvalidStateTransition(target)
            
            old_state = self._state
            self._state = target
            self._logger.info(
                "State transition: %s -> %s",
                old_state.value,
                target.value
            )
    
    async def xǁLifecycleManagerǁtransition_to__mutmut_9(self, target: ServerState) -> None:
        """Transition to a new state with validation.
        
        Args:
            target: Target state to transition to.
            
        Raises:
            InvalidStateTransition: If the transition is not valid.
        """
        async with self._state_lock:
            if target not in VALID_TRANSITIONS.get(self._state, []):
                raise InvalidStateTransition(self._state, )
            
            old_state = self._state
            self._state = target
            self._logger.info(
                "State transition: %s -> %s",
                old_state.value,
                target.value
            )
    
    async def xǁLifecycleManagerǁtransition_to__mutmut_10(self, target: ServerState) -> None:
        """Transition to a new state with validation.
        
        Args:
            target: Target state to transition to.
            
        Raises:
            InvalidStateTransition: If the transition is not valid.
        """
        async with self._state_lock:
            if target not in VALID_TRANSITIONS.get(self._state, []):
                raise InvalidStateTransition(self._state, target)
            
            old_state = None
            self._state = target
            self._logger.info(
                "State transition: %s -> %s",
                old_state.value,
                target.value
            )
    
    async def xǁLifecycleManagerǁtransition_to__mutmut_11(self, target: ServerState) -> None:
        """Transition to a new state with validation.
        
        Args:
            target: Target state to transition to.
            
        Raises:
            InvalidStateTransition: If the transition is not valid.
        """
        async with self._state_lock:
            if target not in VALID_TRANSITIONS.get(self._state, []):
                raise InvalidStateTransition(self._state, target)
            
            old_state = self._state
            self._state = None
            self._logger.info(
                "State transition: %s -> %s",
                old_state.value,
                target.value
            )
    
    async def xǁLifecycleManagerǁtransition_to__mutmut_12(self, target: ServerState) -> None:
        """Transition to a new state with validation.
        
        Args:
            target: Target state to transition to.
            
        Raises:
            InvalidStateTransition: If the transition is not valid.
        """
        async with self._state_lock:
            if target not in VALID_TRANSITIONS.get(self._state, []):
                raise InvalidStateTransition(self._state, target)
            
            old_state = self._state
            self._state = target
            self._logger.info(
                None,
                old_state.value,
                target.value
            )
    
    async def xǁLifecycleManagerǁtransition_to__mutmut_13(self, target: ServerState) -> None:
        """Transition to a new state with validation.
        
        Args:
            target: Target state to transition to.
            
        Raises:
            InvalidStateTransition: If the transition is not valid.
        """
        async with self._state_lock:
            if target not in VALID_TRANSITIONS.get(self._state, []):
                raise InvalidStateTransition(self._state, target)
            
            old_state = self._state
            self._state = target
            self._logger.info(
                "State transition: %s -> %s",
                None,
                target.value
            )
    
    async def xǁLifecycleManagerǁtransition_to__mutmut_14(self, target: ServerState) -> None:
        """Transition to a new state with validation.
        
        Args:
            target: Target state to transition to.
            
        Raises:
            InvalidStateTransition: If the transition is not valid.
        """
        async with self._state_lock:
            if target not in VALID_TRANSITIONS.get(self._state, []):
                raise InvalidStateTransition(self._state, target)
            
            old_state = self._state
            self._state = target
            self._logger.info(
                "State transition: %s -> %s",
                old_state.value,
                None
            )
    
    async def xǁLifecycleManagerǁtransition_to__mutmut_15(self, target: ServerState) -> None:
        """Transition to a new state with validation.
        
        Args:
            target: Target state to transition to.
            
        Raises:
            InvalidStateTransition: If the transition is not valid.
        """
        async with self._state_lock:
            if target not in VALID_TRANSITIONS.get(self._state, []):
                raise InvalidStateTransition(self._state, target)
            
            old_state = self._state
            self._state = target
            self._logger.info(
                old_state.value,
                target.value
            )
    
    async def xǁLifecycleManagerǁtransition_to__mutmut_16(self, target: ServerState) -> None:
        """Transition to a new state with validation.
        
        Args:
            target: Target state to transition to.
            
        Raises:
            InvalidStateTransition: If the transition is not valid.
        """
        async with self._state_lock:
            if target not in VALID_TRANSITIONS.get(self._state, []):
                raise InvalidStateTransition(self._state, target)
            
            old_state = self._state
            self._state = target
            self._logger.info(
                "State transition: %s -> %s",
                target.value
            )
    
    async def xǁLifecycleManagerǁtransition_to__mutmut_17(self, target: ServerState) -> None:
        """Transition to a new state with validation.
        
        Args:
            target: Target state to transition to.
            
        Raises:
            InvalidStateTransition: If the transition is not valid.
        """
        async with self._state_lock:
            if target not in VALID_TRANSITIONS.get(self._state, []):
                raise InvalidStateTransition(self._state, target)
            
            old_state = self._state
            self._state = target
            self._logger.info(
                "State transition: %s -> %s",
                old_state.value,
                )
    
    async def xǁLifecycleManagerǁtransition_to__mutmut_18(self, target: ServerState) -> None:
        """Transition to a new state with validation.
        
        Args:
            target: Target state to transition to.
            
        Raises:
            InvalidStateTransition: If the transition is not valid.
        """
        async with self._state_lock:
            if target not in VALID_TRANSITIONS.get(self._state, []):
                raise InvalidStateTransition(self._state, target)
            
            old_state = self._state
            self._state = target
            self._logger.info(
                "XXState transition: %s -> %sXX",
                old_state.value,
                target.value
            )
    
    async def xǁLifecycleManagerǁtransition_to__mutmut_19(self, target: ServerState) -> None:
        """Transition to a new state with validation.
        
        Args:
            target: Target state to transition to.
            
        Raises:
            InvalidStateTransition: If the transition is not valid.
        """
        async with self._state_lock:
            if target not in VALID_TRANSITIONS.get(self._state, []):
                raise InvalidStateTransition(self._state, target)
            
            old_state = self._state
            self._state = target
            self._logger.info(
                "state transition: %s -> %s",
                old_state.value,
                target.value
            )
    
    async def xǁLifecycleManagerǁtransition_to__mutmut_20(self, target: ServerState) -> None:
        """Transition to a new state with validation.
        
        Args:
            target: Target state to transition to.
            
        Raises:
            InvalidStateTransition: If the transition is not valid.
        """
        async with self._state_lock:
            if target not in VALID_TRANSITIONS.get(self._state, []):
                raise InvalidStateTransition(self._state, target)
            
            old_state = self._state
            self._state = target
            self._logger.info(
                "STATE TRANSITION: %S -> %S",
                old_state.value,
                target.value
            )
    
    xǁLifecycleManagerǁtransition_to__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLifecycleManagerǁtransition_to__mutmut_1': xǁLifecycleManagerǁtransition_to__mutmut_1, 
        'xǁLifecycleManagerǁtransition_to__mutmut_2': xǁLifecycleManagerǁtransition_to__mutmut_2, 
        'xǁLifecycleManagerǁtransition_to__mutmut_3': xǁLifecycleManagerǁtransition_to__mutmut_3, 
        'xǁLifecycleManagerǁtransition_to__mutmut_4': xǁLifecycleManagerǁtransition_to__mutmut_4, 
        'xǁLifecycleManagerǁtransition_to__mutmut_5': xǁLifecycleManagerǁtransition_to__mutmut_5, 
        'xǁLifecycleManagerǁtransition_to__mutmut_6': xǁLifecycleManagerǁtransition_to__mutmut_6, 
        'xǁLifecycleManagerǁtransition_to__mutmut_7': xǁLifecycleManagerǁtransition_to__mutmut_7, 
        'xǁLifecycleManagerǁtransition_to__mutmut_8': xǁLifecycleManagerǁtransition_to__mutmut_8, 
        'xǁLifecycleManagerǁtransition_to__mutmut_9': xǁLifecycleManagerǁtransition_to__mutmut_9, 
        'xǁLifecycleManagerǁtransition_to__mutmut_10': xǁLifecycleManagerǁtransition_to__mutmut_10, 
        'xǁLifecycleManagerǁtransition_to__mutmut_11': xǁLifecycleManagerǁtransition_to__mutmut_11, 
        'xǁLifecycleManagerǁtransition_to__mutmut_12': xǁLifecycleManagerǁtransition_to__mutmut_12, 
        'xǁLifecycleManagerǁtransition_to__mutmut_13': xǁLifecycleManagerǁtransition_to__mutmut_13, 
        'xǁLifecycleManagerǁtransition_to__mutmut_14': xǁLifecycleManagerǁtransition_to__mutmut_14, 
        'xǁLifecycleManagerǁtransition_to__mutmut_15': xǁLifecycleManagerǁtransition_to__mutmut_15, 
        'xǁLifecycleManagerǁtransition_to__mutmut_16': xǁLifecycleManagerǁtransition_to__mutmut_16, 
        'xǁLifecycleManagerǁtransition_to__mutmut_17': xǁLifecycleManagerǁtransition_to__mutmut_17, 
        'xǁLifecycleManagerǁtransition_to__mutmut_18': xǁLifecycleManagerǁtransition_to__mutmut_18, 
        'xǁLifecycleManagerǁtransition_to__mutmut_19': xǁLifecycleManagerǁtransition_to__mutmut_19, 
        'xǁLifecycleManagerǁtransition_to__mutmut_20': xǁLifecycleManagerǁtransition_to__mutmut_20
    }
    
    def transition_to(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLifecycleManagerǁtransition_to__mutmut_orig"), object.__getattribute__(self, "xǁLifecycleManagerǁtransition_to__mutmut_mutants"), args, kwargs, self)
        return result 
    
    transition_to.__signature__ = _mutmut_signature(xǁLifecycleManagerǁtransition_to__mutmut_orig)
    xǁLifecycleManagerǁtransition_to__mutmut_orig.__name__ = 'xǁLifecycleManagerǁtransition_to'
    
    def xǁLifecycleManagerǁregister_health_check__mutmut_orig(self, check: Callable[[], HealthStatus]) -> None:
        """Register a health check function.
        
        Args:
            check: Health check function that returns HealthStatus.
        """
        self._health_checks.append(check)
    
    def xǁLifecycleManagerǁregister_health_check__mutmut_1(self, check: Callable[[], HealthStatus]) -> None:
        """Register a health check function.
        
        Args:
            check: Health check function that returns HealthStatus.
        """
        self._health_checks.append(None)
    
    xǁLifecycleManagerǁregister_health_check__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLifecycleManagerǁregister_health_check__mutmut_1': xǁLifecycleManagerǁregister_health_check__mutmut_1
    }
    
    def register_health_check(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLifecycleManagerǁregister_health_check__mutmut_orig"), object.__getattribute__(self, "xǁLifecycleManagerǁregister_health_check__mutmut_mutants"), args, kwargs, self)
        return result 
    
    register_health_check.__signature__ = _mutmut_signature(xǁLifecycleManagerǁregister_health_check__mutmut_orig)
    xǁLifecycleManagerǁregister_health_check__mutmut_orig.__name__ = 'xǁLifecycleManagerǁregister_health_check'
    
    def xǁLifecycleManagerǁregister_startup_hook__mutmut_orig(self, hook: Callable[[], None]) -> None:
        """Register a startup hook.
        
        Args:
            hook: Function to call during startup.
        """
        self._startup_hooks.append(hook)
    
    def xǁLifecycleManagerǁregister_startup_hook__mutmut_1(self, hook: Callable[[], None]) -> None:
        """Register a startup hook.
        
        Args:
            hook: Function to call during startup.
        """
        self._startup_hooks.append(None)
    
    xǁLifecycleManagerǁregister_startup_hook__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLifecycleManagerǁregister_startup_hook__mutmut_1': xǁLifecycleManagerǁregister_startup_hook__mutmut_1
    }
    
    def register_startup_hook(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLifecycleManagerǁregister_startup_hook__mutmut_orig"), object.__getattribute__(self, "xǁLifecycleManagerǁregister_startup_hook__mutmut_mutants"), args, kwargs, self)
        return result 
    
    register_startup_hook.__signature__ = _mutmut_signature(xǁLifecycleManagerǁregister_startup_hook__mutmut_orig)
    xǁLifecycleManagerǁregister_startup_hook__mutmut_orig.__name__ = 'xǁLifecycleManagerǁregister_startup_hook'
    
    def xǁLifecycleManagerǁregister_shutdown_hook__mutmut_orig(self, hook: Callable[[], None]) -> None:
        """Register a shutdown hook.
        
        Args:
            hook: Function to call during shutdown.
        """
        self._shutdown_hooks.append(hook)
    
    def xǁLifecycleManagerǁregister_shutdown_hook__mutmut_1(self, hook: Callable[[], None]) -> None:
        """Register a shutdown hook.
        
        Args:
            hook: Function to call during shutdown.
        """
        self._shutdown_hooks.append(None)
    
    xǁLifecycleManagerǁregister_shutdown_hook__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLifecycleManagerǁregister_shutdown_hook__mutmut_1': xǁLifecycleManagerǁregister_shutdown_hook__mutmut_1
    }
    
    def register_shutdown_hook(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLifecycleManagerǁregister_shutdown_hook__mutmut_orig"), object.__getattribute__(self, "xǁLifecycleManagerǁregister_shutdown_hook__mutmut_mutants"), args, kwargs, self)
        return result 
    
    register_shutdown_hook.__signature__ = _mutmut_signature(xǁLifecycleManagerǁregister_shutdown_hook__mutmut_orig)
    xǁLifecycleManagerǁregister_shutdown_hook__mutmut_orig.__name__ = 'xǁLifecycleManagerǁregister_shutdown_hook'
    
    async def xǁLifecycleManagerǁinitialize__mutmut_orig(self) -> None:
        """Initialize the server."""
        await self.transition_to(ServerState.INITIALIZING)
        
        try:
            # Run startup hooks
            for hook in self._startup_hooks:
                hook()
            
            await self.transition_to(ServerState.READY)
            self._logger.info("Server initialized successfully")
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.error("Initialization failed: %s", e)
            await self.transition_to(ServerState.ERROR)
            raise
    
    async def xǁLifecycleManagerǁinitialize__mutmut_1(self) -> None:
        """Initialize the server."""
        await self.transition_to(None)
        
        try:
            # Run startup hooks
            for hook in self._startup_hooks:
                hook()
            
            await self.transition_to(ServerState.READY)
            self._logger.info("Server initialized successfully")
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.error("Initialization failed: %s", e)
            await self.transition_to(ServerState.ERROR)
            raise
    
    async def xǁLifecycleManagerǁinitialize__mutmut_2(self) -> None:
        """Initialize the server."""
        await self.transition_to(ServerState.INITIALIZING)
        
        try:
            # Run startup hooks
            for hook in self._startup_hooks:
                hook()
            
            await self.transition_to(None)
            self._logger.info("Server initialized successfully")
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.error("Initialization failed: %s", e)
            await self.transition_to(ServerState.ERROR)
            raise
    
    async def xǁLifecycleManagerǁinitialize__mutmut_3(self) -> None:
        """Initialize the server."""
        await self.transition_to(ServerState.INITIALIZING)
        
        try:
            # Run startup hooks
            for hook in self._startup_hooks:
                hook()
            
            await self.transition_to(ServerState.READY)
            self._logger.info(None)
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.error("Initialization failed: %s", e)
            await self.transition_to(ServerState.ERROR)
            raise
    
    async def xǁLifecycleManagerǁinitialize__mutmut_4(self) -> None:
        """Initialize the server."""
        await self.transition_to(ServerState.INITIALIZING)
        
        try:
            # Run startup hooks
            for hook in self._startup_hooks:
                hook()
            
            await self.transition_to(ServerState.READY)
            self._logger.info("XXServer initialized successfullyXX")
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.error("Initialization failed: %s", e)
            await self.transition_to(ServerState.ERROR)
            raise
    
    async def xǁLifecycleManagerǁinitialize__mutmut_5(self) -> None:
        """Initialize the server."""
        await self.transition_to(ServerState.INITIALIZING)
        
        try:
            # Run startup hooks
            for hook in self._startup_hooks:
                hook()
            
            await self.transition_to(ServerState.READY)
            self._logger.info("server initialized successfully")
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.error("Initialization failed: %s", e)
            await self.transition_to(ServerState.ERROR)
            raise
    
    async def xǁLifecycleManagerǁinitialize__mutmut_6(self) -> None:
        """Initialize the server."""
        await self.transition_to(ServerState.INITIALIZING)
        
        try:
            # Run startup hooks
            for hook in self._startup_hooks:
                hook()
            
            await self.transition_to(ServerState.READY)
            self._logger.info("SERVER INITIALIZED SUCCESSFULLY")
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.error("Initialization failed: %s", e)
            await self.transition_to(ServerState.ERROR)
            raise
    
    async def xǁLifecycleManagerǁinitialize__mutmut_7(self) -> None:
        """Initialize the server."""
        await self.transition_to(ServerState.INITIALIZING)
        
        try:
            # Run startup hooks
            for hook in self._startup_hooks:
                hook()
            
            await self.transition_to(ServerState.READY)
            self._logger.info("Server initialized successfully")
            
        except Exception as e:
            logger.debug(None)
            self._logger.error("Initialization failed: %s", e)
            await self.transition_to(ServerState.ERROR)
            raise
    
    async def xǁLifecycleManagerǁinitialize__mutmut_8(self) -> None:
        """Initialize the server."""
        await self.transition_to(ServerState.INITIALIZING)
        
        try:
            # Run startup hooks
            for hook in self._startup_hooks:
                hook()
            
            await self.transition_to(ServerState.READY)
            self._logger.info("Server initialized successfully")
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.error(None, e)
            await self.transition_to(ServerState.ERROR)
            raise
    
    async def xǁLifecycleManagerǁinitialize__mutmut_9(self) -> None:
        """Initialize the server."""
        await self.transition_to(ServerState.INITIALIZING)
        
        try:
            # Run startup hooks
            for hook in self._startup_hooks:
                hook()
            
            await self.transition_to(ServerState.READY)
            self._logger.info("Server initialized successfully")
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.error("Initialization failed: %s", None)
            await self.transition_to(ServerState.ERROR)
            raise
    
    async def xǁLifecycleManagerǁinitialize__mutmut_10(self) -> None:
        """Initialize the server."""
        await self.transition_to(ServerState.INITIALIZING)
        
        try:
            # Run startup hooks
            for hook in self._startup_hooks:
                hook()
            
            await self.transition_to(ServerState.READY)
            self._logger.info("Server initialized successfully")
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.error(e)
            await self.transition_to(ServerState.ERROR)
            raise
    
    async def xǁLifecycleManagerǁinitialize__mutmut_11(self) -> None:
        """Initialize the server."""
        await self.transition_to(ServerState.INITIALIZING)
        
        try:
            # Run startup hooks
            for hook in self._startup_hooks:
                hook()
            
            await self.transition_to(ServerState.READY)
            self._logger.info("Server initialized successfully")
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.error("Initialization failed: %s", )
            await self.transition_to(ServerState.ERROR)
            raise
    
    async def xǁLifecycleManagerǁinitialize__mutmut_12(self) -> None:
        """Initialize the server."""
        await self.transition_to(ServerState.INITIALIZING)
        
        try:
            # Run startup hooks
            for hook in self._startup_hooks:
                hook()
            
            await self.transition_to(ServerState.READY)
            self._logger.info("Server initialized successfully")
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.error("XXInitialization failed: %sXX", e)
            await self.transition_to(ServerState.ERROR)
            raise
    
    async def xǁLifecycleManagerǁinitialize__mutmut_13(self) -> None:
        """Initialize the server."""
        await self.transition_to(ServerState.INITIALIZING)
        
        try:
            # Run startup hooks
            for hook in self._startup_hooks:
                hook()
            
            await self.transition_to(ServerState.READY)
            self._logger.info("Server initialized successfully")
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.error("initialization failed: %s", e)
            await self.transition_to(ServerState.ERROR)
            raise
    
    async def xǁLifecycleManagerǁinitialize__mutmut_14(self) -> None:
        """Initialize the server."""
        await self.transition_to(ServerState.INITIALIZING)
        
        try:
            # Run startup hooks
            for hook in self._startup_hooks:
                hook()
            
            await self.transition_to(ServerState.READY)
            self._logger.info("Server initialized successfully")
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.error("INITIALIZATION FAILED: %S", e)
            await self.transition_to(ServerState.ERROR)
            raise
    
    async def xǁLifecycleManagerǁinitialize__mutmut_15(self) -> None:
        """Initialize the server."""
        await self.transition_to(ServerState.INITIALIZING)
        
        try:
            # Run startup hooks
            for hook in self._startup_hooks:
                hook()
            
            await self.transition_to(ServerState.READY)
            self._logger.info("Server initialized successfully")
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.error("Initialization failed: %s", e)
            await self.transition_to(None)
            raise
    
    xǁLifecycleManagerǁinitialize__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLifecycleManagerǁinitialize__mutmut_1': xǁLifecycleManagerǁinitialize__mutmut_1, 
        'xǁLifecycleManagerǁinitialize__mutmut_2': xǁLifecycleManagerǁinitialize__mutmut_2, 
        'xǁLifecycleManagerǁinitialize__mutmut_3': xǁLifecycleManagerǁinitialize__mutmut_3, 
        'xǁLifecycleManagerǁinitialize__mutmut_4': xǁLifecycleManagerǁinitialize__mutmut_4, 
        'xǁLifecycleManagerǁinitialize__mutmut_5': xǁLifecycleManagerǁinitialize__mutmut_5, 
        'xǁLifecycleManagerǁinitialize__mutmut_6': xǁLifecycleManagerǁinitialize__mutmut_6, 
        'xǁLifecycleManagerǁinitialize__mutmut_7': xǁLifecycleManagerǁinitialize__mutmut_7, 
        'xǁLifecycleManagerǁinitialize__mutmut_8': xǁLifecycleManagerǁinitialize__mutmut_8, 
        'xǁLifecycleManagerǁinitialize__mutmut_9': xǁLifecycleManagerǁinitialize__mutmut_9, 
        'xǁLifecycleManagerǁinitialize__mutmut_10': xǁLifecycleManagerǁinitialize__mutmut_10, 
        'xǁLifecycleManagerǁinitialize__mutmut_11': xǁLifecycleManagerǁinitialize__mutmut_11, 
        'xǁLifecycleManagerǁinitialize__mutmut_12': xǁLifecycleManagerǁinitialize__mutmut_12, 
        'xǁLifecycleManagerǁinitialize__mutmut_13': xǁLifecycleManagerǁinitialize__mutmut_13, 
        'xǁLifecycleManagerǁinitialize__mutmut_14': xǁLifecycleManagerǁinitialize__mutmut_14, 
        'xǁLifecycleManagerǁinitialize__mutmut_15': xǁLifecycleManagerǁinitialize__mutmut_15
    }
    
    def initialize(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLifecycleManagerǁinitialize__mutmut_orig"), object.__getattribute__(self, "xǁLifecycleManagerǁinitialize__mutmut_mutants"), args, kwargs, self)
        return result 
    
    initialize.__signature__ = _mutmut_signature(xǁLifecycleManagerǁinitialize__mutmut_orig)
    xǁLifecycleManagerǁinitialize__mutmut_orig.__name__ = 'xǁLifecycleManagerǁinitialize'
    
    async def xǁLifecycleManagerǁstart__mutmut_orig(self) -> None:
        """Start accepting requests."""
        if self._state != ServerState.READY:
            raise InvalidStateTransition(self._state, ServerState.RUNNING)
        
        await self.transition_to(ServerState.RUNNING)
        self._logger.info("Server started and accepting requests")
    
    async def xǁLifecycleManagerǁstart__mutmut_1(self) -> None:
        """Start accepting requests."""
        if self._state == ServerState.READY:
            raise InvalidStateTransition(self._state, ServerState.RUNNING)
        
        await self.transition_to(ServerState.RUNNING)
        self._logger.info("Server started and accepting requests")
    
    async def xǁLifecycleManagerǁstart__mutmut_2(self) -> None:
        """Start accepting requests."""
        if self._state != ServerState.READY:
            raise InvalidStateTransition(None, ServerState.RUNNING)
        
        await self.transition_to(ServerState.RUNNING)
        self._logger.info("Server started and accepting requests")
    
    async def xǁLifecycleManagerǁstart__mutmut_3(self) -> None:
        """Start accepting requests."""
        if self._state != ServerState.READY:
            raise InvalidStateTransition(self._state, None)
        
        await self.transition_to(ServerState.RUNNING)
        self._logger.info("Server started and accepting requests")
    
    async def xǁLifecycleManagerǁstart__mutmut_4(self) -> None:
        """Start accepting requests."""
        if self._state != ServerState.READY:
            raise InvalidStateTransition(ServerState.RUNNING)
        
        await self.transition_to(ServerState.RUNNING)
        self._logger.info("Server started and accepting requests")
    
    async def xǁLifecycleManagerǁstart__mutmut_5(self) -> None:
        """Start accepting requests."""
        if self._state != ServerState.READY:
            raise InvalidStateTransition(self._state, )
        
        await self.transition_to(ServerState.RUNNING)
        self._logger.info("Server started and accepting requests")
    
    async def xǁLifecycleManagerǁstart__mutmut_6(self) -> None:
        """Start accepting requests."""
        if self._state != ServerState.READY:
            raise InvalidStateTransition(self._state, ServerState.RUNNING)
        
        await self.transition_to(None)
        self._logger.info("Server started and accepting requests")
    
    async def xǁLifecycleManagerǁstart__mutmut_7(self) -> None:
        """Start accepting requests."""
        if self._state != ServerState.READY:
            raise InvalidStateTransition(self._state, ServerState.RUNNING)
        
        await self.transition_to(ServerState.RUNNING)
        self._logger.info(None)
    
    async def xǁLifecycleManagerǁstart__mutmut_8(self) -> None:
        """Start accepting requests."""
        if self._state != ServerState.READY:
            raise InvalidStateTransition(self._state, ServerState.RUNNING)
        
        await self.transition_to(ServerState.RUNNING)
        self._logger.info("XXServer started and accepting requestsXX")
    
    async def xǁLifecycleManagerǁstart__mutmut_9(self) -> None:
        """Start accepting requests."""
        if self._state != ServerState.READY:
            raise InvalidStateTransition(self._state, ServerState.RUNNING)
        
        await self.transition_to(ServerState.RUNNING)
        self._logger.info("server started and accepting requests")
    
    async def xǁLifecycleManagerǁstart__mutmut_10(self) -> None:
        """Start accepting requests."""
        if self._state != ServerState.READY:
            raise InvalidStateTransition(self._state, ServerState.RUNNING)
        
        await self.transition_to(ServerState.RUNNING)
        self._logger.info("SERVER STARTED AND ACCEPTING REQUESTS")
    
    xǁLifecycleManagerǁstart__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLifecycleManagerǁstart__mutmut_1': xǁLifecycleManagerǁstart__mutmut_1, 
        'xǁLifecycleManagerǁstart__mutmut_2': xǁLifecycleManagerǁstart__mutmut_2, 
        'xǁLifecycleManagerǁstart__mutmut_3': xǁLifecycleManagerǁstart__mutmut_3, 
        'xǁLifecycleManagerǁstart__mutmut_4': xǁLifecycleManagerǁstart__mutmut_4, 
        'xǁLifecycleManagerǁstart__mutmut_5': xǁLifecycleManagerǁstart__mutmut_5, 
        'xǁLifecycleManagerǁstart__mutmut_6': xǁLifecycleManagerǁstart__mutmut_6, 
        'xǁLifecycleManagerǁstart__mutmut_7': xǁLifecycleManagerǁstart__mutmut_7, 
        'xǁLifecycleManagerǁstart__mutmut_8': xǁLifecycleManagerǁstart__mutmut_8, 
        'xǁLifecycleManagerǁstart__mutmut_9': xǁLifecycleManagerǁstart__mutmut_9, 
        'xǁLifecycleManagerǁstart__mutmut_10': xǁLifecycleManagerǁstart__mutmut_10
    }
    
    def start(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLifecycleManagerǁstart__mutmut_orig"), object.__getattribute__(self, "xǁLifecycleManagerǁstart__mutmut_mutants"), args, kwargs, self)
        return result 
    
    start.__signature__ = _mutmut_signature(xǁLifecycleManagerǁstart__mutmut_orig)
    xǁLifecycleManagerǁstart__mutmut_orig.__name__ = 'xǁLifecycleManagerǁstart'
    
    async def xǁLifecycleManagerǁshutdown__mutmut_orig(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_1(self, graceful: bool = False) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_2(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful or self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_3(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state != ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_4(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(None)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_5(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = None
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_6(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests >= 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_7(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 1:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_8(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() + drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_9(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start >= self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_10(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        None,
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_11(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        None
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_12(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_13(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_14(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "XXDrain timeout reached with %d active requestsXX",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_15(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_16(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "DRAIN TIMEOUT REACHED WITH %D ACTIVE REQUESTS",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_17(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    return
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_18(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(None)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_19(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(1.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_20(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(None)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_21(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(None)
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_22(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error(None, e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_23(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", None)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_24(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error(e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_25(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", )
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_26(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("XXShutdown hook failed: %sXX", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_27(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_28(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("SHUTDOWN HOOK FAILED: %S", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_29(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(None)
        self._shutdown_event.set()
        self._logger.info("Server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_30(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info(None)
    
    async def xǁLifecycleManagerǁshutdown__mutmut_31(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("XXServer shutdown completeXX")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_32(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("server shutdown complete")
    
    async def xǁLifecycleManagerǁshutdown__mutmut_33(self, graceful: bool = True) -> None:
        """Shutdown the server.
        
        Args:
            graceful: If True, wait for active requests to complete.
        """
        if graceful and self._state == ServerState.RUNNING:
            await self.transition_to(ServerState.DRAINING)
            
            # Wait for active requests with timeout
            drain_start = time.time()
            while self._active_requests > 0:
                if time.time() - drain_start > self._config.drain_timeout_seconds:
                    self._logger.warning(
                        "Drain timeout reached with %d active requests",
                        self._active_requests
                    )
                    break
                await asyncio.sleep(0.1)
        
        await self.transition_to(ServerState.STOPPING)
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                self._logger.error("Shutdown hook failed: %s", e)
        
        await self.transition_to(ServerState.STOPPED)
        self._shutdown_event.set()
        self._logger.info("SERVER SHUTDOWN COMPLETE")
    
    xǁLifecycleManagerǁshutdown__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLifecycleManagerǁshutdown__mutmut_1': xǁLifecycleManagerǁshutdown__mutmut_1, 
        'xǁLifecycleManagerǁshutdown__mutmut_2': xǁLifecycleManagerǁshutdown__mutmut_2, 
        'xǁLifecycleManagerǁshutdown__mutmut_3': xǁLifecycleManagerǁshutdown__mutmut_3, 
        'xǁLifecycleManagerǁshutdown__mutmut_4': xǁLifecycleManagerǁshutdown__mutmut_4, 
        'xǁLifecycleManagerǁshutdown__mutmut_5': xǁLifecycleManagerǁshutdown__mutmut_5, 
        'xǁLifecycleManagerǁshutdown__mutmut_6': xǁLifecycleManagerǁshutdown__mutmut_6, 
        'xǁLifecycleManagerǁshutdown__mutmut_7': xǁLifecycleManagerǁshutdown__mutmut_7, 
        'xǁLifecycleManagerǁshutdown__mutmut_8': xǁLifecycleManagerǁshutdown__mutmut_8, 
        'xǁLifecycleManagerǁshutdown__mutmut_9': xǁLifecycleManagerǁshutdown__mutmut_9, 
        'xǁLifecycleManagerǁshutdown__mutmut_10': xǁLifecycleManagerǁshutdown__mutmut_10, 
        'xǁLifecycleManagerǁshutdown__mutmut_11': xǁLifecycleManagerǁshutdown__mutmut_11, 
        'xǁLifecycleManagerǁshutdown__mutmut_12': xǁLifecycleManagerǁshutdown__mutmut_12, 
        'xǁLifecycleManagerǁshutdown__mutmut_13': xǁLifecycleManagerǁshutdown__mutmut_13, 
        'xǁLifecycleManagerǁshutdown__mutmut_14': xǁLifecycleManagerǁshutdown__mutmut_14, 
        'xǁLifecycleManagerǁshutdown__mutmut_15': xǁLifecycleManagerǁshutdown__mutmut_15, 
        'xǁLifecycleManagerǁshutdown__mutmut_16': xǁLifecycleManagerǁshutdown__mutmut_16, 
        'xǁLifecycleManagerǁshutdown__mutmut_17': xǁLifecycleManagerǁshutdown__mutmut_17, 
        'xǁLifecycleManagerǁshutdown__mutmut_18': xǁLifecycleManagerǁshutdown__mutmut_18, 
        'xǁLifecycleManagerǁshutdown__mutmut_19': xǁLifecycleManagerǁshutdown__mutmut_19, 
        'xǁLifecycleManagerǁshutdown__mutmut_20': xǁLifecycleManagerǁshutdown__mutmut_20, 
        'xǁLifecycleManagerǁshutdown__mutmut_21': xǁLifecycleManagerǁshutdown__mutmut_21, 
        'xǁLifecycleManagerǁshutdown__mutmut_22': xǁLifecycleManagerǁshutdown__mutmut_22, 
        'xǁLifecycleManagerǁshutdown__mutmut_23': xǁLifecycleManagerǁshutdown__mutmut_23, 
        'xǁLifecycleManagerǁshutdown__mutmut_24': xǁLifecycleManagerǁshutdown__mutmut_24, 
        'xǁLifecycleManagerǁshutdown__mutmut_25': xǁLifecycleManagerǁshutdown__mutmut_25, 
        'xǁLifecycleManagerǁshutdown__mutmut_26': xǁLifecycleManagerǁshutdown__mutmut_26, 
        'xǁLifecycleManagerǁshutdown__mutmut_27': xǁLifecycleManagerǁshutdown__mutmut_27, 
        'xǁLifecycleManagerǁshutdown__mutmut_28': xǁLifecycleManagerǁshutdown__mutmut_28, 
        'xǁLifecycleManagerǁshutdown__mutmut_29': xǁLifecycleManagerǁshutdown__mutmut_29, 
        'xǁLifecycleManagerǁshutdown__mutmut_30': xǁLifecycleManagerǁshutdown__mutmut_30, 
        'xǁLifecycleManagerǁshutdown__mutmut_31': xǁLifecycleManagerǁshutdown__mutmut_31, 
        'xǁLifecycleManagerǁshutdown__mutmut_32': xǁLifecycleManagerǁshutdown__mutmut_32, 
        'xǁLifecycleManagerǁshutdown__mutmut_33': xǁLifecycleManagerǁshutdown__mutmut_33
    }
    
    def shutdown(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLifecycleManagerǁshutdown__mutmut_orig"), object.__getattribute__(self, "xǁLifecycleManagerǁshutdown__mutmut_mutants"), args, kwargs, self)
        return result 
    
    shutdown.__signature__ = _mutmut_signature(xǁLifecycleManagerǁshutdown__mutmut_orig)
    xǁLifecycleManagerǁshutdown__mutmut_orig.__name__ = 'xǁLifecycleManagerǁshutdown'
    
    async def xǁLifecycleManagerǁtrack_request_start__mutmut_orig(self) -> bool:
        """Track the start of a request.
        
        Returns:
            True if the request can proceed, False if server is draining.
        """
        if not self.is_accepting_requests:
            return False
        
        async with self._requests_lock:
            if self._active_requests >= self._config.max_concurrent_requests:
                return False
            self._active_requests += 1
        return True
    
    async def xǁLifecycleManagerǁtrack_request_start__mutmut_1(self) -> bool:
        """Track the start of a request.
        
        Returns:
            True if the request can proceed, False if server is draining.
        """
        if self.is_accepting_requests:
            return False
        
        async with self._requests_lock:
            if self._active_requests >= self._config.max_concurrent_requests:
                return False
            self._active_requests += 1
        return True
    
    async def xǁLifecycleManagerǁtrack_request_start__mutmut_2(self) -> bool:
        """Track the start of a request.
        
        Returns:
            True if the request can proceed, False if server is draining.
        """
        if not self.is_accepting_requests:
            return True
        
        async with self._requests_lock:
            if self._active_requests >= self._config.max_concurrent_requests:
                return False
            self._active_requests += 1
        return True
    
    async def xǁLifecycleManagerǁtrack_request_start__mutmut_3(self) -> bool:
        """Track the start of a request.
        
        Returns:
            True if the request can proceed, False if server is draining.
        """
        if not self.is_accepting_requests:
            return False
        
        async with self._requests_lock:
            if self._active_requests > self._config.max_concurrent_requests:
                return False
            self._active_requests += 1
        return True
    
    async def xǁLifecycleManagerǁtrack_request_start__mutmut_4(self) -> bool:
        """Track the start of a request.
        
        Returns:
            True if the request can proceed, False if server is draining.
        """
        if not self.is_accepting_requests:
            return False
        
        async with self._requests_lock:
            if self._active_requests >= self._config.max_concurrent_requests:
                return True
            self._active_requests += 1
        return True
    
    async def xǁLifecycleManagerǁtrack_request_start__mutmut_5(self) -> bool:
        """Track the start of a request.
        
        Returns:
            True if the request can proceed, False if server is draining.
        """
        if not self.is_accepting_requests:
            return False
        
        async with self._requests_lock:
            if self._active_requests >= self._config.max_concurrent_requests:
                return False
            self._active_requests = 1
        return True
    
    async def xǁLifecycleManagerǁtrack_request_start__mutmut_6(self) -> bool:
        """Track the start of a request.
        
        Returns:
            True if the request can proceed, False if server is draining.
        """
        if not self.is_accepting_requests:
            return False
        
        async with self._requests_lock:
            if self._active_requests >= self._config.max_concurrent_requests:
                return False
            self._active_requests -= 1
        return True
    
    async def xǁLifecycleManagerǁtrack_request_start__mutmut_7(self) -> bool:
        """Track the start of a request.
        
        Returns:
            True if the request can proceed, False if server is draining.
        """
        if not self.is_accepting_requests:
            return False
        
        async with self._requests_lock:
            if self._active_requests >= self._config.max_concurrent_requests:
                return False
            self._active_requests += 2
        return True
    
    async def xǁLifecycleManagerǁtrack_request_start__mutmut_8(self) -> bool:
        """Track the start of a request.
        
        Returns:
            True if the request can proceed, False if server is draining.
        """
        if not self.is_accepting_requests:
            return False
        
        async with self._requests_lock:
            if self._active_requests >= self._config.max_concurrent_requests:
                return False
            self._active_requests += 1
        return False
    
    xǁLifecycleManagerǁtrack_request_start__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLifecycleManagerǁtrack_request_start__mutmut_1': xǁLifecycleManagerǁtrack_request_start__mutmut_1, 
        'xǁLifecycleManagerǁtrack_request_start__mutmut_2': xǁLifecycleManagerǁtrack_request_start__mutmut_2, 
        'xǁLifecycleManagerǁtrack_request_start__mutmut_3': xǁLifecycleManagerǁtrack_request_start__mutmut_3, 
        'xǁLifecycleManagerǁtrack_request_start__mutmut_4': xǁLifecycleManagerǁtrack_request_start__mutmut_4, 
        'xǁLifecycleManagerǁtrack_request_start__mutmut_5': xǁLifecycleManagerǁtrack_request_start__mutmut_5, 
        'xǁLifecycleManagerǁtrack_request_start__mutmut_6': xǁLifecycleManagerǁtrack_request_start__mutmut_6, 
        'xǁLifecycleManagerǁtrack_request_start__mutmut_7': xǁLifecycleManagerǁtrack_request_start__mutmut_7, 
        'xǁLifecycleManagerǁtrack_request_start__mutmut_8': xǁLifecycleManagerǁtrack_request_start__mutmut_8
    }
    
    def track_request_start(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLifecycleManagerǁtrack_request_start__mutmut_orig"), object.__getattribute__(self, "xǁLifecycleManagerǁtrack_request_start__mutmut_mutants"), args, kwargs, self)
        return result 
    
    track_request_start.__signature__ = _mutmut_signature(xǁLifecycleManagerǁtrack_request_start__mutmut_orig)
    xǁLifecycleManagerǁtrack_request_start__mutmut_orig.__name__ = 'xǁLifecycleManagerǁtrack_request_start'
    
    async def xǁLifecycleManagerǁtrack_request_end__mutmut_orig(self) -> None:
        """Track the end of a request."""
        async with self._requests_lock:
            self._active_requests = max(0, self._active_requests - 1)
    
    async def xǁLifecycleManagerǁtrack_request_end__mutmut_1(self) -> None:
        """Track the end of a request."""
        async with self._requests_lock:
            self._active_requests = None
    
    async def xǁLifecycleManagerǁtrack_request_end__mutmut_2(self) -> None:
        """Track the end of a request."""
        async with self._requests_lock:
            self._active_requests = max(None, self._active_requests - 1)
    
    async def xǁLifecycleManagerǁtrack_request_end__mutmut_3(self) -> None:
        """Track the end of a request."""
        async with self._requests_lock:
            self._active_requests = max(0, None)
    
    async def xǁLifecycleManagerǁtrack_request_end__mutmut_4(self) -> None:
        """Track the end of a request."""
        async with self._requests_lock:
            self._active_requests = max(self._active_requests - 1)
    
    async def xǁLifecycleManagerǁtrack_request_end__mutmut_5(self) -> None:
        """Track the end of a request."""
        async with self._requests_lock:
            self._active_requests = max(0, )
    
    async def xǁLifecycleManagerǁtrack_request_end__mutmut_6(self) -> None:
        """Track the end of a request."""
        async with self._requests_lock:
            self._active_requests = max(1, self._active_requests - 1)
    
    async def xǁLifecycleManagerǁtrack_request_end__mutmut_7(self) -> None:
        """Track the end of a request."""
        async with self._requests_lock:
            self._active_requests = max(0, self._active_requests + 1)
    
    async def xǁLifecycleManagerǁtrack_request_end__mutmut_8(self) -> None:
        """Track the end of a request."""
        async with self._requests_lock:
            self._active_requests = max(0, self._active_requests - 2)
    
    xǁLifecycleManagerǁtrack_request_end__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLifecycleManagerǁtrack_request_end__mutmut_1': xǁLifecycleManagerǁtrack_request_end__mutmut_1, 
        'xǁLifecycleManagerǁtrack_request_end__mutmut_2': xǁLifecycleManagerǁtrack_request_end__mutmut_2, 
        'xǁLifecycleManagerǁtrack_request_end__mutmut_3': xǁLifecycleManagerǁtrack_request_end__mutmut_3, 
        'xǁLifecycleManagerǁtrack_request_end__mutmut_4': xǁLifecycleManagerǁtrack_request_end__mutmut_4, 
        'xǁLifecycleManagerǁtrack_request_end__mutmut_5': xǁLifecycleManagerǁtrack_request_end__mutmut_5, 
        'xǁLifecycleManagerǁtrack_request_end__mutmut_6': xǁLifecycleManagerǁtrack_request_end__mutmut_6, 
        'xǁLifecycleManagerǁtrack_request_end__mutmut_7': xǁLifecycleManagerǁtrack_request_end__mutmut_7, 
        'xǁLifecycleManagerǁtrack_request_end__mutmut_8': xǁLifecycleManagerǁtrack_request_end__mutmut_8
    }
    
    def track_request_end(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLifecycleManagerǁtrack_request_end__mutmut_orig"), object.__getattribute__(self, "xǁLifecycleManagerǁtrack_request_end__mutmut_mutants"), args, kwargs, self)
        return result 
    
    track_request_end.__signature__ = _mutmut_signature(xǁLifecycleManagerǁtrack_request_end__mutmut_orig)
    xǁLifecycleManagerǁtrack_request_end__mutmut_orig.__name__ = 'xǁLifecycleManagerǁtrack_request_end'
    
    def xǁLifecycleManagerǁget_health__mutmut_orig(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_1(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_2(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=None,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_3(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=None,
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_4(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details=None
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_5(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_6(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_7(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_8(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=True,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_9(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"XXstateXX": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_10(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"STATE": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_11(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = None
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_12(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = False
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_13(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = None
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_14(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"XXstateXX": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_15(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"STATE": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_16(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = None
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_17(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(None):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_18(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = None
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_19(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = None
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_20(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "XXhealthyXX": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_21(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "HEALTHY": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_22(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "XXmessageXX": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_23(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "MESSAGE": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_24(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_25(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = None
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_26(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = True
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_27(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(None)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_28(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(None)
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_29(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = None
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_30(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = True
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_31(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = None
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_32(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"XXhealthyXX": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_33(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"HEALTHY": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_34(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": True, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_35(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "XXerrorXX": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_36(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "ERROR": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_37(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(None)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_38(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(None)
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_39(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=None,
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_40(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message=None,
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_41(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            details=None
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_42(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            message="; ".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_43(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_44(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "All checks passed",
            )
    
    def xǁLifecycleManagerǁget_health__mutmut_45(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(None) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_46(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="XX; XX".join(messages) if messages else "All checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_47(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "XXAll checks passedXX",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_48(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "all checks passed",
            details=details
        )
    
    def xǁLifecycleManagerǁget_health__mutmut_49(self) -> HealthStatus:
        """Get aggregated health status.
        
        Returns:
            Aggregated health status from all registered checks.
        """
        if not self.is_healthy:
            return HealthStatus(
                healthy=False,
                message=f"Server in {self._state.value} state",
                details={"state": self._state.value}
            )
        
        all_healthy = True
        details: dict[str, Any] = {"state": self._state.value}
        messages: list[str] = []
        
        for i, check in enumerate(self._health_checks):
            try:
                result = check()
                details[f"check_{i}"] = {
                    "healthy": result.healthy,
                    "message": result.message
                }
                if not result.healthy:
                    all_healthy = False
                    messages.append(result.message)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                all_healthy = False
                details[f"check_{i}"] = {"healthy": False, "error": str(e)}
                messages.append(f"Check {i} failed: {e}")
        
        return HealthStatus(
            healthy=all_healthy,
            message="; ".join(messages) if messages else "ALL CHECKS PASSED",
            details=details
        )
    
    xǁLifecycleManagerǁget_health__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLifecycleManagerǁget_health__mutmut_1': xǁLifecycleManagerǁget_health__mutmut_1, 
        'xǁLifecycleManagerǁget_health__mutmut_2': xǁLifecycleManagerǁget_health__mutmut_2, 
        'xǁLifecycleManagerǁget_health__mutmut_3': xǁLifecycleManagerǁget_health__mutmut_3, 
        'xǁLifecycleManagerǁget_health__mutmut_4': xǁLifecycleManagerǁget_health__mutmut_4, 
        'xǁLifecycleManagerǁget_health__mutmut_5': xǁLifecycleManagerǁget_health__mutmut_5, 
        'xǁLifecycleManagerǁget_health__mutmut_6': xǁLifecycleManagerǁget_health__mutmut_6, 
        'xǁLifecycleManagerǁget_health__mutmut_7': xǁLifecycleManagerǁget_health__mutmut_7, 
        'xǁLifecycleManagerǁget_health__mutmut_8': xǁLifecycleManagerǁget_health__mutmut_8, 
        'xǁLifecycleManagerǁget_health__mutmut_9': xǁLifecycleManagerǁget_health__mutmut_9, 
        'xǁLifecycleManagerǁget_health__mutmut_10': xǁLifecycleManagerǁget_health__mutmut_10, 
        'xǁLifecycleManagerǁget_health__mutmut_11': xǁLifecycleManagerǁget_health__mutmut_11, 
        'xǁLifecycleManagerǁget_health__mutmut_12': xǁLifecycleManagerǁget_health__mutmut_12, 
        'xǁLifecycleManagerǁget_health__mutmut_13': xǁLifecycleManagerǁget_health__mutmut_13, 
        'xǁLifecycleManagerǁget_health__mutmut_14': xǁLifecycleManagerǁget_health__mutmut_14, 
        'xǁLifecycleManagerǁget_health__mutmut_15': xǁLifecycleManagerǁget_health__mutmut_15, 
        'xǁLifecycleManagerǁget_health__mutmut_16': xǁLifecycleManagerǁget_health__mutmut_16, 
        'xǁLifecycleManagerǁget_health__mutmut_17': xǁLifecycleManagerǁget_health__mutmut_17, 
        'xǁLifecycleManagerǁget_health__mutmut_18': xǁLifecycleManagerǁget_health__mutmut_18, 
        'xǁLifecycleManagerǁget_health__mutmut_19': xǁLifecycleManagerǁget_health__mutmut_19, 
        'xǁLifecycleManagerǁget_health__mutmut_20': xǁLifecycleManagerǁget_health__mutmut_20, 
        'xǁLifecycleManagerǁget_health__mutmut_21': xǁLifecycleManagerǁget_health__mutmut_21, 
        'xǁLifecycleManagerǁget_health__mutmut_22': xǁLifecycleManagerǁget_health__mutmut_22, 
        'xǁLifecycleManagerǁget_health__mutmut_23': xǁLifecycleManagerǁget_health__mutmut_23, 
        'xǁLifecycleManagerǁget_health__mutmut_24': xǁLifecycleManagerǁget_health__mutmut_24, 
        'xǁLifecycleManagerǁget_health__mutmut_25': xǁLifecycleManagerǁget_health__mutmut_25, 
        'xǁLifecycleManagerǁget_health__mutmut_26': xǁLifecycleManagerǁget_health__mutmut_26, 
        'xǁLifecycleManagerǁget_health__mutmut_27': xǁLifecycleManagerǁget_health__mutmut_27, 
        'xǁLifecycleManagerǁget_health__mutmut_28': xǁLifecycleManagerǁget_health__mutmut_28, 
        'xǁLifecycleManagerǁget_health__mutmut_29': xǁLifecycleManagerǁget_health__mutmut_29, 
        'xǁLifecycleManagerǁget_health__mutmut_30': xǁLifecycleManagerǁget_health__mutmut_30, 
        'xǁLifecycleManagerǁget_health__mutmut_31': xǁLifecycleManagerǁget_health__mutmut_31, 
        'xǁLifecycleManagerǁget_health__mutmut_32': xǁLifecycleManagerǁget_health__mutmut_32, 
        'xǁLifecycleManagerǁget_health__mutmut_33': xǁLifecycleManagerǁget_health__mutmut_33, 
        'xǁLifecycleManagerǁget_health__mutmut_34': xǁLifecycleManagerǁget_health__mutmut_34, 
        'xǁLifecycleManagerǁget_health__mutmut_35': xǁLifecycleManagerǁget_health__mutmut_35, 
        'xǁLifecycleManagerǁget_health__mutmut_36': xǁLifecycleManagerǁget_health__mutmut_36, 
        'xǁLifecycleManagerǁget_health__mutmut_37': xǁLifecycleManagerǁget_health__mutmut_37, 
        'xǁLifecycleManagerǁget_health__mutmut_38': xǁLifecycleManagerǁget_health__mutmut_38, 
        'xǁLifecycleManagerǁget_health__mutmut_39': xǁLifecycleManagerǁget_health__mutmut_39, 
        'xǁLifecycleManagerǁget_health__mutmut_40': xǁLifecycleManagerǁget_health__mutmut_40, 
        'xǁLifecycleManagerǁget_health__mutmut_41': xǁLifecycleManagerǁget_health__mutmut_41, 
        'xǁLifecycleManagerǁget_health__mutmut_42': xǁLifecycleManagerǁget_health__mutmut_42, 
        'xǁLifecycleManagerǁget_health__mutmut_43': xǁLifecycleManagerǁget_health__mutmut_43, 
        'xǁLifecycleManagerǁget_health__mutmut_44': xǁLifecycleManagerǁget_health__mutmut_44, 
        'xǁLifecycleManagerǁget_health__mutmut_45': xǁLifecycleManagerǁget_health__mutmut_45, 
        'xǁLifecycleManagerǁget_health__mutmut_46': xǁLifecycleManagerǁget_health__mutmut_46, 
        'xǁLifecycleManagerǁget_health__mutmut_47': xǁLifecycleManagerǁget_health__mutmut_47, 
        'xǁLifecycleManagerǁget_health__mutmut_48': xǁLifecycleManagerǁget_health__mutmut_48, 
        'xǁLifecycleManagerǁget_health__mutmut_49': xǁLifecycleManagerǁget_health__mutmut_49
    }
    
    def get_health(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLifecycleManagerǁget_health__mutmut_orig"), object.__getattribute__(self, "xǁLifecycleManagerǁget_health__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_health.__signature__ = _mutmut_signature(xǁLifecycleManagerǁget_health__mutmut_orig)
    xǁLifecycleManagerǁget_health__mutmut_orig.__name__ = 'xǁLifecycleManagerǁget_health'
    
    async def wait_for_shutdown(self) -> None:
        """Wait for shutdown to complete."""
        await self._shutdown_event.wait()
    
    def xǁLifecycleManagerǁsetup_signal_handlers__mutmut_orig(self) -> None:
        """set up signal handlers for graceful shutdown."""
        loop = asyncio.get_event_loop()
        
        for sig in (signal.SIGTERM, signal.SIGINT):
            # Capture sig in lambda to avoid closure issue
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(self.shutdown(graceful=True))
            )
        
        self._logger.info("Signal handlers configured")
    
    def xǁLifecycleManagerǁsetup_signal_handlers__mutmut_1(self) -> None:
        """set up signal handlers for graceful shutdown."""
        loop = None
        
        for sig in (signal.SIGTERM, signal.SIGINT):
            # Capture sig in lambda to avoid closure issue
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(self.shutdown(graceful=True))
            )
        
        self._logger.info("Signal handlers configured")
    
    def xǁLifecycleManagerǁsetup_signal_handlers__mutmut_2(self) -> None:
        """set up signal handlers for graceful shutdown."""
        loop = asyncio.get_event_loop()
        
        for sig in (signal.SIGTERM, signal.SIGINT):
            # Capture sig in lambda to avoid closure issue
            loop.add_signal_handler(
                None,
                lambda s=sig: asyncio.create_task(self.shutdown(graceful=True))
            )
        
        self._logger.info("Signal handlers configured")
    
    def xǁLifecycleManagerǁsetup_signal_handlers__mutmut_3(self) -> None:
        """set up signal handlers for graceful shutdown."""
        loop = asyncio.get_event_loop()
        
        for sig in (signal.SIGTERM, signal.SIGINT):
            # Capture sig in lambda to avoid closure issue
            loop.add_signal_handler(
                sig,
                None
            )
        
        self._logger.info("Signal handlers configured")
    
    def xǁLifecycleManagerǁsetup_signal_handlers__mutmut_4(self) -> None:
        """set up signal handlers for graceful shutdown."""
        loop = asyncio.get_event_loop()
        
        for sig in (signal.SIGTERM, signal.SIGINT):
            # Capture sig in lambda to avoid closure issue
            loop.add_signal_handler(
                lambda s=sig: asyncio.create_task(self.shutdown(graceful=True))
            )
        
        self._logger.info("Signal handlers configured")
    
    def xǁLifecycleManagerǁsetup_signal_handlers__mutmut_5(self) -> None:
        """set up signal handlers for graceful shutdown."""
        loop = asyncio.get_event_loop()
        
        for sig in (signal.SIGTERM, signal.SIGINT):
            # Capture sig in lambda to avoid closure issue
            loop.add_signal_handler(
                sig,
                )
        
        self._logger.info("Signal handlers configured")
    
    def xǁLifecycleManagerǁsetup_signal_handlers__mutmut_6(self) -> None:
        """set up signal handlers for graceful shutdown."""
        loop = asyncio.get_event_loop()
        
        for sig in (signal.SIGTERM, signal.SIGINT):
            # Capture sig in lambda to avoid closure issue
            loop.add_signal_handler(
                sig,
                lambda s=sig: None
            )
        
        self._logger.info("Signal handlers configured")
    
    def xǁLifecycleManagerǁsetup_signal_handlers__mutmut_7(self) -> None:
        """set up signal handlers for graceful shutdown."""
        loop = asyncio.get_event_loop()
        
        for sig in (signal.SIGTERM, signal.SIGINT):
            # Capture sig in lambda to avoid closure issue
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(None)
            )
        
        self._logger.info("Signal handlers configured")
    
    def xǁLifecycleManagerǁsetup_signal_handlers__mutmut_8(self) -> None:
        """set up signal handlers for graceful shutdown."""
        loop = asyncio.get_event_loop()
        
        for sig in (signal.SIGTERM, signal.SIGINT):
            # Capture sig in lambda to avoid closure issue
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(self.shutdown(graceful=None))
            )
        
        self._logger.info("Signal handlers configured")
    
    def xǁLifecycleManagerǁsetup_signal_handlers__mutmut_9(self) -> None:
        """set up signal handlers for graceful shutdown."""
        loop = asyncio.get_event_loop()
        
        for sig in (signal.SIGTERM, signal.SIGINT):
            # Capture sig in lambda to avoid closure issue
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(self.shutdown(graceful=False))
            )
        
        self._logger.info("Signal handlers configured")
    
    def xǁLifecycleManagerǁsetup_signal_handlers__mutmut_10(self) -> None:
        """set up signal handlers for graceful shutdown."""
        loop = asyncio.get_event_loop()
        
        for sig in (signal.SIGTERM, signal.SIGINT):
            # Capture sig in lambda to avoid closure issue
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(self.shutdown(graceful=True))
            )
        
        self._logger.info(None)
    
    def xǁLifecycleManagerǁsetup_signal_handlers__mutmut_11(self) -> None:
        """set up signal handlers for graceful shutdown."""
        loop = asyncio.get_event_loop()
        
        for sig in (signal.SIGTERM, signal.SIGINT):
            # Capture sig in lambda to avoid closure issue
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(self.shutdown(graceful=True))
            )
        
        self._logger.info("XXSignal handlers configuredXX")
    
    def xǁLifecycleManagerǁsetup_signal_handlers__mutmut_12(self) -> None:
        """set up signal handlers for graceful shutdown."""
        loop = asyncio.get_event_loop()
        
        for sig in (signal.SIGTERM, signal.SIGINT):
            # Capture sig in lambda to avoid closure issue
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(self.shutdown(graceful=True))
            )
        
        self._logger.info("signal handlers configured")
    
    def xǁLifecycleManagerǁsetup_signal_handlers__mutmut_13(self) -> None:
        """set up signal handlers for graceful shutdown."""
        loop = asyncio.get_event_loop()
        
        for sig in (signal.SIGTERM, signal.SIGINT):
            # Capture sig in lambda to avoid closure issue
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(self.shutdown(graceful=True))
            )
        
        self._logger.info("SIGNAL HANDLERS CONFIGURED")
    
    xǁLifecycleManagerǁsetup_signal_handlers__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLifecycleManagerǁsetup_signal_handlers__mutmut_1': xǁLifecycleManagerǁsetup_signal_handlers__mutmut_1, 
        'xǁLifecycleManagerǁsetup_signal_handlers__mutmut_2': xǁLifecycleManagerǁsetup_signal_handlers__mutmut_2, 
        'xǁLifecycleManagerǁsetup_signal_handlers__mutmut_3': xǁLifecycleManagerǁsetup_signal_handlers__mutmut_3, 
        'xǁLifecycleManagerǁsetup_signal_handlers__mutmut_4': xǁLifecycleManagerǁsetup_signal_handlers__mutmut_4, 
        'xǁLifecycleManagerǁsetup_signal_handlers__mutmut_5': xǁLifecycleManagerǁsetup_signal_handlers__mutmut_5, 
        'xǁLifecycleManagerǁsetup_signal_handlers__mutmut_6': xǁLifecycleManagerǁsetup_signal_handlers__mutmut_6, 
        'xǁLifecycleManagerǁsetup_signal_handlers__mutmut_7': xǁLifecycleManagerǁsetup_signal_handlers__mutmut_7, 
        'xǁLifecycleManagerǁsetup_signal_handlers__mutmut_8': xǁLifecycleManagerǁsetup_signal_handlers__mutmut_8, 
        'xǁLifecycleManagerǁsetup_signal_handlers__mutmut_9': xǁLifecycleManagerǁsetup_signal_handlers__mutmut_9, 
        'xǁLifecycleManagerǁsetup_signal_handlers__mutmut_10': xǁLifecycleManagerǁsetup_signal_handlers__mutmut_10, 
        'xǁLifecycleManagerǁsetup_signal_handlers__mutmut_11': xǁLifecycleManagerǁsetup_signal_handlers__mutmut_11, 
        'xǁLifecycleManagerǁsetup_signal_handlers__mutmut_12': xǁLifecycleManagerǁsetup_signal_handlers__mutmut_12, 
        'xǁLifecycleManagerǁsetup_signal_handlers__mutmut_13': xǁLifecycleManagerǁsetup_signal_handlers__mutmut_13
    }
    
    def setup_signal_handlers(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLifecycleManagerǁsetup_signal_handlers__mutmut_orig"), object.__getattribute__(self, "xǁLifecycleManagerǁsetup_signal_handlers__mutmut_mutants"), args, kwargs, self)
        return result 
    
    setup_signal_handlers.__signature__ = _mutmut_signature(xǁLifecycleManagerǁsetup_signal_handlers__mutmut_orig)
    xǁLifecycleManagerǁsetup_signal_handlers__mutmut_orig.__name__ = 'xǁLifecycleManagerǁsetup_signal_handlers'


# Module-level instance for convenience
_lifecycle_manager: Optional[LifecycleManager] = None


def x_get_lifecycle_manager__mutmut_orig() -> LifecycleManager:
    """Get or create the global lifecycle manager.
    
    Returns:
        The global LifecycleManager instance.
    """
    global _lifecycle_manager
    if _lifecycle_manager is None:
        _lifecycle_manager = LifecycleManager()
    return _lifecycle_manager


def x_get_lifecycle_manager__mutmut_1() -> LifecycleManager:
    """Get or create the global lifecycle manager.
    
    Returns:
        The global LifecycleManager instance.
    """
    global _lifecycle_manager
    if _lifecycle_manager is not None:
        _lifecycle_manager = LifecycleManager()
    return _lifecycle_manager


def x_get_lifecycle_manager__mutmut_2() -> LifecycleManager:
    """Get or create the global lifecycle manager.
    
    Returns:
        The global LifecycleManager instance.
    """
    global _lifecycle_manager
    if _lifecycle_manager is None:
        _lifecycle_manager = None
    return _lifecycle_manager

x_get_lifecycle_manager__mutmut_mutants : ClassVar[MutantDict] = {
'x_get_lifecycle_manager__mutmut_1': x_get_lifecycle_manager__mutmut_1, 
    'x_get_lifecycle_manager__mutmut_2': x_get_lifecycle_manager__mutmut_2
}

def get_lifecycle_manager(*args, **kwargs):
    result = _mutmut_trampoline(x_get_lifecycle_manager__mutmut_orig, x_get_lifecycle_manager__mutmut_mutants, args, kwargs)
    return result 

get_lifecycle_manager.__signature__ = _mutmut_signature(x_get_lifecycle_manager__mutmut_orig)
x_get_lifecycle_manager__mutmut_orig.__name__ = 'x_get_lifecycle_manager'


def x_reset_lifecycle_manager__mutmut_orig() -> None:
    """Reset the global lifecycle manager (for testing)."""
    global _lifecycle_manager
    _lifecycle_manager = None


def x_reset_lifecycle_manager__mutmut_1() -> None:
    """Reset the global lifecycle manager (for testing)."""
    global _lifecycle_manager
    _lifecycle_manager = ""

x_reset_lifecycle_manager__mutmut_mutants : ClassVar[MutantDict] = {
'x_reset_lifecycle_manager__mutmut_1': x_reset_lifecycle_manager__mutmut_1
}

def reset_lifecycle_manager(*args, **kwargs):
    result = _mutmut_trampoline(x_reset_lifecycle_manager__mutmut_orig, x_reset_lifecycle_manager__mutmut_mutants, args, kwargs)
    return result 

reset_lifecycle_manager.__signature__ = _mutmut_signature(x_reset_lifecycle_manager__mutmut_orig)
x_reset_lifecycle_manager__mutmut_orig.__name__ = 'x_reset_lifecycle_manager'
