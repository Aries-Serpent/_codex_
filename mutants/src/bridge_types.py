"""
Typed Message Formats for Bridge Communication

Defines strictly typed message structures for secure IPC
between cognitive brain and Copilot watcher.

Part of Phase 2: Fragile Bridge Elimination
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional, Union
from datetime import datetime
from enum import Enum
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


class MessageType(Enum):
    """Enumeration of valid message types."""
    CONTEXT_UPDATE = "context_update"
    QUERY = "query"
    RESPONSE = "response"
    STATUS = "status"
    ERROR = "error"
    HEARTBEAT = "heartbeat"


class SourceType(Enum):
    """Enumeration of valid message sources."""
    COGNITIVE_BRAIN = "cognitive_brain"
    COPILOT_WATCHER = "copilot_watcher"
    ORCHESTRATOR = "orchestrator"
    AGENT = "agent"


@dataclass
class BaseMessage:
    """Base message structure with common fields."""
    timestamp: str  # ISO 8601 format
    source: str
    message_type: str
    message_id: Optional[str] = None  # For request-response correlation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ContextUpdate(BaseMessage):
    """
    Context update message from cognitive brain to Copilot.
    
    Shares current cognitive state, execution context, and
    decision-making information.
    """
    context: Dict[str, Any]
    execution_state: Optional[str] = None  # "observing", "orienting", "deciding", "acting"
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class QueryMessage(BaseMessage):
    """
    Query message requesting information or action.
    """
    query: str
    query_type: str  # "info", "action", "validation"
    parameters: Optional[Dict[str, Any]] = None
    requires_response: bool = True


@dataclass
class ResponseMessage(BaseMessage):
    """
    Response message to a query.
    """
    response_to: str  # message_id of original query
    status: str  # "success", "error", "pending"
    data: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class StatusMessage(BaseMessage):
    """
    Status update message.
    """
    component: str  # "cognitive_brain", "orchestrator", "agent"
    status: str  # "running", "idle", "error", "stopped"
    metrics: Optional[Dict[str, Any]] = None


@dataclass
class ErrorMessage(BaseMessage):
    """
    Error notification message.
    """
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    recovery_action: Optional[str] = None


@dataclass
class HeartbeatMessage(BaseMessage):
    """
    Heartbeat message for connection monitoring.
    """
    uptime_seconds: float
    last_activity: str  # ISO 8601 timestamp


# Type union for all message types
BridgeMessage = Union[
    ContextUpdate,
    QueryMessage,
    ResponseMessage,
    StatusMessage,
    ErrorMessage,
    HeartbeatMessage
]


def x_create_context_update__mutmut_orig(
    source: str,
    context: Dict[str, Any],
    execution_state: Optional[str] = None,
    confidence: Optional[float] = None
) -> ContextUpdate:
    """
    Factory function to create context update message.
    
    Args:
        source: Message source
        context: Context data
        execution_state: Current OODA loop state
        confidence: Confidence level (0.0 to 1.0)
        
    Returns:
        ContextUpdate message
    """
    return ContextUpdate(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.CONTEXT_UPDATE.value,
        context=context,
        execution_state=execution_state,
        confidence=confidence
    )


def x_create_context_update__mutmut_1(
    source: str,
    context: Dict[str, Any],
    execution_state: Optional[str] = None,
    confidence: Optional[float] = None
) -> ContextUpdate:
    """
    Factory function to create context update message.
    
    Args:
        source: Message source
        context: Context data
        execution_state: Current OODA loop state
        confidence: Confidence level (0.0 to 1.0)
        
    Returns:
        ContextUpdate message
    """
    return ContextUpdate(
        timestamp=None,
        source=source,
        message_type=MessageType.CONTEXT_UPDATE.value,
        context=context,
        execution_state=execution_state,
        confidence=confidence
    )


def x_create_context_update__mutmut_2(
    source: str,
    context: Dict[str, Any],
    execution_state: Optional[str] = None,
    confidence: Optional[float] = None
) -> ContextUpdate:
    """
    Factory function to create context update message.
    
    Args:
        source: Message source
        context: Context data
        execution_state: Current OODA loop state
        confidence: Confidence level (0.0 to 1.0)
        
    Returns:
        ContextUpdate message
    """
    return ContextUpdate(
        timestamp=datetime.now().isoformat(),
        source=None,
        message_type=MessageType.CONTEXT_UPDATE.value,
        context=context,
        execution_state=execution_state,
        confidence=confidence
    )


def x_create_context_update__mutmut_3(
    source: str,
    context: Dict[str, Any],
    execution_state: Optional[str] = None,
    confidence: Optional[float] = None
) -> ContextUpdate:
    """
    Factory function to create context update message.
    
    Args:
        source: Message source
        context: Context data
        execution_state: Current OODA loop state
        confidence: Confidence level (0.0 to 1.0)
        
    Returns:
        ContextUpdate message
    """
    return ContextUpdate(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=None,
        context=context,
        execution_state=execution_state,
        confidence=confidence
    )


def x_create_context_update__mutmut_4(
    source: str,
    context: Dict[str, Any],
    execution_state: Optional[str] = None,
    confidence: Optional[float] = None
) -> ContextUpdate:
    """
    Factory function to create context update message.
    
    Args:
        source: Message source
        context: Context data
        execution_state: Current OODA loop state
        confidence: Confidence level (0.0 to 1.0)
        
    Returns:
        ContextUpdate message
    """
    return ContextUpdate(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.CONTEXT_UPDATE.value,
        context=None,
        execution_state=execution_state,
        confidence=confidence
    )


def x_create_context_update__mutmut_5(
    source: str,
    context: Dict[str, Any],
    execution_state: Optional[str] = None,
    confidence: Optional[float] = None
) -> ContextUpdate:
    """
    Factory function to create context update message.
    
    Args:
        source: Message source
        context: Context data
        execution_state: Current OODA loop state
        confidence: Confidence level (0.0 to 1.0)
        
    Returns:
        ContextUpdate message
    """
    return ContextUpdate(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.CONTEXT_UPDATE.value,
        context=context,
        execution_state=None,
        confidence=confidence
    )


def x_create_context_update__mutmut_6(
    source: str,
    context: Dict[str, Any],
    execution_state: Optional[str] = None,
    confidence: Optional[float] = None
) -> ContextUpdate:
    """
    Factory function to create context update message.
    
    Args:
        source: Message source
        context: Context data
        execution_state: Current OODA loop state
        confidence: Confidence level (0.0 to 1.0)
        
    Returns:
        ContextUpdate message
    """
    return ContextUpdate(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.CONTEXT_UPDATE.value,
        context=context,
        execution_state=execution_state,
        confidence=None
    )


def x_create_context_update__mutmut_7(
    source: str,
    context: Dict[str, Any],
    execution_state: Optional[str] = None,
    confidence: Optional[float] = None
) -> ContextUpdate:
    """
    Factory function to create context update message.
    
    Args:
        source: Message source
        context: Context data
        execution_state: Current OODA loop state
        confidence: Confidence level (0.0 to 1.0)
        
    Returns:
        ContextUpdate message
    """
    return ContextUpdate(
        source=source,
        message_type=MessageType.CONTEXT_UPDATE.value,
        context=context,
        execution_state=execution_state,
        confidence=confidence
    )


def x_create_context_update__mutmut_8(
    source: str,
    context: Dict[str, Any],
    execution_state: Optional[str] = None,
    confidence: Optional[float] = None
) -> ContextUpdate:
    """
    Factory function to create context update message.
    
    Args:
        source: Message source
        context: Context data
        execution_state: Current OODA loop state
        confidence: Confidence level (0.0 to 1.0)
        
    Returns:
        ContextUpdate message
    """
    return ContextUpdate(
        timestamp=datetime.now().isoformat(),
        message_type=MessageType.CONTEXT_UPDATE.value,
        context=context,
        execution_state=execution_state,
        confidence=confidence
    )


def x_create_context_update__mutmut_9(
    source: str,
    context: Dict[str, Any],
    execution_state: Optional[str] = None,
    confidence: Optional[float] = None
) -> ContextUpdate:
    """
    Factory function to create context update message.
    
    Args:
        source: Message source
        context: Context data
        execution_state: Current OODA loop state
        confidence: Confidence level (0.0 to 1.0)
        
    Returns:
        ContextUpdate message
    """
    return ContextUpdate(
        timestamp=datetime.now().isoformat(),
        source=source,
        context=context,
        execution_state=execution_state,
        confidence=confidence
    )


def x_create_context_update__mutmut_10(
    source: str,
    context: Dict[str, Any],
    execution_state: Optional[str] = None,
    confidence: Optional[float] = None
) -> ContextUpdate:
    """
    Factory function to create context update message.
    
    Args:
        source: Message source
        context: Context data
        execution_state: Current OODA loop state
        confidence: Confidence level (0.0 to 1.0)
        
    Returns:
        ContextUpdate message
    """
    return ContextUpdate(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.CONTEXT_UPDATE.value,
        execution_state=execution_state,
        confidence=confidence
    )


def x_create_context_update__mutmut_11(
    source: str,
    context: Dict[str, Any],
    execution_state: Optional[str] = None,
    confidence: Optional[float] = None
) -> ContextUpdate:
    """
    Factory function to create context update message.
    
    Args:
        source: Message source
        context: Context data
        execution_state: Current OODA loop state
        confidence: Confidence level (0.0 to 1.0)
        
    Returns:
        ContextUpdate message
    """
    return ContextUpdate(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.CONTEXT_UPDATE.value,
        context=context,
        confidence=confidence
    )


def x_create_context_update__mutmut_12(
    source: str,
    context: Dict[str, Any],
    execution_state: Optional[str] = None,
    confidence: Optional[float] = None
) -> ContextUpdate:
    """
    Factory function to create context update message.
    
    Args:
        source: Message source
        context: Context data
        execution_state: Current OODA loop state
        confidence: Confidence level (0.0 to 1.0)
        
    Returns:
        ContextUpdate message
    """
    return ContextUpdate(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.CONTEXT_UPDATE.value,
        context=context,
        execution_state=execution_state,
        )

x_create_context_update__mutmut_mutants : ClassVar[MutantDict] = {
'x_create_context_update__mutmut_1': x_create_context_update__mutmut_1, 
    'x_create_context_update__mutmut_2': x_create_context_update__mutmut_2, 
    'x_create_context_update__mutmut_3': x_create_context_update__mutmut_3, 
    'x_create_context_update__mutmut_4': x_create_context_update__mutmut_4, 
    'x_create_context_update__mutmut_5': x_create_context_update__mutmut_5, 
    'x_create_context_update__mutmut_6': x_create_context_update__mutmut_6, 
    'x_create_context_update__mutmut_7': x_create_context_update__mutmut_7, 
    'x_create_context_update__mutmut_8': x_create_context_update__mutmut_8, 
    'x_create_context_update__mutmut_9': x_create_context_update__mutmut_9, 
    'x_create_context_update__mutmut_10': x_create_context_update__mutmut_10, 
    'x_create_context_update__mutmut_11': x_create_context_update__mutmut_11, 
    'x_create_context_update__mutmut_12': x_create_context_update__mutmut_12
}

def create_context_update(*args, **kwargs):
    result = _mutmut_trampoline(x_create_context_update__mutmut_orig, x_create_context_update__mutmut_mutants, args, kwargs)
    return result 

create_context_update.__signature__ = _mutmut_signature(x_create_context_update__mutmut_orig)
x_create_context_update__mutmut_orig.__name__ = 'x_create_context_update'


def x_create_query__mutmut_orig(
    source: str,
    query: str,
    query_type: str = "info",
    parameters: Optional[Dict[str, Any]] = None,
    message_id: Optional[str] = None
) -> QueryMessage:
    """
    Factory function to create query message.
    
    Args:
        source: Message source
        query: Query string
        query_type: Type of query
        parameters: Optional parameters
        message_id: Optional message ID for correlation
        
    Returns:
        QueryMessage
    """
    return QueryMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.QUERY.value,
        message_id=message_id or f"query_{datetime.now().timestamp()}",
        query=query,
        query_type=query_type,
        parameters=parameters
    )


def x_create_query__mutmut_1(
    source: str,
    query: str,
    query_type: str = "XXinfoXX",
    parameters: Optional[Dict[str, Any]] = None,
    message_id: Optional[str] = None
) -> QueryMessage:
    """
    Factory function to create query message.
    
    Args:
        source: Message source
        query: Query string
        query_type: Type of query
        parameters: Optional parameters
        message_id: Optional message ID for correlation
        
    Returns:
        QueryMessage
    """
    return QueryMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.QUERY.value,
        message_id=message_id or f"query_{datetime.now().timestamp()}",
        query=query,
        query_type=query_type,
        parameters=parameters
    )


def x_create_query__mutmut_2(
    source: str,
    query: str,
    query_type: str = "INFO",
    parameters: Optional[Dict[str, Any]] = None,
    message_id: Optional[str] = None
) -> QueryMessage:
    """
    Factory function to create query message.
    
    Args:
        source: Message source
        query: Query string
        query_type: Type of query
        parameters: Optional parameters
        message_id: Optional message ID for correlation
        
    Returns:
        QueryMessage
    """
    return QueryMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.QUERY.value,
        message_id=message_id or f"query_{datetime.now().timestamp()}",
        query=query,
        query_type=query_type,
        parameters=parameters
    )


def x_create_query__mutmut_3(
    source: str,
    query: str,
    query_type: str = "info",
    parameters: Optional[Dict[str, Any]] = None,
    message_id: Optional[str] = None
) -> QueryMessage:
    """
    Factory function to create query message.
    
    Args:
        source: Message source
        query: Query string
        query_type: Type of query
        parameters: Optional parameters
        message_id: Optional message ID for correlation
        
    Returns:
        QueryMessage
    """
    return QueryMessage(
        timestamp=None,
        source=source,
        message_type=MessageType.QUERY.value,
        message_id=message_id or f"query_{datetime.now().timestamp()}",
        query=query,
        query_type=query_type,
        parameters=parameters
    )


def x_create_query__mutmut_4(
    source: str,
    query: str,
    query_type: str = "info",
    parameters: Optional[Dict[str, Any]] = None,
    message_id: Optional[str] = None
) -> QueryMessage:
    """
    Factory function to create query message.
    
    Args:
        source: Message source
        query: Query string
        query_type: Type of query
        parameters: Optional parameters
        message_id: Optional message ID for correlation
        
    Returns:
        QueryMessage
    """
    return QueryMessage(
        timestamp=datetime.now().isoformat(),
        source=None,
        message_type=MessageType.QUERY.value,
        message_id=message_id or f"query_{datetime.now().timestamp()}",
        query=query,
        query_type=query_type,
        parameters=parameters
    )


def x_create_query__mutmut_5(
    source: str,
    query: str,
    query_type: str = "info",
    parameters: Optional[Dict[str, Any]] = None,
    message_id: Optional[str] = None
) -> QueryMessage:
    """
    Factory function to create query message.
    
    Args:
        source: Message source
        query: Query string
        query_type: Type of query
        parameters: Optional parameters
        message_id: Optional message ID for correlation
        
    Returns:
        QueryMessage
    """
    return QueryMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=None,
        message_id=message_id or f"query_{datetime.now().timestamp()}",
        query=query,
        query_type=query_type,
        parameters=parameters
    )


def x_create_query__mutmut_6(
    source: str,
    query: str,
    query_type: str = "info",
    parameters: Optional[Dict[str, Any]] = None,
    message_id: Optional[str] = None
) -> QueryMessage:
    """
    Factory function to create query message.
    
    Args:
        source: Message source
        query: Query string
        query_type: Type of query
        parameters: Optional parameters
        message_id: Optional message ID for correlation
        
    Returns:
        QueryMessage
    """
    return QueryMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.QUERY.value,
        message_id=None,
        query=query,
        query_type=query_type,
        parameters=parameters
    )


def x_create_query__mutmut_7(
    source: str,
    query: str,
    query_type: str = "info",
    parameters: Optional[Dict[str, Any]] = None,
    message_id: Optional[str] = None
) -> QueryMessage:
    """
    Factory function to create query message.
    
    Args:
        source: Message source
        query: Query string
        query_type: Type of query
        parameters: Optional parameters
        message_id: Optional message ID for correlation
        
    Returns:
        QueryMessage
    """
    return QueryMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.QUERY.value,
        message_id=message_id or f"query_{datetime.now().timestamp()}",
        query=None,
        query_type=query_type,
        parameters=parameters
    )


def x_create_query__mutmut_8(
    source: str,
    query: str,
    query_type: str = "info",
    parameters: Optional[Dict[str, Any]] = None,
    message_id: Optional[str] = None
) -> QueryMessage:
    """
    Factory function to create query message.
    
    Args:
        source: Message source
        query: Query string
        query_type: Type of query
        parameters: Optional parameters
        message_id: Optional message ID for correlation
        
    Returns:
        QueryMessage
    """
    return QueryMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.QUERY.value,
        message_id=message_id or f"query_{datetime.now().timestamp()}",
        query=query,
        query_type=None,
        parameters=parameters
    )


def x_create_query__mutmut_9(
    source: str,
    query: str,
    query_type: str = "info",
    parameters: Optional[Dict[str, Any]] = None,
    message_id: Optional[str] = None
) -> QueryMessage:
    """
    Factory function to create query message.
    
    Args:
        source: Message source
        query: Query string
        query_type: Type of query
        parameters: Optional parameters
        message_id: Optional message ID for correlation
        
    Returns:
        QueryMessage
    """
    return QueryMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.QUERY.value,
        message_id=message_id or f"query_{datetime.now().timestamp()}",
        query=query,
        query_type=query_type,
        parameters=None
    )


def x_create_query__mutmut_10(
    source: str,
    query: str,
    query_type: str = "info",
    parameters: Optional[Dict[str, Any]] = None,
    message_id: Optional[str] = None
) -> QueryMessage:
    """
    Factory function to create query message.
    
    Args:
        source: Message source
        query: Query string
        query_type: Type of query
        parameters: Optional parameters
        message_id: Optional message ID for correlation
        
    Returns:
        QueryMessage
    """
    return QueryMessage(
        source=source,
        message_type=MessageType.QUERY.value,
        message_id=message_id or f"query_{datetime.now().timestamp()}",
        query=query,
        query_type=query_type,
        parameters=parameters
    )


def x_create_query__mutmut_11(
    source: str,
    query: str,
    query_type: str = "info",
    parameters: Optional[Dict[str, Any]] = None,
    message_id: Optional[str] = None
) -> QueryMessage:
    """
    Factory function to create query message.
    
    Args:
        source: Message source
        query: Query string
        query_type: Type of query
        parameters: Optional parameters
        message_id: Optional message ID for correlation
        
    Returns:
        QueryMessage
    """
    return QueryMessage(
        timestamp=datetime.now().isoformat(),
        message_type=MessageType.QUERY.value,
        message_id=message_id or f"query_{datetime.now().timestamp()}",
        query=query,
        query_type=query_type,
        parameters=parameters
    )


def x_create_query__mutmut_12(
    source: str,
    query: str,
    query_type: str = "info",
    parameters: Optional[Dict[str, Any]] = None,
    message_id: Optional[str] = None
) -> QueryMessage:
    """
    Factory function to create query message.
    
    Args:
        source: Message source
        query: Query string
        query_type: Type of query
        parameters: Optional parameters
        message_id: Optional message ID for correlation
        
    Returns:
        QueryMessage
    """
    return QueryMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_id=message_id or f"query_{datetime.now().timestamp()}",
        query=query,
        query_type=query_type,
        parameters=parameters
    )


def x_create_query__mutmut_13(
    source: str,
    query: str,
    query_type: str = "info",
    parameters: Optional[Dict[str, Any]] = None,
    message_id: Optional[str] = None
) -> QueryMessage:
    """
    Factory function to create query message.
    
    Args:
        source: Message source
        query: Query string
        query_type: Type of query
        parameters: Optional parameters
        message_id: Optional message ID for correlation
        
    Returns:
        QueryMessage
    """
    return QueryMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.QUERY.value,
        query=query,
        query_type=query_type,
        parameters=parameters
    )


def x_create_query__mutmut_14(
    source: str,
    query: str,
    query_type: str = "info",
    parameters: Optional[Dict[str, Any]] = None,
    message_id: Optional[str] = None
) -> QueryMessage:
    """
    Factory function to create query message.
    
    Args:
        source: Message source
        query: Query string
        query_type: Type of query
        parameters: Optional parameters
        message_id: Optional message ID for correlation
        
    Returns:
        QueryMessage
    """
    return QueryMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.QUERY.value,
        message_id=message_id or f"query_{datetime.now().timestamp()}",
        query_type=query_type,
        parameters=parameters
    )


def x_create_query__mutmut_15(
    source: str,
    query: str,
    query_type: str = "info",
    parameters: Optional[Dict[str, Any]] = None,
    message_id: Optional[str] = None
) -> QueryMessage:
    """
    Factory function to create query message.
    
    Args:
        source: Message source
        query: Query string
        query_type: Type of query
        parameters: Optional parameters
        message_id: Optional message ID for correlation
        
    Returns:
        QueryMessage
    """
    return QueryMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.QUERY.value,
        message_id=message_id or f"query_{datetime.now().timestamp()}",
        query=query,
        parameters=parameters
    )


def x_create_query__mutmut_16(
    source: str,
    query: str,
    query_type: str = "info",
    parameters: Optional[Dict[str, Any]] = None,
    message_id: Optional[str] = None
) -> QueryMessage:
    """
    Factory function to create query message.
    
    Args:
        source: Message source
        query: Query string
        query_type: Type of query
        parameters: Optional parameters
        message_id: Optional message ID for correlation
        
    Returns:
        QueryMessage
    """
    return QueryMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.QUERY.value,
        message_id=message_id or f"query_{datetime.now().timestamp()}",
        query=query,
        query_type=query_type,
        )


def x_create_query__mutmut_17(
    source: str,
    query: str,
    query_type: str = "info",
    parameters: Optional[Dict[str, Any]] = None,
    message_id: Optional[str] = None
) -> QueryMessage:
    """
    Factory function to create query message.
    
    Args:
        source: Message source
        query: Query string
        query_type: Type of query
        parameters: Optional parameters
        message_id: Optional message ID for correlation
        
    Returns:
        QueryMessage
    """
    return QueryMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.QUERY.value,
        message_id=message_id and f"query_{datetime.now().timestamp()}",
        query=query,
        query_type=query_type,
        parameters=parameters
    )

x_create_query__mutmut_mutants : ClassVar[MutantDict] = {
'x_create_query__mutmut_1': x_create_query__mutmut_1, 
    'x_create_query__mutmut_2': x_create_query__mutmut_2, 
    'x_create_query__mutmut_3': x_create_query__mutmut_3, 
    'x_create_query__mutmut_4': x_create_query__mutmut_4, 
    'x_create_query__mutmut_5': x_create_query__mutmut_5, 
    'x_create_query__mutmut_6': x_create_query__mutmut_6, 
    'x_create_query__mutmut_7': x_create_query__mutmut_7, 
    'x_create_query__mutmut_8': x_create_query__mutmut_8, 
    'x_create_query__mutmut_9': x_create_query__mutmut_9, 
    'x_create_query__mutmut_10': x_create_query__mutmut_10, 
    'x_create_query__mutmut_11': x_create_query__mutmut_11, 
    'x_create_query__mutmut_12': x_create_query__mutmut_12, 
    'x_create_query__mutmut_13': x_create_query__mutmut_13, 
    'x_create_query__mutmut_14': x_create_query__mutmut_14, 
    'x_create_query__mutmut_15': x_create_query__mutmut_15, 
    'x_create_query__mutmut_16': x_create_query__mutmut_16, 
    'x_create_query__mutmut_17': x_create_query__mutmut_17
}

def create_query(*args, **kwargs):
    result = _mutmut_trampoline(x_create_query__mutmut_orig, x_create_query__mutmut_mutants, args, kwargs)
    return result 

create_query.__signature__ = _mutmut_signature(x_create_query__mutmut_orig)
x_create_query__mutmut_orig.__name__ = 'x_create_query'


def x_create_response__mutmut_orig(
    source: str,
    response_to: str,
    status: str = "success",
    data: Optional[Any] = None,
    error: Optional[str] = None
) -> ResponseMessage:
    """
    Factory function to create response message.
    
    Args:
        source: Message source
        response_to: ID of message being responded to
        status: Response status
        data: Response data
        error: Error message if status is "error"
        
    Returns:
        ResponseMessage
    """
    return ResponseMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.RESPONSE.value,
        response_to=response_to,
        status=status,
        data=data,
        error=error
    )


def x_create_response__mutmut_1(
    source: str,
    response_to: str,
    status: str = "XXsuccessXX",
    data: Optional[Any] = None,
    error: Optional[str] = None
) -> ResponseMessage:
    """
    Factory function to create response message.
    
    Args:
        source: Message source
        response_to: ID of message being responded to
        status: Response status
        data: Response data
        error: Error message if status is "error"
        
    Returns:
        ResponseMessage
    """
    return ResponseMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.RESPONSE.value,
        response_to=response_to,
        status=status,
        data=data,
        error=error
    )


def x_create_response__mutmut_2(
    source: str,
    response_to: str,
    status: str = "SUCCESS",
    data: Optional[Any] = None,
    error: Optional[str] = None
) -> ResponseMessage:
    """
    Factory function to create response message.
    
    Args:
        source: Message source
        response_to: ID of message being responded to
        status: Response status
        data: Response data
        error: Error message if status is "error"
        
    Returns:
        ResponseMessage
    """
    return ResponseMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.RESPONSE.value,
        response_to=response_to,
        status=status,
        data=data,
        error=error
    )


def x_create_response__mutmut_3(
    source: str,
    response_to: str,
    status: str = "success",
    data: Optional[Any] = None,
    error: Optional[str] = None
) -> ResponseMessage:
    """
    Factory function to create response message.
    
    Args:
        source: Message source
        response_to: ID of message being responded to
        status: Response status
        data: Response data
        error: Error message if status is "error"
        
    Returns:
        ResponseMessage
    """
    return ResponseMessage(
        timestamp=None,
        source=source,
        message_type=MessageType.RESPONSE.value,
        response_to=response_to,
        status=status,
        data=data,
        error=error
    )


def x_create_response__mutmut_4(
    source: str,
    response_to: str,
    status: str = "success",
    data: Optional[Any] = None,
    error: Optional[str] = None
) -> ResponseMessage:
    """
    Factory function to create response message.
    
    Args:
        source: Message source
        response_to: ID of message being responded to
        status: Response status
        data: Response data
        error: Error message if status is "error"
        
    Returns:
        ResponseMessage
    """
    return ResponseMessage(
        timestamp=datetime.now().isoformat(),
        source=None,
        message_type=MessageType.RESPONSE.value,
        response_to=response_to,
        status=status,
        data=data,
        error=error
    )


def x_create_response__mutmut_5(
    source: str,
    response_to: str,
    status: str = "success",
    data: Optional[Any] = None,
    error: Optional[str] = None
) -> ResponseMessage:
    """
    Factory function to create response message.
    
    Args:
        source: Message source
        response_to: ID of message being responded to
        status: Response status
        data: Response data
        error: Error message if status is "error"
        
    Returns:
        ResponseMessage
    """
    return ResponseMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=None,
        response_to=response_to,
        status=status,
        data=data,
        error=error
    )


def x_create_response__mutmut_6(
    source: str,
    response_to: str,
    status: str = "success",
    data: Optional[Any] = None,
    error: Optional[str] = None
) -> ResponseMessage:
    """
    Factory function to create response message.
    
    Args:
        source: Message source
        response_to: ID of message being responded to
        status: Response status
        data: Response data
        error: Error message if status is "error"
        
    Returns:
        ResponseMessage
    """
    return ResponseMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.RESPONSE.value,
        response_to=None,
        status=status,
        data=data,
        error=error
    )


def x_create_response__mutmut_7(
    source: str,
    response_to: str,
    status: str = "success",
    data: Optional[Any] = None,
    error: Optional[str] = None
) -> ResponseMessage:
    """
    Factory function to create response message.
    
    Args:
        source: Message source
        response_to: ID of message being responded to
        status: Response status
        data: Response data
        error: Error message if status is "error"
        
    Returns:
        ResponseMessage
    """
    return ResponseMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.RESPONSE.value,
        response_to=response_to,
        status=None,
        data=data,
        error=error
    )


def x_create_response__mutmut_8(
    source: str,
    response_to: str,
    status: str = "success",
    data: Optional[Any] = None,
    error: Optional[str] = None
) -> ResponseMessage:
    """
    Factory function to create response message.
    
    Args:
        source: Message source
        response_to: ID of message being responded to
        status: Response status
        data: Response data
        error: Error message if status is "error"
        
    Returns:
        ResponseMessage
    """
    return ResponseMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.RESPONSE.value,
        response_to=response_to,
        status=status,
        data=None,
        error=error
    )


def x_create_response__mutmut_9(
    source: str,
    response_to: str,
    status: str = "success",
    data: Optional[Any] = None,
    error: Optional[str] = None
) -> ResponseMessage:
    """
    Factory function to create response message.
    
    Args:
        source: Message source
        response_to: ID of message being responded to
        status: Response status
        data: Response data
        error: Error message if status is "error"
        
    Returns:
        ResponseMessage
    """
    return ResponseMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.RESPONSE.value,
        response_to=response_to,
        status=status,
        data=data,
        error=None
    )


def x_create_response__mutmut_10(
    source: str,
    response_to: str,
    status: str = "success",
    data: Optional[Any] = None,
    error: Optional[str] = None
) -> ResponseMessage:
    """
    Factory function to create response message.
    
    Args:
        source: Message source
        response_to: ID of message being responded to
        status: Response status
        data: Response data
        error: Error message if status is "error"
        
    Returns:
        ResponseMessage
    """
    return ResponseMessage(
        source=source,
        message_type=MessageType.RESPONSE.value,
        response_to=response_to,
        status=status,
        data=data,
        error=error
    )


def x_create_response__mutmut_11(
    source: str,
    response_to: str,
    status: str = "success",
    data: Optional[Any] = None,
    error: Optional[str] = None
) -> ResponseMessage:
    """
    Factory function to create response message.
    
    Args:
        source: Message source
        response_to: ID of message being responded to
        status: Response status
        data: Response data
        error: Error message if status is "error"
        
    Returns:
        ResponseMessage
    """
    return ResponseMessage(
        timestamp=datetime.now().isoformat(),
        message_type=MessageType.RESPONSE.value,
        response_to=response_to,
        status=status,
        data=data,
        error=error
    )


def x_create_response__mutmut_12(
    source: str,
    response_to: str,
    status: str = "success",
    data: Optional[Any] = None,
    error: Optional[str] = None
) -> ResponseMessage:
    """
    Factory function to create response message.
    
    Args:
        source: Message source
        response_to: ID of message being responded to
        status: Response status
        data: Response data
        error: Error message if status is "error"
        
    Returns:
        ResponseMessage
    """
    return ResponseMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        response_to=response_to,
        status=status,
        data=data,
        error=error
    )


def x_create_response__mutmut_13(
    source: str,
    response_to: str,
    status: str = "success",
    data: Optional[Any] = None,
    error: Optional[str] = None
) -> ResponseMessage:
    """
    Factory function to create response message.
    
    Args:
        source: Message source
        response_to: ID of message being responded to
        status: Response status
        data: Response data
        error: Error message if status is "error"
        
    Returns:
        ResponseMessage
    """
    return ResponseMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.RESPONSE.value,
        status=status,
        data=data,
        error=error
    )


def x_create_response__mutmut_14(
    source: str,
    response_to: str,
    status: str = "success",
    data: Optional[Any] = None,
    error: Optional[str] = None
) -> ResponseMessage:
    """
    Factory function to create response message.
    
    Args:
        source: Message source
        response_to: ID of message being responded to
        status: Response status
        data: Response data
        error: Error message if status is "error"
        
    Returns:
        ResponseMessage
    """
    return ResponseMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.RESPONSE.value,
        response_to=response_to,
        data=data,
        error=error
    )


def x_create_response__mutmut_15(
    source: str,
    response_to: str,
    status: str = "success",
    data: Optional[Any] = None,
    error: Optional[str] = None
) -> ResponseMessage:
    """
    Factory function to create response message.
    
    Args:
        source: Message source
        response_to: ID of message being responded to
        status: Response status
        data: Response data
        error: Error message if status is "error"
        
    Returns:
        ResponseMessage
    """
    return ResponseMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.RESPONSE.value,
        response_to=response_to,
        status=status,
        error=error
    )


def x_create_response__mutmut_16(
    source: str,
    response_to: str,
    status: str = "success",
    data: Optional[Any] = None,
    error: Optional[str] = None
) -> ResponseMessage:
    """
    Factory function to create response message.
    
    Args:
        source: Message source
        response_to: ID of message being responded to
        status: Response status
        data: Response data
        error: Error message if status is "error"
        
    Returns:
        ResponseMessage
    """
    return ResponseMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.RESPONSE.value,
        response_to=response_to,
        status=status,
        data=data,
        )

x_create_response__mutmut_mutants : ClassVar[MutantDict] = {
'x_create_response__mutmut_1': x_create_response__mutmut_1, 
    'x_create_response__mutmut_2': x_create_response__mutmut_2, 
    'x_create_response__mutmut_3': x_create_response__mutmut_3, 
    'x_create_response__mutmut_4': x_create_response__mutmut_4, 
    'x_create_response__mutmut_5': x_create_response__mutmut_5, 
    'x_create_response__mutmut_6': x_create_response__mutmut_6, 
    'x_create_response__mutmut_7': x_create_response__mutmut_7, 
    'x_create_response__mutmut_8': x_create_response__mutmut_8, 
    'x_create_response__mutmut_9': x_create_response__mutmut_9, 
    'x_create_response__mutmut_10': x_create_response__mutmut_10, 
    'x_create_response__mutmut_11': x_create_response__mutmut_11, 
    'x_create_response__mutmut_12': x_create_response__mutmut_12, 
    'x_create_response__mutmut_13': x_create_response__mutmut_13, 
    'x_create_response__mutmut_14': x_create_response__mutmut_14, 
    'x_create_response__mutmut_15': x_create_response__mutmut_15, 
    'x_create_response__mutmut_16': x_create_response__mutmut_16
}

def create_response(*args, **kwargs):
    result = _mutmut_trampoline(x_create_response__mutmut_orig, x_create_response__mutmut_mutants, args, kwargs)
    return result 

create_response.__signature__ = _mutmut_signature(x_create_response__mutmut_orig)
x_create_response__mutmut_orig.__name__ = 'x_create_response'


def x_create_status__mutmut_orig(
    source: str,
    component: str,
    status: str,
    metrics: Optional[Dict[str, Any]] = None
) -> StatusMessage:
    """
    Factory function to create status message.
    
    Args:
        source: Message source
        component: Component name
        status: Status string
        metrics: Optional metrics
        
    Returns:
        StatusMessage
    """
    return StatusMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.STATUS.value,
        component=component,
        status=status,
        metrics=metrics
    )


def x_create_status__mutmut_1(
    source: str,
    component: str,
    status: str,
    metrics: Optional[Dict[str, Any]] = None
) -> StatusMessage:
    """
    Factory function to create status message.
    
    Args:
        source: Message source
        component: Component name
        status: Status string
        metrics: Optional metrics
        
    Returns:
        StatusMessage
    """
    return StatusMessage(
        timestamp=None,
        source=source,
        message_type=MessageType.STATUS.value,
        component=component,
        status=status,
        metrics=metrics
    )


def x_create_status__mutmut_2(
    source: str,
    component: str,
    status: str,
    metrics: Optional[Dict[str, Any]] = None
) -> StatusMessage:
    """
    Factory function to create status message.
    
    Args:
        source: Message source
        component: Component name
        status: Status string
        metrics: Optional metrics
        
    Returns:
        StatusMessage
    """
    return StatusMessage(
        timestamp=datetime.now().isoformat(),
        source=None,
        message_type=MessageType.STATUS.value,
        component=component,
        status=status,
        metrics=metrics
    )


def x_create_status__mutmut_3(
    source: str,
    component: str,
    status: str,
    metrics: Optional[Dict[str, Any]] = None
) -> StatusMessage:
    """
    Factory function to create status message.
    
    Args:
        source: Message source
        component: Component name
        status: Status string
        metrics: Optional metrics
        
    Returns:
        StatusMessage
    """
    return StatusMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=None,
        component=component,
        status=status,
        metrics=metrics
    )


def x_create_status__mutmut_4(
    source: str,
    component: str,
    status: str,
    metrics: Optional[Dict[str, Any]] = None
) -> StatusMessage:
    """
    Factory function to create status message.
    
    Args:
        source: Message source
        component: Component name
        status: Status string
        metrics: Optional metrics
        
    Returns:
        StatusMessage
    """
    return StatusMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.STATUS.value,
        component=None,
        status=status,
        metrics=metrics
    )


def x_create_status__mutmut_5(
    source: str,
    component: str,
    status: str,
    metrics: Optional[Dict[str, Any]] = None
) -> StatusMessage:
    """
    Factory function to create status message.
    
    Args:
        source: Message source
        component: Component name
        status: Status string
        metrics: Optional metrics
        
    Returns:
        StatusMessage
    """
    return StatusMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.STATUS.value,
        component=component,
        status=None,
        metrics=metrics
    )


def x_create_status__mutmut_6(
    source: str,
    component: str,
    status: str,
    metrics: Optional[Dict[str, Any]] = None
) -> StatusMessage:
    """
    Factory function to create status message.
    
    Args:
        source: Message source
        component: Component name
        status: Status string
        metrics: Optional metrics
        
    Returns:
        StatusMessage
    """
    return StatusMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.STATUS.value,
        component=component,
        status=status,
        metrics=None
    )


def x_create_status__mutmut_7(
    source: str,
    component: str,
    status: str,
    metrics: Optional[Dict[str, Any]] = None
) -> StatusMessage:
    """
    Factory function to create status message.
    
    Args:
        source: Message source
        component: Component name
        status: Status string
        metrics: Optional metrics
        
    Returns:
        StatusMessage
    """
    return StatusMessage(
        source=source,
        message_type=MessageType.STATUS.value,
        component=component,
        status=status,
        metrics=metrics
    )


def x_create_status__mutmut_8(
    source: str,
    component: str,
    status: str,
    metrics: Optional[Dict[str, Any]] = None
) -> StatusMessage:
    """
    Factory function to create status message.
    
    Args:
        source: Message source
        component: Component name
        status: Status string
        metrics: Optional metrics
        
    Returns:
        StatusMessage
    """
    return StatusMessage(
        timestamp=datetime.now().isoformat(),
        message_type=MessageType.STATUS.value,
        component=component,
        status=status,
        metrics=metrics
    )


def x_create_status__mutmut_9(
    source: str,
    component: str,
    status: str,
    metrics: Optional[Dict[str, Any]] = None
) -> StatusMessage:
    """
    Factory function to create status message.
    
    Args:
        source: Message source
        component: Component name
        status: Status string
        metrics: Optional metrics
        
    Returns:
        StatusMessage
    """
    return StatusMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        component=component,
        status=status,
        metrics=metrics
    )


def x_create_status__mutmut_10(
    source: str,
    component: str,
    status: str,
    metrics: Optional[Dict[str, Any]] = None
) -> StatusMessage:
    """
    Factory function to create status message.
    
    Args:
        source: Message source
        component: Component name
        status: Status string
        metrics: Optional metrics
        
    Returns:
        StatusMessage
    """
    return StatusMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.STATUS.value,
        status=status,
        metrics=metrics
    )


def x_create_status__mutmut_11(
    source: str,
    component: str,
    status: str,
    metrics: Optional[Dict[str, Any]] = None
) -> StatusMessage:
    """
    Factory function to create status message.
    
    Args:
        source: Message source
        component: Component name
        status: Status string
        metrics: Optional metrics
        
    Returns:
        StatusMessage
    """
    return StatusMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.STATUS.value,
        component=component,
        metrics=metrics
    )


def x_create_status__mutmut_12(
    source: str,
    component: str,
    status: str,
    metrics: Optional[Dict[str, Any]] = None
) -> StatusMessage:
    """
    Factory function to create status message.
    
    Args:
        source: Message source
        component: Component name
        status: Status string
        metrics: Optional metrics
        
    Returns:
        StatusMessage
    """
    return StatusMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.STATUS.value,
        component=component,
        status=status,
        )

x_create_status__mutmut_mutants : ClassVar[MutantDict] = {
'x_create_status__mutmut_1': x_create_status__mutmut_1, 
    'x_create_status__mutmut_2': x_create_status__mutmut_2, 
    'x_create_status__mutmut_3': x_create_status__mutmut_3, 
    'x_create_status__mutmut_4': x_create_status__mutmut_4, 
    'x_create_status__mutmut_5': x_create_status__mutmut_5, 
    'x_create_status__mutmut_6': x_create_status__mutmut_6, 
    'x_create_status__mutmut_7': x_create_status__mutmut_7, 
    'x_create_status__mutmut_8': x_create_status__mutmut_8, 
    'x_create_status__mutmut_9': x_create_status__mutmut_9, 
    'x_create_status__mutmut_10': x_create_status__mutmut_10, 
    'x_create_status__mutmut_11': x_create_status__mutmut_11, 
    'x_create_status__mutmut_12': x_create_status__mutmut_12
}

def create_status(*args, **kwargs):
    result = _mutmut_trampoline(x_create_status__mutmut_orig, x_create_status__mutmut_mutants, args, kwargs)
    return result 

create_status.__signature__ = _mutmut_signature(x_create_status__mutmut_orig)
x_create_status__mutmut_orig.__name__ = 'x_create_status'


def x_create_error__mutmut_orig(
    source: str,
    error_type: str,
    error_message: str,
    stack_trace: Optional[str] = None,
    recovery_action: Optional[str] = None
) -> ErrorMessage:
    """
    Factory function to create error message.
    
    Args:
        source: Message source
        error_type: Type of error
        error_message: Error description
        stack_trace: Optional stack trace
        recovery_action: Optional recovery suggestion
        
    Returns:
        ErrorMessage
    """
    return ErrorMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.ERROR.value,
        error_type=error_type,
        error_message=error_message,
        stack_trace=stack_trace,
        recovery_action=recovery_action
    )


def x_create_error__mutmut_1(
    source: str,
    error_type: str,
    error_message: str,
    stack_trace: Optional[str] = None,
    recovery_action: Optional[str] = None
) -> ErrorMessage:
    """
    Factory function to create error message.
    
    Args:
        source: Message source
        error_type: Type of error
        error_message: Error description
        stack_trace: Optional stack trace
        recovery_action: Optional recovery suggestion
        
    Returns:
        ErrorMessage
    """
    return ErrorMessage(
        timestamp=None,
        source=source,
        message_type=MessageType.ERROR.value,
        error_type=error_type,
        error_message=error_message,
        stack_trace=stack_trace,
        recovery_action=recovery_action
    )


def x_create_error__mutmut_2(
    source: str,
    error_type: str,
    error_message: str,
    stack_trace: Optional[str] = None,
    recovery_action: Optional[str] = None
) -> ErrorMessage:
    """
    Factory function to create error message.
    
    Args:
        source: Message source
        error_type: Type of error
        error_message: Error description
        stack_trace: Optional stack trace
        recovery_action: Optional recovery suggestion
        
    Returns:
        ErrorMessage
    """
    return ErrorMessage(
        timestamp=datetime.now().isoformat(),
        source=None,
        message_type=MessageType.ERROR.value,
        error_type=error_type,
        error_message=error_message,
        stack_trace=stack_trace,
        recovery_action=recovery_action
    )


def x_create_error__mutmut_3(
    source: str,
    error_type: str,
    error_message: str,
    stack_trace: Optional[str] = None,
    recovery_action: Optional[str] = None
) -> ErrorMessage:
    """
    Factory function to create error message.
    
    Args:
        source: Message source
        error_type: Type of error
        error_message: Error description
        stack_trace: Optional stack trace
        recovery_action: Optional recovery suggestion
        
    Returns:
        ErrorMessage
    """
    return ErrorMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=None,
        error_type=error_type,
        error_message=error_message,
        stack_trace=stack_trace,
        recovery_action=recovery_action
    )


def x_create_error__mutmut_4(
    source: str,
    error_type: str,
    error_message: str,
    stack_trace: Optional[str] = None,
    recovery_action: Optional[str] = None
) -> ErrorMessage:
    """
    Factory function to create error message.
    
    Args:
        source: Message source
        error_type: Type of error
        error_message: Error description
        stack_trace: Optional stack trace
        recovery_action: Optional recovery suggestion
        
    Returns:
        ErrorMessage
    """
    return ErrorMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.ERROR.value,
        error_type=None,
        error_message=error_message,
        stack_trace=stack_trace,
        recovery_action=recovery_action
    )


def x_create_error__mutmut_5(
    source: str,
    error_type: str,
    error_message: str,
    stack_trace: Optional[str] = None,
    recovery_action: Optional[str] = None
) -> ErrorMessage:
    """
    Factory function to create error message.
    
    Args:
        source: Message source
        error_type: Type of error
        error_message: Error description
        stack_trace: Optional stack trace
        recovery_action: Optional recovery suggestion
        
    Returns:
        ErrorMessage
    """
    return ErrorMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.ERROR.value,
        error_type=error_type,
        error_message=None,
        stack_trace=stack_trace,
        recovery_action=recovery_action
    )


def x_create_error__mutmut_6(
    source: str,
    error_type: str,
    error_message: str,
    stack_trace: Optional[str] = None,
    recovery_action: Optional[str] = None
) -> ErrorMessage:
    """
    Factory function to create error message.
    
    Args:
        source: Message source
        error_type: Type of error
        error_message: Error description
        stack_trace: Optional stack trace
        recovery_action: Optional recovery suggestion
        
    Returns:
        ErrorMessage
    """
    return ErrorMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.ERROR.value,
        error_type=error_type,
        error_message=error_message,
        stack_trace=None,
        recovery_action=recovery_action
    )


def x_create_error__mutmut_7(
    source: str,
    error_type: str,
    error_message: str,
    stack_trace: Optional[str] = None,
    recovery_action: Optional[str] = None
) -> ErrorMessage:
    """
    Factory function to create error message.
    
    Args:
        source: Message source
        error_type: Type of error
        error_message: Error description
        stack_trace: Optional stack trace
        recovery_action: Optional recovery suggestion
        
    Returns:
        ErrorMessage
    """
    return ErrorMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.ERROR.value,
        error_type=error_type,
        error_message=error_message,
        stack_trace=stack_trace,
        recovery_action=None
    )


def x_create_error__mutmut_8(
    source: str,
    error_type: str,
    error_message: str,
    stack_trace: Optional[str] = None,
    recovery_action: Optional[str] = None
) -> ErrorMessage:
    """
    Factory function to create error message.
    
    Args:
        source: Message source
        error_type: Type of error
        error_message: Error description
        stack_trace: Optional stack trace
        recovery_action: Optional recovery suggestion
        
    Returns:
        ErrorMessage
    """
    return ErrorMessage(
        source=source,
        message_type=MessageType.ERROR.value,
        error_type=error_type,
        error_message=error_message,
        stack_trace=stack_trace,
        recovery_action=recovery_action
    )


def x_create_error__mutmut_9(
    source: str,
    error_type: str,
    error_message: str,
    stack_trace: Optional[str] = None,
    recovery_action: Optional[str] = None
) -> ErrorMessage:
    """
    Factory function to create error message.
    
    Args:
        source: Message source
        error_type: Type of error
        error_message: Error description
        stack_trace: Optional stack trace
        recovery_action: Optional recovery suggestion
        
    Returns:
        ErrorMessage
    """
    return ErrorMessage(
        timestamp=datetime.now().isoformat(),
        message_type=MessageType.ERROR.value,
        error_type=error_type,
        error_message=error_message,
        stack_trace=stack_trace,
        recovery_action=recovery_action
    )


def x_create_error__mutmut_10(
    source: str,
    error_type: str,
    error_message: str,
    stack_trace: Optional[str] = None,
    recovery_action: Optional[str] = None
) -> ErrorMessage:
    """
    Factory function to create error message.
    
    Args:
        source: Message source
        error_type: Type of error
        error_message: Error description
        stack_trace: Optional stack trace
        recovery_action: Optional recovery suggestion
        
    Returns:
        ErrorMessage
    """
    return ErrorMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        error_type=error_type,
        error_message=error_message,
        stack_trace=stack_trace,
        recovery_action=recovery_action
    )


def x_create_error__mutmut_11(
    source: str,
    error_type: str,
    error_message: str,
    stack_trace: Optional[str] = None,
    recovery_action: Optional[str] = None
) -> ErrorMessage:
    """
    Factory function to create error message.
    
    Args:
        source: Message source
        error_type: Type of error
        error_message: Error description
        stack_trace: Optional stack trace
        recovery_action: Optional recovery suggestion
        
    Returns:
        ErrorMessage
    """
    return ErrorMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.ERROR.value,
        error_message=error_message,
        stack_trace=stack_trace,
        recovery_action=recovery_action
    )


def x_create_error__mutmut_12(
    source: str,
    error_type: str,
    error_message: str,
    stack_trace: Optional[str] = None,
    recovery_action: Optional[str] = None
) -> ErrorMessage:
    """
    Factory function to create error message.
    
    Args:
        source: Message source
        error_type: Type of error
        error_message: Error description
        stack_trace: Optional stack trace
        recovery_action: Optional recovery suggestion
        
    Returns:
        ErrorMessage
    """
    return ErrorMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.ERROR.value,
        error_type=error_type,
        stack_trace=stack_trace,
        recovery_action=recovery_action
    )


def x_create_error__mutmut_13(
    source: str,
    error_type: str,
    error_message: str,
    stack_trace: Optional[str] = None,
    recovery_action: Optional[str] = None
) -> ErrorMessage:
    """
    Factory function to create error message.
    
    Args:
        source: Message source
        error_type: Type of error
        error_message: Error description
        stack_trace: Optional stack trace
        recovery_action: Optional recovery suggestion
        
    Returns:
        ErrorMessage
    """
    return ErrorMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.ERROR.value,
        error_type=error_type,
        error_message=error_message,
        recovery_action=recovery_action
    )


def x_create_error__mutmut_14(
    source: str,
    error_type: str,
    error_message: str,
    stack_trace: Optional[str] = None,
    recovery_action: Optional[str] = None
) -> ErrorMessage:
    """
    Factory function to create error message.
    
    Args:
        source: Message source
        error_type: Type of error
        error_message: Error description
        stack_trace: Optional stack trace
        recovery_action: Optional recovery suggestion
        
    Returns:
        ErrorMessage
    """
    return ErrorMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.ERROR.value,
        error_type=error_type,
        error_message=error_message,
        stack_trace=stack_trace,
        )

x_create_error__mutmut_mutants : ClassVar[MutantDict] = {
'x_create_error__mutmut_1': x_create_error__mutmut_1, 
    'x_create_error__mutmut_2': x_create_error__mutmut_2, 
    'x_create_error__mutmut_3': x_create_error__mutmut_3, 
    'x_create_error__mutmut_4': x_create_error__mutmut_4, 
    'x_create_error__mutmut_5': x_create_error__mutmut_5, 
    'x_create_error__mutmut_6': x_create_error__mutmut_6, 
    'x_create_error__mutmut_7': x_create_error__mutmut_7, 
    'x_create_error__mutmut_8': x_create_error__mutmut_8, 
    'x_create_error__mutmut_9': x_create_error__mutmut_9, 
    'x_create_error__mutmut_10': x_create_error__mutmut_10, 
    'x_create_error__mutmut_11': x_create_error__mutmut_11, 
    'x_create_error__mutmut_12': x_create_error__mutmut_12, 
    'x_create_error__mutmut_13': x_create_error__mutmut_13, 
    'x_create_error__mutmut_14': x_create_error__mutmut_14
}

def create_error(*args, **kwargs):
    result = _mutmut_trampoline(x_create_error__mutmut_orig, x_create_error__mutmut_mutants, args, kwargs)
    return result 

create_error.__signature__ = _mutmut_signature(x_create_error__mutmut_orig)
x_create_error__mutmut_orig.__name__ = 'x_create_error'


def x_create_heartbeat__mutmut_orig(source: str, uptime_seconds: float) -> HeartbeatMessage:
    """
    Factory function to create heartbeat message.
    
    Args:
        source: Message source
        uptime_seconds: Uptime in seconds
        
    Returns:
        HeartbeatMessage
    """
    return HeartbeatMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.HEARTBEAT.value,
        uptime_seconds=uptime_seconds,
        last_activity=datetime.now().isoformat()
    )


def x_create_heartbeat__mutmut_1(source: str, uptime_seconds: float) -> HeartbeatMessage:
    """
    Factory function to create heartbeat message.
    
    Args:
        source: Message source
        uptime_seconds: Uptime in seconds
        
    Returns:
        HeartbeatMessage
    """
    return HeartbeatMessage(
        timestamp=None,
        source=source,
        message_type=MessageType.HEARTBEAT.value,
        uptime_seconds=uptime_seconds,
        last_activity=datetime.now().isoformat()
    )


def x_create_heartbeat__mutmut_2(source: str, uptime_seconds: float) -> HeartbeatMessage:
    """
    Factory function to create heartbeat message.
    
    Args:
        source: Message source
        uptime_seconds: Uptime in seconds
        
    Returns:
        HeartbeatMessage
    """
    return HeartbeatMessage(
        timestamp=datetime.now().isoformat(),
        source=None,
        message_type=MessageType.HEARTBEAT.value,
        uptime_seconds=uptime_seconds,
        last_activity=datetime.now().isoformat()
    )


def x_create_heartbeat__mutmut_3(source: str, uptime_seconds: float) -> HeartbeatMessage:
    """
    Factory function to create heartbeat message.
    
    Args:
        source: Message source
        uptime_seconds: Uptime in seconds
        
    Returns:
        HeartbeatMessage
    """
    return HeartbeatMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=None,
        uptime_seconds=uptime_seconds,
        last_activity=datetime.now().isoformat()
    )


def x_create_heartbeat__mutmut_4(source: str, uptime_seconds: float) -> HeartbeatMessage:
    """
    Factory function to create heartbeat message.
    
    Args:
        source: Message source
        uptime_seconds: Uptime in seconds
        
    Returns:
        HeartbeatMessage
    """
    return HeartbeatMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.HEARTBEAT.value,
        uptime_seconds=None,
        last_activity=datetime.now().isoformat()
    )


def x_create_heartbeat__mutmut_5(source: str, uptime_seconds: float) -> HeartbeatMessage:
    """
    Factory function to create heartbeat message.
    
    Args:
        source: Message source
        uptime_seconds: Uptime in seconds
        
    Returns:
        HeartbeatMessage
    """
    return HeartbeatMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.HEARTBEAT.value,
        uptime_seconds=uptime_seconds,
        last_activity=None
    )


def x_create_heartbeat__mutmut_6(source: str, uptime_seconds: float) -> HeartbeatMessage:
    """
    Factory function to create heartbeat message.
    
    Args:
        source: Message source
        uptime_seconds: Uptime in seconds
        
    Returns:
        HeartbeatMessage
    """
    return HeartbeatMessage(
        source=source,
        message_type=MessageType.HEARTBEAT.value,
        uptime_seconds=uptime_seconds,
        last_activity=datetime.now().isoformat()
    )


def x_create_heartbeat__mutmut_7(source: str, uptime_seconds: float) -> HeartbeatMessage:
    """
    Factory function to create heartbeat message.
    
    Args:
        source: Message source
        uptime_seconds: Uptime in seconds
        
    Returns:
        HeartbeatMessage
    """
    return HeartbeatMessage(
        timestamp=datetime.now().isoformat(),
        message_type=MessageType.HEARTBEAT.value,
        uptime_seconds=uptime_seconds,
        last_activity=datetime.now().isoformat()
    )


def x_create_heartbeat__mutmut_8(source: str, uptime_seconds: float) -> HeartbeatMessage:
    """
    Factory function to create heartbeat message.
    
    Args:
        source: Message source
        uptime_seconds: Uptime in seconds
        
    Returns:
        HeartbeatMessage
    """
    return HeartbeatMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        uptime_seconds=uptime_seconds,
        last_activity=datetime.now().isoformat()
    )


def x_create_heartbeat__mutmut_9(source: str, uptime_seconds: float) -> HeartbeatMessage:
    """
    Factory function to create heartbeat message.
    
    Args:
        source: Message source
        uptime_seconds: Uptime in seconds
        
    Returns:
        HeartbeatMessage
    """
    return HeartbeatMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.HEARTBEAT.value,
        last_activity=datetime.now().isoformat()
    )


def x_create_heartbeat__mutmut_10(source: str, uptime_seconds: float) -> HeartbeatMessage:
    """
    Factory function to create heartbeat message.
    
    Args:
        source: Message source
        uptime_seconds: Uptime in seconds
        
    Returns:
        HeartbeatMessage
    """
    return HeartbeatMessage(
        timestamp=datetime.now().isoformat(),
        source=source,
        message_type=MessageType.HEARTBEAT.value,
        uptime_seconds=uptime_seconds,
        )

x_create_heartbeat__mutmut_mutants : ClassVar[MutantDict] = {
'x_create_heartbeat__mutmut_1': x_create_heartbeat__mutmut_1, 
    'x_create_heartbeat__mutmut_2': x_create_heartbeat__mutmut_2, 
    'x_create_heartbeat__mutmut_3': x_create_heartbeat__mutmut_3, 
    'x_create_heartbeat__mutmut_4': x_create_heartbeat__mutmut_4, 
    'x_create_heartbeat__mutmut_5': x_create_heartbeat__mutmut_5, 
    'x_create_heartbeat__mutmut_6': x_create_heartbeat__mutmut_6, 
    'x_create_heartbeat__mutmut_7': x_create_heartbeat__mutmut_7, 
    'x_create_heartbeat__mutmut_8': x_create_heartbeat__mutmut_8, 
    'x_create_heartbeat__mutmut_9': x_create_heartbeat__mutmut_9, 
    'x_create_heartbeat__mutmut_10': x_create_heartbeat__mutmut_10
}

def create_heartbeat(*args, **kwargs):
    result = _mutmut_trampoline(x_create_heartbeat__mutmut_orig, x_create_heartbeat__mutmut_mutants, args, kwargs)
    return result 

create_heartbeat.__signature__ = _mutmut_signature(x_create_heartbeat__mutmut_orig)
x_create_heartbeat__mutmut_orig.__name__ = 'x_create_heartbeat'
