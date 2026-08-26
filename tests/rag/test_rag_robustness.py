"""
Comprehensive tests for RAG timeout hardening and resilience.

PHASE 4D PLANSET 003: RAG Module Robustness
Authority: D-tier autonomous
Target Reliability: 99%+
"""

import builtins
import hashlib
import importlib
import sys
import time
import types
import unittest
from unittest.mock import MagicMock, patch

from rag.hardened_embedding import HardenedEmbeddingPipeline
from rag.monitoring import OperationMetric, RAGMonitor
from rag.monitoring import set_rag_monitor as set_monitor
from rag.pipelines.embedding import EmbeddingConfig, EmbeddingPipeline
from rag.resilience import (
    FailureType,
    RetryConfig,
    RetryStrategy,
)
from rag.timeout_manager import (
    CircuitState,
    TimeoutConfig,
    TimeoutManager,
    TimeoutMetrics,
)


class TestEmbeddingPipelineLogging(unittest.TestCase):
    """Tests for privacy-safe embedding logs and meta-tensor fallback handling."""

    def test_numpy_fallback_error_mentions_current_module(self):
        """Missing numpy should point at the active module path, not the legacy package path."""
        original_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "numpy":
                raise ImportError("numpy is unavailable")
            return original_import(name, *args, **kwargs)

        sys.modules.pop("aries_serpent_core.rag.embeddings", None)
        with patch("builtins.__import__", side_effect=fake_import):
            module = importlib.import_module("aries_serpent_core.rag.embeddings")
            with self.assertRaisesRegex(AttributeError, r"aries_serpent_core\.rag\.embeddings"):
                getattr(module.np, "missing_attribute")
            with self.assertRaisesRegex(ImportError, r"aries_serpent_core\.rag\.embeddings"):
                module.np.array()

    def test_embed_text_logs_hash_not_raw_text(self):
        """Sensitive input should not be logged verbatim when the model fails."""
        pipeline = EmbeddingPipeline()
        pipeline._use_fallback = False
        pipeline._model = MagicMock()
        pipeline._model.encode.side_effect = RuntimeError("model exploded")
        text = "super-secret-query-bearing-user-data"
        expected_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]

        with patch("rag.pipelines.embedding.logger.warning") as mock_warning:
            result = pipeline.embed_text(text)

        self.assertEqual(result.model, "fallback-hash")
        logged_payload = " ".join(
            str(arg) for call in mock_warning.call_args_list for arg in call.args
        )
        self.assertNotIn(text, logged_payload)
        self.assertIn(expected_hash, logged_payload)

    def test_safe_load_sentence_transformer_attempts_meta_fallback(self):
        """NotImplementedError must trigger the meta-to-empty fallback before generic runtime errors."""
        from aries_serpent_core.rag._model_utils import safe_load_sentence_transformer

        first_model = MagicMock()
        first_model.eval.return_value = None
        materialized_model = MagicMock()
        materialized_model.eval.return_value = None
        materialized_model.named_parameters.return_value = []

        meta_model = MagicMock()
        meta_model.to_empty.return_value = materialized_model

        fake_sentence_transformers = types.SimpleNamespace(
            SentenceTransformer=MagicMock(
                side_effect=[NotImplementedError("meta tensor"), meta_model]
            )
        )

        with patch.dict(sys.modules, {"sentence_transformers": fake_sentence_transformers}):
            result = safe_load_sentence_transformer("test-model", None)

        self.assertIs(result, materialized_model)
        self.assertEqual(fake_sentence_transformers.SentenceTransformer.call_count, 2)
        materialized_model.to_empty.assert_not_called()
        meta_model.to_empty.assert_called_once_with(device="cpu")


