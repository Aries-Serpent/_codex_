"""
Test Evaluate Cli Flags

Test module for evaluate cli flags.
"""

from __future__ import annotations

import json
import sys
import types

from click.testing import CliRunner


def _stub_settings() -> None:
    if "codex_ml.config.settings" in sys.modules:
        return
    module = types.ModuleType("codex_ml.config.settings")

    class _StubSettings:
        pass

    class _StubEvalRow:
        @staticmethod
        def model_json_schema() -> dict:
            return {}

    def _schema() -> dict:
        return {}

    def _get() -> _StubSettings:
        return _StubSettings()

    module.AppSettings = _StubSettings
    module.EvalRow = _StubEvalRow
    module.eval_row_schema = _schema  # type: ignore[attr-defined]
    module.get_settings = _get  # type: ignore[attr-defined]
    sys.modules["codex_ml.config.settings"] = module


def _stub_runner() -> None:
    module = types.ModuleType("codex_ml.eval.runner")

    class RunnerEvaluationError(Exception):
        pass

    def run(_eval_cfg, data_cfg=None):
        return {
            "metrics": {"f1": 0.77, "acc": 0.88},
            "num_records": 42,
            "run_id": "from-summary",
        }

    module.EvaluationError = RunnerEvaluationError  # type: ignore[attr-defined]
    module.run_evaluation = run  # type: ignore[attr-defined]
    sys.modules["codex_ml.eval.runner"] = module


def test_metrics_only_and_run_id(tmp_path, monkeypatch) -> None:
    _stub_settings()
    _stub_runner()

    # Import after stubs
    import codex_ml.cli.codex_cli as cli
    from codex_ml.cli.codex_cli import codex

    class _EvalCfg:
        dataset_path = "data/val.jsonl"
        output_dir = ".codex/eval"

    class _DataCfg:
        pass

    class _Cfg:
        evaluation = _EvalCfg()
        data = _DataCfg()

    def fake_load(config, overrides):
        return _Cfg(), {"ok": True}

    monkeypatch.setattr(cli, "load_app_config", fake_load, raising=True)

    out = tmp_path / "m.ndjson"
    runner = CliRunner()

    # metrics-only prints only the metrics mapping
    res = runner.invoke(codex, ["evaluate", "--config", "x.yaml", "--metrics-only"])
    assert res.exit_code == 0, res.output
    obj = json.loads(res.output)
    assert set(obj.keys()) == {"f1", "acc"}

    # run-id flag is honored and present in NDJSON record
    res = runner.invoke(
        codex,
        [
            "evaluate",
            "--config",
            "x.yaml",
            "--run-id",
            "explicit-123",
            "--log-metrics",
            str(out),
        ],
    )
    assert res.exit_code == 0, res.output
    line = out.read_text().strip().splitlines()[-1]
    rec = json.loads(line)
    assert rec["run_id"] == "explicit-123", "Condition must be true"
    assert rec["metrics"]["acc"] == 0.88, "Condition must be true"
    assert "timestamp" in rec, "Condition must be true"


def test_metrics_sink_flags(tmp_path, monkeypatch) -> None:
    _stub_settings()
    _stub_runner()

    import codex_ml.cli.codex_cli as cli
    from codex_ml.cli.codex_cli import codex

    class _EvalCfg:
        def __init__(self) -> None:
            self.dataset_path = "data/val.jsonl"
            self.output_dir = ".codex/eval"
            self.metrics_sink = "none"
            self.metrics_sink_path: str | None = None

    class _DataCfg:
        pass

    eval_cfg = _EvalCfg()

    class _Cfg:
        evaluation = eval_cfg
        data = _DataCfg()

    def fake_load(config, overrides):
        return _Cfg(), {"ok": True}

    monkeypatch.setattr(cli, "load_app_config", fake_load, raising=True)

    metrics_path = tmp_path / "secondary.csv"
    runner = CliRunner()
    res = runner.invoke(
        codex,
        [
            "evaluate",
            "--config",
            "x.yaml",
            "--metrics-sink",
            "csv",
            "--metrics-path",
            str(metrics_path),
        ],
    )
    assert res.exit_code == 0, res.output
    assert eval_cfg.metrics_sink == "csv", "metrics_sink is not valid"
    assert eval_cfg.metrics_sink_path == str(metrics_path), "metrics_sink_path is not valid"
