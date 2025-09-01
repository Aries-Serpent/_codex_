<!-- BEGIN: CODEX_DOCS_SAFETY -->

# Safety

Codex provides several layers of safeguards to reduce accidental leakage and
harmful behaviour:

- Blocklist/allowlist regex heuristics filter disallowed prompts.
- Logits masking helper prevents generation of known unsafe tokens.
- Sandboxed subprocess execution for tools with strict timeout limits.
- API layer masks strings resembling API keys (e.g. `sk-...`) unless
  `DISABLE_SECRET_FILTER=1`.
- Request rate limiting defends against abuse of public endpoints.
- Red-team evaluation using datasets like
  [RealToxicityPrompts](https://huggingface.co/datasets/allenai/real-toxicity-prompts)
  and curated leaked‑credential corpora.

### Guidelines

1. Run `pre-commit run --all-files` before committing to catch security issues.
2. Store secrets in environment variables; never hard-code credentials.
3. Review model outputs for prompt‑injection attempts and document mitigations.

Future iterations will include automated red-team harnesses and expanded
coverage of model and data card requirements.
