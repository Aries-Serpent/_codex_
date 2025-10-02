from __future__ import annotations

import argparse
import os
from pathlib import Path
from uuid import uuid4


def _import_mlflow():
    try:
        import mlflow  # type: ignore[import]
    except Exception as exc:  # pragma: no cover - optional dependency
        raise SystemExit("mlflow is required for this smoke test") from exc
    return mlflow


def run_smoke(output: Path, tracking_uri: str | None = None) -> str:
    from codex_ml.logging.run_logger import RunLogger
    from codex_ml.tracking.mlflow_guard import bootstrap_offline_tracking, last_decision
    from codex_ml.tracking.writers import MLflowWriter

    output.mkdir(parents=True, exist_ok=True)
    prev_local_dir = os.environ.get("CODEX_MLFLOW_LOCAL_DIR")
    prev_tracking_uri = os.environ.get("MLFLOW_TRACKING_URI")
    if tracking_uri is not None:
        os.environ["MLFLOW_TRACKING_URI"] = tracking_uri
    os.environ["CODEX_MLFLOW_LOCAL_DIR"] = str(output)
    try:
        effective_uri = bootstrap_offline_tracking(force=True, requested_uri=tracking_uri)
        decision = last_decision()
        if decision is None:
            raise RuntimeError("MLflow guard did not produce a decision record")
        if decision.fallback_reason and decision.requested_uri and not decision.allow_remote:
            raise SystemExit("Remote MLflow URIs are blocked. Set MLFLOW_ALLOW_REMOTE=1 to opt in.")
        if not effective_uri.startswith("file:") and not decision.allow_remote:
            raise SystemExit(f"Expected file: URI, got {effective_uri}")

        mlflow = _import_mlflow()
        mlflow.set_tracking_uri(effective_uri)
        mlflow.set_experiment("offline-smoke")

        run_id = f"offline-smoke-{uuid4().hex[:8]}"
        run_dir = output / "runs" / run_id
        logger = RunLogger(run_dir, run_id)
        logger.log_metric(step=1, split="train", metric="loss", value=0.42, dataset="smoke")
        logger.close()

        summary_path = run_dir / "tracking_summary.ndjson"
        writer = MLflowWriter(
            effective_uri,
            "offline-smoke",
            run_id,
            {"source": "mlflow-offline-cli"},
            summary_path=summary_path,
        )
        writer.log({"metric": "loss", "value": 0.42, "step": 1, "split": "train"})
        writer.close()
        return effective_uri
    finally:
        if prev_local_dir is not None:
            os.environ["CODEX_MLFLOW_LOCAL_DIR"] = prev_local_dir
        else:
            os.environ.pop("CODEX_MLFLOW_LOCAL_DIR", None)
        if prev_tracking_uri is not None:
            os.environ["MLFLOW_TRACKING_URI"] = prev_tracking_uri
        else:
            os.environ.pop("MLFLOW_TRACKING_URI", None)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run an offline MLflow smoke test")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/mlflow_offline"),
        help="Directory for offline MLflow artifacts",
    )
    parser.add_argument(
        "--tracking-uri",
        type=str,
        default=None,
        help="Optional tracking URI to force for the smoke run",
    )
    args = parser.parse_args(argv)
    uri = run_smoke(args.output, tracking_uri=args.tracking_uri)
    print(f"Offline MLflow run completed. Tracking URI: {uri}")


if __name__ == "__main__":  # pragma: no cover - manual invocation
    main()
