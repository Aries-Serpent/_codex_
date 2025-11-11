"""Command-line interface for AST analysis."""

from pathlib import Path
from typing import Optional

import click


@click.group()
def cli():
    """Codex AST Analysis CLI."""
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--format", "-f", type=click.Choice(["json", "text", "yaml"]), default="text")
def analyze(path: str, output: Optional[str], format: str):
    """Analyze AST for a file or directory."""
    path_obj = Path(path)
    
    if path_obj.is_file():
        click.echo(f"Analyzing file: {path_obj}")
        # TODO: Implement file analysis
    elif path_obj.is_dir():
        click.echo(f"Analyzing directory: {path_obj}")
        # TODO: Implement directory analysis
    
    click.echo("✓ Analysis complete")


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Report file path (default: audit_report.html)")
def audit(path: str, output: Optional[str]):
    """Run full codebase audit."""
    path_obj = Path(path)
    output_file = Path(output or "audit_report.html")
    
    click.echo(f"Auditing codebase: {path_obj}")
    click.echo(f"Output: {output_file}")
    
    # TODO: Implement full audit
    
    click.echo(f"✓ Audit complete: {output_file}")


@cli.command()
@click.argument("commit1", type=str)
@click.argument("commit2", type=str)
@click.option("--metric", "-m", type=str, default="complexity")
def diff(commit1: str, commit2: str, metric: str):
    """Compare AST metrics between two commits."""
    click.echo(f"Comparing {commit1}..{commit2}")
    click.echo(f"Metric: {metric}")
    
    # TODO: Implement commit diff
    
    click.echo("✓ Diff complete")


if __name__ == "__main__":
    cli()
