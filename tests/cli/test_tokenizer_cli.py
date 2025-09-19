import json
from types import SimpleNamespace

import pytest
from click.testing import CliRunner

codex_cli = pytest.importorskip("codex_ml.cli.codex_cli")


def _patch_tokenizer_pipeline(monkeypatch, *, error_cls=RuntimeError, **methods):
    pipeline = SimpleNamespace(**methods)
    pipeline.TokenizerPipelineError = error_cls
    monkeypatch.setattr(codex_cli, "_get_tokenizer_pipeline", lambda: pipeline)
    return pipeline


def _runner() -> CliRunner:
    return CliRunner()


def test_tokenizer_train_cli_invokes_pipeline(monkeypatch, tmp_path):
    calls: list[tuple[str, int | None, bool]] = []

    def fake_run_train(config: str, stream_chunk_size=None, dry_run=False):
        calls.append((config, stream_chunk_size, dry_run))
        return tmp_path / "artifacts"

    _patch_tokenizer_pipeline(monkeypatch, run_train=fake_run_train)

    runner = _runner()
    config_path = tmp_path / "cfg.yaml"
    config_path.write_text("tokenization: {}\n", encoding="utf-8")
    result = runner.invoke(
        codex_cli.codex,
        ["tokenizer", "train", "--config", str(config_path), "--stream-chunk-size", "4096"],
    )
    assert result.exit_code == 0
    assert calls == [(str(config_path), 4096, False)]
    assert "tokenizer artifacts written" in result.output

    result_dry_run = runner.invoke(
        codex_cli.codex,
        ["tokenizer", "train", "--config", str(config_path), "--dry-run"],
    )
    assert result_dry_run.exit_code == 0
    assert calls[-1] == (str(config_path), None, True)
    assert "dry run complete" in result_dry_run.output


def test_tokenizer_validate_cli_prints_json(monkeypatch, tmp_path):
    report = {"files": ["a.txt"], "num_files": 1, "missing_files": []}

    def fake_run_validate(config: str):
        assert config == str(config_path)
        return report

    _patch_tokenizer_pipeline(monkeypatch, run_validate=fake_run_validate)

    runner = _runner()
    config_path = tmp_path / "cfg.yaml"
    config_path.write_text("tokenization: {}\n", encoding="utf-8")
    result = runner.invoke(codex_cli.codex, ["tokenizer", "validate", "--config", str(config_path)])
    assert result.exit_code == 0
    assert json.loads(result.output) == report


def test_tokenizer_encode_cli(monkeypatch):
    captured: list[tuple[str, str]] = []

    def fake_run_encode(path: str, text: str):
        captured.append((path, text))
        return [1, 2, 3]

    _patch_tokenizer_pipeline(monkeypatch, run_encode=fake_run_encode)

    runner = _runner()
    result = runner.invoke(
        codex_cli.codex, ["tokenizer", "encode", "hello"], catch_exceptions=False
    )
    assert result.exit_code == 0
    assert captured == [(codex_cli.DEFAULT_TOKENIZER_JSON, "hello")]
    assert result.output.strip() == "1 2 3"

    # stdin fallback
    result_stdin = runner.invoke(codex_cli.codex, ["tokenizer", "encode"], input="hi there")
    assert result_stdin.exit_code == 0
    assert captured[-1] == (codex_cli.DEFAULT_TOKENIZER_JSON, "hi there")


def test_tokenizer_decode_cli(monkeypatch):
    captured: list[tuple[str, tuple[int, ...]]] = []

    def fake_run_decode(path: str, token_ids: tuple[int, ...]):
        captured.append((path, token_ids))
        return "decoded"

    _patch_tokenizer_pipeline(monkeypatch, run_decode=fake_run_decode)

    runner = _runner()
    result = runner.invoke(
        codex_cli.codex,
        ["tokenizer", "decode", "1", "2", "3", "--tokenizer-path", "tok.json"],
    )
    assert result.exit_code == 0
    assert captured == [("tok.json", (1, 2, 3))]
    assert result.output.strip() == "decoded"

    result_stdin = runner.invoke(codex_cli.codex, ["tokenizer", "decode"], input="4 5 6\n")
    assert result_stdin.exit_code == 0
    assert captured[-1] == (codex_cli.DEFAULT_TOKENIZER_JSON, (4, 5, 6))


def test_tokenizer_cli_error_propagation(monkeypatch):
    class BoomError(Exception):
        pass

    def raising_encode(path: str, text: str):
        raise BoomError("boom")

    _patch_tokenizer_pipeline(monkeypatch, run_encode=raising_encode, error_cls=BoomError)

    runner = _runner()
    result = runner.invoke(codex_cli.codex, ["tokenizer", "encode", "oops"])
    assert result.exit_code != 0
    assert "boom" in result.output
