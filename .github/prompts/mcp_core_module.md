# [Script Collection]: mcp_core_modules_setup.py
> Generated: 2024-11-18 03:40:04 | Author: mbaetiong
> Assistant: GitHub Copilot Chat Assistant

Included files
| File path | Description |
|---|---|
| mcp/config.py | Unified MCP configuration loader (mcp.json + env) |
| mcp/registry.py | MCPToolRegistry: tool discovery, introspection, invocation |
| mcp/auth.py | API-key based authenticator/authorizer and Principal model |
| mcp/rate_limit.py | In-memory per-principal rate limiter |
| mcp/errors.py | MCPError hierarchy mapping JSON-RPC codes to HTTP statuses |
| mcp/versioning.py | MCP version negotiation helper |
| mcp/metrics.py | Lightweight in-memory metrics hooks |
| services/ita/app/security.py | FastAPI integration: require_auth, authz, rate-limiting deps |
| services/ita/app/main.py | FastAPI startup/shutdown hooks, /tools endpoints |
| temp/bridge_codex_copilot_bridge/mcp/server/server.py | JSON-RPC MCPServer (listTools, callTool, negotiateVersion) |
| tests/... | Unit tests for registry, auth, rate limit, errors, versioning |
| MCP_IMPLEMENTATION_SUMMARY.md | Documentation summary (implementation & status) |

Below are the scripts as requested, each embedded in its own code block.

---

mcp/config.py
```python
# mcp/config.py
"""
Unified configuration for MCP server components (registry, auth, rate limiting, etc).
Loads settings from `mcp.json` and environment variables (ITA_URL, ITA_API_KEY, etc).
"""
import os
import json
from typing import Any, Dict, List, Optional

# Default paths and environment keys
_MCP_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "mcp.json")
_ENV_ITA_URL = "ITA_URL"
_ENV_ITA_API_KEY = "ITA_API_KEY"
_ENV_MCP_RATE_LIMIT = "MCP_RATE_LIMIT"  # optional global rate limit (calls per minute)

class MCPToolConfig(Dict[str, Any]):
    """Typed alias for tool config entries (name, description, endpoint, etc)."""
    pass

class MCPSettings:
    """Holds MCP configuration loaded from file and environment."""
    def __init__(self, tools: List[MCPToolConfig], base_url: str, api_key: Optional[str], default_rate_limit: int):
        self.tools = tools
        self.base_url = base_url
        self.api_key = api_key
        self.default_rate_limit = default_rate_limit

def load_mcp_config() -> MCPSettings:
    """Load MCP configuration from mcp.json and environment. Env vars override file defaults."""
    # Load tool definitions from JSON file (if present)
    tools: List[MCPToolConfig] = []
    if os.path.isfile(_MCP_CONFIG_PATH):
        try:
            with open(_MCP_CONFIG_PATH, "r") as f:
                data = json.load(f)
                tools = data.get("tools", [])
        except Exception:
            # If config file is malformed or unreadable, proceed with empty tools list
            tools = []

    # Read environment overrides
    base_url = os.environ.get(_ENV_ITA_URL, "http://localhost:8000")  # default ITA base URL
    api_key = os.environ.get(_ENV_ITA_API_KEY)  # may be None if not set
    rate_limit_env = os.environ.get(_ENV_MCP_RATE_LIMIT)
    default_rate_limit = int(rate_limit_env) if rate_limit_env else 60  # default 60 calls/min

    return MCPSettings(tools=tools, base_url=base_url, api_key=api_key, default_rate_limit=default_rate_limit)
```

---

