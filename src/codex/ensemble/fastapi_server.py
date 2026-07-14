"""FastAPI server for real-time ensemble predictions."""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
import uvicorn

from src.codex.ensemble.ensemble_predictor import EnsemblePredictor, EnsembleConfig
from src.codex.ensemble.types import PredictionType

logger = logging.getLogger(__name__)


# Pydantic models for API
class PredictionRequest(BaseModel):
    """Request model for single prediction."""

    features: Dict[str, Any] = Field(..., description="Feature dictionary for prediction")
    prediction_type: str = Field("classification", description="Type of prediction")


class BatchPredictionRequest(BaseModel):
    """Request model for batch predictions."""

    features_list: List[Dict[str, Any]] = Field(..., description="List of feature dictionaries")
    prediction_type: str = Field("classification", description="Type of prediction")


class PredictionResponse(BaseModel):
    """Response model for predictions."""

    prediction: Any
    confidence: float
    prediction_type: str
    timestamp: str
    execution_time_ms: float
    escalated: bool
    escalation_reason: Optional[str] = None
    models: List[Dict[str, Any]]
    voting_scores: Dict[str, float]


class BatchPredictionResponse(BaseModel):
    """Response model for batch predictions."""

    predictions: List[PredictionResponse]
    count: int
    timestamp: str
    total_execution_time_ms: float


class PerformanceMetricsResponse(BaseModel):
    """Response model for performance metrics."""

    total_predictions: int
    escalated_predictions: int
    escalation_rate: float
    avg_execution_time_ms: float
    p95_execution_time_ms: float
    p99_execution_time_ms: float
    avg_confidence: float
    min_confidence: float
    max_confidence: float
    model_accuracies: Dict[str, float]
    configuration: Dict[str, Any]


class HealthCheckResponse(BaseModel):
    """Response model for health check."""

    status: str
    models: Dict[str, str]
    timestamp: str
    test_prediction: Optional[Dict[str, Any]] = None


