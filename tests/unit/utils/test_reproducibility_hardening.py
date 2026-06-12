import json
import os
import sys
from unittest.mock import MagicMock, patch

from src.codex_ml.utils.reproducibility_hardening import (
    ReproducibilityManager,
    create_reproducibility_manifest,
    enable_deterministic_training,
    save_env_snapshot,
)

 # pragma: allowlist secret # pragma: allowlist secret

def test_enable_deterministic_training_success():
    """Test deterministic training with all dependencies mocked successfully."""
    mock_numpy = MagicMock()
    mock_torch = MagicMock()
    mock_torch.cuda.is_available.return_value = True
    mock_torch.backends.cudnn.deterministic = False
    mock_torch.backends.cudnn.benchmark = True
    mock_tf = MagicMock()
    mock_tf.config.experimental.enable_op_determinism = MagicMock()

    with patch("random.seed"), \
         patch.dict("sys.modules", {"numpy": mock_numpy, "torch": mock_torch, "tensorflow": mock_tf}):

        status = enable_deterministic_training(42, strict=True)

        assert status["python_random"] is True
        assert status["python_hash_seed"] is True
        assert os.environ["PYTHONHASHSEED"] == "42"

        assert status["numpy"] is True
        mock_numpy.random.seed.assert_called_once_with(42)

        assert status["torch"] is True
        mock_torch.manual_seed.assert_called_once_with(42)
        assert status["torch_cuda"] is True
        mock_torch.cuda.manual_seed.assert_called_once_with(42)
        mock_torch.cuda.manual_seed_all.assert_called_once_with(42)
        assert status["cudnn_deterministic"] is True
        assert mock_torch.backends.cudnn.deterministic is True
        assert mock_torch.backends.cudnn.benchmark is False
        assert status["cublas_workspace"] is True
        assert os.environ["CUBLAS_WORKSPACE_CONFIG"] == ":4096:8"

        assert status["torch_deterministic_algorithms"] is True
        mock_torch.use_deterministic_algorithms.assert_called_once_with(True)

        assert status["tensorflow"] is True
        mock_tf.random.set_seed.assert_called_once_with(42)
        assert status["tensorflow_deterministic"] is True
        mock_tf.config.experimental.enable_op_determinism.assert_called_once()

def test_enable_deterministic_training_missing_dependencies():
    """Test when numpy, torch, tensorflow are missing."""
    with patch.dict("sys.modules", {"numpy": None, "torch": None, "tensorflow": None}):
        status = enable_deterministic_training(42)
        assert status["python_random"] is True
        assert status["numpy"] is None
        assert status["torch"] is None
        assert status["tensorflow"] is None

def test_enable_deterministic_training_exceptions():
    """Test exceptions in setting seeds."""
    class MockEnviron(dict):
        def __setitem__(self, key, value):
            raise Exception("mock env error")

    with patch("random.seed", side_effect=Exception("mock random error")), \
         patch("src.codex_ml.utils.reproducibility_hardening.os.environ", MockEnviron()):
        status = enable_deterministic_training(42)
        assert status["python_random"] is False
        assert status["python_hash_seed"] is False

    mock_numpy = MagicMock()
    mock_numpy.random.seed.side_effect = Exception("numpy error")
    mock_torch = MagicMock()
    mock_torch.manual_seed.side_effect = Exception("torch error")
    mock_tf = MagicMock()
    mock_tf.random.set_seed.side_effect = Exception("tf error")

    with patch.dict("sys.modules", {"numpy": mock_numpy, "torch": mock_torch, "tensorflow": mock_tf}):
        status = enable_deterministic_training(42)
        assert status["numpy"] is False
        assert status["torch"] is False
        assert status["tensorflow"] is False

