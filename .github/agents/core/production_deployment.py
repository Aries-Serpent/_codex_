"""
Production Deployment Module for Cognitive Brain.

Phase 8.5 Implementation:
- HealthCheckEndpoint: Service health monitoring
- MonitoringIntegration: Logging and metrics
- DeploymentConfiguration: Docker/K8s config generation
- ProductionTestSuite: Production-ready test harness

Status: Skeleton implementation (Phase 8.5)
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Tuple
from abc import ABC, abstractmethod
from enum import Enum
import json
import time
from datetime import datetime


class HealthStatus(Enum):
    """Health check status values."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check.
    
    Attributes:
        component: Component name
        status: Health status
        message: Status message
        latency_ms: Check latency in milliseconds
        details: Additional details
        timestamp: Check timestamp
    """
    component: str
    status: HealthStatus
    message: str = ""
    latency_ms: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    
    def __post_init__(self):
        """Initialize computed fields."""
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


class HealthCheck(ABC):
    """Abstract base class for health checks."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get check name."""
        pass
    
    @abstractmethod
    def check(self) -> HealthCheckResult:
        """Perform health check."""
        pass


class MemoryHealthCheck(HealthCheck):
    """Check memory usage health."""
    
    @property
    def name(self) -> str:
        return "memory"
    
    def __init__(self, threshold_mb: float = 1024.0):
        """Initialize memory health check.
        
        Args:
            threshold_mb: Memory threshold in MB
        """
        self.threshold_mb = threshold_mb
    
    def check(self) -> HealthCheckResult:
        """Check memory usage."""
        start = time.time()
        
        try:
            import sys
            # NOTE: This is a placeholder implementation for demonstration.
            # In production, use psutil.Process().memory_info().rss / (1024 * 1024)
            # The current implementation uses sys.getsizeof as a minimal footprint check.
            memory_mb = sys.getsizeof({}) / (1024 * 1024)  # Minimal object memory only
            
            latency = (time.time() - start) * 1000
            
            # For placeholder, always report healthy since we're not measuring real usage
            status = HealthStatus.HEALTHY
            message = f"Memory check completed (placeholder): {memory_mb:.4f}MB"
            
            return HealthCheckResult(
                component=self.name,
                status=status,
                message=message,
                latency_ms=latency,
                details={'memory_mb': memory_mb, 'threshold_mb': self.threshold_mb},
            )
        except Exception as e:
            return HealthCheckResult(
                component=self.name,
                status=HealthStatus.UNKNOWN,
                message=f"Check failed: {str(e)}",
                latency_ms=(time.time() - start) * 1000,
            )


