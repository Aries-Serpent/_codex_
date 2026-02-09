"""ML-based Pattern Recognition for Cognitive Brain.

This module provides machine learning capabilities for:
- Symptom classification
- Resolution recommendation
- Success prediction
- Pattern extraction from historical data

Author: GitHub Copilot Coding Agent
Date: 2026-02-05
"""

from __future__ import annotations

from .data_pipeline import (
    DataPipeline,
    DataSourceType,
    FeatureExtractor,
    PatternDataset,
    PatternSample,
    RawDataRecord,
    TrainingDataGenerator,
    create_pipeline_from_defaults,
)
from .integration import (
    BrainMLBridge,
    EnhancedAgentRouter,
    IntegratedPipeline,
    MLEnhancedPatternMatcher,
    MLEnhancedQueryResult,
    RoutingDecision,
    create_integrated_pipeline,
    enhance_brain_with_ml,
)
from .recommender import (
    CosineSimilarity,
    JaccardSimilarity,
    Recommendation,
    RecommendationResult,
    ResolutionIndex,
    ResolutionRecommender,
    SuccessPredictor,
)
from .symptom_classifier import (
    ClassificationResult,
    NaiveBayesClassifier,
    SymptomClassifier,
    TfidfVectorizer,
)
from .validation import (
    HyperparameterTuner,
    MetricType,
    ModelRegistry,
    ModelValidator,
    ModelVersion,
    PerformanceRecord,
    PerformanceTracker,
    TuningPipeline,
    TuningResult,
    ValidationMetrics,
    create_registry,
    create_tracker,
    create_tuner,
    create_tuning_pipeline,
    create_validator,
)

__all__ = [
    # Data Pipeline
    "DataPipeline",
    "DataSourceType",
    "FeatureExtractor",
    "PatternDataset",
    "PatternSample",
    "RawDataRecord",
    "TrainingDataGenerator",
    "create_pipeline_from_defaults",
    # Symptom Classifier
    "ClassificationResult",
    "NaiveBayesClassifier",
    "SymptomClassifier",
    "TfidfVectorizer",
    # Recommender
    "CosineSimilarity",
    "JaccardSimilarity",
    "Recommendation",
    "RecommendationResult",
    "ResolutionIndex",
    "ResolutionRecommender",
    "SuccessPredictor",
    # Integration
    "BrainMLBridge",
    "EnhancedAgentRouter",
    "IntegratedPipeline",
    "MLEnhancedPatternMatcher",
    "MLEnhancedQueryResult",
    "RoutingDecision",
    "create_integrated_pipeline",
    "enhance_brain_with_ml",
    # Validation & Tuning
    "HyperparameterTuner",
    "MetricType",
    "ModelRegistry",
    "ModelValidator",
    "ModelVersion",
    "PerformanceRecord",
    "PerformanceTracker",
    "TuningPipeline",
    "TuningResult",
    "ValidationMetrics",
    "create_registry",
    "create_tracker",
    "create_tuner",
    "create_tuning_pipeline",
    "create_validator",
]
