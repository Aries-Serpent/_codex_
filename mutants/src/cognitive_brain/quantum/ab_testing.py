"""
A/B Testing Framework for Quantum Features

Provides deterministic user assignment, variant selection, and statistical
significance calculation for validating quantum feature performance through
controlled experiments.
"""

import hashlib
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from cognitive_brain.models.quantum_metrics import (
    QuantumMetric,
    QuantumMetricRepository,
)
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


class Variant(Enum):
    """Experiment variant types."""

    CONTROL = "control"
    TREATMENT = "treatment"


@dataclass
class ExperimentConfig:
    """
    Configuration for an A/B experiment.

    Attributes:
        experiment_id: Unique identifier (e.g., 'EXP-1')
        name: Human-readable name
        feature: Quantum feature being tested
        sample_size: Target number of observations
        control_description: Description of control variant
        treatment_description: Description of treatment variant
        success_metric: Primary metric for evaluation
        metadata: Additional experiment metadata
    """

    experiment_id: str
    name: str
    feature: str
    sample_size: int
    control_description: str
    treatment_description: str
    success_metric: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration."""
        if self.sample_size < 10:
            raise ValueError("sample_size must be at least 10")
        if not self.experiment_id:
            raise ValueError("experiment_id is required")


@dataclass
class ExperimentResult:
    """
    Results of an A/B experiment.

    Attributes:
        experiment_id: Experiment identifier
        control_mean: Mean of control variant
        treatment_mean: Mean of treatment variant
        control_std: Standard deviation of control
        treatment_std: Standard deviation of treatment
        control_n: Sample size of control
        treatment_n: Sample size of treatment
        p_value: Statistical significance (p-value)
        confidence_interval: 95% CI for difference
        is_significant: Whether result is statistically significant
        effect_size: Relative improvement (treatment vs control)
    """

    experiment_id: str
    control_mean: float
    treatment_mean: float
    control_std: float
    treatment_std: float
    control_n: int
    treatment_n: int
    p_value: float
    confidence_interval: Tuple[float, float]
    is_significant: bool
    effect_size: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "experiment_id": self.experiment_id,
            "control_mean": self.control_mean,
            "treatment_mean": self.treatment_mean,
            "control_std": self.control_std,
            "treatment_std": self.treatment_std,
            "control_n": self.control_n,
            "treatment_n": self.treatment_n,
            "p_value": self.p_value,
            "confidence_interval": self.confidence_interval,
            "is_significant": self.is_significant,
            "effect_size": self.effect_size,
        }


class ABTestFramework:
    """
    A/B testing framework for quantum feature validation.

    Provides deterministic user assignment, variant tracking, and statistical
    analysis for controlled experiments comparing quantum-enhanced features
    against classical baselines.

    Example:
        >>> framework = ABTestFramework(repository)
        >>> config = ExperimentConfig(
        ...     experiment_id='EXP-1',
        ...     name='Superposition Test',
        ...     feature='superposition',
        ...     sample_size=100,
        ...     control_description='Classical decision',
        ...     treatment_description='Quantum superposition',
        ...     success_metric='accuracy'
        ... )
        >>> framework.create_experiment(config)
        >>>
        >>> variant = framework.assign_variant('EXP-1', 'user-123')
        >>> # Record metrics for each variant
        >>> framework.record_metric('EXP-1', 'user-123', 0.95)
        >>>
        >>> # Analyze results
        >>> result = framework.analyze_experiment('EXP-1')
        >>> print(f"Significant: {result.is_significant}, p={result.p_value:.3f}")
    """

    def xǁABTestFrameworkǁ__init____mutmut_orig(self, repository: QuantumMetricRepository):
        """
        Initialize A/B testing framework.

        Args:
            repository: Database repository for metrics
        """
        self.repository = repository
        self._experiments: Dict[str, ExperimentConfig] = {}
        self._assignments: Dict[
            Tuple[str, str], Variant
        ] = {}  # (exp_id, user_id) -> variant

    def xǁABTestFrameworkǁ__init____mutmut_1(self, repository: QuantumMetricRepository):
        """
        Initialize A/B testing framework.

        Args:
            repository: Database repository for metrics
        """
        self.repository = None
        self._experiments: Dict[str, ExperimentConfig] = {}
        self._assignments: Dict[
            Tuple[str, str], Variant
        ] = {}  # (exp_id, user_id) -> variant

    def xǁABTestFrameworkǁ__init____mutmut_2(self, repository: QuantumMetricRepository):
        """
        Initialize A/B testing framework.

        Args:
            repository: Database repository for metrics
        """
        self.repository = repository
        self._experiments: Dict[str, ExperimentConfig] = None
        self._assignments: Dict[
            Tuple[str, str], Variant
        ] = {}  # (exp_id, user_id) -> variant

    def xǁABTestFrameworkǁ__init____mutmut_3(self, repository: QuantumMetricRepository):
        """
        Initialize A/B testing framework.

        Args:
            repository: Database repository for metrics
        """
        self.repository = repository
        self._experiments: Dict[str, ExperimentConfig] = {}
        self._assignments: Dict[
            Tuple[str, str], Variant
        ] = None  # (exp_id, user_id) -> variant
    
    xǁABTestFrameworkǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁABTestFrameworkǁ__init____mutmut_1': xǁABTestFrameworkǁ__init____mutmut_1, 
        'xǁABTestFrameworkǁ__init____mutmut_2': xǁABTestFrameworkǁ__init____mutmut_2, 
        'xǁABTestFrameworkǁ__init____mutmut_3': xǁABTestFrameworkǁ__init____mutmut_3
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁABTestFrameworkǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁABTestFrameworkǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁABTestFrameworkǁ__init____mutmut_orig)
    xǁABTestFrameworkǁ__init____mutmut_orig.__name__ = 'xǁABTestFrameworkǁ__init__'

    def xǁABTestFrameworkǁcreate_experiment__mutmut_orig(self, config: ExperimentConfig) -> None:
        """
        Create a new A/B experiment.

        Args:
            config: Experiment configuration

        Raises:
            ValueError: If experiment already exists
        """
        if config.experiment_id in self._experiments:
            raise ValueError(f"Experiment {config.experiment_id} already exists")

        self._experiments[config.experiment_id] = config

    def xǁABTestFrameworkǁcreate_experiment__mutmut_1(self, config: ExperimentConfig) -> None:
        """
        Create a new A/B experiment.

        Args:
            config: Experiment configuration

        Raises:
            ValueError: If experiment already exists
        """
        if config.experiment_id not in self._experiments:
            raise ValueError(f"Experiment {config.experiment_id} already exists")

        self._experiments[config.experiment_id] = config

    def xǁABTestFrameworkǁcreate_experiment__mutmut_2(self, config: ExperimentConfig) -> None:
        """
        Create a new A/B experiment.

        Args:
            config: Experiment configuration

        Raises:
            ValueError: If experiment already exists
        """
        if config.experiment_id in self._experiments:
            raise ValueError(None)

        self._experiments[config.experiment_id] = config

    def xǁABTestFrameworkǁcreate_experiment__mutmut_3(self, config: ExperimentConfig) -> None:
        """
        Create a new A/B experiment.

        Args:
            config: Experiment configuration

        Raises:
            ValueError: If experiment already exists
        """
        if config.experiment_id in self._experiments:
            raise ValueError(f"Experiment {config.experiment_id} already exists")

        self._experiments[config.experiment_id] = None
    
    xǁABTestFrameworkǁcreate_experiment__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁABTestFrameworkǁcreate_experiment__mutmut_1': xǁABTestFrameworkǁcreate_experiment__mutmut_1, 
        'xǁABTestFrameworkǁcreate_experiment__mutmut_2': xǁABTestFrameworkǁcreate_experiment__mutmut_2, 
        'xǁABTestFrameworkǁcreate_experiment__mutmut_3': xǁABTestFrameworkǁcreate_experiment__mutmut_3
    }
    
    def create_experiment(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁABTestFrameworkǁcreate_experiment__mutmut_orig"), object.__getattribute__(self, "xǁABTestFrameworkǁcreate_experiment__mutmut_mutants"), args, kwargs, self)
        return result 
    
    create_experiment.__signature__ = _mutmut_signature(xǁABTestFrameworkǁcreate_experiment__mutmut_orig)
    xǁABTestFrameworkǁcreate_experiment__mutmut_orig.__name__ = 'xǁABTestFrameworkǁcreate_experiment'

    def xǁABTestFrameworkǁget_experiment__mutmut_orig(self, experiment_id: str) -> Optional[ExperimentConfig]:
        """
        Get experiment configuration.

        Args:
            experiment_id: Experiment identifier

        Returns:
            ExperimentConfig if found, None otherwise
        """
        return self._experiments.get(experiment_id)

    def xǁABTestFrameworkǁget_experiment__mutmut_1(self, experiment_id: str) -> Optional[ExperimentConfig]:
        """
        Get experiment configuration.

        Args:
            experiment_id: Experiment identifier

        Returns:
            ExperimentConfig if found, None otherwise
        """
        return self._experiments.get(None)
    
    xǁABTestFrameworkǁget_experiment__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁABTestFrameworkǁget_experiment__mutmut_1': xǁABTestFrameworkǁget_experiment__mutmut_1
    }
    
    def get_experiment(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁABTestFrameworkǁget_experiment__mutmut_orig"), object.__getattribute__(self, "xǁABTestFrameworkǁget_experiment__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_experiment.__signature__ = _mutmut_signature(xǁABTestFrameworkǁget_experiment__mutmut_orig)
    xǁABTestFrameworkǁget_experiment__mutmut_orig.__name__ = 'xǁABTestFrameworkǁget_experiment'

    def xǁABTestFrameworkǁassign_variant__mutmut_orig(self, experiment_id: str, user_id: str) -> Variant:
        """
        Assign user to a variant deterministically.

        Uses hash-based assignment to ensure:
        - Same user always gets same variant
        - Approximately 50/50 split across population

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant (CONTROL or TREATMENT)

        Raises:
            ValueError: If experiment doesn't exist
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Check if already assigned
        key = (experiment_id, user_id)
        if key in self._assignments:
            return self._assignments[key]

        # Deterministic hash-based assignment
        hash_input = f"{experiment_id}:{user_id}".encode("utf-8")
        hash_value = hashlib.sha256(hash_input).hexdigest()
        hash_int = int(hash_value, 16)

        # 50/50 split based on hash parity
        variant = Variant.TREATMENT if hash_int % 2 == 0 else Variant.CONTROL

        # Cache assignment
        self._assignments[key] = variant

        return variant

    def xǁABTestFrameworkǁassign_variant__mutmut_1(self, experiment_id: str, user_id: str) -> Variant:
        """
        Assign user to a variant deterministically.

        Uses hash-based assignment to ensure:
        - Same user always gets same variant
        - Approximately 50/50 split across population

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant (CONTROL or TREATMENT)

        Raises:
            ValueError: If experiment doesn't exist
        """
        if experiment_id in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Check if already assigned
        key = (experiment_id, user_id)
        if key in self._assignments:
            return self._assignments[key]

        # Deterministic hash-based assignment
        hash_input = f"{experiment_id}:{user_id}".encode("utf-8")
        hash_value = hashlib.sha256(hash_input).hexdigest()
        hash_int = int(hash_value, 16)

        # 50/50 split based on hash parity
        variant = Variant.TREATMENT if hash_int % 2 == 0 else Variant.CONTROL

        # Cache assignment
        self._assignments[key] = variant

        return variant

    def xǁABTestFrameworkǁassign_variant__mutmut_2(self, experiment_id: str, user_id: str) -> Variant:
        """
        Assign user to a variant deterministically.

        Uses hash-based assignment to ensure:
        - Same user always gets same variant
        - Approximately 50/50 split across population

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant (CONTROL or TREATMENT)

        Raises:
            ValueError: If experiment doesn't exist
        """
        if experiment_id not in self._experiments:
            raise ValueError(None)

        # Check if already assigned
        key = (experiment_id, user_id)
        if key in self._assignments:
            return self._assignments[key]

        # Deterministic hash-based assignment
        hash_input = f"{experiment_id}:{user_id}".encode("utf-8")
        hash_value = hashlib.sha256(hash_input).hexdigest()
        hash_int = int(hash_value, 16)

        # 50/50 split based on hash parity
        variant = Variant.TREATMENT if hash_int % 2 == 0 else Variant.CONTROL

        # Cache assignment
        self._assignments[key] = variant

        return variant

    def xǁABTestFrameworkǁassign_variant__mutmut_3(self, experiment_id: str, user_id: str) -> Variant:
        """
        Assign user to a variant deterministically.

        Uses hash-based assignment to ensure:
        - Same user always gets same variant
        - Approximately 50/50 split across population

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant (CONTROL or TREATMENT)

        Raises:
            ValueError: If experiment doesn't exist
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Check if already assigned
        key = None
        if key in self._assignments:
            return self._assignments[key]

        # Deterministic hash-based assignment
        hash_input = f"{experiment_id}:{user_id}".encode("utf-8")
        hash_value = hashlib.sha256(hash_input).hexdigest()
        hash_int = int(hash_value, 16)

        # 50/50 split based on hash parity
        variant = Variant.TREATMENT if hash_int % 2 == 0 else Variant.CONTROL

        # Cache assignment
        self._assignments[key] = variant

        return variant

    def xǁABTestFrameworkǁassign_variant__mutmut_4(self, experiment_id: str, user_id: str) -> Variant:
        """
        Assign user to a variant deterministically.

        Uses hash-based assignment to ensure:
        - Same user always gets same variant
        - Approximately 50/50 split across population

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant (CONTROL or TREATMENT)

        Raises:
            ValueError: If experiment doesn't exist
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Check if already assigned
        key = (experiment_id, user_id)
        if key not in self._assignments:
            return self._assignments[key]

        # Deterministic hash-based assignment
        hash_input = f"{experiment_id}:{user_id}".encode("utf-8")
        hash_value = hashlib.sha256(hash_input).hexdigest()
        hash_int = int(hash_value, 16)

        # 50/50 split based on hash parity
        variant = Variant.TREATMENT if hash_int % 2 == 0 else Variant.CONTROL

        # Cache assignment
        self._assignments[key] = variant

        return variant

    def xǁABTestFrameworkǁassign_variant__mutmut_5(self, experiment_id: str, user_id: str) -> Variant:
        """
        Assign user to a variant deterministically.

        Uses hash-based assignment to ensure:
        - Same user always gets same variant
        - Approximately 50/50 split across population

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant (CONTROL or TREATMENT)

        Raises:
            ValueError: If experiment doesn't exist
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Check if already assigned
        key = (experiment_id, user_id)
        if key in self._assignments:
            return self._assignments[key]

        # Deterministic hash-based assignment
        hash_input = None
        hash_value = hashlib.sha256(hash_input).hexdigest()
        hash_int = int(hash_value, 16)

        # 50/50 split based on hash parity
        variant = Variant.TREATMENT if hash_int % 2 == 0 else Variant.CONTROL

        # Cache assignment
        self._assignments[key] = variant

        return variant

    def xǁABTestFrameworkǁassign_variant__mutmut_6(self, experiment_id: str, user_id: str) -> Variant:
        """
        Assign user to a variant deterministically.

        Uses hash-based assignment to ensure:
        - Same user always gets same variant
        - Approximately 50/50 split across population

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant (CONTROL or TREATMENT)

        Raises:
            ValueError: If experiment doesn't exist
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Check if already assigned
        key = (experiment_id, user_id)
        if key in self._assignments:
            return self._assignments[key]

        # Deterministic hash-based assignment
        hash_input = f"{experiment_id}:{user_id}".encode(None)
        hash_value = hashlib.sha256(hash_input).hexdigest()
        hash_int = int(hash_value, 16)

        # 50/50 split based on hash parity
        variant = Variant.TREATMENT if hash_int % 2 == 0 else Variant.CONTROL

        # Cache assignment
        self._assignments[key] = variant

        return variant

    def xǁABTestFrameworkǁassign_variant__mutmut_7(self, experiment_id: str, user_id: str) -> Variant:
        """
        Assign user to a variant deterministically.

        Uses hash-based assignment to ensure:
        - Same user always gets same variant
        - Approximately 50/50 split across population

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant (CONTROL or TREATMENT)

        Raises:
            ValueError: If experiment doesn't exist
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Check if already assigned
        key = (experiment_id, user_id)
        if key in self._assignments:
            return self._assignments[key]

        # Deterministic hash-based assignment
        hash_input = f"{experiment_id}:{user_id}".encode("XXutf-8XX")
        hash_value = hashlib.sha256(hash_input).hexdigest()
        hash_int = int(hash_value, 16)

        # 50/50 split based on hash parity
        variant = Variant.TREATMENT if hash_int % 2 == 0 else Variant.CONTROL

        # Cache assignment
        self._assignments[key] = variant

        return variant

    def xǁABTestFrameworkǁassign_variant__mutmut_8(self, experiment_id: str, user_id: str) -> Variant:
        """
        Assign user to a variant deterministically.

        Uses hash-based assignment to ensure:
        - Same user always gets same variant
        - Approximately 50/50 split across population

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant (CONTROL or TREATMENT)

        Raises:
            ValueError: If experiment doesn't exist
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Check if already assigned
        key = (experiment_id, user_id)
        if key in self._assignments:
            return self._assignments[key]

        # Deterministic hash-based assignment
        hash_input = f"{experiment_id}:{user_id}".encode("UTF-8")
        hash_value = hashlib.sha256(hash_input).hexdigest()
        hash_int = int(hash_value, 16)

        # 50/50 split based on hash parity
        variant = Variant.TREATMENT if hash_int % 2 == 0 else Variant.CONTROL

        # Cache assignment
        self._assignments[key] = variant

        return variant

    def xǁABTestFrameworkǁassign_variant__mutmut_9(self, experiment_id: str, user_id: str) -> Variant:
        """
        Assign user to a variant deterministically.

        Uses hash-based assignment to ensure:
        - Same user always gets same variant
        - Approximately 50/50 split across population

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant (CONTROL or TREATMENT)

        Raises:
            ValueError: If experiment doesn't exist
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Check if already assigned
        key = (experiment_id, user_id)
        if key in self._assignments:
            return self._assignments[key]

        # Deterministic hash-based assignment
        hash_input = f"{experiment_id}:{user_id}".encode("utf-8")
        hash_value = None
        hash_int = int(hash_value, 16)

        # 50/50 split based on hash parity
        variant = Variant.TREATMENT if hash_int % 2 == 0 else Variant.CONTROL

        # Cache assignment
        self._assignments[key] = variant

        return variant

    def xǁABTestFrameworkǁassign_variant__mutmut_10(self, experiment_id: str, user_id: str) -> Variant:
        """
        Assign user to a variant deterministically.

        Uses hash-based assignment to ensure:
        - Same user always gets same variant
        - Approximately 50/50 split across population

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant (CONTROL or TREATMENT)

        Raises:
            ValueError: If experiment doesn't exist
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Check if already assigned
        key = (experiment_id, user_id)
        if key in self._assignments:
            return self._assignments[key]

        # Deterministic hash-based assignment
        hash_input = f"{experiment_id}:{user_id}".encode("utf-8")
        hash_value = hashlib.sha256(None).hexdigest()
        hash_int = int(hash_value, 16)

        # 50/50 split based on hash parity
        variant = Variant.TREATMENT if hash_int % 2 == 0 else Variant.CONTROL

        # Cache assignment
        self._assignments[key] = variant

        return variant

    def xǁABTestFrameworkǁassign_variant__mutmut_11(self, experiment_id: str, user_id: str) -> Variant:
        """
        Assign user to a variant deterministically.

        Uses hash-based assignment to ensure:
        - Same user always gets same variant
        - Approximately 50/50 split across population

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant (CONTROL or TREATMENT)

        Raises:
            ValueError: If experiment doesn't exist
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Check if already assigned
        key = (experiment_id, user_id)
        if key in self._assignments:
            return self._assignments[key]

        # Deterministic hash-based assignment
        hash_input = f"{experiment_id}:{user_id}".encode("utf-8")
        hash_value = hashlib.sha256(hash_input).hexdigest()
        hash_int = None

        # 50/50 split based on hash parity
        variant = Variant.TREATMENT if hash_int % 2 == 0 else Variant.CONTROL

        # Cache assignment
        self._assignments[key] = variant

        return variant

    def xǁABTestFrameworkǁassign_variant__mutmut_12(self, experiment_id: str, user_id: str) -> Variant:
        """
        Assign user to a variant deterministically.

        Uses hash-based assignment to ensure:
        - Same user always gets same variant
        - Approximately 50/50 split across population

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant (CONTROL or TREATMENT)

        Raises:
            ValueError: If experiment doesn't exist
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Check if already assigned
        key = (experiment_id, user_id)
        if key in self._assignments:
            return self._assignments[key]

        # Deterministic hash-based assignment
        hash_input = f"{experiment_id}:{user_id}".encode("utf-8")
        hash_value = hashlib.sha256(hash_input).hexdigest()
        hash_int = int(None, 16)

        # 50/50 split based on hash parity
        variant = Variant.TREATMENT if hash_int % 2 == 0 else Variant.CONTROL

        # Cache assignment
        self._assignments[key] = variant

        return variant

    def xǁABTestFrameworkǁassign_variant__mutmut_13(self, experiment_id: str, user_id: str) -> Variant:
        """
        Assign user to a variant deterministically.

        Uses hash-based assignment to ensure:
        - Same user always gets same variant
        - Approximately 50/50 split across population

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant (CONTROL or TREATMENT)

        Raises:
            ValueError: If experiment doesn't exist
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Check if already assigned
        key = (experiment_id, user_id)
        if key in self._assignments:
            return self._assignments[key]

        # Deterministic hash-based assignment
        hash_input = f"{experiment_id}:{user_id}".encode("utf-8")
        hash_value = hashlib.sha256(hash_input).hexdigest()
        hash_int = int(hash_value, None)

        # 50/50 split based on hash parity
        variant = Variant.TREATMENT if hash_int % 2 == 0 else Variant.CONTROL

        # Cache assignment
        self._assignments[key] = variant

        return variant

    def xǁABTestFrameworkǁassign_variant__mutmut_14(self, experiment_id: str, user_id: str) -> Variant:
        """
        Assign user to a variant deterministically.

        Uses hash-based assignment to ensure:
        - Same user always gets same variant
        - Approximately 50/50 split across population

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant (CONTROL or TREATMENT)

        Raises:
            ValueError: If experiment doesn't exist
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Check if already assigned
        key = (experiment_id, user_id)
        if key in self._assignments:
            return self._assignments[key]

        # Deterministic hash-based assignment
        hash_input = f"{experiment_id}:{user_id}".encode("utf-8")
        hash_value = hashlib.sha256(hash_input).hexdigest()
        hash_int = int(16)

        # 50/50 split based on hash parity
        variant = Variant.TREATMENT if hash_int % 2 == 0 else Variant.CONTROL

        # Cache assignment
        self._assignments[key] = variant

        return variant

    def xǁABTestFrameworkǁassign_variant__mutmut_15(self, experiment_id: str, user_id: str) -> Variant:
        """
        Assign user to a variant deterministically.

        Uses hash-based assignment to ensure:
        - Same user always gets same variant
        - Approximately 50/50 split across population

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant (CONTROL or TREATMENT)

        Raises:
            ValueError: If experiment doesn't exist
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Check if already assigned
        key = (experiment_id, user_id)
        if key in self._assignments:
            return self._assignments[key]

        # Deterministic hash-based assignment
        hash_input = f"{experiment_id}:{user_id}".encode("utf-8")
        hash_value = hashlib.sha256(hash_input).hexdigest()
        hash_int = int(hash_value, )

        # 50/50 split based on hash parity
        variant = Variant.TREATMENT if hash_int % 2 == 0 else Variant.CONTROL

        # Cache assignment
        self._assignments[key] = variant

        return variant

    def xǁABTestFrameworkǁassign_variant__mutmut_16(self, experiment_id: str, user_id: str) -> Variant:
        """
        Assign user to a variant deterministically.

        Uses hash-based assignment to ensure:
        - Same user always gets same variant
        - Approximately 50/50 split across population

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant (CONTROL or TREATMENT)

        Raises:
            ValueError: If experiment doesn't exist
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Check if already assigned
        key = (experiment_id, user_id)
        if key in self._assignments:
            return self._assignments[key]

        # Deterministic hash-based assignment
        hash_input = f"{experiment_id}:{user_id}".encode("utf-8")
        hash_value = hashlib.sha256(hash_input).hexdigest()
        hash_int = int(hash_value, 17)

        # 50/50 split based on hash parity
        variant = Variant.TREATMENT if hash_int % 2 == 0 else Variant.CONTROL

        # Cache assignment
        self._assignments[key] = variant

        return variant

    def xǁABTestFrameworkǁassign_variant__mutmut_17(self, experiment_id: str, user_id: str) -> Variant:
        """
        Assign user to a variant deterministically.

        Uses hash-based assignment to ensure:
        - Same user always gets same variant
        - Approximately 50/50 split across population

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant (CONTROL or TREATMENT)

        Raises:
            ValueError: If experiment doesn't exist
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Check if already assigned
        key = (experiment_id, user_id)
        if key in self._assignments:
            return self._assignments[key]

        # Deterministic hash-based assignment
        hash_input = f"{experiment_id}:{user_id}".encode("utf-8")
        hash_value = hashlib.sha256(hash_input).hexdigest()
        hash_int = int(hash_value, 16)

        # 50/50 split based on hash parity
        variant = None

        # Cache assignment
        self._assignments[key] = variant

        return variant

    def xǁABTestFrameworkǁassign_variant__mutmut_18(self, experiment_id: str, user_id: str) -> Variant:
        """
        Assign user to a variant deterministically.

        Uses hash-based assignment to ensure:
        - Same user always gets same variant
        - Approximately 50/50 split across population

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant (CONTROL or TREATMENT)

        Raises:
            ValueError: If experiment doesn't exist
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Check if already assigned
        key = (experiment_id, user_id)
        if key in self._assignments:
            return self._assignments[key]

        # Deterministic hash-based assignment
        hash_input = f"{experiment_id}:{user_id}".encode("utf-8")
        hash_value = hashlib.sha256(hash_input).hexdigest()
        hash_int = int(hash_value, 16)

        # 50/50 split based on hash parity
        variant = Variant.TREATMENT if hash_int / 2 == 0 else Variant.CONTROL

        # Cache assignment
        self._assignments[key] = variant

        return variant

    def xǁABTestFrameworkǁassign_variant__mutmut_19(self, experiment_id: str, user_id: str) -> Variant:
        """
        Assign user to a variant deterministically.

        Uses hash-based assignment to ensure:
        - Same user always gets same variant
        - Approximately 50/50 split across population

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant (CONTROL or TREATMENT)

        Raises:
            ValueError: If experiment doesn't exist
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Check if already assigned
        key = (experiment_id, user_id)
        if key in self._assignments:
            return self._assignments[key]

        # Deterministic hash-based assignment
        hash_input = f"{experiment_id}:{user_id}".encode("utf-8")
        hash_value = hashlib.sha256(hash_input).hexdigest()
        hash_int = int(hash_value, 16)

        # 50/50 split based on hash parity
        variant = Variant.TREATMENT if hash_int % 3 == 0 else Variant.CONTROL

        # Cache assignment
        self._assignments[key] = variant

        return variant

    def xǁABTestFrameworkǁassign_variant__mutmut_20(self, experiment_id: str, user_id: str) -> Variant:
        """
        Assign user to a variant deterministically.

        Uses hash-based assignment to ensure:
        - Same user always gets same variant
        - Approximately 50/50 split across population

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant (CONTROL or TREATMENT)

        Raises:
            ValueError: If experiment doesn't exist
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Check if already assigned
        key = (experiment_id, user_id)
        if key in self._assignments:
            return self._assignments[key]

        # Deterministic hash-based assignment
        hash_input = f"{experiment_id}:{user_id}".encode("utf-8")
        hash_value = hashlib.sha256(hash_input).hexdigest()
        hash_int = int(hash_value, 16)

        # 50/50 split based on hash parity
        variant = Variant.TREATMENT if hash_int % 2 != 0 else Variant.CONTROL

        # Cache assignment
        self._assignments[key] = variant

        return variant

    def xǁABTestFrameworkǁassign_variant__mutmut_21(self, experiment_id: str, user_id: str) -> Variant:
        """
        Assign user to a variant deterministically.

        Uses hash-based assignment to ensure:
        - Same user always gets same variant
        - Approximately 50/50 split across population

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant (CONTROL or TREATMENT)

        Raises:
            ValueError: If experiment doesn't exist
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Check if already assigned
        key = (experiment_id, user_id)
        if key in self._assignments:
            return self._assignments[key]

        # Deterministic hash-based assignment
        hash_input = f"{experiment_id}:{user_id}".encode("utf-8")
        hash_value = hashlib.sha256(hash_input).hexdigest()
        hash_int = int(hash_value, 16)

        # 50/50 split based on hash parity
        variant = Variant.TREATMENT if hash_int % 2 == 1 else Variant.CONTROL

        # Cache assignment
        self._assignments[key] = variant

        return variant

    def xǁABTestFrameworkǁassign_variant__mutmut_22(self, experiment_id: str, user_id: str) -> Variant:
        """
        Assign user to a variant deterministically.

        Uses hash-based assignment to ensure:
        - Same user always gets same variant
        - Approximately 50/50 split across population

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant (CONTROL or TREATMENT)

        Raises:
            ValueError: If experiment doesn't exist
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Check if already assigned
        key = (experiment_id, user_id)
        if key in self._assignments:
            return self._assignments[key]

        # Deterministic hash-based assignment
        hash_input = f"{experiment_id}:{user_id}".encode("utf-8")
        hash_value = hashlib.sha256(hash_input).hexdigest()
        hash_int = int(hash_value, 16)

        # 50/50 split based on hash parity
        variant = Variant.TREATMENT if hash_int % 2 == 0 else Variant.CONTROL

        # Cache assignment
        self._assignments[key] = None

        return variant
    
    xǁABTestFrameworkǁassign_variant__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁABTestFrameworkǁassign_variant__mutmut_1': xǁABTestFrameworkǁassign_variant__mutmut_1, 
        'xǁABTestFrameworkǁassign_variant__mutmut_2': xǁABTestFrameworkǁassign_variant__mutmut_2, 
        'xǁABTestFrameworkǁassign_variant__mutmut_3': xǁABTestFrameworkǁassign_variant__mutmut_3, 
        'xǁABTestFrameworkǁassign_variant__mutmut_4': xǁABTestFrameworkǁassign_variant__mutmut_4, 
        'xǁABTestFrameworkǁassign_variant__mutmut_5': xǁABTestFrameworkǁassign_variant__mutmut_5, 
        'xǁABTestFrameworkǁassign_variant__mutmut_6': xǁABTestFrameworkǁassign_variant__mutmut_6, 
        'xǁABTestFrameworkǁassign_variant__mutmut_7': xǁABTestFrameworkǁassign_variant__mutmut_7, 
        'xǁABTestFrameworkǁassign_variant__mutmut_8': xǁABTestFrameworkǁassign_variant__mutmut_8, 
        'xǁABTestFrameworkǁassign_variant__mutmut_9': xǁABTestFrameworkǁassign_variant__mutmut_9, 
        'xǁABTestFrameworkǁassign_variant__mutmut_10': xǁABTestFrameworkǁassign_variant__mutmut_10, 
        'xǁABTestFrameworkǁassign_variant__mutmut_11': xǁABTestFrameworkǁassign_variant__mutmut_11, 
        'xǁABTestFrameworkǁassign_variant__mutmut_12': xǁABTestFrameworkǁassign_variant__mutmut_12, 
        'xǁABTestFrameworkǁassign_variant__mutmut_13': xǁABTestFrameworkǁassign_variant__mutmut_13, 
        'xǁABTestFrameworkǁassign_variant__mutmut_14': xǁABTestFrameworkǁassign_variant__mutmut_14, 
        'xǁABTestFrameworkǁassign_variant__mutmut_15': xǁABTestFrameworkǁassign_variant__mutmut_15, 
        'xǁABTestFrameworkǁassign_variant__mutmut_16': xǁABTestFrameworkǁassign_variant__mutmut_16, 
        'xǁABTestFrameworkǁassign_variant__mutmut_17': xǁABTestFrameworkǁassign_variant__mutmut_17, 
        'xǁABTestFrameworkǁassign_variant__mutmut_18': xǁABTestFrameworkǁassign_variant__mutmut_18, 
        'xǁABTestFrameworkǁassign_variant__mutmut_19': xǁABTestFrameworkǁassign_variant__mutmut_19, 
        'xǁABTestFrameworkǁassign_variant__mutmut_20': xǁABTestFrameworkǁassign_variant__mutmut_20, 
        'xǁABTestFrameworkǁassign_variant__mutmut_21': xǁABTestFrameworkǁassign_variant__mutmut_21, 
        'xǁABTestFrameworkǁassign_variant__mutmut_22': xǁABTestFrameworkǁassign_variant__mutmut_22
    }
    
    def assign_variant(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁABTestFrameworkǁassign_variant__mutmut_orig"), object.__getattribute__(self, "xǁABTestFrameworkǁassign_variant__mutmut_mutants"), args, kwargs, self)
        return result 
    
    assign_variant.__signature__ = _mutmut_signature(xǁABTestFrameworkǁassign_variant__mutmut_orig)
    xǁABTestFrameworkǁassign_variant__mutmut_orig.__name__ = 'xǁABTestFrameworkǁassign_variant'

    def xǁABTestFrameworkǁget_assignment__mutmut_orig(self, experiment_id: str, user_id: str) -> Optional[Variant]:
        """
        Get existing variant assignment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant if exists, None otherwise
        """
        return self._assignments.get((experiment_id, user_id))

    def xǁABTestFrameworkǁget_assignment__mutmut_1(self, experiment_id: str, user_id: str) -> Optional[Variant]:
        """
        Get existing variant assignment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant if exists, None otherwise
        """
        return self._assignments.get(None)
    
    xǁABTestFrameworkǁget_assignment__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁABTestFrameworkǁget_assignment__mutmut_1': xǁABTestFrameworkǁget_assignment__mutmut_1
    }
    
    def get_assignment(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁABTestFrameworkǁget_assignment__mutmut_orig"), object.__getattribute__(self, "xǁABTestFrameworkǁget_assignment__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_assignment.__signature__ = _mutmut_signature(xǁABTestFrameworkǁget_assignment__mutmut_orig)
    xǁABTestFrameworkǁget_assignment__mutmut_orig.__name__ = 'xǁABTestFrameworkǁget_assignment'

    def xǁABTestFrameworkǁrecord_metric__mutmut_orig(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_1(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = None
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_2(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(None)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_3(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_4(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(None)

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_5(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = None
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_6(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(None, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_7(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, None)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_8(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_9(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, )
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_10(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_11(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = None

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_12(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(None, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_13(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, None)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_14(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_15(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, )

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_16(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = None
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_17(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata and {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_18(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            None
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_19(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "XXexperiment_idXX": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_20(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "EXPERIMENT_ID": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_21(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "XXuser_idXX": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_22(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "USER_ID": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_23(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "XXvariantXX": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_24(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "VARIANT": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_25(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = None

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_26(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=None,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_27(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=None,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_28(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=None,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_29(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=None,
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_30(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=None,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_31(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_32(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_33(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_34(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            metadata=full_metadata,
        )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_35(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            )

        return self.repository.create(metric)

    def xǁABTestFrameworkǁrecord_metric__mutmut_36(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuantumMetric:
        """
        Record metric for a user in an experiment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            metric_value: Metric value to record
            metadata: Optional metadata

        Returns:
            Created QuantumMetric instance

        Raises:
            ValueError: If experiment doesn't exist or user not assigned
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        variant = self.get_assignment(experiment_id, user_id)
        if not variant:
            variant = self.assign_variant(experiment_id, user_id)

        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata.update(
            {
                "experiment_id": experiment_id,
                "user_id": user_id,
                "variant": variant.value,
            }
        )

        # Record metric
        metric = QuantumMetric(
            feature=config.feature,
            metric_name=config.success_metric,
            metric_value=metric_value,
            agent_id=f"exp-{experiment_id}",
            metadata=full_metadata,
        )

        return self.repository.create(None)
    
    xǁABTestFrameworkǁrecord_metric__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁABTestFrameworkǁrecord_metric__mutmut_1': xǁABTestFrameworkǁrecord_metric__mutmut_1, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_2': xǁABTestFrameworkǁrecord_metric__mutmut_2, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_3': xǁABTestFrameworkǁrecord_metric__mutmut_3, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_4': xǁABTestFrameworkǁrecord_metric__mutmut_4, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_5': xǁABTestFrameworkǁrecord_metric__mutmut_5, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_6': xǁABTestFrameworkǁrecord_metric__mutmut_6, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_7': xǁABTestFrameworkǁrecord_metric__mutmut_7, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_8': xǁABTestFrameworkǁrecord_metric__mutmut_8, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_9': xǁABTestFrameworkǁrecord_metric__mutmut_9, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_10': xǁABTestFrameworkǁrecord_metric__mutmut_10, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_11': xǁABTestFrameworkǁrecord_metric__mutmut_11, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_12': xǁABTestFrameworkǁrecord_metric__mutmut_12, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_13': xǁABTestFrameworkǁrecord_metric__mutmut_13, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_14': xǁABTestFrameworkǁrecord_metric__mutmut_14, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_15': xǁABTestFrameworkǁrecord_metric__mutmut_15, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_16': xǁABTestFrameworkǁrecord_metric__mutmut_16, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_17': xǁABTestFrameworkǁrecord_metric__mutmut_17, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_18': xǁABTestFrameworkǁrecord_metric__mutmut_18, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_19': xǁABTestFrameworkǁrecord_metric__mutmut_19, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_20': xǁABTestFrameworkǁrecord_metric__mutmut_20, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_21': xǁABTestFrameworkǁrecord_metric__mutmut_21, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_22': xǁABTestFrameworkǁrecord_metric__mutmut_22, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_23': xǁABTestFrameworkǁrecord_metric__mutmut_23, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_24': xǁABTestFrameworkǁrecord_metric__mutmut_24, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_25': xǁABTestFrameworkǁrecord_metric__mutmut_25, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_26': xǁABTestFrameworkǁrecord_metric__mutmut_26, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_27': xǁABTestFrameworkǁrecord_metric__mutmut_27, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_28': xǁABTestFrameworkǁrecord_metric__mutmut_28, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_29': xǁABTestFrameworkǁrecord_metric__mutmut_29, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_30': xǁABTestFrameworkǁrecord_metric__mutmut_30, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_31': xǁABTestFrameworkǁrecord_metric__mutmut_31, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_32': xǁABTestFrameworkǁrecord_metric__mutmut_32, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_33': xǁABTestFrameworkǁrecord_metric__mutmut_33, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_34': xǁABTestFrameworkǁrecord_metric__mutmut_34, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_35': xǁABTestFrameworkǁrecord_metric__mutmut_35, 
        'xǁABTestFrameworkǁrecord_metric__mutmut_36': xǁABTestFrameworkǁrecord_metric__mutmut_36
    }
    
    def record_metric(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁABTestFrameworkǁrecord_metric__mutmut_orig"), object.__getattribute__(self, "xǁABTestFrameworkǁrecord_metric__mutmut_mutants"), args, kwargs, self)
        return result 
    
    record_metric.__signature__ = _mutmut_signature(xǁABTestFrameworkǁrecord_metric__mutmut_orig)
    xǁABTestFrameworkǁrecord_metric__mutmut_orig.__name__ = 'xǁABTestFrameworkǁrecord_metric'

    def xǁABTestFrameworkǁget_variant_metrics__mutmut_orig(self, experiment_id: str, variant: Variant) -> List[float]:
        """
        Get all metric values for a variant.

        Args:
            experiment_id: Experiment identifier
            variant: Variant to get metrics for

        Returns:
            List of metric values
        """
        config = self.get_experiment(experiment_id)
        if not config:
            return []

        # Query metrics from repository
        metrics = self.repository.find_by_feature(config.feature, limit=10000)

        # Filter by experiment and variant
        values = []
        for metric in metrics:
            if (
                metric.metadata.get("experiment_id") == experiment_id
                and metric.metadata.get("variant") == variant.value
                and metric.metric_name == config.success_metric
            ):
                values.append(metric.metric_value)

        return values

    def xǁABTestFrameworkǁget_variant_metrics__mutmut_1(self, experiment_id: str, variant: Variant) -> List[float]:
        """
        Get all metric values for a variant.

        Args:
            experiment_id: Experiment identifier
            variant: Variant to get metrics for

        Returns:
            List of metric values
        """
        config = None
        if not config:
            return []

        # Query metrics from repository
        metrics = self.repository.find_by_feature(config.feature, limit=10000)

        # Filter by experiment and variant
        values = []
        for metric in metrics:
            if (
                metric.metadata.get("experiment_id") == experiment_id
                and metric.metadata.get("variant") == variant.value
                and metric.metric_name == config.success_metric
            ):
                values.append(metric.metric_value)

        return values

    def xǁABTestFrameworkǁget_variant_metrics__mutmut_2(self, experiment_id: str, variant: Variant) -> List[float]:
        """
        Get all metric values for a variant.

        Args:
            experiment_id: Experiment identifier
            variant: Variant to get metrics for

        Returns:
            List of metric values
        """
        config = self.get_experiment(None)
        if not config:
            return []

        # Query metrics from repository
        metrics = self.repository.find_by_feature(config.feature, limit=10000)

        # Filter by experiment and variant
        values = []
        for metric in metrics:
            if (
                metric.metadata.get("experiment_id") == experiment_id
                and metric.metadata.get("variant") == variant.value
                and metric.metric_name == config.success_metric
            ):
                values.append(metric.metric_value)

        return values

    def xǁABTestFrameworkǁget_variant_metrics__mutmut_3(self, experiment_id: str, variant: Variant) -> List[float]:
        """
        Get all metric values for a variant.

        Args:
            experiment_id: Experiment identifier
            variant: Variant to get metrics for

        Returns:
            List of metric values
        """
        config = self.get_experiment(experiment_id)
        if config:
            return []

        # Query metrics from repository
        metrics = self.repository.find_by_feature(config.feature, limit=10000)

        # Filter by experiment and variant
        values = []
        for metric in metrics:
            if (
                metric.metadata.get("experiment_id") == experiment_id
                and metric.metadata.get("variant") == variant.value
                and metric.metric_name == config.success_metric
            ):
                values.append(metric.metric_value)

        return values

    def xǁABTestFrameworkǁget_variant_metrics__mutmut_4(self, experiment_id: str, variant: Variant) -> List[float]:
        """
        Get all metric values for a variant.

        Args:
            experiment_id: Experiment identifier
            variant: Variant to get metrics for

        Returns:
            List of metric values
        """
        config = self.get_experiment(experiment_id)
        if not config:
            return []

        # Query metrics from repository
        metrics = None

        # Filter by experiment and variant
        values = []
        for metric in metrics:
            if (
                metric.metadata.get("experiment_id") == experiment_id
                and metric.metadata.get("variant") == variant.value
                and metric.metric_name == config.success_metric
            ):
                values.append(metric.metric_value)

        return values

    def xǁABTestFrameworkǁget_variant_metrics__mutmut_5(self, experiment_id: str, variant: Variant) -> List[float]:
        """
        Get all metric values for a variant.

        Args:
            experiment_id: Experiment identifier
            variant: Variant to get metrics for

        Returns:
            List of metric values
        """
        config = self.get_experiment(experiment_id)
        if not config:
            return []

        # Query metrics from repository
        metrics = self.repository.find_by_feature(None, limit=10000)

        # Filter by experiment and variant
        values = []
        for metric in metrics:
            if (
                metric.metadata.get("experiment_id") == experiment_id
                and metric.metadata.get("variant") == variant.value
                and metric.metric_name == config.success_metric
            ):
                values.append(metric.metric_value)

        return values

    def xǁABTestFrameworkǁget_variant_metrics__mutmut_6(self, experiment_id: str, variant: Variant) -> List[float]:
        """
        Get all metric values for a variant.

        Args:
            experiment_id: Experiment identifier
            variant: Variant to get metrics for

        Returns:
            List of metric values
        """
        config = self.get_experiment(experiment_id)
        if not config:
            return []

        # Query metrics from repository
        metrics = self.repository.find_by_feature(config.feature, limit=None)

        # Filter by experiment and variant
        values = []
        for metric in metrics:
            if (
                metric.metadata.get("experiment_id") == experiment_id
                and metric.metadata.get("variant") == variant.value
                and metric.metric_name == config.success_metric
            ):
                values.append(metric.metric_value)

        return values

    def xǁABTestFrameworkǁget_variant_metrics__mutmut_7(self, experiment_id: str, variant: Variant) -> List[float]:
        """
        Get all metric values for a variant.

        Args:
            experiment_id: Experiment identifier
            variant: Variant to get metrics for

        Returns:
            List of metric values
        """
        config = self.get_experiment(experiment_id)
        if not config:
            return []

        # Query metrics from repository
        metrics = self.repository.find_by_feature(limit=10000)

        # Filter by experiment and variant
        values = []
        for metric in metrics:
            if (
                metric.metadata.get("experiment_id") == experiment_id
                and metric.metadata.get("variant") == variant.value
                and metric.metric_name == config.success_metric
            ):
                values.append(metric.metric_value)

        return values

    def xǁABTestFrameworkǁget_variant_metrics__mutmut_8(self, experiment_id: str, variant: Variant) -> List[float]:
        """
        Get all metric values for a variant.

        Args:
            experiment_id: Experiment identifier
            variant: Variant to get metrics for

        Returns:
            List of metric values
        """
        config = self.get_experiment(experiment_id)
        if not config:
            return []

        # Query metrics from repository
        metrics = self.repository.find_by_feature(config.feature, )

        # Filter by experiment and variant
        values = []
        for metric in metrics:
            if (
                metric.metadata.get("experiment_id") == experiment_id
                and metric.metadata.get("variant") == variant.value
                and metric.metric_name == config.success_metric
            ):
                values.append(metric.metric_value)

        return values

    def xǁABTestFrameworkǁget_variant_metrics__mutmut_9(self, experiment_id: str, variant: Variant) -> List[float]:
        """
        Get all metric values for a variant.

        Args:
            experiment_id: Experiment identifier
            variant: Variant to get metrics for

        Returns:
            List of metric values
        """
        config = self.get_experiment(experiment_id)
        if not config:
            return []

        # Query metrics from repository
        metrics = self.repository.find_by_feature(config.feature, limit=10001)

        # Filter by experiment and variant
        values = []
        for metric in metrics:
            if (
                metric.metadata.get("experiment_id") == experiment_id
                and metric.metadata.get("variant") == variant.value
                and metric.metric_name == config.success_metric
            ):
                values.append(metric.metric_value)

        return values

    def xǁABTestFrameworkǁget_variant_metrics__mutmut_10(self, experiment_id: str, variant: Variant) -> List[float]:
        """
        Get all metric values for a variant.

        Args:
            experiment_id: Experiment identifier
            variant: Variant to get metrics for

        Returns:
            List of metric values
        """
        config = self.get_experiment(experiment_id)
        if not config:
            return []

        # Query metrics from repository
        metrics = self.repository.find_by_feature(config.feature, limit=10000)

        # Filter by experiment and variant
        values = None
        for metric in metrics:
            if (
                metric.metadata.get("experiment_id") == experiment_id
                and metric.metadata.get("variant") == variant.value
                and metric.metric_name == config.success_metric
            ):
                values.append(metric.metric_value)

        return values

    def xǁABTestFrameworkǁget_variant_metrics__mutmut_11(self, experiment_id: str, variant: Variant) -> List[float]:
        """
        Get all metric values for a variant.

        Args:
            experiment_id: Experiment identifier
            variant: Variant to get metrics for

        Returns:
            List of metric values
        """
        config = self.get_experiment(experiment_id)
        if not config:
            return []

        # Query metrics from repository
        metrics = self.repository.find_by_feature(config.feature, limit=10000)

        # Filter by experiment and variant
        values = []
        for metric in metrics:
            if (
                metric.metadata.get("experiment_id") == experiment_id
                and metric.metadata.get("variant") == variant.value or metric.metric_name == config.success_metric
            ):
                values.append(metric.metric_value)

        return values

    def xǁABTestFrameworkǁget_variant_metrics__mutmut_12(self, experiment_id: str, variant: Variant) -> List[float]:
        """
        Get all metric values for a variant.

        Args:
            experiment_id: Experiment identifier
            variant: Variant to get metrics for

        Returns:
            List of metric values
        """
        config = self.get_experiment(experiment_id)
        if not config:
            return []

        # Query metrics from repository
        metrics = self.repository.find_by_feature(config.feature, limit=10000)

        # Filter by experiment and variant
        values = []
        for metric in metrics:
            if (
                metric.metadata.get("experiment_id") == experiment_id or metric.metadata.get("variant") == variant.value
                and metric.metric_name == config.success_metric
            ):
                values.append(metric.metric_value)

        return values

    def xǁABTestFrameworkǁget_variant_metrics__mutmut_13(self, experiment_id: str, variant: Variant) -> List[float]:
        """
        Get all metric values for a variant.

        Args:
            experiment_id: Experiment identifier
            variant: Variant to get metrics for

        Returns:
            List of metric values
        """
        config = self.get_experiment(experiment_id)
        if not config:
            return []

        # Query metrics from repository
        metrics = self.repository.find_by_feature(config.feature, limit=10000)

        # Filter by experiment and variant
        values = []
        for metric in metrics:
            if (
                metric.metadata.get(None) == experiment_id
                and metric.metadata.get("variant") == variant.value
                and metric.metric_name == config.success_metric
            ):
                values.append(metric.metric_value)

        return values

    def xǁABTestFrameworkǁget_variant_metrics__mutmut_14(self, experiment_id: str, variant: Variant) -> List[float]:
        """
        Get all metric values for a variant.

        Args:
            experiment_id: Experiment identifier
            variant: Variant to get metrics for

        Returns:
            List of metric values
        """
        config = self.get_experiment(experiment_id)
        if not config:
            return []

        # Query metrics from repository
        metrics = self.repository.find_by_feature(config.feature, limit=10000)

        # Filter by experiment and variant
        values = []
        for metric in metrics:
            if (
                metric.metadata.get("XXexperiment_idXX") == experiment_id
                and metric.metadata.get("variant") == variant.value
                and metric.metric_name == config.success_metric
            ):
                values.append(metric.metric_value)

        return values

    def xǁABTestFrameworkǁget_variant_metrics__mutmut_15(self, experiment_id: str, variant: Variant) -> List[float]:
        """
        Get all metric values for a variant.

        Args:
            experiment_id: Experiment identifier
            variant: Variant to get metrics for

        Returns:
            List of metric values
        """
        config = self.get_experiment(experiment_id)
        if not config:
            return []

        # Query metrics from repository
        metrics = self.repository.find_by_feature(config.feature, limit=10000)

        # Filter by experiment and variant
        values = []
        for metric in metrics:
            if (
                metric.metadata.get("EXPERIMENT_ID") == experiment_id
                and metric.metadata.get("variant") == variant.value
                and metric.metric_name == config.success_metric
            ):
                values.append(metric.metric_value)

        return values

    def xǁABTestFrameworkǁget_variant_metrics__mutmut_16(self, experiment_id: str, variant: Variant) -> List[float]:
        """
        Get all metric values for a variant.

        Args:
            experiment_id: Experiment identifier
            variant: Variant to get metrics for

        Returns:
            List of metric values
        """
        config = self.get_experiment(experiment_id)
        if not config:
            return []

        # Query metrics from repository
        metrics = self.repository.find_by_feature(config.feature, limit=10000)

        # Filter by experiment and variant
        values = []
        for metric in metrics:
            if (
                metric.metadata.get("experiment_id") != experiment_id
                and metric.metadata.get("variant") == variant.value
                and metric.metric_name == config.success_metric
            ):
                values.append(metric.metric_value)

        return values

    def xǁABTestFrameworkǁget_variant_metrics__mutmut_17(self, experiment_id: str, variant: Variant) -> List[float]:
        """
        Get all metric values for a variant.

        Args:
            experiment_id: Experiment identifier
            variant: Variant to get metrics for

        Returns:
            List of metric values
        """
        config = self.get_experiment(experiment_id)
        if not config:
            return []

        # Query metrics from repository
        metrics = self.repository.find_by_feature(config.feature, limit=10000)

        # Filter by experiment and variant
        values = []
        for metric in metrics:
            if (
                metric.metadata.get("experiment_id") == experiment_id
                and metric.metadata.get(None) == variant.value
                and metric.metric_name == config.success_metric
            ):
                values.append(metric.metric_value)

        return values

    def xǁABTestFrameworkǁget_variant_metrics__mutmut_18(self, experiment_id: str, variant: Variant) -> List[float]:
        """
        Get all metric values for a variant.

        Args:
            experiment_id: Experiment identifier
            variant: Variant to get metrics for

        Returns:
            List of metric values
        """
        config = self.get_experiment(experiment_id)
        if not config:
            return []

        # Query metrics from repository
        metrics = self.repository.find_by_feature(config.feature, limit=10000)

        # Filter by experiment and variant
        values = []
        for metric in metrics:
            if (
                metric.metadata.get("experiment_id") == experiment_id
                and metric.metadata.get("XXvariantXX") == variant.value
                and metric.metric_name == config.success_metric
            ):
                values.append(metric.metric_value)

        return values

    def xǁABTestFrameworkǁget_variant_metrics__mutmut_19(self, experiment_id: str, variant: Variant) -> List[float]:
        """
        Get all metric values for a variant.

        Args:
            experiment_id: Experiment identifier
            variant: Variant to get metrics for

        Returns:
            List of metric values
        """
        config = self.get_experiment(experiment_id)
        if not config:
            return []

        # Query metrics from repository
        metrics = self.repository.find_by_feature(config.feature, limit=10000)

        # Filter by experiment and variant
        values = []
        for metric in metrics:
            if (
                metric.metadata.get("experiment_id") == experiment_id
                and metric.metadata.get("VARIANT") == variant.value
                and metric.metric_name == config.success_metric
            ):
                values.append(metric.metric_value)

        return values

    def xǁABTestFrameworkǁget_variant_metrics__mutmut_20(self, experiment_id: str, variant: Variant) -> List[float]:
        """
        Get all metric values for a variant.

        Args:
            experiment_id: Experiment identifier
            variant: Variant to get metrics for

        Returns:
            List of metric values
        """
        config = self.get_experiment(experiment_id)
        if not config:
            return []

        # Query metrics from repository
        metrics = self.repository.find_by_feature(config.feature, limit=10000)

        # Filter by experiment and variant
        values = []
        for metric in metrics:
            if (
                metric.metadata.get("experiment_id") == experiment_id
                and metric.metadata.get("variant") != variant.value
                and metric.metric_name == config.success_metric
            ):
                values.append(metric.metric_value)

        return values

    def xǁABTestFrameworkǁget_variant_metrics__mutmut_21(self, experiment_id: str, variant: Variant) -> List[float]:
        """
        Get all metric values for a variant.

        Args:
            experiment_id: Experiment identifier
            variant: Variant to get metrics for

        Returns:
            List of metric values
        """
        config = self.get_experiment(experiment_id)
        if not config:
            return []

        # Query metrics from repository
        metrics = self.repository.find_by_feature(config.feature, limit=10000)

        # Filter by experiment and variant
        values = []
        for metric in metrics:
            if (
                metric.metadata.get("experiment_id") == experiment_id
                and metric.metadata.get("variant") == variant.value
                and metric.metric_name != config.success_metric
            ):
                values.append(metric.metric_value)

        return values

    def xǁABTestFrameworkǁget_variant_metrics__mutmut_22(self, experiment_id: str, variant: Variant) -> List[float]:
        """
        Get all metric values for a variant.

        Args:
            experiment_id: Experiment identifier
            variant: Variant to get metrics for

        Returns:
            List of metric values
        """
        config = self.get_experiment(experiment_id)
        if not config:
            return []

        # Query metrics from repository
        metrics = self.repository.find_by_feature(config.feature, limit=10000)

        # Filter by experiment and variant
        values = []
        for metric in metrics:
            if (
                metric.metadata.get("experiment_id") == experiment_id
                and metric.metadata.get("variant") == variant.value
                and metric.metric_name == config.success_metric
            ):
                values.append(None)

        return values
    
    xǁABTestFrameworkǁget_variant_metrics__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁABTestFrameworkǁget_variant_metrics__mutmut_1': xǁABTestFrameworkǁget_variant_metrics__mutmut_1, 
        'xǁABTestFrameworkǁget_variant_metrics__mutmut_2': xǁABTestFrameworkǁget_variant_metrics__mutmut_2, 
        'xǁABTestFrameworkǁget_variant_metrics__mutmut_3': xǁABTestFrameworkǁget_variant_metrics__mutmut_3, 
        'xǁABTestFrameworkǁget_variant_metrics__mutmut_4': xǁABTestFrameworkǁget_variant_metrics__mutmut_4, 
        'xǁABTestFrameworkǁget_variant_metrics__mutmut_5': xǁABTestFrameworkǁget_variant_metrics__mutmut_5, 
        'xǁABTestFrameworkǁget_variant_metrics__mutmut_6': xǁABTestFrameworkǁget_variant_metrics__mutmut_6, 
        'xǁABTestFrameworkǁget_variant_metrics__mutmut_7': xǁABTestFrameworkǁget_variant_metrics__mutmut_7, 
        'xǁABTestFrameworkǁget_variant_metrics__mutmut_8': xǁABTestFrameworkǁget_variant_metrics__mutmut_8, 
        'xǁABTestFrameworkǁget_variant_metrics__mutmut_9': xǁABTestFrameworkǁget_variant_metrics__mutmut_9, 
        'xǁABTestFrameworkǁget_variant_metrics__mutmut_10': xǁABTestFrameworkǁget_variant_metrics__mutmut_10, 
        'xǁABTestFrameworkǁget_variant_metrics__mutmut_11': xǁABTestFrameworkǁget_variant_metrics__mutmut_11, 
        'xǁABTestFrameworkǁget_variant_metrics__mutmut_12': xǁABTestFrameworkǁget_variant_metrics__mutmut_12, 
        'xǁABTestFrameworkǁget_variant_metrics__mutmut_13': xǁABTestFrameworkǁget_variant_metrics__mutmut_13, 
        'xǁABTestFrameworkǁget_variant_metrics__mutmut_14': xǁABTestFrameworkǁget_variant_metrics__mutmut_14, 
        'xǁABTestFrameworkǁget_variant_metrics__mutmut_15': xǁABTestFrameworkǁget_variant_metrics__mutmut_15, 
        'xǁABTestFrameworkǁget_variant_metrics__mutmut_16': xǁABTestFrameworkǁget_variant_metrics__mutmut_16, 
        'xǁABTestFrameworkǁget_variant_metrics__mutmut_17': xǁABTestFrameworkǁget_variant_metrics__mutmut_17, 
        'xǁABTestFrameworkǁget_variant_metrics__mutmut_18': xǁABTestFrameworkǁget_variant_metrics__mutmut_18, 
        'xǁABTestFrameworkǁget_variant_metrics__mutmut_19': xǁABTestFrameworkǁget_variant_metrics__mutmut_19, 
        'xǁABTestFrameworkǁget_variant_metrics__mutmut_20': xǁABTestFrameworkǁget_variant_metrics__mutmut_20, 
        'xǁABTestFrameworkǁget_variant_metrics__mutmut_21': xǁABTestFrameworkǁget_variant_metrics__mutmut_21, 
        'xǁABTestFrameworkǁget_variant_metrics__mutmut_22': xǁABTestFrameworkǁget_variant_metrics__mutmut_22
    }
    
    def get_variant_metrics(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁABTestFrameworkǁget_variant_metrics__mutmut_orig"), object.__getattribute__(self, "xǁABTestFrameworkǁget_variant_metrics__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_variant_metrics.__signature__ = _mutmut_signature(xǁABTestFrameworkǁget_variant_metrics__mutmut_orig)
    xǁABTestFrameworkǁget_variant_metrics__mutmut_orig.__name__ = 'xǁABTestFrameworkǁget_variant_metrics'

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_orig(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_1(
        self, experiment_id: str, alpha: float = 1.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_2(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = None
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_3(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(None)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_4(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_5(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(None)

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_6(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = None
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_7(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(None, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_8(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, None)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_9(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_10(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, )
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_11(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = None

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_12(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(None, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_13(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, None)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_14(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_15(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, )

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_16(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 and len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_17(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) <= 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_18(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 3 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_19(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) <= 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_20(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 3:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_21(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                None
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_22(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = None
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_23(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) * len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_24(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(None) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_25(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = None

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_26(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) * len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_27(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(None) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_28(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = None
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_29(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(None, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_30(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, None)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_31(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_32(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, )
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_33(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = None

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_34(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(None, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_35(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, None)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_36(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_37(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, )

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_38(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = None

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_39(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            None,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_40(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            None,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_41(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            None,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_42(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            None,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_43(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            None,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_44(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            None,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_45(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_46(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_47(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_48(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_49(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_50(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_51(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = None

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_52(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            None,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_53(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            None,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_54(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            None,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_55(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            None,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_56(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            None,
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_57(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            None,
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_58(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            None,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_59(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_60(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_61(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_62(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_63(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_64(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_65(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_66(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = None
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_67(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 1.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_68(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean == 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_69(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 1:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_70(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = None

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_71(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) / 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_72(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) * abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_73(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean + control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_74(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(None)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_75(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 101

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_76(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=None,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_77(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=None,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_78(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=None,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_79(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=None,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_80(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=None,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_81(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=None,
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_82(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=None,
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_83(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=None,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_84(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=None,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_85(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=None,
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_86(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=None,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_87(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_88(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_89(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_90(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_91(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_92(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_93(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_94(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_95(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            is_significant=(p_value < alpha),
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_96(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            effect_size=effect_size,
        )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_97(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value < alpha),
            )

    def xǁABTestFrameworkǁanalyze_experiment__mutmut_98(
        self, experiment_id: str, alpha: float = 0.05
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical significance testing.

        Performs two-sample t-test to compare control and treatment variants.

        Args:
            experiment_id: Experiment identifier
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            ExperimentResult with statistical analysis

        Raises:
            ValueError: If experiment doesn't exist or insufficient data
        """
        config = self.get_experiment(experiment_id)
        if not config:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get metrics for each variant
        control_values = self.get_variant_metrics(experiment_id, Variant.CONTROL)
        treatment_values = self.get_variant_metrics(experiment_id, Variant.TREATMENT)

        if len(control_values) < 2 or len(treatment_values) < 2:
            raise ValueError(
                f"Insufficient data: control={len(control_values)}, "
                f"treatment={len(treatment_values)}. Need at least 2 each."
            )

        # Calculate statistics
        control_mean = sum(control_values) / len(control_values)
        treatment_mean = sum(treatment_values) / len(treatment_values)

        control_std = self._calculate_std(control_values, control_mean)
        treatment_std = self._calculate_std(treatment_values, treatment_mean)

        # Perform t-test
        t_stat, p_value = self._two_sample_ttest(
            control_values,
            treatment_values,
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
        )

        # Calculate 95% confidence interval for difference
        ci = self._confidence_interval(
            control_mean,
            treatment_mean,
            control_std,
            treatment_std,
            len(control_values),
            len(treatment_values),
            alpha,
        )

        # Calculate effect size (relative improvement)
        effect_size = 0.0
        if control_mean != 0:
            effect_size = ((treatment_mean - control_mean) / abs(control_mean)) * 100

        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            p_value=p_value,
            confidence_interval=ci,
            is_significant=(p_value <= alpha),
            effect_size=effect_size,
        )
    
    xǁABTestFrameworkǁanalyze_experiment__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁABTestFrameworkǁanalyze_experiment__mutmut_1': xǁABTestFrameworkǁanalyze_experiment__mutmut_1, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_2': xǁABTestFrameworkǁanalyze_experiment__mutmut_2, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_3': xǁABTestFrameworkǁanalyze_experiment__mutmut_3, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_4': xǁABTestFrameworkǁanalyze_experiment__mutmut_4, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_5': xǁABTestFrameworkǁanalyze_experiment__mutmut_5, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_6': xǁABTestFrameworkǁanalyze_experiment__mutmut_6, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_7': xǁABTestFrameworkǁanalyze_experiment__mutmut_7, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_8': xǁABTestFrameworkǁanalyze_experiment__mutmut_8, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_9': xǁABTestFrameworkǁanalyze_experiment__mutmut_9, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_10': xǁABTestFrameworkǁanalyze_experiment__mutmut_10, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_11': xǁABTestFrameworkǁanalyze_experiment__mutmut_11, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_12': xǁABTestFrameworkǁanalyze_experiment__mutmut_12, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_13': xǁABTestFrameworkǁanalyze_experiment__mutmut_13, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_14': xǁABTestFrameworkǁanalyze_experiment__mutmut_14, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_15': xǁABTestFrameworkǁanalyze_experiment__mutmut_15, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_16': xǁABTestFrameworkǁanalyze_experiment__mutmut_16, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_17': xǁABTestFrameworkǁanalyze_experiment__mutmut_17, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_18': xǁABTestFrameworkǁanalyze_experiment__mutmut_18, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_19': xǁABTestFrameworkǁanalyze_experiment__mutmut_19, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_20': xǁABTestFrameworkǁanalyze_experiment__mutmut_20, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_21': xǁABTestFrameworkǁanalyze_experiment__mutmut_21, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_22': xǁABTestFrameworkǁanalyze_experiment__mutmut_22, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_23': xǁABTestFrameworkǁanalyze_experiment__mutmut_23, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_24': xǁABTestFrameworkǁanalyze_experiment__mutmut_24, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_25': xǁABTestFrameworkǁanalyze_experiment__mutmut_25, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_26': xǁABTestFrameworkǁanalyze_experiment__mutmut_26, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_27': xǁABTestFrameworkǁanalyze_experiment__mutmut_27, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_28': xǁABTestFrameworkǁanalyze_experiment__mutmut_28, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_29': xǁABTestFrameworkǁanalyze_experiment__mutmut_29, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_30': xǁABTestFrameworkǁanalyze_experiment__mutmut_30, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_31': xǁABTestFrameworkǁanalyze_experiment__mutmut_31, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_32': xǁABTestFrameworkǁanalyze_experiment__mutmut_32, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_33': xǁABTestFrameworkǁanalyze_experiment__mutmut_33, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_34': xǁABTestFrameworkǁanalyze_experiment__mutmut_34, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_35': xǁABTestFrameworkǁanalyze_experiment__mutmut_35, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_36': xǁABTestFrameworkǁanalyze_experiment__mutmut_36, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_37': xǁABTestFrameworkǁanalyze_experiment__mutmut_37, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_38': xǁABTestFrameworkǁanalyze_experiment__mutmut_38, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_39': xǁABTestFrameworkǁanalyze_experiment__mutmut_39, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_40': xǁABTestFrameworkǁanalyze_experiment__mutmut_40, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_41': xǁABTestFrameworkǁanalyze_experiment__mutmut_41, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_42': xǁABTestFrameworkǁanalyze_experiment__mutmut_42, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_43': xǁABTestFrameworkǁanalyze_experiment__mutmut_43, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_44': xǁABTestFrameworkǁanalyze_experiment__mutmut_44, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_45': xǁABTestFrameworkǁanalyze_experiment__mutmut_45, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_46': xǁABTestFrameworkǁanalyze_experiment__mutmut_46, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_47': xǁABTestFrameworkǁanalyze_experiment__mutmut_47, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_48': xǁABTestFrameworkǁanalyze_experiment__mutmut_48, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_49': xǁABTestFrameworkǁanalyze_experiment__mutmut_49, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_50': xǁABTestFrameworkǁanalyze_experiment__mutmut_50, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_51': xǁABTestFrameworkǁanalyze_experiment__mutmut_51, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_52': xǁABTestFrameworkǁanalyze_experiment__mutmut_52, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_53': xǁABTestFrameworkǁanalyze_experiment__mutmut_53, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_54': xǁABTestFrameworkǁanalyze_experiment__mutmut_54, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_55': xǁABTestFrameworkǁanalyze_experiment__mutmut_55, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_56': xǁABTestFrameworkǁanalyze_experiment__mutmut_56, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_57': xǁABTestFrameworkǁanalyze_experiment__mutmut_57, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_58': xǁABTestFrameworkǁanalyze_experiment__mutmut_58, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_59': xǁABTestFrameworkǁanalyze_experiment__mutmut_59, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_60': xǁABTestFrameworkǁanalyze_experiment__mutmut_60, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_61': xǁABTestFrameworkǁanalyze_experiment__mutmut_61, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_62': xǁABTestFrameworkǁanalyze_experiment__mutmut_62, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_63': xǁABTestFrameworkǁanalyze_experiment__mutmut_63, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_64': xǁABTestFrameworkǁanalyze_experiment__mutmut_64, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_65': xǁABTestFrameworkǁanalyze_experiment__mutmut_65, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_66': xǁABTestFrameworkǁanalyze_experiment__mutmut_66, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_67': xǁABTestFrameworkǁanalyze_experiment__mutmut_67, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_68': xǁABTestFrameworkǁanalyze_experiment__mutmut_68, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_69': xǁABTestFrameworkǁanalyze_experiment__mutmut_69, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_70': xǁABTestFrameworkǁanalyze_experiment__mutmut_70, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_71': xǁABTestFrameworkǁanalyze_experiment__mutmut_71, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_72': xǁABTestFrameworkǁanalyze_experiment__mutmut_72, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_73': xǁABTestFrameworkǁanalyze_experiment__mutmut_73, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_74': xǁABTestFrameworkǁanalyze_experiment__mutmut_74, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_75': xǁABTestFrameworkǁanalyze_experiment__mutmut_75, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_76': xǁABTestFrameworkǁanalyze_experiment__mutmut_76, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_77': xǁABTestFrameworkǁanalyze_experiment__mutmut_77, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_78': xǁABTestFrameworkǁanalyze_experiment__mutmut_78, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_79': xǁABTestFrameworkǁanalyze_experiment__mutmut_79, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_80': xǁABTestFrameworkǁanalyze_experiment__mutmut_80, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_81': xǁABTestFrameworkǁanalyze_experiment__mutmut_81, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_82': xǁABTestFrameworkǁanalyze_experiment__mutmut_82, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_83': xǁABTestFrameworkǁanalyze_experiment__mutmut_83, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_84': xǁABTestFrameworkǁanalyze_experiment__mutmut_84, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_85': xǁABTestFrameworkǁanalyze_experiment__mutmut_85, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_86': xǁABTestFrameworkǁanalyze_experiment__mutmut_86, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_87': xǁABTestFrameworkǁanalyze_experiment__mutmut_87, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_88': xǁABTestFrameworkǁanalyze_experiment__mutmut_88, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_89': xǁABTestFrameworkǁanalyze_experiment__mutmut_89, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_90': xǁABTestFrameworkǁanalyze_experiment__mutmut_90, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_91': xǁABTestFrameworkǁanalyze_experiment__mutmut_91, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_92': xǁABTestFrameworkǁanalyze_experiment__mutmut_92, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_93': xǁABTestFrameworkǁanalyze_experiment__mutmut_93, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_94': xǁABTestFrameworkǁanalyze_experiment__mutmut_94, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_95': xǁABTestFrameworkǁanalyze_experiment__mutmut_95, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_96': xǁABTestFrameworkǁanalyze_experiment__mutmut_96, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_97': xǁABTestFrameworkǁanalyze_experiment__mutmut_97, 
        'xǁABTestFrameworkǁanalyze_experiment__mutmut_98': xǁABTestFrameworkǁanalyze_experiment__mutmut_98
    }
    
    def analyze_experiment(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁABTestFrameworkǁanalyze_experiment__mutmut_orig"), object.__getattribute__(self, "xǁABTestFrameworkǁanalyze_experiment__mutmut_mutants"), args, kwargs, self)
        return result 
    
    analyze_experiment.__signature__ = _mutmut_signature(xǁABTestFrameworkǁanalyze_experiment__mutmut_orig)
    xǁABTestFrameworkǁanalyze_experiment__mutmut_orig.__name__ = 'xǁABTestFrameworkǁanalyze_experiment'

    def xǁABTestFrameworkǁ_calculate_std__mutmut_orig(self, values: List[float], mean: float) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0

        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)

    def xǁABTestFrameworkǁ_calculate_std__mutmut_1(self, values: List[float], mean: float) -> float:
        """Calculate standard deviation."""
        if len(values) <= 2:
            return 0.0

        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)

    def xǁABTestFrameworkǁ_calculate_std__mutmut_2(self, values: List[float], mean: float) -> float:
        """Calculate standard deviation."""
        if len(values) < 3:
            return 0.0

        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)

    def xǁABTestFrameworkǁ_calculate_std__mutmut_3(self, values: List[float], mean: float) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 1.0

        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)

    def xǁABTestFrameworkǁ_calculate_std__mutmut_4(self, values: List[float], mean: float) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0

        variance = None
        return math.sqrt(variance)

    def xǁABTestFrameworkǁ_calculate_std__mutmut_5(self, values: List[float], mean: float) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0

        variance = sum((x - mean) ** 2 for x in values) * (len(values) - 1)
        return math.sqrt(variance)

    def xǁABTestFrameworkǁ_calculate_std__mutmut_6(self, values: List[float], mean: float) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0

        variance = sum(None) / (len(values) - 1)
        return math.sqrt(variance)

    def xǁABTestFrameworkǁ_calculate_std__mutmut_7(self, values: List[float], mean: float) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0

        variance = sum((x - mean) * 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)

    def xǁABTestFrameworkǁ_calculate_std__mutmut_8(self, values: List[float], mean: float) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0

        variance = sum((x + mean) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)

    def xǁABTestFrameworkǁ_calculate_std__mutmut_9(self, values: List[float], mean: float) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0

        variance = sum((x - mean) ** 3 for x in values) / (len(values) - 1)
        return math.sqrt(variance)

    def xǁABTestFrameworkǁ_calculate_std__mutmut_10(self, values: List[float], mean: float) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0

        variance = sum((x - mean) ** 2 for x in values) / (len(values) + 1)
        return math.sqrt(variance)

    def xǁABTestFrameworkǁ_calculate_std__mutmut_11(self, values: List[float], mean: float) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0

        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 2)
        return math.sqrt(variance)

    def xǁABTestFrameworkǁ_calculate_std__mutmut_12(self, values: List[float], mean: float) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0

        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(None)
    
    xǁABTestFrameworkǁ_calculate_std__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁABTestFrameworkǁ_calculate_std__mutmut_1': xǁABTestFrameworkǁ_calculate_std__mutmut_1, 
        'xǁABTestFrameworkǁ_calculate_std__mutmut_2': xǁABTestFrameworkǁ_calculate_std__mutmut_2, 
        'xǁABTestFrameworkǁ_calculate_std__mutmut_3': xǁABTestFrameworkǁ_calculate_std__mutmut_3, 
        'xǁABTestFrameworkǁ_calculate_std__mutmut_4': xǁABTestFrameworkǁ_calculate_std__mutmut_4, 
        'xǁABTestFrameworkǁ_calculate_std__mutmut_5': xǁABTestFrameworkǁ_calculate_std__mutmut_5, 
        'xǁABTestFrameworkǁ_calculate_std__mutmut_6': xǁABTestFrameworkǁ_calculate_std__mutmut_6, 
        'xǁABTestFrameworkǁ_calculate_std__mutmut_7': xǁABTestFrameworkǁ_calculate_std__mutmut_7, 
        'xǁABTestFrameworkǁ_calculate_std__mutmut_8': xǁABTestFrameworkǁ_calculate_std__mutmut_8, 
        'xǁABTestFrameworkǁ_calculate_std__mutmut_9': xǁABTestFrameworkǁ_calculate_std__mutmut_9, 
        'xǁABTestFrameworkǁ_calculate_std__mutmut_10': xǁABTestFrameworkǁ_calculate_std__mutmut_10, 
        'xǁABTestFrameworkǁ_calculate_std__mutmut_11': xǁABTestFrameworkǁ_calculate_std__mutmut_11, 
        'xǁABTestFrameworkǁ_calculate_std__mutmut_12': xǁABTestFrameworkǁ_calculate_std__mutmut_12
    }
    
    def _calculate_std(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁABTestFrameworkǁ_calculate_std__mutmut_orig"), object.__getattribute__(self, "xǁABTestFrameworkǁ_calculate_std__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _calculate_std.__signature__ = _mutmut_signature(xǁABTestFrameworkǁ_calculate_std__mutmut_orig)
    xǁABTestFrameworkǁ_calculate_std__mutmut_orig.__name__ = 'xǁABTestFrameworkǁ_calculate_std'

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_orig(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**2 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_1(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = None
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**2 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_2(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = None

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**2 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_3(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = None

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_4(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt(None)

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_5(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) - (treatment_std**2 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_6(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 * n1) + (treatment_std**2 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_7(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std * 2 / n1) + (treatment_std**2 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_8(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**3 / n1) + (treatment_std**2 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_9(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**2 * n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_10(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std * 2 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_11(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**3 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_12(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**2 / n2))

        if se != 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_13(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**2 / n2))

        if se == 1:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_14(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**2 / n2))

        if se == 0:
            return (1.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_15(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**2 / n2))

        if se == 0:
            return (0.0, 2.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_16(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**2 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = None

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_17(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**2 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) * se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_18(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**2 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean + control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_19(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**2 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = None

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_20(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**2 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(None, treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_21(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**2 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, None, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_22(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**2 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, None, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_23(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**2 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, None)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_24(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**2 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_25(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**2 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_26(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**2 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_27(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**2 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, )

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_28(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**2 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = None

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_29(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**2 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(None, df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_30(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**2 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), None)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_31(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**2 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(df)

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_32(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**2 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(t_stat), )

        return (t_stat, p_value)

    def xǁABTestFrameworkǁ_two_sample_ttest__mutmut_33(
        self,
        control: List[float],
        treatment: List[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> Tuple[float, float]:
        """
        Perform two-sample t-test.

        Returns:
            Tuple of (t-statistic, p-value)
        """
        n1 = len(control)
        n2 = len(treatment)

        # Pooled standard error
        se = math.sqrt((control_std**2 / n1) + (treatment_std**2 / n2))

        if se == 0:
            return (0.0, 1.0)

        # T-statistic
        t_stat = (treatment_mean - control_mean) / se

        # Degrees of freedom (Welch-Satterthwaite)
        df = self._welch_df(control_std, treatment_std, n1, n2)

        # P-value (two-tailed) using t-distribution approximation
        p_value = self._t_distribution_pvalue(abs(None), df)

        return (t_stat, p_value)
    
    xǁABTestFrameworkǁ_two_sample_ttest__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_1': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_1, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_2': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_2, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_3': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_3, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_4': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_4, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_5': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_5, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_6': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_6, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_7': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_7, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_8': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_8, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_9': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_9, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_10': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_10, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_11': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_11, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_12': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_12, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_13': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_13, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_14': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_14, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_15': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_15, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_16': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_16, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_17': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_17, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_18': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_18, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_19': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_19, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_20': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_20, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_21': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_21, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_22': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_22, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_23': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_23, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_24': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_24, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_25': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_25, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_26': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_26, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_27': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_27, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_28': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_28, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_29': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_29, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_30': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_30, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_31': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_31, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_32': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_32, 
        'xǁABTestFrameworkǁ_two_sample_ttest__mutmut_33': xǁABTestFrameworkǁ_two_sample_ttest__mutmut_33
    }
    
    def _two_sample_ttest(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁABTestFrameworkǁ_two_sample_ttest__mutmut_orig"), object.__getattribute__(self, "xǁABTestFrameworkǁ_two_sample_ttest__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _two_sample_ttest.__signature__ = _mutmut_signature(xǁABTestFrameworkǁ_two_sample_ttest__mutmut_orig)
    xǁABTestFrameworkǁ_two_sample_ttest__mutmut_orig.__name__ = 'xǁABTestFrameworkǁ_two_sample_ttest'

    def xǁABTestFrameworkǁ_welch_df__mutmut_orig(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_1(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 or std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_2(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 != 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_3(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 1 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_4(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 != 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_5(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 1:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_6(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(None)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_7(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 + 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_8(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 - n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_9(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 3)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_10(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = None
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_11(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) * 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_12(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) - (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_13(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 * n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_14(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1 * 2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_15(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**3 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_16(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 * n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_17(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2 * 2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_18(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**3 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_19(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 3
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_20(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = None

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_21(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) - (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_22(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 * (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_23(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1 * 4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_24(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**5 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_25(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 / (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_26(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1 * 2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_27(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**3 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_28(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 + 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_29(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 2))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_30(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 * (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_31(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2 * 4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_32(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**5 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_33(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 / (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_34(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2 * 2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_35(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**3 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_36(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 + 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_37(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 2)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_38(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator != 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_39(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 1:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_40(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(None)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_41(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 + 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_42(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 - n2 - 2)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_43(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 3)

        return numerator / denominator

    def xǁABTestFrameworkǁ_welch_df__mutmut_44(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator * denominator
    
    xǁABTestFrameworkǁ_welch_df__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁABTestFrameworkǁ_welch_df__mutmut_1': xǁABTestFrameworkǁ_welch_df__mutmut_1, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_2': xǁABTestFrameworkǁ_welch_df__mutmut_2, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_3': xǁABTestFrameworkǁ_welch_df__mutmut_3, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_4': xǁABTestFrameworkǁ_welch_df__mutmut_4, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_5': xǁABTestFrameworkǁ_welch_df__mutmut_5, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_6': xǁABTestFrameworkǁ_welch_df__mutmut_6, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_7': xǁABTestFrameworkǁ_welch_df__mutmut_7, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_8': xǁABTestFrameworkǁ_welch_df__mutmut_8, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_9': xǁABTestFrameworkǁ_welch_df__mutmut_9, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_10': xǁABTestFrameworkǁ_welch_df__mutmut_10, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_11': xǁABTestFrameworkǁ_welch_df__mutmut_11, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_12': xǁABTestFrameworkǁ_welch_df__mutmut_12, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_13': xǁABTestFrameworkǁ_welch_df__mutmut_13, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_14': xǁABTestFrameworkǁ_welch_df__mutmut_14, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_15': xǁABTestFrameworkǁ_welch_df__mutmut_15, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_16': xǁABTestFrameworkǁ_welch_df__mutmut_16, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_17': xǁABTestFrameworkǁ_welch_df__mutmut_17, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_18': xǁABTestFrameworkǁ_welch_df__mutmut_18, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_19': xǁABTestFrameworkǁ_welch_df__mutmut_19, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_20': xǁABTestFrameworkǁ_welch_df__mutmut_20, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_21': xǁABTestFrameworkǁ_welch_df__mutmut_21, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_22': xǁABTestFrameworkǁ_welch_df__mutmut_22, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_23': xǁABTestFrameworkǁ_welch_df__mutmut_23, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_24': xǁABTestFrameworkǁ_welch_df__mutmut_24, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_25': xǁABTestFrameworkǁ_welch_df__mutmut_25, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_26': xǁABTestFrameworkǁ_welch_df__mutmut_26, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_27': xǁABTestFrameworkǁ_welch_df__mutmut_27, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_28': xǁABTestFrameworkǁ_welch_df__mutmut_28, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_29': xǁABTestFrameworkǁ_welch_df__mutmut_29, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_30': xǁABTestFrameworkǁ_welch_df__mutmut_30, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_31': xǁABTestFrameworkǁ_welch_df__mutmut_31, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_32': xǁABTestFrameworkǁ_welch_df__mutmut_32, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_33': xǁABTestFrameworkǁ_welch_df__mutmut_33, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_34': xǁABTestFrameworkǁ_welch_df__mutmut_34, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_35': xǁABTestFrameworkǁ_welch_df__mutmut_35, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_36': xǁABTestFrameworkǁ_welch_df__mutmut_36, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_37': xǁABTestFrameworkǁ_welch_df__mutmut_37, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_38': xǁABTestFrameworkǁ_welch_df__mutmut_38, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_39': xǁABTestFrameworkǁ_welch_df__mutmut_39, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_40': xǁABTestFrameworkǁ_welch_df__mutmut_40, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_41': xǁABTestFrameworkǁ_welch_df__mutmut_41, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_42': xǁABTestFrameworkǁ_welch_df__mutmut_42, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_43': xǁABTestFrameworkǁ_welch_df__mutmut_43, 
        'xǁABTestFrameworkǁ_welch_df__mutmut_44': xǁABTestFrameworkǁ_welch_df__mutmut_44
    }
    
    def _welch_df(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁABTestFrameworkǁ_welch_df__mutmut_orig"), object.__getattribute__(self, "xǁABTestFrameworkǁ_welch_df__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _welch_df.__signature__ = _mutmut_signature(xǁABTestFrameworkǁ_welch_df__mutmut_orig)
    xǁABTestFrameworkǁ_welch_df__mutmut_orig.__name__ = 'xǁABTestFrameworkǁ_welch_df'

    def xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_orig(self, t_stat: float, df: float) -> float:
        """
        Approximate p-value for t-distribution (two-tailed).

        Uses normal approximation for large df (>30), otherwise uses
        a simple approximation based on t-distribution properties.
        """
        if df > 30:
            # Normal approximation for large df
            return 2 * (1 - self._normal_cdf(t_stat))

        # Simple approximation for smaller df
        # More accurate implementation would use scipy.stats.t.sf
        z_approx = t_stat * math.sqrt(df / (df + t_stat**2))
        return 2 * (1 - self._normal_cdf(abs(z_approx)))

    def xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_1(self, t_stat: float, df: float) -> float:
        """
        Approximate p-value for t-distribution (two-tailed).

        Uses normal approximation for large df (>30), otherwise uses
        a simple approximation based on t-distribution properties.
        """
        if df >= 30:
            # Normal approximation for large df
            return 2 * (1 - self._normal_cdf(t_stat))

        # Simple approximation for smaller df
        # More accurate implementation would use scipy.stats.t.sf
        z_approx = t_stat * math.sqrt(df / (df + t_stat**2))
        return 2 * (1 - self._normal_cdf(abs(z_approx)))

    def xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_2(self, t_stat: float, df: float) -> float:
        """
        Approximate p-value for t-distribution (two-tailed).

        Uses normal approximation for large df (>30), otherwise uses
        a simple approximation based on t-distribution properties.
        """
        if df > 31:
            # Normal approximation for large df
            return 2 * (1 - self._normal_cdf(t_stat))

        # Simple approximation for smaller df
        # More accurate implementation would use scipy.stats.t.sf
        z_approx = t_stat * math.sqrt(df / (df + t_stat**2))
        return 2 * (1 - self._normal_cdf(abs(z_approx)))

    def xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_3(self, t_stat: float, df: float) -> float:
        """
        Approximate p-value for t-distribution (two-tailed).

        Uses normal approximation for large df (>30), otherwise uses
        a simple approximation based on t-distribution properties.
        """
        if df > 30:
            # Normal approximation for large df
            return 2 / (1 - self._normal_cdf(t_stat))

        # Simple approximation for smaller df
        # More accurate implementation would use scipy.stats.t.sf
        z_approx = t_stat * math.sqrt(df / (df + t_stat**2))
        return 2 * (1 - self._normal_cdf(abs(z_approx)))

    def xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_4(self, t_stat: float, df: float) -> float:
        """
        Approximate p-value for t-distribution (two-tailed).

        Uses normal approximation for large df (>30), otherwise uses
        a simple approximation based on t-distribution properties.
        """
        if df > 30:
            # Normal approximation for large df
            return 3 * (1 - self._normal_cdf(t_stat))

        # Simple approximation for smaller df
        # More accurate implementation would use scipy.stats.t.sf
        z_approx = t_stat * math.sqrt(df / (df + t_stat**2))
        return 2 * (1 - self._normal_cdf(abs(z_approx)))

    def xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_5(self, t_stat: float, df: float) -> float:
        """
        Approximate p-value for t-distribution (two-tailed).

        Uses normal approximation for large df (>30), otherwise uses
        a simple approximation based on t-distribution properties.
        """
        if df > 30:
            # Normal approximation for large df
            return 2 * (1 + self._normal_cdf(t_stat))

        # Simple approximation for smaller df
        # More accurate implementation would use scipy.stats.t.sf
        z_approx = t_stat * math.sqrt(df / (df + t_stat**2))
        return 2 * (1 - self._normal_cdf(abs(z_approx)))

    def xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_6(self, t_stat: float, df: float) -> float:
        """
        Approximate p-value for t-distribution (two-tailed).

        Uses normal approximation for large df (>30), otherwise uses
        a simple approximation based on t-distribution properties.
        """
        if df > 30:
            # Normal approximation for large df
            return 2 * (2 - self._normal_cdf(t_stat))

        # Simple approximation for smaller df
        # More accurate implementation would use scipy.stats.t.sf
        z_approx = t_stat * math.sqrt(df / (df + t_stat**2))
        return 2 * (1 - self._normal_cdf(abs(z_approx)))

    def xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_7(self, t_stat: float, df: float) -> float:
        """
        Approximate p-value for t-distribution (two-tailed).

        Uses normal approximation for large df (>30), otherwise uses
        a simple approximation based on t-distribution properties.
        """
        if df > 30:
            # Normal approximation for large df
            return 2 * (1 - self._normal_cdf(None))

        # Simple approximation for smaller df
        # More accurate implementation would use scipy.stats.t.sf
        z_approx = t_stat * math.sqrt(df / (df + t_stat**2))
        return 2 * (1 - self._normal_cdf(abs(z_approx)))

    def xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_8(self, t_stat: float, df: float) -> float:
        """
        Approximate p-value for t-distribution (two-tailed).

        Uses normal approximation for large df (>30), otherwise uses
        a simple approximation based on t-distribution properties.
        """
        if df > 30:
            # Normal approximation for large df
            return 2 * (1 - self._normal_cdf(t_stat))

        # Simple approximation for smaller df
        # More accurate implementation would use scipy.stats.t.sf
        z_approx = None
        return 2 * (1 - self._normal_cdf(abs(z_approx)))

    def xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_9(self, t_stat: float, df: float) -> float:
        """
        Approximate p-value for t-distribution (two-tailed).

        Uses normal approximation for large df (>30), otherwise uses
        a simple approximation based on t-distribution properties.
        """
        if df > 30:
            # Normal approximation for large df
            return 2 * (1 - self._normal_cdf(t_stat))

        # Simple approximation for smaller df
        # More accurate implementation would use scipy.stats.t.sf
        z_approx = t_stat / math.sqrt(df / (df + t_stat**2))
        return 2 * (1 - self._normal_cdf(abs(z_approx)))

    def xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_10(self, t_stat: float, df: float) -> float:
        """
        Approximate p-value for t-distribution (two-tailed).

        Uses normal approximation for large df (>30), otherwise uses
        a simple approximation based on t-distribution properties.
        """
        if df > 30:
            # Normal approximation for large df
            return 2 * (1 - self._normal_cdf(t_stat))

        # Simple approximation for smaller df
        # More accurate implementation would use scipy.stats.t.sf
        z_approx = t_stat * math.sqrt(None)
        return 2 * (1 - self._normal_cdf(abs(z_approx)))

    def xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_11(self, t_stat: float, df: float) -> float:
        """
        Approximate p-value for t-distribution (two-tailed).

        Uses normal approximation for large df (>30), otherwise uses
        a simple approximation based on t-distribution properties.
        """
        if df > 30:
            # Normal approximation for large df
            return 2 * (1 - self._normal_cdf(t_stat))

        # Simple approximation for smaller df
        # More accurate implementation would use scipy.stats.t.sf
        z_approx = t_stat * math.sqrt(df * (df + t_stat**2))
        return 2 * (1 - self._normal_cdf(abs(z_approx)))

    def xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_12(self, t_stat: float, df: float) -> float:
        """
        Approximate p-value for t-distribution (two-tailed).

        Uses normal approximation for large df (>30), otherwise uses
        a simple approximation based on t-distribution properties.
        """
        if df > 30:
            # Normal approximation for large df
            return 2 * (1 - self._normal_cdf(t_stat))

        # Simple approximation for smaller df
        # More accurate implementation would use scipy.stats.t.sf
        z_approx = t_stat * math.sqrt(df / (df - t_stat**2))
        return 2 * (1 - self._normal_cdf(abs(z_approx)))

    def xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_13(self, t_stat: float, df: float) -> float:
        """
        Approximate p-value for t-distribution (two-tailed).

        Uses normal approximation for large df (>30), otherwise uses
        a simple approximation based on t-distribution properties.
        """
        if df > 30:
            # Normal approximation for large df
            return 2 * (1 - self._normal_cdf(t_stat))

        # Simple approximation for smaller df
        # More accurate implementation would use scipy.stats.t.sf
        z_approx = t_stat * math.sqrt(df / (df + t_stat * 2))
        return 2 * (1 - self._normal_cdf(abs(z_approx)))

    def xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_14(self, t_stat: float, df: float) -> float:
        """
        Approximate p-value for t-distribution (two-tailed).

        Uses normal approximation for large df (>30), otherwise uses
        a simple approximation based on t-distribution properties.
        """
        if df > 30:
            # Normal approximation for large df
            return 2 * (1 - self._normal_cdf(t_stat))

        # Simple approximation for smaller df
        # More accurate implementation would use scipy.stats.t.sf
        z_approx = t_stat * math.sqrt(df / (df + t_stat**3))
        return 2 * (1 - self._normal_cdf(abs(z_approx)))

    def xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_15(self, t_stat: float, df: float) -> float:
        """
        Approximate p-value for t-distribution (two-tailed).

        Uses normal approximation for large df (>30), otherwise uses
        a simple approximation based on t-distribution properties.
        """
        if df > 30:
            # Normal approximation for large df
            return 2 * (1 - self._normal_cdf(t_stat))

        # Simple approximation for smaller df
        # More accurate implementation would use scipy.stats.t.sf
        z_approx = t_stat * math.sqrt(df / (df + t_stat**2))
        return 2 / (1 - self._normal_cdf(abs(z_approx)))

    def xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_16(self, t_stat: float, df: float) -> float:
        """
        Approximate p-value for t-distribution (two-tailed).

        Uses normal approximation for large df (>30), otherwise uses
        a simple approximation based on t-distribution properties.
        """
        if df > 30:
            # Normal approximation for large df
            return 2 * (1 - self._normal_cdf(t_stat))

        # Simple approximation for smaller df
        # More accurate implementation would use scipy.stats.t.sf
        z_approx = t_stat * math.sqrt(df / (df + t_stat**2))
        return 3 * (1 - self._normal_cdf(abs(z_approx)))

    def xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_17(self, t_stat: float, df: float) -> float:
        """
        Approximate p-value for t-distribution (two-tailed).

        Uses normal approximation for large df (>30), otherwise uses
        a simple approximation based on t-distribution properties.
        """
        if df > 30:
            # Normal approximation for large df
            return 2 * (1 - self._normal_cdf(t_stat))

        # Simple approximation for smaller df
        # More accurate implementation would use scipy.stats.t.sf
        z_approx = t_stat * math.sqrt(df / (df + t_stat**2))
        return 2 * (1 + self._normal_cdf(abs(z_approx)))

    def xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_18(self, t_stat: float, df: float) -> float:
        """
        Approximate p-value for t-distribution (two-tailed).

        Uses normal approximation for large df (>30), otherwise uses
        a simple approximation based on t-distribution properties.
        """
        if df > 30:
            # Normal approximation for large df
            return 2 * (1 - self._normal_cdf(t_stat))

        # Simple approximation for smaller df
        # More accurate implementation would use scipy.stats.t.sf
        z_approx = t_stat * math.sqrt(df / (df + t_stat**2))
        return 2 * (2 - self._normal_cdf(abs(z_approx)))

    def xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_19(self, t_stat: float, df: float) -> float:
        """
        Approximate p-value for t-distribution (two-tailed).

        Uses normal approximation for large df (>30), otherwise uses
        a simple approximation based on t-distribution properties.
        """
        if df > 30:
            # Normal approximation for large df
            return 2 * (1 - self._normal_cdf(t_stat))

        # Simple approximation for smaller df
        # More accurate implementation would use scipy.stats.t.sf
        z_approx = t_stat * math.sqrt(df / (df + t_stat**2))
        return 2 * (1 - self._normal_cdf(None))

    def xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_20(self, t_stat: float, df: float) -> float:
        """
        Approximate p-value for t-distribution (two-tailed).

        Uses normal approximation for large df (>30), otherwise uses
        a simple approximation based on t-distribution properties.
        """
        if df > 30:
            # Normal approximation for large df
            return 2 * (1 - self._normal_cdf(t_stat))

        # Simple approximation for smaller df
        # More accurate implementation would use scipy.stats.t.sf
        z_approx = t_stat * math.sqrt(df / (df + t_stat**2))
        return 2 * (1 - self._normal_cdf(abs(None)))
    
    xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_1': xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_1, 
        'xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_2': xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_2, 
        'xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_3': xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_3, 
        'xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_4': xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_4, 
        'xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_5': xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_5, 
        'xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_6': xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_6, 
        'xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_7': xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_7, 
        'xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_8': xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_8, 
        'xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_9': xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_9, 
        'xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_10': xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_10, 
        'xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_11': xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_11, 
        'xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_12': xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_12, 
        'xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_13': xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_13, 
        'xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_14': xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_14, 
        'xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_15': xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_15, 
        'xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_16': xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_16, 
        'xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_17': xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_17, 
        'xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_18': xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_18, 
        'xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_19': xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_19, 
        'xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_20': xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_20
    }
    
    def _t_distribution_pvalue(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_orig"), object.__getattribute__(self, "xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _t_distribution_pvalue.__signature__ = _mutmut_signature(xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_orig)
    xǁABTestFrameworkǁ_t_distribution_pvalue__mutmut_orig.__name__ = 'xǁABTestFrameworkǁ_t_distribution_pvalue'

    def xǁABTestFrameworkǁ_normal_cdf__mutmut_orig(self, x: float) -> float:
        """Cumulative distribution function for standard normal distribution."""
        # Using error function approximation
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    def xǁABTestFrameworkǁ_normal_cdf__mutmut_1(self, x: float) -> float:
        """Cumulative distribution function for standard normal distribution."""
        # Using error function approximation
        return 0.5 / (1 + math.erf(x / math.sqrt(2)))

    def xǁABTestFrameworkǁ_normal_cdf__mutmut_2(self, x: float) -> float:
        """Cumulative distribution function for standard normal distribution."""
        # Using error function approximation
        return 1.5 * (1 + math.erf(x / math.sqrt(2)))

    def xǁABTestFrameworkǁ_normal_cdf__mutmut_3(self, x: float) -> float:
        """Cumulative distribution function for standard normal distribution."""
        # Using error function approximation
        return 0.5 * (1 - math.erf(x / math.sqrt(2)))

    def xǁABTestFrameworkǁ_normal_cdf__mutmut_4(self, x: float) -> float:
        """Cumulative distribution function for standard normal distribution."""
        # Using error function approximation
        return 0.5 * (2 + math.erf(x / math.sqrt(2)))

    def xǁABTestFrameworkǁ_normal_cdf__mutmut_5(self, x: float) -> float:
        """Cumulative distribution function for standard normal distribution."""
        # Using error function approximation
        return 0.5 * (1 + math.erf(None))

    def xǁABTestFrameworkǁ_normal_cdf__mutmut_6(self, x: float) -> float:
        """Cumulative distribution function for standard normal distribution."""
        # Using error function approximation
        return 0.5 * (1 + math.erf(x * math.sqrt(2)))

    def xǁABTestFrameworkǁ_normal_cdf__mutmut_7(self, x: float) -> float:
        """Cumulative distribution function for standard normal distribution."""
        # Using error function approximation
        return 0.5 * (1 + math.erf(x / math.sqrt(None)))

    def xǁABTestFrameworkǁ_normal_cdf__mutmut_8(self, x: float) -> float:
        """Cumulative distribution function for standard normal distribution."""
        # Using error function approximation
        return 0.5 * (1 + math.erf(x / math.sqrt(3)))
    
    xǁABTestFrameworkǁ_normal_cdf__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁABTestFrameworkǁ_normal_cdf__mutmut_1': xǁABTestFrameworkǁ_normal_cdf__mutmut_1, 
        'xǁABTestFrameworkǁ_normal_cdf__mutmut_2': xǁABTestFrameworkǁ_normal_cdf__mutmut_2, 
        'xǁABTestFrameworkǁ_normal_cdf__mutmut_3': xǁABTestFrameworkǁ_normal_cdf__mutmut_3, 
        'xǁABTestFrameworkǁ_normal_cdf__mutmut_4': xǁABTestFrameworkǁ_normal_cdf__mutmut_4, 
        'xǁABTestFrameworkǁ_normal_cdf__mutmut_5': xǁABTestFrameworkǁ_normal_cdf__mutmut_5, 
        'xǁABTestFrameworkǁ_normal_cdf__mutmut_6': xǁABTestFrameworkǁ_normal_cdf__mutmut_6, 
        'xǁABTestFrameworkǁ_normal_cdf__mutmut_7': xǁABTestFrameworkǁ_normal_cdf__mutmut_7, 
        'xǁABTestFrameworkǁ_normal_cdf__mutmut_8': xǁABTestFrameworkǁ_normal_cdf__mutmut_8
    }
    
    def _normal_cdf(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁABTestFrameworkǁ_normal_cdf__mutmut_orig"), object.__getattribute__(self, "xǁABTestFrameworkǁ_normal_cdf__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _normal_cdf.__signature__ = _mutmut_signature(xǁABTestFrameworkǁ_normal_cdf__mutmut_orig)
    xǁABTestFrameworkǁ_normal_cdf__mutmut_orig.__name__ = 'xǁABTestFrameworkǁ_normal_cdf'

    def xǁABTestFrameworkǁ_confidence_interval__mutmut_orig(
        self,
        mean1: float,
        mean2: float,
        std1: float,
        std2: float,
        n1: int,
        n2: int,
        alpha: float,
    ) -> Tuple[float, float]:
        """
        Calculate 95% confidence interval for difference of means.

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        diff = mean2 - mean1
        se = math.sqrt((std1**2 / n1) + (std2**2 / n2))

        # Critical value (approximation: z=1.96 for 95% CI)
        z_critical = 1.96

        margin = z_critical * se

        return (diff - margin, diff + margin)

    def xǁABTestFrameworkǁ_confidence_interval__mutmut_1(
        self,
        mean1: float,
        mean2: float,
        std1: float,
        std2: float,
        n1: int,
        n2: int,
        alpha: float,
    ) -> Tuple[float, float]:
        """
        Calculate 95% confidence interval for difference of means.

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        diff = None
        se = math.sqrt((std1**2 / n1) + (std2**2 / n2))

        # Critical value (approximation: z=1.96 for 95% CI)
        z_critical = 1.96

        margin = z_critical * se

        return (diff - margin, diff + margin)

    def xǁABTestFrameworkǁ_confidence_interval__mutmut_2(
        self,
        mean1: float,
        mean2: float,
        std1: float,
        std2: float,
        n1: int,
        n2: int,
        alpha: float,
    ) -> Tuple[float, float]:
        """
        Calculate 95% confidence interval for difference of means.

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        diff = mean2 + mean1
        se = math.sqrt((std1**2 / n1) + (std2**2 / n2))

        # Critical value (approximation: z=1.96 for 95% CI)
        z_critical = 1.96

        margin = z_critical * se

        return (diff - margin, diff + margin)

    def xǁABTestFrameworkǁ_confidence_interval__mutmut_3(
        self,
        mean1: float,
        mean2: float,
        std1: float,
        std2: float,
        n1: int,
        n2: int,
        alpha: float,
    ) -> Tuple[float, float]:
        """
        Calculate 95% confidence interval for difference of means.

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        diff = mean2 - mean1
        se = None

        # Critical value (approximation: z=1.96 for 95% CI)
        z_critical = 1.96

        margin = z_critical * se

        return (diff - margin, diff + margin)

    def xǁABTestFrameworkǁ_confidence_interval__mutmut_4(
        self,
        mean1: float,
        mean2: float,
        std1: float,
        std2: float,
        n1: int,
        n2: int,
        alpha: float,
    ) -> Tuple[float, float]:
        """
        Calculate 95% confidence interval for difference of means.

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        diff = mean2 - mean1
        se = math.sqrt(None)

        # Critical value (approximation: z=1.96 for 95% CI)
        z_critical = 1.96

        margin = z_critical * se

        return (diff - margin, diff + margin)

    def xǁABTestFrameworkǁ_confidence_interval__mutmut_5(
        self,
        mean1: float,
        mean2: float,
        std1: float,
        std2: float,
        n1: int,
        n2: int,
        alpha: float,
    ) -> Tuple[float, float]:
        """
        Calculate 95% confidence interval for difference of means.

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        diff = mean2 - mean1
        se = math.sqrt((std1**2 / n1) - (std2**2 / n2))

        # Critical value (approximation: z=1.96 for 95% CI)
        z_critical = 1.96

        margin = z_critical * se

        return (diff - margin, diff + margin)

    def xǁABTestFrameworkǁ_confidence_interval__mutmut_6(
        self,
        mean1: float,
        mean2: float,
        std1: float,
        std2: float,
        n1: int,
        n2: int,
        alpha: float,
    ) -> Tuple[float, float]:
        """
        Calculate 95% confidence interval for difference of means.

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        diff = mean2 - mean1
        se = math.sqrt((std1**2 * n1) + (std2**2 / n2))

        # Critical value (approximation: z=1.96 for 95% CI)
        z_critical = 1.96

        margin = z_critical * se

        return (diff - margin, diff + margin)

    def xǁABTestFrameworkǁ_confidence_interval__mutmut_7(
        self,
        mean1: float,
        mean2: float,
        std1: float,
        std2: float,
        n1: int,
        n2: int,
        alpha: float,
    ) -> Tuple[float, float]:
        """
        Calculate 95% confidence interval for difference of means.

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        diff = mean2 - mean1
        se = math.sqrt((std1 * 2 / n1) + (std2**2 / n2))

        # Critical value (approximation: z=1.96 for 95% CI)
        z_critical = 1.96

        margin = z_critical * se

        return (diff - margin, diff + margin)

    def xǁABTestFrameworkǁ_confidence_interval__mutmut_8(
        self,
        mean1: float,
        mean2: float,
        std1: float,
        std2: float,
        n1: int,
        n2: int,
        alpha: float,
    ) -> Tuple[float, float]:
        """
        Calculate 95% confidence interval for difference of means.

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        diff = mean2 - mean1
        se = math.sqrt((std1**3 / n1) + (std2**2 / n2))

        # Critical value (approximation: z=1.96 for 95% CI)
        z_critical = 1.96

        margin = z_critical * se

        return (diff - margin, diff + margin)

    def xǁABTestFrameworkǁ_confidence_interval__mutmut_9(
        self,
        mean1: float,
        mean2: float,
        std1: float,
        std2: float,
        n1: int,
        n2: int,
        alpha: float,
    ) -> Tuple[float, float]:
        """
        Calculate 95% confidence interval for difference of means.

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        diff = mean2 - mean1
        se = math.sqrt((std1**2 / n1) + (std2**2 * n2))

        # Critical value (approximation: z=1.96 for 95% CI)
        z_critical = 1.96

        margin = z_critical * se

        return (diff - margin, diff + margin)

    def xǁABTestFrameworkǁ_confidence_interval__mutmut_10(
        self,
        mean1: float,
        mean2: float,
        std1: float,
        std2: float,
        n1: int,
        n2: int,
        alpha: float,
    ) -> Tuple[float, float]:
        """
        Calculate 95% confidence interval for difference of means.

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        diff = mean2 - mean1
        se = math.sqrt((std1**2 / n1) + (std2 * 2 / n2))

        # Critical value (approximation: z=1.96 for 95% CI)
        z_critical = 1.96

        margin = z_critical * se

        return (diff - margin, diff + margin)

    def xǁABTestFrameworkǁ_confidence_interval__mutmut_11(
        self,
        mean1: float,
        mean2: float,
        std1: float,
        std2: float,
        n1: int,
        n2: int,
        alpha: float,
    ) -> Tuple[float, float]:
        """
        Calculate 95% confidence interval for difference of means.

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        diff = mean2 - mean1
        se = math.sqrt((std1**2 / n1) + (std2**3 / n2))

        # Critical value (approximation: z=1.96 for 95% CI)
        z_critical = 1.96

        margin = z_critical * se

        return (diff - margin, diff + margin)

    def xǁABTestFrameworkǁ_confidence_interval__mutmut_12(
        self,
        mean1: float,
        mean2: float,
        std1: float,
        std2: float,
        n1: int,
        n2: int,
        alpha: float,
    ) -> Tuple[float, float]:
        """
        Calculate 95% confidence interval for difference of means.

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        diff = mean2 - mean1
        se = math.sqrt((std1**2 / n1) + (std2**2 / n2))

        # Critical value (approximation: z=1.96 for 95% CI)
        z_critical = None

        margin = z_critical * se

        return (diff - margin, diff + margin)

    def xǁABTestFrameworkǁ_confidence_interval__mutmut_13(
        self,
        mean1: float,
        mean2: float,
        std1: float,
        std2: float,
        n1: int,
        n2: int,
        alpha: float,
    ) -> Tuple[float, float]:
        """
        Calculate 95% confidence interval for difference of means.

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        diff = mean2 - mean1
        se = math.sqrt((std1**2 / n1) + (std2**2 / n2))

        # Critical value (approximation: z=1.96 for 95% CI)
        z_critical = 2.96

        margin = z_critical * se

        return (diff - margin, diff + margin)

    def xǁABTestFrameworkǁ_confidence_interval__mutmut_14(
        self,
        mean1: float,
        mean2: float,
        std1: float,
        std2: float,
        n1: int,
        n2: int,
        alpha: float,
    ) -> Tuple[float, float]:
        """
        Calculate 95% confidence interval for difference of means.

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        diff = mean2 - mean1
        se = math.sqrt((std1**2 / n1) + (std2**2 / n2))

        # Critical value (approximation: z=1.96 for 95% CI)
        z_critical = 1.96

        margin = None

        return (diff - margin, diff + margin)

    def xǁABTestFrameworkǁ_confidence_interval__mutmut_15(
        self,
        mean1: float,
        mean2: float,
        std1: float,
        std2: float,
        n1: int,
        n2: int,
        alpha: float,
    ) -> Tuple[float, float]:
        """
        Calculate 95% confidence interval for difference of means.

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        diff = mean2 - mean1
        se = math.sqrt((std1**2 / n1) + (std2**2 / n2))

        # Critical value (approximation: z=1.96 for 95% CI)
        z_critical = 1.96

        margin = z_critical / se

        return (diff - margin, diff + margin)

    def xǁABTestFrameworkǁ_confidence_interval__mutmut_16(
        self,
        mean1: float,
        mean2: float,
        std1: float,
        std2: float,
        n1: int,
        n2: int,
        alpha: float,
    ) -> Tuple[float, float]:
        """
        Calculate 95% confidence interval for difference of means.

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        diff = mean2 - mean1
        se = math.sqrt((std1**2 / n1) + (std2**2 / n2))

        # Critical value (approximation: z=1.96 for 95% CI)
        z_critical = 1.96

        margin = z_critical * se

        return (diff + margin, diff + margin)

    def xǁABTestFrameworkǁ_confidence_interval__mutmut_17(
        self,
        mean1: float,
        mean2: float,
        std1: float,
        std2: float,
        n1: int,
        n2: int,
        alpha: float,
    ) -> Tuple[float, float]:
        """
        Calculate 95% confidence interval for difference of means.

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        diff = mean2 - mean1
        se = math.sqrt((std1**2 / n1) + (std2**2 / n2))

        # Critical value (approximation: z=1.96 for 95% CI)
        z_critical = 1.96

        margin = z_critical * se

        return (diff - margin, diff - margin)
    
    xǁABTestFrameworkǁ_confidence_interval__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁABTestFrameworkǁ_confidence_interval__mutmut_1': xǁABTestFrameworkǁ_confidence_interval__mutmut_1, 
        'xǁABTestFrameworkǁ_confidence_interval__mutmut_2': xǁABTestFrameworkǁ_confidence_interval__mutmut_2, 
        'xǁABTestFrameworkǁ_confidence_interval__mutmut_3': xǁABTestFrameworkǁ_confidence_interval__mutmut_3, 
        'xǁABTestFrameworkǁ_confidence_interval__mutmut_4': xǁABTestFrameworkǁ_confidence_interval__mutmut_4, 
        'xǁABTestFrameworkǁ_confidence_interval__mutmut_5': xǁABTestFrameworkǁ_confidence_interval__mutmut_5, 
        'xǁABTestFrameworkǁ_confidence_interval__mutmut_6': xǁABTestFrameworkǁ_confidence_interval__mutmut_6, 
        'xǁABTestFrameworkǁ_confidence_interval__mutmut_7': xǁABTestFrameworkǁ_confidence_interval__mutmut_7, 
        'xǁABTestFrameworkǁ_confidence_interval__mutmut_8': xǁABTestFrameworkǁ_confidence_interval__mutmut_8, 
        'xǁABTestFrameworkǁ_confidence_interval__mutmut_9': xǁABTestFrameworkǁ_confidence_interval__mutmut_9, 
        'xǁABTestFrameworkǁ_confidence_interval__mutmut_10': xǁABTestFrameworkǁ_confidence_interval__mutmut_10, 
        'xǁABTestFrameworkǁ_confidence_interval__mutmut_11': xǁABTestFrameworkǁ_confidence_interval__mutmut_11, 
        'xǁABTestFrameworkǁ_confidence_interval__mutmut_12': xǁABTestFrameworkǁ_confidence_interval__mutmut_12, 
        'xǁABTestFrameworkǁ_confidence_interval__mutmut_13': xǁABTestFrameworkǁ_confidence_interval__mutmut_13, 
        'xǁABTestFrameworkǁ_confidence_interval__mutmut_14': xǁABTestFrameworkǁ_confidence_interval__mutmut_14, 
        'xǁABTestFrameworkǁ_confidence_interval__mutmut_15': xǁABTestFrameworkǁ_confidence_interval__mutmut_15, 
        'xǁABTestFrameworkǁ_confidence_interval__mutmut_16': xǁABTestFrameworkǁ_confidence_interval__mutmut_16, 
        'xǁABTestFrameworkǁ_confidence_interval__mutmut_17': xǁABTestFrameworkǁ_confidence_interval__mutmut_17
    }
    
    def _confidence_interval(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁABTestFrameworkǁ_confidence_interval__mutmut_orig"), object.__getattribute__(self, "xǁABTestFrameworkǁ_confidence_interval__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _confidence_interval.__signature__ = _mutmut_signature(xǁABTestFrameworkǁ_confidence_interval__mutmut_orig)
    xǁABTestFrameworkǁ_confidence_interval__mutmut_orig.__name__ = 'xǁABTestFrameworkǁ_confidence_interval'

    def xǁABTestFrameworkǁget_variant_distribution__mutmut_orig(
        self, experiment_id: str, n_samples: int = 1000
    ) -> Dict[Variant, int]:
        """
        Get distribution of variant assignments over n_samples users.

        Useful for validating 50/50 split.

        Args:
            experiment_id: Experiment identifier
            n_samples: Number of sample user IDs to test

        Returns:
            Dictionary mapping variant to count
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        distribution = {Variant.CONTROL: 0, Variant.TREATMENT: 0}

        for i in range(n_samples):
            user_id = f"test-user-{i}"
            variant = self.assign_variant(experiment_id, user_id)
            distribution[variant] += 1

        return distribution

    def xǁABTestFrameworkǁget_variant_distribution__mutmut_1(
        self, experiment_id: str, n_samples: int = 1001
    ) -> Dict[Variant, int]:
        """
        Get distribution of variant assignments over n_samples users.

        Useful for validating 50/50 split.

        Args:
            experiment_id: Experiment identifier
            n_samples: Number of sample user IDs to test

        Returns:
            Dictionary mapping variant to count
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        distribution = {Variant.CONTROL: 0, Variant.TREATMENT: 0}

        for i in range(n_samples):
            user_id = f"test-user-{i}"
            variant = self.assign_variant(experiment_id, user_id)
            distribution[variant] += 1

        return distribution

    def xǁABTestFrameworkǁget_variant_distribution__mutmut_2(
        self, experiment_id: str, n_samples: int = 1000
    ) -> Dict[Variant, int]:
        """
        Get distribution of variant assignments over n_samples users.

        Useful for validating 50/50 split.

        Args:
            experiment_id: Experiment identifier
            n_samples: Number of sample user IDs to test

        Returns:
            Dictionary mapping variant to count
        """
        if experiment_id in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        distribution = {Variant.CONTROL: 0, Variant.TREATMENT: 0}

        for i in range(n_samples):
            user_id = f"test-user-{i}"
            variant = self.assign_variant(experiment_id, user_id)
            distribution[variant] += 1

        return distribution

    def xǁABTestFrameworkǁget_variant_distribution__mutmut_3(
        self, experiment_id: str, n_samples: int = 1000
    ) -> Dict[Variant, int]:
        """
        Get distribution of variant assignments over n_samples users.

        Useful for validating 50/50 split.

        Args:
            experiment_id: Experiment identifier
            n_samples: Number of sample user IDs to test

        Returns:
            Dictionary mapping variant to count
        """
        if experiment_id not in self._experiments:
            raise ValueError(None)

        distribution = {Variant.CONTROL: 0, Variant.TREATMENT: 0}

        for i in range(n_samples):
            user_id = f"test-user-{i}"
            variant = self.assign_variant(experiment_id, user_id)
            distribution[variant] += 1

        return distribution

    def xǁABTestFrameworkǁget_variant_distribution__mutmut_4(
        self, experiment_id: str, n_samples: int = 1000
    ) -> Dict[Variant, int]:
        """
        Get distribution of variant assignments over n_samples users.

        Useful for validating 50/50 split.

        Args:
            experiment_id: Experiment identifier
            n_samples: Number of sample user IDs to test

        Returns:
            Dictionary mapping variant to count
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        distribution = None

        for i in range(n_samples):
            user_id = f"test-user-{i}"
            variant = self.assign_variant(experiment_id, user_id)
            distribution[variant] += 1

        return distribution

    def xǁABTestFrameworkǁget_variant_distribution__mutmut_5(
        self, experiment_id: str, n_samples: int = 1000
    ) -> Dict[Variant, int]:
        """
        Get distribution of variant assignments over n_samples users.

        Useful for validating 50/50 split.

        Args:
            experiment_id: Experiment identifier
            n_samples: Number of sample user IDs to test

        Returns:
            Dictionary mapping variant to count
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        distribution = {Variant.CONTROL: 1, Variant.TREATMENT: 0}

        for i in range(n_samples):
            user_id = f"test-user-{i}"
            variant = self.assign_variant(experiment_id, user_id)
            distribution[variant] += 1

        return distribution

    def xǁABTestFrameworkǁget_variant_distribution__mutmut_6(
        self, experiment_id: str, n_samples: int = 1000
    ) -> Dict[Variant, int]:
        """
        Get distribution of variant assignments over n_samples users.

        Useful for validating 50/50 split.

        Args:
            experiment_id: Experiment identifier
            n_samples: Number of sample user IDs to test

        Returns:
            Dictionary mapping variant to count
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        distribution = {Variant.CONTROL: 0, Variant.TREATMENT: 1}

        for i in range(n_samples):
            user_id = f"test-user-{i}"
            variant = self.assign_variant(experiment_id, user_id)
            distribution[variant] += 1

        return distribution

    def xǁABTestFrameworkǁget_variant_distribution__mutmut_7(
        self, experiment_id: str, n_samples: int = 1000
    ) -> Dict[Variant, int]:
        """
        Get distribution of variant assignments over n_samples users.

        Useful for validating 50/50 split.

        Args:
            experiment_id: Experiment identifier
            n_samples: Number of sample user IDs to test

        Returns:
            Dictionary mapping variant to count
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        distribution = {Variant.CONTROL: 0, Variant.TREATMENT: 0}

        for i in range(None):
            user_id = f"test-user-{i}"
            variant = self.assign_variant(experiment_id, user_id)
            distribution[variant] += 1

        return distribution

    def xǁABTestFrameworkǁget_variant_distribution__mutmut_8(
        self, experiment_id: str, n_samples: int = 1000
    ) -> Dict[Variant, int]:
        """
        Get distribution of variant assignments over n_samples users.

        Useful for validating 50/50 split.

        Args:
            experiment_id: Experiment identifier
            n_samples: Number of sample user IDs to test

        Returns:
            Dictionary mapping variant to count
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        distribution = {Variant.CONTROL: 0, Variant.TREATMENT: 0}

        for i in range(n_samples):
            user_id = None
            variant = self.assign_variant(experiment_id, user_id)
            distribution[variant] += 1

        return distribution

    def xǁABTestFrameworkǁget_variant_distribution__mutmut_9(
        self, experiment_id: str, n_samples: int = 1000
    ) -> Dict[Variant, int]:
        """
        Get distribution of variant assignments over n_samples users.

        Useful for validating 50/50 split.

        Args:
            experiment_id: Experiment identifier
            n_samples: Number of sample user IDs to test

        Returns:
            Dictionary mapping variant to count
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        distribution = {Variant.CONTROL: 0, Variant.TREATMENT: 0}

        for i in range(n_samples):
            user_id = f"test-user-{i}"
            variant = None
            distribution[variant] += 1

        return distribution

    def xǁABTestFrameworkǁget_variant_distribution__mutmut_10(
        self, experiment_id: str, n_samples: int = 1000
    ) -> Dict[Variant, int]:
        """
        Get distribution of variant assignments over n_samples users.

        Useful for validating 50/50 split.

        Args:
            experiment_id: Experiment identifier
            n_samples: Number of sample user IDs to test

        Returns:
            Dictionary mapping variant to count
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        distribution = {Variant.CONTROL: 0, Variant.TREATMENT: 0}

        for i in range(n_samples):
            user_id = f"test-user-{i}"
            variant = self.assign_variant(None, user_id)
            distribution[variant] += 1

        return distribution

    def xǁABTestFrameworkǁget_variant_distribution__mutmut_11(
        self, experiment_id: str, n_samples: int = 1000
    ) -> Dict[Variant, int]:
        """
        Get distribution of variant assignments over n_samples users.

        Useful for validating 50/50 split.

        Args:
            experiment_id: Experiment identifier
            n_samples: Number of sample user IDs to test

        Returns:
            Dictionary mapping variant to count
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        distribution = {Variant.CONTROL: 0, Variant.TREATMENT: 0}

        for i in range(n_samples):
            user_id = f"test-user-{i}"
            variant = self.assign_variant(experiment_id, None)
            distribution[variant] += 1

        return distribution

    def xǁABTestFrameworkǁget_variant_distribution__mutmut_12(
        self, experiment_id: str, n_samples: int = 1000
    ) -> Dict[Variant, int]:
        """
        Get distribution of variant assignments over n_samples users.

        Useful for validating 50/50 split.

        Args:
            experiment_id: Experiment identifier
            n_samples: Number of sample user IDs to test

        Returns:
            Dictionary mapping variant to count
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        distribution = {Variant.CONTROL: 0, Variant.TREATMENT: 0}

        for i in range(n_samples):
            user_id = f"test-user-{i}"
            variant = self.assign_variant(user_id)
            distribution[variant] += 1

        return distribution

    def xǁABTestFrameworkǁget_variant_distribution__mutmut_13(
        self, experiment_id: str, n_samples: int = 1000
    ) -> Dict[Variant, int]:
        """
        Get distribution of variant assignments over n_samples users.

        Useful for validating 50/50 split.

        Args:
            experiment_id: Experiment identifier
            n_samples: Number of sample user IDs to test

        Returns:
            Dictionary mapping variant to count
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        distribution = {Variant.CONTROL: 0, Variant.TREATMENT: 0}

        for i in range(n_samples):
            user_id = f"test-user-{i}"
            variant = self.assign_variant(experiment_id, )
            distribution[variant] += 1

        return distribution

    def xǁABTestFrameworkǁget_variant_distribution__mutmut_14(
        self, experiment_id: str, n_samples: int = 1000
    ) -> Dict[Variant, int]:
        """
        Get distribution of variant assignments over n_samples users.

        Useful for validating 50/50 split.

        Args:
            experiment_id: Experiment identifier
            n_samples: Number of sample user IDs to test

        Returns:
            Dictionary mapping variant to count
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        distribution = {Variant.CONTROL: 0, Variant.TREATMENT: 0}

        for i in range(n_samples):
            user_id = f"test-user-{i}"
            variant = self.assign_variant(experiment_id, user_id)
            distribution[variant] = 1

        return distribution

    def xǁABTestFrameworkǁget_variant_distribution__mutmut_15(
        self, experiment_id: str, n_samples: int = 1000
    ) -> Dict[Variant, int]:
        """
        Get distribution of variant assignments over n_samples users.

        Useful for validating 50/50 split.

        Args:
            experiment_id: Experiment identifier
            n_samples: Number of sample user IDs to test

        Returns:
            Dictionary mapping variant to count
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        distribution = {Variant.CONTROL: 0, Variant.TREATMENT: 0}

        for i in range(n_samples):
            user_id = f"test-user-{i}"
            variant = self.assign_variant(experiment_id, user_id)
            distribution[variant] -= 1

        return distribution

    def xǁABTestFrameworkǁget_variant_distribution__mutmut_16(
        self, experiment_id: str, n_samples: int = 1000
    ) -> Dict[Variant, int]:
        """
        Get distribution of variant assignments over n_samples users.

        Useful for validating 50/50 split.

        Args:
            experiment_id: Experiment identifier
            n_samples: Number of sample user IDs to test

        Returns:
            Dictionary mapping variant to count
        """
        if experiment_id not in self._experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        distribution = {Variant.CONTROL: 0, Variant.TREATMENT: 0}

        for i in range(n_samples):
            user_id = f"test-user-{i}"
            variant = self.assign_variant(experiment_id, user_id)
            distribution[variant] += 2

        return distribution
    
    xǁABTestFrameworkǁget_variant_distribution__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁABTestFrameworkǁget_variant_distribution__mutmut_1': xǁABTestFrameworkǁget_variant_distribution__mutmut_1, 
        'xǁABTestFrameworkǁget_variant_distribution__mutmut_2': xǁABTestFrameworkǁget_variant_distribution__mutmut_2, 
        'xǁABTestFrameworkǁget_variant_distribution__mutmut_3': xǁABTestFrameworkǁget_variant_distribution__mutmut_3, 
        'xǁABTestFrameworkǁget_variant_distribution__mutmut_4': xǁABTestFrameworkǁget_variant_distribution__mutmut_4, 
        'xǁABTestFrameworkǁget_variant_distribution__mutmut_5': xǁABTestFrameworkǁget_variant_distribution__mutmut_5, 
        'xǁABTestFrameworkǁget_variant_distribution__mutmut_6': xǁABTestFrameworkǁget_variant_distribution__mutmut_6, 
        'xǁABTestFrameworkǁget_variant_distribution__mutmut_7': xǁABTestFrameworkǁget_variant_distribution__mutmut_7, 
        'xǁABTestFrameworkǁget_variant_distribution__mutmut_8': xǁABTestFrameworkǁget_variant_distribution__mutmut_8, 
        'xǁABTestFrameworkǁget_variant_distribution__mutmut_9': xǁABTestFrameworkǁget_variant_distribution__mutmut_9, 
        'xǁABTestFrameworkǁget_variant_distribution__mutmut_10': xǁABTestFrameworkǁget_variant_distribution__mutmut_10, 
        'xǁABTestFrameworkǁget_variant_distribution__mutmut_11': xǁABTestFrameworkǁget_variant_distribution__mutmut_11, 
        'xǁABTestFrameworkǁget_variant_distribution__mutmut_12': xǁABTestFrameworkǁget_variant_distribution__mutmut_12, 
        'xǁABTestFrameworkǁget_variant_distribution__mutmut_13': xǁABTestFrameworkǁget_variant_distribution__mutmut_13, 
        'xǁABTestFrameworkǁget_variant_distribution__mutmut_14': xǁABTestFrameworkǁget_variant_distribution__mutmut_14, 
        'xǁABTestFrameworkǁget_variant_distribution__mutmut_15': xǁABTestFrameworkǁget_variant_distribution__mutmut_15, 
        'xǁABTestFrameworkǁget_variant_distribution__mutmut_16': xǁABTestFrameworkǁget_variant_distribution__mutmut_16
    }
    
    def get_variant_distribution(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁABTestFrameworkǁget_variant_distribution__mutmut_orig"), object.__getattribute__(self, "xǁABTestFrameworkǁget_variant_distribution__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_variant_distribution.__signature__ = _mutmut_signature(xǁABTestFrameworkǁget_variant_distribution__mutmut_orig)
    xǁABTestFrameworkǁget_variant_distribution__mutmut_orig.__name__ = 'xǁABTestFrameworkǁget_variant_distribution'


# Predefined experiment configurations
EXP_1_CONFIG = ExperimentConfig(
    experiment_id="EXP-1",
    name="Superposition Engine Validation",
    feature="superposition",
    sample_size=100,
    control_description="Classical sequential decision logic",
    treatment_description="Quantum superposition parallel evaluation",
    success_metric="accuracy",
    metadata={
        "target_improvement": 0.15,  # 15% improvement target
        "duration_weeks": 1,
    },
)

EXP_2_CONFIG = ExperimentConfig(
    experiment_id="EXP-2",
    name="Entanglement Manager Validation",
    feature="entanglement",
    sample_size=500,
    control_description="Independent agent execution",
    treatment_description="Entangled agent state synchronization",
    success_metric="redundancy_rate",
    metadata={
        "target_improvement": 0.30,  # 30% redundancy reduction
        "duration_weeks": 1,
    },
)

EXP_3_CONFIG = ExperimentConfig(
    experiment_id="EXP-3",
    name="Uncertainty Optimizer Validation",
    feature="uncertainty",
    sample_size=50,
    control_description="Fixed 90% test coverage",
    treatment_description="Adaptive risk-based coverage",
    success_metric="test_time",
    metadata={
        "target_improvement": 0.25,  # 25% time reduction
        "duration_weeks": 1,
    },
)
