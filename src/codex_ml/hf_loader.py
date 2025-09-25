import os
from typing import Optional

from transformers import (
    AutoModel,
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizerBase,
)


def _required_revision(explicit: Optional[str]) -> str:
    rev = explicit or os.environ.get("HF_REVISION") or os.environ.get("HUGGINGFACE_REVISION")
    if not rev:
        raise RuntimeError(
            "Hugging Face `revision` is required (Bandit B615). "
            "Set HF_REVISION/HUGGINGFACE_REVISION env var or pass `revision=`."
        )
    return rev


def load_tokenizer(
    repo_id: str,
    *,
    revision: Optional[str] = None,
    trust_remote_code: bool = False,
) -> PreTrainedTokenizerBase:
    rev = _required_revision(revision)
    return AutoTokenizer.from_pretrained(  # nosec B615 - revision enforced via _required_revision
        repo_id,
        revision=rev,
        trust_remote_code=trust_remote_code,
    )


def load_model(
    repo_id: str,
    *,
    revision: Optional[str] = None,
    trust_remote_code: bool = False,
) -> PreTrainedModel:
    rev = _required_revision(revision)
    return AutoModel.from_pretrained(  # nosec B615 - revision enforced via _required_revision
        repo_id,
        revision=rev,
        trust_remote_code=trust_remote_code,
    )


def load_causal_lm(
    repo_id: str,
    *,
    revision: Optional[str] = None,
    trust_remote_code: bool = False,
) -> PreTrainedModel:
    rev = _required_revision(revision)
    return AutoModelForCausalLM.from_pretrained(  # nosec B615 - revision enforced via _required_revision
        repo_id,
        revision=rev,
        trust_remote_code=trust_remote_code,
    )
