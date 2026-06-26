"""
Comprehensive tests for bridge_types module.

Tests cover all message types, enums, and factory functions for bridge communication.
"""

from __future__ import annotations

from bridge_types import (
    BaseMessage,
    ContextUpdate,
    ErrorMessage,
    HeartbeatMessage,
    MessageType,
    QueryMessage,
    ResponseMessage,
    SourceType,
    StatusMessage,
    create_context_update,
    create_error,
    create_heartbeat,
    create_query,
    create_response,
    create_status,
)


class TestMessageType:
    """Test MessageType enum."""

    def test_message_type_values(self):
        """Test MessageType enum values."""
        assert MessageType.CONTEXT_UPDATE.value == "context_update", "Value must be initialized"
        assert MessageType.QUERY.value == "query", "Value must be initialized"
        assert MessageType.RESPONSE.value == "response", "Response must not be empty"
        assert MessageType.STATUS.value == "status", "Value must be initialized"
        assert MessageType.ERROR.value == "error", "Value must be initialized"
        assert MessageType.HEARTBEAT.value == "heartbeat", "Value must be initialized"

    def test_message_type_all_values(self):
        """Test all MessageType values are strings."""
        for msg_type in MessageType:
            assert isinstance(msg_type.value, str)

    def test_message_type_count(self):
        """Test MessageType has expected number of values."""
        types = list(MessageType)
        assert len(types) == 6, "Types must not be empty"


class TestSourceType:
    """Test SourceType enum."""

    def test_source_type_values(self):
        """Test SourceType enum values."""
        assert SourceType.COGNITIVE_BRAIN.value == "cognitive_brain", "Value must be initialized"
        assert SourceType.COPILOT_WATCHER.value == "copilot_watcher", "Value must be initialized"
        assert SourceType.ORCHESTRATOR.value == "orchestrator", "Value must be initialized"
        assert SourceType.AGENT.value == "agent", "Value must be initialized"

    def test_source_type_all_values(self):
        """Test all SourceType values are strings."""
        for source_type in SourceType:
            assert isinstance(source_type.value, str)

    def test_source_type_count(self):
        """Test SourceType has expected number of values."""
        sources = list(SourceType)
        assert len(sources) == 4, "Sources must not be empty"


class TestBaseMessage:
    """Test BaseMessage dataclass."""

    def test_base_message_creation(self):
        """Test creating BaseMessage."""
        msg = BaseMessage(
            timestamp="2024-01-01T12:00:00Z",
            source="test_source",
            message_type="test_type",
        )
        assert msg.timestamp == "2024-01-01T12:00:00Z", "timestamp is not valid"
        assert msg.source == "test_source", "source is not valid"
        assert msg.message_type == "test_type", "message_type is not valid"
        assert msg.message_id is None, "message_id is not valid"

    def test_base_message_with_id(self):
        """Test BaseMessage with message ID."""
        msg = BaseMessage(
            timestamp="2024-01-01T12:00:00Z",
            source="test",
            message_type="type",
            message_id="msg-123",
        )
        assert msg.message_id == "msg-123", "message_id is not valid"

    def test_base_message_to_dict(self):
        """Test BaseMessage to_dict conversion."""
        msg = BaseMessage(
            timestamp="2024-01-01T12:00:00Z",
            source="test",
            message_type="type",
            message_id="msg-123",
        )
        result = msg.to_dict()
        assert isinstance(result, dict)
        assert result["timestamp"] == "2024-01-01T12:00:00Z", "Result must not be empty"
        assert result["source"] == "test", "Result must not be empty"
        assert result["message_type"] == "type", "Result must not be empty"
        assert result["message_id"] == "msg-123", "Result must not be empty"

    def test_base_message_to_dict_none_id(self):
        """Test to_dict with None message_id."""
        msg = BaseMessage(
            timestamp="2024-01-01T12:00:00Z",
            source="test",
            message_type="type",
        )
        result = msg.to_dict()
        assert result["message_id"] is None, "Result must not be empty"


