import pytest

from codex_ml.symbolic_pipeline import (
    PretrainCfg,
    RLHFCfg,
    SFTCfg,
    Weights,
    run_codex_symbolic_pipeline,
)


def _toy_data():
    corpus = ["def foo():\n    return 1", "print('hello')"]
    demos = [
        {"prompt": "a", "completion": "b"},
        {"prompt": "c", "completion": "d"},
    ]
    prefs = [("p", "a", "b", 1)]
    return corpus, demos, prefs


def test_pipeline_deterministic_and_losses_positive():
    corpus, demos, prefs = _toy_data()
    summary1 = run_codex_symbolic_pipeline(
        corpus=corpus,
        demos=demos,
        prefs=prefs,
        w=Weights(alpha=0.4, beta=0.4, gamma=0.2),
        pre_cfg=PretrainCfg(),
        sft_cfg=SFTCfg(),
        rlhf_cfg=RLHFCfg(),
    )
    summary2 = run_codex_symbolic_pipeline(
        corpus=corpus,
        demos=demos,
        prefs=prefs,
        w=Weights(alpha=0.4, beta=0.4, gamma=0.2),
        pre_cfg=PretrainCfg(),
        sft_cfg=SFTCfg(),
        rlhf_cfg=RLHFCfg(),
    )
    assert summary1 == summary2
    losses = summary1["losses"]
    for value in losses.values():
        assert value >= 0


def test_pipeline_empty_inputs_error():
    corpus, demos, prefs = _toy_data()
    with pytest.raises(ValueError):
        run_codex_symbolic_pipeline(corpus=[], demos=demos, prefs=prefs)
    with pytest.raises(ValueError):
        run_codex_symbolic_pipeline(corpus=corpus, demos=[], prefs=prefs)
    with pytest.raises(ValueError):
        run_codex_symbolic_pipeline(corpus=corpus, demos=demos, prefs=[])


def test_bad_config_validation():
    corpus, demos, prefs = _toy_data()
    with pytest.raises(ValueError):
        PretrainCfg(epochs=0)
    with pytest.raises(ValueError):
        SFTCfg(lr=-1)
    with pytest.raises(ValueError):
        RLHFCfg(lr=-0.5)
    # Ensure valid config runs
    summary = run_codex_symbolic_pipeline(
        corpus=corpus,
        demos=demos,
        prefs=prefs,
        pre_cfg=PretrainCfg(),
        sft_cfg=SFTCfg(),
        rlhf_cfg=RLHFCfg(),
    )
    assert "objective_U" in summary