class DatabaseHealthCheck(HealthCheck):
    """Check database connectivity health."""
    
    @property
    def name(self) -> str:
        return "database"
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database health check.
        
        Args:
            db_path: Path to database file
        """
        self.db_path = db_path or ":memory:"
    
    def check(self) -> HealthCheckResult:
        """Check database connectivity."""
        start = time.time()
        
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path, timeout=5.0)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            conn.close()
            
            latency = (time.time() - start) * 1000
            
            return HealthCheckResult(
                component=self.name,
                status=HealthStatus.HEALTHY,
                message="Database connection successful",
                latency_ms=latency,
                details={'db_path': self.db_path},
            )
        except Exception as e:
            return HealthCheckResult(
                component=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}",
                latency_ms=(time.time() - start) * 1000,
            )


class LearningEngineHealthCheck(HealthCheck):
    """Check learning engine health."""
    
    @property
    def name(self) -> str:
        return "learning_engine"
    
    def __init__(self, engine: Optional[Any] = None):
        """Initialize learning engine health check.
        
        Args:
            engine: Learning engine instance to check
        """
        self.engine = engine
    
    def check(self) -> HealthCheckResult:
        """Check learning engine status."""
        start = time.time()
        
        if self.engine is None:
            return HealthCheckResult(
                component=self.name,
                status=HealthStatus.UNKNOWN,
                message="No engine configured",
                latency_ms=(time.time() - start) * 1000,
            )
        
        try:
            # Check engine has required methods
            has_select = hasattr(self.engine, 'select_action')
            has_update = hasattr(self.engine, 'update')
            
            latency = (time.time() - start) * 1000
            
            if has_select and has_update:
                return HealthCheckResult(
                    component=self.name,
                    status=HealthStatus.HEALTHY,
                    message="Learning engine operational",
                    latency_ms=latency,
                    details={'has_select_action': has_select, 'has_update': has_update},
                )
            else:
                return HealthCheckResult(
                    component=self.name,
                    status=HealthStatus.DEGRADED,
                    message="Learning engine missing methods",
                    latency_ms=latency,
                    details={'has_select_action': has_select, 'has_update': has_update},
                )
        except Exception as e:
            return HealthCheckResult(
                component=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Check failed: {str(e)}",
                latency_ms=(time.time() - start) * 1000,
            )


class HealthCheckEndpoint:
    """Aggregated health check endpoint.
    
    Manages multiple health checks and provides unified health status.
    
    Attributes:
        checks: Registered health checks
        results: Last check results
        check_interval_seconds: Interval between automatic checks
    """
    
    def __init__(self, check_interval_seconds: float = 30.0):
        """Initialize health check endpoint.
        
        Args:
            check_interval_seconds: Interval between checks
        """
        self.checks: List[HealthCheck] = []
        self.results: Dict[str, HealthCheckResult] = {}
        self.check_interval_seconds = check_interval_seconds
        self._last_check_time: Optional[float] = None
    
    def register(self, check: HealthCheck) -> None:
        """Register a health check.
        
        Args:
            check: Health check to register
        """
        self.checks.append(check)
    
    def run_checks(self) -> Dict[str, HealthCheckResult]:
        """Run all registered health checks.
        
        Returns:
            Results for all checks
        """
        for check in self.checks:
            result = check.check()
            self.results[check.name] = result
        
        self._last_check_time = time.time()
        return dict(self.results)
    
    def get_overall_status(self) -> HealthStatus:
        """Get overall health status.
        
        Returns:
            Aggregated health status
        """
        if not self.results:
            return HealthStatus.UNKNOWN
        
        statuses = [r.status for r in self.results.values()]
        
        if all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        elif any(s == HealthStatus.UNHEALTHY for s in statuses):
            return HealthStatus.UNHEALTHY
        elif any(s == HealthStatus.DEGRADED for s in statuses):
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.UNKNOWN
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response.
        
        Returns:
            Dictionary representation
        """
        return {
            'status': self.get_overall_status().value,
            'checks': {
                name: {
                    'status': result.status.value,
                    'message': result.message,
                    'latency_ms': result.latency_ms,
                    'timestamp': result.timestamp,
                }
                for name, result in self.results.items()
            },
            'last_check': datetime.fromtimestamp(self._last_check_time).isoformat()
            if self._last_check_time else None,
        }


# =============================================================================
# MONITORING INTEGRATION
# =============================================================================


@dataclass
class MetricValue:
    """A metric measurement.
    
    Attributes:
        name: Metric name
        value: Metric value
        labels: Metric labels
        timestamp: Measurement timestamp
    """
    name: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


