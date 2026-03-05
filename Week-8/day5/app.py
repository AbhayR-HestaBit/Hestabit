# week 8 deliverables
from __future__ import annotations
import json
import time
import uuid
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from deploy.model_loader import get_model
    from deploy.config import MODEL_PATH, N_CTX, N_THREADS, N_BATCH, N_GPU_LAYERS, VERBOSE
except ImportError:
    logger.error("Required module 'deploy' not found. Please ensure deploy/ folder exists.")
    # Fallback to defaults if module missing (for demonstration)
    MODEL_PATH = "quantized/model.gguf"
    N_CTX, N_THREADS, N_BATCH, N_GPU_LAYERS, VERBOSE = 2048, 4, 512, 0, False
    def get_model(): return None

app = FastAPI(
    title="Week 8 Local LLM API",
    description="Production-ready FastAPI app for local GGUF model inference",
    version="1.1.0",
)
LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
CHAT_STORE = LOG_DIR / "chat_sessions.json"
REQUEST_LOG = LOG_DIR / "requests.jsonl"
class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    max_tokens: int = Field(default=128, ge=1, le=1024)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    top_k: int = Field(default=40, ge=1, le=200)
    repeat_penalty: float = Field(default=1.1, ge=0.5, le=2.0)
    stream: bool = False
    system_prompt: Optional[str] = None
class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    system_prompt: str = Field(default="You are a helpful local medical assistant.")
    max_tokens: int = Field(default=128, ge=1, le=1024)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    top_k: int = Field(default=40, ge=1, le=200)
    repeat_penalty: float = Field(default=1.1, ge=0.5, le=2.0)
def append_request_log(payload: Dict[str, Any]) -> None:
    try:
        with REQUEST_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.error(f"Failed to log request: {e}")

def load_chat_sessions() -> Dict[str, List[Dict[str, str]]]:
    if CHAT_STORE.exists():
        try:
            return json.loads(CHAT_STORE.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error(f"Error reading chat store: {e}")
            return {}
    return {}
def save_chat_sessions(data: Dict[str, List[Dict[str, str]]]) -> None:
    try:
        CHAT_STORE.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except Exception as e:
        logger.error(f"Failed to save chat sessions: {e}")
def build_generate_prompt(prompt: str, system_prompt: Optional[str] = None) -> str:
    if system_prompt:
        return (
            f"<system>\n{system_prompt}\n</system>\n"
            f"<user>\n{prompt}\n</user>\n"
            f"<assistant>\n"
        )
    return prompt
def build_chat_prompt(
    system_prompt: str,
    history: List[Dict[str, str]],
    user_message: str,
) -> str:
    parts = [f"<system>\n{system_prompt}\n</system>"]
    for turn in history:
        role = turn.get("role", "user")
        content = turn.get("content", "")
        parts.append(f"<{role}>\n{content}\n</{role}>")
    parts.append(f"<user>\n{user_message}\n</user>")
    parts.append("<assistant>\n")
    return "\n".join(parts)
def run_inference(
    prompt: str,
    max_tokens: int,
    temperature: float,
    top_p: float,
    top_k: int,
    repeat_penalty: float,
) -> Dict[str, Any]:
    logger.info(f"Running inference for prompt (len: {len(prompt)})")
    try:
        llm = get_model()
        if llm is None:
            raise RuntimeError("LLM instance is not initialized.")
            
        started = time.time()
        output = llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            repeat_penalty=repeat_penalty,
            echo=False,
        )
        elapsed = round(time.time() - started, 4)
        text = output["choices"][0]["text"].strip()
        usage = output.get("usage", {})
        
        logger.info(f"Inference completed in {elapsed}s")
        return {
            "text": text,
            "latency_sec": elapsed,
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens"),
        }
    except Exception as e:
        logger.error(f"Critical error during inference: {str(e)}", exc_info=True)
        return {
            "text": "Internal error: could not generate response.",
            "latency_sec": 0.0,
            "error": str(e)
        }
@app.get("/health")
def health() -> Dict[str, Any]:
    model_exists = Path(MODEL_PATH).exists()
    return {
        "status": "ok",
        "model_path": str(MODEL_PATH),
        "model_exists": model_exists,
        "n_ctx": N_CTX,
        "n_threads": N_THREADS,
        "n_batch": N_BATCH,
        "n_gpu_layers": N_GPU_LAYERS,
        "verbose": VERBOSE,
    }
@app.post("/generate")
def generate(req: GenerateRequest) -> Dict[str, Any]:
    if not Path(MODEL_PATH).exists():
        raise HTTPException(status_code=500, detail=f"Model not found at: {MODEL_PATH}")
    request_id = str(uuid.uuid4())
    final_prompt = build_generate_prompt(req.prompt, req.system_prompt)
    result = run_inference(
        prompt=final_prompt,
        max_tokens=req.max_tokens,
        temperature=req.temperature,
        top_p=req.top_p,
        top_k=req.top_k,
        repeat_penalty=req.repeat_penalty,
    )
    log_payload = {
        "request_id": request_id,
        "endpoint": "/generate",
        "prompt": req.prompt,
        "system_prompt": req.system_prompt,
        "params": {
            "max_tokens": req.max_tokens,
            "temperature": req.temperature,
            "top_p": req.top_p,
            "top_k": req.top_k,
            "repeat_penalty": req.repeat_penalty,
        },
        "result": result,
    }
    append_request_log(log_payload)
    return {
        "request_id": request_id,
        "endpoint": "/generate",
        **result,
    }
@app.post("/chat")
def chat(req: ChatRequest) -> Dict[str, Any]:
    if not Path(MODEL_PATH).exists():
        raise HTTPException(status_code=500, detail=f"Model not found at: {MODEL_PATH}")
    request_id = str(uuid.uuid4())
    sessions = load_chat_sessions()
    history = sessions.get(req.session_id, [])
    final_prompt = build_chat_prompt(
        system_prompt=req.system_prompt,
        history=history,
        user_message=req.message,
    )
    result = run_inference(
        prompt=final_prompt,
        max_tokens=req.max_tokens,
        temperature=req.temperature,
        top_p=req.top_p,
        top_k=req.top_k,
        repeat_penalty=req.repeat_penalty,
    )
    assistant_text = result["text"]
    history.append({"role": "user", "content": req.message})
    history.append({"role": "assistant", "content": assistant_text})
    sessions[req.session_id] = history
    save_chat_sessions(sessions)
    log_payload = {
        "request_id": request_id,
        "endpoint": "/chat",
        "session_id": req.session_id,
        "message": req.message,
        "system_prompt": req.system_prompt,
        "params": {
            "max_tokens": req.max_tokens,
            "temperature": req.temperature,
            "top_p": req.top_p,
            "top_k": req.top_k,
            "repeat_penalty": req.repeat_penalty,
        },
        "result": result,
    }
    append_request_log(log_payload)
    return {
        "request_id": request_id,
        "endpoint": "/chat",
        "session_id": req.session_id,
        "history_length": len(history),
        **result,
    }