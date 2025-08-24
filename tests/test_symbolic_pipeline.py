import math

import pytest

from codex_ml.symbolic_pipeline import (
    PretrainCfg,
    RLHFCfg,
    SFTCfg,
    Weights,
    loss_sft,
    pretrain,
    rlhf_ppo,
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


def test_sft_empty_demos_raises():
    model = pretrain(["a"], PretrainCfg(seed=0))
    with pytest.raises(ValueError):
        sft(model, [], SFTCfg(seed=0))


def test_train_reward_model_empty_prefs_raises():
    model = pretrain(["a"], PretrainCfg(seed=0))
    with pytest.raises(ValueError):
        train_reward_model([], model)


def test_rlhf_missing_prefs_raises():
    model = pretrain(["a"], PretrainCfg(seed=0))
    model = sft(model, [{"prompt": "p", "completion": "a"}], SFTCfg(seed=0))
    rm = train_reward_model([("p", "a", "b", 1)], model)
    rm.meta.pop("prefs")
    with pytest.raises(ValueError):
        rlhf_ppo(model, rm, RLHFCfg(seed=0))


def test_rlhf_cfg_invalid():
    with pytest.raises(ValueError):
        RLHFCfg(ppo_clip=-0.1)


def test_rlhf_deterministic():
    corpus, demos, prefs = _basic_data()
    M0a = pretrain(corpus, PretrainCfg(seed=0))
    M0b = pretrain(corpus, PretrainCfg(seed=0))
    M1a = sft(M0a, demos, SFTCfg(seed=0, batch_size=1))
    M1b = sft(M0b, demos, SFTCfg(seed=0, batch_size=1))
    rm = train_reward_model(prefs, M1a)
    M2a = rlhf_ppo(M1a, rm, RLHFCfg(seed=0))
    M2b = rlhf_ppo(M1b, rm, RLHFCfg(seed=0))
    assert M2a.meta["token_probs"] == M2b.meta["token_probs"]
