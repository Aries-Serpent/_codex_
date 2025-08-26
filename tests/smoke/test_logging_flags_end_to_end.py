# BEGIN: CODEX_SMOKE_LOGGING_FLAGS
import os, argparse, tempfile, importlib.util
from pathlib import Path
import pytest


def test_deploy_logging_flags_bootstrap_and_log():
    # dynamic import of deploy_codex_pipeline.py
    target = Path("deploy_codex_pipeline.py").resolve()
    if not target.exists():
        pytest.skip("deploy_codex_pipeline.py not present; generate or patch first")

    spec = importlib.util.spec_from_file_location("deploy_codex_pipeline", str(target))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore

    ap = argparse.ArgumentParser()
    if hasattr(mod, "_codex_patch_argparse"):
        mod._codex_patch_argparse(ap)
    else:
        pytest.skip("_codex_patch_argparse not found")

    ns = ap.parse_args(
        [
            "--enable-wandb",
            "--mlflow-enable",
            "--mlflow-experiment",
            "codex-smoke",
        ]
    )

    os.environ.setdefault("WANDB_MODE", "offline")

    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp) / "run"
        run_dir.mkdir(parents=True, exist_ok=True)
        if not hasattr(mod, "_codex_logging_bootstrap") or not hasattr(
            mod, "_codex_log_all"
        ):
            pytest.skip("logging helpers missing; patch deploy_codex_pipeline.py")

        handles = mod._codex_logging_bootstrap(
            ns, run_dir, params={"wandb_project": "codex-smoke"}
        )
        mod._codex_log_all(handles, step=1, metrics={"loss": 0.123})
        tb_dir = run_dir / "tb"
        if handles.get("tb") is not None:
            assert any(tb_dir.glob("events.*")), "TensorBoard events missing"
