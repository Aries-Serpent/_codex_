"""
Features Module

This module provides functionality for features.

Usage:
    from cli.features import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

import logging

logger = logging.getLogger(__name__)

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from codex.logging.structured_logger import logger
from codex_ml.features.feature_store import FeatureStore
from codex_ml.features.monitoring import FeatureHealthMonitor

app = typer.Typer(help="Feature store management commands")
console = Console()


@app.command()
def list_features(
    store_path: Path = typer.Option(".codex/feature_store", help="Feature store path"),
):
    """List all registered features."""
    try:
        store = FeatureStore(store_path)
        features = store.list_features()

        if not features:
            console.logger.info("[yellow]No features registered yet[/yellow]")
            return

        console.logger.info(f"\n[bold]Registered Features ({len(features)}):[/bold]")
        for name in sorted(features):
            console.logger.info(f"  • {name}")
        console.print()
    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        console.logger.info("[red]Error: <ERROR_TYPE>[/red]")
        raise typer.Exit(1) from e


@app.command()
def check_health(
    store_path: Path = typer.Option(".codex/feature_store", help="Feature store path"),
    freshness_threshold: int = typer.Option(60, help="Freshness threshold (minutes)"),
):
    """Check health of all features."""
    try:
        store = FeatureStore(store_path)
        monitor = FeatureHealthMonitor(freshness_threshold_minutes=freshness_threshold)

        features = store.list_features()
        if not features:
            console.logger.info("[yellow]No features to check[/yellow]")
            return

        health_status = monitor.check_all_features(features)

        table = Table(title="Feature Health Status")
        table.add_column("Feature", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Freshness", justify="center")
        table.add_column("Level", justify="center")
        table.add_column("Errors", justify="right")
        table.add_column("Warnings")

        for name, status in health_status.items():
            status_emoji = "✅" if status.is_healthy else "❌"
            freshness = (
                f"{status.freshness_minutes:.1f}m"
                if status.freshness_minutes != float("inf")
                else "∞"
            )
            warnings_str = "; ".join(status.warnings) if status.warnings else ""

            # Color freshness level
            level_colors = {
                "FRESH": "[green]FRESH[/green]",
                "ACCEPTABLE": "[yellow]ACCEPTABLE[/yellow]",
                "STALE": "[orange]STALE[/orange]",
                "VERY_STALE": "[red]VERY_STALE[/red]",
                "UNKNOWN": "[dim]UNKNOWN[/dim]",
            }
            level_colored = level_colors.get(status.freshness_level, status.freshness_level)

            table.add_row(
                name,
                status_emoji,
                freshness,
                level_colored,
                str(status.error_count),
                warnings_str,
            )

        console.logger.info(table)
    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        console.logger.info("[red]Error: <ERROR_TYPE>[/red]")
        raise typer.Exit(1) from e


@app.command()
def export_metadata(
    store_path: Path = typer.Option(".codex/feature_store", help="Feature store path"),
    output: Path = typer.Option("features_metadata.json", help="Output file"),
):
    """Export feature metadata to JSON."""
    try:
        store = FeatureStore(store_path)

        metadata = {}
        for name in store.list_features():
            meta = store.get_feature_metadata(name)
            if meta:
                metadata[name] = meta.to_dict()

        with open(output, "w") as f:
            json.dump(metadata, f, indent=2)

        console.logger.info(f"✅ Exported metadata for {len(metadata)} features to {output}")
    except (IOError, OSError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        console.logger.info("[red]Error: <ERROR_TYPE>[/red]")
        raise typer.Exit(1) from e


@app.command()
def clear_cache(
    store_path: Path = typer.Option(".codex/feature_store", help="Feature store path"),
):
    """Clear feature cache."""
    try:
        store = FeatureStore(store_path)
        store.clear_cache()
        console.logger.info("✅ Feature cache cleared")
    except (IOError, OSError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        console.logger.info("[red]Error: <ERROR_TYPE>[/red]")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
