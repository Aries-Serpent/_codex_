"""Command line helpers for inspecting and exercising tokenizers."""

from __future__ import annotations

import inspect as inspect_module
import json
import logging
import shutil
import sys
import types
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, NoReturn

logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    import typer as _typer
except (ImportError, AttributeError):  # pragma: no cover - fallback when typer missing
    _typer = None
else:
    required_attrs = {"Typer", "echo", "Option", "Exit"}
    if not required_attrs.issubset(set(dir(_typer))):
        _typer = None


# Fallback implementations are always defined unconditionally at module level so
# they are importable and testable regardless of whether typer is installed.
# The ``if _typer is None:`` block below only wires the runtime namespace shim.


class _FallbackTyper:
    """Minimal Typer-like interface used when the dependency is unavailable."""

    def __init__(self, **kwargs: object) -> None:
        self._commands: dict[str, tuple[types.FunctionType, inspect_module.Signature]] = {}
        self._help_text = kwargs.get("help")

    def command(self, name: str | None = None):
        def _register(func: types.FunctionType) -> types.FunctionType:
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


class _FallbackExit(SystemExit):
    """Replacement for :class:`typer.Exit` when Typer isn't installed."""


def _fallback_echo(message: object, *, err: bool = False) -> None:
    stream = sys.stderr if err else sys.stdout
    print(message, file=stream)


def _fallback_option(default=None, *_: object, **__: object):
    return default


if _typer is None:  # pragma: no cover - fallback CLI when typer missing
    typer = types.SimpleNamespace(
        Typer=_FallbackTyper,
        echo=_fallback_echo,
        Option=_fallback_option,
        Exit=_FallbackExit,
    )
else:  # pragma: no cover - typer available
    typer = _typer

from tokenizer.fast_tokenizer import build_tokenizer  # noqa: E402

app = typer.Typer(help="Tokenizer utilities")

_ERROR_REPORT_DIR = Path("_codex_reports")
_ERROR_QUESTION_TEMPLATE = (
    "What adjustments would resolve this issue so the {step} command can succeed?"
)


def _format_context(context: dict[str, Any] | str | None) -> str:
    """Render context information as a JSON string for logging."""

    if context is None:
        return "None"
    if isinstance(context, str):
        return context
    try:
        return json.dumps(context, sort_keys=True, default=str)
    except (ValueError, TypeError):
        logger.warning("Exception occurred", exc_info=True)
        return str(context)


