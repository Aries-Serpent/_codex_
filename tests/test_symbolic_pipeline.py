import random

from codex_ml.symbolic_pipeline import (
    PretrainCfg,
    RLHFCfg,
    SFTCfg,
    Weights,
    run_codex_symbolic_pipeline,
)


def test_run_codex_symbolic_pipeline_losses_and_objective_bounded():
    random.seed(0)
    corpus = ["def foo():\n    pass", "print('hello')"]
    demos = [
        {"prompt": "a", "completion": "b"},
        {"prompt": "c", "completion": "d"},
    ]
    prefs = [("p", "a", "b", 1)]

    summary = run_codex_symbolic_pipeline(
        corpus=corpus,
        demos=demos,
        prefs=prefs,
        w=Weights(alpha=0.4, beta=0.4, gamma=0.2),
        pre_cfg=PretrainCfg(),
        sft_cfg=SFTCfg(),
        rlhf_cfg=RLHFCfg(),
    )

    losses = summary["losses"]
    for name in ("L_SFT", "L_RLHF", "Omega"):
        assert 0 <= losses[name] <= 1
    assert 0 <= summary["objective_U"] <= 1
