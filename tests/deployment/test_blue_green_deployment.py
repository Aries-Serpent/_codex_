"""
Test Blue Green Deployment

Test module for blue green deployment.
"""

from pathlib import Path


def test_helm_configuration_supports_scaling() -> None:
    values = Path("deploy/helm/values.yaml").read_text(encoding="utf-8")
    assert "replicaCount: 3" in values, "Value must be initialized"
    assert "autoscaling" in values, "Value must be initialized"
