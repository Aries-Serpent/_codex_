#!/usr/bin/env python3
"""
Rollback Playbook Generator

Analyzes K8s manifests and generates comprehensive rollback procedures.
This script extracts deployment specifications and creates step-by-step
rollback instructions for all resource types.

Usage:
    python generate_rollback_playbook.py --manifests-dir <dir> --output <dir>
    python generate_rollback_playbook.py --manifests-dir manifests/k8s --output .codex
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RollbackPlaybookGenerator:
    """Generates rollback procedures from K8s manifests."""

    def __init__(self, manifests_dir: str, output_dir: str):
        self.manifests_dir = Path(manifests_dir)
        self.output_dir = Path(output_dir)
        self.resources = {
            'deployments': [],
            'statefulsets': [],
            'daemonsets': [],
            'services': [],
            'configmaps': [],
            'secrets': [],
            'hpas': [],
            'other': []
        }
        self.image_registry = {}

    def load_manifests(self) -> None:
        """Load all K8s manifests from directory."""
        logger.info(f"Loading manifests from {self.manifests_dir}")

        for root, dirs, files in os.walk(self.manifests_dir):
            for file in files:
                if file.endswith(('.yaml', '.yml')):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r') as f:
                            docs = yaml.safe_load_all(f)
                            for doc in docs:
                                if doc:
                                    self._process_resource(doc, file_path)
                    except Exception as e:
                        logger.warning(f"Error loading {file_path}: {e}")

    def _process_resource(self, resource: Dict[str, Any], source: Path) -> None:
        """Process a single K8s resource."""
        if not resource.get('kind'):
            return

        kind = resource['kind'].lower()
        name = resource.get('metadata', {}).get('name', 'unknown')
        namespace = resource.get('metadata', {}).get('namespace', 'default')

        resource_info = {
            'name': name,
            'namespace': namespace,
            'kind': resource['kind'],
            'source': str(source),
            'spec': resource.get('spec', {}),
            'metadata': resource.get('metadata', {})
        }

        if kind == 'deployment':
            self.resources['deployments'].append(resource_info)
            self._extract_images(resource_info, 'deployment')
        elif kind == 'statefulset':
            self.resources['statefulsets'].append(resource_info)
            self._extract_images(resource_info, 'statefulset')
        elif kind == 'daemonset':
            self.resources['daemonsets'].append(resource_info)
            self._extract_images(resource_info, 'daemonset')
        elif kind == 'service':
            self.resources['services'].append(resource_info)
        elif kind == 'configmap':
            self.resources['configmaps'].append(resource_info)
        elif kind == 'secret':
            self.resources['secrets'].append(resource_info)
        elif kind == 'horizontalpodautoscaler':
            self.resources['hpas'].append(resource_info)
        else:
            self.resources['other'].append(resource_info)

    def _extract_images(self, resource_info: Dict[str, Any], resource_type: str) -> None:
        """Extract container images from workload resources."""
        spec = resource_info.get('spec', {})
        template_spec = spec.get('template', {}).get('spec', {})
        containers = template_spec.get('containers', [])

        key = f"{resource_type}:{resource_info['namespace']}/{resource_info['name']}"
        images = []
        for container in containers:
            image = container.get('image', '')
            if image:
                images.append(image)

        if images:
            self.image_registry[key] = images

    def generate_playbook(self) -> str:
        """Generate comprehensive rollback playbook."""
        playbook = []

        playbook.append("# Rollback Procedures Playbook\n")
        playbook.append(f"**Generated:** {datetime.utcnow().isoformat()}Z\n")
        playbook.append("**Status:** DRAFT - Review before production use\n\n")

        playbook.append("---\n\n")
        playbook.append("## Table of Contents\n")
        playbook.append("1. Quick Reference (5-minute rollback)\n")
        playbook.append("2. Detailed Procedures (step-by-step)\n")
        playbook.append("3. Emergency Procedures (panic button)\n")
        playbook.append("4. Validation Procedures\n")
        playbook.append("5. Known Issues and Edge Cases\n\n")

        # Quick Reference Section
        playbook.append("---\n\n")
        playbook.append("## 1. Quick Reference (5-Minute Rollback)\n\n")
        playbook.append("**Use this section for rapid rollback in production incidents.**\n\n")

        for deployment in self.resources['deployments']:
            ns = deployment['namespace']
            name = deployment['name']
            playbook.append(f"### Rollback {name}\n\n")
            playbook.append("```bash\n")
            playbook.append("# Get current revision\n")
            playbook.append(f"kubectl rollout history deployment/{name} -n {ns}\n\n")
            playbook.append("# Rollback to previous revision\n")
            playbook.append(f"kubectl rollout undo deployment/{name} -n {ns}\n\n")
            playbook.append("# Wait for rollback to complete\n")
            playbook.append(f"kubectl rollout status deployment/{name} -n {ns} --timeout=5m\n")
            playbook.append("```\n\n")

        # Detailed Procedures
        playbook.append("---\n\n")
        playbook.append("## 2. Detailed Procedures (Step-by-Step)\n\n")

        playbook.append("### Pre-Rollback Checks\n\n")
        playbook.append("1. **Verify cluster connectivity:**\n")
        playbook.append("   ```bash\n")
        playbook.append("   kubectl cluster-info\n")
        playbook.append("   ```\n\n")

        playbook.append("2. **Check current deployment status:**\n")
        for deployment in self.resources['deployments']:
            ns = deployment['namespace']
            name = deployment['name']
            playbook.append("   ```bash\n")
            playbook.append(f"   kubectl get deployment {name} -n {ns}\n")
            playbook.append(f"   kubectl describe deployment {name} -n {ns}\n")
            playbook.append("   ```\n\n")

        playbook.append("3. **Check pod status:**\n")
        playbook.append("   ```bash\n")
        playbook.append("   kubectl get pods -n default\n")
        playbook.append("   kubectl get pods --all-namespaces\n")
        playbook.append("   ```\n\n")

        playbook.append("### Rollout History\n\n")
        for deployment in self.resources['deployments']:
            ns = deployment['namespace']
            name = deployment['name']
            replicas = deployment.get('spec', {}).get('replicas', 1)
            strategy = deployment.get('spec', {}).get('strategy', {}).get('type', 'RollingUpdate')

            playbook.append(f"**Deployment:** {name} (namespace: {ns})\n")
            playbook.append(f"- **Replicas:** {replicas}\n")
            playbook.append(f"- **Strategy:** {strategy}\n")
            playbook.append(f"- **Images:** {', '.join(self.image_registry.get(f'deployment:{ns}/{name}', ['unknown']))}\n\n")

            playbook.append(f"**Rollback procedure for {name}:**\n\n")
            playbook.append("```bash\n")
            playbook.append("# Step 1: View rollout history\n")
            playbook.append(f"kubectl rollout history deployment/{name} -n {ns}\n\n")
            playbook.append("# Step 2: Get details for specific revision (optional)\n")
            playbook.append(f"kubectl rollout history deployment/{name} -n {ns} --revision=<N>\n\n")
            playbook.append("# Step 3: Perform rollback to previous revision\n")
            playbook.append(f"kubectl rollout undo deployment/{name} -n {ns}\n\n")
            playbook.append("# OR: Rollback to specific revision\n")
            playbook.append(f"kubectl rollout undo deployment/{name} -n {ns} --to-revision=<N>\n\n")
            playbook.append("# Step 4: Monitor rollback progress\n")
            playbook.append(f"kubectl rollout status deployment/{name} -n {ns} --timeout=10m\n\n")
            playbook.append("# Step 5: Verify pods are running\n")
            playbook.append(f"kubectl get pods -n {ns} -l app={deployment.get('metadata', {}).get('labels', {}).get('app', 'unknown')}\n")
            playbook.append("```\n\n")

        # Emergency Procedures
        playbook.append("---\n\n")
        playbook.append("## 3. Emergency Procedures (Panic Button)\n\n")
        playbook.append("**Use only in severe incidents. For controlled rollback, use Detailed Procedures.**\n\n")

        for deployment in self.resources['deployments']:
            ns = deployment['namespace']
            name = deployment['name']
            playbook.append(f"### Emergency Rollback: {name}\n\n")
            playbook.append("```bash\n")
            playbook.append("# Option 1: Kill all pods (Kubernetes will restart with previous image)\n")
            playbook.append(f"kubectl delete pods --all -n {ns}\n\n")
            playbook.append("# Option 2: Immediate rollback\n")
            playbook.append(f"kubectl set image deployment/{name} codex-ml=codex-ml:stable -n {ns} --record\n\n")
            playbook.append("# Option 3: Scale down and up\n")
            playbook.append(f"kubectl scale deployment {name} --replicas=0 -n {ns}\n")
            playbook.append("sleep 10\n")
            playbook.append(f"kubectl scale deployment {name} --replicas=3 -n {ns}\n")
            playbook.append("```\n\n")

        # Validation Procedures
        playbook.append("---\n\n")
        playbook.append("## 4. Validation Procedures\n\n")

        playbook.append("### Health Checks\n\n")
        playbook.append("```bash\n")
        playbook.append("# Check deployment health\n")
        for deployment in self.resources['deployments']:
            ns = deployment['namespace']
            name = deployment['name']
            playbook.append(f"kubectl get deployment {name} -n {ns} -o json | jq '.status'\n\n")

        playbook.append("# Check pod health\n")
        playbook.append("kubectl get pods -n default -o wide\n\n")

        playbook.append("# Check service endpoints\n")
        for service in self.resources['services']:
            ns = service['namespace']
            name = service['name']
            playbook.append(f"kubectl get endpoints {name} -n {ns}\n")
        playbook.append("```\n\n")

        playbook.append("### Success Criteria\n\n")
        for deployment in self.resources['deployments']:
            replicas = deployment.get('spec', {}).get('replicas', 1)
            playbook.append(f"- ✅ All {replicas} replicas are Running\n")
            playbook.append("- ✅ All replicas are Ready (1/1)\n")
        playbook.append("- ✅ No CrashLoopBackOff pods\n")
        playbook.append("- ✅ Health endpoints responding\n")
        playbook.append("- ✅ Metrics available\n\n")

        # Known Issues
        playbook.append("---\n\n")
        playbook.append("## 5. Known Issues and Edge Cases\n\n")

        playbook.append("### Issue: Insufficient Resources\n")
        playbook.append("- **Symptom:** Pods stuck in Pending\n")
        playbook.append("- **Solution:** Check resource requests/limits; scale down other workloads\n\n")

        playbook.append("### Issue: Image Pull Errors\n")
        playbook.append("- **Symptom:** Pods stuck in ImagePullBackOff\n")
        playbook.append("- **Solution:** Verify image registry credentials; check network connectivity\n\n")

        playbook.append("### Issue: CrashLoopBackOff\n")
        playbook.append("- **Symptom:** Pods restart continuously\n")
        playbook.append("- **Solution:** Check logs: `kubectl logs <pod> -n <ns>`; verify environment variables\n\n")

        playbook.append("### Issue: Service Connection Refused\n")
        playbook.append("- **Symptom:** Connection refused to service endpoint\n")
        playbook.append("- **Solution:** Verify service selector labels; check pod network policies\n\n")

        # Deployment RPO/RTO
        playbook.append("---\n\n")
        playbook.append("## Deployment RPO/RTO\n\n")

        playbook.append("| Metric | Value | Notes |\n")
        playbook.append("|--------|-------|-------|\n")
        for deployment in self.resources['deployments']:
            ns = deployment['namespace']
            name = deployment['name']
            strategy = deployment.get('spec', {}).get('strategy', {}).get('type', 'RollingUpdate')
            replicas = deployment.get('spec', {}).get('replicas', 1)

            # Calculate estimated RTO based on strategy
            if strategy == 'RollingUpdate':
                rto = f"{replicas * 2}-{replicas * 3} minutes"
            else:
                rto = f"{replicas * 1}-{replicas * 2} minutes"

            playbook.append(f"| {name} | RTO: {rto} | Strategy: {strategy} |\n")

        playbook.append("\n")

        return ''.join(playbook)

    def generate_quick_reference(self) -> str:
        """Generate quick reference text version."""
        reference = []

        reference.append("=" * 80 + "\n")
        reference.append("ROLLBACK PROCEDURES - QUICK REFERENCE\n")
        reference.append("=" * 80 + "\n\n")

        reference.append("CRITICAL: Use only in emergency situations. Follow Detailed Procedures for safety.\n\n")

        for deployment in self.resources['deployments']:
            ns = deployment['namespace']
            name = deployment['name']

            reference.append(f"\n{name.upper()} - Quick Rollback (2 min)\n")
            reference.append("-" * 40 + "\n")
            reference.append(f"kubectl rollout undo deployment/{name} -n {ns}\n")
            reference.append(f"kubectl rollout status deployment/{name} -n {ns} --timeout=10m\n\n")

        reference.append("\nEMERGENCY CONTACTS\n")
        reference.append("-" * 40 + "\n")
        reference.append("Primary On-Call: [See ESCALATION_CONTACTS.md]\n")
        reference.append("Escalation: ops-oncall@company.com\n\n")

        reference.append("For full procedures, see: rollback-procedures.md\n")

        return ''.join(reference)

    def run(self) -> bool:
        """Execute playbook generation."""
        try:
            logger.info("Starting rollback playbook generation...")

            # Load manifests
            self.load_manifests()
            logger.info(f"Loaded {len([d for d in self.resources.values()])} resources")

            # Generate playbook
            playbook = self.generate_playbook()

            # Save playbook
            playbook_path = self.output_dir / 'rollback-procedures.md'
            playbook_path.write_text(playbook)
            logger.info(f"Playbook saved to {playbook_path}")

            # Generate quick reference
            quick_ref = self.generate_quick_reference()
            quick_ref_path = self.output_dir / 'ROLLBACK_PLAYBOOK_PROCEDURES.txt'
            quick_ref_path.write_text(quick_ref)
            logger.info(f"Quick reference saved to {quick_ref_path}")

            # Generate metadata
            metadata = {
                'generated': datetime.utcnow().isoformat() + 'Z',
                'manifests_count': sum(len(v) for v in self.resources.values()),
                'deployments': len(self.resources['deployments']),
                'services': len(self.resources['services']),
                'statefulsets': len(self.resources['statefulsets']),
                'daemonsets': len(self.resources['daemonsets']),
                'images': self.image_registry
            }

            metadata_path = self.output_dir / 'rollback-playbook-metadata.json'
            metadata_path.write_text(json.dumps(metadata, indent=2))
            logger.info(f"Metadata saved to {metadata_path}")

            logger.info("✅ Rollback playbook generation complete")
            return True

        except Exception as e:
            logger.error(f"❌ Error generating playbook: {e}", exc_info=True)
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate rollback procedures from K8s manifests'
    )
    parser.add_argument(
        '--manifests-dir',
        default='manifests/k8s',
        help='Directory containing K8s manifests'
    )
    parser.add_argument(
        '--output',
        default='.codex',
        help='Output directory for generated procedures'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    generator = RollbackPlaybookGenerator(args.manifests_dir, args.output)
    success = generator.run()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
