from __future__ import annotations

import pytest

transformers = pytest.importorskip("transformers")

from codex_ml.models.registry import get_model  # noqa: E402
from codex_ml.plugins.registries import models as plugin_models  # noqa: E402

GPT2Config = transformers.GPT2Config
GPT2LMHeadModel = transformers.GPT2LMHeadModel
LlamaConfig = transformers.LlamaConfig
LlamaForCausalLM = transformers.LlamaForCausalLM


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_gpt2_offline_loads_local_checkpoint(tmp_path):
    target = tmp_path / "gpt2"
    config = GPT2Config(
        vocab_size=32,
        n_positions=32,
        n_ctx=32,
        n_embd=32,
        n_layer=1,
        n_head=4,
        bos_token_id=0,
        eos_token_id=1,
    )
    model = GPT2LMHeadModel(config)
    model.save_pretrained(target)

    loaded = get_model("gpt2-offline", {"local_path": str(target)})
    assert isinstance(loaded, GPT2LMHeadModel)
    assert loaded.config.vocab_size == 32


def test_gpt2_offline_missing_path(tmp_path):
    missing = tmp_path / "missing"
    with pytest.raises(FileNotFoundError):
        get_model("gpt2-offline", {"local_path": str(missing)})


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_plugin_catalogue_gpt2_offline(tmp_path):
    target = tmp_path / "gpt2"
    config = GPT2Config(
        vocab_size=32,
        n_positions=32,
        n_ctx=32,
        n_embd=32,
        n_layer=1,
        n_head=4,
        bos_token_id=0,
        eos_token_id=1,
    )
    model = GPT2LMHeadModel(config)
    model.save_pretrained(target)

    loaded = plugin_models.resolve_and_instantiate("gpt2-offline", {"local_path": str(target)})
    assert isinstance(loaded, GPT2LMHeadModel)


def test_plugin_catalogue_gpt2_offline_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        plugin_models.resolve_and_instantiate(
            "gpt2-offline", {"local_path": str(tmp_path / "missing")}
        )


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_tinyllama_offline_loads_local_checkpoint(tmp_path):
    target = tmp_path / "tinyllama"
    config = LlamaConfig(
        vocab_size=48,
        hidden_size=64,
        intermediate_size=128,
        num_hidden_layers=1,
        num_attention_heads=4,
        num_key_value_heads=4,
        max_position_embeddings=32,
        rms_norm_eps=1e-5,
        pad_token_id=0,
        bos_token_id=1,
        eos_token_id=2,
    )
    model = LlamaForCausalLM(config)
    model.save_pretrained(target)

    loaded = get_model("tinyllama-offline", {"local_path": str(target)})
    assert isinstance(loaded, LlamaForCausalLM)
    assert loaded.config.hidden_size == 64


def test_tinyllama_offline_missing_path(tmp_path):
    missing = tmp_path / "missing"
    with pytest.raises(FileNotFoundError):
        get_model("tinyllama-offline", {"local_path": str(missing)})


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_plugin_catalogue_tinyllama_offline(tmp_path):
    target = tmp_path / "tinyllama"
    config = LlamaConfig(
        vocab_size=48,
        hidden_size=64,
        intermediate_size=128,
        num_hidden_layers=1,
        num_attention_heads=4,
        num_key_value_heads=4,
        max_position_embeddings=32,
        rms_norm_eps=1e-5,
        pad_token_id=0,
        bos_token_id=1,
        eos_token_id=2,
    )
    model = LlamaForCausalLM(config)
    model.save_pretrained(target)

    loaded = plugin_models.resolve_and_instantiate("tinyllama-offline", {"local_path": str(target)})
    assert isinstance(loaded, LlamaForCausalLM)


def test_plugin_catalogue_tinyllama_offline_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        plugin_models.resolve_and_instantiate(
            "tinyllama-offline",
            {"local_path": str(tmp_path / "missing")},
        )


def test_plugins_cli_lists_offline_models():
    pytest.importorskip("typer")
    from typer.testing import CliRunner

    from codex_ml.cli import plugins_cli

    runner = CliRunner()
    result = runner.invoke(plugins_cli.app, ["list", "models"])
    assert result.exit_code == 0
    output = result.stdout.splitlines()
    assert any("gpt2-offline" in line for line in output)
    assert any("tinyllama-offline" in line for line in output)
