"""Code audit CLI - Phase 1 implementation stub."""

import sys

import click


@click.command()
@click.option("--check-dependencies", is_flag=True, help="Check for vulnerable dependencies")
@click.option("--check-vulns", is_flag=True, help="Check for security vulnerabilities")
@click.option("--format", type=click.Choice(["json", "yaml", "html"]), default="json")
@click.option("--output", type=click.Path(), help="Output file")
def audit_main(check_dependencies: bool, check_vulns: bool, format: str, output: str):
    """Run security and quality audit.

    Examples:
        codex-audit --check-dependencies --check-vulns
        codex-audit --format html --output audit.html
    """
    click.echo("🔐 Running code audit...")

    if check_dependencies:
        click.echo("  ✓ Checking dependencies")

    if check_vulns:
        click.echo("  ✓ Checking vulnerabilities")

    # Phase 2 - Implement full audit
    click.echo("\n❌  codex-audit is not yet implemented (Phase 2 pending)", err=True)
    click.echo("See docs/REPO_ADMIN_IMPLEMENTATION_DECISIONS.md for details", err=True)
    sys.exit(1)


if __name__ == "__main__":
    audit_main()
