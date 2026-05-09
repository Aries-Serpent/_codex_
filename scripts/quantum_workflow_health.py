#!/usr/bin/env python3
"""
Quantum-Inspired Workflow Health Analyzer

Principles Applied:
1. Superposition: Workflows exist in multiple states until observed
2. Entanglement: Related workflows affect each other's health
3. Wave Function Collapse: Observation determines definite state
4. Uncertainty Principle: Cannot know exact state without measurement
5. Tunneling: Workflows can "tunnel" through failure states unexpectedly
"""

import argparse
import json
import math
import os
import random
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Optional

import requests


class ComplexEncoder(json.JSONEncoder):
    """Custom JSON encoder for complex numbers"""
    def default(self, obj):
        if isinstance(obj, complex):
            return {'real': obj.real, 'imag': obj.imag}
        return super().default(obj)


@dataclass
class QuantumWorkflowState:
    """Represents workflow in quantum superposition"""
    workflow_id: int
    name: str
    status: str
    conclusion: Optional[str]

    # Quantum properties
    health_amplitude: complex  # Wave function amplitude
    phase: float  # Quantum phase
    entangled_with: list[int]  # Entangled workflow IDs

    # Measured properties
    measured_health: Optional[str] = None
    measurement_time: Optional[str] = None

    def __post_init__(self):
        """Initialize quantum state"""
        if self.health_amplitude is None:
            self.health_amplitude = self._calculate_amplitude()
        if self.phase is None:
            self.phase = random.uniform(0, 2 * math.pi)

    def _calculate_amplitude(self) -> complex:
        """Calculate wave function amplitude from workflow state"""
        if self.status == 'completed':
            if self.conclusion == 'success':
                return complex(0.9, 0.1)  # High health
            if self.conclusion == 'failure':
                return complex(0.1, 0.9)  # Low health
            return complex(0.5, 0.5)  # Uncertain
        # In progress = superposition
        return complex(0.7, 0.3)

    def measure_health(self) -> str:
        """Collapse wave function to definite health state"""
        if self.measured_health:
            return self.measured_health

        # Calculate probability from amplitude
        probability = abs(self.health_amplitude) ** 2

        # Collapse to definite state
        if probability > 0.8:
            self.measured_health = 'healthy'
        elif probability > 0.4:
            self.measured_health = 'degraded'
        else:
            self.measured_health = 'critical'

        self.measurement_time = datetime.now(timezone.utc).isoformat()
        return self.measured_health

    def apply_entanglement(self, other_states: list['QuantumWorkflowState']):
        """Apply entanglement effects from related workflows"""
        amplitude_updated = False
        for other in other_states:
            if other.workflow_id in self.entangled_with:
                # Entanglement causes correlation
                if other.measured_health == 'critical':
                    # Reduce our health amplitude
                    self.health_amplitude *= 0.8
                    amplitude_updated = True
                elif other.measured_health == 'healthy':
                    # Increase our health amplitude
                    self.health_amplitude *= 1.1
                    amplitude_updated = True

        if amplitude_updated:
            # Invalidate cached measurement so it reflects the updated amplitude
            self.measured_health = None
            self.measurement_time = None


