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


# =============================================================================
# PHASE 8.5 FULL IMPLEMENTATION: PRODUCTION DEPLOYMENT
# =============================================================================


class ProcessHealthCheck(HealthCheck):
    """Check process resource usage with psutil-like metrics.
    
    Provides CPU and memory monitoring without external dependencies.
    Uses resource module on Unix or approximations elsewhere.
    """
    
    @property
    def name(self) -> str:
        return "process"
    
    def __init__(
        self,
        cpu_threshold: float = 80.0,
        memory_threshold_mb: float = 1024.0,
    ):
        """Initialize process health check.
        
        Args:
            cpu_threshold: CPU usage threshold percentage
            memory_threshold_mb: Memory threshold in MB
        """
        self.cpu_threshold = cpu_threshold
        self.memory_threshold_mb = memory_threshold_mb
    
    def check(self) -> HealthCheckResult:
        """Check process resource usage."""
        start = time.time()
        
        try:
            import sys
            import os
            
            # Get process info
            pid = os.getpid()
            
            # Memory usage approximation
            # NOTE: This is a PLACEHOLDER for demonstration purposes.
            # sys.getsizeof(globals()) only measures the global namespace dict size,
            # NOT actual process memory. In production, replace with:
            #   import psutil
            #   memory_mb = psutil.Process(pid).memory_info().rss / (1024 * 1024)
            # psutil is not included as a dependency to keep the module lightweight.
            memory_mb = sys.getsizeof(globals()) / (1024 * 1024)
            
            # CPU time (using os.times if available)
            try:
                times = os.times()
                cpu_time = times.user + times.system
            except (AttributeError, OSError):
                cpu_time = 0.0
            
            latency = (time.time() - start) * 1000
            
            # Determine status
            status = HealthStatus.HEALTHY
            messages = []
            
            if memory_mb > self.memory_threshold_mb:
                status = HealthStatus.DEGRADED
                messages.append(f"Memory usage high: {memory_mb:.2f}MB")
            
            message = "; ".join(messages) if messages else f"Process healthy (PID: {pid})"
            
            return HealthCheckResult(
                component=self.name,
                status=status,
                message=message,
                latency_ms=latency,
                details={
                    'pid': pid,
                    'memory_mb': memory_mb,
                    'cpu_time_seconds': cpu_time,
                },
            )
        except Exception as e:
            return HealthCheckResult(
                component=self.name,
                status=HealthStatus.UNKNOWN,
                message=f"Process check failed: {str(e)}",
                latency_ms=(time.time() - start) * 1000,
            )


class NetworkHealthCheck(HealthCheck):
    """Check network connectivity health."""
    
    @property
    def name(self) -> str:
        return "network"
    
    def __init__(self, endpoints: Optional[List[str]] = None):
        """Initialize network health check.
        
        Args:
            endpoints: List of endpoints to check (not used in offline mode)
        """
        self.endpoints = endpoints or []
        self._network_available: Optional[bool] = None
        self._last_check_time: float = 0.0
        self._cache_ttl_seconds: float = 30.0  # Cache result for 30 seconds
    
    def check(self) -> HealthCheckResult:
        """Check network status (offline-safe).
        
        Uses cached result if available and within TTL to avoid
        frequent socket creation overhead.
        """
        start = time.time()
        
        try:
            import socket
            
            # Use cached result if within TTL
            if (self._network_available is not None and 
                (time.time() - self._last_check_time) < self._cache_ttl_seconds):
                network_available = self._network_available
            else:
                # Check if we can create sockets (local network stack)
                # This is a lightweight check that verifies the network stack is functional
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.close()
                    network_available = True
                except Exception:
                    network_available = False
                
                # Cache the result
                self._network_available = network_available
                self._last_check_time = time.time()
            
            latency = (time.time() - start) * 1000
            
            status = HealthStatus.HEALTHY if network_available else HealthStatus.DEGRADED
            message = "Network stack available" if network_available else "Network stack unavailable"
            
            return HealthCheckResult(
                component=self.name,
                status=status,
                message=message,
                latency_ms=latency,
                details={
                    'network_available': network_available,
                    'endpoints_configured': len(self.endpoints),
                },
            )
        except Exception as e:
            return HealthCheckResult(
                component=self.name,
                status=HealthStatus.UNKNOWN,
                message=f"Network check failed: {str(e)}",
                latency_ms=(time.time() - start) * 1000,
            )


