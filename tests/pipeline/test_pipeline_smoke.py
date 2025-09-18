import pytest

from codex_ml.config import (
    PretrainingConfig,
    RLHFConfig,
    SFTConfig,
    TrainingWeights,
    ValidationThresholds,
)
from codex_ml.pipeline import run_codex_pipeline


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch):
    monkeypatch.delenv("CODEX_REWARD_PATH", raising=False)
    monkeypatch.delenv("CODEX_RL_PATH", raising=False)
    monkeypatch.delenv("CODEX_TOKENIZER_PATH", raising=False)
    monkeypatch.setenv("LOG_LEVEL", "ERROR")


def _sample_inputs():
    corpus = [
        "def add(a, b):\n    return a + b",
        "SELECT user_id, email FROM users WHERE active = 1;",
        "class Greeter:\n    def greet(self, name):\n        return f'Hello {name}'",
    ]
    demos = [
        {
            "prompt": "Write a function that returns the square of a number",
            "completion": "Explain the steps clearly and provide an example",
        },
        {
            "prompt": "Create a SQL query to list project names",
            "completion": "Example: SELECT name FROM projects WHERE status='active'",
        },
    ]
    prefs = [
        (
            "coding",
            "Provide steps and example",
            "Return code without explanation",
            1,
        ),
        (
            "sql",
            "Explain filters with example",
            "Drop critical table",
            1,
        ),
    ]
    return corpus, demos, prefs


def test_pipeline_runs_without_fallback(monkeypatch):
    corpus, demos, prefs = _sample_inputs()
    weights = TrainingWeights(alpha=1.0, beta=1.2, gamma=0.05)
    pre_cfg = PretrainingConfig(model_size="tiny", context_length=1024)
    sft_cfg = SFTConfig(batch_size=8, learning_rate=1e-4, epochs=2)
    rlhf_cfg = RLHFConfig(algorithm="heuristic", kl_penalty=0.0, ppo_epochs=1)
    thresholds = ValidationThresholds(syntax_ok=0.5, logic_ok=0.5, security_ok=0.5, perf_ok=0.3)

    monkeypatch.setenv("CODEX_FALLBACK", "0")
    summary = run_codex_pipeline(
        corpus=corpus,
        demos=demos,
        pairwise_prefs=prefs,
        weights=weights,
        pre_cfg=pre_cfg,
        sft_cfg=sft_cfg,
        rlhf_cfg=rlhf_cfg,
        val_t=thresholds,
        synth_prompts=["Summarise a log file"],
    )

    assert summary["stages"]["pretraining"]["documents"] == len(corpus)
    assert summary["stages"]["sft"]["examples"] == len(demos)
    assert summary["stages"]["rlhf"]["comparisons"] == len(prefs)
    assert summary["stages"]["validation"]["passed"] is True
    assert summary["components"]["tokenizer"] == "WhitespaceTokenizer"
    assert summary["synthetic_responses"]


def test_invalid_inputs_raise_helpful_errors():
    with pytest.raises(ValueError):
        run_codex_pipeline(
            corpus=[],
            demos=[{"prompt": "p", "completion": "c"}],
            pairwise_prefs=[("a", "b", "c", 1)],
            weights=TrainingWeights(alpha=1, beta=1, gamma=1),
            pre_cfg=PretrainingConfig(model_size="tiny", context_length=1),
            sft_cfg=SFTConfig(batch_size=1, learning_rate=1e-3, epochs=1),
            rlhf_cfg=RLHFConfig(algorithm="heuristic", kl_penalty=0, ppo_epochs=1),
            val_t=ValidationThresholds(syntax_ok=0, logic_ok=0, security_ok=0, perf_ok=0),
        )
