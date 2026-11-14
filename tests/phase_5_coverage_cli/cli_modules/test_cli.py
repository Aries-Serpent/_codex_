"""Tests for src/cli.py module."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

_CLI_MODULE_PATH = Path(__file__).resolve().parents[3] / "src" / "cli.py"
cli: ModuleType | None = None


@pytest.fixture(scope="module", autouse=True)
def load_standalone_cli():
    """Load the module under test by file path because ``cli`` resolves to a package."""
    global cli
    saved_path = list(sys.path)
    sentinel = object()
    module_names = ("cli", "cli.train_codex", "tokenization", "tokenization.loader")
    saved_modules = {name: sys.modules.get(name, sentinel) for name in module_names}
    spec = importlib.util.spec_from_file_location("_codex_standalone_cli", _CLI_MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["cli"] = module
    cli = module
    try:
        spec.loader.exec_module(module)
        yield module
    finally:
        sys.path[:] = saved_path
        cli = None
        for name, previous in saved_modules.items():
            if previous is sentinel:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = previous


@pytest.fixture
def cli_main_mocks(monkeypatch):
    """Prepare a complete, deterministic configuration for ``cli.main``."""
    from contextlib import nullcontext

    config = {
        "model": {"target": "model.Factory"},
        "optimizer": {"target": "optimizer.Factory"},
        "data": {"name": "synthetic_classification"},
        "loss": {},
        "metric": {},
        "trainer": {"epochs": 2},
        "logging": {},
        "device": "cpu",
    }
    calls = SimpleNamespace(
        initialize=MagicMock(return_value=nullcontext()),
        compose=MagicMock(return_value=object()),
        to_container=MagicMock(return_value=config),
        model=MagicMock(return_value=object()),
        optimizer=MagicMock(return_value=object()),
        loaders=MagicMock(return_value=("train-loader", "validation-loader")),
        loss=MagicMock(return_value="loss-function"),
        metric=MagicMock(return_value="metric-function"),
        trainer_config=MagicMock(),
        logging_config=MagicMock(),
    )
    trainer = MagicMock()
    monkeypatch.setattr(cli, "initialize_config_dir", calls.initialize)
    monkeypatch.setattr(cli, "compose", calls.compose)
    monkeypatch.setattr(cli.OmegaConf, "to_container", calls.to_container)
    monkeypatch.setattr(cli, "_instantiate_model", calls.model)
    monkeypatch.setattr(cli, "_instantiate_optimizer", calls.optimizer)
    monkeypatch.setattr(cli, "_resolve_dataloaders", calls.loaders)
    monkeypatch.setattr(cli, "_resolve_loss", calls.loss)
    monkeypatch.setattr(cli, "_resolve_metric", calls.metric)
    monkeypatch.setattr(cli, "TrainerConfig", calls.trainer_config)
    monkeypatch.setattr(cli, "LoggingConfig", calls.logging_config)
    monkeypatch.setattr(cli, "Trainer", MagicMock(return_value=trainer))
    calls.trainer = trainer
    return calls


class TestCliConstants:
    """Test module constants."""

    def test_cli_package_path_is_path(self) -> None:
        """Test CLI_PACKAGE_PATH is a Path."""
        assert isinstance(cli.CLI_PACKAGE_PATH, Path)

    def test_project_root_is_path(self) -> None:
        """Test PROJECT_ROOT is a Path."""
        assert isinstance(cli.PROJECT_ROOT, Path)

    def test_tokenization_dir_is_path(self) -> None:
        """Test TOKENIZATION_DIR is a Path."""
        assert isinstance(cli.TOKENIZATION_DIR, Path)


class TestCliHelperFunctions:
    """Test helper functions."""

    def test_section_to_dict_with_dict(self) -> None:
        """Test _section_to_dict with dict input."""
        section = {"key": "value", "nested": {"inner": "data"}}
        result = cli._section_to_dict(section)
        assert result == section, "Result must not be empty"
        assert isinstance(result, dict)

    def test_section_to_dict_with_none(self) -> None:
        """Test _section_to_dict with None input."""
        result = cli._section_to_dict(None)
        assert result == {}, "Result must not be empty"
        assert isinstance(result, dict)

    def test_section_to_dict_with_string(self) -> None:
        """Test _section_to_dict with non-dict input."""
        result = cli._section_to_dict("not a dict")
        assert result == {}, "Result must not be empty"

    def test_section_to_dict_with_list(self) -> None:
        """Test _section_to_dict with list input."""
        result = cli._section_to_dict([1, 2, 3])
        assert result == {}, "Result must not be empty"


class TestCliSimpleSyntheticData:
    """Test simple_synthetic_data function."""

    def test_simple_synthetic_data_callable(self) -> None:
        """Test that simple_synthetic_data is callable."""
        assert callable(cli.simple_synthetic_data), "Data must not be empty"

    def test_simple_synthetic_data_returns_tuple(self) -> None:
        """Test that function returns tuple."""
        with patch.object(cli, "build_registered_dataset") as mock_build:
            mock_build.return_value = ([], None)
            result = cli.simple_synthetic_data(num_samples=100)
        assert result == ([], None)
        mock_build.assert_called_once_with("synthetic_classification", num_samples=100)


class TestCliMetricFunctions:
    """Test metric functions."""

    def test_classification_accuracy_callable(self) -> None:
        """Test classification_accuracy function exists."""
        assert callable(cli.classification_accuracy), "Condition must be true"

    def test_classification_accuracy_with_numpy_arrays(self) -> None:
        """Test classification_accuracy with numpy arrays."""
        import numpy as np

        logits = np.array([[0.1, 0.9], [0.8, 0.2], [0.3, 0.7]])
        labels = np.array([1, 0, 1])
        assert cli.classification_accuracy(logits, labels) == 1.0


class TestCliResolutionFunctions:
    """Test configuration resolution functions."""

    def test_resolve_callable_valid_target(self) -> None:
        """Test _resolve_callable with valid target."""
        result = cli._resolve_callable("pathlib.Path")
        assert result is Path, "Result must not be empty"

    def test_resolve_callable_invalid_module(self) -> None:
        """Test _resolve_callable with invalid module."""
        with pytest.raises(ModuleNotFoundError):
            cli._resolve_callable("nonexistent_module.NonexistentClass")

    def test_resolve_callable_invalid_attribute(self) -> None:
        """Test _resolve_callable with invalid attribute."""
        with pytest.raises(AttributeError):
            cli._resolve_callable("pathlib.NonexistentAttribute")

    def test_resolve_callable_non_callable(self) -> None:
        """Test _resolve_callable with non-callable attribute."""
        with pytest.raises(TypeError):
            cli._resolve_callable("sys.version")  # version is a string, not callable

    def test_resolve_callable_no_module_path(self) -> None:
        """Test _resolve_callable with invalid target format."""
        with pytest.raises(ValueError):
            cli._resolve_callable("NoModulePath")


class TestCliInstantiators:
    """Test instantiator functions."""

    def test_instantiate_model_requires_target(self) -> None:
        """Test _instantiate_model requires target."""
        with pytest.raises(ValueError):
            cli._instantiate_model({"target": None})

    def test_instantiate_model_with_target(self) -> None:
        """Test _instantiate_model with valid target."""
        model_cfg = {"target": "torch.nn.Linear", "params": {"in_features": 10, "out_features": 5}}
        with patch.object(cli, "_resolve_callable") as mock_resolve:
            mock_linear = MagicMock(return_value="model")
            mock_resolve.return_value = mock_linear
            result = cli._instantiate_model(model_cfg)
            assert result == "model"
            mock_resolve.assert_called_once_with("torch.nn.Linear")
            mock_linear.assert_called_once_with(in_features=10, out_features=5)

    def test_instantiate_optimizer_requires_target(self) -> None:
        """Test _instantiate_optimizer requires target."""
        mock_model = MagicMock()
        with pytest.raises(ValueError):
            cli._instantiate_optimizer({}, mock_model)

    def test_resolve_loss_with_default(self) -> None:
        """Test _resolve_loss with default."""
        torch_module = ModuleType("torch")
        torch_module.__path__ = []
        nn_module = ModuleType("torch.nn")
        nn_module.__path__ = []
        functional_module = ModuleType("torch.nn.functional")
        cross_entropy = MagicMock(name="cross_entropy")
        functional_module.cross_entropy = cross_entropy
        with patch.dict(
            sys.modules,
            {
                "torch": torch_module,
                "torch.nn": nn_module,
                "torch.nn.functional": functional_module,
            },
        ):
            result = cli._resolve_loss(None)
        assert result is cross_entropy

    def test_resolve_loss_with_custom_target(self) -> None:
        """Test _resolve_loss with custom target."""
        loss_cfg = {"target": "torch.nn.CrossEntropyLoss"}
        with patch.object(cli, "_resolve_callable") as mock_resolve:
            mock_loss = MagicMock(name="loss")
            mock_resolve.return_value = mock_loss
            result = cli._resolve_loss(loss_cfg)
            assert result is mock_loss
            mock_resolve.assert_called_once_with("torch.nn.CrossEntropyLoss")

    def test_resolve_metric_with_none(self) -> None:
        """Test _resolve_metric with None."""
        result = cli._resolve_metric(None)
        assert result is None, "Result must not be empty"

    def test_resolve_metric_with_accuracy_name(self) -> None:
        """Test _resolve_metric with accuracy name."""
        metric_cfg = {"name": "accuracy"}
        result = cli._resolve_metric(metric_cfg)
        assert callable(result), "Result must not be empty"


class TestCliDataloaderResolution:
    """Test dataloader resolution."""

    def test_resolve_dataloaders_requires_config(self) -> None:
        """Test _resolve_dataloaders requires configuration."""
        with pytest.raises(ValueError):
            cli._resolve_dataloaders({})

    def test_resolve_dataloaders_with_target(self) -> None:
        """Test _resolve_dataloaders with target."""
        data_cfg = {"target": "torch.utils.data.DataLoader"}
        with patch.object(cli, "_resolve_callable") as mock_resolve:
            mock_loader_builder = MagicMock(return_value=([1, 2, 3], [4, 5, 6]))
            mock_resolve.return_value = mock_loader_builder
            result = cli._resolve_dataloaders(data_cfg)
        assert result == ([1, 2, 3], [4, 5, 6])
        mock_resolve.assert_called_once_with("torch.utils.data.DataLoader")
        mock_loader_builder.assert_called_once_with()

    def test_resolve_dataloaders_with_name(self) -> None:
        """Test _resolve_dataloaders with name."""
        data_cfg = {"name": "synthetic_classification"}
        with patch.object(cli, "build_registered_dataset") as mock_build:
            mock_build.return_value = ([1, 2, 3], None)
            result = cli._resolve_dataloaders(data_cfg)
        assert result == ([1, 2, 3], None)
        mock_build.assert_called_once_with("synthetic_classification")


class TestCliMainFunction:
    """Test main CLI function."""

    def test_main_requires_config_path(self) -> None:
        """Test main requires --config-path argument."""
        with pytest.raises(SystemExit) as exc_info:
            cli.main([])
        assert exc_info.value.code == 2

    def test_main_help_argument(self) -> None:
        """Test main --help shows help."""
        with pytest.raises(SystemExit) as exc_info:
            cli.main(["--help"])
        assert exc_info.value.code == 0

    def test_main_with_valid_config_path(self, temp_config_dir: Path, cli_main_mocks) -> None:
        """Test main composes the selected config, runs training, and closes the trainer."""
        assert cli.main(["--config-path", str(temp_config_dir)]) == 0
        cli_main_mocks.initialize.assert_called_once_with(
            version_base=None, config_dir=str(temp_config_dir)
        )
        cli_main_mocks.compose.assert_called_once_with(config_name="train", overrides=[])
        cli_main_mocks.to_container.assert_called_once()
        cli_main_mocks.trainer.train.assert_called_once_with()
        cli_main_mocks.trainer.close.assert_called_once_with()


class TestCliArgumentParsing:
    """Test argument parsing."""

    def test_parse_config_path_argument(self, cli_main_mocks) -> None:
        """Test --config-path reaches Hydra initialization."""
        assert cli.main(["--config-path", "/tmp/configs"]) == 0
        cli_main_mocks.initialize.assert_called_once_with(
            version_base=None, config_dir="/tmp/configs"
        )

    def test_parse_config_name_argument(self, cli_main_mocks) -> None:
        """Test --config-name reaches the config composition call."""
        assert cli.main(["--config-path", "/tmp", "--config-name", "custom_train"]) == 0
        cli_main_mocks.compose.assert_called_once_with(config_name="custom_train", overrides=[])

    def test_parse_overrides(self, cli_main_mocks) -> None:
        """Test Hydra-style overrides reach the config composition call."""
        overrides = ["trainer.epochs=5", "trainer.batch_size=64"]
        assert cli.main(["--config-path", "/tmp", *overrides]) == 0
        cli_main_mocks.compose.assert_called_once_with(config_name="train", overrides=overrides)
