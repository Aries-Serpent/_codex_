"""Convenience wrapper for HuggingFace causal language models."""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module, util
from typing import Any, Mapping

_VALID_DTYPES = {"fp32", "fp16", "bf16"}
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


def x__resolve_device__mutmut_orig(torch_module: Any, device: str) -> str:
    if device != "auto":
        return device
    cuda = getattr(torch_module, "cuda", None)
    if cuda is not None and callable(getattr(cuda, "is_available", None)):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "cuda"
    return "cpu"


def x__resolve_device__mutmut_1(torch_module: Any, device: str) -> str:
    if device == "auto":
        return device
    cuda = getattr(torch_module, "cuda", None)
    if cuda is not None and callable(getattr(cuda, "is_available", None)):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "cuda"
    return "cpu"


def x__resolve_device__mutmut_2(torch_module: Any, device: str) -> str:
    if device != "XXautoXX":
        return device
    cuda = getattr(torch_module, "cuda", None)
    if cuda is not None and callable(getattr(cuda, "is_available", None)):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "cuda"
    return "cpu"


def x__resolve_device__mutmut_3(torch_module: Any, device: str) -> str:
    if device != "AUTO":
        return device
    cuda = getattr(torch_module, "cuda", None)
    if cuda is not None and callable(getattr(cuda, "is_available", None)):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "cuda"
    return "cpu"


def x__resolve_device__mutmut_4(torch_module: Any, device: str) -> str:
    if device != "auto":
        return device
    cuda = None
    if cuda is not None and callable(getattr(cuda, "is_available", None)):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "cuda"
    return "cpu"


def x__resolve_device__mutmut_5(torch_module: Any, device: str) -> str:
    if device != "auto":
        return device
    cuda = getattr(None, "cuda", None)
    if cuda is not None and callable(getattr(cuda, "is_available", None)):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "cuda"
    return "cpu"


def x__resolve_device__mutmut_6(torch_module: Any, device: str) -> str:
    if device != "auto":
        return device
    cuda = getattr(torch_module, None, None)
    if cuda is not None and callable(getattr(cuda, "is_available", None)):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "cuda"
    return "cpu"


def x__resolve_device__mutmut_7(torch_module: Any, device: str) -> str:
    if device != "auto":
        return device
    cuda = getattr("cuda", None)
    if cuda is not None and callable(getattr(cuda, "is_available", None)):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "cuda"
    return "cpu"


def x__resolve_device__mutmut_8(torch_module: Any, device: str) -> str:
    if device != "auto":
        return device
    cuda = getattr(torch_module, None)
    if cuda is not None and callable(getattr(cuda, "is_available", None)):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "cuda"
    return "cpu"


def x__resolve_device__mutmut_9(torch_module: Any, device: str) -> str:
    if device != "auto":
        return device
    cuda = getattr(torch_module, "cuda", )
    if cuda is not None and callable(getattr(cuda, "is_available", None)):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "cuda"
    return "cpu"


def x__resolve_device__mutmut_10(torch_module: Any, device: str) -> str:
    if device != "auto":
        return device
    cuda = getattr(torch_module, "XXcudaXX", None)
    if cuda is not None and callable(getattr(cuda, "is_available", None)):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "cuda"
    return "cpu"


def x__resolve_device__mutmut_11(torch_module: Any, device: str) -> str:
    if device != "auto":
        return device
    cuda = getattr(torch_module, "CUDA", None)
    if cuda is not None and callable(getattr(cuda, "is_available", None)):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "cuda"
    return "cpu"


def x__resolve_device__mutmut_12(torch_module: Any, device: str) -> str:
    if device != "auto":
        return device
    cuda = getattr(torch_module, "cuda", None)
    if cuda is not None or callable(getattr(cuda, "is_available", None)):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "cuda"
    return "cpu"


def x__resolve_device__mutmut_13(torch_module: Any, device: str) -> str:
    if device != "auto":
        return device
    cuda = getattr(torch_module, "cuda", None)
    if cuda is None and callable(getattr(cuda, "is_available", None)):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "cuda"
    return "cpu"


def x__resolve_device__mutmut_14(torch_module: Any, device: str) -> str:
    if device != "auto":
        return device
    cuda = getattr(torch_module, "cuda", None)
    if cuda is not None and callable(None):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "cuda"
    return "cpu"


def x__resolve_device__mutmut_15(torch_module: Any, device: str) -> str:
    if device != "auto":
        return device
    cuda = getattr(torch_module, "cuda", None)
    if cuda is not None and callable(getattr(None, "is_available", None)):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "cuda"
    return "cpu"


def x__resolve_device__mutmut_16(torch_module: Any, device: str) -> str:
    if device != "auto":
        return device
    cuda = getattr(torch_module, "cuda", None)
    if cuda is not None and callable(getattr(cuda, None, None)):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "cuda"
    return "cpu"


def x__resolve_device__mutmut_17(torch_module: Any, device: str) -> str:
    if device != "auto":
        return device
    cuda = getattr(torch_module, "cuda", None)
    if cuda is not None and callable(getattr("is_available", None)):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "cuda"
    return "cpu"


def x__resolve_device__mutmut_18(torch_module: Any, device: str) -> str:
    if device != "auto":
        return device
    cuda = getattr(torch_module, "cuda", None)
    if cuda is not None and callable(getattr(cuda, None)):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "cuda"
    return "cpu"


def x__resolve_device__mutmut_19(torch_module: Any, device: str) -> str:
    if device != "auto":
        return device
    cuda = getattr(torch_module, "cuda", None)
    if cuda is not None and callable(getattr(cuda, "is_available", )):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "cuda"
    return "cpu"


def x__resolve_device__mutmut_20(torch_module: Any, device: str) -> str:
    if device != "auto":
        return device
    cuda = getattr(torch_module, "cuda", None)
    if cuda is not None and callable(getattr(cuda, "XXis_availableXX", None)):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "cuda"
    return "cpu"


def x__resolve_device__mutmut_21(torch_module: Any, device: str) -> str:
    if device != "auto":
        return device
    cuda = getattr(torch_module, "cuda", None)
    if cuda is not None and callable(getattr(cuda, "IS_AVAILABLE", None)):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "cuda"
    return "cpu"


def x__resolve_device__mutmut_22(torch_module: Any, device: str) -> str:
    if device != "auto":
        return device
    cuda = getattr(torch_module, "cuda", None)
    if cuda is not None and callable(getattr(cuda, "is_available", None)):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "XXcudaXX"
    return "cpu"


def x__resolve_device__mutmut_23(torch_module: Any, device: str) -> str:
    if device != "auto":
        return device
    cuda = getattr(torch_module, "cuda", None)
    if cuda is not None and callable(getattr(cuda, "is_available", None)):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "CUDA"
    return "cpu"


def x__resolve_device__mutmut_24(torch_module: Any, device: str) -> str:
    if device != "auto":
        return device
    cuda = getattr(torch_module, "cuda", None)
    if cuda is not None and callable(getattr(cuda, "is_available", None)):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "cuda"
    return "XXcpuXX"


def x__resolve_device__mutmut_25(torch_module: Any, device: str) -> str:
    if device != "auto":
        return device
    cuda = getattr(torch_module, "cuda", None)
    if cuda is not None and callable(getattr(cuda, "is_available", None)):
        if cuda.is_available():  # pragma: no cover - depends on runtime CUDA
            return "cuda"
    return "CPU"

