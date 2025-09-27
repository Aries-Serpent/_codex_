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

## Prompt sanitisation policy

Codex sanitises prompts and outputs before they are fed to a model. The
default policy now:

- Uses `yaml.safe_load` when parsing optional policy snippets so untrusted YAML
  cannot instantiate arbitrary Python objects.
- Ships an extended library of regular expressions that catch common secret
  formats (AWS, Google, Slack), credential key/value pairs, private key blocks,
  and email addresses.
- Allows opt-in policy extensions via small YAML fragments:

```yaml
# policy.yaml
regex:
  - (?i)customer_id\s*[:=]\s*\d+
pii:
  - \b\d{4}-\d{4}-\d{4}-\d{4}\b
```

Apply the overrides by passing the YAML string to `sanitize_prompt` (or wiring
them into the `SafetyConfig` used by training/evaluation tooling). Invalid or
malicious YAML is ignored and the base policy remains in effect.

## Local secret scanning

Use the lightweight scanner to spot obvious secrets before pushing changes:

```bash
make codex-secrets-scan              # scans git diff against HEAD
python tools/scan_secrets.py docs/   # scan specific paths
```

The script runs locally, requires no external services, and flags any lines
matching built-in credential patterns. Review findings carefully—some false
positives are expected when working with fixtures and test data.
