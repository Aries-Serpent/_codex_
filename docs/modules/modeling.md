# Modeling utilities

The `codex_ml.hf_loader` module wraps Hugging Face loaders with offline-first
and plug-in friendly behaviour.

## `load_causal_lm`

```python
load_causal_lm(
    repo_id,
    *,
    revision=None,
    trust_remote_code=False,
    device=None,
    dtype=None,
    peft_cfg=None,
)
```

* **Registry aware** – if `repo_id` matches a constructor registered via
  `register_causal_lm`, that callable is invoked instead of the Hugging Face
  loader.  This keeps tests and custom fixtures hermetic.
* **Revision guard** – remote identifiers still flow through
  `_required_revision`, so Bandit B615 policies remain intact.
* **AMP dtype mapping** – passing `dtype="bf16"` or `dtype="fp16"` maps to
  `torch.bfloat16` / `torch.float16`.  Unsupported values are ignored to avoid
  hard failures on CPU-only machines.
* **Device moves** – when a `device` string is provided, the loader attempts to
  call `.to(device)` and logs any failures without aborting the run.
* **LoRA / PEFT integration** – dictionaries passed via `peft_cfg` are converted
  to `peft.LoraConfig` when the dependency is available.  Missing modules,
  invalid configs or runtime errors are logged and do not prevent the base model
  from loading.

## Registering constructors

Use the decorator to inject custom constructors:

```python
from codex_ml.hf_loader import register_causal_lm


@register_causal_lm("tiny-fixture")
def build_fixture(*, device=None, dtype=None, peft_cfg=None):
    model = TinyFixtureModel()
    if device:
        model.to(device)
    return model
```

Clean-up helpers are available for tests: `get_registered_causal_lm(name)`
returns the callable (or `None`) and `unregister_causal_lm(name)` removes the
entry.