class PredictionAPIServer:
    """FastAPI server for real-time ensemble predictions."""

    def __init__(
        self,
        config: Optional[EnsembleConfig] = None,
        workers: int = 4,
        host: str = "0.0.0.0",
        port: int = 8000,
    ):
        """Initialize prediction API server.

        Args:
            config: Ensemble configuration
            workers: Number of worker threads
            host: Server host
            port: Server port
        """
        self.config = config or EnsembleConfig()
        self.host = host
        self.port = port
        self.predictor = EnsemblePredictor(self.config)
        self.executor = ThreadPoolExecutor(max_workers=workers)

        # Metrics tracking
        self.total_requests = 0
        self.total_errors = 0
        self.request_times: List[float] = []

        # Create FastAPI app
        self.app = self._create_app()

    def _create_app(self) -> FastAPI:
        """Create and configure FastAPI app.

        Returns:
            FastAPI application instance
        """
        app = FastAPI(
            title="Ensemble Prediction API",
            description="Real-time multi-model ensemble prediction service",
            version="1.0.0",
        )

        # Routes
        @app.post("/predict", response_model=PredictionResponse)
        async def predict_endpoint(request: PredictionRequest) -> PredictionResponse:
            """Make a single prediction."""
            start_time = time.time()

            try:
                self.total_requests += 1

                # Validate prediction type
                try:
                    pred_type = PredictionType[request.prediction_type.upper()]
                except KeyError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid prediction_type: {request.prediction_type}. "
                        f"Valid types: {[pt.value for pt in PredictionType]}",
                    )

                # Make prediction
                result = self.predictor.predict(request.features, pred_type)

                # Track metrics
                exec_time = result.total_execution_time_ms
                self.request_times.append(exec_time)

                return PredictionResponse(
                    prediction=result.prediction,
                    confidence=result.confidence,
                    prediction_type=result.prediction_type.value,
                    timestamp=result.timestamp,
                    execution_time_ms=exec_time,
                    escalated=result.escalated,
                    escalation_reason=result.escalation_reason,
                    models=[m.to_dict() for m in result.model_predictions],
                    voting_scores=result.voting_scores,
                )

            except HTTPException:
                raise
            except Exception as e:
                self.total_errors += 1
                logger.error(f"Prediction failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @app.post("/batch_predict", response_model=BatchPredictionResponse)
        async def batch_predict_endpoint(request: BatchPredictionRequest) -> BatchPredictionResponse:
            """Make batch predictions."""
            start_time = time.time()

            try:
                self.total_requests += 1

                # Validate prediction type
                try:
                    pred_type = PredictionType[request.prediction_type.upper()]
                except KeyError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid prediction_type: {request.prediction_type}",
                    )

                # Make batch predictions
                results = self.predictor.batch_predict(request.features_list, pred_type)

                # Track metrics
                for result in results:
                    self.request_times.append(result.total_execution_time_ms)

                batch_exec_time = (time.time() - start_time) * 1000

                return BatchPredictionResponse(
                    predictions=[
                        PredictionResponse(
                            prediction=r.prediction,
                            confidence=r.confidence,
                            prediction_type=r.prediction_type.value,
                            timestamp=r.timestamp,
                            execution_time_ms=r.total_execution_time_ms,
                            escalated=r.escalated,
                            escalation_reason=r.escalation_reason,
                            models=[m.to_dict() for m in r.model_predictions],
                            voting_scores=r.voting_scores,
                        )
                        for r in results
                    ],
                    count=len(results),
                    timestamp=datetime.utcnow().isoformat() + "Z",
                    total_execution_time_ms=batch_exec_time,
                )

            except HTTPException:
                raise
            except Exception as e:
                self.total_errors += 1
                logger.error(f"Batch prediction failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/metrics", response_model=PerformanceMetricsResponse)
        async def metrics_endpoint() -> PerformanceMetricsResponse:
            """Get performance metrics."""
            try:
                performance = self.predictor.get_ensemble_performance()
                accuracies = self.predictor.get_model_accuracy_estimates()

                return PerformanceMetricsResponse(
                    total_predictions=performance.get("total_predictions", 0),
                    escalated_predictions=performance.get("escalated_predictions", 0),
                    escalation_rate=performance.get("escalation_rate", 0.0),
                    avg_execution_time_ms=performance.get("avg_execution_time_ms", 0.0),
                    p95_execution_time_ms=performance.get("p95_execution_time_ms", 0.0),
                    p99_execution_time_ms=performance.get("p99_execution_time_ms", 0.0),
                    avg_confidence=performance.get("avg_confidence", 0.0),
                    min_confidence=performance.get("min_confidence", 0.0),
                    max_confidence=performance.get("max_confidence", 1.0),
                    model_accuracies=accuracies,
                    configuration={
                        "heuristic_weight": self.config.heuristic_weight,
                        "ml_weight": self.config.ml_weight,
                        "symbolic_weight": self.config.symbolic_weight,
                        "confidence_threshold": self.config.confidence_threshold,
                        "disagreement_threshold": self.config.disagreement_threshold,
                        "max_execution_time_ms": self.config.max_execution_time_ms,
                    },
                )

            except Exception as e:
                logger.error(f"Failed to get metrics: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/health", response_model=HealthCheckResponse)
        async def health_check() -> HealthCheckResponse:
            """Health check endpoint."""
            try:
                # Test prediction
                test_features = {
                    "confidence": 0.7,
                    "frequency": 50,
                    "days_old": 5,
                    "priority": 5,
                    "category": "test",
                }

                result = self.predictor.predict(test_features)

                return HealthCheckResponse(
                    status="healthy",
                    models={
                        "heuristic": "ok",
                        "ml": "ok",
                        "symbolic": "ok",
                    },
                    timestamp=datetime.utcnow().isoformat() + "Z",
                    test_prediction={
                        "prediction": result.prediction,
                        "confidence": result.confidence,
                        "execution_time_ms": result.total_execution_time_ms,
                    },
                )

            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return HealthCheckResponse(
                    status="unhealthy",
                    models={
                        "heuristic": "error",
                        "ml": "error",
                        "symbolic": "error",
                    },
                    timestamp=datetime.utcnow().isoformat() + "Z",
                )

        @app.get("/stats")
        async def stats_endpoint() -> Dict[str, Any]:
            """Server statistics endpoint."""
            import numpy as np

            request_times_array = np.array(self.request_times) if self.request_times else np.array([0])

            return {
                "total_requests": self.total_requests,
                "total_errors": self.total_errors,
                "error_rate": self.total_errors / self.total_requests
                if self.total_requests > 0
                else 0.0,
                "avg_request_time_ms": float(np.mean(request_times_array)),
                "p50_request_time_ms": float(np.percentile(request_times_array, 50)),
                "p95_request_time_ms": float(np.percentile(request_times_array, 95)),
                "p99_request_time_ms": float(np.percentile(request_times_array, 99)),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

        return app

    def run(self, reload: bool = False) -> None:
        """Run the FastAPI server.

        Args:
            reload: Enable auto-reload on file changes
        """
        logger.info(f"Starting Prediction API server on {self.host}:{self.port}")
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info",
            reload=reload,
        )

    def get_app(self) -> FastAPI:
        """Get FastAPI application instance.

        Returns:
            FastAPI application
        """
        return self.app


# For direct execution
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create and run server
    config = EnsembleConfig(
        heuristic_weight=0.3,
        ml_weight=0.4,
        symbolic_weight=0.3,
        confidence_threshold=0.70,
        disagreement_threshold=0.15,
    )

    server = PredictionAPIServer(config=config, port=8000)
    server.run()
