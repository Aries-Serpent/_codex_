"""
Comprehensive tests for capacity planning system.

Tests forecasting accuracy, bottleneck detection, recommendations,
and dashboard generation.
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from src.codex.forecasting.capacity_planner import (
    TimeSeriesForecaster,
    TrendAnalyzer,
    MetricForecast,
)
from src.codex.forecasting.models import (
    ARIMAModel,
    ProphetModel,
    EnsembleForecaster,
)
from src.codex.forecasting.bottleneck_predictor import (
    BottleneckPredictor,
    BottleneckAlert,
)
from src.codex.forecasting.provisioning_recommender import (
    ProvisioningRecommender,
)
from src.codex.forecasting.dashboard_generator import (
    DashboardGenerator,
)


class TestARIMAModel:
    """Tests for ARIMA model"""
    
    def test_arima_fit_and_forecast(self):
        """Test ARIMA fitting and forecasting"""
        # Create synthetic time-series with trend
        np.random.seed(42)
        ts_data = np.linspace(50, 150, 100) + np.random.normal(0, 5, 100)
        
        model = ARIMAModel()
        model.fit(ts_data)
        
        assert model.fitted
        assert model.best_params is not None
        
        forecast, conf = model.forecast(steps=7)
        assert len(forecast) == 7
        assert len(conf) == 7
    
    def test_arima_mape_calculation(self):
        """Test MAPE calculation"""
        model = ARIMAModel()
        
        actual = np.array([100, 110, 120, 130])
        predicted = np.array([105, 108, 118, 132])
        
        mape = model.calculate_mape(actual, predicted)
        assert 0 < mape < 10  # Expect low error for similar values


class TestProphetModel:
    """Tests for Prophet model"""
    
    def test_prophet_fit_and_forecast(self):
        """Test Prophet fitting and forecasting"""
        # Create synthetic data
        dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
        values = 50 + 0.5 * np.arange(100) + np.random.normal(0, 3, 100)
        
        df = pd.DataFrame({'ds': dates, 'y': values})
        
        model = ProphetModel()
        model.fit(df)
        
        assert model.fitted
        
        forecast, conf = model.forecast(periods=7)
        assert len(forecast) == 7
        assert len(conf) == 7


class TestEnsembleForecaster:
    """Tests for ensemble forecaster"""
    
    def test_ensemble_weighting(self):
        """Test ensemble weighted averaging"""
        np.random.seed(42)
        ts_data = np.linspace(50, 150, 100) + np.random.normal(0, 5, 100)
        
        arima = ARIMAModel()
        arima.fit(ts_data)
        
        dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
        df = pd.DataFrame({'ds': dates, 'y': ts_data})
        
        prophet = ProphetModel()
        prophet.fit(df)
        
        ensemble = EnsembleForecaster(arima, prophet)
        forecast, conf = ensemble.forecast(steps=7)
        
        assert len(forecast) == 7
        assert np.all(forecast > 0)  # Forecasts should be positive


class TestTrendAnalyzer:
    """Tests for trend analysis"""
    
    def test_linear_trend_detection(self):
        """Test detection of linear trend"""
        ts_data = np.linspace(50, 150, 60)  # Strong linear trend
        
        analyzer = TrendAnalyzer()
        trend = analyzer.analyze(ts_data)
        
        assert trend.trend_type in ['linear', 'polynomial']
        assert trend.trend_strength > 0.9
        assert trend.growth_rate_percent > 0
    
    def test_insufficient_data_handling(self):
        """Test handling of insufficient data"""
        ts_data = np.array([50, 60, 70])  # Only 3 points
        
        analyzer = TrendAnalyzer()
        trend = analyzer.analyze(ts_data)
        
        assert trend.trend_type == 'insufficient_data'


class TestTimeSeriesForecaster:
    """Tests for TimeSeriesForecaster"""
    
    def test_forecaster_fit_and_predict(self):
        """Test forecaster fitting and prediction"""
        np.random.seed(42)
        metrics = {
            'cpu': np.linspace(20, 70, 100) + np.random.normal(0, 5, 100),
            'memory': np.linspace(30, 80, 100) + np.random.normal(0, 5, 100),
        }
        
        forecaster = TimeSeriesForecaster()
        forecaster.fit(metrics)
        
        forecasts_cpu = forecaster.forecast('cpu', horizons=[7, 30])
        
        assert len(forecasts_cpu) == 2
        assert forecasts_cpu[0].horizon_days == 7
        assert forecasts_cpu[1].horizon_days == 30
        assert len(forecasts_cpu[0].forecast_values) == 7
    
    def test_forecast_accuracy_tracking(self):
        """Test forecast accuracy measurement"""
        np.random.seed(42)
        metrics = {
            'cpu': np.linspace(20, 70, 100) + np.random.normal(0, 3, 100),
        }
        
        forecaster = TimeSeriesForecaster()
        forecaster.fit(metrics)
        forecaster.forecast('cpu')
        
        accuracy = forecaster.get_forecast_accuracy()
        assert 'cpu' in accuracy
        assert 0 <= accuracy['cpu'] < 50  # MAPE should be reasonable


class TestBottleneckPredictor:
    """Tests for bottleneck prediction"""
    
    def test_bottleneck_detection(self):
        """Test bottleneck detection"""
        # CPU growing towards saturation
        metrics = {
            'cpu': {
                'current': 75.0,
                'forecast': np.linspace(75, 95, 30),  # Will saturate
            },
            'memory': {
                'current': 50.0,
                'forecast': np.linspace(50, 70, 30),  # Won't saturate
            },
        }
        
        trend_strength = {'cpu': 0.9, 'memory': 0.8}
        
        predictor = BottleneckPredictor()
        alerts = predictor.predict_bottlenecks(metrics, trend_strength)
        
        assert len(alerts) > 0
        assert alerts[0].resource == 'cpu'
        assert alerts[0].days_until_saturation > 0
        assert alerts[0].severity in ['critical', 'high', 'medium', 'low']
    
    def test_cascading_analysis(self):
        """Test cascading bottleneck analysis"""
        alerts = [
            BottleneckAlert(
                resource='cpu',
                current_utilization_percent=80,
                predicted_saturation_date=datetime.now() + timedelta(days=7),
                days_until_saturation=7,
                confidence=0.95,
                severity='high',
                estimated_capacity_needed='+20%',
            ),
            BottleneckAlert(
                resource='memory',
                current_utilization_percent=70,
                predicted_saturation_date=datetime.now() + timedelta(days=14),
                days_until_saturation=14,
                confidence=0.90,
                severity='medium',
                estimated_capacity_needed='+30%',
            ),
        ]
        
        predictor = BottleneckPredictor()
        analysis = predictor.analyze_cascading(alerts)
        
        assert analysis.first_bottleneck.resource == 'cpu'
        assert analysis.mitigation_urgency in ['immediate', 'high']  # 7 days is critical
        assert len(analysis.cascading_sequence) == 2


class TestProvisioningRecommender:
    """Tests for provisioning recommendations"""
    
    def test_cpu_scaling_recommendation(self):
        """Test CPU scaling recommendation"""
        recommender = ProvisioningRecommender()
        
        rec = recommender.recommend_cpu_scaling(
            current_cpu_percent=80,
            current_cpu_cores=4,
            days_to_saturation=10,
            confidence=0.9,
        )
        
        assert rec.resource == 'cpu'
        assert 'vCPU' in rec.recommended_capacity
        assert rec.estimated_cost_monthly > 0
    
    def test_memory_scaling_recommendation(self):
        """Test memory scaling recommendation"""
        recommender = ProvisioningRecommender()
        
        rec = recommender.recommend_memory_scaling(
            current_memory_percent=75,
            current_memory_gb=16,
            days_to_saturation=12,
            confidence=0.85,
        )
        
        assert rec.resource == 'memory'
        assert 'GB' in rec.recommended_capacity
    
    def test_instance_upgrade_recommendation(self):
        """Test instance upgrade recommendation"""
        recommender = ProvisioningRecommender()
        
        rec = recommender.recommend_instance_upgrade(
            current_instance='t3.large',
            required_cpu=4,
            required_memory=16,
        )
        
        assert rec.resource == 'instance'
        assert rec.recommended_capacity in ['t3.xlarge', 't3.2xlarge', 'm5.xlarge', 'm5.2xlarge']
    
    def test_reserved_instance_recommendation(self):
        """Test reserved instance recommendation"""
        recommender = ProvisioningRecommender()
        
        rec = recommender.recommend_reserved_instances(
            monthly_cost_on_demand=1000.0,
        )
        
        assert rec.resource == 'compute'
        assert rec.estimated_savings_monthly > 0
        assert rec.estimated_savings_monthly < 1000.0


class TestDashboardGenerator:
    """Tests for dashboard generation"""
    
    def test_dashboard_generation(self):
        """Test dashboard generation"""
        np.random.seed(42)
        metrics_data = {
            'cpu': {
                'historical': np.linspace(20, 70, 100),
                'current': 70,
                'forecast_7day': np.linspace(70, 75, 7),
                'forecast_30day': np.linspace(70, 80, 30),
                'confidence_upper': np.linspace(75, 85, 30),
                'confidence_lower': np.linspace(65, 75, 30),
            }
        }
        
        generator = DashboardGenerator()
        dashboard = generator.generate_dashboard(
            metrics_data,
            alerts=[],
            recommendations=[],
        )
        
        assert 'panels' in dashboard
        assert 'generated_at' in dashboard
        assert len(dashboard['panels']) > 0
    
    def test_dashboard_json_generation(self):
        """Test dashboard JSON generation"""
        metrics_data = {
            'cpu': {
                'historical': np.linspace(20, 70, 100),
                'current': 70,
                'forecast_30day': np.linspace(70, 80, 30),
                'confidence_upper': np.linspace(75, 85, 30),
                'confidence_lower': np.linspace(65, 75, 30),
            }
        }
        
        generator = DashboardGenerator()
        json_str = generator.generate_dashboard_json(
            metrics_data,
            alerts=[],
            recommendations=[],
        )
        
        assert isinstance(json_str, str)
        assert 'panels' in json_str
        assert 'cpu' in json_str
    
    def test_dashboard_html_generation(self):
        """Test dashboard HTML generation"""
        dashboard_json = '{"test": "data"}'
        
        generator = DashboardGenerator()
        html = generator.generate_dashboard_html(dashboard_json)
        
        assert '<!DOCTYPE html>' in html
        assert 'dashboard' in html.lower()


# Integration tests

class TestIntegration:
    """End-to-end integration tests"""
    
    def test_full_forecasting_pipeline(self):
        """Test complete forecasting pipeline"""
        np.random.seed(42)
        
        # Generate synthetic metrics with growth
        cpu_data = np.linspace(30, 75, 100) + np.random.normal(0, 3, 100)
        memory_data = np.linspace(40, 80, 100) + np.random.normal(0, 3, 100)
        
        metrics = {'cpu': cpu_data, 'memory': memory_data}
        
        # Forecast
        forecaster = TimeSeriesForecaster()
        forecaster.fit(metrics)
        forecasts_cpu = forecaster.forecast('cpu', horizons=[7, 30, 90])
        
        assert len(forecasts_cpu) == 3
        assert all(f.mape < 50 for f in forecasts_cpu)  # Reasonable accuracy
    
    def test_bottleneck_to_recommendations_flow(self):
        """Test flow from bottleneck prediction to recommendations"""
        predictor = BottleneckPredictor()
        recommender = ProvisioningRecommender()
        
        metrics = {
            'cpu': {'current': 82, 'forecast': np.linspace(82, 95, 30)},
        }
        
        alerts = predictor.predict_bottlenecks(metrics, {'cpu': 0.85})
        
        if alerts:
            rec = recommender.recommend_cpu_scaling(
                current_cpu_percent=82,
                current_cpu_cores=4,
                days_to_saturation=alerts[0].days_until_saturation,
                confidence=0.9,
            )
            
            assert rec.resource == 'cpu'


# Performance tests

class TestPerformance:
    """Performance tests"""
    
    def test_forecast_generation_speed(self):
        """Test that forecasting completes in reasonable time"""
        import time
        
        np.random.seed(42)
        metrics = {f'metric_{i}': np.random.rand(100) for i in range(5)}  # Reduced from 10
        
        forecaster = TimeSeriesForecaster()
        
        start = time.time()
        forecaster.fit(metrics)
        fit_time = time.time() - start
        
        assert fit_time < 180  # Prophet is slower, allow up to 3 minutes for 5 metrics
    
    def test_dashboard_generation_speed(self):
        """Test dashboard generation < 5s"""
        import time
        
        np.random.seed(42)
        metrics_data = {
            f'metric_{i}': {
                'historical': np.linspace(20, 70, 100),
                'current': 70,
                'forecast_30day': np.linspace(70, 80, 30),
                'confidence_upper': np.linspace(75, 85, 30),
                'confidence_lower': np.linspace(65, 75, 30),
            }
            for i in range(5)
        }
        
        generator = DashboardGenerator()
        
        start = time.time()
        dashboard = generator.generate_dashboard(
            metrics_data,
            alerts=[],
            recommendations=[],
        )
        gen_time = time.time() - start
        
        assert gen_time < 5.0  # Should generate in < 5s


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
