"""Unit tests for MCP server behavior."""

import asyncio
from typing import Any, Optional

import pytest

from mcp.server import MCPServer, Tool, ToolRegistry
from mcp.server.stdio import (
    InvalidMessageError,
    MessageTooLargeError,
    StdioTransport,
    TransportConfig,
    TransportError,
)


def _run(coro: Any) -> Any:
    """Helper to run async coroutines in sync tests."""
    return asyncio.run(coro)


def test_server_listtools_request() -> None:
    """Test that mcp.listTools returns a plain list as the JSON-RPC result.

    This validates the requirement that listTools must return a plain list
    of tools, not wrapped in an object like {"tools": [...], "version": "..."}.
    This matches JSON-RPC client expectations and the MCP specification.
    """
    # Arrange
    registry = ToolRegistry()
    registry.register(Tool(name="tool1", description="First tool"))
    registry.register(Tool(name="tool2", description="Second tool"))
    server = MCPServer(tool_registry=registry)

    # Act: JSON-RPC request (not notification) for mcp.listTools
    request: dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": "abc",
        "method": "mcp.listTools",
        "params": {},
    }
    response: Optional[dict[str, Any]] = _run(server.handle_request(request))

    # Assert: JSON-RPC response structure
    assert response is not None, "response must be initialized"
    assert response["jsonrpc"] == "2.0", "Response must not be empty"
    assert response["id"] == "abc", "Response must not be empty"

    result = response["result"]
    # Requirement: result must be a plain list
    assert isinstance(result, list)
    assert all(isinstance(t, dict) for t in result)

    names = {t["name"] for t in result}
    assert names == {"tool1", "tool2"}


def test_server_notification_handling() -> None:
    """Test that JSON-RPC notifications (requests without 'id') produce no response.

    Per JSON-RPC 2.0 spec, notifications are requests that omit the 'id' field.
    The server must execute any side effects but must NOT send back a response,
    even if the method is unknown or errors occur.
    """
    registry = ToolRegistry()
    server = MCPServer(tool_registry=registry)

    # Notification: no "id" field
    request: dict[str, Any] = {
        "jsonrpc": "2.0",
        "method": "mcp.listTools",
        "params": {},
    }

    response = _run(server.handle_request(request))

    # Requirement: notifications must NOT produce a response
    assert response is None, "Response must not be empty"


def test_server_negotiate_version() -> None:
    """Test that mcp.negotiateVersion returns a plain string as the JSON-RPC result.

    This validates the requirement that negotiateVersion must return the negotiated
    version string directly (not wrapped in a dict), matching the expectations from
    PR #2286 discussion_r2538925659.
    """
    # Arrange
    registry = ToolRegistry()
    server = MCPServer(tool_registry=registry)

    # Act: JSON-RPC request for mcp.negotiateVersion with client supporting multiple versions
    request: dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": "vneg",
        "method": "mcp.negotiateVersion",
        "params": {"supported": ["0.9", "1.0"]},
    }
    response: Optional[dict[str, Any]] = _run(server.handle_request(request))

    # Assert: JSON-RPC response structure
    assert response is not None, "response must be initialized"
    assert response["jsonrpc"] == "2.0", "Response must not be empty"
    assert response["id"] == "vneg", "Response must not be empty"

    # Requirement: result must be a plain string (the negotiated version)
    result = response["result"]
    assert isinstance(result, str)
    assert result == "1.0", "Result must not be empty"


def test_server_negotiate_version_no_overlap() -> None:
    """Test that mcp.negotiateVersion returns a JSON-RPC error when no version matches.

    When the client's supported versions have no overlap with the server's supported
    versions, the server must respond with a JSON-RPC error (code -32602).
    """
    # Arrange
    registry = ToolRegistry()
    server = MCPServer(tool_registry=registry)

    # Act: JSON-RPC request with no overlapping versions
    request: dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": "vneg-no-overlap",
        "method": "mcp.negotiateVersion",
        "params": {"supported": ["0.8", "0.9"]},
    }
    response: Optional[dict[str, Any]] = _run(server.handle_request(request))

    # Assert: JSON-RPC error response
    assert response is not None, "response must be initialized"
    assert response["jsonrpc"] == "2.0", "Response must not be empty"
    assert response["id"] == "vneg-no-overlap", "Response must not be empty"
    assert "error" in response, "Response must not be empty"
    assert response["error"]["code"] == -32602, "Response must not be empty"
    assert "No compatible version found" in response["error"]["message"], "Response must not be empty"


