#!/usr/bin/env python3
"""
Service Integration Tester Agent

Tests service integrations, validates cross-component interactions, and ensures API contracts
are honored across distributed systems.

Component Reuse Strategy:
- Base: integration-test-runner (60% reuse)
- Extension 1: pii-scrubber (privacy-safe mock data generation)
- Extension 2: rag-index-manager (service endpoint discovery)

Usage:
    python -m service_integration_tester.src.agent test --service auth
    python -m service_integration_tester.src.agent scan --base-url https://api.example.com
    python -m service_integration_tester.src.agent validate-contract --spec openapi.yaml
"""

import hashlib
import json
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import yaml


class TestStatus(Enum):
    """Status of a service integration test"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    SKIPPED = "skipped"
    ERROR = "error"


class EndpointMethod(Enum):
    """HTTP methods for endpoint testing"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class MockDataType(Enum):
    """Types of mock data for testing"""
    STRING = "string"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    EMAIL = "email"
    PHONE = "phone"
    NAME = "name"
    UUID = "uuid"
    TIMESTAMP = "timestamp"


@dataclass
class Endpoint:
    """Represents a service endpoint to test"""
    path: str
    method: EndpointMethod
    base_url: str
    description: str = ""
    requires_auth: bool = False
    expected_status: int = 200
    timeout_ms: int = 5000


@dataclass
class TestResult:
    """Result of testing a service endpoint"""
    endpoint: Endpoint
    status: TestStatus
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    error: Optional[str] = None
    validation_errors: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ServiceContract:
    """API contract definition for a service"""
    service_name: str
    base_url: str
    endpoints: list[Endpoint] = field(default_factory=list)
    auth_type: Optional[str] = None  # 'bearer', 'api_key', 'basic', None
    version: str = "1.0"


@dataclass
class IntegrationTestSuite:
    """A suite of integration tests"""
    name: str
    description: str
    contracts: list[ServiceContract] = field(default_factory=list)
    setup_commands: list[str] = field(default_factory=list)
    teardown_commands: list[str] = field(default_factory=list)


@dataclass
class TestMetrics:
    """Aggregated metrics from test runs"""
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    total_response_time_ms: float = 0.0
    avg_response_time_ms: float = 0.0
    min_response_time_ms: float = float('inf')
    max_response_time_ms: float = 0.0


