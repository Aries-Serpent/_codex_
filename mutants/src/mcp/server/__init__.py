"""MCP server entrypoints and in-process JSON-RPC handlers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
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
class Tool:
    name: str
    description: str
    schema: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        payload = {"name": self.name, "description": self.description}
        if self.schema is not None:
            payload["schema"] = self.schema
        return payload


@dataclass
class ToolRegistry:
    _tools: list[Tool] = field(default_factory=list)

    def register(self, tool: Tool) -> None:
        self._tools.append(tool)

    def list_tools(self) -> list[dict[str, Any]]:
        return [tool.to_dict() for tool in self._tools]


class MCPServer:
    """Minimal JSON-RPC server for tests and in-process usage."""

    def xǁMCPServerǁ__init____mutmut_orig(self, tool_registry: Optional[ToolRegistry] = None) -> None:
        self.tool_registry = tool_registry or ToolRegistry()
        self.supported_versions = ["1.0"]

    def xǁMCPServerǁ__init____mutmut_1(self, tool_registry: Optional[ToolRegistry] = None) -> None:
        self.tool_registry = None
        self.supported_versions = ["1.0"]

    def xǁMCPServerǁ__init____mutmut_2(self, tool_registry: Optional[ToolRegistry] = None) -> None:
        self.tool_registry = tool_registry and ToolRegistry()
        self.supported_versions = ["1.0"]

    def xǁMCPServerǁ__init____mutmut_3(self, tool_registry: Optional[ToolRegistry] = None) -> None:
        self.tool_registry = tool_registry or ToolRegistry()
        self.supported_versions = None

    def xǁMCPServerǁ__init____mutmut_4(self, tool_registry: Optional[ToolRegistry] = None) -> None:
        self.tool_registry = tool_registry or ToolRegistry()
        self.supported_versions = ["XX1.0XX"]
    
    xǁMCPServerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPServerǁ__init____mutmut_1': xǁMCPServerǁ__init____mutmut_1, 
        'xǁMCPServerǁ__init____mutmut_2': xǁMCPServerǁ__init____mutmut_2, 
        'xǁMCPServerǁ__init____mutmut_3': xǁMCPServerǁ__init____mutmut_3, 
        'xǁMCPServerǁ__init____mutmut_4': xǁMCPServerǁ__init____mutmut_4
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPServerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMCPServerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMCPServerǁ__init____mutmut_orig)
    xǁMCPServerǁ__init____mutmut_orig.__name__ = 'xǁMCPServerǁ__init__'

    async def xǁMCPServerǁhandle_request__mutmut_orig(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_1(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = None
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_2(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get(None)
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_3(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("XXidXX")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_4(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("ID")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_5(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = None
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_6(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get(None)
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_7(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("XXmethodXX")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_8(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("METHOD")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_9(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = None

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_10(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get(None, {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_11(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", None)

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_12(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get({})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_13(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", )

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_14(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("XXparamsXX", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_15(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("PARAMS", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_16(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is not None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_17(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method != "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_18(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "XXmcp.listToolsXX":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_19(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listtools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_20(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "MCP.LISTTOOLS":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_21(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"XXjsonrpcXX": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_22(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"JSONRPC": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_23(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "XX2.0XX", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_24(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "XXidXX": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_25(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "ID": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_26(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "XXresultXX": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_27(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "RESULT": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_28(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method != "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_29(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "XXmcp.negotiateVersionXX":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_30(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateversion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_31(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "MCP.NEGOTIATEVERSION":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_32(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = None
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_33(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get(None, [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_34(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", None)
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_35(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get([])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_36(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", )
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_37(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("XXsupportedXX", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_38(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("SUPPORTED", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_39(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(None):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_40(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v not in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_41(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"XXjsonrpcXX": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_42(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"JSONRPC": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_43(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "XX2.0XX", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_44(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "XXidXX": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_45(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "ID": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_46(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "XXresultXX": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_47(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "RESULT": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_48(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "XX1.0XX"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_49(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "XXjsonrpcXX": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_50(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "JSONRPC": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_51(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "XX2.0XX",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_52(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "XXidXX": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_53(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "ID": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_54(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "XXerrorXX": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_55(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "ERROR": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_56(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"XXcodeXX": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_57(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"CODE": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_58(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": +32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_59(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32603, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_60(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "XXmessageXX": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_61(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "MESSAGE": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_62(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "XXNo compatible version foundXX"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_63(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "no compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_64(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "NO COMPATIBLE VERSION FOUND"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_65(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "XXjsonrpcXX": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_66(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "JSONRPC": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_67(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "XX2.0XX",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_68(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "XXidXX": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_69(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "ID": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_70(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "XXerrorXX": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_71(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "ERROR": {"code": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_72(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"XXcodeXX": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_73(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"CODE": -32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_74(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": +32601, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_75(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32602, "message": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_76(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "XXmessageXX": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_77(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "MESSAGE": "Method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_78(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "XXMethod not foundXX"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_79(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "method not found"},
        }

    async def xǁMCPServerǁhandle_request__mutmut_80(self, request: dict[str, Any]) -> Optional[dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications return no response.
        if request_id is None:
            return None

        if method == "mcp.listTools":
            return {"jsonrpc": "2.0", "id": request_id, "result": self.tool_registry.list_tools()}

        if method == "mcp.negotiateVersion":
            supported = params.get("supported", [])
            if any(v in self.supported_versions for v in supported):
                return {"jsonrpc": "2.0", "id": request_id, "result": "1.0"}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "No compatible version found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "METHOD NOT FOUND"},
        }
    
    xǁMCPServerǁhandle_request__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPServerǁhandle_request__mutmut_1': xǁMCPServerǁhandle_request__mutmut_1, 
        'xǁMCPServerǁhandle_request__mutmut_2': xǁMCPServerǁhandle_request__mutmut_2, 
        'xǁMCPServerǁhandle_request__mutmut_3': xǁMCPServerǁhandle_request__mutmut_3, 
        'xǁMCPServerǁhandle_request__mutmut_4': xǁMCPServerǁhandle_request__mutmut_4, 
        'xǁMCPServerǁhandle_request__mutmut_5': xǁMCPServerǁhandle_request__mutmut_5, 
        'xǁMCPServerǁhandle_request__mutmut_6': xǁMCPServerǁhandle_request__mutmut_6, 
        'xǁMCPServerǁhandle_request__mutmut_7': xǁMCPServerǁhandle_request__mutmut_7, 
        'xǁMCPServerǁhandle_request__mutmut_8': xǁMCPServerǁhandle_request__mutmut_8, 
        'xǁMCPServerǁhandle_request__mutmut_9': xǁMCPServerǁhandle_request__mutmut_9, 
        'xǁMCPServerǁhandle_request__mutmut_10': xǁMCPServerǁhandle_request__mutmut_10, 
        'xǁMCPServerǁhandle_request__mutmut_11': xǁMCPServerǁhandle_request__mutmut_11, 
        'xǁMCPServerǁhandle_request__mutmut_12': xǁMCPServerǁhandle_request__mutmut_12, 
        'xǁMCPServerǁhandle_request__mutmut_13': xǁMCPServerǁhandle_request__mutmut_13, 
        'xǁMCPServerǁhandle_request__mutmut_14': xǁMCPServerǁhandle_request__mutmut_14, 
        'xǁMCPServerǁhandle_request__mutmut_15': xǁMCPServerǁhandle_request__mutmut_15, 
        'xǁMCPServerǁhandle_request__mutmut_16': xǁMCPServerǁhandle_request__mutmut_16, 
        'xǁMCPServerǁhandle_request__mutmut_17': xǁMCPServerǁhandle_request__mutmut_17, 
        'xǁMCPServerǁhandle_request__mutmut_18': xǁMCPServerǁhandle_request__mutmut_18, 
        'xǁMCPServerǁhandle_request__mutmut_19': xǁMCPServerǁhandle_request__mutmut_19, 
        'xǁMCPServerǁhandle_request__mutmut_20': xǁMCPServerǁhandle_request__mutmut_20, 
        'xǁMCPServerǁhandle_request__mutmut_21': xǁMCPServerǁhandle_request__mutmut_21, 
        'xǁMCPServerǁhandle_request__mutmut_22': xǁMCPServerǁhandle_request__mutmut_22, 
        'xǁMCPServerǁhandle_request__mutmut_23': xǁMCPServerǁhandle_request__mutmut_23, 
        'xǁMCPServerǁhandle_request__mutmut_24': xǁMCPServerǁhandle_request__mutmut_24, 
        'xǁMCPServerǁhandle_request__mutmut_25': xǁMCPServerǁhandle_request__mutmut_25, 
        'xǁMCPServerǁhandle_request__mutmut_26': xǁMCPServerǁhandle_request__mutmut_26, 
        'xǁMCPServerǁhandle_request__mutmut_27': xǁMCPServerǁhandle_request__mutmut_27, 
        'xǁMCPServerǁhandle_request__mutmut_28': xǁMCPServerǁhandle_request__mutmut_28, 
        'xǁMCPServerǁhandle_request__mutmut_29': xǁMCPServerǁhandle_request__mutmut_29, 
        'xǁMCPServerǁhandle_request__mutmut_30': xǁMCPServerǁhandle_request__mutmut_30, 
        'xǁMCPServerǁhandle_request__mutmut_31': xǁMCPServerǁhandle_request__mutmut_31, 
        'xǁMCPServerǁhandle_request__mutmut_32': xǁMCPServerǁhandle_request__mutmut_32, 
        'xǁMCPServerǁhandle_request__mutmut_33': xǁMCPServerǁhandle_request__mutmut_33, 
        'xǁMCPServerǁhandle_request__mutmut_34': xǁMCPServerǁhandle_request__mutmut_34, 
        'xǁMCPServerǁhandle_request__mutmut_35': xǁMCPServerǁhandle_request__mutmut_35, 
        'xǁMCPServerǁhandle_request__mutmut_36': xǁMCPServerǁhandle_request__mutmut_36, 
        'xǁMCPServerǁhandle_request__mutmut_37': xǁMCPServerǁhandle_request__mutmut_37, 
        'xǁMCPServerǁhandle_request__mutmut_38': xǁMCPServerǁhandle_request__mutmut_38, 
        'xǁMCPServerǁhandle_request__mutmut_39': xǁMCPServerǁhandle_request__mutmut_39, 
        'xǁMCPServerǁhandle_request__mutmut_40': xǁMCPServerǁhandle_request__mutmut_40, 
        'xǁMCPServerǁhandle_request__mutmut_41': xǁMCPServerǁhandle_request__mutmut_41, 
        'xǁMCPServerǁhandle_request__mutmut_42': xǁMCPServerǁhandle_request__mutmut_42, 
        'xǁMCPServerǁhandle_request__mutmut_43': xǁMCPServerǁhandle_request__mutmut_43, 
        'xǁMCPServerǁhandle_request__mutmut_44': xǁMCPServerǁhandle_request__mutmut_44, 
        'xǁMCPServerǁhandle_request__mutmut_45': xǁMCPServerǁhandle_request__mutmut_45, 
        'xǁMCPServerǁhandle_request__mutmut_46': xǁMCPServerǁhandle_request__mutmut_46, 
        'xǁMCPServerǁhandle_request__mutmut_47': xǁMCPServerǁhandle_request__mutmut_47, 
        'xǁMCPServerǁhandle_request__mutmut_48': xǁMCPServerǁhandle_request__mutmut_48, 
        'xǁMCPServerǁhandle_request__mutmut_49': xǁMCPServerǁhandle_request__mutmut_49, 
        'xǁMCPServerǁhandle_request__mutmut_50': xǁMCPServerǁhandle_request__mutmut_50, 
        'xǁMCPServerǁhandle_request__mutmut_51': xǁMCPServerǁhandle_request__mutmut_51, 
        'xǁMCPServerǁhandle_request__mutmut_52': xǁMCPServerǁhandle_request__mutmut_52, 
        'xǁMCPServerǁhandle_request__mutmut_53': xǁMCPServerǁhandle_request__mutmut_53, 
        'xǁMCPServerǁhandle_request__mutmut_54': xǁMCPServerǁhandle_request__mutmut_54, 
        'xǁMCPServerǁhandle_request__mutmut_55': xǁMCPServerǁhandle_request__mutmut_55, 
        'xǁMCPServerǁhandle_request__mutmut_56': xǁMCPServerǁhandle_request__mutmut_56, 
        'xǁMCPServerǁhandle_request__mutmut_57': xǁMCPServerǁhandle_request__mutmut_57, 
        'xǁMCPServerǁhandle_request__mutmut_58': xǁMCPServerǁhandle_request__mutmut_58, 
        'xǁMCPServerǁhandle_request__mutmut_59': xǁMCPServerǁhandle_request__mutmut_59, 
        'xǁMCPServerǁhandle_request__mutmut_60': xǁMCPServerǁhandle_request__mutmut_60, 
        'xǁMCPServerǁhandle_request__mutmut_61': xǁMCPServerǁhandle_request__mutmut_61, 
        'xǁMCPServerǁhandle_request__mutmut_62': xǁMCPServerǁhandle_request__mutmut_62, 
        'xǁMCPServerǁhandle_request__mutmut_63': xǁMCPServerǁhandle_request__mutmut_63, 
        'xǁMCPServerǁhandle_request__mutmut_64': xǁMCPServerǁhandle_request__mutmut_64, 
        'xǁMCPServerǁhandle_request__mutmut_65': xǁMCPServerǁhandle_request__mutmut_65, 
        'xǁMCPServerǁhandle_request__mutmut_66': xǁMCPServerǁhandle_request__mutmut_66, 
        'xǁMCPServerǁhandle_request__mutmut_67': xǁMCPServerǁhandle_request__mutmut_67, 
        'xǁMCPServerǁhandle_request__mutmut_68': xǁMCPServerǁhandle_request__mutmut_68, 
        'xǁMCPServerǁhandle_request__mutmut_69': xǁMCPServerǁhandle_request__mutmut_69, 
        'xǁMCPServerǁhandle_request__mutmut_70': xǁMCPServerǁhandle_request__mutmut_70, 
        'xǁMCPServerǁhandle_request__mutmut_71': xǁMCPServerǁhandle_request__mutmut_71, 
        'xǁMCPServerǁhandle_request__mutmut_72': xǁMCPServerǁhandle_request__mutmut_72, 
        'xǁMCPServerǁhandle_request__mutmut_73': xǁMCPServerǁhandle_request__mutmut_73, 
        'xǁMCPServerǁhandle_request__mutmut_74': xǁMCPServerǁhandle_request__mutmut_74, 
        'xǁMCPServerǁhandle_request__mutmut_75': xǁMCPServerǁhandle_request__mutmut_75, 
        'xǁMCPServerǁhandle_request__mutmut_76': xǁMCPServerǁhandle_request__mutmut_76, 
        'xǁMCPServerǁhandle_request__mutmut_77': xǁMCPServerǁhandle_request__mutmut_77, 
        'xǁMCPServerǁhandle_request__mutmut_78': xǁMCPServerǁhandle_request__mutmut_78, 
        'xǁMCPServerǁhandle_request__mutmut_79': xǁMCPServerǁhandle_request__mutmut_79, 
        'xǁMCPServerǁhandle_request__mutmut_80': xǁMCPServerǁhandle_request__mutmut_80
    }
    
    def handle_request(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPServerǁhandle_request__mutmut_orig"), object.__getattribute__(self, "xǁMCPServerǁhandle_request__mutmut_mutants"), args, kwargs, self)
        return result 
    
    handle_request.__signature__ = _mutmut_signature(xǁMCPServerǁhandle_request__mutmut_orig)
    xǁMCPServerǁhandle_request__mutmut_orig.__name__ = 'xǁMCPServerǁhandle_request'


def get_app():
    from src.mcp.server.facade_fastapi import APP

    return APP


__all__ = ["MCPServer", "Tool", "ToolRegistry", "get_app"]
