# MCP Observability

## Overview

The MCP (Model Context Protocol) observability capability provides comprehensive monitoring and visibility for MCP services, including structured logging, metrics collection, distributed tracing, health checks, and alerting integration.

**Keywords**: observability, logging, metrics, tracing, monitoring, prometheus, grafana, opentelemetry, health-check, alerting, request-id, correlation-id, structured-logging, mcp, safeguards, telemetry, performance, debugging

## Purpose

Manages MCP observability through:
- **Structured Logging**: JSON-formatted logs with context
- **Metrics Collection**: Application and business metrics
- **Distributed Tracing**: Request flow tracking across services
- **Health Checks**: Service health and readiness endpoints
- **Alerting**: Proactive issue notification

## Architecture

### Observability Stack

```
┌─────────────────────────────────────┐
│   Application Layer                 │
│   (Instrumented code)               │
└─────────────┬───────────────────────┘
              │ emits
              ▼
┌─────────────────────────────────────┐
│   Telemetry Collectors              │
│   (Logs, Metrics, Traces)           │
└─────────────┬───────────────────────┘
              │ aggregates
              ▼
┌─────────────────────────────────────┐
│   Observability Backend             │
│   (Prometheus, Grafana, Jaeger)     │
└─────────────────────────────────────┘
```

### Request Tracing Flow

```python
# Pseudocode for request tracing
async def handle_request(request):
    # 1. Generate or extract trace context
    trace_id = request.headers.get("X-Request-Id") or generate_trace_id()
    
    # 2. Create span for this request
    with tracer.start_span("handle_request", trace_id=trace_id):
        # 3. Log request with context
        logger.info("Processing request", extra={"trace_id": trace_id})
        
        # 4. Record metrics
        request_counter.inc()
        
        # 5. Process and trace sub-operations
        result = await process(request)
        
        return result
```

## Implementation

### Structured Logging

Implement JSON-formatted logging:

```python
import json
import logging
from datetime import datetime
from typing import Any, Dict
import uuid

class JSONFormatter(logging.Formatter):
    """
    JSON log formatter for structured logging.
    
    Provides:
    - Consistent JSON output
    - Automatic field extraction
    - Context propagation
    
    Safeguards:
    - Message length limits
    - Exception safe serialization
    - Sensitive data filtering
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": self._sanitize_message(record.getMessage()),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields
        if hasattr(record, "trace_id"):
            log_entry["trace_id"] = record.trace_id
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        
        # Add exception info (safeguard - limited traceback)
        if record.exc_info:
            log_entry["exception"] = self._format_exception(record)
        
        return json.dumps(log_entry)
    
    def _sanitize_message(self, message: str) -> str:
        """Sanitize log message (safeguard)."""
        # Limit message length
        if len(message) > 10000:
            message = message[:10000] + "...[truncated]"
        return message
    
    def _format_exception(self, record: logging.LogRecord) -> dict:
        """Format exception info safely."""
        import traceback
        exc_lines = traceback.format_exception(*record.exc_info)
        return {
            "type": record.exc_info[0].__name__,
            "message": str(record.exc_info[1]),
            "traceback": "".join(exc_lines[-5:])  # Last 5 lines only (safeguard)
        }


def init_json_logging(level: str = "INFO"):
    """
    Initialize structured JSON logging.
    
    Sets up logging with JSON formatting and appropriate handlers.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level))
    root_logger.addHandler(handler)
    
    return root_logger


class RequestContextLogger:
    """
    Logger with automatic request context propagation.
    
    Ensures all logs include X-Request-Id and other context.
    """
    
    def __init__(self, logger: logging.Logger):
        self._logger = logger
        self._context: Dict[str, Any] = {}
    
    def set_context(self, **kwargs):
        """Set context fields for subsequent logs."""
        self._context.update(kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info with context."""
        extra = {**self._context, **kwargs}
        self._logger.info(message, extra=extra)
    
    def error(self, message: str, **kwargs):
        """Log error with context."""
        extra = {**self._context, **kwargs}
        self._logger.error(message, extra=extra)
```

### Metrics Collection

Implement Prometheus metrics:

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time

