"""
Learning Adapter for CI Testing Agent.

Enhances the CI Testing Agent with cognitive learning capabilities:
- Learning-based test prioritization
- Failure pattern prediction
- Intelligent test selection
- Performance optimization

This adapter integrates the Cognitive Brain's adaptive learning
with CI testing workflows.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import json
from pathlib import Path

# Try imports from cognitive brain
try:
    from ...core.adaptive_learning import AdaptiveLearningEngine, RewardShaper
    from ...core.pattern_recognizer import PatternRecognizer
except ImportError:
    AdaptiveLearningEngine = None
    RewardShaper = None
    PatternRecognizer = None


@dataclass
class TestCase:
    """Representation of a test case.
    
    Attributes:
        name: Test name/identifier
        file_path: Path to test file
        duration_ms: Historical duration
        failure_rate: Historical failure rate
        priority: Calculated priority score
        tags: Test tags/markers
    """
    name: str
    file_path: str
    duration_ms: float = 0.0
    failure_rate: float = 0.0
    priority: float = 0.5
    tags: List[str] = field(default_factory=list)


@dataclass
class TestResult:
    """Result from test execution.
    
    Attributes:
        test: Test case that was run
        passed: Whether test passed
        duration_ms: Actual duration
        error_message: Error message if failed
    """
    test: TestCase
    passed: bool
    duration_ms: float
    error_message: str = ""


class LearningAdapter:
    """Learning adapter for CI Testing Agent.
    
    Enhances CI testing with cognitive learning for:
    1. Test prioritization based on learned patterns
    2. Failure prediction using historical data
    3. Intelligent test selection for efficiency
    4. Continuous improvement of testing strategy
    
    Example:
        adapter = LearningAdapter()
        adapter.initialize()
        
        # Prioritize tests
        tests = [TestCase(name="test_1", file_path="test.py"), ...]
        prioritized = adapter.prioritize_tests(tests, context)
        
        # Report results for learning
        for result in results:
            adapter.report_result(result)
        
        # End session
        adapter.end_session()
    """
    
    def __init__(
        self,
        db_path: Optional[Path] = None,
        policy_path: Optional[Path] = None,
        learning_enabled: bool = True,
    ):
        """Initialize learning adapter.
        
        Args:
            db_path: Path to learning database
            policy_path: Path to save/load policy
            learning_enabled: Whether to enable learning
        """
        self.db_path = db_path
        self.policy_path = policy_path
        self.learning_enabled = learning_enabled
        
        self.engine: Optional[Any] = None
        self.reward_shaper: Optional[Any] = None
        self.pattern_recognizer: Optional[Any] = None
        
        # Test history
        self.test_history: Dict[str, List[bool]] = {}  # name -> [pass/fail history]
        self.session_results: List[TestResult] = []
        
        # Prioritization state
        self.prioritization_actions = [
            'run_first',      # High priority, run first
            'run_normal',     # Normal priority
            'run_last',       # Low priority
            'skip_if_green',  # Skip if previously passing
            'always_run',     # Critical test, always run
        ]
        
        self.initialized = False
    
    def initialize(self) -> None:
        """Initialize the learning adapter."""
        if AdaptiveLearningEngine is None or not self.learning_enabled:
            self.initialized = False
            return
        
        self.engine = AdaptiveLearningEngine(
            learning_rate=0.1,
            discount_factor=0.9,
            epsilon=0.15,  # More exploration for test selection
            batch_size=32,
        )
        self.engine.register_actions(self.prioritization_actions)
        
        if RewardShaper:
            self.reward_shaper = RewardShaper(
                accuracy_weight=0.5,  # Focus on catching failures
                speed_weight=0.3,     # But also care about speed
                confidence_weight=0.1,
                coherence_weight=0.1,
            )
        
        # Load existing policy
        if self.policy_path and self.policy_path.exists():
            self._load_policy()
        
        self.initialized = True
    
    def prioritize_tests(
        self,
        tests: List[TestCase],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[TestCase]:
        """Prioritize tests using learned patterns.
        
        Args:
            tests: List of test cases to prioritize
            context: Current context (changed files, PR info, etc.)
            
        Returns:
            Tests sorted by priority (highest first)
        """
        context = context or {}
        
        # Calculate priority for each test
        prioritized = []
        for test in tests:
            priority = self._calculate_priority(test, context)
            test.priority = priority
            prioritized.append(test)
        
        # Sort by priority (highest first)
        prioritized.sort(key=lambda t: t.priority, reverse=True)
        
        return prioritized
    
    def _calculate_priority(self, test: TestCase, context: Dict[str, Any]) -> float:
        """Calculate priority for a test.
        
        Args:
            test: Test case
            context: Current context
            
        Returns:
            Priority score (0-1)
        """
        # Base priority
        priority = 0.5
        
        # Factor 1: Historical failure rate
        if test.name in self.test_history:
            history = self.test_history[test.name]
            if history:
                failure_rate = 1 - (sum(history) / len(history))
                priority += failure_rate * 0.3
        
        # Factor 2: Test duration (prefer faster tests early)
        if test.duration_ms > 0:
            # Normalize: faster tests get higher priority
            duration_factor = 1.0 / (1.0 + test.duration_ms / 1000)
            priority += duration_factor * 0.1
        
        # Factor 3: Changed files relevance
        changed_files = context.get('changed_files', [])
        if changed_files:
            # Check if test is related to changed files
            for changed in changed_files:
                if self._is_test_related(test, changed):
                    priority += 0.2
                    break
        
        # Factor 4: Use learning engine if available
        if self.engine and self.initialized:
            state = self._build_state(test, context)
            action = self.engine.select_action(state)
            
            # Adjust priority based on action
            action_priority_boost = {
                'run_first': 0.3,
                'always_run': 0.25,
                'run_normal': 0.0,
                'run_last': -0.2,
                'skip_if_green': -0.3,
            }
            priority += action_priority_boost.get(action, 0.0)
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, priority))
    
    def _is_test_related(self, test: TestCase, changed_file: str) -> bool:
        """Check if test is related to a changed file.
        
        Args:
            test: Test case
            changed_file: Path to changed file
            
        Returns:
            True if related
        """
        # Simple heuristic: check for name overlap
        test_name = test.name.lower()
        changed_name = Path(changed_file).stem.lower()
        
        # Remove common prefixes/suffixes
        test_name = test_name.replace('test_', '').replace('_test', '')
        
        return changed_name in test_name or test_name in changed_name
    
    def _build_state(self, test: TestCase, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build state representation for learning.
        
        Args:
            test: Test case
            context: Current context
            
        Returns:
            State dictionary
        """
        state = {
            'failure_rate': test.failure_rate,
            'duration_normalized': min(1.0, test.duration_ms / 10000),
            'has_changed_files': 1 if context.get('changed_files') else 0,
        }
        
        # Add history features
        if test.name in self.test_history:
            history = self.test_history[test.name][-10:]  # Last 10 runs
            state['recent_failures'] = 1 - (sum(history) / len(history)) if history else 0.5
        else:
            state['recent_failures'] = 0.5
        
        return state
    
    def report_result(self, result: TestResult) -> None:
        """Report test result for learning.
        
        Args:
            result: Test execution result
        """
        # Update history
        if result.test.name not in self.test_history:
            self.test_history[result.test.name] = []
        
        self.test_history[result.test.name].append(result.passed)
        
        # Keep limited history
        if len(self.test_history[result.test.name]) > 100:
            self.test_history[result.test.name].pop(0)
        
        # Update test stats
        result.test.duration_ms = result.duration_ms
        history = self.test_history[result.test.name]
        result.test.failure_rate = 1 - (sum(history) / len(history))
        
        # Track session results
        self.session_results.append(result)
        
        # Update learning
        if self.engine and self.initialized:
            self._update_learning(result)
    
    def _update_learning(self, result: TestResult) -> None:
        """Update learning engine with result.
        
        Args:
            result: Test execution result
        """
        state = self._build_state(result.test, {})
        
        # Determine what action was effectively taken
        if result.test.priority > 0.7:
            action = 'run_first'
        elif result.test.priority > 0.5:
            action = 'run_normal'
        else:
            action = 'run_last'
        
        # Calculate reward
        reward = self._calculate_reward(result)
        
        # Update
        self.engine.update(
            state=state,
            action=action,
            reward=reward,
            next_state=state,
            done=True,
        )
    
    def _calculate_reward(self, result: TestResult) -> float:
        """Calculate reward for test result.
        
        Args:
            result: Test execution result
            
        Returns:
            Reward value
        """
        reward = 0.0
        
        # Reward for catching failures early (high priority + failure = good)
        if not result.passed and result.test.priority > 0.6:
            reward += 1.0  # Caught failure early
        elif not result.passed and result.test.priority < 0.4:
            reward -= 0.5  # Missed prioritizing a failing test
        
        # Small reward for fast tests
        if result.duration_ms < 1000:
            reward += 0.1
        
        # Penalty for slow tests that pass (could have been deprioritized)
        if result.passed and result.duration_ms > 5000 and result.test.priority > 0.5:
            reward -= 0.2
        
        return reward
    
    def end_session(self) -> Dict[str, Any]:
        """End testing session and update learning.
        
        Returns:
            Session statistics
        """
        stats = {
            'total_tests': len(self.session_results),
            'passed': sum(1 for r in self.session_results if r.passed),
            'failed': sum(1 for r in self.session_results if not r.passed),
            'total_duration_ms': sum(r.duration_ms for r in self.session_results),
        }
        
        if self.engine and self.initialized:
            # Calculate session reward
            total_reward = 0.0
            for result in self.session_results:
                total_reward += self._calculate_reward(result)
            
            self.engine.end_episode(total_reward)
            
            # Learn from replay
            self.engine.learn_from_replay()
            
            stats['learning'] = self.engine.get_statistics()
            
            # Save policy
            if self.policy_path:
                self._save_policy()
        
        # Clear session
        self.session_results.clear()
        
        return stats
    
    def predict_failures(self, tests: List[TestCase]) -> List[Tuple[TestCase, float]]:
        """Predict which tests are likely to fail.
        
        Args:
            tests: List of test cases
            
        Returns:
            List of (test, failure_probability) tuples, sorted by probability
        """
        predictions = []
        
        for test in tests:
            # Base prediction on history
            prob = test.failure_rate
            
            # Boost based on recent failures
            if test.name in self.test_history:
                recent = self.test_history[test.name][-5:]
                if recent:
                    recent_failure_rate = 1 - (sum(recent) / len(recent))
                    prob = 0.5 * prob + 0.5 * recent_failure_rate
            
            predictions.append((test, prob))
        
        # Sort by failure probability (highest first)
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        return predictions
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get adapter statistics.
        
        Returns:
            Statistics dictionary
        """
        stats = {
            'initialized': self.initialized,
            'learning_enabled': self.learning_enabled,
            'tracked_tests': len(self.test_history),
            'session_results': len(self.session_results),
        }
        
        if self.engine:
            stats['engine'] = self.engine.get_statistics()
        
        return stats
    
    def _save_policy(self) -> None:
        """Save policy to file."""
        if not self.engine or not self.policy_path:
            return
        
        data = {
            'policy': self.engine.save_policy(),
            'test_history': {k: v[-50:] for k, v in self.test_history.items()},
        }
        
        self.policy_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.policy_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_policy(self) -> None:
        """Load policy from file."""
        if not self.engine or not self.policy_path:
            return
        
        try:
            with open(self.policy_path, 'r') as f:
                data = json.load(f)
            
            if 'policy' in data:
                self.engine.load_policy(data['policy'])
            
            if 'test_history' in data:
                self.test_history = data['test_history']
        except Exception as e:
            # If loading fails, continue with a fresh policy but log the error for debugging.
            import logging
            logging.getLogger(__name__).warning(
                "Failed to load learning policy from %s: %s",
                self.policy_path,
                e,
            )
