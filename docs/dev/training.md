# Training Loop Notes

The functional training loop (`codex_ml.training.functional_training.train`) is
designed for deterministic local runs where the Hugging Face trainer is not
available.  This section highlights a few implementation details that are easy
to overlook when extending the loop.

## Gradient accumulation

* `gradient_accumulation_steps` controls how many batches are processed before
  calling `optimizer.step()`.  The effective batch size for a single-process run
  becomes `batch_size × gradient_accumulation_steps`.  In distributed setups
  multiply by `world_size` as well.
* The loop divides the reported loss by `gradient_accumulation_steps` so that
  gradients match the large-batch baseline.  Logging, however, always records
  the raw (pre-division) loss for easier comparison across runs.
* Any remainder at the end of an epoch triggers a final optimiser step.  This
  "tail flush" avoids carrying gradients into the next epoch when the number of
  batches is not a multiple of the accumulation factor.

## AMP and gradient clipping

When automatic mixed precision (AMP) is enabled we create a `GradScaler` and
scale the divided loss before `backward()`.  Prior to clipping or stepping we
explicitly call `scaler.unscale_(optimizer)` to convert gradients back to FP32
and reuse the same clipping utility (`codex_ml.utils.train_helpers.clip_gradients`).
The helper degrades gracefully to a no-op if torch or AMP are unavailable.

Always call `optimizer.zero_grad(set_to_none=True)` after each update (including
the tail flush) to avoid retaining references to the previous computation graph
between accumulation windows.
