"""
Simple Trainer Module

This module provides functionality for simple trainer.

Usage:
    from training.simple_trainer import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    import torch
except Exception:  # pragma: no cover - handle missing torch lazily
    torch = None  # type: ignore[assignment]
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


class SimpleTrainer:
    """Minimal trainer for deterministic smoke tests."""

    def xǁSimpleTrainerǁ__init____mutmut_orig(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_1(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "XXcpuXX",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_2(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "CPU",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_3(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 4,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_4(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "XXval/lossXX",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_5(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "VAL/LOSS",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_6(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "XXminXX",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_7(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "MIN",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_8(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is not None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_9(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError(None)
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_10(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("XXtorch is required for SimpleTrainerXX")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_11(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for simpletrainer")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_12(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("TORCH IS REQUIRED FOR SIMPLETRAINER")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_13(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = None
        self.optimizer = optimizer
        self.device = device
        if mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_14(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(None)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_15(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(device)
        self.optimizer = None
        self.device = device
        if mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_16(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = None
        if mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_17(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_18(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"XXminXX", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_19(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"MIN", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_20(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"min", "XXmaxXX"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_21(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"min", "MAX"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_22(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"min", "max"}:
            raise ValueError(None)
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_23(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"min", "max"}:
            raise ValueError("XXmode must be 'min' or 'max'XX")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_24(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"min", "max"}:
            raise ValueError("MODE MUST BE 'MIN' OR 'MAX'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_25(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = None
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_26(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = None
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_27(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = None
        self.mode = mode
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_28(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = None
        self._best_metric: float | None = None

    def xǁSimpleTrainerǁ__init____mutmut_29(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cpu",
        checkpoint_dir: str | None = None,
        keep_best_k: int = 3,
        monitor: str = "val/loss",
        mode: str = "min",
    ) -> None:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model = model.to(device)
        self.optimizer = optimizer
        self.device = device
        if mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        self.checkpoint_dir = checkpoint_dir
        self.keep_best_k = keep_best_k
        self.monitor = monitor
        self.mode = mode
        self._best_metric: float | None = ""
    
    xǁSimpleTrainerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSimpleTrainerǁ__init____mutmut_1': xǁSimpleTrainerǁ__init____mutmut_1, 
        'xǁSimpleTrainerǁ__init____mutmut_2': xǁSimpleTrainerǁ__init____mutmut_2, 
        'xǁSimpleTrainerǁ__init____mutmut_3': xǁSimpleTrainerǁ__init____mutmut_3, 
        'xǁSimpleTrainerǁ__init____mutmut_4': xǁSimpleTrainerǁ__init____mutmut_4, 
        'xǁSimpleTrainerǁ__init____mutmut_5': xǁSimpleTrainerǁ__init____mutmut_5, 
        'xǁSimpleTrainerǁ__init____mutmut_6': xǁSimpleTrainerǁ__init____mutmut_6, 
        'xǁSimpleTrainerǁ__init____mutmut_7': xǁSimpleTrainerǁ__init____mutmut_7, 
        'xǁSimpleTrainerǁ__init____mutmut_8': xǁSimpleTrainerǁ__init____mutmut_8, 
        'xǁSimpleTrainerǁ__init____mutmut_9': xǁSimpleTrainerǁ__init____mutmut_9, 
        'xǁSimpleTrainerǁ__init____mutmut_10': xǁSimpleTrainerǁ__init____mutmut_10, 
        'xǁSimpleTrainerǁ__init____mutmut_11': xǁSimpleTrainerǁ__init____mutmut_11, 
        'xǁSimpleTrainerǁ__init____mutmut_12': xǁSimpleTrainerǁ__init____mutmut_12, 
        'xǁSimpleTrainerǁ__init____mutmut_13': xǁSimpleTrainerǁ__init____mutmut_13, 
        'xǁSimpleTrainerǁ__init____mutmut_14': xǁSimpleTrainerǁ__init____mutmut_14, 
        'xǁSimpleTrainerǁ__init____mutmut_15': xǁSimpleTrainerǁ__init____mutmut_15, 
        'xǁSimpleTrainerǁ__init____mutmut_16': xǁSimpleTrainerǁ__init____mutmut_16, 
        'xǁSimpleTrainerǁ__init____mutmut_17': xǁSimpleTrainerǁ__init____mutmut_17, 
        'xǁSimpleTrainerǁ__init____mutmut_18': xǁSimpleTrainerǁ__init____mutmut_18, 
        'xǁSimpleTrainerǁ__init____mutmut_19': xǁSimpleTrainerǁ__init____mutmut_19, 
        'xǁSimpleTrainerǁ__init____mutmut_20': xǁSimpleTrainerǁ__init____mutmut_20, 
        'xǁSimpleTrainerǁ__init____mutmut_21': xǁSimpleTrainerǁ__init____mutmut_21, 
        'xǁSimpleTrainerǁ__init____mutmut_22': xǁSimpleTrainerǁ__init____mutmut_22, 
        'xǁSimpleTrainerǁ__init____mutmut_23': xǁSimpleTrainerǁ__init____mutmut_23, 
        'xǁSimpleTrainerǁ__init____mutmut_24': xǁSimpleTrainerǁ__init____mutmut_24, 
        'xǁSimpleTrainerǁ__init____mutmut_25': xǁSimpleTrainerǁ__init____mutmut_25, 
        'xǁSimpleTrainerǁ__init____mutmut_26': xǁSimpleTrainerǁ__init____mutmut_26, 
        'xǁSimpleTrainerǁ__init____mutmut_27': xǁSimpleTrainerǁ__init____mutmut_27, 
        'xǁSimpleTrainerǁ__init____mutmut_28': xǁSimpleTrainerǁ__init____mutmut_28, 
        'xǁSimpleTrainerǁ__init____mutmut_29': xǁSimpleTrainerǁ__init____mutmut_29
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSimpleTrainerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁSimpleTrainerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁSimpleTrainerǁ__init____mutmut_orig)
    xǁSimpleTrainerǁ__init____mutmut_orig.__name__ = 'xǁSimpleTrainerǁ__init__'

    def xǁSimpleTrainerǁstep__mutmut_orig(self, batch: tuple[torch.Tensor, torch.Tensor]) -> float:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model.train()
        inputs, targets = batch
        inputs = inputs.to(self.device)
        targets = targets.to(self.device)
        outputs = self.model(inputs)
        loss = torch.nn.functional.cross_entropy(outputs, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return float(loss.detach().cpu().item())

    def xǁSimpleTrainerǁstep__mutmut_1(self, batch: tuple[torch.Tensor, torch.Tensor]) -> float:
        if torch is not None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model.train()
        inputs, targets = batch
        inputs = inputs.to(self.device)
        targets = targets.to(self.device)
        outputs = self.model(inputs)
        loss = torch.nn.functional.cross_entropy(outputs, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return float(loss.detach().cpu().item())

    def xǁSimpleTrainerǁstep__mutmut_2(self, batch: tuple[torch.Tensor, torch.Tensor]) -> float:
        if torch is None:
            raise RuntimeError(None)
        self.model.train()
        inputs, targets = batch
        inputs = inputs.to(self.device)
        targets = targets.to(self.device)
        outputs = self.model(inputs)
        loss = torch.nn.functional.cross_entropy(outputs, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return float(loss.detach().cpu().item())

    def xǁSimpleTrainerǁstep__mutmut_3(self, batch: tuple[torch.Tensor, torch.Tensor]) -> float:
        if torch is None:
            raise RuntimeError("XXtorch is required for SimpleTrainerXX")
        self.model.train()
        inputs, targets = batch
        inputs = inputs.to(self.device)
        targets = targets.to(self.device)
        outputs = self.model(inputs)
        loss = torch.nn.functional.cross_entropy(outputs, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return float(loss.detach().cpu().item())

    def xǁSimpleTrainerǁstep__mutmut_4(self, batch: tuple[torch.Tensor, torch.Tensor]) -> float:
        if torch is None:
            raise RuntimeError("torch is required for simpletrainer")
        self.model.train()
        inputs, targets = batch
        inputs = inputs.to(self.device)
        targets = targets.to(self.device)
        outputs = self.model(inputs)
        loss = torch.nn.functional.cross_entropy(outputs, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return float(loss.detach().cpu().item())

    def xǁSimpleTrainerǁstep__mutmut_5(self, batch: tuple[torch.Tensor, torch.Tensor]) -> float:
        if torch is None:
            raise RuntimeError("TORCH IS REQUIRED FOR SIMPLETRAINER")
        self.model.train()
        inputs, targets = batch
        inputs = inputs.to(self.device)
        targets = targets.to(self.device)
        outputs = self.model(inputs)
        loss = torch.nn.functional.cross_entropy(outputs, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return float(loss.detach().cpu().item())

    def xǁSimpleTrainerǁstep__mutmut_6(self, batch: tuple[torch.Tensor, torch.Tensor]) -> float:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model.train()
        inputs, targets = None
        inputs = inputs.to(self.device)
        targets = targets.to(self.device)
        outputs = self.model(inputs)
        loss = torch.nn.functional.cross_entropy(outputs, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return float(loss.detach().cpu().item())

    def xǁSimpleTrainerǁstep__mutmut_7(self, batch: tuple[torch.Tensor, torch.Tensor]) -> float:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model.train()
        inputs, targets = batch
        inputs = None
        targets = targets.to(self.device)
        outputs = self.model(inputs)
        loss = torch.nn.functional.cross_entropy(outputs, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return float(loss.detach().cpu().item())

    def xǁSimpleTrainerǁstep__mutmut_8(self, batch: tuple[torch.Tensor, torch.Tensor]) -> float:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model.train()
        inputs, targets = batch
        inputs = inputs.to(None)
        targets = targets.to(self.device)
        outputs = self.model(inputs)
        loss = torch.nn.functional.cross_entropy(outputs, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return float(loss.detach().cpu().item())

    def xǁSimpleTrainerǁstep__mutmut_9(self, batch: tuple[torch.Tensor, torch.Tensor]) -> float:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model.train()
        inputs, targets = batch
        inputs = inputs.to(self.device)
        targets = None
        outputs = self.model(inputs)
        loss = torch.nn.functional.cross_entropy(outputs, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return float(loss.detach().cpu().item())

    def xǁSimpleTrainerǁstep__mutmut_10(self, batch: tuple[torch.Tensor, torch.Tensor]) -> float:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model.train()
        inputs, targets = batch
        inputs = inputs.to(self.device)
        targets = targets.to(None)
        outputs = self.model(inputs)
        loss = torch.nn.functional.cross_entropy(outputs, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return float(loss.detach().cpu().item())

    def xǁSimpleTrainerǁstep__mutmut_11(self, batch: tuple[torch.Tensor, torch.Tensor]) -> float:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model.train()
        inputs, targets = batch
        inputs = inputs.to(self.device)
        targets = targets.to(self.device)
        outputs = None
        loss = torch.nn.functional.cross_entropy(outputs, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return float(loss.detach().cpu().item())

    def xǁSimpleTrainerǁstep__mutmut_12(self, batch: tuple[torch.Tensor, torch.Tensor]) -> float:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model.train()
        inputs, targets = batch
        inputs = inputs.to(self.device)
        targets = targets.to(self.device)
        outputs = self.model(None)
        loss = torch.nn.functional.cross_entropy(outputs, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return float(loss.detach().cpu().item())

    def xǁSimpleTrainerǁstep__mutmut_13(self, batch: tuple[torch.Tensor, torch.Tensor]) -> float:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model.train()
        inputs, targets = batch
        inputs = inputs.to(self.device)
        targets = targets.to(self.device)
        outputs = self.model(inputs)
        loss = None
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return float(loss.detach().cpu().item())

    def xǁSimpleTrainerǁstep__mutmut_14(self, batch: tuple[torch.Tensor, torch.Tensor]) -> float:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model.train()
        inputs, targets = batch
        inputs = inputs.to(self.device)
        targets = targets.to(self.device)
        outputs = self.model(inputs)
        loss = torch.nn.functional.cross_entropy(None, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return float(loss.detach().cpu().item())

    def xǁSimpleTrainerǁstep__mutmut_15(self, batch: tuple[torch.Tensor, torch.Tensor]) -> float:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model.train()
        inputs, targets = batch
        inputs = inputs.to(self.device)
        targets = targets.to(self.device)
        outputs = self.model(inputs)
        loss = torch.nn.functional.cross_entropy(outputs, None)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return float(loss.detach().cpu().item())

    def xǁSimpleTrainerǁstep__mutmut_16(self, batch: tuple[torch.Tensor, torch.Tensor]) -> float:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model.train()
        inputs, targets = batch
        inputs = inputs.to(self.device)
        targets = targets.to(self.device)
        outputs = self.model(inputs)
        loss = torch.nn.functional.cross_entropy(targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return float(loss.detach().cpu().item())

    def xǁSimpleTrainerǁstep__mutmut_17(self, batch: tuple[torch.Tensor, torch.Tensor]) -> float:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model.train()
        inputs, targets = batch
        inputs = inputs.to(self.device)
        targets = targets.to(self.device)
        outputs = self.model(inputs)
        loss = torch.nn.functional.cross_entropy(outputs, )
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return float(loss.detach().cpu().item())

    def xǁSimpleTrainerǁstep__mutmut_18(self, batch: tuple[torch.Tensor, torch.Tensor]) -> float:
        if torch is None:
            raise RuntimeError("torch is required for SimpleTrainer")
        self.model.train()
        inputs, targets = batch
        inputs = inputs.to(self.device)
        targets = targets.to(self.device)
        outputs = self.model(inputs)
        loss = torch.nn.functional.cross_entropy(outputs, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return float(None)
    
    xǁSimpleTrainerǁstep__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSimpleTrainerǁstep__mutmut_1': xǁSimpleTrainerǁstep__mutmut_1, 
        'xǁSimpleTrainerǁstep__mutmut_2': xǁSimpleTrainerǁstep__mutmut_2, 
        'xǁSimpleTrainerǁstep__mutmut_3': xǁSimpleTrainerǁstep__mutmut_3, 
        'xǁSimpleTrainerǁstep__mutmut_4': xǁSimpleTrainerǁstep__mutmut_4, 
        'xǁSimpleTrainerǁstep__mutmut_5': xǁSimpleTrainerǁstep__mutmut_5, 
        'xǁSimpleTrainerǁstep__mutmut_6': xǁSimpleTrainerǁstep__mutmut_6, 
        'xǁSimpleTrainerǁstep__mutmut_7': xǁSimpleTrainerǁstep__mutmut_7, 
        'xǁSimpleTrainerǁstep__mutmut_8': xǁSimpleTrainerǁstep__mutmut_8, 
        'xǁSimpleTrainerǁstep__mutmut_9': xǁSimpleTrainerǁstep__mutmut_9, 
        'xǁSimpleTrainerǁstep__mutmut_10': xǁSimpleTrainerǁstep__mutmut_10, 
        'xǁSimpleTrainerǁstep__mutmut_11': xǁSimpleTrainerǁstep__mutmut_11, 
        'xǁSimpleTrainerǁstep__mutmut_12': xǁSimpleTrainerǁstep__mutmut_12, 
        'xǁSimpleTrainerǁstep__mutmut_13': xǁSimpleTrainerǁstep__mutmut_13, 
        'xǁSimpleTrainerǁstep__mutmut_14': xǁSimpleTrainerǁstep__mutmut_14, 
        'xǁSimpleTrainerǁstep__mutmut_15': xǁSimpleTrainerǁstep__mutmut_15, 
        'xǁSimpleTrainerǁstep__mutmut_16': xǁSimpleTrainerǁstep__mutmut_16, 
        'xǁSimpleTrainerǁstep__mutmut_17': xǁSimpleTrainerǁstep__mutmut_17, 
        'xǁSimpleTrainerǁstep__mutmut_18': xǁSimpleTrainerǁstep__mutmut_18
    }
    
    def step(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSimpleTrainerǁstep__mutmut_orig"), object.__getattribute__(self, "xǁSimpleTrainerǁstep__mutmut_mutants"), args, kwargs, self)
        return result 
    
    step.__signature__ = _mutmut_signature(xǁSimpleTrainerǁstep__mutmut_orig)
    xǁSimpleTrainerǁstep__mutmut_orig.__name__ = 'xǁSimpleTrainerǁstep'

    def xǁSimpleTrainerǁsave_if_better__mutmut_orig(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_1(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None and self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_2(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is not None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_3(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is not None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_4(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = None
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_5(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(None)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_6(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_7(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" or metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_8(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode != "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_9(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "XXminXX" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_10(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "MIN" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_11(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric > self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_12(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" or metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_13(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode != "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_14(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "XXmaxXX" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_15(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "MAX" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_16(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric < self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_17(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            None,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_18(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            None,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_19(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=None,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_20(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=None,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_21(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=None,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_22(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=None,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_23(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=None,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_24(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra=None,
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_25(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_26(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_27(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_28(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_29(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_30(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_31(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            extra={"monitor": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_32(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_33(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"XXmonitorXX": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_34(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"MONITOR": self.monitor},
        )
        self._best_metric = metric

    def xǁSimpleTrainerǁsave_if_better__mutmut_35(self, epoch: int, val_metric: float) -> None:
        """Persist a checkpoint when the monitored metric improves."""

        if torch is None or self.checkpoint_dir is None:
            return
        metric = float(val_metric)
        if self._best_metric is not None:
            if self.mode == "min" and metric >= self._best_metric:
                return
            if self.mode == "max" and metric <= self._best_metric:
                return
        from .checkpointing import save_checkpoint

        save_checkpoint(
            self.model,
            self.optimizer,
            epoch=epoch,
            val_metric=metric,
            out_dir=self.checkpoint_dir,
            mode=self.mode,
            keep_best_k=self.keep_best_k,
            extra={"monitor": self.monitor},
        )
        self._best_metric = None
    
    xǁSimpleTrainerǁsave_if_better__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSimpleTrainerǁsave_if_better__mutmut_1': xǁSimpleTrainerǁsave_if_better__mutmut_1, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_2': xǁSimpleTrainerǁsave_if_better__mutmut_2, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_3': xǁSimpleTrainerǁsave_if_better__mutmut_3, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_4': xǁSimpleTrainerǁsave_if_better__mutmut_4, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_5': xǁSimpleTrainerǁsave_if_better__mutmut_5, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_6': xǁSimpleTrainerǁsave_if_better__mutmut_6, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_7': xǁSimpleTrainerǁsave_if_better__mutmut_7, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_8': xǁSimpleTrainerǁsave_if_better__mutmut_8, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_9': xǁSimpleTrainerǁsave_if_better__mutmut_9, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_10': xǁSimpleTrainerǁsave_if_better__mutmut_10, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_11': xǁSimpleTrainerǁsave_if_better__mutmut_11, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_12': xǁSimpleTrainerǁsave_if_better__mutmut_12, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_13': xǁSimpleTrainerǁsave_if_better__mutmut_13, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_14': xǁSimpleTrainerǁsave_if_better__mutmut_14, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_15': xǁSimpleTrainerǁsave_if_better__mutmut_15, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_16': xǁSimpleTrainerǁsave_if_better__mutmut_16, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_17': xǁSimpleTrainerǁsave_if_better__mutmut_17, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_18': xǁSimpleTrainerǁsave_if_better__mutmut_18, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_19': xǁSimpleTrainerǁsave_if_better__mutmut_19, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_20': xǁSimpleTrainerǁsave_if_better__mutmut_20, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_21': xǁSimpleTrainerǁsave_if_better__mutmut_21, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_22': xǁSimpleTrainerǁsave_if_better__mutmut_22, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_23': xǁSimpleTrainerǁsave_if_better__mutmut_23, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_24': xǁSimpleTrainerǁsave_if_better__mutmut_24, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_25': xǁSimpleTrainerǁsave_if_better__mutmut_25, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_26': xǁSimpleTrainerǁsave_if_better__mutmut_26, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_27': xǁSimpleTrainerǁsave_if_better__mutmut_27, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_28': xǁSimpleTrainerǁsave_if_better__mutmut_28, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_29': xǁSimpleTrainerǁsave_if_better__mutmut_29, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_30': xǁSimpleTrainerǁsave_if_better__mutmut_30, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_31': xǁSimpleTrainerǁsave_if_better__mutmut_31, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_32': xǁSimpleTrainerǁsave_if_better__mutmut_32, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_33': xǁSimpleTrainerǁsave_if_better__mutmut_33, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_34': xǁSimpleTrainerǁsave_if_better__mutmut_34, 
        'xǁSimpleTrainerǁsave_if_better__mutmut_35': xǁSimpleTrainerǁsave_if_better__mutmut_35
    }
    
    def save_if_better(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSimpleTrainerǁsave_if_better__mutmut_orig"), object.__getattribute__(self, "xǁSimpleTrainerǁsave_if_better__mutmut_mutants"), args, kwargs, self)
        return result 
    
    save_if_better.__signature__ = _mutmut_signature(xǁSimpleTrainerǁsave_if_better__mutmut_orig)
    xǁSimpleTrainerǁsave_if_better__mutmut_orig.__name__ = 'xǁSimpleTrainerǁsave_if_better'
