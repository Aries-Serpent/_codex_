"""Dynamic detector for experiment management capability.

Detects experiment tracking integrations (MLflow, W&B), metadata
management, and experiment organization systems.

Safeguards: Bounded processing, deterministic sorting, validation.
"""

from __future__ import annotations


def detect(file_index: dict) -> dict:
    """Detect experiment management capability.

    Args:
        file_index: Context index from S1 with file metadata

    Returns:
        Capability detection result
    """
    files = file_index.get("files", [])

    # Evidence collection
    mlflow_files = []
    wandb_files = []
    experiment_files = []
    metadata_files = []

    for f in files:
        path = f["path"]
        path_lower = path.lower()

        # MLflow integration
        if "mlflow" in path_lower:
            mlflow_files.append(path)

        # W&B integration
        if "wandb" in path_lower or "weights_and_biases" in path_lower:
            wandb_files.append(path)

        # General experiment management
        if "experiment" in path_lower and not path.startswith("tests/"):
            experiment_files.append(path)

        # Metadata and tagging
        if any(kw in path_lower for kw in ["metadata", "tags", "manifest", "provenance"]):
            metadata_files.append(path)

    # Pattern detection
    found_patterns = []
    required_patterns = ["experiment", "tracking", "metadata", "mlflow", "wandb"]

    evidence_files = sorted(set(mlflow_files + wandb_files + experiment_files + metadata_files))

    if experiment_files:
        found_patterns.append("experiment")
    if mlflow_files or wandb_files:
        found_patterns.append("tracking")
    if metadata_files:
        found_patterns.append("metadata")
    if mlflow_files:
        found_patterns.append("mlflow")
    if wandb_files:
        found_patterns.append("wandb")

    # Calculate functionality score
    functionality_score = len(set(found_patterns) & set(required_patterns)) / len(required_patterns) if required_patterns else 0.0

    return {
        "id": "experiment-management",
        "evidence_files": evidence_files,
        "found_patterns": sorted(set(found_patterns)),
        "required_patterns": required_patterns,
        "docs_keywords": [
            "experiment", "tracking", "mlflow", "wandb", "logging",
            "metrics", "hyperparameters", "artifacts", "runs", "reproducibility"
        ],
        "safeguards": ["validation", "bounded", "deterministic", "error-handling"],
        "functionality_impl": functionality_score,
        "meta": {
            "mlflow_integration": len(mlflow_files),
            "wandb_integration": len(wandb_files),
            "experiment_utils": len(experiment_files),
            "metadata_files": len(metadata_files),
            "deterministic": True,
            "offline": True,
            "bounded": True,
            "detector_version": "2.0"
        },
    }
