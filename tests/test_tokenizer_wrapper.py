from codex_ml.interfaces.tokenizer import HFTokenizer


def test_padding_truncation_shapes():
    tk = HFTokenizer(
        "hf-internal-testing/tiny-random-bert",
        max_length=8,
        padding="max_length",
        truncation=True,
    )
    out = tk.batch_encode(["hello", "this is a longer sentence"])
    assert all(len(ids) == 8 for ids in out)