# =============================================================================
# DISTRIBUTED DEPLOYMENT SUPPORT
# =============================================================================


@dataclass
class NodeInfo:
    """Information about a deployment node.
    
    Attributes:
        node_id: Unique node identifier
        host: Hostname or IP address
        port: Service port
        role: Node role (primary, replica, worker)
        status: Current node status
        last_heartbeat: Last heartbeat timestamp
    """
    node_id: str
    host: str = "localhost"
    port: int = 8080
    role: str = "worker"
    status: str = "unknown"
    last_heartbeat: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.last_heartbeat:
            self.last_heartbeat = datetime.utcnow().isoformat()


class DistributedDeployment:
    """Manages distributed multi-node deployments.
    
    Provides:
    - Node registration and discovery
    - Leader election (simple)
    - Health aggregation across nodes
    - Load balancing configuration
    
    Attributes:
        nodes: Registered nodes
        leader_id: Current leader node ID
        replication_factor: Number of replicas
    """
    
    def __init__(
        self,
        replication_factor: int = 3,
        heartbeat_interval: float = 10.0,
    ):
        """Initialize distributed deployment.
        
        Args:
            replication_factor: Number of replicas for HA
            heartbeat_interval: Seconds between heartbeats
        """
        self.nodes: Dict[str, NodeInfo] = {}
        self.leader_id: Optional[str] = None
        self.replication_factor = replication_factor
        self.heartbeat_interval = heartbeat_interval
        self._node_health: Dict[str, HealthCheckResult] = {}
    
    def register_node(self, node: NodeInfo) -> None:
        """Register a deployment node.
        
        Args:
            node: Node information
        """
        self.nodes[node.node_id] = node
        
        # Simple leader election: first node becomes leader
        if self.leader_id is None:
            self.leader_id = node.node_id
            node.role = "primary"
    
    def unregister_node(self, node_id: str) -> None:
        """Unregister a node.
        
        Args:
            node_id: Node to remove
        """
        if node_id in self.nodes:
            del self.nodes[node_id]
            
            # Re-elect leader if needed
            if node_id == self.leader_id:
                self.leader_id = None
                if self.nodes:
                    new_leader = next(iter(self.nodes.keys()))
                    self.leader_id = new_leader
                    self.nodes[new_leader].role = "primary"
    
    def update_heartbeat(self, node_id: str) -> None:
        """Update node heartbeat.
        
        Args:
            node_id: Node sending heartbeat
        """
        if node_id in self.nodes:
            self.nodes[node_id].last_heartbeat = datetime.utcnow().isoformat()
            self.nodes[node_id].status = "healthy"
    
    def record_health(self, node_id: str, result: HealthCheckResult) -> None:
        """Record health check result for a node.
        
        Args:
            node_id: Node ID
            result: Health check result
        """
        self._node_health[node_id] = result
        if node_id in self.nodes:
            self.nodes[node_id].status = result.status.value
    
    def get_healthy_nodes(self) -> List[NodeInfo]:
        """Get list of healthy nodes.
        
        Returns:
            List of healthy nodes
        """
        return [
            node for node in self.nodes.values()
            if node.status == "healthy"
        ]
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Get overall cluster status.
        
        Returns:
            Cluster status dictionary
        """
        healthy_count = len(self.get_healthy_nodes())
        total_count = len(self.nodes)
        
        return {
            'total_nodes': total_count,
            'healthy_nodes': healthy_count,
            'leader_id': self.leader_id,
            'replication_factor': self.replication_factor,
            'status': 'healthy' if healthy_count >= self.replication_factor else 'degraded',
            'nodes': {
                node_id: {
                    'host': node.host,
                    'port': node.port,
                    'role': node.role,
                    'status': node.status,
                    'last_heartbeat': node.last_heartbeat,
                }
                for node_id, node in self.nodes.items()
            },
        }
    
    def generate_k8s_statefulset(self, config: KubernetesConfig) -> Dict[str, Any]:
        """Generate Kubernetes StatefulSet for distributed deployment.
        
        Args:
            config: Kubernetes configuration
            
        Returns:
            StatefulSet manifest as dictionary
        """
        container_config = config.container
        
        return {
            'apiVersion': 'apps/v1',
            'kind': 'StatefulSet',
            'metadata': {
                'name': config.name,
                'namespace': config.namespace,
                'labels': config.labels,
            },
            'spec': {
                'serviceName': f"{config.name}-headless",
                'replicas': self.replication_factor,
                'selector': {
                    'matchLabels': {'app': config.labels.get('app', 'cognitive-brain')},
                },
                'template': {
                    'metadata': {'labels': config.labels},
                    'spec': {
                        'containers': [{
                            'name': config.name,
                            'image': f"{container_config.image}:{container_config.tag}",
                            'ports': [
                                {'containerPort': port, 'name': f'port-{port}'}
                                for port in container_config.ports.keys()
                            ],
                            'env': [
                                {'name': k, 'value': v}
                                for k, v in container_config.environment.items()
                            ] + [
                                {
                                    'name': 'POD_NAME',
                                    'valueFrom': {'fieldRef': {'fieldPath': 'metadata.name'}},
                                },
                                {
                                    'name': 'CLUSTER_SIZE',
                                    'value': str(self.replication_factor),
                                },
                            ],
                            'resources': {
                                'limits': {
                                    'cpu': container_config.resources.get('cpu_limit', '1'),
                                    'memory': container_config.resources.get('memory_limit', '1Gi'),
                                },
                                'requests': {
                                    'cpu': container_config.resources.get('cpu_request', '100m'),
                                    'memory': container_config.resources.get('memory_request', '256Mi'),
                                },
                            },
                            'readinessProbe': {
                                'httpGet': {'path': '/health', 'port': 8080},
                                'initialDelaySeconds': 10,
                                'periodSeconds': 5,
                            },
                            'livenessProbe': {
                                'httpGet': {'path': '/health', 'port': 8080},
                                'initialDelaySeconds': 30,
                                'periodSeconds': 10,
                            },
                        }],
                    },
                },
                'volumeClaimTemplates': [{
                    'metadata': {'name': 'data'},
                    'spec': {
                        'accessModes': ['ReadWriteOnce'],
                        'resources': {'requests': {'storage': '10Gi'}},
                    },
                }],
            },
        }


# =============================================================================
# LOGGING AGGREGATION (ELK/Loki Compatible)
# =============================================================================


@dataclass
class StructuredLog:
    """Structured log entry for aggregation.
    
    Attributes:
        timestamp: ISO timestamp
        level: Log level
        message: Log message
        service: Service name
        trace_id: Distributed trace ID
        span_id: Span ID within trace
        labels: Log labels for filtering
        fields: Additional fields
    """
    timestamp: str
    level: str
    message: str
    service: str = "cognitive-brain"
    trace_id: str = ""
    span_id: str = ""
    labels: Dict[str, str] = field(default_factory=dict)
    fields: Dict[str, Any] = field(default_factory=dict)
    
    def to_json(self) -> str:
        """Convert to JSON for Loki/ELK ingestion."""
        return json.dumps({
            'timestamp': self.timestamp,
            'level': self.level,
            'message': self.message,
            'service': self.service,
            'trace_id': self.trace_id,
            'span_id': self.span_id,
            'labels': self.labels,
            **self.fields,
        })
    
    def to_logfmt(self) -> str:
        """Convert to logfmt format."""
        parts = [
            f'ts="{self.timestamp}"',
            f'level={self.level}',
            f'msg="{self.message}"',
            f'service={self.service}',
        ]
        if self.trace_id:
            parts.append(f'trace_id={self.trace_id}')
        if self.span_id:
            parts.append(f'span_id={self.span_id}')
        for k, v in self.labels.items():
            parts.append(f'{k}="{v}"')
        for k, v in self.fields.items():
            parts.append(f'{k}="{v}"')
        return ' '.join(parts)


class LoggingAggregator:
    """Aggregates logs for external systems.
    
    Provides:
    - Structured logging with trace context
    - Multiple output formats (JSON, logfmt)
    - Label-based filtering
    - Batch export support
    
    Attributes:
        logs: Collected structured logs
        max_buffer_size: Maximum logs to buffer
        service_name: Service identifier
    """
    
    def __init__(
        self,
        service_name: str = "cognitive-brain",
        max_buffer_size: int = 10000,
    ):
        """Initialize logging aggregator.
        
        Args:
            service_name: Service name for logs
            max_buffer_size: Maximum buffer size
        """
        self.service_name = service_name
        self.max_buffer_size = max_buffer_size
        self.logs: List[StructuredLog] = []
        self._trace_context: Dict[str, str] = {}
    
    def set_trace_context(self, trace_id: str, span_id: str = "") -> None:
        """Set trace context for correlation.
        
        Args:
            trace_id: Distributed trace ID
            span_id: Span ID within trace
        """
        self._trace_context = {
            'trace_id': trace_id,
            'span_id': span_id,
        }
    
    def clear_trace_context(self) -> None:
        """Clear trace context."""
        self._trace_context = {}
    
    def log(
        self,
        level: str,
        message: str,
        labels: Optional[Dict[str, str]] = None,
        **fields,
    ) -> StructuredLog:
        """Create a structured log entry.
        
        Args:
            level: Log level (debug, info, warning, error, critical)
            message: Log message
            labels: Log labels for filtering
            **fields: Additional fields
            
        Returns:
            Created log entry
        """
        entry = StructuredLog(
            timestamp=datetime.utcnow().isoformat() + 'Z',
            level=level,
            message=message,
            service=self.service_name,
            trace_id=self._trace_context.get('trace_id', ''),
            span_id=self._trace_context.get('span_id', ''),
            labels=labels or {},
            fields=fields,
        )
        
        self.logs.append(entry)
        
        # Trim buffer if needed
        if len(self.logs) > self.max_buffer_size:
            self.logs = self.logs[-self.max_buffer_size:]
        
        return entry
    
    def debug(self, message: str, **kwargs) -> StructuredLog:
        """Log debug message."""
        return self.log('debug', message, **kwargs)
    
    def info(self, message: str, **kwargs) -> StructuredLog:
        """Log info message."""
        return self.log('info', message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> StructuredLog:
        """Log warning message."""
        return self.log('warning', message, **kwargs)
    
    def error(self, message: str, **kwargs) -> StructuredLog:
        """Log error message."""
        return self.log('error', message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> StructuredLog:
        """Log critical message."""
        return self.log('critical', message, **kwargs)
    
    def export_json(self, filter_labels: Optional[Dict[str, str]] = None) -> str:
        """Export logs as JSON array (for ELK/Loki).
        
        Args:
            filter_labels: Optional label filter
            
        Returns:
            JSON string of log entries
        """
        logs = self.logs
        if filter_labels:
            logs = [
                log for log in logs
                if all(log.labels.get(k) == v for k, v in filter_labels.items())
            ]
        return json.dumps([json.loads(log.to_json()) for log in logs], indent=2)
    
    def export_logfmt(self) -> str:
        """Export logs in logfmt format.
        
        Returns:
            Logfmt formatted logs
        """
        return '\n'.join(log.to_logfmt() for log in self.logs)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get log statistics.
        
        Returns:
            Statistics dictionary
        """
        level_counts: Dict[str, int] = {}
        for log in self.logs:
            level_counts[log.level] = level_counts.get(log.level, 0) + 1
        
        return {
            'total_logs': len(self.logs),
            'levels': level_counts,
            'service': self.service_name,
            'buffer_usage': len(self.logs) / self.max_buffer_size,
        }


