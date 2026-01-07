# Status Reporting - Capability Documentation

## Overview

The status reporting capability provides comprehensive system status monitoring, health checks, and reporting mechanisms for the _codex_ project. This system enables real-time visibility into application health, performance metrics, and operational status across all components.

**Keywords**: status, reporting, health, monitoring, metrics, dashboard, alerts, observability, health-check, status-endpoint, telemetry

## Architecture

### Status Components

1. **Health Checks**
   - Liveness probes: Is the application running?
   - Readiness probes: Is the application ready to serve traffic?
   - Startup probes: Has the application completed initialization?
   - Dependency health: Are external services available?

2. **Status Endpoints**
   - `/health`: Basic health check endpoint
   - `/status`: Detailed system status
   - `/metrics`: Prometheus-compatible metrics
   - `/ready`: Readiness check for load balancers

3. **Reporting Mechanisms**
   - Real-time dashboards
   - Periodic status reports
   - Alert notifications
   - Historical trend analysis

### Status Levels

- **Healthy**: All systems operational
- **Degraded**: Partial functionality available
- **Unhealthy**: Critical issues detected
- **Unknown**: Unable to determine status

## Detection Patterns

The status reporting detector identifies:

1. **Status Endpoints**:
   - Health check routes (`/health`, `/healthz`, `/ping`)
   - Status API endpoints
   - Readiness endpoints
   - Liveness endpoints

2. **Monitoring Integration**:
   - Prometheus metrics exporters
   - Grafana dashboard configurations
   - DataDog integration
   - New Relic monitoring

3. **Alert Mechanisms**:
   - PagerDuty integration
   - Slack notifications
   - Email alerts
   - SMS notifications

## Usage Examples

### Example 1: FastAPI Health Check

```python
# src/api/health.py
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from datetime import datetime
import psutil

app = FastAPI()

@app.get("/health", tags=["status"])
async def health_check():
    """
    Basic health check endpoint.
    Returns system health status.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "codex-api",
        "version": "1.0.0"
    }

@app.get("/status", tags=["status"])
async def detailed_status():
    """
    Detailed system status with metrics.
    Includes CPU, memory, and service health.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage_percent": psutil.disk_usage('/').percent
        },
        "services": {
            "database": check_database_health(),
            "cache": check_cache_health(),
            "storage": check_storage_health()
        }
    }

@app.get("/ready", tags=["status"])
async def readiness_check():
    """
    Readiness check for load balancers.
    Returns 200 if ready, 503 if not ready.
    """
    if not is_application_ready():
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not ready"}
        )
    return {"status": "ready"}

def check_database_health() -> dict:
    """Check database connectivity and health."""
    try:
        # Validate database connection
        db.execute("SELECT 1")
        return {"status": "healthy", "response_time_ms": 5}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

def check_cache_health() -> dict:
    """Check cache service health."""
    try:
        cache.ping()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

def is_application_ready() -> bool:
    """Determine if application is ready to serve traffic."""
    # Validation checks
    return all([
        check_database_health()["status"] == "healthy",
        check_cache_health()["status"] == "healthy",
        models_loaded(),
        configuration_valid()
    ])
```

### Example 2: Kubernetes Health Probes

```yaml
# k8s/deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codex-api
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api
        image: codex-api:latest
        ports:
        - containerPort: 8000
        
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
        
        startupProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 0
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 30
```

### Example 3: Comprehensive Status Dashboard

