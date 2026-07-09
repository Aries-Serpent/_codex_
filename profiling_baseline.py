#!/usr/bin/env python3
"""
Performance profiling script for Phase 3 Lane 3
Establishes baselines for key code paths
"""

import time
import psutil
import os
import sys
import json
import cProfile
import pstats
import io
from typing import Dict, List, Tuple, Any
from pathlib import Path

# Process tracking
def get_memory_usage() -> Dict[str, float]:
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return {
        'rss_mb': mem_info.rss / 1024 / 1024,  # Resident set size
        'vms_mb': mem_info.vms / 1024 / 1024,  # Virtual memory size
    }

def get_cpu_times() -> Tuple[float, float]:
    """Get user and system CPU times"""
    process = psutil.Process(os.getpid())
    cpu_times = process.cpu_times()
    return cpu_times.user, cpu_times.system

class PerformanceBaseline:
    """Track performance metrics"""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {
            'operations': [],
            'bottlenecks': [],
            'summary': {}
        }
        self.start_memory = get_memory_usage()
        self.start_cpu = get_cpu_times()
    
    def profile_operation(self, name: str, func, *args, **kwargs) -> Any:
        """Profile a function and record metrics"""
        print(f"\n📊 Profiling: {name}")
        
        mem_before = get_memory_usage()
        cpu_before = get_cpu_times()
        time_start = time.perf_counter()
        
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            print(f"⚠️  Error: {e}")
            result = None
        
        time_end = time.perf_counter()
        mem_after = get_memory_usage()
        cpu_after = get_cpu_times()
        
        elapsed = time_end - time_start
        mem_delta = mem_after['rss_mb'] - mem_before['rss_mb']
        cpu_user = cpu_after[0] - cpu_before[0]
        cpu_sys = cpu_after[1] - cpu_before[1]
        
        metric = {
            'name': name,
            'elapsed_ms': elapsed * 1000,
            'memory_delta_mb': mem_delta,
            'cpu_user_s': cpu_user,
            'cpu_sys_s': cpu_sys,
            'status': 'success' if result is not None else 'failed'
        }
        
        self.metrics['operations'].append(metric)
        print(f"  ⏱️  Time: {elapsed*1000:.2f}ms")
        print(f"  💾 Memory: {mem_delta:+.2f}MB")
        print(f"  🔧 CPU: {cpu_user:.3f}s user, {cpu_sys:.3f}s sys")
        
        return result
    
    def identify_bottlenecks(self, top_n: int = 5):
        """Identify top N slowest operations"""
        sorted_ops = sorted(self.metrics['operations'], 
                          key=lambda x: x['elapsed_ms'], 
                          reverse=True)
        
        self.metrics['bottlenecks'] = sorted_ops[:top_n]
        print(f"\n🔍 Top {top_n} bottlenecks:")
        for i, op in enumerate(self.metrics['bottlenecks'], 1):
            print(f"  {i}. {op['name']}: {op['elapsed_ms']:.2f}ms")
    
    def generate_summary(self):
        """Generate performance summary"""
        if not self.metrics['operations']:
            return
        
        total_time = sum(op['elapsed_ms'] for op in self.metrics['operations'])
        avg_time = total_time / len(self.metrics['operations'])
        max_time = max(op['elapsed_ms'] for op in self.metrics['operations'])
        
        self.metrics['summary'] = {
            'total_operations': len(self.metrics['operations']),
            'total_time_ms': total_time,
            'avg_time_ms': avg_time,
            'max_time_ms': max_time,
            'successful': sum(1 for op in self.metrics['operations'] if op['status'] == 'success'),
            'failed': sum(1 for op in self.metrics['operations'] if op['status'] == 'failed'),
        }
    
    def export_metrics(self, output_file: str):
        """Export metrics to JSON"""
        with open(output_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        print(f"\n✅ Metrics exported to {output_file}")

# Test imports and basic operations
def test_import_performance():
    """Profile imports"""
    print("\n=== TESTING IMPORTS ===")
    baseline = PerformanceBaseline()
    
    # Test CLI module import
    baseline.profile_operation(
        "Import src.cli",
        __import__, 'src.cli'
    )
    
    # Test codex_utils import
    baseline.profile_operation(
        "Import src.codex_utils",
        __import__, 'src.codex_utils'
    )
    
    return baseline

def test_cache_operations():
    """Profile cache operations"""
    print("\n=== TESTING CACHE OPERATIONS ===")
    baseline = PerformanceBaseline()
    
    try:
        from src.cache import LRUCache
        
        # Create cache
        cache = baseline.profile_operation(
            "Create LRU cache (capacity=1000)",
            LRUCache, capacity=1000
        )
        
        if cache:
            # Insertion
            def insert_items():
                for i in range(100):
                    cache.put(f"key_{i}", f"value_{i}")
            
            baseline.profile_operation("Insert 100 items", insert_items)
            
            # Retrieval
            def retrieve_items():
                for i in range(100):
                    cache.get(f"key_{i}")
            
            baseline.profile_operation("Retrieve 100 items", retrieve_items)
    except ImportError as e:
        print(f"⚠️  Cache module not available: {e}")
    
    return baseline

def test_file_operations():
    """Profile file I/O operations"""
    print("\n=== TESTING FILE OPERATIONS ===")
    baseline = PerformanceBaseline()
    
    # Create test data
    test_file = "/tmp/test_perf_data.txt"
    test_data = "x" * (1024 * 100)  # 100KB
    
    # Write test
    def write_file():
        with open(test_file, 'w') as f:
            f.write(test_data)
    
    baseline.profile_operation("Write 100KB file", write_file)
    
    # Read test
    def read_file():
        with open(test_file, 'r') as f:
            return f.read()
    
    baseline.profile_operation("Read 100KB file", read_file)
    
    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)
    
    return baseline

