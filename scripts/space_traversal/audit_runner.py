#!/usr/bin/env python3
"""
Audit Runner

Purpose:
    Runs audit_runner

Usage:
    python scripts/space_traversal/audit_runner.py [options]

    Examples:
    $ python scripts/space_traversal/audit_runner.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""

from __future__ import annotations

"""
Audit Runner - Orchestrates security audits across the codebase
"""

import argparse
import importlib.util
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]

EXIT_MISSING_ARTIFACTS = 2
EXIT_SCORE_REGRESSION = 3
EXIT_LOW_MATURITY = 4
EXIT_MISSING_DETECTOR = 5

_audit_spec = importlib.util.find_spec("scripts.space_traversal.security_audit")
_deps_spec = importlib.util.find_spec("scripts.space_traversal.dependency_scanner")
_quality_spec = importlib.util.find_spec("scripts.space_traversal.code_quality_checker")
_vuln_spec = importlib.util.find_spec("scripts.space_traversal.vulnerability_db")

if _audit_spec:
    from .security_audit import SecurityAuditor
else:
    SecurityAuditor = None

if _deps_spec:
    from .dependency_scanner import DependencyScanner
else:
    DependencyScanner = None

if _quality_spec:
    from .code_quality_checker import CodeQualityChecker
else:
    CodeQualityChecker = None

if _vuln_spec:
    from .vulnerability_db import VulnerabilityDatabase
else:
    VulnerabilityDatabase = None

if importlib.util.find_spec("yaml"):
    import yaml
else:
    yaml = None


class AuditRunner:
    """Main orchestrator for security audits"""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the audit runner

        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.auditor = SecurityAuditor(self.config) if SecurityAuditor else None
        self.dep_scanner = DependencyScanner(self.config) if DependencyScanner else None
        self.quality_checker = CodeQualityChecker(self.config) if CodeQualityChecker else None
        self.vuln_db = VulnerabilityDatabase(self.config) if VulnerabilityDatabase else None
        
    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        try:
            if config_path and config_path.exists():
                if yaml and config_path.suffix in [".yml", ".yaml"]:
                    with open(config_path, encoding="utf-8") as f:
                        return yaml.safe_load(f)
                with open(config_path, encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error("Failed to load config from %s: %s", config_path, e)

        # Return default configuration
        return {
            "scan_paths": ["src", "scripts"],
            "exclude_paths": [".git", "__pycache__", "venv"],
            "severity_threshold": "medium",
            "output_format": "json",
        }

    def run_full_audit(self, target_path: Path) -> Dict[str, Any]:
        """
        Run complete security audit suite

        Args:
            target_path: Root path to audit

        Returns:
            Dictionary containing audit results
        """
        logger.info("Starting full audit of %s", target_path)
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "target": str(target_path),
            "audits": {},
        }

        if self.auditor:
            try:
                logger.info("Running security audit...")
                results["audits"]["security"] = self.auditor.scan(target_path)
            except Exception as e:
                logger.error("Security audit failed: %s", e)
                results["audits"]["security"] = {"error": str(e)}

        if self.dep_scanner:
            try:
                logger.info("Scanning dependencies...")
                results["audits"]["dependencies"] = self.dep_scanner.scan(target_path)
            except Exception as e:
                logger.error("Dependency scan failed: %s", e)
                results["audits"]["dependencies"] = {"error": str(e)}

        if self.quality_checker:
            try:
                logger.info("Checking code quality...")
                results["audits"]["quality"] = self.quality_checker.check(target_path)
            except Exception as e:
                logger.error("Quality check failed: %s", e)
                results["audits"]["quality"] = {"error": str(e)}

        if self.vuln_db:
            try:
                logger.info("Checking vulnerability database...")
                results["audits"]["vulnerabilities"] = self.vuln_db.check(target_path)
            except Exception as e:
                logger.error("Vulnerability check failed: %s", e)
                results["audits"]["vulnerabilities"] = {"error": str(e)}

        results["summary"] = self._generate_summary(results["audits"])

        logger.info("Audit complete")
        return results

    def _generate_summary(self, audits: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics from audit results"""
        summary = {
            "total_issues": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        }

        try:
            for audit_results in audits.values():
                if isinstance(audit_results, dict) and "issues" in audit_results:
                    for issue in audit_results["issues"]:
                        summary["total_issues"] += 1
                        severity = issue.get("severity", "info").lower()
                        if severity in summary:
                            summary[severity] += 1
        except Exception as e:
            logger.error("Failed to generate summary: %s", e)

        return summary

    def save_results(self, results: Dict[str, Any], output_path: Path) -> None:
        """Save audit results to file"""
        try:
            output_format = self.config.get("output_format", "json")

            if output_format == "yaml" and yaml:
                with open(output_path, "w", encoding="utf-8") as f:
                    yaml.dump(results, f, default_flow_style=False)
            else:
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2)

            logger.info("Results saved to %s", output_path)
        except Exception as e:
            logger.error("Failed to save results: %s", e)
            raise


# ---------------------------------------------------------------------------
# Module-level utility functions for test integration
# ---------------------------------------------------------------------------

