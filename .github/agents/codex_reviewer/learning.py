"""
Self-Evolution and Learning System

This module contains the learning system that allows the agent to improve
over time based on feedback and review outcomes.
"""

from typing import Dict, List, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SelfEvolutionSystem:
    """
    Learns from reviews and feedback to improve over time.
    
    Tracks:
    - Suggestion acceptance rates
    - Review accuracy
    - Pattern effectiveness
    - User feedback
    """
    
    def __init__(self):
        """Initialize learning system."""
        self.review_history = []
        self.feedback_history = []
        self.learned_patterns = {}
        
    async def learn_from_review(self, context, result):
        """
        Learn from completed review.
        
        Stores review metadata and extracts patterns from successful suggestions.
        
        Args:
            context: ReviewContext for the review
            result: ReviewResult with outcomes
        """
        # Store review metadata
        await self._store_review_metadata(context, result)
        
        # Extract patterns from suggestions
        await self._extract_patterns(result.suggestions)
        
        # Update confidence calibration
        await self._update_confidence_model(result)
        
        logger.info(f"Learned from review #{context.pr_number}")
    
    async def integrate_feedback(self, feedback: Dict[str, Any]):
        """
        Integrate human feedback into learning system.
        
        Args:
            feedback: Feedback data from human reviewers
        """
        # Track which suggestions were accepted/rejected
        await self._track_suggestion_outcomes(feedback)
        
        # Adjust weights based on feedback
        await self._adjust_criteria_weights(feedback)
        
        # Learn new patterns from feedback
        await self._learn_from_feedback_patterns(feedback)
        
        logger.info("Integrated human feedback")
    
    async def learn_from_user_input(self, content: str):
        """
        Learn from explicit user teaching via @codex-reviewer learn: comments.
        
        Args:
            content: Learning content provided by user
        """
        # Parse and store the learning content
        learning_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "content": content,
            "type": "user_input"
        }
        
        self.learned_patterns[f"user_{len(self.learned_patterns)}"] = learning_entry
        
        logger.info(f"Learned from user input: {content[:50]}...")
    
    async def _store_review_metadata(self, context, result):
        """Store review metadata for analysis."""
        metadata = {
            "pr_number": context.pr_number,
            "repo": context.repo,
            "timestamp": datetime.utcnow().isoformat(),
            "confidence": result.confidence,
            "status": result.status,
            "suggestions_count": len(result.suggestions),
            "knowledge_gaps_count": len(result.knowledge_gaps),
            "review_time_seconds": result.review_time_seconds
        }
        
        self.review_history.append(metadata)
        
        # Keep only recent history (last 100 reviews)
        if len(self.review_history) > 100:
            self.review_history = self.review_history[-100:]
    
    async def _extract_patterns(self, suggestions: List[Dict[str, Any]]):
        """Extract patterns from suggestions."""
        for suggestion in suggestions:
            category = suggestion.get("category", "unknown")
            pattern_key = f"{category}_{suggestion.get('type', 'generic')}"
            
            if pattern_key not in self.learned_patterns:
                self.learned_patterns[pattern_key] = {
                    "count": 0,
                    "examples": []
                }
            
            self.learned_patterns[pattern_key]["count"] += 1
            
            # Store example (keep max 5)
            if len(self.learned_patterns[pattern_key]["examples"]) < 5:
                self.learned_patterns[pattern_key]["examples"].append({
                    "description": suggestion.get("description", ""),
                    "severity": suggestion.get("severity", "medium")
                })
    
    async def _update_confidence_model(self, result):
        """Update confidence calibration based on outcomes."""
        # TODO: Implement confidence model updates
        # This would track prediction accuracy vs actual outcomes
        pass
    
    async def _track_suggestion_outcomes(self, feedback: Dict[str, Any]):
        """Track which suggestions were accepted or rejected."""
        accepted = feedback.get("suggestions_accepted", [])
        rejected = feedback.get("suggestions_rejected", [])
        
        self.feedback_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "accepted_count": len(accepted),
            "rejected_count": len(rejected)
        })
        
        # Calculate acceptance rate
        if self.feedback_history:
            total_accepted = sum(f["accepted_count"] for f in self.feedback_history)
            total_rejected = sum(f["rejected_count"] for f in self.feedback_history)
            total = total_accepted + total_rejected
            
            if total > 0:
                acceptance_rate = total_accepted / total
                logger.info(f"Suggestion acceptance rate: {acceptance_rate:.1%}")
    
    async def _adjust_criteria_weights(self, feedback: Dict[str, Any]):
        """Adjust criteria weights based on feedback."""
        # TODO: Implement adaptive weight adjustment
        # This would increase weights for categories with high acceptance
        pass
    
    async def _learn_from_feedback_patterns(self, feedback: Dict[str, Any]):
        """Learn new patterns from feedback."""
        # TODO: Implement pattern learning from feedback
        # This would identify what types of suggestions are most valued
        pass
