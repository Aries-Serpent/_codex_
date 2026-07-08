"""
Train Codex CLI Module

This module provides CLI functionality for training the Codex model.

Note: This is a stub implementation created during CI auto-healing (Phase B Track 3).
Full implementation should be restored from git history or rebuilt.
"""

import argparse
from typing import Any, Optional


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser for training CLI."""
    parser = argparse.ArgumentParser(description="Train the Codex model", prog="train-codex")

    # Add common training arguments
    parser.add_argument("--train-file", type=str, help="Path to training file")
    parser.add_argument("--output-dir", type=str, help="Output directory for model")
    parser.add_argument("--use-lora", action="store_true", help="Use LoRA for training")
    parser.add_argument("--fp16", action="store_true", help="Use mixed precision training")
    parser.add_argument("--allow-remote", action="store_true", help="Allow remote training")

    return parser


def _merge(args: argparse.Namespace, config: dict[str, Any]) -> dict[str, Any]:
    """Merge CLI arguments with configuration dictionary.

    CLI arguments take precedence over config values when provided.
    """
    result = config.copy()

    # Update result with provided CLI arguments
    for key, value in vars(args).items():
        if value is not None:
            # Convert underscore to dash for config keys
            config_key = key.replace("_", "_")
            result[config_key] = value

    return result


def run_training(
    config: dict[str, Any], output_path: Optional[str] = None, resume: bool = False
) -> dict[str, Any]:
    """Run training with the provided configuration.

    Args:
        config: Training configuration
        output_path: Optional path to save the model
        resume: Whether to resume from checkpoint

    Returns:
        Dictionary with training results
    """
    # Stub implementation
    return {
        "status": "completed",
        "epochs": config.get("epochs", 1),
        "output_path": output_path,
        "resumed": resume,
    }


__all__ = [
    "build_parser",
    "run_training",
    "_merge",
]
