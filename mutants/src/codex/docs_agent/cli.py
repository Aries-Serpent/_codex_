"""
CLI Module for Docs Agent

Command-line interface for processing documentation, building indexes,
and managing the docs_agent system.

Authority: Lane 3 Unified Documentation Agent
"""

import json
import logging
import sys
from pathlib import Path
from typing import Optional

import click

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Docs Agent: Machine-Readable Documentation Infrastructure

    Commands for processing documentation, building semantic indexes,
    and managing documentation as structured JSONL records.
    """
    pass


@cli.command()
@click.argument("docs_dir", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), default="docs.jsonl", help="Output JSONL file")
@click.option("--prefix", "-p", default="doc", help="ID prefix for documents")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def process(docs_dir: str, output: str, prefix: str, verbose: bool):
    """Process Markdown documentation to JSONL format

    Examples:
        $ docs-agent process ./docs -o docs.jsonl
        $ docs-agent process ./api-docs -p api-doc
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    from .document_processor import DocumentProcessor

    logger.info(f"Processing documentation from: {docs_dir}")
    logger.info(f"Output file: {output}")

    processor = DocumentProcessor()
    try:
        count = processor.process_directory(Path(docs_dir), prefix=prefix)
        processor.write_jsonl(Path(output))

        stats = processor.get_statistics()

        click.echo("\n" + "=" * 60)
        click.echo("DOCUMENTATION PROCESSING COMPLETE")
        click.echo("=" * 60)
        click.echo(f"Documents:    {stats['documents']}")
        click.echo(f"Sections:     {stats['sections']}")
        click.echo(f"Blocks:       {stats['blocks']}")
        click.echo(f"Total:        {stats['total_records']}")
        click.echo(f"Output:       {output}")
        click.echo("=" * 60 + "\n")

    except Exception as e:
        click.echo(f"ERROR: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("jsonl_file", type=click.Path(exists=True))
@click.option(
    "--schemas-dir",
    type=click.Path(exists=True),
    default=".codex/schemas",
    help="Schemas directory",
)
@click.option("--csv-report", type=click.Path(), help="Output CSV validation report")
@click.option("--json-report", type=click.Path(), help="Output JSON validation report")
@click.option("--html-report", type=click.Path(), help="Output HTML validation report")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def validate(
    jsonl_file: str,
    schemas_dir: str,
    csv_report: Optional[str],
    json_report: Optional[str],
    html_report: Optional[str],
    verbose: bool,
):
    """Validate JSONL documentation file

    Examples:
        $ docs-agent validate docs.jsonl
        $ docs-agent validate docs.jsonl --json-report report.json
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    from .schema_validator import SchemaValidator

    logger.info(f"Validating: {jsonl_file}")

    try:
        validator = SchemaValidator(Path(schemas_dir))
        results = validator.validate_file(Path(jsonl_file))

        # Print summary
        click.echo("\n" + "=" * 60)
        click.echo("VALIDATION SUMMARY")
        click.echo("=" * 60)
        click.echo(f"Total records:    {results['total_records']}")
        click.echo(f"Valid:            {results['valid_records']}")
        click.echo(f"Invalid:          {results['invalid_records']}")
        click.echo(f"Accuracy:         {results['accuracy_percent']:.1f}%")

        if results["records_by_type"]:
            click.echo("\nRecords by type:")
            for rtype, count in sorted(results["records_by_type"].items()):
                click.echo(f"  {rtype}: {count}")

        if results["errors"]:
            click.echo("\nFirst 5 errors:")
            for error in results["errors"][:5]:
                click.echo(f"  Line {error.get('line')}: {error['message']}")

        click.echo("=" * 60 + "\n")

        # Generate reports
        if csv_report:
            click.echo(f"CSV report would be saved to: {csv_report}")
        if json_report:
            click.echo(f"JSON report would be saved to: {json_report}")
        if html_report:
            click.echo(f"HTML report would be saved to: {html_report}")

        # Exit with appropriate code
        sys.exit(0 if results["invalid_records"] == 0 else 1)

    except Exception as e:
        click.echo(f"ERROR: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("jsonl_file", type=click.Path(exists=True))
@click.option("--model", default="all-MiniLM-L6-v2", help="Embedding model name")
@click.option(
    "--output", "-o", type=click.Path(), default="semantic_index", help="Output index file path"
)
@click.option("--batch-size", type=int, default=32, help="Batch size for embeddings")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def build_index(jsonl_file: str, model: str, output: str, batch_size: int, verbose: bool):
    """Build semantic search index from JSONL

    Examples:
        $ docs-agent build-index docs.jsonl -o index.faiss
        $ docs-agent build-index docs.jsonl --model all-mpnet-base-v2
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    from .semantic_indexer import SemanticIndexer

    logger.info(f"Building semantic index from: {jsonl_file}")
    logger.info(f"Model: {model}")

    try:
        indexer = SemanticIndexer(model_name=model)

        # Load records from JSONL
        with open(jsonl_file, "r") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                indexer.add_record(record)

        click.echo(f"Loaded {len(indexer.records)} records")

        # Build index
        click.echo("Building semantic index...")
        stats = indexer.build_index(batch_size=batch_size)

        # Save index
        indexer.save_index(Path(output))

        # Print summary
        click.echo("\n" + "=" * 60)
        click.echo("INDEX BUILD COMPLETE")
        click.echo("=" * 60)
        click.echo(f"Total records:    {stats['record_count']}")
        click.echo(f"Indexed:          {stats['indexed']}")
        click.echo(f"Embedding dim:    {stats.get('embedding_dim', 'N/A')}")
        click.echo(f"Output:           {output}*")
        click.echo("=" * 60 + "\n")

    except Exception as e:
        click.echo(f"ERROR: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("index_path", type=click.Path(exists=True))
@click.argument("query", required=False)
@click.option("--limit", "-k", type=int, default=10, help="Number of results")
@click.option("--threshold", type=float, default=0.0, help="Similarity threshold")
@click.option("--interactive", "-i", is_flag=True, help="Interactive search mode")
def search(index_path: str, query: Optional[str], limit: int, threshold: float, interactive: bool):
    """Search semantic index

    Examples:
        $ docs-agent search index.json "how to authenticate"
        $ docs-agent search index.json -i  # Interactive mode
    """
    from .semantic_indexer import SemanticIndexer

    logger.info(f"Loading index from: {index_path}")

    try:
        indexer = SemanticIndexer()
        if not indexer.load_index(Path(index_path)):
            click.echo("ERROR: Failed to load index", err=True)
            sys.exit(1)

        stats = indexer.get_statistics()
        click.echo("\nIndex Statistics:")
        click.echo(f"  Model: {stats['model_name']}")
        click.echo(f"  Records: {stats['total_records']}")
        click.echo(f"  Indexed: {stats['indexed_records']}")

        if interactive:
            click.echo("\nEntering interactive search mode (Ctrl+C to exit)\n")
            while True:
                query = click.prompt("Search query")
                if not query:
                    continue

                results = indexer.search(query, k=limit, threshold=threshold)

                click.echo(f"\nFound {len(results)} results:\n")
                for i, result in enumerate(results, 1):
                    click.echo(f"{i}. {result.title} (score: {result.score:.3f})")
                    click.echo(f"   Type: {result.record_type}")
                    click.echo(f"   Content: {result.content[:100]}...")
                    click.echo()

        elif query:
            results = indexer.search(query, k=limit, threshold=threshold)

            click.echo(f"\nFound {len(results)} results:\n")
            for i, result in enumerate(results, 1):
                click.echo(f"{i}. {result.title} (score: {result.score:.3f})")
                click.echo(f"   Type: {result.record_type}")
                click.echo(f"   Content: {result.content[:100]}...")
                click.echo()

        else:
            click.echo("Provide query or use --interactive mode", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"ERROR: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--host", default="127.0.0.1", help="Server host")
@click.option("--port", type=int, default=5000, help="Server port")
@click.option("--latency", is_flag=True, help="Enable latency simulation")
@click.option("--error-rate", type=float, default=0.0, help="Error rate (0.0-1.0)")
def mock_server(host: str, port: int, latency: bool, error_rate: float):
    """Run mock HTTP server for testing

    Examples:
        $ docs-agent mock-server --port 8000
        $ docs-agent mock-server --latency --error-rate 0.1
    """
    from .http_mock_server import MockHTTPServer

    click.echo(f"\nStarting mock server on {host}:{port}")
    click.echo(f"Latency simulation: {'enabled' if latency else 'disabled'}")
    click.echo(f"Error rate: {error_rate:.1%}\n")

    try:
        server = MockHTTPServer(host=host, port=port, enable_latency=latency)
        server.set_error_rate(error_rate)
        server.run(debug=False)
    except Exception as e:
        click.echo(f"ERROR: {e}", err=True)
        sys.exit(1)


@cli.command()
def version():
    """Show version information"""
    click.echo("Docs Agent v1.0.0")
    click.echo("Machine-Readable Documentation Infrastructure")
    click.echo("Authority: Lane 3 Unified Documentation Agent")


if __name__ == "__main__":
    cli()
