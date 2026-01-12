#!/usr/bin/env python3
"""
Unit tests for Service Integration Tester Agent

Tests cover:
- PII scrubbing functionality
- Mock data generation
- Endpoint discovery
- Single endpoint testing
- Contract validation
- Metrics tracking
- Report generation
"""

import pytest
import json
from pathlib import Path
from datetime import datetime, timezone
import tempfile
import yaml

# Import agent components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent import (
    ServiceIntegrationTester,
    TestStatus,
    EndpointMethod,
    MockDataType,
    Endpoint,
    ServiceContract,
    IntegrationTestSuite,
    TestResult,
    TestMetrics,
)


class TestPIIScrubbing:
    """Test PII scrubbing functionality"""
    
    def test_scrub_email_token_mode(self):
        """Test email scrubbing with token replacement"""
        tester = ServiceIntegrationTester()
        text = "Contact me at john.doe@example.com for info"
        
        result = tester.scrub_pii(text, mode="token")
        
        assert "john.doe@example.com" not in result
        assert "[EMAIL_REDACTED]" in result
    
    def test_scrub_phone_token_mode(self):
        """Test phone number scrubbing"""
        tester = ServiceIntegrationTester()
        text = "Call us at +1-555-123-4567 today"
        
        result = tester.scrub_pii(text, mode="token")
        
        assert "+1-555-123-4567" not in result
        assert "[PHONE_REDACTED]" in result
    
    def test_scrub_ssn(self):
        """Test SSN scrubbing"""
        tester = ServiceIntegrationTester()
        text = "SSN: 123-45-6789"
        
        result = tester.scrub_pii(text, mode="token")
        
        assert "123-45-6789" not in result
        assert "[SSN_REDACTED]" in result
    
    def test_scrub_credit_card(self):
        """Test credit card scrubbing"""
        tester = ServiceIntegrationTester()
        text = "Card: 1234-5678-9012-3456"
        
        result = tester.scrub_pii(text, mode="token")
        
        assert "1234-5678-9012-3456" not in result
        assert "[CREDIT_CARD_REDACTED]" in result
    
    def test_scrub_ip_address(self):
        """Test IP address scrubbing"""
        tester = ServiceIntegrationTester()
        text = "Server IP: 192.168.1.100"
        
        result = tester.scrub_pii(text, mode="token")
        
        assert "192.168.1.100" not in result
        assert "[IP_ADDRESS_REDACTED]" in result
    
    def test_scrub_aws_key(self):
        """Test AWS key scrubbing"""
        tester = ServiceIntegrationTester()
        text = "Key: AKIAIOSFODNN7EXAMPLE"
        
        result = tester.scrub_pii(text, mode="token")
        
        assert "AKIAIOSFODNN7EXAMPLE" not in result
        assert "[AWS_KEY_REDACTED]" in result
    
    def test_scrub_multiple_pii_types(self):
        """Test scrubbing multiple PII types in one text"""
        tester = ServiceIntegrationTester()
        text = "Contact john@example.com or call 555-1234 from IP 10.0.0.1"
        
        result = tester.scrub_pii(text, mode="token")
        
        assert "john@example.com" not in result
        assert "555-1234" not in result
        assert "10.0.0.1" not in result
    
    def test_scrub_hash_mode(self):
        """Test PII scrubbing with hash mode"""
        tester = ServiceIntegrationTester()
        text = "Email: test@example.com"
        
        result = tester.scrub_pii(text, mode="hash")
        
        assert "test@example.com" not in result
        assert "email_" in result
    
    def test_scrub_semantic_mode(self):
        """Test PII scrubbing with semantic preservation"""
        tester = ServiceIntegrationTester()
        text = "Contact: real.person@company.com"
        
        result = tester.scrub_pii(text, mode="semantic")
        
        assert "real.person@company.com" not in result
        assert "user@example.com" in result


