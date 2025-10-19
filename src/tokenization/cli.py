from __future__ import annotations

import inspect as inspect_module
import json
import shutil
import sys
import types
from pathlib import Path
from typing import Callable

try:  # pragma: no cover - optional dependency
    import typer as _typer  # type: ignore
except Exception:  # pragma: no cover - fallback CLI when typer missing
    _typer = None
else:
    required_attrs = {"Typer", "echo", "Option"}
    if not required_attrs.issubset(set(dir(_typer))):
        _typer = None

if _typer is None:  # pragma: no cover - fallback CLI when typer missing or incomplete

    class _FallbackTyper:
        def __init__(self, **kwargs: object) -> None:
            self._commands: dict[str, tuple[Callable[..., object], inspect_module.Signature]] = {}
            self._help_text = kwargs.get("help")

        def command(self, name: str | None = None):
            def _register(func):
                cmd_name = name or func.__name__.replace("_", "-")
                self._commands[cmd_name] = (func, inspect_module.signature(func))
                return func

            return _register

        def _print_app_help(self) -> None:
            if self._help_text:
                print(self._help_text)
            if self._commands:
                print("Commands:")
                for command in sorted(self._commands):
                    print(f"  {command}")

        def _print_command_help(self, name: str, signature: inspect_module.Signature) -> None:
            params = []
            for param in signature.parameters.values():
                placeholder = param.name.upper()
                if param.default is inspect_module.Signature.empty:
                    params.append(placeholder)
                else:
                    params.append(f"[{placeholder}]")
            usage = " ".join(params)
            if usage:
                print(f"Usage: {name} {usage}")
            else:
                print(f"Usage: {name}")

        def __call__(self) -> None:
            argv = sys.argv[1:]
            if not argv or argv[0] in {"--help", "-h"}:
                self._print_app_help()
                raise SystemExit(0)
            cmd_name, *rest = argv
            entry = self._commands.get(cmd_name)
            if entry is None:
                print(f"Unknown command: {cmd_name}", file=sys.stderr)
                self._print_app_help()
                raise SystemExit(1)
            func, signature = entry
            if rest and rest[0] in {"--help", "-h"}:
                self._print_command_help(cmd_name, signature)
                raise SystemExit(0)
            params = list(signature.parameters.values())
            converted: list[object] = []
            for arg, param in zip(rest, params, strict=False):
                annotation = param.annotation
                if annotation is Path or annotation == "Path":
                    converted.append(Path(arg))
                else:
                    converted.append(arg)
            func(*converted)

    def _fallback_echo(message: object, *, err: bool = False) -> None:
        stream = sys.stderr if err else sys.stdout
        print(message, file=stream)

    def _fallback_option(default=None, *_: object, **__: object):
        return default

    typer = types.SimpleNamespace(
        Typer=_FallbackTyper, echo=_fallback_echo, Option=_fallback_option
    )
else:
    typer = _typer

from .fast_tokenizer import build_tokenizer

app = typer.Typer(help="Tokenizer utilities")


def _resolve_root(path: Path) -> Path:
    return path if path.is_dir() else path.parent


def _load_tokenizer(path: Path):
    try:
        return build_tokenizer(path)
    except FileNotFoundError as exc:
        typer.echo(f"Tokenizer not found: {exc}", err=True)
        raise SystemExit(1)
    except Exception as exc:
        typer.echo(f"Failed to load tokenizer from {path}: {exc}", err=True)
        raise SystemExit(1)


@app.command()
def vocab(
    tokenizer_path: Path,
    limit: int = typer.Option(10, help="Number of sample tokens to display"),
) -> None:
    """Print vocabulary size with a handful of sample tokens."""

    tokenizer = _load_tokenizer(tokenizer_path)
    vocab_size = getattr(tokenizer, "vocab_size", None)
    if vocab_size is None:
        typer.echo("Tokenizer does not expose a vocab size attribute", err=True)
        raise SystemExit(1)

    size_int = int(vocab_size)
    typer.echo(f"Vocab size: {size_int}")

    converter = getattr(tokenizer, "convert_ids_to_tokens", None)
    if not callable(converter):
        typer.echo("Tokenizer lacks convert_ids_to_tokens; skipping sample tokens.")
        return

    for idx in range(min(limit, size_int)):
        try:
            token = converter(idx)
        except Exception as exc:  # pragma: no cover - defensive guard
            typer.echo(f"Failed to convert token {idx}: {exc}", err=True)
            break
        typer.echo(f"{idx}: {token}")


