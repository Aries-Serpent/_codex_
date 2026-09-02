"""
Training loop initialization helpers.

Extracted from run_training() to reduce cyclomatic complexity.
These helpers encapsulate the initialization logic into smaller,
testable functions with lower complexity.
"""

import logging
import os
import time
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


def setup_differential_privacy_config(
    dp_config: Any, env_prefix: str = "CODEX_DP_"
) -> Any:
    """Extract and setup differential privacy configuration.
    
    Handles:
    - DifferentialPrivacyConfig instances
    - dict-based configs
    - Environment variable fallbacks
    
    Args:
        dp_config: DifferentialPrivacyConfig, dict, or None
        env_prefix: Environment variable prefix
    
    Returns:
        DifferentialPrivacyConfig or None
    
    Reduces complexity by extracting 50+ branch points from run_training.
    """
    from codex_ml.training.dp_config import DifferentialPrivacyConfig
    
    # Fast path: already configured
    if isinstance(dp_config, DifferentialPrivacyConfig):
        return dp_config
    
    # Path 2: dict-based config
    if isinstance(dp_config, dict):
        try:
            return DifferentialPrivacyConfig(**dp_config)
        except TypeError as exc:
            logger.warning("Invalid differential privacy config: %s", exc)
            return None
    
    # Path 3: environment variable configuration
    env_flag = os.getenv(f"{env_prefix}ENABLED")
    if not env_flag or str(env_flag).strip().lower() not in {"1", "true", "yes", "on"}:
        return None
    
    # Build DP kwargs from environment
    dp_kwargs: dict[str, bool | float] = {"enabled": True}
    for field_name, env_name in (
        ("epsilon", f"{env_prefix}EPSILON"),
        ("delta", f"{env_prefix}DELTA"),
        ("noise_multiplier", f"{env_prefix}NOISE_MULTIPLIER"),
        ("max_grad_norm", f"{env_prefix}MAX_GRAD_NORM"),
    ):
        raw = os.getenv(env_name)
        if raw is None:
            continue
        try:
            dp_kwargs[field_name] = float(raw)
        except ValueError:
            logger.debug(f"Unable to parse {field_name} env var {env_name}")
    
    # Check secure RNG
    secure_rng_flag = os.getenv(f"{env_prefix}SECURE_RNG")
    if secure_rng_flag and secure_rng_flag.lower() in {"1", "true", "yes", "on"}:
        dp_kwargs["secure_rng"] = True
    
    # Create config
    try:
        return DifferentialPrivacyConfig(**dp_kwargs)
    except ImportError as exc:
        logger.warning("Differential privacy disabled: %s", exc)
        return None


def setup_artifacts_directory(
    art_dir: Optional[str | Path],
    create_telemetry: bool = False,
) -> Path | None:
    """Setup artifacts directory and initialize metric files.
    
    Args:
        art_dir: Artifacts directory path
        create_telemetry: Whether to create telemetry.ndjson
    
    Returns:
        Path object or None if creation failed
    
    Reduces complexity by extracting try-except blocks and file creation logic.
    """
    if art_dir is None:
        art_dir = Path("runs/train_loop")
    else:
        art_dir = Path(art_dir)
    
    try:
        art_dir.mkdir(parents=True, exist_ok=True)
        
        # Create telemetry file if requested
        if create_telemetry:
            telemetry_file = art_dir / "telemetry.ndjson"
            telemetry_file.touch(exist_ok=True)
        
        # Initialize metrics files
        metrics_ndjson = art_dir / "metrics.ndjson"
        metrics_ndjson.touch(exist_ok=True)
        
        metrics_json = art_dir / "metrics.json"
        if not metrics_json.exists():
            metrics_json.write_text("[]\n", encoding="utf-8")
        
        return art_dir
    
    except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:
        logger.warning("Failed to prepare artifacts directory '%s': %s", art_dir, exc)
        return None


