from __future__ import annotations

from pathlib import Path
from typing import Any

from common.registry import DATASETS, METRICS, MODELS
from hhg_logistics.model.peft_utils import load_hf_llm

try:  # pragma: no cover - optional dependency
    import pandas as pd
except Exception:  # pragma: no cover
    pd = None  # type: ignore


@MODELS.register("hf_tiny_gpt2")
def register_tiny_model(cfg) -> dict[str, Any]:
    bundle = load_hf_llm(
        pretrained="sshleifer/tiny-gpt2",
        tokenizer_name="sshleifer/tiny-gpt2",
        dtype=str(getattr(cfg.model, "dtype", "float32")),
        trust_remote_code=bool(getattr(cfg.model, "trust_remote_code", False)),
        low_cpu_mem_usage=True,
    )
    return {"model": bundle.model, "tokenizer": bundle.tokenizer}


@DATASETS.register("features_csv")
def register_features_csv(cfg) -> dict[str, Any]:
    path = Path(cfg.pipeline.features.output_path)
    if pd is None:
        return {"path": str(path)}
    frame = pd.read_csv(path)
    return {"df": frame, "path": str(path)}


@METRICS.register("mean_value")
def register_mean_value(df=None, **_kwargs) -> float:
    if df is None or "value" not in df.columns:
        return float("nan")
    return float(df["value"].mean())
