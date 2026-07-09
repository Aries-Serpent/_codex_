"""
docs_agent: Machine-Readable Documentation Infrastructure

Core module for converting documentation to JSONL format, building semantic
indexes, and providing search and MCP integration capabilities.

Authority: Lane 3 Unified Documentation Agent
Status: Task 3.2 Implementation
"""

__version__ = "1.0.0"
__author__ = "Unified Documentation Agent"

from . import (
    cli,
    document_processor,
    http_mock_server,
    mcp_bridge,
    schema_validator,
    semantic_indexer,
)

__all__ = [
    "schema_validator",
    "document_processor",
    "semantic_indexer",
    "mcp_bridge",
    "http_mock_server",
    "cli",
]