class TestMockDataGeneration:
    """Test mock data generation functionality"""
    
    def test_generate_default_mock_data(self):
        """Test generating mock data with default schema"""
        tester = ServiceIntegrationTester()
        
        data = tester.generate_mock_data()
        
        assert 'id' in data
        assert 'name' in data
        assert 'created_at' in data
    
    def test_generate_custom_schema_string(self):
        """Test generating string type mock data"""
        tester = ServiceIntegrationTester()
        schema = {'username': 'string'}
        
        data = tester.generate_mock_data(schema)
        
        assert 'username' in data
        assert isinstance(data['username'], str)
        assert 'test_username_value' in data['username']
    
    def test_generate_custom_schema_int(self):
        """Test generating integer type mock data"""
        tester = ServiceIntegrationTester()
        schema = {'age': 'int', 'count': 'int'}
        
        data = tester.generate_mock_data(schema)
        
        assert 'age' in data
        assert 'count' in data
        assert isinstance(data['age'], int)
        assert isinstance(data['count'], int)
    
    def test_generate_custom_schema_bool(self):
        """Test generating boolean type mock data"""
        tester = ServiceIntegrationTester()
        schema = {'active': 'bool', 'verified': 'bool'}
        
        data = tester.generate_mock_data(schema)
        
        assert 'active' in data
        assert 'verified' in data
        assert isinstance(data['active'], bool)
        assert isinstance(data['verified'], bool)
    
    def test_generate_custom_schema_email(self):
        """Test generating email type mock data"""
        tester = ServiceIntegrationTester()
        schema = {'email': 'email'}
        
        data = tester.generate_mock_data(schema)
        
        assert 'email' in data
        assert '@' in data['email']
        assert 'example.com' in data['email']
    
    def test_generate_custom_schema_uuid(self):
        """Test generating UUID type mock data"""
        tester = ServiceIntegrationTester()
        schema = {'id': 'uuid'}
        
        data = tester.generate_mock_data(schema)
        
        assert 'id' in data
        assert '-' in data['id']  # UUID format
    
    def test_generate_custom_schema_timestamp(self):
        """Test generating timestamp type mock data"""
        tester = ServiceIntegrationTester()
        schema = {'created': 'timestamp'}
        
        data = tester.generate_mock_data(schema)
        
        assert 'created' in data
        # Should be ISO format
        datetime.fromisoformat(data['created'].replace('Z', '+00:00'))
    
    def test_generate_mixed_schema(self):
        """Test generating mock data with mixed types"""
        tester = ServiceIntegrationTester()
        schema = {
            'name': 'string',
            'age': 'int',
            'email': 'email',
            'active': 'bool',
            'score': 'float'
        }
        
        data = tester.generate_mock_data(schema)
        
        assert len(data) == 5
        assert isinstance(data['name'], str)
        assert isinstance(data['age'], int)
        assert '@' in data['email']
        assert isinstance(data['active'], bool)
        assert isinstance(data['score'], float)


