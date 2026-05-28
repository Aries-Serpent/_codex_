from __future__ import annotations

import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.training import accelerate_init_guard as guard


class TrainingAccelerateGuardCoverageTests(unittest.TestCase):
    def test_is_gpu_available_with_mocked_torch(self) -> None:
        mocked_torch = SimpleNamespace(cuda=SimpleNamespace(is_available=lambda: True))
        with patch.dict(sys.modules, {"torch": mocked_torch}):
            self.assertTrue(guard.is_gpu_available())

    def test_is_accelerate_available_cached_true(self) -> None:
        with patch.object(guard, "_ACCELERATOR_AVAILABLE", True), patch.object(
            guard, "Accelerator", object
        ):
            self.assertTrue(guard.is_accelerate_available())

    def test_is_accelerate_available_import_paths(self) -> None:
        with (
            patch.object(guard, "_ACCELERATOR_AVAILABLE", False),
            patch.object(guard, "_ACCELERATE_SPEC_AVAILABLE", False),
        ):
            self.assertFalse(guard.is_accelerate_available())

    def test_safe_init_returns_cpu_only_when_no_accelerate(self) -> None:
        with (
            patch.object(guard, "is_gpu_available", return_value=False),
            patch.object(guard, "is_accelerate_available", return_value=False),
            patch.dict(os.environ, {"CUDA_VISIBLE_DEVICES": ""}, clear=False),
        ):
            result = guard.safe_accelerate_init(cpu_fallback=True, raise_on_error=False)
        self.assertFalse(result.success)
        self.assertEqual(result.skip_reason, "cpu_only")

    def test_safe_init_no_accelerate_non_cpu_env(self) -> None:
        with (
            patch.object(guard, "is_gpu_available", return_value=False),
            patch.object(guard, "is_accelerate_available", return_value=False),
            patch.dict(os.environ, {"CUDA_VISIBLE_DEVICES": "0"}, clear=False),
        ):
            result = guard.safe_accelerate_init(cpu_fallback=False, raise_on_error=False)
        self.assertFalse(result.success)
        self.assertEqual(result.skip_reason, "no_accelerate")

    def test_safe_init_success_path(self) -> None:
        fake_state = SimpleNamespace(distributed_type="MULTI_CPU")
        def fake_accelerator_cls():
            return SimpleNamespace(state=fake_state)

        with (
            patch.object(guard, "is_gpu_available", return_value=True),
            patch.object(guard, "is_accelerate_available", return_value=True),
            patch.object(guard, "Accelerator", fake_accelerator_cls),
            patch.dict(os.environ, {"WORLD_SIZE": "4", "RANK": "2"}, clear=False),
        ):
            result = guard.safe_accelerate_init(cpu_fallback=True, raise_on_error=False)
        self.assertTrue(result.success)
        self.assertEqual(result.world_size, 4)
        self.assertEqual(result.rank, 2)
        self.assertEqual(result.backend, "MULTI_CPU")

    def test_safe_init_error_and_raise_mode(self) -> None:
        def boom():
            raise RuntimeError("accelerator failed")

        with (
            patch.object(guard, "is_gpu_available", return_value=True),
            patch.object(guard, "is_accelerate_available", return_value=True),
            patch.object(guard, "Accelerator", boom),
        ):
            result = guard.safe_accelerate_init(cpu_fallback=True, raise_on_error=False)
            self.assertFalse(result.success)
            self.assertIn("RuntimeError", result.error or "")

            with self.assertRaises(RuntimeError):
                guard.safe_accelerate_init(cpu_fallback=True, raise_on_error=True)

    def test_get_distributed_env_info_defaults(self) -> None:
        info = guard.get_distributed_env_info()
        self.assertIn("WORLD_SIZE", info)
        self.assertIn("MASTER_ADDR", info)
