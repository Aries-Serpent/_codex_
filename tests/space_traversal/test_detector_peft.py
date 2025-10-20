from __future__ import annotations

from pathlib import Path
import importlib.util
import types


def _load_module(path: Path, name: str) -> types.ModuleType:
    if not path.is_absolute():
        repo_root = Path(__file__).resolve().parents[2]
        path = repo_root / path
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    assert spec and spec.loader
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def test_detector_peft_finds_tokens(tmp_path: Path) -> None:
    content = (
        '\nfrom peft import LoraConfig, get_peft_model\n'
        'def wire(model):\n'
        '    return get_peft_model(model, LoraConfig(r=8, lora_alpha=16))\n'
    )
    (tmp_path / 'modeling.py').write_text(content, encoding='utf-8')

    detector_path = Path('scripts/space_traversal/detectors/detector_peft.py')
    module = _load_module(detector_path, 'detector_peft')
    result = module.detect(tmp_path)  # type: ignore[attr-defined]

    assert result['id'] == 'peft_hooks'
    assert result['files_with_peft'] == 1
    assert 'LoraConfig' in list(result['evidence'].values())[0]

