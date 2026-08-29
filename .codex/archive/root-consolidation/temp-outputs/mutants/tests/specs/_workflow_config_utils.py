"""
 Workflow Config Utils Module

This module provides functionality for  workflow config utils.

Usage:
    from specs._workflow_config_utils import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any


@contextmanager
def temporary_workflow_config(
    yaml_module: Any, mutator: Callable[[dict[str, Any]], None]
) -> Iterator[None]:
    cfg_path = Path(".copilot-space/workflow.yaml")
    original_text = cfg_path.read_text(encoding="utf-8")
    cfg = yaml_module.safe_load(original_text) or {}
    mutator(cfg)
    cfg_path.write_text(yaml_module.safe_dump(cfg), encoding="utf-8")
    try:
        yield
    finally:
        cfg_path.write_text(original_text, encoding="utf-8")
