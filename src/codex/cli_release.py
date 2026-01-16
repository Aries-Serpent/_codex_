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
    res = verify_bundle(bundle)
    typer.echo(json.dumps(res, indent=2))


@app.command("unpack")
def cmd_unpack(
    bundle: Path = typer.Argument(DEFAULT_BUNDLE, exists=True),
    dest: Path = typer.Option(DEFAULT_DEST, "--dest"),
    allow_scripts: bool = typer.Option(False, "--allow-scripts/--no-allow-scripts"),
) -> None:
    d = unpack_bundle(bundle, dest, allow_scripts=allow_scripts)
    typer.echo(json.dumps({"dest": d.as_posix()}, indent=2))
