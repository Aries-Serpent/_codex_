#!/usr/bin/env bash
# setup.sh — Repo-native Codex setup for GPT-OSS local runtime
# Target: Ubuntu 24.04 (Codex-universal style), agent internet ON, unrestricted HTTP.
# Behavior:
#   - Creates .venv under the repo
#   - Prefetches GPT-OSS weights (20b default; 120b switchable)
#   - vLLM (GPU) default; Transformers (CPU) fallback with a FastAPI proxy providing OpenAI-compatible endpoints
#   - Helpers: stop.sh, switch_model.sh (20b↔120b), start_tp.sh (tensor-parallel)
# References: OpenAI GPT-OSS 16 GB / 80 GB & 128k ctx; vLLM recipe; your codex-base repo.

run_user_setup() {
  local repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  local script_path="${CODEX_USER_SETUP_PATH:-${repo_root}/.codex/user_setup.sh}"
  local sentinel="${repo_root}/.codex/.user_setup.done"
  [[ -f "$script_path" ]] || return 0
  if [[ -f "$sentinel" && "${CODEX_USER_SETUP_FORCE:-0}" != "1" ]]; then
    return 0
  fi
  local log_dir="${repo_root}/.codex/setup_logs"
  mkdir -p "$log_dir" "${repo_root}/.codex"
  local ts="$(date -u +%Y%m%dT%H%M%SZ)"
  local log_file="${log_dir}/${ts}.log"
  local sid="${CODEX_SESSION_ID:-}"
  if [[ -n "$sid" ]]; then
    (
      cd "$repo_root"
      python3 - "$sid" <<'PY'
from src.codex.logging.session_logger import log_event
import sys
sid = sys.argv[1]
try:
    log_event(sid, 'system', 'user_setup:start')
except Exception:
    pass
PY
    )
  fi
  (
    cd "$repo_root"
    bash "$script_path" >"$log_file" 2>&1
  )
  local status=$?
  if [[ -n "$sid" ]]; then
    (
      cd "$repo_root"
      python3 - "$sid" <<'PY'
from src.codex.logging.session_logger import log_event
import sys
sid = sys.argv[1]
try:
    log_event(sid, 'system', 'user_setup:end')
except Exception:
    pass
PY
    )
  fi
  if [[ $status -eq 0 ]]; then
    touch "$sentinel"
  fi
  return $status
}

if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
  return 0
fi

set -euo pipefail

# ---- Location & knobs ----
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKDIR="${REPO_ROOT}/gpt-oss"
PYVENV="${WORKDIR}/.venv"
PORT="${PORT:-8000}"
MODEL="${MODEL:-openai/gpt-oss-20b}"          # override via env; later: openai/gpt-oss-120b
CTX="${CTX:-32768}"                            # reduce if VRAM is tight; both models support up to 128k
DOWNLOAD_DIR="${DOWNLOAD_DIR:-${WORKDIR}/weights-$(basename "${MODEL}")}"

echo "[SETUP] repo=${REPO_ROOT} workdir=${WORKDIR} model=${MODEL} ctx=${CTX} port=${PORT}"

mkdir -p "${WORKDIR}/runtime"
cd "${WORKDIR}"

# ---- System tools (idempotent) ----
if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y git git-lfs curl jq lsof pkg-config python3-venv build-essential pciutils
fi
git lfs install || true

# ---- Python env & HF fast downloads ----
python3 -m venv "${PYVENV}"
# shellcheck disable=SC1090
source "${PYVENV}/bin/activate"
pip install -U pip uv "huggingface_hub[cli]" hf-transfer
export HF_HUB_ENABLE_HF_TRANSFER=1

# ---- .env for runtime scripts ----
cat > "${WORKDIR}/.env" <<ENV
MODEL=${MODEL}
CTX=${CTX}
DOWNLOAD_DIR=${DOWNLOAD_DIR}
PORT=${PORT}
ENV

# ---- Prefetch weights ----
echo "[SETUP] Downloading weights to ${DOWNLOAD_DIR}"
huggingface-cli download "${MODEL}" --local-dir "${DOWNLOAD_DIR}" --include="*"

# ---- Stop helper (works for both vLLM and proxy) ----
cat > "${WORKDIR}/runtime/stop.sh" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
PID=$(lsof -ti tcp:8000 || true)
[ -n "${PID}" ] && kill ${PID} && echo "Stopped PID ${PID}" || echo "No server listening on :8000"
SH
chmod +x "${WORKDIR}/runtime/stop.sh"

