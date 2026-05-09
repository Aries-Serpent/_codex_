"""Tests for scripts/cognitive/cb_fallbacks.py — shared CB fallback helpers."""
from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import pytest

from scripts.cognitive.cb_fallbacks import (
    import_optional,
    rate_limited_call,
    with_fallback,
)

# ---------------------------------------------------------------------------
# import_optional
# ---------------------------------------------------------------------------

class TestImportOptional:
    def test_returns_module_when_available(self):
        mod = import_optional("json")
        assert mod is not None
        assert hasattr(mod, "dumps")

    def test_returns_none_for_missing_module(self):
        result = import_optional("_nonexistent_module_xyz_")
        assert result is None

    def test_returns_attr_from_module(self):
        dumps = import_optional("json", attr="dumps")
        import json
        assert dumps is json.dumps

    def test_returns_none_for_missing_attr(self):
        result = import_optional("json", attr="_does_not_exist_")
        assert result is None

    def test_missing_module_with_attr_returns_none(self):
        result = import_optional("_nonexistent_xyz_", attr="something")
        assert result is None


# ---------------------------------------------------------------------------
# with_fallback
# ---------------------------------------------------------------------------

class TestWithFallback:
    def test_returns_func_result_on_success(self):
        assert with_fallback(lambda: 42, default=0) == 42

    def test_returns_default_on_exception(self):
        assert with_fallback(lambda: 1 / 0, default=-1) == -1

    def test_returns_default_on_specified_exc(self):
        result = with_fallback(
            lambda: int("bad"),
            default="fallback",
            exc_types=(ValueError,),
        )
        assert result == "fallback"

    def test_propagates_unspecified_exc(self):
        with pytest.raises(TypeError):
            with_fallback(
                lambda: None + 1,  # type: ignore[operator]
                default="x",
                exc_types=(ValueError,),
            )

    def test_none_default(self):
        assert with_fallback(lambda: [][0], default=None) is None

    def test_false_default(self):
        assert with_fallback(lambda: 1 / 0, default=False) is False


# ---------------------------------------------------------------------------
# rate_limited_call
# ---------------------------------------------------------------------------

class TestRateLimitedCall:
    def test_calls_func_when_quota_ok(self):
        mock_func = MagicMock(return_value="result")
        with patch(
            "scripts.cognitive.cb_fallbacks._get_trickle_status",
            return_value={"resources": {"core": {"remaining": 100, "reset": int(time.time()) + 3600}}},
        ):
            result = rate_limited_call(mock_func, "arg1", kwarg="kw")
        mock_func.assert_called_once_with("arg1", kwarg="kw")
        assert result == "result"

    def test_calls_func_when_trickle_unavailable(self):
        """Degrades gracefully: no trickle module → proceeds immediately."""
        mock_func = MagicMock(return_value=99)
        with patch(
            "scripts.cognitive.cb_fallbacks._get_trickle_status",
            return_value={},
        ):
            result = rate_limited_call(mock_func)
        assert result == 99

    def test_waits_and_retries_when_quota_low(self):
        mock_func = MagicMock(return_value="ok")
        reset_ts = int(time.time()) + 1  # reset in 1 second
        statuses = [
            {"resources": {"core": {"remaining": 0, "reset": reset_ts}}},
            {"resources": {"core": {"remaining": 100, "reset": reset_ts}}},
        ]
        with patch(
            "scripts.cognitive.cb_fallbacks._get_trickle_status",
            side_effect=statuses,
        ), patch("scripts.cognitive.cb_fallbacks.time.sleep") as mock_sleep:
            result = rate_limited_call(mock_func, min_remaining=10, max_retries=2)
        assert result == "ok"
        mock_sleep.assert_called()

    def test_raises_after_max_retries_exhausted(self):
        exhausted_status = {"resources": {"core": {"remaining": 0, "reset": int(time.time()) + 5}}}
        with patch(
            "scripts.cognitive.cb_fallbacks._get_trickle_status",
            return_value=exhausted_status,
        ), patch("scripts.cognitive.cb_fallbacks.time.sleep"):
            with pytest.raises(RuntimeError, match="rate limit exhausted"):
                rate_limited_call(lambda: None, min_remaining=10, max_retries=1)

    def test_propagates_func_exception(self):
        with patch(
            "scripts.cognitive.cb_fallbacks._get_trickle_status",
            return_value={"resources": {"core": {"remaining": 500, "reset": 0}}},
        ):
            with pytest.raises(ValueError, match="boom"):
                rate_limited_call(lambda: (_ for _ in ()).throw(ValueError("boom")))

    def test_custom_resource_bucket(self):
        mock_func = MagicMock(return_value="search_result")
        with patch(
            "scripts.cognitive.cb_fallbacks._get_trickle_status",
            return_value={"resources": {"search": {"remaining": 25, "reset": 0}}},
        ):
            result = rate_limited_call(mock_func, resource="search", min_remaining=5)
        assert result == "search_result"


# ---------------------------------------------------------------------------
# Integration: cognitive_brain_core uses cb_fallbacks
# ---------------------------------------------------------------------------

class TestCognitiveBrainCoreIntegration:
    def test_perception_tolerates_missing_psutil(self):
        import tempfile

        from scripts.cognitive.cognitive_brain_core import PerceptionLayer
        with tempfile.TemporaryDirectory() as tmp:
            layer = PerceptionLayer(workspace=__import__("pathlib").Path(tmp))
            with patch("scripts.cognitive.cb_fallbacks.import_optional", return_value=None):
                data = layer.perceive()
        assert "sources_collected" in data
        assert data["system_load"] is None

    def test_action_executor_uses_rate_limited_call(self):
        import tempfile

        from scripts.cognitive.cognitive_brain_core import ActionExecutor
        with tempfile.TemporaryDirectory() as tmp:
            executor = ActionExecutor(workspace=__import__("pathlib").Path(tmp))
            decisions = {
                "tasks": [
                    {"agent": 1, "task": "pattern_analysis"},
                    {"agent": 2, "task": "performance_monitoring"},
                ],
            }
            with patch(
                "scripts.cognitive.cb_fallbacks._get_trickle_status",
                return_value={"resources": {"core": {"remaining": 500, "reset": 0}}},
            ):
                result = executor.execute(decisions)
        assert result["tasks_completed"] == 2
        assert result["success_rate"] == 1.0
        assert result["failures"] == []