class QuantumWorkflowHealthAnalyzer:
    """Analyze workflow health using quantum-inspired principles"""

    def __init__(self, github_token: str, repo: str = 'Aries-Serpent/_codex_'):
        self.token = github_token
        self.repo = repo
        self.base_url = f'https://api.github.com/repos/{repo}'
        self.headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github+json'
        }

    def fetch_workflows(self, commit_sha: str) -> list[dict]:
        """Fetch all workflows for a commit"""
        url = f'{self.base_url}/actions/runs'
        params = {'per_page': 100, 'head_sha': commit_sha}

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        all_runs = response.json()['workflow_runs']

        # Filter by commit SHA
        return [run for run in all_runs if run['head_sha'].startswith(commit_sha[:7])]

    def create_quantum_states(self, workflows: list[dict]) -> list[QuantumWorkflowState]:
        """Convert workflows to quantum states"""
        states = []

        # Identify entanglements (workflows that run together)
        workflow_groups = self._identify_entanglements(workflows)

        for workflow in workflows:
            entangled = workflow_groups.get(workflow['id'], [])

            state = QuantumWorkflowState(
                workflow_id=workflow['id'],
                name=workflow['name'],
                status=workflow['status'],
                conclusion=workflow.get('conclusion'),
                health_amplitude=None,  # Will be calculated
                phase=None,
                entangled_with=entangled
            )
            states.append(state)

        return states

    def _identify_entanglements(self, workflows: list[dict]) -> dict[int, list[int]]:
        """Identify which workflows are entangled (share dependencies)"""
        entanglements = {}

        # Group workflows by event type and branch
        groups = {}
        for wf in workflows:
            key = (wf['event'], wf['head_branch'])
            if key not in groups:
                groups[key] = []
            groups[key].append(wf['id'])

        # Workflows in same group are entangled
        for group_ids in groups.values():
            for wf_id in group_ids:
                entanglements[wf_id] = [x for x in group_ids if x != wf_id]

        return entanglements

    def analyze_health(self, states: list[QuantumWorkflowState]) -> dict:
        """Perform quantum health analysis"""

        # Phase 1: Measure all states (collapse wave functions)
        for state in states:
            state.measure_health()

        # Phase 2: Apply entanglement effects
        for state in states:
            state.apply_entanglement(states)
            # Re-measure after entanglement
            state.measured_health = None
            state.measure_health()

        # Phase 3: Calculate aggregate metrics
        health_counts = {'healthy': 0, 'degraded': 0, 'critical': 0}
        for state in states:
            health_counts[state.measured_health] += 1

        # Phase 4: Quantum tunneling detection
        # (workflows that unexpectedly recovered from failures)
        tunneling_events = self._detect_tunneling(states)

        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_workflows': len(states),
            'health_distribution': health_counts,
            'critical_failures': health_counts['critical'],
            'tunneling_events': len(tunneling_events),
            'overall_health': self._calculate_overall_health(health_counts),
            'quantum_coherence': self._calculate_coherence(states),
            'states': [asdict(s) for s in states],
            'tunneling_details': tunneling_events
        }

    def _detect_tunneling(self, states: list[QuantumWorkflowState]) -> list[dict]:
        """Detect quantum tunneling events (unexpected recoveries)"""
        tunneling = []

        # Look for workflows that went from critical to healthy
        # without expected intermediate states
        for state in states:
            if state.measured_health == 'healthy' and abs(state.health_amplitude.imag) > 0.5:
                tunneling.append({
                    'workflow_id': state.workflow_id,
                    'name': state.name,
                    'description': 'Unexpected recovery from potential failure'
                })

        return tunneling

    def _calculate_overall_health(self, health_counts: dict[str, int]) -> str:
        """Calculate overall system health"""
        total = sum(health_counts.values())
        if total == 0:
            return 'unknown'

        healthy_ratio = health_counts['healthy'] / total

        if healthy_ratio > 0.8:
            return 'healthy'
        if healthy_ratio > 0.5:
            return 'degraded'
        return 'critical'

    def _calculate_coherence(self, states: list[QuantumWorkflowState]) -> float:
        """Calculate quantum coherence (system stability)"""
        if not states:
            return 0.0

        # High coherence = stable system
        # Low coherence = unstable/chaotic system
        phases = [s.phase for s in states]
        phase_variance = sum((p - sum(phases)/len(phases))**2 for p in phases) / len(phases)

        # Normalize to 0-1 scale (lower variance = higher coherence)
        coherence = 1.0 / (1.0 + phase_variance)
        return round(coherence, 3)


def main():
    parser = argparse.ArgumentParser(description='Quantum-Inspired Workflow Health Analysis')
    parser.add_argument('--commit-sha', required=True, help='Commit SHA to analyze')
    parser.add_argument('--full-analysis', action='store_true', help='Run full analysis')

    args = parser.parse_args()

    # Get GitHub token from environment
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set")
        sys.exit(1)

    # Run analysis
    analyzer = QuantumWorkflowHealthAnalyzer(token)

    print(f"🔬 Performing quantum health analysis for commit {args.commit_sha[:7]}...")

    workflows = analyzer.fetch_workflows(args.commit_sha)
    print(f"📊 Found {len(workflows)} workflows")

    states = analyzer.create_quantum_states(workflows)
    print(f"🌀 Created {len(states)} quantum states")

    results = analyzer.analyze_health(states)

    # Save results
    os.makedirs('.codex/monitoring', exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    report_file = f'.codex/monitoring/health_report_{timestamp}.json'

    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2, cls=ComplexEncoder)

    # Also save as "latest"
    with open('.codex/monitoring/health_report_latest.json', 'w') as f:
        json.dump(results, f, indent=2, cls=ComplexEncoder)

    # Print summary
    print("\n" + "="*70)
    print("🎯 QUANTUM HEALTH ANALYSIS RESULTS")
    print("="*70)
    print(f"Overall Health: {results['overall_health'].upper()}")
    print(f"Quantum Coherence: {results['quantum_coherence']} (stability measure)")
    print("\nHealth Distribution:")
    print(f"  ✅ Healthy: {results['health_distribution']['healthy']}")
    print(f"  ⚠️  Degraded: {results['health_distribution']['degraded']}")
    print(f"  🚨 Critical: {results['health_distribution']['critical']}")

    if results['tunneling_events'] > 0:
        print(f"\n🌀 Quantum Tunneling Events: {results['tunneling_events']}")
        print("   (Unexpected recoveries detected)")

    print(f"\n📄 Full report saved: {report_file}")
    print("="*70)

    # Exit with appropriate code
    if results['critical_failures'] > 0:
        print("\n❌ CRITICAL FAILURES DETECTED")
        sys.exit(1)
    elif results['overall_health'] == 'degraded':
        print("\n⚠️  SYSTEM HEALTH DEGRADED")
        sys.exit(0)  # Don't fail the workflow, just warn
    else:
        print("\n✅ ALL SYSTEMS HEALTHY")
        sys.exit(0)


if __name__ == '__main__':
    main()
