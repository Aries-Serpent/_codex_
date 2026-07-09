"""
Intent Inferer - Infer code intent using heuristics and LLM.

Combines deterministic heuristics with LLM-based semantic analysis
to produce a structured intent specification.

Author: mbaetiong
Generated: 2025-12-17

Safeguards:
- Confidence scoring for uncertainty
- Heuristic fallback when LLM unavailable
- Assumption tracking
- Conservative inference mode
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Optional

logger = logging.getLogger(__name__)


@dataclass
class InputSpec:
    """Specification for a code input."""

    name: str
    type: Literal["cli_arg", "stdin", "file", "env_var", "network"]
    required: bool = True


@dataclass
class OutputSpec:
    """Specification for a code output."""

    name: str
    type: Literal["stdout", "stderr", "file", "network", "return_value"]


@dataclass
class IntentSpec:
    """Inferred intent specification for code.

    Represents the inferred purpose, inputs, outputs, and constraints
    of analyzed code. Includes confidence score and tracking of
    assumptions made during inference.

    Attributes:
        snapshot_id: Reference to the analyzed snapshot
        timestamp: When inference was performed
        goal: High-level purpose of the code
        actors: Who/what interacts with this code
        inputs: list of input specifications
        outputs: list of output specifications
        constraints: Behavioral constraints
        side_effects: Potential side effects
        confidence: Confidence score (0.0-1.0)
        inference_method: How intent was inferred
        llm_provenance_ref: Reference to LLM provenance record
        assumptions: Assumptions made during inference
    """

    snapshot_id: str
    timestamp: datetime
    goal: str
    actors: list[str] = field(default_factory=list)
    inputs: list[InputSpec] = field(default_factory=list)
    outputs: list[OutputSpec] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    side_effects: list[str] = field(default_factory=list)
    confidence: float = 0.5
    inference_method: Literal["heuristic", "llm", "hybrid"] = "heuristic"
    llm_provenance_ref: Optional[str] = None
    assumptions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp.isoformat(),
            "goal": self.goal,
            "actors": self.actors,
            "inputs": [
                {"name": i.name, "type": i.type, "required": i.required} for i in self.inputs
            ],
            "outputs": [{"name": o.name, "type": o.type} for o in self.outputs],
            "constraints": self.constraints,
            "side_effects": self.side_effects,
            "confidence": self.confidence,
            "inference_method": self.inference_method,
            "llm_provenance_ref": self.llm_provenance_ref,
            "assumptions": self.assumptions,
        }

    def save(self, path: Path) -> None:
        """Save intent spec to YAML file."""
        try:
            import yaml

            with path.open("w", encoding="utf-8") as f:
                yaml.dump(self.to_dict(), f, default_flow_style=False)
        except ImportError as e:
            type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
            # Fallback to JSON
            with path.open("w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2)


def _detect_cli_tool(imports: list[str], exports: list[str]) -> bool:
    """Detect if code is a CLI tool."""
    cli_indicators = {"argparse", "click", "typer", "fire", "docopt"}
    return bool(cli_indicators & set(imports))


def _detect_gui_app(imports: list[str]) -> bool:
    """Detect if code is a GUI application."""
    gui_indicators = {"tkinter", "PyQt5", "PyQt6", "PySide6", "wx", "kivy"}
    return bool(gui_indicators & set(imports))


def _detect_web_service(imports: list[str]) -> bool:
    """Detect if code is a web service."""
    web_indicators = {"flask", "fastapi", "django", "bottle", "tornado", "aiohttp"}
    return bool(web_indicators & set(imports))


def _detect_networked(imports: list[str]) -> bool:
    """Detect if code makes network calls."""
    network_indicators = {"requests", "httpx", "urllib", "socket", "aiohttp"}
    return bool(network_indicators & set(imports))


def _detect_data_processing(imports: list[str]) -> bool:
    """Detect if code is for data processing."""
    data_indicators = {"pandas", "numpy", "polars", "dask", "csv", "json"}
    return bool(data_indicators & set(imports))


def _infer_heuristic(
    static_report: dict[str, Any],
    source_excerpt: str,
) -> IntentSpec:
    """Infer intent using deterministic heuristics.

    Args:
        static_report: Static analysis report data
        source_excerpt: First portion of main source file

    Returns:
        IntentSpec from heuristic analysis
    """
    now = datetime.now(timezone.utc)
    snapshot_id = static_report.get("snapshot_id", "unknown")

    # Collect all imports across files
    all_imports: list[str] = []
    for file_data in static_report.get("files", []):
        all_imports.extend(file_data.get("imports", []))
    all_imports = list(set(all_imports))

    # Determine code type
    actors = ["user"]
    inputs: list[InputSpec] = []
    outputs: list[OutputSpec] = []
    constraints: list[str] = []
    side_effects: list[str] = []
    assumptions: list[str] = []

    if _detect_cli_tool(all_imports, []):
        goal = "Command-line tool for processing input and producing output"
        actors = ["user", "shell"]
        inputs.append(InputSpec(name="args", type="cli_arg", required=True))
        outputs.append(OutputSpec(name="result", type="stdout"))
        confidence = 0.75
    elif _detect_web_service(all_imports):
        goal = "Web service providing HTTP API endpoints"
        actors = ["http_client", "user"]
        inputs.append(InputSpec(name="request", type="network", required=True))
        outputs.append(OutputSpec(name="response", type="network"))
        side_effects.append("Listens on network port")
        confidence = 0.80
    elif _detect_gui_app(all_imports):
        goal = "Graphical user interface application"
        actors = ["user"]
        inputs.append(InputSpec(name="user_input", type="stdin", required=False))
        outputs.append(OutputSpec(name="display", type="stdout"))
        side_effects.append("Creates GUI window")
        confidence = 0.70
    elif _detect_data_processing(all_imports):
        goal = "Data processing script for transforming datasets"
        actors = ["user", "data_source"]
        inputs.append(InputSpec(name="input_data", type="file", required=True))
        outputs.append(OutputSpec(name="output_data", type="file"))
        confidence = 0.65
    elif _detect_networked(all_imports):
        goal = "Networked application that communicates over HTTP/TCP"
        actors = ["user", "remote_server"]
        inputs.append(InputSpec(name="request_params", type="cli_arg", required=False))
        outputs.append(OutputSpec(name="response", type="stdout"))
        side_effects.append("Makes network requests")
        constraints.append("Requires network access")
        confidence = 0.60
    else:
        goal = "Python script for general-purpose computation"
        assumptions.append("No specific framework detected, assuming general script")
        confidence = 0.40

    # Check for main entry point patterns
    if "if __name__" in source_excerpt:
        constraints.append("Has executable entry point")
        confidence = min(confidence + 0.1, 1.0)

    return IntentSpec(
        snapshot_id=snapshot_id,
        timestamp=now,
        goal=goal,
        actors=actors,
        inputs=inputs,
        outputs=outputs,
        constraints=constraints,
        side_effects=side_effects,
        confidence=confidence,
        inference_method="heuristic",
        assumptions=assumptions,
    )


def infer_intent(
    static_report: dict[str, Any],
    runtime_report: Optional[dict[str, Any]] = None,
    source_excerpt: str = "",
    use_llm: bool = False,
    llm_client: Optional[Any] = None,
    provenance_dir: Optional[Path] = None,
) -> IntentSpec:
    """Infer intent for analyzed code.

    Combines deterministic heuristics with optional LLM-based analysis
    to produce a structured intent specification.

    Args:
        static_report: Static analysis report dictionary
        runtime_report: Optional runtime analysis report
        source_excerpt: First portion of main source file (max 500 lines)
        use_llm: Whether to use LLM for enhanced inference
        llm_client: Optional LLM client instance
        provenance_dir: Directory for storing LLM provenance

    Returns:
        IntentSpec with inferred intent

    Example:
        >>> with open("static-report.json") as f:
        ...     static = json.load(f)
        >>> intent = infer_intent(static, source_excerpt=source[:500])
        >>> logger.info(f"Goal: {intent.goal} (confidence: {intent.confidence})")
    """
    # Start with heuristic inference
    intent = _infer_heuristic(static_report, source_excerpt)

    # Optionally enhance with LLM
    if use_llm and llm_client is not None:
        try:
            # Build context for LLM
            context = {
                "static_summary": static_report.get("summary", {}),
                "imports": [],
                "source_excerpt": source_excerpt[:8000],  # Token budget
            }

            for file_data in static_report.get("files", []):
                context["imports"].extend(file_data.get("imports", []))
            context["imports"] = list(set(context["imports"]))

            # Add runtime observations if available
            if runtime_report:
                context["runtime_observations"] = runtime_report.get("execution_results", [])

            # Call LLM for enhanced inference
            llm_result = llm_client.infer_intent(context)

            if llm_result:
                # Merge LLM insights with heuristic base
                if llm_result.get("goal"):
                    intent.goal = llm_result["goal"]
                if llm_result.get("confidence"):
                    intent.confidence = (intent.confidence + llm_result["confidence"]) / 2
                intent.inference_method = "hybrid"

                # Store provenance
                if provenance_dir and llm_result.get("provenance_ref"):
                    intent.llm_provenance_ref = llm_result["provenance_ref"]

                logger.info("Enhanced intent with LLM: confidence=%.2f", intent.confidence)

        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning("LLM enhancement failed, using heuristic only: %s", e)
            intent.assumptions.append(f"LLM enhancement failed: {e}")

    return intent
