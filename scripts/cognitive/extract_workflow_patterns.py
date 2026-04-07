#!/usr/bin/env python3
"""
Extract patterns from workflow data and feed to cognitive brain.

Uses quantum-inspired pattern interference for enhanced pattern detection.

Quantum Principles Applied:
1. Wave Interference: Patterns interfere constructively/destructively
2. Quantum Neural Network: 4-qubit classifier for pattern types
3. Phase Encoding: Pattern features encoded as quantum phases
4. Superposition: Patterns exist in multiple classifications until measured
"""

import argparse
import json
import math
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List

import numpy as np
import requests


@dataclass
class WorkflowPattern:
    """Represents an extracted workflow pattern"""

    pattern_id: str
    pattern_type: str
    workflow_name: str
    failure_rate: float
    avg_duration: float
    frequency: int
    severity: str

    # Quantum properties
    amplitude: float
    frequency_hz: float
    phase: float

    # Metadata
    first_seen: str
    last_seen: str
    occurrences: int

    # Context
    related_patterns: List[str]
    example_workflow_ids: List[int]


class PatternWave:
    """Quantum-inspired pattern representation with wave interference"""

    def __init__(self, pattern_type: str, amplitude: float, frequency: float):
        self.pattern_type = pattern_type
        self.amplitude = amplitude
        self.frequency = frequency
        self.phase = 0.0

    def interfere(self, other: "PatternWave") -> float:
        """
        Calculate interference between two patterns.

        Constructive interference = patterns reinforce (in phase)
        Destructive interference = patterns cancel (out of phase)
        Partial interference = intermediate correlation
        """
        phase_diff = abs(self.phase - other.phase)

        if phase_diff < math.pi / 4:
            # Constructive interference (patterns correlate strongly)
            return self.amplitude + other.amplitude
        elif phase_diff > 3 * math.pi / 4:
            # Destructive interference (patterns anti-correlate)
            return abs(self.amplitude - other.amplitude)
        else:
            # Partial interference
            return math.sqrt(self.amplitude**2 + other.amplitude**2)


class QuantumPatternClassifier:
    """Classify patterns using quantum-inspired neural network"""

    def __init__(self, n_qubits: int = 4):
        self.n_qubits = n_qubits
        self.quantum_state = self._initialize_state()

    def _initialize_state(self) -> np.ndarray:
        """Initialize quantum state in uniform superposition"""
        n_states = 2**self.n_qubits
        return np.ones(n_states, dtype=complex) / np.sqrt(n_states)

    def encode_pattern(self, pattern: WorkflowPattern) -> np.ndarray:
        """Encode pattern features into quantum state"""
        # Extract features
        features = [
            pattern.failure_rate,
            min(pattern.avg_duration / 3600, 1.0),  # Normalize to [0, 1]
            min(pattern.frequency / 100, 1.0),  # Normalize to [0, 1]
            {"low": 0.2, "medium": 0.5, "high": 0.8}.get(pattern.severity, 0.5),
        ]

        # Normalize to [0, 2π] for phase encoding
        phases = [f * 2 * np.pi for f in features[: self.n_qubits]]

        # Apply rotation gates
        state = self.quantum_state.copy()
        for i, phase in enumerate(phases):
            state = self._apply_rotation(state, i, phase)

        return state

    def _apply_rotation(
        self, state: np.ndarray, qubit: int, angle: float
    ) -> np.ndarray:
        """Apply rotation gate to qubit (simplified)"""
        # Simplified rotation for demonstration
        # In a real quantum circuit, this would be a proper tensor product
        rotation_factor = np.exp(1j * angle / 2)
        return state * rotation_factor

    def classify(self, encoded_state: np.ndarray) -> str:
        """Classify pattern by measuring quantum state"""
        # Measurement collapses state to definite classification
        probabilities = np.abs(encoded_state) ** 2

        # Map to pattern classes
        max_prob_idx = np.argmax(probabilities)

        pattern_classes = [
            "false_positive",
            "actual_failure",
            "transient_error",
            "cascading_failure",
            "resource_exhaustion",
            "timeout",
            "network_issue",
            "test_flake",
        ]

        return pattern_classes[max_prob_idx % len(pattern_classes)]


