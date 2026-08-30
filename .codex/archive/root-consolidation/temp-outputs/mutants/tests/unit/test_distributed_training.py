"""
Unit tests for codex_ml.distributed module.

Tests distributed training setup, DDP initialization, and environment parsing.
"""

import os
from unittest.mock import patch

import pytest


class TestDistributedMinimal:
    """Test distributed.minimal module."""

    def test_minimal_module_import(self):
        """Test minimal module can be imported."""
        from codex_ml.distributed import minimal

        assert minimal is not None, "minimal must be initialized"

    def test_env_opted_in_import(self):
        """Test _env_opted_in function can be imported."""
        from codex_ml.distributed.minimal import _env_opted_in

        assert _env_opted_in is not None, "_env_opted_in must be initialized"
        assert callable(_env_opted_in), "Condition must be true"

    @patch.dict(os.environ, {"CODEX_DDP_ENABLE": "1"}, clear=False)
    def test_env_opted_in_true(self):
        """Test _env_opted_in returns True when flag is 1."""
        from codex_ml.distributed.minimal import _env_opted_in

        opted_in, flag_name = _env_opted_in("CODEX_DDP_ENABLE")

        assert opted_in is True, "opted_in is not valid"
        assert flag_name == "CODEX_DDP_ENABLE", "flag_name is not valid"

    @patch.dict(os.environ, {"CODEX_DDP_ENABLE": "0"}, clear=False)
    def test_env_opted_in_false(self):
        """Test _env_opted_in returns False when flag is 0."""
        from codex_ml.distributed.minimal import _env_opted_in

        opted_in, _flag_name = _env_opted_in("CODEX_DDP_ENABLE")

        assert opted_in is False, "opted_in is not valid"

    @patch.dict(os.environ, {}, clear=True)
    def test_env_opted_in_missing(self):
        """Test _env_opted_in returns False when flag is missing."""
        from codex_ml.distributed.minimal import _env_opted_in

        opted_in, flag_name = _env_opted_in("NONEXISTENT_FLAG")

        assert opted_in is False, "opted_in is not valid"
        assert flag_name is None, "flag_name is not valid"


class TestParseEnvInt:
    """Test _parse_env_int function."""

    def test_parse_env_int_import(self):
        """Test _parse_env_int can be imported."""
        from codex_ml.distributed.minimal import _parse_env_int

        assert _parse_env_int is not None, "_parse_env_int must be initialized"
        assert callable(_parse_env_int), "Condition must be true"

    @patch.dict(os.environ, {"TEST_VAR": "42"}, clear=False)
    def test_parse_env_int_valid(self):
        """Test _parse_env_int with valid integer."""
        from codex_ml.distributed.minimal import _parse_env_int

        result = _parse_env_int("TEST_VAR")

        assert result == 42, "Result must not be empty"

    @patch.dict(os.environ, {}, clear=True)
    def test_parse_env_int_missing(self):
        """Test _parse_env_int with missing variable."""
        from codex_ml.distributed.minimal import _parse_env_int

        result = _parse_env_int("NONEXISTENT_VAR")

        assert result is None, "Result must not be empty"

    @patch.dict(os.environ, {"TEST_VAR": "not_an_int"}, clear=False)
    def test_parse_env_int_invalid(self):
        """Test _parse_env_int with invalid integer."""
        from codex_ml.distributed.minimal import _parse_env_int

        with pytest.warns(RuntimeWarning, match="expected integer"):
            result = _parse_env_int("TEST_VAR")
            assert result is None, "Result must not be empty"