class TestTimeoutManager(unittest.TestCase):
    """Tests for timeout management."""

    def setUp(self):
        self.config = TimeoutConfig(
            embedding_timeout=10.0,
            retrieval_timeout=5.0,
        )
        self.manager = TimeoutManager(self.config)

    def test_circuit_breaker_initialization(self):
        """Test circuit breaker starts closed."""
        circuit = self.manager.get_circuit_breaker("test_op")
        self.assertEqual(circuit.state, CircuitState.CLOSED)
        self.assertFalse(self.manager.is_circuit_open("test_op"))

    def test_circuit_breaker_opens_after_failures(self):
        """Test circuit opens after threshold failures."""
        circuit = self.manager.get_circuit_breaker("test_op")

        # Record failures
        for _ in range(self.config.circuit_breaker_threshold):
            circuit.record_failure(self.config)

        self.assertEqual(circuit.state, CircuitState.OPEN)
        self.assertTrue(self.manager.is_circuit_open("test_op"))

    def test_circuit_breaker_half_open_after_reset_time(self):
        """Test circuit transitions to half-open after reset time."""
        circuit = self.manager.get_circuit_breaker("test_op")

        # Open the circuit
        for _ in range(self.config.circuit_breaker_threshold):
            circuit.record_failure(self.config)

        self.assertTrue(self.manager.is_circuit_open("test_op"))

        # Simulate time passing
        circuit.last_state_change = time.time() - self.config.circuit_breaker_reset_time - 1

        # Should transition to half-open
        is_open = self.manager.is_circuit_open("test_op")
        self.assertEqual(circuit.state, CircuitState.HALF_OPEN)

    def test_timeout_metrics_recording(self):
        """Test timeout metrics are recorded."""
        metrics = TimeoutMetrics(
            operation_type="test",
            start_time=time.time() - 1.0,
        )
        metrics.compute_duration()

        self.assertGreater(metrics.duration_ms, 950)  # ~1000ms
        self.assertLess(metrics.duration_ms, 1050)


class TestRetryStrategy(unittest.TestCase):
    """Tests for retry strategy."""

    def setUp(self):
        self.config = RetryConfig(
            max_retries=3,
            initial_backoff=0.01,
            max_backoff=0.5,
            enable_jitter=False,  # Disable jitter for predictable tests
        )
        self.strategy = RetryStrategy(self.config)

    def test_classify_timeout_error(self):
        """Test timeout error classification."""
        error = TimeoutError("Operation timed out")
        failure_type = self.strategy.classify_error(error)
        self.assertEqual(failure_type, FailureType.TIMEOUT)

    def test_classify_transient_error(self):
        """Test transient error classification."""
        error = ConnectionError("Connection refused")
        failure_type = self.strategy.classify_error(error)
        self.assertEqual(failure_type, FailureType.TRANSIENT)

    def test_classify_resource_exhaustion(self):
        """Test resource exhaustion classification."""
        error = MemoryError("Out of memory")
        failure_type = self.strategy.classify_error(error)
        self.assertEqual(failure_type, FailureType.RESOURCE_EXHAUSTED)

    def test_should_retry_timeout(self):
        """Test timeout errors are retried."""
        error = TimeoutError("Timeout")
        self.assertTrue(self.strategy.should_retry(error, attempt=0))
        self.assertTrue(self.strategy.should_retry(error, attempt=1))
        self.assertTrue(self.strategy.should_retry(error, attempt=2))

    def test_should_not_retry_after_max_attempts(self):
        """Test no retry after max attempts."""
        error = TimeoutError("Timeout")
        self.assertFalse(
            self.strategy.should_retry(error, attempt=self.config.max_retries)
        )

    def test_backoff_calculation(self):
        """Test exponential backoff calculation."""
        backoff_0 = self.strategy.calculate_backoff(0)
        backoff_1 = self.strategy.calculate_backoff(1)
        backoff_2 = self.strategy.calculate_backoff(2)

        self.assertEqual(backoff_0, self.config.initial_backoff)
        self.assertAlmostEqual(
            backoff_1, self.config.initial_backoff * 2, places=2
        )
        self.assertAlmostEqual(
            backoff_2, self.config.initial_backoff * 4, places=2
        )

    def test_execute_with_retries_success(self):
        """Test successful execution without retries."""
        call_count = 0

        def success_fn():
            nonlocal call_count
            call_count += 1
            return "success"

        result, metrics = self.strategy.execute_with_retries(
            success_fn, operation_name="test"
        )

        self.assertEqual(result, "success")
        self.assertEqual(call_count, 1)
        self.assertEqual(metrics.total_attempts, 1)

    def test_execute_with_retries_eventual_success(self):
        """Test eventual success after retries."""
        call_count = 0

        def retry_fn():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise TimeoutError("Timeout")
            return "success"

        result, metrics = self.strategy.execute_with_retries(
            retry_fn, operation_name="test"
        )

        self.assertEqual(result, "success")
        self.assertEqual(call_count, 3)
        self.assertEqual(metrics.total_attempts, 3)

    def test_execute_with_retries_exhausted(self):
        """Test failure after retries exhausted."""
        call_count = 0

        def always_fail():
            nonlocal call_count
            call_count += 1
            raise TimeoutError("Timeout")

        with self.assertRaises(TimeoutError):
            self.strategy.execute_with_retries(
                always_fail, operation_name="test"
            )

        self.assertEqual(call_count, self.config.max_retries + 1)


