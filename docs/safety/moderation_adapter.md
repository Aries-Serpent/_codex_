# Moderation adapter

The moderation adapter supplements the existing safety filters with an explicit
pre-/post-flight check before prompts are ingested or model outputs are returned.
It is built to work offline by default and can layer additional providers when
needed.

## How it works

1. **Provider call (optional).** If `provider` is configured, the adapter imports
   the `module:function` pair and passes the text plus the stage (`prompt` or
   `output`). Any truthy `approved` response is honoured.
2. **Offline fallback.** Regardless of the provider outcome, the adapter
   evaluates the text against the repository policy
   (`configs/base/safety/policy.yaml` by default). This keeps the guard in place even
   when the provider is unreachable.
3. **Decision logging.** Blocks raise `ModerationRejection` unless `fail_open`
   is set. When an `audit_log` path is supplied, each decision is appended as an
   NDJSON object with a content digest and sanitized payload.

## Training configuration

Set the adapter through `TrainingRunConfig.safety.moderation`:

```yaml
safety:
  enabled: true
  policy_path: configs/base/safety/policy.yaml
  moderation:
    enabled: true
    provider: offline               # or module:function
    rules_path: configs/base/safety/policy.yaml
    fail_open: false
    audit_log: artifacts/safety/moderation.ndjson
    label: training
```text

Hydra overrides can toggle individual fields:

```bash
python -m codex_ml.cli.train \
  training.safety.moderation.enabled=true \
  training.safety.moderation.audit_log=artifacts/safety/moderation.ndjson
```text

When moderation blocks a prompt or sample, training raises `ModerationRejection`
with the offending rule IDs. The failure is also written to
`.codex/errors.ndjson` under the `train.moderation` step.

## CLI usage

The inference CLI exposes equivalent controls:

```bash
python -m codex_ml.cli.infer \
  --prompt "classify this support ticket" \
  --moderation \
  --moderation-policy configs/base/safety/policy.yaml \
  --moderation-audit-log artifacts/safety/moderation.ndjson
```text

Key flags:

- `--moderation` turns the adapter on.
- `--moderation-provider module:function` adds a custom classifier.
- `--moderation-fail-open` lets the run continue when a block occurs
  (the event is still logged).

The CLI manifest (`artifacts/infer/<timestamp>.json`) records both the original
prompt and the moderated result along with the moderation decision metadata.

## Auditing

Audit entries are JSON lines in the configured file:

```json
{
  "event": "moderation.decision",
  "timestamp": "Previous Cycle-01-18T12:34:56Z",
  "stage": "prompt",
  "provider": "offline",
  "approved": true,
  "matches": [],
  "fail_open": false,
  "label": "cli.infer",
  "original_digest": "5c0495…"
}
```text

Use `jq` or `tail -f` during incident response to monitor decisions. Because
only digests and sanitized text are stored, the log remains safe to share with
security reviewers.
