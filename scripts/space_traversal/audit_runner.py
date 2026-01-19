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
import hashlib
import importlib.util
import json
import logging
import os
import sys
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from jinja2 import Environment, FileSystemLoader

from scripts.space_traversal import capability_scoring
from scripts.space_traversal.coverage_ingest import discover_and_parse_coverage
from scripts.space_traversal.dup_similarity import duplication_ratio_token_similarity
from scripts.space_traversal.trend_aggregator import aggregate_trends, generate_trend_report

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


def _merge_list(target: dict, key: str, values: Iterable[str]) -> None:
    existing = set(target.get(key, []) or [])
    existing.update(values)
    target[key] = sorted(existing)


def _blank_capability(cap_id: str) -> dict[str, Any]:
    return {
        "id": cap_id,
        "evidence_files": [],
        "found_patterns": [],
        "required_patterns": [],
        "docs_keywords": [],
        "meta": {"override_only": True},
    }


def apply_overrides(capabilities: list[dict[str, Any]], cfg: dict[str, Any]) -> list[dict[str, Any]]:
    overrides = cfg.get("capability_map", {}).get("overrides", {})
    if not overrides:
        return capabilities

    cap_map: dict[str, dict[str, Any]] = {cap["id"]: deepcopy(cap) for cap in capabilities}
    consumed: set[str] = set()

    for canonical, aliases in overrides.items():
        merged = deepcopy(cap_map.get(canonical, _blank_capability(canonical)))
        for alias in aliases:
            alias_cap = cap_map.get(alias)
            if not alias_cap:
                continue
            _merge_list(merged, "evidence_files", alias_cap.get("evidence_files", []))
            _merge_list(merged, "found_patterns", alias_cap.get("found_patterns", []))
            _merge_list(merged, "required_patterns", alias_cap.get("required_patterns", []))
            _merge_list(merged, "docs_keywords", alias_cap.get("docs_keywords", []))
            if alias_cap.get("meta"):
                merged.setdefault("meta", {}).update(alias_cap["meta"])
            consumed.add(alias)

        cap_map[canonical] = merged

    final_caps = [cap for cap_id, cap in cap_map.items() if cap_id not in consumed]
    return sorted(final_caps, key=lambda cap: cap.get("id", ""))


def validate_detector_output(detector: dict[str, Any], detector_name: str) -> bool:
    required_keys = {"id", "evidence_files", "found_patterns", "required_patterns"}
    if not required_keys.issubset(detector):
        logger.warning("Detector %s missing required keys", detector_name)
        return False

    if not isinstance(detector.get("evidence_files"), list):
        return False
    if not isinstance(detector.get("found_patterns"), list):
        return False
    if not isinstance(detector.get("required_patterns"), list):
        return False

    return True


def stage_s3_capabilities(cfg: dict[str, Any], facets: dict[str, Any]) -> list[dict[str, Any]]:
    artifacts_dir = Path(cfg.get("output", {}).get("artifacts_dir", "audit_artifacts"))
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    facet_map = facets.get("facets", {}) if isinstance(facets, dict) else {}
    capabilities = []
    for cap_id, files in sorted(facet_map.items()):
        capabilities.append(
            {
                "id": cap_id,
                "evidence_files": sorted(set(files)),
                "found_patterns": [cap_id],
                "required_patterns": [cap_id],
                "docs_keywords": [],
                "meta": {"source": "facets"},
            }
        )

    overrides = cfg.get("capability_map", {}).get("overrides", {})
    cap_ids = {cap["id"] for cap in capabilities}
    missing_aliases = [
        alias
        for aliases in overrides.values()
        for alias in aliases
        if alias not in cap_ids
    ]

    if missing_aliases and cfg.get("options", {}).get("fail_on_missing_detector"):
        logger.error("Missing detectors for overrides: %s", ", ".join(sorted(missing_aliases)))
        raise SystemExit(EXIT_MISSING_DETECTOR)

    capabilities = apply_overrides(capabilities, cfg)
    (artifacts_dir / "capabilities_raw.json").write_text(
        json.dumps({"capabilities": capabilities}, indent=2), encoding="utf-8"
    )
    return capabilities


def duplication_ratio(
    evidence_files: list[str],
    file_cache: Optional[dict[str, str]] = None,
    cfg: Optional[dict[str, Any]] = None,
) -> float:
    files = [f for f in evidence_files if f]
    if len(files) <= 1:
        return 0.0

    dup_cfg = (cfg or {}).get("scoring", {}).get("dup", {})
    heuristic = dup_cfg.get("heuristic", "simple")

    if heuristic == "token_similarity" and file_cache is not None:
        try:
            return duplication_ratio_token_similarity(
                files,
                file_cache,
                threshold=float(dup_cfg.get("threshold", 0.7)),
                max_pairwise=int(dup_cfg.get("max_pairwise", 1000)),
                max_tokens_per_file=int(dup_cfg.get("max_tokens_per_file", 1000)),
            )
        except Exception as e:
            logger.warning("Token similarity duplication failed, falling back: %s", e)

    stems = [Path(path).stem.lower() for path in files]
    counts: dict[str, int] = {}
    for stem in stems:
        counts[stem] = counts.get(stem, 0) + 1
    duplicates = sum(max(count - 1, 0) for count in counts.values())
    evidence_count = max(len(stems), 1)
    ratio = duplicates / evidence_count
    return max(0.0, min(1.0, ratio))


