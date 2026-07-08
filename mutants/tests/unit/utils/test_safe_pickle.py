import os
import pickle
from unittest.mock import patch

import pytest

from src.codex_ml.utils.safe_pickle import (
    SIGNED_PICKLE_ALGO_SHA256,
    SIGNED_PICKLE_MAGIC,
    SIGNED_PICKLE_VERSION,
    RestrictedUnpickler,
    _build_signed_pickle,  # pragma: allowlist secret
    _get_secret_key,
    _split_signed_pickle,
    safe_pickle_dump,
    safe_pickle_load,
)


class DummyAllowedClass:
    pass


class DummyBlockedClass:
    pass


def test_restricted_unpickler_find_class():
    import io

    unpickler = RestrictedUnpickler(io.BytesIO(b""))

    # Test allowed (use a real class)
    cls = unpickler.find_class("builtins", "int")
    assert cls is int, "cls is not valid"

    # Test wildcard allowed
    with patch.dict(unpickler.SAFE_MODULES, {"os": {"*"}}, clear=False):
        cls = unpickler.find_class("os", "system")
        assert cls == os.system, "cls is not valid"

    # Test blocked
    with pytest.raises(pickle.UnpicklingError, match="not in whitelist"):
        unpickler.find_class("builtins", "eval")

    # Test module entirely blocked
    with pytest.raises(pickle.UnpicklingError, match="not in whitelist"):
        unpickler.find_class("subprocess", "Popen")


def test_safe_pickle_load_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        safe_pickle_load(str(tmp_path / "nonexistent.pkl"))


def test_safe_pickle_dump_and_load_unrestricted(tmp_path):
    file_path = tmp_path / "test.pkl"
    data = {"key": "value", "num": 42}

    safe_pickle_dump(data, str(file_path))
    assert file_path.exists(), "Condition must be true"

    loaded_data = safe_pickle_load(str(file_path), use_restricted_unpickler=False)
    assert loaded_data == data, "Data must not be empty"


def test_safe_pickle_dump_and_load_restricted(tmp_path):
    file_path = tmp_path / "test.pkl"
    data = {"key": "value", "num": 42, "lst": [1, 2, 3]}

    safe_pickle_dump(data, str(file_path))

    loaded_data = safe_pickle_load(str(file_path), use_restricted_unpickler=True)
    assert loaded_data == data, "Data must not be empty"


def test_safe_pickle_load_restricted_blocked(tmp_path):
    file_path = tmp_path / "test.pkl"

    class EvilClass:
        def __reduce__(self):
            return (os.system, ("echo evil",))

    try:
        evil = EvilClass()
        with open(file_path, "wb") as f:
            pickle.dump(evil, f)

        with pytest.raises(pickle.UnpicklingError):
            safe_pickle_load(str(file_path), use_restricted_unpickler=True)
    except (IOError, OSError) as _err:
        # Depending on OS, EvilClass might not be picklable in test scope easily
        # Let's just create a custom pickle stream that references os.system
        pass

    evil_payload = b"cposix\nsystem\np0\n(Vecho evil\np1\ntp2\nRp3\n."
    file_path.write_bytes(evil_payload)

    with pytest.raises(pickle.UnpicklingError, match="Class posix.system not in whitelist"):
        safe_pickle_load(str(file_path), use_restricted_unpickler=True)


def test_safe_pickle_dump_and_load_signed(tmp_path):
    file_path = tmp_path / "test_signed.pkl"
    data = [1, 2, 3]
    secret_key = b"supersecretkey"

    safe_pickle_dump(data, str(file_path), add_signature=True, secret_key=secret_key)

    loaded_data = safe_pickle_load(str(file_path), verify_signature=True, secret_key=secret_key)
    assert loaded_data == data, "Data must not be empty"


