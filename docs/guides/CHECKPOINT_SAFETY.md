# Checkpoint Safety & Test Plan

This guide explains why we default to safer checkpoint loading, how the
`load_checkpoint(safe=True)` regression test works, and how to run it
predictably in local or CI environments.

## Why "safe" checkpoint loading?

PyTorch checkpoints are pickle files. When deserializing, arbitrary Python
code embedded in the file can run. The official documentation warns to
"never load a checkpoint from an untrusted source" because pickle is
inherently unsafe.
[PyTorch serialization warnings](https://pytorch.org/docs/stable/notes/serialization.html#warnings)
cover the threat model, and the beginner tutorial repeats the same
guidance when introducing checkpointing workflows.
[Saving and loading models — PyTorch tutorial](https://docs.pytorch.org/tutorials/beginner/saving_loading_models.html)

PyTorch 2.1 introduced `torch.load(..., weights_only=True)`, which limits
deserialization to tensors, containers, and other safe primitives. We
mirror the recommendation from the [`torch.load` reference](https://pytorch.org/docs/stable/generated/torch.load.html)
by enabling this parameter when `safe=True`. If the current runtime does
not expose the flag (older PyTorch), we fail closed with a clear
`RuntimeError` instead of silently falling back to unsafe behavior.

Static analysis tools also highlight the risk. Bandit rule `B614
(pytorch_load)` marks `torch.load` without `weights_only=True` as a
potential issue.
[Bandit security rule B614](https://bandit.readthedocs.io/en/latest/plugins/b614_pytorch_load.html)
When you can avoid pickle entirely, prefer formats that never execute
Python objects, such as
[`safetensors`](https://huggingface.co/docs/safetensors/index).

## What the regression test does

`tests/utils/test_checkpointing_safe_load.py` exercises both code paths of
`load_checkpoint` using a tensor-only state dict written with
`torch.save`:

- When the runtime supports `weights_only`, the call succeeds and returns
  a mapping containing genuine tensors.
- When the runtime lacks the parameter, `load_checkpoint(..., safe=True)`
  raises `RuntimeError`. This protects consumers who expect the safer
  behavior.
- We also assert that `safe=False` always loads successfully (trusted
  path), ensuring that the non-restricted mode still round-trips the
  same artifact.

The test intentionally saves only tensors—no custom classes or lambda
objects—because the goal is validating the safety gate and confirming
that the helper returns tensors unchanged.

## Running the test locally

For deterministic local runs, disable auto-loading of third-party pytest
plugins. This prevents stray plugins from interfering with collection or
fixtures.

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/utils/test_checkpointing_safe_load.py
```
If PyTorch is unavailable, the test module calls
[`pytest.importorskip`](https://docs.pytest.org/en/stable/reference/reference.html#pytest.importorskip)
to skip gracefully. The `tmp_path` fixture handles temporary directories
with no extra setup.

## References

1. PyTorch — [Serialization notes: warnings](https://pytorch.org/docs/stable/notes/serialization.html#warnings)
2. PyTorch — [Saving and loading models tutorial](https://docs.pytorch.org/tutorials/beginner/saving_loading_models.html)
3. PyTorch — [`torch.load` API reference](https://pytorch.org/docs/stable/generated/torch.load.html)
4. PyCQA Bandit — [`B614: pytorch_load`](https://bandit.readthedocs.io/en/latest/plugins/b614_pytorch_load.html)
5. Hugging Face — [`safetensors` documentation](https://huggingface.co/docs/safetensors/index)
6. pytest — [`importorskip` reference](https://docs.pytest.org/en/stable/reference/reference.html#pytest.importorskip)
