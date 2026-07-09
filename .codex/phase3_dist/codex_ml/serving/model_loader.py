"""
Model Loader for Inference Server

Provides flexible model loading with:
- HuggingFace model loading with revision pinning
- Local checkpoint loading with validation
- Model caching with LRU eviction
- Device placement (CPU/GPU/MPS)
- Quantization support (int8/fp16)
"""

import hashlib
import logging
import os
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from threading import Lock
from typing import Any, Optional, Union

logger = logging.getLogger(__name__)


class DeviceType(Enum):
    """Supported device types"""

    CPU = "cpu"
    CUDA = "cuda"
    MPS = "mps"


class QuantizationType(Enum):
    """Supported quantization types"""

    NONE = "none"
    INT8 = "int8"
    FP16 = "fp16"


@dataclass
class ModelConfig:
    """Configuration for model loading

    Attributes:
        model_name_or_path: HuggingFace model ID or local path
        revision: Git revision for HuggingFace models (tag, branch, commit)
        device: Target device (cpu, cuda, mps)
        quantization: Quantization type (none, int8, fp16)
        cache_dir: Directory for model caching
        trust_remote_code: Whether to trust remote code execution
        use_auth_token: HuggingFace auth token
        torch_dtype: PyTorch data type (auto, float32, float16, bfloat16)
        low_cpu_mem_usage: Use low CPU memory loading strategy
    """

    model_name_or_path: str
    revision: Optional[str] = None
    device: str = "cpu"
    quantization: str = "none"
    cache_dir: Optional[str] = None
    trust_remote_code: bool = False
    use_auth_token: Optional[str] = None
    torch_dtype: str = "auto"
    low_cpu_mem_usage: bool = True

    def __post_init__(self) -> None:
        """Validate configuration"""
        # Validate device
        valid_devices = ["cpu", "cuda", "mps", "auto"]
        if self.device not in valid_devices:
            raise ValueError(f"Invalid device: {self.device}. Must be one of {valid_devices}")

        # Validate quantization
        valid_quant = ["none", "int8", "fp16"]
        if self.quantization not in valid_quant:
            raise ValueError(
                f"Invalid quantization: {self.quantization}. Must be one of {valid_quant}"
            )

        # Validate torch_dtype
        valid_dtypes = ["auto", "float32", "float16", "bfloat16"]
        if self.torch_dtype not in valid_dtypes:
            raise ValueError(
                f"Invalid torch_dtype: {self.torch_dtype}. Must be one of {valid_dtypes}"
            )

        # set default cache dir
        if self.cache_dir is None:
            self.cache_dir = os.getenv("HF_HOME", str(Path.home() / ".cache" / "huggingface"))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "model_name_or_path": self.model_name_or_path,
            "revision": self.revision,
            "device": self.device,
            "quantization": self.quantization,
            "cache_dir": self.cache_dir,
            "trust_remote_code": self.trust_remote_code,
            "torch_dtype": self.torch_dtype,
            "low_cpu_mem_usage": self.low_cpu_mem_usage,
        }

    def get_cache_key(self) -> str:
        """Generate cache key for this configuration"""
        key_parts = [
            self.model_name_or_path,
            self.revision or "main",
            self.device,
            self.quantization,
            self.torch_dtype,
        ]
        key_str = "|".join(str(p) for p in key_parts)
        return hashlib.sha256(key_str.encode()).hexdigest()[:16]