class TestRAGMonitor(unittest.TestCase):
    """Tests for RAG monitoring."""

    def setUp(self):
        self.monitor = RAGMonitor(window_size=10)

    def test_record_successful_metric(self):
        """Test recording successful operation."""
        metric = OperationMetric(
            operation_type="embedding",
            timestamp=time.time(),
            duration_ms=100.0,
            success=True,
        )

        self.monitor.record_metric(metric)
        health = self.monitor.get_operation_health("embedding")

        self.assertEqual(health["total_operations"], 1)
        self.assertEqual(health["successful_operations"], 1)
        self.assertEqual(health["success_rate"], 1.0)

    def test_record_failed_metric(self):
        """Test recording failed operation."""
        metric = OperationMetric(
            operation_type="retrieval",
            timestamp=time.time(),
            duration_ms=100.0,
            success=False,
        )

        self.monitor.record_metric(metric)
        health = self.monitor.get_operation_health("retrieval")

        self.assertEqual(health["total_operations"], 1)
        self.assertEqual(health["failed_operations"], 1)
        self.assertEqual(health["error_rate"], 1.0)

    def test_record_timeout_metric(self):
        """Test recording timeout."""
        metric = OperationMetric(
            operation_type="embedding",
            timestamp=time.time(),
            duration_ms=100.0,
            success=False,
            timed_out=True,
        )

        self.monitor.record_metric(metric)
        health = self.monitor.get_operation_health("embedding")

        self.assertEqual(health["timed_out_operations"], 1)
        self.assertEqual(health["timeout_rate"], 1.0)

    def test_percentile_calculation(self):
        """Test percentile calculations."""
        for i in range(100):
            metric = OperationMetric(
                operation_type="test",
                timestamp=time.time(),
                duration_ms=float(i),  # 0-99ms
                success=True,
            )
            self.monitor.record_metric(metric)

        health = self.monitor.get_operation_health("test")

        # P50 should be around 50ms
        self.assertGreater(health["duration_ms"]["p50"], 40)
        self.assertLess(health["duration_ms"]["p50"], 60)

        # P95 should be around 95ms
        self.assertGreater(health["duration_ms"]["p95"], 90)

        # P99 should be close to 99ms
        self.assertGreater(health["duration_ms"]["p99"], 95)


