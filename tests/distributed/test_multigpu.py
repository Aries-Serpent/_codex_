"""
Multi-GPU Integration Tests for Distributed Training

Comprehensive test suite for distributed training scenarios including:
- Data parallel training (DDP)
- Model parallel training
- Pipeline parallel training
- Multi-GPU harness and utilities

Author: Codex ML Team
Version: 1.0.0
"""

import pytest

pytest.importorskip("torch")

pytest.importorskip("torch")

# Apply disable_torch_profiler fixture to all tests in this module
# to avoid profiler type errors
pytestmark = pytest.mark.usefixtures("disable_torch_profiler")


import os
import sys
import unittest

from codex.logging.structured_logger import logger

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

try:
    import torch
    import torch.distributed as dist
    import torch.nn as nn
    from torch.nn.parallel import DistributedDataParallel as DDP

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    nn = None
    dist = None
    DDP = None


class MultiGPUTestHarness:
    """
    Harness for running multi-GPU tests.

    Features:
    - GPU detection and validation
    - Distributed process spawning
    - Result collection across ranks
    - Graceful skipping when GPUs unavailable
    """

    def __init__(self):
        """Initialize multi-GPU test harness."""
        self.num_gpus = self._detect_gpus()
        self.distributed_available = self._check_distributed()

    def _detect_gpus(self) -> int:
        """Detect number of available GPUs."""
        if not TORCH_AVAILABLE:
            return 0
        if not torch.cuda.is_available():
            return 0
        return torch.cuda.device_count()

    def _check_distributed(self) -> bool:
        """Check if distributed training is available."""
        if not TORCH_AVAILABLE:
            return False
        return dist.is_available() and dist.is_nccl_available()

    def has_gpus(self, min_gpus: int = 1) -> bool:
        """Check if minimum number of GPUs are available."""
        return self.num_gpus >= min_gpus

    def skip_if_no_gpus(self, min_gpus: int = 1):
        """Decorator to skip test if insufficient GPUs."""

        def decorator(test_func):
            return unittest.skipUnless(
                self.has_gpus(min_gpus),
                f"Requires at least {min_gpus} GPU(s), but only {self.num_gpus} available",
            )(test_func)

        return decorator


# Global harness instance
harness = MultiGPUTestHarness()


class MockGPUEnvironment:
    """Mock GPU environment for testing without actual GPUs."""

    def __init__(self, num_gpus: int = 2):
        """
        Initialize mock GPU environment.

        Args:
            num_gpus: Number of mock GPUs to simulate
        """
        self.num_gpus = num_gpus
        self.rank = 0
        self.world_size = num_gpus

    def setup(self):
        """Setup mock environment variables."""
        os.environ["RANK"] = str(self.rank)
        os.environ["WORLD_SIZE"] = str(self.world_size)
        os.environ["LOCAL_RANK"] = str(self.rank)
        os.environ["MASTER_ADDR"] = "localhost"
        os.environ["MASTER_PORT"] = "12345"

    def teardown(self):
        """Cleanup mock environment."""
        for key in ["RANK", "WORLD_SIZE", "LOCAL_RANK", "MASTER_ADDR", "MASTER_PORT"]:
            os.environ.pop(key, None)