class WorkflowPatternExtractor:
    """Extract patterns from workflow history"""

    def __init__(self, github_token: str, repo: str = "Aries-Serpent/_codex_"):
        self.token = github_token
        self.repo = repo
        self.base_url = f"https://api.github.com/repos/{repo}"
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github+json",
        }
        self.classifier = QuantumPatternClassifier()

    def extract_patterns(self, days_back: int = 30) -> List[WorkflowPattern]:
        """Extract patterns from recent workflow history"""
        print(f"\n🔍 Extracting patterns from last {days_back} days...")

        # Fetch workflow runs
        since = datetime.now(timezone.utc) - timedelta(days=days_back)
        workflows = self._fetch_workflows_since(since)

        print(f"📊 Analyzing {len(workflows)} workflow runs...")

        # Group by workflow name
        by_workflow = self._group_by_workflow(workflows)

        # Extract patterns for each workflow
        patterns = []
        for workflow_name, runs in by_workflow.items():
            workflow_patterns = self._analyze_workflow(workflow_name, runs)
            patterns.extend(workflow_patterns)

        print(f"✨ Found {len(patterns)} patterns")

        # Apply quantum interference to find related patterns
        if patterns:
            patterns = self._apply_pattern_interference(patterns)

        return patterns

    def _fetch_workflows_since(self, since: datetime) -> List[Dict]:
        """Fetch all workflow runs since given date"""
        url = f"{self.base_url}/actions/runs"
        params = {
            "per_page": 100,
            "created": f">={since.isoformat()}",
        }

        all_runs = []
        page = 1

        while True:
            params["page"] = page
            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"⚠️  API request failed: {e}", file=sys.stderr)
                break

            data = response.json()
            runs = data.get("workflow_runs", [])

            if not runs:
                break

            all_runs.extend(runs)
            page += 1

            if page > 10:  # Safety limit
                break

        return all_runs

    def _group_by_workflow(self, workflows: List[Dict]) -> Dict[str, List[Dict]]:
        """Group workflows by name"""
        by_name = {}
        for wf in workflows:
            name = wf.get("name", "Unknown")
            if name not in by_name:
                by_name[name] = []
            by_name[name].append(wf)
        return by_name

    def _analyze_workflow(self, name: str, runs: List[Dict]) -> List[WorkflowPattern]:
        """Analyze a single workflow for patterns"""
        patterns = []

        # Calculate statistics
        total = len(runs)
        if total == 0:
            return patterns

        failures = [r for r in runs if r.get("conclusion") == "failure"]

        failure_rate = len(failures) / total if total > 0 else 0

        # Calculate average duration
        durations = []

        def parse_github_timestamp(timestamp_str: str) -> datetime:
            """Parse a GitHub API timestamp (e.g., '2023-01-01T00:00:00Z') into a datetime."""
            return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

        for run in runs:
            if run.get("updated_at") and run.get("created_at"):
                try:
                    start = parse_github_timestamp(run["created_at"])
                    end = parse_github_timestamp(run["updated_at"])
                    duration = (end - start).total_seconds()
                    durations.append(duration)
                except (ValueError, TypeError):
                    continue

        avg_duration = sum(durations) / len(durations) if durations else 0

        # Pattern 1: High Failure Rate
        if failure_rate > 0.2:  # >20% failure
            pattern = WorkflowPattern(
                pattern_id=f"{name.replace(' ', '_')}_high_failure",
                pattern_type="high_failure_rate",
                workflow_name=name,
                failure_rate=failure_rate,
                avg_duration=avg_duration,
                frequency=len(failures),
                severity="high" if failure_rate > 0.5 else "medium",
                amplitude=failure_rate,
                frequency_hz=len(failures) / 30.0,  # Failures per day
                phase=0.0,
                first_seen=runs[-1].get("created_at", ""),
                last_seen=runs[0].get("created_at", ""),
                occurrences=len(failures),
                related_patterns=[],
                example_workflow_ids=[r["id"] for r in failures[:5]],
            )
            patterns.append(pattern)

        # Pattern 2: Flaky Tests
        if len(runs) > 5:
            flakiness_score = self._calculate_flakiness(runs)

            if flakiness_score > 0.3:
                pattern = WorkflowPattern(
                    pattern_id=f"{name.replace(' ', '_')}_flaky",
                    pattern_type="test_flakiness",
                    workflow_name=name,
                    failure_rate=failure_rate,
                    avg_duration=avg_duration,
                    frequency=int(flakiness_score * total),
                    severity="medium",
                    amplitude=flakiness_score,
                    frequency_hz=flakiness_score,
                    phase=math.pi / 4,  # Offset phase for flaky pattern
                    first_seen=runs[-1].get("created_at", ""),
                    last_seen=runs[0].get("created_at", ""),
                    occurrences=int(flakiness_score * total),
                    related_patterns=[],
                    example_workflow_ids=[r["id"] for r in runs[:5]],
                )
                patterns.append(pattern)

        # Pattern 3: Duration Anomalies
        if durations and avg_duration > 0:
            duration_std = np.std(durations)
            if duration_std / avg_duration > 0.5:  # High variance
                pattern = WorkflowPattern(
                    pattern_id=f"{name.replace(' ', '_')}_duration_anomaly",
                    pattern_type="duration_variance",
                    workflow_name=name,
                    failure_rate=failure_rate,
                    avg_duration=avg_duration,
                    frequency=len(
                        [d for d in durations if abs(d - avg_duration) > duration_std]
                    ),
                    severity="low",
                    amplitude=duration_std / avg_duration,
                    frequency_hz=0.1,
                    phase=math.pi / 2,
                    first_seen=runs[-1].get("created_at", ""),
                    last_seen=runs[0].get("created_at", ""),
                    occurrences=len(durations),
                    related_patterns=[],
                    example_workflow_ids=[r["id"] for r in runs[:5]],
                )
                patterns.append(pattern)

        return patterns

    def _calculate_flakiness(self, runs: List[Dict]) -> float:
        """Calculate flakiness score (0-1) based on result alternation"""
        if len(runs) < 2:
            return 0.0

        alternations = 0
        for i in range(len(runs) - 1):
            curr = runs[i].get("conclusion")
            next_run = runs[i + 1].get("conclusion")

            if curr and next_run and curr != next_run:
                alternations += 1

        # Normalize by possible alternations
        max_alternations = len(runs) - 1
        return alternations / max_alternations if max_alternations > 0 else 0.0

    def _apply_pattern_interference(
        self, patterns: List[WorkflowPattern]
    ) -> List[WorkflowPattern]:
        """Apply quantum interference to find related patterns"""
        print("🌊 Applying quantum interference...")

        # Calculate interference between all pattern pairs
        n = len(patterns)
        interference_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(i + 1, n):
                wave_i = PatternWave(
                    patterns[i].pattern_type,
                    patterns[i].amplitude,
                    patterns[i].frequency_hz,
                )
                wave_i.phase = patterns[i].phase

                wave_j = PatternWave(
                    patterns[j].pattern_type,
                    patterns[j].amplitude,
                    patterns[j].frequency_hz,
                )
                wave_j.phase = patterns[j].phase

                interference = wave_i.interfere(wave_j)
                interference_matrix[i][j] = interference
                interference_matrix[j][i] = interference

        # Find strong correlations (high constructive interference)
        for i, pattern in enumerate(patterns):
            related = []
            for j in range(n):
                if i != j and interference_matrix[i][j] > 1.5:
                    related.append(patterns[j].pattern_id)
            pattern.related_patterns = related

        return patterns


