# BEGIN: CODEX_SMOKE_TRAINER
import os, tempfile
from pathlib import Path
import pytest


def test_hf_trainer_on_tiny_hello_dataset():
    try:
        from datasets import Dataset
        from transformers import (
            AutoTokenizer,
            AutoModelForCausalLM,
            DataCollatorForLanguageModeling,
            Trainer,
            TrainingArguments,
        )
    except Exception as e:
        pytest.skip(f"missing libs: {e}")

    texts = [
        "Hello Codex, this is a tiny trainer smoke test.",
        "Small data, small model, single-step training.",
    ]
    ds = Dataset.from_list([{"text": t} for t in texts])

    model_id = "sshleifer/tiny-gpt2"
    tok = AutoTokenizer.from_pretrained(model_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    def tok_fn(batch):
        return tok(batch["text"], truncation=True, padding="max_length", max_length=64)

    ds_tok = ds.map(tok_fn, batched=True, remove_columns=["text"])
    collator = DataCollatorForLanguageModeling(tokenizer=tok, mlm=False)
    model = AutoModelForCausalLM.from_pretrained(model_id)

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        args = TrainingArguments(
            output_dir=str(out),
            overwrite_output_dir=True,
            per_device_train_batch_size=2,
            num_train_epochs=1,
            max_steps=1,
            logging_steps=1,
            save_steps=1,
            report_to=[],
            fp16=False,
        )
        trainer = Trainer(
            model=model, args=args, train_dataset=ds_tok, data_collator=collator
        )
        trainer.train()
        assert (out / "trainer_state.json").exists()
        assert any(out.glob("checkpoint-*"))
