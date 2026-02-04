"""Utility datasets and data loader helpers for Codex smoke tests."""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, cast

from utils.error_logging import append_error

if TYPE_CHECKING:  # pragma: no cover - imported for typing only
    from torch.utils.data import DataLoader as TorchDataLoaderType
    from torch.utils.data import Dataset as TorchDatasetType
    from torch.utils.data import (
        Subset,
    )
else:  # pragma: no cover - runtime fallbacks when torch is unavailable
    TorchDataLoaderType = Any
    TorchDatasetType = Any
    Subset = Any
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


class BatchTokenizer(Protocol):
    """Callable producing tokeniser batches with arbitrary keyword arguments."""

    def __call__(
        self,
        texts: Sequence[str],
        /,
        *args: Any,
        **kwargs: Any,
    ) -> dict[str, Any]: ...


torch: Any
try:  # pragma: no cover - optional dependency guard
    import torch as _torch_mod
except Exception:  # pragma: no cover - allow repository usage without torch
    torch = None
else:
    torch = _torch_mod

try:  # pragma: no cover - guard for environments without torch data utilities
    from torch.utils.data import DataLoader as TorchDataLoader
    from torch.utils.data import Dataset as TorchDataset
    from torch.utils.data import TensorDataset as TorchTensorDataset
    from torch.utils.data import random_split as torch_random_split
except Exception:  # pragma: no cover - provide graceful degradation
    TorchDataLoader = cast(Any, None)
    TorchDataset = cast(Any, None)
    TorchTensorDataset = cast(Any, None)
    torch_random_split = cast(Any, None)

BaseDataset: type[Any]
if TorchDataset is not None:
    BaseDataset = TorchDataset
else:

    class _FallbackDataset:  # pragma: no cover - simple duck-typed fallback
        pass

    BaseDataset = _FallbackDataset

if TYPE_CHECKING:
    BaseDataset = TorchDatasetType


@dataclass(slots=True)
class DataConfig:
    """Configuration describing how to prepare data loaders."""

    dataset_path: str
    validation_path: str | None = None
    batch_size: int = 8
    split_ratio: Sequence[float] = (0.8, 0.2)
    shuffle: bool = True
    max_length: int = 128
    seed: int = 42
    num_workers: int = 0


@dataclass(slots=True)
class DataLoaderConfig:
    """User-facing config for text classification helpers."""

    file_path: str
    batch_size: int = 8
    max_length: int = 128
    validation_split: float = 0.2
    seed: int = 42

    def to_data_config(self) -> DataConfig:
        if not 0 <= float(self.validation_split) < 1:
            raise ValueError("validation_split must be in [0, 1)")
        split_ratio = (1 - float(self.validation_split), float(self.validation_split))
        return DataConfig(
            dataset_path=self.file_path,
            validation_path=None,
            batch_size=int(self.batch_size),
            split_ratio=split_ratio,
            shuffle=True,
            max_length=int(self.max_length),
            seed=int(self.seed),
            num_workers=0,
        )