class TestWarningFunctions:
    """Test warning helper functions."""

    def test_warn_missing_dist_import(self):
        """Test _warn_missing_dist function."""
        from codex_ml.distributed.minimal import _warn_missing_dist

        assert _warn_missing_dist is not None, "_warn_missing_dist must be initialized"
        assert callable(_warn_missing_dist), "Condition must be true"

    def test_warn_missing_dist_issues_warning(self):
        """Test _warn_missing_dist issues RuntimeWarning."""
        from codex_ml.distributed.minimal import _warn_missing_dist

        with pytest.warns(RuntimeWarning, match="torch.distributed"):
            _warn_missing_dist("TEST_FLAG")

    def test_warn_failed_init_import(self):
        """Test _warn_failed_init function."""
        from codex_ml.distributed.minimal import _warn_failed_init

        assert _warn_failed_init is not None, "_warn_failed_init must be initialized"
        assert callable(_warn_failed_init), "Condition must be true"

    def test_warn_failed_init_issues_warning(self):
        """Test _warn_failed_init issues RuntimeWarning."""
        from codex_ml.distributed.minimal import _warn_failed_init

        error = RuntimeError("Test error")

        with pytest.warns(RuntimeWarning, match="Failed to initialize"):
            _warn_failed_init("nccl", "TEST_FLAG", error)

    def test_warn_device_set_failed_import(self):
        """Test _warn_device_set_failed function."""
        from codex_ml.distributed.minimal import _warn_device_set_failed

        assert _warn_device_set_failed is not None, "_warn_device_set_failed must be initialized"
        assert callable(_warn_device_set_failed), "Condition must be true"


class TestOptInValues:
    """Test opt-in value constants."""

    def test_opt_in_values_constant(self):
        """Test _OPT_IN_VALUES constant exists."""
        from codex_ml.distributed.minimal import _OPT_IN_VALUES

        assert _OPT_IN_VALUES is not None, "_OPT_IN_VALUES must be initialized"
        assert isinstance(_OPT_IN_VALUES, (set, tuple, list))

    def test_opt_in_values_includes_common_values(self):
        """Test _OPT_IN_VALUES includes common true values."""
        from codex_ml.distributed.minimal import _OPT_IN_VALUES

        # Should include "1", "true", etc.
        assert "1" in _OPT_IN_VALUES, "Value must be initialized"
        assert any(v.lower() == "true" for v in _OPT_IN_VALUES), "Value must be initialized"


class TestFallbackEnvFlags:
    """Test fallback environment flags."""

    def test_fallback_env_flags_constant(self):
        """Test _FALLBACK_ENV_FLAGS constant exists."""
        from codex_ml.distributed.minimal import _FALLBACK_ENV_FLAGS

        assert _FALLBACK_ENV_FLAGS is not None, "_FALLBACK_ENV_FLAGS must be initialized"
        assert isinstance(_FALLBACK_ENV_FLAGS, (tuple, list))

    def test_fallback_env_flags_includes_codex_ddp(self):
        """Test _FALLBACK_ENV_FLAGS includes CODEX_DDP_ENABLE."""
        from codex_ml.distributed.minimal import _FALLBACK_ENV_FLAGS

        assert "CODEX_DDP_ENABLE" in _FALLBACK_ENV_FLAGS, "Condition must be true"


class TestIterCandidateFlags:
    """Test _iter_candidate_flags function."""

    def test_iter_candidate_flags_import(self):
        """Test _iter_candidate_flags can be imported."""
        from codex_ml.distributed.minimal import _iter_candidate_flags

        assert _iter_candidate_flags is not None, "_iter_candidate_flags must be initialized"
        assert callable(_iter_candidate_flags), "Condition must be true"

    def test_iter_candidate_flags_yields_primary(self):
        """Test _iter_candidate_flags yields primary flag first."""
        from codex_ml.distributed.minimal import _iter_candidate_flags

        flags = list(_iter_candidate_flags("PRIMARY_FLAG"))

        assert len(flags) > 0, "Flags must not be empty"
        assert flags[0] == "PRIMARY_FLAG", "Condition must be true"

    def test_iter_candidate_flags_yields_fallbacks(self):
        """Test _iter_candidate_flags yields fallback flags."""
        from codex_ml.distributed.minimal import _iter_candidate_flags

        flags = list(_iter_candidate_flags("PRIMARY_FLAG"))

        # Should include at least primary + fallbacks
        assert len(flags) >= 2, "Flags must not be empty"
