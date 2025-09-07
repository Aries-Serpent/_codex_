from unittest.mock import patch

from codex_ml.eval.datasets import Example, load_dataset


def test_load_hf_dataset() -> None:
    class DummyHFDS:
        column_names = ["text"]

        def __getitem__(self, key: str):  # pragma: no cover - simple stub
            return ["a", "b", "c"]

    with patch(
        "codex_ml.eval.datasets.hf_load_dataset",
        return_value=DummyHFDS(),
    ) as mock_load:
        data = load_dataset(
            "hf://hf-internal-testing/tiny-wikitext-2",
            max_samples=2,
            hf_split="train",
        )
        mock_load.assert_called_once_with(
            "hf-internal-testing/tiny-wikitext-2",
            None,
            split="train",
        )
        assert len(data) == 2
        assert all(isinstance(item, Example) for item in data)
        assert data[0].input == data[0].target


def test_load_hf_dataset_with_owner_and_config() -> None:
    class DummyHFDS:
        column_names = ["text"]

        def __getitem__(self, key: str):  # pragma: no cover - simple stub
            return ["sample"]

    with patch("codex_ml.eval.datasets.hf_load_dataset", return_value=DummyHFDS()) as mock_load:
        data = load_dataset("hf://openai/gsm8k/main", max_samples=1)
        mock_load.assert_called_once_with("openai/gsm8k", "main", split="train")
        assert data == [Example("sample", "sample")]
