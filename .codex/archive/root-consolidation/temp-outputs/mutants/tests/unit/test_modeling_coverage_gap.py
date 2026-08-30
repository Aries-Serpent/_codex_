"""Gap-fill tests for modeling.py module - comprehensive coverage for model initialization.

This test suite covers:
- dtype resolution and validation
- device resolution (cpu/cuda)
- configuration coercion from various input formats
- LoRA settings configuration
- Model and tokenizer initialization helpers
"""

from __future__ import annotations

import pytest

from modeling import (
    _DTYPE_MAP,
    LoraSettings,
    ModelInitConfig,
    _coerce_config,
    _needs_bf16,
    _resolve_device,
    _resolve_dtype,
    resolve_dtype,
)


class TestDtypeResolution:
    """Test dtype resolution and validation."""

    def test_resolve_dtype_float32_default(self):
        """Test resolving default float32 dtype."""
        dtype = _resolve_dtype(None)
        import torch

        assert dtype == torch.float32, "dtype is not valid"

    def test_resolve_dtype_explicit_float32(self):
        """Test resolving explicit float32."""
        dtype = _resolve_dtype("float32")
        import torch

        assert dtype == torch.float32, "dtype is not valid"

    def test_resolve_dtype_fp32_alias(self):
        """Test resolving fp32 alias for float32."""
        dtype = _resolve_dtype("fp32")
        import torch

        assert dtype == torch.float32, "dtype is not valid"

    def test_resolve_dtype_bfloat16(self):
        """Test resolving bfloat16 dtype."""
        dtype = _resolve_dtype("bfloat16")
        import torch

        assert dtype == torch.bfloat16, "dtype is not valid"

    def test_resolve_dtype_bf16_alias(self):
        """Test resolving bf16 alias for bfloat16."""
        dtype = _resolve_dtype("bf16")
        import torch

        assert dtype == torch.bfloat16, "dtype is not valid"

    def test_resolve_dtype_float16(self):
        """Test resolving float16 dtype."""
        dtype = _resolve_dtype("float16")
        import torch

        assert dtype == torch.float16, "dtype is not valid"

    def test_resolve_dtype_fp16_alias(self):
        """Test resolving fp16 alias for float16."""
        dtype = _resolve_dtype("fp16")
        import torch

        assert dtype == torch.float16, "dtype is not valid"

    def test_resolve_dtype_half_alias(self):
        """Test resolving half alias for float16."""
        dtype = _resolve_dtype("half")
        import torch

        assert dtype == torch.float16, "dtype is not valid"

    def test_resolve_dtype_case_insensitive(self):
        """Test that dtype resolution is case-insensitive."""
        dtype_lower = _resolve_dtype("float32")
        dtype_upper = _resolve_dtype("FLOAT32")
        dtype_mixed = _resolve_dtype("Float32")
        import torch

        assert dtype_lower == dtype_upper == dtype_mixed == torch.float32, "dtype_lower is not valid"

    def test_resolve_dtype_invalid_raises_error(self):
        """Test that invalid dtype raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported dtype"):
            _resolve_dtype("invalid_dtype")

    def test_resolve_dtype_public_api(self):
        """Test public API resolve_dtype function."""
        dtype = resolve_dtype("float32")
        import torch

        assert dtype == torch.float32, "dtype is not valid"


class TestDeviceResolution:
    """Test device resolution logic."""

    def test_resolve_device_cpu_explicit(self):
        """Test explicit cpu device."""
        device = _resolve_device("cpu")
        assert device == "cpu", "device is not valid"

    def test_resolve_device_cuda_explicit(self):
        """Test explicit cuda device."""
        device = _resolve_device("cuda")
        assert device == "cuda", "device is not valid"

    def test_resolve_device_cuda_with_index(self):
        """Test CUDA device with explicit index."""
        device = _resolve_device("cuda:0")
        assert device == "cuda:0", "device is not valid"

    def test_resolve_device_auto_defaults(self):
        """Test auto device resolution."""
        device = _resolve_device("auto")
        # Should be either cuda or cpu depending on availability
        assert device in ("cpu", "cuda")

    def test_resolve_device_none_defaults(self):
        """Test None device defaults to auto."""
        device = _resolve_device(None)
        # Should be either cuda or cpu depending on availability
        assert device in ("cpu", "cuda")

    def test_resolve_device_empty_string_defaults(self):
        """Test empty string device defaults to auto."""
        device = _resolve_device("")
        # Should be either cuda or cpu depending on availability
        assert device in ("cpu", "cuda")


class TestLoraSettings:
    """Test LoRA settings configuration."""

    def test_lora_settings_defaults(self):
        """Test default LoRA settings."""
        lora = LoraSettings()
        assert lora.enabled is False, "enabled is not valid"
        assert lora.r == 8, "r is not valid"
        assert lora.alpha == 16, "alpha is not valid"
        assert lora.dropout == 0.0, "dropout is not valid"
        assert lora.target_modules == ("q_proj", "v_proj")
        assert lora.bias == "none", "bias is not valid"
        assert lora.task_type == "CAUSAL_LM", "task_type is not valid"

    def test_lora_settings_enabled(self):
        """Test enabling LoRA settings."""
        lora = LoraSettings(enabled=True, r=16, alpha=32)
        assert lora.enabled is True, "enabled is not valid"
        assert lora.r == 16, "r is not valid"
        assert lora.alpha == 32, "alpha is not valid"

    def test_lora_settings_custom_target_modules(self):
        """Test custom target modules."""
        custom_modules = ("q_proj", "v_proj", "k_proj")
        lora = LoraSettings(target_modules=custom_modules)
        assert lora.target_modules == custom_modules, "target_modules is not valid"

    def test_lora_settings_custom_dropout(self):
        """Test custom dropout."""
        lora = LoraSettings(dropout=0.1)
        assert lora.dropout == 0.1, "dropout is not valid"

    def test_lora_settings_custom_bias(self):
        """Test custom bias setting."""
        lora = LoraSettings(bias="all")
        assert lora.bias == "all", "bias is not valid"

    def test_lora_settings_custom_task_type(self):
        """Test custom task type."""
        lora = LoraSettings(task_type="TOKEN_CLS")
        assert lora.task_type == "TOKEN_CLS", "task_type is not valid"


class TestModelInitConfig:
    """Test ModelInitConfig dataclass."""

    def test_model_init_config_minimal(self):
        """Test minimal ModelInitConfig."""
        config = ModelInitConfig(model_name="gpt2")
        assert config.model_name == "gpt2", "model_name is not valid"
        assert config.tokenizer_name is None, "tokenizer_name is not valid"
        assert config.dtype == "float32", "dtype is not valid"
        assert config.device == "auto", "device is not valid"
        assert config.trust_remote_code is False, "trust_remote_code is not valid"

    def test_model_init_config_full(self):
        """Test full ModelInitConfig with all parameters."""
        lora = LoraSettings(enabled=True)
        config = ModelInitConfig(
            model_name="meta-llama/Llama-2-7b",
            tokenizer_name="meta-llama/Llama-2-7b",
            dtype="bfloat16",
            device="cuda",
            trust_remote_code=True,
            load_config={"load_in_4bit": True},
            lora=lora,
            bf16_require_capability=True,
        )
        assert config.model_name == "meta-llama/Llama-2-7b", "model_name is not valid"
        assert config.tokenizer_name == "meta-llama/Llama-2-7b", "tokenizer_name is not valid"
        assert config.dtype == "bfloat16", "dtype is not valid"
        assert config.device == "cuda", "device is not valid"
        assert config.trust_remote_code is True, "trust_remote_code is not valid"
        assert config.load_config == {"load_in_4bit": True}, "load_config is not valid"
        assert config.lora.enabled is True, "enabled is not valid"
        assert config.bf16_require_capability is True, "bf16_require_capability is not valid"


class TestConfigCoercion:
    """Test configuration coercion from various input formats."""

    def test_coerce_config_basic_dict(self):
        """Test coercing basic dictionary config."""
        config_dict = {"model_name": "gpt2"}
        config = _coerce_config(config_dict)
        assert isinstance(config, ModelInitConfig)
        assert config.model_name == "gpt2", "model_name is not valid"

    def test_coerce_config_model_name_alias(self):
        """Test model_name resolution from aliases."""
        # Test 'name' alias
        config = _coerce_config({"name": "gpt2"})
        assert config.model_name == "gpt2", "model_name is not valid"

        # Test 'pretrained_model_name_or_path' alias
        config = _coerce_config({"pretrained_model_name_or_path": "gpt2"})
        assert config.model_name == "gpt2", "model_name is not valid"

    def test_coerce_config_tokenizer_name(self):
        """Test tokenizer_name extraction."""
        config = _coerce_config(
            {
                "model_name": "gpt2",
                "tokenizer_name": "gpt2",
            }
        )
        assert config.tokenizer_name == "gpt2", "tokenizer_name is not valid"

    def test_coerce_config_dtype_resolution(self):
        """Test dtype resolution in config."""
        config = _coerce_config(
            {
                "model_name": "gpt2",
                "dtype": "float32",
            }
        )
        assert config.dtype == "float32", "dtype is not valid"

    def test_coerce_config_dtype_alias(self):
        """Test torch_dtype alias."""
        config = _coerce_config(
            {
                "model_name": "gpt2",
                "torch_dtype": "float32",
            }
        )
        assert config.dtype == "float32", "dtype is not valid"

    def test_coerce_config_device_resolution(self):
        """Test device resolution in config."""
        config = _coerce_config(
            {
                "model_name": "gpt2",
                "device": "cpu",
            }
        )
        assert config.device == "cpu", "device is not valid"

    def test_coerce_config_trust_remote_code(self):
        """Test trust_remote_code flag."""
        config = _coerce_config(
            {
                "model_name": "gpt2",
                "trust_remote_code": True,
            }
        )
        assert config.trust_remote_code is True, "trust_remote_code is not valid"

    def test_coerce_config_load_config(self):
        """Test load_config extraction."""
        load_cfg = {"load_in_4bit": True}
        config = _coerce_config(
            {
                "model_name": "gpt2",
                "load_config": load_cfg,
            }
        )
        assert config.load_config == load_cfg, "load_config is not valid"

    def test_coerce_config_load_kwargs_alias(self):
        """Test load_kwargs as alias for load_config."""
        load_cfg = {"load_in_4bit": True}
        config = _coerce_config(
            {
                "model_name": "gpt2",
                "load_kwargs": load_cfg,
            }
        )
        assert config.load_config == load_cfg, "load_config is not valid"

    def test_coerce_config_lora_settings(self):
        """Test LoRA settings in config."""
        config = _coerce_config(
            {
                "model_name": "gpt2",
                "lora": {
                    "enabled": True,
                    "r": 16,
                    "lora_alpha": 32,
                },
            }
        )
        assert config.lora.enabled is True, "enabled is not valid"
        assert config.lora.r == 16, "r is not valid"
        assert config.lora.alpha == 32, "alpha is not valid"

    def test_coerce_config_use_lora_shorthand(self):
        """Test use_lora shorthand flag."""
        config = _coerce_config(
            {
                "model_name": "gpt2",
                "use_lora": True,
            }
        )
        assert config.lora.enabled is True, "enabled is not valid"

    def test_coerce_config_lora_rank_alias(self):
        """Test lora_rank as r alias."""
        config = _coerce_config(
            {
                "model_name": "gpt2",
                "lora": {"enabled": True},
                "lora_rank": 16,
            }
        )
        assert config.lora.r == 16, "r is not valid"

    def test_coerce_config_bf16_require_capability(self):
        """Test bf16_require_capability flag."""
        config = _coerce_config(
            {
                "model_name": "gpt2",
                "bf16_require_capability": True,
            }
        )
        assert config.bf16_require_capability is True, "bf16_require_capability is not valid"

    def test_coerce_config_reproducibility_section(self):
        """Test bf16_require_capability in reproducibility section."""
        config = _coerce_config(
            {
                "model_name": "gpt2",
                "reproducibility": {
                    "bf16_require_capability": True,
                },
            }
        )
        assert config.bf16_require_capability is True, "bf16_require_capability is not valid"

    def test_coerce_config_missing_model_name_raises_error(self):
        """Test that missing model_name raises ValueError."""
        with pytest.raises(ValueError, match="model_name"):
            _coerce_config({})

    def test_coerce_config_invalid_lora_section_raises_error(self):
        """Test that invalid lora section raises TypeError."""
        with pytest.raises(TypeError, match="lora must be a mapping"):
            _coerce_config(
                {
                    "model_name": "gpt2",
                    "lora": "invalid",
                }
            )

    def test_coerce_config_invalid_load_config_raises_error(self):
        """Test that invalid load_config raises TypeError."""
        with pytest.raises(TypeError, match="load_config"):
            _coerce_config(
                {
                    "model_name": "gpt2",
                    "load_config": "invalid",
                }
            )


class TestNeedsBf16:
    """Test bf16 detection helper."""

    def test_needs_bf16_by_name_bf16(self):
        """Test bf16 detection by name."""
        assert _needs_bf16("bf16", None) is True
        assert _needs_bf16("bfloat16", None) is True

    def test_needs_bf16_by_name_lowercase(self):
        """Test case-insensitive bf16 detection."""
        assert _needs_bf16("BF16", None) is True
        assert _needs_bf16("BFLOAT16", None) is True

    def test_needs_bf16_by_name_other_dtypes(self):
        """Test that other dtypes return False."""
        assert _needs_bf16("float32", None) is False
        assert _needs_bf16("fp16", None) is False
        assert _needs_bf16(None, None) is False

    def test_needs_bf16_by_dtype_obj(self):
        """Test bf16 detection by dtype object."""
        import torch

        assert _needs_bf16(None, torch.bfloat16) is True
        assert _needs_bf16(None, torch.float32) is False


class TestDtypeMap:
    """Test dtype mapping."""

    def test_dtype_map_contains_all_dtypes(self):
        """Test that _DTYPE_MAP contains expected dtypes."""
        assert "float32" in _DTYPE_MAP, "Condition must be true"
        assert "fp32" in _DTYPE_MAP, "Condition must be true"
        assert "float16" in _DTYPE_MAP, "Condition must be true"
        assert "fp16" in _DTYPE_MAP, "Condition must be true"
        assert "half" in _DTYPE_MAP, "Condition must be true"
        assert "bfloat16" in _DTYPE_MAP, "Condition must be true"
        assert "bf16" in _DTYPE_MAP, "Condition must be true"

    def test_dtype_map_values_are_torch_dtypes(self):
        """Test that all values in _DTYPE_MAP are torch dtypes."""
        import torch

        for key, dtype in _DTYPE_MAP.items():
            assert isinstance(dtype, torch.dtype), f"Value for {key} is not a torch dtype"
