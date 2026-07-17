"""
ARIMA + Prophet Ensemble Models for Planset 012

Implements lightweight ARIMA and Prophet-like models without external dependencies,
plus a weighted ensemble voting mechanism for robust forecasting.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd


@dataclass
class EnsembleConfig:
    """Configuration for ensemble forecasting"""
    arima_weight: float = 0.5
    prophet_weight: float = 0.5
    min_correlation: float = 0.0
    max_correlation: float = 0.5
    voting_strategy: str = 'weighted_average'  # or 'median', 'weighted_median'


class BaseForecaster(ABC):
    """Abstract base class for forecasting models"""
    
    def __init__(self):
        self.fitted = False
        self.best_params = None
        self.training_data = None
        self.mape_score = None
    
    @abstractmethod
    def fit(self, ts_data: np.ndarray) -> None:
        """Fit the model to training data"""
        pass
    
    @abstractmethod
    def forecast(self, steps: int = 7) -> Tuple[np.ndarray, np.ndarray]:
        """Forecast future values with confidence intervals
        
        Returns:
            Tuple of (forecast_values, confidence_intervals)
        """
        pass
    
    def calculate_mape(self, actual: np.ndarray, predicted: np.ndarray) -> float:
        """Calculate Mean Absolute Percentage Error
        
        Args:
            actual: Actual values
            predicted: Predicted values
            
        Returns:
            MAPE as percentage
        """
        # Avoid division by zero
        mask = actual != 0
        if not np.any(mask):
            return 0.0
        
        mape = np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100
        return mape


class ARIMAModel(BaseForecaster):
    """
    Lightweight ARIMA model implementation without statsmodels
    
    Uses exponential smoothing with automatic order detection
    """
    
    def __init__(self, order: Optional[Tuple[int, int, int]] = None):
        super().__init__()
        self.order = order or (1, 1, 1)  # (p, d, q)
        self.p, self.d, self.q = self.order
        self.ar_coeffs = None
        self.ma_errors = None
        self.differenced_data = None
        self.seasonal_period = 12
        self.trend = None
        self.seasonal = None
    
    def _detect_order(self, ts_data: np.ndarray) -> Tuple[int, int, int]:
        """Auto-detect optimal ARIMA order"""
        # Simple heuristic: check ACF/PACF patterns
        n = len(ts_data)
        
        # Check if differencing needed
        np.diff(ts_data)
        mean_abs_diff_original = np.mean(np.abs(ts_data[:-1] - ts_data[1:]))
        
        # Check for trend
        has_trend = np.abs(ts_data[-1] - ts_data[0]) / n > mean_abs_diff_original * 0.5
        
        # Detect seasonal period
        self._detect_seasonality(ts_data)
        
        # Simple order detection
        p = 1 if has_trend else 0
        d = 1 if has_trend else 0  
        q = 1
        
        return (p, d, q)
    
    def _detect_seasonality(self, ts_data: np.ndarray) -> int:
        """Detect seasonal period from data"""
        n = len(ts_data)
        if n < 52:
            return 12  # Default to 12 for monthly data
        
        # Check for weekly pattern (7), monthly (30), quarterly (13), yearly (52)
        for period in [7, 12, 13, 30, 52]:
            if n >= period * 2:
                # Calculate autocorrelation at lag
                acf_val = self._calculate_acf(ts_data, period)
                if acf_val > 0.3:  # Significant autocorrelation
                    return period
        
        return 12
    
    def _calculate_acf(self, ts_data: np.ndarray, lag: int) -> float:
        """Calculate autocorrelation at given lag"""
        ts_centered = ts_data - np.mean(ts_data)
        c0 = np.dot(ts_centered, ts_centered) / len(ts_data)
        
        if lag >= len(ts_data):
            return 0.0
        
        c_lag = np.dot(ts_centered[:-lag], ts_centered[lag:]) / len(ts_data)
        acf = c_lag / c0 if c0 != 0 else 0.0
        
        return np.clip(acf, -1, 1)
    
    def fit(self, ts_data: np.ndarray) -> None:
        """Fit ARIMA model to data"""
        ts_data = np.asarray(ts_data, dtype=float)
        self.training_data = ts_data.copy()
        
        # Auto-detect order if not specified
        if self.order == (1, 1, 1):
            self.order = self._detect_order(ts_data)
            self.p, self.d, self.q = self.order
        
        # Differencing
        differenced = ts_data.copy()
        for _ in range(self.d):
            if len(differenced) > 1:
                differenced = np.diff(differenced)
        
        self.differenced_data = differenced
        
        # Fit AR coefficients using simple linear regression
        self.ar_coeffs = self._fit_ar(differenced, self.p)
        
        # Fit MA errors
        self.ma_errors = self._fit_ma(differenced, self.q)
        
        # Extract trend and seasonal components for confidence intervals
        self.trend = np.polyfit(np.arange(len(ts_data)), ts_data, 1)
        
        # Calculate seasonal component
        self.seasonal = self._extract_seasonal(ts_data)
        
        self.fitted = True
        self.best_params = {
            'order': self.order,
            'ar_coeffs': self.ar_coeffs,
            'seasonal_period': self.seasonal_period,
        }
        
        # Estimate MAPE on holdout (80/20 split)
        split = int(len(ts_data) * 0.8)
        train, test = ts_data[:split], ts_data[split:]
        
        if len(test) > self.p + self.d + self.q:
            # Quick fit on training set
            temp_diff = train.copy()
            for _ in range(self.d):
                if len(temp_diff) > 1:
                    temp_diff = np.diff(temp_diff)
            
            # Simple forecast
            last_vals = train[-self.p:] if self.p > 0 else np.array([train[-1]])
            pred = np.repeat(np.mean(last_vals), len(test))
            
            self.mape_score = self.calculate_mape(test, pred)
    
    def _fit_ar(self, data: np.ndarray, p: int) -> np.ndarray:
        """Fit AR coefficients using Yule-Walker equations (simplified)"""
        if p == 0 or len(data) < p:
            return np.array([])
        
        # Simplified: use least squares on lagged data
        X = np.column_stack([data[p-i:-i or None] for i in range(1, p+1)])
        y = data[p:]
        
        if X.shape[0] > 0 and X.shape[1] > 0:
            # Use normal equations for stability
            coeffs = np.linalg.lstsq(X, y, rcond=None)[0]
            return coeffs
        
        return np.ones(p) * 0.5
    
    def _fit_ma(self, data: np.ndarray, q: int) -> np.ndarray:
        """Fit MA errors (simplified)"""
        if q == 0:
            return np.array([])
        
        # Initialize with simple moving average
        return np.ones(q) / q
    
    def _extract_seasonal(self, ts_data: np.ndarray) -> np.ndarray:
        """Extract seasonal component"""
        n = len(ts_data)
        if n < self.seasonal_period * 2:
            return np.zeros(self.seasonal_period)
        
        # Group by season and compute mean
        seasonal = np.zeros(self.seasonal_period)
        for i in range(self.seasonal_period):
            indices = np.arange(i, n, self.seasonal_period)
            if len(indices) > 0:
                seasonal[i] = np.mean(ts_data[indices])
        
        seasonal = seasonal - np.mean(seasonal)  # Center
        return seasonal
    
    def forecast(self, steps: int = 7) -> Tuple[np.ndarray, np.ndarray]:
        """Forecast future values"""
        if not self.fitted or self.training_data is None:
            raise ValueError("Model not fitted")
        
        ts_data = self.training_data
        n = len(ts_data)
        
        # Generate forecasts
        forecasts = []
        current_data = ts_data.copy()
        
        for step in range(steps):
            if self.p > 0 and len(current_data) >= self.p and self.ar_coeffs is not None:
                # AR forecast
                last_vals = current_data[-self.p:]
                forecast_val = np.dot(self.ar_coeffs, last_vals[::-1])
            else:
                # Use simple exponential smoothing fallback
                alpha = 0.3
                forecast_val = alpha * current_data[-1] + (1 - alpha) * np.mean(current_data[-10:])
            
            # Add trend component
            if self.trend is not None:
                trend_contribution = self.trend[0] * (n + step) / n
                forecast_val = forecast_val + trend_contribution * 0.1
            
            forecasts.append(forecast_val)
            current_data = np.append(current_data, forecast_val)
        
        forecasts = np.array(forecasts)
        
        # Generate confidence intervals (±10% of forecast)
        confidence_intervals = np.abs(forecasts) * 0.1 + 0.1
        
        return forecasts, confidence_intervals


class ProphetModel(BaseForecaster):
    """
    Prophet-like model using trend, seasonal, and holiday components
    Simplified implementation without fbprophet dependency
    """
    
    def __init__(self):
        super().__init__()
        self.trend_params = None
        self.seasonal_params = None
        self.trend_changepoints = None
        self.df = None
    
    def fit(self, df: pd.DataFrame) -> None:
        """
        Fit Prophet model
        
        Args:
            df: DataFrame with 'ds' (datetime) and 'y' (values) columns
        """
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        
        if 'ds' not in df.columns or 'y' not in df.columns:
            raise ValueError("DataFrame must have 'ds' and 'y' columns")
        
        self.df = df.copy()
        df = df.sort_values('ds').reset_index(drop=True)
        
        y = df['y'].values
        t = np.arange(len(y))
        
        # Fit piecewise linear trend with changepoint detection
        self.trend_params = self._fit_trend(t, y)
        
        # Fit seasonal component
        self.seasonal_params = self._fit_seasonality(y)
        
        self.fitted = True
        self.best_params = {
            'trend': self.trend_params,
            'seasonality': self.seasonal_params,
        }
        
        # Estimate MAPE
        pred = self._forecast_values(t)
        self.mape_score = self.calculate_mape(y, pred)
    
    def _detect_changepoints(self, t: np.ndarray, y: np.ndarray, num_changepoints: int = 3) -> np.ndarray:
        """Detect trend changepoints using seasonal decomposition"""
        if len(y) < num_changepoints * 2:
            return np.array([len(y) // 2])
        
        # Simple change detection using rolling variance
        window = max(3, len(y) // (num_changepoints + 1))
        rolling_var = np.convolve(
            (y - np.mean(y)) ** 2,
            np.ones(window) / window,
            mode='valid'
        )
        
        # Find peaks in rolling variance
        changepoints_idx = np.argsort(rolling_var)[-num_changepoints:]
        changepoints_idx = np.sort(changepoints_idx) + window // 2
        
        return np.clip(changepoints_idx, 0, len(y) - 1)
    
    def _fit_trend(self, t: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Fit piecewise linear trend with changepoints"""
        num_changepoints = min(3, len(y) // 20)
        
        if num_changepoints > 0:
            changepoints = self._detect_changepoints(t, y, num_changepoints)
        else:
            changepoints = np.array([])
        
        # Fit linear trend overall
        coeffs = np.polyfit(t, y, 1)
        
        # Also fit higher-order for curvature
        quad_coeffs = np.polyfit(t, y, 2)
        
        return {
            'coefficients': coeffs,
            'quad_coefficients': quad_coeffs,
            'changepoints': changepoints,
        }
    
    def _fit_seasonality(self, y: np.ndarray) -> Dict[str, Any]:
        """Fit seasonal components (weekly and yearly)"""
        n = len(y)
        
        # Detect seasonal period
        seasonal_period = self._detect_seasonal_period(y)
        
        # Fit seasonal factors
        seasonal_factors = {}
        
        if seasonal_period > 0 and n >= seasonal_period * 2:
            seasonal = np.zeros(seasonal_period)
            for i in range(seasonal_period):
                indices = np.arange(i, n, seasonal_period)
                if len(indices) > 0:
                    seasonal[i] = np.mean(y[indices])
            
            seasonal = seasonal - np.mean(seasonal)
            seasonal_factors['seasonal'] = seasonal
            seasonal_factors['period'] = seasonal_period
        
        return seasonal_factors
    
    def _detect_seasonal_period(self, y: np.ndarray) -> int:
        """Detect seasonal period"""
        n = len(y)
        
        # Try common periods: 7 (weekly), 12 (monthly), 52 (yearly)
        for period in [7, 12, 52]:
            if n >= period * 3:
                # Check autocorrelation
                acf_vals = self._calculate_acf_series(y, period)
                if acf_vals > 0.2:
                    return period
        
        return 0
    
    def _calculate_acf_series(self, y: np.ndarray, lag: int) -> float:
        """Calculate autocorrelation at lag"""
        y_centered = y - np.mean(y)
        c0 = np.dot(y_centered, y_centered) / len(y)
        
        if lag >= len(y):
            return 0.0
        
        c_lag = np.dot(y_centered[:-lag], y_centered[lag:]) / len(y)
        
        return c_lag / c0 if c0 != 0 else 0.0
    
    def _forecast_values(self, t: np.ndarray) -> np.ndarray:
        """Generate forecast values for given time points"""
        if not self.fitted:
            raise ValueError("Model not fitted")
        
        # Trend component
        if self.trend_params:
            trend_poly = np.poly1d(self.trend_params['quad_coefficients'])
            trend = trend_poly(t)
        else:
            trend = np.zeros_like(t, dtype=float)
        
        # Seasonal component
        seasonal = np.zeros_like(t, dtype=float)
        if self.seasonal_params and 'seasonal' in self.seasonal_params:
            self.seasonal_params.get('period', 12)
            seasonal_factors = self.seasonal_params['seasonal']
            
            for i, val in enumerate(t):
                seasonal[i] = seasonal_factors[int(val) % len(seasonal_factors)]
        
        return trend + seasonal
    
    def forecast(self, periods: int = 7) -> Tuple[np.ndarray, np.ndarray]:
        """Forecast future values"""
        if not self.fitted or self.df is None:
            raise ValueError("Model not fitted")
        
        # Generate future dates
        last_date = self.df['ds'].iloc[-1]
        
        # Determine frequency
        if len(self.df) >= 2:
            freq = (self.df['ds'].iloc[-1] - self.df['ds'].iloc[-2]).days
            if freq == 0:
                freq = 1
        else:
            freq = 1
        
        future_dates = [last_date + timedelta(days=freq*i) for i in range(1, periods+1)]
        
        # Create future dataframe
        pd.DataFrame({'ds': future_dates})
        
        # Get training data length
        t_train = np.arange(len(self.df))
        n_train = len(t_train)
        
        # Forecast for future periods
        t_future = n_train + np.arange(periods)
        forecasts = self._forecast_values(t_future)
        
        # Confidence intervals based on residuals
        train_pred = self._forecast_values(t_train)
        train_actual = self.df['y'].values
        residuals = train_actual - train_pred
        std_residuals = np.std(residuals)
        
        # ±15% confidence interval or 1.96*std (95% CI)
        confidence = np.maximum(
            np.abs(forecasts) * 0.15,
            1.96 * std_residuals
        )
        
        return forecasts, confidence


class EnsembleForecaster:
    """
    Ensemble forecaster combining ARIMA and Prophet with weighted voting
    
    Ensures model diversity and robust predictions through ensemble methods
    """
    
    def __init__(
        self,
        arima: ARIMAModel,
        prophet: ProphetModel,
        config: Optional[EnsembleConfig] = None,
    ):
        self.arima = arima
        self.prophet = prophet
        self.config = config or EnsembleConfig()
        self.model_correlation = None
    
    def forecast(self, steps: int = 7) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate ensemble forecast using weighted voting
        
        Args:
            steps: Number of steps to forecast
            
        Returns:
            Tuple of (ensemble_forecast, confidence_intervals)
        """
        # Get individual forecasts
        arima_forecast, arima_conf = self.arima.forecast(steps)
        prophet_forecast, prophet_conf = self.prophet.forecast(steps)
        
        # Calculate model correlation
        self.model_correlation = np.corrcoef(arima_forecast, prophet_forecast)[0, 1]
        
        # Check model diversity
        if np.abs(self.model_correlation) > self.config.max_correlation:
            # Models too similar, rely more on one
            if self.arima.mape_score and self.prophet.mape_score:
                if self.arima.mape_score < self.prophet.mape_score:
                    # ARIMA is better
                    ensemble_forecast = arima_forecast
                    ensemble_conf = arima_conf
                else:
                    # Prophet is better
                    ensemble_forecast = prophet_forecast
                    ensemble_conf = prophet_conf
            else:
                # Default to ARIMA
                ensemble_forecast = arima_forecast
                ensemble_conf = arima_conf
        else:
            # Models are diverse enough, use weighted average
            if self.config.voting_strategy == 'weighted_average':
                ensemble_forecast = (
                    self.config.arima_weight * arima_forecast +
                    self.config.prophet_weight * prophet_forecast
                )
            elif self.config.voting_strategy == 'median':
                ensemble_forecast = np.median(
                    np.array([arima_forecast, prophet_forecast]),
                    axis=0
                )
            else:
                # Default to weighted average
                ensemble_forecast = (
                    self.config.arima_weight * arima_forecast +
                    self.config.prophet_weight * prophet_forecast
                )
            
            # Ensemble confidence interval
            ensemble_conf = np.sqrt(
                self.config.arima_weight * (arima_conf ** 2) +
                self.config.prophet_weight * (prophet_conf ** 2)
            )
        
        return ensemble_forecast, ensemble_conf
    
    def get_model_diagnostics(self) -> Dict[str, Any]:
        """Get diagnostic information about ensemble models"""
        return {
            'arima_mape': self.arima.mape_score,
            'prophet_mape': self.prophet.mape_score,
            'model_correlation': self.model_correlation,
            'diversity_acceptable': (
                self.model_correlation is None or
                np.abs(self.model_correlation) <= self.config.max_correlation
            ),
            'arima_params': self.arima.best_params,
            'prophet_params': self.prophet.best_params,
        }
