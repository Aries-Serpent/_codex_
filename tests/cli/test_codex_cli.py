from __future__ import annotations

import builtins
import importlib
import json
import sys
from types import ModuleType

import pytest
from click.testing import CliRunner

from codex.cli import cli as codex_root_cli
from codex.cli import logs as codex_logs_group

try:
    _CODEX_ML_CLI: ModuleType | None = importlib.import_module("codex_ml.cli.codex_cli")
except Exception as exc:  # pragma: no cover - optional dependency path
    _CODEX_ML_CLI = None
    _CODEX_ML_IMPORT_ERROR = exc
else:
    _CODEX_ML_IMPORT_ERROR = None


@pytest.fixture(autouse=True)
def _clear_tokenizer_pipeline_cache():
    if _CODEX_ML_CLI is None:
        yield
        return
    cache_clear = getattr(_CODEX_ML_CLI._get_tokenizer_pipeline, "cache_clear", None)
    if cache_clear is not None:
        cache_clear()
    yield
    cache_clear = getattr(_CODEX_ML_CLI._get_tokenizer_pipeline, "cache_clear", None)
    if cache_clear is not None:
        cache_clear()


@pytest.fixture
def codex_cli() -> ModuleType:
    if _CODEX_ML_CLI is None:
        pytest.skip(f"codex_ml CLI unavailable: {_CODEX_ML_IMPORT_ERROR}")
    return _CODEX_ML_CLI


def _runner() -> CliRunner:
    return CliRunner()


@pytest.mark.tokenizer
def test_tokenizer_cli_reports_missing_tokenizers(monkeypatch, codex_cli):
    """Optional dependencies produce actionable CLI errors."""

    runner = _runner()
    monkeypatch.delitem(sys.modules, "codex_ml.tokenization.pipeline", raising=False)

    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "codex_ml.tokenization.pipeline":
            raise ModuleNotFoundError("No module named 'tokenizers'", name="tokenizers")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    result = runner.invoke(codex_cli.codex, ["tokenizer", "encode", "hi"])
    assert result.exit_code != 0
    assert "optional 'tokenizers' dependency" in result.output


@pytest.mark.tokenizer
def test_tokenizer_cli_train_validate_roundtrip(tmp_path, codex_cli):
    """Train, validate, encode, and decode with the CLI."""

    pytest.importorskip("tokenizers")

    runner = _runner()
    corpus = tmp_path / "corpus.txt"
    corpus.write_text("hello codex\nhello world\n", encoding="utf-8")

    out_dir = tmp_path / "artifacts"
    config_path = tmp_path / "tokenizer.yaml"
    config_path.write_text(
        "\n".join(
            [
                "tokenization:",
                f"  corpus_glob: {corpus}",
                "  model_type: bpe",
                "  vocab_size: 64",
                "  character_coverage: 0.9995",
                "  seed: 7",
                "  workers: 1",
                f"  out_dir: {out_dir}",
                "  name: cli",
                "  streaming: true",
                "  stream_chunk_size: 64",
                "  dry_run: false",
            ]
        ),
        encoding="utf-8",
    )

    train_result = runner.invoke(
        codex_cli.codex, ["tokenizer", "train", "--config", str(config_path)]
    )
    assert train_result.exit_code == 0
    assert "tokenizer artifacts written to" in train_result.output

    model_dir = out_dir / "cli"
    tokenizer_json = model_dir / "tokenizer.json"
    manifest_path = model_dir / "manifest.json"
    assert tokenizer_json.exists()
    assert manifest_path.exists()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    config_manifest = manifest.get("config", {})
    assert config_manifest.get("stream_chunk_size") == 64
    assert config_manifest.get("streaming") is True

    validate_result = runner.invoke(
        codex_cli.codex, ["tokenizer", "validate", "--config", str(config_path)]
    )
    assert validate_result.exit_code == 0
    report = json.loads(validate_result.output)
    assert report["tokenizer_exists"]
    assert report["manifest_exists"]
    assert report["manifest"]["hash"]
    assert report["provenance_path"].endswith("provenance")

    encode_result = runner.invoke(
        codex_cli.codex,
        ["tokenizer", "encode", "hello codex", "--tokenizer-path", str(tokenizer_json)],
        catch_exceptions=False,
    )
    assert encode_result.exit_code == 0
    encoded_ids = encode_result.output.strip().split()
    assert encoded_ids

    decode_result = runner.invoke(
        codex_cli.codex,
        [
            "tokenizer",
            "decode",
            *encoded_ids,
            "--tokenizer-path",
            str(tokenizer_json),
        ],
        catch_exceptions=False,
    )
    assert decode_result.exit_code == 0
    assert decode_result.output.strip() == "hello codex"


def test_root_cli_help_lists_commands() -> None:
    runner = _runner()
    result = runner.invoke(codex_root_cli, [])
    assert result.exit_code == 0
    assert "Available subcommands:" in result.output
    for expected in {"logs", "tasks", "run"}:
        assert expected in result.output
    assert "ALLOWED_TASKS" in result.output


def test_root_cli_invalid_command_exits_non_zero() -> None:
    runner = _runner()
    result = runner.invoke(codex_root_cli, ["__missing__"])
    assert result.exit_code != 0
    assert "No such command" in result.output or "Unexpected extra arguments" in result.output


def test_logs_group_help_lists_commands() -> None:
    runner = _runner()
    result = runner.invoke(codex_logs_group, [])
    assert result.exit_code == 0
    assert "Available subcommands:" in result.output
    for expected in {"init", "ingest", "query"}:
        assert expected in result.output


def test_logs_group_invalid_command_exits_non_zero() -> None:
    runner = _runner()
    result = runner.invoke(codex_logs_group, ["__missing__"])
    assert result.exit_code != 0
    assert "No such command" in result.output or "Unexpected extra arguments" in result.output
