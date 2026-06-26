"""
Test File Uri Normalization

Test module for file uri normalization.
"""

from __future__ import annotations

from codex_ml.tracking.guards import normalize_mlflow_uri


def test_normalize_file_uri_variants(tmp_path):
    target = tmp_path / "mlruns"
    target.mkdir()
    variants = [
        f"file:/{target}",
        f"file:///{target}",
        str(target),
    ]
    normalized = {normalize_mlflow_uri(v) for v in variants}
    assert len(normalized) == 1, "Normalized must not be empty"
    uri = normalized.pop()
    assert uri is not None, "uri must be initialized"
    assert uri.startswith("file://"), "Condition must be true"
    assert uri.endswith("/mlruns"), "Condition must be true"