mcp/registry.py
```python
# mcp/registry.py
from typing import Any, Callable, Dict, List, Optional
import importlib
import requests

from . import config
from .errors import ToolNotFoundError, ToolExecutionError

class MCPToolRegistry:
    """Registry of available tools for MCP. Handles tool lookup, listing, and invocation."""

    def __init__(self, settings: config.MCPSettings):
        self.settings = settings
        # Map tool name to either a callable function or an endpoint dict
        self._tools: Dict[str, Dict[str, Any]] = {}
        # Register all tools from settings
        for tool in settings.tools:
            name = tool.get("name")
            if not name:
                continue
            entry: Dict[str, Any] = {"description": tool.get("description", "")}
            # If a callable path is specified in config (e.g. "callable": "module.func"), import it
            if tool.get("callable"):
                try:
                    mod_name, func_name = tool["callable"].rsplit(".", 1)
                    func = getattr(importlib.import_module(mod_name), func_name)
                    entry["callable"] = func
                except Exception as e:
                    # Skip tools with invalid callables
                    entry["callable_error"] = str(e)
            elif tool.get("endpoint"):
                # Store endpoint info (will call via HTTP)
                entry["endpoint"] = tool["endpoint"]
                entry["method"] = tool.get("method", "POST")
            self._tools[name] = entry

    def list_tools(self) -> List[Dict[str, Any]]:
        """Return a list of tools with their name and description (for introspection)."""
        tools_list: List[Dict[str, str]] = []
        for name, entry in self._tools.items():
            tools_list.append({
                "name": name,
                "description": entry.get("description", "")
            })
        return tools_list

    def call_tool(self, name: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Invoke the specified tool by name with given params. Returns tool result or raises MCPError."""
        if name not in self._tools:
            raise ToolNotFoundError(f"Tool '{name}' is not registered")
        tool_entry = self._tools[name]
        params = params or {}

        # If the tool is a local callable function
        if "callable" in tool_entry:
            try:
                func: Callable = tool_entry["callable"]
                return func(**params)  # call with keyword arguments
            except Exception as e:
                # Wrap any tool exception into a ToolExecutionError for consistent error handling
                raise ToolExecutionError(f"Error in tool '{name}': {e}")

        # If the tool is defined by an HTTP endpoint
        if "endpoint" in tool_entry:
            url = tool_entry["endpoint"]
            # If endpoint is relative, prepend base_url from config
            if url.startswith("/"):
                url = self.settings.base_url.rstrip("/") + url
            method = tool_entry.get("method", "POST").upper()
            try:
                headers = {}
                if self.settings.api_key:
                    headers["Authorization"] = f"Bearer {self.settings.api_key}"
                timeout = 5  # seconds (avoid no-timeout calls)
                if method == "GET":
                    resp = requests.get(url, params=params, headers=headers, timeout=timeout)
                else:
                    resp = requests.post(url, json=params, headers=headers, timeout=timeout)
                resp.raise_for_status()
            except requests.HTTPError as http_err:
                # HTTP error from tool service
                raise ToolExecutionError(f"Tool '{name}' HTTP {http_err.response.status_code}: {http_err.response.text}")
            except Exception as e:
                # Network or other error
                raise ToolExecutionError(f"Failed to call tool '{name}': {e}")

            # If successful, parse JSON response if possible
            try:
                return resp.json()
            except ValueError:
                # Return raw text if not JSON
                return resp.text

        # If tool entry is invalid (neither callable nor endpoint)
        raise ToolExecutionError(f"Tool '{name}' configuration is invalid")
```

---

