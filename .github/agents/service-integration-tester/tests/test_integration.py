#!/usr/bin/env python3
"""
Integration tests for Service Integration Tester Agent

Tests full workflows including:
- Multi-service testing
- End-to-end contract validation
- Performance testing workflows
- CLI integration
- File I/O operations
"""

import pytest
import json
import subprocess
import tempfile
from pathlib import Path
import yaml

# Import agent components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent import (
    ServiceIntegrationTester,
    TestStatus,
    EndpointMethod,
    Endpoint,
    ServiceContract,
    IntegrationTestSuite,
)


class TestMultiServiceIntegration:
    """Test integration across multiple services"""
    
    def test_multiple_services_health_check(self):
        """Test health checks across multiple services"""
        tester = ServiceIntegrationTester()
        
        services = {
            'auth': 'https://auth.example.com',
            'users': 'https://users.example.com',
            'payments': 'https://payments.example.com'
        }
        
        all_results = []
        
        for service_name, base_url in services.items():
            endpoints = tester.scan_endpoints(base_url, "common")
            
            for endpoint in endpoints:
                result = tester.test_endpoint_sync(endpoint)
                all_results.append(result)
        
        assert len(all_results) > 0
        # At least some endpoints should succeed
        success_count = sum(1 for r in all_results if r.status == TestStatus.SUCCESS)
        assert success_count > 0
    
    def test_service_dependency_chain(self):
        """Test a chain of dependent service calls"""
        tester = ServiceIntegrationTester()
        
        # Step 1: Authenticate
        auth_endpoint = Endpoint(
            path="/auth/login",
            method=EndpointMethod.POST,
            base_url="https://api.example.com",
            expected_status=200
        )
        auth_result = tester.test_endpoint_sync(
            auth_endpoint,
            payload={'username': 'testuser', 'password': 'testpass'}
        )
        
        assert auth_result.status in [TestStatus.SUCCESS, TestStatus.FAILURE]
        
        # Step 2: Fetch user data (would use token from step 1)
        user_endpoint = Endpoint(
            path="/api/user/profile",
            method=EndpointMethod.GET,
            base_url="https://api.example.com",
            requires_auth=True
        )
        user_result = tester.test_endpoint_sync(
            user_endpoint,
            headers={'Authorization': 'Bearer mock-token'}
        )
        
        assert user_result.status in [TestStatus.SUCCESS, TestStatus.FAILURE]
        
        # Step 3: Update profile
        update_endpoint = Endpoint(
            path="/api/user/profile",
            method=EndpointMethod.PATCH,
            base_url="https://api.example.com",
            requires_auth=True
        )
        update_result = tester.test_endpoint_sync(
            update_endpoint,
            headers={'Authorization': 'Bearer mock-token'},
            payload={'display_name': 'Updated Name'}
        )
        
        assert update_result.status in [TestStatus.SUCCESS, TestStatus.FAILURE]
        
        # Verify all steps were recorded
        assert len(tester.test_results) == 3
    
    def test_parallel_service_testing(self):
        """Test multiple services in parallel (simulated)"""
        tester = ServiceIntegrationTester()
        
        contracts = [
            ServiceContract(
                service_name="service1",
                base_url="https://service1.example.com",
                endpoints=[
                    Endpoint(path="/health", method=EndpointMethod.GET, 
                            base_url="https://service1.example.com")
                ]
            ),
            ServiceContract(
                service_name="service2",
                base_url="https://service2.example.com",
                endpoints=[
                    Endpoint(path="/health", method=EndpointMethod.GET,
                            base_url="https://service2.example.com")
                ]
            ),
            ServiceContract(
                service_name="service3",
                base_url="https://service3.example.com",
                endpoints=[
                    Endpoint(path="/health", method=EndpointMethod.GET,
                            base_url="https://service3.example.com")
                ]
            ),
        ]
        
        all_results = []
        for contract in contracts:
            results = tester.test_service_contract(contract)
            all_results.extend(results)
        
        assert len(all_results) == 3
        assert tester.metrics.total_tests == 3


