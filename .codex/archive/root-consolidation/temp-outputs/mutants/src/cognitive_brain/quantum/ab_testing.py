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
from typing import Any, Optional

from cognitive_brain.models.quantum_metrics import (
    QuantumMetric,
    QuantumMetricRepository,
)


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
    metadata: dict[str, Any] = field(default_factory=dict)

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
    confidence_interval: tuple[float, float]
    is_significant: bool
    effect_size: float

    def to_dict(self) -> dict[str, Any]:
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

    def __init__(self, repository: QuantumMetricRepository):
        """
        Initialize A/B testing framework.

        Args:
            repository: Database repository for metrics
        """
        self.repository = repository
        self._experiments: dict[str, ExperimentConfig] = {}
        self._assignments: dict[tuple[str, str], Variant] = {}  # (exp_id, user_id) -> variant

    def create_experiment(self, config: ExperimentConfig) -> None:
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

    def get_experiment(self, experiment_id: str) -> Optional[ExperimentConfig]:
        """
        Get experiment configuration.

        Args:
            experiment_id: Experiment identifier

        Returns:
            ExperimentConfig if found, None otherwise
        """
        return self._experiments.get(experiment_id)

    def assign_variant(self, experiment_id: str, user_id: str) -> Variant:
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
        hash_input = f"{experiment_id}:{user_id}".encode()
        hash_value = hashlib.sha256(hash_input).hexdigest()
        hash_int = int(hash_value, 16)

        # 50/50 split based on hash parity
        variant = Variant.TREATMENT if hash_int % 2 == 0 else Variant.CONTROL

        # Cache assignment
        self._assignments[key] = variant

        return variant

    def get_assignment(self, experiment_id: str, user_id: str) -> Optional[Variant]:
        """
        Get existing variant assignment.

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant if exists, None otherwise
        """
        return self._assignments.get((experiment_id, user_id))

    def record_metric(
        self,
        experiment_id: str,
        user_id: str,
        metric_value: float,
        metadata: Optional[dict[str, Any]] = None,
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

    def get_variant_metrics(self, experiment_id: str, variant: Variant) -> list[float]:
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

    def analyze_experiment(self, experiment_id: str, alpha: float = 0.05) -> ExperimentResult:
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
        _t_stat, p_value = self._two_sample_ttest(
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

    def _calculate_std(self, values: list[float], mean: float) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0

        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)

    def _two_sample_ttest(
        self,
        control: list[float],
        treatment: list[float],
        control_mean: float,
        treatment_mean: float,
        control_std: float,
        treatment_std: float,
    ) -> tuple[float, float]:
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

    def _welch_df(self, std1: float, std2: float, n1: int, n2: int) -> float:
        """Calculate Welch-Satterthwaite degrees of freedom."""
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)

        numerator = ((std1**2 / n1) + (std2**2 / n2)) ** 2
        denominator = (std1**4 / (n1**2 * (n1 - 1))) + (std2**4 / (n2**2 * (n2 - 1)))

        if denominator == 0:
            return float(n1 + n2 - 2)

        return numerator / denominator

    def _t_distribution_pvalue(self, t_stat: float, df: float) -> float:
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

    def _normal_cdf(self, x: float) -> float:
        """Cumulative distribution function for standard normal distribution."""
        # Using error function approximation
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    def _confidence_interval(
        self,
        mean1: float,
        mean2: float,
        std1: float,
        std2: float,
        n1: int,
        n2: int,
        alpha: float,
    ) -> tuple[float, float]:
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

    def get_variant_distribution(
        self, experiment_id: str, n_samples: int = 1000
    ) -> dict[Variant, int]:
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
