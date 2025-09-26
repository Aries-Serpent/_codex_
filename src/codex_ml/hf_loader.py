import os
from pathlib import Path
from typing import Optional, Union
from urllib.parse import unquote, urlparse

from transformers import (
    AutoModel,
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizerBase,
)


RepoId = Union[str, os.PathLike[str]]


def _is_local_identifier(repo_id: RepoId) -> bool:
    if isinstance(repo_id, os.PathLike):
        candidate_path = Path(repo_id).expanduser()
        if candidate_path.exists():
            return True
        candidate_str = str(candidate_path)
    else:
        candidate_str = str(repo_id)
        candidate_path = Path(candidate_str).expanduser()
        if candidate_path.exists():
            return True

    parsed = urlparse(candidate_str)
    if parsed.scheme != "file":
        return False
    local_path = Path(unquote(parsed.path)).expanduser()
    if parsed.netloc and not local_path.is_absolute():
        local_path = Path(f"//{parsed.netloc}{local_path}")
    return local_path.exists()


def _required_revision(repo_id: RepoId, explicit: Optional[str]) -> Optional[str]:
    if _is_local_identifier(repo_id):
        return explicit
    rev = explicit or os.environ.get("HF_REVISION") or os.environ.get("HUGGINGFACE_REVISION")
    if not rev:
        raise RuntimeError(
            "Hugging Face `revision` is required (Bandit B615). "
            "Set HF_REVISION/HUGGINGFACE_REVISION env var or pass `revision=`."
        )
    return rev


def load_tokenizer(
    repo_id: RepoId,
    *,
    revision: Optional[str] = None,
    trust_remote_code: bool = False,
) -> PreTrainedTokenizerBase:
    rev = _required_revision(repo_id, revision)
    return AutoTokenizer.from_pretrained(  # nosec B615 - revision enforced via _required_revision
        repo_id,
        revision=rev,
        trust_remote_code=trust_remote_code,
    )


def load_model(
    repo_id: RepoId,
    *,
    revision: Optional[str] = None,
    trust_remote_code: bool = False,
) -> PreTrainedModel:
    rev = _required_revision(repo_id, revision)
    return AutoModel.from_pretrained(  # nosec B615 - revision enforced via _required_revision
        repo_id,
        revision=rev,
        trust_remote_code=trust_remote_code,
    )


def load_causal_lm(
    repo_id: RepoId,
    *,
    revision: Optional[str] = None,
    trust_remote_code: bool = False,
) -> PreTrainedModel:
    rev = _required_revision(repo_id, revision)
    return AutoModelForCausalLM.from_pretrained(  # nosec B615 - revision enforced via _required_revision
        repo_id,
        revision=rev,
        trust_remote_code=trust_remote_code,
    )