def test_enable_deterministic_training_torch_no_cuda_and_strict_exception():
    mock_torch = MagicMock()
    mock_torch.cuda.is_available.return_value = False
    mock_torch.use_deterministic_algorithms.side_effect = Exception("strict error")
    with patch.dict("sys.modules", {"torch": mock_torch, "numpy": None, "tensorflow": None}):
        status = enable_deterministic_training(42, strict=True)
        assert status["torch"] is True
        assert status["torch_cuda"] is None
        assert status["torch_deterministic_algorithms"] is False

def test_enable_deterministic_training_tf_no_op_determinism():
    class _Experimental:
        pass

    mock_tf = MagicMock()
    mock_tf.config.experimental = _Experimental()
    with patch.dict("sys.modules", {"tensorflow": mock_tf, "numpy": None, "torch": None}):
        status = enable_deterministic_training(42)
        assert status["tensorflow"] is True
        assert status["tensorflow_deterministic"] is None

def test_save_env_snapshot(tmp_path):
    output_path = tmp_path / "env_snapshot.txt"

    mock_git_commit = "abc1234567890def"  # pragma: allowlist secret
    mock_git_dirty = " M some_file.py"
    mock_pip_freeze = "package==1.0.0\nother==2.0.0"

    def mock_check_output(args, **kwargs):
        if "rev-parse" in args:
            return mock_git_commit
        if "status" in args:
            return mock_git_dirty
        if "freeze" in args:
            return mock_pip_freeze
        return ""

    mock_torch = MagicMock()
    mock_torch.cuda.is_available.return_value = True
    mock_torch.version.cuda = "11.7"
    mock_torch.backends.cudnn.version.return_value = 8500
    mock_torch.cuda.device_count.return_value = 1
    mock_torch.cuda.get_device_name.return_value = "Mock GPU"
    mock_torch.cuda.get_device_capability.return_value = (8, 6)

    with patch("subprocess.check_output", side_effect=mock_check_output), \
         patch.dict("sys.modules", {"torch": mock_torch}):
        snapshot = save_env_snapshot(output_path, include_pip_freeze=True)

        assert snapshot["python_version"] == sys.version
        assert snapshot["python_executable"] == sys.executable
        assert snapshot["git_commit"] == "abc1234567890def"  # pragma: allowlist secret
        assert snapshot["git_dirty"] is True
        assert snapshot["pip_freeze"] == ["package==1.0.0", "other==2.0.0"]
        assert snapshot["cuda_available"] is True
        assert snapshot["cuda_version"] == "11.7"
        assert snapshot["cudnn_version"] == 8500
        assert snapshot["gpu_count"] == 1
        assert len(snapshot["gpu_devices"]) == 1

        assert output_path.exists()
        assert output_path.with_suffix(".json").exists()

        with open(output_path.with_suffix(".json")) as f:
            data = json.load(f)
            assert data["git_commit"] == "abc1234567890def"  # pragma: allowlist secret

def test_save_env_snapshot_no_git_no_gpu(tmp_path):
    output_path = tmp_path / "env_snapshot.txt"

    with patch("subprocess.check_output", side_effect=Exception("Git error")), \
         patch.dict("sys.modules", {"torch": None}):
        snapshot = save_env_snapshot(output_path, include_pip_freeze=False)

        assert snapshot["git_commit"] is None
        assert snapshot["git_dirty"] is None
        assert snapshot["pip_freeze"] is None
        assert snapshot["cuda_available"] is None

def test_save_env_snapshot_gpu_error(tmp_path):
    output_path = tmp_path / "env_snapshot.txt"

    mock_torch = MagicMock()
    mock_torch.cuda.is_available.side_effect = Exception("GPU error")

    with patch("subprocess.check_output", side_effect=Exception("Git error")), \
         patch.dict("sys.modules", {"torch": mock_torch}):
        snapshot = save_env_snapshot(output_path, include_pip_freeze=False)
        assert "cuda_available" not in snapshot

def test_save_env_snapshot_pip_error(tmp_path):
    output_path = tmp_path / "env_snapshot.txt"

    def mock_check_output(args, **kwargs):
        if "freeze" in args:
            raise Exception("pip error")
        return b""

    with patch("subprocess.check_output", side_effect=mock_check_output), \
         patch.dict("sys.modules", {"torch": None}):
        snapshot = save_env_snapshot(output_path, include_pip_freeze=True)
        assert snapshot["pip_freeze"] == []

