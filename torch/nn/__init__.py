"""Minimal torch.nn stub for type checking and optional dependency safety."""

from __future__ import annotations

from typing import Any, Iterable

from torch import Tensor


class Module:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.training = True
        self._buffers: dict[str, Any] = {}

    def train(self, mode: bool = True) -> "Module":
        self.training = mode
        return self

    def eval(self) -> "Module":
        self.training = False
        return self

    def state_dict(self) -> dict[str, Any]:
        return {}

    def register_buffer(self, name: str, tensor: Any, *args: Any, **kwargs: Any) -> None:
        self._buffers[name] = tensor

    def apply(self, fn: Any) -> "Module":
        fn(self)
        return self

    def parameters(self) -> list[Any]:
        return []

    def to(self, *args: Any, **kwargs: Any) -> "Module":
        return self


class Parameter(Tensor):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class Linear(Module):
    def __init__(
        self,
        in_features: int,
        out_features: int,
        bias: bool = True,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.in_features = in_features
        self.out_features = out_features
        self.bias = bias


class Sequential(Module):
    def __init__(self, *modules: Any) -> None:
        super().__init__()
        self._modules = list(modules)


class Dropout(Module):
    def __init__(self, p: float = 0.5, inplace: bool = False) -> None:
        super().__init__()
        self.p = p
        self.inplace = inplace


class LayerNorm(Module):
    def __init__(
        self,
        normalized_shape: Any,
        eps: float = 1e-5,
        elementwise_affine: bool = True,
    ) -> None:
        super().__init__()
        self.normalized_shape = normalized_shape
        self.eps = eps
        self.elementwise_affine = elementwise_affine


class Embedding(Module):
    def __init__(self, num_embeddings: int, embedding_dim: int, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.num_embeddings = num_embeddings
        self.embedding_dim = embedding_dim


class GELU(Module):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ReLU(Module):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class Tanh(Module):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class Sigmoid(Module):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModuleList(Module):
    def __init__(self, modules: Iterable[Any] | None = None) -> None:
        super().__init__()
        self._modules = list(modules or [])


class MultiheadAttention(Module):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__()


class CrossEntropyLoss(Module):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__()


class MSELoss(Module):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__()


class BCELoss(Module):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__()


class BCEWithLogitsLoss(Module):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__()


class Conv1d(Module):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__()


class Conv2d(Module):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__()


class LSTM(Module):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__()


class GRU(Module):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__()


class BatchNorm1d(Module):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__()


class BatchNorm2d(Module):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__()


class functional:
    pass


__all__ = [
    "Module",
    "Linear",
    "Sequential",
    "Dropout",
    "LayerNorm",
    "Embedding",
    "GELU",
    "ReLU",
    "Tanh",
    "Sigmoid",
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
    "BatchNorm1d",
    "BatchNorm2d",
    "Parameter",
    "functional",
]