class TestEndToEndContractValidation:
    """Test end-to-end contract validation workflows"""
    
    def test_complete_api_contract_validation(self):
        """Test validating a complete API contract"""
        tester = ServiceIntegrationTester()
        
        # Create comprehensive OpenAPI spec
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            spec = {
                'openapi': '3.0.0',
                'info': {'title': 'Test API', 'version': '1.0.0'},
                'paths': {
                    '/health': {
                        'get': {
                            'summary': 'Health check',
                            'responses': {'200': {'description': 'Healthy'}}
                        }
                    },
                    '/api/users': {
                        'get': {
                            'summary': 'List users',
                            'responses': {'200': {'description': 'User list'}}
                        },
                        'post': {
                            'summary': 'Create user',
                            'security': [{'bearerAuth': []}],
                            'responses': {'201': {'description': 'User created'}}
                        }
                    },
                    '/api/users/{id}': {
                        'get': {
                            'summary': 'Get user',
                            'responses': {'200': {'description': 'User details'}}
                        },
                        'put': {
                            'summary': 'Update user',
                            'security': [{'bearerAuth': []}],
                            'responses': {'200': {'description': 'User updated'}}
                        },
                        'delete': {
                            'summary': 'Delete user',
                            'security': [{'bearerAuth': []}],
                            'responses': {'204': {'description': 'User deleted'}}
                        }
                    }
                }
            }
            yaml.dump(spec, f)
            spec_path = Path(f.name)
        
        try:
            base_url = "https://api.example.com"
            
            # Discover endpoints
            endpoints = tester.scan_endpoints(base_url, spec_path)
            
            assert len(endpoints) > 0
            
            # Validate contract
            compliant, violations = tester.validate_contract_compliance(spec_path, base_url)
            
            assert isinstance(compliant, bool)
            assert isinstance(violations, list)
            
        finally:
            spec_path.unlink()
    
    def test_rest_api_crud_workflow(self):
        """Test complete REST API CRUD workflow"""
        tester = ServiceIntegrationTester()
        base_url = "https://api.example.com"
        
        # CREATE
        create_endpoint = Endpoint(
            path="/api/resources",
            method=EndpointMethod.POST,
            base_url=base_url,
            expected_status=201
        )
        create_payload = tester.generate_mock_data({
            'name': 'string',
            'description': 'string',
            'active': 'bool'
        })
        create_result = tester.test_endpoint_sync(create_endpoint, payload=create_payload)
        
        assert create_result.status == TestStatus.SUCCESS
        
        # READ (list)
        list_endpoint = Endpoint(
            path="/api/resources",
            method=EndpointMethod.GET,
            base_url=base_url
        )
        list_result = tester.test_endpoint_sync(list_endpoint)
        
        assert list_result.status == TestStatus.SUCCESS
        
        # READ (single)
        get_endpoint = Endpoint(
            path="/api/resources/123",
            method=EndpointMethod.GET,
            base_url=base_url
        )
        get_result = tester.test_endpoint_sync(get_endpoint)
        
        assert get_result.status == TestStatus.SUCCESS
        
        # UPDATE
        update_endpoint = Endpoint(
            path="/api/resources/123",
            method=EndpointMethod.PUT,
            base_url=base_url
        )
        update_payload = tester.generate_mock_data({
            'name': 'string',
            'description': 'string'
        })
        update_result = tester.test_endpoint_sync(update_endpoint, payload=update_payload)
        
        assert update_result.status == TestStatus.SUCCESS
        
        # DELETE
        delete_endpoint = Endpoint(
            path="/api/resources/123",
            method=EndpointMethod.DELETE,
            base_url=base_url,
            expected_status=204
        )
        delete_result = tester.test_endpoint_sync(delete_endpoint, expected_status=204)
        
        # All operations recorded
        assert len(tester.test_results) == 5


class TestPerformanceWorkflows:
    """Test performance testing workflows"""
    
    def test_response_time_tracking(self):
        """Test that response times are tracked correctly"""
        tester = ServiceIntegrationTester()
        
        endpoint = Endpoint(
            path="/health",
            method=EndpointMethod.GET,
            base_url="https://api.example.com"
        )
        
        # Run multiple tests
        for _ in range(5):
            tester.test_endpoint_sync(endpoint)
        
        metrics = tester.get_metrics()
        
        assert metrics['total_tests'] == 5
        assert metrics['avg_response_time_ms'] > 0
        assert metrics['min_response_time_ms'] > 0
        assert metrics['max_response_time_ms'] > 0
        assert metrics['min_response_time_ms'] <= metrics['avg_response_time_ms']
        assert metrics['avg_response_time_ms'] <= metrics['max_response_time_ms']
    
    def test_load_testing_simulation(self):
        """Test simulating load testing"""
        tester = ServiceIntegrationTester()
        
        endpoint = Endpoint(
            path="/api/endpoint",
            method=EndpointMethod.GET,
            base_url="https://api.example.com"
        )
        
        # Simulate 20 requests
        num_requests = 20
        for _ in range(num_requests):
            tester.test_endpoint_sync(endpoint)
        
        metrics = tester.get_metrics()
        
        assert metrics['total_tests'] == num_requests
        assert metrics['success_rate'] >= 0.0
        assert metrics['total_response_time_ms'] > 0
    
    def test_performance_degradation_detection(self):
        """Test detecting performance degradation"""
        tester = ServiceIntegrationTester()
        
        endpoint = Endpoint(
            path="/api/slow",
            method=EndpointMethod.GET,
            base_url="https://api.example.com",
            timeout_ms=1000
        )
        
        # Run tests
        for _ in range(10):
            tester.test_endpoint_sync(endpoint)
        
        metrics = tester.get_metrics()
        
        # Check if any requests exceeded threshold
        slow_requests = [
            r for r in tester.test_results
            if r.response_time_ms and r.response_time_ms > endpoint.timeout_ms
        ]
        
        # All should be under timeout (in mock implementation)
        assert len(slow_requests) == 0


