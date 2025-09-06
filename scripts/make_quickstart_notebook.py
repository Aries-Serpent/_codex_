from __future__ import annotations

import nbformat as nbf


def main() -> None:
    nb = nbf.v4.new_notebook()
    nb.metadata["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    nb.metadata["language_info"] = {"name": "python", "pygments_lexer": "ipython3"}

    cells = []
    cells.append(
        nbf.v4.new_markdown_cell(
            """# Codex Quick‑Start (Offline)

This notebook trains a tiny model on a synthetic dataset and logs metrics to TensorBoard. It is designed to run **offline** on CPU in under two minutes.
"""
        )
    )
    cells.append(
        nbf.v4.new_code_cell(
            """import os, random, math
from pathlib import Path
import torch
from datasets import Dataset
from transformers import DataCollatorForLanguageModeling, Trainer, TrainingArguments
from codex_ml.modeling.codex_model_loader import load_model_with_optional_lora
from codex_ml.tokenization.train_tokenizer import TrainTokenizerConfig, run as train_tokenizer
from interfaces.tokenizer import HFTokenizer
random.seed(0)
torch.manual_seed(0)
print('PyTorch', torch.__version__)
"""
        )
    )
    cells.append(
        nbf.v4.new_code_cell(
            """# 1) Build a tiny in-memory corpus
texts = ['hello world', 'foo bar', 'lorem ipsum'] * 100
Path('runs').mkdir(exist_ok=True)
with open('runs/tiny_corpus.txt', 'w', encoding='utf-8') as fh:
    fh.write('\\n'.join(texts))
texts[:3]
"""
        )
    )
    cells.append(
        nbf.v4.new_code_cell(
            """# 2) Train a tokenizer from the corpus (offline)
cfg = TrainTokenizerConfig(input_file='runs/tiny_corpus.txt', output_dir='runs/tokenizer', vocab_size=50)
train_tokenizer(cfg)
tk = HFTokenizer(name_or_path=None, artifacts_dir='runs/tokenizer', max_length=64, padding='max_length', truncation=True)
print('Vocab size', tk.vocab_size)
"""
        )
    )
    cells.append(
        nbf.v4.new_code_cell(
            """# 3) Prepare datasets

ds = Dataset.from_dict({'text': texts})

def encode(batch):
    ids = tk.batch_encode(batch['text'])
    return {'input_ids': ids, 'labels': ids}

tokenized = ds.map(encode, batched=True, remove_columns=['text'])
split = tokenized.train_test_split(test_size=0.2, seed=0)
train_ds, val_ds = split['train'], split['test']
len(train_ds), len(val_ds)
"""
        )
    )
    cells.append(
        nbf.v4.new_code_cell(
            """# 4) Load a tiny decoder-only model
model = load_model_with_optional_lora('decoder_only', model_config={'vocab_size': tk.vocab_size, 'd_model':32, 'n_heads':4, 'n_layers':2, 'max_seq_len':64})
"""
        )
    )
    cells.append(
        nbf.v4.new_code_cell(
            """# 5) Train with HF Trainer
collator = DataCollatorForLanguageModeling(tk._tk, mlm=False)
args = TrainingArguments(
    output_dir='runs/quickstart',
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    max_steps=20,
    eval_steps=10,
    logging_steps=5,
    save_steps=20,
    report_to=['tensorboard'],
    logging_dir='runs/tb',
    remove_unused_columns=False,
)
trainer = Trainer(model=model, args=args, train_dataset=train_ds, eval_dataset=val_ds, data_collator=collator)
trainer.train()
"""
        )
    )
    cells.append(
        nbf.v4.new_code_cell(
            """# 6) Evaluate and log perplexity
import csv
metrics = trainer.evaluate()
ppl = math.exp(metrics['eval_loss'])
with open('runs/eval.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['metric', 'value'])
    writer.writerow(['perplexity', ppl])
print('Perplexity', ppl)
"""
        )
    )
    cells.append(
        nbf.v4.new_code_cell(
            """# 7) Inspect generated checkpoints
import os
os.listdir('runs/quickstart')
"""
        )
    )
    cells.append(
        nbf.v4.new_markdown_cell(
            """TensorBoard logs are written under `runs/tb`.
Launch with:

```
tensorboard --logdir runs/tb
```

Remove the `runs/` directory to clean up.
"""
        )
    )

    nb.cells = cells
    nbf.write(nb, "notebooks/quick_start.ipynb")


if __name__ == "__main__":
    main()
