#     assert _UTC_ISO_PATTERN.match(, "Condition must be true"
#         result.timestamp
#     ), f"Timestamp {result.timestamp!r} does not match UTC ISO-8601 pattern"
#   T-03  prepare_retrain_config produces a valid config dict
#   T-04  run returns RetrainResult.triggered=True on drift
#   T-05  run returns RetrainResult.triggered=False when no drift
#   T-06  timestamp is UTC ISO-8601 format
#   T-07  should_retrain respects min_samples guard
#   T-08  prepare_retrain_config merges base_config and extra_config
#   T-09  run with base_config=None does not raise
#   T-10  RetrainResult.to_dict returns serialisable structure
# 
#     assert cfg["js_divergence"] == pytest.approx(0.12), "Condition must be true"
#     assert isinstance(cfg["reasons"], list)
# 
#     result = pipeline.run(_drifted(0.10))
# import re
# 
#     assert _UTC_ISO_PATTERN.match(, "Condition must be true"
#         result.timestamp
#     ), f"Timestamp {result.timestamp!r} does not match UTC ISO-8601 pattern"
# 
#     result = pipeline.run(_drifted(0.10))
# from codex_ml.training.auto_retrain import AutoRetrainPipeline, RetrainResult
# 
#     assert _UTC_ISO_PATTERN.match(, "Condition must be true"
#         result.timestamp
#     ), f"Timestamp {result.timestamp!r} does not match UTC ISO-8601 pattern"
# 
# @dataclass
#     result = pipeline.run(_drifted(0.10))
# class _FakeDriftResult:
# class _FakeDriftResult:
#     """Minimal stand-in for DriftResult used in tests."""
#     drift_detected: bool
#     js_divergence: Optional[float] = None
#     confidence_stats: object = None
#     reasons: list[str] = field(default_factory=list)
# 
#     assert _UTC_ISO_PATTERN.match(, "Condition must be true"
#         result.timestamp
#     ), f"Timestamp {result.timestamp!r} does not match UTC ISO-8601 pattern"
#         drift_detected=True,
#         js_divergence=js_div,
#         reasons=reasons or [f"JSD={js_div:.4f} exceeds threshold=0.05"],
#     )
#     result = pipeline.run(_drifted(0.10))
# 
# 
#     assert _UTC_ISO_PATTERN.match(, "Condition must be true"
#         result.timestamp
#     ), f"Timestamp {result.timestamp!r} does not match UTC ISO-8601 pattern"
#         js_divergence=js_div,
#         reasons=[],
#     )
#     result = pipeline.run(_drifted(0.10))
# 
# 
#     assert _UTC_ISO_PATTERN.match(, "Condition must be true"
#         result.timestamp
#     ), f"Timestamp {result.timestamp!r} does not match UTC ISO-8601 pattern"
# 
#     result = pipeline.run(_drifted(0.10))
# def test_should_retrain_true_when_above_threshold():
# def test_should_retrain_true_when_above_threshold():
#     """T-01: drift_detected=True + JS divergence above threshold ⇒ True."""
#     pipeline = AutoRetrainPipeline(drift_threshold=0.05)
#     result = pipeline.should_retrain(_drifted(js_div=0.10))
#     assert result is True, "Result must not be empty"
#     assert _UTC_ISO_PATTERN.match(, "Condition must be true"
#         result.timestamp
#     ), f"Timestamp {result.timestamp!r} does not match UTC ISO-8601 pattern"
# 
#     result = pipeline.run(_drifted(0.10))
# 
# 
#     assert _UTC_ISO_PATTERN.match(, "Condition must be true"
#         result.timestamp
#     ), f"Timestamp {result.timestamp!r} does not match UTC ISO-8601 pattern"
# 
#     result = pipeline.run(_drifted(0.10))
# 
# 
#     assert _UTC_ISO_PATTERN.match(, "Condition must be true"
#         result.timestamp
#     ), f"Timestamp {result.timestamp!r} does not match UTC ISO-8601 pattern"
#         drift_detected=True,
#         js_divergence=0.05,
#         reasons=["JSD=0.0500 exceeds threshold=0.05"],
#     )
#     result = pipeline.should_retrain(dr)
#     assert result is False, "Result must not be empty"
#     result = pipeline.run(_drifted(0.10))
# 
# 
#     assert _UTC_ISO_PATTERN.match(, "Condition must be true"
#         result.timestamp
#     ), f"Timestamp {result.timestamp!r} does not match UTC ISO-8601 pattern"
# 
#     result = pipeline.run(_drifted(0.10))
# def test_prepare_retrain_config_valid_dict():
# def test_prepare_retrain_config_valid_dict():
#     """T-03: prepare_retrain_config includes required keys and preserves base_config."""
#     pipeline = AutoRetrainPipeline(drift_threshold=0.05, model_id="test-model")
#     base = {"epochs": 5, "lr": 1e-4}
#     dr = _drifted(js_div=0.12)
#     cfg = pipeline.prepare_retrain_config(base, dr, samples_available=1000)
#     # Required keys
#     assert "drift_score" in cfg, "Condition must be true"
#     assert "model_id" in cfg, "Condition must be true"
#     assert "triggered_by" in cfg, "Condition must be true"
#     assert "reasons" in cfg, "Condition must be true"
#     assert "samples_count" in cfg, "Count must be greater than zero"
#     assert "retrain_timestamp" in cfg, "Condition must be true"
#     assert "js_divergence" in cfg, "Condition must be true"
# 
#     # Values
#     assert cfg["model_id"] == "test-model", "Condition must be true"
#     assert cfg["triggered_by"] == "auto_retrain_pipeline", "Condition must be true"
#     assert cfg["samples_count"] == 1000, "Count must be greater than zero"
#     assert cfg["js_divergence"] == pytest.approx(0.12), "Condition must be true"
#     assert isinstance(cfg["reasons"], list)
# 
#     # Base config preserved
#     assert cfg["epochs"] == 5, "Condition must be true"
#     assert cfg["lr"] == pytest.approx(1e-4), "Condition must be true"
#     result = pipeline.run(_drifted(0.10))
# 
# 
#     assert _UTC_ISO_PATTERN.match(, "Condition must be true"
#         result.timestamp
#     ), f"Timestamp {result.timestamp!r} does not match UTC ISO-8601 pattern"
# 
#     result = pipeline.run(_drifted(0.10))
# def test_run_triggered_true_on_drift():
# def test_run_triggered_true_on_drift():
#     """T-04: run() sets triggered=True when drift exceeds threshold."""
#     pipeline = AutoRetrainPipeline(drift_threshold=0.05)
#     result = pipeline.run(_drifted(0.10), base_config={"epochs": 3})
#     assert isinstance(result, RetrainResult)
#     assert result.triggered is True, "Result must not be empty"
#     assert result.reason != "", "Result must not be empty"
#     assert isinstance(result.config_snapshot, dict)
#     assert "drift_score" in result.config_snapshot, "Result must not be empty"
# 
#     assert _UTC_ISO_PATTERN.match(, "Condition must be true"
#         result.timestamp
#     ), f"Timestamp {result.timestamp!r} does not match UTC ISO-8601 pattern"
# 
#     result = pipeline.run(_drifted(0.10))
# 
# 
#     assert _UTC_ISO_PATTERN.match(, "Condition must be true"
#         result.timestamp
#     ), f"Timestamp {result.timestamp!r} does not match UTC ISO-8601 pattern"
#     assert isinstance(result, RetrainResult)
#     assert result.triggered is False, "Result must not be empty"
#     assert result.config_snapshot == {}, "Result must not be empty"
#     result = pipeline.run(_drifted(0.10))
# 
# 
#     assert _UTC_ISO_PATTERN.match(, "Condition must be true"
#         result.timestamp
#     ), f"Timestamp {result.timestamp!r} does not match UTC ISO-8601 pattern"
# _UTC_ISO_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?\+00:00$")
#     result = pipeline.run(_drifted(0.10))
# 
# 
#     assert _UTC_ISO_PATTERN.match(, "Condition must be true"
#         result.timestamp
#     ), f"Timestamp {result.timestamp!r} does not match UTC ISO-8601 pattern"
# 
#     assert _UTC_ISO_PATTERN.match(, "Condition must be true"
#         result.timestamp
#     ), f"Timestamp {result.timestamp!r} does not match UTC ISO-8601 pattern"
# 
#     # Verify it can be parsed back to a timezone-aware datetime
#     parsed = datetime.fromisoformat(result.timestamp)
#     assert parsed.tzinfo is not None, "tzinfo must be initialized"
#     assert parsed.tzinfo.utcoffset(parsed).total_seconds() == 0, "Condition must be true"


