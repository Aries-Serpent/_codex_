"""StdioTransport for MCP communication over stdin/stdout.

This module provides the stdio transport layer for MCP:
- Reading JSON-RPC messages from stdin
- Writing JSON-RPC responses to stdout
- Message framing and parsing
- Error handling for malformed input
"""

import asyncio
import json
import logging
import sys
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class TransportConfig:
    """Configuration for stdio transport."""

    max_message_size: int = 1024 * 1024  # 1MB default
    read_timeout_seconds: float = 300.0  # 5 minutes
    encoding: str = "utf-8"


class TransportError(Exception):
    """Base exception for transport errors."""


class MessageTooLargeError(TransportError):
    """Raised when a message exceeds the maximum size."""

    def __init__(self, size: int, max_size: int) -> None:
        self.size = size
        self.max_size = max_size
        super().__init__(f"Message size {size} exceeds maximum {max_size}")


class InvalidMessageError(TransportError):
    """Raised when a message cannot be parsed."""

    def __init__(self, reason: str, raw_data: Optional[str] = None) -> None:
        self.reason = reason
        self.raw_data = raw_data
        super().__init__(f"Invalid message: {reason}")


class StdioTransport:
    """Stdio transport for MCP JSON-RPC communication.

    This transport reads JSON-RPC messages from stdin and writes
    responses to stdout. Each message is expected to be on a single
    line (newline-delimited JSON).
    """

    def __init__(
        self,
        config: Optional[TransportConfig] = None,
        reader: Optional[asyncio.StreamReader] = None,
        writer: Optional[asyncio.StreamWriter] = None,
    ) -> None:
        """Initialize the stdio transport.

        Args:
            config: Transport configuration.
            reader: Optional custom reader (for testing).
            writer: Optional custom writer (for testing).
        """
        self._config = config or TransportConfig()
        self._reader = reader
        self._writer = writer
        self._running = False
        self._logger = logging.getLogger(__name__)

    async def _get_reader(self) -> asyncio.StreamReader:
        """Get or create the stdin reader."""
        if self._reader is not None:
            return self._reader

        # Create reader from stdin
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        self._reader = reader
        return reader

    async def _get_writer(self) -> asyncio.StreamWriter:
        """Get or create the stdout writer."""
        if self._writer is not None:
            return self._writer

        # Create writer to stdout
        loop = asyncio.get_event_loop()
        transport, protocol = await loop.connect_write_pipe(asyncio.Protocol, sys.stdout)
        writer = asyncio.StreamWriter(transport, protocol, None, loop)
        self._writer = writer
        return writer

    async def read_message(self) -> Optional[dict[str, Any]]:
        """Read a single JSON-RPC message from stdin.

        Returns:
            Parsed JSON-RPC message, or None if EOF reached.

        Raises:
            MessageTooLargeError: If message exceeds max size.
            InvalidMessageError: If message cannot be parsed.
        """
        reader = await self._get_reader()

        try:
            # Read a line with timeout
            line = await asyncio.wait_for(
                reader.readline(), timeout=self._config.read_timeout_seconds
            )
        except asyncio.TimeoutError:
            self._logger.warning("Read timeout reached")
            return None

        if not line:
            # EOF reached
            return None

        # Check message size
        if len(line) > self._config.max_message_size:
            raise MessageTooLargeError(len(line), self._config.max_message_size)

        # Decode and parse
        text: Optional[str] = None
        try:
            text = line.decode(self._config.encoding).strip()
            if not text:
                return None
            return json.loads(text)
        except UnicodeDecodeError as e:
            type(e).__name__
            logger.debug("UnicodeDecodeError: <ERROR_TYPE>")
            raise InvalidMessageError(f"Invalid encoding: {e}", str(line[:100])) from e
        except json.JSONDecodeError as e:
            raise InvalidMessageError(f"Invalid JSON: {e}", text[:100] if text else None) from e

    async def write_message(self, message: dict[str, Any]) -> None:
        """Write a JSON-RPC message to stdout.

        Args:
            message: JSON-RPC message to write.
        """
        writer = await self._get_writer()

        # Serialize and encode
        text = json.dumps(message, separators=(",", ":"))
        data = (text + "\n").encode(self._config.encoding)

        # Check size
        if len(data) > self._config.max_message_size:
            raise MessageTooLargeError(len(data), self._config.max_message_size)

        writer.write(data)
        await writer.drain()

    async def message_stream(self) -> AsyncIterator[dict[str, Any]]:
        """Iterate over incoming messages.

        Yields:
            Parsed JSON-RPC messages until EOF or error.
        """
        self._running = True

        while self._running:
            try:
                message = await self.read_message()
                if message is None:
                    break
                yield message
            except TransportError as e:
                type(e).__name__
                logger.debug("TransportError: <ERROR_TYPE>")
                self._logger.error("Transport error: %s", e)
                # Continue reading after recoverable errors
                continue

    def stop(self) -> None:
        """Stop reading messages."""
        self._running = False

    async def close(self) -> None:
        """Close the transport."""
        self.stop()
        if self._writer:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except (IOError, OSError) as exc:
                type(exc).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                # Ignore errors during writer closure - the stream may already be closed
                # or in an invalid state. This is a cleanup operation and errors are non-critical.
                self._logger.debug("Writer close failed: %s", exc)


class MockStdioTransport(StdioTransport):
    """Mock transport for testing without actual stdio."""

    def __init__(self, messages: Optional[list] = None) -> None:
        """Initialize mock transport.

        Args:
            messages: list of messages to return from read_message.
        """
        super().__init__()
        self._mock_messages = messages or []
        self._written_messages: list = []
        self._message_index = 0

    async def read_message(self) -> Optional[dict[str, Any]]:
        """Read from the mock message queue."""
        if self._message_index >= len(self._mock_messages):
            return None

        message = self._mock_messages[self._message_index]
        self._message_index += 1
        return message

    async def write_message(self, message: dict[str, Any]) -> None:
        """Write to the mock message buffer."""
        self._written_messages.append(message)

    def get_written_messages(self) -> list:
        """Get all messages written to this transport."""
        return self._written_messages

    def add_mock_message(self, message: dict[str, Any]) -> None:
        """Add a message to the mock queue."""
        self._mock_messages.append(message)