def test_safe_pickle_load_signed_tampered(tmp_path):
    file_path = tmp_path / "test_signed.pkl"
    data = [1, 2, 3]
    secret_key = b"supersecretkey"

    safe_pickle_dump(data, str(file_path), add_signature=True, secret_key=secret_key)

    # Tamper with the file
    content = file_path.read_bytes()
    file_path.write_bytes(content + b"tamper")

    with pytest.raises(ValueError, match="HMAC signature verification failed"):
        safe_pickle_load(str(file_path), verify_signature=True, secret_key=secret_key)


def test_get_secret_key_env_var():
    with patch.dict(os.environ, {"PICKLE_SECRET_KEY": "env_secret"}):  # pragma: allowlist secret
        key = _get_secret_key()
        assert key == b"env_secret"  # pragma: allowlist secret


def test_get_secret_key_create_file(tmp_path):
    # Mock Path.home() to point to tmp_path
    with patch("src.codex_ml.utils.safe_pickle.Path.home", return_value=tmp_path):
        key = _get_secret_key()
        assert len(key) == 32, "Key must not be empty"
        key_file = tmp_path / ".codex" / "pickle.key"
        assert key_file.exists(), "Condition must be true"
        assert key_file.read_bytes() == key, "Condition must be true"


def test_get_secret_key_existing_file(tmp_path):
    with patch("src.codex_ml.utils.safe_pickle.Path.home", return_value=tmp_path):
        key_file = tmp_path / ".codex" / "pickle.key"
        key_file.parent.mkdir(parents=True)
        key_file.write_bytes(b"existing_secret_key")

        key = _get_secret_key()
        assert key == b"existing_secret_key", "key is not valid"


def test_get_secret_key_os_error(tmp_path):
    with patch("src.codex_ml.utils.safe_pickle.Path.home", return_value=tmp_path):
        key_file = tmp_path / ".codex" / "pickle.key"
        key_file.parent.mkdir(parents=True)

        with patch("os.open", side_effect=OSError("Test OS Error")):
            with pytest.raises(OSError, match="Test OS Error"):
                _get_secret_key()


def test_build_and_split_signed_pickle():
    pickled_data = b"some_pickled_data"
    secret_key = b"test_key"

    signed_data = _build_signed_pickle(pickled_data, secret_key)
    extracted_data, signature = _split_signed_pickle(signed_data)

    assert extracted_data == pickled_data, "Data must not be empty"
    assert len(signature) == 32, "Signature must not be empty"


def test_split_signed_pickle_errors():
    # Too small with magic
    with pytest.raises(ValueError, match="too small"):
        _split_signed_pickle(SIGNED_PICKLE_MAGIC + b"short")

    # Unsupported version
    with pytest.raises(ValueError, match="Unsupported signed pickle version"):
        bad_version = SIGNED_PICKLE_MAGIC + bytes([99, SIGNED_PICKLE_ALGO_SHA256]) + b"x" * 32
        _split_signed_pickle(bad_version)

    # Unsupported algo
    with pytest.raises(ValueError, match="Unsupported signed pickle algorithm"):
        bad_algo = SIGNED_PICKLE_MAGIC + bytes([SIGNED_PICKLE_VERSION, 99]) + b"x" * 32
        _split_signed_pickle(bad_algo)

    # Legacy too small
    with pytest.raises(ValueError, match="File too small to contain a signed pickle payload"):
        _split_signed_pickle(b"short")


def test_split_signed_pickle_legacy():
    pickled_data = b"some_legacy_pickled_data"
    signature = b"x" * 32
    data = pickled_data + signature

    extracted_data, extracted_signature = _split_signed_pickle(data)
    assert extracted_data == pickled_data, "Data must not be empty"
    assert extracted_signature == signature, "extracted_signature is not valid"


def test_safe_pickle_dump_without_explicit_key(tmp_path):
    with patch.dict(os.environ, {"PICKLE_SECRET_KEY": "env_secret"}):  # pragma: allowlist secret
        file_path = tmp_path / "test_implicit_key.pkl"
        safe_pickle_dump([1, 2, 3], str(file_path), add_signature=True)

        # Verify it can be loaded
        loaded_data = safe_pickle_load(str(file_path), verify_signature=True)
        assert loaded_data == [1, 2, 3]