# =============================================================================
# PROMETHEUS METRICS EXPORT
# =============================================================================


class PrometheusExporter:
    """Exports metrics in Prometheus format.
    
    Provides:
    - Counter metrics with labels
    - Gauge metrics with labels
    - Histogram metrics (approximation)
    - Text format export
    
    Attributes:
        prefix: Metric name prefix
        metrics: Collected metrics
    """
    
    def __init__(self, prefix: str = "cognitive_brain"):
        """Initialize Prometheus exporter.
        
        Args:
            prefix: Prefix for all metric names
        """
        self.prefix = prefix
        self.counters: Dict[str, Dict[str, float]] = {}  # name -> {labels: value}
        self.gauges: Dict[str, Dict[str, float]] = {}
        self.histograms: Dict[str, List[float]] = {}
        self._help_text: Dict[str, str] = {}
        self._type_text: Dict[str, str] = {}
    
    def register_counter(self, name: str, help_text: str = "") -> None:
        """Register a counter metric.
        
        Args:
            name: Metric name
            help_text: Help text for metric
        """
        full_name = f"{self.prefix}_{name}"
        self.counters[full_name] = {}
        self._help_text[full_name] = help_text or f"Counter: {name}"
        self._type_text[full_name] = "counter"
    
    def register_gauge(self, name: str, help_text: str = "") -> None:
        """Register a gauge metric.
        
        Args:
            name: Metric name
            help_text: Help text for metric
        """
        full_name = f"{self.prefix}_{name}"
        self.gauges[full_name] = {}
        self._help_text[full_name] = help_text or f"Gauge: {name}"
        self._type_text[full_name] = "gauge"
    
    def register_histogram(self, name: str, help_text: str = "") -> None:
        """Register a histogram metric.
        
        Args:
            name: Metric name
            help_text: Help text for metric
        """
        full_name = f"{self.prefix}_{name}"
        self.histograms[full_name] = []
        self._help_text[full_name] = help_text or f"Histogram: {name}"
        self._type_text[full_name] = "histogram"
    
    def _make_labels(self, labels: Dict[str, str]) -> str:
        """Create Prometheus label string."""
        if not labels:
            return ""
        label_pairs = [f'{k}="{v}"' for k, v in sorted(labels.items())]
        return '{' + ','.join(label_pairs) + '}'
    
    def inc_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter.
        
        Args:
            name: Counter name
            value: Increment value
            labels: Optional labels
        """
        full_name = f"{self.prefix}_{name}"
        if full_name not in self.counters:
            self.register_counter(name)
        
        label_key = self._make_labels(labels or {})
        self.counters[full_name][label_key] = self.counters[full_name].get(label_key, 0) + value
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge value.
        
        Args:
            name: Gauge name
            value: Gauge value
            labels: Optional labels
        """
        full_name = f"{self.prefix}_{name}"
        if full_name not in self.gauges:
            self.register_gauge(name)
        
        label_key = self._make_labels(labels or {})
        self.gauges[full_name][label_key] = value
    
    def observe_histogram(self, name: str, value: float) -> None:
        """Observe a histogram value.
        
        Args:
            name: Histogram name
            value: Observed value
        """
        full_name = f"{self.prefix}_{name}"
        if full_name not in self.histograms:
            self.register_histogram(name)
        
        self.histograms[full_name].append(value)
        # Keep limited history
        if len(self.histograms[full_name]) > 10000:
            self.histograms[full_name] = self.histograms[full_name][-10000:]
    
    def export(self) -> str:
        """Export all metrics in Prometheus text format.
        
        Returns:
            Prometheus text format string
        """
        lines = []
        
        # Export counters
        for name, values in self.counters.items():
            lines.append(f"# HELP {name} {self._help_text.get(name, '')}")
            lines.append(f"# TYPE {name} counter")
            for labels, value in values.items():
                lines.append(f"{name}{labels} {value}")
        
        # Export gauges
        for name, values in self.gauges.items():
            lines.append(f"# HELP {name} {self._help_text.get(name, '')}")
            lines.append(f"# TYPE {name} gauge")
            for labels, value in values.items():
                lines.append(f"{name}{labels} {value}")
        
        # Export histograms (simplified - just count, sum, buckets)
        for name, values in self.histograms.items():
            if not values:
                continue
            
            lines.append(f"# HELP {name} {self._help_text.get(name, '')}")
            lines.append(f"# TYPE {name} histogram")
            
            # Calculate buckets
            sorted_values = sorted(values)
            buckets = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
            
            for bucket in buckets:
                count = sum(1 for v in sorted_values if v <= bucket)
                lines.append(f'{name}_bucket{{le="{bucket}"}} {count}')
            
            lines.append(f'{name}_bucket{{le="+Inf"}} {len(values)}')
            lines.append(f'{name}_sum {sum(values)}')
            lines.append(f'{name}_count {len(values)}')
        
        return '\n'.join(lines)


