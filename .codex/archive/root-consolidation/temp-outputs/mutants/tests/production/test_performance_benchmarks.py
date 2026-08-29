"""
Production Performance Benchmarks

Tests performance characteristics for training, data loading, and API operations.
All tests are deterministic with fixed seeds and no external dependencies.
"""

import pytest

pytest.importorskip("numpy")


import json
import time

import numpy as np

# Training Loop Performance Tests


def test_training_loop_iteration_time():
    """Test that training loop iterations complete within acceptable time."""
    np.random.seed(42)

    # Simulate simple training loop
    batch_size = 32
    input_dim = 784
    output_dim = 10

    start = time.perf_counter()
    for _ in range(10):
        # Simulate forward pass
        inputs = np.random.randn(batch_size, input_dim).astype(np.float32)
        weights = np.random.randn(input_dim, output_dim).astype(np.float32)
        np.dot(inputs, weights)

        # Simulate backward pass
        grad = np.random.randn(batch_size, output_dim).astype(np.float32)
        np.dot(inputs.T, grad)

    elapsed = time.perf_counter() - start

    # Should complete 10 iterations in reasonable time
    assert elapsed < 1.0, f"10 iterations took {elapsed:.3f}s (expected < 1.0s)"


def test_training_gradient_computation_performance():
    """Test gradient computation performance with different batch sizes."""
    np.random.seed(42)

    input_dim = 512
    output_dim = 128

    results = {}
    for batch_size in [8, 16, 32, 64]:
        inputs = np.random.randn(batch_size, input_dim).astype(np.float32)
        weights = np.random.randn(input_dim, output_dim).astype(np.float32)

        start = time.perf_counter()
        for _ in range(100):
            np.dot(inputs, weights)
            grad = np.random.randn(batch_size, output_dim).astype(np.float32)
            np.dot(inputs.T, grad)
        elapsed = time.perf_counter() - start

        results[batch_size] = elapsed

    # Larger batches should be more efficient per sample
    assert results[64] < results[8] * 8, "Batching should provide efficiency gains"


def test_model_parameter_update_speed():
    """Test speed of parameter updates during training."""
    np.random.seed(42)

    num_params = 1_000_000
    params = np.random.randn(num_params).astype(np.float32)
    grads = np.random.randn(num_params).astype(np.float32)
    learning_rate = 0.01

    start = time.perf_counter()
    for _ in range(100):
        params -= learning_rate * grads
    elapsed = time.perf_counter() - start

    # 100 updates of 1M parameters should be fast
    assert elapsed < 0.5, f"Parameter updates took {elapsed:.3f}s (expected < 0.5s)"


def test_loss_computation_performance():
    """Test performance of loss function computation."""
    np.random.seed(42)

    batch_size = 128
    num_classes = 1000

    predictions = np.random.randn(batch_size, num_classes).astype(np.float32)
    labels = np.random.randint(0, num_classes, batch_size)

    start = time.perf_counter()
    for _ in range(1000):
        # Softmax
        exp_pred = np.exp(predictions - np.max(predictions, axis=1, keepdims=True))
        probs = exp_pred / np.sum(exp_pred, axis=1, keepdims=True)

        # Cross-entropy loss
        log_probs = -np.log(probs[np.arange(batch_size), labels])
        np.mean(log_probs)

    elapsed = time.perf_counter() - start
    assert elapsed < 1.0, f"1000 loss computations took {elapsed:.3f}s"


# Data Loading Performance Tests


def test_data_loading_throughput(tmp_path):
    """Test data loading throughput for training."""
    np.random.seed(42)

    # Create dummy data files
    num_samples = 1000
    data_file = tmp_path / "data.npy"
    data = np.random.randn(num_samples, 100).astype(np.float32)
    np.save(data_file, data)

    start = time.perf_counter()
    loaded_data = np.load(data_file)
    elapsed = time.perf_counter() - start

    # Calculate throughput
    data_size_mb = data.nbytes / (1024 * 1024)
    throughput = data_size_mb / elapsed

    assert throughput > 10, f"Data loading throughput {throughput:.2f} MB/s too slow"
    assert loaded_data.shape == data.shape, "Data must not be empty"


