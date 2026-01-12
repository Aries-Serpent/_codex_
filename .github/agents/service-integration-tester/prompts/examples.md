# Service Integration Tester - Usage Examples

This document provides real-world examples of using the Service Integration Tester agent.

## Table of Contents

1. [Example 1: Microservice Health Checks](#example-1-microservice-health-checks)
2. [Example 2: REST API Contract Testing](#example-2-rest-api-contract-testing)
3. [Example 3: Authenticated API Testing](#example-3-authenticated-api-testing)
4. [Example 4: End-to-End User Journey](#example-4-end-to-end-user-journey)
5. [Example 5: Multi-Environment Testing](#example-5-multi-environment-testing)
6. [Example 6: Performance Testing](#example-6-performance-testing)

---

## Example 1: Microservice Health Checks

Test health endpoints across multiple microservices.

```python
from service_integration_tester import ServiceIntegrationTester

# Initialize tester
tester = ServiceIntegrationTester()

# Define microservices
microservices = {
    'auth': 'https://auth-service.example.com',
    'users': 'https://user-service.example.com',
    'payments': 'https://payment-service.example.com',
    'notifications': 'https://notification-service.example.com',
    'analytics': 'https://analytics-service.example.com'
}

# Test each service
results = {}
for service_name, service_url in microservices.items():
    print(f"Testing {service_name} service...")
    
    # Discover health endpoints
    endpoints = tester.scan_endpoints(service_url, "common")
    
    # Test first endpoint (usually /health)
    if endpoints:
        result = tester.test_endpoint_sync(endpoints[0])
        results[service_name] = {
            'status': result.status,
            'response_time': result.response_time_ms,
            'status_code': result.status_code
        }
        
        if result.status == 'success':
            print(f"  ✅ {service_name}: Healthy ({result.response_time_ms:.0f}ms)")
        else:
            print(f"  ❌ {service_name}: Unhealthy")
            if result.error:
                print(f"     Error: {result.error}")

# Summary report
print("\n" + "="*60)
print("Health Check Summary")
print("="*60)
healthy = sum(1 for r in results.values() if r['status'] == 'success')
total = len(results)
print(f"Services Healthy: {healthy}/{total} ({healthy/total*100:.0f}%)")
print(f"Average Response Time: {sum(r['response_time'] for r in results.values())/total:.0f}ms")
```

**Output**:
```
Testing auth service...
  ✅ auth: Healthy (45ms)
Testing users service...
  ✅ users: Healthy (52ms)
Testing payments service...
  ✅ payments: Healthy (38ms)
Testing notifications service...
  ✅ notifications: Healthy (41ms)
Testing analytics service...
  ✅ analytics: Healthy (67ms)

============================================================
Health Check Summary
============================================================
Services Healthy: 5/5 (100%)
Average Response Time: 49ms
```

---

## Example 2: REST API Contract Testing

Validate that your API implementation matches its OpenAPI specification.

```python
from pathlib import Path
from service_integration_tester import ServiceIntegrationTester, Endpoint

# Load configuration
config_path = Path("config/agent_config.yaml")
tester = ServiceIntegrationTester(config_path)

# Discover endpoints from OpenAPI spec
base_url = "https://api.example.com"
spec_path = Path("openapi.yaml")
endpoints = tester.scan_endpoints(base_url, spec_path)

print(f"Discovered {len(endpoints)} endpoints from spec")

# Test each endpoint
contract_violations = []

for endpoint in endpoints:
    print(f"\nTesting {endpoint.method} {endpoint.path}")
    
    # Prepare test data for POST/PUT/PATCH
    payload = None
    expected_status = 200
    
    if endpoint.method in ['POST', 'PUT', 'PATCH']:
        # Generate mock data based on endpoint
        if 'user' in endpoint.path:
            schema = {'name': 'name', 'email': 'email', 'age': 'int'}
        elif 'product' in endpoint.path:
            schema = {'name': 'string', 'price': 'float', 'available': 'bool'}
        else:
            schema = None
        
        payload = tester.generate_mock_data(schema)
        expected_status = 201 if endpoint.method == 'POST' else 200
    
    # Test endpoint
    result = tester.test_endpoint_sync(
        endpoint,
        payload=payload,
        expected_status=expected_status
    )
    
    # Check for contract violations
    if result.validation_errors:
        contract_violations.append({
            'endpoint': f"{endpoint.method} {endpoint.path}",
            'errors': result.validation_errors
        })
        print(f"  ❌ Contract violation detected")
    else:
        print(f"  ✅ Contract validated ({result.response_time_ms:.0f}ms)")

# Final report
print("\n" + "="*70)
print("Contract Validation Report")
print("="*70)
if not contract_violations:
    print("✅ All endpoints comply with OpenAPI contract")
else:
    print(f"❌ Found {len(contract_violations)} contract violations:")
    for violation in contract_violations:
        print(f"\n{violation['endpoint']}:")
        for error in violation['errors']:
            print(f"  - {error}")
```

---

## Example 3: Authenticated API Testing

Test endpoints that require authentication.

```python
from service_integration_tester import ServiceIntegrationTester, Endpoint
import os

tester = ServiceIntegrationTester()
base_url = "https://api.example.com"

# Get API credentials from environment
api_key = os.environ.get('API_KEY', 'test-api-key')
bearer_token = os.environ.get('BEARER_TOKEN', '')

# Test with API Key authentication
print("Testing API Key Authentication...")
api_key_endpoint = Endpoint(
    path="/api/protected/data",
    method="GET",
    base_url=base_url
)

result = tester.test_endpoint_sync(
    api_key_endpoint,
    headers={'X-API-Key': api_key}
)

if result.status_code == 401:
    print("  ❌ API Key authentication failed")
elif result.status_code == 200:
    print(f"  ✅ API Key auth successful ({result.response_time_ms:.0f}ms)")

# Test with Bearer authentication
print("\nTesting Bearer Authentication...")
bearer_endpoint = Endpoint(
    path="/api/user/profile",
    method="GET",
    base_url=base_url
)

result = tester.test_endpoint_sync(
    bearer_endpoint,
    headers={'Authorization': f'Bearer {bearer_token}'}
)

if result.status_code == 401:
    print("  ❌ Bearer authentication failed")
elif result.status_code == 200:
    print(f"  ✅ Bearer auth successful ({result.response_time_ms:.0f}ms)")

# Test without authentication (should fail)
print("\nTesting endpoint without authentication (should fail)...")
result = tester.test_endpoint_sync(bearer_endpoint)

if result.status_code == 401:
    print("  ✅ Correctly rejected unauthenticated request")
else:
    print(f"  ⚠️  Unexpected status: {result.status_code}")
```

---

## Example 4: End-to-End User Journey

Test a complete user journey across multiple endpoints.

```python
from service_integration_tester import ServiceIntegrationTester, Endpoint

tester = ServiceIntegrationTester()
base_url = "https://api.example.com"

print("Testing E2E User Journey: Purchase Flow")
print("="*70)

# Step 1: User Registration
print("\n1. User Registration")
register_endpoint = Endpoint(
    path="/api/auth/register",
    method="POST",
    base_url=base_url,
    expected_status=201
)
register_payload = tester.generate_mock_data({
    'username': 'string',
    'email': 'email',
    'password': 'string'
})
register_result = tester.test_endpoint_sync(register_endpoint, payload=register_payload)

if register_result.status != 'success':
    print(f"   ❌ Registration failed")
    exit(1)

print(f"   ✅ User registered")

# Step 2: Login
print("\n2. User Login")
login_endpoint = Endpoint(
    path="/api/auth/login",
    method="POST",
    base_url=base_url
)
login_payload = {
    'username': register_payload['username'],
    'password': register_payload['password']
}
login_result = tester.test_endpoint_sync(login_endpoint, payload=login_payload)

if login_result.status != 'success':
    print(f"   ❌ Login failed")
    exit(1)

auth_token = "mock-jwt-token"  # In real scenario, extract from response
print(f"   ✅ Login successful, token obtained")

# Step 3: Browse Products
print("\n3. Browse Products")
products_endpoint = Endpoint(
    path="/api/products",
    method="GET",
    base_url=base_url
)
products_result = tester.test_endpoint_sync(
    products_endpoint,
    headers={'Authorization': f'Bearer {auth_token}'}
)

if products_result.status != 'success':
    print(f"   ❌ Product browse failed")
    exit(1)

print(f"   ✅ Products retrieved")

# Step 4: Add to Cart
print("\n4. Add to Cart")
cart_endpoint = Endpoint(
    path="/api/cart/items",
    method="POST",
    base_url=base_url,
    expected_status=201
)
cart_payload = {'product_id': '123', 'quantity': 2}
cart_result = tester.test_endpoint_sync(
    cart_endpoint,
    headers={'Authorization': f'Bearer {auth_token}'},
    payload=cart_payload
)

if cart_result.status != 'success':
    print(f"   ❌ Add to cart failed")
    exit(1)

print(f"   ✅ Item added to cart")

# Step 5: Checkout
print("\n5. Create Order")
order_endpoint = Endpoint(
    path="/api/orders",
    method="POST",
    base_url=base_url,
    expected_status=201
)
order_payload = tester.generate_mock_data({
    'shipping_address': 'string',
    'payment_method': 'string'
})
order_result = tester.test_endpoint_sync(
    order_endpoint,
    headers={'Authorization': f'Bearer {auth_token}'},
    payload=order_payload
)

if order_result.status != 'success':
    print(f"   ❌ Order creation failed")
    exit(1)

order_id = "ORDER123"  # Extract from response
print(f"   ✅ Order created: {order_id}")

# Journey complete
print("\n" + "="*70)
print("✅ E2E User Journey: PASSED")
print("="*70)

# Generate journey report
metrics = tester.get_metrics()
print(f"\nTotal Steps: {metrics['total_tests']}")
print(f"Success Rate: {metrics['passed'] / metrics['total_tests'] * 100:.0f}%")
print(f"Total Journey Time: {metrics['total_response_time_ms']:.0f}ms")
```

---

## Example 5: Multi-Environment Testing

Test the same endpoints across multiple environments.

```python
from service_integration_tester import ServiceIntegrationTester

# Define environments
environments = {
    'dev': 'https://dev-api.example.com',
    'staging': 'https://staging-api.example.com',
    'production': 'https://api.example.com'
}

# Endpoints to test
test_endpoints = [
    {'path': '/health', 'method': 'GET'},
    {'path': '/api/status', 'method': 'GET'},
    {'path': '/api/version', 'method': 'GET'}
]

# Test each environment
results = {}

for env_name, base_url in environments.items():
    print(f"\nTesting {env_name.upper()} environment...")
    print("-" * 60)
    
    tester = ServiceIntegrationTester()
    endpoints = tester.scan_endpoints(base_url, test_endpoints)
    
    for endpoint in endpoints:
        result = tester.test_endpoint_sync(endpoint)
        
        key = f"{env_name}:{endpoint.path}"
        results[key] = {
            'status': result.status,
            'status_code': result.status_code,
            'response_time': result.response_time_ms
        }
        
        status_icon = "✅" if result.status == 'success' else "❌"
        print(f"  {status_icon} {endpoint.path}: {result.status_code} ({result.response_time_ms:.0f}ms)")

# Environment comparison
print("\n" + "="*60)
print("Environment Comparison")
print("="*60)

for env_name in environments.keys():
    env_results = {k: v for k, v in results.items() if k.startswith(f"{env_name}:")}
    success_count = sum(1 for r in env_results.values() if r['status'] == 'success')
    avg_time = sum(r['response_time'] for r in env_results.values()) / len(env_results)
    
    print(f"\n{env_name.upper()}:")
    print(f"  Success Rate: {success_count}/{len(env_results)}")
    print(f"  Avg Response Time: {avg_time:.0f}ms")
```

---

## Example 6: Performance Testing

Measure and track endpoint performance over multiple iterations.

```python
from service_integration_tester import ServiceIntegrationTester, Endpoint
import statistics

tester = ServiceIntegrationTester()
base_url = "https://api.example.com"

# Define endpoints to test
endpoints_to_test = [
    Endpoint(path="/api/users", method="GET", base_url=base_url),
    Endpoint(path="/api/products", method="GET", base_url=base_url),
    Endpoint(path="/api/orders", method="GET", base_url=base_url),
]

# Number of iterations
iterations = 20

print(f"Running performance tests ({iterations} iterations per endpoint)...")
print("="*70)

performance_data = {}

for endpoint in endpoints_to_test:
    print(f"\nTesting {endpoint.path}...")
    
    response_times = []
    success_count = 0
    
    # Run iterations
    for i in range(iterations):
        result = tester.test_endpoint_sync(endpoint)
        
        if result.status == 'success':
            success_count += 1
            response_times.append(result.response_time_ms)
    
    # Calculate statistics
    if response_times:
        performance_data[endpoint.path] = {
            'success_rate': (success_count / iterations) * 100,
            'avg': statistics.mean(response_times),
            'median': statistics.median(response_times),
            'min': min(response_times),
            'max': max(response_times),
            'p95': sorted(response_times)[int(len(response_times) * 0.95)],
            'p99': sorted(response_times)[int(len(response_times) * 0.99)]
        }
        
        print(f"  Success Rate: {performance_data[endpoint.path]['success_rate']:.0f}%")
        print(f"  Avg: {performance_data[endpoint.path]['avg']:.1f}ms")
        print(f"  Median: {performance_data[endpoint.path]['median']:.1f}ms")
        print(f"  Min/Max: {performance_data[endpoint.path]['min']:.1f}ms / {performance_data[endpoint.path]['max']:.1f}ms")
        print(f"  P95/P99: {performance_data[endpoint.path]['p95']:.1f}ms / {performance_data[endpoint.path]['p99']:.1f}ms")

# Performance summary
print("\n" + "="*70)
print("Performance Summary")
print("="*70)

for path, stats in performance_data.items():
    status = "✅" if stats['p95'] < 1000 else "⚠️"
    print(f"{status} {path}: {stats['avg']:.0f}ms avg, {stats['p95']:.0f}ms p95")
```

---

## CI/CD Integration Example

GitHub Actions workflow:

```yaml
name: Service Integration Tests

on:
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Test Staging API
        uses: ./.github/agents/service-integration-tester
        with:
          base-url: 'https://staging-api.example.com'
          endpoints: 'openapi.yaml'
          fail-on-error: 'true'
          output-file: 'staging_report.txt'
          export-json: 'true'
      
      - name: Performance Check
        uses: ./.github/agents/service-integration-tester
        with:
          base-url: 'https://staging-api.example.com'
          test-common: 'true'
          measure-performance: 'true'
          performance-iterations: '20'
      
      - name: Upload Results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: integration-test-results
          path: |
            staging_report.txt
            integration_results.json
```

---

These examples cover the most common use cases for the Service Integration Tester agent. For more advanced patterns, see `advanced.md`.
