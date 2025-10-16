from __future__ import annotations

import inspect as inspect_module
import json
import shutil
import sys
import types
from collections.abc import Callable
from pathlib import Path
from typing import Annotated

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

    def _fallback_echo(message: object) -> None:
        print(message)

    def _fallback_option(default=None, *_: object, **__: object):
        return default

    typer = types.SimpleNamespace(
        Typer=_FallbackTyper, echo=_fallback_echo, Option=_fallback_option
    )
else:
    typer = _typer

try:  # pragma: no cover - optional dependency
    from tokenizers import Tokenizer  # type: ignore
except Exception:  # pragma: no cover - fallback when tokenizers missing

    class Tokenizer:  # type: ignore[no-redef]
        def __init__(self, data: dict, path: Path) -> None:
            self._data = data
            self._path = path

        @classmethod
        def from_file(cls, path: str) -> Tokenizer:
            file_path = Path(path)
            data = json.loads(file_path.read_text())
            return cls(data, file_path)

        def get_vocab_size(self) -> int:
            vocab = self._data.get("model", {}).get("vocab")
            if isinstance(vocab, list):
                return len(vocab)
            vocab_list = self._data.get("vocab", [])
            if isinstance(vocab_list, list):
                return len(vocab_list)
            value = self._data.get("vocab_size")
            return int(value) if isinstance(value, int | float | str) else 0

        def get_special_tokens(self) -> list[str]:
            added_tokens = self._data.get("added_tokens", [])
            if not isinstance(added_tokens, list):
                return []
            return [
                item.get("content")
                for item in added_tokens
                if isinstance(item, dict) and item.get("special")
            ]

        def encode(self, text: str):  # pragma: no cover - encode requires optional dependency
            raise RuntimeError("The 'tokenizers' package is required for encode operations")


app = typer.Typer(help="Tokenizer utilities")


def _load(path: Path) -> Tokenizer:
    return Tokenizer.from_file(str(path / "tokenizer.json"))


@app.command()
def inspect(path: Path) -> None:
    tk = _load(path)
    manifest_path = path / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    tokenizer_config = json.loads((path / "tokenizer.json").read_text())
    special_tokens: object | None = None
    try:
        getter = getattr(tk, "get_special_tokens", None)
        if callable(getter):
            special_tokens = getter()
    except Exception:
        special_tokens = None
    if special_tokens is None:
        added_tokens = tokenizer_config.get("added_tokens", [])
        special_tokens = [item.get("content") for item in added_tokens if item.get("special")]
        if not special_tokens:
            cfg = manifest.get("config", {})
            special_tokens = {
                "pad": cfg.get("padding"),
                "truncation": cfg.get("truncation"),
                "max_length": cfg.get("max_length"),
            }
    typer.echo(f"vocab_size: {tk.get_vocab_size()}")
    typer.echo(f"special_tokens_or_cfg: {special_tokens}")
    cfg = manifest.get("config", {})
    pad = cfg.get("padding")
    trunc = cfg.get("truncation")
    max_len = cfg.get("max_length")
    typer.echo(f"padding: {pad} truncation: {trunc} max_length: {max_len}")


@app.command()
def encode(
    tokenizer_path: Path,
    text: str,
    from_file: Annotated[
        bool,
        typer.Option("--from-file", help="Treat TEXT as path"),
    ] = False,
    show_ids: Annotated[bool, typer.Option(help="Show token ids")] = True,
    show_tokens: Annotated[bool, typer.Option(help="Show decoded tokens")] = False,
) -> None:
    tk = _load(tokenizer_path)
    if from_file:
        text = Path(text).read_text()
    enc = tk.encode(text)
    if show_ids:
        typer.echo("ids: " + " ".join(str(i) for i in enc.ids))
    if show_tokens:
        typer.echo("tokens: " + " ".join(enc.tokens))


@app.command()
def export(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for name in ("tokenizer.json", "manifest.json", "spm.model", "spm.vocab"):
        p = src / name
        if p.exists():
            shutil.copy2(p, dst / name)
    manifest_path = src / "manifest.json"
    readme = dst / "README.md"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        readme.write_text(
            "# Tokenizer Export\n\n````json\n" + json.dumps(manifest, indent=2) + "\n````\n"
        )
    else:
        readme.write_text("# Tokenizer Export\n")


if __name__ == "__main__":
    app()