x__resolve_device__mutmut_mutants : ClassVar[MutantDict] = {
'x__resolve_device__mutmut_1': x__resolve_device__mutmut_1, 
    'x__resolve_device__mutmut_2': x__resolve_device__mutmut_2, 
    'x__resolve_device__mutmut_3': x__resolve_device__mutmut_3, 
    'x__resolve_device__mutmut_4': x__resolve_device__mutmut_4, 
    'x__resolve_device__mutmut_5': x__resolve_device__mutmut_5, 
    'x__resolve_device__mutmut_6': x__resolve_device__mutmut_6, 
    'x__resolve_device__mutmut_7': x__resolve_device__mutmut_7, 
    'x__resolve_device__mutmut_8': x__resolve_device__mutmut_8, 
    'x__resolve_device__mutmut_9': x__resolve_device__mutmut_9, 
    'x__resolve_device__mutmut_10': x__resolve_device__mutmut_10, 
    'x__resolve_device__mutmut_11': x__resolve_device__mutmut_11, 
    'x__resolve_device__mutmut_12': x__resolve_device__mutmut_12, 
    'x__resolve_device__mutmut_13': x__resolve_device__mutmut_13, 
    'x__resolve_device__mutmut_14': x__resolve_device__mutmut_14, 
    'x__resolve_device__mutmut_15': x__resolve_device__mutmut_15, 
    'x__resolve_device__mutmut_16': x__resolve_device__mutmut_16, 
    'x__resolve_device__mutmut_17': x__resolve_device__mutmut_17, 
    'x__resolve_device__mutmut_18': x__resolve_device__mutmut_18, 
    'x__resolve_device__mutmut_19': x__resolve_device__mutmut_19, 
    'x__resolve_device__mutmut_20': x__resolve_device__mutmut_20, 
    'x__resolve_device__mutmut_21': x__resolve_device__mutmut_21, 
    'x__resolve_device__mutmut_22': x__resolve_device__mutmut_22, 
    'x__resolve_device__mutmut_23': x__resolve_device__mutmut_23, 
    'x__resolve_device__mutmut_24': x__resolve_device__mutmut_24, 
    'x__resolve_device__mutmut_25': x__resolve_device__mutmut_25
}

def _resolve_device(*args, **kwargs):
    result = _mutmut_trampoline(x__resolve_device__mutmut_orig, x__resolve_device__mutmut_mutants, args, kwargs)
    return result 

_resolve_device.__signature__ = _mutmut_signature(x__resolve_device__mutmut_orig)
x__resolve_device__mutmut_orig.__name__ = 'x__resolve_device'


def x__dtype_map__mutmut_orig(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr(torch_module, "float32", None),
        "fp16": getattr(torch_module, "float16", None),
        "bf16": getattr(torch_module, "bfloat16", None),
    }


def x__dtype_map__mutmut_1(torch_module: Any) -> dict[str, Any]:
    return {
        "XXfp32XX": getattr(torch_module, "float32", None),
        "fp16": getattr(torch_module, "float16", None),
        "bf16": getattr(torch_module, "bfloat16", None),
    }


def x__dtype_map__mutmut_2(torch_module: Any) -> dict[str, Any]:
    return {
        "FP32": getattr(torch_module, "float32", None),
        "fp16": getattr(torch_module, "float16", None),
        "bf16": getattr(torch_module, "bfloat16", None),
    }


def x__dtype_map__mutmut_3(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr(None, "float32", None),
        "fp16": getattr(torch_module, "float16", None),
        "bf16": getattr(torch_module, "bfloat16", None),
    }


def x__dtype_map__mutmut_4(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr(torch_module, None, None),
        "fp16": getattr(torch_module, "float16", None),
        "bf16": getattr(torch_module, "bfloat16", None),
    }


def x__dtype_map__mutmut_5(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr("float32", None),
        "fp16": getattr(torch_module, "float16", None),
        "bf16": getattr(torch_module, "bfloat16", None),
    }


def x__dtype_map__mutmut_6(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr(torch_module, None),
        "fp16": getattr(torch_module, "float16", None),
        "bf16": getattr(torch_module, "bfloat16", None),
    }


def x__dtype_map__mutmut_7(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr(torch_module, "float32", ),
        "fp16": getattr(torch_module, "float16", None),
        "bf16": getattr(torch_module, "bfloat16", None),
    }


def x__dtype_map__mutmut_8(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr(torch_module, "XXfloat32XX", None),
        "fp16": getattr(torch_module, "float16", None),
        "bf16": getattr(torch_module, "bfloat16", None),
    }


def x__dtype_map__mutmut_9(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr(torch_module, "FLOAT32", None),
        "fp16": getattr(torch_module, "float16", None),
        "bf16": getattr(torch_module, "bfloat16", None),
    }


def x__dtype_map__mutmut_10(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr(torch_module, "float32", None),
        "XXfp16XX": getattr(torch_module, "float16", None),
        "bf16": getattr(torch_module, "bfloat16", None),
    }


def x__dtype_map__mutmut_11(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr(torch_module, "float32", None),
        "FP16": getattr(torch_module, "float16", None),
        "bf16": getattr(torch_module, "bfloat16", None),
    }


def x__dtype_map__mutmut_12(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr(torch_module, "float32", None),
        "fp16": getattr(None, "float16", None),
        "bf16": getattr(torch_module, "bfloat16", None),
    }


def x__dtype_map__mutmut_13(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr(torch_module, "float32", None),
        "fp16": getattr(torch_module, None, None),
        "bf16": getattr(torch_module, "bfloat16", None),
    }


def x__dtype_map__mutmut_14(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr(torch_module, "float32", None),
        "fp16": getattr("float16", None),
        "bf16": getattr(torch_module, "bfloat16", None),
    }


def x__dtype_map__mutmut_15(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr(torch_module, "float32", None),
        "fp16": getattr(torch_module, None),
        "bf16": getattr(torch_module, "bfloat16", None),
    }


def x__dtype_map__mutmut_16(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr(torch_module, "float32", None),
        "fp16": getattr(torch_module, "float16", ),
        "bf16": getattr(torch_module, "bfloat16", None),
    }


def x__dtype_map__mutmut_17(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr(torch_module, "float32", None),
        "fp16": getattr(torch_module, "XXfloat16XX", None),
        "bf16": getattr(torch_module, "bfloat16", None),
    }


def x__dtype_map__mutmut_18(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr(torch_module, "float32", None),
        "fp16": getattr(torch_module, "FLOAT16", None),
        "bf16": getattr(torch_module, "bfloat16", None),
    }


def x__dtype_map__mutmut_19(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr(torch_module, "float32", None),
        "fp16": getattr(torch_module, "float16", None),
        "XXbf16XX": getattr(torch_module, "bfloat16", None),
    }


def x__dtype_map__mutmut_20(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr(torch_module, "float32", None),
        "fp16": getattr(torch_module, "float16", None),
        "BF16": getattr(torch_module, "bfloat16", None),
    }


def x__dtype_map__mutmut_21(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr(torch_module, "float32", None),
        "fp16": getattr(torch_module, "float16", None),
        "bf16": getattr(None, "bfloat16", None),
    }


def x__dtype_map__mutmut_22(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr(torch_module, "float32", None),
        "fp16": getattr(torch_module, "float16", None),
        "bf16": getattr(torch_module, None, None),
    }


def x__dtype_map__mutmut_23(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr(torch_module, "float32", None),
        "fp16": getattr(torch_module, "float16", None),
        "bf16": getattr("bfloat16", None),
    }


def x__dtype_map__mutmut_24(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr(torch_module, "float32", None),
        "fp16": getattr(torch_module, "float16", None),
        "bf16": getattr(torch_module, None),
    }


def x__dtype_map__mutmut_25(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr(torch_module, "float32", None),
        "fp16": getattr(torch_module, "float16", None),
        "bf16": getattr(torch_module, "bfloat16", ),
    }