mcp/auth.py
```python
# mcp/auth.py
from typing import Optional
import os

from .errors import AuthenticationError, AuthorizationError

class Principal:
    """Represents an authenticated principal (user or service) invoking MCP tools."""
    def __init__(self, principal_id: str, role: Optional[str] = None):
        self.id = principal_id
        self.role = role

class MCPAuthenticator:
    """Simple API-key based authenticator for MCP requests."""
    def __init__(self, valid_api_keys: Optional[list[str]] = None):
        # Load allowed API keys from env if not provided
        self._valid_keys = valid_api_keys or []
        env_key = os.environ.get("ITA_API_KEY")
        if env_key:
            self._valid_keys.append(env_key)
        # Allow list may be extended via config or multi-key setup in future
        self._valid_keys = list(set(self._valid_keys))  # deduplicate

    def authenticate(self, api_key: str) -> Principal:
        """Authenticate a request by API key. Returns Principal if valid, else raises AuthenticationError."""
        if not api_key or api_key not in self._valid_keys:
            raise AuthenticationError("Invalid or missing API key")
        # For now, principal_id can be the API key itself or a hash thereof (using key prefix for anonymity)
        pid_display = api_key[:6] + "..." if len(api_key) > 6 else api_key
        return Principal(principal_id=pid_display, role=None)

class MCPAuthorizer:
    """Authorization stub. In a real system, checks principal's permissions for specific tool."""
    def __init__(self, permissions: Optional[dict[str, list[str]]] = None):
        # `permissions` can map principal roles or IDs to allowed tool names
        self.permissions = permissions or {}

    def authorize(self, principal: Principal, tool_name: str) -> None:
        """Authorize a principal for the given tool. Raises AuthorizationError if not permitted."""
        # If no specific permissions configured, allow all authenticated principals by default
        if not self.permissions:
            return
        # Otherwise, check if principal's id or role is allowed for the tool
        allowed = False
        if principal.role and tool_name in self.permissions.get(principal.role, []):
            allowed = True
        if tool_name in self.permissions.get(principal.id, []):
            allowed = True
        if not allowed:
            raise AuthorizationError(f"Principal '{principal.id}' not authorized for tool '{tool_name}'")
```

---

mcp/rate_limit.py
```python
# mcp/rate_limit.py
import time
from collections import deque, defaultdict
from typing import DefaultDict, Deque

from .errors import RateLimitError

class MCPRateLimiter:
    """In-memory token-bucket rate limiter for MCP calls (per principal)."""

    def __init__(self, max_calls_per_minute: int = 60):
        self.max_calls = max_calls_per_minute
        self.window_seconds = 60
        # Dictionary of principal_id -> deque of call timestamps (within current window)
        self._calls: DefaultDict[str, Deque[float]] = defaultdict(lambda: deque(maxlen=self.max_calls))

    def allow_request(self, principal_id: str) -> None:
        """ Record a call for the given principal. If exceeding max_calls per minute, raise RateLimitError. """
        now = time.time()
        call_times = self._calls[principal_id]
        # Purge timestamps older than 60 seconds from the left of the deque
        while call_times and now - call_times[0] > self.window_seconds:
            call_times.popleft()
        if len(call_times) >= self.max_calls:
            # Already reached max calls in the last window
            raise RateLimitError(f"Rate limit exceeded for principal '{principal_id}'")
        # Otherwise, record this call
        call_times.append(now)
```

---

mcp/errors.py
```python
# mcp/errors.py
class MCPError(Exception):
    """Base class for MCP errors with structured information."""
    code: int = -32000  # JSON-RPC error code (default: generic server error)
    http_status: int = 500  # HTTP status code (default: Internal Server Error)

    def __init__(self, message: str = "", code: int = None, http_status: int = None):
        super().__init__(message)
        if code is not None:
            self.code = code
        if http_status is not None:
            self.http_status = http_status

# Specific MCP error types
class AuthenticationError(MCPError):
    code = -32600  # Invalid Request (use -32600 for auth issues)
    http_status = 401

class AuthorizationError(MCPError):
    code = -32600
    http_status = 403

class RateLimitError(MCPError):
    code = -32002  # Custom server error code for rate limiting
    http_status = 429

class ToolNotFoundError(MCPError):
    code = -32601  # JSON-RPC: Method not found
    http_status = 404

class ToolExecutionError(MCPError):
    code = -32603  # JSON-RPC: Internal error
    http_status = 500

class VersionMismatchError(MCPError):
    code = -32003
    http_status = 400
```

---

