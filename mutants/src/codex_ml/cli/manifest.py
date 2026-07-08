"""
Manifest Module

This module provides functionality for manifest.

Usage:
    from cli.manifest import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Optional

try:
    import typer

    TYPER_AVAILABLE = True
except ImportError:
    TYPER_AVAILABLE = False

from ..checkpointing.schema_v2 import sha256_hexdigest, to_canonical_bytes

HELP = """\
Usage:
  python -m codex_ml.cli.manifest hash --path PATH [--update-readme README.md]
"""

BADGE_START = "<!-- codex:manifest:start -->"
BADGE_END = "<!-- codex:manifest:end -->"

# Create Typer app for CLI tests
if TYPER_AVAILABLE:
    app = typer.Typer(help="Manifest validation and hash commands")

    @app.command()
    def validate(
        path: Path = typer.Option(..., help="Path to manifest JSON file"),
        strict: bool = typer.Option(False, help="Enable strict validation"),
    ):
        """Validate a manifest file against the schema."""
        try:
            data = json.loads(path.read_text(encoding="utf-8"))

            # Check schema version
            schema = data.get("schema", "")
            if schema != "codex.checkpoint.v2":
                typer.echo(f"Error: invalid schema '{schema}' (expected 'codex.checkpoint.v2')")
                raise typer.Exit(2)

            # In strict mode, reject unknown fields
            if strict:
                known_fields = {"schema", "run", "weights", "format", "bytes"}
                unknown = set(data.keys()) - known_fields
                if unknown:
                    typer.echo(f"Error: unknown fields in strict mode: {unknown}")
                    raise typer.Exit(2)

            typer.echo("Validation passed")
            # Return normally for success (exit code 0)

        except json.JSONDecodeError as e:
            typer.echo(f"Error: invalid JSON: {e}")
            raise typer.Exit(2) from e
        except typer.Exit:
            # Re-raise typer.Exit to preserve exit code
            raise
        except (IOError, OSError) as e:
            typer.echo(f"Error: {e}")
            raise typer.Exit(2) from e

    @app.command()
    def init(
        out: Path = typer.Option(..., help="Output path for the manifest JSON file"),
        run_id: str = typer.Option(..., help="Run identifier"),
    ):
        """Create a new manifest file with schema codex.checkpoint.v2."""
        import time

        manifest_data = {
            "schema": "codex.checkpoint.v2",
            "run": {
                "id": run_id,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
        }
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")
        typer.echo(f"Manifest written to {out}")

    @app.command()
    def hash(
        path: Path = typer.Option(..., help="Path to manifest JSON file"),
        update_readme: Optional[Path] = typer.Option(
            None, "--update-readme", help="README.md to update"
        ),
    ):
        """Compute SHA-256 digest of a manifest file and optionally update a README."""
        _DIGEST_START = "<!-- manifest-digest:start -->"
        _DIGEST_END = "<!-- manifest-digest:end -->"
        data = json.loads(path.read_text(encoding="utf-8"))
        digest = sha256_hexdigest(to_canonical_bytes(data))
        typer.echo(digest)
        if update_readme:
            readme = Path(update_readme).read_text(encoding="utf-8")
            block = f"{_DIGEST_START}\n<!-- sha256:{digest} -->\n{_DIGEST_END}"
            if _DIGEST_START in readme and _DIGEST_END in readme:
                pattern = re.compile(
                    re.escape(_DIGEST_START) + r".*?" + re.escape(_DIGEST_END),
                    flags=re.DOTALL,
                )
                new = pattern.sub(block, readme)
            else:
                new = readme + "\n\n" + block + "\n"
            Path(update_readme).write_text(new, encoding="utf-8")


def _usage() -> int:
    sys.stdout.write(HELP)
    return 0


def _badge(digest: str) -> str:
    # static Shields badge (no runtime fetch)
    # https://shields.io/docs/static-badges
    label = "manifest"
    msg = f"sha256:{digest[:8]}"
    color = "blue"
    return f"![manifest](https://img.shields.io/badge/{label}-{msg}-{color})"


def cmd_hash(path: Path, update_readme: Optional[Path]) -> int:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    digest = sha256_hexdigest(to_canonical_bytes(data))
    sys.stdout.write(digest + "\n")
    if update_readme:
        readme = Path(update_readme).read_text(encoding="utf-8")
        block = f"{BADGE_START}\n{_badge(digest)}\n{BADGE_END}"
        if BADGE_START in readme and BADGE_END in readme:
            pattern = re.compile(
                re.escape(BADGE_START) + r".*?" + re.escape(BADGE_END),
                flags=re.DOTALL,
            )
            new = pattern.sub(block, readme)
        else:
            new = readme + "\n\n" + block + "\n"
        Path(update_readme).write_text(new, encoding="utf-8")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] != "hash":
        return _usage()
    # naive argv parse to avoid external deps
    path = None
    update = None
    i = 1
    while i < len(argv):
        if argv[i] in ("--path", "-p") and i + 1 < len(argv):
            path = Path(argv[i + 1])
            i += 2
        elif argv[i] == "--update-readme" and i + 1 < len(argv):
            update = Path(argv[i + 1])
            i += 2
        else:
            return _usage()
    if not path:
        return _usage()
    return cmd_hash(path, update)


if __name__ == "__main__":
    raise SystemExit(main())