@app.command()
def inspect(tokenizer_path: Path) -> None:
    """Show manifest metadata for a tokenizer directory."""

    tokenizer = _load_tokenizer(tokenizer_path)
    root = _resolve_root(tokenizer_path)
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

    special_tokens: object | None = None
    getter = getattr(tokenizer, "all_special_tokens", None)
    if callable(getter):
        special_tokens = list(getter())
    if not special_tokens:
        config_path = root / "tokenizer.json"
        if config_path.exists():
            try:
                tokenizer_config = json.loads(config_path.read_text())
            except json.JSONDecodeError:
                tokenizer_config = {}
            added_tokens = tokenizer_config.get("added_tokens", [])
            if isinstance(added_tokens, list):
                special_tokens = [
                    item.get("content")
                    for item in added_tokens
                    if isinstance(item, dict) and item.get("special")
                ]
    typer.echo(f"vocab_size: {getattr(tokenizer, 'vocab_size', 'unknown')}")
    typer.echo(f"special_tokens: {special_tokens}")

    cfg = manifest.get("config", {}) if isinstance(manifest, dict) else {}
    pad = cfg.get("padding")
    trunc = cfg.get("truncation")
    max_len = cfg.get("max_length")
    typer.echo(f"padding: {pad} truncation: {trunc} max_length: {max_len}")


@app.command()
def encode(
    tokenizer_path: Path,
    text: str,
    pad_to: int = typer.Option(0, help="Optional padding / truncation length"),
    from_file: bool = typer.Option(False, help="Treat TEXT as a file path"),
    show_tokens: bool = typer.Option(False, help="Show token strings"),
) -> None:
    """Encode TEXT using the tokenizer located at TOKENIZER_PATH."""

    tokenizer = _load_tokenizer(tokenizer_path)
    if from_file:
        text = Path(text).read_text(encoding="utf-8")

    encoded = tokenizer(
        text,
        padding="max_length" if pad_to else False,
        max_length=pad_to or None,
    )
    input_ids = encoded.get("input_ids") if isinstance(encoded, dict) else None
    if input_ids is None and hasattr(encoded, "input_ids"):
        input_ids = getattr(encoded, "input_ids")
    if input_ids is None:
        typer.echo("Tokenizer did not return input_ids", err=True)
        raise SystemExit(1)
    if input_ids and isinstance(input_ids[0], list):
        ids_list = input_ids[0]
    else:
        ids_list = list(input_ids)
    typer.echo("ids: " + " ".join(str(i) for i in ids_list))

    if show_tokens:
        converter = getattr(tokenizer, "convert_ids_to_tokens", None)
        if callable(converter):
            tokens = [converter(i) for i in ids_list]
            typer.echo("tokens: " + " ".join(tokens))
        else:
            typer.echo("Tokenizer lacks convert_ids_to_tokens; cannot show tokens.")


@app.command()
def decode(tokenizer_path: Path, ids: str) -> None:
    """Decode a comma-separated list of token ids."""

    tokenizer = _load_tokenizer(tokenizer_path)
    try:
        id_list = [int(item.strip()) for item in ids.split(",") if item.strip()]
    except ValueError as exc:
        typer.echo(f"Invalid token id in '{ids}': {exc}", err=True)
        raise SystemExit(1)
    typer.echo(tokenizer.decode(id_list))


@app.command()
def export(src: Path, dst: Path) -> None:
    """Copy tokenizer artifacts (json/manifest/spm) to DST."""

    dst.mkdir(parents=True, exist_ok=True)
    for name in ("tokenizer.json", "manifest.json", "spm.model", "spm.vocab"):
        p = _resolve_root(src) / name
        if p.exists():
            shutil.copy2(p, dst / name)


if __name__ == "__main__":
    app()


__all__ = ["app", "vocab", "inspect", "encode", "decode", "export"]