class TestContextUpdate:
    """Test ContextUpdate message."""

    def test_context_update_creation_minimal(self):
        """Test creating minimal ContextUpdate."""
        msg = ContextUpdate(
            timestamp="2024-01-01T12:00:00Z",
            source="brain",
            message_type="context_update",
            context={"key": "value"},
        )
        assert msg.source == "brain", "source is not valid"
        assert msg.context == {"key": "value"}, "Value must be initialized"
        assert msg.execution_state is None, "execution_state is not valid"
        assert msg.confidence is None, "confidence is not valid"

    def test_context_update_creation_full(self):
        """Test creating full ContextUpdate."""
        msg = ContextUpdate(
            timestamp="2024-01-01T12:00:00Z",
            source="brain",
            message_type="context_update",
            context={"data": 123},
            execution_state="deciding",
            confidence=0.95,
            metadata={"key": "value"},
        )
        assert msg.execution_state == "deciding", "execution_state is not valid"
        assert msg.confidence == 0.95, "confidence is not valid"
        assert msg.metadata == {"key": "value"}, "Data must not be empty"

    def test_context_update_to_dict(self):
        """Test ContextUpdate to_dict."""
        msg = ContextUpdate(
            timestamp="2024-01-01T12:00:00Z",
            source="brain",
            message_type="context_update",
            context={"test": 1},
            execution_state="observing",
        )
        result = msg.to_dict()
        assert result["context"] == {"test": 1}, "Result must not be empty"
        assert result["execution_state"] == "observing", "Result must not be empty"


class TestQueryMessage:
    """Test QueryMessage."""

    def test_query_message_creation_minimal(self):
        """Test creating minimal QueryMessage."""
        msg = QueryMessage(
            timestamp="2024-01-01T12:00:00Z",
            source="agent",
            message_type="query",
            query="What is 2+2?",
            query_type="info",
        )
        assert msg.query == "What is 2+2?", "query is not valid"
        assert msg.query_type == "info", "query_type is not valid"
        assert msg.requires_response is True, "Response must not be empty"
        assert msg.parameters is None, "parameters is not valid"

    def test_query_message_creation_full(self):
        """Test creating full QueryMessage."""
        params = {"key": "value"}
        msg = QueryMessage(
            timestamp="2024-01-01T12:00:00Z",
            source="agent",
            message_type="query",
            message_id="q-1",
            query="Execute action",
            query_type="action",
            parameters=params,
            requires_response=False,
        )
        assert msg.message_id == "q-1", "message_id is not valid"
        assert msg.parameters == params, "parameters is not valid"
        assert msg.requires_response is False, "Response must not be empty"


class TestResponseMessage:
    """Test ResponseMessage."""

    def test_response_message_success(self):
        """Test ResponseMessage with success status."""
        msg = ResponseMessage(
            timestamp="2024-01-01T12:00:00Z",
            source="watcher",
            message_type="response",
            response_to="q-1",
            status="success",
            data={"result": 4},
        )
        assert msg.response_to == "q-1", "Response must not be empty"
        assert msg.status == "success", "status is not valid"
        assert msg.data == {"result": 4}, "Result must not be empty"
        assert msg.error is None, "Error should be raised or set"

    def test_response_message_error(self):
        """Test ResponseMessage with error status."""
        msg = ResponseMessage(
            timestamp="2024-01-01T12:00:00Z",
            source="watcher",
            message_type="response",
            response_to="q-1",
            status="error",
            error="Something went wrong",
        )
        assert msg.status == "error", "Error should be raised or set"
        assert msg.error == "Something went wrong", "Error should be raised or set"
        assert msg.data is None, "Data must not be empty"

    def test_response_message_pending(self):
        """Test ResponseMessage with pending status."""
        msg = ResponseMessage(
            timestamp="2024-01-01T12:00:00Z",
            source="orchestrator",
            message_type="response",
            response_to="q-1",
            status="pending",
        )
        assert msg.status == "pending", "status is not valid"