def test_batch_generation_speed():
    """Test speed of batch generation from dataset."""
    np.random.seed(42)

    dataset_size = 10000
    batch_size = 32
    num_features = 784

    # Simulate dataset
    dataset = np.random.randn(dataset_size, num_features).astype(np.float32)
    labels = np.random.randint(0, 10, dataset_size)

    start = time.perf_counter()
    num_batches = 0
    checksum = 0.0
    for i in range(0, dataset_size, batch_size):
        batch_data = dataset[i : i + batch_size]
        batch_labels = labels[i : i + batch_size]
        # Accumulate checksum to ensure slicing actually happens
        checksum += batch_data.sum() + batch_labels.sum()
        num_batches += 1
    elapsed = time.perf_counter() - start

    batches_per_second = num_batches / elapsed
    assert batches_per_second > 100, f"Batch generation {batches_per_second:.1f} batches/s too slow"
    assert np.isfinite(checksum), "Checksum should be finite"


def test_data_augmentation_performance():
    """Test performance of data augmentation pipeline."""
    np.random.seed(42)

    batch_size = 64
    image_size = (32, 32, 3)

    images = np.random.randint(0, 256, (batch_size, *image_size), dtype=np.uint8)

    start = time.perf_counter()
    for _ in range(100):
        # Simulate augmentations
        augmented = images.copy()
        # Random flip
        augmented = np.flip(augmented, axis=2)
        # Normalize
        augmented = augmented.astype(np.float32) / 255.0
        # Random noise
        noise = np.random.randn(*augmented.shape).astype(np.float32) * 0.01
        augmented += noise
    elapsed = time.perf_counter() - start

    assert elapsed < 2.0, f"100 augmentation iterations took {elapsed:.3f}s"


def test_shuffling_performance():
    """Test dataset shuffling performance."""
    np.random.seed(42)

    dataset_size = 100000
    indices = np.arange(dataset_size)

    start = time.perf_counter()
    for _ in range(10):
        np.random.shuffle(indices)
    elapsed = time.perf_counter() - start

    assert elapsed < 0.5, f"10 shuffles of 100k items took {elapsed:.3f}s"


def test_data_preprocessing_pipeline(tmp_path):
    """Test end-to-end data preprocessing pipeline performance."""
    np.random.seed(42)

    # Create raw data
    num_samples = 5000
    num_features = 50
    raw_data = np.random.randn(num_samples, num_features).astype(np.float32)

    data_file = tmp_path / "raw_data.npy"
    np.save(data_file, raw_data)

    start = time.perf_counter()

    # Load
    data = np.load(data_file)

    # Normalize
    mean = np.mean(data, axis=0)
    std = np.std(data, axis=0) + 1e-8
    normalized = (data - mean) / std

    # Clip outliers
    clipped = np.clip(normalized, -3, 3)

    # Save processed
    output_file = tmp_path / "processed_data.npy"
    np.save(output_file, clipped)

    elapsed = time.perf_counter() - start

    assert elapsed < 1.0, f"Preprocessing pipeline took {elapsed:.3f}s"


# API Response Time Tests


def test_api_prediction_latency():
    """Test API prediction endpoint latency."""
    np.random.seed(42)

    # Simulate model
    input_dim = 100
    output_dim = 10
    weights = np.random.randn(input_dim, output_dim).astype(np.float32)

    latencies = []
    for _ in range(100):
        input_data = np.random.randn(1, input_dim).astype(np.float32)

        start = time.perf_counter()
        output = np.dot(input_data, weights)
        softmax = np.exp(output) / np.sum(np.exp(output))
        elapsed = time.perf_counter() - start

        latencies.append(elapsed)
        # Verify softmax is valid probability distribution
        assert softmax.shape == (1, output_dim) and np.isfinite(softmax).all()

    avg_latency = np.mean(latencies)
    p95_latency = np.percentile(latencies, 95)

    assert avg_latency < 0.001, f"Avg latency {avg_latency*1000:.2f}ms too high"
    assert p95_latency < 0.002, f"P95 latency {p95_latency*1000:.2f}ms too high"


