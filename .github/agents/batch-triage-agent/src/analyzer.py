"""
Batch Triage Analyzer - Extended BatchTriageEngine with cognitive brain integration

Extends the base BatchTriageEngine from scripts/ci/batch_triage.py with additional
capabilities for pattern recognition, learning, and cognitive brain integration.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add parent directories to path for imports
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.ci.batch_triage import (
    BatchTriageEngine,
    FailureRecord,
    TriageGroup,
)

logger = logging.getLogger(__name__)


class BatchTriageAnalyzer(BatchTriageEngine):
    """
    Enhanced batch triage analyzer with cognitive brain integration.
    
    Extends BatchTriageEngine with:
    - Pattern learning and storage
    - Historical context retrieval
    - Confidence scoring
    - Metrics tracking
    """
    
    def __init__(
        self,
        repo: str = "Aries-Serpent/_codex_",
        cognitive_brain_path: Optional[Path] = None,
    ):
        """
        Initialize the analyzer.
        
        Args:
            repo: GitHub repository in format "owner/repo"
            cognitive_brain_path: Path to cognitive brain storage
        """
        super().__init__(repo=repo)
        
        self.cognitive_brain_path = cognitive_brain_path or Path(".codex/cognitive_brain")
        self.patterns_dir = self.cognitive_brain_path / "patterns" / "ci_failures"
        self.patterns_dir.mkdir(parents=True, exist_ok=True)
        
        # Additional tracking
        self.confidence_scores: Dict[int, float] = {}
        self.historical_matches: Dict[int, List[Dict]] = {}
    
    def analyze_with_confidence(self, failure: FailureRecord) -> float:
        """
        Analyze failure and return confidence score.
        
        Args:
            failure: Failure record to analyze
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        self.analyze_failure(failure)
        
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on analysis depth
        if failure.root_cause and failure.root_cause != "Unknown root cause - manual investigation required":
            confidence += 0.2
        
        if failure.detected_issues:
            confidence += 0.2
        
        if failure.suggested_actions:
            confidence += 0.1
        
        # Store confidence score
        self.confidence_scores[failure.issue_number] = confidence
        
        return confidence
    
    def enrich_with_historical_context(self, failure: FailureRecord) -> Dict[str, Any]:
        """
        Enrich failure with historical context from cognitive brain.
        
        Args:
            failure: Failure record to enrich
            
        Returns:
            Dictionary of historical context
        """
        if not failure.failure_type:
            return {}
        
        # Search for similar failures in pattern storage
        pattern_files = list(self.patterns_dir.glob(f"*{failure.failure_type}*.json"))
        
        context = {
            "total_occurrences": len(pattern_files),
            "similar_failures": [],
            "common_remediations": [],
            "avg_resolution_time": None,
        }
        
        import json
        for pattern_file in pattern_files[:5]:  # Limit to 5 most recent
            try:
                with open(pattern_file, 'r') as f:
                    data = json.load(f)
                    context["similar_failures"].append({
                        "timestamp": data.get("timestamp"),
                        "root_cause": data.get("root_cause"),
                        "resolution": data.get("resolution"),
                    })
            except Exception as e:
                logger.warning(f"Failed to read pattern file {pattern_file}: {e}")
        
        self.historical_matches[failure.issue_number] = context["similar_failures"]
        
        return context
    
    def calculate_group_confidence(self, group: TriageGroup) -> float:
        """
        Calculate overall confidence for a triage group.
        
        Args:
            group: Triage group to evaluate
            
        Returns:
            Average confidence score for the group
        """
        if not group.failures:
            return 0.0
        
        total_confidence = 0.0
        for failure in group.failures:
            total_confidence += self.confidence_scores.get(failure.issue_number, 0.5)
        
        return total_confidence / len(group.failures)
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get analysis metrics.
        
        Returns:
            Dictionary of metrics
        """
        return {
            "total_failures": len(self.failures),
            "total_groups": len(self.groups),
            "avg_confidence": sum(self.confidence_scores.values()) / len(self.confidence_scores) if self.confidence_scores else 0.0,
            "high_confidence_count": sum(1 for c in self.confidence_scores.values() if c >= 0.8),
            "low_confidence_count": sum(1 for c in self.confidence_scores.values() if c < 0.5),
            "with_historical_context": len(self.historical_matches),
        }
    
    def export_for_learning(self) -> Dict[str, Any]:
        """
        Export analysis results for cognitive brain learning.
        
        Returns:
            Dictionary suitable for pattern learning
        """
        from datetime import datetime
        
        return {
            "timestamp": datetime.now().isoformat(),
            "repository": self.repo,
            "failures": [
                {
                    "issue_number": f.issue_number,
                    "failure_type": f.failure_type,
                    "root_cause": f.root_cause,
                    "severity": f.severity,
                    "confidence": self.confidence_scores.get(f.issue_number, 0.5),
                    "detected_issues": f.detected_issues,
                    "suggested_actions": f.suggested_actions,
                }
                for f in self.failures
            ],
            "groups": [
                {
                    "group_id": g.group_id,
                    "root_cause": g.root_cause,
                    "severity": g.severity,
                    "failure_count": g.failure_count,
                    "confidence": self.calculate_group_confidence(g),
                }
                for g in self.groups
            ],
            "metrics": self.get_metrics(),
        }
