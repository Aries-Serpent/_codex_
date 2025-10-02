"""Offline MLflow smoke test ensuring file-based tracking."""

from __future__ import annotations

import argparse
import os
from pathlib import Path


def _import_mlflow():
    try:
        import mlflow  # type: ignore[import]
    except Exception as exc:  # pragma: no cover - optional dependency
        raise SystemExit("mlflow is required for this smoke test") from exc
    return mlflow


def run_smoke(output: Path) -> str:
    from codex_ml.tracking.mlflow_guard import bootstrap_offline_tracking

    output.mkdir(parents=True, exist_ok=True)
    prev_local_dir = os.environ.get("CODEX_MLFLOW_LOCAL_DIR")
    os.environ["CODEX_MLFLOW_LOCAL_DIR"] = str(output)
    try:
        tracking_uri = bootstrap_offline_tracking(force=True)
        mlflow = _import_mlflow()
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment("offline-smoke")
        with mlflow.start_run(run_name="offline-smoke"):
            mlflow.log_params({"example": "mlflow_offline_smoke"})
            mlflow.log_metric("loss", 0.42, step=1)
            artifact_path = output / "artifact.txt"
            artifact_path.write_text("offline artifact", encoding="utf-8")
            mlflow.log_artifact(str(artifact_path))
        return tracking_uri
    finally:
        if prev_local_dir is not None:
            os.environ["CODEX_MLFLOW_LOCAL_DIR"] = prev_local_dir
        else:
            os.environ.pop("CODEX_MLFLOW_LOCAL_DIR", None)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run an offline MLflow smoke test")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/mlflow_offline"),
        help="Directory for offline MLflow artifacts",
    )
    args = parser.parse_args(argv)
    uri = run_smoke(args.output)
    print(f"Offline MLflow run completed. Tracking URI: {uri}")


if __name__ == "__main__":  # pragma: no cover - manual invocation
    main()
