"""
CLI Main - Command-line interface for Codex Ingestion Pipeline.

Provides commands for ingesting, analyzing, transforming, and verifying
Python code through the pipeline.

Author: mbaetiong
Generated: 2025-12-17

Commands:
- ingest: Create snapshot from source
- analyze: Run static+runtime analysis
- transform: Apply/propose changes
- verify: Compare baseline vs patched
- pr: Create GitHub PR
- list: List snapshots
- show: Show snapshot details
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

# Try to use typer, fall back to argparse
_TYPER_IMPORT_ERROR: Optional[str] = None
try:
    import typer

    # Verify typer is actually the real package
    if hasattr(typer, "Typer"):
        from typing import Annotated

        TYPER_AVAILABLE = True
    else:
        TYPER_AVAILABLE = False
        import argparse
except ImportError as e:
    # Store error for later reporting when main() is called
    _TYPER_IMPORT_ERROR = str(e)
    TYPER_AVAILABLE = False
    import argparse

from codex.logging.structured_logger import logger

if TYPER_AVAILABLE:
    app = typer.Typer(
        name="codex",
        help="Codex Python Ingestion Pipeline CLI",
        add_completion=False,
    )

    @app.command()
    def ingest(
        source: Annotated[str, typer.Argument(help="File path, ZIP, or Git URL")],
        manifest: Annotated[
            Optional[Path], typer.Option("--manifest", "-m", help="Manifest file path")
        ] = None,
        snapshot_id: Annotated[
            Optional[str], typer.Option("--snapshot-id", help="Custom snapshot ID")
        ] = None,
    ):
        """Ingest a Python file or repository."""
        from codex.ingest import ingest as do_ingest

        try:
            snapshot = do_ingest(source, manifest_path=manifest, snapshot_id=snapshot_id)
            typer.echo(f"✅ Created snapshot: {snapshot.snapshot_id}")
            typer.echo(f"   Location: {snapshot.snapshot_dir}")
            typer.echo(f"   Hash: {snapshot.content_hash[:16]}...")
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            typer.echo(f"❌ Error: {e}", err=True)
            raise typer.Exit(1) from e

    @app.command()
    def analyze(
        snapshot_id: Annotated[str, typer.Argument(help="Snapshot ID to analyze")],
        static_only: Annotated[
            bool, typer.Option("--static-only", help="Run only static analysis")
        ] = False,
        runtime_only: Annotated[
            bool, typer.Option("--runtime-only", help="Run only runtime analysis")
        ] = False,
    ):
        """Run analysis on a snapshot."""
        from codex.analyze.static import analyze as static_analyze

        artifacts_dir = Path("artifacts") / snapshot_id
        if not artifacts_dir.exists():
            typer.echo(f"❌ Snapshot not found: {snapshot_id}", err=True)
            raise typer.Exit(1)

        source_dir = artifacts_dir / "source"

        if not runtime_only:
            typer.echo("Running static analysis...")
            report = static_analyze(source_dir, snapshot_id)
            report.save(artifacts_dir / "static-report.json")
            typer.echo(f"✅ Static analysis complete: {len(report.files)} files")
            typer.echo(
                f"   Lint issues: {report.summary.get('lint_error_count', 0)} errors, {report.summary.get('lint_warning_count', 0)} warnings"  # noqa: E501
            )
            typer.echo(f"   Security issues: {report.summary.get('security_issue_count', 0)}")

        if not static_only:
            typer.echo("ℹ️  Runtime analysis: not implemented in this version")

    @app.command()
    def transform(
        snapshot_id: Annotated[str, typer.Argument(help="Snapshot ID to transform")],
        tier: Annotated[
            Optional[str],
            typer.Option("--tier", "-t", help="Tier to apply (A, B, or C)"),
        ] = None,
        auto: Annotated[bool, typer.Option("--auto", help="Auto-apply Tier A changes")] = False,
        dry_run: Annotated[bool, typer.Option("--dry-run", help="Don't modify files")] = True,
    ):
        """Apply transformations to a snapshot."""
        from codex.transform.transformer import Tier
        from codex.transform.transformer import transform as do_transform

        artifacts_dir = Path("artifacts") / snapshot_id
        if not artifacts_dir.exists():
            typer.echo(f"❌ Snapshot not found: {snapshot_id}", err=True)
            raise typer.Exit(1)

        source_dir = artifacts_dir / "source"

        tier_enum = None
        if tier:
            tier_enum = Tier[tier.upper()]

        typer.echo(f"Transforming snapshot {snapshot_id}...")
        result = do_transform(
            source_dir, snapshot_id, tier=tier_enum, auto_apply=auto, dry_run=dry_run
        )
        result.save(artifacts_dir / "patches")

        typer.echo("✅ Transform complete:")
        typer.echo(f"   Tier A patches: {len(result.tier_a_patches)}")
        typer.echo(f"   Tier B patches: {len(result.tier_b_patches)}")
        typer.echo(f"   Tier C suggestions: {len(result.tier_c_suggestions)}")
        if result.applied:
            typer.echo("   Changes applied to source")
        else:
            typer.echo("   Dry run - no changes applied")

    @app.command()
    def verify(
        snapshot_id: Annotated[str, typer.Argument(help="Snapshot ID to verify")],
        compare_mode: Annotated[
            bool, typer.Option("--compare", help="Run behavior comparison")
        ] = False,
        tolerance: Annotated[
            str, typer.Option("--tolerance", help="Comparison tolerance")
        ] = "strict",
    ):
        """Verify behavior preservation."""
        from codex.verify.comparator import ComparisonMode, compare

        artifacts_dir = Path("artifacts") / snapshot_id
        if not artifacts_dir.exists():
            typer.echo(f"❌ Snapshot not found: {snapshot_id}", err=True)
            raise typer.Exit(1)

        if compare_mode:
            baseline_dir = artifacts_dir / "source"
            patched_dir = (
                artifacts_dir / "patched" if (artifacts_dir / "patched").exists() else baseline_dir
            )

            mode = ComparisonMode[tolerance.upper()]
            result = compare(baseline_dir, patched_dir, mode=mode)
            result.save(artifacts_dir / "behavior-diff.json")

            status = "✅" if result.result == "pass" else "❌" if result.result == "fail" else "⚠️"
            typer.echo(f"{status} Comparison result: {result.result.upper()}")
            for comp in result.comparisons:
                typer.echo(f"   {comp.input_ref}: {comp.result}")
        else:
            typer.echo("ℹ️  Use --compare to run behavior comparison")

    @app.command("list")
    def list_snapshots(
        status: Annotated[Optional[str], typer.Option("--status", help="Filter by status")] = None,
    ):
        """List all snapshots."""
        artifacts_dir = Path("artifacts")
        if not artifacts_dir.exists():
            typer.echo("No snapshots found")
            return

        snapshots = sorted(artifacts_dir.iterdir())
        for snapshot_path in snapshots:
            if snapshot_path.is_dir():
                meta_path = snapshot_path / "snapshot-meta.json"
                if meta_path.exists():
                    with meta_path.open() as f:
                        meta = json.load(f)
                    typer.echo(f"  {meta['snapshot_id']} - {meta.get('source', 'unknown')}")
                else:
                    typer.echo(f"  {snapshot_path.name} (no metadata)")

    @app.command()
    def show(
        snapshot_id: Annotated[str, typer.Argument(help="Snapshot ID")],
        as_json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
    ):
        """Show snapshot details."""
        artifacts_dir = Path("artifacts") / snapshot_id
        if not artifacts_dir.exists():
            typer.echo(f"❌ Snapshot not found: {snapshot_id}", err=True)
            raise typer.Exit(1)

        meta_path = artifacts_dir / "snapshot-meta.json"
        if meta_path.exists():
            with meta_path.open() as f:
                meta = json.load(f)

            if as_json:
                typer.echo(json.dumps(meta, indent=2))
            else:
                typer.echo(f"Snapshot: {meta['snapshot_id']}")
                typer.echo(f"Source: {meta.get('source', 'unknown')}")
                typer.echo(f"Created: {meta.get('created_at', 'unknown')}")
                typer.echo(f"Hash: {meta.get('content_hash', 'unknown')[:16]}...")
                typer.echo(f"Files: {meta.get('file_count', 'unknown')}")
        else:
            typer.echo("No metadata available")

    @app.command("ast-view")
    def ast_view(
        source: Annotated[str, typer.Argument(help="Source file path to visualize")],
        output: Annotated[
            str, typer.Option("--output", "-o", help="Output HTML file")
        ] = "ast_report.html",
        open_browser: Annotated[
            bool, typer.Option("--open", help="Open result in browser")
        ] = False,
    ) -> None:
        """Generate HTML AST visualization report."""
        from codex.ast.graph import ASTGraph
        from codex.ast.parser import UniversalParser
        from codex.ast.visualize import HTMLVisualizer

        source_path = Path(source)
        if not source_path.exists():
            typer.echo(f"Error: source file not found: {source}", err=True)
            raise typer.Exit(code=1)

        parser = UniversalParser()
        root = parser.parse_file(source_path)
        if root is None:
            typer.echo(f"Error: failed to parse {source}", err=True)
            raise typer.Exit(code=1)

        # Flatten node tree into a list for the visualizer.
        def _flatten(node, acc) -> list:
            acc.append(node)
            for child in node.children or []:
                _flatten(child, acc)
            return acc

        nodes = _flatten(root, [])
        visualizer = HTMLVisualizer()
        visualizer.render_html(nodes, ASTGraph(), {}, output)
        if open_browser:
            import webbrowser

            webbrowser.open(f"file://{output}")
        typer.echo(f"AST report written to {output} ({len(nodes)} nodes from {source})")

    def main() -> None:
        """Main entry point."""
        # Emit typer import error warning if it occurred
        if _TYPER_IMPORT_ERROR:

            logger.error(
                f"Warning: typer import failed ({_TYPER_IMPORT_ERROR}). Using limited CLI.",
            )
        app()

else:
    # Fallback to argparse
    def main() -> None:
        """Main entry point using argparse."""
        parser = argparse.ArgumentParser(
            description="Codex Python Ingestion Pipeline CLI",
            prog="codex",
        )

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Ingest command
        ingest_parser = subparsers.add_parser("ingest", help="Ingest a Python file or repository")
        ingest_parser.add_argument("source", help="File path, ZIP, or Git URL")
        ingest_parser.add_argument("--manifest", "-m", help="Manifest file path")
        ingest_parser.add_argument("--snapshot-id", help="Custom snapshot ID")

        # Analyze command
        analyze_parser = subparsers.add_parser("analyze", help="Run analysis on a snapshot")
        analyze_parser.add_argument("snapshot_id", help="Snapshot ID to analyze")
        analyze_parser.add_argument(
            "--static-only", action="store_true", help="Run only static analysis"
        )

        # Transform command
        transform_parser = subparsers.add_parser("transform", help="Apply transformations")
        transform_parser.add_argument("snapshot_id", help="Snapshot ID to transform")
        transform_parser.add_argument("--tier", "-t", help="Tier to apply (A, B, or C)")
        transform_parser.add_argument("--auto", action="store_true", help="Auto-apply Tier A")
        transform_parser.add_argument(
            "--dry-run", action="store_true", default=True, help="Don't modify files"
        )

        # List command
        list_parser = subparsers.add_parser("list", help="List all snapshots")
        list_parser.add_argument("--status", help="Filter by status")

        # Show command
        show_parser = subparsers.add_parser("show", help="Show snapshot details")
        show_parser.add_argument("snapshot_id", help="Snapshot ID")
        show_parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        if not args.command:
            parser.print_help()
            sys.exit(1)

        logger.info(f"Command: {args.command}")
        logger.info("Note: Full CLI requires 'typer' package. Install with: pip install typer")

    app = None


if __name__ == "__main__":
    main()
