"""
Comprehensive test suite for PEFT hooks detector.

Tests cover PEFT/LoRA detection, hook patterns, adapter integration,
and edge cases following the High Maturity Achievement Plan.
"""
import importlib.util
import types
from pathlib import Path
from typing import Any, Dict, Iterable

import pytest


def _load_module(path: Path, name: str) -> types.ModuleType:
    """Load detector module dynamically."""
    if not path.is_absolute():
        repo_root = Path(__file__).resolve().parents[2]
        path = repo_root / path
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def _context_index_for(paths: Iterable[Path]) -> Dict[str, Any]:
    """Create context index from file paths using absolute paths."""
    return {
        "files": [
            {"path": str(path.resolve())}
            for path in paths
        ],
    }


class TestPEFTDetection:
    """Test PEFT/LoRA token detection."""
    
    def test_lora_config_detection(self, tmp_path: Path):
        """Test detection of LoRA configuration."""
        test_file = tmp_path / "model.py"
        test_file.write_text("""
from peft import LoraConfig, get_peft_model

config = LoraConfig(r=8, lora_alpha=32)
model = get_peft_model(base_model, config)
""", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_peft.py")
        module = _load_module(detector_path, "detector_peft")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)
        
        assert result["id"] == "peft_hooks"
        assert "peft" in result["found_patterns"]
        assert "lora" in result["found_patterns"]
        assert "LoraConfig" in result["found_patterns"]
        assert result["files_with_peft"] == 1
    
    def test_adapter_detection(self, tmp_path: Path):
        """Test detection of adapter patterns."""
        test_file = tmp_path / "adapter.py"
        test_file.write_text("""
from peft import PeftModel, inject_adapter

model = PeftModel.from_pretrained(base, adapter_path)
inject_adapter(model, adapter_config)
""", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_peft.py")
        module = _load_module(detector_path, "detector_peft")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)
        
        assert "adapter" in result["found_patterns"]
        assert "PeftModel" in result["found_patterns"]
    
    def test_kbit_training_detection(self, tmp_path: Path):
        """Test detection of quantization-aware training."""
        test_file = tmp_path / "quantized.py"
        test_file.write_text("""
from peft import prepare_model_for_kbit_training

model = prepare_model_for_kbit_training(model)
""", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_peft.py")
        module = _load_module(detector_path, "detector_peft")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)
        
        assert "prepare_model_for_kbit_training" in result["found_patterns"]
    
    def test_multiple_peft_tokens(self, tmp_path: Path):
        """Test file with multiple PEFT tokens."""
        test_file = tmp_path / "comprehensive.py"
        test_file.write_text("""
from peft import LoraConfig, PeftModel, get_peft_model, LoraLayer

config = LoraConfig(r=16, lora_alpha=32)
peft_model = get_peft_model(base_model, config)
""", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_peft.py")
        module = _load_module(detector_path, "detector_peft")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)
        
        assert len(result["found_patterns"]) >= 4
        assert result["total_peft_tokens"] >= 4


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_no_peft_code(self, tmp_path: Path):
        """Test file without PEFT code."""
        test_file = tmp_path / "plain.py"
        test_file.write_text("x = 1 + 2\nprint(x)\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_peft.py")
        module = _load_module(detector_path, "detector_peft")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)
        
        assert result["files_with_peft"] == 0
        assert len(result["evidence_files"]) == 0
    
    def test_empty_file_list(self):
        """Test with no files."""
        detector_path = Path("scripts/space_traversal/detectors/detector_peft.py")
        module = _load_module(detector_path, "detector_peft")
        context_index = {"files": []}
        result = module.detect(context_index)
        
        assert result["files_with_peft"] == 0
    
    def test_non_python_files_ignored(self, tmp_path: Path):
        """Test that non-Python files are ignored."""
        test_file = tmp_path / "data.txt"
        test_file.write_text("peft lora LoraConfig\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_peft.py")
        module = _load_module(detector_path, "detector_peft")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)
        
        assert result["files_with_peft"] == 0


class TestMetricsCalculation:
    """Test metrics calculation."""
    
    def test_metrics_present(self, tmp_path: Path):
        """Test that metrics are calculated."""
        test_file = tmp_path / "model.py"
        test_file.write_text("from peft import lora, adapter\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_peft.py")
        module = _load_module(detector_path, "detector_peft")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)
        
        assert "metrics" in result
        assert "files_with_peft" in result["metrics"]
        assert "unique_tokens_found" in result["metrics"]
        assert "total_token_occurrences" in result["metrics"]
    
    def test_multiple_files_aggregation(self, tmp_path: Path):
        """Test aggregation across multiple files."""
        files = []
        for i in range(3):
            f = tmp_path / f"model{i}.py"
            f.write_text(f"from peft import lora\nconfig = LoraConfig()\n", encoding="utf-8")
            files.append(f)
        
        detector_path = Path("scripts/space_traversal/detectors/detector_peft.py")
        module = _load_module(detector_path, "detector_peft")
        context_index = _context_index_for(files)
        result = module.detect(context_index)
        
        assert result["files_with_peft"] == 3
        assert result["metrics"]["files_with_peft"] == 3


class TestDetectorContract:
    """Test detector contract compliance."""
    
    def test_required_fields(self, tmp_path: Path):
        """Test all required detector fields are present."""
        test_file = tmp_path / "test.py"
        test_file.write_text("from peft import lora\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_peft.py")
        module = _load_module(detector_path, "detector_peft")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)
        
        assert "id" in result
        assert result["id"] == "peft_hooks"
        assert "evidence_files" in result
        assert "found_patterns" in result
        assert "required_patterns" in result
        assert "docs_keywords" in result
        assert "meta" in result
    
    def test_metadata_correctness(self, tmp_path: Path):
        """Test metadata fields."""
        test_file = tmp_path / "test.py"
        test_file.write_text("from peft import lora\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_peft.py")
        module = _load_module(detector_path, "detector_peft")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)
        
        assert result["meta"]["deterministic"] is True
        assert result["meta"]["offline"] is True
        assert result["meta"]["bounded"] is True
    
    def test_docs_keywords_present(self, tmp_path: Path):
        """Test documentation keywords."""
        test_file = tmp_path / "test.py"
        test_file.write_text("from peft import lora\n", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_peft.py")
        module = _load_module(detector_path, "detector_peft")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)
        
        expected = ["peft", "lora", "adapter", "fine-tuning", "efficient"]
        for keyword in expected:
            assert keyword in result["docs_keywords"]


class TestIntegration:
    """Test integration scenarios."""
    
    def test_realistic_peft_file(self, tmp_path: Path):
        """Test detection in realistic PEFT implementation."""
        test_file = tmp_path / "train_lora.py"
        test_file.write_text("""
import torch
from transformers import AutoModelForCausalLM
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# Load base model
model = AutoModelForCausalLM.from_pretrained("model_name")

# Prepare for quantized training
model = prepare_model_for_kbit_training(model)

# Configure LoRA
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
)

# Apply PEFT
peft_model = get_peft_model(model, lora_config)
peft_model.print_trainable_parameters()

# Training loop
for batch in dataloader:
    loss = peft_model(**batch).loss
    loss.backward()
""", encoding="utf-8")
        
        detector_path = Path("scripts/space_traversal/detectors/detector_peft.py")
        module = _load_module(detector_path, "detector_peft")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)
        
        assert result["files_with_peft"] == 1
        assert "peft" in result["found_patterns"]
        assert "lora" in result["found_patterns"]
        assert "LoraConfig" in result["found_patterns"]
        assert result["total_peft_tokens"] >= 4
