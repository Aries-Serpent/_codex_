# Differential Privacy & Secret Redaction

Codex ML includes first-class hooks for privacy-preserving fine-tuning. The `DifferentialPrivacyConfig`
provides a lightweight façade over [Opacus](https://opacus.ai/) so you can enable DP-SGD with a single
configuration block. The logging stack also performs automatic redaction to prevent accidental leakage of
API keys and personally identifiable information (PII).

## Differential privacy configuration

Create a configuration object and pass it to `run_training`:

```python
from codex_ml.training.dp_config import DifferentialPrivacyConfig, make_private_model

config = DifferentialPrivacyConfig(
    enabled=True,
    epsilon=1.0,
    delta=1e-5,
    noise_multiplier=1.2,
    max_grad_norm=1.0,
)
```text

The training loop accepts either a `DifferentialPrivacyConfig` instance or a dictionary loaded from your Hydra
configuration. When `enabled=True`, Opacus wraps the model, optimizer, and data loader, ensuring gradients are
clipped and noise is injected according to the configuration.

### CLI usage

```bash
# configs/training/profiles/default.yaml
telemetry:
  metrics_enable: true

differential_privacy:
  enabled: true
  epsilon: 1.0
  delta: 1e-5
  noise_multiplier: 1.2
  max_grad_norm: 1.0
```text

The CLI automatically forwards the `differential_privacy` section to the training loop. Alternatively set
`CODEX_DP_ENABLED=1` and optional overrides (`CODEX_DP_EPSILON`, `CODEX_DP_NOISE_MULTIPLIER`, etc.) to configure DP
purely via environment variables.

## Secret redaction

Structured session and metrics logs are processed by `SecretRedactor` before being persisted. The utility removes
API keys, bearer tokens, AWS secrets, passwords, and emails using regex-based detection:

```python
from codex_ml.safety.redaction import SecretRedactor

redactor = SecretRedactor()
redacted = redactor.redact("api_key=sk-1234567890")
# -> "api_key=[REDACTED_API_KEY]"
```text

Nested dictionaries and lists are supported through `redact_dict`, making it safe to redact configuration payloads
before logging.

## Operational guidance

* Install Opacus when enabling DP: `pip install opacus`.
* Monitor the `codex_ml_training_steps_total` counter to ensure DP-enabled runs progress as expected.
* Retain the `.codex/logs/session_<ID>.jsonl` artifacts to prove that secret redaction is functioning during audits.