class MetricsCollector:
    """Collects and aggregates metrics.
    
    Attributes:
        metrics: Collected metrics
        counters: Counter metrics
        gauges: Gauge metrics
    """
    
    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: List[MetricValue] = []
        self.counters: Dict[str, float] = {}
        self.gauges: Dict[str, float] = {}
    
    def increment(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric.
        
        Args:
            name: Counter name
            value: Increment value
            labels: Metric labels
        """
        key = self._make_key(name, labels or {})
        self.counters[key] = self.counters.get(key, 0) + value
        self.metrics.append(MetricValue(name, self.counters[key], labels or {}))
    
    def gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge metric.
        
        Args:
            name: Gauge name
            value: Gauge value
            labels: Metric labels
        """
        key = self._make_key(name, labels or {})
        self.gauges[key] = value
        self.metrics.append(MetricValue(name, value, labels or {}))
    
    def _make_key(self, name: str, labels: Dict[str, str]) -> str:
        """Create unique key from name and labels."""
        if not labels:
            return name
        label_str = ','.join(f'{k}={v}' for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    def get_counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """Get counter value."""
        key = self._make_key(name, labels or {})
        return self.counters.get(key, 0)
    
    def get_gauge(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """Get gauge value."""
        key = self._make_key(name, labels or {})
        return self.gauges.get(key, 0)
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        return {
            'counters': dict(self.counters),
            'gauges': dict(self.gauges),
            'total_measurements': len(self.metrics),
        }


class LogLevel(Enum):
    """Log levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class LogEntry:
    """A log entry.
    
    Attributes:
        level: Log level
        message: Log message
        logger: Logger name
        timestamp: Log timestamp
        extra: Additional context
    """
    level: LogLevel
    message: str
    logger: str = "cognitive_brain"
    timestamp: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'level': self.level.value,
            'message': self.message,
            'logger': self.logger,
            'timestamp': self.timestamp,
            **self.extra,
        }


class LogAggregator:
    """Aggregates log entries for monitoring.
    
    Attributes:
        entries: Log entries
        max_entries: Maximum entries to retain
    """
    
    def __init__(self, max_entries: int = 1000):
        """Initialize log aggregator.
        
        Args:
            max_entries: Maximum entries to keep
        """
        self.entries: List[LogEntry] = []
        self.max_entries = max_entries
    
    def log(self, level: LogLevel, message: str, **extra) -> LogEntry:
        """Add a log entry.
        
        Args:
            level: Log level
            message: Log message
            **extra: Additional context
            
        Returns:
            Created log entry
        """
        entry = LogEntry(level=level, message=message, extra=extra)
        self.entries.append(entry)
        
        # Trim if needed
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]
        
        return entry
    
    def debug(self, message: str, **extra) -> LogEntry:
        """Log debug message."""
        return self.log(LogLevel.DEBUG, message, **extra)
    
    def info(self, message: str, **extra) -> LogEntry:
        """Log info message."""
        return self.log(LogLevel.INFO, message, **extra)
    
    def warning(self, message: str, **extra) -> LogEntry:
        """Log warning message."""
        return self.log(LogLevel.WARNING, message, **extra)
    
    def error(self, message: str, **extra) -> LogEntry:
        """Log error message."""
        return self.log(LogLevel.ERROR, message, **extra)
    
    def critical(self, message: str, **extra) -> LogEntry:
        """Log critical message."""
        return self.log(LogLevel.CRITICAL, message, **extra)
    
    def get_entries(
        self,
        level: Optional[LogLevel] = None,
        limit: int = 100,
    ) -> List[LogEntry]:
        """Get log entries.
        
        Args:
            level: Filter by level
            limit: Maximum entries to return
            
        Returns:
            Matching log entries
        """
        entries = self.entries
        if level:
            entries = [e for e in entries if e.level == level]
        return entries[-limit:]


class MonitoringIntegration:
    """Unified monitoring integration.
    
    Combines health checks, metrics, and logging.
    
    Attributes:
        health: Health check endpoint
        metrics: Metrics collector
        logs: Log aggregator
    """
    
    def __init__(self):
        """Initialize monitoring integration."""
        self.health = HealthCheckEndpoint()
        self.metrics = MetricsCollector()
        self.logs = LogAggregator()
        
        # Register default health checks
        self.health.register(MemoryHealthCheck())
        self.health.register(DatabaseHealthCheck())
    
    def record_action(
        self,
        action: str,
        success: bool,
        latency_ms: float,
        **labels,
    ) -> None:
        """Record an action execution.
        
        Args:
            action: Action name
            success: Whether action succeeded
            latency_ms: Execution latency
            **labels: Additional labels
        """
        self.metrics.increment(
            'cognitive_brain_actions_total',
            labels={'action': action, 'success': str(success).lower(), **labels},
        )
        self.metrics.gauge(
            'cognitive_brain_action_latency_ms',
            latency_ms,
            labels={'action': action, **labels},
        )
        
        level = LogLevel.INFO if success else LogLevel.WARNING
        self.logs.log(level, f"Action executed: {action}", success=success, latency_ms=latency_ms)
    
    def record_learning_update(
        self,
        domain: str,
        q_value_delta: float,
    ) -> None:
        """Record a learning update.
        
        Args:
            domain: Learning domain
            q_value_delta: Change in Q-value
        """
        self.metrics.increment(
            'cognitive_brain_learning_updates_total',
            labels={'domain': domain},
        )
        self.metrics.gauge(
            'cognitive_brain_q_value_delta',
            q_value_delta,
            labels={'domain': domain},
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get full monitoring status.
        
        Returns:
            Status dictionary
        """
        self.health.run_checks()
        return {
            'health': self.health.to_dict(),
            'metrics': self.metrics.get_all_metrics(),
            'logs': {
                'recent_errors': [
                    e.to_dict() for e in self.logs.get_entries(LogLevel.ERROR, limit=10)
                ],
                'total_entries': len(self.logs.entries),
            },
        }


# =============================================================================
# DEPLOYMENT CONFIGURATION
# =============================================================================


@dataclass
class ContainerConfig:
    """Container configuration.
    
    Attributes:
        image: Container image name
        tag: Image tag
        ports: Port mappings (container:host)
        environment: Environment variables
        volumes: Volume mounts
        resources: Resource limits
    """
    image: str = "cognitive-brain"
    tag: str = "latest"
    ports: Dict[int, int] = field(default_factory=lambda: {8080: 8080})
    environment: Dict[str, str] = field(default_factory=dict)
    volumes: Dict[str, str] = field(default_factory=dict)
    resources: Dict[str, Any] = field(default_factory=lambda: {
        'cpu_limit': '1',
        'memory_limit': '1Gi',
        'cpu_request': '100m',
        'memory_request': '256Mi',
    })


@dataclass
class KubernetesConfig:
    """Kubernetes deployment configuration.
    
    Attributes:
        name: Deployment name
        namespace: Kubernetes namespace
        replicas: Number of replicas
        container: Container configuration
        labels: Resource labels
        annotations: Resource annotations
    """
    name: str = "cognitive-brain"
    namespace: str = "default"
    replicas: int = 1
    container: ContainerConfig = field(default_factory=ContainerConfig)
    labels: Dict[str, str] = field(default_factory=lambda: {
        'app': 'cognitive-brain',
        'component': 'learning-engine',
    })
    annotations: Dict[str, str] = field(default_factory=dict)


class DeploymentConfiguration:
    """Generates deployment configurations.
    
    Creates Docker and Kubernetes configurations for
    production deployment.
    
    Attributes:
        container: Container configuration
        k8s: Kubernetes configuration
    """
    
    def __init__(
        self,
        container: Optional[ContainerConfig] = None,
        k8s: Optional[KubernetesConfig] = None,
    ):
        """Initialize deployment configuration.
        
        Args:
            container: Container config
            k8s: Kubernetes config
        """
        self.container = container or ContainerConfig()
        self.k8s = k8s or KubernetesConfig()
    
    def generate_dockerfile(self) -> str:
        """Generate Dockerfile content.
        
        Returns:
            Dockerfile content
        """
        env_lines = '\n'.join(
            f'ENV {k}={v}'
            for k, v in self.container.environment.items()
        )
        
        port_expose = ' '.join(str(p) for p in self.container.ports.keys())
        
        return f'''# Cognitive Brain Production Dockerfile
# Generated by DeploymentConfiguration

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Environment
{env_lines}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8080/health')"

# Expose ports
EXPOSE {port_expose}

# Run
CMD ["python", "-m", "cognitive_brain.server"]
'''
    
    def generate_k8s_deployment(self) -> Dict[str, Any]:
        """Generate Kubernetes deployment manifest.
        
        Returns:
            Kubernetes deployment as dictionary
        """
        return {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': self.k8s.name,
                'namespace': self.k8s.namespace,
                'labels': self.k8s.labels,
                'annotations': self.k8s.annotations,
            },
            'spec': {
                'replicas': self.k8s.replicas,
                'selector': {
                    'matchLabels': {'app': self.k8s.labels.get('app', 'cognitive-brain')},
                },
                'template': {
                    'metadata': {
                        'labels': self.k8s.labels,
                    },
                    'spec': {
                        'containers': [{
                            'name': self.k8s.name,
                            'image': f"{self.container.image}:{self.container.tag}",
                            'ports': [
                                {'containerPort': port}
                                for port in self.container.ports.keys()
                            ],
                            'env': [
                                {'name': k, 'value': v}
                                for k, v in self.container.environment.items()
                            ],
                            'resources': {
                                'limits': {
                                    'cpu': self.container.resources.get('cpu_limit', '1'),
                                    'memory': self.container.resources.get('memory_limit', '1Gi'),
                                },
                                'requests': {
                                    'cpu': self.container.resources.get('cpu_request', '100m'),
                                    'memory': self.container.resources.get('memory_request', '256Mi'),
                                },
                            },
                            'livenessProbe': {
                                'httpGet': {
                                    'path': '/health',
                                    'port': 8080,
                                },
                                'initialDelaySeconds': 30,
                                'periodSeconds': 10,
                            },
                            'readinessProbe': {
                                'httpGet': {
                                    'path': '/health',
                                    'port': 8080,
                                },
                                'initialDelaySeconds': 5,
                                'periodSeconds': 5,
                            },
                        }],
                    },
                },
            },
        }
    
    def generate_k8s_service(self) -> Dict[str, Any]:
        """Generate Kubernetes service manifest.
        
        Returns:
            Kubernetes service as dictionary
        """
        return {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': f"{self.k8s.name}-service",
                'namespace': self.k8s.namespace,
            },
            'spec': {
                'selector': {'app': self.k8s.labels.get('app', 'cognitive-brain')},
                'ports': [
                    {'port': host, 'targetPort': container}
                    for container, host in self.container.ports.items()
                ],
                'type': 'ClusterIP',
            },
        }
    
    def to_json(self, manifest: Dict[str, Any]) -> str:
        """Convert manifest to JSON string.
        
        Note: For YAML output, use PyYAML library in production.
        This method provides JSON-formatted output which is compatible
        with Kubernetes (kubectl apply -f supports JSON).
        
        Args:
            manifest: Manifest dictionary
            
        Returns:
            JSON string (Kubernetes-compatible)
        """
        return json.dumps(manifest, indent=2)


# =============================================================================
# PRODUCTION TEST SUITE
# =============================================================================


class ProductionTest(ABC):
    """Abstract base class for production tests."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Test name."""
        pass
    
    @property
    @abstractmethod
    def critical(self) -> bool:
        """Whether test is critical for deployment."""
        pass
    
    @abstractmethod
    def run(self) -> Tuple[bool, str]:
        """Run the test.
        
        Returns:
            Tuple of (passed, message)
        """
        pass


class HealthEndpointTest(ProductionTest):
    """Test health endpoint availability."""
    
    @property
    def name(self) -> str:
        return "health_endpoint"
    
    @property
    def critical(self) -> bool:
        return True
    
    def __init__(self, endpoint: HealthCheckEndpoint):
        """Initialize test."""
        self.endpoint = endpoint
    
    def run(self) -> Tuple[bool, str]:
        """Run health endpoint test."""
        try:
            results = self.endpoint.run_checks()
            status = self.endpoint.get_overall_status()
            
            if status in (HealthStatus.HEALTHY, HealthStatus.DEGRADED):
                return True, f"Health endpoint operational: {status.value}"
            else:
                return False, f"Health endpoint unhealthy: {status.value}"
        except Exception as e:
            return False, f"Health endpoint failed: {str(e)}"


class LearningEngineTest(ProductionTest):
    """Test learning engine functionality."""
    
    @property
    def name(self) -> str:
        return "learning_engine"
    
    @property
    def critical(self) -> bool:
        return True
    
    def __init__(self, engine: Optional[Any] = None):
        """Initialize test."""
        self.engine = engine
    
    def run(self) -> Tuple[bool, str]:
        """Run learning engine test."""
        if self.engine is None:
            return False, "No learning engine configured"
        
        try:
            # Check basic methods exist
            if not hasattr(self.engine, 'select_action'):
                return False, "Learning engine missing select_action"
            if not hasattr(self.engine, 'update'):
                return False, "Learning engine missing update"
            
            return True, "Learning engine operational"
        except Exception as e:
            return False, f"Learning engine test failed: {str(e)}"


class ProductionTestSuite:
    """Production-ready test harness.
    
    Runs production tests before and after deployment.
    
    Attributes:
        tests: Registered tests
        results: Test results
    """
    
    def __init__(self):
        """Initialize test suite."""
        self.tests: List[ProductionTest] = []
        self.results: Dict[str, Tuple[bool, str]] = {}
    
    def register(self, test: ProductionTest) -> None:
        """Register a production test.
        
        Args:
            test: Test to register
        """
        self.tests.append(test)
    
    def run_all(self) -> bool:
        """Run all registered tests.
        
        Returns:
            True if all critical tests passed
        """
        all_critical_passed = True
        
        for test in self.tests:
            passed, message = test.run()
            self.results[test.name] = (passed, message)
            
            if test.critical and not passed:
                all_critical_passed = False
        
        return all_critical_passed
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test summary.
        
        Returns:
            Summary dictionary
        """
        passed = sum(1 for p, _ in self.results.values() if p)
        failed = len(self.results) - passed
        
        return {
            'total': len(self.results),
            'passed': passed,
            'failed': failed,
            'all_critical_passed': all(
                p for test in self.tests
                for p, _ in [self.results.get(test.name, (True, ''))]
                if test.critical
            ),
            'results': {
                name: {'passed': passed, 'message': msg}
                for name, (passed, msg) in self.results.items()
            },
        }
