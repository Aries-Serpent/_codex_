"""
RAG CLI Commands for Autonomous Index Management

Provides comprehensive command-line interface for RAG operations including:
- Building and querying indices
- Tenant management
- Statistics and metrics export
- Index operations (list, delete, merge)

Integrates with the core RAG pipeline in src/codex/rag/
"""

import json
import logging
from pathlib import Path
from typing import Any, Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

logger = logging.getLogger(__name__)

# Re-export RAGIndexer so tests can patch codex.cli_rag.RAGIndexer
try:
    from codex.rag.indexer import RAGIndexer
except ImportError:  # pragma: no cover - optional dependency

    class RAGIndexer:  # type: ignore[no-redef]
        """Stub when codex.rag is not installed."""

        def __init__(self, *args, **kwargs) -> None:
            raise ImportError(
                "RAGIndexer requires codex.rag extras. Install with: pip install -e '.[rag]'"
            )


# Re-export RAGRetriever (alias for Retriever) so tests can patch
# codex.cli_rag.RAGRetriever and query() picks up the patched class.
try:
    from codex.rag.retriever import Retriever as RAGRetriever
except ImportError:  # pragma: no cover - optional dependency

    class RAGRetriever:  # type: ignore[no-redef]
        """Stub when codex.rag is not installed."""

        def __init__(self, *args, **kwargs) -> None:
            raise ImportError(
                "RAGRetriever requires codex.rag extras. Install with: pip install -e '.[rag]'"
            )


__all__ = ["RAGIndexer", "RAGRetriever", "app"]

# Create Typer app for RAG commands
app = typer.Typer(
    name="rag",
    help="RAG (Retrieval-Augmented Generation) index management and querying",
    no_args_is_help=True,
)

console = Console()


def _validate_files(files: list[str]) -> list[Path]:
    """
    Validate and resolve file patterns to actual paths.

    Args:
        files: List of file patterns (supports glob patterns)

    Returns:
        List of resolved Path objects

    Raises:
        typer.BadParameter: If no valid files found
    """
    from glob import glob

    resolved: list[Any] = []
    for pattern in files:
        matches = glob(pattern, recursive=True)
        if not matches:
            console.print(
                f"[yellow]⚠️  No files found matching: {pattern}[/yellow]"
            )  # codeql[py/clear-text-logging-sensitive-data]
        else:
            resolved.extend(Path(m) for m in matches)

    if not resolved:
        raise typer.BadParameter("No valid files found matching the provided patterns")

    return resolved


