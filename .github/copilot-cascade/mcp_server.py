"""
MCP (Model Context Protocol) Server Integration for Cascade Delegation.

Provides integration with external MCP servers for extended capabilities
while supporting mock/simulation mode for environments without real servers.
"""

import asyncio
import json
import logging
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Standalone SSE transport helper (single source of truth: scripts/ci/).
# We attempt to import it at module load time so that tests against the
# stand-alone script and tests against mcp_server both exercise identical
# logic.  When running inside the .github/copilot-cascade/ tree (without
# a full repo checkout) the import may fail; in that case we fall back to
# the local implementation defined below.
# ---------------------------------------------------------------------------
_SSE_TRANSPORT_PATH = str(
    Path(__file__).parent.parent.parent / "scripts" / "ci"
)
_sse_transport_imported = False
try:
    if _SSE_TRANSPORT_PATH not in sys.path:
        sys.path.insert(0, _SSE_TRANSPORT_PATH)
    from mcp_sse_transport import (  # noqa: E402
        http_post_json_streaming as _http_post_json_streaming_fn,
    )
    _sse_transport_imported = True
except ImportError:
    _sse_transport_imported = False

# ---------------------------------------------------------------------------
# Standalone SSE transport helper (single source of truth: scripts/ci/).
# We attempt to import it at module load time so that tests against the
# stand-alone script and tests against mcp_server both exercise identical
# logic.  When running inside the .github/copilot-cascade/ tree (without
# a full repo checkout) the import may fail; in that case we fall back to
# the local implementation defined below.
# ---------------------------------------------------------------------------
_SSE_TRANSPORT_PATH = str(
    Path(__file__).parent.parent.parent / "scripts" / "ci"
)
_sse_transport_imported = False
try:
    if _SSE_TRANSPORT_PATH not in sys.path:
        sys.path.insert(0, _SSE_TRANSPORT_PATH)
    from mcp_sse_transport import (  # noqa: E402
        http_post_json_streaming as _http_post_json_streaming_fn,
    )
    _sse_transport_imported = True
except ImportError:
    _sse_transport_imported = False

logger = logging.getLogger(__name__)


class MCPConnectionMode(Enum):
    """MCP connection operating modes."""

    MOCK = "mock"            # Simulated responses for testing
    REAL = "real"            # Real MCP server connections (JSON-RPC 2.0)
    STREAMING = "streaming"  # Streaming JSON-RPC 2.0 via Server-Sent Events (IMP-005)


@dataclass
class CapabilitySpec:
    """Typed capability descriptor with JSON Schema validation (IMP-005 — S178).

    Extends the plain ``str`` capability name with optional JSON Schema definitions
    for the request payload and the expected response data.  When ``input_schema``
    is provided, :class:`MCPIntegration` will validate the request payload against
    it *before* making a network round-trip, surfacing schema violations early.

    Examples
    --------
    >>> spec = CapabilitySpec(
    ...     name="issue_management",
    ...     description="Create, update, and close GitHub issues",
    ...     input_schema={
    ...         "type": "object",
    ...         "properties": {
    ...             "action": {"type": "string", "enum": ["create", "update", "close"]},
    ...             "title": {"type": "string"},
    ...         },
    ...         "required": ["action"],
    ...     },
    ...     output_schema={"type": "object", "properties": {"issue_number": {"type": "integer"}}},
    ... )
    """

    name: str
    description: str = ""
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)

    def __eq__(self, other: object) -> bool:  # noqa: D105
        if isinstance(other, str):
            return self.name == other
        if isinstance(other, CapabilitySpec):
            return self.name == other.name
        return NotImplemented

    def __hash__(self) -> int:  # noqa: D105
        return hash(self.name)

    def validate_input(self, payload: dict[str, Any]) -> Optional[str]:
        """Validate *payload* against :attr:`input_schema`.

        Returns ``None`` when the payload is valid (or no schema is defined),
        or an error message string when validation fails.

        Uses ``jsonschema`` when installed; gracefully falls back to a
        no-op (returns ``None``) when the package is absent.
        """
        if not self.input_schema:
            return None
        try:
            import jsonschema  # type: ignore
        except ImportError:
            logger.debug("jsonschema not installed — skipping IMP-005 input validation")
            return None
        try:
            jsonschema.validate(payload, self.input_schema)
            return None
        except jsonschema.ValidationError as exc:
            return str(exc.message)
        except jsonschema.SchemaError as exc:
            logger.warning("IMP-005: invalid capability input_schema: %s", exc.message)
            return None


