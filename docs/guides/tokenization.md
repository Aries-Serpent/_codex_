# Tokenization Guide
> Generated: 2025-10-17 21:05:18 UTC | Author: mbaetiong

Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

## Canonical Modules
- codex_ml.tokenization.adapter
- codex_ml.tokenization.hf_adapter
- codex_ml.tokenization.sentencepiece_adapter

## Optional Dependencies
- HuggingFace tokenizers / transformers (optional)
- sentencepiece (optional)

## Legacy Shims (Deprecation)
The following legacy imports remain for compatibility and emit DeprecationWarning:
- src.tokenization.api
- src.tokenization.sentencepiece_adapter

Prefer canonical modules for all new code paths.

## Fixtures & Offline Training
- See tools/make_spm_fixture.py for generating deterministic SPM fixtures.
