from __future__ import annotations

import importlib.util
import sys
import tempfile
import types
from dataclasses import dataclass
from pathlib import Path


def _load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader, "spec is not valid"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ooda_orchestrator_execute_and_metrics(monkeypatch):
    @dataclass
    class ActionResult:
        success: bool
        output: dict | None = None
        metrics: dict | None = None
        errors: list[str] | None = None

    class Planner:
        pass

    class MemoryInterface:
        pass

    class PhysicsOfThought:
        def __init__(self, *_args, **_kwargs):
            self.last_input = None

        def reason(self, data):
            self.last_input = data
            return ActionResult(
                success=True, output={"ok": True}, metrics={"latency": 1.2}, errors=[]
            )

    base_mod = types.ModuleType("cognitive_brain.base")
    base_mod.ActionResult = ActionResult
    base_mod.MemoryInterface = MemoryInterface
    base_mod.PhysicsOfThought = PhysicsOfThought
    base_mod.Planner = Planner
    monkeypatch.setitem(sys.modules, "cognitive_brain.base", base_mod)

    module = _load_module(
        "cognitive_app_orchestrator_under_test",
        Path(os.path.join(tempfile.gettempdir(), "workspace/Aries-Serpent/_codex_/cognitive_app/src/orchestrator.py")),
    )

    stores: list[tuple[str, dict, dict]] = []

    class MemoryImpl:
        def store(self, key, payload, metadata=None):
            stores.append((key, payload, metadata or {}))

    orchestrator = module.OODAOrchestrator(Planner(), MemoryImpl())
    result = orchestrator.execute({"prompt": "test"}, {"session": "s1"})
    assert result.success is True, "Result must not be empty"
    assert stores and stores[0][2] == {"type": "execution_record"}, "stores is not valid"
    metrics = orchestrator.get_execution_metrics()
    assert metrics["total_executions"] == 1, "Condition must be true"
    assert metrics["success_rate"] == 1.0, "Condition must be true"


def test_ooda_orchestrator_failure_path(monkeypatch):
    @dataclass
    class ActionResult:
        success: bool
        output: dict | None = None
        metrics: dict | None = None
        errors: list[str] | None = None

    class Planner:
        pass

    class MemoryInterface:
        pass

    class PhysicsOfThought:
        def __init__(self, *_args, **_kwargs):
            pass

        def reason(self, _data):
            raise RuntimeError("boom")

    base_mod = types.ModuleType("cognitive_brain.base")
    base_mod.ActionResult = ActionResult
    base_mod.MemoryInterface = MemoryInterface
    base_mod.PhysicsOfThought = PhysicsOfThought
    base_mod.Planner = Planner
    monkeypatch.setitem(sys.modules, "cognitive_brain.base", base_mod)

    module = _load_module(
        "cognitive_app_orchestrator_failure_under_test",
        Path(os.path.join(tempfile.gettempdir(), "workspace/Aries-Serpent/_codex_/cognitive_app/src/orchestrator.py")),
    )

    class MemoryImpl:
        def store(self, *_args, **_kwargs):
            return None

    result = module.OODAOrchestrator(Planner(), MemoryImpl()).execute({"prompt": "x"})
    assert result.success is False, "Result must not be empty"
    assert result.errors and "boom" in result.errors[0], "Result must not be empty"


def test_meta_learning_shared_memory_and_pattern_library(tmp_path):
    module = _load_module(
        "meta_learning_engine_under_test",
        Path(os.path.join(tempfile.gettempdir(), "workspace/Aries-Serpent/_codex_/scripts/cognitive/meta_learning_engine.py")),
    )

    shared = module.SharedMemory(tmp_path / "shared")
    data_id = shared.store(
        {"key": "value"}, {"source_agent": 1, "target_agent": 2, "pattern_type": "code"}
    )
    assert shared.retrieve(data_id) == {"key": "value"}, "Data must not be empty"
    assert shared.search({"source_agent": 1}) == [data_id], "Data must not be empty"

    library = module.PatternLibrary(tmp_path / "patterns")
    p1 = module.Pattern(
        pattern_id="p1",
        pattern_type="code",
        source_agent=1,
        context={"lang": "python", "scope": "tests"},
        effectiveness=0.9,
    )
    p2 = module.Pattern(
        pattern_id="p2",
        pattern_type="code",
        source_agent=2,
        context={"lang": "python"},
        effectiveness=0.8,
    )
    library.add_pattern(p1)
    library.add_pattern(p2)
    similar = library.find_similar_patterns(p1, threshold=0.5)
    assert any(p.pattern_id == "p2" for p in similar), "pattern_id is not valid"
    library.update_pattern_usage("p1")
    assert library.get_pattern("p1").usage_count == 1, "Count must be greater than zero"