class TestEndpointDiscovery:
    """Test endpoint discovery functionality"""
    
    def test_scan_common_endpoints(self):
        """Test scanning for common health endpoints"""
        tester = ServiceIntegrationTester()
        base_url = "https://api.example.com"
        
        endpoints = tester.scan_endpoints(base_url, "common")
        
        assert len(endpoints) > 0
        paths = [ep.path for ep in endpoints]
        assert '/health' in paths
        assert '/status' in paths
    
    def test_scan_endpoints_with_list(self):
        """Test scanning endpoints from a list"""
        tester = ServiceIntegrationTester()
        base_url = "https://api.example.com"
        spec_list = [
            {'path': '/api/users', 'method': 'GET'},
            {'path': '/api/users', 'method': 'POST'},
        ]
        
        endpoints = tester.scan_endpoints(base_url, spec_list)
        
        assert len(endpoints) == 2
        assert endpoints[0].path == '/api/users'
        assert endpoints[0].method == EndpointMethod.GET
        assert endpoints[1].method == EndpointMethod.POST
    
    def test_scan_endpoints_caching(self):
        """Test that discovered endpoints are cached"""
        tester = ServiceIntegrationTester()
        base_url = "https://api.example.com"
        
        tester.scan_endpoints(base_url, "common")
        
        assert base_url in tester.discovered_endpoints
        assert len(tester.discovered_endpoints[base_url]) > 0
    
    def test_scan_openapi_spec(self):
        """Test scanning endpoints from OpenAPI spec"""
        tester = ServiceIntegrationTester()
        
        # Create temporary OpenAPI spec
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            spec = {
                'openapi': '3.0.0',
                'paths': {
                    '/api/users': {
                        'get': {'summary': 'List users'},
                        'post': {'summary': 'Create user', 'security': [{'bearerAuth': []}]}
                    },
                    '/api/products': {
                        'get': {'summary': 'List products'}
                    }
                }
            }
            yaml.dump(spec, f)
            spec_path = Path(f.name)
        
        try:
            base_url = "https://api.example.com"
            endpoints = tester.scan_endpoints(base_url, spec_path)
            
            assert len(endpoints) == 3
            paths = [ep.path for ep in endpoints]
            assert '/api/users' in paths
            assert '/api/products' in paths
            
            # Check auth requirement
            post_endpoint = [ep for ep in endpoints if ep.method == EndpointMethod.POST][0]
            assert post_endpoint.requires_auth
        finally:
            spec_path.unlink()


class TestEndpointTesting:
    """Test single endpoint testing functionality"""
    
    def test_test_endpoint_success(self):
        """Test successful endpoint test"""
        tester = ServiceIntegrationTester()
        endpoint = Endpoint(
            path="/health",
            method=EndpointMethod.GET,
            base_url="https://api.example.com"
        )
        
        result = tester.test_endpoint_sync(endpoint)
        
        assert result.status == TestStatus.SUCCESS
        assert result.status_code == 200
        assert result.response_time_ms is not None
        assert result.response_time_ms > 0
    
    def test_test_endpoint_with_headers(self):
        """Test endpoint with custom headers"""
        tester = ServiceIntegrationTester()
        endpoint = Endpoint(
            path="/api/protected",
            method=EndpointMethod.GET,
            base_url="https://api.example.com",
            requires_auth=True
        )
        headers = {'Authorization': 'Bearer test-token'}
        
        result = tester.test_endpoint_sync(endpoint, headers=headers)
        
        assert result.status in [TestStatus.SUCCESS, TestStatus.FAILURE]
    
    def test_test_endpoint_with_payload(self):
        """Test endpoint with request payload"""
        tester = ServiceIntegrationTester()
        endpoint = Endpoint(
            path="/api/users",
            method=EndpointMethod.POST,
            base_url="https://api.example.com",
            expected_status=201
        )
        payload = {'name': 'Test User', 'email': 'test@example.com'}
        
        result = tester.test_endpoint_sync(endpoint, payload=payload)
        
        assert result.status == TestStatus.SUCCESS
        assert result.status_code == 201
    
    def test_test_endpoint_pii_scrubbing(self):
        """Test that PII is scrubbed from payloads"""
        tester = ServiceIntegrationTester()
        endpoint = Endpoint(
            path="/api/users",
            method=EndpointMethod.POST,
            base_url="https://api.example.com"
        )
        payload = {
            'name': 'John Doe',
            'email': 'john.doe@realcompany.com',
            'phone': '555-123-4567'
        }
        
        result = tester.test_endpoint_sync(endpoint, payload=payload)
        
        # PII should be scrubbed before sending
        assert result.status in [TestStatus.SUCCESS, TestStatus.FAILURE]
    
    def test_test_endpoint_metrics_update(self):
        """Test that metrics are updated after endpoint test"""
        tester = ServiceIntegrationTester()
        endpoint = Endpoint(
            path="/health",
            method=EndpointMethod.GET,
            base_url="https://api.example.com"
        )
        
        initial_total = tester.metrics.total_tests
        tester.test_endpoint_sync(endpoint)
        
        assert tester.metrics.total_tests == initial_total + 1
        assert tester.metrics.passed > 0 or tester.metrics.failed > 0


