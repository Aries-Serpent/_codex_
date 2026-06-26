from src.codex_ml.utils.config_drift import ConfigDrift, detect_config_drift, embed_config_hash


def test_config_drift(tmp_path):
    c1 = {"a": 1, "b": 2}
    drift1 = ConfigDrift(c1)

    baseline_path = tmp_path / "baseline.json"
    drift1.save_baseline(baseline_path)

    drift2 = ConfigDrift.load_baseline(baseline_path)
    assert drift2.config == c1, "config is not valid"

    drift3 = ConfigDrift({"a": 1, "b": 3, "c": 4})
    diff = drift3.compare(drift2)
    assert isinstance(diff, dict)

    assert drift3.has_drift(baseline_path) is True, "Condition must be true"
    assert drift1.has_drift(baseline_path) is False, "Condition must be true"


def test_detect_config_drift_convenience(tmp_path):
    c1 = {"x": 1}
    baseline_path = tmp_path / "baseline2.json"
    ConfigDrift(c1).save_baseline(baseline_path)

    # Actually detect_config_drift uses ConfigDrift internally.
    assert detect_config_drift({"x": 2}, baseline_path) is True
    assert detect_config_drift(c1, baseline_path) is False


def test_embed_config_hash():
    cfg = {"a": 1}
    ckpt = {"state_dict": {}}
    updated = embed_config_hash(cfg, ckpt)
    assert "metadata" in updated, "Data must not be empty"
    assert "config_hash" in updated["metadata"], "Data must not be empty"