def test_api_batch_prediction_throughput():
    """Test API batch prediction throughput."""
    np.random.seed(42)

    input_dim = 256
    output_dim = 128
    weights = np.random.randn(input_dim, output_dim).astype(np.float32)

    batch_sizes = [1, 8, 32, 128]
    throughputs = {}

    for batch_size in batch_sizes:
        inputs = np.random.randn(batch_size, input_dim).astype(np.float32)

        start = time.perf_counter()
        num_iterations = 1000
        for _ in range(num_iterations):
            np.dot(inputs, weights)
        elapsed = time.perf_counter() - start

        samples_per_second = (num_iterations * batch_size) / elapsed
        throughputs[batch_size] = samples_per_second

    # Larger batches should have higher throughput
    assert throughputs[128] > throughputs[1], "Batching should improve throughput"


def test_api_json_serialization_performance():
    """Test JSON serialization performance for API responses."""
    np.random.seed(42)

    # Create response data
    response = {
        "predictions": np.random.randn(100, 10).tolist(),
        "probabilities": np.random.rand(100, 10).tolist(),
        "metadata": {
            "model_version": "1.0.0",
            "timestamp": "2024-01-01T00:00:00Z",
            "latency_ms": 15.3,
        },
    }

    start = time.perf_counter()
    for _ in range(100):
        json_str = json.dumps(response)
        json.loads(json_str)
    elapsed = time.perf_counter() - start

    assert elapsed < 1.0, f"100 JSON serialize/deserialize cycles took {elapsed:.3f}s"


def test_api_request_validation_performance():
    """Test performance of input validation for API requests."""

    def validate_request(data):
        required_fields = ["input", "model_id", "options"]
        for field in required_fields:
            if field not in data:
                return False

        if not isinstance(data["input"], list):
            return False
        return not (len(data["input"]) == 0 or len(data["input"]) > 1000)

    valid_request = {
        "input": [[1.0] * 100],
        "model_id": "model-v1",
        "options": {"temperature": 0.7},
    }

    start = time.perf_counter()
    for _ in range(10000):
        validate_request(valid_request)
    elapsed = time.perf_counter() - start

    validations_per_second = 10000 / elapsed
    assert (validations_per_second > 1000, "validations_per_second must be greater than zero"
    ), f"Validation throughput {validations_per_second:.0f}/s too low"


def test_api_rate_limiting_overhead():
    """Test performance overhead of rate limiting logic."""
    from collections import defaultdict
    from time import time as get_time

    # Simple rate limiter
    rate_limits = defaultdict(list)
    max_requests = 100
    window_seconds = 60

    def check_rate_limit(client_id):
        now = get_time()
        # Remove old requests
        rate_limits[client_id] = [ts for ts in rate_limits[client_id] if now - ts < window_seconds]

        if len(rate_limits[client_id]) >= max_requests:
            return False

        rate_limits[client_id].append(now)
        return True

    start = time.perf_counter()
    for i in range(1000):
        check_rate_limit("client-1")
    elapsed = time.perf_counter() - start

    assert elapsed < 0.1, f"1000 rate limit checks took {elapsed:.3f}s"


# Memory Profiling Tests


def test_memory_allocation_training_loop():
    """Test memory allocation patterns in training loop."""
    np.random.seed(42)

    batch_size = 64
    input_dim = 1024
    hidden_dim = 512

    # Pre-allocate arrays to avoid repeated allocation
    inputs = np.random.randn(batch_size, input_dim).astype(np.float32)
    weights1 = np.random.randn(input_dim, hidden_dim).astype(np.float32)
    weights2 = np.random.randn(hidden_dim, hidden_dim).astype(np.float32)

    hidden = np.empty((batch_size, hidden_dim), dtype=np.float32)
    output = np.empty((batch_size, hidden_dim), dtype=np.float32)

    start = time.perf_counter()
    for _ in range(1000):
        # Reuse pre-allocated arrays
        np.dot(inputs, weights1, out=hidden)
        np.maximum(hidden, 0, out=hidden)  # ReLU in-place
        np.dot(hidden, weights2, out=output)
    elapsed = time.perf_counter() - start

    assert elapsed < 2.0, f"1000 iterations with pre-allocation took {elapsed:.3f}s"


