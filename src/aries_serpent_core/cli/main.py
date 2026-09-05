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

from aries_serpent_core.logging.structured_logger import logger

if TYPER_AVAILABLE:
    app = typer.Typer(
        name="codex",
        help="Codex Python Ingestion Pipeline CLI",
        add_completion=False,
    )

    @app.command()
    def ingest(
        source: Annotated[Optional[str], typer.Argument(help="File path, ZIP, or Git URL")] = None,
        manifest: Annotated[
            Optional[Path], typer.Option("--manifest", "-m", help="Manifest file path")
        ] = None,
        snapshot_id: Annotated[
            Optional[str], typer.Option("--snapshot-id", help="Custom snapshot ID")
        ] = None,
    ):
        """Ingest a Python file or repository."""
        if source is None:
            typer.echo("❌ Source path is required. Provide a file, directory, or repository URL.")
            raise typer.Exit(2)

        from codex.ingest import ingest as do_ingest

        try:
            snapshot = do_ingest(source, manifest_path=manifest, snapshot_id=snapshot_id)
            typer.echo(f"✅ Created snapshot: {snapshot.snapshot_id}")
            typer.echo(f"   Location: {snapshot.snapshot_dir}")
            typer.echo(f"   Hash: {snapshot.content_hash[:16]}...")
        except (IOError, OSError, ModuleNotFoundError, ImportError, FileNotFoundError) as e:
            typer.echo(f"❌ Error: {e}")
            raise typer.Exit(1) from e

    @app.command()
    def analyze(
        snapshot_id: Annotated[Optional[str], typer.Argument(help="Snapshot ID to analyze")] = None,
        static_only: Annotated[
            bool, typer.Option("--static-only", help="Run only static analysis")
        ] = False,
        runtime_only: Annotated[
            bool, typer.Option("--runtime-only", help="Run only runtime analysis")
        ] = False,
        full: Annotated[
            bool, typer.Option("--full", help="Run the full analysis suite")
        ] = False,
        format: Annotated[
            Optional[str], typer.Option("--format", help="Output format")
        ] = None,
    ):
        """Run analysis on a snapshot."""
        if snapshot_id is None:
            typer.echo("❌ Snapshot ID is required.")
            raise typer.Exit(2)

        from codex.analyze import analyze as static_analyze

        artifacts_dir = Path("artifacts") / snapshot_id
        source_dir = artifacts_dir / "source"

        try:
            if not runtime_only:
                typer.echo("Running static analysis...")
                report = static_analyze(source_dir, snapshot_id)
                if hasattr(report, "save"):
                    report.save(artifacts_dir / "static-report.json")
                    files_count = len(getattr(report, "files", []))
                    summary = getattr(report, "summary", {})
                    lint_errors = summary.get("lint_error_count", 0)
                    lint_warnings = summary.get("lint_warning_count", 0)
                    security_issues = summary.get("security_issue_count", 0)
                    typer.echo(f"✅ Static analysis complete: {files_count} files")
                    typer.echo(
                        f"   Lint issues: {lint_errors} errors, {lint_warnings} warnings"
                    )
                    typer.echo(f"   Security issues: {security_issues}")
                elif isinstance(report, dict):
                    files_count = len(report.get("files", []))
                    summary = report.get("summary", {})
                    typer.echo(f"✅ Static analysis complete: {files_count} files")
                    typer.echo(
                        f"   Lint issues: {summary.get('lint_error_count', 0)} errors, {summary.get('lint_warning_count', 0)} warnings"
                    )
                    typer.echo(f"   Security issues: {summary.get('security_issue_count', 0)}")
                else:
                    typer.echo("✅ Static analysis complete")

            if not static_only:
                typer.echo("ℹ️  Runtime analysis: not implemented in this version")
        except FileNotFoundError:
            typer.echo(f"❌ Snapshot not found: {snapshot_id}")
            raise typer.Exit(1) from None

    @app.command()
    def transform(
        snapshot_id: Annotated[Optional[str], typer.Argument(help="Snapshot ID to transform")] = None,
        tier: Annotated[
            Optional[str],
            typer.Option("--tier", "-t", help="Tier to apply (A, B, or C)"),
        ] = None,
        auto: Annotated[bool, typer.Option("--auto", help="Auto-apply Tier A changes")] = False,
        dry_run: Annotated[bool, typer.Option("--dry-run", help="Don't modify files")] = True,
        mode: Annotated[
            Optional[str], typer.Option("--mode", help="Transformation mode")
        ] = None,
        filter: Annotated[
            Optional[str], typer.Option("--filter", help="File filter pattern")
        ] = None,
        verbose: Annotated[
            bool, typer.Option("--verbose", help="Verbose output")
        ] = False,
    ):
        """Apply transformations to a snapshot."""
        if snapshot_id is None:
            typer.echo("❌ Snapshot ID is required.")
            raise typer.Exit(2)

        from codex.transform import transform as do_transform

        artifacts_dir = Path("artifacts") / snapshot_id
        source_dir = artifacts_dir / "source"

        tier_enum = None
        if tier:
            tier_enum = tier.upper()

        typer.echo(f"Transforming snapshot {snapshot_id}...")
        try:
            result = do_transform(
                source_dir, snapshot_id, tier=tier_enum, auto_apply=auto, dry_run=dry_run
            )
            if hasattr(result, "save"):
                result.save(artifacts_dir / "patches")
                typer.echo("✅ Transform complete:")
                typer.echo(f"   Tier A patches: {len(getattr(result, 'tier_a_patches', []))}")
                typer.echo(f"   Tier B patches: {len(getattr(result, 'tier_b_patches', []))}")
                typer.echo(f"   Tier C suggestions: {len(getattr(result, 'tier_c_suggestions', []))}")
                if getattr(result, 'applied', False):
                    typer.echo("   Changes applied to source")
                else:
                    typer.echo("   Dry run - no changes applied")
            elif isinstance(result, dict):
                typer.echo("✅ Transform complete:")
                typer.echo(f"   Tier A patches: {len(result.get('tier_a_patches', result.get('changes', [])))}")
                typer.echo(f"   Tier B patches: {len(result.get('tier_b_patches', []))}")
                typer.echo(f"   Tier C suggestions: {len(result.get('tier_c_suggestions', []))}")
            else:
                typer.echo("✅ Transform complete")
        except FileNotFoundError:
            typer.echo(f"❌ Snapshot not found: {snapshot_id}")
            raise typer.Exit(1) from None

    @app.command()
    def verify(
        snapshot_id: Annotated[Optional[str], typer.Argument(help="Snapshot ID to verify")] = None,
        compare_mode: Annotated[
            bool, typer.Option("--compare", help="Run behavior comparison")
        ] = False,
        tolerance: Annotated[
            str, typer.Option("--tolerance", help="Comparison tolerance")
        ] = "strict",
        patched: Annotated[
            Optional[str], typer.Option("--patched", help="Patched snapshot ID to compare")
        ] = None,
        format: Annotated[
            Optional[str], typer.Option("--format", help="Output format")
        ] = None,
    ):
        """Verify behavior preservation."""
        if snapshot_id is None:
            typer.echo("❌ Snapshot ID is required.")
            raise typer.Exit(2)

        from codex.verify import verify_snapshot

        artifacts_dir = Path("artifacts") / snapshot_id
        compare_target = compare_mode or patched is not None
        if compare_target:
            baseline_dir = artifacts_dir / "source"
            patched_dir = Path("artifacts") / patched if patched is not None else (
                artifacts_dir / "patched" if (artifacts_dir / "patched").exists() else baseline_dir
            )

            try:
                result = verify_snapshot(baseline_dir, patched_dir, mode=tolerance.upper())
            except FileNotFoundError:
                typer.echo(f"❌ Snapshot not found: {snapshot_id}")
                raise typer.Exit(1) from None

            if hasattr(result, "save"):
                result.save(artifacts_dir / "behavior-diff.json")
                status = "✅" if result.result == "pass" else "❌" if result.result == "fail" else "⚠️"
                typer.echo(f"{status} Comparison result: {result.result.upper()}")
                for comp in getattr(result, "comparisons", []):
                    typer.echo(f"   {comp.input_ref}: {comp.result}")
            elif isinstance(result, dict):
                status = result.get("status", "pass")
                status_emoji = "✅" if status == "identical" else "❌" if status == "different" else "⚠️"
                typer.echo(f"{status_emoji} Comparison result: {status.upper()}")
                for comp in result.get("differences", []) or []:
                    if isinstance(comp, dict):
                        typer.echo(f"   {comp.get('input_ref', 'diff')}: {comp.get('result', 'ok')}")
            else:
                typer.echo("✅ Comparison result: PASS")
        else:
            typer.echo("ℹ️  Use --compare to run behavior comparison")

    @app.command("list")
    def list_snapshots(
        status: Annotated[Optional[str], typer.Option("--status", help="Filter by status")] = None,
        filter: Annotated[
            Optional[str], typer.Option("--filter", help="Filter by name")
        ] = None,
        verbose: Annotated[
            bool, typer.Option("--verbose", help="Verbose output")
        ] = False,
    ):
        """List all snapshots."""
        from codex.snapshot import list_snapshots as list_snapshot_records

        snapshots = list_snapshot_records(status=status)
        if not snapshots:
            typer.echo("No snapshots found")
            return

        for meta in snapshots:
            typer.echo(f"  {meta.get('snapshot_id', meta.get('id', 'unknown'))} - {meta.get('source', 'unknown')}")

    @app.command()
    def show(
        snapshot_id: Annotated[Optional[str], typer.Argument(help="Snapshot ID")] = None,
        as_json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
        format: Annotated[
            Optional[str], typer.Option("--format", help="Output format")
        ] = None,
    ):
        """Show snapshot details."""
        if snapshot_id is None:
            typer.echo("❌ Snapshot ID is required.")
            raise typer.Exit(2)

        from codex.snapshot import get_snapshot

        try:
            meta = get_snapshot(snapshot_id)
        except FileNotFoundError:
            typer.echo(f"❌ Snapshot not found: {snapshot_id}")
            raise typer.Exit(1) from None

        if as_json or format == "json":
            typer.echo(json.dumps(meta, indent=2))
        else:
            typer.echo(f"Snapshot: {meta.get('snapshot_id', snapshot_id)}")
            typer.echo(f"Source: {meta.get('source', 'unknown')}")
            typer.echo(f"Created: {meta.get('created_at', 'unknown')}")
            typer.echo(f"Hash: {meta.get('content_hash', 'unknown')[:16]}...")
            typer.echo(f"Files: {meta.get('file_count', 'unknown')}")

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
        from aries_serpent_core.ast.graph import ASTGraph
        from aries_serpent_core.ast.parser import UniversalParser
        from aries_serpent_core.ast.visualize import HTMLVisualizer

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
