import os
import random
import sys
from types import SimpleNamespace

import pytest

from codex_ml.eval import metrics as M
from codex_ml.interfaces import get_component
from codex_ml.monitoring import codex_logging as cl
from codex_ml.utils import set_reproducible
from codex_ml.utils.checkpointing import load_training_checkpoint, save_checkpoint


# Checkpoint integrity test
def test_checkpoint_integrity(tmp_path):
    torch = pytest.importorskip("torch")
    model = torch.nn.Linear(1, 1)
    opt = torch.optim.SGD(model.parameters(), lr=0.1)
    ckpt = tmp_path / "model.pt"
    save_checkpoint(str(ckpt), model, opt, scheduler=None, epoch=1, extra={})
    ckpt.write_bytes(b"corrupt")
    with pytest.raises(RuntimeError, match="checksum mismatch"):
        load_training_checkpoint(str(ckpt), model, opt)


# Metrics correctness
def test_metrics_correctness():
    import math

    ppl = M.perplexity([math.log(4), math.log(4)], [0, 1], from_logits=False)
    assert ppl == pytest.approx(4.0)
    acc = M.token_accuracy([1, 2, 3], [1, 2, 0], ignore_index=0)
    assert acc == pytest.approx(2 / 2)

    pytest.importorskip("nltk")
    score = M.bleu(["a b"], ["a b"])
    assert score == pytest.approx(1.0)

    pytest.importorskip("rouge_score")
    r = M.rouge_l(["a b c"], ["a b c"])
    assert r is not None and r["rougeL_f"] == pytest.approx(1.0)


# Reproducibility test
def test_set_reproducible_repeatable():
    torch = pytest.importorskip("torch")
    set_reproducible(123)
    py1 = random.random()
    np1 = pytest.importorskip("numpy").random.rand()
    t1 = torch.rand(1)

    set_reproducible(123)
    assert py1 == random.random()
    assert np1 == pytest.importorskip("numpy").random.rand()
    assert torch.allclose(t1, torch.rand(1))


# Logging initialization
def test_logging_initialization(monkeypatch, tmp_path):
    calls = {}

    class DummyWriter:
        def __init__(self, logdir):
            calls["tb"] = logdir

        def add_scalar(self, *args, **kwargs):
            pass

    monkeypatch.setattr(cl, "SummaryWriter", DummyWriter)
    monkeypatch.setattr(cl, "wandb", SimpleNamespace(init=lambda **kw: calls.setdefault("wb", kw)))
    dummy_mlflow = SimpleNamespace(
        set_tracking_uri=lambda uri: calls.setdefault("ml_uri", uri),
        set_experiment=lambda exp: calls.setdefault("ml_exp", exp),
        start_run=lambda: calls.setdefault("ml_run", True),
    )
    monkeypatch.setattr(cl, "mlflow", dummy_mlflow)

    cfg = {
        "tensorboard": {"enable": True, "logdir": str(tmp_path)},
        "wandb": {"enable": True, "project": "proj"},
        "mlflow": {"enable": True, "tracking_uri": "uri", "experiment": "exp"},
    }
    loggers = cl._codex_logging_bootstrap(SimpleNamespace(hydra_cfg=cfg))
    assert isinstance(loggers.tb, DummyWriter)
    assert calls["wb"]["mode"] == "offline" and calls["wb"]["project"] == "proj"
    assert calls["ml_uri"] == "uri" and calls["ml_exp"] == "exp"


# Interface loader


def test_interface_loader_env(tmp_path):
    module = tmp_path / "dummy_tok.py"
    module.write_text("class Tok:\n    def __init__(self):\n        self.ok = True\n")
    sys.path.insert(0, str(tmp_path))
    os.environ["CODEX_TOKENIZER_PATH"] = "dummy_tok:Tok"
    try:
        inst = get_component("CODEX_TOKENIZER_PATH", "dummy_tok:Tok")
        assert inst.ok
    finally:
        sys.path.remove(str(tmp_path))
        os.environ.pop("CODEX_TOKENIZER_PATH", None)
