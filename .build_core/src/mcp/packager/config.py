"""
Config Module

This module provides functionality for config.

Usage:
    from packager.config import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PackageConfig:
    name: str
    description: str = ""
    template: str = "base"
    output_dir: str = "./mcp_package"
    python_package: str = "mcp_package"
    entrypoint: str = "app.py"
    include_cli: bool = True
    include_tests: bool = True
    include_docs: bool = True
    include_serverless: bool = False
    serverless_target: Optional[str] = None
    dependencies: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    features: list[str] = field(default_factory=list)
