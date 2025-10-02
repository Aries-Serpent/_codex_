"""Offline MLflow smoke test ensuring file-based tracking."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from urllib.parse import urlparse


def _import_mlflow():
    try:
        import mlflow  # type: ignore[import]
    except Exception as exc:  # pragma: no cover - optional dependency
        raise SystemExit("mlflow is required for this smoke test") from exc
    return mlflow


def _is_local_uri(uri: str) -> bool:
    parsed = urlparse(uri)
    if parsed.scheme in {"", "file"}:
        if parsed.scheme == "file":
            netloc = parsed.netloc or ""
            return netloc in {"", "localhost"}
        return True
    return False


def run_smoke(output: Path, tracking_uri: str | None = None) -> str:
    from codex_ml.logging.run_logger import RunLogger
    from codex_ml.tracking.mlflow_guard import bootstrap_offline_tracking_decision
    from codex_ml.tracking.writers import MLflowWriter

    output = output.expanduser()
    output.mkdir(parents=True, exist_ok=True)
    local_store = output / "mlruns"
    run_dir = output / "offline-smoke"
    run_dir.mkdir(parents=True, exist_ok=True)

    prev_local_dir = os.environ.get("CODEX_MLFLOW_LOCAL_DIR")
    prev_tracking_uri = os.environ.get("MLFLOW_TRACKING_URI")
    writer = None
    try:
        if tracking_uri is not None:
            os.environ["MLFLOW_TRACKING_URI"] = tracking_uri
        os.environ["CODEX_MLFLOW_LOCAL_DIR"] = str(local_store)

        _import_mlflow()
        decision = bootstrap_offline_tracking_decision(force=True)
        effective_uri = decision.effective_uri

        if tracking_uri and not _is_local_uri(tracking_uri) and not decision.allow_remote:
            raise SystemExit("Remote MLflow URI blocked; set MLFLOW_ALLOW_REMOTE=1 to override.")
        if not effective_uri.startswith("file:"):
            raise SystemExit(f"Expected file:// tracking URI, received '{effective_uri}'.")

        writer = MLflowWriter(
            effective_uri,
            "offline-smoke",
            "offline-smoke",
            {"source": "mlflow_offline_cli"},
            summary_path=run_dir / "tracking_summary.ndjson",
        )

        ml_module = getattr(writer, "_mlflow", None)
        if ml_module is None:
            raise SystemExit("MLflow writer failed to initialise; ensure mlflow is installed.")

        run_logger = RunLogger(run_dir, run_id="offline-smoke")
        try:
            record = run_logger.log_metric(
                step=1,
                split="eval",
                metric="loss",
                value=0.42,
                tags={"source": "mlflow_offline_cli"},
            )
        finally:
            run_logger.close()

        writer.log(record)
        artifact_path = run_dir / "artifact.txt"
        artifact_path.write_text("offline artifact", encoding="utf-8")
        try:
            ml_module.log_params({"example": "mlflow_offline_smoke"})  # type: ignore[attr-defined]
        except Exception:
            pass
        try:
            ml_module.log_artifact(str(artifact_path))  # type: ignore[attr-defined]
        except Exception:
            pass

        return effective_uri
    finally:
        if writer is not None:
            writer.close()
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
        help="Optional MLflow tracking URI to validate. Must be file:// unless MLFLOW_ALLOW_REMOTE=1.",
    )
    args = parser.parse_args(argv)
    uri = run_smoke(args.output, tracking_uri=args.tracking_uri)
    print(f"Offline MLflow run completed. Tracking URI: {uri}")


if __name__ == "__main__":  # pragma: no cover - manual invocation
    main()
