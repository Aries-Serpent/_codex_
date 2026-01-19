"""
Batch Triage Learning Engine - Cognitive Brain Integration

This module implements the learning and feedback loop for the batch triage system,
storing patterns, tracking remediation success rates, and providing historical context
for improved decision-making.

Part of Phase 1 Milestone 1.2: Cognitive Brain Feedback Loop
"""

from __future__ import annotations

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import statistics


@dataclass
class FailurePattern:
    """Represents a detected failure pattern"""
    pattern_id: str
    pattern_type: str  # error_message, stack_trace, workflow_name, etc.
    signature: str  # Unique identifier for pattern matching
    occurrences: int
    first_seen: str
    last_seen: str
    success_rate: float  # Remediation success rate
    common_remediations: List[str]
    confidence_score: float


@dataclass
class TriageOutcome:
    """Represents the outcome of a single failure triage"""
    failure_id: str
    failure_type: str
    pattern_matched: Optional[str]
    remediation_applied: Optional[str]
    success: bool
    resolution_time_seconds: Optional[int]
    timestamp: str


class BatchTriageLearningEngine:
    """Records and learns from batch triage outcomes"""
    
    def __init__(
        self, 
        kb_path: Path = Path(".codex/cognitive_brain"),
        metrics_path: Path = Path(".codex/metrics")
    ):
        self.kb_path = Path(kb_path)
        self.patterns_dir = self.kb_path / "patterns" / "ci_failures"
        self.metrics_file = Path(metrics_path) / "batch_triage_metrics.yaml"
        
        # Create directories
        self.patterns_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Cache for performance
        self._patterns_cache: Optional[Dict[str, FailurePattern]] = None
        self._remediations_cache: Optional[List[Dict]] = None
    
    def record_triage_outcome(
        self, 
        batch_id: str, 
        outcomes: List[TriageOutcome]
    ) -> None:
        """
        Store triage results in cognitive brain KB
        
        Args:
            batch_id: Unique identifier for this batch triage run
            outcomes: List of triage outcomes for this batch
        """
        timestamp = datetime.now().isoformat()
        outcome_file = self.patterns_dir / f"batch_{batch_id}_{timestamp.replace(':', '-')}.json"
        
        # Extract patterns from outcomes
        patterns_detected = self._extract_patterns_from_outcomes(outcomes)
        success_rate = self._calculate_success_rate(outcomes)
        
        data = {
            "batch_id": batch_id,
            "timestamp": timestamp,
            "total_failures": len(outcomes),
            "outcomes": [asdict(o) for o in outcomes],
            "patterns_detected": patterns_detected,
            "success_rate": success_rate,
            "resolution_time_avg": self._calculate_avg_resolution_time(outcomes)
        }
        
        outcome_file.write_text(json.dumps(data, indent=2))
        self._update_metrics(data)
        
        # Invalidate cache
        self._patterns_cache = None
    
    def extract_patterns(
        self, 
        failure_descriptions: List[str]
    ) -> List[FailurePattern]:
        """
        Extract recurring failure patterns using signature matching
        
        Args:
            failure_descriptions: List of failure descriptions/error messages
            
        Returns:
            List of detected failure patterns
        """
        # Load historical patterns
        historical = self._load_historical_patterns()
        
        # Generate signatures for current failures
        current_signatures = {}
        for desc in failure_descriptions:
            sig = self._generate_signature(desc)
            if sig not in current_signatures:
                current_signatures[sig] = {
                    "description": desc,
                    "count": 0,
                    "pattern_type": self._classify_pattern_type(desc)
                }
            current_signatures[sig]["count"] += 1
        
        # Match against historical patterns
        matched_patterns = []
        for sig, info in current_signatures.items():
            if sig in historical:
                # Known pattern - update stats
                pattern = historical[sig]
                pattern.occurrences += info["count"]
                pattern.last_seen = datetime.now().isoformat()
                matched_patterns.append(pattern)
            else:
                # New pattern - create entry
                new_pattern = FailurePattern(
                    pattern_id=self._generate_pattern_id(sig),
                    pattern_type=info["pattern_type"],
                    signature=sig,
                    occurrences=info["count"],
                    first_seen=datetime.now().isoformat(),
                    last_seen=datetime.now().isoformat(),
                    success_rate=0.0,
                    common_remediations=[],
                    confidence_score=0.5  # Start with medium confidence
                )
                matched_patterns.append(new_pattern)
        
        # Save updated patterns
        self._save_patterns(matched_patterns)
        
        return matched_patterns
    
    def update_remediation_success_rate(
        self, 
        remediation_id: str, 
        pattern_id: str,
        success: bool,
        resolution_time: Optional[int] = None
    ) -> None:
        """
        Track which fixes work - reinforcement learning
        
        Args:
            remediation_id: Unique identifier for the remediation
            pattern_id: Pattern this remediation addressed
            success: Whether the remediation was successful
            resolution_time: Time to resolve in seconds
        """
        remediations_db = self.patterns_dir / "remediations.jsonl"
        
        entry = {
            "remediation_id": remediation_id,
            "pattern_id": pattern_id,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "resolution_time": resolution_time
        }
        
        # Append to JSONL for easy querying
        with open(remediations_db, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        # Update success rates for pattern
        self._recalculate_pattern_success_rates(pattern_id)
        
        # Invalidate cache
        self._remediations_cache = None
    
    def get_historical_context(self, failure_type: str) -> Dict[str, Any]:
        """
        Retrieve past similar failures for better context
        
        Args:
            failure_type: Type of failure to query
            
        Returns:
            Dictionary with historical statistics and recommendations
        """
        # Load all patterns matching this failure type
        patterns = self._load_patterns_by_type(failure_type)
        
        if not patterns:
            return {
                "total_occurrences": 0,
                "common_remediations": [],
                "success_rates": {},
                "time_to_resolve": None,
                "confidence": "low"
            }
        
        # Aggregate remediations across patterns
        all_remediations = []
        for p in patterns:
            all_remediations.extend(p.common_remediations)
        
        remediation_counts = Counter(all_remediations)
        
        # Get success rates from remediation DB
        success_rates = self._get_remediation_success_rates(failure_type)
        
        # Calculate average resolution time
        resolution_times = self._get_resolution_times(failure_type)
        avg_time = statistics.mean(resolution_times) if resolution_times else None
        
        return {
            "total_occurrences": sum(p.occurrences for p in patterns),
            "common_remediations": [
                {"remediation": r, "count": c} 
                for r, c in remediation_counts.most_common(5)
            ],
            "success_rates": success_rates,
            "time_to_resolve": avg_time,
            "confidence": self._calculate_confidence(len(patterns), sum(p.occurrences for p in patterns))
        }
    
    def get_best_remediation(
        self, 
        failure_type: str,
        failure_description: str
    ) -> Optional[Dict[str, Any]]:
        """
        Use historical success rates to recommend best fix
        
        Args:
            failure_type: Type of failure
            failure_description: Detailed description of the failure
            
        Returns:
            Best remediation with confidence score and metadata
        """
        # Get historical context
        context = self.get_historical_context(failure_type)
        
        if context["total_occurrences"] < 3:
            # Not enough data, return None
            return None
        
        # Match against known patterns
        signature = self._generate_signature(failure_description)
        patterns = self._load_historical_patterns()
        
        if signature in patterns:
            pattern = patterns[signature]
            
            if pattern.common_remediations:
                # Sort by success rate
                remediations_with_scores = []
                for rem in pattern.common_remediations:
                    success_rate = context["success_rates"].get(rem, 0.0)
                    remediations_with_scores.append({
                        "description": rem,
                        "success_rate": success_rate,
                        "pattern_confidence": pattern.confidence_score
                    })
                
                remediations_with_scores.sort(
                    key=lambda x: x["success_rate"] * x["pattern_confidence"],
                    reverse=True
                )
                
                if remediations_with_scores:
                    best = remediations_with_scores[0]
                    return {
                        "remediation": best["description"],
                        "confidence": best["success_rate"] * best["pattern_confidence"],
                        "success_rate": best["success_rate"],
                        "pattern_id": pattern.pattern_id,
                        "historical_occurrences": pattern.occurrences
                    }
        
        # Fallback to most common remediation for this failure type
        if context["common_remediations"]:
            most_common = context["common_remediations"][0]
            return {
                "remediation": most_common["remediation"],
                "confidence": 0.5,  # Medium confidence for fallback
                "success_rate": context["success_rates"].get(most_common["remediation"], 0.0),
                "pattern_id": None,
                "historical_occurrences": most_common["count"]
            }
        
        return None
    
    # Private helper methods
    
    def _generate_signature(self, text: str) -> str:
        """Generate a unique signature for pattern matching"""
        # Normalize text: lowercase, remove timestamps, IDs, etc.
        normalized = text.lower()
        
        # Remove common variable parts
        import re
        normalized = re.sub(r'\d{4}-\d{2}-\d{2}', 'DATE', normalized)
        normalized = re.sub(r'\d+', 'NUM', normalized)
        normalized = re.sub(r'[a-f0-9]{32,}', 'HASH', normalized)
        
        # Hash for consistent signature
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    
    def _generate_pattern_id(self, signature: str) -> str:
        """Generate a human-readable pattern ID"""
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"PAT-{timestamp}-{signature[:8]}"
    
    def _classify_pattern_type(self, description: str) -> str:
        """Classify the type of pattern based on description"""
        lower_desc = description.lower()
        
        if "test" in lower_desc and "fail" in lower_desc:
            return "test_failure"
        elif "timeout" in lower_desc:
            return "timeout"
        elif "import" in lower_desc or "module" in lower_desc:
            return "import_error"
        elif "syntax" in lower_desc:
            return "syntax_error"
        elif "permission" in lower_desc or "access" in lower_desc:
            return "permission_error"
        elif "network" in lower_desc or "connection" in lower_desc:
            return "network_error"
        else:
            return "unknown"
    
    def _load_historical_patterns(self) -> Dict[str, FailurePattern]:
        """Load all historical patterns from storage"""
        if self._patterns_cache is not None:
            return self._patterns_cache
        
        patterns = {}
        patterns_file = self.patterns_dir / "patterns.json"
        
        if patterns_file.exists():
            data = json.loads(patterns_file.read_text())
            for p_dict in data:
                pattern = FailurePattern(**p_dict)
                patterns[pattern.signature] = pattern
        
        self._patterns_cache = patterns
        return patterns
    
    def _save_patterns(self, patterns: List[FailurePattern]) -> None:
        """Save patterns to storage"""
        patterns_file = self.patterns_dir / "patterns.json"
        
        # Merge with existing patterns
        existing = self._load_historical_patterns()
        for pattern in patterns:
            existing[pattern.signature] = pattern
        
        # Save all patterns
        patterns_data = [asdict(p) for p in existing.values()]
        patterns_file.write_text(json.dumps(patterns_data, indent=2))
        
        # Invalidate cache
        self._patterns_cache = None
    
    def _load_patterns_by_type(self, failure_type: str) -> List[FailurePattern]:
        """Load patterns matching a specific failure type"""
        all_patterns = self._load_historical_patterns()
        return [p for p in all_patterns.values() if p.pattern_type == failure_type]
    
    def _extract_patterns_from_outcomes(self, outcomes: List[TriageOutcome]) -> List[str]:
        """Extract pattern IDs from triage outcomes"""
        return [o.pattern_matched for o in outcomes if o.pattern_matched]
    
    def _calculate_success_rate(self, outcomes: List[TriageOutcome]) -> float:
        """Calculate overall success rate for outcomes"""
        if not outcomes:
            return 0.0
        successful = sum(1 for o in outcomes if o.success)
        return successful / len(outcomes)
    
    def _calculate_avg_resolution_time(self, outcomes: List[TriageOutcome]) -> Optional[float]:
        """Calculate average resolution time in seconds"""
        times = [o.resolution_time_seconds for o in outcomes if o.resolution_time_seconds]
        return statistics.mean(times) if times else None
    
    def _update_metrics(self, data: Dict) -> None:
        """Update aggregated metrics file"""
        import yaml
        
        metrics = {}
        if self.metrics_file.exists():
            metrics = yaml.safe_load(self.metrics_file.read_text()) or {}
        
        # Initialize if needed
        if "batch_triage" not in metrics:
            metrics["batch_triage"] = {
                "total_runs": 0,
                "total_failures_processed": 0,
                "overall_success_rate": 0.0,
                "avg_resolution_time": 0.0,
                "last_updated": None
            }
        
        # Update metrics
        bt_metrics = metrics["batch_triage"]
        bt_metrics["total_runs"] += 1
        bt_metrics["total_failures_processed"] += data["total_failures"]
        
        # Update rolling averages
        prev_runs = bt_metrics["total_runs"] - 1
        if prev_runs > 0:
            bt_metrics["overall_success_rate"] = (
                (bt_metrics["overall_success_rate"] * prev_runs + data["success_rate"]) 
                / bt_metrics["total_runs"]
            )
            if data.get("resolution_time_avg"):
                prev_avg = bt_metrics.get("avg_resolution_time", 0)
                bt_metrics["avg_resolution_time"] = (
                    (prev_avg * prev_runs + data["resolution_time_avg"]) 
                    / bt_metrics["total_runs"]
                )
        else:
            bt_metrics["overall_success_rate"] = data["success_rate"]
            bt_metrics["avg_resolution_time"] = data.get("resolution_time_avg", 0)
        
        bt_metrics["last_updated"] = datetime.now().isoformat()
        
        # Save
        self.metrics_file.write_text(yaml.dump(metrics, default_flow_style=False))
    
    def _recalculate_pattern_success_rates(self, pattern_id: str) -> None:
        """Recalculate success rates for a pattern based on remediation history"""
        remediations_db = self.patterns_dir / "remediations.jsonl"
        
        if not remediations_db.exists():
            return
        
        # Load all remediations for this pattern
        remediation_results = []
        with open(remediations_db, 'r') as f:
            for line in f:
                entry = json.loads(line)
                if entry.get("pattern_id") == pattern_id:
                    remediation_results.append(entry)
        
        if not remediation_results:
            return
        
        # Calculate success rate
        successful = sum(1 for r in remediation_results if r["success"])
        success_rate = successful / len(remediation_results)
        
        # Update pattern
        patterns = self._load_historical_patterns()
        for pattern in patterns.values():
            if pattern.pattern_id == pattern_id:
                pattern.success_rate = success_rate
                # Update confidence based on sample size
                pattern.confidence_score = min(
                    1.0, 
                    0.5 + (len(remediation_results) / 20.0) * 0.5
                )
                break
        
        # Save updated patterns
        self._save_patterns(list(patterns.values()))
    
    def _get_remediation_success_rates(self, failure_type: str) -> Dict[str, float]:
        """Get success rates for remediations by failure type"""
        remediations_db = self.patterns_dir / "remediations.jsonl"
        
        if not remediations_db.exists():
            return {}
        
        # Get patterns of this type
        patterns = self._load_patterns_by_type(failure_type)
        pattern_ids = {p.pattern_id for p in patterns}
        
        # Load remediations for these patterns
        remediation_outcomes = defaultdict(list)
        with open(remediations_db, 'r') as f:
            for line in f:
                entry = json.loads(line)
                if entry.get("pattern_id") in pattern_ids:
                    rem_id = entry.get("remediation_id", "unknown")
                    remediation_outcomes[rem_id].append(entry["success"])
        
        # Calculate success rates
        success_rates = {}
        for rem_id, outcomes in remediation_outcomes.items():
            success_rates[rem_id] = sum(outcomes) / len(outcomes) if outcomes else 0.0
        
        return success_rates
    
    def _get_resolution_times(self, failure_type: str) -> List[int]:
        """Get resolution times for a failure type"""
        remediations_db = self.patterns_dir / "remediations.jsonl"
        
        if not remediations_db.exists():
            return []
        
        patterns = self._load_patterns_by_type(failure_type)
        pattern_ids = {p.pattern_id for p in patterns}
        
        resolution_times = []
        with open(remediations_db, 'r') as f:
            for line in f:
                entry = json.loads(line)
                if entry.get("pattern_id") in pattern_ids:
                    if entry.get("resolution_time"):
                        resolution_times.append(entry["resolution_time"])
        
        return resolution_times
    
    def _calculate_confidence(self, pattern_count: int, total_occurrences: int) -> str:
        """Calculate confidence level based on data volume"""
        if total_occurrences >= 20:
            return "high"
        elif total_occurrences >= 10:
            return "medium"
        else:
            return "low"
