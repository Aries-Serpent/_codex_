"""
Brain Processor - Core processing logic for Cognitive Brain Agent.

Coordinates the PDA loop, learning integration, and pattern management.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json
from pathlib import Path

# Try imports from parent packages
try:
    from ...core.adaptive_learning import AdaptiveLearningEngine
except ImportError:
    # Fallback for standalone testing
    AdaptiveLearningEngine = None


@dataclass
class TaskContext:
    """Context for a cognitive processing task.
    
    Attributes:
        task_id: Unique task identifier
        task_type: Type of task (e.g., 'code_review', 'test_selection')
        input_data: Input data for processing
        metadata: Additional context
    """
    task_id: str
    task_type: str
    input_data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessingResult:
    """Result from cognitive processing.
    
    Attributes:
        task_id: Original task identifier
        success: Whether processing succeeded
        output: Processing output
        patterns_used: Patterns applied during processing
        learning_updates: Learning updates made
        metrics: Performance metrics
    """
    task_id: str
    success: bool
    output: Any
    patterns_used: List[str] = field(default_factory=list)
    learning_updates: int = 0
    metrics: Dict[str, float] = field(default_factory=dict)


class CognitiveBrainProcessor:
    """Core processor for Cognitive Brain Agent.
    
    Orchestrates the full cognitive processing pipeline:
    1. Perceive: Analyze context and retrieve patterns
    2. Decide: Select optimal action using Q-learning
    3. Act: Execute the action
    4. AfterMath: Update learning and extract patterns
    
    Example:
        processor = CognitiveBrainProcessor()
        context = TaskContext(
            task_id="task-001",
            task_type="code_review",
            input_data={"file": "example.py", "changes": [...]}
        )
        result = processor.process(context)
    """
    
    def __init__(
        self,
        db_path: Optional[Path] = None,
        learning_enabled: bool = True,
        pattern_threshold: float = 0.7,
    ):
        """Initialize the processor.
        
        Args:
            db_path: Path to cognitive brain database
            learning_enabled: Whether to enable adaptive learning
            pattern_threshold: Minimum confidence for pattern matching
        """
        self.db_path = db_path or Path(".codex/cognitive_brain.db")
        self.learning_enabled = learning_enabled
        self.pattern_threshold = pattern_threshold
        
        # Initialize components (if available)
        self.learning_engine = None
        self.pattern_recognizer = None
        self.brain = None
        
        if AdaptiveLearningEngine and learning_enabled:
            self.learning_engine = AdaptiveLearningEngine()
            self.learning_engine.register_actions([
                'approve', 'reject', 'defer', 'request_review',
                'run_tests', 'skip_tests', 'prioritize',
            ])
        
        # Action handlers
        self.action_handlers: Dict[str, callable] = {}
        
        # Processing history
        self.history: List[ProcessingResult] = []
    
    def register_action_handler(self, action: str, handler: callable) -> None:
        """Register a handler for an action.
        
        Args:
            action: Action identifier
            handler: Callable that executes the action
        """
        self.action_handlers[action] = handler
    
    def process(self, context: TaskContext) -> ProcessingResult:
        """Process a task through the full PDA + AfterMath loop.
        
        Args:
            context: Task context with input data
            
        Returns:
            Processing result with output and metrics
        """
        # Phase 1: Perceive
        perception = self._perceive(context)
        
        # Phase 2: Decide
        action = self._decide(perception)
        
        # Phase 3: Act
        output, success = self._act(action, context)
        
        # Phase 4: AfterMath
        metrics = self._aftermath(context, action, output, success)
        
        # Build result
        result = ProcessingResult(
            task_id=context.task_id,
            success=success,
            output=output,
            patterns_used=perception.get('patterns', []),
            learning_updates=metrics.get('learning_updates', 0),
            metrics=metrics,
        )
        
        self.history.append(result)
        return result
    
    def _perceive(self, context: TaskContext) -> Dict[str, Any]:
        """Perceive phase: Analyze context and retrieve patterns.
        
        Args:
            context: Task context
            
        Returns:
            Perception dictionary with features and patterns
        """
        perception = {
            'task_type': context.task_type,
            'features': {},
            'patterns': [],
        }
        
        # Extract features from input
        input_data = context.input_data
        
        if 'complexity' in input_data:
            perception['features']['complexity'] = input_data['complexity']
        
        if 'risk_level' in input_data:
            perception['features']['risk'] = input_data['risk_level']
        
        if 'priority' in input_data:
            perception['features']['priority'] = input_data['priority']
        
        # Query patterns if recognizer available
        if self.pattern_recognizer:
            patterns = self.pattern_recognizer.find_patterns(context.task_type)
            perception['patterns'] = [p.name for p in patterns]
        
        return perception
    
    def _decide(self, perception: Dict[str, Any]) -> str:
        """Decide phase: Select optimal action using Q-learning.
        
        Args:
            perception: Perception from perceive phase
            
        Returns:
            Selected action identifier
        """
        if self.learning_engine:
            # Use Q-learning for action selection
            state = {
                'task_type': hash(perception['task_type']) % 100,
                **perception.get('features', {}),
            }
            return self.learning_engine.select_action(state)
        
        # Default action without learning
        return 'approve'
    
    def _act(self, action: str, context: TaskContext) -> tuple:
        """Act phase: Execute the selected action.
        
        Args:
            action: Action to execute
            context: Task context
            
        Returns:
            Tuple of (output, success)
        """
        if action in self.action_handlers:
            try:
                output = self.action_handlers[action](context)
                return output, True
            except Exception as e:
                return {'error': str(e)}, False
        
        # Default behavior
        return {'action': action, 'status': 'completed'}, True
    
    def _aftermath(
        self,
        context: TaskContext,
        action: str,
        output: Any,
        success: bool,
    ) -> Dict[str, Any]:
        """AfterMath phase: Update learning and extract patterns.
        
        Args:
            context: Task context
            action: Action that was taken
            output: Action output
            success: Whether action succeeded
            
        Returns:
            Metrics dictionary
        """
        metrics = {
            'success': 1.0 if success else 0.0,
            'learning_updates': 0,
        }
        
        if self.learning_engine and self.learning_enabled:
            # Calculate reward
            reward = self._calculate_reward(success, output)
            
            # Build state representations
            state = {'task_type': hash(context.task_type) % 100}
            next_state = {'task_type': hash(context.task_type) % 100, 'completed': 1}
            
            # Update learning
            td_error = self.learning_engine.update(
                state=state,
                action=action,
                reward=reward,
                next_state=next_state,
                done=True,
            )
            
            # Learn from replay
            self.learning_engine.learn_from_replay()
            
            # End episode
            self.learning_engine.end_episode(reward)
            
            metrics['td_error'] = td_error
            metrics['learning_updates'] = 1
            metrics['q_convergence'] = self.learning_engine.state.q_value_convergence
        
        return metrics
    
    def _calculate_reward(self, success: bool, output: Any) -> float:
        """Calculate reward for learning.
        
        Args:
            success: Whether action succeeded
            output: Action output
            
        Returns:
            Reward value
        """
        if not success:
            return -1.0
        
        # Base reward for success
        reward = 1.0
        
        # Bonus for efficiency
        if isinstance(output, dict):
            if output.get('fast', False):
                reward += 0.2
            if output.get('accurate', False):
                reward += 0.3
        
        return reward
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processor statistics.
        
        Returns:
            Statistics dictionary
        """
        stats = {
            'total_tasks': len(self.history),
            'success_rate': 0.0,
            'learning_enabled': self.learning_enabled,
        }
        
        if self.history:
            successes = sum(1 for r in self.history if r.success)
            stats['success_rate'] = successes / len(self.history)
        
        if self.learning_engine:
            stats['learning'] = self.learning_engine.get_statistics()
        
        return stats
    
    def save_state(self, path: Path) -> None:
        """Save processor state to file.
        
        Args:
            path: Output file path
        """
        state = {
            'learning_enabled': self.learning_enabled,
            'pattern_threshold': self.pattern_threshold,
            'history_count': len(self.history),
        }
        
        if self.learning_engine:
            state['policy'] = self.learning_engine.save_policy()
        
        with open(path, 'w') as f:
            json.dump(state, f, indent=2, default=str)
    
    def load_state(self, path: Path) -> None:
        """Load processor state from file.
        
        Args:
            path: Input file path
        """
        with open(path, 'r') as f:
            state = json.load(f)
        
        self.learning_enabled = state.get('learning_enabled', True)
        self.pattern_threshold = state.get('pattern_threshold', 0.7)
        
        if self.learning_engine and 'policy' in state:
            self.learning_engine.load_policy(state['policy'])
