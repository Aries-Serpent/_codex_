from __future__ import annotations

import click

from codex_ml.telemetry import start_metrics_server


@click.group()
def codex() -> None:
    """Codex command line interface."""


@codex.command()
@click.option("--text", multiple=True, help="Training texts")
def train(text: list[str]):
    if not text:
        click.echo("no texts provided")
        return
    model = "sshleifer/tiny-gpt2"
    from transformers import AutoModelForCausalLM, AutoTokenizer

    from training.functional_training import TrainCfg, run_custom_trainer

    tokenizer = AutoTokenizer.from_pretrained(model)
    model = AutoModelForCausalLM.from_pretrained(model)
    cfg = TrainCfg(epochs=1, batch_size=1)
    run_custom_trainer(model, tokenizer, text, None, cfg)
    click.echo("train done")


@codex.command("metrics-server")
@click.option("--port", default=8000, show_default=True)
def metrics_server(port: int) -> None:
    if start_metrics_server(port=port):
        click.echo(f"metrics server running on {port}")
    else:
        click.echo("prometheus_client missing", err=True)


@codex.command()
@click.argument("text")
def tokenize(text: str):
    from codex_ml.tokenization.hf_tokenizer import HFTokenizerAdapter

    tok = HFTokenizerAdapter.load()
    ids = tok.encode(text)
    click.echo(str(ids))


@codex.command()
def repo_map():
    click.echo("repo map not implemented")


@codex.command()
@click.option("--dataset", default="dummy")
def evaluate(dataset: str):
    click.echo(f"evaluate {dataset} not implemented")


if __name__ == "__main__":  # pragma: no cover
    codex()
