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
    assert rec["run_id"] == "explicit-123"
    assert rec["metrics"]["acc"] == 0.88
    assert "timestamp" in rec