class TextClassificationDataset(BaseDataset):
    """Simple TSV loader producing ``(text, label)`` tuples."""

    def xǁTextClassificationDatasetǁ__init____mutmut_orig(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_1(self, file_path: str) -> None:
        self.file_path = None
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_2(self, file_path: str) -> None:
        self.file_path = Path(None)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_3(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = None
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_4(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open(None, encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_5(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding=None) as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_6(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open(encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_7(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", ) as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_8(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("XXrXX", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_9(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("R", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_10(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="XXutf-8XX") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_11(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="UTF-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_12(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(None, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_13(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=None):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_14(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_15(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, ):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_16(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=2):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_17(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = None
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_18(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_19(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        break
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_20(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = None
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_21(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split(None, maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_22(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=None)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_23(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split(maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_24(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", )
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_25(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.rsplit("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_26(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("XX\tXX", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_27(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=2)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_28(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append(None)
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_29(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(None)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_30(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(None)
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_31(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            None,
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_32(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            None,
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_33(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            None,
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_34(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            None,
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_35(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_36(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_37(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_38(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_39(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "XX3.5XX",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_40(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "XXdataset parseXX",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_41(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "DATASET PARSE",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_42(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(None),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_43(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(None)
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_44(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error(None, "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_45(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", None, str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_46(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", None, str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_47(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), None)
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_48(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_49(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_50(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_51(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), )
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_52(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("XX3.5XX", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_53(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "XXdataset loadXX", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_54(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "DATASET LOAD", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_55(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(None), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_56(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(None))
            raise
        if not self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_57(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if self.samples:
            raise ValueError(f"dataset at {self.file_path} contains no usable rows")

    def xǁTextClassificationDatasetǁ__init____mutmut_58(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.samples: list[tuple[str, int]] = []
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        text, label = line.split("\t", maxsplit=1)
                        self.samples.append((text, int(label)))
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        append_error(
                            "3.5",
                            "dataset parse",
                            str(exc),
                            f"path={self.file_path} line={line_number}",
                        )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            append_error("3.5", "dataset load", str(exc), str(self.file_path))
            raise
        if not self.samples:
            raise ValueError(None)
    
    xǁTextClassificationDatasetǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTextClassificationDatasetǁ__init____mutmut_1': xǁTextClassificationDatasetǁ__init____mutmut_1, 
        'xǁTextClassificationDatasetǁ__init____mutmut_2': xǁTextClassificationDatasetǁ__init____mutmut_2, 
        'xǁTextClassificationDatasetǁ__init____mutmut_3': xǁTextClassificationDatasetǁ__init____mutmut_3, 
        'xǁTextClassificationDatasetǁ__init____mutmut_4': xǁTextClassificationDatasetǁ__init____mutmut_4, 
        'xǁTextClassificationDatasetǁ__init____mutmut_5': xǁTextClassificationDatasetǁ__init____mutmut_5, 
        'xǁTextClassificationDatasetǁ__init____mutmut_6': xǁTextClassificationDatasetǁ__init____mutmut_6, 
        'xǁTextClassificationDatasetǁ__init____mutmut_7': xǁTextClassificationDatasetǁ__init____mutmut_7, 
        'xǁTextClassificationDatasetǁ__init____mutmut_8': xǁTextClassificationDatasetǁ__init____mutmut_8, 
        'xǁTextClassificationDatasetǁ__init____mutmut_9': xǁTextClassificationDatasetǁ__init____mutmut_9, 
        'xǁTextClassificationDatasetǁ__init____mutmut_10': xǁTextClassificationDatasetǁ__init____mutmut_10, 
        'xǁTextClassificationDatasetǁ__init____mutmut_11': xǁTextClassificationDatasetǁ__init____mutmut_11, 
        'xǁTextClassificationDatasetǁ__init____mutmut_12': xǁTextClassificationDatasetǁ__init____mutmut_12, 
        'xǁTextClassificationDatasetǁ__init____mutmut_13': xǁTextClassificationDatasetǁ__init____mutmut_13, 
        'xǁTextClassificationDatasetǁ__init____mutmut_14': xǁTextClassificationDatasetǁ__init____mutmut_14, 
        'xǁTextClassificationDatasetǁ__init____mutmut_15': xǁTextClassificationDatasetǁ__init____mutmut_15, 
        'xǁTextClassificationDatasetǁ__init____mutmut_16': xǁTextClassificationDatasetǁ__init____mutmut_16, 
        'xǁTextClassificationDatasetǁ__init____mutmut_17': xǁTextClassificationDatasetǁ__init____mutmut_17, 
        'xǁTextClassificationDatasetǁ__init____mutmut_18': xǁTextClassificationDatasetǁ__init____mutmut_18, 
        'xǁTextClassificationDatasetǁ__init____mutmut_19': xǁTextClassificationDatasetǁ__init____mutmut_19, 
        'xǁTextClassificationDatasetǁ__init____mutmut_20': xǁTextClassificationDatasetǁ__init____mutmut_20, 
        'xǁTextClassificationDatasetǁ__init____mutmut_21': xǁTextClassificationDatasetǁ__init____mutmut_21, 
        'xǁTextClassificationDatasetǁ__init____mutmut_22': xǁTextClassificationDatasetǁ__init____mutmut_22, 
        'xǁTextClassificationDatasetǁ__init____mutmut_23': xǁTextClassificationDatasetǁ__init____mutmut_23, 
        'xǁTextClassificationDatasetǁ__init____mutmut_24': xǁTextClassificationDatasetǁ__init____mutmut_24, 
        'xǁTextClassificationDatasetǁ__init____mutmut_25': xǁTextClassificationDatasetǁ__init____mutmut_25, 
        'xǁTextClassificationDatasetǁ__init____mutmut_26': xǁTextClassificationDatasetǁ__init____mutmut_26, 
        'xǁTextClassificationDatasetǁ__init____mutmut_27': xǁTextClassificationDatasetǁ__init____mutmut_27, 
        'xǁTextClassificationDatasetǁ__init____mutmut_28': xǁTextClassificationDatasetǁ__init____mutmut_28, 
        'xǁTextClassificationDatasetǁ__init____mutmut_29': xǁTextClassificationDatasetǁ__init____mutmut_29, 
        'xǁTextClassificationDatasetǁ__init____mutmut_30': xǁTextClassificationDatasetǁ__init____mutmut_30, 
        'xǁTextClassificationDatasetǁ__init____mutmut_31': xǁTextClassificationDatasetǁ__init____mutmut_31, 
        'xǁTextClassificationDatasetǁ__init____mutmut_32': xǁTextClassificationDatasetǁ__init____mutmut_32, 
        'xǁTextClassificationDatasetǁ__init____mutmut_33': xǁTextClassificationDatasetǁ__init____mutmut_33, 
        'xǁTextClassificationDatasetǁ__init____mutmut_34': xǁTextClassificationDatasetǁ__init____mutmut_34, 
        'xǁTextClassificationDatasetǁ__init____mutmut_35': xǁTextClassificationDatasetǁ__init____mutmut_35, 
        'xǁTextClassificationDatasetǁ__init____mutmut_36': xǁTextClassificationDatasetǁ__init____mutmut_36, 
        'xǁTextClassificationDatasetǁ__init____mutmut_37': xǁTextClassificationDatasetǁ__init____mutmut_37, 
        'xǁTextClassificationDatasetǁ__init____mutmut_38': xǁTextClassificationDatasetǁ__init____mutmut_38, 
        'xǁTextClassificationDatasetǁ__init____mutmut_39': xǁTextClassificationDatasetǁ__init____mutmut_39, 
        'xǁTextClassificationDatasetǁ__init____mutmut_40': xǁTextClassificationDatasetǁ__init____mutmut_40, 
        'xǁTextClassificationDatasetǁ__init____mutmut_41': xǁTextClassificationDatasetǁ__init____mutmut_41, 
        'xǁTextClassificationDatasetǁ__init____mutmut_42': xǁTextClassificationDatasetǁ__init____mutmut_42, 
        'xǁTextClassificationDatasetǁ__init____mutmut_43': xǁTextClassificationDatasetǁ__init____mutmut_43, 
        'xǁTextClassificationDatasetǁ__init____mutmut_44': xǁTextClassificationDatasetǁ__init____mutmut_44, 
        'xǁTextClassificationDatasetǁ__init____mutmut_45': xǁTextClassificationDatasetǁ__init____mutmut_45, 
        'xǁTextClassificationDatasetǁ__init____mutmut_46': xǁTextClassificationDatasetǁ__init____mutmut_46, 
        'xǁTextClassificationDatasetǁ__init____mutmut_47': xǁTextClassificationDatasetǁ__init____mutmut_47, 
        'xǁTextClassificationDatasetǁ__init____mutmut_48': xǁTextClassificationDatasetǁ__init____mutmut_48, 
        'xǁTextClassificationDatasetǁ__init____mutmut_49': xǁTextClassificationDatasetǁ__init____mutmut_49, 
        'xǁTextClassificationDatasetǁ__init____mutmut_50': xǁTextClassificationDatasetǁ__init____mutmut_50, 
        'xǁTextClassificationDatasetǁ__init____mutmut_51': xǁTextClassificationDatasetǁ__init____mutmut_51, 
        'xǁTextClassificationDatasetǁ__init____mutmut_52': xǁTextClassificationDatasetǁ__init____mutmut_52, 
        'xǁTextClassificationDatasetǁ__init____mutmut_53': xǁTextClassificationDatasetǁ__init____mutmut_53, 
        'xǁTextClassificationDatasetǁ__init____mutmut_54': xǁTextClassificationDatasetǁ__init____mutmut_54, 
        'xǁTextClassificationDatasetǁ__init____mutmut_55': xǁTextClassificationDatasetǁ__init____mutmut_55, 
        'xǁTextClassificationDatasetǁ__init____mutmut_56': xǁTextClassificationDatasetǁ__init____mutmut_56, 
        'xǁTextClassificationDatasetǁ__init____mutmut_57': xǁTextClassificationDatasetǁ__init____mutmut_57, 
        'xǁTextClassificationDatasetǁ__init____mutmut_58': xǁTextClassificationDatasetǁ__init____mutmut_58
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTextClassificationDatasetǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁTextClassificationDatasetǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁTextClassificationDatasetǁ__init____mutmut_orig)
    xǁTextClassificationDatasetǁ__init____mutmut_orig.__name__ = 'xǁTextClassificationDatasetǁ__init__'

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.samples)

    def __getitem__(self, idx: int) -> tuple[str, int]:  # pragma: no cover - trivial
        return self.samples[idx]


def x__collate_text_batch__mutmut_orig(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_1(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is not None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_2(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError(None)
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_3(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("XXtorch is required for batch collationXX")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_4(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("TORCH IS REQUIRED FOR BATCH COLLATION")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_5(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = None
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_6(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=None)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_7(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_8(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, )
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_9(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=True)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_10(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = None
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_11(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            None,
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_12(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding=None,
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_13(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=None,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_14(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=None,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_15(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors=None,
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_16(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_17(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_18(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_19(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_20(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_21(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(None),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_22(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="XXmax_lengthXX",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_23(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="MAX_LENGTH",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_24(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=False,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_25(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="XXptXX",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_26(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="PT",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_27(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(None)
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_28(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error(None, "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_29(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", None, str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_30(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", None, f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_31(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), None)
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_32(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_33(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_34(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_35(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), )
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_36(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("XX3.5XX", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_37(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "XXtokenize batchXX", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_38(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "TOKENIZE BATCH", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_39(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(None), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_40(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = None
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_41(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get(None)
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_42(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("XXinput_idsXX")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_43(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("INPUT_IDS")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_44(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is not None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_45(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError(None)
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_46(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("XXtokenizer output is missing 'input_ids'XX")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_47(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("TOKENIZER OUTPUT IS MISSING 'INPUT_IDS'")
    return input_ids, torch.tensor(labels, dtype=torch.long)


def x__collate_text_batch__mutmut_48(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(None, dtype=torch.long)


def x__collate_text_batch__mutmut_49(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, dtype=None)


def x__collate_text_batch__mutmut_50(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(dtype=torch.long)


def x__collate_text_batch__mutmut_51(
    tokenizer: BatchTokenizer,
    batch: Iterable[tuple[str, int]],
    *,
    max_length: int,
) -> tuple[Any, Any]:
    if torch is None:  # pragma: no cover - enforced by build_dataloaders guard
        raise RuntimeError("torch is required for batch collation")
    texts, labels = zip(*batch, strict=False)
    try:
        encodings = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        append_error("3.5", "tokenize batch", str(exc), f"texts={len(texts)}")
        raise
    input_ids = encodings.get("input_ids")
    if input_ids is None:
        raise KeyError("tokenizer output is missing 'input_ids'")
    return input_ids, torch.tensor(labels, )

x__collate_text_batch__mutmut_mutants : ClassVar[MutantDict] = {
'x__collate_text_batch__mutmut_1': x__collate_text_batch__mutmut_1, 
    'x__collate_text_batch__mutmut_2': x__collate_text_batch__mutmut_2, 
    'x__collate_text_batch__mutmut_3': x__collate_text_batch__mutmut_3, 
    'x__collate_text_batch__mutmut_4': x__collate_text_batch__mutmut_4, 
    'x__collate_text_batch__mutmut_5': x__collate_text_batch__mutmut_5, 
    'x__collate_text_batch__mutmut_6': x__collate_text_batch__mutmut_6, 
    'x__collate_text_batch__mutmut_7': x__collate_text_batch__mutmut_7, 
    'x__collate_text_batch__mutmut_8': x__collate_text_batch__mutmut_8, 
    'x__collate_text_batch__mutmut_9': x__collate_text_batch__mutmut_9, 
    'x__collate_text_batch__mutmut_10': x__collate_text_batch__mutmut_10, 
    'x__collate_text_batch__mutmut_11': x__collate_text_batch__mutmut_11, 
    'x__collate_text_batch__mutmut_12': x__collate_text_batch__mutmut_12, 
    'x__collate_text_batch__mutmut_13': x__collate_text_batch__mutmut_13, 
    'x__collate_text_batch__mutmut_14': x__collate_text_batch__mutmut_14, 
    'x__collate_text_batch__mutmut_15': x__collate_text_batch__mutmut_15, 
    'x__collate_text_batch__mutmut_16': x__collate_text_batch__mutmut_16, 
    'x__collate_text_batch__mutmut_17': x__collate_text_batch__mutmut_17, 
    'x__collate_text_batch__mutmut_18': x__collate_text_batch__mutmut_18, 
    'x__collate_text_batch__mutmut_19': x__collate_text_batch__mutmut_19, 
    'x__collate_text_batch__mutmut_20': x__collate_text_batch__mutmut_20, 
    'x__collate_text_batch__mutmut_21': x__collate_text_batch__mutmut_21, 
    'x__collate_text_batch__mutmut_22': x__collate_text_batch__mutmut_22, 
    'x__collate_text_batch__mutmut_23': x__collate_text_batch__mutmut_23, 
    'x__collate_text_batch__mutmut_24': x__collate_text_batch__mutmut_24, 
    'x__collate_text_batch__mutmut_25': x__collate_text_batch__mutmut_25, 
    'x__collate_text_batch__mutmut_26': x__collate_text_batch__mutmut_26, 
    'x__collate_text_batch__mutmut_27': x__collate_text_batch__mutmut_27, 
    'x__collate_text_batch__mutmut_28': x__collate_text_batch__mutmut_28, 
    'x__collate_text_batch__mutmut_29': x__collate_text_batch__mutmut_29, 
    'x__collate_text_batch__mutmut_30': x__collate_text_batch__mutmut_30, 
    'x__collate_text_batch__mutmut_31': x__collate_text_batch__mutmut_31, 
    'x__collate_text_batch__mutmut_32': x__collate_text_batch__mutmut_32, 
    'x__collate_text_batch__mutmut_33': x__collate_text_batch__mutmut_33, 
    'x__collate_text_batch__mutmut_34': x__collate_text_batch__mutmut_34, 
    'x__collate_text_batch__mutmut_35': x__collate_text_batch__mutmut_35, 
    'x__collate_text_batch__mutmut_36': x__collate_text_batch__mutmut_36, 
    'x__collate_text_batch__mutmut_37': x__collate_text_batch__mutmut_37, 
    'x__collate_text_batch__mutmut_38': x__collate_text_batch__mutmut_38, 
    'x__collate_text_batch__mutmut_39': x__collate_text_batch__mutmut_39, 
    'x__collate_text_batch__mutmut_40': x__collate_text_batch__mutmut_40, 
    'x__collate_text_batch__mutmut_41': x__collate_text_batch__mutmut_41, 
    'x__collate_text_batch__mutmut_42': x__collate_text_batch__mutmut_42, 
    'x__collate_text_batch__mutmut_43': x__collate_text_batch__mutmut_43, 
    'x__collate_text_batch__mutmut_44': x__collate_text_batch__mutmut_44, 
    'x__collate_text_batch__mutmut_45': x__collate_text_batch__mutmut_45, 
    'x__collate_text_batch__mutmut_46': x__collate_text_batch__mutmut_46, 
    'x__collate_text_batch__mutmut_47': x__collate_text_batch__mutmut_47, 
    'x__collate_text_batch__mutmut_48': x__collate_text_batch__mutmut_48, 
    'x__collate_text_batch__mutmut_49': x__collate_text_batch__mutmut_49, 
    'x__collate_text_batch__mutmut_50': x__collate_text_batch__mutmut_50, 
    'x__collate_text_batch__mutmut_51': x__collate_text_batch__mutmut_51
}

def _collate_text_batch(*args, **kwargs):
    result = _mutmut_trampoline(x__collate_text_batch__mutmut_orig, x__collate_text_batch__mutmut_mutants, args, kwargs)
    return result 

_collate_text_batch.__signature__ = _mutmut_signature(x__collate_text_batch__mutmut_orig)
x__collate_text_batch__mutmut_orig.__name__ = 'x__collate_text_batch'


def x__coerce_tokenizer__mutmut_orig(tokenizer: Any) -> BatchTokenizer:
    batch_encode = getattr(tokenizer, "batch_encode_plus", None)
    if batch_encode is None and callable(tokenizer):
        batch_encode = tokenizer
    if batch_encode is None:
        message = "tokenizer must provide 'batch_encode_plus' or be callable"
        raise AttributeError(message)
    return cast(BatchTokenizer, batch_encode)


def x__coerce_tokenizer__mutmut_1(tokenizer: Any) -> BatchTokenizer:
    batch_encode = None
    if batch_encode is None and callable(tokenizer):
        batch_encode = tokenizer
    if batch_encode is None:
        message = "tokenizer must provide 'batch_encode_plus' or be callable"
        raise AttributeError(message)
    return cast(BatchTokenizer, batch_encode)


def x__coerce_tokenizer__mutmut_2(tokenizer: Any) -> BatchTokenizer:
    batch_encode = getattr(None, "batch_encode_plus", None)
    if batch_encode is None and callable(tokenizer):
        batch_encode = tokenizer
    if batch_encode is None:
        message = "tokenizer must provide 'batch_encode_plus' or be callable"
        raise AttributeError(message)
    return cast(BatchTokenizer, batch_encode)


def x__coerce_tokenizer__mutmut_3(tokenizer: Any) -> BatchTokenizer:
    batch_encode = getattr(tokenizer, None, None)
    if batch_encode is None and callable(tokenizer):
        batch_encode = tokenizer
    if batch_encode is None:
        message = "tokenizer must provide 'batch_encode_plus' or be callable"
        raise AttributeError(message)
    return cast(BatchTokenizer, batch_encode)


def x__coerce_tokenizer__mutmut_4(tokenizer: Any) -> BatchTokenizer:
    batch_encode = getattr("batch_encode_plus", None)
    if batch_encode is None and callable(tokenizer):
        batch_encode = tokenizer
    if batch_encode is None:
        message = "tokenizer must provide 'batch_encode_plus' or be callable"
        raise AttributeError(message)
    return cast(BatchTokenizer, batch_encode)


def x__coerce_tokenizer__mutmut_5(tokenizer: Any) -> BatchTokenizer:
    batch_encode = getattr(tokenizer, None)
    if batch_encode is None and callable(tokenizer):
        batch_encode = tokenizer
    if batch_encode is None:
        message = "tokenizer must provide 'batch_encode_plus' or be callable"
        raise AttributeError(message)
    return cast(BatchTokenizer, batch_encode)


def x__coerce_tokenizer__mutmut_6(tokenizer: Any) -> BatchTokenizer:
    batch_encode = getattr(tokenizer, "batch_encode_plus", )
    if batch_encode is None and callable(tokenizer):
        batch_encode = tokenizer
    if batch_encode is None:
        message = "tokenizer must provide 'batch_encode_plus' or be callable"
        raise AttributeError(message)
    return cast(BatchTokenizer, batch_encode)


def x__coerce_tokenizer__mutmut_7(tokenizer: Any) -> BatchTokenizer:
    batch_encode = getattr(tokenizer, "XXbatch_encode_plusXX", None)
    if batch_encode is None and callable(tokenizer):
        batch_encode = tokenizer
    if batch_encode is None:
        message = "tokenizer must provide 'batch_encode_plus' or be callable"
        raise AttributeError(message)
    return cast(BatchTokenizer, batch_encode)


def x__coerce_tokenizer__mutmut_8(tokenizer: Any) -> BatchTokenizer:
    batch_encode = getattr(tokenizer, "BATCH_ENCODE_PLUS", None)
    if batch_encode is None and callable(tokenizer):
        batch_encode = tokenizer
    if batch_encode is None:
        message = "tokenizer must provide 'batch_encode_plus' or be callable"
        raise AttributeError(message)
    return cast(BatchTokenizer, batch_encode)


def x__coerce_tokenizer__mutmut_9(tokenizer: Any) -> BatchTokenizer:
    batch_encode = getattr(tokenizer, "batch_encode_plus", None)
    if batch_encode is None or callable(tokenizer):
        batch_encode = tokenizer
    if batch_encode is None:
        message = "tokenizer must provide 'batch_encode_plus' or be callable"
        raise AttributeError(message)
    return cast(BatchTokenizer, batch_encode)


def x__coerce_tokenizer__mutmut_10(tokenizer: Any) -> BatchTokenizer:
    batch_encode = getattr(tokenizer, "batch_encode_plus", None)
    if batch_encode is not None and callable(tokenizer):
        batch_encode = tokenizer
    if batch_encode is None:
        message = "tokenizer must provide 'batch_encode_plus' or be callable"
        raise AttributeError(message)
    return cast(BatchTokenizer, batch_encode)


def x__coerce_tokenizer__mutmut_11(tokenizer: Any) -> BatchTokenizer:
    batch_encode = getattr(tokenizer, "batch_encode_plus", None)
    if batch_encode is None and callable(None):
        batch_encode = tokenizer
    if batch_encode is None:
        message = "tokenizer must provide 'batch_encode_plus' or be callable"
        raise AttributeError(message)
    return cast(BatchTokenizer, batch_encode)


def x__coerce_tokenizer__mutmut_12(tokenizer: Any) -> BatchTokenizer:
    batch_encode = getattr(tokenizer, "batch_encode_plus", None)
    if batch_encode is None and callable(tokenizer):
        batch_encode = None
    if batch_encode is None:
        message = "tokenizer must provide 'batch_encode_plus' or be callable"
        raise AttributeError(message)
    return cast(BatchTokenizer, batch_encode)


def x__coerce_tokenizer__mutmut_13(tokenizer: Any) -> BatchTokenizer:
    batch_encode = getattr(tokenizer, "batch_encode_plus", None)
    if batch_encode is None and callable(tokenizer):
        batch_encode = tokenizer
    if batch_encode is not None:
        message = "tokenizer must provide 'batch_encode_plus' or be callable"
        raise AttributeError(message)
    return cast(BatchTokenizer, batch_encode)


def x__coerce_tokenizer__mutmut_14(tokenizer: Any) -> BatchTokenizer:
    batch_encode = getattr(tokenizer, "batch_encode_plus", None)
    if batch_encode is None and callable(tokenizer):
        batch_encode = tokenizer
    if batch_encode is None:
        message = None
        raise AttributeError(message)
    return cast(BatchTokenizer, batch_encode)


def x__coerce_tokenizer__mutmut_15(tokenizer: Any) -> BatchTokenizer:
    batch_encode = getattr(tokenizer, "batch_encode_plus", None)
    if batch_encode is None and callable(tokenizer):
        batch_encode = tokenizer
    if batch_encode is None:
        message = "XXtokenizer must provide 'batch_encode_plus' or be callableXX"
        raise AttributeError(message)
    return cast(BatchTokenizer, batch_encode)


def x__coerce_tokenizer__mutmut_16(tokenizer: Any) -> BatchTokenizer:
    batch_encode = getattr(tokenizer, "batch_encode_plus", None)
    if batch_encode is None and callable(tokenizer):
        batch_encode = tokenizer
    if batch_encode is None:
        message = "TOKENIZER MUST PROVIDE 'BATCH_ENCODE_PLUS' OR BE CALLABLE"
        raise AttributeError(message)
    return cast(BatchTokenizer, batch_encode)


def x__coerce_tokenizer__mutmut_17(tokenizer: Any) -> BatchTokenizer:
    batch_encode = getattr(tokenizer, "batch_encode_plus", None)
    if batch_encode is None and callable(tokenizer):
        batch_encode = tokenizer
    if batch_encode is None:
        message = "tokenizer must provide 'batch_encode_plus' or be callable"
        raise AttributeError(None)
    return cast(BatchTokenizer, batch_encode)


def x__coerce_tokenizer__mutmut_18(tokenizer: Any) -> BatchTokenizer:
    batch_encode = getattr(tokenizer, "batch_encode_plus", None)
    if batch_encode is None and callable(tokenizer):
        batch_encode = tokenizer
    if batch_encode is None:
        message = "tokenizer must provide 'batch_encode_plus' or be callable"
        raise AttributeError(message)
    return cast(None, batch_encode)


def x__coerce_tokenizer__mutmut_19(tokenizer: Any) -> BatchTokenizer:
    batch_encode = getattr(tokenizer, "batch_encode_plus", None)
    if batch_encode is None and callable(tokenizer):
        batch_encode = tokenizer
    if batch_encode is None:
        message = "tokenizer must provide 'batch_encode_plus' or be callable"
        raise AttributeError(message)
    return cast(BatchTokenizer, None)


def x__coerce_tokenizer__mutmut_20(tokenizer: Any) -> BatchTokenizer:
    batch_encode = getattr(tokenizer, "batch_encode_plus", None)
    if batch_encode is None and callable(tokenizer):
        batch_encode = tokenizer
    if batch_encode is None:
        message = "tokenizer must provide 'batch_encode_plus' or be callable"
        raise AttributeError(message)
    return cast(batch_encode)


def x__coerce_tokenizer__mutmut_21(tokenizer: Any) -> BatchTokenizer:
    batch_encode = getattr(tokenizer, "batch_encode_plus", None)
    if batch_encode is None and callable(tokenizer):
        batch_encode = tokenizer
    if batch_encode is None:
        message = "tokenizer must provide 'batch_encode_plus' or be callable"
        raise AttributeError(message)
    return cast(BatchTokenizer, )

x__coerce_tokenizer__mutmut_mutants : ClassVar[MutantDict] = {
'x__coerce_tokenizer__mutmut_1': x__coerce_tokenizer__mutmut_1, 
    'x__coerce_tokenizer__mutmut_2': x__coerce_tokenizer__mutmut_2, 
    'x__coerce_tokenizer__mutmut_3': x__coerce_tokenizer__mutmut_3, 
    'x__coerce_tokenizer__mutmut_4': x__coerce_tokenizer__mutmut_4, 
    'x__coerce_tokenizer__mutmut_5': x__coerce_tokenizer__mutmut_5, 
    'x__coerce_tokenizer__mutmut_6': x__coerce_tokenizer__mutmut_6, 
    'x__coerce_tokenizer__mutmut_7': x__coerce_tokenizer__mutmut_7, 
    'x__coerce_tokenizer__mutmut_8': x__coerce_tokenizer__mutmut_8, 
    'x__coerce_tokenizer__mutmut_9': x__coerce_tokenizer__mutmut_9, 
    'x__coerce_tokenizer__mutmut_10': x__coerce_tokenizer__mutmut_10, 
    'x__coerce_tokenizer__mutmut_11': x__coerce_tokenizer__mutmut_11, 
    'x__coerce_tokenizer__mutmut_12': x__coerce_tokenizer__mutmut_12, 
    'x__coerce_tokenizer__mutmut_13': x__coerce_tokenizer__mutmut_13, 
    'x__coerce_tokenizer__mutmut_14': x__coerce_tokenizer__mutmut_14, 
    'x__coerce_tokenizer__mutmut_15': x__coerce_tokenizer__mutmut_15, 
    'x__coerce_tokenizer__mutmut_16': x__coerce_tokenizer__mutmut_16, 
    'x__coerce_tokenizer__mutmut_17': x__coerce_tokenizer__mutmut_17, 
    'x__coerce_tokenizer__mutmut_18': x__coerce_tokenizer__mutmut_18, 
    'x__coerce_tokenizer__mutmut_19': x__coerce_tokenizer__mutmut_19, 
    'x__coerce_tokenizer__mutmut_20': x__coerce_tokenizer__mutmut_20, 
    'x__coerce_tokenizer__mutmut_21': x__coerce_tokenizer__mutmut_21
}

def _coerce_tokenizer(*args, **kwargs):
    result = _mutmut_trampoline(x__coerce_tokenizer__mutmut_orig, x__coerce_tokenizer__mutmut_mutants, args, kwargs)
    return result 

_coerce_tokenizer.__signature__ = _mutmut_signature(x__coerce_tokenizer__mutmut_orig)
x__coerce_tokenizer__mutmut_orig.__name__ = 'x__coerce_tokenizer'


def x__build_dataloaders_from_config__mutmut_orig(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_1(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None and TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_2(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is not None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_3(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is not None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_4(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = None
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_5(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "XXtorch and torch.utils.data are required to build dataloadersXX"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_6(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "TORCH AND TORCH.UTILS.DATA ARE REQUIRED TO BUILD DATALOADERS"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_7(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(None)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_8(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = None

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_9(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(None)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_10(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = None
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_11(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(None)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_12(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = None
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_13(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = None
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_14(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(None) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_15(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_16(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = None
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_17(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(None)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_18(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is not None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_19(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError(None)
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_20(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("XXtorch.utils.data.random_split is unavailableXX")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_21(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("TORCH.UTILS.DATA.RANDOM_SPLIT IS UNAVAILABLE")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_22(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = None
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_23(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(None)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_24(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) == 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_25(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 3:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_26(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError(None)
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_27(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("XXsplit_ratio must contain train and validation fractionsXX")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_28(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("SPLIT_RATIO MUST CONTAIN TRAIN AND VALIDATION FRACTIONS")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_29(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = None
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_30(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(None)
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_31(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) / split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_32(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[1])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_33(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = None
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_34(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(None, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_35(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, None)
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_36(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_37(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, )
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_38(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(2, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_39(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(None, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_40(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, None))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_41(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_42(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, ))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_43(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) + 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_44(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 2))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_45(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) < 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_46(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 2:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_47(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = None
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_48(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = None
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_49(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) + train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_50(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len != 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_51(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 1:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_52(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = None
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_53(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = ""
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_54(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = None
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_55(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(None)
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_56(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(None))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_57(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = None

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_58(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                None,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_59(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                None,
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_60(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=None,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_61(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_62(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_63(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_64(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(None, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_65(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, None, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_66(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=None)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_67(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_68(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_69(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, )

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_70(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = None
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_71(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        None,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_72(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=None,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_73(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=None,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_74(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=None,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_75(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=None,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_76(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_77(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_78(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_79(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_80(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_81(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is not None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_82(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = ""
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_83(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = None
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_84(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            None,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_85(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=None,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_86(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=None,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_87(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=None,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_88(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=None,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_89(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_90(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            shuffle=False,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_91(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_92(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            collate_fn=collate,
        )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_93(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
            )
    return train_loader, val_loader


def x__build_dataloaders_from_config__mutmut_94(
    tokenizer: Any,
    config: DataConfig,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders according to ``config``."""

    if torch is None or TorchDataLoader is None:
        message = "torch and torch.utils.data are required to build dataloaders"
        raise RuntimeError(message)

    batch_encode = _coerce_tokenizer(tokenizer)

    if config.validation_path:
        train_set = TextClassificationDataset(config.dataset_path)
        val_path = config.validation_path
        val_set: TorchDatasetType | None = (
            TextClassificationDataset(val_path) if val_path is not None else None
        )
    else:
        dataset = TextClassificationDataset(config.dataset_path)
        if torch_random_split is None:
            raise RuntimeError("torch.utils.data.random_split is unavailable")
        split = list(config.split_ratio)
        if len(split) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        train_len = round(len(dataset) * split[0])
        train_len = max(1, min(train_len, len(dataset) - 1))
        if len(dataset) <= 1:
            train_len = len(dataset)
        val_len = len(dataset) - train_len
        if val_len == 0:
            train_set = dataset
            val_set = None
        else:
            generator = torch.Generator().manual_seed(int(config.seed))
            train_set, val_set = torch_random_split(
                dataset,
                [train_len, val_len],
                generator=generator,
            )

    def collate(batch: Iterable[tuple[str, int]]) -> tuple[Any, Any]:
        return _collate_text_batch(batch_encode, batch, max_length=config.max_length)

    train_loader = TorchDataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=config.shuffle,
        num_workers=config.num_workers,
        collate_fn=collate,
    )
    val_loader: TorchDataLoaderType | None
    if val_set is None:
        val_loader = None
    else:
        val_loader = TorchDataLoader(
            val_set,
            batch_size=config.batch_size,
            shuffle=True,
            num_workers=config.num_workers,
            collate_fn=collate,
        )
    return train_loader, val_loader

x__build_dataloaders_from_config__mutmut_mutants : ClassVar[MutantDict] = {
'x__build_dataloaders_from_config__mutmut_1': x__build_dataloaders_from_config__mutmut_1, 
    'x__build_dataloaders_from_config__mutmut_2': x__build_dataloaders_from_config__mutmut_2, 
    'x__build_dataloaders_from_config__mutmut_3': x__build_dataloaders_from_config__mutmut_3, 
    'x__build_dataloaders_from_config__mutmut_4': x__build_dataloaders_from_config__mutmut_4, 
    'x__build_dataloaders_from_config__mutmut_5': x__build_dataloaders_from_config__mutmut_5, 
    'x__build_dataloaders_from_config__mutmut_6': x__build_dataloaders_from_config__mutmut_6, 
    'x__build_dataloaders_from_config__mutmut_7': x__build_dataloaders_from_config__mutmut_7, 
    'x__build_dataloaders_from_config__mutmut_8': x__build_dataloaders_from_config__mutmut_8, 
    'x__build_dataloaders_from_config__mutmut_9': x__build_dataloaders_from_config__mutmut_9, 
    'x__build_dataloaders_from_config__mutmut_10': x__build_dataloaders_from_config__mutmut_10, 
    'x__build_dataloaders_from_config__mutmut_11': x__build_dataloaders_from_config__mutmut_11, 
    'x__build_dataloaders_from_config__mutmut_12': x__build_dataloaders_from_config__mutmut_12, 
    'x__build_dataloaders_from_config__mutmut_13': x__build_dataloaders_from_config__mutmut_13, 
    'x__build_dataloaders_from_config__mutmut_14': x__build_dataloaders_from_config__mutmut_14, 
    'x__build_dataloaders_from_config__mutmut_15': x__build_dataloaders_from_config__mutmut_15, 
    'x__build_dataloaders_from_config__mutmut_16': x__build_dataloaders_from_config__mutmut_16, 
    'x__build_dataloaders_from_config__mutmut_17': x__build_dataloaders_from_config__mutmut_17, 
    'x__build_dataloaders_from_config__mutmut_18': x__build_dataloaders_from_config__mutmut_18, 
    'x__build_dataloaders_from_config__mutmut_19': x__build_dataloaders_from_config__mutmut_19, 
    'x__build_dataloaders_from_config__mutmut_20': x__build_dataloaders_from_config__mutmut_20, 
    'x__build_dataloaders_from_config__mutmut_21': x__build_dataloaders_from_config__mutmut_21, 
    'x__build_dataloaders_from_config__mutmut_22': x__build_dataloaders_from_config__mutmut_22, 
    'x__build_dataloaders_from_config__mutmut_23': x__build_dataloaders_from_config__mutmut_23, 
    'x__build_dataloaders_from_config__mutmut_24': x__build_dataloaders_from_config__mutmut_24, 
    'x__build_dataloaders_from_config__mutmut_25': x__build_dataloaders_from_config__mutmut_25, 
    'x__build_dataloaders_from_config__mutmut_26': x__build_dataloaders_from_config__mutmut_26, 
    'x__build_dataloaders_from_config__mutmut_27': x__build_dataloaders_from_config__mutmut_27, 
    'x__build_dataloaders_from_config__mutmut_28': x__build_dataloaders_from_config__mutmut_28, 
    'x__build_dataloaders_from_config__mutmut_29': x__build_dataloaders_from_config__mutmut_29, 
    'x__build_dataloaders_from_config__mutmut_30': x__build_dataloaders_from_config__mutmut_30, 
    'x__build_dataloaders_from_config__mutmut_31': x__build_dataloaders_from_config__mutmut_31, 
    'x__build_dataloaders_from_config__mutmut_32': x__build_dataloaders_from_config__mutmut_32, 
    'x__build_dataloaders_from_config__mutmut_33': x__build_dataloaders_from_config__mutmut_33, 
    'x__build_dataloaders_from_config__mutmut_34': x__build_dataloaders_from_config__mutmut_34, 
    'x__build_dataloaders_from_config__mutmut_35': x__build_dataloaders_from_config__mutmut_35, 
    'x__build_dataloaders_from_config__mutmut_36': x__build_dataloaders_from_config__mutmut_36, 
    'x__build_dataloaders_from_config__mutmut_37': x__build_dataloaders_from_config__mutmut_37, 
    'x__build_dataloaders_from_config__mutmut_38': x__build_dataloaders_from_config__mutmut_38, 
    'x__build_dataloaders_from_config__mutmut_39': x__build_dataloaders_from_config__mutmut_39, 
    'x__build_dataloaders_from_config__mutmut_40': x__build_dataloaders_from_config__mutmut_40, 
    'x__build_dataloaders_from_config__mutmut_41': x__build_dataloaders_from_config__mutmut_41, 
    'x__build_dataloaders_from_config__mutmut_42': x__build_dataloaders_from_config__mutmut_42, 
    'x__build_dataloaders_from_config__mutmut_43': x__build_dataloaders_from_config__mutmut_43, 
    'x__build_dataloaders_from_config__mutmut_44': x__build_dataloaders_from_config__mutmut_44, 
    'x__build_dataloaders_from_config__mutmut_45': x__build_dataloaders_from_config__mutmut_45, 
    'x__build_dataloaders_from_config__mutmut_46': x__build_dataloaders_from_config__mutmut_46, 
    'x__build_dataloaders_from_config__mutmut_47': x__build_dataloaders_from_config__mutmut_47, 
    'x__build_dataloaders_from_config__mutmut_48': x__build_dataloaders_from_config__mutmut_48, 
    'x__build_dataloaders_from_config__mutmut_49': x__build_dataloaders_from_config__mutmut_49, 
    'x__build_dataloaders_from_config__mutmut_50': x__build_dataloaders_from_config__mutmut_50, 
    'x__build_dataloaders_from_config__mutmut_51': x__build_dataloaders_from_config__mutmut_51, 
    'x__build_dataloaders_from_config__mutmut_52': x__build_dataloaders_from_config__mutmut_52, 
    'x__build_dataloaders_from_config__mutmut_53': x__build_dataloaders_from_config__mutmut_53, 
    'x__build_dataloaders_from_config__mutmut_54': x__build_dataloaders_from_config__mutmut_54, 
    'x__build_dataloaders_from_config__mutmut_55': x__build_dataloaders_from_config__mutmut_55, 
    'x__build_dataloaders_from_config__mutmut_56': x__build_dataloaders_from_config__mutmut_56, 
    'x__build_dataloaders_from_config__mutmut_57': x__build_dataloaders_from_config__mutmut_57, 
    'x__build_dataloaders_from_config__mutmut_58': x__build_dataloaders_from_config__mutmut_58, 
    'x__build_dataloaders_from_config__mutmut_59': x__build_dataloaders_from_config__mutmut_59, 
    'x__build_dataloaders_from_config__mutmut_60': x__build_dataloaders_from_config__mutmut_60, 
    'x__build_dataloaders_from_config__mutmut_61': x__build_dataloaders_from_config__mutmut_61, 
    'x__build_dataloaders_from_config__mutmut_62': x__build_dataloaders_from_config__mutmut_62, 
    'x__build_dataloaders_from_config__mutmut_63': x__build_dataloaders_from_config__mutmut_63, 
    'x__build_dataloaders_from_config__mutmut_64': x__build_dataloaders_from_config__mutmut_64, 
    'x__build_dataloaders_from_config__mutmut_65': x__build_dataloaders_from_config__mutmut_65, 
    'x__build_dataloaders_from_config__mutmut_66': x__build_dataloaders_from_config__mutmut_66, 
    'x__build_dataloaders_from_config__mutmut_67': x__build_dataloaders_from_config__mutmut_67, 
    'x__build_dataloaders_from_config__mutmut_68': x__build_dataloaders_from_config__mutmut_68, 
    'x__build_dataloaders_from_config__mutmut_69': x__build_dataloaders_from_config__mutmut_69, 
    'x__build_dataloaders_from_config__mutmut_70': x__build_dataloaders_from_config__mutmut_70, 
    'x__build_dataloaders_from_config__mutmut_71': x__build_dataloaders_from_config__mutmut_71, 
    'x__build_dataloaders_from_config__mutmut_72': x__build_dataloaders_from_config__mutmut_72, 
    'x__build_dataloaders_from_config__mutmut_73': x__build_dataloaders_from_config__mutmut_73, 
    'x__build_dataloaders_from_config__mutmut_74': x__build_dataloaders_from_config__mutmut_74, 
    'x__build_dataloaders_from_config__mutmut_75': x__build_dataloaders_from_config__mutmut_75, 
    'x__build_dataloaders_from_config__mutmut_76': x__build_dataloaders_from_config__mutmut_76, 
    'x__build_dataloaders_from_config__mutmut_77': x__build_dataloaders_from_config__mutmut_77, 
    'x__build_dataloaders_from_config__mutmut_78': x__build_dataloaders_from_config__mutmut_78, 
    'x__build_dataloaders_from_config__mutmut_79': x__build_dataloaders_from_config__mutmut_79, 
    'x__build_dataloaders_from_config__mutmut_80': x__build_dataloaders_from_config__mutmut_80, 
    'x__build_dataloaders_from_config__mutmut_81': x__build_dataloaders_from_config__mutmut_81, 
    'x__build_dataloaders_from_config__mutmut_82': x__build_dataloaders_from_config__mutmut_82, 
    'x__build_dataloaders_from_config__mutmut_83': x__build_dataloaders_from_config__mutmut_83, 
    'x__build_dataloaders_from_config__mutmut_84': x__build_dataloaders_from_config__mutmut_84, 
    'x__build_dataloaders_from_config__mutmut_85': x__build_dataloaders_from_config__mutmut_85, 
    'x__build_dataloaders_from_config__mutmut_86': x__build_dataloaders_from_config__mutmut_86, 
    'x__build_dataloaders_from_config__mutmut_87': x__build_dataloaders_from_config__mutmut_87, 
    'x__build_dataloaders_from_config__mutmut_88': x__build_dataloaders_from_config__mutmut_88, 
    'x__build_dataloaders_from_config__mutmut_89': x__build_dataloaders_from_config__mutmut_89, 
    'x__build_dataloaders_from_config__mutmut_90': x__build_dataloaders_from_config__mutmut_90, 
    'x__build_dataloaders_from_config__mutmut_91': x__build_dataloaders_from_config__mutmut_91, 
    'x__build_dataloaders_from_config__mutmut_92': x__build_dataloaders_from_config__mutmut_92, 
    'x__build_dataloaders_from_config__mutmut_93': x__build_dataloaders_from_config__mutmut_93, 
    'x__build_dataloaders_from_config__mutmut_94': x__build_dataloaders_from_config__mutmut_94
}

def _build_dataloaders_from_config(*args, **kwargs):
    result = _mutmut_trampoline(x__build_dataloaders_from_config__mutmut_orig, x__build_dataloaders_from_config__mutmut_mutants, args, kwargs)
    return result 

_build_dataloaders_from_config.__signature__ = _mutmut_signature(x__build_dataloaders_from_config__mutmut_orig)
x__build_dataloaders_from_config__mutmut_orig.__name__ = 'x__build_dataloaders_from_config'


def x_build_dataloaders__mutmut_orig(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_1(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 9,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_2(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 129,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_3(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = False,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_4(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 43,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_5(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 1,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_6(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = None
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_7(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(None, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_8(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, None)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_9(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_10(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, )

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_11(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) == 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_12(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 3:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_13(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError(None)
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_14(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("XXsplit_ratio must contain train and validation fractionsXX")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_15(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("SPLIT_RATIO MUST CONTAIN TRAIN AND VALIDATION FRACTIONS")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_16(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = None
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_17(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(None)
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_18(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(None))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_19(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_20(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 1.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_21(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 < ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_22(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total < 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_23(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 2.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_24(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError(None)
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_25(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("XXsplit_ratio values must sum to 1.0XX")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_26(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("SPLIT_RATIO VALUES MUST SUM TO 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_27(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = None
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_28(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=None,
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_29(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=None,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_30(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=None,
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_31(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=None,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_32(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=None,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_33(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=None,
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_34(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=None,
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_35(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=None,
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_36(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_37(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_38(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_39(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_40(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_41(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_42(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_43(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_44(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(None),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_45(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(None),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_46(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(None),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_47(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(None),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_48(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(None),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_49(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(None, config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_50(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, None)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_51(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(config)

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_52(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, )

    raise TypeError("build_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_53(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError(None)


def x_build_dataloaders__mutmut_54(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("XXbuild_dataloaders expects (tokenizer, DataConfig) or (path, tokenizer)XX")


def x_build_dataloaders__mutmut_55(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("build_dataloaders expects (tokenizer, dataconfig) or (path, tokenizer)")


def x_build_dataloaders__mutmut_56(
    data_path_or_tokenizer: Any,
    tokenizer_or_config: Any,
    *,
    batch_size: int = 8,
    max_length: int = 128,
    split_ratio: Sequence[float] = (0.8, 0.2),
    shuffle: bool = True,
    seed: int = 42,
    num_workers: int = 0,
    validation_path: str | None = None,
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Create train/validation dataloaders with a legacy-friendly signature."""

    if isinstance(tokenizer_or_config, DataConfig):
        tokenizer = data_path_or_tokenizer
        return _build_dataloaders_from_config(tokenizer, tokenizer_or_config)

    if isinstance(data_path_or_tokenizer, (str, Path)):
        if len(split_ratio) != 2:
            raise ValueError("split_ratio must contain train and validation fractions")
        ratio_total = float(sum(split_ratio))
        if not 0.99 <= ratio_total <= 1.01:
            raise ValueError("split_ratio values must sum to 1.0")
        config = DataConfig(
            dataset_path=str(data_path_or_tokenizer),
            validation_path=validation_path,
            batch_size=int(batch_size),
            split_ratio=split_ratio,
            shuffle=shuffle,
            max_length=int(max_length),
            seed=int(seed),
            num_workers=int(num_workers),
        )
        return _build_dataloaders_from_config(tokenizer_or_config, config)

    raise TypeError("BUILD_DATALOADERS EXPECTS (TOKENIZER, DATACONFIG) OR (PATH, TOKENIZER)")

x_build_dataloaders__mutmut_mutants : ClassVar[MutantDict] = {
'x_build_dataloaders__mutmut_1': x_build_dataloaders__mutmut_1, 
    'x_build_dataloaders__mutmut_2': x_build_dataloaders__mutmut_2, 
    'x_build_dataloaders__mutmut_3': x_build_dataloaders__mutmut_3, 
    'x_build_dataloaders__mutmut_4': x_build_dataloaders__mutmut_4, 
    'x_build_dataloaders__mutmut_5': x_build_dataloaders__mutmut_5, 
    'x_build_dataloaders__mutmut_6': x_build_dataloaders__mutmut_6, 
    'x_build_dataloaders__mutmut_7': x_build_dataloaders__mutmut_7, 
    'x_build_dataloaders__mutmut_8': x_build_dataloaders__mutmut_8, 
    'x_build_dataloaders__mutmut_9': x_build_dataloaders__mutmut_9, 
    'x_build_dataloaders__mutmut_10': x_build_dataloaders__mutmut_10, 
    'x_build_dataloaders__mutmut_11': x_build_dataloaders__mutmut_11, 
    'x_build_dataloaders__mutmut_12': x_build_dataloaders__mutmut_12, 
    'x_build_dataloaders__mutmut_13': x_build_dataloaders__mutmut_13, 
    'x_build_dataloaders__mutmut_14': x_build_dataloaders__mutmut_14, 
    'x_build_dataloaders__mutmut_15': x_build_dataloaders__mutmut_15, 
    'x_build_dataloaders__mutmut_16': x_build_dataloaders__mutmut_16, 
    'x_build_dataloaders__mutmut_17': x_build_dataloaders__mutmut_17, 
    'x_build_dataloaders__mutmut_18': x_build_dataloaders__mutmut_18, 
    'x_build_dataloaders__mutmut_19': x_build_dataloaders__mutmut_19, 
    'x_build_dataloaders__mutmut_20': x_build_dataloaders__mutmut_20, 
    'x_build_dataloaders__mutmut_21': x_build_dataloaders__mutmut_21, 
    'x_build_dataloaders__mutmut_22': x_build_dataloaders__mutmut_22, 
    'x_build_dataloaders__mutmut_23': x_build_dataloaders__mutmut_23, 
    'x_build_dataloaders__mutmut_24': x_build_dataloaders__mutmut_24, 
    'x_build_dataloaders__mutmut_25': x_build_dataloaders__mutmut_25, 
    'x_build_dataloaders__mutmut_26': x_build_dataloaders__mutmut_26, 
    'x_build_dataloaders__mutmut_27': x_build_dataloaders__mutmut_27, 
    'x_build_dataloaders__mutmut_28': x_build_dataloaders__mutmut_28, 
    'x_build_dataloaders__mutmut_29': x_build_dataloaders__mutmut_29, 
    'x_build_dataloaders__mutmut_30': x_build_dataloaders__mutmut_30, 
    'x_build_dataloaders__mutmut_31': x_build_dataloaders__mutmut_31, 
    'x_build_dataloaders__mutmut_32': x_build_dataloaders__mutmut_32, 
    'x_build_dataloaders__mutmut_33': x_build_dataloaders__mutmut_33, 
    'x_build_dataloaders__mutmut_34': x_build_dataloaders__mutmut_34, 
    'x_build_dataloaders__mutmut_35': x_build_dataloaders__mutmut_35, 
    'x_build_dataloaders__mutmut_36': x_build_dataloaders__mutmut_36, 
    'x_build_dataloaders__mutmut_37': x_build_dataloaders__mutmut_37, 
    'x_build_dataloaders__mutmut_38': x_build_dataloaders__mutmut_38, 
    'x_build_dataloaders__mutmut_39': x_build_dataloaders__mutmut_39, 
    'x_build_dataloaders__mutmut_40': x_build_dataloaders__mutmut_40, 
    'x_build_dataloaders__mutmut_41': x_build_dataloaders__mutmut_41, 
    'x_build_dataloaders__mutmut_42': x_build_dataloaders__mutmut_42, 
    'x_build_dataloaders__mutmut_43': x_build_dataloaders__mutmut_43, 
    'x_build_dataloaders__mutmut_44': x_build_dataloaders__mutmut_44, 
    'x_build_dataloaders__mutmut_45': x_build_dataloaders__mutmut_45, 
    'x_build_dataloaders__mutmut_46': x_build_dataloaders__mutmut_46, 
    'x_build_dataloaders__mutmut_47': x_build_dataloaders__mutmut_47, 
    'x_build_dataloaders__mutmut_48': x_build_dataloaders__mutmut_48, 
    'x_build_dataloaders__mutmut_49': x_build_dataloaders__mutmut_49, 
    'x_build_dataloaders__mutmut_50': x_build_dataloaders__mutmut_50, 
    'x_build_dataloaders__mutmut_51': x_build_dataloaders__mutmut_51, 
    'x_build_dataloaders__mutmut_52': x_build_dataloaders__mutmut_52, 
    'x_build_dataloaders__mutmut_53': x_build_dataloaders__mutmut_53, 
    'x_build_dataloaders__mutmut_54': x_build_dataloaders__mutmut_54, 
    'x_build_dataloaders__mutmut_55': x_build_dataloaders__mutmut_55, 
    'x_build_dataloaders__mutmut_56': x_build_dataloaders__mutmut_56
}

def build_dataloaders(*args, **kwargs):
    result = _mutmut_trampoline(x_build_dataloaders__mutmut_orig, x_build_dataloaders__mutmut_mutants, args, kwargs)
    return result 

build_dataloaders.__signature__ = _mutmut_signature(x_build_dataloaders__mutmut_orig)
x_build_dataloaders__mutmut_orig.__name__ = 'x_build_dataloaders'


def x_build_text_classification_dataloaders__mutmut_orig(
    tokenizer: Any, config: DataLoaderConfig
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Compat shim that accepts :class:`DataLoaderConfig` inputs."""

    return _build_dataloaders_from_config(tokenizer, config.to_data_config())


def x_build_text_classification_dataloaders__mutmut_1(
    tokenizer: Any, config: DataLoaderConfig
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Compat shim that accepts :class:`DataLoaderConfig` inputs."""

    return _build_dataloaders_from_config(None, config.to_data_config())


def x_build_text_classification_dataloaders__mutmut_2(
    tokenizer: Any, config: DataLoaderConfig
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Compat shim that accepts :class:`DataLoaderConfig` inputs."""

    return _build_dataloaders_from_config(tokenizer, None)


def x_build_text_classification_dataloaders__mutmut_3(
    tokenizer: Any, config: DataLoaderConfig
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Compat shim that accepts :class:`DataLoaderConfig` inputs."""

    return _build_dataloaders_from_config(config.to_data_config())


def x_build_text_classification_dataloaders__mutmut_4(
    tokenizer: Any, config: DataLoaderConfig
) -> tuple[TorchDataLoaderType, TorchDataLoaderType | None]:
    """Compat shim that accepts :class:`DataLoaderConfig` inputs."""

    return _build_dataloaders_from_config(tokenizer, )

x_build_text_classification_dataloaders__mutmut_mutants : ClassVar[MutantDict] = {
'x_build_text_classification_dataloaders__mutmut_1': x_build_text_classification_dataloaders__mutmut_1, 
    'x_build_text_classification_dataloaders__mutmut_2': x_build_text_classification_dataloaders__mutmut_2, 
    'x_build_text_classification_dataloaders__mutmut_3': x_build_text_classification_dataloaders__mutmut_3, 
    'x_build_text_classification_dataloaders__mutmut_4': x_build_text_classification_dataloaders__mutmut_4
}

def build_text_classification_dataloaders(*args, **kwargs):
    result = _mutmut_trampoline(x_build_text_classification_dataloaders__mutmut_orig, x_build_text_classification_dataloaders__mutmut_mutants, args, kwargs)
    return result 

build_text_classification_dataloaders.__signature__ = _mutmut_signature(x_build_text_classification_dataloaders__mutmut_orig)
x_build_text_classification_dataloaders__mutmut_orig.__name__ = 'x_build_text_classification_dataloaders'


def x_load_text_classification_dataset__mutmut_orig(path: str | Path) -> TextClassificationDataset:
    """Load a TSV text classification dataset."""

    return TextClassificationDataset(str(path))


def x_load_text_classification_dataset__mutmut_1(path: str | Path) -> TextClassificationDataset:
    """Load a TSV text classification dataset."""

    return TextClassificationDataset(None)


def x_load_text_classification_dataset__mutmut_2(path: str | Path) -> TextClassificationDataset:
    """Load a TSV text classification dataset."""

    return TextClassificationDataset(str(None))

x_load_text_classification_dataset__mutmut_mutants : ClassVar[MutantDict] = {
'x_load_text_classification_dataset__mutmut_1': x_load_text_classification_dataset__mutmut_1, 
    'x_load_text_classification_dataset__mutmut_2': x_load_text_classification_dataset__mutmut_2
}

def load_text_classification_dataset(*args, **kwargs):
    result = _mutmut_trampoline(x_load_text_classification_dataset__mutmut_orig, x_load_text_classification_dataset__mutmut_mutants, args, kwargs)
    return result 

load_text_classification_dataset.__signature__ = _mutmut_signature(x_load_text_classification_dataset__mutmut_orig)
x_load_text_classification_dataset__mutmut_orig.__name__ = 'x_load_text_classification_dataset'


def x__compute_lengths__mutmut_orig(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_1(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_2(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError(None)
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_3(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("XXlengths_or_fracs must be non-emptyXX")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_4(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("LENGTHS_OR_FRACS MUST BE NON-EMPTY")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_5(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = None
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_6(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[1]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_7(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) and any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_8(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(None):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_9(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = None
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_10(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(None) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_11(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = None
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_12(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(None)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_13(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_14(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (1.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_15(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 < total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_16(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total < 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_17(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 2.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_18(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError(None)
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_19(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("XXfractions must sum to 1.0XX")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_20(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("FRACTIONS MUST SUM TO 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_21(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = None
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_22(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(None) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_23(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n / frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_24(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = None
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_25(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n + sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_26(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(None)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_27(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = None
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_28(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 1
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_29(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder >= 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_30(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 1:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_31(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] = 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_32(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] -= 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_33(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx / len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_34(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 2
            remainder -= 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_35(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder = 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_36(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder += 1
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_37(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 2
            idx += 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_38(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx = 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_39(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx -= 1
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_40(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 2
        return lengths
    return [int(x) for x in lengths_or_fracs]


def x__compute_lengths__mutmut_41(n: int, lengths_or_fracs: Sequence[int | float]) -> list[int]:
    """Normalise a sequence of lengths or fractions to integer lengths."""

    if not lengths_or_fracs:
        raise ValueError("lengths_or_fracs must be non-empty")
    first = lengths_or_fracs[0]
    if isinstance(first, float) or any(isinstance(x, float) for x in lengths_or_fracs):
        fracs = [float(x) for x in lengths_or_fracs]
        total = sum(fracs)
        if not (0.999 <= total <= 1.001):
            raise ValueError("fractions must sum to 1.0")
        lengths = [int(n * frac) for frac in fracs]
        remainder = n - sum(lengths)
        idx = 0
        while remainder > 0:
            lengths[idx % len(lengths)] += 1
            remainder -= 1
            idx += 1
        return lengths
    return [int(None) for x in lengths_or_fracs]

x__compute_lengths__mutmut_mutants : ClassVar[MutantDict] = {
'x__compute_lengths__mutmut_1': x__compute_lengths__mutmut_1, 
    'x__compute_lengths__mutmut_2': x__compute_lengths__mutmut_2, 
    'x__compute_lengths__mutmut_3': x__compute_lengths__mutmut_3, 
    'x__compute_lengths__mutmut_4': x__compute_lengths__mutmut_4, 
    'x__compute_lengths__mutmut_5': x__compute_lengths__mutmut_5, 
    'x__compute_lengths__mutmut_6': x__compute_lengths__mutmut_6, 
    'x__compute_lengths__mutmut_7': x__compute_lengths__mutmut_7, 
    'x__compute_lengths__mutmut_8': x__compute_lengths__mutmut_8, 
    'x__compute_lengths__mutmut_9': x__compute_lengths__mutmut_9, 
    'x__compute_lengths__mutmut_10': x__compute_lengths__mutmut_10, 
    'x__compute_lengths__mutmut_11': x__compute_lengths__mutmut_11, 
    'x__compute_lengths__mutmut_12': x__compute_lengths__mutmut_12, 
    'x__compute_lengths__mutmut_13': x__compute_lengths__mutmut_13, 
    'x__compute_lengths__mutmut_14': x__compute_lengths__mutmut_14, 
    'x__compute_lengths__mutmut_15': x__compute_lengths__mutmut_15, 
    'x__compute_lengths__mutmut_16': x__compute_lengths__mutmut_16, 
    'x__compute_lengths__mutmut_17': x__compute_lengths__mutmut_17, 
    'x__compute_lengths__mutmut_18': x__compute_lengths__mutmut_18, 
    'x__compute_lengths__mutmut_19': x__compute_lengths__mutmut_19, 
    'x__compute_lengths__mutmut_20': x__compute_lengths__mutmut_20, 
    'x__compute_lengths__mutmut_21': x__compute_lengths__mutmut_21, 
    'x__compute_lengths__mutmut_22': x__compute_lengths__mutmut_22, 
    'x__compute_lengths__mutmut_23': x__compute_lengths__mutmut_23, 
    'x__compute_lengths__mutmut_24': x__compute_lengths__mutmut_24, 
    'x__compute_lengths__mutmut_25': x__compute_lengths__mutmut_25, 
    'x__compute_lengths__mutmut_26': x__compute_lengths__mutmut_26, 
    'x__compute_lengths__mutmut_27': x__compute_lengths__mutmut_27, 
    'x__compute_lengths__mutmut_28': x__compute_lengths__mutmut_28, 
    'x__compute_lengths__mutmut_29': x__compute_lengths__mutmut_29, 
    'x__compute_lengths__mutmut_30': x__compute_lengths__mutmut_30, 
    'x__compute_lengths__mutmut_31': x__compute_lengths__mutmut_31, 
    'x__compute_lengths__mutmut_32': x__compute_lengths__mutmut_32, 
    'x__compute_lengths__mutmut_33': x__compute_lengths__mutmut_33, 
    'x__compute_lengths__mutmut_34': x__compute_lengths__mutmut_34, 
    'x__compute_lengths__mutmut_35': x__compute_lengths__mutmut_35, 
    'x__compute_lengths__mutmut_36': x__compute_lengths__mutmut_36, 
    'x__compute_lengths__mutmut_37': x__compute_lengths__mutmut_37, 
    'x__compute_lengths__mutmut_38': x__compute_lengths__mutmut_38, 
    'x__compute_lengths__mutmut_39': x__compute_lengths__mutmut_39, 
    'x__compute_lengths__mutmut_40': x__compute_lengths__mutmut_40, 
    'x__compute_lengths__mutmut_41': x__compute_lengths__mutmut_41
}

def _compute_lengths(*args, **kwargs):
    result = _mutmut_trampoline(x__compute_lengths__mutmut_orig, x__compute_lengths__mutmut_mutants, args, kwargs)
    return result 

_compute_lengths.__signature__ = _mutmut_signature(x__compute_lengths__mutmut_orig)
x__compute_lengths__mutmut_orig.__name__ = 'x__compute_lengths'


def x_deterministic_split__mutmut_orig(
    dataset: TorchDatasetType,
    lengths_or_fracs: Sequence[int | float],
    *,
    seed: int = 1337,
) -> tuple[Subset, ...]:
    """Deterministically split a dataset using a seeded ``torch.Generator``."""

    if torch is None or torch_random_split is None:
        raise RuntimeError("torch is required for deterministic_split")
    lengths = _compute_lengths(len(dataset), lengths_or_fracs)
    generator = torch.Generator().manual_seed(int(seed))
    parts = torch_random_split(dataset, lengths, generator=generator)
    return tuple(parts)


def x_deterministic_split__mutmut_1(
    dataset: TorchDatasetType,
    lengths_or_fracs: Sequence[int | float],
    *,
    seed: int = 1338,
) -> tuple[Subset, ...]:
    """Deterministically split a dataset using a seeded ``torch.Generator``."""

    if torch is None or torch_random_split is None:
        raise RuntimeError("torch is required for deterministic_split")
    lengths = _compute_lengths(len(dataset), lengths_or_fracs)
    generator = torch.Generator().manual_seed(int(seed))
    parts = torch_random_split(dataset, lengths, generator=generator)
    return tuple(parts)


def x_deterministic_split__mutmut_2(
    dataset: TorchDatasetType,
    lengths_or_fracs: Sequence[int | float],
    *,
    seed: int = 1337,
) -> tuple[Subset, ...]:
    """Deterministically split a dataset using a seeded ``torch.Generator``."""

    if torch is None and torch_random_split is None:
        raise RuntimeError("torch is required for deterministic_split")
    lengths = _compute_lengths(len(dataset), lengths_or_fracs)
    generator = torch.Generator().manual_seed(int(seed))
    parts = torch_random_split(dataset, lengths, generator=generator)
    return tuple(parts)


def x_deterministic_split__mutmut_3(
    dataset: TorchDatasetType,
    lengths_or_fracs: Sequence[int | float],
    *,
    seed: int = 1337,
) -> tuple[Subset, ...]:
    """Deterministically split a dataset using a seeded ``torch.Generator``."""

    if torch is not None or torch_random_split is None:
        raise RuntimeError("torch is required for deterministic_split")
    lengths = _compute_lengths(len(dataset), lengths_or_fracs)
    generator = torch.Generator().manual_seed(int(seed))
    parts = torch_random_split(dataset, lengths, generator=generator)
    return tuple(parts)


def x_deterministic_split__mutmut_4(
    dataset: TorchDatasetType,
    lengths_or_fracs: Sequence[int | float],
    *,
    seed: int = 1337,
) -> tuple[Subset, ...]:
    """Deterministically split a dataset using a seeded ``torch.Generator``."""

    if torch is None or torch_random_split is not None:
        raise RuntimeError("torch is required for deterministic_split")
    lengths = _compute_lengths(len(dataset), lengths_or_fracs)
    generator = torch.Generator().manual_seed(int(seed))
    parts = torch_random_split(dataset, lengths, generator=generator)
    return tuple(parts)


def x_deterministic_split__mutmut_5(
    dataset: TorchDatasetType,
    lengths_or_fracs: Sequence[int | float],
    *,
    seed: int = 1337,
) -> tuple[Subset, ...]:
    """Deterministically split a dataset using a seeded ``torch.Generator``."""

    if torch is None or torch_random_split is None:
        raise RuntimeError(None)
    lengths = _compute_lengths(len(dataset), lengths_or_fracs)
    generator = torch.Generator().manual_seed(int(seed))
    parts = torch_random_split(dataset, lengths, generator=generator)
    return tuple(parts)


def x_deterministic_split__mutmut_6(
    dataset: TorchDatasetType,
    lengths_or_fracs: Sequence[int | float],
    *,
    seed: int = 1337,
) -> tuple[Subset, ...]:
    """Deterministically split a dataset using a seeded ``torch.Generator``."""

    if torch is None or torch_random_split is None:
        raise RuntimeError("XXtorch is required for deterministic_splitXX")
    lengths = _compute_lengths(len(dataset), lengths_or_fracs)
    generator = torch.Generator().manual_seed(int(seed))
    parts = torch_random_split(dataset, lengths, generator=generator)
    return tuple(parts)


def x_deterministic_split__mutmut_7(
    dataset: TorchDatasetType,
    lengths_or_fracs: Sequence[int | float],
    *,
    seed: int = 1337,
) -> tuple[Subset, ...]:
    """Deterministically split a dataset using a seeded ``torch.Generator``."""

    if torch is None or torch_random_split is None:
        raise RuntimeError("TORCH IS REQUIRED FOR DETERMINISTIC_SPLIT")
    lengths = _compute_lengths(len(dataset), lengths_or_fracs)
    generator = torch.Generator().manual_seed(int(seed))
    parts = torch_random_split(dataset, lengths, generator=generator)
    return tuple(parts)


def x_deterministic_split__mutmut_8(
    dataset: TorchDatasetType,
    lengths_or_fracs: Sequence[int | float],
    *,
    seed: int = 1337,
) -> tuple[Subset, ...]:
    """Deterministically split a dataset using a seeded ``torch.Generator``."""

    if torch is None or torch_random_split is None:
        raise RuntimeError("torch is required for deterministic_split")
    lengths = None
    generator = torch.Generator().manual_seed(int(seed))
    parts = torch_random_split(dataset, lengths, generator=generator)
    return tuple(parts)


def x_deterministic_split__mutmut_9(
    dataset: TorchDatasetType,
    lengths_or_fracs: Sequence[int | float],
    *,
    seed: int = 1337,
) -> tuple[Subset, ...]:
    """Deterministically split a dataset using a seeded ``torch.Generator``."""

    if torch is None or torch_random_split is None:
        raise RuntimeError("torch is required for deterministic_split")
    lengths = _compute_lengths(None, lengths_or_fracs)
    generator = torch.Generator().manual_seed(int(seed))
    parts = torch_random_split(dataset, lengths, generator=generator)
    return tuple(parts)


def x_deterministic_split__mutmut_10(
    dataset: TorchDatasetType,
    lengths_or_fracs: Sequence[int | float],
    *,
    seed: int = 1337,
) -> tuple[Subset, ...]:
    """Deterministically split a dataset using a seeded ``torch.Generator``."""

    if torch is None or torch_random_split is None:
        raise RuntimeError("torch is required for deterministic_split")
    lengths = _compute_lengths(len(dataset), None)
    generator = torch.Generator().manual_seed(int(seed))
    parts = torch_random_split(dataset, lengths, generator=generator)
    return tuple(parts)


def x_deterministic_split__mutmut_11(
    dataset: TorchDatasetType,
    lengths_or_fracs: Sequence[int | float],
    *,
    seed: int = 1337,
) -> tuple[Subset, ...]:
    """Deterministically split a dataset using a seeded ``torch.Generator``."""

    if torch is None or torch_random_split is None:
        raise RuntimeError("torch is required for deterministic_split")
    lengths = _compute_lengths(lengths_or_fracs)
    generator = torch.Generator().manual_seed(int(seed))
    parts = torch_random_split(dataset, lengths, generator=generator)
    return tuple(parts)


def x_deterministic_split__mutmut_12(
    dataset: TorchDatasetType,
    lengths_or_fracs: Sequence[int | float],
    *,
    seed: int = 1337,
) -> tuple[Subset, ...]:
    """Deterministically split a dataset using a seeded ``torch.Generator``."""

    if torch is None or torch_random_split is None:
        raise RuntimeError("torch is required for deterministic_split")
    lengths = _compute_lengths(len(dataset), )
    generator = torch.Generator().manual_seed(int(seed))
    parts = torch_random_split(dataset, lengths, generator=generator)
    return tuple(parts)


def x_deterministic_split__mutmut_13(
    dataset: TorchDatasetType,
    lengths_or_fracs: Sequence[int | float],
    *,
    seed: int = 1337,
) -> tuple[Subset, ...]:
    """Deterministically split a dataset using a seeded ``torch.Generator``."""

    if torch is None or torch_random_split is None:
        raise RuntimeError("torch is required for deterministic_split")
    lengths = _compute_lengths(len(dataset), lengths_or_fracs)
    generator = None
    parts = torch_random_split(dataset, lengths, generator=generator)
    return tuple(parts)


def x_deterministic_split__mutmut_14(
    dataset: TorchDatasetType,
    lengths_or_fracs: Sequence[int | float],
    *,
    seed: int = 1337,
) -> tuple[Subset, ...]:
    """Deterministically split a dataset using a seeded ``torch.Generator``."""

    if torch is None or torch_random_split is None:
        raise RuntimeError("torch is required for deterministic_split")
    lengths = _compute_lengths(len(dataset), lengths_or_fracs)
    generator = torch.Generator().manual_seed(None)
    parts = torch_random_split(dataset, lengths, generator=generator)
    return tuple(parts)


def x_deterministic_split__mutmut_15(
    dataset: TorchDatasetType,
    lengths_or_fracs: Sequence[int | float],
    *,
    seed: int = 1337,
) -> tuple[Subset, ...]:
    """Deterministically split a dataset using a seeded ``torch.Generator``."""

    if torch is None or torch_random_split is None:
        raise RuntimeError("torch is required for deterministic_split")
    lengths = _compute_lengths(len(dataset), lengths_or_fracs)
    generator = torch.Generator().manual_seed(int(None))
    parts = torch_random_split(dataset, lengths, generator=generator)
    return tuple(parts)


def x_deterministic_split__mutmut_16(
    dataset: TorchDatasetType,
    lengths_or_fracs: Sequence[int | float],
    *,
    seed: int = 1337,
) -> tuple[Subset, ...]:
    """Deterministically split a dataset using a seeded ``torch.Generator``."""

    if torch is None or torch_random_split is None:
        raise RuntimeError("torch is required for deterministic_split")
    lengths = _compute_lengths(len(dataset), lengths_or_fracs)
    generator = torch.Generator().manual_seed(int(seed))
    parts = None
    return tuple(parts)


def x_deterministic_split__mutmut_17(
    dataset: TorchDatasetType,
    lengths_or_fracs: Sequence[int | float],
    *,
    seed: int = 1337,
) -> tuple[Subset, ...]:
    """Deterministically split a dataset using a seeded ``torch.Generator``."""

    if torch is None or torch_random_split is None:
        raise RuntimeError("torch is required for deterministic_split")
    lengths = _compute_lengths(len(dataset), lengths_or_fracs)
    generator = torch.Generator().manual_seed(int(seed))
    parts = torch_random_split(None, lengths, generator=generator)
    return tuple(parts)


def x_deterministic_split__mutmut_18(
    dataset: TorchDatasetType,
    lengths_or_fracs: Sequence[int | float],
    *,
    seed: int = 1337,
) -> tuple[Subset, ...]:
    """Deterministically split a dataset using a seeded ``torch.Generator``."""

    if torch is None or torch_random_split is None:
        raise RuntimeError("torch is required for deterministic_split")
    lengths = _compute_lengths(len(dataset), lengths_or_fracs)
    generator = torch.Generator().manual_seed(int(seed))
    parts = torch_random_split(dataset, None, generator=generator)
    return tuple(parts)


def x_deterministic_split__mutmut_19(
    dataset: TorchDatasetType,
    lengths_or_fracs: Sequence[int | float],
    *,
    seed: int = 1337,
) -> tuple[Subset, ...]:
    """Deterministically split a dataset using a seeded ``torch.Generator``."""

    if torch is None or torch_random_split is None:
        raise RuntimeError("torch is required for deterministic_split")
    lengths = _compute_lengths(len(dataset), lengths_or_fracs)
    generator = torch.Generator().manual_seed(int(seed))
    parts = torch_random_split(dataset, lengths, generator=None)
    return tuple(parts)


def x_deterministic_split__mutmut_20(
    dataset: TorchDatasetType,
    lengths_or_fracs: Sequence[int | float],
    *,
    seed: int = 1337,
) -> tuple[Subset, ...]:
    """Deterministically split a dataset using a seeded ``torch.Generator``."""

    if torch is None or torch_random_split is None:
        raise RuntimeError("torch is required for deterministic_split")
    lengths = _compute_lengths(len(dataset), lengths_or_fracs)
    generator = torch.Generator().manual_seed(int(seed))
    parts = torch_random_split(lengths, generator=generator)
    return tuple(parts)


def x_deterministic_split__mutmut_21(
    dataset: TorchDatasetType,
    lengths_or_fracs: Sequence[int | float],
    *,
    seed: int = 1337,
) -> tuple[Subset, ...]:
    """Deterministically split a dataset using a seeded ``torch.Generator``."""

    if torch is None or torch_random_split is None:
        raise RuntimeError("torch is required for deterministic_split")
    lengths = _compute_lengths(len(dataset), lengths_or_fracs)
    generator = torch.Generator().manual_seed(int(seed))
    parts = torch_random_split(dataset, generator=generator)
    return tuple(parts)


def x_deterministic_split__mutmut_22(
    dataset: TorchDatasetType,
    lengths_or_fracs: Sequence[int | float],
    *,
    seed: int = 1337,
) -> tuple[Subset, ...]:
    """Deterministically split a dataset using a seeded ``torch.Generator``."""

    if torch is None or torch_random_split is None:
        raise RuntimeError("torch is required for deterministic_split")
    lengths = _compute_lengths(len(dataset), lengths_or_fracs)
    generator = torch.Generator().manual_seed(int(seed))
    parts = torch_random_split(dataset, lengths, )
    return tuple(parts)


def x_deterministic_split__mutmut_23(
    dataset: TorchDatasetType,
    lengths_or_fracs: Sequence[int | float],
    *,
    seed: int = 1337,
) -> tuple[Subset, ...]:
    """Deterministically split a dataset using a seeded ``torch.Generator``."""

    if torch is None or torch_random_split is None:
        raise RuntimeError("torch is required for deterministic_split")
    lengths = _compute_lengths(len(dataset), lengths_or_fracs)
    generator = torch.Generator().manual_seed(int(seed))
    parts = torch_random_split(dataset, lengths, generator=generator)
    return tuple(None)

x_deterministic_split__mutmut_mutants : ClassVar[MutantDict] = {
'x_deterministic_split__mutmut_1': x_deterministic_split__mutmut_1, 
    'x_deterministic_split__mutmut_2': x_deterministic_split__mutmut_2, 
    'x_deterministic_split__mutmut_3': x_deterministic_split__mutmut_3, 
    'x_deterministic_split__mutmut_4': x_deterministic_split__mutmut_4, 
    'x_deterministic_split__mutmut_5': x_deterministic_split__mutmut_5, 
    'x_deterministic_split__mutmut_6': x_deterministic_split__mutmut_6, 
    'x_deterministic_split__mutmut_7': x_deterministic_split__mutmut_7, 
    'x_deterministic_split__mutmut_8': x_deterministic_split__mutmut_8, 
    'x_deterministic_split__mutmut_9': x_deterministic_split__mutmut_9, 
    'x_deterministic_split__mutmut_10': x_deterministic_split__mutmut_10, 
    'x_deterministic_split__mutmut_11': x_deterministic_split__mutmut_11, 
    'x_deterministic_split__mutmut_12': x_deterministic_split__mutmut_12, 
    'x_deterministic_split__mutmut_13': x_deterministic_split__mutmut_13, 
    'x_deterministic_split__mutmut_14': x_deterministic_split__mutmut_14, 
    'x_deterministic_split__mutmut_15': x_deterministic_split__mutmut_15, 
    'x_deterministic_split__mutmut_16': x_deterministic_split__mutmut_16, 
    'x_deterministic_split__mutmut_17': x_deterministic_split__mutmut_17, 
    'x_deterministic_split__mutmut_18': x_deterministic_split__mutmut_18, 
    'x_deterministic_split__mutmut_19': x_deterministic_split__mutmut_19, 
    'x_deterministic_split__mutmut_20': x_deterministic_split__mutmut_20, 
    'x_deterministic_split__mutmut_21': x_deterministic_split__mutmut_21, 
    'x_deterministic_split__mutmut_22': x_deterministic_split__mutmut_22, 
    'x_deterministic_split__mutmut_23': x_deterministic_split__mutmut_23
}

def deterministic_split(*args, **kwargs):
    result = _mutmut_trampoline(x_deterministic_split__mutmut_orig, x_deterministic_split__mutmut_mutants, args, kwargs)
    return result 

deterministic_split.__signature__ = _mutmut_signature(x_deterministic_split__mutmut_orig)
x_deterministic_split__mutmut_orig.__name__ = 'x_deterministic_split'


def x_tiny_tensor_dataset__mutmut_orig(
    n: int = 32,
    d_in: int = 8,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None or TorchTensorDataset is None:
        raise RuntimeError("torch is required for tiny_tensor_dataset")
    inputs = torch.randn(n, d_in)
    targets = torch.randint(0, n_classes, (n,))
    return TorchTensorDataset(inputs, targets)


def x_tiny_tensor_dataset__mutmut_1(
    n: int = 33,
    d_in: int = 8,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None or TorchTensorDataset is None:
        raise RuntimeError("torch is required for tiny_tensor_dataset")
    inputs = torch.randn(n, d_in)
    targets = torch.randint(0, n_classes, (n,))
    return TorchTensorDataset(inputs, targets)


def x_tiny_tensor_dataset__mutmut_2(
    n: int = 32,
    d_in: int = 9,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None or TorchTensorDataset is None:
        raise RuntimeError("torch is required for tiny_tensor_dataset")
    inputs = torch.randn(n, d_in)
    targets = torch.randint(0, n_classes, (n,))
    return TorchTensorDataset(inputs, targets)


def x_tiny_tensor_dataset__mutmut_3(
    n: int = 32,
    d_in: int = 8,
    n_classes: int = 5,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None or TorchTensorDataset is None:
        raise RuntimeError("torch is required for tiny_tensor_dataset")
    inputs = torch.randn(n, d_in)
    targets = torch.randint(0, n_classes, (n,))
    return TorchTensorDataset(inputs, targets)


def x_tiny_tensor_dataset__mutmut_4(
    n: int = 32,
    d_in: int = 8,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None and TorchTensorDataset is None:
        raise RuntimeError("torch is required for tiny_tensor_dataset")
    inputs = torch.randn(n, d_in)
    targets = torch.randint(0, n_classes, (n,))
    return TorchTensorDataset(inputs, targets)


def x_tiny_tensor_dataset__mutmut_5(
    n: int = 32,
    d_in: int = 8,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is not None or TorchTensorDataset is None:
        raise RuntimeError("torch is required for tiny_tensor_dataset")
    inputs = torch.randn(n, d_in)
    targets = torch.randint(0, n_classes, (n,))
    return TorchTensorDataset(inputs, targets)


def x_tiny_tensor_dataset__mutmut_6(
    n: int = 32,
    d_in: int = 8,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None or TorchTensorDataset is not None:
        raise RuntimeError("torch is required for tiny_tensor_dataset")
    inputs = torch.randn(n, d_in)
    targets = torch.randint(0, n_classes, (n,))
    return TorchTensorDataset(inputs, targets)


def x_tiny_tensor_dataset__mutmut_7(
    n: int = 32,
    d_in: int = 8,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None or TorchTensorDataset is None:
        raise RuntimeError(None)
    inputs = torch.randn(n, d_in)
    targets = torch.randint(0, n_classes, (n,))
    return TorchTensorDataset(inputs, targets)


def x_tiny_tensor_dataset__mutmut_8(
    n: int = 32,
    d_in: int = 8,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None or TorchTensorDataset is None:
        raise RuntimeError("XXtorch is required for tiny_tensor_datasetXX")
    inputs = torch.randn(n, d_in)
    targets = torch.randint(0, n_classes, (n,))
    return TorchTensorDataset(inputs, targets)


def x_tiny_tensor_dataset__mutmut_9(
    n: int = 32,
    d_in: int = 8,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None or TorchTensorDataset is None:
        raise RuntimeError("TORCH IS REQUIRED FOR TINY_TENSOR_DATASET")
    inputs = torch.randn(n, d_in)
    targets = torch.randint(0, n_classes, (n,))
    return TorchTensorDataset(inputs, targets)


def x_tiny_tensor_dataset__mutmut_10(
    n: int = 32,
    d_in: int = 8,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None or TorchTensorDataset is None:
        raise RuntimeError("torch is required for tiny_tensor_dataset")
    inputs = None
    targets = torch.randint(0, n_classes, (n,))
    return TorchTensorDataset(inputs, targets)


def x_tiny_tensor_dataset__mutmut_11(
    n: int = 32,
    d_in: int = 8,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None or TorchTensorDataset is None:
        raise RuntimeError("torch is required for tiny_tensor_dataset")
    inputs = torch.randn(None, d_in)
    targets = torch.randint(0, n_classes, (n,))
    return TorchTensorDataset(inputs, targets)


def x_tiny_tensor_dataset__mutmut_12(
    n: int = 32,
    d_in: int = 8,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None or TorchTensorDataset is None:
        raise RuntimeError("torch is required for tiny_tensor_dataset")
    inputs = torch.randn(n, None)
    targets = torch.randint(0, n_classes, (n,))
    return TorchTensorDataset(inputs, targets)


def x_tiny_tensor_dataset__mutmut_13(
    n: int = 32,
    d_in: int = 8,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None or TorchTensorDataset is None:
        raise RuntimeError("torch is required for tiny_tensor_dataset")
    inputs = torch.randn(d_in)
    targets = torch.randint(0, n_classes, (n,))
    return TorchTensorDataset(inputs, targets)


def x_tiny_tensor_dataset__mutmut_14(
    n: int = 32,
    d_in: int = 8,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None or TorchTensorDataset is None:
        raise RuntimeError("torch is required for tiny_tensor_dataset")
    inputs = torch.randn(n, )
    targets = torch.randint(0, n_classes, (n,))
    return TorchTensorDataset(inputs, targets)


def x_tiny_tensor_dataset__mutmut_15(
    n: int = 32,
    d_in: int = 8,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None or TorchTensorDataset is None:
        raise RuntimeError("torch is required for tiny_tensor_dataset")
    inputs = torch.randn(n, d_in)
    targets = None
    return TorchTensorDataset(inputs, targets)


def x_tiny_tensor_dataset__mutmut_16(
    n: int = 32,
    d_in: int = 8,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None or TorchTensorDataset is None:
        raise RuntimeError("torch is required for tiny_tensor_dataset")
    inputs = torch.randn(n, d_in)
    targets = torch.randint(None, n_classes, (n,))
    return TorchTensorDataset(inputs, targets)


def x_tiny_tensor_dataset__mutmut_17(
    n: int = 32,
    d_in: int = 8,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None or TorchTensorDataset is None:
        raise RuntimeError("torch is required for tiny_tensor_dataset")
    inputs = torch.randn(n, d_in)
    targets = torch.randint(0, None, (n,))
    return TorchTensorDataset(inputs, targets)


def x_tiny_tensor_dataset__mutmut_18(
    n: int = 32,
    d_in: int = 8,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None or TorchTensorDataset is None:
        raise RuntimeError("torch is required for tiny_tensor_dataset")
    inputs = torch.randn(n, d_in)
    targets = torch.randint(0, n_classes, None)
    return TorchTensorDataset(inputs, targets)


def x_tiny_tensor_dataset__mutmut_19(
    n: int = 32,
    d_in: int = 8,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None or TorchTensorDataset is None:
        raise RuntimeError("torch is required for tiny_tensor_dataset")
    inputs = torch.randn(n, d_in)
    targets = torch.randint(n_classes, (n,))
    return TorchTensorDataset(inputs, targets)


def x_tiny_tensor_dataset__mutmut_20(
    n: int = 32,
    d_in: int = 8,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None or TorchTensorDataset is None:
        raise RuntimeError("torch is required for tiny_tensor_dataset")
    inputs = torch.randn(n, d_in)
    targets = torch.randint(0, (n,))
    return TorchTensorDataset(inputs, targets)


def x_tiny_tensor_dataset__mutmut_21(
    n: int = 32,
    d_in: int = 8,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None or TorchTensorDataset is None:
        raise RuntimeError("torch is required for tiny_tensor_dataset")
    inputs = torch.randn(n, d_in)
    targets = torch.randint(0, n_classes, )
    return TorchTensorDataset(inputs, targets)


def x_tiny_tensor_dataset__mutmut_22(
    n: int = 32,
    d_in: int = 8,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None or TorchTensorDataset is None:
        raise RuntimeError("torch is required for tiny_tensor_dataset")
    inputs = torch.randn(n, d_in)
    targets = torch.randint(1, n_classes, (n,))
    return TorchTensorDataset(inputs, targets)


def x_tiny_tensor_dataset__mutmut_23(
    n: int = 32,
    d_in: int = 8,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None or TorchTensorDataset is None:
        raise RuntimeError("torch is required for tiny_tensor_dataset")
    inputs = torch.randn(n, d_in)
    targets = torch.randint(0, n_classes, (n,))
    return TorchTensorDataset(None, targets)


def x_tiny_tensor_dataset__mutmut_24(
    n: int = 32,
    d_in: int = 8,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None or TorchTensorDataset is None:
        raise RuntimeError("torch is required for tiny_tensor_dataset")
    inputs = torch.randn(n, d_in)
    targets = torch.randint(0, n_classes, (n,))
    return TorchTensorDataset(inputs, None)


def x_tiny_tensor_dataset__mutmut_25(
    n: int = 32,
    d_in: int = 8,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None or TorchTensorDataset is None:
        raise RuntimeError("torch is required for tiny_tensor_dataset")
    inputs = torch.randn(n, d_in)
    targets = torch.randint(0, n_classes, (n,))
    return TorchTensorDataset(targets)


def x_tiny_tensor_dataset__mutmut_26(
    n: int = 32,
    d_in: int = 8,
    n_classes: int = 4,
) -> TorchTensorDataset:
    """Construct a small synthetic dataset for deterministic smoke tests."""

    if torch is None or TorchTensorDataset is None:
        raise RuntimeError("torch is required for tiny_tensor_dataset")
    inputs = torch.randn(n, d_in)
    targets = torch.randint(0, n_classes, (n,))
    return TorchTensorDataset(inputs, )

x_tiny_tensor_dataset__mutmut_mutants : ClassVar[MutantDict] = {
'x_tiny_tensor_dataset__mutmut_1': x_tiny_tensor_dataset__mutmut_1, 
    'x_tiny_tensor_dataset__mutmut_2': x_tiny_tensor_dataset__mutmut_2, 
    'x_tiny_tensor_dataset__mutmut_3': x_tiny_tensor_dataset__mutmut_3, 
    'x_tiny_tensor_dataset__mutmut_4': x_tiny_tensor_dataset__mutmut_4, 
    'x_tiny_tensor_dataset__mutmut_5': x_tiny_tensor_dataset__mutmut_5, 
    'x_tiny_tensor_dataset__mutmut_6': x_tiny_tensor_dataset__mutmut_6, 
    'x_tiny_tensor_dataset__mutmut_7': x_tiny_tensor_dataset__mutmut_7, 
    'x_tiny_tensor_dataset__mutmut_8': x_tiny_tensor_dataset__mutmut_8, 
    'x_tiny_tensor_dataset__mutmut_9': x_tiny_tensor_dataset__mutmut_9, 
    'x_tiny_tensor_dataset__mutmut_10': x_tiny_tensor_dataset__mutmut_10, 
    'x_tiny_tensor_dataset__mutmut_11': x_tiny_tensor_dataset__mutmut_11, 
    'x_tiny_tensor_dataset__mutmut_12': x_tiny_tensor_dataset__mutmut_12, 
    'x_tiny_tensor_dataset__mutmut_13': x_tiny_tensor_dataset__mutmut_13, 
    'x_tiny_tensor_dataset__mutmut_14': x_tiny_tensor_dataset__mutmut_14, 
    'x_tiny_tensor_dataset__mutmut_15': x_tiny_tensor_dataset__mutmut_15, 
    'x_tiny_tensor_dataset__mutmut_16': x_tiny_tensor_dataset__mutmut_16, 
    'x_tiny_tensor_dataset__mutmut_17': x_tiny_tensor_dataset__mutmut_17, 
    'x_tiny_tensor_dataset__mutmut_18': x_tiny_tensor_dataset__mutmut_18, 
    'x_tiny_tensor_dataset__mutmut_19': x_tiny_tensor_dataset__mutmut_19, 
    'x_tiny_tensor_dataset__mutmut_20': x_tiny_tensor_dataset__mutmut_20, 
    'x_tiny_tensor_dataset__mutmut_21': x_tiny_tensor_dataset__mutmut_21, 
    'x_tiny_tensor_dataset__mutmut_22': x_tiny_tensor_dataset__mutmut_22, 
    'x_tiny_tensor_dataset__mutmut_23': x_tiny_tensor_dataset__mutmut_23, 
    'x_tiny_tensor_dataset__mutmut_24': x_tiny_tensor_dataset__mutmut_24, 
    'x_tiny_tensor_dataset__mutmut_25': x_tiny_tensor_dataset__mutmut_25, 
    'x_tiny_tensor_dataset__mutmut_26': x_tiny_tensor_dataset__mutmut_26
}

def tiny_tensor_dataset(*args, **kwargs):
    result = _mutmut_trampoline(x_tiny_tensor_dataset__mutmut_orig, x_tiny_tensor_dataset__mutmut_mutants, args, kwargs)
    return result 

tiny_tensor_dataset.__signature__ = _mutmut_signature(x_tiny_tensor_dataset__mutmut_orig)
x_tiny_tensor_dataset__mutmut_orig.__name__ = 'x_tiny_tensor_dataset'


__all__ = [
    "DataConfig",
    "TextClassificationDataset",
    "build_dataloaders",
    "deterministic_split",
    "tiny_tensor_dataset",
]
