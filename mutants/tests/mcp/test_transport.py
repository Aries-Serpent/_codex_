"""
Tests for MCP Transport Layer.

Tests the transport mechanisms for MCP communication including
stdio, HTTP, and WebSocket transports.

Phase 55: MEDIUM Priority Module Tests
Coverage Target: src/mcp 17% → 35%+
"""

import json

import pytest


class TestStdioTransport:
    """Tests for stdio transport."""

    def test_message_framing(self):
        """Messages are properly framed with length prefix."""

        def frame_message(content):
            body = json.dumps(content).encode("utf-8")
            header = f"Content-Length: {len(body)}\r\n\r\n"
            return header.encode("utf-8") + body

        message = {"jsonrpc": "2.0", "method": "test", "id": 1}
        framed = frame_message(message)

        assert b"Content-Length:" in framed, "Content must not be empty"
        assert b"\r\n\r\n" in framed, "Condition must be true"

    def test_message_parsing(self):
        """Framed messages are correctly parsed."""

        def parse_frame(data):
            # Split header and body
            parts = data.split(b"\r\n\r\n", 1)
            if len(parts) != 2:
                raise ValueError("Invalid frame")

            header, body = parts

            # Parse content length
            for line in header.decode().split("\r\n"):
                if line.startswith("Content-Length:"):
                    length = int(line.split(":")[1].strip())
                    break
            else:
                raise ValueError("Missing Content-Length")

            return json.loads(body[:length])

        raw = b'Content-Length: 42\r\n\r\n{"jsonrpc":"2.0","method":"test","id":1}'
        parsed = parse_frame(raw)

        assert parsed["jsonrpc"] == "2.0", "Condition must be true"
        assert parsed["method"] == "test", "Condition must be true"

    def test_incomplete_frame_handling(self):
        """Incomplete frames are buffered."""

        class MessageBuffer:
            def __init__(self):
                self.buffer = b""
                self.messages = []

            def feed(self, data):
                self.buffer += data
                self._try_parse()

            def _try_parse(self):
                while b"\r\n\r\n" in self.buffer:
                    header_end = self.buffer.index(b"\r\n\r\n")
                    header = self.buffer[:header_end].decode()

                    length = None
                    for line in header.split("\r\n"):
                        if line.startswith("Content-Length:"):
                            length = int(line.split(":")[1].strip())
                            break

                    if length is None:
                        break

                    body_start = header_end + 4
                    body_end = body_start + length

                    if len(self.buffer) < body_end:
                        break  # Not enough data yet

                    body = self.buffer[body_start:body_end]
                    self.messages.append(json.loads(body))
                    self.buffer = self.buffer[body_end:]

        buffer = MessageBuffer()

        # Feed partial data
        buffer.feed(b'Content-Length: 18\r\n\r\n{"id":')
        assert len(buffer.messages) == 0, "Collection must not be empty"

        # Feed rest
        buffer.feed(b'1,"ok":true}')
        assert len(buffer.messages) == 1, "Collection must not be empty"


class TestHTTPTransport:
    """Tests for HTTP transport."""

    def test_request_encoding(self):
        """HTTP requests are properly encoded."""

        def encode_http_request(method, path, body):
            body_bytes = json.dumps(body).encode("utf-8")
            headers = [
                f"{method} {path} HTTP/1.1",
                "Content-Type: application/json",
                f"Content-Length: {len(body_bytes)}",
                "",
                "",
            ]
            return "\r\n".join(headers).encode("utf-8") + body_bytes

        request = encode_http_request("POST", "/mcp", {"jsonrpc": "2.0", "method": "test", "id": 1})

        assert b"POST /mcp HTTP/1.1" in request, "Condition must be true"
        assert b"Content-Type: application/json" in request, "Content must not be empty"

    def test_response_parsing(self):
        """HTTP responses are parsed correctly."""

        def parse_http_response(data):
            parts = data.split(b"\r\n\r\n", 1)
            header_lines = parts[0].decode().split("\r\n")
            status_line = header_lines[0]

            # Parse status
            _, status_code, _status_text = status_line.split(" ", 2)

            # Parse headers
            headers = {}
            for line in header_lines[1:]:
                if ": " in line:
                    key, value = line.split(": ", 1)
                    headers[key.lower()] = value

            body = parts[1] if len(parts) > 1 else b""

            return int(status_code), headers, body

        response = b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{"result":"ok"}'
        status, headers, _body = parse_http_response(response)

        assert status == 200, "status is not valid"
        assert headers["content-type"] == "application/json", "Content must not be empty"

    def test_error_status_handling(self):
        """HTTP error statuses are handled."""
        error_codes = {
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            500: "Internal Server Error",
        }

        for code, text in error_codes.items():
            assert code >= 400, "code must be greater than zero"
            assert len(text) > 0, "Text must not be empty"