mcp/versioning.py
```python
# mcp/versioning.py
from .errors import VersionMismatchError

# Define supported protocol versions. Example format "1.0"
MCP_VERSIONS = ["1.0"]

def negotiate_version(client_versions: list[str]) -> str:
    """
    Given a list of version identifiers from a client, negotiate the highest compatible version.
    Returns the agreed version, or raises VersionMismatchError if no common version exists.
    """
    supported = set(MCP_VERSIONS)
    client_set = set(client_versions or [])
    common = sorted(supported.intersection(client_set), reverse=True)
    if not common:
        # No overlap in versions
        raise VersionMismatchError("No compatible MCP version found")
    agreed = common[0]
    return agreed
```

---

mcp/metrics.py
```python
# mcp/metrics.py
"""
Lightweight in-memory metrics for MCP (counters for tool usage, errors, etc.).
"""
from collections import Counter

# Simple counters storage
_counters = Counter()

def record_tool_call(tool_name: str, success: bool) -> None:
    """
    Record a tool call event for metrics. Increments total call counter and error counter if failed.
    """
    _counters["mcp_tool_calls_total"] += 1
    _counters[f"mcp_tool_calls_{tool_name}"] += 1
    if not success:
        _counters["mcp_tool_errors_total"] += 1

def get_metrics_snapshot() -> dict:
    """Return a snapshot of current metrics counters (for observability/monitoring)."""
    return dict(_counters)
```

---

services/ita/app/security.py
```python
# services/ita/app/security.py
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.api_key import APIKeyHeader
from fastapi import Depends

from mcp.auth import MCPAuthenticator, MCPAuthorizer, Principal
from mcp.rate_limit import MCPRateLimiter
from mcp.errors import AuthenticationError, AuthorizationError, RateLimitError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
api_key_scheme = APIKeyHeader(name="Authorization", auto_error=False)

# Module-level singletons (maintain state across requests)
authenticator = MCPAuthenticator()  # loads valid API key(s) from env
authorizer = MCPAuthorizer()  # no specific permissions configured (allow all)
rate_limiter = MCPRateLimiter()  # default rate limit (calls per minute) from config is set in startup

def require_auth(api_key: str = Depends(api_key_scheme)) -> Principal:
    """
    FastAPI dependency to require a valid API key. Returns Principal if authenticated.
    """
    if not api_key:
        # APIKeyHeader will yield the raw "Authorization" header; expect format "Bearer <KEY>"
        raise AuthenticationError("Missing API key")
    # If header is like "Bearer <KEY>", extract the token part
    token = api_key.split()[-1] if " " in api_key else api_key
    principal = authenticator.authenticate(token)
    return principal

def check_authorization(principal: Principal = Depends(require_auth), tool: str = ""):
    """
    Dependency to enforce authorization for a given tool name. Use as Depends with tool name context.
    """
    try:
        if tool:
            authorizer.authorize(principal, tool)
    except AuthorizationError:
        # FastAPI will catch this as an HTTPException via exception handler (set up in main app)
        raise

def enforce_rate_limit(principal: Principal = Depends(require_auth)):
    """
    Dependency to enforce rate limiting for the current principal.
    """
    try:
        rate_limiter.allow_request(principal.id)
    except RateLimitError:
        raise
```

---

