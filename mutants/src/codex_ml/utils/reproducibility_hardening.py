"""
WP-G: Reproducibility Hardening

Comprehensive reproducibility utilities combining deterministic training,
environment capture, and seed management for full reproducibility.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import random
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from codex.logging.structured_logger import logger

logger = logging.getLogger(__name__)

__all__ = [
    "ReproducibilityManager",
    "create_reproducibility_manifest",
    "enable_deterministic_training",
    "save_env_snapshot",
]


def enable_deterministic_training(seed: int = 42, *, strict: bool = False) -> dict[str, Any]:
    """
    Enable deterministic training with comprehensive seeding.

    Sets seeds for:
    - Python built-in random
    - NumPy (if available)
    - PyTorch (if available)
    - TensorFlow (if available)
    - CUDA/CuDNN (if available)

    Args:
        seed: Random seed to use (default: 42)
        strict: If True, enables strictest determinism (may impact performance)

    Returns:
        Dict with status of each seeding operation

    Example:
        >>> status = enable_deterministic_training(seed=42, strict=True)
        >>> logger.info(status['python_random'])
        True
    """
    logger.info(
        f"Enabling deterministic training with seed={seed}, strict={strict}"
    )  # codeql[py/clear-text-logging-sensitive-data]

    status: dict[str, Any] = {}
    try:
        random.seed(seed)
        status["python_random"] = True
        logger.debug("✓ Python random seeded")  # codeql[py/clear-text-logging-sensitive-data]
    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        status["python_random"] = False
        logger.warning(
            "Failed to seed Python random: <ERROR_TYPE>"
        )  # codeql[py/clear-text-logging-sensitive-data]

    # 2. Python hash seed (for dict/set order)
    try:
        os.environ["PYTHONHASHSEED"] = str(seed)
        status["python_hash_seed"] = True
        logger.debug("✓ PYTHONHASHSEED set")  # codeql[py/clear-text-logging-sensitive-data]
    except (ImportError, AttributeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        status["python_hash_seed"] = False
        logger.warning(
            "Failed to set PYTHONHASHSEED: <ERROR_TYPE>"
        )  # codeql[py/clear-text-logging-sensitive-data]

    # 3. NumPy
    try:
        import numpy as np

        np.random.seed(seed)
        status["numpy"] = True
        logger.debug("✓ NumPy seeded")  # codeql[py/clear-text-logging-sensitive-data]
    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        status["numpy"] = None  # Not installed
        logger.debug(
            "NumPy not available (skipped)"
        )  # codeql[py/clear-text-logging-sensitive-data]
    except AttributeError as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        status["numpy"] = False
        logger.warning(
            "Failed to seed NumPy: <ERROR_TYPE>"
        )  # codeql[py/clear-text-logging-sensitive-data]

    # 4. PyTorch
    try:
        import torch

        torch.manual_seed(seed)
        status["torch"] = True
        logger.debug("✓ PyTorch seeded")  # codeql[py/clear-text-logging-sensitive-data]

        # CUDA seeding
        if torch.cuda.is_available():
            torch.cuda.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
            status["torch_cuda"] = True
            logger.debug("✓ PyTorch CUDA seeded")  # codeql[py/clear-text-logging-sensitive-data]

            # CuDNN determinism
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
            status["cudnn_deterministic"] = True
            logger.debug(
                "✓ CuDNN deterministic mode enabled"
            )  # codeql[py/clear-text-logging-sensitive-data]

            # CUDA workspace config for deterministic algorithms
            os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
            status["cublas_workspace"] = True
            logger.debug(
                "✓ CUBLAS workspace configured"
            )  # codeql[py/clear-text-logging-sensitive-data]
        else:
            status["torch_cuda"] = None  # CUDA not available
            status["cudnn_deterministic"] = None
            status["cublas_workspace"] = None

        # PyTorch deterministic algorithms
        if strict:
            try:
                torch.use_deterministic_algorithms(True)
                status["torch_deterministic_algorithms"] = True
                logger.debug(
                    "✓ PyTorch deterministic algorithms enabled (strict mode)"
                )  # codeql[py/clear-text-logging-sensitive-data]
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.debug(
                    "Exception: <ERROR_TYPE>"
                )  # codeql[py/clear-text-logging-sensitive-data]
                status["torch_deterministic_algorithms"] = False
                logger.warning(
                    "Failed to enable deterministic algorithms: <ERROR_TYPE>"
                )  # codeql[py/clear-text-logging-sensitive-data]
        else:
            status["torch_deterministic_algorithms"] = None  # Not enabled in non-strict mode

    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        status["torch"] = None  # Not installed
        status["torch_cuda"] = None
        status["cudnn_deterministic"] = None
        status["cublas_workspace"] = None
        status["torch_deterministic_algorithms"] = None
        logger.debug(
            "PyTorch not available (skipped)"
        )  # codeql[py/clear-text-logging-sensitive-data]
    except AttributeError as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        status["torch"] = False
        logger.warning(
            "Failed to seed PyTorch: <ERROR_TYPE>"
        )  # codeql[py/clear-text-logging-sensitive-data]

    # 5. TensorFlow (if available)
    try:
        import tensorflow as tf

        # Set seed
        tf.random.set_seed(seed)
        status["tensorflow"] = True
        logger.debug("✓ TensorFlow seeded")  # codeql[py/clear-text-logging-sensitive-data]

        # Enable deterministic ops in TF 2.x
        if hasattr(tf.config.experimental, "enable_op_determinism"):
            tf.config.experimental.enable_op_determinism()
            status["tensorflow_deterministic"] = True
            logger.debug(
                "✓ TensorFlow deterministic ops enabled"
            )  # codeql[py/clear-text-logging-sensitive-data]
        else:
            status["tensorflow_deterministic"] = None

    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        status["tensorflow"] = None  # Not installed
        status["tensorflow_deterministic"] = None
        logger.debug(
            "TensorFlow not available (skipped)"
        )  # codeql[py/clear-text-logging-sensitive-data]
    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        status["tensorflow"] = False
        logger.warning(
            "Failed to seed TensorFlow: <ERROR_TYPE>"
        )  # codeql[py/clear-text-logging-sensitive-data]

    # Log summary
    enabled_count = sum(1 for v in status.values() if v is True)
    total_applicable = sum(1 for v in status.values() if v is not None)

    logger.info(
        f"✓ Deterministic training enabled: {enabled_count}/{total_applicable} components seeded"
    )

    return status


def save_env_snapshot(output_path: Path | str, include_pip_freeze: bool = True) -> dict[str, Any]:
    """
    Save environment snapshot for reproducibility.

    Captures:
    - Python version and executable
    - Platform information
    - Git commit (if in git repo)
    - Installed packages (pip freeze)
    - CUDA/GPU information (if available)
    - Environment variables (selected)

    Args:
        output_path: Path to save snapshot (e.g., "artifacts/env_snapshot.txt")
        include_pip_freeze: Whether to include pip freeze output

    Returns:
        Dict with environment snapshot data

    Example:
        >>> snapshot = save_env_snapshot("artifacts/env_snapshot.txt")
        >>> logger.info(f"Python: {snapshot['python_version']}")
    """  # noqa: E501
    logger.info(
        f"Capturing environment snapshot to {output_path}"
    )  # codeql[py/clear-text-logging-sensitive-data]

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    snapshot: dict[str, Any] = {}  # 1. Python information
    snapshot["python_version"] = sys.version
    snapshot["python_executable"] = sys.executable
    snapshot["python_version_info"] = {
        "major": sys.version_info.major,
        "minor": sys.version_info.minor,
        "micro": sys.version_info.micro,
    }

    # 2. Platform information
    import platform

    snapshot["platform"] = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }

    # 3. Git information
    try:
        git_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=5,
        ).strip()
        snapshot["git_commit"] = git_commit

        # Check for uncommitted changes
        git_status = subprocess.check_output(
            ["git", "status", "--porcelain"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=5,
        ).strip()
        snapshot["git_dirty"] = bool(git_status)

    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        snapshot["git_commit"] = None
        snapshot["git_dirty"] = None
        logger.debug(
            "Git information not available: <ERROR_TYPE>"
        )  # codeql[py/clear-text-logging-sensitive-data]

    # 4. Pip freeze (installed packages)
    if include_pip_freeze:
        try:
            pip_freeze = subprocess.check_output(
                [sys.executable, "-m", "pip", "freeze"], text=True, timeout=30
            )
            snapshot["pip_freeze"] = pip_freeze.strip().split("\n")
        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
            snapshot["pip_freeze"] = []
            logger.warning(
                "Failed to capture pip freeze: <ERROR_TYPE>"
            )  # codeql[py/clear-text-logging-sensitive-data]
    else:
        snapshot["pip_freeze"] = None

    # 5. GPU information (if available)
    try:
        import torch

        snapshot["cuda_available"] = torch.cuda.is_available()

        if torch.cuda.is_available():
            snapshot["cuda_version"] = torch.version.cuda
            snapshot["cudnn_version"] = torch.backends.cudnn.version()
            snapshot["gpu_count"] = torch.cuda.device_count()
            snapshot["gpu_devices"] = [
                {
                    "index": i,
                    "name": torch.cuda.get_device_name(i),
                    "capability": torch.cuda.get_device_capability(i),
                }
                for i in range(torch.cuda.device_count())
            ]
        else:
            snapshot["cuda_version"] = None
            snapshot["cudnn_version"] = None
            snapshot["gpu_count"] = 0
            snapshot["gpu_devices"] = []

    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        snapshot["cuda_available"] = None
        snapshot["cuda_version"] = None
        snapshot["cudnn_version"] = None
        snapshot["gpu_count"] = None
        snapshot["gpu_devices"] = None
    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        logger.warning(
            "Failed to capture GPU information: <ERROR_TYPE>"
        )  # codeql[py/clear-text-logging-sensitive-data]

    # 6. Selected environment variables
    env_vars_to_capture = [
        "PYTHONHASHSEED",
        "CUBLAS_WORKSPACE_CONFIG",
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "CUDA_VISIBLE_DEVICES",
    ]
    snapshot["environment_variables"] = {var: os.environ.get(var) for var in env_vars_to_capture}

    # 7. Timestamp
    snapshot["timestamp"] = datetime.now(timezone.utc).isoformat()

    # Write to file (human-readable format)
    with open(output_path, "w") as f:
        f.write("# Environment Snapshot for Reproducibility\n")
        f.write(f"# Generated: {snapshot['timestamp']}\n")
        f.write("\n")

        f.write("## Python Information\n")
        f.write(f"Version: {snapshot['python_version']}\n")
        f.write(f"Executable: {snapshot['python_executable']}\n")
        f.write("\n")

        f.write("## Platform Information\n")
        for key, value in snapshot["platform"].items():
            f.write(f"{key}: {value}\n")
        f.write("\n")

        if snapshot["git_commit"]:
            f.write("## Git Information\n")
            f.write(f"Commit: {snapshot['git_commit']}\n")
            f.write(f"Dirty: {snapshot['git_dirty']}\n")
            f.write("\n")

        if snapshot.get("cuda_available"):
            f.write("## GPU Information\n")
            f.write(f"CUDA Available: {snapshot['cuda_available']}\n")
            f.write(f"CUDA Version: {snapshot['cuda_version']}\n")
            f.write(f"CuDNN Version: {snapshot['cudnn_version']}\n")
            f.write(f"GPU Count: {snapshot['gpu_count']}\n")
            for gpu in snapshot["gpu_devices"]:
                f.write(f"  GPU {gpu['index']}: {gpu['name']} (capability {gpu['capability']})\n")
            f.write("\n")

        f.write("## Environment Variables\n")
        for var, value in snapshot["environment_variables"].items():
            f.write(f"{var}: {value}\n")
        f.write("\n")

        if snapshot["pip_freeze"]:
            f.write("## Installed Packages (pip freeze)\n")
            for package in snapshot["pip_freeze"]:
                f.write(f"{package}\n")

    # Also save JSON version
    json_path = output_path.with_suffix(".json")
    with open(json_path, "w") as f:
        json.dump(snapshot, f, indent=2, default=str)

    logger.info(
        f"✓ Environment snapshot saved to {output_path} and {json_path}"
    )  # codeql[py/clear-text-logging-sensitive-data]

    return snapshot


def create_reproducibility_manifest(
    seed: int,
    output_dir: Path | str,
    config: Optional[dict[str, Any]] = None,
    dataset_hash: Optional[str] = None,
) -> dict[str, Any]:
    """
    Create comprehensive reproducibility manifest.

    Combines deterministic seeding status and environment snapshot
    into a single manifest for full reproducibility documentation.

    Args:
        seed: Random seed used
        output_dir: Directory to save manifest files
        config: Optional training configuration to include
        dataset_hash: Optional dataset hash/identifier

    Returns:
        Complete reproducibility manifest

    Example:
        >>> manifest = create_reproducibility_manifest(
        ...     seed=42,
        ...     output_dir="artifacts/repro",
        ...     config={"lr": 1e-4},
        ...     dataset_hash="abc123"
        ... )
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(
        f"Creating reproducibility manifest in {output_dir}"
    )  # codeql[py/clear-text-logging-sensitive-data]

    manifest: dict[str, Any] = {}
    seed_status = enable_deterministic_training(seed=seed)
    manifest["seed"] = seed
    manifest["seeding_status"] = seed_status

    # 2. Environment snapshot
    env_snapshot_path = output_dir / "env_snapshot.txt"
    env_snapshot = save_env_snapshot(env_snapshot_path)
    manifest["environment"] = {
        "python_version": env_snapshot["python_version"],
        "git_commit": env_snapshot.get("git_commit"),
        "git_dirty": env_snapshot.get("git_dirty"),
        "cuda_available": env_snapshot.get("cuda_available"),
        "platform": env_snapshot["platform"],
    }
    manifest["env_snapshot_path"] = str(env_snapshot_path)

    # 3. Configuration
    if config is not None:
        manifest["config"] = config

    # 4. Dataset information
    if dataset_hash is not None:
        manifest["dataset_hash"] = dataset_hash

    # 5. Timestamp
    manifest["created_at"] = datetime.now(timezone.utc).isoformat()

    # 6. Compute manifest hash
    manifest_str = json.dumps(manifest, sort_keys=True, default=str)
    manifest_hash = hashlib.sha256(manifest_str.encode()).hexdigest()[:16]
    manifest["manifest_hash"] = manifest_hash

    # Save manifest
    manifest_path = output_dir / "reproducibility_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2, default=str)

    logger.info(
        f"✓ Reproducibility manifest created: {manifest_path}"
    )  # codeql[py/clear-text-logging-sensitive-data]
    logger.info(f"  Manifest hash: {manifest_hash}")  # codeql[py/clear-text-logging-sensitive-data]

    return manifest


