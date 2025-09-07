from unittest.mock import call, patch

from codex_ml.eval.datasets import Example, load_dataset


def test_load_hf_dataset() -> None:
    class DummyHFDS:
        column_names = ["text"]

        def __getitem__(self, key: str):  # pragma: no cover - simple stub
            return ["a", "b", "c"]

    def loader(dataset_name: str, config: str | None, *, split: str):
        if dataset_name == "hf-internal-testing" and config == "tiny-wikitext-2":
            raise FileNotFoundError
        return DummyHFDS()

    with patch(
        "codex_ml.eval.datasets.hf_load_dataset", side_effect=loader
    ) as mock_load, patch("codex_ml.eval.datasets.HAS_DATASETS", True):
        data = load_dataset(
            "hf://hf-internal-testing/tiny-wikitext-2",
            max_samples=2,
            hf_split="train",
        )
        assert mock_load.call_args_list == [
            call("hf-internal-testing", "tiny-wikitext-2", split="train"),
            call("hf-internal-testing/tiny-wikitext-2", None, split="train"),
        ]
        assert len(data) == 2
        assert all(isinstance(item, Example) for item in data)
        assert data[0].input == data[0].target


def test_load_hf_dataset_with_owner_and_config() -> None:
    class DummyHFDS:
        column_names = ["text"]

        def __getitem__(self, key: str):  # pragma: no cover - simple stub
            return ["sample"]

    with patch(
        "codex_ml.eval.datasets.hf_load_dataset", return_value=DummyHFDS()
    ) as mock_load, patch("codex_ml.eval.datasets.HAS_DATASETS", True):
        data = load_dataset("hf://openai/gsm8k/main", max_samples=1)
        mock_load.assert_called_once_with("openai/gsm8k", "main", split="train")
        assert data == [Example("sample", "sample")]


def test_load_hf_dataset_with_config_only() -> None:
    class DummyHFDS:
        column_names = ["text"]

        def __getitem__(self, key: str):  # pragma: no cover - simple stub
            return ["sample"]

    with patch(
        "codex_ml.eval.datasets.hf_load_dataset", return_value=DummyHFDS()
    ) as mock_load, patch("codex_ml.eval.datasets.HAS_DATASETS", True):
        data = load_dataset("hf://glue/mrpc", max_samples=1)
        mock_load.assert_called_once_with("glue", "mrpc", split="train")
        assert data == [Example("sample", "sample")]
