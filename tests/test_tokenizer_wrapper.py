from interfaces.tokenizer import HFTokenizer


def test_padding_truncation_shapes():
    tk = HFTokenizer(
        "distilbert-base-uncased",
        max_length=8,
        padding="max_length",
        truncation=True,
    )
    out = tk.encode(["hello", "this is a longer sentence"])
    assert out["input_ids"].shape[1] == 8
    assert out["attention_mask"].shape == out["input_ids"].shape
