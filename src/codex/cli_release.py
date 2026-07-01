"""
Cli Release Module

This module provides functionality for cli release.

Usage:
    from codex.cli_release import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import json
from pathlib import Path

import typer

from codex.release.api import pack_release, unpack_bundle, verify_bundle

DEFAULT_MANIFEST = Path("release.manifest.json")
DEFAULT_STAGING = Path("work/release_staging")
DEFAULT_BUNDLE = Path("dist/codex-release.tar.gz")
DEFAULT_DEST = Path("/opt/codex/app")

app = typer.Typer(help="Codex Release (offline pack/verify/unpack)")


@app.command("init-manifest")
def cmd_init_manifest(
    out: Path = typer.Argument(DEFAULT_MANIFEST),
) -> None:
    """Initialize a release manifest template.

    Creates a template manifest JSON file with placeholder values for all
    required fields. Use this as a starting point for defining release
    contents, target platforms, and deployment metadata.

    Args:
        out: Output manifest path (default: release.manifest.json)

    Template Fields:
        - release_id: Unique identifier (e.g., codex-YYYY.MM.DD-r01)
        - version: Semantic version (e.g., vYYYY.MM.DD)
        - created_at: ISO 8601 timestamp
        - actor: Creator identifier
        - target: Platforms (linux/amd64, etc.)
        - components: Files to package
        - symlinks: Symbolic links to create
        - post_unpack_commands: Scripts to run after unpack
        - checks: Integrity checksums

    Examples:
        # Create manifest in current directory
        codex release init-manifest

        # Custom location
        codex release init-manifest /tmp/release.manifest.json

    See Also:
        codex release pack - Pack release bundle from manifest
    """
    out.write_text(
        json.dumps(
            {
                "release_id": "codex-YYYY.MM.DD-r01",
                "version": "vYYYY.MM.DD",
                "created_at": "YYYY-MM-DDTHH:MM:SSZ",
                "actor": "marc",
                "target": {"platforms": ["linux/amd64"], "apps": []},
                "components": [
                    {
                        "tombstone": "<uuid>",
                        "dest_path": "bin/codex-cli",
                        "mode": "0755",
                        "type": "file",
                    },
                ],
                "symlinks": [],
                "post_unpack_commands": [],
                "checks": {"sha256_manifest": "<filled at pack time>"},
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    typer.echo(out.as_posix())


@app.command("pack")
def cmd_pack(
    manifest: Path = typer.Argument(DEFAULT_MANIFEST, exists=True),
    staging: Path = typer.Option(DEFAULT_STAGING, "--staging"),
    out_bundle: Path = typer.Option(DEFAULT_BUNDLE, "--out"),
) -> None:
    """Pack a release bundle from manifest.

    Creates a compressed tar.gz bundle containing all components specified
    in the manifest. Each component's integrity is verified during packing
    and recorded in the locked manifest.

    Args:
        manifest: Path to manifest file (must exist)
        staging: Staging directory for bundle creation (default: work/release_staging)
        out_bundle: Output bundle path (default: dist/codex-release.tar.gz)

    Output:
        JSON with bundle path and SHA256 manifest hash

    Examples:
        # Pack with default settings
        codex release pack release.manifest.json

        # Custom staging and output
        codex release pack release.manifest.json \\
          --staging /tmp/staging \\
          --out dist/codex-v1.tar.gz

    See Also:
        codex release init-manifest - Create manifest template
        codex release verify - Verify bundle integrity
        codex release unpack - Extract bundle to destination
    """
    bundle, locked = pack_release(manifest, staging, out_bundle)
    typer.echo(
        json.dumps(
            {
                "bundle": bundle.as_posix(),
                "locked": {"sha256_manifest": locked["checks"]["sha256_manifest"]},
            },
            indent=2,
        )
    )


@app.command("verify")
def cmd_verify(
    bundle: Path = typer.Argument(DEFAULT_BUNDLE, exists=True),
) -> None:
    """Verify integrity of a release bundle.

    Validates all component checksums in the bundle and compares them against
    the locked manifest. Ensures bundle has not been corrupted or tampered with.

    Args:
        bundle: Path to bundle file (must exist)

    Output:
        JSON verification result with:
        - ok: Boolean indicating successful verification
        - checksums: Per-component verification results
        - timestamp: Verification timestamp

    Examples:
        # Verify with default name
        codex release verify

        # Verify custom bundle
        codex release verify dist/codex-custom.tar.gz

    See Also:
        codex release pack - Create bundle from manifest
        codex release unpack - Extract verified bundle
    """
    res = verify_bundle(bundle)
    typer.echo(json.dumps(res, indent=2))


@app.command("unpack")
def cmd_unpack(
    bundle: Path = typer.Argument(DEFAULT_BUNDLE, exists=True),
    dest: Path = typer.Option(DEFAULT_DEST, "--dest"),
    allow_scripts: bool = typer.Option(False, "--allow-scripts/--no-allow-scripts"),
) -> None:
    """Unpack a release bundle to destination.

    Extracts bundle contents to the specified destination directory. Optionally
    executes post-unpack scripts (e.g., service restart, database migration).

    Args:
        bundle: Path to bundle file (must exist)
        dest: Destination directory (default: /opt/codex/app)
        allow_scripts: Execute post-unpack scripts (default: False)

    Output:
        JSON with destination path

    Examples:
        # Unpack to default location
        codex release unpack

        # Unpack to custom location
        codex release unpack dist/codex-release.tar.gz --dest /opt/custom

        # Execute post-unpack scripts
        codex release unpack --allow-scripts

        # No scripts (safer default)
        codex release unpack --no-allow-scripts

    Safety:
        By default, post-unpack scripts are NOT executed. Use --allow-scripts
        only if you trust the bundle source and have reviewed the scripts.

    See Also:
        codex release verify - Verify bundle before unpacking
        codex release pack - Create bundle from manifest
    """
    d = unpack_bundle(bundle, dest, allow_scripts=allow_scripts)
    typer.echo(json.dumps({"dest": d.as_posix()}, indent=2))