def stage_s4_scoring(cfg: dict[str, Any], capabilities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    artifacts_dir = Path(cfg.get("output", {}).get("artifacts_dir", "audit_artifacts"))
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    weights = cfg.get("weights", {})
    thresholds = cfg.get("scoring", {}).get("thresholds", {})

    coverage_map = discover_and_parse_coverage(cfg, artifacts_dir) or {}

    scored_caps = []
    for cap in capabilities:
        required = cap.get("required_patterns", []) or []
        found = cap.get("found_patterns", []) or []
        missing_patterns = sorted(set(required) - set(found))

        functionality = len(found) / max(1, len(required)) if required else 0.0
        consistency = max(0.0, 1.0 - duplication_ratio(cap.get("evidence_files", []), None, cfg))
        base_tests = 1.0 if any("test" in str(f).lower() for f in cap.get("evidence_files", [])) else 0.0
        coverage_scores = [
            coverage_map.get(path, {}).get("percent", 0.0)
            for path in cap.get("evidence_files", [])
            if path in coverage_map
        ]
        coverage_percent = max(coverage_scores) if coverage_scores else 0.0
        tests_component = max(base_tests, coverage_percent)
        safeguards = 0.0
        documentation = 1.0 if cap.get("docs_keywords") else 0.0

        components = {
            "functionality": round(functionality, 6),
            "consistency": round(consistency, 6),
            "tests": round(tests_component, 6),
            "safeguards": round(safeguards, 6),
            "documentation": round(documentation, 6),
        }
        score = capability_scoring.score_capability(components, weights) if weights else 0.0

        scored = deepcopy(cap)
        scored["components"] = components
        scored["score"] = round(score, 6)
        scored["missing_patterns"] = missing_patterns
        scored_caps.append(scored)

    scored_payload = {
        "capabilities": scored_caps,
        "thresholds": thresholds,
        "generated": datetime.utcnow().isoformat(),
    }
    (artifacts_dir / "capabilities_scored.json").write_text(
        json.dumps(scored_payload, indent=2), encoding="utf-8"
    )
    return scored_caps


def stage_s5_gaps(cfg: dict[str, Any], scored_caps: list[dict[str, Any]]) -> dict[str, Any]:
    artifacts_dir = Path(cfg.get("output", {}).get("artifacts_dir", "audit_artifacts"))
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    thresholds = cfg.get("scoring", {}).get("thresholds", {})
    low_threshold = float(thresholds.get("low", 0.7))

    low_maturity = [cap for cap in scored_caps if cap.get("score", 0.0) < low_threshold]
    gaps = {
        "low_maturity": low_maturity,
        "missing_detectors": [],
        "summary": {"low_count": len(low_maturity)},
    }

    (artifacts_dir / "gaps.json").write_text(json.dumps(gaps, indent=2), encoding="utf-8")

    component_gaps = []
    for cap in scored_caps:
        components = cap.get("components", {}) or {}
        zero_components = [k for k, v in components.items() if v <= 0]
        required = cap.get("required_patterns", []) or []
        found = cap.get("found_patterns", []) or []
        missing_patterns = sorted(set(required) - set(found))
        component_gaps.append(
            {
                "id": cap.get("id"),
                "zero_components": zero_components,
                "missing_patterns": missing_patterns,
            }
        )

    component_gaps_payload = {
        "component_gaps": component_gaps,
        "total_capabilities": len(scored_caps),
    }
    (artifacts_dir / "component_gaps.json").write_text(
        json.dumps(component_gaps_payload, indent=2), encoding="utf-8"
    )

    return gaps


def _resolve_matrix_template(cfg: dict[str, Any]) -> Path:
    output_cfg = cfg.get("output", {})
    template_path = output_cfg.get("matrix_template") or cfg.get("matrix_template")
    if template_path:
        return Path(template_path)
    return ROOT / "templates" / "audit" / "capability_matrix.md.j2"


def render_template(cfg: dict[str, Any], context: dict[str, Any]) -> tuple[Path, Path]:
    output_cfg = cfg.get("output", {})
    reports_dir = Path(output_cfg.get("reports_dir", "reports"))
    reports_dir.mkdir(parents=True, exist_ok=True)

    template_path = _resolve_matrix_template(cfg)
    env = Environment(loader=FileSystemLoader(template_path.parent))
    template = env.get_template(template_path.name)

    rendered = template.render(**context)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    md_path = reports_dir / f"capability_matrix_{timestamp}.md"
    md_path.write_text(rendered, encoding="utf-8")

    metrics_schema_version = cfg.get("metrics_schema_version", "2.0.0")
    json_payload = {**context, "metrics_schema_version": metrics_schema_version}
    json_path = md_path.with_suffix(".json")
    json_path.write_text(json.dumps(json_payload, indent=2), encoding="utf-8")

    return md_path, json_path


def stage_s6_render(
    cfg: dict[str, Any], scored_caps: list[dict[str, Any]], gaps: dict[str, Any]
) -> Path:
    thresholds = cfg.get("scoring", {}).get("thresholds", {})
    context = {
        "timestamp": datetime.utcnow().isoformat(),
        "capabilities": scored_caps,
        "gaps": gaps,
        "weights": cfg.get("weights", {}),
        "thresholds": thresholds,
    }
    md_path, _ = render_template(cfg, context)
    return md_path


def _hash_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def stage_s7_manifest(cfg: dict[str, Any]) -> dict[str, Any]:
    artifacts_dir = Path(cfg.get("output", {}).get("artifacts_dir", "audit_artifacts"))
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    artifacts = []
    for path in sorted(artifacts_dir.iterdir(), key=lambda p: p.name):
        if not path.is_file():
            continue
        artifacts.append(
            {
                "name": path.name,
                "path": str(path.relative_to(artifacts_dir)),
                "sha256": _hash_file(path),
            }
        )

    manifest = {
        "timestamp": datetime.utcnow().isoformat(),
        "artifacts": artifacts,
        "metrics_schema_version": cfg.get("metrics_schema_version", "2.0.0"),
    }

    coverage_path = artifacts_dir / "coverage_map.json"
    if coverage_path.exists():
        coverage_map = json.loads(coverage_path.read_text(encoding="utf-8"))
        percents = [entry.get("percent", 0.0) for entry in coverage_map.values()]
        if percents:
            manifest["coverage_stats"] = {
                "total_files": len(percents),
                "min_percent": min(percents),
                "max_percent": max(percents),
                "avg_percent": sum(percents) / len(percents),
            }
        else:
            manifest["coverage_stats"] = {
                "total_files": 0,
                "min_percent": 0.0,
                "max_percent": 0.0,
                "avg_percent": 0.0,
            }

    out_path = ROOT / "audit_run_manifest.json"
    out_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def command_validate(cfg: dict[str, Any]) -> None:
    artifacts_dir = Path(cfg.get("output", {}).get("artifacts_dir", "audit_artifacts"))
    scored_path = artifacts_dir / "capabilities_scored.json"
    if not scored_path.exists():
        raise SystemExit(EXIT_MISSING_ARTIFACTS)

    scored_data = json.loads(scored_path.read_text(encoding="utf-8"))
    capabilities = scored_data.get("capabilities", [])

    thresholds = cfg.get("scoring", {}).get("thresholds", {})
    low_threshold = float(thresholds.get("low", 0.7))

    low_maturity = [cap for cap in capabilities if cap.get("score", 0.0) < low_threshold]

    gaps_path = artifacts_dir / "gaps.json"
    missing_detectors = []
    if gaps_path.exists():
        gaps = json.loads(gaps_path.read_text(encoding="utf-8"))
        missing_detectors = gaps.get("missing_detectors", [])
        if gaps.get("low_maturity"):
            low_maturity = gaps["low_maturity"]

    options = cfg.get("options", {})
    if options.get("fail_on_missing_detector") and missing_detectors:
        raise SystemExit(EXIT_MISSING_DETECTOR)

    if options.get("fail_on_low_maturity", False) and low_maturity:
        raise SystemExit(EXIT_LOW_MATURITY)


def command_explain(args: argparse.Namespace, cfg: dict[str, Any]) -> None:
    artifacts_dir = Path(cfg.get("output", {}).get("artifacts_dir", "audit_artifacts"))
    scored_path = artifacts_dir / "capabilities_scored.json"
    scored_data = json.loads(scored_path.read_text(encoding="utf-8"))
    capabilities = scored_data.get("capabilities", [])

    target = args.capability
    cap = next((c for c in capabilities if c.get("id") == target), None)
    if not cap:
        print(f"Capability {target} not found")
        return

    explanation = capability_scoring.explain_score(cap, cfg.get("weights", {}))
    print(f"Explain: {target}")
    for name, detail in explanation["partials"].items():
        print(
            f"- {name}: value={detail['component_value']:.3f} "
            f"weight={detail['weight']:.3f} contribution={detail['contribution']:.3f}"
        )
    print(f"Total score: {explanation['score']:.3f}")


def run_stage(cfg: dict[str, Any], stage: str) -> None:
    if stage.upper() == "TRENDS":
        artifacts_dir = Path(cfg.get("output", {}).get("artifacts_dir", "audit_artifacts"))
        reports_dir = Path(cfg.get("output", {}).get("reports_dir", "reports"))
        trend_data = aggregate_trends(
            artifacts_dir=artifacts_dir,
            reports_dir=reports_dir,
            lookback_days=cfg.get("trends", {}).get("lookback_days"),
        )
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_path = artifacts_dir / "trends" / f"trend_report_{timestamp}.md"
        generate_trend_report(trend_data, output_path)
        return
    raise ValueError(f"Unknown stage: {stage}")


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
