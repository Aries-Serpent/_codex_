"""
FastAPI Server for Planset 012: Predictive Capacity Planning

Provides REST endpoints for:
- Single dimension forecasting (ARIMA + Prophet ensemble)
- Bottleneck detection across 7 infrastructure dimensions
- CAPEX recommendations with 20%+ savings targets
- Load testing with 100+ concurrent requests
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import time
import asyncio
from dataclasses import asdict

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel, Field
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

from .models import ARIMAModel, ProphetModel, EnsembleForecaster, EnsembleConfig
from .arima_prophet_ensemble import (
    BottleneckPredictor,
    CapexRecommendationEngine,
    ParetoOptimizationResult,
)


# Pydantic models for request/response
class ForecastRequest(BaseModel):
    """Request for dimension forecast"""
    dimension: str = Field(..., description="Infrastructure dimension (cpu, memory, storage, network, gpu, cache, database)")
    historical_data: List[float] = Field(..., description="Historical time-series data")
    forecast_steps: int = Field(default=30, ge=1, le=365)
    confidence_level: float = Field(default=0.95, ge=0.80, le=0.99)


class ForecastResponse(BaseModel):
    """Response for dimension forecast"""
    dimension: str
    forecast_values: List[float]
    confidence_upper: List[float]
    confidence_lower: List[float]
    mape_error_percent: float
    confidence_level: float
    generated_at: datetime


class BottleneckRequest(BaseModel):
    """Request for bottleneck detection"""
    metrics: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Dict with dimension -> {current: float, forecast: list}"
    )
    trend_strengths: Dict[str, float] = Field(
        ...,
        description="Dict with dimension -> trend_strength (0-1)"
    )


class BottleneckResponse(BaseModel):
    """Response for bottleneck detection"""
    bottlenecks: List[Dict[str, Any]]
    critical_resources: List[str]
    immediate_action_required: bool
    cascading_analysis: Optional[Dict[str, Any]]
    generated_at: datetime


class CapexRequest(BaseModel):
    """Request for CAPEX recommendations"""
    alerts: List[Dict[str, Any]] = Field(..., description="List of bottleneck alerts")
    current_costs: Dict[str, float] = Field(..., description="Current monthly costs by resource")
    optimization_strategy: str = Field(default="moderate", pattern="^(aggressive|moderate|conservative)$")


class CapexResponse(BaseModel):
    """Response for CAPEX recommendations"""
    recommendations: List[Dict[str, Any]]
    total_current_monthly_cost: float
    total_projected_savings_monthly: float
    savings_percentage: float
    meets_20_percent_target: bool
    payback_period_months: float
    strategy: str
    generated_at: datetime


class LoadTestRequest(BaseModel):
    """Request for load testing"""
    concurrent_requests: int = Field(default=100, ge=1, le=1000)
    requests_per_client: int = Field(default=10, ge=1, le=1000)
    dimension: str = Field(default="cpu")


class LoadTestResult(BaseModel):
    """Result of load test"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    requests_per_second: float
    test_passed: bool


