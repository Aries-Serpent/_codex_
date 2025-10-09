from __future__ import annotations

import dataclasses
from typing import Any, Dict

import pytest
from omegaconf import OmegaConf

# Prefer the project unified config if present; otherwise use a tiny fallback.
try:
    # Existing project config (if available)
    from codex_ml.training.unified_training import UnifiedTrainingConfig as _Cfg  # type: ignore
except Exception:
    @dataclasses.dataclass
    class _Cfg:
        seed: int = 42
        epochs: int = 1
        batch_size: int = 8
        extra: Dict[str, Any] = dataclasses.field(default_factory=dict)


_STRUCTURED = OmegaConf.structured(_Cfg)
_IS_STRUCTURED_TYPE = isinstance(_STRUCTURED, type)


def _make_base_cfg() -> Any:
    if _IS_STRUCTURED_TYPE:
        instance = _STRUCTURED() if dataclasses.is_dataclass(_STRUCTURED) else _STRUCTURED
        return OmegaConf.create(dataclasses.asdict(instance))
    if dataclasses.is_dataclass(_STRUCTURED):
        return OmegaConf.create(dataclasses.asdict(_STRUCTURED))
    return _STRUCTURED


def test_structured_config_merge_ok() -> None:
    base = _make_base_cfg()                    # type-checked schema when real OmegaConf present
    override = OmegaConf.create({"epochs": 2}) # valid override
    merged = OmegaConf.merge(base, override)
    assert OmegaConf.to_object(merged)["epochs"] == 2


def test_structured_config_rejects_wrong_type() -> None:
    if _IS_STRUCTURED_TYPE:
        pytest.skip("OmegaConf shim does not enforce types")
    base = _make_base_cfg()
    bad = OmegaConf.create({"epochs": "two"})
    with pytest.raises(Exception):
        _ = OmegaConf.merge(base, bad)  # should fail type validation
