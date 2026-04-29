#!/usr/bin/env python
"""
Manage Plugins

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/manage_plugins.py [options]

    Examples:
    $ python scripts/manage_plugins.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""


import argparse
import json
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from codex_ml.plugins.entry_points import (
    EntryPointPluginRegistry,
    PluginValidator,
    discover_plugins,
)

logger = logging.getLogger(__name__)


def _safe_str(value: str) -> str:
    """Return *value* with newlines replaced so it cannot inject fake log lines."""
    return value.replace("\r", " ").replace("\n", " ")


def cmd_list(args):
    """List all discovered plugins."""
    registry = EntryPointPluginRegistry()
    discovered = registry.discover_plugins()

    print("=" * 70)
    print("DISCOVERED PLUGINS")
    print("=" * 70)

    total_count = 0
    for group, plugins in discovered.items():
        if plugins:
            print(f"\n{group}:")
            for plugin in plugins:
                status = "✓" if not plugin.error else "✗"
                version = f" (v{plugin.version})" if plugin.version else ""
                error = f" - ERROR: {plugin.error}" if plugin.error else ""
                print(f"  {status} {plugin.name}{version}{error}")
                total_count += 1

    print(f"\nTotal plugins discovered: {total_count}")
    print("=" * 70)


def cmd_discover(args):
    """Discover plugins and optionally auto-load them."""
    print("=" * 70)
    print("DISCOVERING PLUGINS")
    print("=" * 70)

    discovered = discover_plugins(auto_load=args.auto_load)

    for group, plugins in discovered.items():
        if plugins:
            print(f"\n{group} ({len(plugins)} plugins):")
            for plugin in plugins:
                status = "✓ LOADED" if plugin.loaded else "○ Discovered"
                if plugin.error:
                    status = "✗ ERROR"

                print(f"  {status} {plugin.name}")
                if plugin.version:
                    print(f"    Version: {plugin.version}")
                if plugin.description:
                    print(f"    Description: {plugin.description}")
                if plugin.error:
                    print(f"    Error: {plugin.error}")

    print("\n" + "=" * 70)
    print("DISCOVERY COMPLETE")
    print("=" * 70)


def cmd_validate(args):
    """Validate a specific plugin."""
    registry = EntryPointPluginRegistry()
    registry.discover_plugins()

    plugin_info = registry.get_plugin_info(args.group, args.plugin_name)

    if not plugin_info:
        print(f"Plugin '{_safe_str(args.plugin_name)}' not found in group '{_safe_str(args.group)}'")
        return 1

    validator = PluginValidator()
    is_valid, error = validator.validate_plugin(plugin_info)

    print("=" * 70)
    print(f"PLUGIN VALIDATION: {_safe_str(args.plugin_name)}")
    print("=" * 70)
    print(f"Group: {plugin_info.entry_point_group}")
    print(f"Module: {plugin_info.module_name}")
    print(f"Version: {plugin_info.version or 'N/A'}")
    print(f"Status: {'✓ VALID' if is_valid else '✗ INVALID'}")

    if error:
        print(f"\nError: {error}")

    if plugin_info.dependencies:
        print("\nDependencies:")
        for dep in plugin_info.dependencies:
            print(f"  - {dep}")

    print("=" * 70)
    return 0 if is_valid else 1


def cmd_info(args):
    """Show detailed information about a plugin."""
    registry = EntryPointPluginRegistry()
    registry.discover_plugins()

    plugin_info = registry.get_plugin_info(args.group, args.plugin_name)

    if not plugin_info:
        print(f"Plugin '{_safe_str(args.plugin_name)}' not found in group '{_safe_str(args.group)}'")
        return 1

    print("=" * 70)
    print(f"PLUGIN INFORMATION: {_safe_str(args.plugin_name)}")
    print("=" * 70)
    print(f"Name: {plugin_info.name}")
    print(f"Group: {plugin_info.entry_point_group}")
    print(f"Module: {plugin_info.module_name}")
    print(f"Version: {plugin_info.version or 'N/A'}")
    print(f"Description: {plugin_info.description or 'N/A'}")
    print(f"Required Codex Version: {plugin_info.required_codex_version or 'N/A'}")
    print(f"Loaded: {'Yes' if plugin_info.loaded else 'No'}")

    if plugin_info.dependencies:
        print("\nDependencies:")
        for dep in plugin_info.dependencies:
            print(f"  - {dep}")

    if plugin_info.error:
        print(f"\nError: {plugin_info.error}")

    if args.json:
        print("\nJSON Output:")
        print(
            json.dumps(
                {
                    "name": plugin_info.name,
                    "group": plugin_info.entry_point_group,
                    "module": plugin_info.module_name,
                    "version": plugin_info.version,
                    "description": plugin_info.description,
                    "dependencies": plugin_info.dependencies,
                    "required_codex_version": plugin_info.required_codex_version,
                    "loaded": plugin_info.loaded,
                    "error": plugin_info.error,
                },
                indent=2,
            )
        )

    print("=" * 70)
    return 0


def main():
    parser = argparse.ArgumentParser(description="Plugin Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # List command
    parser_list = subparsers.add_parser("list", help="List all plugins")
    parser_list.add_argument("--group", help="Filter by entry point group")

    # Discover command
    parser_discover = subparsers.add_parser("discover", help="Discover plugins")
    parser_discover.add_argument(
        "--auto-load", action="store_true", help="Automatically load valid plugins"
    )

    # Validate command
    parser_validate = subparsers.add_parser("validate", help="Validate a plugin")
    parser_validate.add_argument("plugin_name", help="Plugin name to validate")
    parser_validate.add_argument(
        "--group", default="codex_ml.plugins", help="Entry point group (default: codex_ml.plugins)"
    )

    # Info command
    parser_info = subparsers.add_parser("info", help="Show plugin information")
    parser_info.add_argument("plugin_name", help="Plugin name")
    parser_info.add_argument("--group", required=True, help="Entry point group")
    parser_info.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    try:
        if args.command == "list":
            return cmd_list(args)
        elif args.command == "discover":
            return cmd_discover(args)
        elif args.command == "validate":
            return cmd_validate(args)
        elif args.command == "info":
            return cmd_info(args)
    except Exception:
        logger.exception("Error while executing plugin management command")
        return 1


if __name__ == "__main__":
    sys.exit(main())
