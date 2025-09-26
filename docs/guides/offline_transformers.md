# Offline ML Toolkit Hardening

This playbook consolidates the fixes adopted in the hardening round for `_codex_`.
Each subsection cites the upstream guidance so the workflow can be reproduced on
air‑gapped hosts.

## Verify PyTorch Wheels

Partial or "stub" wheels occasionally ship with only a minimal module that lacks
`torch.utils.data.Dataset`. Use the helper added in
`codex_local_gates.sh`/`tests/conftest.py`:

```bash
python -m codex_ml.utils.torch_checks
```
If the diagnostic reports a missing dataset, reinstall the official CPU wheels:

```bash
python -m pip install torch torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/cpu
```
The PyTorch team documents the dedicated index URLs in their "Start Locally"
matrix, which is the canonical reference for offline wheel selection.[^pytorch]

## Transformers Offline Mode & Cache Layout

The gate script exports the full suite of offline cache variables:

```bash
export HF_HOME=${HOME}/.cache/huggingface
export HF_HUB_CACHE="$HF_HOME/hub"
export TRANSFORMERS_CACHE="$HF_HOME/transformers"
export HF_DATASETS_CACHE="$HF_HOME/datasets"
export TRANSFORMERS_OFFLINE=1
export HF_HUB_OFFLINE=1
export HF_DATASETS_OFFLINE=1
```
This mirrors the Transformers installation guidance for disconnected
environments.[^hf-install] Populate the caches ahead of time with
`huggingface_hub.snapshot_download`, which is the supported method for
pre-caching repositories.[^hf-snapshot]

## Pytest Guards for Optional Dependencies

Tests now treat an incomplete PyTorch install the same as a missing import, so
`pytest.importorskip("torch")` skips gracefully instead of erroring. This
follows the pytest recommendation for optional dependencies.[^pytest]

## Coverage Gates with Environment Overrides

`nox -s tests` honours `COVERAGE_MIN`, falling back to the legacy
`COV_FAIL_UNDER` and defaulting to 85% if neither is set. Invoke the gate with:

```bash
COVERAGE_MIN=60 nox -s tests
```
This keeps the simple override suggested in the nox documentation for running
`session.run` with environment-provided flags.[^nox]

[^pytorch]: [PyTorch — Get Started Locally](https://pytorch.org/get-started/locally/)
[^hf-install]: [Transformers — Offline Mode](https://huggingface.co/docs/transformers/main/installation)
[^hf-snapshot]: [huggingface_hub — Download files from the Hub](https://huggingface.co/docs/huggingface_hub/en/guides/download)
[^pytest]: [pytest API Reference — `importorskip`](https://docs.pytest.org/en/stable/reference/reference.html)
[^nox]: [nox — Sessions and environment variables](https://nox.thea.codes/en/stable/usage.html)