class TestStatusMessage:
    """Test StatusMessage."""

    def test_status_message_creation(self):
        """Test creating StatusMessage."""
        msg = StatusMessage(
            timestamp="2024-01-01T12:00:00Z",
            source="brain",
            message_type="status",
            component="cognitive_brain",
            status="running",
        )
        assert msg.component == "cognitive_brain", "component is not valid"
        assert msg.status == "running", "status is not valid"
        assert msg.metrics is None, "metrics is not valid"

    def test_status_message_with_metrics(self):
        """Test StatusMessage with metrics."""
        metrics = {"cpu": 45.2, "memory": 78.5}
        msg = StatusMessage(
            timestamp="2024-01-01T12:00:00Z",
            source="orchestrator",
            message_type="status",
            component="orchestrator",
            status="idle",
            metrics=metrics,
        )
        assert msg.metrics == metrics, "metrics is not valid"

    def test_status_message_all_statuses(self):
        """Test all status values."""
        statuses = ["running", "idle", "error", "stopped"]
        for status in statuses:
            msg = StatusMessage(
                timestamp="2024-01-01T12:00:00Z",
                source="test",
                message_type="status",
                component="test",
                status=status,
            )
            assert msg.status == status, "status is not valid"


class TestErrorMessage:
    """Test ErrorMessage."""

    def test_error_message_basic(self):
        """Test basic ErrorMessage."""
        msg = ErrorMessage(
            timestamp="2024-01-01T12:00:00Z",
            source="agent",
            message_type="error",
            error_type="ValueError",
            error_message="Invalid input",
        )
        assert msg.error_type == "ValueError", "Value must be initialized"
        assert msg.error_message == "Invalid input", "Error should be raised or set"
        assert msg.stack_trace is None, "stack_trace is not valid"
        assert msg.recovery_action is None, "recovery_action is not valid"

    def test_error_message_full(self):
        """Test full ErrorMessage."""
        trace = "Traceback (most recent call last)..."
        msg = ErrorMessage(
            timestamp="2024-01-01T12:00:00Z",
            source="orchestrator",
            message_type="error",
            error_type="RuntimeError",
            error_message="Process failed",
            stack_trace=trace,
            recovery_action="Retry",
        )
        assert msg.stack_trace == trace, "stack_trace is not valid"
        assert msg.recovery_action == "Retry", "recovery_action is not valid"


class TestHeartbeatMessage:
    """Test HeartbeatMessage."""

    def test_heartbeat_message_creation(self):
        """Test creating HeartbeatMessage."""
        msg = HeartbeatMessage(
            timestamp="2024-01-01T12:00:00Z",
            source="watcher",
            message_type="heartbeat",
            uptime_seconds=3600.5,
            last_activity="2024-01-01T11:59:00Z",
        )
        assert msg.uptime_seconds == 3600.5, "uptime_seconds is not valid"
        assert msg.last_activity == "2024-01-01T11:59:00Z", "last_activity is not valid"

    def test_heartbeat_message_zero_uptime(self):
        """Test HeartbeatMessage with zero uptime."""
        msg = HeartbeatMessage(
            timestamp="2024-01-01T12:00:00Z",
            source="agent",
            message_type="heartbeat",
            uptime_seconds=0.0,
            last_activity="2024-01-01T12:00:00Z",
        )
        assert msg.uptime_seconds == 0.0, "uptime_seconds is not valid"

    def test_heartbeat_message_large_uptime(self):
        """Test HeartbeatMessage with large uptime."""
        msg = HeartbeatMessage(
            timestamp="2024-01-01T12:00:00Z",
            source="brain",
            message_type="heartbeat",
            uptime_seconds=86400 * 30,  # 30 days
            last_activity="2024-01-01T12:00:00Z",
        )
        assert msg.uptime_seconds == 86400 * 30, "uptime_seconds is not valid"