class TestCLIIntegration:
    """Test CLI integration"""
    
    def test_cli_test_command(self):
        """Test CLI test command"""
        # This would normally invoke the CLI, but we'll test the main function logic
        from agent import ServiceIntegrationTester
        
        tester = ServiceIntegrationTester()
        endpoints = tester.scan_endpoints("https://api.example.com", "common")
        
        assert len(endpoints) > 0
        
        for endpoint in endpoints:
            result = tester.test_endpoint_sync(endpoint)
            assert result.status in [TestStatus.SUCCESS, TestStatus.FAILURE, TestStatus.ERROR]
    
    def test_cli_scan_command(self):
        """Test CLI scan command"""
        tester = ServiceIntegrationTester()
        
        endpoints = tester.scan_endpoints("https://api.example.com", "common")
        
        assert len(endpoints) > 0
        assert all(isinstance(ep, Endpoint) for ep in endpoints)
    
    def test_cli_generate_report_command(self):
        """Test CLI generate-report command"""
        tester = ServiceIntegrationTester()
        
        # Run some tests first
        endpoint = Endpoint(
            path="/health",
            method=EndpointMethod.GET,
            base_url="https://api.example.com"
        )
        tester.test_endpoint_sync(endpoint)
        
        # Generate report
        report = tester.generate_report()
        
        assert len(report) > 0
        assert "SERVICE INTEGRATION TEST REPORT" in report


class TestFileOperations:
    """Test file I/O operations"""
    
    def test_report_generation_to_file(self):
        """Test generating report to file"""
        tester = ServiceIntegrationTester()
        
        # Run tests
        endpoint = Endpoint(
            path="/health",
            method=EndpointMethod.GET,
            base_url="https://api.example.com"
        )
        tester.test_endpoint_sync(endpoint)
        
        # Generate report to file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            report = tester.generate_report(output_path)
            
            assert output_path.exists()
            assert output_path.stat().st_size > 0
            
            content = output_path.read_text()
            assert "SERVICE INTEGRATION TEST REPORT" in content
            assert "SUMMARY" in content
            assert "Total Tests:" in content
        finally:
            output_path.unlink()
    
    def test_json_export(self):
        """Test exporting results as JSON"""
        tester = ServiceIntegrationTester()
        
        # Run tests
        endpoints = [
            Endpoint(path="/health", method=EndpointMethod.GET, base_url="https://api1.example.com"),
            Endpoint(path="/status", method=EndpointMethod.GET, base_url="https://api2.example.com"),
        ]
        
        for endpoint in endpoints:
            tester.test_endpoint_sync(endpoint)
        
        # Export to JSON
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
            assert len(data['results']) == 2
            
            # Verify structure
            first_result = data['results'][0]
            assert 'endpoint' in first_result
            assert 'status' in first_result
            assert 'status_code' in first_result
        finally:
            output_path.unlink()
    
    def test_config_loading(self):
        """Test loading configuration from file"""
        # Create config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config = {
                'agent_name': 'service-integration-tester',
                'cognitive_brain': {
                    'enabled': True,
                    'metrics': ['test_count', 'success_rate', 'avg_response_time']
                },
                'thresholds': {
                    'max_response_time_ms': 5000,
                    'min_success_rate': 0.95
                }
            }
            yaml.dump(config, f)
            config_path = Path(f.name)
        
        try:
            tester = ServiceIntegrationTester(config_path)
            
            assert tester.config is not None
            assert tester.config['agent_name'] == 'service-integration-tester'
            assert 'cognitive_brain' in tester.config
            assert tester.config['cognitive_brain']['enabled']
        finally:
            config_path.unlink()


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_config_path(self):
        """Test handling invalid config path"""
        with pytest.raises(FileNotFoundError):
            ServiceIntegrationTester(Path("/nonexistent/config.yaml"))
    
    def test_empty_test_suite(self):
        """Test running empty test suite"""
        tester = ServiceIntegrationTester()
        
        suite = IntegrationTestSuite(
            name="empty",
            description="Empty suite"
        )
        
        success, metrics = tester.run_integration_suite(suite)
        
        assert success
        assert metrics.total_tests >= 0
    
    def test_generate_report_no_tests(self):
        """Test generating report with no tests run"""
        tester = ServiceIntegrationTester()
        
        report = tester.generate_report()
        
        assert "Total Tests:    0" in report
        assert "Passed:         0" in report


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
