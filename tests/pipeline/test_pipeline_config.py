import json
import logging
import os
from copy import deepcopy

import pytest

pytest.importorskip("omegaconf")

from codex_ml.pipeline import run_codex_pipeline_from_config


@pytest.fixture()
def sample_config():
    return {
        "corpus": ["def foo(): return 1", "print('hello')"],
        "demos": [
            {"prompt": "Explain foo", "completion": "Describe the return value."},
            {
                "prompt": "Describe greeting",
                "completion": "Mention the print statement and output.",
            },
        ],
        "pairwise": [
            {
                "label": "safety",
                "chosen": "Provide remediation steps",
                "rejected": "Suggest deleting prod",
                "preference": 1,
            }
        ],
        "weights": {"alpha": 1.0, "beta": 1.1, "gamma": 0.05},
        "pretraining": {"model_size": "tiny", "context_length": 128},
        "sft": {"batch_size": 4, "learning_rate": 1e-4, "epochs": 1},
        "rlhf": {"algorithm": "heuristic", "kl_penalty": 0.05, "ppo_epochs": 1},
        "validation": {
            "syntax_ok": 0.5,
            "logic_ok": 0.5,
            "security_ok": 0.5,
            "perf_ok": 0.4,
        },
        "synth_prompts": ["Summarise the deployment log", "Create a release checklist"],
        "components": {
            "tokenizer": "codex_ml.interfaces.tokenizer:WhitespaceTokenizer",
        },
        "log_summary": False,
    }


def test_pipeline_config_writes_summary(tmp_path, monkeypatch, sample_config):
    monkeypatch.setenv("CODEX_TOKENIZER_PATH", "original")
    summary_path = tmp_path / "summary.json"
    result = run_codex_pipeline_from_config(
        sample_config,
        seed=321,
        summary_path=str(summary_path),
    )

    assert summary_path.exists()
    assert json.loads(summary_path.read_text()) == result
    assert result["seed"] == 321
    assert os.getenv("CODEX_TOKENIZER_PATH") == "original"


def test_pipeline_config_seed_is_reproducible(sample_config):
    first = run_codex_pipeline_from_config(deepcopy(sample_config), seed=7)
    second = run_codex_pipeline_from_config(deepcopy(sample_config), seed=11)
    third = run_codex_pipeline_from_config(deepcopy(sample_config), seed=7)

    assert first["synthetic_responses"] != second["synthetic_responses"]
    assert first["synthetic_responses"] == third["synthetic_responses"]


def test_pipeline_config_respects_log_summary_toggle(caplog, sample_config):
    caplog.set_level(logging.DEBUG, logger="codex_ml.pipeline")
    run_codex_pipeline_from_config(deepcopy(sample_config), log_summary=False)

    info_records = [
        record
        for record in caplog.records
        if record.levelno == logging.INFO and "codex_pipeline_summary" in record.message
    ]
    debug_records = [
        record
        for record in caplog.records
        if record.levelno == logging.DEBUG and "codex_pipeline_summary" in record.message
    ]

    assert not info_records
    assert debug_records


def test_pipeline_config_rejects_invalid_log_summary(sample_config):
    cfg = deepcopy(sample_config)
    cfg["log_summary"] = "sometimes"
    with pytest.raises(ValueError, match="log_summary must be a boolean value"):
        run_codex_pipeline_from_config(cfg)


@pytest.mark.parametrize(
    "field, value",
    [
        ("corpus", []),
        ("demos", []),
        ("pairwise", []),
        ("weights", {"alpha": -1}),
    ],
)
def test_pipeline_config_validation(field, value, sample_config):
    cfg = deepcopy(sample_config)
    cfg[field] = value
    with pytest.raises(ValueError):
        run_codex_pipeline_from_config(cfg)


def test_pipeline_config_rejects_non_serialisable_component_kwargs(sample_config):
    cfg = deepcopy(sample_config)
    cfg["components"] = {
        "tokenizer": {
            "path": "codex_ml.interfaces.tokenizer:WhitespaceTokenizer",
            "kwargs": {"bad": object()},
        }
    }

    with pytest.raises(
        ValueError,
        match="components.tokenizer.kwargs must be JSON serialisable",
    ):
        run_codex_pipeline_from_config(cfg)