services/ita/app/main.py
```python
# services/ita/app/main.py
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends

from . import models, knowledge_base, git_ops, hygiene

from mcp import config as mcp_config
from mcp.registry import MCPToolRegistry
from mcp.errors import MCPError
from .security import require_auth, enforce_rate_limit, check_authorization

app = FastAPI(title="Codex ITA Service", version="1.0.0")

# Initialize MCP tool registry and config on startup
mcp_registry: Optional[MCPToolRegistry] = None

@app.on_event("startup")
async def startup_event():
    # Load MCP config (tools list, etc) and initialize registry
    settings = mcp_config.load_mcp_config()
    # If the config specifies a custom rate limit, update the global rate_limiter:
    from .security import rate_limiter
    rate_limiter.max_calls = settings.default_rate_limit

    global mcp_registry
    mcp_registry = MCPToolRegistry(settings=settings)

    # Log startup event (structured log for observability)
    try:
        from codex_ml import codex_structured_logging as cslog
        logger = cslog.init_json_logging()
        cslog.log_event(logger, "mcp.startup", tools_loaded=len(settings.tools))
    except ImportError:
        pass

@app.on_event("shutdown")
async def shutdown_event():
    # Optionally, perform cleanup if needed (none for now)
    try:
        from codex_ml import codex_structured_logging as cslog
        logger = cslog.init_json_logging()
        cslog.log_event(logger, "mcp.shutdown", msg="MCP server shutdown complete")
    except ImportError:
        pass

# Unified tools listing endpoint (MCP protocol surface)
@app.get("/tools", dependencies=[Depends(require_auth), Depends(enforce_rate_limit)])
def list_tools_http():
    """
    List all available tools (name and description). Requires auth.
    """
    if mcp_registry is None:
        return []
    return mcp_registry.list_tools()

# Generic tool invocation endpoint (if needed for HTTP calls - optional)
@app.post("/tools/{tool_name}", dependencies=[Depends(require_auth), Depends(enforce_rate_limit)])
def call_tool_http(tool_name: str, params: dict = None):
    """
    Call a tool by name with given parameters. Returns the tool's output or raises error.
    """
    if mcp_registry is None:
        raise HTTPException(status_code=500, detail="MCP registry not initialized")
    try:
        result = mcp_registry.call_tool(tool_name, params or {})
        return {"result": result}
    except MCPError as e:
        # Translate MCPError to HTTP exception with appropriate status
        raise HTTPException(status_code=e.http_status, detail=str(e))
```

---

temp/bridge_codex_copilot_bridge/mcp/server/server.py
```python
# temp/bridge_codex_copilot_bridge/mcp/server/server.py
import json
from typing import Any, Dict

from mcp import config as mcp_config
from mcp.registry import MCPToolRegistry
from mcp.auth import MCPAuthenticator, MCPAuthorizer
from mcp.rate_limit import MCPRateLimiter
from mcp.errors import (
    MCPError,
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
    ToolNotFoundError,
    ToolExecutionError,
    VersionMismatchError,
)
from mcp.versioning import MCP_VERSIONS, negotiate_version
from mcp import metrics

class MCPServer:
    """
    Lightweight JSON-RPC MCP server that handles listTools, callTool, and version negotiation.
    """
    def __init__(self):
        settings = mcp_config.load_mcp_config()
        self.registry = MCPToolRegistry(settings=settings)
        self.authenticator = MCPAuthenticator()
        self.authorizer = MCPAuthorizer()
        self.rate_limiter = MCPRateLimiter(max_calls_per_minute=settings.default_rate_limit)
        self.protocol_versions = MCP_VERSIONS

    def handle_request(self, request_json: str) -> str:
        """
        Process a JSON-RPC request (as JSON string) and return the JSON-RPC response string.
        Supports methods: listTools, callTool, negotiateVersion.
        """
        try:
            request = json.loads(request_json)
        except Exception:
            # Malformed JSON
            error = {"code": -32600, "message": "Invalid Request"}
            return json.dumps({"jsonrpc": "2.0", "error": error, "id": None})

        rpc_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        try:
            # Basic authentication: if an API key is required, expect it in params or headers
            api_key = None
            if isinstance(params, dict) and "api_key" in params:
                api_key = params.pop("api_key")
            if api_key:
                principal = self.authenticator.authenticate(api_key)
            else:
                principal = None

            # Rate limiting: if principal is present, enforce limit
            if principal:
                self.rate_limiter.allow_request(principal.id)

            # Dispatch methods
            if method == "listTools":
                result = self.registry.list_tools()
                response = {"jsonrpc": "2.0", "result": result, "id": rpc_id}

            elif method == "callTool":
                tool_name = params.get("tool") or params.get("tool_name")
                tool_args = params.get("args") or params.get("params") or {}
                if principal:
                    # Authorization: ensure principal allowed to use this tool
                    self.authorizer.authorize(principal, tool_name)
                result = self.registry.call_tool(tool_name, tool_args)
                # Record metrics
                metrics.record_tool_call(tool_name, success=True)
                response = {"jsonrpc": "2.0", "result": result, "id": rpc_id}

            elif method == "negotiateVersion":
                client_versions = params.get("versions") or params.get("client_versions") or []
                agreed = negotiate_version(client_versions)
                response = {"jsonrpc": "2.0", "result": {"version": agreed}, "id": rpc_id}

            else:
                # Unknown method
                raise ToolNotFoundError(f"Method '{method}' not found")

        except MCPError as e:
            # Known MCP error (auth, authZ, rate, tool not found, execution, version mismatch)
            err_obj = {"code": e.code, "message": str(e)}
            # If it’s a tool execution error, also record a failed-call metric
            if isinstance(e, ToolExecutionError):
                tool = params.get("tool") or params.get("tool_name") or method
                metrics.record_tool_call(tool, success=False)
            response = {"jsonrpc": "2.0", "error": err_obj, "id": rpc_id}

        except Exception as e:
            # Unexpected error – return as internal error
            err_obj = {"code": -32603, "message": "Internal error: " + str(e)}
            response = {"jsonrpc": "2.0", "error": err_obj, "id": rpc_id}

        # Serialize and return response
        return json.dumps(response)
```