class TestCreateContextUpdate:
    """Test create_context_update factory function."""

    def test_create_context_update_basic(self):
        """Test basic context update creation."""
        msg = create_context_update("brain", {"data": 1})
        assert msg.source == "brain", "source is not valid"
        assert msg.context == {"data": 1}, "Data must not be empty"
        assert msg.message_type == MessageType.CONTEXT_UPDATE.value, "Value must be initialized"
        assert isinstance(msg.timestamp, str)

    def test_create_context_update_with_state(self):
        """Test context update with execution state."""
        msg = create_context_update(
            "brain", {"data": 1}, execution_state="deciding", confidence=0.88
        )
        assert msg.execution_state == "deciding", "execution_state is not valid"
        assert msg.confidence == 0.88, "confidence is not valid"

    def test_create_context_update_timestamp(self):
        """Test that timestamp is ISO format."""
        msg = create_context_update("brain", {})
        assert "T" in msg.timestamp, "Condition must be true"
        assert "Z" in msg.timestamp or "+" in msg.timestamp, "Condition must be true"


class TestCreateQuery:
    """Test create_query factory function."""

    def test_create_query_basic(self):
        """Test basic query creation."""
        msg = create_query("agent", "Test query")
        assert msg.source == "agent", "source is not valid"
        assert msg.query == "Test query", "query is not valid"
        assert msg.message_type == MessageType.QUERY.value, "Value must be initialized"
        assert msg.query_type == "info", "query_type is not valid"
        assert msg.message_id is not None, "message_id must be initialized"

    def test_create_query_with_type(self):
        """Test query creation with query type."""
        msg = create_query("agent", "Do something", query_type="action")
        assert msg.query_type == "action", "query_type is not valid"

    def test_create_query_with_parameters(self):
        """Test query creation with parameters."""
        params = {"param1": "value1"}
        msg = create_query(
            "agent",
            "Execute",
            query_type="action",
            parameters=params,
        )
        assert msg.parameters == params, "parameters is not valid"

    def test_create_query_custom_id(self):
        """Test query creation with custom message ID."""
        msg = create_query("agent", "Query", message_id="custom-id")
        assert msg.message_id == "custom-id", "message_id is not valid"

    def test_create_query_auto_id(self):
        """Test that query gets auto-generated ID."""
        msg = create_query("agent", "Query")
        assert msg.message_id is not None, "message_id must be initialized"
        assert "query_" in msg.message_id, "Condition must be true"


class TestCreateResponse:
    """Test create_response factory function."""

    def test_create_response_success(self):
        """Test successful response creation."""
        msg = create_response("watcher", "q-1", status="success", data={"result": 42})
        assert msg.response_to == "q-1", "Response must not be empty"
        assert msg.status == "success", "status is not valid"
        assert msg.data == {"result": 42}, "Result must not be empty"
        assert msg.message_type == MessageType.RESPONSE.value, "Response must not be empty"

    def test_create_response_error(self):
        """Test error response creation."""
        msg = create_response("watcher", "q-1", status="error", error="Failed to process")
        assert msg.status == "error", "Error should be raised or set"
        assert msg.error == "Failed to process", "Error should be raised or set"

    def test_create_response_default_success(self):
        """Test response defaults to success."""
        msg = create_response("watcher", "q-1")
        assert msg.status == "success", "status is not valid"


class TestCreateStatus:
    """Test create_status factory function."""

    def test_create_status_basic(self):
        """Test basic status creation."""
        msg = create_status("brain", "cognitive_brain", "running")
        assert msg.source == "brain", "source is not valid"
        assert msg.component == "cognitive_brain", "component is not valid"
        assert msg.status == "running", "status is not valid"
        assert msg.message_type == MessageType.STATUS.value, "Value must be initialized"

    def test_create_status_with_metrics(self):
        """Test status creation with metrics."""
        metrics = {"load": 0.5}
        msg = create_status("orchestrator", "orchestrator", "idle", metrics=metrics)
        assert msg.metrics == metrics, "metrics is not valid"

    def test_create_status_all_statuses(self):
        """Test status creation with all status types."""
        for status in ["running", "idle", "error", "stopped"]:
            msg = create_status("test", "component", status)
            assert msg.status == status, "status is not valid"


