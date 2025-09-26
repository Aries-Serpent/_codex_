# Bandit Fixes & Rationale (Offline)

This document summarises remediations applied after Bandit findings and provides
context for future audits.

## B101: `assert` used for runtime checks

Assertions can be stripped with the `-O` flag, which would bypass important
validations. We replace them with explicit runtime checks and raise meaningful
exceptions instead.

## B404/B603/B607: `subprocess` usage

- Always run commands with `shell=False`.
- Resolve executables via `shutil.which` to enforce absolute paths and avoid
  PATH hijacking.
- Document vetted call sites with `# nosec` comments once inputs are validated.

## B110/B112: Broad exception handling

Where broad `except` clauses are required for resilience, we now log the
exception at `DEBUG` level and annotate the block with `# nosec` to indicate the
intentional handling strategy.

## B105/B106: Hard-coded placeholders

Strings such as `"{REDACTED}"` and `"[UNK]"` are UI placeholders or special
tokens rather than secrets. We annotate these occurrences with `# nosec` and
reference this document.

## B311: Non-cryptographic PRNG

`random.Random` is used solely for deterministic sampling in demos and tests.
We document this and suppress the finding with `# nosec`.

## B614: Unsafe `torch.load`

We default to `torch.load(..., weights_only=True, map_location="cpu")` and
refuse to proceed when the installed PyTorch lacks `weights_only`. For
untrusted checkpoints prefer safer formats such as `safetensors`.

---

**Local testing**

- Run `bandit -r src` after changes.
- Execute `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q` for deterministic test
  runs.
