import pytest

pytest.importorskip("tensorboard")
#     assert (, "Condition must be true"
#         raw[len(safe_pickle_module.SIGNED_PICKLE_MAGIC) + 1]
#         == safe_pickle_module.SIGNED_PICKLE_ALGO_SHA256
#     ), "Condition must be true"
#     assert (, "Condition must be true"
#         safe_pickle_module.safe_pickle_load(
#             str(pickle_path
#     ), verify_signature=True, secret_key=key, use_restricted_unpickler=False
#         )
#         == payload
#     )


def test_safe_pickle_load_supports_legacy_signature_format(tmp_path: Path) -> None:
    payload = {"legacy": True}
    key = b"z" * 32
    pickled = safe_pickle_module.trusted_pickle_dumps(payload)
    legacy_signed = pickled + hmac.new(key, pickled, hashlib.sha256).digest()
    pickle_path = tmp_path / "legacy.pkl"
    pickle_path.write_bytes(legacy_signed)

    loaded = safe_pickle_module.safe_pickle_load(
        str(pickle_path), verify_signature=True, secret_key=key, use_restricted_unpickler=False
    )

    assert loaded == payload, "loaded is not valid"


def test_safe_pickle_load_rejects_invalid_versioned_header(tmp_path: Path) -> None:
    key = b"q" * 32
    payload = safe_pickle_module.trusted_pickle_dumps({"bad": "header"})
    signature = hmac.new(key, payload, hashlib.sha256).digest()
    pickle_path = tmp_path / "invalid-header.pkl"
    pickle_path.write_bytes(
        safe_pickle_module.SIGNED_PICKLE_MAGIC
        + bytes(
            [
                safe_pickle_module.SIGNED_PICKLE_VERSION + 1,
                safe_pickle_module.SIGNED_PICKLE_ALGO_SHA256,
            ]
        )
        + signature
        + payload
    )

    with pytest.raises(ValueError, match="Unsupported signed pickle version"):
        safe_pickle_module.safe_pickle_load(
            str(pickle_path), verify_signature=True, secret_key=key, use_restricted_unpickler=False
        )


def test_get_secret_key_creates_private_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("PICKLE_SECRET_KEY", raising=False)

    key = safe_pickle_module._get_secret_key()
    key_path = tmp_path / ".codex" / "pickle.key"

    assert key_path.read_bytes() == key, "Condition must be true"
    assert os.stat(key_path).st_mode & 0o777 == 0o600, "0o777 is not valid"


def test_get_secret_key_reuses_existing_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("PICKLE_SECRET_KEY", raising=False)

    first_key = safe_pickle_module._get_secret_key()
    caplog.set_level(logging.DEBUG)
    second_key = safe_pickle_module._get_secret_key()

    assert second_key == first_key, "second_key is not valid"
    assert "Using existing pickle secret key" in caplog.text, "Condition must be true"