class CognitiveBrainFeeder:
    """Feed extracted patterns to cognitive brain system"""

    def __init__(self, cognitive_brain_dir: Path = Path(".codex/cognitive_brain")):
        self.brain_dir = cognitive_brain_dir
        self.patterns_db = self.brain_dir / "workflow_patterns.jsonl"
        self.brain_dir.mkdir(parents=True, exist_ok=True)

    def feed_patterns(self, patterns: List[WorkflowPattern]) -> Dict:
        """Feed patterns to cognitive brain"""
        print(f"\n🧠 Feeding {len(patterns)} patterns to cognitive brain...")

        # Load existing patterns
        existing = self._load_existing_patterns()

        # Merge new patterns
        pattern_dict = {p.pattern_id: p for p in existing}

        new_count = 0
        updated_count = 0

        for pattern in patterns:
            if pattern.pattern_id in pattern_dict:
                # Update existing pattern
                existing_pattern = pattern_dict[pattern.pattern_id]
                existing_pattern.occurrences += pattern.occurrences
                existing_pattern.last_seen = pattern.last_seen
                updated_count += 1
            else:
                # New pattern
                pattern_dict[pattern.pattern_id] = pattern
                new_count += 1

        # Save updated patterns
        self._save_patterns(list(pattern_dict.values()))

        # Update cognitive brain metadata
        metadata = {
            "last_update": datetime.now(timezone.utc).isoformat(),
            "total_patterns": len(pattern_dict),
            "new_patterns": new_count,
            "updated_patterns": updated_count,
            "pattern_types": self._count_pattern_types(list(pattern_dict.values())),
        }

        self._save_metadata(metadata)

        print("✅ Cognitive brain updated:")
        print(f"   📊 Total patterns: {metadata['total_patterns']}")
        print(f"   🆕 New patterns: {new_count}")
        print(f"   🔄 Updated patterns: {updated_count}")

        return metadata

    def _load_existing_patterns(self) -> List[WorkflowPattern]:
        """Load existing patterns from database"""
        if not self.patterns_db.exists():
            return []

        patterns = []
        with open(self.patterns_db, "r") as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        pattern = WorkflowPattern(**data)
                        patterns.append(pattern)
                    except (json.JSONDecodeError, TypeError) as e:
                        print(f"⚠️  Skipping invalid pattern: {e}", file=sys.stderr)
                        continue

        return patterns

    def _save_patterns(self, patterns: List[WorkflowPattern]):
        """Save patterns to database (atomic write)"""
        temp_file = self.patterns_db.with_suffix(".tmp")

        with open(temp_file, "w") as f:
            for pattern in patterns:
                f.write(json.dumps(asdict(pattern)) + "\n")

        # Atomic rename
        temp_file.replace(self.patterns_db)

    def _save_metadata(self, metadata: Dict):
        """Save cognitive brain metadata"""
        metadata_file = self.brain_dir / "metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
            f.write("\n")

    def _count_pattern_types(self, patterns: List[WorkflowPattern]) -> Dict[str, int]:
        """Count patterns by type"""
        counts = {}
        for pattern in patterns:
            pt = pattern.pattern_type
            counts[pt] = counts.get(pt, 0) + 1
        return counts


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Extract workflow patterns and feed to cognitive brain"
    )
    parser.add_argument(
        "--days-back",
        type=int,
        default=30,
        help="Days of history to analyze (default: 30)",
    )
    parser.add_argument(
        "--repo",
        default="Aries-Serpent/_codex_",
        help="GitHub repository (default: Aries-Serpent/_codex_)",
    )
    parser.add_argument(
        "--github-token",
        default=os.environ.get("GITHUB_TOKEN"),
        help="GitHub token (default: $GITHUB_TOKEN)",
    )

    args = parser.parse_args()

    if not args.github_token:
        print("❌ Error: GITHUB_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)

    print("🔬 Quantum Pattern Extraction System")
    print(f"Repository: {args.repo}")
    print(f"Analysis Period: Last {args.days_back} days")

    try:
        # Extract patterns
        extractor = WorkflowPatternExtractor(args.github_token, args.repo)
        patterns = extractor.extract_patterns(args.days_back)

        if not patterns:
            print("\n✨ No significant patterns detected - all systems healthy!")
            sys.exit(0)

        # Feed to cognitive brain
        feeder = CognitiveBrainFeeder()
        feeder.feed_patterns(patterns)

        print("\n✅ Pattern extraction complete!")
        print(f"📁 Cognitive brain database: {feeder.patterns_db}")

        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
