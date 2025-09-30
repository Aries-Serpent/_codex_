def test_apply_lora_if_available_identity_without_peft():
    from codex_ml.models.utils.peft import apply_lora_if_available

    class Dummy:
        pass

    model = Dummy()
    wrapped = apply_lora_if_available(model)
    # If `peft` is not installed, helper returns the model unchanged.
    assert wrapped is model