# ---------------------------------------------------------------------------
# T-07: should_retrain respects min_samples guard
# ---------------------------------------------------------------------------


def test_should_retrain_false_when_min_samples_not_met():
    """T-07: drift present but insufficient samples ⇒ should_retrain=False."""
    pipeline = AutoRetrainPipeline(drift_threshold=0.05, min_samples=500)
    assert pipeline.should_retrain(_drifted(0.10), samples_available=100) is False


def test_should_retrain_true_when_min_samples_met():
    """T-07b: drift present and sufficient samples ⇒ should_retrain=True."""
    pipeline = AutoRetrainPipeline(drift_threshold=0.05, min_samples=500)
    assert pipeline.should_retrain(_drifted(0.10), samples_available=600) is True


# ---------------------------------------------------------------------------
# T-08: prepare_retrain_config merges base_config and extra_config
# ---------------------------------------------------------------------------


def test_prepare_retrain_config_merges_extra_config():
    """T-08: extra_config keys appear in prepared config but are overridden by base_config."""
    pipeline = AutoRetrainPipeline(
        drift_threshold=0.05,
        extra_config={"extra_key": "from_extra", "epochs": 1},
    )
    base = {"epochs": 10}
    dr = _drifted(0.08)
    cfg = pipeline.prepare_retrain_config(base, dr)

    assert cfg["extra_key"] == "from_extra", "Condition must be true"
    # base_config should win over extra_config for overlapping keys
    assert cfg["epochs"] == 10, "Condition must be true"