def test_save_env_snapshot_no_cuda_available(tmp_path):
    output_path = tmp_path / "env_snapshot.txt"

    mock_torch = MagicMock()
    mock_torch.cuda.is_available.return_value = False

    with patch("subprocess.check_output", side_effect=Exception("Git error")), \
         patch.dict("sys.modules", {"torch": mock_torch}):
        snapshot = save_env_snapshot(output_path, include_pip_freeze=False)
        assert snapshot["cuda_available"] is False
        assert snapshot["cuda_version"] is None
        assert snapshot["gpu_count"] == 0
        assert snapshot["gpu_devices"] == []

def test_create_reproducibility_manifest_no_config_no_hash(tmp_path):
    with patch("src.codex_ml.utils.reproducibility_hardening.enable_deterministic_training") as mock_enable, \
         patch("src.codex_ml.utils.reproducibility_hardening.save_env_snapshot") as mock_save:

        mock_enable.return_value = {"python_random": True}
        mock_save.return_value = {
            "python_version": "3.10.0",
            "git_commit": "abc",
            "git_dirty": False,
            "cuda_available": False,
            "platform": {"system": "Linux"}
        }

        manifest = create_reproducibility_manifest(
            seed=123,
            output_dir=tmp_path,
        )

        assert manifest["seed"] == 123
        assert "config" not in manifest
        assert "dataset_hash" not in manifest

def test_create_reproducibility_manifest(tmp_path):
    with patch("src.codex_ml.utils.reproducibility_hardening.enable_deterministic_training") as mock_enable, \
         patch("src.codex_ml.utils.reproducibility_hardening.save_env_snapshot") as mock_save:

        mock_enable.return_value = {"python_random": True}
        mock_save.return_value = {
            "python_version": "3.10.0",
            "git_commit": "abc",
            "git_dirty": False,
            "cuda_available": False,
            "platform": {"system": "Linux"}
        }

        manifest = create_reproducibility_manifest(
            seed=123,
            output_dir=tmp_path,
            config={"batch_size": 32},
            dataset_hash="hash456"
        )

        assert manifest["seed"] == 123
        assert manifest["seeding_status"] == {"python_random": True}
        assert manifest["config"] == {"batch_size": 32}
        assert manifest["dataset_hash"] == "hash456"
        assert "manifest_hash" in manifest

        manifest_path = tmp_path / "reproducibility_manifest.json"
        assert manifest_path.exists()

def test_reproducibility_manager(tmp_path):
    with patch("src.codex_ml.utils.reproducibility_hardening.enable_deterministic_training") as mock_enable, \
         patch("src.codex_ml.utils.reproducibility_hardening.save_env_snapshot") as mock_save:

        mock_enable.return_value = {"status": "ok"}
        mock_save.return_value = {"env": "snapshot"}

        manager = ReproducibilityManager(seed=777, output_dir=tmp_path)

        # Test setup
        setup_status = manager.setup(strict=True)
        assert setup_status == {"status": "ok"}
        mock_enable.assert_called_once_with(seed=777, strict=True)

        # Test capture environment
        env = manager.capture_environment()
        assert env == {"env": "snapshot"}
        mock_save.assert_called_once_with(tmp_path / "env_snapshot.txt")

        # Test finalize
        with patch("src.codex_ml.utils.reproducibility_hardening.create_reproducibility_manifest") as mock_create:
            mock_create.return_value = {"manifest": "data"}

            manifest = manager.finalize(config={"lr": 0.01}, dataset_hash="dataset1")

            assert manifest == {"manifest": "data"}
            assert manager.get_manifest() == {"manifest": "data"}
            mock_create.assert_called_once_with(
                seed=777,
                output_dir=tmp_path,
                config={"lr": 0.01},
                dataset_hash="dataset1"
            )
