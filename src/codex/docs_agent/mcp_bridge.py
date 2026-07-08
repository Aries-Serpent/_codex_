"""
MCP Bridge Module for Docs Agent

Integrates with Model Context Protocol (MCP) to expose documentation
search and retrieval as MCP tools for Copilot agents.

Authority: Lane 3 Unified Documentation Agent
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class MCPToolType(Enum):
    """MCP tool types"""

    SEARCH_DOCUMENTS = "search_documents"
    SEARCH_CODE = "search_code"
    SEARCH_ISSUES = "search_issues"
    GET_DOCUMENT = "get_document"
    GET_SECTION = "get_section"
    LIST_DOCUMENTS = "list_documents"


@dataclass
class MCPTool:
    """Represents an MCP tool"""

    name: str
    description: str
    tool_type: MCPToolType
    parameters: Dict[str, Any]
    handler: Callable


class MCPBridge:
    """Bridges Docs Agent to MCP infrastructure"""

    def __init__(self, semantic_indexer):
        """Initialize MCP bridge

        Args:
            semantic_indexer: SemanticIndexer instance
        """
        self.indexer = semantic_indexer
        self.tools = {}
        self.request_id_counter = 0

        self._register_default_tools()

    def _register_default_tools(self):
        """Register default MCP tools"""

        # Search documents tool
        self.register_tool(
            name="search_documents",
            description="Search documentation using semantic similarity",
            parameters={
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "description": "Max results", "default": 10},
                "threshold": {
                    "type": "number",
                    "description": "Similarity threshold",
                    "default": 0.0,
                },
            },
            handler=self._handle_search_documents,
        )

        # Get document tool
        self.register_tool(
            name="get_document",
            description="Retrieve specific document by ID",
            parameters={
                "document_id": {"type": "string", "description": "Document ID"},
            },
            handler=self._handle_get_document,
        )

        # List documents tool
        self.register_tool(
            name="list_documents",
            description="List all indexed documents",
            parameters={
                "limit": {"type": "integer", "description": "Max results", "default": 50},
            },
            handler=self._handle_list_documents,
        )

    def register_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable,
        tool_type: MCPToolType = MCPToolType.GET_DOCUMENT,
    ):
        """Register an MCP tool

        Args:
            name: Tool name
            description: Tool description
            parameters: Parameter schema
            handler: Handler function
            tool_type: Tool type enum
        """
        self.tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "handler": handler,
            "tool_type": tool_type,
        }
        logger.debug(f"Registered MCP tool: {name}")

    def list_tools(self) -> List[Dict[str, Any]]:
        """List all registered tools

        Returns:
            List of tool definitions
        """
        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"],
            }
            for tool in self.tools.values()
        ]

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result
        """
        self.request_id_counter += 1
        request_id = f"req-{self.request_id_counter}"

        if name not in self.tools:
            return {
                "request_id": request_id,
                "success": False,
                "error": f"Unknown tool: {name}",
            }

        tool = self.tools[name]
        handler = tool["handler"]

        try:
            result = handler(arguments)
            return {
                "request_id": request_id,
                "success": True,
                "data": result,
            }
        except Exception as e:
            logger.error(f"Tool {name} failed: {e}")
            return {
                "request_id": request_id,
                "success": False,
                "error": str(e),
            }

    def _handle_search_documents(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle document search request

        Args:
            args: Handler arguments

        Returns:
            Search results
        """
        query = args.get("query", "")
        limit = args.get("limit", 10)
        threshold = args.get("threshold", 0.0)

        if not query:
            return {"error": "Missing query parameter"}

        results = self.indexer.search(query, k=limit, threshold=threshold)

        return {
            "query": query,
            "result_count": len(results),
            "results": [
                {
                    "record_id": r.record_id,
                    "record_type": r.record_type,
                    "title": r.title,
                    "content": r.content,
                    "score": r.score,
                    "metadata": r.metadata,
                }
                for r in results
            ],
        }

    def _handle_get_document(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get document request

        Args:
            args: Handler arguments

        Returns:
            Document data
        """
        doc_id = args.get("document_id")

        if not doc_id:
            return {"error": "Missing document_id parameter"}

        if doc_id not in self.indexer.records:
            return {"error": f"Document not found: {doc_id}"}

        record = self.indexer.records[doc_id]
        return {"document": record}

    def _handle_list_documents(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list documents request

        Args:
            args: Handler arguments

        Returns:
            Document list
        """
        limit = args.get("limit", 50)

        documents = [r for r in self.indexer.records.values() if r.get("type") == "document"]

        return {
            "total": len(documents),
            "returned": min(len(documents), limit),
            "documents": documents[:limit],
        }


# MCP Protocol message types
class MCPMessageType(Enum):
    """MCP message types"""

    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


def create_mcp_message(
    message_type: MCPMessageType,
    method: str,
    params: Optional[Dict[str, Any]] = None,
    request_id: Optional[int] = None,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
) -> Dict[str, Any]:
    """Create MCP protocol message

    Args:
        message_type: Message type
        method: Method name
        params: Method parameters
        request_id: Request ID
        result: Result data
        error: Error message

    Returns:
        MCP message dictionary
    """
    message: Dict[str, Any] = {
        "jsonrpc": "2.0",
        "method": method,
    }

    if request_id is not None:
        message["id"] = request_id

    if params:
        message["params"] = params

    if result is not None:
        message["result"] = result

    if error:
        message["error"] = {"message": error}

    return message


# Utility functions and classes
