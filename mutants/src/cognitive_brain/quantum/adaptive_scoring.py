"""
Adaptive Scoring Optimizer for Superposition Engine

This module implements machine-learning-inspired adaptive scoring to optimize
decision quality in ambiguous scenarios. Learns from feedback to improve weights.

Rayleigh-Inspired Design:
- k₁ optimization through weight tuning
- Resolution enhancement via feedback learning
- Process window control through learning rate

PDA Loop + AfterMath Pattern:
- PLAN: Initialize weights, define update strategy
- DO: Process feedback, update weights
- ASSESS: Measure accuracy improvement
- AfterMath: Track k₁ reduction, coherence trends
"""

from dataclasses import dataclass
from typing import Callable, Dict, List
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


@dataclass
class ScoringWeights:
    """Weights for compliance scoring factors (Phase 8.0 optimized)"""

    compliance_score_weight: float = 0.38  # Reduced from 0.40 (-5%)
    risk_weight: float = 0.32  # Increased from 0.30 (+6.7%)
    cost_weight: float = 0.15  # Unchanged
    impact_weight: float = 0.15  # Unchanged

    def normalize(self) -> "ScoringWeights":
        """Normalize weights to sum to 1.0"""
        total = (
            self.compliance_score_weight
            + self.risk_weight
            + self.cost_weight
            + self.impact_weight
        )
        if total == 0:
            return self
        return ScoringWeights(
            compliance_score_weight=self.compliance_score_weight / total,
            risk_weight=self.risk_weight / total,
            cost_weight=self.cost_weight / total,
            impact_weight=self.impact_weight / total,
        )

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary"""
        return {
            "compliance_score_weight": self.compliance_score_weight,
            "risk_weight": self.risk_weight,
            "cost_weight": self.cost_weight,
            "impact_weight": self.impact_weight,
        }


@dataclass
class FeedbackRecord:
    """Record of decision feedback for learning"""

    audit_id: str
    predicted_decision: str
    actual_decision: str
    is_correct: bool
    audit_features: Dict[str, float]  # Normalized features
    timestamp: float


class AdaptiveScoringOptimizer:
    """
    Adaptive optimizer for superposition scoring functions.

    Uses feedback-driven learning to tune scoring weights for better accuracy
    in ambiguous compliance scenarios.

    Learning Algorithm:
    - Exponential moving average of gradient updates
    - Momentum-based weight adjustments
    - Gradient descent with configurable learning rate

    Rayleigh Metrics:
    - Tracks k₁ (process factor) improvement
    - Monitors resolution enhancement
    - Measures DOF (process window)
    """

    def xǁAdaptiveScoringOptimizerǁ__init____mutmut_orig(self, learning_rate: float = 0.12, momentum: float = 0.9):
        """
        Initialize adaptive scorer with Phase 8.0 optimized learning rate.

        Args:
            learning_rate: Step size for weight updates (default: 0.12, +20% from 0.1)
            momentum: Momentum factor for smoothing (default: 0.9)
        """
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.weights = ScoringWeights().normalize()
        self.feedback_history: List[FeedbackRecord] = []
        self.velocity: Dict[str, float] = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }
        self.k1_history: List[float] = [0.40]  # Track k₁ reduction

    def xǁAdaptiveScoringOptimizerǁ__init____mutmut_1(self, learning_rate: float = 1.12, momentum: float = 0.9):
        """
        Initialize adaptive scorer with Phase 8.0 optimized learning rate.

        Args:
            learning_rate: Step size for weight updates (default: 0.12, +20% from 0.1)
            momentum: Momentum factor for smoothing (default: 0.9)
        """
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.weights = ScoringWeights().normalize()
        self.feedback_history: List[FeedbackRecord] = []
        self.velocity: Dict[str, float] = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }
        self.k1_history: List[float] = [0.40]  # Track k₁ reduction

    def xǁAdaptiveScoringOptimizerǁ__init____mutmut_2(self, learning_rate: float = 0.12, momentum: float = 1.9):
        """
        Initialize adaptive scorer with Phase 8.0 optimized learning rate.

        Args:
            learning_rate: Step size for weight updates (default: 0.12, +20% from 0.1)
            momentum: Momentum factor for smoothing (default: 0.9)
        """
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.weights = ScoringWeights().normalize()
        self.feedback_history: List[FeedbackRecord] = []
        self.velocity: Dict[str, float] = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }
        self.k1_history: List[float] = [0.40]  # Track k₁ reduction

    def xǁAdaptiveScoringOptimizerǁ__init____mutmut_3(self, learning_rate: float = 0.12, momentum: float = 0.9):
        """
        Initialize adaptive scorer with Phase 8.0 optimized learning rate.

        Args:
            learning_rate: Step size for weight updates (default: 0.12, +20% from 0.1)
            momentum: Momentum factor for smoothing (default: 0.9)
        """
        self.learning_rate = None
        self.momentum = momentum
        self.weights = ScoringWeights().normalize()
        self.feedback_history: List[FeedbackRecord] = []
        self.velocity: Dict[str, float] = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }
        self.k1_history: List[float] = [0.40]  # Track k₁ reduction

    def xǁAdaptiveScoringOptimizerǁ__init____mutmut_4(self, learning_rate: float = 0.12, momentum: float = 0.9):
        """
        Initialize adaptive scorer with Phase 8.0 optimized learning rate.

        Args:
            learning_rate: Step size for weight updates (default: 0.12, +20% from 0.1)
            momentum: Momentum factor for smoothing (default: 0.9)
        """
        self.learning_rate = learning_rate
        self.momentum = None
        self.weights = ScoringWeights().normalize()
        self.feedback_history: List[FeedbackRecord] = []
        self.velocity: Dict[str, float] = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }
        self.k1_history: List[float] = [0.40]  # Track k₁ reduction

    def xǁAdaptiveScoringOptimizerǁ__init____mutmut_5(self, learning_rate: float = 0.12, momentum: float = 0.9):
        """
        Initialize adaptive scorer with Phase 8.0 optimized learning rate.

        Args:
            learning_rate: Step size for weight updates (default: 0.12, +20% from 0.1)
            momentum: Momentum factor for smoothing (default: 0.9)
        """
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.weights = None
        self.feedback_history: List[FeedbackRecord] = []
        self.velocity: Dict[str, float] = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }
        self.k1_history: List[float] = [0.40]  # Track k₁ reduction

    def xǁAdaptiveScoringOptimizerǁ__init____mutmut_6(self, learning_rate: float = 0.12, momentum: float = 0.9):
        """
        Initialize adaptive scorer with Phase 8.0 optimized learning rate.

        Args:
            learning_rate: Step size for weight updates (default: 0.12, +20% from 0.1)
            momentum: Momentum factor for smoothing (default: 0.9)
        """
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.weights = ScoringWeights().normalize()
        self.feedback_history: List[FeedbackRecord] = None
        self.velocity: Dict[str, float] = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }
        self.k1_history: List[float] = [0.40]  # Track k₁ reduction

    def xǁAdaptiveScoringOptimizerǁ__init____mutmut_7(self, learning_rate: float = 0.12, momentum: float = 0.9):
        """
        Initialize adaptive scorer with Phase 8.0 optimized learning rate.

        Args:
            learning_rate: Step size for weight updates (default: 0.12, +20% from 0.1)
            momentum: Momentum factor for smoothing (default: 0.9)
        """
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.weights = ScoringWeights().normalize()
        self.feedback_history: List[FeedbackRecord] = []
        self.velocity: Dict[str, float] = None
        self.k1_history: List[float] = [0.40]  # Track k₁ reduction

    def xǁAdaptiveScoringOptimizerǁ__init____mutmut_8(self, learning_rate: float = 0.12, momentum: float = 0.9):
        """
        Initialize adaptive scorer with Phase 8.0 optimized learning rate.

        Args:
            learning_rate: Step size for weight updates (default: 0.12, +20% from 0.1)
            momentum: Momentum factor for smoothing (default: 0.9)
        """
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.weights = ScoringWeights().normalize()
        self.feedback_history: List[FeedbackRecord] = []
        self.velocity: Dict[str, float] = {
            "XXcompliance_score_weightXX": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }
        self.k1_history: List[float] = [0.40]  # Track k₁ reduction

    def xǁAdaptiveScoringOptimizerǁ__init____mutmut_9(self, learning_rate: float = 0.12, momentum: float = 0.9):
        """
        Initialize adaptive scorer with Phase 8.0 optimized learning rate.

        Args:
            learning_rate: Step size for weight updates (default: 0.12, +20% from 0.1)
            momentum: Momentum factor for smoothing (default: 0.9)
        """
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.weights = ScoringWeights().normalize()
        self.feedback_history: List[FeedbackRecord] = []
        self.velocity: Dict[str, float] = {
            "COMPLIANCE_SCORE_WEIGHT": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }
        self.k1_history: List[float] = [0.40]  # Track k₁ reduction

    def xǁAdaptiveScoringOptimizerǁ__init____mutmut_10(self, learning_rate: float = 0.12, momentum: float = 0.9):
        """
        Initialize adaptive scorer with Phase 8.0 optimized learning rate.

        Args:
            learning_rate: Step size for weight updates (default: 0.12, +20% from 0.1)
            momentum: Momentum factor for smoothing (default: 0.9)
        """
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.weights = ScoringWeights().normalize()
        self.feedback_history: List[FeedbackRecord] = []
        self.velocity: Dict[str, float] = {
            "compliance_score_weight": 1.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }
        self.k1_history: List[float] = [0.40]  # Track k₁ reduction

    def xǁAdaptiveScoringOptimizerǁ__init____mutmut_11(self, learning_rate: float = 0.12, momentum: float = 0.9):
        """
        Initialize adaptive scorer with Phase 8.0 optimized learning rate.

        Args:
            learning_rate: Step size for weight updates (default: 0.12, +20% from 0.1)
            momentum: Momentum factor for smoothing (default: 0.9)
        """
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.weights = ScoringWeights().normalize()
        self.feedback_history: List[FeedbackRecord] = []
        self.velocity: Dict[str, float] = {
            "compliance_score_weight": 0.0,
            "XXrisk_weightXX": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }
        self.k1_history: List[float] = [0.40]  # Track k₁ reduction

    def xǁAdaptiveScoringOptimizerǁ__init____mutmut_12(self, learning_rate: float = 0.12, momentum: float = 0.9):
        """
        Initialize adaptive scorer with Phase 8.0 optimized learning rate.

        Args:
            learning_rate: Step size for weight updates (default: 0.12, +20% from 0.1)
            momentum: Momentum factor for smoothing (default: 0.9)
        """
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.weights = ScoringWeights().normalize()
        self.feedback_history: List[FeedbackRecord] = []
        self.velocity: Dict[str, float] = {
            "compliance_score_weight": 0.0,
            "RISK_WEIGHT": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }
        self.k1_history: List[float] = [0.40]  # Track k₁ reduction

    def xǁAdaptiveScoringOptimizerǁ__init____mutmut_13(self, learning_rate: float = 0.12, momentum: float = 0.9):
        """
        Initialize adaptive scorer with Phase 8.0 optimized learning rate.

        Args:
            learning_rate: Step size for weight updates (default: 0.12, +20% from 0.1)
            momentum: Momentum factor for smoothing (default: 0.9)
        """
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.weights = ScoringWeights().normalize()
        self.feedback_history: List[FeedbackRecord] = []
        self.velocity: Dict[str, float] = {
            "compliance_score_weight": 0.0,
            "risk_weight": 1.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }
        self.k1_history: List[float] = [0.40]  # Track k₁ reduction

    def xǁAdaptiveScoringOptimizerǁ__init____mutmut_14(self, learning_rate: float = 0.12, momentum: float = 0.9):
        """
        Initialize adaptive scorer with Phase 8.0 optimized learning rate.

        Args:
            learning_rate: Step size for weight updates (default: 0.12, +20% from 0.1)
            momentum: Momentum factor for smoothing (default: 0.9)
        """
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.weights = ScoringWeights().normalize()
        self.feedback_history: List[FeedbackRecord] = []
        self.velocity: Dict[str, float] = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "XXcost_weightXX": 0.0,
            "impact_weight": 0.0,
        }
        self.k1_history: List[float] = [0.40]  # Track k₁ reduction

    def xǁAdaptiveScoringOptimizerǁ__init____mutmut_15(self, learning_rate: float = 0.12, momentum: float = 0.9):
        """
        Initialize adaptive scorer with Phase 8.0 optimized learning rate.

        Args:
            learning_rate: Step size for weight updates (default: 0.12, +20% from 0.1)
            momentum: Momentum factor for smoothing (default: 0.9)
        """
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.weights = ScoringWeights().normalize()
        self.feedback_history: List[FeedbackRecord] = []
        self.velocity: Dict[str, float] = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "COST_WEIGHT": 0.0,
            "impact_weight": 0.0,
        }
        self.k1_history: List[float] = [0.40]  # Track k₁ reduction

    def xǁAdaptiveScoringOptimizerǁ__init____mutmut_16(self, learning_rate: float = 0.12, momentum: float = 0.9):
        """
        Initialize adaptive scorer with Phase 8.0 optimized learning rate.

        Args:
            learning_rate: Step size for weight updates (default: 0.12, +20% from 0.1)
            momentum: Momentum factor for smoothing (default: 0.9)
        """
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.weights = ScoringWeights().normalize()
        self.feedback_history: List[FeedbackRecord] = []
        self.velocity: Dict[str, float] = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 1.0,
            "impact_weight": 0.0,
        }
        self.k1_history: List[float] = [0.40]  # Track k₁ reduction

    def xǁAdaptiveScoringOptimizerǁ__init____mutmut_17(self, learning_rate: float = 0.12, momentum: float = 0.9):
        """
        Initialize adaptive scorer with Phase 8.0 optimized learning rate.

        Args:
            learning_rate: Step size for weight updates (default: 0.12, +20% from 0.1)
            momentum: Momentum factor for smoothing (default: 0.9)
        """
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.weights = ScoringWeights().normalize()
        self.feedback_history: List[FeedbackRecord] = []
        self.velocity: Dict[str, float] = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "XXimpact_weightXX": 0.0,
        }
        self.k1_history: List[float] = [0.40]  # Track k₁ reduction

    def xǁAdaptiveScoringOptimizerǁ__init____mutmut_18(self, learning_rate: float = 0.12, momentum: float = 0.9):
        """
        Initialize adaptive scorer with Phase 8.0 optimized learning rate.

        Args:
            learning_rate: Step size for weight updates (default: 0.12, +20% from 0.1)
            momentum: Momentum factor for smoothing (default: 0.9)
        """
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.weights = ScoringWeights().normalize()
        self.feedback_history: List[FeedbackRecord] = []
        self.velocity: Dict[str, float] = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "IMPACT_WEIGHT": 0.0,
        }
        self.k1_history: List[float] = [0.40]  # Track k₁ reduction

    def xǁAdaptiveScoringOptimizerǁ__init____mutmut_19(self, learning_rate: float = 0.12, momentum: float = 0.9):
        """
        Initialize adaptive scorer with Phase 8.0 optimized learning rate.

        Args:
            learning_rate: Step size for weight updates (default: 0.12, +20% from 0.1)
            momentum: Momentum factor for smoothing (default: 0.9)
        """
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.weights = ScoringWeights().normalize()
        self.feedback_history: List[FeedbackRecord] = []
        self.velocity: Dict[str, float] = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 1.0,
        }
        self.k1_history: List[float] = [0.40]  # Track k₁ reduction

    def xǁAdaptiveScoringOptimizerǁ__init____mutmut_20(self, learning_rate: float = 0.12, momentum: float = 0.9):
        """
        Initialize adaptive scorer with Phase 8.0 optimized learning rate.

        Args:
            learning_rate: Step size for weight updates (default: 0.12, +20% from 0.1)
            momentum: Momentum factor for smoothing (default: 0.9)
        """
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.weights = ScoringWeights().normalize()
        self.feedback_history: List[FeedbackRecord] = []
        self.velocity: Dict[str, float] = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }
        self.k1_history: List[float] = None  # Track k₁ reduction

    def xǁAdaptiveScoringOptimizerǁ__init____mutmut_21(self, learning_rate: float = 0.12, momentum: float = 0.9):
        """
        Initialize adaptive scorer with Phase 8.0 optimized learning rate.

        Args:
            learning_rate: Step size for weight updates (default: 0.12, +20% from 0.1)
            momentum: Momentum factor for smoothing (default: 0.9)
        """
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.weights = ScoringWeights().normalize()
        self.feedback_history: List[FeedbackRecord] = []
        self.velocity: Dict[str, float] = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }
        self.k1_history: List[float] = [1.4]  # Track k₁ reduction
    
    xǁAdaptiveScoringOptimizerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAdaptiveScoringOptimizerǁ__init____mutmut_1': xǁAdaptiveScoringOptimizerǁ__init____mutmut_1, 
        'xǁAdaptiveScoringOptimizerǁ__init____mutmut_2': xǁAdaptiveScoringOptimizerǁ__init____mutmut_2, 
        'xǁAdaptiveScoringOptimizerǁ__init____mutmut_3': xǁAdaptiveScoringOptimizerǁ__init____mutmut_3, 
        'xǁAdaptiveScoringOptimizerǁ__init____mutmut_4': xǁAdaptiveScoringOptimizerǁ__init____mutmut_4, 
        'xǁAdaptiveScoringOptimizerǁ__init____mutmut_5': xǁAdaptiveScoringOptimizerǁ__init____mutmut_5, 
        'xǁAdaptiveScoringOptimizerǁ__init____mutmut_6': xǁAdaptiveScoringOptimizerǁ__init____mutmut_6, 
        'xǁAdaptiveScoringOptimizerǁ__init____mutmut_7': xǁAdaptiveScoringOptimizerǁ__init____mutmut_7, 
        'xǁAdaptiveScoringOptimizerǁ__init____mutmut_8': xǁAdaptiveScoringOptimizerǁ__init____mutmut_8, 
        'xǁAdaptiveScoringOptimizerǁ__init____mutmut_9': xǁAdaptiveScoringOptimizerǁ__init____mutmut_9, 
        'xǁAdaptiveScoringOptimizerǁ__init____mutmut_10': xǁAdaptiveScoringOptimizerǁ__init____mutmut_10, 
        'xǁAdaptiveScoringOptimizerǁ__init____mutmut_11': xǁAdaptiveScoringOptimizerǁ__init____mutmut_11, 
        'xǁAdaptiveScoringOptimizerǁ__init____mutmut_12': xǁAdaptiveScoringOptimizerǁ__init____mutmut_12, 
        'xǁAdaptiveScoringOptimizerǁ__init____mutmut_13': xǁAdaptiveScoringOptimizerǁ__init____mutmut_13, 
        'xǁAdaptiveScoringOptimizerǁ__init____mutmut_14': xǁAdaptiveScoringOptimizerǁ__init____mutmut_14, 
        'xǁAdaptiveScoringOptimizerǁ__init____mutmut_15': xǁAdaptiveScoringOptimizerǁ__init____mutmut_15, 
        'xǁAdaptiveScoringOptimizerǁ__init____mutmut_16': xǁAdaptiveScoringOptimizerǁ__init____mutmut_16, 
        'xǁAdaptiveScoringOptimizerǁ__init____mutmut_17': xǁAdaptiveScoringOptimizerǁ__init____mutmut_17, 
        'xǁAdaptiveScoringOptimizerǁ__init____mutmut_18': xǁAdaptiveScoringOptimizerǁ__init____mutmut_18, 
        'xǁAdaptiveScoringOptimizerǁ__init____mutmut_19': xǁAdaptiveScoringOptimizerǁ__init____mutmut_19, 
        'xǁAdaptiveScoringOptimizerǁ__init____mutmut_20': xǁAdaptiveScoringOptimizerǁ__init____mutmut_20, 
        'xǁAdaptiveScoringOptimizerǁ__init____mutmut_21': xǁAdaptiveScoringOptimizerǁ__init____mutmut_21
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAdaptiveScoringOptimizerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁAdaptiveScoringOptimizerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁAdaptiveScoringOptimizerǁ__init____mutmut_orig)
    xǁAdaptiveScoringOptimizerǁ__init____mutmut_orig.__name__ = 'xǁAdaptiveScoringOptimizerǁ__init__'

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_orig(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_1(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = None
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_2(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5)) - self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_3(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5)) - self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_4(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5) - self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_5(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight / features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_6(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get(None, 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_7(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", None)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_8(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get(0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_9(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", )
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_10(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("XXcompliance_scoreXX", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_11(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("COMPLIANCE_SCORE", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_12(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 1.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_13(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight / (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_14(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 + features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_15(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (2.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_16(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get(None, 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_17(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", None))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_18(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get(0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_19(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", ))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_20(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("XXrisk_scoreXX", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_21(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("RISK_SCORE", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_22(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 1.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_23(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight / (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_24(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 + features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_25(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (2.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_26(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get(None, 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_27(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", None))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_28(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get(0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_29(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", ))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_30(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("XXcost_scoreXX", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_31(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("COST_SCORE", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_32(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 1.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_33(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight / features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_34(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get(None, 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_35(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", None)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_36(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get(0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_37(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", )
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_38(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("XXimpact_scoreXX", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_39(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("IMPACT_SCORE", 0.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_40(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 1.5)
        )
        return max(0.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_41(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(None, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_42(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, None)

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_43(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_44(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, )

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_45(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(1.0, min(1.0, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_46(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(None, score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_47(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, None))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_48(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(score))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_49(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(1.0, ))

    def xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_50(self, features: Dict[str, float]) -> float:
        """
        Compute weighted score for decision.

        Args:
            features: Normalized feature dict with keys:
                - compliance_score: 0-1
                - risk_score: 0-1 (0=low, 1=high)
                - cost_score: 0-1 (0=low, 1=high)
                - impact_score: 0-1

        Returns:
            Weighted score 0-1
        """
        score = (
            self.weights.compliance_score_weight * features.get("compliance_score", 0.5)
            + self.weights.risk_weight
            * (1.0 - features.get("risk_score", 0.5))  # Invert risk
            + self.weights.cost_weight
            * (1.0 - features.get("cost_score", 0.5))  # Invert cost
            + self.weights.impact_weight * features.get("impact_score", 0.5)
        )
        return max(0.0, min(2.0, score))
    
    xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_1': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_1, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_2': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_2, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_3': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_3, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_4': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_4, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_5': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_5, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_6': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_6, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_7': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_7, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_8': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_8, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_9': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_9, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_10': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_10, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_11': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_11, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_12': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_12, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_13': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_13, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_14': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_14, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_15': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_15, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_16': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_16, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_17': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_17, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_18': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_18, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_19': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_19, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_20': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_20, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_21': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_21, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_22': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_22, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_23': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_23, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_24': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_24, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_25': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_25, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_26': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_26, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_27': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_27, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_28': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_28, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_29': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_29, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_30': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_30, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_31': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_31, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_32': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_32, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_33': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_33, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_34': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_34, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_35': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_35, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_36': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_36, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_37': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_37, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_38': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_38, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_39': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_39, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_40': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_40, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_41': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_41, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_42': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_42, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_43': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_43, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_44': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_44, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_45': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_45, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_46': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_46, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_47': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_47, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_48': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_48, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_49': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_49, 
        'xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_50': xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_50
    }
    
    def compute_score(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_orig"), object.__getattribute__(self, "xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_mutants"), args, kwargs, self)
        return result 
    
    compute_score.__signature__ = _mutmut_signature(xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_orig)
    xǁAdaptiveScoringOptimizerǁcompute_score__mutmut_orig.__name__ = 'xǁAdaptiveScoringOptimizerǁcompute_score'

    def xǁAdaptiveScoringOptimizerǁadd_feedback__mutmut_orig(self, feedback: FeedbackRecord) -> None:
        """
        Add feedback record for learning.

        Args:
            feedback: FeedbackRecord with decision outcome
        """
        self.feedback_history.append(feedback)

    def xǁAdaptiveScoringOptimizerǁadd_feedback__mutmut_1(self, feedback: FeedbackRecord) -> None:
        """
        Add feedback record for learning.

        Args:
            feedback: FeedbackRecord with decision outcome
        """
        self.feedback_history.append(None)
    
    xǁAdaptiveScoringOptimizerǁadd_feedback__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAdaptiveScoringOptimizerǁadd_feedback__mutmut_1': xǁAdaptiveScoringOptimizerǁadd_feedback__mutmut_1
    }
    
    def add_feedback(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAdaptiveScoringOptimizerǁadd_feedback__mutmut_orig"), object.__getattribute__(self, "xǁAdaptiveScoringOptimizerǁadd_feedback__mutmut_mutants"), args, kwargs, self)
        return result 
    
    add_feedback.__signature__ = _mutmut_signature(xǁAdaptiveScoringOptimizerǁadd_feedback__mutmut_orig)
    xǁAdaptiveScoringOptimizerǁadd_feedback__mutmut_orig.__name__ = 'xǁAdaptiveScoringOptimizerǁadd_feedback'

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_orig(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_1(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) <= 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_2(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 6:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_3(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = None
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_4(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[+20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_5(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-21:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_6(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = None

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_7(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(None)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_8(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = None

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_9(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] - self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_10(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum / self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_11(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate / gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_12(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(None, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_13(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, None)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_14(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_15(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, )

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_16(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 1.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_17(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = None
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_18(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = None
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_19(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=None,
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_20(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=None,
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_21(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=None,
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_22(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=None,
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_23(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_24(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_25(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_26(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_27(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                None,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_28(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                None,
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_29(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_30(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_31(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                1.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_32(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"] - self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_33(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["XXcompliance_score_weightXX"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_34(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["COMPLIANCE_SCORE_WEIGHT"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_35(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["XXcompliance_score_weightXX"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_36(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["COMPLIANCE_SCORE_WEIGHT"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_37(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                None, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_38(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, None
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_39(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_40(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_41(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                1.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_42(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] - self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_43(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["XXrisk_weightXX"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_44(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["RISK_WEIGHT"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_45(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["XXrisk_weightXX"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_46(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["RISK_WEIGHT"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_47(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                None, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_48(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, None
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_49(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_50(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_51(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                1.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_52(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] - self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_53(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["XXcost_weightXX"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_54(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["COST_WEIGHT"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_55(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["XXcost_weightXX"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_56(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["COST_WEIGHT"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_57(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                None, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_58(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, None
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_59(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_60(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_61(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                1.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_62(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] - self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_63(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["XXimpact_weightXX"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_64(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["IMPACT_WEIGHT"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_65(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["XXimpact_weightXX"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_66(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["IMPACT_WEIGHT"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_67(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = None

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_68(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = None

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_69(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] + old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_70(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = None
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_71(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) * len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_72(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(None) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_73(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(2 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_74(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = None  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_75(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 / (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_76(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 1.4 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_77(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 + (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_78(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (2.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_79(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) / 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_80(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy + 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_81(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 1.5) * 0.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_82(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 1.2)  # Empirical mapping
        self.k1_history.append(k1_estimate)

        return changes

    def xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_83(self) -> Dict[str, float]:
        """
        Update weights based on accumulated feedback.

        Uses gradient descent with momentum:
        1. Compute gradients from recent feedback
        2. Update velocity with momentum
        3. Apply velocity to weights
        4. Normalize weights

        Returns:
            Dict with weight changes
        """
        if len(self.feedback_history) < 5:
            return {}  # Need minimum feedback

        # Compute gradients from recent feedback (last 20)
        recent = self.feedback_history[-20:]
        gradients = self._compute_gradients(recent)

        # Update velocity with momentum
        for key in self.velocity:
            self.velocity[key] = self.momentum * self.velocity[
                key
            ] + self.learning_rate * gradients.get(key, 0.0)

        # Apply velocity to weights
        old_weights = self.weights.to_dict()
        new_weights = ScoringWeights(
            compliance_score_weight=max(
                0.0,
                old_weights["compliance_score_weight"]
                + self.velocity["compliance_score_weight"],
            ),
            risk_weight=max(
                0.0, old_weights["risk_weight"] + self.velocity["risk_weight"]
            ),
            cost_weight=max(
                0.0, old_weights["cost_weight"] + self.velocity["cost_weight"]
            ),
            impact_weight=max(
                0.0, old_weights["impact_weight"] + self.velocity["impact_weight"]
            ),
        )
        self.weights = new_weights.normalize()

        # Compute weight changes
        changes = {
            key: self.weights.to_dict()[key] - old_weights[key] for key in old_weights
        }

        # Update k₁ estimate (process factor)
        accuracy = sum(1 for f in recent if f.is_correct) / len(recent)
        k1_estimate = 0.40 * (1.0 - (accuracy - 0.5) * 0.2)  # Empirical mapping
        self.k1_history.append(None)

        return changes
    
    xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_1': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_1, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_2': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_2, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_3': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_3, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_4': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_4, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_5': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_5, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_6': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_6, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_7': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_7, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_8': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_8, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_9': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_9, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_10': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_10, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_11': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_11, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_12': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_12, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_13': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_13, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_14': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_14, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_15': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_15, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_16': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_16, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_17': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_17, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_18': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_18, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_19': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_19, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_20': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_20, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_21': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_21, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_22': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_22, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_23': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_23, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_24': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_24, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_25': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_25, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_26': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_26, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_27': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_27, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_28': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_28, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_29': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_29, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_30': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_30, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_31': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_31, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_32': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_32, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_33': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_33, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_34': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_34, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_35': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_35, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_36': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_36, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_37': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_37, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_38': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_38, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_39': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_39, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_40': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_40, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_41': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_41, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_42': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_42, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_43': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_43, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_44': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_44, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_45': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_45, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_46': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_46, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_47': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_47, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_48': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_48, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_49': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_49, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_50': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_50, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_51': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_51, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_52': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_52, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_53': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_53, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_54': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_54, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_55': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_55, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_56': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_56, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_57': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_57, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_58': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_58, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_59': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_59, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_60': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_60, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_61': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_61, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_62': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_62, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_63': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_63, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_64': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_64, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_65': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_65, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_66': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_66, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_67': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_67, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_68': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_68, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_69': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_69, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_70': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_70, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_71': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_71, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_72': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_72, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_73': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_73, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_74': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_74, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_75': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_75, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_76': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_76, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_77': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_77, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_78': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_78, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_79': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_79, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_80': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_80, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_81': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_81, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_82': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_82, 
        'xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_83': xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_83
    }
    
    def update_weights(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_orig"), object.__getattribute__(self, "xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_mutants"), args, kwargs, self)
        return result 
    
    update_weights.__signature__ = _mutmut_signature(xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_orig)
    xǁAdaptiveScoringOptimizerǁupdate_weights__mutmut_orig.__name__ = 'xǁAdaptiveScoringOptimizerǁupdate_weights'

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_orig(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_1(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = None

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_2(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "XXcompliance_score_weightXX": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_3(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "COMPLIANCE_SCORE_WEIGHT": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_4(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 1.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_5(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "XXrisk_weightXX": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_6(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "RISK_WEIGHT": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_7(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 1.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_8(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "XXcost_weightXX": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_9(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "COST_WEIGHT": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_10(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 1.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_11(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "XXimpact_weightXX": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_12(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "IMPACT_WEIGHT": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_13(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 1.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_14(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = None
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_15(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 1
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_16(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_17(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count = 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_18(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count -= 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_19(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 2
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_20(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = None

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_21(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = None

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_22(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = +0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_23(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -1.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_24(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(None) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_25(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 1.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_26(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] = factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_27(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] -= factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_28(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["XXcompliance_score_weightXX"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_29(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["COMPLIANCE_SCORE_WEIGHT"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_30(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor / features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_31(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    None, 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_32(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", None
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_33(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_34(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_35(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "XXcompliance_scoreXX", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_36(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "COMPLIANCE_SCORE", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_37(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 1.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_38(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] = factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_39(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] -= factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_40(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["XXrisk_weightXX"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_41(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["RISK_WEIGHT"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_42(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor / (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_43(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 + features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_44(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    2.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_45(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get(None, 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_46(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", None)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_47(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get(0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_48(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", )
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_49(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("XXrisk_scoreXX", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_50(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("RISK_SCORE", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_51(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 1.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_52(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] = factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_53(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] -= factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_54(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["XXcost_weightXX"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_55(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["COST_WEIGHT"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_56(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor / (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_57(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 + features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_58(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    2.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_59(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get(None, 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_60(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", None)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_61(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get(0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_62(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", )
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_63(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("XXcost_scoreXX", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_64(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("COST_SCORE", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_65(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 1.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_66(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] = factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_67(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] -= factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_68(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["XXimpact_weightXX"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_69(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["IMPACT_WEIGHT"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_70(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor / features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_71(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get(None, 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_72(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", None)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_73(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get(0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_74(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", )

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_75(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("XXimpact_scoreXX", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_76(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("IMPACT_SCORE", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_77(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 1.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_78(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count >= 0:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_79(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 1:
            for key in gradients:
                gradients[key] /= incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_80(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] = incorrect_count

        return gradients

    def xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_81(
        self, feedback_batch: List[FeedbackRecord]
    ) -> Dict[str, float]:
        """
        Compute gradients from feedback batch.

        For each incorrect prediction, compute how weight changes would improve:
        - If predicted > actual: reduce positive contributors
        - If predicted < actual: increase positive contributors

        Args:
            feedback_batch: Recent feedback records

        Returns:
            Dict of gradient values for each weight
        """
        gradients = {
            "compliance_score_weight": 0.0,
            "risk_weight": 0.0,
            "cost_weight": 0.0,
            "impact_weight": 0.0,
        }

        incorrect_count = 0
        for record in feedback_batch:
            if not record.is_correct:
                incorrect_count += 1
                features = record.audit_features

                # Simple gradient: adjust weights toward correct decision
                # This is a simplified approach; production would use proper loss gradients
                factor = -0.1 if self._needs_lower_score(record) else 0.1

                gradients["compliance_score_weight"] += factor * features.get(
                    "compliance_score", 0.5
                )
                gradients["risk_weight"] += factor * (
                    1.0 - features.get("risk_score", 0.5)
                )
                gradients["cost_weight"] += factor * (
                    1.0 - features.get("cost_score", 0.5)
                )
                gradients["impact_weight"] += factor * features.get("impact_score", 0.5)

        # Average gradients
        if incorrect_count > 0:
            for key in gradients:
                gradients[key] *= incorrect_count

        return gradients
    
    xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_1': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_1, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_2': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_2, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_3': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_3, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_4': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_4, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_5': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_5, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_6': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_6, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_7': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_7, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_8': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_8, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_9': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_9, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_10': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_10, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_11': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_11, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_12': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_12, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_13': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_13, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_14': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_14, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_15': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_15, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_16': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_16, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_17': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_17, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_18': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_18, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_19': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_19, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_20': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_20, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_21': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_21, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_22': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_22, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_23': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_23, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_24': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_24, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_25': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_25, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_26': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_26, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_27': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_27, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_28': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_28, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_29': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_29, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_30': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_30, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_31': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_31, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_32': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_32, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_33': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_33, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_34': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_34, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_35': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_35, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_36': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_36, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_37': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_37, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_38': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_38, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_39': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_39, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_40': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_40, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_41': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_41, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_42': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_42, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_43': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_43, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_44': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_44, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_45': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_45, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_46': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_46, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_47': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_47, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_48': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_48, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_49': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_49, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_50': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_50, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_51': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_51, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_52': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_52, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_53': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_53, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_54': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_54, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_55': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_55, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_56': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_56, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_57': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_57, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_58': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_58, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_59': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_59, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_60': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_60, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_61': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_61, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_62': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_62, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_63': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_63, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_64': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_64, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_65': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_65, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_66': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_66, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_67': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_67, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_68': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_68, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_69': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_69, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_70': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_70, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_71': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_71, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_72': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_72, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_73': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_73, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_74': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_74, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_75': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_75, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_76': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_76, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_77': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_77, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_78': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_78, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_79': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_79, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_80': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_80, 
        'xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_81': xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_81
    }
    
    def _compute_gradients(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_orig"), object.__getattribute__(self, "xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _compute_gradients.__signature__ = _mutmut_signature(xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_orig)
    xǁAdaptiveScoringOptimizerǁ_compute_gradients__mutmut_orig.__name__ = 'xǁAdaptiveScoringOptimizerǁ_compute_gradients'

    def xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_orig(self, record: FeedbackRecord) -> bool:
        """Determine if predicted score should be lower"""
        # Simplified logic based on decision types
        reject_decisions = {"reject", "REJECT"}
        predicted_is_reject = record.predicted_decision in reject_decisions
        actual_is_reject = record.actual_decision in reject_decisions
        return predicted_is_reject and not actual_is_reject

    def xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_1(self, record: FeedbackRecord) -> bool:
        """Determine if predicted score should be lower"""
        # Simplified logic based on decision types
        reject_decisions = None
        predicted_is_reject = record.predicted_decision in reject_decisions
        actual_is_reject = record.actual_decision in reject_decisions
        return predicted_is_reject and not actual_is_reject

    def xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_2(self, record: FeedbackRecord) -> bool:
        """Determine if predicted score should be lower"""
        # Simplified logic based on decision types
        reject_decisions = {"XXrejectXX", "REJECT"}
        predicted_is_reject = record.predicted_decision in reject_decisions
        actual_is_reject = record.actual_decision in reject_decisions
        return predicted_is_reject and not actual_is_reject

    def xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_3(self, record: FeedbackRecord) -> bool:
        """Determine if predicted score should be lower"""
        # Simplified logic based on decision types
        reject_decisions = {"REJECT", "REJECT"}
        predicted_is_reject = record.predicted_decision in reject_decisions
        actual_is_reject = record.actual_decision in reject_decisions
        return predicted_is_reject and not actual_is_reject

    def xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_4(self, record: FeedbackRecord) -> bool:
        """Determine if predicted score should be lower"""
        # Simplified logic based on decision types
        reject_decisions = {"reject", "XXREJECTXX"}
        predicted_is_reject = record.predicted_decision in reject_decisions
        actual_is_reject = record.actual_decision in reject_decisions
        return predicted_is_reject and not actual_is_reject

    def xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_5(self, record: FeedbackRecord) -> bool:
        """Determine if predicted score should be lower"""
        # Simplified logic based on decision types
        reject_decisions = {"reject", "reject"}
        predicted_is_reject = record.predicted_decision in reject_decisions
        actual_is_reject = record.actual_decision in reject_decisions
        return predicted_is_reject and not actual_is_reject

    def xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_6(self, record: FeedbackRecord) -> bool:
        """Determine if predicted score should be lower"""
        # Simplified logic based on decision types
        reject_decisions = {"reject", "REJECT"}
        predicted_is_reject = None
        actual_is_reject = record.actual_decision in reject_decisions
        return predicted_is_reject and not actual_is_reject

    def xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_7(self, record: FeedbackRecord) -> bool:
        """Determine if predicted score should be lower"""
        # Simplified logic based on decision types
        reject_decisions = {"reject", "REJECT"}
        predicted_is_reject = record.predicted_decision not in reject_decisions
        actual_is_reject = record.actual_decision in reject_decisions
        return predicted_is_reject and not actual_is_reject

    def xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_8(self, record: FeedbackRecord) -> bool:
        """Determine if predicted score should be lower"""
        # Simplified logic based on decision types
        reject_decisions = {"reject", "REJECT"}
        predicted_is_reject = record.predicted_decision in reject_decisions
        actual_is_reject = None
        return predicted_is_reject and not actual_is_reject

    def xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_9(self, record: FeedbackRecord) -> bool:
        """Determine if predicted score should be lower"""
        # Simplified logic based on decision types
        reject_decisions = {"reject", "REJECT"}
        predicted_is_reject = record.predicted_decision in reject_decisions
        actual_is_reject = record.actual_decision not in reject_decisions
        return predicted_is_reject and not actual_is_reject

    def xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_10(self, record: FeedbackRecord) -> bool:
        """Determine if predicted score should be lower"""
        # Simplified logic based on decision types
        reject_decisions = {"reject", "REJECT"}
        predicted_is_reject = record.predicted_decision in reject_decisions
        actual_is_reject = record.actual_decision in reject_decisions
        return predicted_is_reject or not actual_is_reject

    def xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_11(self, record: FeedbackRecord) -> bool:
        """Determine if predicted score should be lower"""
        # Simplified logic based on decision types
        reject_decisions = {"reject", "REJECT"}
        predicted_is_reject = record.predicted_decision in reject_decisions
        actual_is_reject = record.actual_decision in reject_decisions
        return predicted_is_reject and actual_is_reject
    
    xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_1': xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_1, 
        'xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_2': xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_2, 
        'xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_3': xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_3, 
        'xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_4': xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_4, 
        'xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_5': xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_5, 
        'xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_6': xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_6, 
        'xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_7': xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_7, 
        'xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_8': xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_8, 
        'xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_9': xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_9, 
        'xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_10': xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_10, 
        'xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_11': xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_11
    }
    
    def _needs_lower_score(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_orig"), object.__getattribute__(self, "xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _needs_lower_score.__signature__ = _mutmut_signature(xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_orig)
    xǁAdaptiveScoringOptimizerǁ_needs_lower_score__mutmut_orig.__name__ = 'xǁAdaptiveScoringOptimizerǁ_needs_lower_score'

    def xǁAdaptiveScoringOptimizerǁget_current_k1__mutmut_orig(self) -> float:
        """Get current k₁ estimate"""
        return self.k1_history[-1] if self.k1_history else 0.40

    def xǁAdaptiveScoringOptimizerǁget_current_k1__mutmut_1(self) -> float:
        """Get current k₁ estimate"""
        return self.k1_history[+1] if self.k1_history else 0.40

    def xǁAdaptiveScoringOptimizerǁget_current_k1__mutmut_2(self) -> float:
        """Get current k₁ estimate"""
        return self.k1_history[-2] if self.k1_history else 0.40

    def xǁAdaptiveScoringOptimizerǁget_current_k1__mutmut_3(self) -> float:
        """Get current k₁ estimate"""
        return self.k1_history[-1] if self.k1_history else 1.4
    
    xǁAdaptiveScoringOptimizerǁget_current_k1__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAdaptiveScoringOptimizerǁget_current_k1__mutmut_1': xǁAdaptiveScoringOptimizerǁget_current_k1__mutmut_1, 
        'xǁAdaptiveScoringOptimizerǁget_current_k1__mutmut_2': xǁAdaptiveScoringOptimizerǁget_current_k1__mutmut_2, 
        'xǁAdaptiveScoringOptimizerǁget_current_k1__mutmut_3': xǁAdaptiveScoringOptimizerǁget_current_k1__mutmut_3
    }
    
    def get_current_k1(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAdaptiveScoringOptimizerǁget_current_k1__mutmut_orig"), object.__getattribute__(self, "xǁAdaptiveScoringOptimizerǁget_current_k1__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_current_k1.__signature__ = _mutmut_signature(xǁAdaptiveScoringOptimizerǁget_current_k1__mutmut_orig)
    xǁAdaptiveScoringOptimizerǁget_current_k1__mutmut_orig.__name__ = 'xǁAdaptiveScoringOptimizerǁget_current_k1'

    def xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_orig(self) -> float:
        """Get current accuracy from feedback"""
        if not self.feedback_history:
            return 0.0
        recent = self.feedback_history[-50:]
        return sum(1 for f in recent if f.is_correct) / len(recent)

    def xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_1(self) -> float:
        """Get current accuracy from feedback"""
        if self.feedback_history:
            return 0.0
        recent = self.feedback_history[-50:]
        return sum(1 for f in recent if f.is_correct) / len(recent)

    def xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_2(self) -> float:
        """Get current accuracy from feedback"""
        if not self.feedback_history:
            return 1.0
        recent = self.feedback_history[-50:]
        return sum(1 for f in recent if f.is_correct) / len(recent)

    def xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_3(self) -> float:
        """Get current accuracy from feedback"""
        if not self.feedback_history:
            return 0.0
        recent = None
        return sum(1 for f in recent if f.is_correct) / len(recent)

    def xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_4(self) -> float:
        """Get current accuracy from feedback"""
        if not self.feedback_history:
            return 0.0
        recent = self.feedback_history[+50:]
        return sum(1 for f in recent if f.is_correct) / len(recent)

    def xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_5(self) -> float:
        """Get current accuracy from feedback"""
        if not self.feedback_history:
            return 0.0
        recent = self.feedback_history[-51:]
        return sum(1 for f in recent if f.is_correct) / len(recent)

    def xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_6(self) -> float:
        """Get current accuracy from feedback"""
        if not self.feedback_history:
            return 0.0
        recent = self.feedback_history[-50:]
        return sum(1 for f in recent if f.is_correct) * len(recent)

    def xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_7(self) -> float:
        """Get current accuracy from feedback"""
        if not self.feedback_history:
            return 0.0
        recent = self.feedback_history[-50:]
        return sum(None) / len(recent)

    def xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_8(self) -> float:
        """Get current accuracy from feedback"""
        if not self.feedback_history:
            return 0.0
        recent = self.feedback_history[-50:]
        return sum(2 for f in recent if f.is_correct) / len(recent)
    
    xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_1': xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_1, 
        'xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_2': xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_2, 
        'xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_3': xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_3, 
        'xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_4': xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_4, 
        'xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_5': xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_5, 
        'xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_6': xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_6, 
        'xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_7': xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_7, 
        'xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_8': xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_8
    }
    
    def get_accuracy(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_orig"), object.__getattribute__(self, "xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_accuracy.__signature__ = _mutmut_signature(xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_orig)
    xǁAdaptiveScoringOptimizerǁget_accuracy__mutmut_orig.__name__ = 'xǁAdaptiveScoringOptimizerǁget_accuracy'

    def xǁAdaptiveScoringOptimizerǁreset_weights__mutmut_orig(self) -> None:
        """Reset weights to initial values"""
        self.weights = ScoringWeights().normalize()
        self.velocity = {k: 0.0 for k in self.velocity}
        self.k1_history = [0.40]

    def xǁAdaptiveScoringOptimizerǁreset_weights__mutmut_1(self) -> None:
        """Reset weights to initial values"""
        self.weights = None
        self.velocity = {k: 0.0 for k in self.velocity}
        self.k1_history = [0.40]

    def xǁAdaptiveScoringOptimizerǁreset_weights__mutmut_2(self) -> None:
        """Reset weights to initial values"""
        self.weights = ScoringWeights().normalize()
        self.velocity = None
        self.k1_history = [0.40]

    def xǁAdaptiveScoringOptimizerǁreset_weights__mutmut_3(self) -> None:
        """Reset weights to initial values"""
        self.weights = ScoringWeights().normalize()
        self.velocity = {k: 1.0 for k in self.velocity}
        self.k1_history = [0.40]

    def xǁAdaptiveScoringOptimizerǁreset_weights__mutmut_4(self) -> None:
        """Reset weights to initial values"""
        self.weights = ScoringWeights().normalize()
        self.velocity = {k: 0.0 for k in self.velocity}
        self.k1_history = None

    def xǁAdaptiveScoringOptimizerǁreset_weights__mutmut_5(self) -> None:
        """Reset weights to initial values"""
        self.weights = ScoringWeights().normalize()
        self.velocity = {k: 0.0 for k in self.velocity}
        self.k1_history = [1.4]
    
    xǁAdaptiveScoringOptimizerǁreset_weights__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAdaptiveScoringOptimizerǁreset_weights__mutmut_1': xǁAdaptiveScoringOptimizerǁreset_weights__mutmut_1, 
        'xǁAdaptiveScoringOptimizerǁreset_weights__mutmut_2': xǁAdaptiveScoringOptimizerǁreset_weights__mutmut_2, 
        'xǁAdaptiveScoringOptimizerǁreset_weights__mutmut_3': xǁAdaptiveScoringOptimizerǁreset_weights__mutmut_3, 
        'xǁAdaptiveScoringOptimizerǁreset_weights__mutmut_4': xǁAdaptiveScoringOptimizerǁreset_weights__mutmut_4, 
        'xǁAdaptiveScoringOptimizerǁreset_weights__mutmut_5': xǁAdaptiveScoringOptimizerǁreset_weights__mutmut_5
    }
    
    def reset_weights(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAdaptiveScoringOptimizerǁreset_weights__mutmut_orig"), object.__getattribute__(self, "xǁAdaptiveScoringOptimizerǁreset_weights__mutmut_mutants"), args, kwargs, self)
        return result 
    
    reset_weights.__signature__ = _mutmut_signature(xǁAdaptiveScoringOptimizerǁreset_weights__mutmut_orig)
    xǁAdaptiveScoringOptimizerǁreset_weights__mutmut_orig.__name__ = 'xǁAdaptiveScoringOptimizerǁreset_weights'


def x_create_scoring_function__mutmut_orig(
    optimizer: AdaptiveScoringOptimizer,
) -> Callable[[Dict[str, float]], float]:
    """
    Create a scoring function using the optimizer's current weights.

    Args:
        optimizer: AdaptiveScoringOptimizer instance

    Returns:
        Scoring function that takes feature dict and returns score
    """

    def scoring_fn(features: Dict[str, float]) -> float:
        return optimizer.compute_score(features)

    return scoring_fn


def x_create_scoring_function__mutmut_1(
    optimizer: AdaptiveScoringOptimizer,
) -> Callable[[Dict[str, float]], float]:
    """
    Create a scoring function using the optimizer's current weights.

    Args:
        optimizer: AdaptiveScoringOptimizer instance

    Returns:
        Scoring function that takes feature dict and returns score
    """

    def scoring_fn(features: Dict[str, float]) -> float:
        return optimizer.compute_score(None)

    return scoring_fn

x_create_scoring_function__mutmut_mutants : ClassVar[MutantDict] = {
'x_create_scoring_function__mutmut_1': x_create_scoring_function__mutmut_1
}

def create_scoring_function(*args, **kwargs):
    result = _mutmut_trampoline(x_create_scoring_function__mutmut_orig, x_create_scoring_function__mutmut_mutants, args, kwargs)
    return result 

create_scoring_function.__signature__ = _mutmut_signature(x_create_scoring_function__mutmut_orig)
x_create_scoring_function__mutmut_orig.__name__ = 'x_create_scoring_function'


# Backward-compatible alias for imports
AdaptiveScoringEngine = AdaptiveScoringOptimizer