def duplication_ratio(evidence_files, file_cache=None, cfg=None):
    """
    Calculate duplication ratio using configured heuristic.
    
    Args:
        evidence_files: List of file paths to analyze
        file_cache: Optional dict mapping file paths to contents
        cfg: Optional configuration dict with scoring.dup settings
    
    Returns:
        Float between 0.0 and 1.0 representing duplication ratio
    """
    if cfg is None:
        cfg = {}
    
    scoring_cfg = cfg.get("scoring", {})
    dup_cfg = scoring_cfg.get("dup", {})
    heuristic = dup_cfg.get("heuristic", "simple")
    
    try:
        if heuristic == "token_similarity" and file_cache:
            # Token similarity heuristic
            threshold = dup_cfg.get("threshold", 0.7)
            max_pairwise = dup_cfg.get("max_pairwise", 1000)
            max_tokens_per_file = dup_cfg.get("max_tokens_per_file", 1000)
            
            # Import token similarity function
            try:
                from scripts.space_traversal.dup_similarity import duplication_ratio_token_similarity
                return duplication_ratio_token_similarity(
                    evidence_files,
                    file_cache,
                    threshold=threshold,
                    max_pairwise=max_pairwise,
                    max_tokens_per_file=max_tokens_per_file
                )
            except (ImportError, Exception) as e:
                logger.warning(f"Token similarity failed, falling back to simple: {e}")
                # Fall through to simple heuristic
        
        # Simple stem-based duplication (default/fallback)
        from pathlib import Path
        stems = [Path(f).stem for f in evidence_files]
        if not stems:
            return 0.0
        duplicates = len(stems) - len(set(stems))
        ratio = duplicates / len(stems) if stems else 0.0
        return max(0.0, min(1.0, ratio))
        
    except Exception as e:
        logger.error(f"Duplication ratio calculation failed: {e}")
        return 0.0


def stage_s4_scoring(cfg, raw_caps):
    """
    Score capabilities with optional coverage integration (Stage S4).
    
    Args:
        cfg: Configuration dict with weights, scoring, and output settings
        raw_caps: List of capability dicts with evidence_files, patterns, etc.
    
    Returns:
        List of scored capability dicts with added score components
    """
    from pathlib import Path
    
    artifacts_dir = Path(cfg.get("output", {}).get("artifacts_dir", "audit_artifacts"))
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    weights = cfg.get("weights", {
        "functionality": 0.25,
        "consistency": 0.20,
        "tests": 0.25,
        "safeguards": 0.15,
        "documentation": 0.15,
    })
    
    scoring_cfg = cfg.get("scoring", {})
    thresholds = scoring_cfg.get("thresholds", {"low": 0.70, "medium": 0.85})
    
    # Check for coverage integration
    coverage_map = {}
    coverage_cfg = scoring_cfg.get("coverage", {})
    if coverage_cfg.get("enabled", False):
        try:
            # Import and run coverage ingestion
            from scripts.space_traversal.coverage_ingest import discover_and_parse_coverage
            coverage_map = discover_and_parse_coverage(cfg, artifacts_dir) or {}
            logger.info(f"Coverage integration enabled: {len(coverage_map)} files mapped")
        except (ImportError, Exception) as e:
            logger.warning(f"Coverage integration failed: {e}")
    
    # Build file cache for duplication analysis
    file_cache = {}
    for cap in raw_caps:
        evidence = cap.get("evidence_files", [])
        for filepath in evidence:
            if filepath not in file_cache:
                try:
                    full_path = ROOT / filepath
                    if full_path.exists():
                        file_cache[filepath] = full_path.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    file_cache[filepath] = ""
    
    # Score each capability
    scored_caps = []
    for cap in raw_caps:
        required = cap.get("required_patterns", []) or []
        found = cap.get("found_patterns", []) or []
        evidence_files = cap.get("evidence_files", []) or []
        docs_keywords = cap.get("docs_keywords", []) or []
        
        # Functionality: pattern match ratio
        functionality = len(found) / max(1, len(required)) if required else 0.0
        
        # Consistency: inverse of duplication
        consistency = 1.0 - duplication_ratio(evidence_files, file_cache, cfg)
        
        # Tests: coverage-aware scoring
        tests_score = 0.0
        if evidence_files:
            covered_files = sum(1 for f in evidence_files if coverage_map.get(f, {}).get("percent", 0) > 0)
            tests_score = covered_files / len(evidence_files)
        
        # Safeguards: pattern-based heuristic
        safeguards = min(1.0, len(found) * 0.1)
        
        # Documentation: keyword presence
        documentation = min(1.0, len(docs_keywords) * 0.2)
        
        # Compute weighted score
        components = {
            "functionality": functionality,
            "consistency": consistency,
            "tests": tests_score,
            "safeguards": safeguards,
            "documentation": documentation,
        }
        
        score = sum(components[k] * weights.get(k, 0.0) for k in components)
        score = max(0.0, min(1.0, score))
        
        # Determine maturity level
        if score >= thresholds.get("medium", 0.85):
            maturity = "high"
        elif score >= thresholds.get("low", 0.70):
            maturity = "medium"
        else:
            maturity = "low"
        
        scored_cap = {
            **cap,
            "score": score,
            "maturity": maturity,
            "components": components,
            "missing_patterns": sorted(set(required) - set(found)),
        }
        scored_caps.append(scored_cap)
    
    return scored_caps


def main() -> None:
    """Main entry point"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    parser = argparse.ArgumentParser(description="Run security audits")
    parser.add_argument("target", type=Path, nargs="?", help="Target path to audit")
    parser.add_argument("--config", type=Path, help="Configuration file")
    parser.add_argument("--output", type=Path, help="Output file path")

    args = parser.parse_args()

    if args.target is None:
        print("Target path is required", file=sys.stderr)
        sys.exit(2)

    try:
        runner = AuditRunner(args.config)
        results = runner.run_full_audit(args.target)

        if args.output:
            runner.save_results(results, args.output)
        else:
            print(json.dumps(results, indent=2))

    except Exception as e:
        logger.error("Audit failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
