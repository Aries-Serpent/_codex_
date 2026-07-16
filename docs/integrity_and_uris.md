# Integrity & URIs
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Last Updated: 2026-07-16

## File URIs
We normalize **file URIs** to the RFC-8089 triple-slash form: `file:///abs/path`.
Helper: `codex_ml.tracking.guards._as_mlflow_file_uri`.

## Canonical JSON
All checkpoint/manifest metadata is emitted as **deterministic JSON** with:
`sort_keys=True`, tight separators, `ensure_ascii=False`, and `allow_nan=False`.
Writes are **atomic** (temp → fsync → atomic rename → fsync dir).

## Offline Tracking (MLflow & W&B)
Default to local file-backed MLflow and W&B offline/disabled modes. Use
`MLFLOW_ALLOW_REMOTE=1` to explicitly allow remote endpoints.
