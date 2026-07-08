"""
Test Mlflow Wrapper Stub

Test module for mlflow wrapper stub.
"""

from codex_ml.tracking import mlflow_wrapper


def test_log_metric_stub_does_not_crash():
    mlflow_wrapper.log_metric("loss", 1.23)