class TestCreateError:
    """Test create_error factory function."""

    def test_create_error_basic(self):
        """Test basic error creation."""
        msg = create_error("agent", "TypeError", "Wrong type")
        assert msg.error_type == "TypeError", "Error should be raised or set"
        assert msg.error_message == "Wrong type", "Error should be raised or set"
        assert msg.message_type == MessageType.ERROR.value, "Value must be initialized"

    def test_create_error_with_trace(self):
        """Test error creation with stack trace."""
        trace = "Stack trace content"
        msg = create_error("agent", "Error", "Message", stack_trace=trace)
        assert msg.stack_trace == trace, "stack_trace is not valid"

    def test_create_error_with_recovery(self):
        """Test error creation with recovery action."""
        msg = create_error(
            "agent",
            "Error",
            "Message",
            recovery_action="Restart process",
        )
        assert msg.recovery_action == "Restart process", "recovery_action is not valid"


class TestCreateHeartbeat:
    """Test create_heartbeat factory function."""

    def test_create_heartbeat_basic(self):
        """Test basic heartbeat creation."""
        msg = create_heartbeat("watcher", 3600.5)
        assert msg.source == "watcher", "source is not valid"
        assert msg.uptime_seconds == 3600.5, "uptime_seconds is not valid"
        assert msg.message_type == MessageType.HEARTBEAT.value, "Value must be initialized"

    def test_create_heartbeat_last_activity(self):
        """Test that heartbeat sets last_activity."""
        msg = create_heartbeat("brain", 1000)
        assert msg.last_activity is not None, "last_activity must be initialized"
        assert "T" in msg.last_activity, "Condition must be true"

    def test_create_heartbeat_zero_uptime(self):
        """Test heartbeat with zero uptime."""
        msg = create_heartbeat("agent", 0.0)
        assert msg.uptime_seconds == 0.0, "uptime_seconds is not valid"


class TestBridgeTypesIntegration:
    """Integration tests for bridge types."""

    def test_message_correlation_flow(self):
        """Test query-response correlation flow."""
        # Create query
        query = create_query("agent", "Execute task")
        query_id = query.message_id

        # Create response to that query
        response = create_response("orchestrator", query_id, status="success", data={})
        assert response.response_to == query_id, "Response must not be empty"

    def test_status_monitoring_flow(self):
        """Test status monitoring flow."""
        # Various status updates
        status1 = create_status("brain", "brain", "running")
        status2 = create_status("orchestrator", "orchestrator", "idle")

        assert status1.component == "brain", "component is not valid"
        assert status2.component == "orchestrator", "component is not valid"

    def test_error_recovery_flow(self):
        """Test error with recovery flow."""
        error_msg = create_error(
            "agent",
            "ProcessError",
            "Process crashed",
            recovery_action="Retry with backoff",
        )

        # Can chain with status update
        status = create_status("agent", "agent", "error")

        assert error_msg.error_type == "ProcessError", "Error should be raised or set"
        assert status.status == "error", "Error should be raised or set"

    def test_all_message_types_creatable(self):
        """Test that all message types can be created."""
        messages = [
            create_context_update("source", {}),
            create_query("source", "query"),
            create_response("source", "to-id"),
            create_status("source", "comp", "running"),
            create_error("source", "type", "msg"),
            create_heartbeat("source", 100),
        ]

        assert len(messages) == 6, "Messages must not be empty"
        for msg in messages:
            assert isinstance(msg.timestamp, str)
            assert msg.source == "source", "source is not valid"
            assert msg.message_type is not None, "message_type must be initialized"
