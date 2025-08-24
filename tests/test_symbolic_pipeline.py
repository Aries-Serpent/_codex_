import math

import pytest

from codex_ml.symbolic_pipeline import (
    PretrainCfg,
    RLHFCfg,
    SFTCfg,
    Weights,
    loss_sft,
    pretrain,
    run_codex_symbolic_pipeline,
    sft,
    train_reward_model,
)


def _basic_data():
    corpus = ["a b", "b c"]
    demos = [{"prompt": "p", "completion": "a b"}]
    prefs = [("p", "a b", "b c", 1)]
    return corpus, demos, prefs


def test_pipeline_reproducible():
    corpus, demos, prefs = _basic_data()
    cfgs = dict(
        pre_cfg=PretrainCfg(seed=0),
        sft_cfg=SFTCfg(seed=0, batch_size=1),
        rlhf_cfg=RLHFCfg(seed=0),
        w=Weights(),
    )
    summary1 = run_codex_symbolic_pipeline(
        corpus=corpus, demos=demos, prefs=prefs, **cfgs
    )
    summary2 = run_codex_symbolic_pipeline(
        corpus=corpus, demos=demos, prefs=prefs, **cfgs
    )
    assert summary1 == summary2


def test_pretrain_empty_corpus_raises():
    with pytest.raises(ValueError):
        run_codex_symbolic_pipeline(
            corpus=[],
            demos=[{"prompt": "p", "completion": "a"}],
            prefs=[("p", "a", "b", 1)],
        )


def test_invalid_config():
    with pytest.raises(ValueError):
        PretrainCfg(lr=-1.0)


def test_reward_model_accuracy_and_loss():
    corpus, demos, prefs = _basic_data()
    model = pretrain(corpus, PretrainCfg(seed=0))
    model = sft(model, demos, SFTCfg(seed=0, batch_size=1))
    rm = train_reward_model(prefs, model)
    assert rm.meta["accuracy"] == 1.0
    computed = loss_sft(model, demos)
    manual = -sum(math.log(model.meta["token_probs"][t]) for t in ["a", "b"]) / 2
    assert math.isclose(computed, manual)
