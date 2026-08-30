"""
Mock-based tests for src/codex/rag/utils.py that run without real torch.

These tests cover edge-case branches in check_for_meta_tensors that are not
exercised by the torch-dependent tests in tests/test_rag_utils.py:
  - line 95:       'continue' when the named_modules walk encounters the root module
  - lines 105-106: meta tensor detected in a submodule's parameter
  - lines 138-141: exception handler (ValueError/TypeError/RuntimeError)
"""
from unittest.mock import MagicMock, patch

from codex.rag.utils import check_for_meta_tensors


class TestCheckForMetaTensorsMocked:
    """Mock-based tests for check_for_meta_tensors that run without torch."""

    def test_exception_in_parameters_returns_none(self):
        """ValueError raised inside parameters() is caught; function returns None (lines 138-141)."""
        mock_model = MagicMock()
        mock_model.parameters.side_effect = ValueError("unexpected error")

        result = check_for_meta_tensors(mock_model)

        assert result is None, "expected None when an exception occurs during inspection"

    def test_typeerror_in_parameters_returns_none(self):
        """TypeError from parameters() is also caught (lines 138-141)."""
        mock_model = MagicMock()
        mock_model.parameters.side_effect = TypeError("type error")

        result = check_for_meta_tensors(mock_model)

        assert result is None

    def test_root_module_skipped_in_named_modules_walk(self):
        """Root module is skipped via 'continue' in the named_modules walk (line 95).

        Non-root submodule processing is validated by
        test_meta_tensor_detected_in_submodule_parameter.
        """
        fake_module_class = type("FakeModule", (), {})
        mock_torch = MagicMock()
        mock_torch.nn.Module = fake_module_class

        mock_model = MagicMock()
        mock_model.parameters.return_value = []
        mock_model.buffers.return_value = []
        # named_modules() yields (name, module) tuples; the first is always the root
        mock_model.named_modules.return_value = [("", mock_model)]

        with patch.dict("sys.modules", {"torch": mock_torch}):
            result = check_for_meta_tensors(mock_model)

        # Root is skipped, no sub-modules → no meta tensors found
        assert result is False

    def test_meta_tensor_detected_in_submodule_parameter(self):
        """is_meta=True on a submodule parameter → return True (lines 105-106)."""
        fake_module_class = type("FakeModule", (), {})
        mock_torch = MagicMock()
        mock_torch.nn.Module = fake_module_class

        mock_model = MagicMock()
        mock_model.parameters.return_value = []
        mock_model.buffers.return_value = []

        mock_sub = MagicMock()
        mock_param = MagicMock()
        mock_param.is_meta = True
        mock_param.shape = (4,)
        mock_sub.named_parameters.return_value = [("w", mock_param)]
        mock_sub.named_buffers.return_value = []

        # named_modules yields root (skipped) then a real submodule
        mock_model.named_modules.return_value = [("", mock_model), ("sub", mock_sub)]

        with patch.dict("sys.modules", {"torch": mock_torch}):
            result = check_for_meta_tensors(mock_model)

        assert result is True, "should detect meta tensor in submodule parameter"