def setup_metrics_registry(
    telemetry_enable: bool,
    telemetry_port: Optional[int],
    env_port_key: str = "CODEX_METRICS_PORT",
) -> tuple[Any | None, int | None]:
    """Setup Prometheus metrics registry and determine port.
    
    Args:
        telemetry_enable: Whether telemetry is enabled
        telemetry_port: Explicit port override
        env_port_key: Environment variable for port
    
    Returns:
        (metrics_registry, port) tuple
    
    Reduces complexity by extracting metrics setup logic.
    """
    try:
        from codex_ml.tracking.metrics import CodexMetricsRegistry, metrics_enabled
    except ImportError:
        logger.debug("Metrics registry not available")
        return None, None
    
    # Determine port
    metrics_port = None
    metrics_env_port = os.getenv(env_port_key)
    
    if metrics_env_port:
        try:
            metrics_port = int(metrics_env_port)
        except ValueError:
            logger.debug(f"Invalid {env_port_key} value '%s'", metrics_env_port)
    
    if metrics_port is None and telemetry_port is not None:
        metrics_port = int(telemetry_port)
    
    # Create registry if needed
    metrics_registry = None
    if metrics_enabled() or telemetry_enable:
        try:
            metrics_registry = CodexMetricsRegistry()
            metrics_registry.active_sessions.set(1)
            from codex_ml.tracking.metrics import start_metrics_server
            start_metrics_server(port=metrics_port or 8000)
        except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:
            logger.debug("Prometheus metrics disabled: %s", exc)
    
    return metrics_registry, metrics_port


def setup_mlflow(
    mlflow_enable: bool,
    mlflow_uri: Optional[str],
    mlflow_experiment: Optional[str],
    run_params: dict[str, Any],
) -> None:
    """Setup MLflow tracking.
    
    Args:
        mlflow_enable: Whether MLflow is enabled
        mlflow_uri: MLflow tracking URI
        mlflow_experiment: MLflow experiment name
        run_params: Parameters to log
    
    Reduces complexity by extracting MLflow setup logic (10+ branches).
    """
    try:
        import mlflow
    except ImportError:
        logger.debug("MLflow not available")
        return
    
    if not mlflow_enable:
        return
    
    try:
        from codex_ml.tracking.mlflow_guard import bootstrap_offline_tracking
        
        safe_uri = bootstrap_offline_tracking()
        
        # Process URI override
        if mlflow_uri:
            if str(mlflow_uri).startswith("file:"):
                safe_uri = str(mlflow_uri)
            elif str(mlflow_uri).startswith("http"):
                logger.warning(
                    "Blocking remote MLflow URI '%s'; using local file backend %s",
                    mlflow_uri,
                    safe_uri,
                )
            else:
                try:
                    safe_uri = Path(mlflow_uri).expanduser().resolve().as_uri()
                except (IOError, OSError, ModuleNotFoundError, ImportError):
                    logger.warning(
                        "Unable to coerce MLflow URI '%s'; using %s",
                        mlflow_uri,
                        safe_uri,
                    )
        
        mlflow.set_tracking_uri(safe_uri)
        mlflow.set_experiment(mlflow_experiment)
        mlflow.start_run()
        mlflow.log_params(run_params)
    
    except Exception as exc:
        logger.warning("MLflow setup failed: %s", exc)


def build_model_kwargs(
    model_cfg: Optional[dict],
    device_str: str,
    dtype_obj: Any,
    lora: bool,
    lora_cfg: Optional[dict],
) -> dict[str, Any]:
    """Build model initialization keyword arguments.
    
    Args:
        model_cfg: Base model config dict
        device_str: Device string
        dtype_obj: Target dtype object
        lora: Whether to enable LoRA
        lora_cfg: LoRA configuration
    
    Returns:
        Model kwargs dict
    
    Reduces complexity by extracting model config building logic.
    """
    model_kwargs = dict(model_cfg or {})
    model_kwargs.setdefault("device", str(device_str))
    
    if dtype_obj is not None:
        model_kwargs.setdefault("dtype", dtype_obj)
    
    if lora:
        model_kwargs["lora"] = {"enabled": True, **(lora_cfg or {})}
    
    return model_kwargs


