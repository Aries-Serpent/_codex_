"""
Command-line interface for parsing and querying AST structures.

Provides commands to parse source files, extract statistics, and query
specific node types across Python, YAML, JSON, and SQL languages.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Optional

from codex.ast_adapters import (
    JSONASTAdapter,
    PythonASTAdapter,
    SQLASTAdapter,
    YAMLASTAdapter,
)

logger = logging.getLogger(__name__)


def get_adapter(language: str) -> Any:
    """Get the appropriate adapter for the specified language.

    Args:
        language: Language identifier (python, yaml, json, sql)

    Returns:
        Configured AST adapter instance

    Raises:
        ValueError: If language is not supported
    """
    adapters = {
        "python": PythonASTAdapter,
        "yaml": YAMLASTAdapter,
        "json": JSONASTAdapter,
        "sql": SQLASTAdapter,
    }

    if language not in adapters:
        raise ValueError(
            f"Unsupported language: {language}. Supported languages: {', '.join(adapters.keys())}"
        )

    return adapters[language]()


def parse_command(args) -> int:
    """Parse a file and output the AST as JSON.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        file_path = Path(args.file)
        if not file_path.exists():
            logger.error(f"Error: File not found: {file_path}")
            return 1

        adapter = get_adapter(args.language)
        root = adapter.parse_file(str(file_path))

        # Convert AST to dictionary representation
        ast_dict = root.to_dict()

        # Output as formatted JSON
        logger.info(json.dumps(ast_dict, indent=2))
        return 0

    except (IOError, OSError) as e:
        type(e).__name__
        logger.error("Error parsing file: <ERROR_TYPE>")
        return 1


def stats_command(args) -> int:
    """Parse a file and output statistics about the AST.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        file_path = Path(args.file)
        if not file_path.exists():
            logger.error(f"Error: File not found: {file_path}")
            return 1

        adapter = get_adapter(args.language)
        adapter.parse_file(str(file_path))

        # Get statistics
        stats = adapter.get_stats()

        # Output as formatted JSON
        logger.info(json.dumps(stats, indent=2))
        return 0

    except (IOError, OSError) as e:
        type(e).__name__
        logger.error("Error getting statistics: <ERROR_TYPE>")
        return 1


def query_command(args) -> int:
    """Parse a file and query for specific node types.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        file_path = Path(args.file)
        if not file_path.exists():
            logger.error(f"Error: File not found: {file_path}")
            return 1

        adapter = get_adapter(args.language)
        adapter.parse_file(str(file_path))

        # Query for nodes
        nodes = adapter.find_nodes_by_type(args.type)

        # Build result list
        result = []
        for node in nodes:
            node_info = {
                "type": node.node_type,
                "name": node.name,
                "line_start": node.line_start,
                "line_end": node.line_end,
                "column_start": node.column_start,
                "column_end": node.column_end,
            }
            # Add metadata if requested
            if args.metadata:
                node_info["metadata"] = node.metadata
            result.append(node_info)

        # Output as formatted JSON
        logger.info(json.dumps(result, indent=2))
        return 0

    except (IOError, OSError) as e:
        type(e).__name__
        logger.error("Error querying nodes: <ERROR_TYPE>")
        return 1


def main(argv: Optional[list[Any]] = None) -> int:
    """Main entry point for the CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv)

    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        prog="codex_ast",
        description="Parse and query AST structures across multiple languages",
        epilog="Supported languages: python, yaml, json, sql",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Parse command
    parse_parser = subparsers.add_parser("parse", help="Parse a file and output the AST as JSON")
    parse_parser.add_argument("file", help="Path to the file to parse")
    parse_parser.add_argument(
        "-l",
        "--language",
        required=True,
        choices=["python", "yaml", "json", "sql"],
        help="Source language",
    )

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Parse a file and output statistics")
    stats_parser.add_argument("file", help="Path to the file to parse")
    stats_parser.add_argument(
        "-l",
        "--language",
        required=True,
        choices=["python", "yaml", "json", "sql"],
        help="Source language",
    )

    # Query command
    query_parser = subparsers.add_parser("query", help="Query for specific node types")
    query_parser.add_argument("file", help="Path to the file to parse")
    query_parser.add_argument(
        "-l",
        "--language",
        required=True,
        choices=["python", "yaml", "json", "sql"],
        help="Source language",
    )
    query_parser.add_argument(
        "-t",
        "--type",
        required=True,
        help="Node type to query (e.g., function, class, mapping)",
    )
    query_parser.add_argument(
        "-m", "--metadata", action="store_true", help="Include metadata in output"
    )

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    # Dispatch to command handler
    if args.command == "parse":
        return parse_command(args)
    if args.command == "stats":
        return stats_command(args)
    if args.command == "query":
        return query_command(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
