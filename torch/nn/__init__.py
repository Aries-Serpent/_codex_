"""Minimal torch.nn shim for test environments.

Extended stub: covers all nn.* attributes referenced in src/ so mypy can
resolve them without the real torch wheel installed.  The stubs use
permissive *args/**kwargs signatures so mypy doesn't raise [call-arg] errors
against real downstream call-sites.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

__all__ = [
    "Module",
    "Linear",
    "Sequential",
    "Dropout",
    "LayerNorm",
    "Embedding",
    "GELU",
    "ReLU",
    "SiLU",
    "Tanh",
    "ModuleList",
    "MultiheadAttention",
    "CrossEntropyLoss",
    "MSELoss",
    "BCELoss",
    "BCEWithLogitsLoss",
    "Conv1d",
    "Conv2d",
    "LSTM",
    "GRU",
    "Softmax",
    "LogSoftmax",
    "Sigmoid",
    "BatchNorm1d",
    "BatchNorm2d",
    "Parameter",
    "functional",
]


class Module:  # pragma: no cover - convenience stub
    training: bool = True

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.training = True

    def train(self, mode: bool = True) -> "Module":
        self.training = mode
        return self

    def eval(self) -> "Module":
        return self.train(False)

    def forward(self, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        ...

    def __call__(self, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        return self.forward(*args, **kwargs)

    def parameters(self, recurse: bool = True) -> Iterator[Any]:
        return iter([])

    def named_parameters(self, *args: Any, **kwargs: Any) -> Iterator[Any]:
        return iter([])

    def modules(self) -> Iterator["Module"]:
        return iter([self])

    def named_modules(self, *args: Any, **kwargs: Any) -> Iterator[Any]:
        return iter([])

    def children(self) -> Iterator["Module"]:
        return iter([])

    def named_children(self) -> Iterator[Any]:
        return iter([])

    def to(self, *args: Any, **kwargs: Any) -> "Module":
        return self

    def cuda(self, device: Any = None) -> "Module":
        return self

    def cpu(self) -> "Module":
        return self

    def float(self) -> "Module":
        return self

    def half(self) -> "Module":
        return self

    def zero_grad(self, set_to_none: bool = True) -> None:
        ...

    def state_dict(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return {}

    def load_state_dict(self, state_dict: Any, strict: bool = True) -> Any:
        ...

    def register_buffer(self, name: str, tensor: Any, persistent: bool = True) -> None:
        ...

    def register_parameter(self, name: str, param: Any) -> None:
        ...

    def apply(self, fn: Any) -> "Module":
        return self

    def requires_grad_(self, requires_grad: bool = True) -> "Module":
        return self

    def __setattr__(self, name: str, value: Any) -> None:
        object.__setattr__(self, name, value)

    def __getattr__(self, name: str) -> Any:
        raise AttributeError(name)


class Linear(Module):  # pragma: no cover
    weight: Any
    bias: Any

    def __init__(self, in_features: int, out_features: int, bias: bool = True, **kwargs: Any) -> None:
        super().__init__()
        self.weight = None
        self.bias = None


class Sequential(Module):  # pragma: no cover
    def __init__(self, *args: Any) -> None:
        super().__init__()

    def __iter__(self) -> Iterator[Module]:
        return iter([])


class Dropout(Module):  # pragma: no cover
    def __init__(self, p: float = 0.5, inplace: bool = False) -> None:
        super().__init__()


class LayerNorm(Module):  # pragma: no cover
    weight: Any
    bias: Any

    def __init__(self, normalized_shape: Any, eps: float = 1e-5, **kwargs: Any) -> None:
        super().__init__()
        self.weight = None
        self.bias = None


class Embedding(Module):  # pragma: no cover
    weight: Any

    def __init__(self, num_embeddings: int, embedding_dim: int, **kwargs: Any) -> None:
        super().__init__()
        self.weight = None


class GELU(Module):  # pragma: no cover
    def __init__(self, **kwargs: Any) -> None:
        super().__init__()


class ReLU(Module):  # pragma: no cover
    def __init__(self, inplace: bool = False) -> None:
        super().__init__()


class SiLU(Module):  # pragma: no cover
    def __init__(self, inplace: bool = False) -> None:
        super().__init__()


class Tanh(Module):  # pragma: no cover
    def __init__(self) -> None:
        super().__init__()


class Sigmoid(Module):  # pragma: no cover
    def __init__(self) -> None:
        super().__init__()


class Softmax(Module):  # pragma: no cover
    def __init__(self, dim: int = -1) -> None:
        super().__init__()


class LogSoftmax(Module):  # pragma: no cover
    def __init__(self, dim: int = -1) -> None:
        super().__init__()


class ModuleList(Module):  # pragma: no cover
    def __init__(self, modules: Any = None) -> None:
        super().__init__()

    def __iter__(self) -> Iterator[Module]:
        return iter([])

    def __getitem__(self, idx: int) -> Module:
        return Module()

    def __len__(self) -> int:
        return 0

    def append(self, module: Module) -> "ModuleList":
        return self


class MultiheadAttention(Module):  # pragma: no cover
    def __init__(self, embed_dim: int, num_heads: int, **kwargs: Any) -> None:
        super().__init__()


class CrossEntropyLoss(Module):  # pragma: no cover
    def __init__(self, **kwargs: Any) -> None:
        super().__init__()


class MSELoss(Module):  # pragma: no cover
    def __init__(self, **kwargs: Any) -> None:
        super().__init__()


class BCELoss(Module):  # pragma: no cover
    def __init__(self, **kwargs: Any) -> None:
        super().__init__()


class BCEWithLogitsLoss(Module):  # pragma: no cover
    def __init__(self, **kwargs: Any) -> None:
        super().__init__()


class Conv1d(Module):  # pragma: no cover
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__()


class Conv2d(Module):  # pragma: no cover
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__()


class LSTM(Module):  # pragma: no cover
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__()


class GRU(Module):  # pragma: no cover
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__()


class BatchNorm1d(Module):  # pragma: no cover
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__()


class BatchNorm2d(Module):  # pragma: no cover
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__()


class Parameter:  # pragma: no cover
    data: Any
    requires_grad: bool = True

    def __init__(self, data: Any = None, requires_grad: bool = True) -> None:
        self.data = data
        self.requires_grad = requires_grad


# Import functional submodule for torch.nn.functional access
from torch.nn import functional  # noqa: E402, F401


class _InitModule:  # pragma: no cover - nn.init stub
    """Stub for torch.nn.init module."""

    @staticmethod
    def normal_(tensor: Any, mean: float = 0.0, std: float = 1.0) -> Any:
        return tensor

    @staticmethod
    def zeros_(tensor: Any) -> Any:
        return tensor

    @staticmethod
    def ones_(tensor: Any) -> Any:
        return tensor

    @staticmethod
    def constant_(tensor: Any, val: float) -> Any:
        return tensor

    @staticmethod
    def xavier_uniform_(tensor: Any, gain: float = 1.0) -> Any:
        return tensor

    @staticmethod
    def xavier_normal_(tensor: Any, gain: float = 1.0) -> Any:
        return tensor

    @staticmethod
    def kaiming_uniform_(tensor: Any, a: float = 0, mode: str = "fan_in", nonlinearity: str = "leaky_relu") -> Any:
        return tensor

    @staticmethod
    def kaiming_normal_(tensor: Any, a: float = 0, mode: str = "fan_in", nonlinearity: str = "leaky_relu") -> Any:
        return tensor

    @staticmethod
    def uniform_(tensor: Any, a: float = 0.0, b: float = 1.0) -> Any:
        return tensor

    @staticmethod
    def eye_(tensor: Any) -> Any:
        return tensor

    @staticmethod
    def orthogonal_(tensor: Any, gain: float = 1.0) -> Any:
        return tensor


init = _InitModule()  # noqa: F841
