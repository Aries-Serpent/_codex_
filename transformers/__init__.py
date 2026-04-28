"""Lightweight stub for optional dependency ``transformers``.

This module allows the offline test matrix to run without installing the
heavyweight Hugging Face stack.  When the real library is available it is
imported transparently; otherwise minimal stand-ins are provided so that
``pytest.importorskip("transformers")`` passes while still surfacing clear
errors if any functionality is exercised.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def _load_real_module() -> ModuleType | None:
    current_path = Path(__file__).resolve()
    current_dir = current_path.parent
    excluded_paths = {current_dir, current_dir.parent}
    search_paths = []
    for p in sys.path:
        try:
            resolved = Path(p).resolve()
        except (OSError, RuntimeError, TypeError, ValueError):
            continue
        if resolved not in excluded_paths:
            search_paths.append(p)
    spec = importlib.machinery.PathFinder().find_spec("transformers", search_paths)
    if spec is None or spec.loader is None:
        return None
    origin = getattr(spec, "origin", None)
    if origin and Path(origin).resolve() == current_path:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[__name__] = module
    spec.loader.exec_module(module)
    return module


class _Stub:
    def __init__(self, target: str) -> None:
        self._target = target

    def __call__(self, *args, **kwargs):  # pragma: no cover - defensive
        raise ImportError(
            f"Optional dependency '{self._target}' is not installed; "
            "install transformers to enable this functionality."
        )

    def __getattr__(self, name: str):  # pragma: no cover - defensive
        raise ImportError(
            f"Optional dependency '{self._target}' is not installed; "
            "install transformers to enable this functionality."
        )


_real = _load_real_module()

if _real is not None:
    globals().update({k: getattr(_real, k) for k in dir(_real) if not k.startswith("__")})
    __all__ = [k for k in dir(_real) if not k.startswith("__")]
else:  # pragma: no cover - exercised in minimal test envs
    # Use proper stub classes (not _Stub instances) so type annotations remain valid.

    _ERR = "transformers is not installed"

    class PreTrainedModel:
        def __init__(self, *args, **kwargs):
            raise ImportError(_ERR)

        def forward(self, *args, **kwargs):
            raise ImportError(_ERR)

        def generate(self, *args, **kwargs):
            raise ImportError(_ERR)

        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            raise ImportError(_ERR)

        @classmethod
        def from_config(cls, *args, **kwargs):
            raise ImportError(_ERR)

    class PreTrainedTokenizerBase:
        pad_token: str = ""
        eos_token: str = ""
        unk_token: str = ""
        bos_token: str = ""
        pad_token_id: int = 0
        eos_token_id: int = 0
        bos_token_id: int = 0
        pad_token_type_id: int = 0
        model_max_length: int = 512
        vocab_size: int = 0
        name_or_path: str = ""

        def __init__(self, *args, **kwargs):
            raise ImportError(_ERR)

        def __call__(self, *args, **kwargs):
            raise ImportError(_ERR)

        def encode(self, *args, **kwargs):
            raise ImportError(_ERR)

        def decode(self, *args, **kwargs):
            raise ImportError(_ERR)

        def batch_decode(self, *args, **kwargs):
            raise ImportError(_ERR)

        def add_special_tokens(self, *args, **kwargs):
            raise ImportError(_ERR)

        def convert_tokens_to_ids(self, *args, **kwargs):
            raise ImportError(_ERR)

        def save_pretrained(self, *args, **kwargs):
            raise ImportError(_ERR)

        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            raise ImportError(_ERR)

    class PreTrainedTokenizerFast(PreTrainedTokenizerBase):
        pass

    class GPT2Config:
        def __init__(self, *args, **kwargs):
            raise ImportError(_ERR)

    class AutoModel:
        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            raise ImportError(_ERR)

        @classmethod
        def from_config(cls, *args, **kwargs):
            raise ImportError(_ERR)

    class AutoConfig:
        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            raise ImportError(_ERR)

        @classmethod
        def for_model(cls, *args, **kwargs):
            raise ImportError(_ERR)

        def to_dict(self, *args, **kwargs):
            raise ImportError(_ERR)

        def save_pretrained(self, *args, **kwargs):
            raise ImportError(_ERR)

    class AutoModelForCausalLM(AutoModel):
        def generate(self, *args, **kwargs):
            raise ImportError(_ERR)

    class AutoModelForMaskedLM(AutoModel):
        pass

    class AutoModelForSequenceClassification(AutoModel):
        pass

    class AutoModelForSeq2SeqLM(AutoModel):
        pass

    class BertModel(PreTrainedModel):
        pass

    class GPT2LMHeadModel(PreTrainedModel):
        pass

    class T5ForConditionalGeneration(PreTrainedModel):
        pass

    class RobertaModel(PreTrainedModel):
        pass

    class DistilBertModel(PreTrainedModel):
        pass

    class AutoTokenizer:
        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            raise ImportError(_ERR)

    class BitsAndBytesConfig:
        def __init__(self, *args, **kwargs):
            raise ImportError(_ERR)

    class DataCollatorForLanguageModeling:
        def __init__(self, *args, **kwargs):
            raise ImportError(_ERR)

    class EarlyStoppingCallback:
        def __init__(self, *args, **kwargs):
            raise ImportError(_ERR)

    class TrainerCallback:
        pass

    class TrainingArguments:
        gradient_accumulation_steps: int = 1
        max_steps: int = -1
        num_train_epochs: float = 3.0
        learning_rate: float = 5e-5
        per_device_train_batch_size: int = 8
        output_dir: str = ""
        logging_steps: int = 10
        save_steps: int = 500
        evaluation_strategy: str = "no"
        load_best_model_at_end: bool = False
        fp16: bool = False
        dataloader_num_workers: int = 0
        local_rank: int = -1
        world_size: int = 1

        def __init__(self, *args, **kwargs):
            raise ImportError(_ERR)

    class TrainerState:
        epoch: float = 0.0
        global_step: int = 0
        best_metric: float | None = None
        log_history: list = []

    class Trainer:
        model: PreTrainedModel
        optimizer: object
        lr_scheduler: object
        state: TrainerState

        def __init__(self, *args, **kwargs):
            raise ImportError(_ERR)

        def train(self, *args, **kwargs):
            raise ImportError(_ERR)

        def evaluate(self, *args, **kwargs):
            raise ImportError(_ERR)

        def save_model(self, *args, **kwargs):
            raise ImportError(_ERR)

        def add_callback(self, *args, **kwargs):
            raise ImportError(_ERR)

        def get_train_dataloader(self, *args, **kwargs):
            raise ImportError(_ERR)

        def create_optimizer_and_scheduler(self, *args, **kwargs):
            raise ImportError(_ERR)

        def prediction_loop(self, *args, **kwargs):
            raise ImportError(_ERR)

        def compute_loss(self, *args, **kwargs):
            raise ImportError(_ERR)

    def get_scheduler(*args, **kwargs):
        raise ImportError(_ERR)

    __version__ = "999.0.0+stub"
    __all__ = [
        "AutoConfig",
        "AutoModel",
        "AutoModelForCausalLM",
        "AutoModelForMaskedLM",
        "AutoModelForSequenceClassification",
        "AutoModelForSeq2SeqLM",
        "AutoTokenizer",
        "BertModel",
        "BitsAndBytesConfig",
        "DataCollatorForLanguageModeling",
        "DistilBertModel",
        "EarlyStoppingCallback",
        "GPT2Config",
        "GPT2LMHeadModel",
        "PreTrainedModel",
        "PreTrainedTokenizerBase",
        "PreTrainedTokenizerFast",
        "RobertaModel",
        "T5ForConditionalGeneration",
        "Trainer",
        "TrainerCallback",
        "TrainerState",
        "TrainingArguments",
        "get_scheduler",
        "__version__",
    ]
    __path__ = []
