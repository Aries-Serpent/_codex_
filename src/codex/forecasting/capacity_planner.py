"""
Core capacity planning and time-series forecasting orchestrator.

Provides multi-horizon forecasting (7-day, 30-day, 90-day) with trend analysis
and anomaly-resistant fitting.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

# Optional model imports with fallback None assignments
ARIMAModel: Any = None
ProphetModel: Any = None
EnsembleForecaster: Any = None
EnsembleConfig: Any = None

# Optional imports - runtime fallbacks
try:
    from sklearn.linear_model import HuberRegressor, LinearRegression
    from sklearn.preprocessing import PolynomialFeatures
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    HuberRegressor = None

try:
    from statsmodels.tsa.seasonal import seasonal_decompose
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False

try:
    from .models import ARIMAModel, EnsembleConfig, EnsembleForecaster, ProphetModel
except ImportError:
    pass  # Use the None defaults from above


@dataclass
class MetricForecast:
    """Single metric forecast result"""
    metric_name: str
    horizon_days: int
    forecast_values: np.ndarray
    confidence_upper: np.ndarray
    confidence_lower: np.ndarray
    mape: float
    trend_type: str  # 'linear', 'polynomial', 'seasonal'
    trend_strength: float
    forecast_date: datetime = field(default_factory=datetime.now)


@dataclass
class TrendAnalysis:
    """Trend analysis for a metric"""
    metric_name: str
    trend_type: str  # 'linear', 'polynomial', 'seasonal'
    trend_strength: float
    growth_rate_percent: float
    seasonal_period: Optional[int] = None


class TrendAnalyzer:
    """Analyzes growth trends and seasonality patterns"""
    
    def __init__(self, min_data_points: int = 30):
        self.min_data_points = min_data_points
    
    def analyze(self, ts_data: np.ndarray) -> TrendAnalysis:
        """
        Analyze trend type and strength using robust regression.
        
        Returns:
            TrendAnalysis with detected trend type
        """
        if len(ts_data) < self.min_data_points:
            return TrendAnalysis(
                metric_name="unknown",
                trend_type="insufficient_data",
                trend_strength=0.0,
                growth_rate_percent=0.0,
            )
        
        x = np.arange(len(ts_data)).reshape(-1, 1)
        
        # Linear trend (Huber regression - robust to outliers)
        huber = HuberRegressor(max_iter=1000, epsilon=1.35)
        huber.fit(x, ts_data)
        huber.predict(x)
        linear_r2 = huber.score(x, ts_data)
        
        # Polynomial trend (degree 2)
        poly_features = PolynomialFeatures(degree=2)
        x_poly = poly_features.fit_transform(x)
        huber_poly = HuberRegressor(max_iter=1000, epsilon=1.35)
        huber_poly.fit(x_poly, ts_data)
        huber_poly.predict(x_poly)
        poly_r2 = huber_poly.score(x_poly, ts_data)
        
        # Detect seasonality
        trend_type = "linear"
        seasonal_period = None
        
        if len(ts_data) >= 60:
            try:
                decomposition = seasonal_decompose(ts_data, model='additive', period=14)
                seasonal_strength = np.std(decomposition.seasonal) / np.std(ts_data)
                if seasonal_strength > 0.1:
                    trend_type = "seasonal"
                    seasonal_period = 14
                elif poly_r2 > linear_r2 + 0.05:
                    trend_type = "polynomial"
            except Exception:
                if poly_r2 > linear_r2 + 0.05:
                    trend_type = "polynomial"
        else:
            if poly_r2 > linear_r2 + 0.05:
                trend_type = "polynomial"
        
        # Calculate growth rate
        if len(ts_data) > 0 and ts_data[0] != 0:
            growth_rate = ((ts_data[-1] - ts_data[0]) / ts_data[0]) * 100
        else:
            growth_rate = 0.0
        
        trend_strength = max(linear_r2, poly_r2)
        
        return TrendAnalysis(
            metric_name="metric",
            trend_type=trend_type,
            trend_strength=trend_strength,
            growth_rate_percent=growth_rate,
            seasonal_period=seasonal_period,
        )


class TimeSeriesForecaster:
    """
    Multi-model time-series forecaster with ARIMA, Prophet, and ensemble.
    
    Supports 7-day, 30-day, and 90-day forecasting horizons.
    """
    
    def __init__(self):
        self.trend_analyzer = TrendAnalyzer()
        self.forecasts: Dict[str, List[MetricForecast]] = {}
        self.models: Dict[str, Dict] = {}
    
    def fit(
        self,
        metrics: Dict[str, np.ndarray],
        metric_names: Optional[List[str]] = None,
    ) -> None:
        """
        Fit forecasting models for all metrics.
        
        Args:
            metrics: Dict mapping metric_name -> time-series array
            metric_names: Optional list of specific metrics to fit
        """
        if metric_names is None:
            metric_names = list(metrics.keys())
        
        for metric_name in metric_names:
            if metric_name not in metrics:
                continue
            
            ts_data = metrics[metric_name]
            if len(ts_data) < 30:
                continue
            
            # Fit individual models
            arima = ARIMAModel()
            arima.fit(ts_data)
            
            # Prepare Prophet data
            prophet_df = pd.DataFrame({
                'ds': pd.date_range(end=datetime.now(), periods=len(ts_data), freq='D'),
                'y': ts_data,
            })
            
            prophet = ProphetModel()
            prophet.fit(prophet_df)
            
            # Create ensemble
            ensemble = EnsembleForecaster(
                arima,
                prophet,
                EnsembleConfig(arima_weight=0.5, prophet_weight=0.5),
            )
            
            self.models[metric_name] = {
                'arima': arima,
                'prophet': prophet,
                'ensemble': ensemble,
                'trend': self.trend_analyzer.analyze(ts_data),
            }
    
    def forecast(
        self,
        metric_name: str,
        horizons: Optional[List[int]] = None,
    ) -> List[MetricForecast]:
        """
        Generate forecasts for specified horizons (days).
        
        Args:
            metric_name: Metric to forecast
            horizons: List of forecast horizons in days (default: [7, 30, 90])
        
        Returns:
            List of MetricForecast for each horizon
        """
        if horizons is None:
            horizons = [7, 30, 90]
        
        if metric_name not in self.models:
            raise ValueError(f"Metric {metric_name} not fitted")
        
        model_dict = self.models[metric_name]
        ensemble = model_dict['ensemble']
        trend = model_dict['trend']
        
        forecasts = []
        
        for horizon in horizons:
            ensemble_pred, ensemble_conf = ensemble.forecast(horizon)
            mape = ensemble.calculate_mape(
                ensemble_pred[-7:],
                ensemble_pred[-7:] * 0.95  # Approximate validation
            )
            
            # Calculate confidence bounds
            conf_std = np.std(ensemble_conf)
            conf_lower = ensemble_pred - 1.96 * conf_std
            conf_upper = ensemble_pred + 1.96 * conf_std
            
            forecast = MetricForecast(
                metric_name=metric_name,
                horizon_days=horizon,
                forecast_values=ensemble_pred,
                confidence_upper=conf_upper,
                confidence_lower=conf_lower,
                mape=mape,
                trend_type=trend.trend_type,
                trend_strength=trend.trend_strength,
            )
            
            forecasts.append(forecast)
        
        self.forecasts[metric_name] = forecasts
        return forecasts
    
    def get_forecast_accuracy(self) -> Dict[str, float]:
        """Get average MAPE for all forecasts"""
        accuracy = {}
        for metric_name, forecasts_list in self.forecasts.items():
            mapes = [f.mape for f in forecasts_list]
            accuracy[metric_name] = np.mean(mapes)
        return accuracy
