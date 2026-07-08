pytest.importorskip("mlflow")
"""
Test Capability Contracts

Test module for capability contracts.
"""

import json
import tarfile

import pytest

from codex_ml.deployment.package import build_service_package
from codex_ml.evaluation.loop import run_metrics_evaluation
from codex_ml.interfaces.contracts import (
    TokenizationContractError,
    TrainingContractError,
    validate_tokenizer_contract,
)
from codex_ml.metrics.writers import CSVMetricsWriter, NDJSONMetricsWriter
from codex_ml.security.runtime import (
    PromptSecurityError,
    SecretNotFoundError,
    load_secret,
    scan_prompt_for_unsafe_content,
)
from codex_ml.tokenization.adapter import WhitespaceTokenizer
from codex_ml.training.loop import train_epoch


def test_tokenizer_contract_enforces_error_modes():
    tokenizer = WhitespaceTokenizer()
    validate_tokenizer_contract(tokenizer)

    with pytest.raises(TypeError):
        tokenizer.encode(123)  # type: ignore[arg-type]

    with pytest.raises(TokenizationContractError):
        validate_tokenizer_contract(object())

    with pytest.raises(ValueError):
        tokenizer.decode(["bad"])  # type: ignore[list-item]


class _BadModel:
    def step(self, batch, state):
        return "not-a-mapping"


class _GoodModel:
    def step(self, batch, state):
        return {"loss": 1.0, "accuracy": 0.5}


def test_training_contract_rejects_bad_step():
    with pytest.raises(TrainingContractError):
        train_epoch(_BadModel(), [{"input_ids": [1, 2]}], state={})

    result = train_epoch(_GoodModel(), [{"input_ids": [1, 2]}, {"input_ids": [3, 4]}], state={})
    assert result["loss_mean"] == 1.0, "Result must not be empty"
    assert result["loss_last"] == 1.0, "Result must not be empty"


def test_run_metrics_evaluation_logs_tags(tmp_path):
    ndjson_path = tmp_path / "metrics.ndjson"
    csv_path = tmp_path / "metrics.csv"

    writers = [
        NDJSONMetricsWriter(ndjson_path, run_id="eval-123"),
        CSVMetricsWriter(csv_path, run_id="eval-123"),
    ]

    summary = run_metrics_evaluation(
        [(1, 1), (0, 1)],
        {
            "simple_accuracy": lambda preds, targets: sum(
                int(p == t) for p, t in zip(preds, targets)
            )
            / len(preds)
        },
        metric_writers=writers,
        run_id="eval-123",
        log_system_metrics=False,
        enable_mlflow=False,
    )

    assert summary["metrics"]["simple_accuracy"] == 0.5, "Condition must be true"

    ndjson_lines = ndjson_path.read_text(encoding="utf-8").splitlines()
    assert any(json.loads(line).get("run_id") == "eval-123" for line in ndjson_lines), "Condition must be true"

    csv_rows = csv_path.read_text(encoding="utf-8").splitlines()
    assert "eval-123" in csv_rows[-1], "Condition must be true"


def test_security_helpers_and_packaging(tmp_path, monkeypatch):
    with pytest.raises(PromptSecurityError):
        scan_prompt_for_unsafe_content("rm -rf /")

    secret_store = tmp_path / "secrets.json"
    secret_store.write_text(json.dumps({"api": "token123"}), encoding="utf-8")
    assert load_secret("api", store_path=secret_store) == "token123"
    with pytest.raises(SecretNotFoundError):
        load_secret("missing", store_path=secret_store)

    model_dir = tmp_path / "model"
    model_dir.mkdir()
    (model_dir / "weights.bin").write_bytes(b"0")

    package_path = tmp_path / "pkg.tar.gz"
    result = build_service_package(model_dir, package_path, metadata={"run_id": "pkg-1"})

    assert package_path.exists(), "Condition must be true"
    assert result["run_id"] == "pkg-1", "Result must not be empty"
    with tarfile.open(package_path, "r:gz") as tar:
        names = tar.getnames()
        assert "manifest.json" in names, "Condition must be true"
        manifest = json.loads(tar.extractfile("manifest.json").read())
        assert manifest["run_id"] == "pkg-1", "Condition must be true"
