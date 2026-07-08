#     else:
#         # If peft couldn't apply LoRA to MiniLM (no matching target_modules),
#         # verify training still ran (all params trainable as baseline)
#         assert len(trainable) > 0, "model should have trainable parameters"
