from pathlib import Path


def test_helm_configuration_supports_scaling() -> None:
    values = Path("deploy/helm/values.yaml").read_text(encoding="utf-8")
    assert "replicaCount: 3" in values
    assert "autoscaling" in values
