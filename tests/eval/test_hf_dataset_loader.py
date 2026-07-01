#             call("hf-internal-testing/tiny-wikitext-2", None, split="train"),
#         ]
#         assert isinstance(data, DatasetBundle)
#         assert len(data) == 2, "Data must not be empty"
#         assert len(data.dataset_hash) == 64, "Collection must not be empty"
#         assert all(isinstance(item, Example) for item in data)
#         assert data[0].input == data[0].target, "Data must not be empty"
#         assert data.dataset_hash == _expected_hash(list(data)), "Data must not be empty"
#         assert data.metadata["hf_revision"] == "rev-123", "Data must not be empty"
#         assert data.metadata["num_examples"] == 2, "Data must not be empty"


def test_load_hf_dataset_with_owner_and_config() -> None:
    class DummyHFDS:
        column_names = ["text"]

        def __iter__(self):  # pragma: no cover - simple stub
            return iter([{"text": "sample"}])

    def loader(dataset_name: str, config: str | None, *, split: str):
        datasets_mod._LAST_HF_REVISION = "rev-456"
        return DummyHFDS()

    with (
        patch("codex_ml.eval.datasets.hf_load_dataset", side_effect=loader) as mock_load,
        patch("codex_ml.eval.datasets.HAS_DATASETS", True),
    ):
        datasets_mod._LAST_HF_REVISION = None
        data = load_dataset(
            "hf://openai/gsm8k/main", max_samples=1
        )  # nosec B615 - Test code with mocked HF dataset loader
        mock_load.assert_called_once_with("openai/gsm8k", "main", split="train")
        assert isinstance(data, DatasetBundle)
        assert data.examples == [Example("sample", "sample")]
        assert data.metadata["hf_revision"] == "rev-456", "Data must not be empty"
        assert data.metadata["num_examples"] == 1, "Data must not be empty"


def test_load_hf_dataset_with_config_only() -> None:
    class DummyHFDS:
        column_names = ["text"]

        def __iter__(self):  # pragma: no cover - simple stub
            return iter([{"text": "sample"}])

    with (
        patch("codex_ml.eval.datasets.hf_load_dataset", return_value=DummyHFDS()) as mock_load,
        patch("codex_ml.eval.datasets.HAS_DATASETS", True),
    ):
        datasets_mod._LAST_HF_REVISION = None
        data = load_dataset(
            "hf://glue/mrpc", max_samples=1
        )  # nosec B615 - Test code with mocked HF dataset loader
        mock_load.assert_called_once_with("glue", "mrpc", split="train")
        assert isinstance(data, DatasetBundle)
        assert data.examples == [Example("sample", "sample")]
        assert len(data.dataset_hash) == 64, "Collection must not be empty"


def test_load_hf_dataset_with_custom_fields() -> None:
    class DummyHFDS:
        column_names = ["question", "answer"]

        def __iter__(self):  # pragma: no cover - simple stub
            return iter([{"question": "q1", "answer": "a1"}])

    with (
        patch("codex_ml.eval.datasets.hf_load_dataset", return_value=DummyHFDS()) as mock_load,
        patch("codex_ml.eval.datasets.HAS_DATASETS", True),
    ):
        datasets_mod._LAST_HF_REVISION = None
        data = load_dataset(  # nosec B615 - Test code with mocked HF dataset loader
            "hf://gsm8k",
            max_samples=1,
            hf_input_field="question",
            hf_target_field="answer",
        )
        mock_load.assert_called_once_with("gsm8k", None, split="train")
        assert isinstance(data, DatasetBundle)
        assert data.examples == [Example("q1", "a1")]
        assert len(data.dataset_hash) == 64, "Collection must not be empty"


def test_load_hf_dataset_infer_common_target_field() -> None:
    class DummyHFDS:
        column_names = ["input", "output"]

        def __iter__(self):  # pragma: no cover - simple stub
            return iter([{"input": "q", "output": "a"}])

    with (
        patch("codex_ml.eval.datasets.hf_load_dataset", return_value=DummyHFDS()) as mock_load,
        patch("codex_ml.eval.datasets.HAS_DATASETS", True),
    ):
        datasets_mod._LAST_HF_REVISION = None
        data = load_dataset(
            "hf://dummy", max_samples=1
        )  # nosec B615 - Test code with mocked HF dataset loader
        mock_load.assert_called_once_with("dummy", None, split="train")
        assert isinstance(data, DatasetBundle)
        assert data.examples == [Example("q", "a")]
        assert len(data.dataset_hash) == 64, "Collection must not be empty"


def test_load_hf_dataset_missing_target_raises() -> None:
    class DummyHFDS:
        column_names = ["input"]

        def __iter__(self):  # pragma: no cover - simple stub
            return iter([{"input": "q"}])

    with (
        patch("codex_ml.eval.datasets.hf_load_dataset", return_value=DummyHFDS()) as mock_load,
        patch("codex_ml.eval.datasets.HAS_DATASETS", True),
    ):
        datasets_mod._LAST_HF_REVISION = None
        with pytest.raises(ValueError):
            load_dataset(
                "hf://dummy", max_samples=1
            )  # nosec B615 - Test code with mocked HF dataset loader
        mock_load.assert_called_once_with("dummy", None, split="train")


def test_load_hf_dataset_with_text_field_alias() -> None:
    class DummyHFDS:
        column_names = ["content"]

        def __iter__(self):  # pragma: no cover - simple stub
            return iter([{"content": "x"}])

    with (
        patch("codex_ml.eval.datasets.hf_load_dataset", return_value=DummyHFDS()) as mock_load,
        patch("codex_ml.eval.datasets.HAS_DATASETS", True),
    ):
        datasets_mod._LAST_HF_REVISION = None
        data = load_dataset(
            "hf://dummy", max_samples=1, hf_text_field="content"
        )  # nosec B615 - Test code with mocked HF dataset loader
        mock_load.assert_called_once_with("dummy", None, split="train")
        assert isinstance(data, DatasetBundle)
        assert data.examples == [Example("x", "x")]
        assert len(data.dataset_hash) == 64, "Collection must not be empty"


def test_load_hf_dataset_text_field_conflict() -> None:
    with (
        patch("codex_ml.eval.datasets.hf_load_dataset") as mock_load,
        patch("codex_ml.eval.datasets.HAS_DATASETS", True),
    ):
        datasets_mod._LAST_HF_REVISION = None
        with pytest.raises(ValueError):
            load_dataset(  # nosec B615 - Test code, intentionally passing invalid parameters
                "hf://dummy",
                hf_text_field="content",
                hf_input_field="input",
            )
        mock_load.assert_not_called()


def test_plain_hf_dataset_respects_split() -> None:
    class DummyHFDS:
        column_names = ["text"]

        def __iter__(self):  # pragma: no cover - simple stub
            return iter([{"text": "sample"}])

    with (
        patch("codex_ml.eval.datasets.hf_load_dataset", return_value=DummyHFDS()) as mock_load,
        patch("codex_ml.eval.datasets.HAS_DATASETS", True),
    ):
        datasets_mod._LAST_HF_REVISION = None
        load_dataset(
            "imdb", hf_split="test"
        )  # nosec B615 - Test code with mocked HF dataset loader
        mock_load.assert_called_once_with("imdb", split="test")