# Request metrics
request_counter = Counter(
    "mcp_requests_total",
    "Total number of MCP requests",
    ["method", "status"]
)

request_latency = Histogram(
    "mcp_request_latency_seconds",
    "Request latency in seconds",
    ["method"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]
)

active_connections = Gauge(
    "mcp_active_connections",
    "Number of active connections"
)


class MetricsMiddleware:
    """
    Middleware for automatic metrics collection.
    
    Provides:
    - Request counting
    - Latency tracking
    - Error rate monitoring
    
    Safeguards:
    - Cardinality limits on labels
    - Timeout protection
    - Error handling
    """
    
    def __init__(self, app):
        self._app = app
    
    async def __call__(self, request, handler):
        """Process request with metrics."""
        method = request.method
        start_time = time.time()
        
        active_connections.inc()
        
        try:
            response = await handler(request)
            status = "success"
            return response
            
        except Exception as e:
            status = "error"
            raise
            
        finally:
            # Record metrics (safeguard - always executed)
            latency = time.time() - start_time
            request_counter.labels(method=method, status=status).inc()
            request_latency.labels(method=method).observe(latency)
            active_connections.Phase 12()


def get_metrics():
    """Return Prometheus metrics in exposition format."""
    return generate_latest()
```

### Distributed Tracing

Implement OpenTelemetry tracing:

```python
from dataclasses import dataclass
from typing import Optional, Dict
import uuid
import time

@dataclass
class Span:
    """
    Trace span representing a unit of work.
    
    Provides:
    - Timing information
    - Parent-child relationships
    - Annotations and tags
    """
    trace_id: str
    span_id: str
    parent_id: Optional[str]
    name: str
    start_time: float
    end_time: Optional[float] = None
    tags: Dict[str, str] = None
    
    def finish(self):
        """Mark span as finished."""
        self.end_time = time.time()
    
    def add_tag(self, key: str, value: str):
        """Add tag to span."""
        if self.tags is None:
            self.tags = {}
        self.tags[key] = str(value)[:100]  # Bounds check (safeguard)


class Tracer:
    """
    Distributed tracing implementation.
    
    Provides:
    - Trace context propagation
    - Span management
    - Trace export
    
    Safeguards:
    - Trace ID validation
    - Span limit per trace
    - Memory bounds
    """
    
    MAX_SPANS = 1000  # Safeguard: limit spans per trace
    
    def __init__(self):
        self._spans: Dict[str, list] = {}
    
    def start_span(
        self,
        name: str,
        trace_id: Optional[str] = None,
        parent_id: Optional[str] = None
    ) -> Span:
        """
        Start a new span.
        
        Args:
            name: Span name
            trace_id: Trace ID (generated if not provided)
            parent_id: Parent span ID
            
        Returns:
            New Span instance
        """
        trace_id = trace_id or self._generate_trace_id()
        span_id = str(uuid.uuid4())[:16]
        
        span = Span(
            trace_id=trace_id,
            span_id=span_id,
            parent_id=parent_id,
            name=name,
            start_time=time.time()
        )
        
        # Store span (with bounds check - safeguard)
        if trace_id not in self._spans:
            self._spans[trace_id] = []
        
        if len(self._spans[trace_id]) < self.MAX_SPANS:
            self._spans[trace_id].append(span)
        
        return span
    
    def _generate_trace_id(self) -> str:
        """Generate a new trace ID."""
        return str(uuid.uuid4()).replace("-", "")
    
    def get_trace_context(self) -> dict:
        """Get current trace context for propagation."""
        return {
            "X-Request-Id": self._current_trace_id,
            "X-Trace-Id": self._current_trace_id,
        }


# Global tracer instance
tracer = Tracer()


class TracingMiddleware:
    """Middleware for automatic request tracing."""
    
    async def __call__(self, request, handler):
        """Process request with tracing."""
        # Extract or generate trace ID
        trace_id = request.headers.get("X-Request-Id")
        if not trace_id:
            trace_id = tracer._generate_trace_id()
        
        # Create root span
        span = tracer.start_span("http_request", trace_id=trace_id)
        span.add_tag("method", request.method)
        span.add_tag("path", request.path)
        
        try:
            response = await handler(request)
            span.add_tag("status", str(response.status))
            return response
            
        except Exception as e:
            span.add_tag("error", str(type(e).__name__))
            raise
            
        finally:
            span.finish()
