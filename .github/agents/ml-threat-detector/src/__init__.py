"""ML Threat Detector Agent Package."""

__version__ = "1.0.0"
__author__ = "Copilot Agent System"

from .feature_extraction import FeatureExtractor, SecurityFeatures
from .ml_model import MLThreatDetector, ThreatFeatures

__all__ = ["MLThreatDetector", "ThreatFeatures", "FeatureExtractor", "SecurityFeatures"]
