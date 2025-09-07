# Privacy

Differential privacy training can be enabled via the training config:

```yaml
privacy:
  enabled: true
  noise_multiplier: 1.0
  max_grad_norm: 1.0
```

The training loop integrates `opacus` when available and logs the privacy budget.
