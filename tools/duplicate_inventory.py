#!/usr/bin/env python3
"""
Duplicate Inventory CLI

Command-line interface for comprehensive duplicate detection across the codebase.

Usage:
    python tools/duplicate_inventory.py [REPO_PATH] [OPTIONS]

Examples:
    # Scan current directory with all modes
    python tools/duplicate_inventory.py .

    # Scan with specific modes
    python tools/duplicate_inventory.py . --modes exact,normalized

    # Specify output directory
    python tools/duplicate_inventory.py . --output-dir ./dup_analysis

    # Use configuration file
    python tools/duplicate_inventory.py . --config .dupinv.yaml
"""

import argparse
import sys
from pathlib import Path


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Comprehensive duplicate detection for codebases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Positional arguments
    parser.add_argument(
        "repo_path",
        type=str,
        nargs="?",
        default=".",
        help="Path to repository root (default: current directory)",
    )

    # Detection options
    parser.add_argument(
        "--modes",
        type=str,
        default="exact",
        help="Comma-separated detection modes: exact,normalized,ast,semantic (default: exact)",
    )

    # Output options
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./duplicate_analysis",
        help="Output directory (default: ./duplicate_analysis)",
    )

    parser.add_argument(
        "--formats",
        type=str,
        default="all",
        help="Output formats: yaml,json,csv,markdown,all (default: all)",
    )

    # Configuration
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file",
    )

    # Exclusion options
    parser.add_argument(
        "--exclude",
        action="append",
        help="Exclude patterns (can be repeated)",
    )

    parser.add_argument(
        "--no-gitignore",
        action="store_true",
        help="Don't respect .gitignore",
    )

    # Display options
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Quiet mode (errors only)",
    )

    # Parse arguments
    args = parser.parse_args()

    # Validate repository path
    repo_path = Path(args.repo_path).resolve()
    if not repo_path.exists():
        print(f"Error: Repository path does not exist: {repo_path}", file=sys.stderr)
        return 1

    if not repo_path.is_dir():
        print(f"Error: Repository path is not a directory: {repo_path}", file=sys.stderr)
        return 1

    # Parse modes
    modes = [m.strip() for m in args.modes.split(",") if m.strip()]

    # Parse formats
    if args.formats == "all":
        formats = ["yaml", "json", "csv", "markdown"]
    else:
        formats = [f.strip() for f in args.formats.split(",") if f.strip()]

    # Load configuration
    config = {}
    if args.config:
        try:
            import yaml

            with open(args.config, "r") as f:
                config = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading configuration: {e}", file=sys.stderr)
            return 1

    # Update config with CLI arguments
    if args.exclude:
        config.setdefault("exclude_patterns", []).extend(args.exclude)

    if args.no_gitignore:
        config["respect_gitignore"] = False

    # Import and run scanner
    try:
        from tools.dupinv.core import DuplicateScanner

        if not args.quiet:
            print(f"Scanning repository: {repo_path}")
            print(f"Detection modes: {', '.join(modes)}")
            print(f"Output directory: {args.output_dir}")
            print()

        # Initialize scanner
        scanner = DuplicateScanner(repo_path, config)

        # Run scan
        if not args.quiet:
            print("Running scan...")

        inventory = scanner.scan(modes=modes)

        # Write outputs
        if not args.quiet:
            print(f"Found {inventory.metadata.total_groups} duplicate groups")
            print(f"Scanned {inventory.metadata.total_files_scanned} files")
            print(f"Scan duration: {inventory.metadata.scan_duration_seconds:.2f}s")
            print()
            print(f"Writing outputs to {args.output_dir}...")

        scanner.write_outputs(inventory, Path(args.output_dir), formats=formats)

        if not args.quiet:
            print("Done!")

        # Exit with appropriate code
        # 0 = success, no violations
        # 1 = success, but violations found
        return 1 if inventory.metadata.total_violations > 0 else 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
