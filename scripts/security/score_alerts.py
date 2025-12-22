"""
Risk scoring system for Semgrep alerts.

Risk Score = severity_weight × criticality_weight × exploitability_weight

Author: mbaetiong
Generated: 2025-12-17

Safeguards:
- Input validation on file paths and rule IDs
- Bounds checking on score values
- Defensive error handling
"""

from __future__ import annotations

import csv
import fnmatch
import json
import logging
from pathlib import Path
from typing import Any

# Configure logging
logger = logging.getLogger(__name__)

# Severity weights
SEVERITY_WEIGHTS: dict[str, float] = {
    "critical": 4.0,
    "high": 3.0,
    "medium": 2.0,
    "low": 1.0,
    "warning": 0.5,
    "note": 0.5,
    "unknown": 1.0,
}

# Priority bucket thresholds
PRIORITY_THRESHOLDS: dict[str, float] = {
    "P0": 9.0,   # Critical: 9-36
    "P1": 6.0,   # High: 6-8.9
    "P2": 3.0,   # Medium: 3-5.9
    "P3": 0.0,   # Low: 0-2.9
}

# Safeguards: Bounds
MAX_SCORE = 100.0
MIN_SCORE = 0.0


def load_criticality_map(path: Path) -> dict[str, Any]:
    """Load the criticality map from YAML."""
    try:
        import yaml
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except ImportError as e:
       logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        logger.warning("PyYAML not installed, using default criticality map")
        return {
            "critical_paths": ["src/agents/**", "src/config/**"],
            "high_paths": ["src/**"],
            "medium_paths": ["scripts/**"],
            "low_paths": ["tests/**", "docs/**"],
            "rule_categories": {
                "critical": ["injection", "secrets"],
                "high": ["cryptography", "authorization"],
                "medium": ["xss", "logging"],
                "low": ["code-quality", "best-practice"],
            },
        }
    except Exception as e:
       logger.debug(f"Exception: {e}")
        logger.error(f"Error loading criticality map: {e}")
        return {}


def get_path_weight(file_path: str, criticality_map: dict[str, Any]) -> float:
    """Get the criticality weight for a file path."""
    # Input validation (safeguard)
    if not file_path or not isinstance(file_path, str):
        return 1.0
    
    path_weights = [
        ("critical_paths", 3.0),
        ("high_paths", 2.0),
        ("medium_paths", 1.5),
        ("low_paths", 1.0),
    ]
    
    for category, weight in path_weights:
        patterns = criticality_map.get(category, [])
        for pattern in patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return weight
    
    return 1.0  # Default weight


def get_rule_weight(rule_id: str, criticality_map: dict[str, Any]) -> float:
    """Get the exploitability weight for a rule."""
    # Input validation (safeguard)
    if not rule_id or not isinstance(rule_id, str):
        return 1.0
    
    rule_categories = criticality_map.get("rule_categories", {})
    
    category_weights = {
        "critical": 3.0,
        "high": 2.0,
        "medium": 1.5,
        "low": 1.0,
    }
    
    rule_lower = rule_id.lower()
    
    for category, keywords in rule_categories.items():
        if not isinstance(keywords, list):
            continue
        for keyword in keywords:
            if keyword in rule_lower:
                return category_weights.get(category, 1.0)
    
    return 1.0  # Default weight


def calculate_risk_score(
    severity: str,
    file_path: str,
    rule_id: str,
    criticality_map: dict[str, Any],
) -> float:
    """Calculate the risk score for an alert."""
    severity_weight = SEVERITY_WEIGHTS.get(severity.lower(), 1.0)
    path_weight = get_path_weight(file_path, criticality_map)
    rule_weight = get_rule_weight(rule_id, criticality_map)
    
    score = severity_weight * path_weight * rule_weight
    
    # Bounds check (safeguard)
    return max(MIN_SCORE, min(MAX_SCORE, score))


def get_priority_bucket(risk_score: float) -> str:
    """Determine the priority bucket based on risk score."""
    for bucket, threshold in PRIORITY_THRESHOLDS.items():
        if risk_score >= threshold:
            return bucket
    return "P3"


def score_all_alerts(
    alerts_file: Path, 
    criticality_file: Path, 
    output_file: Path
) -> None:
    """Score all alerts and output prioritized list."""
    # Load data
    try:
        with open(alerts_file) as f:
            alerts = json.load(f)
    except FileNotFoundError as e:
       logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        logger.error(f"Alerts file not found: {alerts_file}")
        return
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in alerts file: {e}")
        return
    
    criticality_map = load_criticality_map(criticality_file)
    
    # Score each alert
    scored_alerts = []
    
    for alert in alerts:
        rule = alert.get("rule", {})
        rule_id = rule.get("id", "unknown")
        severity = rule.get("severity", "unknown")
        
        location = alert.get("most_recent_instance", {}).get("location", {})
        file_path = location.get("path", "unknown")
        line = location.get("start_line", 0)
        
        risk_score = calculate_risk_score(
            severity=severity,
            file_path=file_path,
            rule_id=rule_id,
            criticality_map=criticality_map,
        )
        
        priority = get_priority_bucket(risk_score)
        
        scored_alerts.append({
            "alert_id": alert.get("number", 0),
            "rule_id": rule_id,
            "rule_name": rule.get("name", ""),
            "severity": severity,
            "file": file_path,
            "line": line,
            "risk_score": round(risk_score, 2),
            "priority_bucket": priority,
            "html_url": alert.get("html_url", ""),
        })
    
    # Sort by risk score descending
    scored_alerts.sort(key=lambda x: x["risk_score"], reverse=True)
    
    # Write output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    if scored_alerts:
        with open(output_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=scored_alerts[0].keys())
            writer.writeheader()
            writer.writerows(scored_alerts)
    
    logger.info(f"✅ Scored {len(scored_alerts)} alerts")
    logger.info(f"💾 Saved to {output_file}")
    
    # Print summary
    priority_counts: dict[str, int] = {}
    for alert in scored_alerts:
        bucket = alert["priority_bucket"]
        priority_counts[bucket] = priority_counts.get(bucket, 0) + 1
    
    logger.info("\n📊 Priority Distribution:")
    for bucket in ["P0", "P1", "P2", "P3"]:
        count = priority_counts.get(bucket, 0)
        logger.info(f"  {bucket}: {count} alerts")


def main() -> None:
    """Main entry point."""
    logging.basicConfig(level=logging.INFO)
    
    base_dir = Path(".github/security")
    
    score_all_alerts(
        alerts_file=base_dir / "semgrep-alerts-export.json",
        criticality_file=base_dir / "criticality-map.yaml",
        output_file=base_dir / "prioritized-alerts.csv",
    )


if __name__ == "__main__":
    main()