def _format_bytes(size_bytes: int) -> str:
    """Format byte size to human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0  # type: ignore[assignment]
    return f"{size_bytes:.2f} TB"


@app.command("build")
def build(
    files: list[str] = typer.Option(
        ...,
        "--files",
        "-f",
        help="File patterns to index (supports glob, e.g., 'docs/**/*.md')",
    ),
    index_name: str = typer.Option(
        "default",
        "--index-name",
        "-i",
        help="Name for the index",
    ),
    tenant_id: str = typer.Option(
        "default",
        "--tenant-id",
        "-t",
        help="Tenant identifier for multi-tenancy",
    ),
    chunk_size: int = typer.Option(
        1000,
        "--chunk-size",
        "-c",
        help="Maximum chunk size in characters",
        min=100,
        max=10000,
    ),
    overlap: int = typer.Option(
        128,
        "--overlap",
        "-o",
        help="Overlap between chunks in characters",
        min=0,
    ),
    model_name: str = typer.Option(
        "sentence-transformers/all-MiniLM-L6-v2",
        "--model",
        "-m",
        help="Embedding model name",
    ),
) -> None:
    """
    Build a FAISS index from files for semantic search.

    This command:
    1. Reads and chunks text from specified files
    2. Generates embeddings using the specified model
    3. Creates a FAISS index for fast similarity search
    4. Persists index and metadata to disk

    Examples:
        # Index all markdown files
        codex rag build --files "docs/**/*.md" --index-name docs

        # Index Python source code
        codex rag build --files "src/**/*.py" --index-name code --chunk-size 1500

        # Multi-tenant setup
        codex rag build --files "docs/**/*.md" --tenant-id customer_a --index-name docs
    """
    try:
        from codex.rag import build_index_from_files

        # Validate inputs
        if overlap >= chunk_size:
            console.print(
                "[red]❌ Overlap must be less than chunk size[/red]"
            )  # codeql[py/clear-text-logging-sensitive-data]
            raise typer.Exit(1)

        resolved_files = _validate_files(files)

        console.print(
            f"[cyan]📚 Building index '{index_name}' for tenant '{tenant_id}'[/cyan]"
        )  # codeql[py/clear-text-logging-sensitive-data]
        console.print(
            f"[dim]   Files: {len(resolved_files)}[/dim]"
        )  # codeql[py/clear-text-logging-sensitive-data]
        console.print(
            f"[dim]   Chunk size: {chunk_size}, Overlap: {overlap}[/dim]"
        )  # codeql[py/clear-text-logging-sensitive-data]
        console.print(
            f"[dim]   Model: {model_name}[/dim]\n"
        )  # codeql[py/clear-text-logging-sensitive-data]

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Building index...", total=None)

            index_path = build_index_from_files(
                files=resolved_files,
                index_name=index_name,
                tenant_id=tenant_id,
                chunk_size=chunk_size,
                overlap=overlap,
            )

            progress.update(task, completed=True)

        console.print(
            "\n[green]✅ Index built successfully![/green]"
        )  # codeql[py/clear-text-logging-sensitive-data]
        console.print(
            f"[dim]   Location: {index_path}[/dim]"
        )  # codeql[py/clear-text-logging-sensitive-data]

    except ImportError as e:
        type(e).__name__
        console.print(
            "[red]❌ Missing dependencies: <ERROR_TYPE>[/red]"
        )  # codeql[py/clear-text-logging-sensitive-data]
        console.print(
            "[yellow]Install with: pip install sentence-transformers faiss-cpu[/yellow]"
        )  # codeql[py/clear-text-logging-sensitive-data]
        raise typer.Exit(1) from e
    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        console.print(
            "[red]❌ Failed to build index: <ERROR_TYPE>[/red]"
        )  # codeql[py/clear-text-logging-sensitive-data]
        logger.exception("Error building index")  # codeql[py/clear-text-logging-sensitive-data]
        raise typer.Exit(1) from e


@app.command("query")
def query(
    query_text: str = typer.Argument(
        ...,
        help="Query text for semantic search",
    ),
    index_name: str = typer.Option(
        "default",
        "--index-name",
        "-i",
        help="Name of the index to query",
    ),
    tenant_id: str = typer.Option(
        "default",
        "--tenant-id",
        "-t",
        help="Tenant identifier",
    ),
    top_k: int = typer.Option(
        5,
        "--top-k",
        "-k",
        help="Number of results to return",
        min=1,
        max=100,
    ),
    min_score: float = typer.Option(
        0.0,
        "--min-score",
        "-s",
        help="Minimum similarity score (0.0-1.0)",
        min=0.0,
        max=1.0,
    ),
    output_format: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format",
    ),
) -> None:
    """
    Query an existing FAISS index with semantic search.

    Returns the top-k most similar chunks with provenance information
    (file paths, line numbers, similarity scores).

    Examples:
        # Basic query
        codex rag query "authentication implementation"

        # Query specific index with more results
        codex rag query "error handling" --index-name code --top-k 10

        # Filter by minimum score
        codex rag query "API endpoints" --min-score 0.7

        # JSON output for programmatic use
        codex rag query "logging" --format json
    """
    try:
        console.print(
            f"[cyan]🔍 Querying index '{index_name}' for tenant '{tenant_id}'[/cyan]\n"
        )  # codeql[py/clear-text-logging-sensitive-data]

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Loading index...", total=None)

            retriever = RAGRetriever(
                index_name=index_name,
                tenant_id=tenant_id,
            )

            progress.update(task, description="Searching...")

            results = retriever.query(
                query_text=query_text,
                top_k=top_k,
                min_score=min_score,
            )

            progress.update(task, completed=True)

        if not results:
            console.print(
                "[yellow]No results found[/yellow]"
            )  # codeql[py/clear-text-logging-sensitive-data]
            return

        console.print(
            f"\n[green]Found {len(results)} results:[/green]\n"
        )  # codeql[py/clear-text-logging-sensitive-data]

        if output_format == "json":
            logger.info(
                json.dumps(results, indent=2, default=str)
            )  # codeql[py/clear-text-logging-sensitive-data]
        else:
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Score", style="green", width=8)
            table.add_column("File", style="blue")
            table.add_column("Text", style="white")

            for result in results:
                score = result.get("score", 0.0)
                file_path = result.get("file", "unknown")
                text = result.get("text", "")

                # Truncate text for display
                display_text = text[:100] + "..." if len(text) > 100 else text

                table.add_row(
                    f"{score:.4f}",
                    str(file_path),
                    display_text,
                )

            console.print(table)  # codeql[py/clear-text-logging-sensitive-data]

    except FileNotFoundError as err:
        console.print(
            f"[red]❌ Index '{index_name}' not found for tenant '{tenant_id}'[/red]"
        )  # codeql[py/clear-text-logging-sensitive-data]
        console.print(
            "[yellow]Build an index first with: codex rag build[/yellow]"
        )  # codeql[py/clear-text-logging-sensitive-data]
        raise typer.Exit(1) from err
    except ImportError as e:
        type(e).__name__
        console.print(
            "[red]❌ Missing dependencies: <ERROR_TYPE>[/red]"
        )  # codeql[py/clear-text-logging-sensitive-data]
        raise typer.Exit(1) from e
    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        console.print(
            "[red]❌ Query failed: <ERROR_TYPE>[/red]"
        )  # codeql[py/clear-text-logging-sensitive-data]
        logger.exception("Error querying index")  # codeql[py/clear-text-logging-sensitive-data]
        raise typer.Exit(1) from e


@app.command("list")
def list_indices(
    tenant_id: str = typer.Option(
        "default",
        "--tenant-id",
        "-t",
        help="Tenant identifier",
    ),
    index_dir: str = typer.Option(
        ".codex/tenants",
        "--index-dir",
        "-d",
        help="Base directory for indices",
    ),
) -> None:
    """
    List all indices for a tenant.

    Displays index names, number of chunks, size, and creation time.

    Examples:
        # List default tenant indices
        codex rag list

        # List specific tenant indices
        codex rag list --tenant-id customer_a
    """
    try:
        tenant_path = Path(index_dir) / tenant_id

        if not tenant_path.exists():
            console.print(
                f"[yellow]No indices found for tenant '{tenant_id}'[/yellow]"
            )  # codeql[py/clear-text-logging-sensitive-data]
            console.print(
                f"[dim]   Path: {tenant_path}[/dim]"
            )  # codeql[py/clear-text-logging-sensitive-data]
            return

        indices = []
        for index_path in tenant_path.iterdir():
            if index_path.is_dir():
                metadata_file = index_path / "metadata.json"
                if metadata_file.exists():
                    try:
                        metadata = json.loads(metadata_file.read_text())
                        indices.append(
                            {
                                "name": index_path.name,
                                "chunks": metadata.get("num_chunks", 0),
                                "created": metadata.get("created_at", "unknown"),
                                "model": metadata.get("model_name", "unknown"),
                                "path": index_path,
                            }
                        )
                    except (IOError, OSError) as e:
                        type(e).__name__
                        logger.warning(
                            f"Failed to read metadata for {index_path}: <ERROR_TYPE>"
                        )  # codeql[py/clear-text-logging-sensitive-data]

        if not indices:
            console.print(
                f"[yellow]No valid indices found for tenant '{tenant_id}'[/yellow]"
            )  # codeql[py/clear-text-logging-sensitive-data]
            return

        console.print(
            f"[cyan]📋 Indices for tenant '{tenant_id}':[/cyan]\n"
        )  # codeql[py/clear-text-logging-sensitive-data]

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Index Name", style="blue")
        table.add_column("Chunks", style="green", justify="right")
        table.add_column("Model", style="yellow")
        table.add_column("Created", style="dim")

        for idx in indices:
            table.add_row(
                idx["name"],
                str(idx["chunks"]),
                idx["model"],
                idx["created"],
            )

        console.print(table)  # codeql[py/clear-text-logging-sensitive-data]
        console.print(
            f"\n[dim]Total: {len(indices)} indices[/dim]"
        )  # codeql[py/clear-text-logging-sensitive-data]

    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        console.print(
            "[red]❌ Failed to list indices: <ERROR_TYPE>[/red]"
        )  # codeql[py/clear-text-logging-sensitive-data]
        logger.exception("Error listing indices")  # codeql[py/clear-text-logging-sensitive-data]
        raise typer.Exit(1) from e


@app.command("delete")
def delete(
    index_name: str = typer.Option(
        ...,
        "--index-name",
        "-i",
        help="Name of the index to delete",
    ),
    tenant_id: str = typer.Option(
        "default",
        "--tenant-id",
        "-t",
        help="Tenant identifier",
    ),
    index_dir: str = typer.Option(
        ".codex/tenants",
        "--index-dir",
        "-d",
        help="Base directory for indices",
    ),
    confirm: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation prompt",
    ),
) -> None:
    """
    Delete an index.

    This operation is irreversible. Use with caution.

    Examples:
        # Delete with confirmation
        codex rag delete --index-name old_index

        # Delete without confirmation
        codex rag delete --index-name old_index --yes
    """
    try:
        import shutil

        index_path = Path(index_dir) / tenant_id / index_name

        if not index_path.exists():
            console.print(
                f"[red]❌ Index '{index_name}' not found for tenant '{tenant_id}'[/red]"
            )  # codeql[py/clear-text-logging-sensitive-data]
            raise typer.Exit(1)

        if not confirm:
            confirmed = typer.confirm(
                f"Are you sure you want to delete index '{index_name}' for tenant '{tenant_id}'?",
                default=False,
            )
            if not confirmed:
                console.print(
                    "[yellow]Cancelled[/yellow]"
                )  # codeql[py/clear-text-logging-sensitive-data]
                return

        shutil.rmtree(index_path)
        console.print(
            f"[green]✅ Deleted index '{index_name}' for tenant '{tenant_id}'[/green]"
        )  # codeql[py/clear-text-logging-sensitive-data]

    except (IOError, OSError) as e:
        type(e).__name__
        console.print(
            "[red]❌ Failed to delete index: <ERROR_TYPE>[/red]"
        )  # codeql[py/clear-text-logging-sensitive-data]
        logger.exception("Error deleting index")  # codeql[py/clear-text-logging-sensitive-data]
        raise typer.Exit(1) from e


@app.command("merge")
def merge(
    source_indices: list[str] = typer.Option(
        ...,
        "--source",
        "-s",
        help="Source index names to merge",
    ),
    target_index: str = typer.Option(
        ...,
        "--target",
        "-t",
        help="Target index name",
    ),
    tenant_id: str = typer.Option(
        "default",
        "--tenant-id",
        help="Tenant identifier",
    ),
) -> None:
    """
    Merge multiple indices into a single index.

    Combines embeddings and metadata from multiple source indices into
    a new target index. Source indices remain unchanged.

    Examples:
        # Merge documentation and code indices
        codex rag merge --source docs --source code --target all

        # Multi-tenant merge
        codex rag merge --source idx1 --source idx2 --target combined --tenant-id customer_a
    """
    try:
        from codex.rag import IndexOperation, manage_tenant_indices

        if not source_indices or len(source_indices) < 2:
            console.print(
                "[red]❌ At least 2 source indices required for merge[/red]"
            )  # codeql[py/clear-text-logging-sensitive-data]
            raise typer.Exit(1)

        console.print(
            f"[cyan]🔀 Merging {len(source_indices)} indices into '{target_index}'[/cyan]\n"
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Merging indices...", total=None)

            result = manage_tenant_indices(
                tenant_id=tenant_id,
                operation=IndexOperation.MERGE,
                index_names=source_indices,
                merge_name=target_index,
            )

            progress.update(task, completed=True)

        if result.success:
            console.print(
                "\n[green]✅ Indices merged successfully![/green]"
            )  # codeql[py/clear-text-logging-sensitive-data]
            console.print(
                f"[dim]   Target: {target_index}[/dim]"
            )  # codeql[py/clear-text-logging-sensitive-data]
            if result.details and "chunks_count" in result.details:
                console.print(
                    f"[dim]   Total chunks: {result.details['chunks_count']}[/dim]"
                )  # codeql[py/clear-text-logging-sensitive-data]
        else:
            console.print(
                f"[red]❌ Merge failed: {result.message}[/red]"
            )  # codeql[py/clear-text-logging-sensitive-data]
            raise typer.Exit(1)

    except ImportError as e:
        type(e).__name__
        console.print(
            "[red]❌ Missing dependencies: <ERROR_TYPE>[/red]"
        )  # codeql[py/clear-text-logging-sensitive-data]
        raise typer.Exit(1) from e
    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        console.print(
            "[red]❌ Merge failed: <ERROR_TYPE>[/red]"
        )  # codeql[py/clear-text-logging-sensitive-data]
        logger.exception("Error merging indices")  # codeql[py/clear-text-logging-sensitive-data]
        raise typer.Exit(1) from e


@app.command("stats")
def stats(
    index_name: str = typer.Option(
        "default",
        "--index-name",
        "-i",
        help="Name of the index",
    ),
    tenant_id: str = typer.Option(
        "default",
        "--tenant-id",
        "-t",
        help="Tenant identifier",
    ),
    index_dir: str = typer.Option(
        ".codex/tenants",
        "--index-dir",
        "-d",
        help="Base directory for indices",
    ),
) -> None:
    """
    Show detailed statistics for an index.

    Displays:
    - Number of chunks
    - Embedding dimension
    - Total size on disk
    - Model information
    - Creation timestamp

    Examples:
        # Show stats for default index
        codex rag stats

        # Show stats for specific index
        codex rag stats --index-name docs --tenant-id customer_a
    """
    try:
        index_path = Path(index_dir) / tenant_id / index_name

        if not index_path.exists():
            console.print(
                f"[red]❌ Index '{index_name}' not found for tenant '{tenant_id}'[/red]"
            )  # codeql[py/clear-text-logging-sensitive-data]
            raise typer.Exit(1)

        # Read metadata
        metadata_file = index_path / "metadata.json"
        if not metadata_file.exists():
            console.print(
                "[red]❌ Index metadata not found[/red]"
            )  # codeql[py/clear-text-logging-sensitive-data]
            raise typer.Exit(1)

        metadata = json.loads(metadata_file.read_text())

        # Calculate directory size
        total_size = sum(f.stat().st_size for f in index_path.rglob("*") if f.is_file())

        console.print(
            f"[cyan]📊 Statistics for index '{index_name}' (tenant: {tenant_id})[/cyan]\n"
        )

        table = Table(show_header=False, box=None)
        table.add_column("Property", style="bold blue")
        table.add_column("Value", style="white")

        table.add_row("Index Name", index_name)
        table.add_row("Tenant ID", tenant_id)
        table.add_row("Chunks", str(metadata.get("num_chunks", 0)))
        table.add_row("Embedding Dimension", str(metadata.get("embedding_dim", "unknown")))
        table.add_row("Model", metadata.get("model_name", "unknown"))
        table.add_row("Size", _format_bytes(total_size))
        table.add_row("Created", metadata.get("created_at", "unknown"))
        table.add_row("Location", str(index_path))

        console.print(table)  # codeql[py/clear-text-logging-sensitive-data]

    except (IOError, OSError) as e:
        type(e).__name__
        console.print(
            "[red]❌ Failed to get stats: <ERROR_TYPE>[/red]"
        )  # codeql[py/clear-text-logging-sensitive-data]
        logger.exception("Error getting stats")  # codeql[py/clear-text-logging-sensitive-data]
        raise typer.Exit(1) from e


@app.command("metrics")
def metrics(
    output_format: str = typer.Option(
        "prometheus",
        "--format",
        "-f",
        help="Output format (prometheus or json)",
    ),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (default: stdout)",
    ),
) -> None:
    """
    Export RAG metrics for monitoring.

    Supports Prometheus and JSON formats for integration with
    monitoring systems like Grafana, CloudWatch, etc.

    Examples:
        # Export to stdout
        codex rag metrics

        # Export to file
        codex rag metrics --output metrics.txt

        # JSON format
        codex rag metrics --format json --output metrics.json
    """
    try:
        from codex.rag import get_metrics

        metrics_obj = get_metrics()

        if output_format == "prometheus":
            content = metrics_obj.export_prometheus()
        elif output_format == "json":
            stats = metrics_obj.get_statistics()
            content = json.dumps(stats, indent=2, default=str)
        else:
            console.print(
                f"[red]❌ Unknown format: {output_format}[/red]"
            )  # codeql[py/clear-text-logging-sensitive-data]
            raise typer.Exit(1)

        if output_file:
            output_file.write_text(content)
            console.print(
                f"[green]✅ Metrics exported to {output_file}[/green]"
            )  # codeql[py/clear-text-logging-sensitive-data]
        else:
            logger.info(content)

    except ImportError as e:
        type(e).__name__
        console.print(
            "[red]❌ Missing dependencies: <ERROR_TYPE>[/red]"
        )  # codeql[py/clear-text-logging-sensitive-data]
        raise typer.Exit(1) from e
    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        console.print(
            "[red]❌ Failed to export metrics: <ERROR_TYPE>[/red]"
        )  # codeql[py/clear-text-logging-sensitive-data]
        logger.exception("Error exporting metrics")  # codeql[py/clear-text-logging-sensitive-data]
        raise typer.Exit(1) from e


@app.command()
def benchmark(
    benchmark_type: str = typer.Option(
        "all",
        "--type",
        "-t",
        help="Benchmark type: embedding, indexing, retrieval, e2e, all",
    ),
    corpus_size: Optional[int] = typer.Option(
        None,
        "--corpus-size",
        "-c",
        help="Corpus size for benchmarks (defaults vary by type)",
    ),
    runs: int = typer.Option(5, "--runs", "-r", help="Number of runs per benchmark"),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file for results (JSON or CSV)"
    ),
    baseline: Optional[str] = typer.Option(
        None, "--baseline", "-b", help="Baseline JSON file for regression detection"
    ),
    threshold: float = typer.Option(10.0, "--threshold", help="Regression threshold percentage"),
):
    """
    Run performance benchmarks on RAG pipeline.

    Benchmark types:
    - embedding: Test embedding provider latency and throughput
    - indexing: Test indexing performance with various corpus sizes
    - retrieval: Test query latency and accuracy
    - e2e: Test complete end-to-end pipeline
    - all: Run all benchmarks
    """
    try:
        from codex.rag.benchmarks import (
            benchmark_e2e_pipeline,
            benchmark_embedding_providers,
            benchmark_indexing,
            benchmark_retrieval,
        )

        console.print(
            f"[bold blue]🔬 Running {benchmark_type} benchmarks...[/bold blue]"
        )  # codeql[py/clear-text-logging-sensitive-data]

        results = []

        if benchmark_type in ["embedding", "all"]:
            console.print(
                "[cyan]→ Benchmarking embedding providers...[/cyan]"
            )  # codeql[py/clear-text-logging-sensitive-data]
            result = benchmark_embedding_providers(runs=runs)
            results.extend(result["results"])

        if benchmark_type in ["indexing", "all"]:
            console.print(
                "[cyan]→ Benchmarking indexing performance...[/cyan]"
            )  # codeql[py/clear-text-logging-sensitive-data]
            corpus_sizes = [corpus_size] if corpus_size else [100, 1000, 10000]
            result = benchmark_indexing(corpus_sizes=corpus_sizes, runs=runs)
            results.extend(result["results"])

        if benchmark_type in ["retrieval", "all"]:
            console.print(
                "[cyan]→ Benchmarking retrieval performance...[/cyan]"
            )  # codeql[py/clear-text-logging-sensitive-data]
            index_sizes = [corpus_size] if corpus_size else [100, 1000, 10000]
            result = benchmark_retrieval(index_sizes=index_sizes, runs=runs)
            results.extend(result["results"])

        if benchmark_type in ["e2e", "all"]:
            console.print(
                "[cyan]→ Benchmarking end-to-end pipeline...[/cyan]"
            )  # codeql[py/clear-text-logging-sensitive-data]
            corpus_sizes = [corpus_size] if corpus_size else [100, 1000]
            result = benchmark_e2e_pipeline(corpus_sizes=corpus_sizes, runs=runs)
            results.extend(result["results"])

        # Display summary table
        table = Table(title="Benchmark Results")
        table.add_column("Benchmark", style="cyan")
        table.add_column("Duration (ms)", justify="right")
        table.add_column("Memory (MB)", justify="right")
        table.add_column("Status", justify="center")

        for r in results:
            status = "✅" if r["success"] else "❌"
            table.add_row(r["name"], f"{r['duration_ms']:.2f}", f"{r['memory_mb']:.2f}", status)

        console.print(table)  # codeql[py/clear-text-logging-sensitive-data]

        # Export results
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if output.endswith(".json"):
                with open(output, "w") as f:
                    json.dump({"results": results}, f, indent=2)
                console.print(
                    f"[green]✅ Results exported to {output}[/green]"
                )  # codeql[py/clear-text-logging-sensitive-data]
            elif output.endswith(".csv"):
                import csv

                with open(output, "w", newline="") as f:
                    if results:
                        writer = csv.DictWriter(f, fieldnames=results[0].keys())
                        writer.writeheader()
                        writer.writerows(results)
                console.print(
                    f"[green]✅ Results exported to {output}[/green]"
                )  # codeql[py/clear-text-logging-sensitive-data]

        # Check for regressions
        if baseline:
            from codex.rag.benchmarks.runner import BenchmarkRunner

            runner = BenchmarkRunner()
            runner.results = [type("obj", (), r) for r in results]

            comparison = runner.compare_with_baseline(baseline, threshold)

            if comparison["has_regressions"]:
                console.print(
                    "\n[red]⚠️  Performance regressions detected:[/red]"
                )  # codeql[py/clear-text-logging-sensitive-data]
                for reg in comparison["regressions"]:
                    console.print(
                        f"  • {reg['name']}: {reg['duration_change_percent']:.1f}% slower"
                    )
                raise typer.Exit(1)
            console.print(
                "\n[green]✅ No performance regressions detected[/green]"
            )  # codeql[py/clear-text-logging-sensitive-data]

    except ImportError as e:
        type(e).__name__
        console.print(
            "[red]❌ Missing benchmark dependencies: <ERROR_TYPE>[/red]"
        )  # codeql[py/clear-text-logging-sensitive-data]
        raise typer.Exit(1) from e
    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        console.print(
            "[red]❌ Benchmark failed: <ERROR_TYPE>[/red]"
        )  # codeql[py/clear-text-logging-sensitive-data]
        logger.exception("Benchmark error")  # codeql[py/clear-text-logging-sensitive-data]
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