def build_training_state(
    model: Any,
    optimizer: Any,
    scheduler: Any,
    dataset_total_records: int,
    run_config: Optional[dict],
    art_dir_path: Path | None,
    amp: bool,
    amp_dtype: Optional[str],
    mlflow_enable: bool,
    mlflow_uri: Optional[str],
    mlflow_experiment: Optional[str],
    telemetry_enable: bool,
    telemetry_port: Optional[int],
    grad_accum: int,
    deterministic_cudnn: bool,
    dp_settings: Any,
    privacy_engine: Any,
    metrics_registry: Any,
    session_id: Optional[str],
) -> dict[str, Any]:
    """Build the training state dictionary.
    
    Args:
        Various training parameters
    
    Returns:
        Training state dict
    
    Reduces complexity by extracting state initialization (30+ lines).
    """
    return {
        "start_time": time.time(),
        "model": model,
        "optimizer": optimizer,
        "scheduler": scheduler,
        "dataset_total_records": dataset_total_records,
        "run_config": run_config,
        "artifacts_dir": str(art_dir_path) if art_dir_path else None,
        "amp": {"enabled": amp, "dtype": amp_dtype},
        "mlflow": {
            "enabled": mlflow_enable,
            "uri": mlflow_uri,
            "experiment": mlflow_experiment,
        },
        "telemetry": {"enabled": telemetry_enable, "port": telemetry_port},
        "grad_accum": int(grad_accum),
        "deterministic_cudnn": bool(deterministic_cudnn),
        "callback_errors": [],
        "dp": dp_settings.as_dict() if dp_settings else {"enabled": False},
        "privacy_engine": bool(privacy_engine),
        "metrics_enabled": bool(metrics_registry),
        "session_id": session_id or "unknown",
    }


def setup_model_device_dtype(
    model: Any,
    device_obj: Any,
    dtype_obj: Any,
    dtype_str: Optional[str],
    art_dir_path: Path | None,
) -> None:
    """Move model to device/dtype and handle telemetry.
    
    Includes bf16 downcast detection and telemetry logging.
    
    Args:
        model: PyTorch model
        device_obj: Target device
        dtype_obj: Target dtype
        dtype_str: String representation of target dtype
        art_dir_path: Artifacts directory
    
    Reduces complexity by extracting nested try-except and if-else blocks (30+ branches).
    """
    try:
        import torch as _torch
    except ImportError:
        logger.debug("PyTorch not available for dtype checks")
        return
    
    try:
        model.to(device_obj)
        if dtype_obj is not None:
            model = model.to(dtype=dtype_obj)
    except (ConnectionError, TimeoutError) as exc:
        logger.warning("Failed to move model to device/dtype: %s", exc)
        return
    
    # Check for effective dtype mismatches
    try:
        eff = _first_param_dtype(model) if hasattr(model, 'parameters') else None
        if eff is None:
            return
        
        # Determine if bf16 was requested
        requested_is_bf16 = False
        req_str = None
        
        if dtype_obj is not None:
            requested_is_bf16 = str(dtype_obj) == str(getattr(_torch, "bfloat16", None))
            req_str = str(dtype_obj)
        
        if (not requested_is_bf16 and isinstance(dtype_str, str) and 
            dtype_str.lower() in {"bf16", "bfloat16"}):
            requested_is_bf16 = True
            req_str = dtype_str
        
        # Log downcast event if applicable
        if (requested_is_bf16 and eff is not None and 
            eff != str(getattr(_torch, "bfloat16", None))):
            from codex_ml._train_init_helpers import _append_metrics_event_local
            _append_metrics_event_local(
                art_dir_path,
                {
                    "type": "telemetry",
                    "event": "bf16_downcast",
                    "requested": req_str or "bf16",
                    "effective": eff,
                    "message": "bf16 requested but parameters not bf16 (downcast)",
                    "timestamp": time.time(),
                },
            )
    except Exception as e:
        logger.debug("Failed to check dtype mismatch: %s", e)