# ---- GPU detection ----
GPU_VENDOR="$( (lspci | grep -Ei 'vga|3d|display' | grep -Eio 'NVIDIA|AMD|Advanced Micro Devices|Intel' | head -n1) || true )"
FALLBACK=0

# ---- vLLM (GPU) preferred path ----
if echo "${GPU_VENDOR}" | grep -qi nvidia; then
  echo "[SETUP] NVIDIA GPU detected → installing vLLM (CUDA 12.8 wheels)"
  uv pip install --pre "vllm==0.10.1+gptoss" \
    --extra-index-url https://wheels.vllm.ai/gpt-oss/ \
    --extra-index-url https://download.pytorch.org/whl/nightly/cu128 \
    --index-strategy unsafe-best-match

  cat > "${WORKDIR}/runtime/start.sh" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../.env"
exec vllm serve "$MODEL" \
  --host 0.0.0.0 --port "${PORT}" \
  --max-model-len "${CTX}" \
  --dtype auto \
  --download-dir "${DOWNLOAD_DIR}"
SH
  chmod +x "${WORKDIR}/runtime/start.sh"

elif echo "${GPU_VENDOR}" | grep -Eqi 'AMD|Advanced Micro Devices'; then
  echo "[SETUP] AMD GPU detected → trying vLLM (ROCm); fallback to Transformers if wheel not available"
  if uv pip install --pre "vllm==0.10.1+gptoss" --index-url https://wheels.vllm.ai/gpt-oss/ 2>/dev/null; then
    echo "[SETUP] vLLM (ROCm) installed"
    cat > "${WORKDIR}/runtime/start.sh" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../.env"
exec vllm serve "$MODEL" \
  --host 0.0.0.0 --port "${PORT}" \
  --max-model-len "${CTX}" \
  --dtype auto \
  --download-dir "${DOWNLOAD_DIR}"
SH
    chmod +x "${WORKDIR}/runtime/start.sh"
  else
    echo "[WARN] ROCm vLLM wheel unavailable in this env → using Transformers fallback"
    FALLBACK=1
  fi

else
  echo "[SETUP] No supported discrete GPU found (or vendor not recognized) → Transformers fallback"
  FALLBACK=1
fi

# ---- Transformers (CPU) fallback + FastAPI proxy (OpenAI-compatible) ----
if [ "${FALLBACK}" = "1" ]; then
  echo "[SETUP] Installing Transformers/Accelerate/Torch + FastAPI proxy"
  pip install "transformers>=4.43" "accelerate>=0.33" "torch>=2.4" --extra-index-url https://download.pytorch.org/whl/cu128 || \
  pip install "transformers>=4.43" "accelerate>=0.33" "torch>=2.4"
  pip install --upgrade fastapi uvicorn ujson

  cat > "${WORKDIR}/runtime/proxy.py" <<'PY'
import os, time, uuid, threading
from typing import List, Optional, Union, Dict, Any, Iterable
from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer

MODEL_NAME = os.environ.get("MODEL", "openai/gpt-oss-20b")
CTX = int(os.environ.get("CTX", "32768"))

_tok = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
if _tok.pad_token_id is None and _tok.eos_token_id is not None:
    _tok.pad_token_id = _tok.eos_token_id

_model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME, torch_dtype="auto", device_map="auto", trust_remote_code=True
)

def build_prompt_from_messages(messages: List[Dict[str, str]]) -> str:
    try:
        return _tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    except Exception:
        sys_txt = ""
        lines = []
        for m in messages:
            role, content = m.get("role","user"), m.get("content","")
            if role == "system":
                sys_txt += content.strip() + "\n"
            else:
                lines.append(f"{role.upper()}: {content.strip()}")
        return (("SYSTEM: " + sys_txt.strip() + "\n") if sys_txt else "") + "\n".join(lines) + "\nASSISTANT:"

def count_tokens(text: str) -> int:
    return len(_tok.encode(text, add_special_tokens=False))

def enforce_token_budget(prompt: str, requested_max_new: int) -> int:
    t_in = count_tokens(prompt)
    budget = max(1, CTX - t_in)
    return min(int(requested_max_new), budget)

