#!/usr/bin/env python3
"""
AST Analysis CLI - Command Line Interface for Codebase Analysis.

Provides commands to analyze, audit, and report on codebase quality.

Usage:
    python -m codex_ml.ast.cli analyze <path> [--format json|text]
    python -m codex_ml.ast.cli audit <path> [--baseline <file>]
    python -m codex_ml.ast.cli stats [--db <path>]
    python -m codex_ml.ast.cli export [--format json|csv] [--output <file>]
"""

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Optional

from codex.logging.structured_logger import logger
from codex_ml.ast.analysis.registry import AnalyzerRegistry
from codex_ml.ast.core.config import ASTConfig
from codex_ml.ast.storage.sqlite_storage import ASTStorage


def get_storage(db_path: Optional[str] = None) -> ASTStorage:
    """Get storage instance.

    Args:
        db_path: Optional path to database

    Returns:
        ASTStorage instance
    """
    path = Path(db_path) if db_path else Path(".codex/ast_analysis.db")
    return ASTStorage(path)


def cmd_analyze(args: argparse.Namespace) -> int:
    """Analyze a file or directory.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 for success)
    """
    target_path = Path(args.path)

    if not target_path.exists():
        logger.info(f"Error: Path does not exist: {target_path}")
        return 1

    # Initialize registry with config
    ASTConfig()
    registry = AnalyzerRegistry()

    logger.info(f"Analyzing: {target_path}")
    logger.info(f"Analyzers: {', '.join(registry.list_analyzers())}")

    # For now, show a placeholder since we don't have a parser yet
    # In a full implementation, this would parse files and run analysis
    logger.info("Note: Full parsing requires libcst/tree-sitter integration.")
    logger.info(f"Registry initialized with {len(registry)} analyzers:")

    for analyzer_type in registry.list_analyzers():
        analyzer = registry.get(analyzer_type)
        if analyzer:
            logger.info(f"  - {analyzer.get_description()}")

    if args.format == "json":
        output = {
            "path": str(target_path),
            "timestamp": datetime.now(UTC).isoformat(),
            "analyzers": registry.list_analyzers(),
            "findings": [],
            "status": "pending_parser_integration",
        }
        logger.info(json.dumps(output, indent=2))

    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    """Run full audit on a codebase.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 for success)
    """
    target_path = Path(args.path)

    if not target_path.exists():
        logger.error(f"Path does not exist: {target_path}")
        return 1

    logger.info(f"Auditing: {target_path}")
    logger.info(f"Baseline: {args.baseline or 'None'}")

    # Placeholder for audit functionality
    logger.info("Audit functionality requires full parser integration.")
    logger.info("This will:")
    logger.info("  1. Parse all Python files in the path")
    logger.info("  2. Run all registered analyzers")
    logger.info("  3. Compare against baseline if provided")
    logger.info("  4. Generate comprehensive report")

    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    """Show analysis statistics.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 for success)
    """
    try:
        storage = get_storage(args.db)
        stats = storage.get_statistics()

        logger.info("=" * 60)
        logger.info("AST ANALYSIS STATISTICS")
        logger.info("=" * 60)

        logger.info(f"Total Analyses: {stats.get('total_analyses', 0)}")
        logger.info(f"Total Findings: {stats.get('total_findings', 0)}")

        if stats.get("findings_by_severity"):
            logger.info("Findings by Severity:")
            for severity, count in sorted(stats["findings_by_severity"].items()):
                logger.info(f"  {severity}: {count}")

        if stats.get("top_finding_types"):
            logger.info("Top Finding Types:")
            for finding_type, count in stats["top_finding_types"].items():
                logger.info(f"  {finding_type}: {count}")

        if stats.get("recent_activity"):
            logger.info("Recent Activity (last 7 days):")
            for date, count in stats["recent_activity"].items():
                logger.info(f"  {date}: {count} analyses")

        return 0

    except (IOError, OSError) as e:
        type(e).__name__
        logger.error("Error getting statistics: <ERROR_TYPE>")
        return 1


def cmd_export(args: argparse.Namespace) -> int:
    """Export analysis results.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 for success)
    """
    try:
        storage = get_storage(args.db)
        findings = storage.get_findings(limit=1000)

        if args.format == "json":
            data = {
                "timestamp": datetime.now(UTC).isoformat(),
                "total": len(findings),
                "findings": [f.to_dict() for f in findings],
            }
            output = json.dumps(data, indent=2, default=str)

        elif args.format == "csv":
            import csv
            import io

            # Use csv module for proper CSV formatting
            string_buffer = io.StringIO()
            writer = csv.writer(string_buffer, quoting=csv.QUOTE_ALL)
            writer.writerow(
                [
                    "finding_id",
                    "type",
                    "severity",
                    "message",
                    "file",
                    "line",
                    "analyzer",
                ]
            )

            for f in findings:
                file_path = str(f.location.file_path) if f.location else ""
                line = f.location.line_start if f.location else ""
                writer.writerow(
                    [
                        f.finding_id,
                        f.type,
                        f.severity,
                        f.message,
                        file_path,
                        line,
                        f.analyzer,
                    ]
                )

            output = string_buffer.getvalue()

        else:
            logger.error(f"Error: Unknown format '{args.format}'")
            return 1

        if args.output:
            Path(args.output).write_text(output)
            logger.info(f"Exported {len(findings)} findings to {args.output}")
        else:
            logger.info(output)

        return 0

    except (IOError, OSError) as e:
        type(e).__name__
        logger.error("Error exporting: <ERROR_TYPE>")
        return 1


def cmd_list(args: argparse.Namespace) -> int:
    """List recent analyses.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 for success)
    """
    try:
        storage = get_storage(args.db)
        analyses = storage.list_analyses(limit=args.limit)

        if not analyses:
            logger.info("No analyses found.")
            return 0

        logger.info(f"{'ID':<20} {'File':<40} {'Findings':<10} {'Date'}")

        for analysis in analyses:
            logger.info(
                f"{analysis['analysis_id'][:18]:<20} "
                f"{analysis['file_path'][:38]:<40} "
                f"{analysis['finding_count']:<10} "
                f"{analysis['timestamp'][:19]}"
            )

        return 0

    except (IOError, OSError) as e:
        type(e).__name__
        logger.error("Error listing analyses: <ERROR_TYPE>")
        return 1


def main() -> int:
    """Main entry point for AST CLI.

    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="AST Analysis CLI - Codebase quality analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--db", help="Path to SQLite database")
    parser.add_argument("--config", help="Path to config file")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a file or directory")
    analyze_parser.add_argument("path", help="Path to analyze")
    analyze_parser.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )
    analyze_parser.set_defaults(func=cmd_analyze)

    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Run full audit")
    audit_parser.add_argument("path", help="Path to audit")
    audit_parser.add_argument("--baseline", help="Baseline file for comparison")
    audit_parser.set_defaults(func=cmd_audit)

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show statistics")
    stats_parser.set_defaults(func=cmd_stats)

    # Export command
    export_parser = subparsers.add_parser("export", help="Export findings")
    export_parser.add_argument(
        "--format", choices=["json", "csv"], default="json", help="Export format"
    )
    export_parser.add_argument("--output", help="Output file path")
    export_parser.set_defaults(func=cmd_export)

    # List command
    list_parser = subparsers.add_parser("list", help="List analyses")
    list_parser.add_argument("--limit", type=int, default=20, help="Max results")
    list_parser.set_defaults(func=cmd_list)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