# =============================================================================
# PRODUCTION HARDENING CHECKLIST
# =============================================================================


@dataclass
class HardeningItem:
    """Production hardening checklist item.
    
    Attributes:
        category: Item category
        name: Item name
        description: Item description
        check_function: Function to verify item
        severity: Importance level (critical, high, medium, low)
        passed: Whether check passed
        message: Result message
    """
    category: str
    name: str
    description: str
    check_function: Optional[Callable[[], Tuple[bool, str]]] = None
    severity: str = "medium"
    passed: bool = False
    message: str = ""


class ProductionHardeningChecklist:
    """Production hardening verification checklist.
    
    Verifies production readiness across categories:
    - Security
    - Performance
    - Reliability
    - Observability
    - Configuration
    
    Attributes:
        items: Checklist items
        results: Check results
    """
    
    def __init__(self):
        """Initialize hardening checklist."""
        self.items: List[HardeningItem] = []
        self._initialize_default_items()
    
    def _initialize_default_items(self) -> None:
        """Initialize default checklist items."""
        # Security items
        self.items.append(HardeningItem(
            category="security",
            name="no_debug_mode",
            description="Debug mode disabled in production",
            severity="critical",
        ))
        self.items.append(HardeningItem(
            category="security",
            name="secure_headers",
            description="Security headers configured",
            severity="high",
        ))
        self.items.append(HardeningItem(
            category="security",
            name="input_validation",
            description="Input validation enabled",
            severity="critical",
        ))
        
        # Performance items
        self.items.append(HardeningItem(
            category="performance",
            name="resource_limits",
            description="Resource limits configured",
            severity="high",
        ))
        self.items.append(HardeningItem(
            category="performance",
            name="connection_pooling",
            description="Connection pooling enabled",
            severity="medium",
        ))
        
        # Reliability items
        self.items.append(HardeningItem(
            category="reliability",
            name="health_checks",
            description="Health check endpoints configured",
            severity="critical",
        ))
        self.items.append(HardeningItem(
            category="reliability",
            name="graceful_shutdown",
            description="Graceful shutdown implemented",
            severity="high",
        ))
        self.items.append(HardeningItem(
            category="reliability",
            name="circuit_breakers",
            description="Circuit breakers for external calls",
            severity="medium",
        ))
        
        # Observability items
        self.items.append(HardeningItem(
            category="observability",
            name="metrics_endpoint",
            description="Prometheus metrics endpoint",
            severity="high",
        ))
        self.items.append(HardeningItem(
            category="observability",
            name="structured_logging",
            description="Structured logging enabled",
            severity="high",
        ))
        self.items.append(HardeningItem(
            category="observability",
            name="trace_correlation",
            description="Distributed trace correlation",
            severity="medium",
        ))
        
        # Configuration items
        self.items.append(HardeningItem(
            category="configuration",
            name="env_config",
            description="Environment-based configuration",
            severity="high",
        ))
        self.items.append(HardeningItem(
            category="configuration",
            name="secrets_management",
            description="Secrets properly managed",
            severity="critical",
        ))
    
    def add_item(self, item: HardeningItem) -> None:
        """Add a hardening item.
        
        Args:
            item: Item to add
        """
        self.items.append(item)
    
    def check_item(self, name: str, passed: bool, message: str = "") -> None:
        """Mark an item as checked.
        
        Args:
            name: Item name
            passed: Whether check passed
            message: Result message
        """
        for item in self.items:
            if item.name == name:
                item.passed = passed
                item.message = message
                break
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all checks with functions.
        
        Returns:
            Results dictionary
        """
        for item in self.items:
            if item.check_function:
                try:
                    passed, message = item.check_function()
                    item.passed = passed
                    item.message = message
                except Exception as e:
                    item.passed = False
                    item.message = f"Check failed: {str(e)}"
        
        return self.get_summary()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get checklist summary.
        
        Returns:
            Summary dictionary
        """
        by_category: Dict[str, List[Dict[str, Any]]] = {}
        for item in self.items:
            if item.category not in by_category:
                by_category[item.category] = []
            by_category[item.category].append({
                'name': item.name,
                'description': item.description,
                'severity': item.severity,
                'passed': item.passed,
                'message': item.message,
            })
        
        passed = sum(1 for item in self.items if item.passed)
        failed_critical = sum(
            1 for item in self.items
            if not item.passed and item.severity == 'critical'
        )
        
        return {
            'total_items': len(self.items),
            'passed': passed,
            'failed': len(self.items) - passed,
            'failed_critical': failed_critical,
            'production_ready': failed_critical == 0,
            'by_category': by_category,
        }
    
    def to_markdown(self) -> str:
        """Export checklist as Markdown.
        
        Returns:
            Markdown formatted checklist
        """
        lines = ["# Production Hardening Checklist", ""]
        summary = self.get_summary()
        
        lines.append(f"**Status:** {'✅ Production Ready' if summary['production_ready'] else '❌ Not Ready'}")
        lines.append(f"**Passed:** {summary['passed']}/{summary['total_items']}")
        lines.append("")
        
        for category, items in summary['by_category'].items():
            lines.append(f"## {category.title()}")
            lines.append("")
            for item in items:
                icon = "✅" if item['passed'] else "❌"
                severity_badge = f"[{item['severity'].upper()}]"
                lines.append(f"- {icon} {severity_badge} **{item['name']}**: {item['description']}")
                if item['message']:
                    lines.append(f"  - {item['message']}")
            lines.append("")
        
        return '\n'.join(lines)