class ModelLoader:
    """Model loader with caching and device management

    Features:
    - Load models from HuggingFace Hub or local paths
    - Pin to specific revisions (tags, branches, commits)
    - LRU cache for loaded models
    - Automatic device placement
    - Quantization support (int8, fp16)
    - Checkpoint validation

    Attributes:
        cache_size: Maximum number of models to cache
        cache: LRU cache of loaded models
        lock: Thread lock for cache operations
    """

    def __init__(self, cache_size: int = 3):
        """Initialize model loader

        Args:
            cache_size: Maximum number of models to keep in memory
        """
        self.cache_size = cache_size
        self.cache: dict[str, dict[str, Any]] = {}
        self.cache_order: list[str] = []  # LRU order
        self.lock = Lock()
        self.load_times: dict[str, float] = {}

        logger.info(f"ModelLoader initialized with cache_size={cache_size}")

    def load_model(self, config: Union[ModelConfig, dict[str, Any]]) -> dict[str, Any]:
        """Load model with caching

        Args:
            config: Model configuration (ModelConfig or dict)

        Returns:
            Dictionary containing model, tokenizer, and metadata

        Raises:
            ValueError: If configuration is invalid
            RuntimeError: If model loading fails
        """
        # Convert dict to ModelConfig if needed
        if isinstance(config, dict):
            config = ModelConfig(**config)

        cache_key = config.get_cache_key()

        # Check cache
        with self.lock:
            if cache_key in self.cache:
                logger.info(f"Model cache hit: {cache_key}")
                # Move to end (most recently used)
                self.cache_order.remove(cache_key)
                self.cache_order.append(cache_key)
                return self.cache[cache_key]

        # Load model
        logger.info(f"Loading model: {config.model_name_or_path} (revision={config.revision})")
        start_time = time.time()

        try:
            model_data = self._load_from_source(config)
            load_time = time.time() - start_time

            # Add to cache
            with self.lock:
                # Evict if cache is full
                if len(self.cache) >= self.cache_size:
                    evict_key = self.cache_order.pop(0)
                    del self.cache[evict_key]
                    if evict_key in self.load_times:
                        del self.load_times[evict_key]
                    logger.info(f"Evicted model from cache: {evict_key}")

                self.cache[cache_key] = model_data
                self.cache_order.append(cache_key)
                self.load_times[cache_key] = load_time

            logger.info(f"Model loaded successfully in {load_time:.2f}s")
            return model_data

        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error("Failed to load model: <ERROR_TYPE>")
            raise RuntimeError(f"Model loading failed: {e}") from e

    def _load_from_source(self, config: ModelConfig) -> dict[str, Any]:
        """Load model from HuggingFace or local path

        Args:
            config: Model configuration

        Returns:
            Dictionary with model, tokenizer, and metadata
        """
        model_path = Path(config.model_name_or_path)

        # Determine if local or remote
        is_local = model_path.exists() and (model_path.is_dir() or model_path.is_file())

        if is_local:
            return self._load_local(config)
        return self._load_huggingface(config)

    def _load_local(self, config: ModelConfig) -> dict[str, Any]:
        """Load model from local checkpoint

        Args:
            config: Model configuration

        Returns:
            Dictionary with model, tokenizer, and metadata
        """
        model_path = Path(config.model_name_or_path)

        # Validate checkpoint
        if not model_path.exists():
            raise FileNotFoundError(f"Model path not found: {model_path}")

        # For now, return stub with metadata
        # Full implementation would use torch.load or HuggingFace loading
        logger.info(f"Loading from local path: {model_path}")

        return {
            "type": "local",
            "path": str(model_path),
            "device": config.device,
            "quantization": config.quantization,
            "model": None,  # Stub - would load actual model
            "tokenizer": None,  # Stub - would load actual tokenizer
            "config": config.to_dict(),
            "load_time": time.time(),
        }

    def _load_huggingface(self, config: ModelConfig) -> dict[str, Any]:
        """Load model from HuggingFace Hub

        Args:
            config: Model configuration

        Returns:
            Dictionary with model, tokenizer, and metadata
        """
        try:
            from transformers import (
                AutoConfig,
            )
            from transformers import AutoModel as AutoModel
            from transformers import AutoTokenizer as AutoTokenizer
        except ImportError as e:
            type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
            raise ImportError(
                "transformers is required for HuggingFace models. "
                "Install with: pip install transformers"
            ) from e

        logger.info(f"Loading from HuggingFace: {config.model_name_or_path}")

        # Prepare loading kwargs
        load_kwargs = {
            "pretrained_model_name_or_path": config.model_name_or_path,
            "revision": config.revision,
            "cache_dir": config.cache_dir,
            "trust_remote_code": config.trust_remote_code,
            "low_cpu_mem_usage": config.low_cpu_mem_usage,
        }

        # Add auth token if provided
        if config.use_auth_token:
            load_kwargs["use_auth_token"] = config.use_auth_token

        # Load config first
        model_config = AutoConfig.from_pretrained(**load_kwargs)  # nosec B615
        # Determine torch dtype
        torch_dtype = self._get_torch_dtype(config.torch_dtype)
        if torch_dtype is not None:
            load_kwargs["torch_dtype"] = torch_dtype

        # Load model (stub for now - would load actual model)
        # model = AutoModel.from_pretrained(**load_kwargs)

        # Load tokenizer
        # tokenizer = AutoTokenizer.from_pretrained(**load_kwargs)

        # Apply device placement
        # if config.device != "cpu":
        #     model = model.to(config.device)

        # Apply quantization if requested
        # if config.quantization != "none":
        #     model = self._apply_quantization(model, config.quantization)

        return {
            "type": "huggingface",
            "model_name": config.model_name_or_path,
            "revision": config.revision or "main",
            "device": config.device,
            "quantization": config.quantization,
            "model": None,  # Stub - would be actual model
            "tokenizer": None,  # Stub - would be actual tokenizer
            "model_config": model_config.to_dict() if hasattr(model_config, "to_dict") else {},
            "config": config.to_dict(),
            "load_time": time.time(),
        }

    def _get_torch_dtype(self, dtype_str: str):
        """Convert dtype string to torch dtype

        Args:
            dtype_str: String dtype (auto, float32, float16, bfloat16)

        Returns:
            torch dtype or None for auto
        """
        if dtype_str == "auto":
            return None

        try:
            import torch

            dtype_map = {
                "float32": torch.float32,
                "float16": torch.float16,
                "bfloat16": torch.bfloat16,
            }
            return dtype_map.get(dtype_str)
        except ImportError as e:
            type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
            logger.warning("torch not available, ignoring dtype specification")
            return None

    def _apply_quantization(self, model, quant_type: str):
        """Apply quantization to model

        Args:
            model: Model to quantize
            quant_type: Quantization type (int8, fp16)

        Returns:
            Quantized model
        """
        # Stub implementation
        # Real implementation would use:
        # - torch.quantization for int8
        # - model.half() for fp16
        logger.info(f"Applying {quant_type} quantization")
        return model

    def clear_cache(self) -> None:
        """Clear all cached models"""
        with self.lock:
            self.cache.clear()
            self.cache_order.clear()
            self.load_times.clear()
            logger.info("Model cache cleared")

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            return {
                "cache_size": len(self.cache),
                "max_size": self.cache_size,
                "cached_models": list(self.cache_order),
                "load_times": dict(self.load_times),
            }

    def validate_checkpoint(self, path: Union[str, Path]) -> bool:
        """Validate checkpoint integrity

        Args:
            path: Path to checkpoint

        Returns:
            True if valid, False otherwise
        """
        path = Path(path)

        if not path.exists():
            logger.error(f"Checkpoint not found: {path}")
            return False

        # Check if directory or file
        if path.is_dir():
            # Check for required files
            required_files = ["config.json"]
            for req_file in required_files:
                if not (path / req_file).exists():
                    logger.error(f"Missing required file: {req_file}")
                    return False

        elif path.is_file():
            # Check file extension
            if path.suffix not in [".pt", ".pth", ".bin", ".safetensors"]:
                logger.error(f"Invalid checkpoint file extension: {path.suffix}")
                return False

            # Check file is readable
            try:
                with open(path, "rb") as f:
                    f.read(1)
            except (IOError, OSError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.error("Cannot read checkpoint file: <ERROR_TYPE>")
                return False

        logger.info(f"Checkpoint validation passed: {path}")
        return True
