"""
AfterMath Handler - Post-action processing for learning and pattern extraction.

Handles the AfterMath phase of the PDA loop, including:
- Reward calculation
- Pattern extraction
- Learning updates
- Metrics collection
"""
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
import hashlib
import json


@dataclass
class PatternCandidate:
    """Candidate pattern extracted from processing.
    
    Attributes:
        name: Pattern identifier
        pattern_type: Type of pattern
        context: Context where pattern was observed
        confidence: Confidence in pattern validity
        occurrences: Number of times observed
    """
    name: str
    pattern_type: str
    context: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.5
    occurrences: int = 1


@dataclass
class LearningUpdate:
    """Record of a learning update.
    
    Attributes:
        state: State representation
        action: Action taken
        reward: Reward received
        td_error: Temporal difference error
        timestamp: When update occurred
    """
    state: str
    action: str
    reward: float
    td_error: float = 0.0
    timestamp: float = 0.0


class AfterMathHandler:
    """Handler for AfterMath processing in PDA loop.
    
    Processes action results to:
    1. Calculate rewards for learning
    2. Extract patterns from successful/failed actions
    3. Update learning engine
    4. Collect performance metrics
    
    Example:
        handler = AfterMathHandler()
        
        result = handler.process(
            action='approve',
            success=True,
            context={'task_type': 'code_review'},
            output={'approved': True}
        )
    """
    
    def __init__(
        self,
        learning_engine: Optional[Any] = None,
        pattern_store: Optional[Any] = None,
        reward_weights: Optional[Dict[str, float]] = None,
    ):
        """Initialize AfterMath handler.
        
        Args:
            learning_engine: AdaptiveLearningEngine instance
            pattern_store: Pattern storage backend
            reward_weights: Custom reward component weights
        """
        self.learning_engine = learning_engine
        self.pattern_store = pattern_store
        self.reward_weights = reward_weights or {
            'success': 1.0,
            'speed': 0.2,
            'accuracy': 0.3,
            'efficiency': 0.2,
        }
        
        # History tracking
        self.updates: List[LearningUpdate] = []
        self.patterns_extracted: List[PatternCandidate] = []
        self.metrics_history: List[Dict[str, float]] = []
        
        # Pattern extraction rules
        self.extraction_rules: List[Callable] = []
    
    def register_extraction_rule(self, rule: Callable) -> None:
        """Register a pattern extraction rule.
        
        Args:
            rule: Callable that takes (action, success, context, output) 
                  and returns Optional[PatternCandidate]
        """
        self.extraction_rules.append(rule)
    
    def process(
        self,
        action: str,
        success: bool,
        context: Dict[str, Any],
        output: Any,
        state: Optional[Dict[str, Any]] = None,
        next_state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Process aftermath of an action.
        
        Args:
            action: Action that was taken
            success: Whether action succeeded
            context: Processing context
            output: Action output
            state: State before action
            next_state: State after action
            
        Returns:
            Processing result with metrics
        """
        result = {
            'reward': 0.0,
            'patterns': [],
            'learning_updates': 0,
            'metrics': {},
        }
        
        # Calculate reward
        reward = self._calculate_reward(action, success, context, output)
        result['reward'] = reward
        
        # Extract patterns
        patterns = self._extract_patterns(action, success, context, output)
        result['patterns'] = [p.name for p in patterns]
        self.patterns_extracted.extend(patterns)
        
        # Store patterns if store available
        if self.pattern_store and patterns:
            for pattern in patterns:
                self._store_pattern(pattern)
        
        # Update learning
        if self.learning_engine and state:
            update = self._update_learning(
                state=state,
                action=action,
                reward=reward,
                next_state=next_state or state,
                done=True,
            )
            result['learning_updates'] = 1
            result['td_error'] = update.td_error
            self.updates.append(update)
        
        # Collect metrics
        metrics = self._collect_metrics(action, success, reward, output)
        result['metrics'] = metrics
        self.metrics_history.append(metrics)
        
        return result
    
    def _calculate_reward(
        self,
        action: str,
        success: bool,
        context: Dict[str, Any],
        output: Any,
    ) -> float:
        """Calculate reward for action.
        
        Args:
            action: Action taken
            success: Whether succeeded
            context: Processing context
            output: Action output
            
        Returns:
            Reward value
        """
        reward = 0.0
        
        # Base reward for success/failure
        if success:
            reward += self.reward_weights.get('success', 1.0)
        else:
            reward -= self.reward_weights.get('success', 1.0) * 0.5
        
        # Speed bonus (if timing available)
        if isinstance(output, dict):
            duration = output.get('duration_ms', 0)
            if duration > 0 and duration < 1000:  # Fast execution
                reward += self.reward_weights.get('speed', 0.2)
        
        # Accuracy bonus
        if isinstance(output, dict) and output.get('accurate', False):
            reward += self.reward_weights.get('accuracy', 0.3)
        
        # Context-specific rewards
        task_type = context.get('task_type', '')
        if task_type == 'critical' and success:
            reward *= 1.5  # Higher reward for critical tasks
        
        return reward
    
    def _extract_patterns(
        self,
        action: str,
        success: bool,
        context: Dict[str, Any],
        output: Any,
    ) -> List[PatternCandidate]:
        """Extract patterns from action result.
        
        Args:
            action: Action taken
            success: Whether succeeded
            context: Processing context
            output: Action output
            
        Returns:
            List of extracted pattern candidates
        """
        patterns = []
        
        # Apply registered extraction rules
        for rule in self.extraction_rules:
            try:
                pattern = rule(action, success, context, output)
                if pattern:
                    patterns.append(pattern)
            except Exception:
                pass  # Skip failed rules
        
        # Default pattern extraction
        if success:
            # Extract success pattern
            pattern_name = f"success_{action}_{context.get('task_type', 'default')}"
            patterns.append(PatternCandidate(
                name=pattern_name,
                pattern_type='success',
                context=context,
                confidence=0.7,
            ))
        else:
            # Extract failure pattern for learning
            pattern_name = f"failure_{action}_{context.get('task_type', 'default')}"
            patterns.append(PatternCandidate(
                name=pattern_name,
                pattern_type='failure',
                context=context,
                confidence=0.6,
            ))
        
        return patterns
    
    def _store_pattern(self, pattern: PatternCandidate) -> None:
        """Store pattern in pattern store.
        
        Args:
            pattern: Pattern to store
        """
        if hasattr(self.pattern_store, 'store_pattern'):
            self.pattern_store.store_pattern(
                name=pattern.name,
                pattern_type=pattern.pattern_type,
                context=pattern.context,
                confidence=pattern.confidence,
            )
    
    def _update_learning(
        self,
        state: Dict[str, Any],
        action: str,
        reward: float,
        next_state: Dict[str, Any],
        done: bool,
    ) -> LearningUpdate:
        """Update learning engine.
        
        Args:
            state: State before action
            action: Action taken
            reward: Reward received
            next_state: Resulting state
            done: Whether episode ended
            
        Returns:
            Learning update record
        """
        import time
        
        td_error = self.learning_engine.update(
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            done=done,
        )
        
        # Learn from replay if available
        if hasattr(self.learning_engine, 'learn_from_replay'):
            self.learning_engine.learn_from_replay()
        
        return LearningUpdate(
            state=str(state),
            action=action,
            reward=reward,
            td_error=td_error,
            timestamp=time.time(),
        )
    
    def _collect_metrics(
        self,
        action: str,
        success: bool,
        reward: float,
        output: Any,
    ) -> Dict[str, float]:
        """Collect processing metrics.
        
        Args:
            action: Action taken
            success: Whether succeeded
            reward: Calculated reward
            output: Action output
            
        Returns:
            Metrics dictionary
        """
        metrics = {
            'success': 1.0 if success else 0.0,
            'reward': reward,
        }
        
        if isinstance(output, dict):
            if 'duration_ms' in output:
                metrics['duration_ms'] = output['duration_ms']
            if 'accuracy' in output:
                metrics['accuracy'] = output['accuracy']
        
        return metrics
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get handler statistics.
        
        Returns:
            Statistics dictionary
        """
        if not self.metrics_history:
            return {'total_updates': 0}
        
        rewards = [m.get('reward', 0) for m in self.metrics_history]
        successes = [m.get('success', 0) for m in self.metrics_history]
        
        return {
            'total_updates': len(self.updates),
            'patterns_extracted': len(self.patterns_extracted),
            'avg_reward': sum(rewards) / len(rewards),
            'success_rate': sum(successes) / len(successes),
            'unique_patterns': len(set(p.name for p in self.patterns_extracted)),
        }
    
    def clear_history(self) -> None:
        """Clear processing history."""
        self.updates.clear()
        self.patterns_extracted.clear()
        self.metrics_history.clear()
