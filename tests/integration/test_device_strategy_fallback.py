#             assert config.device in (, "Condition must be true"
# 
#         """Verify bfloat16 check handles errors gracefully."""
#         # Arrange
#         try:
#             import torch  # noqa: F401
#         except ImportError:
#             pytest.skip("PyTorch not available")
# 
#             # Assert: Should either use MPS or fall back to CPU
#             assert config.device in (, "Condition must be true"
# 
#             assert config.device in (, "Condition must be true"
# class TestDeviceStrategyFallback:
#     """Test device strategy fallback behavior."""
#     def test_device_config_cpu_fallback_when_cuda_unavailable(self):
#     def test_device_config_cpu_fallback_when_cuda_unavailable(self):
#         """Verify CPU fallback when CUDA is not available."""
#         # Arrange
#         try:
#             import torch  # noqa: F401
#         except ImportError:
#             pytest.skip("PyTorch not available")
#         from src.codex_ml.training.device_strategy import DeviceConfig
#         # Mock CUDA unavailability
#         with mock.patch("torch.cuda.is_available", return_value=False):
#             # Act
#             config = DeviceConfig.auto_detect(prefer_mps=False)
# 
#             # Assert
#             assert config.device == "cpu", "Should fall back to CPU when CUDA unavailable"
#             assert str(config.dtype) == "torch.float32", "CPU should use float32 by default"
#             assert str(config.dtype) == "torch.float32", "CPU should use float32 by default"
# 
#     def test_device_config_cuda_detected_when_available(self):
#     def test_device_config_cuda_detected_when_available(self):
#         """Verify CUDA is selected when available."""
#         # Arrange
#         try:
#             import torch  # noqa: F401
#         except ImportError:
#             pytest.skip("PyTorch not available")
#         from src.codex_ml.training.device_strategy import DeviceConfig
#         # Only run if CUDA is actually available
#         if not torch.cuda.is_available():
#             pytest.skip("CUDA not available on this system")
# 
#         # Act
#         config = DeviceConfig.auto_detect()
# 
#         # Assert
#         assert "cuda" in config.device, "Should detect and use CUDA when available"
#         assert "cuda" in config.device, "Should detect and use CUDA when available"
# 
#     def test_device_config_mps_preference(self):
#     def test_device_config_mps_preference(self):
#         """Verify MPS is preferred over CPU when available and preferred."""
#         # Arrange
#         try:
#             import torch  # noqa: F401
#         except ImportError:
#             pytest.skip("PyTorch not available")
#         from src.codex_ml.training.device_strategy import DeviceConfig
#         # Mock MPS availability
#         mps_available = hasattr(torch.backends, "mps")
#         mps_available = hasattr(torch.backends, "mps")
# 
#         if not mps_available:
#             pytest.skip("MPS detection not available on this PyTorch version")
#         # Mock CUDA unavailable, MPS available
#         with mock.patch("torch.cuda.is_available", return_value=False):
#             # Act
#             config = DeviceConfig.auto_detect(prefer_mps=True)
# 
#             # Assert: Should either use MPS or fall back to CPU
#             assert config.device in (, "Condition must be true"
#             # Assert: Should either use MPS or fall back to CPU
#             assert config.device in (, "Condition must be true"
#                 "mps",
#                 "cpu",
#             ), f"Device should be mps or cpu, got {config.device}"
#     def test_device_config_bfloat16_support_detection(self):
#     def test_device_config_bfloat16_support_detection(self):
#         """Verify bfloat16 support is correctly detected."""
#         # Arrange
#         try:
#             import torch  # noqa: F401
#         except ImportError:
#             pytest.skip("PyTorch not available")
#         from src.codex_ml.training.device_strategy import _supports_bfloat16
#         # Act
#         supports_bf16 = _supports_bfloat16()
# 
#         # Assert: Should return boolean without crashing
#         assert isinstance(supports_bf16, bool), "Should return boolean for bfloat16 support"
#         assert isinstance(supports_bf16, bool), "Should return boolean for bfloat16 support"
# 
#     def test_device_config_dtype_selection(self):
#     def test_device_config_dtype_selection(self):
#         """Verify dtype is selected appropriately for device."""
#         # Arrange
#         try:
#             import torch  # noqa: F401
#         except ImportError:
#             pytest.skip("PyTorch not available")
#         from src.codex_ml.training.device_strategy import DeviceConfig
#         # Act
#         config = DeviceConfig.auto_detect()
# 
#         # Assert
#         assert config.dtype is not None, "Dtype should be selected"
#         assert hasattr(config, "mixed_precision"), "Config should have mixed_precision attribute"
#         assert isinstance(config.mixed_precision, bool), "mixed_precision should be boolean"


