# Safety policy guidance

The `codex_ml` demos ship with a default policy (`configs/base/safety/policy.yaml`) that implements
three layers of defence:

1. **Prompt/output sanitisation** (`sanitize_prompt`, `sanitize_output`) redacts secrets and PII
   before data reaches logs, checkpoints, or stdout.
2. **Policy rules** combine literal/regex matches with severities and actions (`block`, `redact`,
   `flag`). Matching rules are logged to `.codex/safety/events.ndjson` with structured metadata.
3. **Optional classifiers** (`CODEX_SAFETY_CLASSIFIER=module:function`) can veto content that passes
   the static rules.

This document explains how to extend the policy safely and how to exercise the runtime toggles.

## YAML schema overview

```yaml
version: 1
log_path: .codex/safety/events.ndjson  # optional override for audit trail
bypass: false                          # default; set true only for offline experiments
allow:                                 # optional allow-list for legit edge cases
  literals: ["rm -rf build"]
  patterns:
    - pattern: "(?i)test(_|-)?password"
      flags: [IGNORECASE]             # re module flags (always uppercase)
rules:
  - id: secrets-redact                # stable identifier for logs/tests
    description: Redact obvious secrets
    reason: credential_leak           # free-form tag surfaced in logs
    severity: high                    # informational label; no behavioural change
    action: redact                    # redact, block, or flag
    replacement: "{REDACTED:SECRET}"  # optional; defaults to `{REDACTED}`
    applies_to: [prompt, output]      # prompt/output/all
    match:
      literals: ["format c:"]        # string literals are matched case-insensitively
      patterns:
        - "AKIA[0-9A-Z]{16}"         # raw regex
        - pattern: "(?i)api[-_]?key\\s*[:=]"  # regex + inline flags
          flags: [IGNORECASE]
```text
Key points:

* Omit `applies_to` to target both prompts and outputs.
* Multiple literals/patterns can be bundled under one rule; each hit is logged with the rule ID.
* `action: block` raises `SafetyViolation` unless a bypass is active or an allow-rule matches.
* `action: redact` substitutes matches and keeps the request alive.
* `action: flag` (supported implicitly) logs the event but allows the request to proceed.

## Runtime controls

* **Bypass single command** – `codex generate --safety-bypass --prompt "rm -rf /"`
* **Disable enforcement entirely** – `codex generate --no-safety ...` (sanitisers still run).
* **Programmatic bypass** – set `CODEX_SAFETY_BYPASS=1` in the environment (also honoured by the
  training helpers).
* **Custom policy file** – `codex generate --safety-policy path/to/policy.yaml`.
* **External classifier** – `CODEX_SAFETY_CLASSIFIER=my.module:allow_fn`. The callable should return
  truthy to allow content; falsy values are treated as `block` actions.

### Moderation adapter

In addition to the rule-driven filters above, `TrainingRunConfig.safety.moderation` enables a
moderation adapter that vets prompts and generated text before they are used. The adapter checks a
pluggable provider (e.g. `module:function`) and always falls back to the repository’s offline policy
(`configs/base/safety/policy.yaml`) so the checks succeed without network access. The core options are:

| Field | Description |
| --- | --- |
| `enabled` | Toggle moderation for the run. |
| `provider` | Optional `module:function` for custom classifiers (default `offline`). |
| `rules_path` | Override path to a policy file for the offline fallback. |
| `fail_open` | Allow execution to continue when moderation blocks content (event is logged). |
| `audit_log` | NDJSON file capturing moderation decisions for auditors. |
| `label` | Free-form tag written to audit records (defaults to `default`). |

Example Hydra override:

```bash
python -m codex_ml.cli.train training.safety.moderation.enabled=true \
  training.safety.moderation.audit_log=artifacts/safety/moderation.ndjson
```text

The CLI also exposes the adapter. To moderate prompts and outputs offline:

```bash
python -m codex_ml.cli.infer --prompt "hello" --moderation --moderation-audit-log artifacts/safety/moderation.ndjson
```text

## Logging & auditing

* Events are appended to `.codex/safety/events.ndjson`. Each entry contains `event`, `rule_id`,
  `action`, `severity`, `stage`, and the sanitised payloads.
* Training failures triggered by `SafetyViolation` are also recorded via `log_error("train.safety", …)`.
* Rotate or archive `.codex/safety/*.ndjson` as appropriate for your environment.
* Keep secrets in `.env` (generated from `.env.example`). The template is tracked,
  but real `.env` files are ignored via `.gitignore`, and the
  `block-env-files` pre-commit hook blocks them (and related dotfiles like
  `.envrc`) from entering the repository.

## Testing changes

* Add deterministic tests under `tests/test_safety.py` or `tests/safety/` that exercise both block
  and redact code paths.
* Use `pytest --cov` (or `nox -s tests`) to ensure the coverage gate ≥80% is maintained.
* When introducing new patterns, include positive and negative test cases to avoid regressions.

## Best practices

* Prefer non-backtracking regex constructs (use `?=` lookaheads sparingly) to avoid latency spikes.
* Keep literals lowercased unless case sensitivity is important; matching is case-insensitive by
  default.
* Document high-severity rules with a `description` and `reason` so operators understand why a
  violation triggered.
* Store local policies next to experiment configs and override them with `--safety-policy` during
  runs; do not edit the shared defaults unless the change should apply to everyone.
* Red-team new policies in a disposable environment before enabling them in automation.