class ChatMessage(BaseModel):
    role: str
    content: Union[str, List[Dict[str, Any]]]

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    max_tokens: Optional[int] = Field(default=256, alias="max_tokens")
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None

class ChatChoice(BaseModel):
    index: int
    finish_reason: Optional[str] = "stop"
    message: Dict[str, Any]

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatChoice]
    usage: Optional[Dict[str, int]] = None

class CompletionRequest(BaseModel):
    model: str
    prompt: Union[str, List[str]]
    max_tokens: Optional[int] = 256
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None

app = FastAPI()

@app.get("/v1/models")
def list_models():
    return {"object":"list","data":[{"id":MODEL_NAME,"object":"model","created":int(time.time()),"owned_by":"owner"}]}

def _gen_kwargs(temperature: float, top_p: float, max_new_tokens: int) -> Dict[str, Any]:
    do_sample = temperature is not None and temperature > 0
    return dict(
        max_new_tokens=max_new_tokens,
        do_sample=do_sample,
        temperature=float(temperature) if do_sample else None,
        top_p=float(top_p) if do_sample else None,
        eos_token_id=_tok.eos_token_id,
        pad_token_id=_tok.pad_token_id,
    )

def _make_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:24]}"

def _usage(prompt_text: str, out_text: str) -> Dict[str, int]:
    tin = count_tokens(prompt_text)
    tout = count_tokens(out_text)
    return {"prompt_tokens": tin, "completion_tokens": tout, "total_tokens": tin + tout}

@app.post("/v1/chat/completions")
def chat_completions(req: ChatCompletionRequest):
    prompt = build_prompt_from_messages([m.model_dump() for m in req.messages])
    max_new = enforce_token_budget(prompt, int(req.max_tokens or 256))

    if req.stream:
        streamer = TextIteratorStreamer(_tok, skip_prompt=True, skip_special_tokens=True)
        inputs = _tok([prompt], return_tensors="pt").to(_model.device)
        gen_kwargs = _gen_kwargs(req.temperature, req.top_p, max_new)

        thread = threading.Thread(target=_model.generate, kwargs=dict(**inputs, streamer=streamer, **{k:v for k,v in gen_kwargs.items() if v is not None}))
        thread.start()

        def event_stream():
            created = int(time.time())
            chunk_id = _make_id("chatcmpl")
            for token_text in streamer:
                chunk = {"id":chunk_id,"object":"chat.completion.chunk","created":created,"model":req.model,"choices":[{"index":0,"delta":{"role":"assistant","content":token_text},"finish_reason":None}]}
                yield f"data: {JSONResponse(content=chunk).body.decode()}\n\n".encode("utf-8")
            yield b"data: [DONE]\n\n"
        return StreamingResponse(event_stream(), media_type="text/event-stream")

    inputs = _tok([prompt], return_tensors="pt").to(_model.device)
    gen_kwargs = _gen_kwargs(req.temperature, req.top_p, max_new)
    with torch.no_grad():
        out = _model.generate(**inputs, **{k:v for k,v in gen_kwargs.items() if v is not None})
    text = _tok.decode(out[0], skip_special_tokens=True)
    if "ASSISTANT:" in text:
        text = text.split("ASSISTANT:",1)[-1].strip()

    return JSONResponse(content={
      "id":_make_id("chatcmpl"), "object":"chat.completion", "created":int(time.time()),
      "model":req.model, "choices":[{"index":0,"message":{"role":"assistant","content":text},"finish_reason":"stop"}],
      "usage":_usage(prompt, text)
    })

@app.post("/v1/completions")
def completions(req: CompletionRequest):
    prompt = req.prompt if isinstance(req.prompt, str) else "\n\n".join(req.prompt)
    max_new = enforce_token_budget(prompt, int(req.max_tokens or 256))
    inputs = _tok([prompt], return_tensors="pt").to(_model.device)
    gen_kwargs = _gen_kwargs(req.temperature, req.top_p, max_new)

    if req.stream:
        streamer = TextIteratorStreamer(_tok, skip_prompt=True, skip_special_tokens=True)
        thread = threading.Thread(target=_model.generate, kwargs=dict(**inputs, streamer=streamer, **{k:v for k,v in gen_kwargs.items() if v is not None}))
        thread.start()

        def event_stream():
            created = int(time.time())
            chunk_id = _make_id("cmpl")
            for token_text in streamer:
                chunk = {"id":chunk_id,"object":"text_completion.chunk","created":created,"model":req.model,"choices":[{"index":0,"text":token_text,"finish_reason":None}]}
                yield f"data: {JSONResponse(content=chunk).body.decode()}\n\n".encode("utf-8")
            yield b"data: [DONE]\n\n"
        return StreamingResponse(event_stream(), media_type="text/event-stream")

    with torch.no_grad():
        out = _model.generate(**inputs, **{k:v for k,v in gen_kwargs.items() if v is not None})
    text = _tok.decode(out[0], skip_special_tokens=True)
    return JSONResponse(content={"id":_make_id("cmpl"),"object":"text_completion","created":int(time.time()),"model":req.model,"choices":[{"index":0,"text":text,"finish_reason":"stop"}], "usage":_usage(prompt, text)})

