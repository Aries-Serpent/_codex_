import importlib.util
import sys
from pathlib import Path


def _load_mlflow_utils():
    here = Path(__file__).resolve()
    repo = here.parents[2]
    path = (repo / "src" / "codex_ml" / "tracking" / "mlflow_utils.py").resolve()
    spec = importlib.util.spec_from_file_location("codex_ml._mlflow_utils_test", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # ensure annotations resolution sees module
    spec.loader.exec_module(mod)  # type: ignore[arg-type]
    return mod


def test_mlflow_default_uri_constant():
    mod = _load_mlflow_utils()
    default_uri = getattr(mod, "MLFLOW_DEFAULT_URI")
    assert default_uri == "file:./artifacts/mlruns"


def test_mlflow_start_run_disabled_yields_none():
    mod = _load_mlflow_utils()
    MlflowConfig = getattr(mod, "MlflowConfig")
    start_run = getattr(mod, "start_run")
    cfg = MlflowConfig(enable=False)
    with start_run(cfg) as run:
        assert run is None
