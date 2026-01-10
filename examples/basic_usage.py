"""
Basic Usage Example - Rust-Python Hybrid Swarm

This example demonstrates basic usage of the swarm engine.
"""

# Note: Once the library is built with maturin, uncomment and use:
# from codex_swarm import SwarmEngine, TaskManager, Compression

def basic_swarm_example():
    """Basic swarm usage example."""
    print("=" * 60)
    print("Example 1: Basic Swarm Operations")
    print("=" * 60)
    
    # Example code (will work after maturin build)
    example_code = """
    # Create a swarm with 100 agents
    swarm = SwarmEngine(100)
    print(f"Created swarm with {swarm.agent_count()} agents")
    
    # Process a batch of tasks
    num_tasks = 1000
    processed = swarm.process_batch(num_tasks)
    print(f"Processed {processed}/{num_tasks} tasks")
    """
    
    print(example_code)
    print()


def task_manager_example():
    """Task manager usage example."""
    print("=" * 60)
    print("Example 2: Task Manager")
    print("=" * 60)
    
    example_code = """
    # Create task manager
    manager = TaskManager()
    
    # Submit tasks
    task_ids = []
    for i in range(10):
        task_id = manager.submit_task(f"task_{i}")
        task_ids.append(task_id)
        print(f"Submitted task {task_id}")
    
    # Retrieve results
    for _ in range(10):
        result = manager.get_result(timeout=1.0)
        if result:
            task_id, success, data = result
            print(f"Task {task_id}: {'✅' if success else '❌'}")
    """
    
    print(example_code)
    print()


def compression_example():
    """Compression usage example."""
    print("=" * 60)
    print("Example 3: Data Compression")
    print("=" * 60)
    
    example_code = """
    # Compress data
    data = b"Hello, World!" * 1000
    compressed = Compression.compress(data)
    
    ratio = Compression.ratio(data, compressed)
    print(f"Original size: {len(data)} bytes")
    print(f"Compressed size: {len(compressed)} bytes")
    print(f"Compression ratio: {ratio:.2f}x")
    
    # Decompress
    decompressed = Compression.decompress(compressed)
    assert decompressed == data
    print("✅ Data integrity verified")
    """
    
    print(example_code)
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Rust-Python Hybrid Swarm - Basic Usage Examples")
    print("=" * 60)
    print()
    print("Note: These examples will work after building the library:")
    print("  pip install maturin")
    print("  maturin develop --release")
    print()
    
    basic_swarm_example()
    task_manager_example()
    compression_example()
    
    print("=" * 60)
    print("See docs/tutorials/ for more advanced examples")
    print("=" * 60)


if __name__ == "__main__":
    main()
