"""Code analysis CLI - Phase 1 implementation stub."""

import sys

import click


@click.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("--format", type=click.Choice(["json", "yaml", "html", "csv"]), default="json")
@click.option("--output", type=click.Path(), help="Output file (default: stdout)")
@click.option("--threshold", type=int, default=50, help="Long function threshold")
def analyze_main(path: str, format: str, output: str, threshold: int):
    """Analyze code quality and generate metrics report.

    Examples:
        codex-analyze . --format html --output report.html
        codex-analyze src/ --threshold 40
    """
    click.echo(f"🔍 Analyzing code in: {path}")
    click.echo(f"📊 Format: {format}")
    click.echo(f"📏 Threshold: {threshold} lines")

    # Phase 2 - Implement full analysis
    click.echo("\n❌  codex-analyze is not yet implemented (Phase 2 pending)", err=True)
    click.echo("See docs/REPO_ADMIN_IMPLEMENTATION_DECISIONS.md for details", err=True)
    sys.exit(1)


if __name__ == "__main__":
    analyze_main()