def x__dtype_map__mutmut_26(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr(torch_module, "float32", None),
        "fp16": getattr(torch_module, "float16", None),
        "bf16": getattr(torch_module, "XXbfloat16XX", None),
    }


def x__dtype_map__mutmut_27(torch_module: Any) -> dict[str, Any]:
    return {
        "fp32": getattr(torch_module, "float32", None),
        "fp16": getattr(torch_module, "float16", None),
        "bf16": getattr(torch_module, "BFLOAT16", None),
    }

x__dtype_map__mutmut_mutants : ClassVar[MutantDict] = {
'x__dtype_map__mutmut_1': x__dtype_map__mutmut_1, 
    'x__dtype_map__mutmut_2': x__dtype_map__mutmut_2, 
    'x__dtype_map__mutmut_3': x__dtype_map__mutmut_3, 
    'x__dtype_map__mutmut_4': x__dtype_map__mutmut_4, 
    'x__dtype_map__mutmut_5': x__dtype_map__mutmut_5, 
    'x__dtype_map__mutmut_6': x__dtype_map__mutmut_6, 
    'x__dtype_map__mutmut_7': x__dtype_map__mutmut_7, 
    'x__dtype_map__mutmut_8': x__dtype_map__mutmut_8, 
    'x__dtype_map__mutmut_9': x__dtype_map__mutmut_9, 
    'x__dtype_map__mutmut_10': x__dtype_map__mutmut_10, 
    'x__dtype_map__mutmut_11': x__dtype_map__mutmut_11, 
    'x__dtype_map__mutmut_12': x__dtype_map__mutmut_12, 
    'x__dtype_map__mutmut_13': x__dtype_map__mutmut_13, 
    'x__dtype_map__mutmut_14': x__dtype_map__mutmut_14, 
    'x__dtype_map__mutmut_15': x__dtype_map__mutmut_15, 
    'x__dtype_map__mutmut_16': x__dtype_map__mutmut_16, 
    'x__dtype_map__mutmut_17': x__dtype_map__mutmut_17, 
    'x__dtype_map__mutmut_18': x__dtype_map__mutmut_18, 
    'x__dtype_map__mutmut_19': x__dtype_map__mutmut_19, 
    'x__dtype_map__mutmut_20': x__dtype_map__mutmut_20, 
    'x__dtype_map__mutmut_21': x__dtype_map__mutmut_21, 
    'x__dtype_map__mutmut_22': x__dtype_map__mutmut_22, 
    'x__dtype_map__mutmut_23': x__dtype_map__mutmut_23, 
    'x__dtype_map__mutmut_24': x__dtype_map__mutmut_24, 
    'x__dtype_map__mutmut_25': x__dtype_map__mutmut_25, 
    'x__dtype_map__mutmut_26': x__dtype_map__mutmut_26, 
    'x__dtype_map__mutmut_27': x__dtype_map__mutmut_27
}

def _dtype_map(*args, **kwargs):
    result = _mutmut_trampoline(x__dtype_map__mutmut_orig, x__dtype_map__mutmut_mutants, args, kwargs)
    return result 

_dtype_map.__signature__ = _mutmut_signature(x__dtype_map__mutmut_orig)
x__dtype_map__mutmut_orig.__name__ = 'x__dtype_map'


def x__encoding_to_inputs__mutmut_orig(batch: Any) -> Mapping[str, Any]:
    if isinstance(batch, Mapping):
        return batch
    data = getattr(batch, "data", None)
    if isinstance(data, Mapping):
        return data
    raise TypeError(f"Unsupported tokenizer output type: {type(batch)!r}")


def x__encoding_to_inputs__mutmut_1(batch: Any) -> Mapping[str, Any]:
    if isinstance(batch, Mapping):
        return batch
    data = None
    if isinstance(data, Mapping):
        return data
    raise TypeError(f"Unsupported tokenizer output type: {type(batch)!r}")


def x__encoding_to_inputs__mutmut_2(batch: Any) -> Mapping[str, Any]:
    if isinstance(batch, Mapping):
        return batch
    data = getattr(None, "data", None)
    if isinstance(data, Mapping):
        return data
    raise TypeError(f"Unsupported tokenizer output type: {type(batch)!r}")


def x__encoding_to_inputs__mutmut_3(batch: Any) -> Mapping[str, Any]:
    if isinstance(batch, Mapping):
        return batch
    data = getattr(batch, None, None)
    if isinstance(data, Mapping):
        return data
    raise TypeError(f"Unsupported tokenizer output type: {type(batch)!r}")


def x__encoding_to_inputs__mutmut_4(batch: Any) -> Mapping[str, Any]:
    if isinstance(batch, Mapping):
        return batch
    data = getattr("data", None)
    if isinstance(data, Mapping):
        return data
    raise TypeError(f"Unsupported tokenizer output type: {type(batch)!r}")


def x__encoding_to_inputs__mutmut_5(batch: Any) -> Mapping[str, Any]:
    if isinstance(batch, Mapping):
        return batch
    data = getattr(batch, None)
    if isinstance(data, Mapping):
        return data
    raise TypeError(f"Unsupported tokenizer output type: {type(batch)!r}")


def x__encoding_to_inputs__mutmut_6(batch: Any) -> Mapping[str, Any]:
    if isinstance(batch, Mapping):
        return batch
    data = getattr(batch, "data", )
    if isinstance(data, Mapping):
        return data
    raise TypeError(f"Unsupported tokenizer output type: {type(batch)!r}")


def x__encoding_to_inputs__mutmut_7(batch: Any) -> Mapping[str, Any]:
    if isinstance(batch, Mapping):
        return batch
    data = getattr(batch, "XXdataXX", None)
    if isinstance(data, Mapping):
        return data
    raise TypeError(f"Unsupported tokenizer output type: {type(batch)!r}")


def x__encoding_to_inputs__mutmut_8(batch: Any) -> Mapping[str, Any]:
    if isinstance(batch, Mapping):
        return batch
    data = getattr(batch, "DATA", None)
    if isinstance(data, Mapping):
        return data
    raise TypeError(f"Unsupported tokenizer output type: {type(batch)!r}")


def x__encoding_to_inputs__mutmut_9(batch: Any) -> Mapping[str, Any]:
    if isinstance(batch, Mapping):
        return batch
    data = getattr(batch, "data", None)
    if isinstance(data, Mapping):
        return data
    raise TypeError(None)


def x__encoding_to_inputs__mutmut_10(batch: Any) -> Mapping[str, Any]:
    if isinstance(batch, Mapping):
        return batch
    data = getattr(batch, "data", None)
    if isinstance(data, Mapping):
        return data
    raise TypeError(f"Unsupported tokenizer output type: {type(None)!r}")

x__encoding_to_inputs__mutmut_mutants : ClassVar[MutantDict] = {
'x__encoding_to_inputs__mutmut_1': x__encoding_to_inputs__mutmut_1, 
    'x__encoding_to_inputs__mutmut_2': x__encoding_to_inputs__mutmut_2, 
    'x__encoding_to_inputs__mutmut_3': x__encoding_to_inputs__mutmut_3, 
    'x__encoding_to_inputs__mutmut_4': x__encoding_to_inputs__mutmut_4, 
    'x__encoding_to_inputs__mutmut_5': x__encoding_to_inputs__mutmut_5, 
    'x__encoding_to_inputs__mutmut_6': x__encoding_to_inputs__mutmut_6, 
    'x__encoding_to_inputs__mutmut_7': x__encoding_to_inputs__mutmut_7, 
    'x__encoding_to_inputs__mutmut_8': x__encoding_to_inputs__mutmut_8, 
    'x__encoding_to_inputs__mutmut_9': x__encoding_to_inputs__mutmut_9, 
    'x__encoding_to_inputs__mutmut_10': x__encoding_to_inputs__mutmut_10
}

