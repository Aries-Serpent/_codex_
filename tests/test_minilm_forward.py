import pytest

torch = pytest.importorskip("torch", reason="torch not installed")
import torch.nn.functional as F  # noqa: E402

from codex_ml.models import MiniLM, MiniLMConfig  # noqa: E402


def test_minilm_overfits_tiny_batch():
    cfg = MiniLMConfig(vocab_size=10, n_layers=1, d_model=16, n_heads=4, max_seq_len=8)
    model = MiniLM(cfg)
    opt = torch.optim.AdamW(model.parameters(), lr=0.05)
    sched = torch.optim.lr_scheduler.StepLR(opt, step_size=50, gamma=0.5)

    data = torch.tensor([[1, 2, 3, 4, 5, 6, 7, 8]])
    targets = torch.tensor([[2, 3, 4, 5, 6, 7, 8, 9]])

    for _ in range(200):
        opt.zero_grad()
        logits = model(data)
        loss = F.cross_entropy(logits.view(-1, cfg.vocab_size), targets.view(-1))
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        sched.step()
        if loss.item() < 0.05:
            break

    logits = model(data)
    preds = logits.argmax(-1)
    assert torch.equal(preds, targets)
