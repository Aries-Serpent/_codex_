"""
Typed Message Formats for Bridge Communication

Defines strictly typed message structures for secure IPC
between cognitive brain and Copilot watcher.

Part of Phase 2: Fragile Bridge Elimination
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum


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


def create_context_update(
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


def create_query(
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


def create_response(
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


def create_status(
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


def create_error(
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


def create_heartbeat(source: str, uptime_seconds: float) -> HeartbeatMessage:
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