def test_string_operations():
    """Profile string operations"""
    print("\n=== TESTING STRING OPERATIONS ===")
    baseline = PerformanceBaseline()
    
    # String concatenation (slow method)
    def concat_slow():
        result = ""
        for i in range(10000):
            result += f"item_{i};"
        return result
    
    baseline.profile_operation("Concat strings (slow) - 10k items", concat_slow)
    
    # String join (fast method)
    def concat_fast():
        items = [f"item_{i};" for i in range(10000)]
        return "".join(items)
    
    baseline.profile_operation("Concat strings (fast) - 10k items", concat_fast)
    
    return baseline

def test_list_operations():
    """Profile list operations"""
    print("\n=== TESTING LIST OPERATIONS ===")
    baseline = PerformanceBaseline()
    
    # List append
    def list_append():
        items = []
        for i in range(10000):
            items.append(i)
        return items
    
    baseline.profile_operation("List append - 10k items", list_append)
    
    # List comprehension
    def list_comp():
        return [i for i in range(10000)]
    
    baseline.profile_operation("List comprehension - 10k items", list_comp)
    
    return baseline

def main():
    """Main profiling execution"""
    print("🚀 Phase 3 Lane 3: Performance Baseline Establishment")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_metrics = {
        'operations': [],
        'bottlenecks': [],
        'summary': {}
    }
    
    # Run profiling tests
    import_baseline = test_import_performance()
    cache_baseline = test_cache_operations()
    file_baseline = test_file_operations()
    string_baseline = test_string_operations()
    list_baseline = test_list_operations()
    
    # Collect all results
    baselines = [
        import_baseline,
        cache_baseline,
        file_baseline,
        string_baseline,
        list_baseline,
    ]
    
    print("\n=== GENERATING BASELINE REPORT ===")
    
    for baseline in baselines:
        baseline.identify_bottlenecks(top_n=3)
        baseline.generate_summary()
        baseline.export_metrics(f".codex/baseline_{baseline.metrics['summary'].get('total_operations', 'unknown')}_ops.json")
        all_metrics['operations'].extend(baseline.metrics['operations'])
    
    # Global bottleneck analysis
    all_metrics['operations'].sort(key=lambda x: x['elapsed_ms'], reverse=True)
    all_metrics['bottlenecks'] = all_metrics['operations'][:5]
    
    # Export consolidated metrics
    baseline_file = ".codex/PHASE_3_LANE_3_BASELINES.json"
    with open(baseline_file, 'w') as f:
        json.dump(all_metrics, f, indent=2)
    
    print(f"\n✅ Consolidated baseline exported to {baseline_file}")
    print(f"📊 Total operations profiled: {len(all_metrics['operations'])}")
    print(f"🔍 Top 5 bottlenecks identified")

if __name__ == "__main__":
    main()
