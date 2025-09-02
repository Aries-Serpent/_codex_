from codex_ml.tokenization.hf_tokenizer import HFTokenizerAdapter


def test_batch_encode_shapes(monkeypatch):
    class DummyTok:
        def __call__(self, texts, padding, truncation, max_length, return_tensors):
            class Out(dict):
                def __getitem__(self, key):
                    return type(
                        "T",
                        (),
                        {
                            "shape": (len(texts), max_length or 4),
                            "tolist": lambda self: [[0] * (max_length or 4)] * len(texts),
                        },
                    )()

            return Out({"input_ids": None, "attention_mask": None})

    adp = HFTokenizerAdapter(DummyTok())
    enc = adp.batch_encode(["a", "bb"], max_length=6, return_dict=True)
    assert enc["input_ids"].shape == enc["attention_mask"].shape
