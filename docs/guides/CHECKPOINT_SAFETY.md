# Checkpoint Safety & Test Plan

This guide explains why we default to safer checkpoint loading, how the
`load_checkpoint(safe=True)` test works, and how to run it predictably.

## Why “safe” checkpoint loading?

**PyTorch** supports `torch.load(..., weights_only=True)` to “only load weights
and not execute any custom class logic” (paraphrased). This reduces exposure to
arbitrary code execution risks from untrusted pickle payloads. Our helper
wraps `torch.load` and, when `safe=True`, requires `weights_only` support. If
that parameter is unavailable in the local torch build, we fail closed with a
clear `RuntimeError`. :contentReference[oaicite:5]{index=5}

The static analyzer **Bandit** includes rule **B614 (pytorch_load)**, which
flags unsafe loading and explicitly recommends using `weights_only=True` or
switching to a safer format. Our approach follows this guidance. :contentReference[oaicite:6]{index=6}

When possible, prefer **safetensors** (a simple, zero-copy tensor format) for
model weights to avoid pickle entirely. :contentReference[oaicite:7]{index=7}

## What the regression test does

The test constructs a **plain state-dict** of CPU tensors (`dict[str, Tensor]`)
and writes it with `torch.save`. It then calls
`load_checkpoint(safe=True, map_location="cpu")`:

- If the local PyTorch exposes `weights_only`, the load **succeeds** and yields
  a mapping of tensors.
- If not, we **raise RuntimeError** (safer default when we cannot enforce the
  restricted loading mode).

We also assert that `safe=False` always loads (trusted path), which validates
the non-safe code path for completeness. (Both flows are exercised against the
same, object-free state-dict.)

We intentionally do **not** include any custom objects in the saved file; the
test aims to validate the *safety gate* and round-trip behavior specifically
for tensor-only state-dicts.

## Running the test locally

For stable local runs that avoid stray third-party plugins:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/utils/test_checkpointing_safe_load.py
```

This environment variable disables auto-loading of external pytest plugins
discovered on your system, reducing surprising interactions. :contentReference[oaicite:8]{index=8}

If PyTorch is not available in the environment, the test will be **skipped**
via `pytest.importorskip`. :contentReference[oaicite:9]{index=9}

## References

- **PyTorch** `torch.load` (API reference): `weights_only`, `map_location`. :contentReference[oaicite:10]{index=10}  
- **Bandit** B614 rule (pytorch_load): risk and recommendations. :contentReference[oaicite:11]{index=11}  
- **safetensors** documentation (safe, zero-copy tensor format). :contentReference[oaicite:12]{index=12}  
- **pytest** `importorskip` API. :contentReference[oaicite:13]{index=13}  
- **pytest** plugin autoload env var `PYTEST_DISABLE_PLUGIN_AUTOLOAD`. :contentReference[oaicite:14]{index=14}

