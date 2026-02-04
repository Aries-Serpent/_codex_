"""Error hierarchy for MCP components and tests."""

from __future__ import annotations

from typing import Any, Iterable
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


class MCPError(Exception):
    """Base class for MCP-specific errors with codes and HTTP status."""

    code = "MCP_ERROR"
    http_status = 500
    jsonrpc_code = -32000  # JSON-RPC error code

    def xǁMCPErrorǁ__init____mutmut_orig(self, message: str, *, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def xǁMCPErrorǁ__init____mutmut_1(self, message: str, *, details: dict[str, Any] | None = None):
        super().__init__(None)
        self.message = message
        self.details = details or {}

    def xǁMCPErrorǁ__init____mutmut_2(self, message: str, *, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = None
        self.details = details or {}

    def xǁMCPErrorǁ__init____mutmut_3(self, message: str, *, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = None

    def xǁMCPErrorǁ__init____mutmut_4(self, message: str, *, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details and {}
    
    xǁMCPErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPErrorǁ__init____mutmut_1': xǁMCPErrorǁ__init____mutmut_1, 
        'xǁMCPErrorǁ__init____mutmut_2': xǁMCPErrorǁ__init____mutmut_2, 
        'xǁMCPErrorǁ__init____mutmut_3': xǁMCPErrorǁ__init____mutmut_3, 
        'xǁMCPErrorǁ__init____mutmut_4': xǁMCPErrorǁ__init____mutmut_4
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMCPErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMCPErrorǁ__init____mutmut_orig)
    xǁMCPErrorǁ__init____mutmut_orig.__name__ = 'xǁMCPErrorǁ__init__'

    def xǁMCPErrorǁto_dict__mutmut_orig(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.details:
            payload["details"] = self.details
        return payload

    def xǁMCPErrorǁto_dict__mutmut_1(self) -> dict[str, Any]:
        payload: dict[str, Any] = None
        if self.details:
            payload["details"] = self.details
        return payload

    def xǁMCPErrorǁto_dict__mutmut_2(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"XXcodeXX": self.code, "message": self.message}
        if self.details:
            payload["details"] = self.details
        return payload

    def xǁMCPErrorǁto_dict__mutmut_3(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"CODE": self.code, "message": self.message}
        if self.details:
            payload["details"] = self.details
        return payload

    def xǁMCPErrorǁto_dict__mutmut_4(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"code": self.code, "XXmessageXX": self.message}
        if self.details:
            payload["details"] = self.details
        return payload

    def xǁMCPErrorǁto_dict__mutmut_5(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"code": self.code, "MESSAGE": self.message}
        if self.details:
            payload["details"] = self.details
        return payload

    def xǁMCPErrorǁto_dict__mutmut_6(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.details:
            payload["details"] = None
        return payload

    def xǁMCPErrorǁto_dict__mutmut_7(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.details:
            payload["XXdetailsXX"] = self.details
        return payload

    def xǁMCPErrorǁto_dict__mutmut_8(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.details:
            payload["DETAILS"] = self.details
        return payload
    
    xǁMCPErrorǁto_dict__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPErrorǁto_dict__mutmut_1': xǁMCPErrorǁto_dict__mutmut_1, 
        'xǁMCPErrorǁto_dict__mutmut_2': xǁMCPErrorǁto_dict__mutmut_2, 
        'xǁMCPErrorǁto_dict__mutmut_3': xǁMCPErrorǁto_dict__mutmut_3, 
        'xǁMCPErrorǁto_dict__mutmut_4': xǁMCPErrorǁto_dict__mutmut_4, 
        'xǁMCPErrorǁto_dict__mutmut_5': xǁMCPErrorǁto_dict__mutmut_5, 
        'xǁMCPErrorǁto_dict__mutmut_6': xǁMCPErrorǁto_dict__mutmut_6, 
        'xǁMCPErrorǁto_dict__mutmut_7': xǁMCPErrorǁto_dict__mutmut_7, 
        'xǁMCPErrorǁto_dict__mutmut_8': xǁMCPErrorǁto_dict__mutmut_8
    }
    
    def to_dict(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPErrorǁto_dict__mutmut_orig"), object.__getattribute__(self, "xǁMCPErrorǁto_dict__mutmut_mutants"), args, kwargs, self)
        return result 
    
    to_dict.__signature__ = _mutmut_signature(xǁMCPErrorǁto_dict__mutmut_orig)
    xǁMCPErrorǁto_dict__mutmut_orig.__name__ = 'xǁMCPErrorǁto_dict'


class ToolNotFound(MCPError):
    code = "TOOL_NOT_FOUND"
    http_status = 404
    jsonrpc_code = -32601  # Method not found


class ValidationError(MCPError):
    code = "VALIDATION_ERROR"
    http_status = 400
    jsonrpc_code = -32602  # Invalid params


class RateLimitExceeded(MCPError):
    code = "RATE_LIMIT_EXCEEDED"
    http_status = 429
    jsonrpc_code = -32002  # Custom: rate limit


class Unauthorized(MCPError):
    code = "UNAUTHORIZED"
    http_status = 401
    jsonrpc_code = -32001  # Custom: unauthorized


_KNOWN_CODES: Iterable[str] = {
    MCPError.code,
    ToolNotFound.code,
    ValidationError.code,
    RateLimitExceeded.code,
    Unauthorized.code,
}


def x_validate_error_response__mutmut_orig(code: str, message: str) -> bool:
    """Validate that an error response uses a known code and message."""

    if not code or not message:
        return False
    return code in _KNOWN_CODES


def x_validate_error_response__mutmut_1(code: str, message: str) -> bool:
    """Validate that an error response uses a known code and message."""

    if not code and not message:
        return False
    return code in _KNOWN_CODES


def x_validate_error_response__mutmut_2(code: str, message: str) -> bool:
    """Validate that an error response uses a known code and message."""

    if code or not message:
        return False
    return code in _KNOWN_CODES


def x_validate_error_response__mutmut_3(code: str, message: str) -> bool:
    """Validate that an error response uses a known code and message."""

    if not code or message:
        return False
    return code in _KNOWN_CODES


def x_validate_error_response__mutmut_4(code: str, message: str) -> bool:
    """Validate that an error response uses a known code and message."""

    if not code or not message:
        return True
    return code in _KNOWN_CODES


def x_validate_error_response__mutmut_5(code: str, message: str) -> bool:
    """Validate that an error response uses a known code and message."""

    if not code or not message:
        return False
    return code not in _KNOWN_CODES

x_validate_error_response__mutmut_mutants : ClassVar[MutantDict] = {
'x_validate_error_response__mutmut_1': x_validate_error_response__mutmut_1, 
    'x_validate_error_response__mutmut_2': x_validate_error_response__mutmut_2, 
    'x_validate_error_response__mutmut_3': x_validate_error_response__mutmut_3, 
    'x_validate_error_response__mutmut_4': x_validate_error_response__mutmut_4, 
    'x_validate_error_response__mutmut_5': x_validate_error_response__mutmut_5
}

def validate_error_response(*args, **kwargs):
    result = _mutmut_trampoline(x_validate_error_response__mutmut_orig, x_validate_error_response__mutmut_mutants, args, kwargs)
    return result 

validate_error_response.__signature__ = _mutmut_signature(x_validate_error_response__mutmut_orig)
x_validate_error_response__mutmut_orig.__name__ = 'x_validate_error_response'


__all__ = [
    "MCPError",
    "ToolNotFound",
    "ValidationError",
    "RateLimitExceeded",
    "Unauthorized",
    "validate_error_response",
]