def _append_error_block(
    step: str,
    message: str,
    context: dict[str, Any] | str | None,
    question: str | None = None,
) -> None:
    """Append a formatted error report entry to the daily error log."""

    timestamp = datetime.now(timezone.utc).isoformat()
    question_text = question or _ERROR_QUESTION_TEMPLATE.format(step=step)
    log_path = _ERROR_REPORT_DIR / f"errors_{timestamp.split('T')[0]}.md"
    block = (
        "\n:::\n"
        f"Question for ChatGPT @codex {timestamp}:\n"
        f"While performing Step {step}, encountered the following error:\n"
        f"{message}\n"
        f"Context: {_format_context(context)}\n"
        f"{question_text}\n"
        ":::"
    )

    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
    except (IOError, OSError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        typer.echo(f"Failed to ensure error log directory {log_path.parent}: {exc}", err=True)
        return

    try:
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(block + "\n")
    except (IOError, OSError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        typer.echo(f"Failed to append error log to {log_path}: {exc}", err=True)


def _fail(
    step: str,
    message: str,
    context: dict[str, Any] | str | None,
    question: str | None = None,
) -> NoReturn:
    """Record an error, surface the message to stderr, and exit."""

    _append_error_block(step, message, context, question)
    typer.echo(message, err=True)
    raise typer.Exit(1)


def _load_tokenizer(tokenizer_path: Path, *, step: str) -> object:
    """Load a tokenizer from ``tokenizer_path`` with structured error handling."""

    try:
        return build_tokenizer(tokenizer_path)
    except FileNotFoundError as exc:
        type(exc).__name__
        logger.debug("FileNotFoundError: <ERROR_TYPE>")
        _fail(
            step,
            f"Tokenizer not found at {tokenizer_path}",
            {"tokenizer_path": str(tokenizer_path), "error": str(exc)},
            "Could you confirm the tokenizer path or share how to generate it?",
        )
    except (IOError, OSError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        _fail(
            step,
            f"Failed to load tokenizer from {tokenizer_path}: {exc}",
            {"tokenizer_path": str(tokenizer_path), "error": repr(exc)},
            "What adjustments are required to load this tokenizer successfully?",
        )


def _resolve_root(path: Path) -> Path:
    """Return the tokenizer directory regardless of whether ``path`` is a file."""

    return path if path.is_dir() else path.parent


@app.command()
def vocab(
    tokenizer_path: Path,
    limit: int = typer.Option(10, help="Number of sample tokens to display"),
) -> None:
    """Print the tokenizer vocabulary size and a handful of sample tokens."""

    if limit < 0:
        _fail(
            "vocab",
            "limit must be non-negative",
            {"limit": limit},
            "Could you provide a non-negative token preview limit?",
        )

    tokenizer = _load_tokenizer(tokenizer_path, step="vocab")

    vocab_attr = getattr(tokenizer, "vocab_size", None)
    try:
        if callable(vocab_attr):
            vocab_size = int(vocab_attr())
        elif vocab_attr is not None:
            vocab_size = int(vocab_attr)
        else:
            raise AttributeError("Tokenizer does not expose a vocab_size attribute.")
    except (IOError, OSError) as exc:  # pragma: no cover - defensive casting guards
        _fail(
            "vocab",
            f"Unable to determine vocabulary size: {exc}",
            {"tokenizer_path": str(tokenizer_path), "error": repr(exc)},
            "How can we retrieve the vocabulary size for this tokenizer?",
        )

    typer.echo(f"Vocab size: {vocab_size}")

    if limit == 0:
        return

    converter = getattr(tokenizer, "convert_ids_to_tokens", None)
    if not callable(converter):
        typer.echo("Tokenizer lacks convert_ids_to_tokens; skipping sample tokens.")
        return

    sample_count = min(limit, vocab_size)
    for idx in range(sample_count):
        try:
            token = converter(idx)
        except (IOError, OSError) as exc:  # pragma: no cover - optional backend failures
            _append_error_block(
                "vocab",
                f"Failed to preview token {idx}: {exc}",
                {
                    "tokenizer_path": str(tokenizer_path),
                    "token_index": idx,
                    "error": repr(exc),
                },
                "How can we safely preview tokens from this tokenizer?",
            )
            typer.echo(f"Failed to convert token {idx}: {exc}", err=True)
            break
        typer.echo(f"{idx}: {token}")


@app.command()
def inspect(tokenizer_path: Path) -> None:
    """Show manifest metadata and special tokens for the tokenizer."""

    tokenizer = _load_tokenizer(tokenizer_path, step="inspect")
    root = _resolve_root(tokenizer_path)

    manifest: dict[str, Any] = {}
    manifest_path = root / "manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (IOError, OSError) as exc:
            error_type = type(exc).__name__
            logger.debug(f"Exception: {error_type}")
            _append_error_block(
                "inspect",
                f"Failed to parse manifest.json: {exc}",
                {"manifest_path": str(manifest_path), "error": repr(exc)},
                "Could you advise on validating the tokenizer manifest?",
            )
            manifest = {}

    special_tokens: list[str] | None = None
    getter = getattr(tokenizer, "all_special_tokens", None)
    if callable(getter):
        try:
            special_tokens = list(getter())
        except (IOError, OSError) as exc:  # pragma: no cover - backend specific guard
            _append_error_block(
                "inspect",
                f"Failed to collect special tokens: {exc}",
                {"tokenizer_path": str(tokenizer_path), "error": repr(exc)},
                "How can we enumerate special tokens for this tokenizer?",
            )
            special_tokens = None

    if not special_tokens:
        config_path = root / "tokenizer.json"
        if config_path.exists():
            try:
                tokenizer_cfg = json.loads(config_path.read_text(encoding="utf-8"))
            except (IOError, OSError) as exc:
                error_type = type(exc).__name__
                logger.debug(f"Exception: {error_type}")
                _append_error_block(
                    "inspect",
                    f"Failed to parse tokenizer.json: {exc}",
                    {"config_path": str(config_path), "error": repr(exc)},
                    "What steps will restore a readable tokenizer.json?",
                )
            else:
                added = tokenizer_cfg.get("added_tokens", [])
                if isinstance(added, list):
                    special_tokens = [
                        item.get("content")  # type: ignore[misc]
                        for item in added
                        if isinstance(item, dict) and item.get("special")
                    ]

    typer.echo(f"vocab_size: {getattr(tokenizer, 'vocab_size', 'unknown')}")
    typer.echo(f"special_tokens: {special_tokens}")

    cfg = manifest.get("config", {}) if isinstance(manifest, dict) else {}
    pad = cfg.get("padding") if isinstance(cfg, dict) else None
    trunc = cfg.get("truncation") if isinstance(cfg, dict) else None
    max_len = cfg.get("max_length") if isinstance(cfg, dict) else None
    typer.echo(f"padding: {pad} truncation: {trunc} max_length: {max_len}")


@app.command()
def encode(
    tokenizer_path: Path,
    text: str,
    pad_to: int = typer.Option(0, help="Optional padding / truncation length"),
    from_file: bool = typer.Option(False, help="Treat TEXT as a file path"),
    show_tokens: bool = typer.Option(False, help="Show decoded token strings"),
) -> None:
    """Encode text using the tokenizer located at ``TOKENIZER_PATH``."""

    if pad_to < 0:
        _fail(
            "encode",
            "pad_to must be zero or positive",
            {"pad_to": pad_to},
            "Could you provide a non-negative padding length?",
        )

    tokenizer = _load_tokenizer(tokenizer_path, step="encode")

    payload = text
    if from_file:
        input_path = Path(text)
        try:
            payload = input_path.read_text(encoding="utf-8")
        except (IOError, OSError) as exc:
            error_type = type(exc).__name__
            logger.debug(f"Exception: {error_type}")
            _fail(
                "encode",
                f"Failed to read input text from {input_path}: {exc}",
                {"input_path": str(input_path), "error": repr(exc)},
                "How can we make the input text accessible to the encode command?",
            )

    try:
        encoded = tokenizer(  # type: ignore[operator]
            payload,
            padding="max_length" if pad_to else False,
            max_length=pad_to or None,
        )
    except (IOError, OSError) as exc:
        error_type = type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        _fail(
            "encode",
            f"Tokenizer encode failed: {exc}",
            {"tokenizer_path": str(tokenizer_path), "error": repr(exc)},
            "What adjustments would allow this tokenizer to encode the text?",
        )

    ids_candidate: Any | None = None
    if isinstance(encoded, dict):
        ids_candidate = encoded.get("input_ids")
    elif hasattr(encoded, "input_ids"):
        ids_candidate = encoded.input_ids

    if ids_candidate is None:
        _fail(
            "encode",
            "Tokenizer did not provide input_ids in the response",
            {
                "tokenizer_path": str(tokenizer_path),
                "encoded_type": type(encoded).__name__,
            },
            "How can we retrieve token ids from this tokenizer?",
        )

    try:
        ids_source = ids_candidate if isinstance(ids_candidate, Sequence) else list(ids_candidate)
    except (IOError, OSError) as exc:
        error_type = type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        _fail(
            "encode",
            f"Unable to interpret input_ids: {exc}",
            {
                "tokenizer_path": str(tokenizer_path),
                "error": repr(exc),
                "input_ids_type": type(ids_candidate).__name__,
            },
            "What adjustments would allow input ids to be materialised as a list?",
        )

    ids_list: list[int]
    if (
        ids_source
        and isinstance(ids_source[0], Sequence)
        and not isinstance(ids_source[0], (str, bytes))
    ):
        ids_list = [int(x) for x in ids_source[0]]
    else:
        ids_list = [int(x) for x in ids_source]

    typer.echo("ids: " + " ".join(str(i) for i in ids_list))

    if show_tokens:
        converter = getattr(tokenizer, "convert_ids_to_tokens", None)
        if not callable(converter):
            typer.echo("Tokenizer lacks convert_ids_to_tokens; cannot show tokens.")
        else:
            try:
                tokens = [str(converter(i)) for i in ids_list]
            except (IOError, OSError) as exc:
                error_type = type(exc).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                _append_error_block(
                    "encode",
                    f"Failed to convert ids to tokens: {exc}",
                    {
                        "tokenizer_path": str(tokenizer_path),
                        "error": repr(exc),
                        "ids": ids_list,
                    },
                    "How can we inspect token strings for this tokenizer?",
                )
                typer.echo(
                    "Unable to convert ids to tokens; see error report for details.",
                    err=True,
                )
            else:
                typer.echo("tokens: " + " ".join(tokens))


@app.command()
def decode(
    tokenizer_path: Path,
    ids: str,
    skip_special_tokens: bool = typer.Option(
        False, help="Request special tokens be removed when supported"
    ),
) -> None:
    """Decode a comma-separated list of token ids."""

    try:
        id_list = [int(item.strip()) for item in ids.split(",") if item.strip()]
    except ValueError as exc:
        type(exc).__name__
        logger.debug("ValueError: <ERROR_TYPE>")
        _fail(
            "decode",
            f"Invalid token id list '{ids}': {exc}",
            {"ids": ids, "error": str(exc)},
            "Could you provide a comma-separated list of integer ids to decode?",
        )

    tokenizer = _load_tokenizer(tokenizer_path, step="decode")
    decode_fn = getattr(tokenizer, "decode", None)
    if not callable(decode_fn):
        _fail(
            "decode",
            "Tokenizer does not provide a decode function",
            {"tokenizer_path": str(tokenizer_path)},
            "Is there an alternative method to decode token ids?",
        )

    kwargs: dict[str, Any] = {}
    if skip_special_tokens:
        kwargs["skip_special_tokens"] = True

    try:
        decoded = decode_fn(id_list, **kwargs)
    except TypeError as e:
        type(e).__name__
        logger.debug("TypeError: <ERROR_TYPE>")
        logger.warning("TypeError: <ERROR_TYPE>", exc_info=True)
        try:
            decoded = decode_fn(id_list)
        except (IOError, OSError) as exc:  # pragma: no cover - backend guard
            _fail(
                "decode",
                f"Tokenizer decode failed: {exc}",
                {
                    "tokenizer_path": str(tokenizer_path),
                    "error": repr(exc),
                    "ids": id_list,
                },
                "What changes are needed so decoding succeeds?",
            )
    except (IOError, OSError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        _fail(
            "decode",
            f"Tokenizer decode failed: {exc}",
            {
                "tokenizer_path": str(tokenizer_path),
                "error": repr(exc),
                "ids": id_list,
            },
            "What changes are needed so decoding succeeds?",
        )

    typer.echo(str(decoded))


@app.command()
def export(src: Path, dst: Path) -> None:
    """Copy tokenizer artifacts to ``dst`` and write a short README."""

    root = _resolve_root(src)
    try:
        dst.mkdir(parents=True, exist_ok=True)
    except (IOError, OSError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        _fail(
            "export",
            f"Failed to prepare export directory {dst}: {exc}",
            {"destination": str(dst), "error": repr(exc)},
            "How can we create the export directory for tokenizer artifacts?",
        )

    copied_files = []
    for name in ("tokenizer.json", "manifest.json", "spm.model", "spm.vocab"):
        candidate = root / name
        if candidate.exists():
            target = dst / name
            try:
                shutil.copy2(candidate, target)
            except (ValueError, TypeError, RuntimeError) as exc:
                type(exc).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                _append_error_block(
                    "export",
                    f"Failed to copy {candidate} to {target}: {exc}",
                    {
                        "source": str(candidate),
                        "destination": str(target),
                        "error": repr(exc),
                    },
                    "How can we ensure tokenizer artifacts are copied successfully?",
                )
            else:
                copied_files.append(str(target))

    readme_path = dst / "README.md"
    readme_contents = (
        "# Exported Tokenizer\n\n"
        "This directory was generated by `tokenization.cli export`.\n\n"
        "Files copied:\n" + "\n".join(f"- {Path(path).name}" for path in copied_files) + "\n"
    )
    try:
        readme_path.write_text(readme_contents, encoding="utf-8")
    except (IOError, OSError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        _append_error_block(
            "export",
            f"Failed to write README.md: {exc}",
            {"readme_path": str(readme_path), "error": repr(exc)},
            "How can we document the exported tokenizer artifacts?",
        )


if __name__ == "__main__":  # pragma: no cover - manual execution hook
    app()


__all__ = ["app", "decode", "encode", "export", "inspect", "vocab"]