@app.get("/")
def root():
    return {"ok":True,"model":MODEL_NAME,"ctx":CTX}
PY

  # Fallback start runs the proxy
  cat > "${WORKDIR}/runtime/start.sh" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../.env"
exec uvicorn proxy:app --host 0.0.0.0 --port "${PORT}"
SH
  chmod +x "${WORKDIR}/runtime/start.sh"
fi

# ---- Tensor-parallel helper (multi-GPU vLLM) ----
cat > "${WORKDIR}/runtime/start_tp.sh" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../.env"
detect_ngpu() {
  if command -v nvidia-smi >/dev/null 2>&1; then nvidia-smi -L | wc -l
  elif command -v rocminfo >/dev/null 2>&1; then rocminfo | grep -c '^  Name:.*gfx'
  else echo 0; fi
}
NGPU=$(detect_ngpu)
TP="${TP_SIZE:-0}"; [ "$TP" -le 0 ] && TP="$NGPU"
if [ "$TP" -le 1 ]; then echo "[ERROR] Need >=2 GPUs for tensor parallel. Detected: $NGPU"; exit 1; fi
export NCCL_P2P_LEVEL=NVL
export NCCL_IB_DISABLE=1
exec vllm serve "$MODEL" \
  --host 0.0.0.0 --port "${PORT}" \
  --max-model-len "${CTX}" \
  --dtype auto \
  --tensor-parallel-size "${TP}" \
  --download-dir "${DOWNLOAD_DIR}"
SH
chmod +x "${WORKDIR}/runtime/start_tp.sh"

# ---- 20b↔120b switch helper ----
cat > "${WORKDIR}/runtime/switch_model.sh" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ $# -lt 1 ]; then echo "Usage: $0 {20b|120b}"; exit 1; fi
case "$1" in
  20b) NEW="openai/gpt-oss-20b" ;;
  120b) NEW="openai/gpt-oss-120b" ;;
  *) echo "Unknown target: $1"; exit 1 ;;
esac
sed -i "s#openai/gpt-oss-[0-9]*b#${NEW}#g" ./.env
# shellcheck disable=SC1090
source ./.env
echo "[INFO] Downloading weights for $MODEL to $DOWNLOAD_DIR ..."
huggingface-cli download "$MODEL" --local-dir "$DOWNLOAD_DIR" --include="*"
echo "[INFO] Restarting server ..."
./runtime/stop.sh || true
./runtime/start.sh &
echo "[DONE] Switched to $MODEL."
SH
chmod +x "${WORKDIR}/runtime/switch_model.sh"

# ---- Launch & smoke tests ----
echo "[SETUP] Starting runtime..."
"${WORKDIR}/runtime/start.sh" & sleep 8 || true

if curl -sf "http://localhost:${PORT}/v1/models" >/dev/null; then
  echo "[TEST] OpenAI-compatible endpoint detected → chat completion"
  curl -s "http://localhost:${PORT}/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d '{"model":"gpt-oss-20b","messages":[{"role":"user","content":"Say hello in one concise sentence."}],"max_tokens":48}' \
    | jq '.choices[0].message.content'
else
  echo "[TEST] Endpoint not responding; check logs above."
fi

echo "[HEALTH] GPU:"
(nvidia-smi --query-gpu=name,driver_version,memory.total,memory.used --format=csv,noheader || true)
curl -s "http://localhost:${PORT}/v1/models" | jq || true

echo "[DONE] setup.sh complete. Helpers: stop.sh, switch_model.sh {20b|120b}, start_tp.sh (multi-GPU)."
