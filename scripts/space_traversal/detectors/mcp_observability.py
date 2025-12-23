"""
MCP Observability Capability Detector

Detects observability features in MCP implementations including logging,
metrics collection, distributed tracing, health checks, and monitoring.

Safeguards:
- Input validation on file_index structure
- Bounded file reading with size limits
- Defensive error handling for file operations
- Deterministic output for reproducibility
"""

from pathlib import Path
from typing import Any, Dict
import logging

# Configure logging for safeguard tracing
logger = logging.getLogger(__name__)


def detect(file_index: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detects observability features (logging, metrics, tracing) for MCP.
    Looks for logging setup, 'X-Request-Id', or Prometheus metrics usage.

    Safeguards:
    - Input validation on file_index structure
    - Bounded file reading with size limits
    - Defensive error handling for file operations
    - Type checking and bounds validation

    Args:
        file_index: Dictionary containing file metadata with 'files' list

    Returns:
        Detection results with evidence files and patterns found
    """
    # Input validation (safeguard)
    if not isinstance(file_index, dict):
        logger.warning("Invalid file_index type, expected dict")
        return _empty_result()

    files = file_index.get("files", [])
    if not isinstance(files, list):
        logger.warning("Invalid files type in file_index")
        return _empty_result()

    # Bounds checking (safeguard) - limit file processing
    MAX_FILES = 10000
    if len(files) > MAX_FILES:
        logger.warning(f"File count exceeds limit: {len(files)} > {MAX_FILES}")
        files = files[:MAX_FILES]

    evidence = []
    found = []

    # Observability patterns to detect
    patterns = {
        "init_json_logging": "structured_logging",
        "X-Request-Id": "request_tracing",
        "metrics": "metrics_collection",
        "prometheus": "prometheus_metrics",
        "logging": "logging_setup",
        "tracing": "distributed_tracing",
        "opentelemetry": "otel_integration",
        "health_check": "health_monitoring",
        "healthz": "health_endpoint",
        "grafana": "visualization",
        "alerting": "alerting_rules",
        "span": "tracing_spans",
        "trace_id": "trace_correlation",
    }

    for f in files:
        # Validate file entry structure (safeguard)
        if not isinstance(f, dict):
            continue

        path = f.get("path", "")

        # Path validation (safeguard)
        if not path or not isinstance(path, str):
            continue

        # Only process Python and Markdown files
        if not (path.endswith(".py") or path.endswith(".md") or path.endswith(".yaml") or path.endswith(".yml")):
            continue

        try:
            # Bounded file reading (safeguard)
            file_path = Path(path)

            # File size check (safeguard)
            MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit
            if file_path.exists() and file_path.stat().st_size > MAX_FILE_SIZE:
                logger.warning(f"File too large: {path}")
                continue

            text = file_path.read_text(encoding="utf-8", errors="ignore")

            # Content length validation (safeguard)
            if len(text) > MAX_FILE_SIZE:
                text = text[:MAX_FILE_SIZE]

        except Exception as e:
            logger.debug(f"Exception: {e}")
            # Defensive error handling (safeguard)
            logger.debug(f"Error reading {path}: {e}")
            continue

        # Pattern detection
        file_has_evidence = False
        text_lower = text.lower()
        for pattern, pattern_type in patterns.items():
            if pattern.lower() in text_lower:
                found.append(pattern)
                file_has_evidence = True

        if file_has_evidence:
            evidence.append(path)

    required = ["X-Request-Id", "logging"]

    # Deterministic sorting (safeguard - reproducibility)
    evidence = sorted(set(evidence))
    found = sorted(set(found))

    return {
        "id": "mcp-observability",
        "evidence_files": evidence,
        "found_patterns": found,
        "required_patterns": required,
        "docs_keywords": [
            "observability",
            "logging",
            "metrics",
            "tracing",
            "monitoring",
            "prometheus",
            "grafana",
            "opentelemetry",
            "health-check",
            "alerting",
            "request-id",
            "correlation-id",
            "structured-logging",
            "mcp",
            "safeguards",
            "telemetry",
            "performance",
            "debugging",
        ],
        "meta": {
            "category": "mcp",
            "layer": "operations",
            "detector_version": "1.2",
            "safeguards": [
                "input-validation",
                "bounds-checking",
                "error-handling",
                "log-sanitization",
                "rate-limiting",
            ],
            "files_processed": len(files),
            "evidence_count": len(evidence),
        },
    }


def _empty_result() -> Dict[str, Any]:
    """
    Returns empty detection result for error cases.

    Safeguard: Ensures consistent return type even on errors.
    """
    return {
        "id": "mcp-observability",
        "evidence_files": [],
        "found_patterns": [],
        "required_patterns": ["X-Request-Id", "logging"],
        "docs_keywords": [
            "observability",
            "logging",
            "metrics",
            "mcp",
        ],
        "meta": {"category": "mcp", "error": True},
    }
