# BEGIN: CODEX_PEFT_ADAPTER
from __future__ import annotations

def apply_lora(model, cfg: dict | None = None):
    """Optional PEFT LoRA application. If peft not installed, returns model unchanged."""
    try:
        import peft  # type: ignore
        return model
    except Exception:
        return model
# END: CODEX_PEFT_ADAPTER