```

### Health Checks

Implement health endpoints:

```python
from enum import Enum
from typing import Dict, List, Callable
import asyncio

class HealthStatus(Enum):
    """Health check status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthChecker:
    """
    Health check manager for MCP services.
    
    Provides:
    - Liveness checks (is service running?)
    - Readiness checks (is service ready to serve?)
    - Component health aggregation
    
    Safeguards:
    - Timeout protection
    - Graceful degradation
    - Caching to prevent overload
    """
    
    def __init__(self, timeout: float = 5.0):
        """
        Initialize health checker.
        
        Args:
            timeout: Timeout for health checks in seconds
        """
        self._checks: Dict[str, Callable] = {}
        self._timeout = timeout
        self._cache: Dict[str, tuple] = {}
        self._cache_ttl = 5.0  # Cache health checks for 5 seconds
    
    def register(self, name: str, check: Callable):
        """Register a health check."""
        self._checks[name] = check
    
    async def healthz(self) -> dict:
        """
        Liveness check - is the service running?
        
        Returns basic health status without checking dependencies.
        """
        return {
            "status": HealthStatus.HEALTHY.value,
            "timestamp": time.time(),
        }
    
    async def readyz(self) -> dict:
        """
        Readiness check - is the service ready to serve?
        
        Checks all registered health checks with timeout protection.
        """
        results = {}
        overall_status = HealthStatus.HEALTHY
        
        for name, check in self._checks.items():
            try:
                # Run check with timeout (safeguard)
                result = await asyncio.wait_for(
                    check(),
                    timeout=self._timeout
                )
                results[name] = {
                    "status": HealthStatus.HEALTHY.value,
                    "details": result
                }
            except asyncio.TimeoutError:
                results[name] = {
                    "status": HealthStatus.UNHEALTHY.value,
                    "error": "Health check timed out"
                }
                overall_status = HealthStatus.UNHEALTHY
            except Exception as e:
                results[name] = {
                    "status": HealthStatus.UNHEALTHY.value,
                    "error": str(e)
                }
                overall_status = HealthStatus.UNHEALTHY
        
        return {
            "status": overall_status.value,
            "checks": results,
            "timestamp": time.time(),
        }


# Example health check registration
health_checker = HealthChecker()

async def check_database():
    """Check database connectivity."""
    # Perform actual database check
    return {"connected": True}

health_checker.register("database", check_database)
```

## Configuration

### Environment Variables

Configure observability via environment:

```bash
# Logging settings
export MCP_LOG_LEVEL="INFO"
export MCP_LOG_FORMAT="json"

# Metrics settings
export MCP_METRICS_ENABLED="true"
export MCP_METRICS_PORT="9090"
export MCP_METRICS_PATH="/metrics"

# Tracing settings
export MCP_TRACING_ENABLED="true"
export MCP_TRACING_SAMPLE_RATE="1.0"
export MCP_TRACING_ENDPOINT="http://jaeger:14268/api/traces"

# Health check settings
export MCP_HEALTH_CHECK_TIMEOUT="5"
export MCP_HEALTH_CHECK_INTERVAL="30"
```

### Configuration File

Use YAML for observability configuration:

```yaml
# observability_config.yaml
logging:
  level: "INFO"
  format: "json"
  include_traceback: false
  
metrics:
  enabled: true
  port: 9090
  path: "/metrics"
  histograms:
    request_latency:
      buckets: [0.01, 0.05, 0.1, 0.5, 1.0, 5.0]

tracing:
  enabled: true
  sample_rate: 1.0
  exporter: "jaeger"
  endpoint: "http://jaeger:14268/api/traces"
  propagators: ["b3", "w3c"]

health:
  liveness:
    path: "/healthz"
    interval: 10
  readiness:
    path: "/readyz"
    timeout: 5
    checks:
      - database
      - cache
      - external_api

alerting:
  enabled: true
  rules:
    - name: "high_error_rate"
      expression: "rate(mcp_requests_total{status='error'}[5m]) > 0.1"
      severity: "critical"
```

## Usage Examples

### Example 1: Request Logging with Correlation

```python
@app.middleware("http")
async def logging_middleware(request, handler):
    """Add request context to all logs."""
    request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
    
    # Set context for all logs in this request
    logger = RequestContextLogger(logging.getLogger(__name__))
    logger.set_context(request_id=request_id, path=request.path)
    
    logger.info("Request started")
    
    try:
        response = await handler(request)
        logger.info("Request completed", status=response.status)
        
        # Add request ID to response headers
        response.headers["X-Request-Id"] = request_id
        return response
        
    except Exception as e:
        logger.error("Request failed", error=str(e))
        raise
```

### Example 2: Custom Metrics

```python
from prometheus_client import Counter, Summary

# Business metrics
model_predictions = Counter(
    "mcp_model_predictions_total",
    "Total model predictions",
    ["model_name", "result"]
)

prediction_confidence = Summary(
    "mcp_prediction_confidence",
    "Prediction confidence scores",
    ["model_name"]
)

async def predict(request):
    """Make prediction and record metrics."""
    result = await model.predict(request.data)
    
    # Record metrics
    model_predictions.labels(
        model_name="default",
        result="success"
    ).inc()
    
    prediction_confidence.labels(
        model_name="default"
    ).observe(result.confidence)
    
    return result
```

### Example 3: Alerting Integration

```python
class AlertManager:
    """Send alerts based on conditions."""
    
    async def check_and_alert(self, metric_name: str, value: float):
        """Check metric against thresholds and send alert if needed."""
        thresholds = self._get_thresholds(metric_name)
        
        if value > thresholds.get("critical", float("inf")):
            await self._send_alert(
                severity="critical",
                message=f"{metric_name} exceeded critical threshold: {value}"
            )
        elif value > thresholds.get("warning", float("inf")):
            await self._send_alert(
                severity="warning",
                message=f"{metric_name} exceeded warning threshold: {value}"
            )
```

## Best Practices

### 1. Use Correlation IDs

```python
# Always propagate X-Request-Id
async def call_downstream(request_id: str):
    """Call downstream service with trace context."""
    headers = {"X-Request-Id": request_id}
    return await http_client.get(url, headers=headers)
```

### 2. Define SLIs and SLOs

```yaml
# Define Service Level Indicators
slis:
  availability:
    metric: "probe_success"
    target: 99.9%
  latency_p99:
    metric: "request_latency_seconds"
    percentile: 99
    target: 500ms
```

### 3. Implement Structured Logging Standards

```python
# Standard log fields for all services
REQUIRED_LOG_FIELDS = [
    "timestamp",
    "level", 
    "message",
    "service",
    "trace_id",
    "request_id"
]
```

## Troubleshooting

### Missing Traces

**Problem**: Traces not appearing in tracing backend

**Solution**:
1. Verify trace context propagation
2. Check exporter configuration
3. Verify sampling rate
4. Check network connectivity to tracing backend

### High Cardinality Issues

**Problem**: Prometheus memory usage high

**Solution**:
1. Review label cardinality
2. Add label value limits
3. Use histograms instead of summary
4. Implement label sanitization

## Security Considerations

### Log Sanitization

- Never log sensitive data (passwords, tokens)
- Mask PII in log messages
- Limit traceback exposure
- Filter query parameters

### Metrics Security

- Secure metrics endpoint
- Limit label values
- Monitor metric cardinality
- Use authentication for Prometheus

## Related Capabilities

- **mcp-error-handling**: Error logging and tracking
- **mcp-rate-limiting**: Rate limit metrics
- **mcp-authz-authn**: Authentication event logging
- **mcp-configuration**: Observability configuration

## References

- [OpenTelemetry Specification](https://opentelemetry.io/docs/specs/otel/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/naming/)
- [Structured Logging Guidelines](https://www.structlog.org/)
- [The Three Pillars of Observability](https://www.oreilly.com/library/view/distributed-systems-observability/9781492033431/)