class TestServiceContractTesting:
    """Test service contract validation"""
    
    def test_test_service_contract_basic(self):
        """Test basic service contract testing"""
        tester = ServiceIntegrationTester()
        
        contract = ServiceContract(
            service_name="test-service",
            base_url="https://api.example.com",
            endpoints=[
                Endpoint(path="/health", method=EndpointMethod.GET, base_url="https://api.example.com"),
                Endpoint(path="/status", method=EndpointMethod.GET, base_url="https://api.example.com"),
            ]
        )
        
        results = tester.test_service_contract(contract)
        
        assert len(results) == 2
        assert all(isinstance(r, TestResult) for r in results)
    
    def test_test_service_contract_with_auth(self):
        """Test service contract with authentication"""
        tester = ServiceIntegrationTester()
        
        contract = ServiceContract(
            service_name="auth-service",
            base_url="https://api.example.com",
            auth_type="bearer",
            endpoints=[
                Endpoint(path="/api/protected", method=EndpointMethod.GET, 
                        base_url="https://api.example.com", requires_auth=True),
            ]
        )
        
        results = tester.test_service_contract(contract, auth_token="test-token")
        
        assert len(results) == 1
    
    def test_test_service_contract_api_key(self):
        """Test service contract with API key authentication"""
        tester = ServiceIntegrationTester()
        
        contract = ServiceContract(
            service_name="api-key-service",
            base_url="https://api.example.com",
            auth_type="api_key",
            endpoints=[
                Endpoint(path="/api/data", method=EndpointMethod.GET, base_url="https://api.example.com"),
            ]
        )
        
        results = tester.test_service_contract(contract, auth_token="my-api-key")
        
        assert len(results) == 1


class TestIntegrationSuite:
    """Test integration test suite functionality"""
    
    def test_run_integration_suite_empty(self):
        """Test running empty integration suite"""
        tester = ServiceIntegrationTester()
        
        suite = IntegrationTestSuite(
            name="empty-suite",
            description="Empty test suite"
        )
        
        success, metrics = tester.run_integration_suite(suite)
        
        assert success
        assert metrics.total_tests >= 0
    
    def test_run_integration_suite_with_contracts(self):
        """Test running integration suite with contracts"""
        tester = ServiceIntegrationTester()
        
        contract = ServiceContract(
            service_name="test-service",
            base_url="https://api.example.com",
            endpoints=[
                Endpoint(path="/health", method=EndpointMethod.GET, base_url="https://api.example.com"),
            ]
        )
        
        suite = IntegrationTestSuite(
            name="basic-suite",
            description="Basic test suite",
            contracts=[contract]
        )
        
        success, metrics = tester.run_integration_suite(suite)
        
        assert isinstance(success, bool)
        assert metrics.total_tests >= 1
    
    def test_run_integration_suite_verbose(self):
        """Test running integration suite with verbose output"""
        tester = ServiceIntegrationTester()
        
        contract = ServiceContract(
            service_name="verbose-service",
            base_url="https://api.example.com",
            endpoints=[
                Endpoint(path="/status", method=EndpointMethod.GET, base_url="https://api.example.com"),
            ]
        )
        
        suite = IntegrationTestSuite(
            name="verbose-suite",
            description="Verbose test suite",
            contracts=[contract]
        )
        
        success, metrics = tester.run_integration_suite(suite, verbose=True)
        
        assert isinstance(success, bool)