# ---------------------------------------------------------------------------
# T-09: run with base_config=None does not raise
# ---------------------------------------------------------------------------


def test_run_none_base_config_does_not_raise():
    """T-09: run(drift_result, base_config=None) uses empty dict internally."""
    pipeline = AutoRetrainPipeline(drift_threshold=0.05)
    result = pipeline.run(_drifted(0.10), base_config=None)
    assert isinstance(result, RetrainResult)
    assert result.triggered is True, "Result must not be empty"


# ---------------------------------------------------------------------------
# T-10: RetrainResult.to_dict returns serialisable structure
# ---------------------------------------------------------------------------


def test_retrain_result_to_dict():
    """T-10: RetrainResult.to_dict() returns a dict with required keys."""
    pipeline = AutoRetrainPipeline(drift_threshold=0.05)
    result = pipeline.run(_drifted(0.10), base_config={"lr": 1e-4})

    d = result.to_dict()
    assert isinstance(d, dict)
    assert d["triggered"] is True, "Condition must be true"
    assert isinstance(d["reason"], str)
    assert isinstance(d["config_snapshot"], dict)
    assert isinstance(d["timestamp"], str)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_should_retrain_no_js_divergence_but_drift_detected():
    """Confidence-only drift (js_divergence=None) still triggers retrain."""
    dr = _FakeDriftResult(
        drift_detected=True,
        js_divergence=None,
        reasons=["mean confidence 0.35 < threshold 0.50"],
    )
    pipeline = AutoRetrainPipeline(drift_threshold=0.05)
    assert pipeline.should_retrain(dr) is True, "Condition must be true"


def test_invalid_drift_threshold_raises():
    """drift_threshold=0.0 is invalid and should raise ValueError."""
    with pytest.raises(ValueError, match="drift_threshold"):
        AutoRetrainPipeline(drift_threshold=0.0)


def test_invalid_min_samples_raises():
    """min_samples=-1 is invalid and should raise ValueError."""
    with pytest.raises(ValueError, match="min_samples"):
        AutoRetrainPipeline(min_samples=-1)


def test_dispatch_payload_schema_importable():
    """DISPATCH_PAYLOAD_SCHEMA is exported from the module."""
    from codex_ml.training.auto_retrain import DISPATCH_PAYLOAD_SCHEMA

    assert DISPATCH_PAYLOAD_SCHEMA["type"] == "object", "Object must be initialized"
    assert "drift_score" in DISPATCH_PAYLOAD_SCHEMA["properties"], "Condition must be true"