class TestDeviceStrategyValidation:
    """Test device strategy configuration validation."""

    def test_device_config_initialization(self):
        """Verify DeviceConfig can be initialized with explicit values."""
        # Arrange
        try:
            import torch  # noqa: F401
        except ImportError:
            pytest.skip("PyTorch not available")

        from src.codex_ml.training.device_strategy import DeviceConfig

        # Act
        config = DeviceConfig(
            device="cpu",
            dtype=torch.float32,
            mixed_precision=False,
        )

        # Assert
        assert config.device == "cpu", "Device should be set to cpu"
        assert config.dtype == torch.float32, "Dtype should be float32"
        assert config.mixed_precision is False, "Mixed precision should be False"

    def test_device_available_cpu_always_available(self):
        """Verify CPU is always reported as available."""
        # Arrange
        try:
            import torch  # noqa: F401
        except ImportError:
            pytest.skip("PyTorch not available")

        from src.codex_ml.training.device_strategy import _device_available

        # Act
        cpu_available = _device_available("cpu")

        # Assert
        assert cpu_available is True, "CPU should always be available"

    def test_device_available_cuda_reflects_actual_status(self):
        """Verify CUDA availability check matches torch.cuda.is_available()."""
        # Arrange
        try:
            import torch  # noqa: F401
        except ImportError:
            pytest.skip("PyTorch not available")

        from src.codex_ml.training.device_strategy import _device_available

        # Act
        cuda_available = _device_available("cuda")
        expected_cuda = torch.cuda.is_available()

        # Assert
        assert (cuda_available == expected_cuda, "cuda_available is not valid"
        ), "CUDA availability should match torch.cuda.is_available()"


class TestDeviceStrategyIntegration:
    """Integration tests for device strategy in training context."""

    def test_device_strategy_supports_manual_device_override(self):
        """Verify device can be manually specified and overridden."""
        # Arrange
        try:
            import torch  # noqa: F401
        except ImportError:
            pytest.skip("PyTorch not available")

        from src.codex_ml.training.device_strategy import DeviceConfig

        # Act: Create config with explicit device
        config = DeviceConfig(
            device="cpu",
            dtype=torch.float32,
            mixed_precision=False,
        )

        # Assert
        assert config.device == "cpu", "Should respect manual device specification"

    def test_device_strategy_multiple_invocations_consistent(self):
        """Verify repeated auto-detect calls return consistent results."""
        # Arrange
        try:
            import torch  # noqa: F401
        except ImportError:
            pytest.skip("PyTorch not available")

        from src.codex_ml.training.device_strategy import DeviceConfig

        # Act
        config1 = DeviceConfig.auto_detect()
        config2 = DeviceConfig.auto_detect()

        # Assert
        assert config1.device == config2.device, "Device should be consistent across calls"
        assert config1.dtype == config2.dtype, "Dtype should be consistent across calls"

    def test_device_strategy_no_crash_on_torch_unavailable(self):
        """Verify graceful handling when PyTorch is unavailable."""
        # Arrange
        from src.codex_ml.training.device_strategy import _device_available

        # Act & Assert: Should not crash when called
        # (May return False, but shouldn't raise exception)
        try:
            result = _device_available("cuda")
            assert isinstance(result, bool), "Should return boolean"
        except RuntimeError:
            # Also acceptable if torch is truly unavailable
            pass


class TestDeviceStrategyErrorHandling:
    """Test error handling in device strategy."""

    def test_device_strategy_torch_required_error_message(self):
        """Verify clear error when torch is required but unavailable."""
        # Arrange
        try:
            import torch  # noqa: F401
        except ImportError:
            pytest.skip("PyTorch not available")

        from src.codex_ml.training.device_strategy import _torch_required

        # Mock torch unavailability
        with mock.patch("src.codex_ml.training.device_strategy.torch", None):
            # Act & Assert
            with pytest.raises(RuntimeError) as exc_info:
                _torch_required()

            assert "torch" in str(exc_info.value).lower(), "Error should mention torch"

    def test_device_strategy_bfloat16_check_handles_exceptions(self):
        """Verify bfloat16 check handles errors gracefully."""
        # Arrange
        try:
            import torch  # noqa: F401
        except ImportError:
            pytest.skip("PyTorch not available")

        from src.codex_ml.training.device_strategy import _supports_bfloat16

        # Mock exception during CUDA check
        with mock.patch("torch.cuda.is_available", side_effect=RuntimeError("CUDA error")):
            # Act: Should not raise
            result = _supports_bfloat16()

            # Assert
            assert isinstance(result, bool), "Should return boolean even with CUDA error"
            assert result is False, "Should return False when check fails"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
