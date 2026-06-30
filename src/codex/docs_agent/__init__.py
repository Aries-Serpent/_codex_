"""
docs_agent: Machine-Readable Documentation Infrastructure

Core module for converting documentation to JSONL format, building semantic
indexes, and providing search and MCP integration capabilities.

Authority: Lane 3 Unified Documentation Agent
Status: Task 3.2 Implementation
"""

__version__ = "1.0.0"
__author__ = "Unified Documentation Agent"

from . import schema_validator
from . import document_processor
from . import semantic_indexer
from . import mcp_bridge
from . import http_mock_server
from . import cli

__all__ = [
    "schema_validator",
    "document_processor",
    "semantic_indexer",
    "mcp_bridge",
    "http_mock_server",
    "cli",
]
