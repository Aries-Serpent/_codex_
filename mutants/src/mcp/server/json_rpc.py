"""JSON-RPC 2.0 handler for MCP server.

This module provides the JSON-RPC handling layer for MCP:
- Request validation and dispatch
- Error handling and response formatting
- Batch request processing
- Method registration
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Optional, Union

logger = logging.getLogger(__name__)


# JSON-RPC 2.0 error codes
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
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


@dataclass
class JsonRpcRequest:
    """Parsed JSON-RPC request."""
    
    method: str
    params: Optional[dict[str, Any]] = None
    id: Optional[Union[str, int]] = None
    jsonrpc: str = "2.0"
    
    @property
    def is_notification(self) -> bool:
        """Check if this is a notification (no id)."""
        return self.id is None


@dataclass
class JsonRpcResponse:
    """JSON-RPC response."""
    
    id: Optional[Union[str, int]]
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
    
    def xǁJsonRpcHandlerǁ__init____mutmut_orig(self) -> None:
        """Initialize the JSON-RPC handler."""
        self._methods: dict[str, MethodHandler] = {}
        self._logger = logging.getLogger(__name__)
        
    
    def xǁJsonRpcHandlerǁ__init____mutmut_1(self) -> None:
        """Initialize the JSON-RPC handler."""
        self._methods: dict[str, MethodHandler] = None
        self._logger = logging.getLogger(__name__)
        
    
    def xǁJsonRpcHandlerǁ__init____mutmut_2(self) -> None:
        """Initialize the JSON-RPC handler."""
        self._methods: dict[str, MethodHandler] = {}
        self._logger = None
        
    
    def xǁJsonRpcHandlerǁ__init____mutmut_3(self) -> None:
        """Initialize the JSON-RPC handler."""
        self._methods: dict[str, MethodHandler] = {}
        self._logger = logging.getLogger(None)
        
    
    xǁJsonRpcHandlerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁJsonRpcHandlerǁ__init____mutmut_1': xǁJsonRpcHandlerǁ__init____mutmut_1, 
        'xǁJsonRpcHandlerǁ__init____mutmut_2': xǁJsonRpcHandlerǁ__init____mutmut_2, 
        'xǁJsonRpcHandlerǁ__init____mutmut_3': xǁJsonRpcHandlerǁ__init____mutmut_3
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁJsonRpcHandlerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁJsonRpcHandlerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁJsonRpcHandlerǁ__init____mutmut_orig)
    xǁJsonRpcHandlerǁ__init____mutmut_orig.__name__ = 'xǁJsonRpcHandlerǁ__init__'
    def xǁJsonRpcHandlerǁregister_method__mutmut_orig(
        self,
        name: str,
        handler: MethodHandler
    ) -> None:
        """Register a method handler.
        
        Args:
            name: Method name (e.g., "mcp.listTools").
            handler: Async function to handle the method.
        """
        self._methods[name] = handler
        self._logger.debug("Registered method: %s", name)
    def xǁJsonRpcHandlerǁregister_method__mutmut_1(
        self,
        name: str,
        handler: MethodHandler
    ) -> None:
        """Register a method handler.
        
        Args:
            name: Method name (e.g., "mcp.listTools").
            handler: Async function to handle the method.
        """
        self._methods[name] = None
        self._logger.debug("Registered method: %s", name)
    def xǁJsonRpcHandlerǁregister_method__mutmut_2(
        self,
        name: str,
        handler: MethodHandler
    ) -> None:
        """Register a method handler.
        
        Args:
            name: Method name (e.g., "mcp.listTools").
            handler: Async function to handle the method.
        """
        self._methods[name] = handler
        self._logger.debug(None, name)
    def xǁJsonRpcHandlerǁregister_method__mutmut_3(
        self,
        name: str,
        handler: MethodHandler
    ) -> None:
        """Register a method handler.
        
        Args:
            name: Method name (e.g., "mcp.listTools").
            handler: Async function to handle the method.
        """
        self._methods[name] = handler
        self._logger.debug("Registered method: %s", None)
    def xǁJsonRpcHandlerǁregister_method__mutmut_4(
        self,
        name: str,
        handler: MethodHandler
    ) -> None:
        """Register a method handler.
        
        Args:
            name: Method name (e.g., "mcp.listTools").
            handler: Async function to handle the method.
        """
        self._methods[name] = handler
        self._logger.debug(name)
    def xǁJsonRpcHandlerǁregister_method__mutmut_5(
        self,
        name: str,
        handler: MethodHandler
    ) -> None:
        """Register a method handler.
        
        Args:
            name: Method name (e.g., "mcp.listTools").
            handler: Async function to handle the method.
        """
        self._methods[name] = handler
        self._logger.debug("Registered method: %s", )
    def xǁJsonRpcHandlerǁregister_method__mutmut_6(
        self,
        name: str,
        handler: MethodHandler
    ) -> None:
        """Register a method handler.
        
        Args:
            name: Method name (e.g., "mcp.listTools").
            handler: Async function to handle the method.
        """
        self._methods[name] = handler
        self._logger.debug("XXRegistered method: %sXX", name)
    def xǁJsonRpcHandlerǁregister_method__mutmut_7(
        self,
        name: str,
        handler: MethodHandler
    ) -> None:
        """Register a method handler.
        
        Args:
            name: Method name (e.g., "mcp.listTools").
            handler: Async function to handle the method.
        """
        self._methods[name] = handler
        self._logger.debug("registered method: %s", name)
    def xǁJsonRpcHandlerǁregister_method__mutmut_8(
        self,
        name: str,
        handler: MethodHandler
    ) -> None:
        """Register a method handler.
        
        Args:
            name: Method name (e.g., "mcp.listTools").
            handler: Async function to handle the method.
        """
        self._methods[name] = handler
        self._logger.debug("REGISTERED METHOD: %S", name)
    
    xǁJsonRpcHandlerǁregister_method__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁJsonRpcHandlerǁregister_method__mutmut_1': xǁJsonRpcHandlerǁregister_method__mutmut_1, 
        'xǁJsonRpcHandlerǁregister_method__mutmut_2': xǁJsonRpcHandlerǁregister_method__mutmut_2, 
        'xǁJsonRpcHandlerǁregister_method__mutmut_3': xǁJsonRpcHandlerǁregister_method__mutmut_3, 
        'xǁJsonRpcHandlerǁregister_method__mutmut_4': xǁJsonRpcHandlerǁregister_method__mutmut_4, 
        'xǁJsonRpcHandlerǁregister_method__mutmut_5': xǁJsonRpcHandlerǁregister_method__mutmut_5, 
        'xǁJsonRpcHandlerǁregister_method__mutmut_6': xǁJsonRpcHandlerǁregister_method__mutmut_6, 
        'xǁJsonRpcHandlerǁregister_method__mutmut_7': xǁJsonRpcHandlerǁregister_method__mutmut_7, 
        'xǁJsonRpcHandlerǁregister_method__mutmut_8': xǁJsonRpcHandlerǁregister_method__mutmut_8
    }
    
    def register_method(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁJsonRpcHandlerǁregister_method__mutmut_orig"), object.__getattribute__(self, "xǁJsonRpcHandlerǁregister_method__mutmut_mutants"), args, kwargs, self)
        return result 
    
    register_method.__signature__ = _mutmut_signature(xǁJsonRpcHandlerǁregister_method__mutmut_orig)
    xǁJsonRpcHandlerǁregister_method__mutmut_orig.__name__ = 'xǁJsonRpcHandlerǁregister_method'
    
    def xǁJsonRpcHandlerǁunregister_method__mutmut_orig(self, name: str) -> bool:
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
    
    def xǁJsonRpcHandlerǁunregister_method__mutmut_1(self, name: str) -> bool:
        """Unregister a method handler.
        
        Args:
            name: Method name to unregister.
            
        Returns:
            True if method was unregistered, False if not found.
        """
        if name not in self._methods:
            del self._methods[name]
            return True
        return False
    
    def xǁJsonRpcHandlerǁunregister_method__mutmut_2(self, name: str) -> bool:
        """Unregister a method handler.
        
        Args:
            name: Method name to unregister.
            
        Returns:
            True if method was unregistered, False if not found.
        """
        if name in self._methods:
            del self._methods[name]
            return False
        return False
    
    def xǁJsonRpcHandlerǁunregister_method__mutmut_3(self, name: str) -> bool:
        """Unregister a method handler.
        
        Args:
            name: Method name to unregister.
            
        Returns:
            True if method was unregistered, False if not found.
        """
        if name in self._methods:
            del self._methods[name]
            return True
        return True
    
    xǁJsonRpcHandlerǁunregister_method__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁJsonRpcHandlerǁunregister_method__mutmut_1': xǁJsonRpcHandlerǁunregister_method__mutmut_1, 
        'xǁJsonRpcHandlerǁunregister_method__mutmut_2': xǁJsonRpcHandlerǁunregister_method__mutmut_2, 
        'xǁJsonRpcHandlerǁunregister_method__mutmut_3': xǁJsonRpcHandlerǁunregister_method__mutmut_3
    }
    
    def unregister_method(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁJsonRpcHandlerǁunregister_method__mutmut_orig"), object.__getattribute__(self, "xǁJsonRpcHandlerǁunregister_method__mutmut_mutants"), args, kwargs, self)
        return result 
    
    unregister_method.__signature__ = _mutmut_signature(xǁJsonRpcHandlerǁunregister_method__mutmut_orig)
    xǁJsonRpcHandlerǁunregister_method__mutmut_orig.__name__ = 'xǁJsonRpcHandlerǁunregister_method'
    
    def xǁJsonRpcHandlerǁmethod__mutmut_orig(self, name: str) -> Callable[[MethodHandler], MethodHandler]:
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
    
    def xǁJsonRpcHandlerǁmethod__mutmut_1(self, name: str) -> Callable[[MethodHandler], MethodHandler]:
        """Decorator for registering method handlers.
        
        Args:
            name: Method name.
            
        Returns:
            Decorator function.
        """
        def decorator(func: MethodHandler) -> MethodHandler:
            self.register_method(None, func)
            return func
        return decorator
    
    def xǁJsonRpcHandlerǁmethod__mutmut_2(self, name: str) -> Callable[[MethodHandler], MethodHandler]:
        """Decorator for registering method handlers.
        
        Args:
            name: Method name.
            
        Returns:
            Decorator function.
        """
        def decorator(func: MethodHandler) -> MethodHandler:
            self.register_method(name, None)
            return func
        return decorator
    
    def xǁJsonRpcHandlerǁmethod__mutmut_3(self, name: str) -> Callable[[MethodHandler], MethodHandler]:
        """Decorator for registering method handlers.
        
        Args:
            name: Method name.
            
        Returns:
            Decorator function.
        """
        def decorator(func: MethodHandler) -> MethodHandler:
            self.register_method(func)
            return func
        return decorator
    
    def xǁJsonRpcHandlerǁmethod__mutmut_4(self, name: str) -> Callable[[MethodHandler], MethodHandler]:
        """Decorator for registering method handlers.
        
        Args:
            name: Method name.
            
        Returns:
            Decorator function.
        """
        def decorator(func: MethodHandler) -> MethodHandler:
            self.register_method(name, )
            return func
        return decorator
    
    xǁJsonRpcHandlerǁmethod__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁJsonRpcHandlerǁmethod__mutmut_1': xǁJsonRpcHandlerǁmethod__mutmut_1, 
        'xǁJsonRpcHandlerǁmethod__mutmut_2': xǁJsonRpcHandlerǁmethod__mutmut_2, 
        'xǁJsonRpcHandlerǁmethod__mutmut_3': xǁJsonRpcHandlerǁmethod__mutmut_3, 
        'xǁJsonRpcHandlerǁmethod__mutmut_4': xǁJsonRpcHandlerǁmethod__mutmut_4
    }
    
    def method(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁJsonRpcHandlerǁmethod__mutmut_orig"), object.__getattribute__(self, "xǁJsonRpcHandlerǁmethod__mutmut_mutants"), args, kwargs, self)
        return result 
    
    method.__signature__ = _mutmut_signature(xǁJsonRpcHandlerǁmethod__mutmut_orig)
    xǁJsonRpcHandlerǁmethod__mutmut_orig.__name__ = 'xǁJsonRpcHandlerǁmethod'
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_orig(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_1(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get(None) != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_2(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("XXjsonrpcXX") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_3(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("JSONRPC") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_4(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") == "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_5(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "XX2.0XX":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_6(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=None,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_7(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message=None
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_8(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_9(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_10(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="XXInvalid Request: jsonrpc must be '2.0'XX"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_11(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="invalid request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_12(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="INVALID REQUEST: JSONRPC MUST BE '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_13(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = None
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_14(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get(None)
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_15(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("XXmethodXX")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_16(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("METHOD")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_17(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_18(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=None,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_19(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message=None
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_20(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_21(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_22(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="XXInvalid Request: method must be a stringXX"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_23(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="invalid request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_24(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="INVALID REQUEST: METHOD MUST BE A STRING"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_25(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = None
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_26(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get(None)
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_27(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("XXparamsXX")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_28(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("PARAMS")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_29(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None or not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_30(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_31(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_32(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=None,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_33(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message=None
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_34(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_35(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_36(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="XXInvalid params: must be object or arrayXX"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_37(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_38(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="INVALID PARAMS: MUST BE OBJECT OR ARRAY"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_39(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
            )
        
        # Get optional id (can be string, int, or None for notifications)
        request_id = None
        
        # Handle params - convert dict params, log array params for tracking
        parsed_params: Optional[dict[str, Any]] = None
        if isinstance(params, dict):
            parsed_params = params
        elif isinstance(params, list):
            # Array-style params are valid JSON-RPC but we only support named params
            self._logger.debug(
                "Array-style params received for method %s, converting to positional",
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_40(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
            )
        
        # Get optional id (can be string, int, or None for notifications)
        request_id = data.get(None)
        
        # Handle params - convert dict params, log array params for tracking
        parsed_params: Optional[dict[str, Any]] = None
        if isinstance(params, dict):
            parsed_params = params
        elif isinstance(params, list):
            # Array-style params are valid JSON-RPC but we only support named params
            self._logger.debug(
                "Array-style params received for method %s, converting to positional",
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_41(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
            )
        
        # Get optional id (can be string, int, or None for notifications)
        request_id = data.get("XXidXX")
        
        # Handle params - convert dict params, log array params for tracking
        parsed_params: Optional[dict[str, Any]] = None
        if isinstance(params, dict):
            parsed_params = params
        elif isinstance(params, list):
            # Array-style params are valid JSON-RPC but we only support named params
            self._logger.debug(
                "Array-style params received for method %s, converting to positional",
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_42(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
            )
        
        # Get optional id (can be string, int, or None for notifications)
        request_id = data.get("ID")
        
        # Handle params - convert dict params, log array params for tracking
        parsed_params: Optional[dict[str, Any]] = None
        if isinstance(params, dict):
            parsed_params = params
        elif isinstance(params, list):
            # Array-style params are valid JSON-RPC but we only support named params
            self._logger.debug(
                "Array-style params received for method %s, converting to positional",
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_43(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
            )
        
        # Get optional id (can be string, int, or None for notifications)
        request_id = data.get("id")
        
        # Handle params - convert dict params, log array params for tracking
        parsed_params: Optional[dict[str, Any]] = ""
        if isinstance(params, dict):
            parsed_params = params
        elif isinstance(params, list):
            # Array-style params are valid JSON-RPC but we only support named params
            self._logger.debug(
                "Array-style params received for method %s, converting to positional",
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_44(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
            )
        
        # Get optional id (can be string, int, or None for notifications)
        request_id = data.get("id")
        
        # Handle params - convert dict params, log array params for tracking
        parsed_params: Optional[dict[str, Any]] = None
        if isinstance(params, dict):
            parsed_params = None
        elif isinstance(params, list):
            # Array-style params are valid JSON-RPC but we only support named params
            self._logger.debug(
                "Array-style params received for method %s, converting to positional",
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_45(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                None,
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_46(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                None
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_47(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_48(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_49(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                "XXArray-style params received for method %s, converting to positionalXX",
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_50(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                "array-style params received for method %s, converting to positional",
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_51(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                "ARRAY-STYLE PARAMS RECEIVED FOR METHOD %S, CONVERTING TO POSITIONAL",
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_52(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=None,
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_53(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=None,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_54(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=None,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_55(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc=None
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_56(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            params=parsed_params,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_57(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            id=request_id,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_58(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            jsonrpc="2.0"
        )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_59(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            )
    
    def xǁJsonRpcHandlerǁ_parse_request__mutmut_60(
        self,
        data: dict[str, Any]
    ) -> Union[JsonRpcRequest, JsonRpcError]:
        """Parse and validate a JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Parsed request or error.
        """
        # Check jsonrpc version
        if data.get("jsonrpc") != "2.0":
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: jsonrpc must be '2.0'"
            )
        
        # Check method
        method = data.get("method")
        if not isinstance(method, str):
            return JsonRpcError(
                code=INVALID_REQUEST,
                message="Invalid Request: method must be a string"
            )
        
        # Get optional params
        params = data.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            return JsonRpcError(
                code=INVALID_PARAMS,
                message="Invalid params: must be object or array"
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
                method
            )
        
        return JsonRpcRequest(
            method=method,
            params=parsed_params,
            id=request_id,
            jsonrpc="XX2.0XX"
        )
    
    xǁJsonRpcHandlerǁ_parse_request__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁJsonRpcHandlerǁ_parse_request__mutmut_1': xǁJsonRpcHandlerǁ_parse_request__mutmut_1, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_2': xǁJsonRpcHandlerǁ_parse_request__mutmut_2, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_3': xǁJsonRpcHandlerǁ_parse_request__mutmut_3, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_4': xǁJsonRpcHandlerǁ_parse_request__mutmut_4, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_5': xǁJsonRpcHandlerǁ_parse_request__mutmut_5, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_6': xǁJsonRpcHandlerǁ_parse_request__mutmut_6, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_7': xǁJsonRpcHandlerǁ_parse_request__mutmut_7, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_8': xǁJsonRpcHandlerǁ_parse_request__mutmut_8, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_9': xǁJsonRpcHandlerǁ_parse_request__mutmut_9, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_10': xǁJsonRpcHandlerǁ_parse_request__mutmut_10, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_11': xǁJsonRpcHandlerǁ_parse_request__mutmut_11, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_12': xǁJsonRpcHandlerǁ_parse_request__mutmut_12, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_13': xǁJsonRpcHandlerǁ_parse_request__mutmut_13, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_14': xǁJsonRpcHandlerǁ_parse_request__mutmut_14, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_15': xǁJsonRpcHandlerǁ_parse_request__mutmut_15, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_16': xǁJsonRpcHandlerǁ_parse_request__mutmut_16, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_17': xǁJsonRpcHandlerǁ_parse_request__mutmut_17, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_18': xǁJsonRpcHandlerǁ_parse_request__mutmut_18, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_19': xǁJsonRpcHandlerǁ_parse_request__mutmut_19, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_20': xǁJsonRpcHandlerǁ_parse_request__mutmut_20, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_21': xǁJsonRpcHandlerǁ_parse_request__mutmut_21, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_22': xǁJsonRpcHandlerǁ_parse_request__mutmut_22, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_23': xǁJsonRpcHandlerǁ_parse_request__mutmut_23, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_24': xǁJsonRpcHandlerǁ_parse_request__mutmut_24, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_25': xǁJsonRpcHandlerǁ_parse_request__mutmut_25, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_26': xǁJsonRpcHandlerǁ_parse_request__mutmut_26, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_27': xǁJsonRpcHandlerǁ_parse_request__mutmut_27, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_28': xǁJsonRpcHandlerǁ_parse_request__mutmut_28, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_29': xǁJsonRpcHandlerǁ_parse_request__mutmut_29, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_30': xǁJsonRpcHandlerǁ_parse_request__mutmut_30, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_31': xǁJsonRpcHandlerǁ_parse_request__mutmut_31, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_32': xǁJsonRpcHandlerǁ_parse_request__mutmut_32, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_33': xǁJsonRpcHandlerǁ_parse_request__mutmut_33, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_34': xǁJsonRpcHandlerǁ_parse_request__mutmut_34, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_35': xǁJsonRpcHandlerǁ_parse_request__mutmut_35, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_36': xǁJsonRpcHandlerǁ_parse_request__mutmut_36, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_37': xǁJsonRpcHandlerǁ_parse_request__mutmut_37, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_38': xǁJsonRpcHandlerǁ_parse_request__mutmut_38, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_39': xǁJsonRpcHandlerǁ_parse_request__mutmut_39, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_40': xǁJsonRpcHandlerǁ_parse_request__mutmut_40, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_41': xǁJsonRpcHandlerǁ_parse_request__mutmut_41, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_42': xǁJsonRpcHandlerǁ_parse_request__mutmut_42, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_43': xǁJsonRpcHandlerǁ_parse_request__mutmut_43, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_44': xǁJsonRpcHandlerǁ_parse_request__mutmut_44, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_45': xǁJsonRpcHandlerǁ_parse_request__mutmut_45, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_46': xǁJsonRpcHandlerǁ_parse_request__mutmut_46, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_47': xǁJsonRpcHandlerǁ_parse_request__mutmut_47, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_48': xǁJsonRpcHandlerǁ_parse_request__mutmut_48, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_49': xǁJsonRpcHandlerǁ_parse_request__mutmut_49, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_50': xǁJsonRpcHandlerǁ_parse_request__mutmut_50, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_51': xǁJsonRpcHandlerǁ_parse_request__mutmut_51, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_52': xǁJsonRpcHandlerǁ_parse_request__mutmut_52, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_53': xǁJsonRpcHandlerǁ_parse_request__mutmut_53, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_54': xǁJsonRpcHandlerǁ_parse_request__mutmut_54, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_55': xǁJsonRpcHandlerǁ_parse_request__mutmut_55, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_56': xǁJsonRpcHandlerǁ_parse_request__mutmut_56, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_57': xǁJsonRpcHandlerǁ_parse_request__mutmut_57, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_58': xǁJsonRpcHandlerǁ_parse_request__mutmut_58, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_59': xǁJsonRpcHandlerǁ_parse_request__mutmut_59, 
        'xǁJsonRpcHandlerǁ_parse_request__mutmut_60': xǁJsonRpcHandlerǁ_parse_request__mutmut_60
    }
    
    def _parse_request(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁJsonRpcHandlerǁ_parse_request__mutmut_orig"), object.__getattribute__(self, "xǁJsonRpcHandlerǁ_parse_request__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _parse_request.__signature__ = _mutmut_signature(xǁJsonRpcHandlerǁ_parse_request__mutmut_orig)
    xǁJsonRpcHandlerǁ_parse_request__mutmut_orig.__name__ = 'xǁJsonRpcHandlerǁ_parse_request'
    
    async def xǁJsonRpcHandlerǁ_dispatch__mutmut_orig(self, request: JsonRpcRequest) -> Any:
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
            raise JsonRpcError(
                code=METHOD_NOT_FOUND,
                message=f"Method not found: {request.method}"
            )
        
        return await handler(request.params)
    
    async def xǁJsonRpcHandlerǁ_dispatch__mutmut_1(self, request: JsonRpcRequest) -> Any:
        """Dispatch a request to its handler.
        
        Args:
            request: Parsed request.
            
        Returns:
            Handler result.
            
        Raises:
            JsonRpcError: If method not found or handler fails.
        """
        handler = None
        if handler is None:
            raise JsonRpcError(
                code=METHOD_NOT_FOUND,
                message=f"Method not found: {request.method}"
            )
        
        return await handler(request.params)
    
    async def xǁJsonRpcHandlerǁ_dispatch__mutmut_2(self, request: JsonRpcRequest) -> Any:
        """Dispatch a request to its handler.
        
        Args:
            request: Parsed request.
            
        Returns:
            Handler result.
            
        Raises:
            JsonRpcError: If method not found or handler fails.
        """
        handler = self._methods.get(None)
        if handler is None:
            raise JsonRpcError(
                code=METHOD_NOT_FOUND,
                message=f"Method not found: {request.method}"
            )
        
        return await handler(request.params)
    
    async def xǁJsonRpcHandlerǁ_dispatch__mutmut_3(self, request: JsonRpcRequest) -> Any:
        """Dispatch a request to its handler.
        
        Args:
            request: Parsed request.
            
        Returns:
            Handler result.
            
        Raises:
            JsonRpcError: If method not found or handler fails.
        """
        handler = self._methods.get(request.method)
        if handler is not None:
            raise JsonRpcError(
                code=METHOD_NOT_FOUND,
                message=f"Method not found: {request.method}"
            )
        
        return await handler(request.params)
    
    async def xǁJsonRpcHandlerǁ_dispatch__mutmut_4(self, request: JsonRpcRequest) -> Any:
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
            raise JsonRpcError(
                code=None,
                message=f"Method not found: {request.method}"
            )
        
        return await handler(request.params)
    
    async def xǁJsonRpcHandlerǁ_dispatch__mutmut_5(self, request: JsonRpcRequest) -> Any:
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
            raise JsonRpcError(
                code=METHOD_NOT_FOUND,
                message=None
            )
        
        return await handler(request.params)
    
    async def xǁJsonRpcHandlerǁ_dispatch__mutmut_6(self, request: JsonRpcRequest) -> Any:
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
            raise JsonRpcError(
                message=f"Method not found: {request.method}"
            )
        
        return await handler(request.params)
    
    async def xǁJsonRpcHandlerǁ_dispatch__mutmut_7(self, request: JsonRpcRequest) -> Any:
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
            raise JsonRpcError(
                code=METHOD_NOT_FOUND,
                )
        
        return await handler(request.params)
    
    async def xǁJsonRpcHandlerǁ_dispatch__mutmut_8(self, request: JsonRpcRequest) -> Any:
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
            raise JsonRpcError(
                code=METHOD_NOT_FOUND,
                message=f"Method not found: {request.method}"
            )
        
        return await handler(None)
    
    xǁJsonRpcHandlerǁ_dispatch__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁJsonRpcHandlerǁ_dispatch__mutmut_1': xǁJsonRpcHandlerǁ_dispatch__mutmut_1, 
        'xǁJsonRpcHandlerǁ_dispatch__mutmut_2': xǁJsonRpcHandlerǁ_dispatch__mutmut_2, 
        'xǁJsonRpcHandlerǁ_dispatch__mutmut_3': xǁJsonRpcHandlerǁ_dispatch__mutmut_3, 
        'xǁJsonRpcHandlerǁ_dispatch__mutmut_4': xǁJsonRpcHandlerǁ_dispatch__mutmut_4, 
        'xǁJsonRpcHandlerǁ_dispatch__mutmut_5': xǁJsonRpcHandlerǁ_dispatch__mutmut_5, 
        'xǁJsonRpcHandlerǁ_dispatch__mutmut_6': xǁJsonRpcHandlerǁ_dispatch__mutmut_6, 
        'xǁJsonRpcHandlerǁ_dispatch__mutmut_7': xǁJsonRpcHandlerǁ_dispatch__mutmut_7, 
        'xǁJsonRpcHandlerǁ_dispatch__mutmut_8': xǁJsonRpcHandlerǁ_dispatch__mutmut_8
    }
    
    def _dispatch(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁJsonRpcHandlerǁ_dispatch__mutmut_orig"), object.__getattribute__(self, "xǁJsonRpcHandlerǁ_dispatch__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _dispatch.__signature__ = _mutmut_signature(xǁJsonRpcHandlerǁ_dispatch__mutmut_orig)
    xǁJsonRpcHandlerǁ_dispatch__mutmut_orig.__name__ = 'xǁJsonRpcHandlerǁ_dispatch'
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_orig(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_1(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        """Handle a single JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Response dictionary, or None for notifications.
        """
        # Parse request
        parsed = None
        
        if isinstance(parsed, JsonRpcError):
            # Parse error - return error response
            request_id = data.get("id")
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_2(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        """Handle a single JSON-RPC request.
        
        Args:
            data: Raw request data.
            
        Returns:
            Response dictionary, or None for notifications.
        """
        # Parse request
        parsed = self._parse_request(None)
        
        if isinstance(parsed, JsonRpcError):
            # Parse error - return error response
            request_id = data.get("id")
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_3(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            request_id = None
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_4(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            request_id = data.get(None)
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_5(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            request_id = data.get("XXidXX")
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_6(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            request_id = data.get("ID")
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_7(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=None,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_8(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=None
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_9(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_10(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_11(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = None
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_12(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(None)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_13(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(None)
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_14(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    None,
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_15(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    None,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_16(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    None
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_17(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_18(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_19(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_20(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "XXNotification error for %s: %sXX",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_21(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_22(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "NOTIFICATION ERROR FOR %S: %S",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_23(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = None
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_24(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(None)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_25(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=None,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_26(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=None
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_27(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_28(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_29(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(None)
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_30(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug(None, exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_31(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=None)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_32(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug(exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_33(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", )
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_34(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("XXException caught, returningXX", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_35(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_36(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("EXCEPTION CAUGHT, RETURNING", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_37(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=False)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_38(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=None,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_39(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=None
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_40(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_41(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_42(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(None)
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_43(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                None,
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_44(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                None
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_45(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_46(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_47(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "XXUnhandled error in method %sXX",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_48(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_49(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "UNHANDLED ERROR IN METHOD %S",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_50(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_51(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=None
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_52(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_53(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_54(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=None,
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_55(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message=None,
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_56(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=None
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_57(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    message="Internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_58(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_59(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_60(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="XXInternal errorXX",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_61(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="internal error",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_62(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="INTERNAL ERROR",
                    data=str(e)
                ).to_dict()
            ).to_dict()
    
    async def xǁJsonRpcHandlerǁhandle_request__mutmut_63(
        self,
        data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
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
            return JsonRpcResponse(
                id=request_id,
                error=parsed.to_dict()
            ).to_dict()
        
        request = parsed
        
        # Handle notification (no id)
        if request.is_notification:
            try:
                await self._dispatch(request)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                # Log but don't respond to notifications
                self._logger.warning(
                    "Notification error for %s: %s",
                    request.method,
                    e
                )
            return None
        
        # Handle normal request
        try:
            result = await self._dispatch(request)
            return JsonRpcResponse(
                id=request.id,
                result=result
            ).to_dict()
            
        except JsonRpcError as e:
            logger.debug(f"JsonRpcError: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return JsonRpcResponse(
                id=request.id,
                error=e.to_dict()
            ).to_dict()
            
        except Exception as e:
            logger.debug(f"Exception: {e}")
            self._logger.exception(
                "Unhandled error in method %s",
                request.method
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=INTERNAL_ERROR,
                    message="Internal error",
                    data=str(None)
                ).to_dict()
            ).to_dict()
    
    xǁJsonRpcHandlerǁhandle_request__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁJsonRpcHandlerǁhandle_request__mutmut_1': xǁJsonRpcHandlerǁhandle_request__mutmut_1, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_2': xǁJsonRpcHandlerǁhandle_request__mutmut_2, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_3': xǁJsonRpcHandlerǁhandle_request__mutmut_3, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_4': xǁJsonRpcHandlerǁhandle_request__mutmut_4, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_5': xǁJsonRpcHandlerǁhandle_request__mutmut_5, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_6': xǁJsonRpcHandlerǁhandle_request__mutmut_6, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_7': xǁJsonRpcHandlerǁhandle_request__mutmut_7, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_8': xǁJsonRpcHandlerǁhandle_request__mutmut_8, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_9': xǁJsonRpcHandlerǁhandle_request__mutmut_9, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_10': xǁJsonRpcHandlerǁhandle_request__mutmut_10, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_11': xǁJsonRpcHandlerǁhandle_request__mutmut_11, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_12': xǁJsonRpcHandlerǁhandle_request__mutmut_12, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_13': xǁJsonRpcHandlerǁhandle_request__mutmut_13, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_14': xǁJsonRpcHandlerǁhandle_request__mutmut_14, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_15': xǁJsonRpcHandlerǁhandle_request__mutmut_15, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_16': xǁJsonRpcHandlerǁhandle_request__mutmut_16, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_17': xǁJsonRpcHandlerǁhandle_request__mutmut_17, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_18': xǁJsonRpcHandlerǁhandle_request__mutmut_18, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_19': xǁJsonRpcHandlerǁhandle_request__mutmut_19, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_20': xǁJsonRpcHandlerǁhandle_request__mutmut_20, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_21': xǁJsonRpcHandlerǁhandle_request__mutmut_21, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_22': xǁJsonRpcHandlerǁhandle_request__mutmut_22, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_23': xǁJsonRpcHandlerǁhandle_request__mutmut_23, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_24': xǁJsonRpcHandlerǁhandle_request__mutmut_24, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_25': xǁJsonRpcHandlerǁhandle_request__mutmut_25, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_26': xǁJsonRpcHandlerǁhandle_request__mutmut_26, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_27': xǁJsonRpcHandlerǁhandle_request__mutmut_27, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_28': xǁJsonRpcHandlerǁhandle_request__mutmut_28, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_29': xǁJsonRpcHandlerǁhandle_request__mutmut_29, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_30': xǁJsonRpcHandlerǁhandle_request__mutmut_30, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_31': xǁJsonRpcHandlerǁhandle_request__mutmut_31, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_32': xǁJsonRpcHandlerǁhandle_request__mutmut_32, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_33': xǁJsonRpcHandlerǁhandle_request__mutmut_33, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_34': xǁJsonRpcHandlerǁhandle_request__mutmut_34, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_35': xǁJsonRpcHandlerǁhandle_request__mutmut_35, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_36': xǁJsonRpcHandlerǁhandle_request__mutmut_36, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_37': xǁJsonRpcHandlerǁhandle_request__mutmut_37, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_38': xǁJsonRpcHandlerǁhandle_request__mutmut_38, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_39': xǁJsonRpcHandlerǁhandle_request__mutmut_39, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_40': xǁJsonRpcHandlerǁhandle_request__mutmut_40, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_41': xǁJsonRpcHandlerǁhandle_request__mutmut_41, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_42': xǁJsonRpcHandlerǁhandle_request__mutmut_42, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_43': xǁJsonRpcHandlerǁhandle_request__mutmut_43, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_44': xǁJsonRpcHandlerǁhandle_request__mutmut_44, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_45': xǁJsonRpcHandlerǁhandle_request__mutmut_45, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_46': xǁJsonRpcHandlerǁhandle_request__mutmut_46, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_47': xǁJsonRpcHandlerǁhandle_request__mutmut_47, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_48': xǁJsonRpcHandlerǁhandle_request__mutmut_48, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_49': xǁJsonRpcHandlerǁhandle_request__mutmut_49, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_50': xǁJsonRpcHandlerǁhandle_request__mutmut_50, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_51': xǁJsonRpcHandlerǁhandle_request__mutmut_51, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_52': xǁJsonRpcHandlerǁhandle_request__mutmut_52, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_53': xǁJsonRpcHandlerǁhandle_request__mutmut_53, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_54': xǁJsonRpcHandlerǁhandle_request__mutmut_54, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_55': xǁJsonRpcHandlerǁhandle_request__mutmut_55, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_56': xǁJsonRpcHandlerǁhandle_request__mutmut_56, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_57': xǁJsonRpcHandlerǁhandle_request__mutmut_57, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_58': xǁJsonRpcHandlerǁhandle_request__mutmut_58, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_59': xǁJsonRpcHandlerǁhandle_request__mutmut_59, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_60': xǁJsonRpcHandlerǁhandle_request__mutmut_60, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_61': xǁJsonRpcHandlerǁhandle_request__mutmut_61, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_62': xǁJsonRpcHandlerǁhandle_request__mutmut_62, 
        'xǁJsonRpcHandlerǁhandle_request__mutmut_63': xǁJsonRpcHandlerǁhandle_request__mutmut_63
    }
    
    def handle_request(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁJsonRpcHandlerǁhandle_request__mutmut_orig"), object.__getattribute__(self, "xǁJsonRpcHandlerǁhandle_request__mutmut_mutants"), args, kwargs, self)
        return result 
    
    handle_request.__signature__ = _mutmut_signature(xǁJsonRpcHandlerǁhandle_request__mutmut_orig)
    xǁJsonRpcHandlerǁhandle_request__mutmut_orig.__name__ = 'xǁJsonRpcHandlerǁhandle_request'
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_orig(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    message="Invalid Request: empty batch"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=INTERNAL_ERROR,
                        message=str(result)
                    ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_1(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    message="Invalid Request: empty batch"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=INTERNAL_ERROR,
                        message=str(result)
                    ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_2(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=None
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=INTERNAL_ERROR,
                        message=str(result)
                    ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_3(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    message="Invalid Request: empty batch"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=INTERNAL_ERROR,
                        message=str(result)
                    ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_4(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=INTERNAL_ERROR,
                        message=str(result)
                    ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_5(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=None,
                    message="Invalid Request: empty batch"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=INTERNAL_ERROR,
                        message=str(result)
                    ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_6(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    message=None
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=INTERNAL_ERROR,
                        message=str(result)
                    ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_7(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    message="Invalid Request: empty batch"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=INTERNAL_ERROR,
                        message=str(result)
                    ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_8(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=INTERNAL_ERROR,
                        message=str(result)
                    ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_9(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    message="XXInvalid Request: empty batchXX"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=INTERNAL_ERROR,
                        message=str(result)
                    ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_10(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    message="invalid request: empty batch"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=INTERNAL_ERROR,
                        message=str(result)
                    ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_11(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    message="INVALID REQUEST: EMPTY BATCH"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=INTERNAL_ERROR,
                        message=str(result)
                    ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_12(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    message="Invalid Request: empty batch"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = None
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=INTERNAL_ERROR,
                        message=str(result)
                    ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_13(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    message="Invalid Request: empty batch"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(None) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=INTERNAL_ERROR,
                        message=str(result)
                    ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_14(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    message="Invalid Request: empty batch"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = None
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=INTERNAL_ERROR,
                        message=str(result)
                    ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_15(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    message="Invalid Request: empty batch"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=None)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=INTERNAL_ERROR,
                        message=str(result)
                    ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_16(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    message="Invalid Request: empty batch"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=INTERNAL_ERROR,
                        message=str(result)
                    ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_17(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    message="Invalid Request: empty batch"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, )
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=INTERNAL_ERROR,
                        message=str(result)
                    ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_18(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    message="Invalid Request: empty batch"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=INTERNAL_ERROR,
                        message=str(result)
                    ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_19(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    message="Invalid Request: empty batch"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = None
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=INTERNAL_ERROR,
                        message=str(result)
                    ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_20(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    message="Invalid Request: empty batch"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(None)
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_21(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    message="Invalid Request: empty batch"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=None
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_22(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    message="Invalid Request: empty batch"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    error=JsonRpcError(
                        code=INTERNAL_ERROR,
                        message=str(result)
                    ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_23(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    message="Invalid Request: empty batch"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_24(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    message="Invalid Request: empty batch"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=None,
                        message=str(result)
                    ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_25(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    message="Invalid Request: empty batch"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=INTERNAL_ERROR,
                        message=None
                    ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_26(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    message="Invalid Request: empty batch"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        message=str(result)
                    ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_27(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    message="Invalid Request: empty batch"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=INTERNAL_ERROR,
                        ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_28(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    message="Invalid Request: empty batch"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=INTERNAL_ERROR,
                        message=str(None)
                    ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_29(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    message="Invalid Request: empty batch"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=INTERNAL_ERROR,
                        message=str(result)
                    ).to_dict()
                ).to_dict())
            elif result is None:
                responses.append(result)
        
        return responses
    
    async def xǁJsonRpcHandlerǁhandle_batch__mutmut_30(
        self,
        requests: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Handle a batch of JSON-RPC requests.
        
        Args:
            requests: list of request dictionaries.
            
        Returns:
            list of response dictionaries.
        """
        if not requests:
            return [JsonRpcResponse(
                id=None,
                error=JsonRpcError(
                    code=INVALID_REQUEST,
                    message="Invalid Request: empty batch"
                ).to_dict()
            ).to_dict()]
        
        # Process all requests concurrently
        tasks = [self.handle_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None responses (notifications)
        responses = []
        for result in results:
            if isinstance(result, Exception):
                responses.append(JsonRpcResponse(
                    id=None,
                    error=JsonRpcError(
                        code=INTERNAL_ERROR,
                        message=str(result)
                    ).to_dict()
                ).to_dict())
            elif result is not None:
                responses.append(None)
        
        return responses
    
    xǁJsonRpcHandlerǁhandle_batch__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁJsonRpcHandlerǁhandle_batch__mutmut_1': xǁJsonRpcHandlerǁhandle_batch__mutmut_1, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_2': xǁJsonRpcHandlerǁhandle_batch__mutmut_2, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_3': xǁJsonRpcHandlerǁhandle_batch__mutmut_3, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_4': xǁJsonRpcHandlerǁhandle_batch__mutmut_4, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_5': xǁJsonRpcHandlerǁhandle_batch__mutmut_5, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_6': xǁJsonRpcHandlerǁhandle_batch__mutmut_6, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_7': xǁJsonRpcHandlerǁhandle_batch__mutmut_7, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_8': xǁJsonRpcHandlerǁhandle_batch__mutmut_8, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_9': xǁJsonRpcHandlerǁhandle_batch__mutmut_9, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_10': xǁJsonRpcHandlerǁhandle_batch__mutmut_10, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_11': xǁJsonRpcHandlerǁhandle_batch__mutmut_11, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_12': xǁJsonRpcHandlerǁhandle_batch__mutmut_12, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_13': xǁJsonRpcHandlerǁhandle_batch__mutmut_13, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_14': xǁJsonRpcHandlerǁhandle_batch__mutmut_14, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_15': xǁJsonRpcHandlerǁhandle_batch__mutmut_15, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_16': xǁJsonRpcHandlerǁhandle_batch__mutmut_16, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_17': xǁJsonRpcHandlerǁhandle_batch__mutmut_17, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_18': xǁJsonRpcHandlerǁhandle_batch__mutmut_18, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_19': xǁJsonRpcHandlerǁhandle_batch__mutmut_19, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_20': xǁJsonRpcHandlerǁhandle_batch__mutmut_20, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_21': xǁJsonRpcHandlerǁhandle_batch__mutmut_21, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_22': xǁJsonRpcHandlerǁhandle_batch__mutmut_22, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_23': xǁJsonRpcHandlerǁhandle_batch__mutmut_23, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_24': xǁJsonRpcHandlerǁhandle_batch__mutmut_24, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_25': xǁJsonRpcHandlerǁhandle_batch__mutmut_25, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_26': xǁJsonRpcHandlerǁhandle_batch__mutmut_26, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_27': xǁJsonRpcHandlerǁhandle_batch__mutmut_27, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_28': xǁJsonRpcHandlerǁhandle_batch__mutmut_28, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_29': xǁJsonRpcHandlerǁhandle_batch__mutmut_29, 
        'xǁJsonRpcHandlerǁhandle_batch__mutmut_30': xǁJsonRpcHandlerǁhandle_batch__mutmut_30
    }
    
    def handle_batch(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁJsonRpcHandlerǁhandle_batch__mutmut_orig"), object.__getattribute__(self, "xǁJsonRpcHandlerǁhandle_batch__mutmut_mutants"), args, kwargs, self)
        return result 
    
    handle_batch.__signature__ = _mutmut_signature(xǁJsonRpcHandlerǁhandle_batch__mutmut_orig)
    xǁJsonRpcHandlerǁhandle_batch__mutmut_orig.__name__ = 'xǁJsonRpcHandlerǁhandle_batch'
    
    async def xǁJsonRpcHandlerǁhandle__mutmut_orig(
        self,
        data: Union[dict[str, Any], list[dict[str, Any]]]
    ) -> Optional[Union[dict[str, Any], list[dict[str, Any]]]]:
        """Handle a JSON-RPC request or batch.
        
        Args:
            data: Request data (single or batch).
            
        Returns:
            Response data (single or batch), or None for notifications.
        """
        if isinstance(data, list):
            responses = await self.handle_batch(data)
            return responses if responses else None
        else:
            return await self.handle_request(data)
    
    async def xǁJsonRpcHandlerǁhandle__mutmut_1(
        self,
        data: Union[dict[str, Any], list[dict[str, Any]]]
    ) -> Optional[Union[dict[str, Any], list[dict[str, Any]]]]:
        """Handle a JSON-RPC request or batch.
        
        Args:
            data: Request data (single or batch).
            
        Returns:
            Response data (single or batch), or None for notifications.
        """
        if isinstance(data, list):
            responses = None
            return responses if responses else None
        else:
            return await self.handle_request(data)
    
    async def xǁJsonRpcHandlerǁhandle__mutmut_2(
        self,
        data: Union[dict[str, Any], list[dict[str, Any]]]
    ) -> Optional[Union[dict[str, Any], list[dict[str, Any]]]]:
        """Handle a JSON-RPC request or batch.
        
        Args:
            data: Request data (single or batch).
            
        Returns:
            Response data (single or batch), or None for notifications.
        """
        if isinstance(data, list):
            responses = await self.handle_batch(None)
            return responses if responses else None
        else:
            return await self.handle_request(data)
    
    async def xǁJsonRpcHandlerǁhandle__mutmut_3(
        self,
        data: Union[dict[str, Any], list[dict[str, Any]]]
    ) -> Optional[Union[dict[str, Any], list[dict[str, Any]]]]:
        """Handle a JSON-RPC request or batch.
        
        Args:
            data: Request data (single or batch).
            
        Returns:
            Response data (single or batch), or None for notifications.
        """
        if isinstance(data, list):
            responses = await self.handle_batch(data)
            return responses if responses else None
        else:
            return await self.handle_request(None)
    
    xǁJsonRpcHandlerǁhandle__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁJsonRpcHandlerǁhandle__mutmut_1': xǁJsonRpcHandlerǁhandle__mutmut_1, 
        'xǁJsonRpcHandlerǁhandle__mutmut_2': xǁJsonRpcHandlerǁhandle__mutmut_2, 
        'xǁJsonRpcHandlerǁhandle__mutmut_3': xǁJsonRpcHandlerǁhandle__mutmut_3
    }
    
    def handle(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁJsonRpcHandlerǁhandle__mutmut_orig"), object.__getattribute__(self, "xǁJsonRpcHandlerǁhandle__mutmut_mutants"), args, kwargs, self)
        return result 
    
    handle.__signature__ = _mutmut_signature(xǁJsonRpcHandlerǁhandle__mutmut_orig)
    xǁJsonRpcHandlerǁhandle__mutmut_orig.__name__ = 'xǁJsonRpcHandlerǁhandle'
    
    def xǁJsonRpcHandlerǁget_registered_methods__mutmut_orig(self) -> list[str]:
        """Get list of registered method names.
        
        Returns:
            list of method names.
        """
        return list(self._methods.keys())
    
    def xǁJsonRpcHandlerǁget_registered_methods__mutmut_1(self) -> list[str]:
        """Get list of registered method names.
        
        Returns:
            list of method names.
        """
        return list(None)
    
    xǁJsonRpcHandlerǁget_registered_methods__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁJsonRpcHandlerǁget_registered_methods__mutmut_1': xǁJsonRpcHandlerǁget_registered_methods__mutmut_1
    }
    
    def get_registered_methods(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁJsonRpcHandlerǁget_registered_methods__mutmut_orig"), object.__getattribute__(self, "xǁJsonRpcHandlerǁget_registered_methods__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_registered_methods.__signature__ = _mutmut_signature(xǁJsonRpcHandlerǁget_registered_methods__mutmut_orig)
    xǁJsonRpcHandlerǁget_registered_methods__mutmut_orig.__name__ = 'xǁJsonRpcHandlerǁget_registered_methods'