```python
# src/monitoring/status_dashboard.py
from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime, timedelta
import asyncio

@dataclass
class ServiceStatus:
    name: str
    status: str  # healthy, degraded, unhealthy
    last_check: datetime
    response_time_ms: float
    error_message: str = None

class StatusDashboard:
    """
    Comprehensive status reporting dashboard.
    Monitors all system components and dependencies.
    """
    
    def __init__(self):
        self.services: Dict[str, ServiceStatus] = {}
        self.metrics_history: List[dict] = []
    
    async def check_all_services(self) -> Dict[str, ServiceStatus]:
        """
        Check health of all services concurrently.
        Returns status for each service.
        """
        services_to_check = [
            ("database", self.check_database),
            ("cache", self.check_cache),
            ("storage", self.check_storage),
            ("ml_model", self.check_ml_model),
            ("external_api", self.check_external_api)
        ]
        
        results = await asyncio.gather(*[
            self._check_service(name, check_func)
            for name, check_func in services_to_check
        ])
        
        for service_status in results:
            self.services[service_status.name] = service_status
        
        return self.services
    
    async def _check_service(self, name: str, check_func) -> ServiceStatus:
        """Execute health check with timeout and error handling."""
        start_time = datetime.utcnow()
        try:
            result = await asyncio.wait_for(
                check_func(),
                timeout=5.0  # Timeout safeguard
            )
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return ServiceStatus(
                name=name,
                status="healthy",
                last_check=datetime.utcnow(),
                response_time_ms=response_time
            )
        except asyncio.TimeoutError:
            return ServiceStatus(
                name=name,
                status="unhealthy",
                last_check=datetime.utcnow(),
                response_time_ms=5000.0,
                error_message="Health check timeout"
            )
        except Exception as e:
            return ServiceStatus(
                name=name,
                status="unhealthy",
                last_check=datetime.utcnow(),
                response_time_ms=0.0,
                error_message=str(e)
            )
    
    def get_overall_status(self) -> str:
        """
        Determine overall system status based on service health.
        Returns: healthy, degraded, or unhealthy.
        """
        if not self.services:
            return "unknown"
        
        statuses = [s.status for s in self.services.values()]
        
        if all(s == "healthy" for s in statuses):
            return "healthy"
        elif any(s == "unhealthy" for s in statuses):
            critical_services = ["database", "ml_model"]
            if any(self.services.get(s, ServiceStatus("", "unknown", datetime.utcnow(), 0)).status == "unhealthy" 
                   for s in critical_services):
                return "unhealthy"
            return "degraded"
        else:
            return "degraded"
    
    def generate_report(self) -> dict:
        """Generate comprehensive status report."""
        return {
            "overall_status": self.get_overall_status(),
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                name: {
                    "status": service.status,
                    "last_check": service.last_check.isoformat(),
                    "response_time_ms": service.response_time_ms,
                    "error": service.error_message
                }
                for name, service in self.services.items()
            },
            "uptime_hours": self.calculate_uptime(),
            "recent_incidents": self.get_recent_incidents()
        }
    
    async def check_database(self):
        """Validate database connectivity."""
        # Validation and health check
        pass
    
    async def check_cache(self):
        """Validate cache service."""
        pass
    
    async def check_storage(self):
        """Validate storage access."""
        pass
    
    async def check_ml_model(self):
        """Validate ML model availability."""
        pass
    
    async def check_external_api(self):
        """Validate external API connectivity."""
        pass
```

### Example 4: Alert Integration

```python
# src/monitoring/alerts.py
from enum import Enum
import requests

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertManager:
    """
    Alert management and notification system.
    Sends alerts via multiple channels.
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.alert_history: List[dict] = []
    
    def send_alert(self, title: str, message: str, severity: AlertSeverity):
        """
        Send alert via configured channels.
        Validation: Check rate limiting to prevent alert fatigue.
        """
        # Validate alert not duplicate
        if self._is_duplicate_alert(title, message):
            return
        
        alert_data = {
            "title": title,
            "message": message,
            "severity": severity.value,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send via configured channels
        if self.config.get("slack_enabled"):
            self._send_slack_alert(alert_data)
        
        if self.config.get("email_enabled"):
            self._send_email_alert(alert_data)
        
        if severity == AlertSeverity.CRITICAL and self.config.get("pagerduty_enabled"):
            self._send_pagerduty_alert(alert_data)
        
        self.alert_history.append(alert_data)
    
    def _send_slack_alert(self, alert_data: dict):
        """Send alert to Slack channel."""
        webhook_url = self.config.get("slack_webhook_url")
        if not webhook_url:
            return
        
        payload = {
            "text": f"*{alert_data['title']}*",
            "attachments": [{
                "color": self._get_color(alert_data['severity']),
                "fields": [
                    {"title": "Severity", "value": alert_data['severity'], "short": True},
                    {"title": "Timestamp", "value": alert_data['timestamp'], "short": True},
                    {"title": "Message", "value": alert_data['message'], "short": False}
                ]
            }]
        }
        
        requests.post(webhook_url, json=payload)
    
    def _get_color(self, severity: str) -> str:
        """Map severity to color for visual indicators."""
        colors = {
            "info": "#36a64f",
            "warning": "#ff9900",
            "error": "#ff6600",
            "critical": "#ff0000"
        }
        return colors.get(severity, "#808080")
```

