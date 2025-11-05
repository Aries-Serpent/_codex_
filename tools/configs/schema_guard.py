#!/usr/bin/env python3
"""Offline config schema guard for Codex (OmegaConf/Pydantic).

This tool provides best-effort validation of Hydra/OmegaConf configurations
to catch common shape and type errors early without requiring network access.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _validate(config: dict[str, Any]) -> list[dict[str, str]]:
    """Validate config structure and types.
    
    Parameters
    ----------
    config : dict
        Configuration dictionary to validate
        
    Returns
    -------
    list[dict[str, str]]
        List of validation issues (empty if valid)
    """
    issues = []
    
    # Check root is a mapping
    if not isinstance(config, dict):
        issues.append({
            "path": "root",
            "issue": f"Expected dict, got {type(config).__name__}"
        })
        return issues
    
    # Check training.seed if present
    if "training" in config:
        training = config["training"]
        if isinstance(training, dict) and "seed" in training:
            seed = training["seed"]
            if seed is not None and not isinstance(seed, int):
                issues.append({
                    "path": "training.seed",
                    "issue": f"Expected int or null, got {type(seed).__name__}"
                })
    
    # Check evaluation.metrics if present
    if "evaluation" in config:
        evaluation = config["evaluation"]
        if isinstance(evaluation, dict) and "metrics" in evaluation:
            metrics = evaluation["metrics"]
            if not isinstance(metrics, list):
                issues.append({
                    "path": "evaluation.metrics",
                    "issue": f"Expected list, got {type(metrics).__name__}"
                })
    
    return issues


def validate_config_file(path: Path) -> dict[str, Any]:
    """Validate a config file.
    
    Parameters
    ----------
    path : Path
        Path to config file (YAML or JSON)
        
    Returns
    -------
    dict
        Validation report with 'valid', 'issues', and 'path' fields
    """
    report: dict[str, Any] = {
        "path": str(path),
        "valid": False,
        "issues": []
    }
    
    try:
        # Try OmegaConf first
        try:
            from omegaconf import OmegaConf
            
            cfg = OmegaConf.load(path)
            config_dict = OmegaConf.to_container(cfg, resolve=True)
        except ImportError:
            # Fallback to YAML/JSON
            import yaml
            
            with open(path, 'r') as f:
                if path.suffix == '.json':
                    import json as json_module
                    config_dict = json_module.load(f)
                else:
                    config_dict = yaml.safe_load(f)
        
        # Validate structure
        issues = _validate(config_dict)
        
        report["valid"] = len(issues) == 0
        report["issues"] = issues
        
    except FileNotFoundError:
        report["issues"].append({
            "path": "root",
            "issue": f"File not found: {path}"
        })
    except Exception as e:
        report["issues"].append({
            "path": "root",
            "issue": f"Failed to load config: {e}"
        })
    
    return report


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate Codex config files (offline)"
    )
    parser.add_argument(
        "--path",
        type=Path,
        required=True,
        help="Path to config file (YAML or JSON)"
    )
    
    args = parser.parse_args()
    
    report = validate_config_file(args.path)
    
    print(json.dumps(report, indent=2))
    
    # Always exit 0 (non-blocking)
    return 0


if __name__ == "__main__":
    sys.exit(main())