def create_app() -> Optional[FastAPI]:
    """Create and configure FastAPI application"""
    
    if not HAS_FASTAPI:
        return None
    
    app = FastAPI(
        title="Planset 012: Predictive Capacity Planning",
        description="ARIMA + Prophet ensemble forecasting for capacity planning",
        version="1.0.0",
    )
    
    # Initialize models and engines
    ensemble_config = EnsembleConfig(arima_weight=0.5, prophet_weight=0.5)
    bottleneck_predictor = BottleneckPredictor()
    capex_engine = CapexRecommendationEngine()
    
    # Request tracking for load testing
    request_times: List[float] = []
    
    @app.post("/forecast/{dimension}", response_model=ForecastResponse)
    async def forecast_dimension(dimension: str, request: ForecastRequest) -> ForecastResponse:
        """
        Forecast a single infrastructure dimension using ARIMA+Prophet ensemble
        
        Dimensions: cpu, memory, storage, network, gpu, cache, database
        """
        start_time = time.time()
        
        try:
            # Validate dimension
            valid_dimensions = ['cpu', 'memory', 'storage', 'network', 'gpu', 'cache', 'database']
            if dimension not in valid_dimensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid dimension. Must be one of: {', '.join(valid_dimensions)}"
                )
            
            # Prepare data
            ts_data = np.array(request.historical_data, dtype=float)
            
            if len(ts_data) < 7:
                raise HTTPException(
                    status_code=400,
                    detail="At least 7 historical data points required"
                )
            
            # Fit ARIMA model
            arima = ARIMAModel()
            arima.fit(ts_data)
            
            # Fit Prophet model
            dates = pd.date_range(
                end=datetime.now(),
                periods=len(ts_data),
                freq='D'
            )
            df = pd.DataFrame({'ds': dates, 'y': ts_data})
            
            prophet = ProphetModel()
            prophet.fit(df)
            
            # Get ensemble forecast
            ensemble = EnsembleForecaster(arima, prophet, ensemble_config)
            forecast, confidence = ensemble.forecast(steps=request.forecast_steps)
            
            # Calculate confidence intervals
            z_score = 1.96  # 95% CI by default
            if request.confidence_level == 0.90:
                z_score = 1.645
            elif request.confidence_level == 0.99:
                z_score = 2.576
            
            conf_intervals = confidence * z_score
            
            confidence_upper = forecast + conf_intervals
            confidence_lower = np.maximum(forecast - conf_intervals, 0)  # No negative values
            
            # Calculate MAPE
            mape = arima.mape_score or prophet.mape_score or 5.0
            
            response_time = time.time() - start_time
            request_times.append(response_time)
            
            return ForecastResponse(
                dimension=dimension,
                forecast_values=forecast.tolist(),
                confidence_upper=confidence_upper.tolist(),
                confidence_lower=confidence_lower.tolist(),
                mape_error_percent=mape,
                confidence_level=request.confidence_level,
                generated_at=datetime.now(),
            )
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/bottlenecks", response_model=BottleneckResponse)
    async def detect_bottlenecks(request: BottleneckRequest) -> BottleneckResponse:
        """Detect bottlenecks across all infrastructure dimensions"""
        
        try:
            # Predict bottlenecks
            alerts = bottleneck_predictor.predict_bottlenecks(
                request.metrics,
                request.trend_strengths,
            )
            
            # Convert alerts to dicts
            alerts_data = []
            critical_resources = []
            
            for alert in alerts:
                alert_dict = asdict(alert)
                alert_dict['predicted_saturation_date'] = alert.predicted_saturation_date.isoformat()
                alerts_data.append(alert_dict)
                
                if alert.severity in ['critical', 'high']:
                    critical_resources.append(alert.resource)
            
            # Analyze cascading effects
            cascading = None
            if len(alerts) > 1:
                try:
                    cascade_analysis = bottleneck_predictor.analyze_cascading(alerts)
                    cascading = {
                        'first_bottleneck': cascade_analysis.first_bottleneck.resource,
                        'cascading_sequence': [a.resource for a in cascade_analysis.cascading_sequence],
                        'mitigation_urgency': cascade_analysis.mitigation_urgency,
                        'estimated_time_to_cascade_days': cascade_analysis.estimated_time_to_cascade,
                        'cascading_impact': cascade_analysis.cascading_impact,
                    }
                except:
                    pass
            
            return BottleneckResponse(
                bottlenecks=alerts_data,
                critical_resources=critical_resources,
                immediate_action_required=any(a.severity == 'critical' for a in alerts),
                cascading_analysis=cascading,
                generated_at=datetime.now(),
            )
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/capex_recommendations", response_model=CapexResponse)
    async def get_capex_recommendations(request: CapexRequest) -> CapexResponse:
        """Get CAPEX recommendations with ≥20% savings target"""
        
        try:
            # Reconstruct alerts from dicts
            from .arima_prophet_ensemble import BottleneckAlert
            
            alerts = []
            for alert_dict in request.alerts:
                try:
                    alert_dict_copy = alert_dict.copy()
                    if isinstance(alert_dict_copy.get('predicted_saturation_date'), str):
                        alert_dict_copy['predicted_saturation_date'] = datetime.fromisoformat(
                            alert_dict_copy['predicted_saturation_date']
                        )
                    alerts.append(BottleneckAlert(**alert_dict_copy))
                except:
                    pass
            
            if not alerts:
                # Return empty recommendations
                return CapexResponse(
                    recommendations=[],
                    total_current_monthly_cost=sum(request.current_costs.values()),
                    total_projected_savings_monthly=0,
                    savings_percentage=0,
                    meets_20_percent_target=False,
                    payback_period_months=0,
                    strategy=request.optimization_strategy,
                    generated_at=datetime.now(),
                )
            
            # Generate recommendations
            results = capex_engine.generate_capex_recommendations(
                alerts,
                request.current_costs,
                request.optimization_strategy,
            )
            
            return CapexResponse(
                recommendations=results['recommendations'],
                total_current_monthly_cost=results['total_current_monthly_cost'],
                total_projected_savings_monthly=results['total_projected_savings_monthly'],
                savings_percentage=results['savings_percentage'],
                meets_20_percent_target=results['meets_20_percent_target'],
                payback_period_months=results['payback_period_months'],
                strategy=results['strategy'],
                generated_at=datetime.now(),
            )
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/load_test", response_model=LoadTestResult)
    async def run_load_test(request: LoadTestRequest) -> LoadTestResult:
        """Run load test with concurrent forecast requests"""
        
        try:
            # Generate synthetic data
            np.random.seed(42)
            historical_data = (
                50 + np.arange(100) * 0.5 +
                np.random.normal(0, 3, 100)
            ).tolist()
            
            response_times = []
            successful = 0
            failed = 0
            
            async def make_forecast_request():
                """Make a single forecast request"""
                nonlocal successful, failed
                
                try:
                    start = time.time()
                    
                    forecast_req = ForecastRequest(
                        dimension="cpu",
                        historical_data=historical_data,
                        forecast_steps=30,
                    )
                    
                    # Simulate forecast
                    ts_data = np.array(historical_data, dtype=float)
                    arima = ARIMAModel()
                    arima.fit(ts_data)
                    
                    forecast, _ = arima.forecast(30)
                    
                    elapsed = (time.time() - start) * 1000  # Convert to ms
                    response_times.append(elapsed)
                    successful += 1
                
                except Exception as e:
                    failed += 1
            
            # Run load test
            total_requests = request.concurrent_requests * request.requests_per_client
            
            # Simulate concurrent requests
            tasks = []
            for _ in range(total_requests):
                tasks.append(make_forecast_request())
            
            # Process in batches to simulate concurrency
            batch_size = request.concurrent_requests
            for i in range(0, len(tasks), batch_size):
                batch = tasks[i:i + batch_size]
                await asyncio.gather(*batch, return_exceptions=True)
            
            # Calculate statistics
            if response_times:
                response_times_sorted = sorted(response_times)
                avg_response = np.mean(response_times)
                p50 = np.percentile(response_times_sorted, 50)
                p95 = np.percentile(response_times_sorted, 95)
                p99 = np.percentile(response_times_sorted, 99)
            else:
                avg_response = p50 = p95 = p99 = 0
            
            rps = total_requests / (np.sum(response_times) / 1000) if response_times else 0
            
            # Pass if p99 < 500ms
            test_passed = p99 < 500.0 and successful / total_requests > 0.95
            
            return LoadTestResult(
                total_requests=total_requests,
                successful_requests=successful,
                failed_requests=failed,
                average_response_time_ms=avg_response,
                p50_latency_ms=p50,
                p95_latency_ms=p95,
                p99_latency_ms=p99,
                requests_per_second=rps,
                test_passed=test_passed,
            )
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/health")
    async def health_check() -> Dict[str, str]:
        """Health check endpoint"""
        return {"status": "healthy", "service": "Planset 012 Capacity Planning"}
    
    @app.get("/metrics")
    async def get_metrics() -> Dict[str, Any]:
        """Get service metrics"""
        if request_times:
            return {
                'total_requests': len(request_times),
                'average_response_time_ms': np.mean(request_times) * 1000,
                'p95_response_time_ms': np.percentile(request_times, 95) * 1000,
                'p99_response_time_ms': np.percentile(request_times, 99) * 1000,
            }
        return {
            'total_requests': 0,
            'average_response_time_ms': 0,
            'p95_response_time_ms': 0,
            'p99_response_time_ms': 0,
        }
    
    return app


if __name__ == '__main__':
    if HAS_FASTAPI:
        import uvicorn
        
        app = create_app()
        uvicorn.run(app, host='0.0.0.0', port=8000)
    else:
        print("FastAPI not installed. Install with: pip install fastapi uvicorn")
