"""Canvas Importer/Packager CLI utility.

This is the main executable script providing a command-line interface (CLI) for packaging a repository into a ChatGPT Canvas bundle (zip file of "panels") and verifying such bundles for integrity. It supports multiple input modalities (e.g., a root folder or a list of knowledge files) and chunking strategies (bytes, semantic, tokens) as described in the research plan.

Usage: python canvas_importer_packager.py pack --root path/to/repo [--strategy semantic] [--budget 16000] [--output bundle.zip]
python canvas_importer_packager.py verify --bundle path/to/bundle.zip

Subcommands:
- pack: Traverse input files, split them into panels (chunks) according to strategy and budget, then output a ZIP bundle containing all panels, a manifest, checksums, etc.
- verify: Validate a given bundle's manifest and panel files (reassemble each source file from panels and check SHA-256 hashes, ensure no missing or extra parts, etc).

No truncation of content is performed at any stage (see NO_BREVITY_POLICY.md); the tool ensures that even extremely large files are chunked and included fully across multiple panels.

Environment:
- Requires Python 3.8+.
- pip install tiktoken if using token-based chunking.
"""

import argparse

from packer import pack_directory
from verifier import verify_bundle


def main():
    """Parse CLI arguments and dispatch to pack or verify functionality."""
    parser = argparse.ArgumentParser(
        prog="canvas_importer_packager",
        description="ChatGPT Canvas Importer/Packager: package a project into panels or verify a packaged bundle.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Pack subcommand parser
    pack_parser = subparsers.add_parser(
        "pack", help="Package a directory or files into a Canvas bundle (ZIP)."
    )
    pack_parser.add_argument(
        "--root",
        type=str,
        default=".",
        help="Path to the root directory of the project to pack. Defaults to current directory.",
    )
    pack_parser.add_argument(
        "--output",
        type=str,
        default="canvas_bundle.zip",
        help="Output ZIP file path for the bundle.",
    )
    pack_parser.add_argument(
        "--strategy",
        type=str,
        choices=["bytes", "semantic", "tokens"],
        default="semantic",
        help="Chunking strategy: 'bytes' for fixed byte size, 'semantic' for intelligent chunking by content, 'tokens' for model tokens.",
    )
    pack_parser.add_argument(
        "--budget",
        type=int,
        default=None,
        help="Chunk size limit for the chosen strategy. e.g., max bytes or tokens per chunk. Defaults depend on strategy (see documentation).",
    )
    pack_parser.add_argument(
        "--model",
        type=str,
        default="gpt-4",
        help="Model name for token counting (if strategy='tokens'). Default is 'gpt-4'.",
    )
    # Optional arguments for include/exclude patterns could be added here (from config or CLI flags).
    # e.g., --include-ext, --exclude-glob, etc.

    # Verify subcommand parser
    verify_parser = subparsers.add_parser(
        "verify", help="Verify the integrity of an existing Canvas bundle ZIP."
    )
    verify_parser.add_argument(
        "--bundle", type=str, required=True, help="Path to the Canvas bundle zip file to verify."
    )

    args = parser.parse_args()
    if args.command == "pack":
        # Perform packing: This calls the pack_directory function to create the bundle.
        # On success, it should produce the output ZIP and associated manifest/checksums.
        pack_directory(
            root_path=args.root,
            output_zip=args.output,
            strategy=args.strategy,
            budget=args.budget,
            model=args.model,
        )
        # In a full implementation, pack_directory might print or log a summary (e.g., bundle path, number of panels).
        # Here we just call it; any output or logging is handled inside pack_directory.
    elif args.command == "verify":
        # Perform verification: Calls verify_bundle on the provided bundle path.
        verify_bundle(zip_path=args.bundle)
        # In a full implementation, verify_bundle would print verification results and raise or exit with error code on failure.


if __name__ == "__main__":
    main()
