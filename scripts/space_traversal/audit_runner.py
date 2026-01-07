#!/usr/bin/env python3
"""
Audit Runner - Orchestrates security audits across the codebase
"""

import logging
logger = logging.getLogger(__name__)

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib
import json
from datetime import datetime

try:
    from scripts.space_traversal.security_audit import SecurityAuditor
    from scripts.space_traversal.dependency_scanner import DependencyScanner
    from scripts.space_traversal.code_quality_checker import CodeQualityChecker
    from scripts.space_traversal.vulnerability_db import VulnerabilityDatabase
except ImportError as e:
    logger.error(f"Failed to import audit modules: {e}")
    SecurityAuditor = None  # type: ignore[assignment]
    DependencyScanner = None  # type: ignore[assignment]
    CodeQualityChecker = None  # type: ignore[assignment]
    VulnerabilityDatabase = None  # type: ignore[assignment]

try:
    import yaml
except ImportError as e:
    logger.warning(f"YAML support not available: {e}")
    yaml = None

ROOT = Path(__file__).resolve().parents[2]


class AuditRunner:
    """Main orchestrator for security audits"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the audit runner
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.auditor = _ensure_dependency(SecurityAuditor, "SecurityAuditor")(self.config)
        self.dep_scanner = _ensure_dependency(DependencyScanner, "DependencyScanner")(self.config)
        self.quality_checker = _ensure_dependency(CodeQualityChecker, "CodeQualityChecker")(self.config)
        self.vuln_db = _ensure_dependency(VulnerabilityDatabase, "VulnerabilityDatabase")(self.config)
        
    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        try:
            if config_path and config_path.exists():
                if yaml and config_path.suffix in ['.yml', '.yaml']:
                    with open(config_path) as f:
                        return yaml.safe_load(f)
                else:
                    with open(config_path) as f:
                        return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            
        # Return default configuration
        return {
            'scan_paths': ['src', 'scripts'],
            'exclude_paths': ['.git', '__pycache__', 'venv'],
            'severity_threshold': 'medium',
            'output_format': 'json'
        }
    
    def run_full_audit(self, target_path: Path) -> Dict[str, Any]:
        """
        Run complete security audit suite
        
        Args:
            target_path: Root path to audit
            
        Returns:
            Dictionary containing audit results
        """
        logger.info(f"Starting full audit of {target_path}")
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'target': str(target_path),
            'audits': {}
        }
        
        try:
            # Run security audit
            logger.info("Running security audit...")
            results['audits']['security'] = self.auditor.scan(target_path)
        except Exception as e:
            logger.error(f"Security audit failed: {e}")
            results['audits']['security'] = {'error': str(e)}
            
        try:
            # Scan dependencies
            logger.info("Scanning dependencies...")
            results['audits']['dependencies'] = self.dep_scanner.scan(target_path)
        except Exception as e:
            logger.error(f"Dependency scan failed: {e}")
            results['audits']['dependencies'] = {'error': str(e)}
            
        try:
            # Check code quality
            logger.info("Checking code quality...")
            results['audits']['quality'] = self.quality_checker.check(target_path)
        except Exception as e:
            logger.error(f"Quality check failed: {e}")
            results['audits']['quality'] = {'error': str(e)}
            
        try:
            # Check vulnerability database
            logger.info("Checking vulnerability database...")
            results['audits']['vulnerabilities'] = self.vuln_db.check(target_path)
        except Exception as e:
            logger.error(f"Vulnerability check failed: {e}")
            results['audits']['vulnerabilities'] = {'error': str(e)}
            
        # Generate summary
        results['summary'] = self._generate_summary(results['audits'])
        
        logger.info("Audit complete")
        return results
    
    def _generate_summary(self, audits: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics from audit results"""
        summary = {
            'total_issues': 0,
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0
        }
        
        try:
            for audit_type, audit_results in audits.items():
                if isinstance(audit_results, dict) and 'issues' in audit_results:
                    for issue in audit_results['issues']:
                        summary['total_issues'] += 1
                        severity = issue.get('severity', 'info').lower()
                        if severity in summary:
                            summary[severity] += 1
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            
        return summary
    
    def save_results(self, results: Dict[str, Any], output_path: Path):
        """Save audit results to file"""
        try:
            output_format = self.config.get('output_format', 'json')
            
            if output_format == 'yaml' and yaml:
                with open(output_path, 'w') as f:
                    yaml.dump(results, f, default_flow_style=False)
            else:
                with open(output_path, 'w') as f:
                    json.dump(results, f, indent=2)
                    
            logger.info(f"Results saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            raise


def _ensure_dependency(dep: Any, name: str):
    if dep is None:
        raise RuntimeError(f"{name} dependency is unavailable; ensure audit modules are installed.")
    return dep


def _expand_doc_tokens(domain: str, tokens: List[str]) -> List[str]:
    """Expand doc tokens with naive pluralization and known synonyms."""
    expanded = set()
    for token in tokens:
        normalized = token.strip().lower()
        if not normalized:
            continue
        expanded.add(normalized)
        if not normalized.endswith("s"):
            expanded.add(f"{normalized}s")
    domain_key = domain.strip().lower()
    expanded.add(domain_key)

    synonyms = {
        "tokenization": {"sentencepiece", "tokenizer", "tokenizers", "subword"},
        "checkpointing": {"checkpoint", "checkpoints"},
    }
    expanded.update(synonyms.get(domain_key, set()))
    return sorted(expanded)


def _docs_score(domain: str, cache: Dict[str, str], tokens: List[str]) -> float:
    """Score documentation coverage based on token presence."""
    expanded = _expand_doc_tokens(domain, tokens)
    if not cache:
        return 0.0
    hits = 0
    for _, content in cache.items():
        lower = content.lower()
        if any(token in lower for token in expanded):
            hits += 1
    return hits / max(len(cache), 1)


def render_template(
    cfg: Dict[str, Any],
    payload: Dict[str, Any],
    *,
    template_path: Optional[Path] = None,
) -> tuple[Path, Path]:
    """Render capability matrix Markdown and write a JSON companion file."""
    output_cfg = cfg.get("output", {}) if isinstance(cfg, dict) else {}
    artifacts_dir = Path(output_cfg.get("artifacts_dir", ROOT / "audit_artifacts"))
    reports_dir = Path(output_cfg.get("reports_dir", ROOT / "reports"))
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    tpl_rel = output_cfg.get("matrix_template", "templates/audit/capability_matrix.md.j2")
    template_path = template_path or (ROOT / tpl_rel)

    timestamp = payload.get("timestamp") or datetime.utcnow().isoformat()
    context = dict(payload)
    context.setdefault("timestamp", timestamp)
    context.setdefault("metrics_schema_version", cfg.get("metrics_schema_version", "1.0.0"))

    safe_stamp = timestamp.replace(":", "").replace("-", "").replace("T", "_").split(".")[0]
    md_path = reports_dir / f"capability_matrix_{safe_stamp}.md"
    js_path = artifacts_dir / "capability_matrix.json"

    rendered = None
    try:
        from jinja2 import Environment, FileSystemLoader, select_autoescape  # type: ignore

        if template_path.exists():
            env = Environment(
                loader=FileSystemLoader(str(template_path.parent)),
                autoescape=select_autoescape(["html", "xml", "jinja2"]),
                trim_blocks=True,
                lstrip_blocks=True,
            )
            template = env.get_template(template_path.name)
            rendered = template.render(**context)
    except Exception as exc:
        logger.warning(f"Template rendering unavailable: {exc}")

    if rendered is None:
        rendered = f"# Capability Matrix\n\nGenerated: {timestamp}\n"

    md_path.write_text(rendered, encoding="utf-8")
    js_payload = dict(context)
    js_payload["metrics_schema_version"] = context["metrics_schema_version"]
    js_path.write_text(json.dumps(js_payload, indent=2), encoding="utf-8")
    return md_path, js_path


def _load_workflow_config() -> Dict[str, Any]:
    cfg_path = ROOT / ".copilot-space" / "workflow.yaml"
    if cfg_path.exists() and yaml is not None:
        return yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    return {}


def _artifact_dirs(cfg: Dict[str, Any]) -> tuple[Path, Path]:
    output_cfg = cfg.get("output", {}) if isinstance(cfg, dict) else {}
    artifacts_dir = Path(output_cfg.get("artifacts_dir", ROOT / "audit_artifacts"))
    reports_dir = Path(output_cfg.get("reports_dir", ROOT / "reports"))
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    return artifacts_dir, reports_dir


def _load_doc_cache(root: Path) -> Dict[str, str]:
    cache: Dict[str, str] = {}
    for path in (root / "docs").rglob("*.md"):
        try:
            cache[str(path)] = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
    for path in (root / "guides").rglob("*.md"):
        try:
            cache[str(path)] = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
    return cache


def _resolve_depth_limit() -> int:
    if os.environ.get("AUDIT_DEPTH"):
        return int(os.environ["AUDIT_DEPTH"])
    if os.environ.get("AUDIT_DEPTH_DEFAULT"):
        return int(os.environ["AUDIT_DEPTH_DEFAULT"])
    return 4


def _collect_context_files(root: Path, depth_limit: int) -> list[dict[str, Any]]:
    exclude_dirs = {
        ".git",
        "__pycache__",
        "venv",
        ".venv",
        "node_modules",
        "dist",
        "build",
        ".mypy_cache",
        ".pytest_cache",
        "audit_artifacts",
        "reports",
    }
    entries = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if len(rel.parts) > depth_limit:
            continue
        if any(part in exclude_dirs for part in rel.parts):
            continue
        entries.append({"path": rel.as_posix()})
    entries.sort(key=lambda item: item["path"])
    return entries


def _stage_s1(cfg: Dict[str, Any]) -> None:
    artifacts_dir, _ = _artifact_dirs(cfg)
    context_path = artifacts_dir / "context_index.json"
    depth_limit = _resolve_depth_limit()
    files = _collect_context_files(ROOT, depth_limit)
    payload = {
        "version": cfg.get("version", "1.0.0"),
        "timestamp": datetime.utcnow().isoformat(),
        "count": len(files),
        "files": files,
    }
    context_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _capability_seed_data(files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    evidence = [entry["path"] for entry in files[:5]] or ["README.md"]
    payload = {
        "id": "structural-integrity",
        "name": "Structural Integrity",
        "required_patterns": ["structure", "integrity"],
        "found_patterns": ["structure"],
        "docs_tokens": ["integrity", "structure"],
        "evidence_files": evidence,
    }
    return [
        payload,
        {
            "id": "mcp-tools-integration",
            "name": "MCP Tools Integration",
            "required_patterns": ["mcp", "tools"],
            "found_patterns": ["mcp"],
            "docs_tokens": ["mcp", "tools"],
            "evidence_files": evidence,
        },
    ]


def _stage_s3(cfg: Dict[str, Any]) -> None:
    artifacts_dir, _ = _artifact_dirs(cfg)
    context_path = artifacts_dir / "context_index.json"
    if not context_path.exists():
        _stage_s1(cfg)
    context_data = json.loads(context_path.read_text(encoding="utf-8"))
    files = context_data.get("files", [])
    raw_path = artifacts_dir / "capabilities_raw.json"
    payload = {
        "version": cfg.get("version", "1.0.0"),
        "timestamp": datetime.utcnow().isoformat(),
        "capabilities": [
            {
                **cap,
            }
            for cap in _capability_seed_data(files)
        ],
    }
    raw_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _stage_s2(cfg: Dict[str, Any]) -> None:
    artifacts_dir, _ = _artifact_dirs(cfg)
    facets_path = artifacts_dir / "facets.json"
    if not facets_path.exists():
        facets_path.write_text(
            json.dumps(
                {"version": cfg.get("version", "1.0.0"), "timestamp": datetime.utcnow().isoformat(), "facets": []},
                indent=2,
            ),
            encoding="utf-8",
        )


def _apply_component_caps(components: Dict[str, float], cfg: Dict[str, Any]) -> Dict[str, float]:
    scoring_cfg = cfg.get("scoring", {}) if isinstance(cfg, dict) else {}
    caps = scoring_cfg.get("component_caps", {})
    capped = {}
    for key, value in components.items():
        cap = float(caps.get(key, 1.0))
        capped[key] = min(value, cap)
    return capped


def _stage_s4(cfg: Dict[str, Any]) -> None:
    artifacts_dir, _ = _artifact_dirs(cfg)
    raw_path = artifacts_dir / "capabilities_raw.json"
    if not raw_path.exists():
        _stage_s3(cfg)
    data = json.loads(raw_path.read_text(encoding="utf-8"))
    caps = data.get("capabilities", [])
    weights = cfg.get("weights", {}) if isinstance(cfg, dict) else {}
    doc_cache = _load_doc_cache(ROOT)
    scored_caps = []

    for cap in caps:
        required = cap.get("required_patterns") or []
        found = cap.get("found_patterns") or []
        raw_functionality = len(found) / max(len(required), 1)
        functionality = min(raw_functionality, 1.0)
        documentation = _docs_score(cap.get("id", ""), doc_cache, cap.get("docs_tokens", []))
        components = {
            "functionality": functionality,
            "consistency": 0.5,
            "tests": 0.5,
            "safeguards": 0.5,
            "documentation": documentation,
        }
        components = _apply_component_caps(components, cfg)
        cap = dict(cap)
        cap["components"] = components
        try:
            from scripts.space_traversal.capability_scoring import score_capability

            cap["score"] = score_capability(components, weights) if weights else 0.0
        except Exception:
            cap["score"] = 0.0
        scored_caps.append(cap)

    scoring_cfg = cfg.get("scoring", {}) if isinstance(cfg, dict) else {}
    dup_cfg = scoring_cfg.get("dup", {})
    heuristic = dup_cfg.get("heuristic", "simple")
    heuristic_used = "simple"
    if heuristic == "token_similarity":
        try:
            from scripts.space_traversal import dup_similarity  # noqa: F401

            heuristic_used = "token_similarity"
        except Exception:
            heuristic_used = "simple"
    else:
        heuristic_used = heuristic

    normalized_weights = {}
    if weights:
        from scripts.space_traversal.capability_scoring import normalize_weights

        normalized_weights = normalize_weights(weights)

    scored_payload = {
        "version": cfg.get("version", "1.0.0"),
        "timestamp": datetime.utcnow().isoformat(),
        "weights": weights,
        "normalized_weights": normalized_weights,
        "dup_heuristic": heuristic_used,
        "capabilities": scored_caps,
    }
    (artifacts_dir / "capabilities_scored.json").write_text(
        json.dumps(scored_payload, indent=2), encoding="utf-8"
    )


def _stage_s5(cfg: Dict[str, Any]) -> None:
    artifacts_dir, _ = _artifact_dirs(cfg)
    gaps_path = artifacts_dir / "gaps.json"
    scored_path = artifacts_dir / "capabilities_scored.json"
    if not scored_path.exists():
        _stage_s4(cfg)
    scored = json.loads(scored_path.read_text(encoding="utf-8"))
    thresholds = cfg.get("scoring", {}).get("thresholds", {}) if isinstance(cfg, dict) else {}
    low_threshold = float(thresholds.get("low", 0.0)) if thresholds else 0.0
    gaps = [cap for cap in scored.get("capabilities", []) if cap.get("score", 0.0) < low_threshold]
    payload = {
        "version": cfg.get("version", "1.0.0"),
        "timestamp": datetime.utcnow().isoformat(),
        "gaps": gaps,
    }
    gaps_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _stage_s6(cfg: Dict[str, Any]) -> None:
    artifacts_dir, _ = _artifact_dirs(cfg)
    scored_path = artifacts_dir / "capabilities_scored.json"
    if not scored_path.exists():
        _stage_s4(cfg)
    scored = json.loads(scored_path.read_text(encoding="utf-8"))
    gaps_path = artifacts_dir / "gaps.json"
    if not gaps_path.exists():
        _stage_s5(cfg)
    gaps = json.loads(gaps_path.read_text(encoding="utf-8")).get("gaps", [])
    payload = dict(scored)
    payload.setdefault("weights", cfg.get("weights", {}))
    payload["scoring"] = cfg.get("scoring", {})
    payload["gaps"] = gaps
    payload["template_hash"] = _template_hash(cfg)
    render_template(cfg, payload)


def _compute_repo_root_sha(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file():
            rel = path.relative_to(root).as_posix().encode("utf-8")
            digest.update(rel)
    return digest.hexdigest()


def _template_hash(cfg: Dict[str, Any]) -> str:
    tpl_rel = cfg.get("matrix_template", None)
    output_cfg = cfg.get("output", {}) if isinstance(cfg, dict) else {}
    if tpl_rel is None:
        tpl_rel = output_cfg.get("matrix_template", "templates/audit/capability_matrix.md.j2")
    tpl_path = ROOT / tpl_rel
    if not tpl_path.exists():
        return ""
    return hashlib.sha256(tpl_path.read_bytes()).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _coverage_stats(coverage_path: Path) -> dict[str, float]:
    coverage_data = json.loads(coverage_path.read_text(encoding="utf-8"))
    percents = [float(data.get("percent", 0.0)) for data in coverage_data.values()]
    if not percents:
        return {"total_files": 0, "min_percent": 0.0, "max_percent": 0.0, "avg_percent": 0.0}
    return {
        "total_files": len(percents),
        "min_percent": min(percents),
        "max_percent": max(percents),
        "avg_percent": sum(percents) / len(percents),
    }


def _aggregate_warnings(artifacts_dir: Path, depth_limit: int) -> list[str]:
    warnings: list[str] = []
    content_report = artifacts_dir / "content_filter_report.json"
    if content_report.exists():
        payload = json.loads(content_report.read_text(encoding="utf-8"))
        warnings.extend(payload.get("warnings", []))
    bundles_dir = artifacts_dir / "bundles"
    if bundles_dir.exists():
        for pointer in sorted(bundles_dir.glob("*.pointer.json")):
            payload = json.loads(pointer.read_text(encoding="utf-8"))
            warnings.extend(payload.get("warnings", []))
    if depth_limit < 4:
        warnings.append("depth_restriction_active")
    return warnings


def stage_s7_manifest(cfg: Dict[str, Any]) -> Dict[str, Any]:
    from scripts.space_traversal.stable_manifest import normalize_name
    from scripts.space_traversal.capability_scoring import normalize_weights

    artifacts_dir, _ = _artifact_dirs(cfg)
    depth_limit = _resolve_depth_limit()

    entries = []
    for path in sorted(artifacts_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(artifacts_dir).as_posix()
        entries.append({"name": normalize_name(rel), "sha256": _sha256_file(path)})
    entries.sort(key=lambda item: item["name"])

    weights = cfg.get("weights", {})
    normalized_weights = normalize_weights(weights) if weights else {}

    manifest = {
        "version": cfg.get("version", "1.0.0"),
        "metrics_schema_version": cfg.get("metrics_schema_version", "1.0.0"),
        "timestamp": datetime.utcnow().isoformat(),
        "repo_root_sha": _compute_repo_root_sha(ROOT),
        "template_hash": _template_hash(cfg),
        "artifacts": entries,
        "weights": weights,
        "normalized_weights": normalized_weights,
        "warnings": _aggregate_warnings(artifacts_dir, depth_limit),
    }

    coverage_path = artifacts_dir / "coverage_map.json"
    if coverage_path.exists():
        manifest["coverage_stats"] = _coverage_stats(coverage_path)

    (ROOT / "audit_run_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return manifest


def _stage_s7(cfg: Dict[str, Any]) -> None:
    stage_s7_manifest(cfg)


def _run_stage(stage: str, cfg: Dict[str, Any]) -> None:
    stage = stage.upper()
    if stage == "S1":
        _stage_s1(cfg)
    elif stage == "S2":
        _stage_s2(cfg)
    elif stage == "S3":
        _stage_s3(cfg)
    elif stage == "S4":
        _stage_s4(cfg)
    elif stage == "S5":
        _stage_s5(cfg)
    elif stage == "S6":
        _stage_s6(cfg)
    elif stage == "S7":
        _stage_s7(cfg)
    else:
        raise ValueError(f"Unknown stage: {stage}")


def _run_diff(old_path: Path, new_path: Path) -> str:
    old = json.loads(old_path.read_text(encoding="utf-8"))
    new = json.loads(new_path.read_text(encoding="utf-8"))
    old_caps = {c["id"]: c.get("score", 0.0) for c in old.get("capabilities", [])}
    new_caps = {c["id"]: c.get("score", 0.0) for c in new.get("capabilities", [])}
    ids = sorted(set(old_caps) | set(new_caps))
    lines = ["ID,OLD,NEW,DELTA"]
    for cap_id in ids:
        old_score = old_caps.get(cap_id, 0.0)
        new_score = new_caps.get(cap_id, 0.0)
        delta = new_score - old_score
        lines.append(f"{cap_id},{old_score:.4f},{new_score:.4f},{delta:.4f}")
    return "\n".join(lines) + "\n"


def main():
    """Main entry point"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    import argparse
    parser = argparse.ArgumentParser(description="Run security audits")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run full audit suite")
    run_parser.add_argument("target", type=Path, nargs="?", help="Target path to audit")
    run_parser.add_argument("--config", type=Path, help="Configuration file")
    run_parser.add_argument("--output", type=Path, help="Output file path")

    stage_parser = subparsers.add_parser("stage", help="Run a single audit stage (S1..S7)")
    stage_parser.add_argument("stage", type=str, help="Stage identifier (e.g., S1)")

    diff_parser = subparsers.add_parser("diff", help="Diff two scored capability JSON files")
    diff_parser.add_argument("--old", type=Path, required=True)
    diff_parser.add_argument("--new", type=Path, required=True)

    explain_parser = subparsers.add_parser("explain", help="Explain score composition for a capability")
    explain_parser.add_argument("capability_id", type=str, help="Capability id to explain")

    args = parser.parse_args()

    try:
        if args.command == "run":
            if args.target is None:
                cfg = _load_workflow_config()
                if yaml is None:
                    raise RuntimeError("YAML support required for stage workflows")
                for stage in ("S1", "S2", "S3", "S4", "S5", "S6", "S7"):
                    _run_stage(stage, cfg)
                if args.output:
                    (ROOT / args.output).write_text(
                        json.dumps({"status": "ok", "stages": ["S1", "S2", "S3", "S4", "S5", "S6", "S7"]}, indent=2),
                        encoding="utf-8",
                    )
                else:
                    print(json.dumps({"status": "ok", "stages": ["S1", "S2", "S3", "S4", "S5", "S6", "S7"]}, indent=2))
            else:
                runner = AuditRunner(args.config)
                results = runner.run_full_audit(args.target)
                if args.output:
                    runner.save_results(results, args.output)
                else:
                    print(json.dumps(results, indent=2))
        elif args.command == "stage":
            cfg = _load_workflow_config()
            if yaml is None:
                raise RuntimeError("YAML support required for stage workflows")
            _run_stage(args.stage, cfg)
        elif args.command == "diff":
            output = _run_diff(args.old, args.new)
            print(output, end="")
        elif args.command == "explain":
            cfg = _load_workflow_config()
            if yaml is None:
                raise RuntimeError("YAML support required for stage workflows")
            artifacts_dir, _ = _artifact_dirs(cfg)
            scored_path = artifacts_dir / "capabilities_scored.json"
            if not scored_path.exists():
                _stage_s4(cfg)
            scored = json.loads(scored_path.read_text(encoding="utf-8"))
            weights = cfg.get("weights", {})
            capability_id = args.capability_id
            cap = next((c for c in scored.get("capabilities", []) if c.get("id") == capability_id), None)
            if cap is None:
                raise ValueError(f"Capability not found: {capability_id}")
            from scripts.space_traversal.capability_scoring import explain_score

            explanation = explain_score(cap, weights)
            print(f"Explain: {capability_id}")
            for key, partial in explanation["partials"].items():
                print(
                    f"{key}: component={partial['component_value']:.4f} "
                    f"weight={partial['weight']:.4f} contribution={partial['contribution']:.4f}"
                )
    except Exception as e:
        logger.error(f"Audit failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