## Configuration

### Status Reporting Configuration

```yaml
# status-config.yml
status:
  endpoints:
    health: /health
    status: /status
    metrics: /metrics
    ready: /ready
  
  checks:
    database:
      enabled: true
      timeout_seconds: 5
    cache:
      enabled: true
      timeout_seconds: 3
    storage:
      enabled: true
      timeout_seconds: 5
  
  alerts:
    slack:
      enabled: true
      webhook_url: ${SLACK_WEBHOOK_URL}
      channel: "#alerts"
    email:
      enabled: true
      recipients:
        - ops@example.com
    pagerduty:
      enabled: true
      api_key: ${PAGERDUTY_API_KEY}
  
  metrics:
    collection_interval_seconds: 60
    retention_days: 30
```

## Best Practices

### 1. Health Check Design
- **Quick checks**: Health endpoints should respond within 1-2 seconds
- **Meaningful checks**: Validate actual functionality, not just process existence
- **Graceful degradation**: Return degraded status rather than failing completely
- **Dependency checks**: Include critical dependencies in health checks

### 2. Status Reporting
- **Clear statuses**: Use consistent status values (healthy, degraded, unhealthy)
- **Detailed information**: Provide enough context for debugging
- **Timestamp everything**: Include timestamps for all status checks
- **Historical trends**: Track status over time for pattern detection

### 3. Alert Management
- **Rate limiting**: Prevent alert fatigue with intelligent throttling
- **Severity levels**: Use appropriate severity for different issues
- **Actionable alerts**: Include remediation steps in alert messages
- **Alert aggregation**: Group related alerts to reduce noise

### 4. Monitoring Integration
- **Standardized metrics**: Use Prometheus/OpenMetrics format
- **Dashboard visualization**: Create clear, actionable dashboards
- **Log correlation**: Link status reports with application logs
- **Tracing integration**: Connect status with distributed tracing

## Troubleshooting

### Common Issues

**Issue: Health Check Timeouts**
```python
# Solution: Add timeout safeguards
import asyncio

async def health_check_with_timeout():
    try:
        return await asyncio.wait_for(
            perform_health_check(),
            timeout=5.0
        )
    except asyncio.TimeoutError:
        return {"status": "timeout", "error": "Health check exceeded timeout"}
```

**Issue: False Positive Alerts**
```python
# Solution: Implement alert debouncing
from collections import deque
from datetime import datetime, timedelta

class AlertDebouncer:
    def __init__(self, window_minutes=5, threshold=3):
        self.window = timedelta(minutes=window_minutes)
        self.threshold = threshold
        self.alerts = deque()
    
    def should_alert(self, alert_key: str) -> bool:
        """Validation: Only alert if threshold breached in window."""
        now = datetime.utcnow()
        # Remove old alerts outside window
        while self.alerts and self.alerts[0][1] < now - self.window:
            self.alerts.popleft()
        
        # Count recent alerts for this key
        count = sum(1 for key, _ in self.alerts if key == alert_key)
        
        if count >= self.threshold:
            return True
        
        self.alerts.append((alert_key, now))
        return False
```

## Integration with Other Capabilities

- **Monitoring & Observability**: Provides status data for monitoring systems
- **CI/CD Pipeline**: Health checks validate deployment success
- **Inference Serving**: API health checks ensure model availability
- **MCP Services**: Status reporting for MCP server health

## Safeguards

- **Timeout protection**: All health checks have maximum execution time
- **Error handling**: Graceful failure handling prevents cascading failures
- **Rate limiting**: Alert throttling prevents notification storms
- **Validation**: Input validation on all status endpoints
- **Circuit breakers**: Prevent repeated failing health checks from overwhelming system

---

**Version**: 1.0  
**Last Updated**: 2025-12-09  
**Maintained By**: _codex_ Operations Team
