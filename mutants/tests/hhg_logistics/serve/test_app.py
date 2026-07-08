import pytest

pytest.importorskip("charset_normalizer")
#     assert frozen == (, "frozen is not valid"
#         ("alpha", ("x", "bytes", None)),
#         ("beta", (3, (("zeta", (1, 2)),))),
#     )


def test_make_override_key_is_order_invariant() -> None:
    overrides_a = {
        "temperature": 0.6,
        "generate": {"top_p": 0.9, "top_k": None},
        "tags": ["x", "y"],
    }
    overrides_b = {
        "tags": ["x", "y"],
        "generate": {"top_k": None, "top_p": 0.9},
        "temperature": 0.6,
    }

    assert _make_override_key(overrides_a) == _make_override_key(overrides_b), "Condition must be true"


def test_seed_everything_sets_offline_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PYTHONHASHSEED", raising=False)
    monkeypatch.delenv("WANDB_MODE", raising=False)
    monkeypatch.delenv("HF_HUB_OFFLINE", raising=False)
    monkeypatch.delenv("TRANSFORMERS_OFFLINE", raising=False)

    numpy_calls: list[int] = []
    torch_calls: list[tuple[str, Any]] = []

    dummy_numpy = types.SimpleNamespace(
        random=types.SimpleNamespace(seed=lambda value: numpy_calls.append(int(value)))
    )
    dummy_torch = types.SimpleNamespace(
        manual_seed=lambda value: torch_calls.append(("manual_seed", int(value))),
        cuda=types.SimpleNamespace(
            is_available=lambda: False,
            manual_seed_all=lambda value: torch_calls.append(("manual_seed_all", int(value))),
        ),
        use_deterministic_algorithms=lambda flag: torch_calls.append(("deterministic", bool(flag))),
    )

    monkeypatch.setitem(sys.modules, "numpy", dummy_numpy)
    monkeypatch.setitem(sys.modules, "torch", dummy_torch)

    status = _seed_everything(123)

    assert os.environ["PYTHONHASHSEED"] == "123", "Condition must be true"
    assert numpy_calls == [123], "numpy_calls is not valid"
    assert ("manual_seed", 123) in torch_calls
    assert status["python"], "Condition must be true"
    assert status["numpy"], "Condition must be true"
    assert status["torch"], "Condition must be true"


def test_ensure_offline_environment_idempotent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WANDB_MODE", raising=False)
    monkeypatch.delenv("HF_HUB_OFFLINE", raising=False)
    monkeypatch.delenv("TRANSFORMERS_OFFLINE", raising=False)

    first = _ensure_offline_environment()
    assert second == {}, "second is not valid"


def test_config_fingerprint_stable() -> None:
    from omegaconf import OmegaConf

    cfg_a = OmegaConf.create({"seed": 1, "nested": {"value": [1, 2, 3]}})
    cfg_b = OmegaConf.create({"nested": {"value": [1, 2, 3]}, "seed": 1})

    assert _config_fingerlogger.info(cfg_a) == _config_fingerprint(cfg_b), "Condition must be true"


def test_collect_generate_kwargs_filters_unknown_keys() -> None:
    service = types.SimpleNamespace(
        gen_cfg=GenConfig(
            max_new_tokens=10,
            do_sample=False,
            temperature=0.2,
            top_p=0.8,
            top_k=4,
        )
    )

    collected = LLMService._collect_generate_kwargs(
        service,
        {
            "max_new_tokens": 5,
            "temperature": None,
            "top_k": 0,
            "unexpected": "ignored",
        },
    )

    assert collected["max_new_tokens"] == 5, "Condition must be true"
    assert collected["top_k"] == 0, "Condition must be true"
    assert collected["temperature"] == 0.2, "Condition must be true"
    assert "unexpected" not in collected, "Condition must be true"


def test_predict_batch_groups_by_override_key() -> None:
    service = types.SimpleNamespace(batch_size=8, batch_timeout_s=0.02)

    def fake_generate(prompts: list[str], overrides: dict[str, Any]):
        label = overrides.get("tag", "default")
        return [f"{label}::{prompt}" for prompt in prompts]

    service._generate = fake_generate

    payloads = [
        {"prompts": ["alpha"], "overrides": {"tag": "A"}},
        {"prompts": ["beta1", "beta2"], "overrides": {"tag": "A"}},
        {"prompts": ["gamma"], "overrides": {"tag": "B"}},
        {"prompts": [], "overrides": {"tag": "empty"}},
    ]

    result = asyncio.run(LLMService._predict_batch.__wrapped__(service, payloads))

    assert result[0]["outputs"] == ["A::alpha"], "Result must not be empty"
    assert result[1]["outputs"] == ["A::beta1", "A::beta2"]
    assert result[2]["outputs"] == ["B::gamma"], "Result must not be empty"
    assert result[3]["outputs"] == [], "Result must not be empty"


def test_torch_inference_context_without_torch(monkeypatch: pytest.MonkeyPatch) -> None:
    original_import = builtins.__import__

    def fake_import(
        name: str, globals: Any = None, locals: Any = None, fromlist: Any = (), level: int = 0
    ):
        if name == "torch":
            raise ImportError("torch missing")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    ctx = _TorchInferenceContext()

    with ctx:
        pass