---

tests/space_traversal/test_mcp_detectors.py
```python
# tests/space_traversal/test_mcp_detectors.py
import importlib

# List of MCP detector modules to test
DETECTOR_MODULES = [
    "mcp_protocol_surface",
    "mcp_schema_validation",
    "mcp_tooling_registry",
    "mcp_authz_authn",
    "mcp_rate_limiting",
    "mcp_error_handling",
    "mcp_observability",
    "mcp_configuration",
    "mcp_security_safeguards",
    "mcp_lifecycle_management",
    "mcp_versioning_compat",
    "mcp_multi_tenant",
]

def test_all_mcp_detectors_basic():
    """Ensure each MCP detector can run on an empty file index and returns structure with correct ID."""
    empty_index = {"files": []}
    for module_name in DETECTOR_MODULES:
        mod = importlib.import_module(f"scripts.space_traversal.detectors.{module_name}")
        result = mod.detect(empty_index)
        # Each detector should return a dict with an 'id' matching the capability name
        expected_id = module_name.replace("_", "-")  # e.g., mcp_protocol_surface -> mcp-protocol-surface
        assert result["id"] == expected_id
        assert "evidence_files" in result and "found_patterns" in result
        # The result for empty index should have no evidence found
        assert result["evidence_files"] == [] or len(result["evidence_files"]) == 0
```

---

