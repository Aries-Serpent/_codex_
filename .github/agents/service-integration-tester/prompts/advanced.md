# Service Integration Tester - Advanced Patterns

Advanced usage patterns for experienced users.

## Table of Contents

1. [Pattern 1: Service Mesh Integration Testing](#pattern-1-service-mesh-integration-testing)
2. [Pattern 2: Contract-Driven Development](#pattern-2-contract-driven-development)
3. [Pattern 3: Chaos Testing Integration](#pattern-3-chaos-testing-integration)
4. [Pattern 4: Performance Regression Detection](#pattern-4-performance-regression-detection)
5. [Pattern 5: Multi-Region Latency Testing](#pattern-5-multi-region-latency-testing)
6. [Pattern 6: Advanced Mock Data Generation](#pattern-6-advanced-mock-data-generation)

---

## Pattern 1: Service Mesh Integration Testing

Test services in a service mesh (e.g., Istio, Linkerd) with retry policies and circuit breakers.

```python
from service_integration_tester import (
    ServiceIntegrationTester,
    ServiceContract,
    Endpoint,
    IntegrationTestSuite
)

# Configure for service mesh
tester = ServiceIntegrationTester()

# Define service contracts with mesh-specific configuration
auth_service = ServiceContract(
    service_name="auth-service",
    base_url="https://auth.internal.svc.cluster.local",
    endpoints=[
        Endpoint(path="/health", method="GET", base_url="https://auth.internal.svc.cluster.local"),
        Endpoint(path="/api/login", method="POST", base_url="https://auth.internal.svc.cluster.local"),
    ],
    version="v2"
)

user_service = ServiceContract(
    service_name="user-service",
    base_url="https://users.internal.svc.cluster.local",
    endpoints=[
        Endpoint(path="/health", method="GET", base_url="https://users.internal.svc.cluster.local"),
        Endpoint(path="/api/users", method="GET", base_url="https://users.internal.svc.cluster.local"),
    ],
    version="v2"
)

# Create integration suite with service mesh considerations
suite = IntegrationTestSuite(
    name="service-mesh-tests",
    description="Test services within service mesh with retry and circuit breaker policies",
    contracts=[auth_service, user_service],
    setup_commands=[
        "kubectl apply -f mesh-config.yaml",
        "kubectl wait --for=condition=ready pod -l app=auth-service --timeout=60s"
    ],
    teardown_commands=[
        "kubectl delete -f mesh-config.yaml"
    ]
)

# Run suite with verbose output
success, metrics = tester.run_integration_suite(suite, verbose=True)

# Analyze results for mesh-specific patterns
print("\n=== Service Mesh Analysis ===")
print(f"Overall Success: {success}")
print(f"Mesh Performance Impact: {metrics.avg_response_time_ms:.0f}ms avg")

# Check for circuit breaker triggers
for result in tester.test_results:
    if result.status_code == 503:
        print(f"⚠️  Circuit breaker may be open for {result.endpoint.path}")
```

### Expected Behavior

- **Retries**: Automatic retries handled by mesh
- **Circuit Breakers**: 503 responses when breaker is open
- **Timeouts**: Mesh-level timeouts may override endpoint timeouts
- **Load Balancing**: Requests distributed across pod instances

---

## Pattern 2: Contract-Driven Development

Implement contract-driven development workflow with continuous validation.

```python
from pathlib import Path
from service_integration_tester import ServiceIntegrationTester
import json

class ContractValidator:
    """Contract-driven development validator"""
    
    def __init__(self, spec_path: Path, base_url: str):
        self.spec_path = spec_path
        self.base_url = base_url
        self.tester = ServiceIntegrationTester()
        self.baseline_path = Path(".codex/contract_baselines.json")
    
    def validate_new_endpoints(self) -> bool:
        """Validate that all spec endpoints are implemented"""
        endpoints = self.tester.scan_endpoints(self.base_url, self.spec_path)
        
        all_implemented = True
        
        for endpoint in endpoints:
            result = self.tester.test_endpoint_sync(endpoint)
            
            if result.status_code == 404:
                print(f"❌ Endpoint not implemented: {endpoint.method} {endpoint.path}")
                all_implemented = False
            elif result.status != 'success':
                print(f"⚠️  Endpoint has issues: {endpoint.method} {endpoint.path}")
                all_implemented = False
            else:
                print(f"✅ Endpoint implemented: {endpoint.method} {endpoint.path}")
        
        return all_implemented
    
    def check_breaking_changes(self) -> list:
        """Detect breaking changes from baseline"""
        violations = []
        
        # Load baseline
        if not self.baseline_path.exists():
            print("No baseline found, creating initial baseline...")
            self.create_baseline()
            return violations
        
        with open(self.baseline_path, 'r') as f:
            baseline = json.load(f)
        
        # Validate current against baseline
        current_compliant, current_violations = self.tester.validate_contract_compliance(
            self.spec_path,
            self.base_url
        )
        
        # Check for new violations
        baseline_violations = set(baseline.get('violations', []))
        current_violations_set = set(current_violations)
        
        new_violations = current_violations_set - baseline_violations
        
        if new_violations:
            violations.extend(list(new_violations))
            print(f"❌ Found {len(new_violations)} new breaking changes:")
            for v in new_violations:
                print(f"   - {v}")
        else:
            print("✅ No new breaking changes detected")
        
        return violations
    
    def create_baseline(self):
        """Create contract baseline for future comparison"""
        compliant, violations = self.tester.validate_contract_compliance(
            self.spec_path,
            self.base_url
        )
        
        baseline = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'compliant': compliant,
            'violations': violations,
            'metrics': self.tester.get_metrics()
        }
        
        self.baseline_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.baseline_path, 'w') as f:
            json.dump(baseline, f, indent=2)
        
        print(f"Baseline created: {self.baseline_path}")

# Usage in CI/CD
validator = ContractValidator(
    spec_path=Path("openapi.yaml"),
    base_url="https://api.example.com"
)

# Pre-deployment checks
print("=== Contract Validation ===")
endpoints_ok = validator.validate_new_endpoints()
breaking_changes = validator.check_breaking_changes()

if not endpoints_ok or breaking_changes:
    print("\n❌ Contract validation failed!")
    exit(1)
else:
    print("\n✅ Contract validation passed!")
```

---

## Pattern 3: Chaos Testing Integration

Combine with chaos engineering to test resilience.

```python
from service_integration_tester import ServiceIntegrationTester, Endpoint
import subprocess
import time

class ChaosIntegrationTester:
    """Integration tester with chaos engineering capabilities"""
    
    def __init__(self):
        self.tester = ServiceIntegrationTester()
    
    def test_with_network_delay(self, endpoint: Endpoint, delay_ms: int):
        """Test endpoint with network delay injected"""
        # Inject network delay (using tc or similar)
        try:
            subprocess.run([
                "tc", "qdisc", "add", "dev", "eth0", "root", "netem", 
                "delay", f"{delay_ms}ms"
            ], capture_output=True)
            
            print(f"Injected {delay_ms}ms network delay")
            
            # Test endpoint
            result = self.tester.test_endpoint_sync(endpoint)
            
            # Verify graceful degradation
            if result.response_time_ms and result.response_time_ms > delay_ms:
                print(f"✅ Service handled delay: {result.response_time_ms:.0f}ms")
            else:
                print(f"⚠️  Unexpected response time: {result.response_time_ms:.0f}ms")
            
            return result
        finally:
            # Remove delay
            subprocess.run(["tc", "qdisc", "del", "dev", "eth0", "root"], 
                         capture_output=True)
    
    def test_with_packet_loss(self, endpoint: Endpoint, loss_percent: int):
        """Test endpoint with packet loss"""
        try:
            subprocess.run([
                "tc", "qdisc", "add", "dev", "eth0", "root", "netem",
                "loss", f"{loss_percent}%"
            ], capture_output=True)
            
            print(f"Injected {loss_percent}% packet loss")
            
            # Test with retries
            attempts = 0
            max_attempts = 5
            
            while attempts < max_attempts:
                result = self.tester.test_endpoint_sync(endpoint)
                
                if result.status == 'success':
                    print(f"✅ Service recovered after {attempts + 1} attempts")
                    return result
                
                attempts += 1
                time.sleep(1)
            
            print(f"❌ Service failed after {max_attempts} attempts")
            return result
        finally:
            subprocess.run(["tc", "qdisc", "del", "dev", "eth0", "root"],
                         capture_output=True)
    
    def test_dependency_failure(self, endpoint: Endpoint, dependency_url: str):
        """Test endpoint when dependency is unavailable"""
        print(f"Simulating failure of dependency: {dependency_url}")
        
        # Block dependency (using iptables or similar)
        try:
            subprocess.run([
                "iptables", "-A", "OUTPUT", "-d", dependency_url, 
                "-j", "DROP"
            ], capture_output=True)
            
            # Test primary service
            result = self.tester.test_endpoint_sync(endpoint)
            
            # Check for graceful degradation
            if result.status_code in [503, 504]:
                print("✅ Service returned appropriate error for dependency failure")
            elif result.status == 'success':
                print("✅ Service has fallback mechanism")
            else:
                print(f"⚠️  Unexpected response: {result.status_code}")
            
            return result
        finally:
            subprocess.run([
                "iptables", "-D", "OUTPUT", "-d", dependency_url,
                "-j", "DROP"
            ], capture_output=True)

# Usage
chaos_tester = ChaosIntegrationTester()
endpoint = Endpoint(
    path="/api/users",
    method="GET",
    base_url="https://api.example.com"
)

# Test resilience scenarios
print("=== Chaos Testing ===\n")

print("Scenario 1: Network Delay")
chaos_tester.test_with_network_delay(endpoint, delay_ms=500)

print("\nScenario 2: Packet Loss")
chaos_tester.test_with_packet_loss(endpoint, loss_percent=10)

print("\nScenario 3: Dependency Failure")
chaos_tester.test_dependency_failure(endpoint, "auth-service.internal")
```

---

## Pattern 4: Performance Regression Detection

Detect performance regressions using statistical analysis.

```python
from service_integration_tester import ServiceIntegrationTester, Endpoint
import statistics
import json
from pathlib import Path
from datetime import datetime, timezone

class PerformanceRegressionDetector:
    """Detect performance regressions using baseline comparison"""
    
    def __init__(self, baseline_path: Path):
        self.tester = ServiceIntegrationTester()
        self.baseline_path = baseline_path
        self.baseline = self.load_baseline()
    
    def load_baseline(self) -> dict:
        """Load performance baseline"""
        if not self.baseline_path.exists():
            return {}
        
        with open(self.baseline_path, 'r') as f:
            return json.load(f)
    
    def test_with_regression_detection(
        self,
        endpoint: Endpoint,
        iterations: int = 20,
        threshold: float = 0.20  # 20% regression threshold
    ) -> dict:
        """Test endpoint and detect regressions"""
        
        # Run tests
        response_times = []
        for _ in range(iterations):
            result = self.tester.test_endpoint_sync(endpoint)
            if result.response_time_ms:
                response_times.append(result.response_time_ms)
        
        # Calculate statistics
        current_stats = {
            'mean': statistics.mean(response_times),
            'median': statistics.median(response_times),
            'stdev': statistics.stdev(response_times) if len(response_times) > 1 else 0,
            'p95': sorted(response_times)[int(len(response_times) * 0.95)],
            'p99': sorted(response_times)[int(len(response_times) * 0.99)],
            'samples': len(response_times)
        }
        
        # Compare to baseline
        endpoint_key = f"{endpoint.method}:{endpoint.path}"
        
        if endpoint_key in self.baseline:
            baseline_stats = self.baseline[endpoint_key]
            
            # Calculate regression
            mean_regression = (
                (current_stats['mean'] - baseline_stats['mean']) / 
                baseline_stats['mean']
            )
            p95_regression = (
                (current_stats['p95'] - baseline_stats['p95']) / 
                baseline_stats['p95']
            )
            
            # Check thresholds
            has_regression = (
                mean_regression > threshold or 
                p95_regression > threshold
            )
            
            result = {
                'endpoint': endpoint_key,
                'current': current_stats,
                'baseline': baseline_stats,
                'regression': {
                    'mean': mean_regression * 100,
                    'p95': p95_regression * 100,
                    'detected': has_regression
                }
            }
            
            if has_regression:
                print(f"❌ Performance regression detected for {endpoint_key}")
                print(f"   Mean: {mean_regression*100:.1f}% slower")
                print(f"   P95: {p95_regression*100:.1f}% slower")
            else:
                print(f"✅ No regression for {endpoint_key}")
            
            return result
        else:
            print(f"No baseline for {endpoint_key}, creating baseline...")
            self.baseline[endpoint_key] = current_stats
            self.save_baseline()
            
            return {
                'endpoint': endpoint_key,
                'current': current_stats,
                'baseline': None,
                'regression': None
            }
    
    def save_baseline(self):
        """Save current baseline"""
        self.baseline['last_updated'] = datetime.now(timezone.utc).isoformat()
        
        self.baseline_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.baseline_path, 'w') as f:
            json.dump(self.baseline, f, indent=2)

# Usage
detector = PerformanceRegressionDetector(
    baseline_path=Path(".codex/performance_baselines.json")
)

# Test critical endpoints
endpoints = [
    Endpoint(path="/api/users", method="GET", base_url="https://api.example.com"),
    Endpoint(path="/api/products", method="GET", base_url="https://api.example.com"),
    Endpoint(path="/api/orders", method="GET", base_url="https://api.example.com"),
]

regressions_found = []

for endpoint in endpoints:
    result = detector.test_with_regression_detection(endpoint, iterations=30)
    
    if result['regression'] and result['regression']['detected']:
        regressions_found.append(result)

if regressions_found:
    print(f"\n❌ Found {len(regressions_found)} performance regressions")
    exit(1)
else:
    print("\n✅ No performance regressions detected")
```

---

## Pattern 5: Multi-Region Latency Testing

Test API latency from multiple geographic regions.

```python
from service_integration_tester import ServiceIntegrationTester, Endpoint
from concurrent.futures import ThreadPoolExecutor
import time

class MultiRegionLatencyTester:
    """Test API latency from multiple regions"""
    
    def __init__(self):
        self.regions = {
            'us-east-1': 'https://us-east-1.api.example.com',
            'us-west-2': 'https://us-west-2.api.example.com',
            'eu-west-1': 'https://eu-west-1.api.example.com',
            'ap-southeast-1': 'https://ap-southeast-1.api.example.com',
            'ap-northeast-1': 'https://ap-northeast-1.api.example.com'
        }
    
    def test_region(self, region_name: str, base_url: str, 
                    endpoint_path: str = "/api/ping") -> dict:
        """Test latency for a specific region"""
        tester = ServiceIntegrationTester()
        
        endpoint = Endpoint(
            path=endpoint_path,
            method="GET",
            base_url=base_url
        )
        
        # Test multiple times for accuracy
        response_times = []
        for _ in range(10):
            result = tester.test_endpoint_sync(endpoint)
            if result.response_time_ms:
                response_times.append(result.response_time_ms)
            time.sleep(0.1)
        
        if response_times:
            return {
                'region': region_name,
                'avg_latency': sum(response_times) / len(response_times),
                'min_latency': min(response_times),
                'max_latency': max(response_times),
                'samples': len(response_times)
            }
        else:
            return {
                'region': region_name,
                'error': 'No successful responses'
            }
    
    def test_all_regions(self, endpoint_path: str = "/api/ping") -> dict:
        """Test all regions in parallel"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=len(self.regions)) as executor:
            futures = {
                executor.submit(
                    self.test_region, 
                    region_name, 
                    base_url,
                    endpoint_path
                ): region_name
                for region_name, base_url in self.regions.items()
            }
            
            for future in futures:
                region_name = futures[future]
                try:
                    result = future.result()
                    results[region_name] = result
                except Exception as e:
                    results[region_name] = {'error': str(e)}
        
        return results
    
    def find_optimal_region(self, results: dict) -> str:
        """Find region with lowest latency"""
        valid_results = {
            k: v for k, v in results.items()
            if 'avg_latency' in v
        }
        
        if not valid_results:
            return None
        
        optimal = min(valid_results.items(), 
                     key=lambda x: x[1]['avg_latency'])
        
        return optimal[0]

# Usage
latency_tester = MultiRegionLatencyTester()

print("Testing API latency across regions...")
print("="*70)

results = latency_tester.test_all_regions("/health")

# Display results
for region, data in sorted(results.items()):
    if 'error' in data:
        print(f"❌ {region}: {data['error']}")
    else:
        print(f"✅ {region}:")
        print(f"   Avg: {data['avg_latency']:.1f}ms")
        print(f"   Min/Max: {data['min_latency']:.1f}ms / {data['max_latency']:.1f}ms")

# Find optimal region
optimal = latency_tester.find_optimal_region(results)
if optimal:
    print(f"\n🏆 Optimal region: {optimal}")
    print(f"   Latency: {results[optimal]['avg_latency']:.1f}ms")
```

---

## Pattern 6: Advanced Mock Data Generation

Generate complex, realistic mock data with relationships.

```python
from service_integration_tester import ServiceIntegrationTester
import random
import uuid
from datetime import datetime, timedelta, timezone

class AdvancedMockDataGenerator:
    """Generate complex mock data with relationships"""
    
    def __init__(self):
        self.tester = ServiceIntegrationTester()
    
    def generate_user_ecosystem(self, num_users: int = 10) -> dict:
        """Generate interconnected user data"""
        ecosystem = {
            'users': [],
            'profiles': [],
            'preferences': [],
            'activities': []
        }
        
        for i in range(num_users):
            user_id = str(uuid.uuid4())
            
            # User
            user = self.tester.generate_mock_data({
                'id': 'uuid',
                'email': 'email',
                'created_at': 'timestamp'
            })
            user['id'] = user_id
            ecosystem['users'].append(user)
            
            # Profile
            profile = {
                'user_id': user_id,
                'display_name': f"User {i+1}",
                'bio': f"Test user {i+1} biography",
                'avatar_url': f"https://avatars.example.com/{user_id}"
            }
            ecosystem['profiles'].append(profile)
            
            # Preferences
            preferences = {
                'user_id': user_id,
                'theme': random.choice(['light', 'dark', 'auto']),
                'language': random.choice(['en', 'es', 'fr', 'de']),
                'notifications_enabled': random.choice([True, False])
            }
            ecosystem['preferences'].append(preferences)
            
            # Activities (random 1-5 per user)
            for _ in range(random.randint(1, 5)):
                activity = {
                    'id': str(uuid.uuid4()),
                    'user_id': user_id,
                    'type': random.choice(['login', 'purchase', 'view', 'update']),
                    'timestamp': (
                        datetime.now(timezone.utc) - 
                        timedelta(days=random.randint(0, 30))
                    ).isoformat()
                }
                ecosystem['activities'].append(activity)
        
        return ecosystem
    
    def generate_ecommerce_data(self, num_orders: int = 20) -> dict:
        """Generate realistic e-commerce data"""
        data = {
            'products': [],
            'orders': [],
            'order_items': [],
            'payments': []
        }
        
        # Generate products
        categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports']
        for i in range(50):
            product = {
                'id': str(uuid.uuid4()),
                'name': f"Product {i+1}",
                'category': random.choice(categories),
                'price': round(random.uniform(9.99, 999.99), 2),
                'stock': random.randint(0, 100),
                'created_at': (
                    datetime.now(timezone.utc) - 
                    timedelta(days=random.randint(0, 365))
                ).isoformat()
            }
            data['products'].append(product)
        
        # Generate orders with items
        for _ in range(num_orders):
            order_id = str(uuid.uuid4())
            
            # Order
            order = {
                'id': order_id,
                'user_id': str(uuid.uuid4()),
                'status': random.choice(['pending', 'processing', 'shipped', 'delivered']),
                'created_at': (
                    datetime.now(timezone.utc) - 
                    timedelta(days=random.randint(0, 90))
                ).isoformat()
            }
            data['orders'].append(order)
            
            # Order items (1-5 per order)
            num_items = random.randint(1, 5)
            selected_products = random.sample(data['products'], num_items)
            
            total_amount = 0
            for product in selected_products:
                quantity = random.randint(1, 3)
                item_total = product['price'] * quantity
                total_amount += item_total
                
                order_item = {
                    'id': str(uuid.uuid4()),
                    'order_id': order_id,
                    'product_id': product['id'],
                    'quantity': quantity,
                    'unit_price': product['price'],
                    'total_price': item_total
                }
                data['order_items'].append(order_item)
            
            # Payment
            payment = {
                'id': str(uuid.uuid4()),
                'order_id': order_id,
                'amount': round(total_amount, 2),
                'method': random.choice(['credit_card', 'paypal', 'bank_transfer']),
                'status': 'completed',
                'timestamp': order['created_at']
            }
            data['payments'].append(payment)
        
        return data

# Usage
generator = AdvancedMockDataGenerator()

# Generate user ecosystem
print("Generating user ecosystem...")
user_data = generator.generate_user_ecosystem(num_users=5)
print(f"Generated:")
print(f"  - {len(user_data['users'])} users")
print(f"  - {len(user_data['profiles'])} profiles")
print(f"  - {len(user_data['activities'])} activities")

# Generate e-commerce data
print("\nGenerating e-commerce data...")
ecommerce_data = generator.generate_ecommerce_data(num_orders=10)
print(f"Generated:")
print(f"  - {len(ecommerce_data['products'])} products")
print(f"  - {len(ecommerce_data['orders'])} orders")
print(f"  - {len(ecommerce_data['order_items'])} order items")
print(f"  - {len(ecommerce_data['payments'])} payments")

# Use in integration tests
tester = ServiceIntegrationTester()

# Test creating orders with realistic data
for order in ecommerce_data['orders'][:3]:
    endpoint = Endpoint(
        path="/api/orders",
        method="POST",
        base_url="https://api.example.com"
    )
    
    # Scrub PII before sending
    order_payload = tester.scrub_pii(json.dumps(order))
    
    result = tester.test_endpoint_sync(
        endpoint,
        payload=json.loads(order_payload)
    )
    
    print(f"Order {order['id'][:8]}...: {result.status}")
```

---

## Best Practices for Advanced Patterns

1. **Service Mesh**: Always test with realistic traffic patterns
2. **Contract-Driven**: Maintain baselines in version control
3. **Chaos Testing**: Run in isolated environments only
4. **Regression Detection**: Use statistical significance tests
5. **Multi-Region**: Account for network variability
6. **Mock Data**: Maintain referential integrity in generated data

---

*For basic usage, see examples.md. For agent fundamentals, see main.md*
