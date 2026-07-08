"""JSON-RPC 2.0 handler for MCP server.

This module provides the JSON-RPC handling layer for MCP:
- Request validation and dispatch
- Error handling and response formatting
- Batch request processing
- Method registration
"""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, Optional

logger = logging.getLogger(__name__)


# JSON-RPC 2.0 error codes
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


@dataclass
class JsonRpcRequest:
    """Parsed JSON-RPC request."""

    method: str
    params: Optional[dict[str, Any]] = None
    id: Optional[str | int] = None
    jsonrpc: str = "2.0"

    @property
    def is_notification(self) -> bool:
        """Check if this is a notification (no id)."""
        return self.id is None


@dataclass
class JsonRpcResponse:
    """JSON-RPC response."""

    id: Optional[str | int]
    result: Optional[Any] = None
    error: Optional[dict[str, Any]] = None
    jsonrpc: str = "2.0"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        response: dict[str, Any] = {"jsonrpc": self.jsonrpc, "id": self.id}
        if self.error is not None:
            response["error"] = self.error
        else:
            response["result"] = self.result
        return response


@dataclass
class JsonRpcError:
    """JSON-RPC error with standard fields."""

    code: int
    message: str
    data: Optional[Any] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        error: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.data is not None:
            error["data"] = self.data
        return error


# Type alias for method handlers
MethodHandler = Callable[[Optional[dict[str, Any]]], Awaitable[Any]]


class JsonRpcHandler:
    """Handler for JSON-RPC 2.0 requests.

    This handler implements the JSON-RPC 2.0 specification:
    - Request validation
    - Method dispatch
    - Error handling
    - Notification support
    """

    def __init__(self) -> None:
        """Initialize the JSON-RPC handler."""
        self._methods: dict[str, MethodHandler] = {}
        self._logger = logging.getLogger(__name__)

    def register_method(self, name: str, handler: MethodHandler) -> None:
        """Register a method handler.

        Args:
            name: Method name (e.g., "mcp.listTools").
            handler: Async function to handle the method.
        """
        self._methods[name] = handler
        self._logger.debug("Registered method: %s", name)

    def unregister_method(self, name: str) -> bool:
        """Unregister a method handler.

        Args:
            name: Method name to unregister.

        Returns:
            True if method was unregistered, False if not found.
        """
        if name in self._methods:
            del self._methods[name]
            return True
        return False

    def method(self, name: str) -> Callable[[MethodHandler], MethodHandler]:
        """Decorator for registering method handlers.

        Args:
            name: Method name.

        Returns:
            Decorator function.
        """

        def decorator(func: MethodHandler) -> MethodHandler:
            self.register_method(name, func)
            return func

        return decorator

    def _parse_request(self, data: dict[str, Any]) -> JsonRpcRequest | JsonRpcError:
        """Parse and validate a JSON-RPC request.

        Args:
            data: Raw request data.

        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST, message="Invalid Request: jsonrpc must be '2.0'"
            )

        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST, message="Invalid Request: method must be a string"
            )

        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS, message="Invalid params: must be object or array"
            )

        # Get optional id (can be string, int, or None for notifications)
        request_id = data.get("id")

        # Handle params - convert dict params, log array params for tracking
        parsed_params: Optional[dict[str, Any]] = None
        if isinstance(params, dict):
            parsed_params = params
        elif isinstance(params, list):
            # Array-style params are valid JSON-RPC but we only support named params
            self._logger.debug(
                "Array-style params received for method %s, converting to positional",
                method,
            )

        return JsonRpcRequest(method=method, params=parsed_params, id=request_id, jsonrpc="2.0")

    async def _dispatch(self, request: JsonRpcRequest) -> Any:
        """Dispatch a request to its handler.

        Args:
            request: Parsed request.

        Returns:
            Handler result.

        Raises:
            JsonRpcError: If method not found or handler fails.
        """
        handler = self._methods.get(request.method)
        if handler is None:
            raise JsonRpcError(code=METHOD_NOT_FOUND, message=f"Method not found: {request.method}")  # type: ignore[misc]

        return await handler(request.params)

    async def handle_request(self, data: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Handle a single JSON-RPC request.

        Args:
            data: Raw request data.

        Returns:
            Response dictionary, or None for notifications.
        """
        # Parse request
        parsed = self._parse_request(data)

        if isinstance(parsed, JsonRpcError):
            # Parse error - return error response
            request_id = data.get("id")
            return JsonRpcResponse(id=request_id, error=parsed.to_dict()).to_dict()

        request = parsed

        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except (ConnectionError, TimeoutError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                # Log but don't respond to notifications
                self._logger.warning("Notification error for %s: %s", request.method, e)
            return None

        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(id=request.id, result=result).to_dict()

        except JsonRpcError as e:  # type: ignore[misc]
            type(e).__name__
            logger.debug("JsonRpcError: <ERROR_TYPE>")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(id=request.id, error=e.to_dict()).to_dict()

        except (ValueError, TypeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            self._logger.exception("Unhandled error in method %s", request.method)
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR, message="Internal error", data=str(e)
                ).to_dict(),
            ).to_dict()

    async def handle_batch(self, requests: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.

        Args:
            requests: list of request dictionaries.

        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [
                JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=INVALID_REQUEST, message="Invalid Request: empty batch"
                    ).to_dict(),
                ).to_dict()
            ]

        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(
                    JsonRpcResponse(
                        id=None,
                        error=JsonRpcError(code=INTERNAL_ERROR, message=str(result)).to_dict(),
                    ).to_dict()
                )
            elif result is not None:
                responses.append(result)  # type: ignore[arg-type]

        return responses

    async def handle(
        self, data: dict[str, Any] | list[dict[str, Any]]
    ) -> Optional[dict[str, Any] | list[dict[str, Any]]]:
        """Handle a JSON-RPC request or batch.

        Args:
            data: Request data (single or batch).

        Returns:
            Response data (single or batch), or None for notifications.
        """
        if isinstance(data, list):
            responses = await self.handle_batch(data)
            return responses if responses else None
        return await self.handle_request(data)

    def get_registered_methods(self) -> list[str]:
        """Get list of registered method names.

        Returns:
            list of method names.
        """
        return list(self._methods.keys())
