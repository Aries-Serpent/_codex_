"""
MCP (Model Context Protocol) Server Integration for Cascade Delegation.

Provides integration with external MCP servers for extended capabilities
while supporting mock/simulation mode for environments without real servers.
"""

import asyncio
import json
import logging
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MCPConnectionMode(Enum):
    """MCP connection operating modes."""

    MOCK = "mock"            # Simulated responses for testing
    REAL = "real"            # Real MCP server connections (JSON-RPC 2.0)
    STREAMING = "streaming"  # Streaming JSON-RPC 2.0 via Server-Sent Events (IMP-005)


@dataclass
class MCPServer:
    """Model Context Protocol server configuration."""

    name: str
    url: str
    capabilities: List[str]
    auth_token: Optional[str] = None
    timeout: int = 30
    enabled: bool = True


@dataclass
class MCPRequest:
    """MCP request structure."""

    server_name: str
    capability: str
    payload: Dict[str, Any]
    request_id: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class MCPResponse:
    """MCP response structure."""

    request_id: str
    server_name: str
    status: str  # success, error, timeout
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MCPIntegration:
    """
    Integrates MCP servers for extended agent capabilities.

    Supports both real and mock modes. Real mode requires MCP_REAL_MODE=true.
    """

    DEFAULT_SERVERS = [
        MCPServer(
            name="github",
            url="mcp://github.com/servers/default",
            capabilities=["repository_access", "issue_management", "pr_operations", "code_search"],
        ),
        MCPServer(
            name="codex_physics",
            url="mcp://localhost:8080/codex/physics",
            capabilities=[
                "quantum_analysis",
                "entanglement_detection",
                "superposition_reasoning",
                "chaos_theory",
            ],
            enabled=False,  # Disabled by default, enable when local server running
        ),
        MCPServer(
            name="local_tools",
            url="mcp://localhost:9090/tools",
            capabilities=["file_operations", "process_management", "network_tools"],
        ),
    ]

    def __init__(self, mode: Optional[MCPConnectionMode] = None):
        """
        Initialize MCP integration.

        Args:
            mode: Connection mode. If None, determined from MCP_REAL_MODE env var.
        """
        self.servers: Dict[str, MCPServer] = {}
        self.active_connections: Dict[str, Any] = {}
        self.request_history: List[MCPRequest] = []
        self.response_cache: Dict[str, MCPResponse] = {}

        # Determine mode from environment or parameter
        if mode is None:
            env_mode = os.getenv("MCP_REAL_MODE", "false").lower()
            env_streaming = os.getenv("MCP_STREAMING_MODE", "false").lower()
            if env_streaming == "true":
                self.mode = MCPConnectionMode.STREAMING
            elif env_mode == "true":
                self.mode = MCPConnectionMode.REAL
            else:
                self.mode = MCPConnectionMode.MOCK
        else:
            self.mode = mode

        logger.info(f"MCP Integration initialized in {self.mode.value} mode")

        # Initialize default servers
        self._initialize_defaults()

    def _initialize_defaults(self):
        """Initialize default MCP servers."""
        for server in self.DEFAULT_SERVERS:
            self.register_server(server)

    def register_server(self, server: MCPServer):
        """Register an MCP server."""
        self.servers[server.name] = server
        logger.info(
            f"Registered MCP server: {server.name} ({'enabled' if server.enabled else 'disabled'})"
        )

    async def connect(self, server_name: str) -> bool:
        """
        Connect to an MCP server.

        Args:
            server_name: Name of server to connect to

        Returns:
            True if connection successful
        """
        if server_name not in self.servers:
            logger.error(f"Server {server_name} not registered")
            return False

        server = self.servers[server_name]

        if not server.enabled:
            logger.warning(f"Server {server_name} is disabled")
            return False

        if self.mode == MCPConnectionMode.MOCK:
            # Mock connection always succeeds
            self.active_connections[server_name] = {
                "status": "connected_mock",
                "timestamp": datetime.now(timezone.utc),
            }
            logger.info(f"Mock connection to {server_name} established")
            return True

        else:
            # Real connection logic (requires aiohttp or similar)
            try:
                # Placeholder for real connection logic
                # In production, this would use actual MCP client library
                logger.info(f"Attempting real connection to {server.url}")

                # Simulated connection attempt
                await asyncio.sleep(0.1)  # Simulated network delay

                self.active_connections[server_name] = {
                    "status": "connected_real",
                    "url": server.url,
                    "timestamp": datetime.now(timezone.utc),
                }
                logger.info(f"Real connection to {server_name} established")
                return True

            except Exception as e:
                logger.error(f"Failed to connect to {server_name}: {e}")
                return False

    async def execute(self, request: MCPRequest) -> MCPResponse:
        """
        Execute an MCP request.

        Args:
            request: MCP request to execute

        Returns:
            MCP response
        """
        self.request_history.append(request)

        # Check if server exists and is enabled
        if request.server_name not in self.servers:
            return MCPResponse(
                request_id=request.request_id,
                server_name=request.server_name,
                status="error",
                error=f"Server {request.server_name} not registered",
            )

        server = self.servers[request.server_name]

        if not server.enabled:
            return MCPResponse(
                request_id=request.request_id,
                server_name=request.server_name,
                status="error",
                error=f"Server {request.server_name} is disabled",
            )

        # Check if capability is supported
        if request.capability not in server.capabilities:
            return MCPResponse(
                request_id=request.request_id,
                server_name=request.server_name,
                status="error",
                error=f"Capability {request.capability} not supported by {request.server_name}",
            )

        # Ensure connection exists
        if request.server_name not in self.active_connections:
            connected = await self.connect(request.server_name)
            if not connected:
                return MCPResponse(
                    request_id=request.request_id,
                    server_name=request.server_name,
                    status="error",
                    error=f"Failed to connect to {request.server_name}",
                )

        # Execute based on mode
        if self.mode == MCPConnectionMode.MOCK:
            response = await self._execute_mock(request, server)
        elif self.mode == MCPConnectionMode.STREAMING:
            response = await self._execute_streaming(request, server)
        else:
            response = await self._execute_real(request, server)

        # Cache response
        self.response_cache[request.request_id] = response

        return response

    async def _execute_mock(self, request: MCPRequest, server: MCPServer) -> MCPResponse:
        """Execute request in mock mode."""
        # Simulated processing delay
        await asyncio.sleep(0.05)

        # Generate mock response based on capability
        mock_data = self._generate_mock_data(request.capability, request.payload)

        return MCPResponse(
            request_id=request.request_id,
            server_name=request.server_name,
            status="success",
            data=mock_data,
        )

    async def _execute_real(self, request: MCPRequest, server: MCPServer) -> MCPResponse:
        """Execute request via JSON-RPC 2.0 over HTTP/HTTPS (IMP-004).

        Sends a JSON-RPC 2.0 POST request to the server endpoint.  The
        endpoint is resolved in priority order:

        1. ``CODEX_MCP_ENDPOINT`` environment variable (staging/dev override)
        2. ``server.url``

        The request body follows the JSON-RPC 2.0 specification::

            {
                "jsonrpc": "2.0",
                "id": "<request_id>",
                "method": "tools/<capability>",
                "params": { ... }
            }

        The response is expected to have either a ``result`` key (success)
        or an ``error`` key (failure) as defined by JSON-RPC 2.0.

        Falls back gracefully: if the endpoint is not an HTTP/HTTPS URL
        (e.g. ``mcp://...`` scheme used in tests), the request is logged
        and a synthetic error response (``status="error"``) is returned,
        indicating an unsupported endpoint scheme, so unit tests that rely
        on mock mode continue to work when ``MCPConnectionMode.REAL`` is
        forced.
        """
        endpoint = os.environ.get("CODEX_MCP_ENDPOINT") or server.url
        logger.info("MCP JSON-RPC 2.0 request → %s (capability=%s)", endpoint, request.capability)

        # Only attempt HTTP/HTTPS transport; other schemes are not supported.
        if not endpoint.startswith(("http://", "https://")):
            logger.warning(
                "MCP endpoint %r uses an unsupported scheme (not http/https); returning error response",
                endpoint,
            )
            return MCPResponse(
                request_id=request.request_id,
                server_name=request.server_name,
                status="error",
                error=f"Unsupported endpoint scheme: {endpoint!r}",
            )

        rpc_payload: Dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": request.request_id,
            "method": f"tools/{request.capability}",
            "params": request.payload,
        }

        try:
            # Run the blocking urllib call in a thread-pool executor so the
            # async event loop is not blocked (aiohttp is not a hard dependency).
            loop = asyncio.get_running_loop()
            body = await loop.run_in_executor(
                None,
                lambda: self._http_post_json(
                    endpoint,
                    rpc_payload,
                    auth_token=server.auth_token,
                    timeout=server.timeout,
                ),
            )

            if "error" in body:
                rpc_error = body["error"]
                message = (
                    rpc_error.get("message", str(rpc_error))
                    if isinstance(rpc_error, dict)
                    else str(rpc_error)
                )
                logger.error("MCP JSON-RPC error from %s: %s", endpoint, message)
                return MCPResponse(
                    request_id=request.request_id,
                    server_name=request.server_name,
                    status="error",
                    error=message,
                )

            result = body.get("result")
            return MCPResponse(
                request_id=request.request_id,
                server_name=request.server_name,
                status="success",
                data=result if isinstance(result, dict) else {"result": result},
            )

        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode(errors="replace")
            logger.error("MCP HTTP error %d from %s: %s", exc.code, endpoint, error_body)
            return MCPResponse(
                request_id=request.request_id,
                server_name=request.server_name,
                status="error",
                error=f"HTTP {exc.code}: {exc.reason}",
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("MCP execution error for %s: %s", endpoint, exc)
            return MCPResponse(
                request_id=request.request_id,
                server_name=request.server_name,
                status="error",
                error=str(exc),
            )

    @staticmethod
    def _http_post_json(
        url: str,
        payload: Dict[str, Any],
        auth_token: Optional[str] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """Send a synchronous HTTP POST with a JSON body and return the decoded response.

        Parameters
        ----------
        url:
            HTTP/HTTPS endpoint to POST to.  Must start with ``https://`` or
            ``http://`` — plain ``http://`` is accepted but callers should
            prefer HTTPS for any production endpoint.
        payload:
            JSON-serialisable request body.
        auth_token:
            Optional bearer token for the ``Authorization`` header.
        timeout:
            Request timeout in seconds.

        Returns
        -------
        dict
            Decoded JSON response body.

        Raises
        ------
        ValueError
            If *url* does not start with ``http://`` or ``https://``.
        """
        if not url.startswith(("http://", "https://")):
            raise ValueError(f"_http_post_json: URL must start with http:// or https://, got: {url!r}")
        data = json.dumps(payload).encode("utf-8")
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec B310
            return json.loads(resp.read())

    async def _execute_streaming(self, request: MCPRequest, server: MCPServer) -> MCPResponse:
        """Execute request via streaming JSON-RPC 2.0 using Server-Sent Events (IMP-005).

        Sends the same JSON-RPC 2.0 POST as ``_execute_real`` but adds
        ``Accept: text/event-stream`` to request SSE streaming.  The server
        should respond with ``Content-Type: text/event-stream`` and emit
        ``data: <json>`` lines.  Each line is accumulated; the *last* data
        line is treated as the final result.

        Falls back transparently to the standard (non-streaming) transport
        when the server responds with a non-SSE ``Content-Type``, ensuring
        backward compatibility with MCP servers that do not support streaming.

        Endpoint resolution follows the same priority as ``_execute_real``:

        1. ``CODEX_MCP_ENDPOINT`` environment variable
        2. ``server.url``
        """
        endpoint = os.environ.get("CODEX_MCP_ENDPOINT") or server.url
        logger.info(
            "MCP JSON-RPC 2.0 streaming request → %s (capability=%s)",
            endpoint,
            request.capability,
        )

        if not endpoint.startswith(("http://", "https://")):
            logger.warning(
                "MCP streaming endpoint %r uses an unsupported scheme; returning error response",
                endpoint,
            )
            return MCPResponse(
                request_id=request.request_id,
                server_name=request.server_name,
                status="error",
                error=f"Unsupported endpoint scheme for streaming: {endpoint!r}",
            )

        rpc_payload: Dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": request.request_id,
            "method": f"tools/{request.capability}",
            "params": request.payload,
        }

        try:
            loop = asyncio.get_running_loop()
            body = await loop.run_in_executor(
                None,
                lambda: self._http_post_json_streaming(
                    endpoint,
                    rpc_payload,
                    auth_token=server.auth_token,
                    timeout=server.timeout,
                ),
            )

            if "error" in body:
                rpc_error = body["error"]
                message = (
                    rpc_error.get("message", str(rpc_error))
                    if isinstance(rpc_error, dict)
                    else str(rpc_error)
                )
                logger.error("MCP streaming JSON-RPC error from %s: %s", endpoint, message)
                return MCPResponse(
                    request_id=request.request_id,
                    server_name=request.server_name,
                    status="error",
                    error=message,
                )

            result = body.get("result")
            streaming_chunks = body.get("_streaming_chunks", 0)
            logger.info(
                "MCP streaming complete from %s — %d SSE chunk(s) received",
                endpoint,
                streaming_chunks,
            )
            return MCPResponse(
                request_id=request.request_id,
                server_name=request.server_name,
                status="success",
                data=(
                    result if isinstance(result, dict)
                    else {"result": result, "_streaming_chunks": streaming_chunks}
                ),
            )

        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode(errors="replace")
            logger.error(
                "MCP streaming HTTP error %d from %s: %s", exc.code, endpoint, error_body
            )
            return MCPResponse(
                request_id=request.request_id,
                server_name=request.server_name,
                status="error",
                error=f"HTTP {exc.code}: {exc.reason}",
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("MCP streaming execution error for %s: %s", endpoint, exc)
            return MCPResponse(
                request_id=request.request_id,
                server_name=request.server_name,
                status="error",
                error=str(exc),
            )

    @staticmethod
    def _http_post_json_streaming(
        url: str,
        payload: Dict[str, Any],
        auth_token: Optional[str] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """POST JSON and read the response as Server-Sent Events (SSE) or plain JSON.

        If the server responds with ``Content-Type: text/event-stream``, each
        ``data: <json>`` line is parsed and accumulated.  The *last* data frame
        that contains a ``result`` or ``error`` key is returned as the final
        body, with an additional ``_streaming_chunks`` counter.

        If the response is plain JSON (non-SSE), the body is decoded normally —
        providing transparent fallback for non-streaming MCP servers.

        Parameters
        ----------
        url:
            HTTP/HTTPS endpoint — must start with ``http://`` or ``https://``.
        payload:
            JSON-serialisable request body (JSON-RPC 2.0 object).
        auth_token:
            Optional bearer token for the ``Authorization`` header.
        timeout:
            Request timeout in seconds.

        Returns
        -------
        dict
            Final decoded JSON result, plus ``_streaming_chunks`` count when
            SSE streaming was used.

        Raises
        ------
        ValueError
            If *url* does not start with ``http://`` or ``https://``.
        """
        if not url.startswith(("http://", "https://")):
            raise ValueError(
                f"_http_post_json_streaming: URL must start with http:// or https://, got: {url!r}"
            )
        data = json.dumps(payload).encode("utf-8")
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream, application/json",
        }
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec B310
            content_type = resp.headers.get("Content-Type", "")
            raw = resp.read()

        if "text/event-stream" not in content_type:
            # Non-streaming server — decode as plain JSON (fallback path).
            return json.loads(raw)

        # Parse SSE stream: collect all `data:` frames, return the final one.
        chunks: List[Dict[str, Any]] = []
        for line in raw.decode("utf-8").splitlines():
            line = line.strip()
            if line.startswith("data:"):
                fragment = line[len("data:"):].strip()
                if fragment in ("", "[DONE]"):
                    continue
                try:
                    frame = json.loads(fragment)
                    if isinstance(frame, dict):
                        chunks.append(frame)
                except json.JSONDecodeError:
                    logger.debug("MCP SSE: skipping non-JSON fragment: %r", fragment)

        if not chunks:
            return {"error": {"message": "SSE stream contained no parseable data frames"}}

        # The last frame with result/error wins; merge chunk count for observability.
        final = chunks[-1]
        final["_streaming_chunks"] = len(chunks)
        return final

    def _generate_mock_data(self, capability: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock response data based on capability."""

        if capability == "repository_access":
            return {
                "repository": payload.get("repo", "unknown"),
                "access_granted": True,
                "branches": ["main", "develop", "feature/new"],
                "recent_commits": 42,
            }

        elif capability == "quantum_analysis":
            return {
                "quantum_state": "superposition",
                "entanglement_score": 0.85,
                "coherence": 0.92,
                "analysis": "System exhibits strong quantum characteristics",
            }

        elif capability == "entanglement_detection":
            return {
                "entangled_pairs": [
                    {"task_a": "task_1", "task_b": "task_3", "strength": 0.78},
                    {"task_a": "task_2", "task_b": "task_4", "strength": 0.65},
                ],
                "total_detected": 2,
            }

        elif capability == "code_search":
            return {
                "query": payload.get("query", ""),
                "results": [
                    {"file": "src/main.py", "line": 42, "match": "def process()"},
                    {"file": "tests/test_main.py", "line": 15, "match": "test_process()"},
                ],
                "total_matches": 2,
            }

        elif capability == "issue_management":
            return {
                "operation": payload.get("operation", "list"),
                "issues": [
                    {"number": 123, "title": "Bug fix", "state": "open"},
                    {"number": 124, "title": "Feature request", "state": "open"},
                ],
                "count": 2,
            }

        else:
            return {
                "capability": capability,
                "status": "executed",
                "mock": True,
                "payload_received": payload,
            }

    async def disconnect(self, server_name: str):
        """Disconnect from an MCP server."""
        if server_name in self.active_connections:
            del self.active_connections[server_name]
            logger.info(f"Disconnected from {server_name}")

    async def disconnect_all(self):
        """Disconnect from all MCP servers."""
        server_names = list(self.active_connections.keys())
        for server_name in server_names:
            await self.disconnect(server_name)

    def get_available_capabilities(self) -> Dict[str, List[str]]:
        """Get all available capabilities from registered servers."""
        capabilities = {}
        for name, server in self.servers.items():
            if server.enabled:
                capabilities[name] = server.capabilities
        return capabilities

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about MCP usage."""
        return {
            "mode": self.mode.value,
            "registered_servers": len(self.servers),
            "active_connections": len(self.active_connections),
            "total_requests": len(self.request_history),
            "cached_responses": len(self.response_cache),
            "servers": {
                name: {
                    "enabled": server.enabled,
                    "capabilities": len(server.capabilities),
                    "connected": name in self.active_connections,
                }
                for name, server in self.servers.items()
            },
        }


# Singleton instance
_mcp_instance: Optional[MCPIntegration] = None


def get_mcp_integration() -> MCPIntegration:
    """Get or create MCP integration singleton."""
    global _mcp_instance
    if _mcp_instance is None:
        _mcp_instance = MCPIntegration()
    return _mcp_instance


# Convenience functions
async def mcp_execute(server_name: str, capability: str, payload: Dict[str, Any]) -> MCPResponse:
    """
    Execute an MCP request (convenience function).

    Args:
        server_name: Name of MCP server
        capability: Capability to invoke
        payload: Request payload

    Returns:
        MCP response
    """
    mcp = get_mcp_integration()
    request = MCPRequest(server_name=server_name, capability=capability, payload=payload)
    return await mcp.execute(request)
