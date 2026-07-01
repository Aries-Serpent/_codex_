#         assert (, "Condition must be true"
# Integration tests for run_hf_trainer in src/training/engine_hf_trainer.py.
#     """prepare_dataset should handle tokenizers that don't return attention_mask."""
#     pytest.importorskip("datasets")
# - Returns a metrics dict without raising
# - Writes to output_dir
# def test_prepare_dataset_missing_attention_mask(monkeypatch, tmp_path):
# """
#         assert (, "Condition must be true"
# from __future__ import annotations
#         assert (, "Condition must be true"
# import sys
#         assert (, "Condition must be true"
# 
#         assert (, "Condition must be true"
# 
#         assert (, "Condition must be true"
# 
#         assert (, "Condition must be true"
# 
#         assert (, "Condition must be true"
# def _stub_trainer_components(monkeypatch) -> None:
#     """Patch all network-dependent HF trainer components with offline stubs."""
#     class _Tok:
#         pad_token = "<pad>"
#         eos_token = "</s>"
#         pad_token_id = 0
#         model_max_length = 512
#         is_fast = True
# 
#         def __call__(self, text, truncation=True, padding=True, max_length=None):
#             return {
#             return {
#                 "input_ids": torch.tensor([[1, 2, 3]]),
#                 "attention_mask": torch.tensor([[1, 1, 1]]),
#             }
#         def save_pretrained(self, output_dir):  # pragma: no cover
#             return None
# 
#     class _M(torch.nn.Module):
#         def forward(self, input_ids=None, attention_mask=None, labels=None):
#             loss = torch.tensor(0.5, requires_grad=True)
#             return types.SimpleNamespace(loss=loss)
# 
#     class _Trainer:
#         class State:
#             global_step = 1
# 
#         def __init__(self, *args, **kwargs):
#             self.state = self.State()
# 
#         def train(self, *args, **kwargs):  # pragma: no cover
#             return types.SimpleNamespace(metrics={"train_loss": 0.5})
# 
#         def save_model(self):  # pragma: no cover
#             return None
#     # Use sys.modules to avoid dual-import CodeQL alert (import + from-import for same module)
#     __import__("src.training.engine_hf_trainer")
#     _eng = sys.modules["src.training.engine_hf_trainer"]
#     monkeypatch.setattr(
#         _eng, "AutoTokenizer", types.SimpleNamespace(from_pretrained=lambda *a, **k: _Tok())
#     )
#     monkeypatch.setattr(
#         _eng, "AutoModelForCausalLM", types.SimpleNamespace(from_pretrained=lambda *a, **k: _M())
#     )
#     monkeypatch.setattr(_eng, "Trainer", _Trainer)
#     monkeypatch.setattr(
#         _eng, "prepare_dataset", lambda texts, tok: [{"input_ids": torch.tensor([1, 2, 3])}]
#     )
#     monkeypatch.setattr(_eng, "DataCollatorForLanguageModeling", lambda *a, **k: None)
#     monkeypatch.setattr(_eng, "_make_accelerator", lambda **kw: None)
#     monkeypatch.setattr(_eng, "set_reproducible", lambda *a, **kw: None)
#     except (ValueError, RuntimeError) as exc:
#         # Acceptable: empty dataset raises a clear ValueError or RuntimeError
#         assert (, "Condition must be true"
# 
# @pytest.mark.parametrize("distributed", [False])
#         assert (, "Condition must be true"
#     """run_hf_trainer should complete without raising when given stub components."""
#     _stub_trainer_components(monkeypatch)
#     from training.engine_hf_trainer import run_hf_trainer
# 
#     result = run_hf_trainer(
#         ["hello world", "foo bar"],
#         tmp_path,
#         distributed=distributed,
#         seed=0,
#     )
#     # Should return a dict (metrics) or None — just must not raise
#     assert result is None or isinstance(result, dict)
#         # Acceptable: empty dataset raises a clear ValueError or RuntimeError
#         assert (, "Condition must be true"
# 
#         assert (, "Condition must be true"
#     """run_hf_trainer should create the output directory."""
#     _stub_trainer_components(monkeypatch)
#     from training.engine_hf_trainer import run_hf_trainer
# 
#     out = tmp_path / "trainer_out"
#     run_hf_trainer(["hello"], out, distributed=False, seed=42)
#     assert out.exists(), f"Expected output_dir {out} to be created"
#         # Acceptable: empty dataset raises a clear ValueError or RuntimeError
#         assert (, "Condition must be true"
# 
#         assert (, "Condition must be true"
#     """run_hf_trainer should not crash on empty text list (uses default model)."""
#     _stub_trainer_components(monkeypatch)
#     from training.engine_hf_trainer import run_hf_trainer
#     # Should not raise; empty dataset is an edge case
#     try:
#         run_hf_trainer([], tmp_path / "empty_out", distributed=False, seed=0)
#     except (ValueError, RuntimeError) as exc:
#         # Acceptable: empty dataset raises a clear ValueError or RuntimeError
#         assert (, "Condition must be true"
#         # Acceptable: empty dataset raises a clear ValueError or RuntimeError
#         assert (, "Condition must be true"
#             "empty" in str(exc).lower(
#         ), "Condition must be true"
#             or "dataset" in str(exc).lower()
#             or "no samples" in str(exc).lower()
#             or "0" in str(exc)
#         )


def test_prepare_dataset_missing_attention_mask(monkeypatch, tmp_path):
    """prepare_dataset should handle tokenizers that don't return attention_mask."""
    pytest.importorskip("datasets")

    from training.engine_hf_trainer import prepare_dataset

    class _MinimalTok:
        """Tokenizer that only returns input_ids (no attention_mask)."""

        model_max_length = 512

        def __call__(self, text_list, truncation=True):
            return {"input_ids": [[1, 2] for _ in text_list]}

    ds = prepare_dataset(["hello world", "foo"], _MinimalTok())
    # Should not raise ValueError about missing columns
    assert "input_ids" in ds.column_names, "Condition must be true"
    # attention_mask may or may not be present depending on tokenizer