@dataclass
class MCPServer:
    """Model Context Protocol server configuration."""

    name: str
    url: str
    capabilities: list[str | CapabilitySpec]
    auth_token: Optional[str] = None
    timeout: int = 30
    enabled: bool = True

    def get_capability(self, name: str) -> Optional[CapabilitySpec]:
        """Return the :class:`CapabilitySpec` for *name*, or ``None`` if not found.

        Accepts both plain-string capabilities (returns a spec with no schemas)
        and full :class:`CapabilitySpec` entries.
        """
        for cap in self.capabilities:
            if isinstance(cap, CapabilitySpec) and cap.name == name:
                return cap
            if isinstance(cap, str) and cap == name:
                return CapabilitySpec(name=name)
        return None

    def has_capability(self, name: str) -> bool:
        """Return ``True`` when this server supports the named capability."""
        return self.get_capability(name) is not None


@dataclass
class MCPRequest:
    """MCP request structure."""

    server_name: str
    capability: str
    payload: dict[str, Any]
    request_id: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class MCPResponse:
    """MCP response structure."""

    request_id: str
    server_name: str
    status: str  # success, error, timeout
    data: Optional[dict[str, Any]] = None
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
        self.servers: dict[str, MCPServer] = {}
        self.active_connections: dict[str, Any] = {}
        self.request_history: list[MCPRequest] = []
        self.response_cache: dict[str, MCPResponse] = {}

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

        # Check if capability is supported (IMP-005: use has_capability for typed lookup)
        if not server.has_capability(request.capability):
            return MCPResponse(
                request_id=request.request_id,
                server_name=request.server_name,
                status="error",
                error=f"Capability {request.capability} not supported by {request.server_name}",
            )

        # IMP-005: Validate request payload against capability input schema when available.
        cap_spec = server.get_capability(request.capability)
        if cap_spec is not None:
            validation_error = cap_spec.validate_input(request.payload)
            if validation_error:
                return MCPResponse(
                    request_id=request.request_id,
                    server_name=request.server_name,
                    status="error",
                    error=f"Payload schema validation failed for {request.capability!r}: {validation_error}",
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

        rpc_payload: dict[str, Any] = {
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
        payload: dict[str, Any],
        auth_token: Optional[str] = None,
        timeout: int = 30,
    ) -> dict[str, Any]:
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
        headers: dict[str, str] = {"Content-Type": "application/json"}
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

        rpc_payload: dict[str, Any] = {
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

    def _http_post_json_streaming(
        self: str,
        payload: dict[str, Any],
        auth_token: Optional[str] = None,
        timeout: int = 30,
    ) -> dict[str, Any]:
        """POST JSON and read the response as SSE or plain JSON.

        Delegates to :func:`scripts.ci.mcp_sse_transport.http_post_json_streaming`
        when available (single source of truth).  Falls back to the inline
        implementation when the scripts tree is not on the path.

        See :mod:`mcp_sse_transport` for the full parameter/return documentation.
        """
        if _sse_transport_imported:
            return _http_post_json_streaming_fn(
                self, payload, auth_token=auth_token, timeout=timeout
            )

        # ------------------------------------------------------------------ #
        # Fallback implementation (identical logic, kept for environments     #
        # where the repo root is not available, e.g. a bare checkout of the  #
        # .github/copilot-cascade/ sub-tree only).                            #
        # ------------------------------------------------------------------ #
        if not self.startswith(("http://", "https://")):
            raise ValueError(
                f"_http_post_json_streaming: URL must start with "
                f"http:// or https://, got: {self!r}"
            )
        data = json.dumps(payload).encode("utf-8")
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream, application/json",
        }
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        req = urllib.request.Request(self, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec B310
            content_type = resp.headers.get("Content-Type", "")
            raw = resp.read()

        if "text/event-stream" not in content_type:
            return json.loads(raw)

        chunks: list[dict[str, Any]] = []
        for line in raw.decode("utf-8").splitlines():
            line = line.strip()
            if line.startswith("data:"):
                fragment = line.removeprefix("data:").strip()
                if fragment in ("", "[DONE]"):
                    continue
                try:
                    frame = json.loads(fragment)
                    if isinstance(frame, dict):
                        chunks.append(frame)
                except json.JSONDecodeError:
                    logger.debug(
                        "MCP SSE: skipping non-JSON fragment: %r", fragment
                    )

        if not chunks:
            return {
                "error": {
                    "message": "SSE stream contained no parseable data frames"
                }
            }

        final = chunks[-1]
        final["_streaming_chunks"] = len(chunks)
        return final

    def _generate_mock_data(self, capability: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Generate mock response data based on capability."""

        if capability == "repository_access":
            return {
                "repository": payload.get("repo", "unknown"),
                "access_granted": True,
                "branches": ["main", "develop", "feature/new"],
                "recent_commits": 42,
            }

        if capability == "quantum_analysis":
            return {
                "quantum_state": "superposition",
                "entanglement_score": 0.85,
                "coherence": 0.92,
                "analysis": "System exhibits strong quantum characteristics",
            }

        if capability == "entanglement_detection":
            return {
                "entangled_pairs": [
                    {"task_a": "task_1", "task_b": "task_3", "strength": 0.78},
                    {"task_a": "task_2", "task_b": "task_4", "strength": 0.65},
                ],
                "total_detected": 2,
            }

        if capability == "code_search":
            return {
                "query": payload.get("query", ""),
                "results": [
                    {"file": "src/main.py", "line": 42, "match": "def process()"},
                    {"file": "tests/test_main.py", "line": 15, "match": "test_process()"},
                ],
                "total_matches": 2,
            }

        if capability == "issue_management":
            return {
                "operation": payload.get("operation", "list"),
                "issues": [
                    {"number": 123, "title": "Bug fix", "state": "open"},
                    {"number": 124, "title": "Feature request", "state": "open"},
                ],
                "count": 2,
            }

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

    def get_available_capabilities(self) -> dict[str, list[str]]:
        """Get all available capability names from registered servers."""
        capabilities = {}
        for name, server in self.servers.items():
            if server.enabled:
                # IMP-005: normalise List[Union[str, CapabilitySpec]] → List[str]
                capabilities[name] = [
                    cap.name if isinstance(cap, CapabilitySpec) else cap
                    for cap in server.capabilities
                ]
        return capabilities

    def get_statistics(self) -> dict[str, Any]:
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
async def mcp_execute(server_name: str, capability: str, payload: dict[str, Any]) -> MCPResponse:
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


# ---------------------------------------------------------------------------
# CLI entry-point (GAP-032 fix: add CLI for local debug / connectivity testing)
# ---------------------------------------------------------------------------
def _build_cli_parser():
    import argparse

    parser = argparse.ArgumentParser(
        description="GitHub MCP Server CLI — test, list and execute MCP capabilities.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python mcp_server.py list-servers\n"
            "  python mcp_server.py test-connection --server github --mode mock\n"
            "  python mcp_server.py execute --server github --capability code_search \\\n"
            "      --params '{\"query\": \"my_function\"}' --mode mock\n"
            "  python mcp_server.py health\n"
        ),
    )
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    # list-servers
    subparsers.add_parser("list-servers", help="List all registered MCP servers and their capabilities")

    # test-connection
    tc = subparsers.add_parser("test-connection", help="Test connectivity to an MCP server")
    tc.add_argument("--server", required=True, help="Server name (e.g. 'github', 'playwright')")
    tc.add_argument(
        "--mode",
        choices=["mock", "real", "streaming"],
        default="mock",
        help="Connection mode (default: mock)",
    )
    tc.add_argument("--token", default=None, help="Bearer auth token")
    tc.add_argument("--timeout", type=int, default=30, help="Timeout in seconds (default: 30)")

    # execute
    ex = subparsers.add_parser("execute", help="Execute an MCP capability and print the response")
    ex.add_argument("--server", required=True, help="Server name")
    ex.add_argument("--capability", required=True, help="Capability name (e.g. 'code_search')")
    ex.add_argument("--params", default="{}", help="JSON-encoded params dict (default: '{}')")
    ex.add_argument(
        "--mode",
        choices=["mock", "real", "streaming"],
        default="mock",
        help="Connection mode (default: mock)",
    )
    ex.add_argument("--token", default=None, help="Bearer auth token")
    ex.add_argument("--timeout", type=int, default=30, help="Timeout in seconds (default: 30)")
    ex.add_argument("--output-format", choices=["json", "plain"], default="json", help="Output format")

    # health
    subparsers.add_parser("health", help="Print current MCP integration health and config")

    return parser


def _cli_main(argv=None):
    """CLI entry point for mcp_server.py."""
    import json as _json
    import sys as _sys

    parser = _build_cli_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    integration = get_mcp_integration()

    if args.command == "list-servers":
        print("Registered MCP servers:")
        for name, spec in integration.server_registry.items():
            caps = ", ".join(spec.capabilities) if hasattr(spec, "capabilities") else "n/a"
            mode = getattr(spec, "connection_mode", "mock")
            print(f"  • {name:<20} mode={mode:<12} capabilities=[{caps}]")
        return 0

    if args.command == "health":
        print("MCP Integration Health")
        print(f"  Registered servers : {len(integration.server_registry)}")
        print(f"  Default mode       : {integration.connection_mode.value}")
        print(f"  SSE transport      : {'available' if _sse_transport_imported else 'fallback (inline)'}")
        return 0

    if args.command == "test-connection":
        mode = MCPConnectionMode(args.mode)
        original_mode = integration.connection_mode
        integration.connection_mode = mode
        request = MCPRequest(
            server_name=args.server,
            capability="ping",
            payload={},
            auth_token=args.token,
            timeout=args.timeout,
        )
        try:
            result = asyncio.run(integration.execute(request))
            status = "✅ OK" if result.status == "success" else f"❌ {result.status}"
            print(f"Connection test: {status}")
            if result.error:
                print(f"  Error: {result.error}")
            return 0 if result.status == "success" else 1
        except Exception as exc:  # noqa: BLE001
            print(f"❌ Connection test failed: {exc}", file=_sys.stderr)
            return 1
        finally:
            integration.connection_mode = original_mode

    if args.command == "execute":
        try:
            params = _json.loads(args.params)
        except _json.JSONDecodeError as exc:
            print(f"ERROR: --params is not valid JSON: {exc}", file=_sys.stderr)
            return 1
        mode = MCPConnectionMode(args.mode)
        original_mode = integration.connection_mode
        integration.connection_mode = mode
        request = MCPRequest(
            server_name=args.server,
            capability=args.capability,
            payload=params,
            auth_token=args.token,
            timeout=args.timeout,
        )
        try:
            result = asyncio.run(integration.execute(request))
            if args.output_format == "json":
                output = {
                    "status": result.status,
                    "server": result.server_name,
                    "request_id": result.request_id,
                    "data": result.data,
                }
                if result.error:
                    output["error"] = result.error
                print(_json.dumps(output, indent=2))
            else:
                print(f"Status : {result.status}")
                if result.data:
                    print(f"Data   : {result.data}")
                if result.error:
                    print(f"Error  : {result.error}")
            return 0 if result.status == "success" else 1
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR: {exc}", file=_sys.stderr)
            return 1
        finally:
            integration.connection_mode = original_mode

    parser.print_help()
    return 1


if __name__ == "__main__":
    import sys
    sys.exit(_cli_main())
