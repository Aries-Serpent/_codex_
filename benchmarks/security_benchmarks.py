"""
Performance benchmarks for security utilities.

These benchmarks measure the performance impact of security functions
to ensure they don't significantly degrade application performance.

Run with: python -m pytest benchmarks/security_benchmarks.py -v
Or: python benchmarks/security_benchmarks.py
"""

import time
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from codex.security import (
    mask_token, mask_email, mask_password, mask_sensitive,
    sanitize_log, sanitize_dict_for_log, hash_secure
)


def benchmark_function(func, *args, iterations=10000, **kwargs):
    """
    Benchmark a function over multiple iterations.
    
    Returns:
        tuple: (avg_time_ms, ops_per_second)
    """
    start = time.perf_counter()
    for _ in range(iterations):
        func(*args, **kwargs)
    end = time.perf_counter()
    
    total_time = end - start
    avg_time_ms = (total_time / iterations) * 1000
    ops_per_sec = iterations / total_time
    
    return avg_time_ms, ops_per_sec


def run_benchmarks():
    """Run all security function benchmarks."""
    
    print("=" * 70)
    print("SECURITY UTILITIES PERFORMANCE BENCHMARKS")
    print("=" * 70)
    print()
    
    # Test data
    test_token = "sk_live_abc123xyz789defg"
    test_email = "user@example.com"
    test_password = "MySecureP@ssw0rd123"
    test_log_safe = "This is a normal log message"
    test_log_malicious = "normal\nFAKE LOG: admin password reset\nmalicious"
    test_dict = {
        "username": "john_doe",
        "action": "login\nattempt",
        "timestamp": "2025-12-23T10:00:00Z"
    }
    test_hash_data = "secret_token_for_hashing"
    
    results = []
    
    # Benchmark 1: mask_token
    print("1. Benchmarking mask_token()...")
    avg_ms, ops_sec = benchmark_function(mask_token, test_token)
    results.append(("mask_token", avg_ms, ops_sec))
    print(f"   Average: {avg_ms:.4f} ms/call")
    print(f"   Throughput: {ops_sec:,.0f} ops/sec")
    print()
    
    # Benchmark 2: mask_email
    print("2. Benchmarking mask_email()...")
    avg_ms, ops_sec = benchmark_function(mask_email, test_email)
    results.append(("mask_email", avg_ms, ops_sec))
    print(f"   Average: {avg_ms:.4f} ms/call")
    print(f"   Throughput: {ops_sec:,.0f} ops/sec")
    print()
    
    # Benchmark 3: mask_password
    print("3. Benchmarking mask_password()...")
    avg_ms, ops_sec = benchmark_function(mask_password, test_password)
    results.append(("mask_password", avg_ms, ops_sec))
    print(f"   Average: {avg_ms:.4f} ms/call")
    print(f"   Throughput: {ops_sec:,.0f} ops/sec")
    print()
    
    # Benchmark 4: mask_sensitive
    print("4. Benchmarking mask_sensitive()...")
    avg_ms, ops_sec = benchmark_function(mask_sensitive, test_token, show_chars=4)
    results.append(("mask_sensitive", avg_ms, ops_sec))
    print(f"   Average: {avg_ms:.4f} ms/call")
    print(f"   Throughput: {ops_sec:,.0f} ops/sec")
    print()
    
    # Benchmark 5: sanitize_log (safe input)
    print("5. Benchmarking sanitize_log() [safe input]...")
    avg_ms, ops_sec = benchmark_function(sanitize_log, test_log_safe)
    results.append(("sanitize_log (safe)", avg_ms, ops_sec))
    print(f"   Average: {avg_ms:.4f} ms/call")
    print(f"   Throughput: {ops_sec:,.0f} ops/sec")
    print()
    
    # Benchmark 6: sanitize_log (malicious input)
    print("6. Benchmarking sanitize_log() [malicious input]...")
    avg_ms, ops_sec = benchmark_function(sanitize_log, test_log_malicious)
    results.append(("sanitize_log (malicious)", avg_ms, ops_sec))
    print(f"   Average: {avg_ms:.4f} ms/call")
    print(f"   Throughput: {ops_sec:,.0f} ops/sec")
    print()
    
    # Benchmark 7: sanitize_dict_for_log
    print("7. Benchmarking sanitize_dict_for_log()...")
    avg_ms, ops_sec = benchmark_function(sanitize_dict_for_log, test_dict)
    results.append(("sanitize_dict_for_log", avg_ms, ops_sec))
    print(f"   Average: {avg_ms:.4f} ms/call")
    print(f"   Throughput: {ops_sec:,.0f} ops/sec")
    print()
    
    # Benchmark 8: hash_secure (SHA-256)
    print("8. Benchmarking hash_secure() [SHA-256]...")
    avg_ms, ops_sec = benchmark_function(hash_secure, test_hash_data, algorithm='sha256')
    results.append(("hash_secure (SHA-256)", avg_ms, ops_sec))
    print(f"   Average: {avg_ms:.4f} ms/call")
    print(f"   Throughput: {ops_sec:,.0f} ops/sec")
    print()
    
    # Benchmark 9: hash_secure (SHA-512)
    print("9. Benchmarking hash_secure() [SHA-512]...")
    avg_ms, ops_sec = benchmark_function(hash_secure, test_hash_data, algorithm='sha512')
    results.append(("hash_secure (SHA-512)", avg_ms, ops_sec))
    print(f"   Average: {avg_ms:.4f} ms/call")
    print(f"   Throughput: {ops_sec:,.0f} ops/sec")
    print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"{'Function':<30} {'Avg Time (ms)':<15} {'Ops/sec':<15}")
    print("-" * 70)
    
    for func_name, avg_ms, ops_sec in results:
        print(f"{func_name:<30} {avg_ms:>14.4f} {ops_sec:>14,.0f}")
    
    print()
    print("=" * 70)
    print("PERFORMANCE ANALYSIS")
    print("=" * 70)
    print()
    
    # Find fastest and slowest
    fastest = min(results, key=lambda x: x[1])
    slowest = max(results, key=lambda x: x[1])
    
    print(f"✅ Fastest: {fastest[0]} ({fastest[1]:.4f} ms/call)")
    print(f"⏱️  Slowest: {slowest[0]} ({slowest[1]:.4f} ms/call)")
    print()
    
    # Performance assessment
    print("Performance Assessment:")
    for func_name, avg_ms, _ in results:
        if avg_ms < 0.001:
            status = "✅ EXCELLENT"
        elif avg_ms < 0.01:
            status = "✅ GOOD"
        elif avg_ms < 0.1:
            status = "⚠️  ACCEPTABLE"
        else:
            status = "❌ NEEDS OPTIMIZATION"
        print(f"  {func_name:<30} {status}")
    
    print()
    print("Recommendation:")
    print("  All functions with <0.01ms average are suitable for high-throughput")
    print("  applications. Functions >0.1ms should be used judiciously in hot paths.")
    print()
    
    return results


class TestSecurityBenchmarks:
    """PyTest benchmark tests."""
    
    def test_mask_token_performance(self, benchmark):
        """Benchmark mask_token using pytest-benchmark."""
        token = "sk_live_abc123xyz789"
        result = benchmark(mask_token, token)
        assert result is not None
    
    def test_sanitize_log_performance(self, benchmark):
        """Benchmark sanitize_log using pytest-benchmark."""
        data = "test\ninjection\tattempt"
        result = benchmark(sanitize_log, data)
        assert result is not None
    
    def test_hash_secure_performance(self, benchmark):
        """Benchmark hash_secure using pytest-benchmark."""
        data = "secret_token"
        result = benchmark(hash_secure, data)
        assert len(result) == 64


if __name__ == "__main__":
    run_benchmarks()
