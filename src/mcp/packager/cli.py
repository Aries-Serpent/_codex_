"""
Cli Module

This module provides functionality for cli.

Usage:
    from packager.cli import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import argparse

from mcp.packager.generator import generate_package, load_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MCP package skeleton")
    parser.add_argument("--config", required=True, help="Path to MCP packager YAML config")
    parser.add_argument("--output", help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output = generate_package(config, output_dir=args.output)
    print(f"Generated MCP package at {output}")


if __name__ == "__main__":
    main()