def _encoding_to_inputs(*args, **kwargs):
    result = _mutmut_trampoline(x__encoding_to_inputs__mutmut_orig, x__encoding_to_inputs__mutmut_mutants, args, kwargs)
    return result 

_encoding_to_inputs.__signature__ = _mutmut_signature(x__encoding_to_inputs__mutmut_orig)
x__encoding_to_inputs__mutmut_orig.__name__ = 'x__encoding_to_inputs'


@dataclass
class ChatModelConfig:
    """Configuration describing how to instantiate :class:`ChatModel`."""

    model_name: str = "sshleifer/tiny-gpt2"
    tokenizer_name: str | None = None
    dtype: str = "fp32"
    device: str = "auto"
    use_lora: bool = False
    lora_r: int | None = None
    lora_alpha: float | None = None
    lora_dropout: float | None = None
    lora_target_modules: tuple[str, ...] | None = None
    generation_kwargs: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        errors: list[str] = []
        if self.dtype not in _VALID_DTYPES:
            errors.append(f"dtype must be one of {sorted(_VALID_DTYPES)}")
        if self.use_lora and self.lora_r is not None and self.lora_r <= 0:
            errors.append("lora_r must be positive when use_lora is enabled")
        if errors:
            raise ValueError("; ".join(errors))

    def resolved_tokenizer_name(self) -> str:
        return self.tokenizer_name or self.model_name