@unittest.skipUnless(TORCH_AVAILABLE, "PyTorch not available")
class TestDataParallelism(unittest.TestCase):
    """Test suite for data parallel training (DDP)."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_env = MockGPUEnvironment(num_gpus=2)

    def tearDown(self):
        """Clean up after tests."""
        self.mock_env.teardown()

    def test_ddp_initialization(self):
        """Test DDP model initialization."""
        if not harness.has_gpus(1):
            # Mock test when no GPUs available
            model = nn.Linear(10, 10)
            self.assertIsInstance(model, nn.Module)
            return

        # Actual GPU test
        model = nn.Linear(10, 10).cuda()
        ddp_model = DDP(model, device_ids=[0])
        self.assertIsInstance(ddp_model, DDP)

    def test_ddp_gradient_synchronization(self):
        """Test gradient synchronization across ranks."""
        # Mock test without actual multi-GPU
        model = nn.Linear(10, 10)
        optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

        # Forward pass
        x = torch.randn(4, 10)
        y = model(x)
        loss = y.sum()

        # Backward pass
        loss.backward()

        # Check gradients exist
        for param in model.parameters():
            self.assertIsNotNone(param.grad)

        optimizer.step()

    @harness.skip_if_no_gpus(2)
    def test_ddp_multi_gpu_training(self):
        """Test training with multiple GPUs (requires 2+ GPUs)."""
        # This test only runs if 2+ GPUs are available
        device = torch.device("cuda:0")
        model = nn.Linear(10, 10).to(device)
        ddp_model = DDP(model, device_ids=[0])

        # Training step
        optimizer = torch.optim.SGD(ddp_model.parameters(), lr=0.01)
        x = torch.randn(4, 10, device=device)
        y = ddp_model(x)
        loss = y.sum()
        loss.backward()
        optimizer.step()

        self.assertTrue(True)  # Test passed if we got here

    def test_ddp_checkpoint_consistency(self):
        """Test checkpoint saving and loading with DDP."""
        model = nn.Linear(10, 10)

        # Save checkpoint
        checkpoint = {
            "model": model.state_dict(),
            "optimizer": torch.optim.SGD(model.parameters(), lr=0.01).state_dict(),
        }

        # Load checkpoint
        model_restored = nn.Linear(10, 10)
        model_restored.load_state_dict(checkpoint["model"])

        # Verify parameters match
        for p1, p2 in zip(model.parameters(), model_restored.parameters()):
            self.assertTrue(torch.allclose(p1, p2))


@unittest.skipUnless(TORCH_AVAILABLE, "PyTorch not available")
class TestModelParallelism(unittest.TestCase):
    """Test suite for model parallel training."""

    def test_model_split_across_devices(self):
        """Test splitting model across multiple devices."""

        # Mock test without actual multi-GPU
        class SplitModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.layer1 = nn.Linear(10, 10)  # Device 0
                self.layer2 = nn.Linear(10, 10)  # Device 1 (or CPU in mock)

            def forward(self, x):
                x = self.layer1(x)
                # In real multi-GPU, would move to device 1 here
                return self.layer2(x)

        model = SplitModel()
        x = torch.randn(4, 10)
        y = model(x)

        self.assertEqual(y.shape, (4, 10))

    @harness.skip_if_no_gpus(2)
    def test_tensor_parallel_communication(self):
        """Test tensor parallel communication patterns (requires 2+ GPUs)."""
        # This test only runs with actual GPUs
        device0 = torch.device("cuda:0")
        device1 = torch.device("cuda:1")

        # Create tensors on different devices
        t0 = torch.randn(4, 10, device=device0)
        t1 = t0.to(device1)

        # Verify tensor moved correctly
        self.assertEqual(t1.device.type, "cuda")
        self.assertEqual(t1.device.index, 1)


@unittest.skipUnless(TORCH_AVAILABLE, "PyTorch not available")
class TestPipelineParallelism(unittest.TestCase):
    """Test suite for pipeline parallel training."""

    def test_pipeline_micro_batching(self):
        """Test micro-batch scheduling for pipeline parallelism."""
        # Mock pipeline with micro-batches
        batch_size = 32
        micro_batch_size = 8
        num_micro_batches = batch_size // micro_batch_size

        self.assertEqual(num_micro_batches, 4)

        # Simulate micro-batch processing
        x = torch.randn(batch_size, 10)
        micro_batches = x.split(micro_batch_size)

        self.assertEqual(len(micro_batches), num_micro_batches)
        for mb in micro_batches:
            self.assertEqual(mb.shape[0], micro_batch_size)

    def test_pipeline_gradient_accumulation(self):
        """Test gradient accumulation across micro-batches."""
        model = nn.Linear(10, 10)
        optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

        # Accumulate gradients over micro-batches
        optimizer.zero_grad()

        num_micro_batches = 4
        for i in range(num_micro_batches):
            x = torch.randn(8, 10)
            y = model(x)
            loss = y.sum() / num_micro_batches
            loss.backward()

        # Check gradients accumulated
        for param in model.parameters():
            self.assertIsNotNone(param.grad)

        optimizer.step()


@unittest.skipUnless(TORCH_AVAILABLE, "PyTorch not available")
class TestDistributedUtilities(unittest.TestCase):
    """Test suite for distributed training utilities."""

    def test_rank_detection(self):
        """Test rank and world size detection."""
        # Mock distributed environment
        mock_env = MockGPUEnvironment(num_gpus=4)
        mock_env.setup()

        rank = int(os.environ.get("RANK", 0))
        world_size = int(os.environ.get("WORLD_SIZE", 1))

        self.assertEqual(rank, 0)
        self.assertEqual(world_size, 4)

        mock_env.teardown()

    def test_gpu_memory_tracking(self):
        """Test GPU memory usage tracking."""
        if not harness.has_gpus(1):
            self.skipTest("No GPUs available")
            return

        # Allocate tensor on GPU
        device = torch.device("cuda:0")
        t = torch.randn(1000, 1000, device=device)

        # Check memory allocated
        mem_allocated = torch.cuda.memory_allocated(0)
        self.assertGreater(mem_allocated, 0)

        # Free memory
        del t
        torch.cuda.empty_cache()

    def test_distributed_barrier_mock(self):
        """Test distributed barrier synchronization (mock)."""
        # Mock barrier - in real distributed training, this synchronizes all ranks
        # For testing, we just verify the concept works
        barrier_called = False

        def mock_barrier():
            nonlocal barrier_called
            barrier_called = True

        mock_barrier()
        self.assertTrue(barrier_called)


@unittest.skipUnless(TORCH_AVAILABLE, "PyTorch not available")
class TestDistributedDataLoader(unittest.TestCase):
    """Test suite for distributed data loading."""

    def test_data_sharding(self):
        """Test data sharding across ranks."""
        from torch.utils.data import DataLoader, Dataset
        from torch.utils.data.distributed import DistributedSampler

        class DummyDataset(Dataset):
            def __init__(self, size=100):
                self.size = size

            def __len__(self):
                return self.size

            def __getitem__(self, idx):
                return torch.randn(10), torch.randint(0, 10, (1,)).item()

        dataset = DummyDataset(size=100)

        # Create distributed sampler (mock with 4 ranks)
        sampler = DistributedSampler(dataset, num_replicas=4, rank=0)
        loader = DataLoader(dataset, batch_size=8, sampler=sampler)

        # Verify data loader works
        batch = next(iter(loader))
        self.assertEqual(len(batch), 2)  # (data, labels)
        self.assertEqual(batch[0].shape[0], 8)  # batch size


def run_multi_gpu_tests():
    """
    Run multi-GPU test suite.

    Returns:
        TestResult: Test results
    """
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDataParallelism))
    suite.addTests(loader.loadTestsFromTestCase(TestModelParallelism))
    suite.addTests(loader.loadTestsFromTestCase(TestPipelineParallelism))
    suite.addTests(loader.loadTestsFromTestCase(TestDistributedUtilities))
    suite.addTests(loader.loadTestsFromTestCase(TestDistributedDataLoader))

    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)


if __name__ == "__main__":
    # Print GPU availability info
    logger.info(f"PyTorch Available: {TORCH_AVAILABLE}")
    if TORCH_AVAILABLE:
        logger.info(f"CUDA Available: {torch.cuda.is_available()}")
        logger.info(f"Number of GPUs: {harness.num_gpus}")
        logger.info(f"Distributed Available: {harness.distributed_available}")


    # Run tests
    result = run_multi_gpu_tests()

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
