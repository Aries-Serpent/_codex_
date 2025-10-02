# Modeling utilities

The modeling package exposes helpers for instantiating decoder-style language
models with optional PEFT integration while remaining friendly to offline
environments.

## `codex_ml.modeling.factory.build_model`

```python
build_model(
    ModelFactoryConfig(
        model_name_or_path,
        dtype=None,
        device_map=None,
        enable_peft=False,
        peft=None,
        loader_kwargs=None,
    ),
)
```

* **dtype guard** – specifying a `dtype` requires `torch` to be installed and
  the attribute to exist on the module. A missing or unknown dtype raises a
  clear error before the loader executes.
* **Device forwarding** – `device_map` is forwarded directly to the underlying
  loader, enabling CPU/GPU placement via configuration.
* **Environment gated PEFT** – LoRA/PEFT adapters only activate when both
  `enable_peft=True` and the environment variable `CODEX_ML_ENABLE_PEFT` resolve
  to a truthy value (`1`, `true`, `yes`, `on`). When the gate is closed the base
  model loads untouched and a log line documents the decision.
* **Adapter configuration** – `PeftAdapterConfig` captures the LoRA parameters
  (`r`, `alpha`, `dropout`, `target_modules`, and optional adapter `path`) and is
  converted into keyword arguments for `load_model_with_optional_lora`.

### Roll-forward from legacy helpers

Older utilities (e.g. `codex_ml.hf_loader.load_causal_lm`) remain available for
compatibility, but new code should prefer the factory to benefit from the
environmental guardrails and focused test coverage introduced here.

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