tests/mcp/test_registry.py
```python
# tests/mcp/test_registry.py
import types
import builtins
import pytest

from mcp.registry import MCPToolRegistry
from mcp import config as mcp_config
from mcp.errors import ToolNotFoundError, ToolExecutionError

# Define a dummy tool function for testing callables
def dummy_tool(x: int, y: int) -> int:
    return x + y

def test_list_and_call_callable_tool(tmp_path, monkeypatch):
    # Prepare a fake mcp.json config file with one callable tool
    tool_config = {"tools": [
        {"name": "dummy", "description": "Dummy addition tool", "callable": "__main__.dummy_tool"}
    ]}
    config_file = tmp_path / "mcp.json"
    config_file.write_text(builtins.str(tool_config))
    # Monkeypatch config loader to use our temp config file
    monkeypatch.setattr(mcp_config, "_MCP_CONFIG_PATH", str(config_file))
    settings = mcp_config.load_mcp_config()
    registry = MCPToolRegistry(settings=settings)
    # list_tools should include the dummy tool
    tools = registry.list_tools()
    assert any(t["name"] == "dummy" for t in tools)
    assert tools[0]["description"] == "Dummy addition tool"
    # call_tool should execute the dummy function correctly
    result = registry.call_tool("dummy", {"x": 2, "y": 3})
    assert result == 5

def test_call_tool_endpoint(monkeypatch):
    # Simulate an endpoint tool by monkeypatching requests.post
    called = {"url": None, "data": None}

    def fake_post(url, json=None, headers=None, timeout=None):
        # Dummy response object with .json() method
        class DummyResponse:
            def __init__(self, data):
                self._data = data
            def raise_for_status(self):
                return None  # always OK
            def json(self):
                return self._data

        called["url"] = url; called["data"] = json
        return DummyResponse({"echo": json})

    import mcp.registry as registry_module
    monkeypatch.setattr(registry_module.requests, "post", fake_post)

    # Prepare config with an endpoint tool
    settings = mcp_config.MCPSettings(
        tools=[{"name": "echo", "description": "Echo tool", "endpoint": "/echo", "method": "POST"}],
        base_url="http://testserver",
        api_key=None,
        default_rate_limit=10
    )
    registry = MCPToolRegistry(settings=settings)
    result = registry.call_tool("echo", {"msg": "hello"})
    # The fake_post should have been called with full URL and data
    assert called["url"] == "http://testserver/echo"
    assert called["data"] == {"msg": "hello"}
    assert result == {"echo": {"msg": "hello"}}

def test_tool_not_found_and_execution_errors():
    settings = mcp_config.MCPSettings(tools=[], base_url="", api_key=None, default_rate_limit=5)
    registry = MCPToolRegistry(settings=settings)
    # call_tool on unknown tool should raise ToolNotFoundError
    with pytest.raises(ToolNotFoundError):
        registry.call_tool("nonexistent")
    # Register a callable that raises an exception to test ToolExecutionError
    def bad_tool():
        raise RuntimeError("failure")
    registry._tools["bad"] = {"description": "Bad tool", "callable": bad_tool}
    with pytest.raises(ToolExecutionError) as exc:
        registry.call_tool("bad")
    # Error message should be wrapped
    assert "Error in tool 'bad'" in str(exc.value)
```

---

tests/mcp/test_auth.py
```python
# tests/mcp/test_auth.py
import os
import builtins
import pytest

from mcp.auth import MCPAuthenticator, MCPAuthorizer, Principal
from mcp.errors import AuthenticationError, AuthorizationError

def test_authenticator_env_key(monkeypatch):
    # Set an env API key and ensure authenticator accepts it
    monkeypatch.setenv("ITA_API_KEY", "SECRET123")
    auth = MCPAuthenticator()
    # Correct key -> returns Principal
    principal = auth.authenticate("SECRET123")
    assert isinstance(principal, Principal)
    assert principal.id.startswith("SECRET")
    # Wrong key -> raises AuthenticationError
    with pytest.raises(AuthenticationError):
        auth.authenticate("WRONGKEY")
    # Clean up env
    monkeypatch.delenv("ITA_API_KEY", raising=False)

def test_authenticator_custom_keys():
    # Provide a custom list of valid keys
    keys = ["KEY1", "KEY2"]
    auth = MCPAuthenticator(valid_api_keys=keys)
    # Should accept both keys
    for k in keys:
        assert auth.authenticate(k).id.startswith(k[:len(k) if len(k)<7 else 6])
    # Non-listed key -> reject
    with pytest.raises(AuthenticationError):
        auth.authenticate("OTHER")

def test_authorizer_permissions():
    # Set up permissions: role 'admin' can use 'toolX'; user 'user123' can use 'toolY'
    perms = {"admin": ["toolX"], "user123": ["toolY"]}
    authorizer = MCPAuthorizer(permissions=perms)
    admin = Principal("alice", role="admin")
    user = Principal("user123", role=None)
    # admin role -> allowed toolX
    authorizer.authorize(admin, "toolX")  # should not raise
    # user id -> allowed toolY
    authorizer.authorize(user, "toolY")  # should not raise
    # Not allowed cases:
    with pytest.raises(AuthorizationError):
        authorizer.authorize(admin, "toolY")  # admin not allowed toolY
    with pytest.raises(AuthorizationError):
        authorizer.authorize(user, "toolX")  # user123 not allowed toolX
```