def setup_dataset_and_loader(
    batch_size: Optional[int],
    vocab_size: int,
    seed: int,
    dataset_cast_policy: Optional[str],
    dtype_obj: Any,
    device_obj: Any,
    art_dir_path: Path | None,
) -> tuple[Any, Any]:
    """Setup PyTorch dataset and dataloader.
    
    Args:
        batch_size: Batch size for training
        vocab_size: Vocabulary size
        seed: Random seed
        dataset_cast_policy: Policy for dataset casting
        dtype_obj: Target dtype
        device_obj: Target device
        art_dir_path: Artifacts directory
    
    Returns:
        (dataset, train_loader) tuple
    
    Reduces complexity by extracting dataset initialization logic (15+ branches).
    """
    try:
        from codex_ml.training.collate import _make_casting_collate
        from codex_ml.training.toy_dataset import ToyDataset
        from torch.utils.data import DataLoader
    except ImportError:
        logger.debug("PyTorch or dataset utilities not available")
        return None, None
    
    effective_batch = batch_size or 8
    dataset = ToyDataset(
        num_samples=64,
        seq_len=16,
        vocab_size=vocab_size,
        seed=seed,
    )
    
    collate = _make_casting_collate(dataset_cast_policy, dtype_obj, device_obj, art_dir_path)
    train_loader = DataLoader(
        dataset,
        batch_size=effective_batch,
        shuffle=True,
        collate_fn=collate,
    )
    
    return dataset, train_loader


def _append_metrics_event_local(
    art_dir: Path | None, 
    event: dict[str, Any]
) -> None:
    """Append metrics event to file."""
    if art_dir is None:
        return
    
    try:
        metrics_file = art_dir / "metrics_events.jsonl"
        with open(metrics_file, "a") as f:
            import json
            f.write(json.dumps(event) + "\n")
    except Exception as e:
        logger.debug("Failed to append metrics event: %s", e)


def _first_param_dtype(model: Any) -> Optional[str]:
    """Get the dtype of the first parameter in the model."""
    try:
        for param in model.parameters():
            return str(param.dtype)
    except Exception:
        return None


def _select_parameters_for_optimization(model: Any) -> Any:
    """Select parameters from the model for optimization.
    
    Returns:
        Model parameters iterator, or None if model has no parameters.
    """
    try:
        return list(model.parameters())
    except Exception:
        return None


def setup_optimizer_with_dp(
    model: Any,
    learning_rate: float,
    dtype_obj: Any,
    dp_settings: Any,
    train_loader: Any,
) -> tuple[Any, Any]:
    """Setup optimizer and differential privacy engine.
    
    Args:
        model: PyTorch model
        learning_rate: Learning rate
        dtype_obj: Target dtype
        dp_settings: Differential privacy config
        train_loader: DataLoader for training
    
    Returns:
        (optimizer, privacy_engine) tuple
    
    Reduces complexity by extracting DP and optimizer setup (20+ branches).
    """
    try:
        import torch.optim as optim
        from codex_ml.training.dp import make_private_model
    except ImportError:
        logger.debug("PyTorch optim or DP not available")
        return None, None
    
    # Setup base optimizer
    optimizer = None
    try:
        params = _select_parameters_for_optimization(model)
        if params:
            try:
                lr_value = float(learning_rate)
            except (TypeError, ValueError):
                lr_value = 1e-3
            optimizer = optim.Adam(params, lr=lr_value)
            
            # Check dtype compatibility
            try:
                eff_dtype = _first_param_dtype(model)
                if eff_dtype is not None and dtype_obj is not None and eff_dtype != str(dtype_obj):
                    logger.warning(
                        "Optimizer built for params dtype=%s; requested model dtype=%s",
                        eff_dtype,
                        str(dtype_obj),
                    )
            except Exception as e:
                logger.debug("Failed to check optimizer dtype compatibility: %s", e)
    except Exception as e:
        logger.warning("Failed to setup optimizer: %s", e)
        return None, None
    
    # Setup differential privacy if requested
    privacy_engine = None
    if dp_settings is not None and optimizer is not None and train_loader is not None:
        try:
            model, optimizer, train_loader, privacy_engine = make_private_model(
                model, optimizer, train_loader, dp_settings
            )
        except ImportError as exc:
            logger.warning("Differential privacy disabled: %s", exc)
            dp_settings = None
        except (IOError, OSError, ModuleNotFoundError) as exc:
            logger.warning("Failed to enable differential privacy: %s", exc)
            dp_settings = None
    
    return optimizer, privacy_engine
