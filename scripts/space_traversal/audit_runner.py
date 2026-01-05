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
    sys.exit(1)

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
        self.auditor = SecurityAuditor(self.config)
        self.dep_scanner = DependencyScanner(self.config)
        self.quality_checker = CodeQualityChecker(self.config)
        self.vuln_db = VulnerabilityDatabase(self.config)
        
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
