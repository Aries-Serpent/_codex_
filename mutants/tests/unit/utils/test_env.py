from src.codex_ml.utils.env import EnvironmentFingerprint, environment_summary


def test_environment_fingerprint():
    fp = EnvironmentFingerprint.capture()
    assert isinstance(fp, EnvironmentFingerprint)
    assert fp.python_version is not None, "python_version must be initialized"
    assert fp.os_platform is not None, "os_platform must be initialized"
    assert isinstance(fp.to_dict(), dict)
    assert len(fp.digest()) == 16, "Collection must not be empty"
    fp.log()


def test_environment_summary():
    summary = environment_summary()
    assert isinstance(summary, dict)
    assert "os" in summary, "Condition must be true"
