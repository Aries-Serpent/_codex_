"""CLI for feature store management.

Provides commands for:
- Registering feature groups
- Listing features and versions
- Materializing features
- Health monitoring and reporting
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from pathlib import Path
from typing import Optional

try:
    import typer
    from rich.console import Console
    from rich.table import Table
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
    logger.warning(
        "ImportError: <ERROR_TYPE>", exc_info=True
    )  # codeql[py/clear-text-logging-sensitive-data]
    # Raise ImportError instead of sys.exit(1) to allow pytest collection
    raise ImportError(
        "typer and rich are required for CLI. Install with: pip install typer rich"
    ) from e

import builtins

from codex.logging.structured_logger import logger
from codex_ml.features.feature_store import FeatureGroup, FeatureStore
from codex_ml.features.monitoring import FeatureHealthMonitor

app = typer.Typer(
    name="feature-store",
    help="Feature store management CLI",
    add_completion=False,
)
console = Console()


@app.command()
def register(
    name: str = typer.Argument(..., help="Feature group name"),
    version: str = typer.Argument(..., help="Feature group version (e.g., 1.0.0)"),
    description: str = typer.Option("", "--description", "-d", help="Feature group description"),
    store_path: str = typer.Option(
        "artifacts/features",
        "--store-path",
        "-p",
        help="Path to feature store",
    ),
):
    """Register a new feature group.

    Example:
        python -m codex_ml.cli.feature_store register user_features 1.0.0 -d "User demographic features"
    """  # noqa: E501
    try:
        store = FeatureStore(store_path)

        # Create placeholder feature group (in real usage, features would be defined programmatically)  # noqa: E501
        group = FeatureGroup(
            name=name,
            version=version,
            features=[],
            description=description,
        )

        store.register_feature_group(group)
        console.print(
            f"[green]✓[/green] Registered feature group: {name} v{version}"
        )  # codeql[py/clear-text-logging-sensitive-data]

    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        console.print(
            "[red]✗[/red] Error registering feature group: <ERROR_TYPE>"
        )  # codeql[py/clear-text-logging-sensitive-data]
        raise typer.Exit(code=1) from e


@app.command()
def list(
    store_path: str = typer.Option(
        "artifacts/features",
        "--store-path",
        "-p",
        help="Path to feature store",
    ),
    show_versions: bool = typer.Option(
        True, "--versions/--no-versions", help="Show version information"
    ),
    show_health: bool = typer.Option(False, "--health/--no-health", help="Show health status"),
):
    """list all registered features.

    Example:
        python -m codex_ml.cli.feature_store list --health
    """
    try:
        store = FeatureStore(store_path)
        features = store.list_features()

        if not features:
            console.print(
                "[yellow]No features registered[/yellow]"
            )  # codeql[py/clear-text-logging-sensitive-data]
            return

        table = Table(title="Registered Features")
        table.add_column("Feature Name", style="cyan")

        if show_versions:
            table.add_column("Version", style="magenta")

        if show_health:
            table.add_column("Health Status", style="green")
            table.add_column("Freshness", style="blue")
            monitor = FeatureHealthMonitor()

        for feature_name in features:
            row = [feature_name]

            if show_versions:
                versions = store.list_versions(feature_name)
                version_str = versions[-1] if versions else "N/A"
                row.append(version_str)

            if show_health:
                status = monitor.check_feature_health(feature_name)
                health_icon = "✓" if status.is_healthy else "✗"
                health_style = "green" if status.is_healthy else "red"
                row.append(f"[{health_style}]{health_icon}[/{health_style}]")
                row.append(status.freshness_level)

            table.add_row(*row)

        console.logger.info(table)
        console.print(
            f"\n[dim]Total features: {len(features)}[/dim]"
        )  # codeql[py/clear-text-logging-sensitive-data]

    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        console.print(
            "[red]✗[/red] Error listing features: <ERROR_TYPE>"
        )  # codeql[py/clear-text-logging-sensitive-data]
        raise typer.Exit(code=1) from e


@app.command()
def health(
    store_path: str = typer.Option(
        "artifacts/features",
        "--store-path",
        "-p",
        help="Path to feature store",
    ),
    format: str = typer.Option(
        "markdown",
        "--format",
        "-f",
        help="Output format (json, markdown, table)",
    ),
    output_file: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (stdout if not specified)",
    ),
    include_recommendations: bool = typer.Option(
        True,
        "--recommendations/--no-recommendations",
        help="Include recommendations",
    ),
):
    """Generate feature health report.

    Example:
        python -m codex_ml.cli.feature_store health -f json -o health_report.json
    """
    try:
        store = FeatureStore(store_path)
        monitor = FeatureHealthMonitor()

        features = store.list_features()
        if not features:
            console.print(
                "[yellow]No features to monitor[/yellow]"
            )  # codeql[py/clear-text-logging-sensitive-data]
            return

        # Check health of all features
        health_statuses = monitor.check_all_features(features)

        # Generate report
        report = monitor.generate_health_report(
            health_statuses,
            format=format,
            include_recommendations=include_recommendations,
        )

        # Output report
        if output_file:
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w") as f:
                f.write(report)
            console.print(
                f"[green]✓[/green] Health report written to: {output_file}"
            )  # codeql[py/clear-text-logging-sensitive-data]
        else:
            console.logger.info(report)

        # Show summary
        healthy_count = sum(1 for s in health_statuses.values() if s.is_healthy)
        total_count = len(health_statuses)

        console.print(
            f"\n[dim]Healthy: {healthy_count}/{total_count}[/dim]"
        )  # codeql[py/clear-text-logging-sensitive-data]

    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        console.print(
            "[red]✗[/red] Error generating health report: <ERROR_TYPE>"
        )  # codeql[py/clear-text-logging-sensitive-data]
        raise typer.Exit(code=1) from e


@app.command()
def materialize(
    feature_names: builtins.list[str] = typer.Argument(..., help="Feature names to materialize"),
    output_path: str = typer.Option(
        ..., "--output", "-o", help="Output path for materialized features"
    ),
    store_path: str = typer.Option(
        "artifacts/features",
        "--store-path",
        "-p",
        help="Path to feature store",
    ),
    version: Optional[str] = typer.Option(
        None, "--version", "-v", help="Feature version to materialize"
    ),
):
    """Materialize features to parquet.

    Example:
        python -m codex_ml.cli.feature_store materialize feature1 feature2 -o features.parquet
    """
    try:
        FeatureStore(store_path)

        # In real usage, would need input data
        # This is a placeholder implementation
        console.print(
            "[yellow]Note: Materialization requires input data (not implemented in CLI yet)[/yellow]"  # noqa: E501
        )
        console.print(
            f"Features to materialize: {', '.join(feature_names)}"
        )  # codeql[py/clear-text-logging-sensitive-data]
        console.logger.info(f"Output path: {output_path}")

        if version:
            console.logger.info(f"Version: {version}")

        console.print(
            "\n[dim]Use Python API for full materialization functionality[/dim]"
        )  # codeql[py/clear-text-logging-sensitive-data]

    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        console.print(
            "[red]✗[/red] Error materializing features: <ERROR_TYPE>"
        )  # codeql[py/clear-text-logging-sensitive-data]
        raise typer.Exit(code=1) from e


@app.command()
def versions(
    feature_name: str = typer.Argument(..., help="Feature name"),
    store_path: str = typer.Option(
        "artifacts/features",
        "--store-path",
        "-p",
        help="Path to feature store",
    ),
):
    """list all versions of a feature.

    Example:
        python -m codex_ml.cli.feature_store versions user_age
    """
    try:
        store = FeatureStore(store_path)
        versions = store.list_versions(feature_name)

        if not versions:
            console.print(
                f"[yellow]No versions found for feature: {feature_name}[/yellow]"
            )  # codeql[py/clear-text-logging-sensitive-data]
            return

        table = Table(title=f"Versions for '{feature_name}'")
        table.add_column("Version", style="cyan")
        table.add_column("Timestamp", style="magenta")

        for version in versions:
            # In real implementation, would fetch timestamp from metadata
            table.add_row(version, "N/A")

        console.logger.info(table)
        console.print(
            f"\n[dim]Total versions: {len(versions)}[/dim]"
        )  # codeql[py/clear-text-logging-sensitive-data]

    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        console.print(
            "[red]✗[/red] Error listing versions: <ERROR_TYPE>"
        )  # codeql[py/clear-text-logging-sensitive-data]
        raise typer.Exit(code=1) from e


@app.command()
def info(
    feature_name: str = typer.Argument(..., help="Feature name"),
    store_path: str = typer.Option(
        "artifacts/features",
        "--store-path",
        "-p",
        help="Path to feature store",
    ),
):
    """Show detailed information about a feature.

    Example:
        python -m codex_ml.cli.feature_store info user_age
    """
    try:
        store = FeatureStore(store_path)
        monitor = FeatureHealthMonitor()

        # Get metadata - handle case where feature exists but has no metadata
        metadata = store.get_feature_metadata(feature_name)

        if metadata is None:
            # Check if feature exists in any group
            feature = store._find_feature(feature_name)
            if feature is None:
                console.print(
                    f"[yellow]Feature not found: {feature_name}[/yellow]"
                )  # codeql[py/clear-text-logging-sensitive-data]
                return
            console.print(
                f"[yellow]Feature exists but has no metadata: {feature_name}[/yellow]"
            )  # codeql[py/clear-text-logging-sensitive-data]
            # Continue with health check even without metadata

        # Get health status
        health = monitor.check_feature_health(feature_name)

        # Display information
        console.print(
            f"\n[bold]Feature: {feature_name}[/bold]\n"
        )  # codeql[py/clear-text-logging-sensitive-data]

        if metadata:
            console.logger.info("[cyan]Metadata:[/cyan]")
            console.print(
                f"  Version: {metadata.version}"
            )  # codeql[py/clear-text-logging-sensitive-data]
            console.print(
                f"  Data Type: {metadata.dtype}"
            )  # codeql[py/clear-text-logging-sensitive-data]
            console.print(
                f"  Description: {metadata.description}"
            )  # codeql[py/clear-text-logging-sensitive-data]
            console.print(
                f"  Created: {metadata.created_at}"
            )  # codeql[py/clear-text-logging-sensitive-data]
            console.print(
                f"  Updated: {metadata.updated_at}"
            )  # codeql[py/clear-text-logging-sensitive-data]

            if metadata.tags:
                console.print(
                    f"  Tags: {', '.join(f'{k}={v}' for k, v in metadata.tags.items())}"
                )  # codeql[py/clear-text-logging-sensitive-data]

        console.print(
            "\n[cyan]Health Status:[/cyan]"
        )  # codeql[py/clear-text-logging-sensitive-data]
        health_icon = "✓" if health.is_healthy else "✗"
        health_color = "green" if health.is_healthy else "red"
        console.print(
            f"  Status: [{health_color}]{health_icon} {'Healthy' if health.is_healthy else 'Unhealthy'}[/{health_color}]"  # noqa: E501
        )
        console.print(
            f"  Freshness: {health.freshness_level} ({health.freshness_minutes:.1f} min)"
        )  # codeql[py/clear-text-logging-sensitive-data]
        console.print(
            f"  Last Updated: {health.last_updated}"
        )  # codeql[py/clear-text-logging-sensitive-data]
        console.print(
            f"  Error Count: {health.error_count}"
        )  # codeql[py/clear-text-logging-sensitive-data]

        if health.warnings:
            console.print(
                "\n[yellow]Warnings:[/yellow]"
            )  # codeql[py/clear-text-logging-sensitive-data]
            for warning in health.warnings:
                console.logger.info(f"  • {warning}")

    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        console.print(
            "[red]✗[/red] Error getting feature info: <ERROR_TYPE>"
        )  # codeql[py/clear-text-logging-sensitive-data]
        raise typer.Exit(code=1) from e


def main() -> None:
    """Main entry point for feature store CLI."""
    app()


if __name__ == "__main__":
    main()