async def _stdio_round_trip() -> bytes:
    reader = asyncio.StreamReader()

    class _MemoryWriter:
        def __init__(self) -> None:
            self.buffer = b""

        def write(self, data: bytes) -> None:
            self.buffer += data

        async def drain(self) -> None:  # pragma: no cover - noop
            return None

    writer = _MemoryWriter()
    transport = StdioTransport(
        config=TransportConfig(max_message_size=1024, read_timeout_seconds=1.0),
        reader=reader,
        writer=writer,  # type: ignore[arg-type]
    )

    reader.feed_data(b'{"jsonrpc":"2.0","id":1,"method":"ping"}\n')
    reader.feed_eof()

    message = await transport.read_message()
    assert message["id"] == 1, "Condition must be true"

    await transport.write_message({"ok": True})
    return writer.buffer


def test_stdio_transport_round_trip() -> None:
    output = _run(_stdio_round_trip())
    assert output.endswith(b"\n"), "Condition must be true"
    assert b'"ok":true' in output, "Condition must be true"


def test_stdio_transport_raises_error_on_invalid_json() -> None:
    async def _exercise() -> None:
        reader = asyncio.StreamReader()
        transport = StdioTransport(reader=reader, writer=None)
        reader.feed_data(b"{not-json}\n")
        reader.feed_eof()
        with pytest.raises(InvalidMessageError, match="Invalid JSON"):
            await transport.read_message()

    _run(_exercise())


def test_stdio_transport_handles_wait_for_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _close_and_raise_timeout(awaitable: Any, *args: Any, **kwargs: Any) -> Any:
        close = getattr(awaitable, "close", None)
        if callable(close):
            close()
        raise asyncio.TimeoutError

    async def _exercise() -> None:
        reader = asyncio.StreamReader()
        transport = StdioTransport(reader=reader, writer=None)
        monkeypatch.setattr(asyncio, "wait_for", _close_and_raise_timeout)
        assert await transport.read_message() is None, "Condition must be true"

    _run(_exercise())


def test_stdio_transport_builds_reader_from_event_loop(monkeypatch: pytest.MonkeyPatch) -> None:
    class _FakeLoop:
        def __init__(self) -> None:
            self.connected = None

        async def connect_read_pipe(self, factory, pipe):
            self.connected = (factory(), pipe)

    async def _verify_reader_creation() -> tuple[bool, bool]:
        import sys

        loop = _FakeLoop()
        transport = StdioTransport(reader=None, writer=None)
        monkeypatch.setattr(asyncio, "get_event_loop", lambda: loop)
        reader = await transport._get_reader()
        return isinstance(reader, asyncio.StreamReader), loop.connected[1] is sys.stdin

    assert _run(_verify_reader_creation()) == (True, True)


def test_stdio_transport_builds_writer_from_event_loop(monkeypatch: pytest.MonkeyPatch) -> None:
    class _FakeLoop:
        async def connect_write_pipe(self, protocol_factory, pipe):
            return object(), protocol_factory()

    class _FakeWriter:
        def __init__(self, transport: Any, protocol: Any, reader: Any, loop: Any) -> None:
            self.transport = transport
            self.protocol = protocol
            self.reader = reader
            self.loop = loop

    async def _verify_writer_creation() -> bool:
        transport = StdioTransport(reader=None, writer=None)
        monkeypatch.setattr(asyncio, "get_event_loop", lambda: _FakeLoop())
        monkeypatch.setattr(asyncio, "StreamWriter", _FakeWriter)
        writer = await transport._get_writer()
        return isinstance(writer, _FakeWriter)

    assert _run(_verify_writer_creation()) is True, "Condition must be true"


