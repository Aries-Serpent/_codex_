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
import json
from datetime import datetime

try:
    from .security_audit import SecurityAuditor
    from .dependency_scanner import DependencyScanner
    from .code_quality_checker import CodeQualityChecker
    from .vulnerability_db import VulnerabilityDatabase
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
    root = Path(__file__).resolve().parents[2]
    output_cfg = cfg.get("output", {}) if isinstance(cfg, dict) else {}
    artifacts_dir = Path(output_cfg.get("artifacts_dir", root / "audit_artifacts"))
    reports_dir = Path(output_cfg.get("reports_dir", root / "reports"))
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    tpl_rel = cfg.get("matrix_template", "templates/audit/capability_matrix.md.j2")
    template_path = template_path or (root / tpl_rel)

    timestamp = payload.get("timestamp") or datetime.utcnow().isoformat()
    context = dict(payload)
    context.setdefault("timestamp", timestamp)
    context.setdefault("metrics_schema_version", cfg.get("metrics_schema_version", "1.0.0"))

    md_path = reports_dir / "capability_matrix.md"
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


def main():
    """Main entry point"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    import argparse
    parser = argparse.ArgumentParser(description='Run security audits')
    parser.add_argument('target', type=Path, help='Target path to audit')
    parser.add_argument('--config', type=Path, help='Configuration file')
    parser.add_argument('--output', type=Path, help='Output file path')
    
    args = parser.parse_args()
    
    try:
        runner = AuditRunner(args.config)
        results = runner.run_full_audit(args.target)
        
        if args.output:
            runner.save_results(results, args.output)
        else:
            print(json.dumps(results, indent=2))
            
    except Exception as e:
        logger.error(f"Audit failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