class TestHardenedEmbeddingPipeline(unittest.TestCase):
    """Tests for hardened embedding pipeline."""

    def setUp(self):
        config = EmbeddingConfig(batch_size=32)
        timeout_config = TimeoutConfig(embedding_timeout=30.0)
        self.timeout_manager = TimeoutManager(timeout_config)
        self.monitor = RAGMonitor()
        set_monitor(self.monitor)

        self.pipeline = HardenedEmbeddingPipeline(
            config=config,
            timeout_manager=self.timeout_manager,
        )

    def test_embed_text_fallback(self):
        """Test fallback to hash-based embedding."""
        result = self.pipeline.embed_text("test text")

        self.assertEqual(result.dimension, self.pipeline.config.dimension)
        self.assertEqual(len(result.embedding), self.pipeline.config.dimension)
        self.assertTrue(all(isinstance(x, (int, float)) for x in result.embedding))

    def test_embed_empty_text(self):
        """Test embedding empty text."""
        result = self.pipeline.embed_text("")

        self.assertEqual(result.dimension, self.pipeline.config.dimension)
        self.assertEqual(result.text, "")

    def test_embed_texts_multiple(self):
        """Test embedding multiple texts."""
        texts = ["text1", "text2", "text3"]
        results = self.pipeline.embed_texts(texts)

        self.assertEqual(len(results), len(texts))
        for result in results:
            self.assertEqual(result.dimension, self.pipeline.config.dimension)


class TestStressScenarios(unittest.TestCase):
    """Stress tests for RAG reliability."""

    def setUp(self):
        config = EmbeddingConfig()
        timeout_config = TimeoutConfig(
            embedding_timeout=30.0,
            enable_circuit_breaker=True,
            circuit_breaker_threshold=5,
        )
        self.timeout_manager = TimeoutManager(timeout_config)
        self.monitor = RAGMonitor()
        set_monitor(self.monitor)

        self.pipeline = HardenedEmbeddingPipeline(
            config=config,
            timeout_manager=self.timeout_manager,
        )

    def test_high_volume_requests(self):
        """Test handling high volume of requests."""
        num_requests = 100
        texts = [f"text {i}" for i in range(num_requests)]

        start_time = time.time()
        for text in texts:
            result = self.pipeline.embed_text(text)
            self.assertIsNotNone(result)

        elapsed = time.time() - start_time

        health = self.monitor.get_operation_health("embedding")
        success_rate = health["success_rate"]

        # Should have high success rate
        self.assertGreater(success_rate, 0.95)

        # Should complete in reasonable time
        self.assertLess(elapsed, 30)  # 30 seconds for 100 texts

    def test_batch_processing_reliability(self):
        """Test batch processing reliability."""
        batch_size = 50
        num_batches = 5

        total_success = 0
        for batch_idx in range(num_batches):
            texts = [f"text {batch_idx}_{i}" for i in range(batch_size)]
            results = self.pipeline.embed_texts(texts)
            total_success += len(results)

        self.assertEqual(total_success, batch_size * num_batches)

        health = self.monitor.get_operation_health("batch_embedding")
        success_rate = health["success_rate"]
        self.assertGreater(success_rate, 0.95)


class TestCircuitBreakerIntegration(unittest.TestCase):
    """Tests for circuit breaker integration."""

    def test_circuit_breaker_prevents_cascade(self):
        """Test circuit breaker prevents cascading failures."""
        config = TimeoutConfig(
            circuit_breaker_threshold=3,
            circuit_breaker_reset_time=1.0,
        )
        manager = TimeoutManager(config)

        # Simulate failures
        for i in range(3):
            metric = TimeoutMetrics(
                operation_type="test",
                start_time=time.time(),
            )
            manager.record_failure("test_op", metric, "error")

        # Circuit should be open
        self.assertTrue(manager.is_circuit_open("test_op"))

        # Wait for reset
        time.sleep(1.1)

        # Should transition to half-open
        is_open = manager.is_circuit_open("test_op")
        circuit = manager.get_circuit_breaker("test_op")
        self.assertEqual(circuit.state, CircuitState.HALF_OPEN)


if __name__ == "__main__":
    unittest.main()
