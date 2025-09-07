from codex_ml.eval.datasets import Example, load_dataset


def test_load_hf_dataset() -> None:
    data = load_dataset("hf://hf-internal-testing/tiny-wikitext-2", max_samples=2, hf_split="train")
    assert len(data) == 2
    assert all(isinstance(item, Example) for item in data)
    assert data[0].input == data[0].target
