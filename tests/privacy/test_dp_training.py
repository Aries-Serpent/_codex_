import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from training.functional_training import TrainCfg, run_custom_trainer


def test_dp_training_runs(tmp_path):
    try:
        import opacus  # noqa: F401
    except Exception:
        return
    model = AutoModelForSequenceClassification.from_pretrained("sshleifer/tiny-distilroberta-base")
    tokenizer = AutoTokenizer.from_pretrained("sshleifer/tiny-distilroberta-base")
    texts = ["hello world", "goodbye"]
    tokenized = tokenizer(texts, padding=True, return_tensors="pt")
    tokenized["labels"] = torch.tensor([0, 1])

    class DS(torch.utils.data.Dataset):
        def __len__(self):
            return 2

        def __getitem__(self, idx):
            return {k: v[idx] for k, v in tokenized.items()}

    ds = DS()
    cfg = TrainCfg(epochs=1, batch_size=2, dp_enabled=True, dp_noise_multiplier=1.0)
    out = run_custom_trainer(model, tokenizer, ds, None, cfg)
    assert "history" in out
