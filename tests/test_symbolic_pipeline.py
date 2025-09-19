import math

import pytest

py = pytest

try:
    import transformers

    from codex_ml.symbolic_pipeline import (
        ModelHandle,
        PretrainCfg,
        RewardModelCfg,
        RLHFCfg,
        SFTCfg,
        Weights,
        loss_sft,
        pretrain,
        regularizer,
        rlhf_ppo,
        run_codex_symbolic_pipeline,
        sft,
        train_reward_model,
    )
except ImportError as exc:  # pragma: no cover - optional deps missing
    py.skip(f"symbolic pipeline optional dependency missing: {exc}", allow_module_level=True)

py.importorskip("omegaconf")
py.importorskip("torch")

if not hasattr(transformers, "AutoTokenizer"):
    py.skip("transformers AutoTokenizer unavailable", allow_module_level=True)


def _basic_data():
    corpus = ["a b", "b c"]
    demos = [{"prompt": "p", "completion": "a b"}]
    prefs = [("p", "a b", "b c", 1)]
    return corpus, demos, prefs


def test_pipeline_reproducible():
    corpus, demos, prefs = _basic_data()
    cfgs = dict(
        pre_cfg=PretrainCfg(),
        sft_cfg=SFTCfg(batch_size=1),
        rlhf_cfg=RLHFCfg(),
        w=Weights(),
    )
    summary1 = run_codex_symbolic_pipeline(corpus=corpus, demos=demos, prefs=prefs, **cfgs)
    summary2 = run_codex_symbolic_pipeline(corpus=corpus, demos=demos, prefs=prefs, **cfgs)
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


def test_sft_cfg_invalid():
    with pytest.raises(ValueError):
        SFTCfg(lr=0)


def test_invalid_sft_config():
    with pytest.raises(ValueError):
        SFTCfg(lr=0)


def test_reward_model_accuracy_and_loss():
    corpus, demos, prefs = _basic_data()
    model = pretrain(corpus, PretrainCfg())
    model = sft(model, demos, SFTCfg(batch_size=1))
    rm = train_reward_model(prefs, model)
    assert rm.meta["accuracy"] == 1.0
    computed = loss_sft(model, demos)
    manual = -sum(math.log(model.meta["token_probs"][t]) for t in ["a", "b"]) / 2
    assert math.isclose(computed, manual)
    assert model.meta["tokens_seen"] == 4
    assert model.meta["tokens_seen_sft"] == 2


def test_sft_empty_demos_raises():
    model = pretrain(["a"], PretrainCfg())
    with pytest.raises(ValueError):
        sft(model, [], SFTCfg())


def test_train_reward_model_empty_prefs_raises():
    model = pretrain(["a"], PretrainCfg())
    with pytest.raises(ValueError):
        train_reward_model([], model)


def test_pipeline_empty_prefs_raises():
    corpus, demos, _ = _basic_data()
    with pytest.raises(ValueError):
        run_codex_symbolic_pipeline(corpus=corpus, demos=demos, prefs=[])


def test_reward_model_cfg_invalid():
    with pytest.raises(ValueError):
        RewardModelCfg(lr=0)


def test_rlhf_missing_prefs_raises():
    model = pretrain(["a"], PretrainCfg())
    model = sft(model, [{"prompt": "p", "completion": "a"}], SFTCfg())
    rm = train_reward_model([("p", "a", "b", 1)], model)
    rm.meta.pop("prefs")
    with pytest.raises(ValueError):
        rlhf_ppo(model, rm, RLHFCfg())


def test_rlhf_cfg_invalid():
    with pytest.raises(ValueError):
        RLHFCfg(ppo_clip=-0.1)


def test_rlhf_deterministic():
    corpus, demos, prefs = _basic_data()
    M0a = pretrain(corpus, PretrainCfg())
    M0b = pretrain(corpus, PretrainCfg())
    M1a = sft(M0a, demos, SFTCfg(batch_size=1))
    M1b = sft(M0b, demos, SFTCfg(batch_size=1))
    rm = train_reward_model(prefs, M1a)
    M2a = rlhf_ppo(M1a, rm, RLHFCfg())
    M2b = rlhf_ppo(M1b, rm, RLHFCfg())
    assert M2a.meta["token_probs"] == M2b.meta["token_probs"]


def test_reward_model_deterministic():
    corpus, demos, prefs = _basic_data()
    model = pretrain(corpus, PretrainCfg())
    model = sft(model, demos, SFTCfg(batch_size=1))
    rm1 = train_reward_model(prefs, model, RewardModelCfg(seed=0))
    rm2 = train_reward_model(prefs, model, RewardModelCfg(seed=0))
    assert rm1.meta["weights"] == rm2.meta["weights"]


def test_regularizer_penalises_dangerous_tokens():
    safe = ModelHandle(
        "m", "stage", {"token_probs": {"safe": 1.0}, "base_token_probs": {"safe": 1.0}}
    )
    dangerous = ModelHandle(
        "m",
        "stage",
        {"token_probs": {"rm": 1.0}, "base_token_probs": {"rm": 1.0}},
    )
    assert regularizer(safe) == 0.0
    assert regularizer(dangerous) == pytest.approx(1.0)