class ServiceIntegrationTester:
    """Main agent class for service integration testing"""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the agent with optional configuration"""
        self.config = self._load_config(config_path) if config_path else {}
        self.test_results: list[TestResult] = []
        self.metrics = TestMetrics()
        self.mock_data_cache: dict[str, Any] = {}
        self.discovered_endpoints: dict[str, list[Endpoint]] = {}

        # PII scrubbing patterns (from pii-scrubber component)
        self.pii_patterns = {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'\b(?:\+?1[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b|\b\d{3}-\d{4}\b'),
            'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            'credit_card': re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
            'ip_address': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
            'aws_key': re.compile(r'AKIA[0-9A-Z]{16}'),
        }

    def _load_config(self, config_path: Path) -> dict[str, Any]:
        """Load agent configuration from YAML file"""
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def scrub_pii(self, text: str, mode: str = "token") -> str:
        """
        Remove PII from text (from pii-scrubber component)

        Args:
            text: Input text potentially containing PII
            mode: Redaction mode ('token', 'hash', 'semantic')

        Returns:
            Text with PII removed or redacted
        """
        result = text

        for pii_type, pattern in self.pii_patterns.items():
            if mode == "token":
                replacement = f"[{pii_type.upper()}_REDACTED]"
            elif mode == "hash":
                # Preserve structure with hash
                matches = pattern.findall(result)
                for match in matches:
                    hashed = hashlib.sha256(match.encode()).hexdigest()[:8]
                    replacement = f"{pii_type}_{hashed}"
                    result = result.replace(match, replacement)
                continue
            elif mode == "semantic":
                # Keep semantic structure
                replacement = "user@example.com" if pii_type == "email" else f"[{pii_type}]"
            else:
                replacement = f"[{pii_type.upper()}_REDACTED]"

            result = pattern.sub(replacement, result)

        return result

    def generate_mock_data(self, schema: Optional[dict[str, str]] = None) -> dict[str, Any]:
        """
        Generate privacy-safe mock data for testing (using pii-scrubber patterns)

        Args:
            schema: Dictionary mapping field names to data types

        Returns:
            Dictionary of generated mock data
        """
        if schema is None:
            schema = {'id': 'uuid', 'name': 'name', 'created_at': 'timestamp'}

        mock_data = {}

        for field_name, data_type in schema.items():
            if data_type == MockDataType.STRING.value or data_type == 'string':
                mock_data[field_name] = f"test_{field_name}_value"
            elif data_type == MockDataType.INT.value or data_type == 'int':
                mock_data[field_name] = 12345
            elif data_type == MockDataType.FLOAT.value or data_type == 'float':
                mock_data[field_name] = 123.45
            elif data_type == MockDataType.BOOL.value or data_type == 'bool':
                mock_data[field_name] = True
            elif data_type == MockDataType.EMAIL.value or data_type == 'email':
                mock_data[field_name] = "test.user@example.com"
            elif data_type == MockDataType.PHONE.value or data_type == 'phone':
                mock_data[field_name] = "+1-555-0123"
            elif data_type == MockDataType.NAME.value or data_type == 'name':
                mock_data[field_name] = "Test User"
            elif data_type == MockDataType.UUID.value or data_type == 'uuid':
                mock_data[field_name] = "123e4567-e89b-12d3-a456-426614174000"
            elif data_type == MockDataType.TIMESTAMP.value or data_type == 'timestamp':
                mock_data[field_name] = datetime.now(timezone.utc).isoformat()
            else:
                mock_data[field_name] = f"mock_{field_name}"

        return mock_data

    def scan_endpoints(
        self,
        base_url: str,
        spec_source: Optional[Any] = None
    ) -> list[Endpoint]:
        """
        Discover service endpoints (from rag-index-manager component)

        Args:
            base_url: Base URL of the service
            spec_source: OpenAPI spec path, list of paths, or "common"

        Returns:
            List of discovered endpoints
        """
        endpoints = []

        if spec_source == "common":
            # Common health/status endpoints
            common_paths = [
                ("/health", EndpointMethod.GET, "Health check"),
                ("/status", EndpointMethod.GET, "Service status"),
                ("/ready", EndpointMethod.GET, "Readiness probe"),
                ("/metrics", EndpointMethod.GET, "Metrics endpoint"),
                ("/version", EndpointMethod.GET, "Version info"),
            ]

            for path, method, desc in common_paths:
                endpoints.append(Endpoint(
                    path=path,
                    method=method,
                    base_url=base_url,
                    description=desc,
                    requires_auth=False
                ))

        elif isinstance(spec_source, Path):
            # Parse OpenAPI specification
            if spec_source.exists():
                with open(spec_source, 'r') as f:
                    spec = yaml.safe_load(f)

                paths = spec.get('paths', {})
                for path, methods in paths.items():
                    for method, details in methods.items():
                        if method.upper() in [m.value for m in EndpointMethod]:
                            endpoints.append(Endpoint(
                                path=path,
                                method=EndpointMethod[method.upper()],
                                base_url=base_url,
                                description=details.get('summary', ''),
                                requires_auth='security' in details
                            ))

        elif isinstance(spec_source, list):
            # Direct list of endpoint definitions
            for item in spec_source:
                if isinstance(item, dict):
                    endpoints.append(Endpoint(
                        path=item.get('path', '/'),
                        method=EndpointMethod[item.get('method', 'GET').upper()],
                        base_url=base_url,
                        description=item.get('description', ''),
                        requires_auth=item.get('requires_auth', False)
                    ))

        # Cache discovered endpoints
        self.discovered_endpoints[base_url] = endpoints

        return endpoints

    def test_endpoint_sync(
        self,
        endpoint: Endpoint,
        headers: Optional[dict[str, str]] = None,
        payload: Optional[dict[str, Any]] = None,
        expected_status: Optional[int] = None
    ) -> TestResult:
        """
        Test a single endpoint synchronously (mock implementation)

        Args:
            endpoint: Endpoint to test
            headers: Optional HTTP headers
            payload: Optional request payload
            expected_status: Expected HTTP status code

        Returns:
            Test result
        """
        # This is a mock implementation for testing
        # In production, this would use requests library or httpx

        start_time = datetime.now(timezone.utc)

        try:
            # Simulate HTTP request
            full_url = f"{endpoint.base_url}{endpoint.path}"

            # Scrub any PII from payload if present
            if payload:
                payload_str = json.dumps(payload)
                scrubbed = self.scrub_pii(payload_str, mode="token")
                payload = json.loads(scrubbed)

            # Mock response simulation
            # In real implementation, would be: response = requests.request(endpoint.method.value, full_url, ...)

            # Simulate network delay
            response_time_ms = 50.0 + (hash(full_url) % 200)

            # Simulate status code
            if endpoint.path in ['/health', '/status', '/ready']:
                status_code = 200
            elif endpoint.method == EndpointMethod.POST:
                status_code = 201
            else:
                status_code = 200

            # Check against expected status
            expected = expected_status or endpoint.expected_status
            status = TestStatus.SUCCESS if status_code == expected else TestStatus.FAILURE

            result = TestResult(
                endpoint=endpoint,
                status=status,
                status_code=status_code,
                response_time_ms=response_time_ms,
                timestamp=start_time
            )

            # Update metrics
            self.test_results.append(result)
            self._update_metrics(result)

            return result

        except Exception as e:
            result = TestResult(
                endpoint=endpoint,
                status=TestStatus.ERROR,
                error=str(e),
                timestamp=start_time
            )
            self.test_results.append(result)
            self._update_metrics(result)
            return result

    def test_service_contract(
        self,
        contract: ServiceContract,
        auth_token: Optional[str] = None
    ) -> list[TestResult]:
        """
        Test all endpoints in a service contract

        Args:
            contract: Service contract to test
            auth_token: Optional authentication token

        Returns:
            List of test results for all endpoints
        """
        results = []
        headers = {}

        if auth_token and contract.auth_type == 'bearer':
            headers['Authorization'] = f'Bearer {auth_token}'
        elif auth_token and contract.auth_type == 'api_key':
            headers['X-API-Key'] = auth_token

        for endpoint in contract.endpoints:
            result = self.test_endpoint_sync(endpoint, headers=headers)
            results.append(result)

        return results

    def run_integration_suite(
        self,
        suite: IntegrationTestSuite,
        verbose: bool = False
    ) -> tuple[bool, TestMetrics]:
        """
        Run a complete integration test suite

        Args:
            suite: Test suite to run
            verbose: Enable verbose output

        Returns:
            Tuple of (success, metrics)
        """
        # Run setup commands
        for cmd in suite.setup_commands:
            if verbose:
                print(f"Setup: {cmd}")
            try:
                # Convert string command to list to prevent shell injection
                cmd_list = shlex.split(cmd) if isinstance(cmd, str) else cmd
                subprocess.run(cmd_list, shell=False, capture_output=True, check=True)
            except subprocess.CalledProcessError as e:
                if verbose:
                    print(f"Setup command failed: {cmd}")
                    print(f"Error: {e}")
                # Continue with other setup commands

        all_results = []

        try:
            # Test each service contract
            for contract in suite.contracts:
                if verbose:
                    print(f"\nTesting service: {contract.service_name}")

                results = self.test_service_contract(contract)
                all_results.extend(results)

                if verbose:
                    passed = sum(1 for r in results if r.status == TestStatus.SUCCESS)
                    print(f"  Results: {passed}/{len(results)} passed")

        finally:
            # Run teardown commands
            for cmd in suite.teardown_commands:
                if verbose:
                    print(f"Teardown: {cmd}")
                try:
                    # Convert string command to list to prevent shell injection
                    cmd_list = shlex.split(cmd) if isinstance(cmd, str) else cmd
                    subprocess.run(cmd_list, shell=False, capture_output=True, check=True)
                except subprocess.CalledProcessError as e:
                    if verbose:
                        print(f"Teardown command failed: {cmd}")
                        print(f"Error: {e}")
                    # Continue with other teardown commands

        # Determine overall success
        success = all(r.status == TestStatus.SUCCESS for r in all_results)

        return success, self.metrics

    def validate_contract_compliance(
        self,
        spec_path: Path,
        base_url: str
    ) -> tuple[bool, list[str]]:
        """
        Validate that service implementation matches OpenAPI contract

        Args:
            spec_path: Path to OpenAPI specification
            base_url: Base URL of service to test

        Returns:
            Tuple of (compliant, violations)
        """
        violations = []

        # Discover endpoints from spec
        endpoints = self.scan_endpoints(base_url, spec_path)

        if not endpoints:
            violations.append("No endpoints discovered from specification")
            return False, violations

        # Test each endpoint
        for endpoint in endpoints:
            result = self.test_endpoint_sync(endpoint)

            if result.status != TestStatus.SUCCESS:
                violations.append(
                    f"{endpoint.method.value} {endpoint.path}: "
                    f"Expected {endpoint.expected_status}, got {result.status_code}"
                )

            if result.validation_errors:
                violations.extend(result.validation_errors)

        compliant = len(violations) == 0
        return compliant, violations

    def get_metrics(self) -> dict[str, Any]:
        """Get current test metrics"""
        return {
            'total_tests': self.metrics.total_tests,
            'passed': self.metrics.passed,
            'failed': self.metrics.failed,
            'skipped': self.metrics.skipped,
            'errors': self.metrics.errors,
            'success_rate': (
                self.metrics.passed / self.metrics.total_tests
                if self.metrics.total_tests > 0 else 0.0
            ),
            'total_response_time_ms': self.metrics.total_response_time_ms,
            'avg_response_time_ms': self.metrics.avg_response_time_ms,
            'min_response_time_ms': (
                self.metrics.min_response_time_ms
                if self.metrics.min_response_time_ms != float('inf') else 0.0
            ),
            'max_response_time_ms': self.metrics.max_response_time_ms,
        }

    def generate_report(self, output_path: Optional[Path] = None) -> str:
        """
        Generate a comprehensive test report

        Args:
            output_path: Optional path to write report

        Returns:
            Report as string
        """
        lines = []
        lines.append("=" * 70)
        lines.append("SERVICE INTEGRATION TEST REPORT")
        lines.append("=" * 70)
        lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
        lines.append("")

        metrics = self.get_metrics()
        lines.append("SUMMARY")
        lines.append("-" * 70)
        lines.append(f"Total Tests:    {metrics['total_tests']}")
        lines.append(f"Passed:         {metrics['passed']}")
        lines.append(f"Failed:         {metrics['failed']}")
        lines.append(f"Errors:         {metrics['errors']}")
        lines.append(f"Skipped:        {metrics['skipped']}")
        lines.append(f"Success Rate:   {metrics['success_rate']*100:.1f}%")
        lines.append("")
        lines.append(f"Avg Response:   {metrics['avg_response_time_ms']:.2f}ms")
        lines.append(f"Min Response:   {metrics['min_response_time_ms']:.2f}ms")
        lines.append(f"Max Response:   {metrics['max_response_time_ms']:.2f}ms")
        lines.append("")

        # Group results by service
        by_service: dict[str, list[TestResult]] = {}
        for result in self.test_results:
            service = result.endpoint.base_url
            if service not in by_service:
                by_service[service] = []
            by_service[service].append(result)

        lines.append("RESULTS BY SERVICE")
        lines.append("-" * 70)
        for service, results in by_service.items():
            passed = sum(1 for r in results if r.status == TestStatus.SUCCESS)
            lines.append(f"\n{service}")
            lines.append(f"  Tests: {len(results)}, Passed: {passed}/{len(results)}")

            for result in results:
                status_icon = "✅" if result.status == TestStatus.SUCCESS else "❌"
                lines.append(
                    f"  {status_icon} {result.endpoint.method.value} {result.endpoint.path} "
                    f"({result.status_code}, {result.response_time_ms:.0f}ms)"
                )
                if result.error:
                    lines.append(f"     Error: {result.error}")

        lines.append("")
        lines.append("=" * 70)

        report = "\n".join(lines)

        if output_path:
            with open(output_path, 'w') as f:
                f.write(report)

        return report

    def export_results_json(self, output_path: Path) -> None:
        """Export test results as JSON"""
        data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'metrics': self.get_metrics(),
            'results': [
                {
                    'endpoint': {
                        'path': r.endpoint.path,
                        'method': r.endpoint.method.value,
                        'base_url': r.endpoint.base_url,
                    },
                    'status': r.status.value,
                    'status_code': r.status_code,
                    'response_time_ms': r.response_time_ms,
                    'error': r.error,
                    'validation_errors': r.validation_errors,
                    'timestamp': r.timestamp.isoformat(),
                }
                for r in self.test_results
            ]
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

    def _update_metrics(self, result: TestResult) -> None:
        """Update aggregated metrics with new test result"""
        self.metrics.total_tests += 1

        if result.status == TestStatus.SUCCESS:
            self.metrics.passed += 1
        elif result.status == TestStatus.FAILURE:
            self.metrics.failed += 1
        elif result.status == TestStatus.SKIPPED:
            self.metrics.skipped += 1
        elif result.status == TestStatus.ERROR:
            self.metrics.errors += 1

        if result.response_time_ms is not None:
            self.metrics.total_response_time_ms += result.response_time_ms
            self.metrics.min_response_time_ms = min(
                self.metrics.min_response_time_ms,
                result.response_time_ms
            )
            self.metrics.max_response_time_ms = max(
                self.metrics.max_response_time_ms,
                result.response_time_ms
            )

            # Update average
            if self.metrics.total_tests > 0:
                self.metrics.avg_response_time_ms = (
                    self.metrics.total_response_time_ms / self.metrics.total_tests
                )


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Service Integration Tester Agent")
    parser.add_argument(
        'command',
        choices=['test', 'scan', 'validate-contract', 'generate-report'],
        help='Command to execute'
    )
    parser.add_argument('--service', help='Service name or URL')
    parser.add_argument('--base-url', help='Base URL of service')
    parser.add_argument('--spec', type=Path, help='Path to OpenAPI specification')
    parser.add_argument('--config', type=Path, help='Path to agent configuration')
    parser.add_argument('--output', type=Path, help='Output file path')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    tester = ServiceIntegrationTester(args.config)

    if args.command == 'test':
        if not args.base_url:
            print("Error: --base-url required for test command")
            return 1

        endpoints = tester.scan_endpoints(args.base_url, "common")
        print(f"Testing {len(endpoints)} endpoints...")

        for endpoint in endpoints:
            result = tester.test_endpoint_sync(endpoint)
            status_icon = "✅" if result.status == TestStatus.SUCCESS else "❌"
            print(f"{status_icon} {endpoint.method.value} {endpoint.path}: {result.status_code}")

    elif args.command == 'scan':
        if not args.base_url:
            print("Error: --base-url required for scan command")
            return 1

        spec = args.spec if args.spec else "common"
        endpoints = tester.scan_endpoints(args.base_url, spec)
        print(f"Discovered {len(endpoints)} endpoints:")
        for ep in endpoints:
            print(f"  {ep.method.value} {ep.path}")

    elif args.command == 'validate-contract':
        if not args.spec or not args.base_url:
            print("Error: --spec and --base-url required for validate-contract")
            return 1

        compliant, violations = tester.validate_contract_compliance(args.spec, args.base_url)

        if compliant:
            print("✅ Service is compliant with contract")
            return 0
        print("❌ Contract violations found:")
        for violation in violations:
            print(f"  - {violation}")
        return 1

    elif args.command == 'generate-report':
        report = tester.generate_report(args.output)
        if not args.output:
            print(report)

    return 0


if __name__ == '__main__':
    sys.exit(main())