class ReproducibilityManager:
    """
    Manager for reproducibility throughout training lifecycle.

    Handles deterministic seeding, environment capture, and manifest creation
    in a unified interface.

    Example:
        >>> manager = ReproducibilityManager(seed=42, output_dir="artifacts/repro")
        >>> manager.setup()  # Enable deterministic training
        >>> # ... training code ...
        >>> manager.finalize(config=config_dict, dataset_hash="abc123")
    """

    def __init__(self, seed: int = 42, output_dir: Path | str = "artifacts/reproducibility"):
        """
        Initialize reproducibility manager.

        Args:
            seed: Random seed to use
            output_dir: Directory for reproducibility artifacts
        """
        self.seed = seed
        self.output_dir = Path(output_dir)
        self.manifest: Optional[dict[str, Any]] = None

    def setup(self, strict: bool = False) -> dict[str, Any]:
        """
        Set up deterministic training environment.

        Args:
            strict: If True, enable strictest determinism

        Returns:
            Seeding status dict
        """
        logger.info(
            f"Setting up reproducibility (seed={self.seed}, strict={strict})"
        )  # codeql[py/clear-text-logging-sensitive-data]
        return enable_deterministic_training(seed=self.seed, strict=strict)

    def capture_environment(self) -> dict[str, Any]:
        """
        Capture environment snapshot.

        Returns:
            Environment snapshot dict
        """
        snapshot_path = self.output_dir / "env_snapshot.txt"
        return save_env_snapshot(snapshot_path)

    def finalize(
        self,
        config: Optional[dict[str, Any]] = None,
        dataset_hash: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Finalize reproducibility documentation.

        Creates complete manifest with all reproducibility information.

        Args:
            config: Training configuration
            dataset_hash: Dataset hash/identifier

        Returns:
            Complete reproducibility manifest
        """
        self.manifest = create_reproducibility_manifest(
            seed=self.seed,
            output_dir=self.output_dir,
            config=config,
            dataset_hash=dataset_hash,
        )
        return self.manifest

    def get_manifest(self) -> Optional[dict[str, Any]]:
        """Get the reproducibility manifest (if finalized)."""
        return self.manifest
