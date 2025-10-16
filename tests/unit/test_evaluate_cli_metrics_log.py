from __future__ import annotations

import json
import sys
import types

from click.testing import CliRunner


def _stub_settings_module() -> None:
    """Provide a minimal settings stub so CLI imports don't require full deps."""
    if "codex_ml.config.settings" in sys.modules:
        return
    m = types.ModuleType("codex_ml.config.settings")

    class _StubAppSettings:  # pragma: no cover
        ...

    class _StubEvalRow:  # pragma: no cover
        @staticmethod
        def model_json_schema() -> dict:
            return {}

    def _eval_row_schema() -> dict:
        return {}

    def _get_settings() -> _StubAppSettings:
        return _StubAppSettings()

    m.AppSettings = _StubAppSettings
    m.EvalRow = _StubEvalRow
    m.eval_row_schema = _eval_row_schema  # type: ignore[attr-defined]
    m.get_settings = _get_settings  # type: ignore[attr-defined]
    sys.modules["codex_ml.config.settings"] = m


def test_evaluate_cli_writes_ndjson(tmp_path, monkeypatch) -> None:
    _stub_settings_module()

    # Stub evaluation runner before importing the CLI entry point.
    runner_mod = types.ModuleType("codex_ml.eval.runner")

    class _EvaluationError(Exception): ...

    def fake_run_evaluation(_eval_cfg, data_cfg=None):
        return {"metrics": {"accuracy": 0.9}, "num_records": 5}

    runner_mod.EvaluationError = _EvaluationError  # type: ignore[attr-defined]
    runner_mod.run_evaluation = fake_run_evaluation  # type: ignore[attr-defined]
    sys.modules["codex_ml.eval.runner"] = runner_mod

    # Lazy import after stubbing to avoid import-time deps
    from codex_ml.cli.codex_cli import codex

    class _DummyEvalCfg:
        dataset_path = "data/eval.jsonl"
        output_dir = ".codex/eval"

    class _DummyDataCfg: ...

    class _DummyAppCfg:
        evaluation = _DummyEvalCfg()
        data = _DummyDataCfg()

    def fake_load_app_config(_config, _overrides):
        return _DummyAppCfg(), {"ok": True}

    # Patch loader/runner on the imported module to keep test hermetic
    import codex_ml.cli.codex_cli as cli_mod

    monkeypatch.setenv("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    monkeypatch.setattr(cli_mod, "load_app_config", fake_load_app_config, raising=True)

    out = tmp_path / "metrics.ndjson"
    runner = CliRunner()
    res = runner.invoke(codex, ["evaluate", "--config", "dummy.yaml", "--log-metrics", str(out)])
    assert res.exit_code == 0, res.output
    text = out.read_text(encoding="utf-8").strip()
    assert text, "expected NDJSON content"
    # Quick shape check on the last line
    line = text.splitlines()[-1]
    rec = json.loads(line)
    assert rec.get("metrics", {}).get("accuracy") == 0.9
    assert rec.get("num_records") == 5
    assert "timestamp" in rec

    # dataset_path resolved & config_path absolute
    assert rec.get("dataset_path").endswith("data/eval.jsonl")
    assert rec.get("config_path").endswith("dummy.yaml")