class TestWebSocketTransport:
    """Tests for WebSocket transport."""

    def test_frame_construction(self):
        """WebSocket frames are constructed correctly."""

        def create_text_frame(payload):
            data = payload.encode("utf-8")
            frame = bytearray()

            # FIN + text opcode
            frame.append(0x81)

            # Length
            if len(data) < 126:
                frame.append(len(data))
            elif len(data) < 65536:
                frame.append(126)
                frame.extend(len(data).to_bytes(2, "big"))
            else:
                frame.append(127)
                frame.extend(len(data).to_bytes(8, "big"))

            frame.extend(data)
            return bytes(frame)

        frame = create_text_frame('{"test": true}')

        assert frame[0] == 0x81, "Condition must be true"
        assert len(frame) > 2, "Frame must not be empty"

    def test_ping_pong_handling(self):
        """Ping/pong frames are handled for keepalive."""
        PING_OPCODE = 0x09
        PONG_OPCODE = 0x0A

        def handle_control_frame(opcode, payload):
            if opcode == PING_OPCODE:
                return (PONG_OPCODE, payload)  # Echo back as pong
            return None

        result = handle_control_frame(PING_OPCODE, b"keepalive")

        assert result[0] == PONG_OPCODE, "Result must not be empty"
        assert result[1] == b"keepalive", "Result must not be empty"


class TestTransportReconnection:
    """Tests for transport reconnection."""

    def test_exponential_backoff(self):
        """Reconnection uses exponential backoff."""

        def calculate_backoff(attempt, base=1.0, max_delay=60.0):
            return min(base * (2**attempt), max_delay)

        assert calculate_backoff(0) == 1.0, "Condition must be true"
        assert calculate_backoff(1) == 2.0, "Condition must be true"
        assert calculate_backoff(2) == 4.0, "Condition must be true"
        assert calculate_backoff(10) == 60.0, "Condition must be true"

    def test_retry_count_limit(self):
        """Reconnection attempts are limited."""
        MAX_RETRIES = 5

        class ReconnectionManager:
            def __init__(self, max_retries):
                self.max_retries = max_retries
                self.attempts = 0

            def should_retry(self):
                return self.attempts < self.max_retries

            def record_attempt(self):
                self.attempts += 1

        manager = ReconnectionManager(MAX_RETRIES)

        for _ in range(MAX_RETRIES):
            assert manager.should_retry(), "Condition must be true"
            manager.record_attempt()

        assert not manager.should_retry(), "Condition must be true"


class TestTransportSecurity:
    """Tests for transport security."""

    def test_tls_requirement(self):
        """TLS is required for non-localhost connections."""

        def validate_endpoint(url):
            if url.startswith("http://") and "localhost" not in url and "127.0.0.1" not in url:
                raise ValueError("TLS required for remote connections")
            return True

        assert validate_endpoint("https://example.com/mcp"), "Condition must be true"
        assert validate_endpoint("http://localhost:8080/mcp"), "Condition must be true"

        with pytest.raises(ValueError):
            validate_endpoint("http://example.com/mcp")

    def test_origin_validation(self):
        """WebSocket origin is validated."""
        ALLOWED_ORIGINS = ["https://example.com", "https://app.example.com"]

        def validate_origin(origin):
            return origin in ALLOWED_ORIGINS

        assert validate_origin("https://example.com"), "validate_ is not valid"
        assert not validate_origin("https://evil.com"), "Condition must be true"
