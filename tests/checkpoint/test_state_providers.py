from dataclasses import dataclass

from codex_ml.utils.checkpointing import (
    GradScalerStateDictProvider,
    ModuleStateDictProvider,
    OptimizerStateDictProvider,
    SchedulerStateDictProvider,
)


@dataclass
class DummyModule:
    weight: int = 1

    def state_dict(self):
        return {"weight": self.weight}

    def load_state_dict(self, state_dict, strict=True):
        self.weight = state_dict["weight"]


def test_module_state_provider_roundtrip():
    module = DummyModule(weight=5)
    provider = ModuleStateDictProvider(module)
    state = provider.state_dict()
    module.weight = 0
    provider.load_state_dict(state)
    assert module.weight == 5


class DummyOptimizer:
    def __init__(self):
        self.state = {"lr": 0.1}

    def state_dict(self):
        return dict(self.state)

    def load_state_dict(self, state_dict):
        self.state = dict(state_dict)


def test_optimizer_state_provider_roundtrip():
    opt = DummyOptimizer()
    provider = OptimizerStateDictProvider(opt)
    state = provider.state_dict()
    opt.state["lr"] = 0.01
    provider.load_state_dict(state)
    assert opt.state["lr"] == 0.1


class DummyScheduler:
    def __init__(self):
        self.state = {"step": 3}

    def state_dict(self):
        return dict(self.state)

    def load_state_dict(self, state_dict):
        self.state = dict(state_dict)


def test_scheduler_state_provider_roundtrip():
    sched = DummyScheduler()
    provider = SchedulerStateDictProvider(sched)
    state = provider.state_dict()
    sched.state["step"] = 10
    provider.load_state_dict(state)
    assert sched.state["step"] == 3


class DummyScaler:
    def __init__(self):
        self.state = {"scale": 1.0}

    def state_dict(self):
        return dict(self.state)

    def load_state_dict(self, state_dict):
        self.state = dict(state_dict)


def test_grad_scaler_state_provider_roundtrip():
    scaler = DummyScaler()
    provider = GradScalerStateDictProvider(scaler)
    state = provider.state_dict()
    scaler.state["scale"] = 2.0
    provider.load_state_dict(state)
    assert scaler.state["scale"] == 1.0