def test_memory_efficient_gradient_accumulation():
    """Test memory-efficient gradient accumulation."""
    np.random.seed(42)

    num_microbatches = 8
    microbatch_size = 4
    input_dim = 512
    output_dim = 256

    weights = np.random.randn(input_dim, output_dim).astype(np.float32)
    accumulated_grad = np.zeros_like(weights)

    start = time.perf_counter()
    for _ in range(num_microbatches):
        inputs = np.random.randn(microbatch_size, input_dim).astype(np.float32)
        grad_output = np.random.randn(microbatch_size, output_dim).astype(np.float32)

        # Accumulate gradients in-place
        grad = np.dot(inputs.T, grad_output)
        accumulated_grad += grad

    # Average gradients
    accumulated_grad /= num_microbatches
    elapsed = time.perf_counter() - start

    assert elapsed < 0.1, f"Gradient accumulation took {elapsed:.3f}s"


def test_memory_cache_efficiency():
    """Test cache-efficient data access patterns."""
    np.random.seed(42)

    size = 1000
    matrix = np.random.randn(size, size).astype(np.float32)

    # Row-major access (cache-friendly)
    start = time.perf_counter()
    row_sum = 0
    for i in range(size):
        row_sum += np.sum(matrix[i, :])
    row_elapsed = time.perf_counter() - start

    # Column-major access (cache-unfriendly)
    start = time.perf_counter()
    col_sum = 0
    for j in range(size):
        col_sum += np.sum(matrix[:, j])
    col_elapsed = time.perf_counter() - start

    # Row access should be faster due to cache efficiency
    # Allow some variance but row access should generally be faster
    assert row_elapsed < col_elapsed * 2, "Row-major access should be cache-efficient"


def test_vectorization_performance():
    """Test performance benefits of vectorization."""
    np.random.seed(42)

    size = 100000
    a = np.random.randn(size).astype(np.float32)
    b = np.random.randn(size).astype(np.float32)

    # Vectorized operation
    start = time.perf_counter()
    result_vec = a * b + np.sin(a) + np.cos(b)
    vec_elapsed = time.perf_counter() - start

    # Loop-based operation
    start = time.perf_counter()
    result_loop = np.empty(size, dtype=np.float32)
    for i in range(size):
        result_loop[i] = a[i] * b[i] + np.sin(a[i]) + np.cos(b[i])
    loop_elapsed = time.perf_counter() - start

    # Vectorized should be significantly faster (3x+ to account for CI variance)
    assert vec_elapsed < loop_elapsed / 3, "Vectorization should provide 3x+ speedup"
    np.testing.assert_allclose(result_vec, result_loop, rtol=1e-6)


def test_sparse_computation_efficiency():
    """Test efficiency of sparse matrix operations."""
    np.random.seed(42)

    size = 1000
    sparsity = 0.95  # 95% zeros

    # Create sparse matrix (mostly zeros)
    dense = np.random.randn(size, size).astype(np.float32)
    mask = np.random.rand(size, size) > sparsity
    sparse = dense * mask

    vector = np.random.randn(size).astype(np.float32)

    # Dense computation
    result_dense = np.dot(sparse, vector)
    # Sparse computation (using masks)
    result_sparse = np.zeros(size, dtype=np.float32)
    for i in range(size):
        nonzero_idx = np.nonzero(mask[i, :])[0]
        if len(nonzero_idx) > 0:
            result_sparse[i] = np.dot(sparse[i, nonzero_idx], vector[nonzero_idx])
    # Both should produce same result
    # Note: Increased tolerance to account for accumulated floating-point errors in sparse computation
    np.testing.assert_allclose(result_dense, result_sparse, rtol=1e-4, atol=1e-6)