def test_stdio_transport_returns_none_for_blank_lines() -> None:
    async def _exercise() -> Optional[dict[str, Any]]:
        reader = asyncio.StreamReader()
        transport = StdioTransport(reader=reader, writer=None)
        reader.feed_data(b"\n")
        reader.feed_eof()
        return await transport.read_message()

    assert _run(_exercise()) is None, "Condition must be true"


def test_stdio_transport_returns_none_for_eof() -> None:
    async def _exercise() -> Optional[dict[str, Any]]:
        eof_reader = asyncio.StreamReader()
        eof_transport = StdioTransport(reader=eof_reader, writer=None)
        eof_reader.feed_eof()
        return await eof_transport.read_message()

    assert _run(_exercise()) is None, "Condition must be true"


def test_stdio_transport_rejects_invalid_encoding() -> None:
    async def _exercise() -> None:
        reader = asyncio.StreamReader()
        transport = StdioTransport(reader=reader, writer=None)
        reader.feed_data(b"\xff\xfe\n")
        reader.feed_eof()
        with pytest.raises(InvalidMessageError, match="Invalid encoding"):
            await transport.read_message()

    _run(_exercise())


def test_stdio_transport_rejects_oversized_writes() -> None:
    class _MemoryWriter:
        def write(self, data: bytes) -> None:
            self.data = data

        async def drain(self) -> None:
            return None

    async def _exercise() -> None:
        transport = StdioTransport(
            config=TransportConfig(max_message_size=4),
            reader=None,
            writer=_MemoryWriter(),  # type: ignore[arg-type]
        )
        with pytest.raises(MessageTooLargeError, match="exceeds maximum"):
            await transport.write_message({"id": 1})

    _run(_exercise())


def test_stdio_transport_rejects_oversized_messages() -> None:
    async def _exercise() -> None:
        reader = asyncio.StreamReader()
        transport = StdioTransport(
            config=TransportConfig(max_message_size=4),
            reader=reader,
            writer=None,
        )
        reader.feed_data(b'{"id":1}\n')
        reader.feed_eof()
        with pytest.raises(MessageTooLargeError, match="exceeds maximum"):
            await transport.read_message()

    _run(_exercise())


def test_message_stream_skips_transport_errors() -> None:
    class _RecoveringTransport(StdioTransport):
        def __init__(self) -> None:
            super().__init__(reader=None, writer=None)
            self._calls = 0

        async def read_message(self) -> Optional[dict[str, Any]]:
            self._calls += 1
            if self._calls == 1:
                raise TransportError("transient")
            if self._calls == 2:
                return {"jsonrpc": "2.0", "id": "ok"}
            return None

    async def _exercise() -> list[dict[str, Any]]:
        transport = _RecoveringTransport()
        return [message async for message in transport.message_stream()]

    assert _run(_exercise()) == [{"jsonrpc": "2.0", "id": "ok"}]


def test_close_swallows_writer_wait_closed_errors() -> None:
    class _BrokenWriter:
        def __init__(self) -> None:
            self.closed = False

        def close(self) -> None:
            self.closed = True

        async def wait_closed(self) -> None:
            raise RuntimeError("already closed")

    async def _exercise() -> bool:
        writer = _BrokenWriter()
        transport = StdioTransport(writer=writer)  # type: ignore[arg-type]
        await transport.close()
        return writer.closed

    assert _run(_exercise()) is True, "Condition must be true"


def test_mock_stdio_transport_buffers_messages() -> None:
    from mcp.server.stdio import MockStdioTransport

    async def _exercise() -> tuple[
        Optional[dict[str, Any]],
        Optional[dict[str, Any]],
        Optional[dict[str, Any]],
        list[dict[str, Any]],
    ]:
        transport = MockStdioTransport(messages=[{"id": 1}])
        transport.add_mock_message({"id": 2})
        first = await transport.read_message()
        second = await transport.read_message()
        empty_result = await transport.read_message()
        await transport.write_message({"ok": True})
        return first, second, empty_result, transport.get_written_messages()

    assert _run(_exercise()) == ({"id": 1}, {"id": 2}, None, [{"ok": True}])