---

tests/mcp/test_rate_limit.py
```python
# tests/mcp/test_rate_limit.py
import time
import pytest

from mcp.rate_limit import MCPRateLimiter, RateLimitError

def test_rate_limiter_allows_within_limit():
    # Use a shorter window for testing (e.g., 5 seconds) by adjusting window_seconds
    rl = MCPRateLimiter(max_calls_per_minute=3)
    rl.window_seconds = 5
    principal_id = "test-user"
    # 3 calls back-to-back should be allowed (equal to limit)
    for i in range(3):
        rl.allow_request(principal_id)
    # 4th call immediately should raise RateLimitError
    with pytest.raises(RateLimitError):
        rl.allow_request(principal_id)
    # After waiting beyond the window, it should reset
    time.sleep(6)  # sleep slightly more than 5 seconds to clear the window
    # Should allow again after window reset
    rl.allow_request(principal_id)  # no exception

def test_rate_limiter_different_principals():
    rl = MCPRateLimiter(max_calls_per_minute=1)
    rl.window_seconds = 60
    # Two different principals each get their own allowance
    rl.allow_request("userA")
    rl.allow_request("userB")
    # Both should have used 1 call; hitting again for each triggers limit
    with pytest.raises(RateLimitError):
        rl.allow_request("userA")
    with pytest.raises(RateLimitError):
        rl.allow_request("userB")
```

---

tests/mcp/test_errors.py
```python
# tests/mcp/test_errors.py
from mcp import errors

def test_error_hierarchy_codes():
    # Each specific error should have the expected JSON-RPC code and HTTP status
    auth_err = errors.AuthenticationError("bad auth")
    assert auth_err.code == -32600 and auth_err.http_status == 401
    authz_err = errors.AuthorizationError("no access")
    assert authz_err.code == -32600 and authz_err.http_status == 403
    rate_err = errors.RateLimitError("too many")
    assert rate_err.code == -32002 and rate_err.http_status == 429
    nf_err = errors.ToolNotFoundError("not found")
    assert nf_err.code == -32601 and nf_err.http_status == 404
    exec_err = errors.ToolExecutionError("fail")
    assert exec_err.code == -32603 and exec_err.http_status == 500
    ver_err = errors.VersionMismatchError("version")
    assert ver_err.code == -32003 and ver_err.http_status == 400
    # MCPError base default codes
    base_err = errors.MCPError("base")
    assert base_err.code == -32000 and base_err.http_status == 500
```

---

tests/mcp/test_versioning.py
```python
# tests/mcp/test_versioning.py
from mcp import versioning
from mcp.errors import VersionMismatchError

def test_negotiate_version_basic():
    # Default server supports ["1.0"] (defined in MCP_VERSIONS)
    assert versioning.MCP_VERSIONS == ["1.0"]
    # If client supports 1.0, we agree on 1.0
    assert versioning.negotiate_version(["1.0", "0.9"]) == "1.0"
    # If client list is empty or no overlap -> VersionMismatchError
    try:
        versioning.negotiate_version(["0.9"])
    except VersionMismatchError as e:
        assert "No compatible MCP version" in str(e)
    else:
        raise AssertionError("Expected VersionMismatchError")
    # Simulate future scenario: if server had multiple versions
    versioning.MCP_VERSIONS = ["1.0", "2.0"]
    # If client supports both, should get highest common (2.0)
    assert versioning.negotiate_version(["1.0", "2.0"]) == "2.0"
    # If client supports only 2.0 and server has 1.0 and 2.0 -> gets 2.0
    assert versioning.negotiate_version(["2.0"]) == "2.0"
```

---

MCP_IMPLEMENTATION_SUMMARY.md
```markdown
# MCP Capabilities Implementation Summary

**Version:** vNext (Post-Tier1 Patchset)

This document summarizes the MCP capability status after the latest patchset, highlighting implementations, tests, and safeguards.

(See the earlier description in the patchset for full details — this file is included alongside the codebase.)
```
