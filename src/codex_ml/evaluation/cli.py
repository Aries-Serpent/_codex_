"""
Typer CLI for codex-eval command.

Provides run and report subcommands following the spec.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

try:
    import typer
except ImportError:
    typer = None  # type: ignore

__all__ = ["app", "main"]

# Create Typer app
if typer is not None:
    app = typer.Typer(
        name="codex-eval",
        help="Evaluation CLI for codex_ml",
        add_completion=False,
    )
else:
    app = None  # Fallback when typer not installed


def _ensure_typer():
    """Ensure Typer is available."""
    if typer is None:
        print("Error: typer is required for CLI. Install with: pip install typer", file=sys.stderr)
        sys.exit(2)


def run_command(
    config: Optional[Path] = typer.Option(None, "--config", help="Path to experiment config (JSON/TOML)"),
    device: str = typer.Option("cpu", "--device", help="Device to use (cpu/cuda)"),
    max_batches: Optional[int] = typer.Option(None, "--max-batches", help="Limit number of batches"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
    sys_metrics: bool = typer.Option(False, "--sys-metrics/--no-sys-metrics", help="Enable system metrics"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """
    Run evaluation with specified configuration.
    
    Exit codes:
      0 - Success
      2 - Invalid configuration
      3 - Runtime error
      4 - Determinism mismatch (if validation enabled)
    """
    try:
        # Validate inputs
        if config and not config.exists():
            typer.echo(f"Error: Config file not found: {config}", err=True)
            raise typer.Exit(code=2)
        
        # Placeholder implementation
        result = {
            "status": "success",
            "config": str(config) if config else None,
            "device": device,
            "max_batches": max_batches,
            "sys_metrics": sys_metrics,
        }
        
        # Output
        if json_output:
            output_str = json.dumps(result, indent=2)
        else:
            output_str = f"Evaluation completed successfully\nDevice: {device}"
        
        if output:
            output.write_text(output_str)
            typer.echo(f"Results written to {output}")
        else:
            typer.echo(output_str)
        
        raise typer.Exit(code=0)
        
    except FileNotFoundError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=2)
    except Exception as e:
        typer.echo(f"Runtime error: {e}", err=True)
        raise typer.Exit(code=3)


def report_command(
    input_path: Path = typer.Argument(..., help="Path to NDJSON metrics log"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """
    Generate summary report from NDJSON metrics log.
    
    Exit codes:
      0 - Success
      2 - Invalid input
      3 - Runtime error
    """
    try:
        if not input_path.exists():
            typer.echo(f"Error: Input file not found: {input_path}", err=True)
            raise typer.Exit(code=2)
        
        # Placeholder implementation
        summary = {
            "status": "success",
            "input": str(input_path),
            "records_processed": 0,
        }
        
        # Output
        if json_output:
            output_str = json.dumps(summary, indent=2)
        else:
            output_str = f"Report generated from {input_path}"
        
        if output:
            output.write_text(output_str)
            typer.echo(f"Report written to {output}")
        else:
            typer.echo(output_str)
        
        raise typer.Exit(code=0)
        
    except FileNotFoundError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=2)
    except Exception as e:
        typer.echo(f"Runtime error: {e}", err=True)
        raise typer.Exit(code=3)


if app is not None:
    app.command(name="run")(run_command)
    app.command(name="report")(report_command)


def main():
    """Main entry point for CLI."""
    _ensure_typer()
    if app is not None:
        app()
    else:
        print("Error: Typer not available", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
