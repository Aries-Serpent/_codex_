# BEGIN: CODEX_UTILS_TRAINING_CALLBACKS
"""Generic training callbacks used across small examples.

Currently only exposes :class:`EarlyStopping`.
"""
from __future__ import annotations

from typing import Optional
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


class EarlyStopping:
    """Signal training halt when a monitored metric plateaus."""

    def xǁEarlyStoppingǁ__init____mutmut_orig(self, patience: int = 3, min_delta: float = 0.0, mode: str = "min") -> None:
        self.patience = patience
        self.min_delta = min_delta
        self.mode = mode
        self.best: Optional[float] = None
        self.wait = 0

    def xǁEarlyStoppingǁ__init____mutmut_1(self, patience: int = 4, min_delta: float = 0.0, mode: str = "min") -> None:
        self.patience = patience
        self.min_delta = min_delta
        self.mode = mode
        self.best: Optional[float] = None
        self.wait = 0

    def xǁEarlyStoppingǁ__init____mutmut_2(self, patience: int = 3, min_delta: float = 1.0, mode: str = "min") -> None:
        self.patience = patience
        self.min_delta = min_delta
        self.mode = mode
        self.best: Optional[float] = None
        self.wait = 0

    def xǁEarlyStoppingǁ__init____mutmut_3(self, patience: int = 3, min_delta: float = 0.0, mode: str = "XXminXX") -> None:
        self.patience = patience
        self.min_delta = min_delta
        self.mode = mode
        self.best: Optional[float] = None
        self.wait = 0

    def xǁEarlyStoppingǁ__init____mutmut_4(self, patience: int = 3, min_delta: float = 0.0, mode: str = "MIN") -> None:
        self.patience = patience
        self.min_delta = min_delta
        self.mode = mode
        self.best: Optional[float] = None
        self.wait = 0

    def xǁEarlyStoppingǁ__init____mutmut_5(self, patience: int = 3, min_delta: float = 0.0, mode: str = "min") -> None:
        self.patience = None
        self.min_delta = min_delta
        self.mode = mode
        self.best: Optional[float] = None
        self.wait = 0

    def xǁEarlyStoppingǁ__init____mutmut_6(self, patience: int = 3, min_delta: float = 0.0, mode: str = "min") -> None:
        self.patience = patience
        self.min_delta = None
        self.mode = mode
        self.best: Optional[float] = None
        self.wait = 0

    def xǁEarlyStoppingǁ__init____mutmut_7(self, patience: int = 3, min_delta: float = 0.0, mode: str = "min") -> None:
        self.patience = patience
        self.min_delta = min_delta
        self.mode = None
        self.best: Optional[float] = None
        self.wait = 0

    def xǁEarlyStoppingǁ__init____mutmut_8(self, patience: int = 3, min_delta: float = 0.0, mode: str = "min") -> None:
        self.patience = patience
        self.min_delta = min_delta
        self.mode = mode
        self.best: Optional[float] = ""
        self.wait = 0

    def xǁEarlyStoppingǁ__init____mutmut_9(self, patience: int = 3, min_delta: float = 0.0, mode: str = "min") -> None:
        self.patience = patience
        self.min_delta = min_delta
        self.mode = mode
        self.best: Optional[float] = None
        self.wait = None

    def xǁEarlyStoppingǁ__init____mutmut_10(self, patience: int = 3, min_delta: float = 0.0, mode: str = "min") -> None:
        self.patience = patience
        self.min_delta = min_delta
        self.mode = mode
        self.best: Optional[float] = None
        self.wait = 1
    
    xǁEarlyStoppingǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁEarlyStoppingǁ__init____mutmut_1': xǁEarlyStoppingǁ__init____mutmut_1, 
        'xǁEarlyStoppingǁ__init____mutmut_2': xǁEarlyStoppingǁ__init____mutmut_2, 
        'xǁEarlyStoppingǁ__init____mutmut_3': xǁEarlyStoppingǁ__init____mutmut_3, 
        'xǁEarlyStoppingǁ__init____mutmut_4': xǁEarlyStoppingǁ__init____mutmut_4, 
        'xǁEarlyStoppingǁ__init____mutmut_5': xǁEarlyStoppingǁ__init____mutmut_5, 
        'xǁEarlyStoppingǁ__init____mutmut_6': xǁEarlyStoppingǁ__init____mutmut_6, 
        'xǁEarlyStoppingǁ__init____mutmut_7': xǁEarlyStoppingǁ__init____mutmut_7, 
        'xǁEarlyStoppingǁ__init____mutmut_8': xǁEarlyStoppingǁ__init____mutmut_8, 
        'xǁEarlyStoppingǁ__init____mutmut_9': xǁEarlyStoppingǁ__init____mutmut_9, 
        'xǁEarlyStoppingǁ__init____mutmut_10': xǁEarlyStoppingǁ__init____mutmut_10
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁEarlyStoppingǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁEarlyStoppingǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁEarlyStoppingǁ__init____mutmut_orig)
    xǁEarlyStoppingǁ__init____mutmut_orig.__name__ = 'xǁEarlyStoppingǁ__init__'

    def xǁEarlyStoppingǁstep__mutmut_orig(self, metric: float) -> bool:
        """Return True if training should stop."""
        if self.best is None:
            self.best = metric
            return False
        improved = False
        if self.mode == "min":
            improved = metric < self.best - self.min_delta
        else:
            improved = metric > self.best + self.min_delta
        if improved:
            self.best = metric
            self.wait = 0
            return False
        self.wait += 1
        return self.wait >= self.patience

    def xǁEarlyStoppingǁstep__mutmut_1(self, metric: float) -> bool:
        """Return True if training should stop."""
        if self.best is not None:
            self.best = metric
            return False
        improved = False
        if self.mode == "min":
            improved = metric < self.best - self.min_delta
        else:
            improved = metric > self.best + self.min_delta
        if improved:
            self.best = metric
            self.wait = 0
            return False
        self.wait += 1
        return self.wait >= self.patience

    def xǁEarlyStoppingǁstep__mutmut_2(self, metric: float) -> bool:
        """Return True if training should stop."""
        if self.best is None:
            self.best = None
            return False
        improved = False
        if self.mode == "min":
            improved = metric < self.best - self.min_delta
        else:
            improved = metric > self.best + self.min_delta
        if improved:
            self.best = metric
            self.wait = 0
            return False
        self.wait += 1
        return self.wait >= self.patience

    def xǁEarlyStoppingǁstep__mutmut_3(self, metric: float) -> bool:
        """Return True if training should stop."""
        if self.best is None:
            self.best = metric
            return True
        improved = False
        if self.mode == "min":
            improved = metric < self.best - self.min_delta
        else:
            improved = metric > self.best + self.min_delta
        if improved:
            self.best = metric
            self.wait = 0
            return False
        self.wait += 1
        return self.wait >= self.patience

    def xǁEarlyStoppingǁstep__mutmut_4(self, metric: float) -> bool:
        """Return True if training should stop."""
        if self.best is None:
            self.best = metric
            return False
        improved = None
        if self.mode == "min":
            improved = metric < self.best - self.min_delta
        else:
            improved = metric > self.best + self.min_delta
        if improved:
            self.best = metric
            self.wait = 0
            return False
        self.wait += 1
        return self.wait >= self.patience

    def xǁEarlyStoppingǁstep__mutmut_5(self, metric: float) -> bool:
        """Return True if training should stop."""
        if self.best is None:
            self.best = metric
            return False
        improved = True
        if self.mode == "min":
            improved = metric < self.best - self.min_delta
        else:
            improved = metric > self.best + self.min_delta
        if improved:
            self.best = metric
            self.wait = 0
            return False
        self.wait += 1
        return self.wait >= self.patience

    def xǁEarlyStoppingǁstep__mutmut_6(self, metric: float) -> bool:
        """Return True if training should stop."""
        if self.best is None:
            self.best = metric
            return False
        improved = False
        if self.mode != "min":
            improved = metric < self.best - self.min_delta
        else:
            improved = metric > self.best + self.min_delta
        if improved:
            self.best = metric
            self.wait = 0
            return False
        self.wait += 1
        return self.wait >= self.patience

    def xǁEarlyStoppingǁstep__mutmut_7(self, metric: float) -> bool:
        """Return True if training should stop."""
        if self.best is None:
            self.best = metric
            return False
        improved = False
        if self.mode == "XXminXX":
            improved = metric < self.best - self.min_delta
        else:
            improved = metric > self.best + self.min_delta
        if improved:
            self.best = metric
            self.wait = 0
            return False
        self.wait += 1
        return self.wait >= self.patience

    def xǁEarlyStoppingǁstep__mutmut_8(self, metric: float) -> bool:
        """Return True if training should stop."""
        if self.best is None:
            self.best = metric
            return False
        improved = False
        if self.mode == "MIN":
            improved = metric < self.best - self.min_delta
        else:
            improved = metric > self.best + self.min_delta
        if improved:
            self.best = metric
            self.wait = 0
            return False
        self.wait += 1
        return self.wait >= self.patience

    def xǁEarlyStoppingǁstep__mutmut_9(self, metric: float) -> bool:
        """Return True if training should stop."""
        if self.best is None:
            self.best = metric
            return False
        improved = False
        if self.mode == "min":
            improved = None
        else:
            improved = metric > self.best + self.min_delta
        if improved:
            self.best = metric
            self.wait = 0
            return False
        self.wait += 1
        return self.wait >= self.patience

    def xǁEarlyStoppingǁstep__mutmut_10(self, metric: float) -> bool:
        """Return True if training should stop."""
        if self.best is None:
            self.best = metric
            return False
        improved = False
        if self.mode == "min":
            improved = metric <= self.best - self.min_delta
        else:
            improved = metric > self.best + self.min_delta
        if improved:
            self.best = metric
            self.wait = 0
            return False
        self.wait += 1
        return self.wait >= self.patience

    def xǁEarlyStoppingǁstep__mutmut_11(self, metric: float) -> bool:
        """Return True if training should stop."""
        if self.best is None:
            self.best = metric
            return False
        improved = False
        if self.mode == "min":
            improved = metric < self.best + self.min_delta
        else:
            improved = metric > self.best + self.min_delta
        if improved:
            self.best = metric
            self.wait = 0
            return False
        self.wait += 1
        return self.wait >= self.patience

    def xǁEarlyStoppingǁstep__mutmut_12(self, metric: float) -> bool:
        """Return True if training should stop."""
        if self.best is None:
            self.best = metric
            return False
        improved = False
        if self.mode == "min":
            improved = metric < self.best - self.min_delta
        else:
            improved = None
        if improved:
            self.best = metric
            self.wait = 0
            return False
        self.wait += 1
        return self.wait >= self.patience

    def xǁEarlyStoppingǁstep__mutmut_13(self, metric: float) -> bool:
        """Return True if training should stop."""
        if self.best is None:
            self.best = metric
            return False
        improved = False
        if self.mode == "min":
            improved = metric < self.best - self.min_delta
        else:
            improved = metric >= self.best + self.min_delta
        if improved:
            self.best = metric
            self.wait = 0
            return False
        self.wait += 1
        return self.wait >= self.patience

    def xǁEarlyStoppingǁstep__mutmut_14(self, metric: float) -> bool:
        """Return True if training should stop."""
        if self.best is None:
            self.best = metric
            return False
        improved = False
        if self.mode == "min":
            improved = metric < self.best - self.min_delta
        else:
            improved = metric > self.best - self.min_delta
        if improved:
            self.best = metric
            self.wait = 0
            return False
        self.wait += 1
        return self.wait >= self.patience

    def xǁEarlyStoppingǁstep__mutmut_15(self, metric: float) -> bool:
        """Return True if training should stop."""
        if self.best is None:
            self.best = metric
            return False
        improved = False
        if self.mode == "min":
            improved = metric < self.best - self.min_delta
        else:
            improved = metric > self.best + self.min_delta
        if improved:
            self.best = None
            self.wait = 0
            return False
        self.wait += 1
        return self.wait >= self.patience

    def xǁEarlyStoppingǁstep__mutmut_16(self, metric: float) -> bool:
        """Return True if training should stop."""
        if self.best is None:
            self.best = metric
            return False
        improved = False
        if self.mode == "min":
            improved = metric < self.best - self.min_delta
        else:
            improved = metric > self.best + self.min_delta
        if improved:
            self.best = metric
            self.wait = None
            return False
        self.wait += 1
        return self.wait >= self.patience

    def xǁEarlyStoppingǁstep__mutmut_17(self, metric: float) -> bool:
        """Return True if training should stop."""
        if self.best is None:
            self.best = metric
            return False
        improved = False
        if self.mode == "min":
            improved = metric < self.best - self.min_delta
        else:
            improved = metric > self.best + self.min_delta
        if improved:
            self.best = metric
            self.wait = 1
            return False
        self.wait += 1
        return self.wait >= self.patience

    def xǁEarlyStoppingǁstep__mutmut_18(self, metric: float) -> bool:
        """Return True if training should stop."""
        if self.best is None:
            self.best = metric
            return False
        improved = False
        if self.mode == "min":
            improved = metric < self.best - self.min_delta
        else:
            improved = metric > self.best + self.min_delta
        if improved:
            self.best = metric
            self.wait = 0
            return True
        self.wait += 1
        return self.wait >= self.patience

    def xǁEarlyStoppingǁstep__mutmut_19(self, metric: float) -> bool:
        """Return True if training should stop."""
        if self.best is None:
            self.best = metric
            return False
        improved = False
        if self.mode == "min":
            improved = metric < self.best - self.min_delta
        else:
            improved = metric > self.best + self.min_delta
        if improved:
            self.best = metric
            self.wait = 0
            return False
        self.wait = 1
        return self.wait >= self.patience

    def xǁEarlyStoppingǁstep__mutmut_20(self, metric: float) -> bool:
        """Return True if training should stop."""
        if self.best is None:
            self.best = metric
            return False
        improved = False
        if self.mode == "min":
            improved = metric < self.best - self.min_delta
        else:
            improved = metric > self.best + self.min_delta
        if improved:
            self.best = metric
            self.wait = 0
            return False
        self.wait -= 1
        return self.wait >= self.patience

    def xǁEarlyStoppingǁstep__mutmut_21(self, metric: float) -> bool:
        """Return True if training should stop."""
        if self.best is None:
            self.best = metric
            return False
        improved = False
        if self.mode == "min":
            improved = metric < self.best - self.min_delta
        else:
            improved = metric > self.best + self.min_delta
        if improved:
            self.best = metric
            self.wait = 0
            return False
        self.wait += 2
        return self.wait >= self.patience

    def xǁEarlyStoppingǁstep__mutmut_22(self, metric: float) -> bool:
        """Return True if training should stop."""
        if self.best is None:
            self.best = metric
            return False
        improved = False
        if self.mode == "min":
            improved = metric < self.best - self.min_delta
        else:
            improved = metric > self.best + self.min_delta
        if improved:
            self.best = metric
            self.wait = 0
            return False
        self.wait += 1
        return self.wait > self.patience
    
    xǁEarlyStoppingǁstep__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁEarlyStoppingǁstep__mutmut_1': xǁEarlyStoppingǁstep__mutmut_1, 
        'xǁEarlyStoppingǁstep__mutmut_2': xǁEarlyStoppingǁstep__mutmut_2, 
        'xǁEarlyStoppingǁstep__mutmut_3': xǁEarlyStoppingǁstep__mutmut_3, 
        'xǁEarlyStoppingǁstep__mutmut_4': xǁEarlyStoppingǁstep__mutmut_4, 
        'xǁEarlyStoppingǁstep__mutmut_5': xǁEarlyStoppingǁstep__mutmut_5, 
        'xǁEarlyStoppingǁstep__mutmut_6': xǁEarlyStoppingǁstep__mutmut_6, 
        'xǁEarlyStoppingǁstep__mutmut_7': xǁEarlyStoppingǁstep__mutmut_7, 
        'xǁEarlyStoppingǁstep__mutmut_8': xǁEarlyStoppingǁstep__mutmut_8, 
        'xǁEarlyStoppingǁstep__mutmut_9': xǁEarlyStoppingǁstep__mutmut_9, 
        'xǁEarlyStoppingǁstep__mutmut_10': xǁEarlyStoppingǁstep__mutmut_10, 
        'xǁEarlyStoppingǁstep__mutmut_11': xǁEarlyStoppingǁstep__mutmut_11, 
        'xǁEarlyStoppingǁstep__mutmut_12': xǁEarlyStoppingǁstep__mutmut_12, 
        'xǁEarlyStoppingǁstep__mutmut_13': xǁEarlyStoppingǁstep__mutmut_13, 
        'xǁEarlyStoppingǁstep__mutmut_14': xǁEarlyStoppingǁstep__mutmut_14, 
        'xǁEarlyStoppingǁstep__mutmut_15': xǁEarlyStoppingǁstep__mutmut_15, 
        'xǁEarlyStoppingǁstep__mutmut_16': xǁEarlyStoppingǁstep__mutmut_16, 
        'xǁEarlyStoppingǁstep__mutmut_17': xǁEarlyStoppingǁstep__mutmut_17, 
        'xǁEarlyStoppingǁstep__mutmut_18': xǁEarlyStoppingǁstep__mutmut_18, 
        'xǁEarlyStoppingǁstep__mutmut_19': xǁEarlyStoppingǁstep__mutmut_19, 
        'xǁEarlyStoppingǁstep__mutmut_20': xǁEarlyStoppingǁstep__mutmut_20, 
        'xǁEarlyStoppingǁstep__mutmut_21': xǁEarlyStoppingǁstep__mutmut_21, 
        'xǁEarlyStoppingǁstep__mutmut_22': xǁEarlyStoppingǁstep__mutmut_22
    }
    
    def step(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁEarlyStoppingǁstep__mutmut_orig"), object.__getattribute__(self, "xǁEarlyStoppingǁstep__mutmut_mutants"), args, kwargs, self)
        return result 
    
    step.__signature__ = _mutmut_signature(xǁEarlyStoppingǁstep__mutmut_orig)
    xǁEarlyStoppingǁstep__mutmut_orig.__name__ = 'xǁEarlyStoppingǁstep'


__all__ = ["EarlyStopping"]

# END: CODEX_UTILS_TRAINING_CALLBACKS