class TestContractValidation:
    """Test API contract compliance validation"""
    
    def test_validate_contract_compliance_success(self):
        """Test successful contract validation"""
        tester = ServiceIntegrationTester()
        
        # Create temporary spec
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            spec = {
                'openapi': '3.0.0',
                'paths': {
                    '/health': {
                        'get': {'summary': 'Health check'}
                    }
                }
            }
            yaml.dump(spec, f)
            spec_path = Path(f.name)
        
        try:
            compliant, violations = tester.validate_contract_compliance(
                spec_path,
                "https://api.example.com"
            )
            
            assert isinstance(compliant, bool)
            assert isinstance(violations, list)
        finally:
            spec_path.unlink()
    
    def test_validate_contract_compliance_no_endpoints(self):
        """Test contract validation with no endpoints"""
        tester = ServiceIntegrationTester()
        
        # Create empty spec
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            spec = {'openapi': '3.0.0', 'paths': {}}
            yaml.dump(spec, f)
            spec_path = Path(f.name)
        
        try:
            compliant, violations = tester.validate_contract_compliance(
                spec_path,
                "https://api.example.com"
            )
            
            assert not compliant
            assert len(violations) > 0
            assert any("No endpoints" in v for v in violations)
        finally:
            spec_path.unlink()


class TestMetricsAndReporting:
    """Test metrics tracking and report generation"""
    
    def test_get_metrics_initial_state(self):
        """Test getting metrics in initial state"""
        tester = ServiceIntegrationTester()
        
        metrics = tester.get_metrics()
        
        assert metrics['total_tests'] == 0
        assert metrics['passed'] == 0
        assert metrics['success_rate'] == 0.0
    
    def test_get_metrics_after_tests(self):
        """Test getting metrics after running tests"""
        tester = ServiceIntegrationTester()
        
        endpoint = Endpoint(
            path="/health",
            method=EndpointMethod.GET,
            base_url="https://api.example.com"
        )
        tester.test_endpoint_sync(endpoint)
        tester.test_endpoint_sync(endpoint)
        
        metrics = tester.get_metrics()
        
        assert metrics['total_tests'] == 2
        assert metrics['success_rate'] > 0.0
    
    def test_generate_report_basic(self):
        """Test generating basic report"""
        tester = ServiceIntegrationTester()
        
        endpoint = Endpoint(
            path="/health",
            method=EndpointMethod.GET,
            base_url="https://api.example.com"
        )
        tester.test_endpoint_sync(endpoint)
        
        report = tester.generate_report()
        
        assert "SERVICE INTEGRATION TEST REPORT" in report
        assert "SUMMARY" in report
        assert "Total Tests:" in report
    
    def test_generate_report_to_file(self):
        """Test generating report to file"""
        tester = ServiceIntegrationTester()
        
        endpoint = Endpoint(
            path="/status",
            method=EndpointMethod.GET,
            base_url="https://api.example.com"
        )
        tester.test_endpoint_sync(endpoint)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            report = tester.generate_report(output_path)
            
            assert output_path.exists()
            content = output_path.read_text()
            assert "SERVICE INTEGRATION TEST REPORT" in content
        finally:
            output_path.unlink()
    
    def test_export_results_json(self):
        """Test exporting results as JSON"""
        tester = ServiceIntegrationTester()
        
        endpoint = Endpoint(
            path="/health",
            method=EndpointMethod.GET,
            base_url="https://api.example.com"
        )
        tester.test_endpoint_sync(endpoint)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            tester.export_results_json(output_path)
            
            assert output_path.exists()
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            assert 'timestamp' in data
            assert 'metrics' in data
            assert 'results' in data
            assert len(data['results']) == 1
        finally:
            output_path.unlink()


class TestConfiguration:
    """Test agent configuration loading"""
    
    def test_load_config_from_file(self):
        """Test loading configuration from YAML file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config = {
                'agent_name': 'service-integration-tester',
                'timeout_ms': 10000,
                'retries': 3
            }
            yaml.dump(config, f)
            config_path = Path(f.name)
        
        try:
            tester = ServiceIntegrationTester(config_path)
            
            assert tester.config is not None
            assert tester.config['agent_name'] == 'service-integration-tester'
        finally:
            config_path.unlink()
    
    def test_init_without_config(self):
        """Test initializing without configuration"""
        tester = ServiceIntegrationTester()
        
        assert tester.config == {}
        assert tester.test_results == []
        assert tester.metrics.total_tests == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