class ChatModel:
    """High-level helper that owns a model, tokenizer and generation defaults."""

    def xǁChatModelǁ__init____mutmut_orig(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_1(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = None
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_2(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = None
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_3(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module(None)
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_4(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("XXtorchXX")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_5(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("TORCH")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_6(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = None
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_7(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module(None)
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_8(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("XXtransformersXX")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_9(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("TRANSFORMERS")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_10(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = None
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_11(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(None, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_12(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, None)
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_13(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr("AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_14(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, )
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_15(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "XXAutoModelForCausalLMXX")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_16(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "automodelforcausallm")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_17(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AUTOMODELFORCAUSALLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_18(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = None

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_19(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(None, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_20(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, None)

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_21(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr("AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_22(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, )

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_23(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "XXAutoTokenizerXX")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_24(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "autotokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_25(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AUTOTOKENIZER")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_26(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = None
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_27(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(None)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_28(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = None
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_29(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(None)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_30(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = None
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_31(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"XXtorch_dtypeXX": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_32(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"TORCH_DTYPE": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_33(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_34(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = None
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_35(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(None, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_36(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(**model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_37(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, )
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_38(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = None
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_39(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(None, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_40(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, None)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_41(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_42(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, )
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_43(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(None, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_44(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, None):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_45(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr("to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_46(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, ):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_47(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "XXtoXX"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_48(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "TO"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_49(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = None
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_50(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(None)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_51(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = None
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_52(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(None)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_53(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = None

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_54(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(None)

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_55(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = None
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_56(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = None
        self._device = resolved_device
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_57(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = None
        self._dtype = dtype

    def xǁChatModelǁ__init____mutmut_58(self, cfg: ChatModelConfig) -> None:
        cfg.validate()
        self.cfg = cfg
        torch_module = import_module("torch")
        transformers_module = import_module("transformers")
        auto_model = getattr(transformers_module, "AutoModelForCausalLM")
        auto_tokenizer = getattr(transformers_module, "AutoTokenizer")

        dtype_lookup = _dtype_map(torch_module)
        dtype = dtype_lookup.get(cfg.dtype)
        model_kwargs = {"torch_dtype": dtype} if dtype is not None else {}
        model = auto_model.from_pretrained(cfg.model_name, **model_kwargs)
        resolved_device = _resolve_device(torch_module, cfg.device)
        if hasattr(model, "to"):
            model = model.to(resolved_device)
        if cfg.use_lora:
            model = self._apply_lora(model)
        tokenizer = auto_tokenizer.from_pretrained(cfg.resolved_tokenizer_name())

        self.model = model
        self.tokenizer = tokenizer
        self._device = resolved_device
        self._dtype = None
    
    xǁChatModelǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁChatModelǁ__init____mutmut_1': xǁChatModelǁ__init____mutmut_1, 
        'xǁChatModelǁ__init____mutmut_2': xǁChatModelǁ__init____mutmut_2, 
        'xǁChatModelǁ__init____mutmut_3': xǁChatModelǁ__init____mutmut_3, 
        'xǁChatModelǁ__init____mutmut_4': xǁChatModelǁ__init____mutmut_4, 
        'xǁChatModelǁ__init____mutmut_5': xǁChatModelǁ__init____mutmut_5, 
        'xǁChatModelǁ__init____mutmut_6': xǁChatModelǁ__init____mutmut_6, 
        'xǁChatModelǁ__init____mutmut_7': xǁChatModelǁ__init____mutmut_7, 
        'xǁChatModelǁ__init____mutmut_8': xǁChatModelǁ__init____mutmut_8, 
        'xǁChatModelǁ__init____mutmut_9': xǁChatModelǁ__init____mutmut_9, 
        'xǁChatModelǁ__init____mutmut_10': xǁChatModelǁ__init____mutmut_10, 
        'xǁChatModelǁ__init____mutmut_11': xǁChatModelǁ__init____mutmut_11, 
        'xǁChatModelǁ__init____mutmut_12': xǁChatModelǁ__init____mutmut_12, 
        'xǁChatModelǁ__init____mutmut_13': xǁChatModelǁ__init____mutmut_13, 
        'xǁChatModelǁ__init____mutmut_14': xǁChatModelǁ__init____mutmut_14, 
        'xǁChatModelǁ__init____mutmut_15': xǁChatModelǁ__init____mutmut_15, 
        'xǁChatModelǁ__init____mutmut_16': xǁChatModelǁ__init____mutmut_16, 
        'xǁChatModelǁ__init____mutmut_17': xǁChatModelǁ__init____mutmut_17, 
        'xǁChatModelǁ__init____mutmut_18': xǁChatModelǁ__init____mutmut_18, 
        'xǁChatModelǁ__init____mutmut_19': xǁChatModelǁ__init____mutmut_19, 
        'xǁChatModelǁ__init____mutmut_20': xǁChatModelǁ__init____mutmut_20, 
        'xǁChatModelǁ__init____mutmut_21': xǁChatModelǁ__init____mutmut_21, 
        'xǁChatModelǁ__init____mutmut_22': xǁChatModelǁ__init____mutmut_22, 
        'xǁChatModelǁ__init____mutmut_23': xǁChatModelǁ__init____mutmut_23, 
        'xǁChatModelǁ__init____mutmut_24': xǁChatModelǁ__init____mutmut_24, 
        'xǁChatModelǁ__init____mutmut_25': xǁChatModelǁ__init____mutmut_25, 
        'xǁChatModelǁ__init____mutmut_26': xǁChatModelǁ__init____mutmut_26, 
        'xǁChatModelǁ__init____mutmut_27': xǁChatModelǁ__init____mutmut_27, 
        'xǁChatModelǁ__init____mutmut_28': xǁChatModelǁ__init____mutmut_28, 
        'xǁChatModelǁ__init____mutmut_29': xǁChatModelǁ__init____mutmut_29, 
        'xǁChatModelǁ__init____mutmut_30': xǁChatModelǁ__init____mutmut_30, 
        'xǁChatModelǁ__init____mutmut_31': xǁChatModelǁ__init____mutmut_31, 
        'xǁChatModelǁ__init____mutmut_32': xǁChatModelǁ__init____mutmut_32, 
        'xǁChatModelǁ__init____mutmut_33': xǁChatModelǁ__init____mutmut_33, 
        'xǁChatModelǁ__init____mutmut_34': xǁChatModelǁ__init____mutmut_34, 
        'xǁChatModelǁ__init____mutmut_35': xǁChatModelǁ__init____mutmut_35, 
        'xǁChatModelǁ__init____mutmut_36': xǁChatModelǁ__init____mutmut_36, 
        'xǁChatModelǁ__init____mutmut_37': xǁChatModelǁ__init____mutmut_37, 
        'xǁChatModelǁ__init____mutmut_38': xǁChatModelǁ__init____mutmut_38, 
        'xǁChatModelǁ__init____mutmut_39': xǁChatModelǁ__init____mutmut_39, 
        'xǁChatModelǁ__init____mutmut_40': xǁChatModelǁ__init____mutmut_40, 
        'xǁChatModelǁ__init____mutmut_41': xǁChatModelǁ__init____mutmut_41, 
        'xǁChatModelǁ__init____mutmut_42': xǁChatModelǁ__init____mutmut_42, 
        'xǁChatModelǁ__init____mutmut_43': xǁChatModelǁ__init____mutmut_43, 
        'xǁChatModelǁ__init____mutmut_44': xǁChatModelǁ__init____mutmut_44, 
        'xǁChatModelǁ__init____mutmut_45': xǁChatModelǁ__init____mutmut_45, 
        'xǁChatModelǁ__init____mutmut_46': xǁChatModelǁ__init____mutmut_46, 
        'xǁChatModelǁ__init____mutmut_47': xǁChatModelǁ__init____mutmut_47, 
        'xǁChatModelǁ__init____mutmut_48': xǁChatModelǁ__init____mutmut_48, 
        'xǁChatModelǁ__init____mutmut_49': xǁChatModelǁ__init____mutmut_49, 
        'xǁChatModelǁ__init____mutmut_50': xǁChatModelǁ__init____mutmut_50, 
        'xǁChatModelǁ__init____mutmut_51': xǁChatModelǁ__init____mutmut_51, 
        'xǁChatModelǁ__init____mutmut_52': xǁChatModelǁ__init____mutmut_52, 
        'xǁChatModelǁ__init____mutmut_53': xǁChatModelǁ__init____mutmut_53, 
        'xǁChatModelǁ__init____mutmut_54': xǁChatModelǁ__init____mutmut_54, 
        'xǁChatModelǁ__init____mutmut_55': xǁChatModelǁ__init____mutmut_55, 
        'xǁChatModelǁ__init____mutmut_56': xǁChatModelǁ__init____mutmut_56, 
        'xǁChatModelǁ__init____mutmut_57': xǁChatModelǁ__init____mutmut_57, 
        'xǁChatModelǁ__init____mutmut_58': xǁChatModelǁ__init____mutmut_58
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁChatModelǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁChatModelǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁChatModelǁ__init____mutmut_orig)
    xǁChatModelǁ__init____mutmut_orig.__name__ = 'xǁChatModelǁ__init__'

    def xǁChatModelǁ_apply_lora__mutmut_orig(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_1(self, model: Any) -> Any:
        spec = None
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_2(self, model: Any) -> Any:
        spec = util.find_spec(None)
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_3(self, model: Any) -> Any:
        spec = util.find_spec("XXpeftXX")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_4(self, model: Any) -> Any:
        spec = util.find_spec("PEFT")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_5(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is not None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_6(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError(None)
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_7(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("XXLoRA requested but the 'peft' package is not installedXX")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_8(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("lora requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_9(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LORA REQUESTED BUT THE 'PEFT' PACKAGE IS NOT INSTALLED")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_10(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = None
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_11(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module(None)
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_12(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("XXpeftXX")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_13(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("PEFT")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_14(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = None
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_15(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(None, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_16(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, None)
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_17(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr("LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_18(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, )
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_19(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "XXLoraConfigXX")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_20(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "loraconfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_21(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LORACONFIG")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_22(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = None
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_23(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(None, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_24(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, None)
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_25(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr("get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_26(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, )
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_27(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "XXget_peft_modelXX")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_28(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "GET_PEFT_MODEL")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_29(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = ""
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_30(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(None, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_31(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, None):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_32(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr("TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_33(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, ):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_34(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "XXTaskTypeXX"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_35(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "tasktype"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_36(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TASKTYPE"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_37(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = None
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_38(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(None, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_39(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, None, None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_40(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr("CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_41(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_42(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", )
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_43(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "XXCAUSAL_LMXX", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_44(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "causal_lm", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_45(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = None
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_46(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "XXrXX": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_47(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "R": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_48(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r and 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_49(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 9,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_50(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "XXlora_alphaXX": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_51(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "LORA_ALPHA": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_52(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha and 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_53(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 17,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_54(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "XXlora_dropoutXX": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_55(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "LORA_DROPOUT": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_56(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout and 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_57(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 1.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_58(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "XXbiasXX": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_59(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "BIAS": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_60(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "XXnoneXX",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_61(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "NONE",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_62(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_63(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = None
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_64(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["XXtarget_modulesXX"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_65(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["TARGET_MODULES"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_66(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(None)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_67(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_68(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = None
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_69(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["XXtask_typeXX"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_70(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["TASK_TYPE"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_71(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = None
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_72(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["XXtask_typeXX"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_73(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["TASK_TYPE"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_74(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "XXCAUSAL_LMXX"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_75(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "causal_lm"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_76(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = None
        return get_peft_model(model, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_77(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(None, lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_78(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, None)

    def xǁChatModelǁ_apply_lora__mutmut_79(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(lora_config)

    def xǁChatModelǁ_apply_lora__mutmut_80(self, model: Any) -> Any:
        spec = util.find_spec("peft")
        if spec is None:
            raise ImportError("LoRA requested but the 'peft' package is not installed")
        peft_module = import_module("peft")
        lora_config_cls = getattr(peft_module, "LoraConfig")
        get_peft_model = getattr(peft_module, "get_peft_model")
        task_type = None
        if hasattr(peft_module, "TaskType"):
            task_type = getattr(peft_module.TaskType, "CAUSAL_LM", None)
        config_kwargs = {
            "r": self.cfg.lora_r or 8,
            "lora_alpha": self.cfg.lora_alpha or 16,
            "lora_dropout": self.cfg.lora_dropout or 0.0,
            "bias": "none",
        }
        if self.cfg.lora_target_modules is not None:
            config_kwargs["target_modules"] = list(self.cfg.lora_target_modules)
        if task_type is not None:
            config_kwargs["task_type"] = task_type
        else:
            config_kwargs["task_type"] = "CAUSAL_LM"
        lora_config = lora_config_cls(**config_kwargs)
        return get_peft_model(model, )
    
    xǁChatModelǁ_apply_lora__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁChatModelǁ_apply_lora__mutmut_1': xǁChatModelǁ_apply_lora__mutmut_1, 
        'xǁChatModelǁ_apply_lora__mutmut_2': xǁChatModelǁ_apply_lora__mutmut_2, 
        'xǁChatModelǁ_apply_lora__mutmut_3': xǁChatModelǁ_apply_lora__mutmut_3, 
        'xǁChatModelǁ_apply_lora__mutmut_4': xǁChatModelǁ_apply_lora__mutmut_4, 
        'xǁChatModelǁ_apply_lora__mutmut_5': xǁChatModelǁ_apply_lora__mutmut_5, 
        'xǁChatModelǁ_apply_lora__mutmut_6': xǁChatModelǁ_apply_lora__mutmut_6, 
        'xǁChatModelǁ_apply_lora__mutmut_7': xǁChatModelǁ_apply_lora__mutmut_7, 
        'xǁChatModelǁ_apply_lora__mutmut_8': xǁChatModelǁ_apply_lora__mutmut_8, 
        'xǁChatModelǁ_apply_lora__mutmut_9': xǁChatModelǁ_apply_lora__mutmut_9, 
        'xǁChatModelǁ_apply_lora__mutmut_10': xǁChatModelǁ_apply_lora__mutmut_10, 
        'xǁChatModelǁ_apply_lora__mutmut_11': xǁChatModelǁ_apply_lora__mutmut_11, 
        'xǁChatModelǁ_apply_lora__mutmut_12': xǁChatModelǁ_apply_lora__mutmut_12, 
        'xǁChatModelǁ_apply_lora__mutmut_13': xǁChatModelǁ_apply_lora__mutmut_13, 
        'xǁChatModelǁ_apply_lora__mutmut_14': xǁChatModelǁ_apply_lora__mutmut_14, 
        'xǁChatModelǁ_apply_lora__mutmut_15': xǁChatModelǁ_apply_lora__mutmut_15, 
        'xǁChatModelǁ_apply_lora__mutmut_16': xǁChatModelǁ_apply_lora__mutmut_16, 
        'xǁChatModelǁ_apply_lora__mutmut_17': xǁChatModelǁ_apply_lora__mutmut_17, 
        'xǁChatModelǁ_apply_lora__mutmut_18': xǁChatModelǁ_apply_lora__mutmut_18, 
        'xǁChatModelǁ_apply_lora__mutmut_19': xǁChatModelǁ_apply_lora__mutmut_19, 
        'xǁChatModelǁ_apply_lora__mutmut_20': xǁChatModelǁ_apply_lora__mutmut_20, 
        'xǁChatModelǁ_apply_lora__mutmut_21': xǁChatModelǁ_apply_lora__mutmut_21, 
        'xǁChatModelǁ_apply_lora__mutmut_22': xǁChatModelǁ_apply_lora__mutmut_22, 
        'xǁChatModelǁ_apply_lora__mutmut_23': xǁChatModelǁ_apply_lora__mutmut_23, 
        'xǁChatModelǁ_apply_lora__mutmut_24': xǁChatModelǁ_apply_lora__mutmut_24, 
        'xǁChatModelǁ_apply_lora__mutmut_25': xǁChatModelǁ_apply_lora__mutmut_25, 
        'xǁChatModelǁ_apply_lora__mutmut_26': xǁChatModelǁ_apply_lora__mutmut_26, 
        'xǁChatModelǁ_apply_lora__mutmut_27': xǁChatModelǁ_apply_lora__mutmut_27, 
        'xǁChatModelǁ_apply_lora__mutmut_28': xǁChatModelǁ_apply_lora__mutmut_28, 
        'xǁChatModelǁ_apply_lora__mutmut_29': xǁChatModelǁ_apply_lora__mutmut_29, 
        'xǁChatModelǁ_apply_lora__mutmut_30': xǁChatModelǁ_apply_lora__mutmut_30, 
        'xǁChatModelǁ_apply_lora__mutmut_31': xǁChatModelǁ_apply_lora__mutmut_31, 
        'xǁChatModelǁ_apply_lora__mutmut_32': xǁChatModelǁ_apply_lora__mutmut_32, 
        'xǁChatModelǁ_apply_lora__mutmut_33': xǁChatModelǁ_apply_lora__mutmut_33, 
        'xǁChatModelǁ_apply_lora__mutmut_34': xǁChatModelǁ_apply_lora__mutmut_34, 
        'xǁChatModelǁ_apply_lora__mutmut_35': xǁChatModelǁ_apply_lora__mutmut_35, 
        'xǁChatModelǁ_apply_lora__mutmut_36': xǁChatModelǁ_apply_lora__mutmut_36, 
        'xǁChatModelǁ_apply_lora__mutmut_37': xǁChatModelǁ_apply_lora__mutmut_37, 
        'xǁChatModelǁ_apply_lora__mutmut_38': xǁChatModelǁ_apply_lora__mutmut_38, 
        'xǁChatModelǁ_apply_lora__mutmut_39': xǁChatModelǁ_apply_lora__mutmut_39, 
        'xǁChatModelǁ_apply_lora__mutmut_40': xǁChatModelǁ_apply_lora__mutmut_40, 
        'xǁChatModelǁ_apply_lora__mutmut_41': xǁChatModelǁ_apply_lora__mutmut_41, 
        'xǁChatModelǁ_apply_lora__mutmut_42': xǁChatModelǁ_apply_lora__mutmut_42, 
        'xǁChatModelǁ_apply_lora__mutmut_43': xǁChatModelǁ_apply_lora__mutmut_43, 
        'xǁChatModelǁ_apply_lora__mutmut_44': xǁChatModelǁ_apply_lora__mutmut_44, 
        'xǁChatModelǁ_apply_lora__mutmut_45': xǁChatModelǁ_apply_lora__mutmut_45, 
        'xǁChatModelǁ_apply_lora__mutmut_46': xǁChatModelǁ_apply_lora__mutmut_46, 
        'xǁChatModelǁ_apply_lora__mutmut_47': xǁChatModelǁ_apply_lora__mutmut_47, 
        'xǁChatModelǁ_apply_lora__mutmut_48': xǁChatModelǁ_apply_lora__mutmut_48, 
        'xǁChatModelǁ_apply_lora__mutmut_49': xǁChatModelǁ_apply_lora__mutmut_49, 
        'xǁChatModelǁ_apply_lora__mutmut_50': xǁChatModelǁ_apply_lora__mutmut_50, 
        'xǁChatModelǁ_apply_lora__mutmut_51': xǁChatModelǁ_apply_lora__mutmut_51, 
        'xǁChatModelǁ_apply_lora__mutmut_52': xǁChatModelǁ_apply_lora__mutmut_52, 
        'xǁChatModelǁ_apply_lora__mutmut_53': xǁChatModelǁ_apply_lora__mutmut_53, 
        'xǁChatModelǁ_apply_lora__mutmut_54': xǁChatModelǁ_apply_lora__mutmut_54, 
        'xǁChatModelǁ_apply_lora__mutmut_55': xǁChatModelǁ_apply_lora__mutmut_55, 
        'xǁChatModelǁ_apply_lora__mutmut_56': xǁChatModelǁ_apply_lora__mutmut_56, 
        'xǁChatModelǁ_apply_lora__mutmut_57': xǁChatModelǁ_apply_lora__mutmut_57, 
        'xǁChatModelǁ_apply_lora__mutmut_58': xǁChatModelǁ_apply_lora__mutmut_58, 
        'xǁChatModelǁ_apply_lora__mutmut_59': xǁChatModelǁ_apply_lora__mutmut_59, 
        'xǁChatModelǁ_apply_lora__mutmut_60': xǁChatModelǁ_apply_lora__mutmut_60, 
        'xǁChatModelǁ_apply_lora__mutmut_61': xǁChatModelǁ_apply_lora__mutmut_61, 
        'xǁChatModelǁ_apply_lora__mutmut_62': xǁChatModelǁ_apply_lora__mutmut_62, 
        'xǁChatModelǁ_apply_lora__mutmut_63': xǁChatModelǁ_apply_lora__mutmut_63, 
        'xǁChatModelǁ_apply_lora__mutmut_64': xǁChatModelǁ_apply_lora__mutmut_64, 
        'xǁChatModelǁ_apply_lora__mutmut_65': xǁChatModelǁ_apply_lora__mutmut_65, 
        'xǁChatModelǁ_apply_lora__mutmut_66': xǁChatModelǁ_apply_lora__mutmut_66, 
        'xǁChatModelǁ_apply_lora__mutmut_67': xǁChatModelǁ_apply_lora__mutmut_67, 
        'xǁChatModelǁ_apply_lora__mutmut_68': xǁChatModelǁ_apply_lora__mutmut_68, 
        'xǁChatModelǁ_apply_lora__mutmut_69': xǁChatModelǁ_apply_lora__mutmut_69, 
        'xǁChatModelǁ_apply_lora__mutmut_70': xǁChatModelǁ_apply_lora__mutmut_70, 
        'xǁChatModelǁ_apply_lora__mutmut_71': xǁChatModelǁ_apply_lora__mutmut_71, 
        'xǁChatModelǁ_apply_lora__mutmut_72': xǁChatModelǁ_apply_lora__mutmut_72, 
        'xǁChatModelǁ_apply_lora__mutmut_73': xǁChatModelǁ_apply_lora__mutmut_73, 
        'xǁChatModelǁ_apply_lora__mutmut_74': xǁChatModelǁ_apply_lora__mutmut_74, 
        'xǁChatModelǁ_apply_lora__mutmut_75': xǁChatModelǁ_apply_lora__mutmut_75, 
        'xǁChatModelǁ_apply_lora__mutmut_76': xǁChatModelǁ_apply_lora__mutmut_76, 
        'xǁChatModelǁ_apply_lora__mutmut_77': xǁChatModelǁ_apply_lora__mutmut_77, 
        'xǁChatModelǁ_apply_lora__mutmut_78': xǁChatModelǁ_apply_lora__mutmut_78, 
        'xǁChatModelǁ_apply_lora__mutmut_79': xǁChatModelǁ_apply_lora__mutmut_79, 
        'xǁChatModelǁ_apply_lora__mutmut_80': xǁChatModelǁ_apply_lora__mutmut_80
    }
    
    def _apply_lora(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁChatModelǁ_apply_lora__mutmut_orig"), object.__getattribute__(self, "xǁChatModelǁ_apply_lora__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _apply_lora.__signature__ = _mutmut_signature(xǁChatModelǁ_apply_lora__mutmut_orig)
    xǁChatModelǁ_apply_lora__mutmut_orig.__name__ = 'xǁChatModelǁ_apply_lora'

    @property
    def device(self) -> str:
        return self._device

    @property
    def dtype(self) -> Any:
        return self._dtype

    def xǁChatModelǁgenerate__mutmut_orig(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_1(self, prompt: str, *, max_tokens: int = 129, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_2(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = None
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_3(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            None,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_4(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors=None,
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_5(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=None,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_6(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=None,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_7(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_8(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_9(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_10(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_11(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="XXptXX",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_12(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="PT",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_13(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=False,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_14(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(None, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_15(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, None):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_16(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr("to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_17(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, ):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_18(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "XXtoXX"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_19(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "TO"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_20(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = None
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_21(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(None)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_22(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = None
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_23(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(None)
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_24(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(None))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_25(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = None
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_26(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault(None, max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_27(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", None)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_28(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault(max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_29(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", )
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_30(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("XXmax_new_tokensXX", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_31(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("MAX_NEW_TOKENS", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_32(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = None
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_33(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_34(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, )
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_35(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = None
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_36(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(None, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_37(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, None, None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_38(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr("sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_39(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_40(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", )
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_41(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "XXsequencesXX", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_42(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "SEQUENCES", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_43(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_44(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = None
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_45(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[1]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_46(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = None
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_47(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[1]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_48(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(None, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_49(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, None):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_50(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr("detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_51(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, ):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_52(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "XXdetachXX"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_53(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "DETACH"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_54(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = None
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_55(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(None, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_56(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, None):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_57(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr("to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_58(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, ):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_59(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "XXtoXX"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_60(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "TO"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_61(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = None
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_62(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to(None)
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_63(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("XXcpuXX")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_64(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("CPU")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_65(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(None, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_66(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, None):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_67(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr("cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_68(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, ):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_69(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "XXcpuXX"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_70(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "CPU"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_71(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = None
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_72(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(None, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_73(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, None):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_74(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr("tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_75(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, ):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_76(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "XXtolistXX"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_77(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "TOLIST"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_78(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = None
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_79(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(None, skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_80(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=None)

    def xǁChatModelǁgenerate__mutmut_81(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(skip_special_tokens=True)

    def xǁChatModelǁgenerate__mutmut_82(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, )

    def xǁChatModelǁgenerate__mutmut_83(self, prompt: str, *, max_tokens: int = 128, **overrides: Any) -> str:
        encoding = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
        )
        if hasattr(encoding, "to"):
            encoding = encoding.to(self.device)
        inputs = dict(_encoding_to_inputs(encoding))
        options = {**self.cfg.generation_kwargs, **overrides}
        options.setdefault("max_new_tokens", max_tokens)
        outputs = self.model.generate(**inputs, **options)
        sequence = getattr(outputs, "sequences", None)
        if sequence is not None:
            token_ids = sequence[0]
        else:
            token_ids = outputs[0]
        if hasattr(token_ids, "detach"):
            token_ids = token_ids.detach()
        if hasattr(token_ids, "to"):
            token_ids = token_ids.to("cpu")
        elif hasattr(token_ids, "cpu"):
            token_ids = token_ids.cpu()
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        return self.tokenizer.decode(token_ids, skip_special_tokens=False)
    
    xǁChatModelǁgenerate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁChatModelǁgenerate__mutmut_1': xǁChatModelǁgenerate__mutmut_1, 
        'xǁChatModelǁgenerate__mutmut_2': xǁChatModelǁgenerate__mutmut_2, 
        'xǁChatModelǁgenerate__mutmut_3': xǁChatModelǁgenerate__mutmut_3, 
        'xǁChatModelǁgenerate__mutmut_4': xǁChatModelǁgenerate__mutmut_4, 
        'xǁChatModelǁgenerate__mutmut_5': xǁChatModelǁgenerate__mutmut_5, 
        'xǁChatModelǁgenerate__mutmut_6': xǁChatModelǁgenerate__mutmut_6, 
        'xǁChatModelǁgenerate__mutmut_7': xǁChatModelǁgenerate__mutmut_7, 
        'xǁChatModelǁgenerate__mutmut_8': xǁChatModelǁgenerate__mutmut_8, 
        'xǁChatModelǁgenerate__mutmut_9': xǁChatModelǁgenerate__mutmut_9, 
        'xǁChatModelǁgenerate__mutmut_10': xǁChatModelǁgenerate__mutmut_10, 
        'xǁChatModelǁgenerate__mutmut_11': xǁChatModelǁgenerate__mutmut_11, 
        'xǁChatModelǁgenerate__mutmut_12': xǁChatModelǁgenerate__mutmut_12, 
        'xǁChatModelǁgenerate__mutmut_13': xǁChatModelǁgenerate__mutmut_13, 
        'xǁChatModelǁgenerate__mutmut_14': xǁChatModelǁgenerate__mutmut_14, 
        'xǁChatModelǁgenerate__mutmut_15': xǁChatModelǁgenerate__mutmut_15, 
        'xǁChatModelǁgenerate__mutmut_16': xǁChatModelǁgenerate__mutmut_16, 
        'xǁChatModelǁgenerate__mutmut_17': xǁChatModelǁgenerate__mutmut_17, 
        'xǁChatModelǁgenerate__mutmut_18': xǁChatModelǁgenerate__mutmut_18, 
        'xǁChatModelǁgenerate__mutmut_19': xǁChatModelǁgenerate__mutmut_19, 
        'xǁChatModelǁgenerate__mutmut_20': xǁChatModelǁgenerate__mutmut_20, 
        'xǁChatModelǁgenerate__mutmut_21': xǁChatModelǁgenerate__mutmut_21, 
        'xǁChatModelǁgenerate__mutmut_22': xǁChatModelǁgenerate__mutmut_22, 
        'xǁChatModelǁgenerate__mutmut_23': xǁChatModelǁgenerate__mutmut_23, 
        'xǁChatModelǁgenerate__mutmut_24': xǁChatModelǁgenerate__mutmut_24, 
        'xǁChatModelǁgenerate__mutmut_25': xǁChatModelǁgenerate__mutmut_25, 
        'xǁChatModelǁgenerate__mutmut_26': xǁChatModelǁgenerate__mutmut_26, 
        'xǁChatModelǁgenerate__mutmut_27': xǁChatModelǁgenerate__mutmut_27, 
        'xǁChatModelǁgenerate__mutmut_28': xǁChatModelǁgenerate__mutmut_28, 
        'xǁChatModelǁgenerate__mutmut_29': xǁChatModelǁgenerate__mutmut_29, 
        'xǁChatModelǁgenerate__mutmut_30': xǁChatModelǁgenerate__mutmut_30, 
        'xǁChatModelǁgenerate__mutmut_31': xǁChatModelǁgenerate__mutmut_31, 
        'xǁChatModelǁgenerate__mutmut_32': xǁChatModelǁgenerate__mutmut_32, 
        'xǁChatModelǁgenerate__mutmut_33': xǁChatModelǁgenerate__mutmut_33, 
        'xǁChatModelǁgenerate__mutmut_34': xǁChatModelǁgenerate__mutmut_34, 
        'xǁChatModelǁgenerate__mutmut_35': xǁChatModelǁgenerate__mutmut_35, 
        'xǁChatModelǁgenerate__mutmut_36': xǁChatModelǁgenerate__mutmut_36, 
        'xǁChatModelǁgenerate__mutmut_37': xǁChatModelǁgenerate__mutmut_37, 
        'xǁChatModelǁgenerate__mutmut_38': xǁChatModelǁgenerate__mutmut_38, 
        'xǁChatModelǁgenerate__mutmut_39': xǁChatModelǁgenerate__mutmut_39, 
        'xǁChatModelǁgenerate__mutmut_40': xǁChatModelǁgenerate__mutmut_40, 
        'xǁChatModelǁgenerate__mutmut_41': xǁChatModelǁgenerate__mutmut_41, 
        'xǁChatModelǁgenerate__mutmut_42': xǁChatModelǁgenerate__mutmut_42, 
        'xǁChatModelǁgenerate__mutmut_43': xǁChatModelǁgenerate__mutmut_43, 
        'xǁChatModelǁgenerate__mutmut_44': xǁChatModelǁgenerate__mutmut_44, 
        'xǁChatModelǁgenerate__mutmut_45': xǁChatModelǁgenerate__mutmut_45, 
        'xǁChatModelǁgenerate__mutmut_46': xǁChatModelǁgenerate__mutmut_46, 
        'xǁChatModelǁgenerate__mutmut_47': xǁChatModelǁgenerate__mutmut_47, 
        'xǁChatModelǁgenerate__mutmut_48': xǁChatModelǁgenerate__mutmut_48, 
        'xǁChatModelǁgenerate__mutmut_49': xǁChatModelǁgenerate__mutmut_49, 
        'xǁChatModelǁgenerate__mutmut_50': xǁChatModelǁgenerate__mutmut_50, 
        'xǁChatModelǁgenerate__mutmut_51': xǁChatModelǁgenerate__mutmut_51, 
        'xǁChatModelǁgenerate__mutmut_52': xǁChatModelǁgenerate__mutmut_52, 
        'xǁChatModelǁgenerate__mutmut_53': xǁChatModelǁgenerate__mutmut_53, 
        'xǁChatModelǁgenerate__mutmut_54': xǁChatModelǁgenerate__mutmut_54, 
        'xǁChatModelǁgenerate__mutmut_55': xǁChatModelǁgenerate__mutmut_55, 
        'xǁChatModelǁgenerate__mutmut_56': xǁChatModelǁgenerate__mutmut_56, 
        'xǁChatModelǁgenerate__mutmut_57': xǁChatModelǁgenerate__mutmut_57, 
        'xǁChatModelǁgenerate__mutmut_58': xǁChatModelǁgenerate__mutmut_58, 
        'xǁChatModelǁgenerate__mutmut_59': xǁChatModelǁgenerate__mutmut_59, 
        'xǁChatModelǁgenerate__mutmut_60': xǁChatModelǁgenerate__mutmut_60, 
        'xǁChatModelǁgenerate__mutmut_61': xǁChatModelǁgenerate__mutmut_61, 
        'xǁChatModelǁgenerate__mutmut_62': xǁChatModelǁgenerate__mutmut_62, 
        'xǁChatModelǁgenerate__mutmut_63': xǁChatModelǁgenerate__mutmut_63, 
        'xǁChatModelǁgenerate__mutmut_64': xǁChatModelǁgenerate__mutmut_64, 
        'xǁChatModelǁgenerate__mutmut_65': xǁChatModelǁgenerate__mutmut_65, 
        'xǁChatModelǁgenerate__mutmut_66': xǁChatModelǁgenerate__mutmut_66, 
        'xǁChatModelǁgenerate__mutmut_67': xǁChatModelǁgenerate__mutmut_67, 
        'xǁChatModelǁgenerate__mutmut_68': xǁChatModelǁgenerate__mutmut_68, 
        'xǁChatModelǁgenerate__mutmut_69': xǁChatModelǁgenerate__mutmut_69, 
        'xǁChatModelǁgenerate__mutmut_70': xǁChatModelǁgenerate__mutmut_70, 
        'xǁChatModelǁgenerate__mutmut_71': xǁChatModelǁgenerate__mutmut_71, 
        'xǁChatModelǁgenerate__mutmut_72': xǁChatModelǁgenerate__mutmut_72, 
        'xǁChatModelǁgenerate__mutmut_73': xǁChatModelǁgenerate__mutmut_73, 
        'xǁChatModelǁgenerate__mutmut_74': xǁChatModelǁgenerate__mutmut_74, 
        'xǁChatModelǁgenerate__mutmut_75': xǁChatModelǁgenerate__mutmut_75, 
        'xǁChatModelǁgenerate__mutmut_76': xǁChatModelǁgenerate__mutmut_76, 
        'xǁChatModelǁgenerate__mutmut_77': xǁChatModelǁgenerate__mutmut_77, 
        'xǁChatModelǁgenerate__mutmut_78': xǁChatModelǁgenerate__mutmut_78, 
        'xǁChatModelǁgenerate__mutmut_79': xǁChatModelǁgenerate__mutmut_79, 
        'xǁChatModelǁgenerate__mutmut_80': xǁChatModelǁgenerate__mutmut_80, 
        'xǁChatModelǁgenerate__mutmut_81': xǁChatModelǁgenerate__mutmut_81, 
        'xǁChatModelǁgenerate__mutmut_82': xǁChatModelǁgenerate__mutmut_82, 
        'xǁChatModelǁgenerate__mutmut_83': xǁChatModelǁgenerate__mutmut_83
    }
    
    def generate(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁChatModelǁgenerate__mutmut_orig"), object.__getattribute__(self, "xǁChatModelǁgenerate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    generate.__signature__ = _mutmut_signature(xǁChatModelǁgenerate__mutmut_orig)
    xǁChatModelǁgenerate__mutmut_orig.__name__ = 'xǁChatModelǁgenerate'


__all__ = ["ChatModel", "ChatModelConfig"]
