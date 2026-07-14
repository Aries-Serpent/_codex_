"""
Predictive Capacity Planning Module

Provides time-series forecasting, bottleneck prediction, and automated 
provisioning recommendations for proactive capacity management.

Planset 012 core modules:
- models: ARIMA + Prophet ensemble models
- arima_prophet_ensemble: Bottleneck detection + CAPEX recommendations
- fastapi_server: REST API for forecasting and recommendations
"""

# Planset 012 core modules
try:
    from .models import ARIMAModel, ProphetModel, EnsembleForecaster, EnsembleConfig
except ImportError:
    pass

try:
    from .arima_prophet_ensemble import (
        BottleneckPredictor,
        CapexRecommendationEngine,
        BottleneckAlert,
        CascadingAnalysis,
        ParetoOptimizationResult,
    )
except ImportError:
    pass

# Legacy modules (optional imports)
try:
    from .capacity_planner import TimeSeriesForecaster
except ImportError:
    pass

try:
    from .bottleneck_predictor import BottleneckPredictor as LegacyBottleneckPredictor
except ImportError:
    pass

try:
    from .provisioning_recommender import ProvisioningRecommender
except ImportError:
    pass

try:
    from .dashboard_generator import DashboardGenerator
except ImportError:
    pass

try:
    from .fastapi_server import create_app
except ImportError:
    pass

__all__ = [
    # Planset 012 core
    "ARIMAModel",
    "ProphetModel",
    "EnsembleForecaster",
    "EnsembleConfig",
    "BottleneckPredictor",
    "CapexRecommendationEngine",
    "BottleneckAlert",
    "CascadingAnalysis",
    "ParetoOptimizationResult",
    "create_app",
    # Legacy
    "TimeSeriesForecaster",
    "ProvisioningRecommender",
    "DashboardGenerator",
]
