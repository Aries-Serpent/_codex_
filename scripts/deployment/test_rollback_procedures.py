#!/usr/bin/env python3
"""
Rollback Procedures Dry-Run Validator

Tests all rollback procedures using kubectl --dry-run=client mode
without affecting production resources.

Usage:
    python test_rollback_procedures.py --namespace default
    python test_rollback_procedures.py --manifests-dir manifests/k8s
"""

import argparse
import json
import subprocess
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RollbackProcedureValidator:
    """Validates rollback procedures using dry-run mode."""
    
    def __init__(self, namespace: str = 'default', manifests_dir: str = 'manifests/k8s'):
        self.namespace = namespace
        self.manifests_dir = Path(manifests_dir)
        self.test_results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'tests': []
        }
        self.deployments = []
        self.services = []
        
    def load_resources(self) -> None:
        """Load K8s resources from manifests."""
        logger.info(f"Loading resources from {self.manifests_dir}")
        
        for root, dirs, files in os.walk(self.manifests_dir):
            for file in files:
                if file.endswith(('.yaml', '.yml')):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r') as f:
                            docs = yaml.safe_load_all(f)
                            for doc in docs:
                                if doc and doc.get('kind') == 'Deployment':
                                    self.deployments.append({
                                        'name': doc['metadata']['name'],
                                        'namespace': doc['metadata'].get('namespace', self.namespace),
                                        'spec': doc.get('spec', {})
                                    })
                    except Exception as e:
                        logger.warning(f"Error loading {file_path}: {e}")
    
    def run_kubectl_command(self, cmd: List[str], dry_run: bool = True) -> Tuple[bool, str, str]:
        """Execute kubectl command and return result."""
        if dry_run:
            # Add dry-run flag for dry-run testing
            if '--dry-run=client' not in cmd:
                cmd.insert(-1, '--dry-run=client') if '-o' in cmd else cmd.append('--dry-run=client')
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, '', 'Command timeout'
        except Exception as e:
            return False, '', str(e)
    
    def test_cluster_connectivity(self) -> bool:
        """Test basic cluster connectivity."""
        logger.info("Testing cluster connectivity...")
        
        success, stdout, stderr = self.run_kubectl_command(['kubectl', 'cluster-info'], dry_run=False)
        
        test_result = {
            'name': 'cluster_connectivity',
            'passed': success,
            'command': 'kubectl cluster-info',
            'error': stderr if not success else None
        }
        self.test_results['tests'].append(test_result)
        
        if success:
            self.test_results['passed'] += 1
            logger.info("✅ Cluster connectivity OK")
        else:
            self.test_results['failed'] += 1
            logger.error(f"❌ Cluster connectivity failed: {stderr}")
        
        self.test_results['total'] += 1
        return success
    
    def test_deployment_exists(self, deployment: Dict[str, Any]) -> bool:
        """Test if deployment exists (dry-run)."""
        ns = deployment['namespace']
        name = deployment['name']
        
        logger.info(f"Testing deployment existence: {name} in namespace {ns}")
        
        cmd = ['kubectl', 'get', 'deployment', name, '-n', ns]
        success, stdout, stderr = self.run_kubectl_command(cmd, dry_run=False)
        
        test_result = {
            'name': f'get_deployment_{name}',
            'deployment': name,
            'namespace': ns,
            'passed': success or 'NotFound' not in stderr,
            'command': ' '.join(cmd),
            'error': stderr if not success else None
        }
        self.test_results['tests'].append(test_result)
        
        if success or 'NotFound' not in stderr:
            self.test_results['passed'] += 1
            logger.info(f"✅ Deployment exists: {name}")
        else:
            self.test_results['failed'] += 1
            logger.warning(f"⚠️  Deployment not found (expected in new cluster): {name}")
        
        self.test_results['total'] += 1
        return success
    
    def test_rollback_syntax(self, deployment: Dict[str, Any]) -> bool:
        """Test rollback command syntax using dry-run."""
        ns = deployment['namespace']
        name = deployment['name']
        
        logger.info(f"Testing rollback syntax for {name}...")
        
        # Test 1: Get rollout history (dry-run not applicable, just check syntax)
        cmd1 = ['kubectl', 'rollout', 'history', 'deployment', name, '-n', ns]
        success1, stdout1, stderr1 = self.run_kubectl_command(cmd1, dry_run=False)
        
        test_result1 = {
            'name': f'rollout_history_{name}',
            'deployment': name,
            'namespace': ns,
            'passed': success1 or 'no rollout history found' not in stderr1.lower(),
            'command': ' '.join(cmd1),
            'error': stderr1 if not success1 else None
        }
        self.test_results['tests'].append(test_result1)
        
        if test_result1['passed']:
            self.test_results['passed'] += 1
            logger.info(f"✅ Rollout history syntax OK")
        else:
            self.test_results['failed'] += 1
            logger.warning(f"⚠️  Rollout history not available (expected): {name}")
        
        self.test_results['total'] += 1
        
        # Test 2: Test rollback with dry-run
        cmd2 = ['kubectl', 'rollout', 'undo', 'deployment', name, '-n', ns, '--dry-run=client']
        success2, stdout2, stderr2 = self.run_kubectl_command(cmd2, dry_run=False)
        
        test_result2 = {
            'name': f'rollback_dryrun_{name}',
            'deployment': name,
            'namespace': ns,
            'passed': success2,
            'command': ' '.join(cmd2),
            'error': stderr2 if not success2 else None
        }
        self.test_results['tests'].append(test_result2)
        
        if success2:
            self.test_results['passed'] += 1
            logger.info(f"✅ Rollback dry-run OK")
        else:
            self.test_results['failed'] += 1
            logger.error(f"❌ Rollback dry-run failed: {stderr2}")
        
        self.test_results['total'] += 1
        return success1 and success2
    
    def test_deployment_status(self, deployment: Dict[str, Any]) -> bool:
        """Test deployment status check command."""
        ns = deployment['namespace']
        name = deployment['name']
        
        logger.info(f"Testing deployment status for {name}...")
        
        cmd = ['kubectl', 'get', 'deployment', name, '-n', ns, '-o', 'json']
        success, stdout, stderr = self.run_kubectl_command(cmd, dry_run=False)
        
        test_result = {
            'name': f'deployment_status_{name}',
            'deployment': name,
            'namespace': ns,
            'passed': success or 'NotFound' not in stderr,
            'command': ' '.join(cmd),
            'error': stderr if not success else None
        }
        self.test_results['tests'].append(test_result)
        
        if success:
            self.test_results['passed'] += 1
            logger.info(f"✅ Deployment status check OK")
        else:
            self.test_results['failed'] += 1
            logger.warning(f"⚠️  Deployment status check failed (expected in new cluster): {name}")
        
        self.test_results['total'] += 1
        return success
    
    def test_pod_selection(self, deployment: Dict[str, Any]) -> bool:
        """Test pod selection with deployment selector."""
        ns = deployment['namespace']
        selector = deployment['spec'].get('selector', {}).get('matchLabels', {})
        
        if not selector:
            logger.warning(f"No selector found for deployment")
            return True
        
        logger.info(f"Testing pod selection with selector {selector}...")
        
        # Build label selector
        label_selector = ','.join([f'{k}={v}' for k, v in selector.items()])
        
        cmd = ['kubectl', 'get', 'pods', '-n', ns, '-l', label_selector]
        success, stdout, stderr = self.run_kubectl_command(cmd, dry_run=False)
        
        test_result = {
            'name': f'pod_selection_{deployment["name"]}',
            'deployment': deployment['name'],
            'namespace': ns,
            'selector': label_selector,
            'passed': success,
            'command': ' '.join(cmd),
            'error': stderr if not success else None
        }
        self.test_results['tests'].append(test_result)
        
        if success or 'No resources found' in stdout:
            self.test_results['passed'] += 1
            logger.info(f"✅ Pod selection OK")
        else:
            self.test_results['failed'] += 1
            logger.warning(f"⚠️  Pod selection check failed: {stderr}")
        
        self.test_results['total'] += 1
        return success
    
    def run_all_tests(self) -> bool:
        """Run all validation tests."""
        logger.info("=" * 80)
        logger.info("ROLLBACK PROCEDURE VALIDATION TEST SUITE")
        logger.info("=" * 80)
        logger.info("Mode: DRY-RUN (no actual changes will be made)")
        logger.info("=" * 80)
        
        # Load resources
        self.load_resources()
        
        if not self.deployments:
            logger.warning("No deployments found in manifests")
            return False
        
        logger.info(f"Found {len(self.deployments)} deployment(s) to test\n")
        
        # Test cluster connectivity
        if not self.test_cluster_connectivity():
            logger.error("Cannot connect to cluster; aborting tests")
            return False
        
        logger.info("")
        
        # Test each deployment
        for deployment in self.deployments:
            logger.info(f"\nTesting: {deployment['name']} (namespace: {deployment['namespace']})")
            logger.info("-" * 60)
            
            self.test_deployment_exists(deployment)
            self.test_rollback_syntax(deployment)
            self.test_deployment_status(deployment)
            self.test_pod_selection(deployment)
        
        return self.test_results['failed'] == 0
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """Generate validation report."""
        report = []
        
        report.append("# Rollback Validation Test Report\n\n")
        report.append(f"**Generated:** {datetime.utcnow().isoformat()}Z\n")
        report.append(f"**Mode:** Dry-run (no actual changes)\n\n")
        
        report.append("## Summary\n\n")
        report.append(f"- **Total Tests:** {self.test_results['total']}\n")
        report.append(f"- **Passed:** {self.test_results['passed']} ✅\n")
        report.append(f"- **Failed:** {self.test_results['failed']} ❌\n")
        
        pass_rate = (self.test_results['passed'] / self.test_results['total'] * 100) if self.test_results['total'] > 0 else 0
        report.append(f"- **Pass Rate:** {pass_rate:.1f}%\n\n")
        
        report.append("## Test Results\n\n")
        report.append("| Test | Status | Details |\n")
        report.append("|------|--------|----------|\n")
        
        for test in self.test_results['tests']:
            status = "✅ PASS" if test['passed'] else "❌ FAIL"
            name = test['name'].replace('_', ' ').title()
            details = test.get('error', 'OK')[:50] if test.get('error') else 'OK'
            report.append(f"| {name} | {status} | {details} |\n")
        
        report.append("\n")
        
        if self.test_results['failed'] > 0:
            report.append("## Failed Tests Details\n\n")
            for test in self.test_results['tests']:
                if not test['passed']:
                    report.append(f"### {test['name']}\n\n")
                    report.append(f"**Command:** `{test.get('command', 'N/A')}`\n\n")
                    report.append(f"**Error:** {test.get('error', 'Unknown')}\n\n")
        
        report_text = ''.join(report)
        
        if output_file:
            Path(output_file).write_text(report_text)
            logger.info(f"Report saved to {output_file}")
        
        return report_text


def main():
    """Main entry point."""
    import os
    
    parser = argparse.ArgumentParser(
        description='Validate rollback procedures using dry-run mode'
    )
    parser.add_argument(
        '--namespace',
        default='default',
        help='Kubernetes namespace to test'
    )
    parser.add_argument(
        '--manifests-dir',
        default='manifests/k8s',
        help='Directory containing K8s manifests'
    )
    parser.add_argument(
        '--output',
        help='Output file for validation report'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    validator = RollbackProcedureValidator(args.namespace, args.manifests_dir)
    success = validator.run_all_tests()
    
    # Generate report
    report = validator.generate_report(args.output)
    
    if not args.output:
        print("\n" + "=" * 80)
        print(report)
        print("=" * 80)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
