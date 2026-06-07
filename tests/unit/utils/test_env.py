from src.codex_ml.utils.env import EnvironmentFingerprint, environment_summary


def test_environment_fingerprint():
    fp = EnvironmentFingerprint.capture()
    assert isinstance(fp, EnvironmentFingerprint)
    assert fp.python_version is not None
    assert fp.os_platform is not None
    assert isinstance(fp.to_dict(), dict)
    assert len(fp.digest()) == 16
    fp.log()


def test_environment_summary():
    summary = environment_summary()
    assert isinstance(summary, dict)
    assert "os" in summary
