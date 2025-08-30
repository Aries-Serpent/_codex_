from interfaces.tokenizer import HFTokenizer


def test_padding_truncation_shapes():
    tk = HFTokenizer(
        "distilbert-base-uncased",
        max_length=8,
        padding="max_length",
        truncation=True,
    )
    out = tk.batch_encode(["hello", "this is a longer sentence"], return_dict=True)
    ids = out["input_ids"]
    assert all(len(seq) == 8 for seq in ids)
    assert "attention_mask" in out and all(len(m) == 8 for m in out["attention_mask"])
