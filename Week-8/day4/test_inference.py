from __future__ import annotations

import argparse
import csv
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

PROMPTS = [
    {
        "id": "qa_1",
        "instruction": "Answer this medical question truthfully.",
        "input": "What is the likely diagnosis in a patient with fever, productive cough, and lobar consolidation on chest X-ray?",
        "expected_keywords": ["pneumonia"],
    },
    {
        "id": "reasoning_1",
        "instruction": "Reason briefly and answer the question.",
        "input": "A patient has unilateral leg swelling after a long flight and suddenly develops neurological deficits. What cardiac finding may explain this?",
        "expected_keywords": ["patent foramen ovale", "pfo"],
    },
    {
        "id": "extraction_1",
        "instruction": "Extract the key entities from the text.",
        "input": "Patient John Doe, age 56, has diabetes mellitus and hypertension and was prescribed metformin 500 mg.",
        "expected_keywords": ["john doe", "56", "diabetes mellitus", "hypertension", "metformin"],
    },
]

def now_ts() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def keyword_accuracy(text: str, expected_keywords: List[str]) -> float:
    if not expected_keywords:
        return 0.0
    lower = text.lower()
    found = sum(1 for kw in expected_keywords if kw.lower() in lower)
    return found / len(expected_keywords)

def build_prompt(item: Dict[str, Any]) -> str:
    instruction = (item.get("instruction") or "").strip()
    inp = (item.get("input") or "").strip()
    if inp:
        return f"### Instruction:\n{instruction}\n\n### Input:\n{inp}\n\n### Response:\n"
    return f"### Instruction:\n{instruction}\n\n### Response:\n"

def detect_vram_mb() -> Optional[float]:
    try:
        import torch
        if torch.cuda.is_available():
            return round(torch.cuda.max_memory_allocated() / (1024 ** 2), 2)
    except Exception:
        pass
    return None

class HFRunner:
    def __init__(self, model_path: str, adapter_path: Optional[str] = None, max_new_tokens: int = 96):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.torch = torch
        self.model_path = model_path
        self.adapter_path = adapter_path
        self.max_new_tokens = max_new_tokens

        self.tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        device_map = "auto" if torch.cuda.is_available() else None

        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=dtype,
            device_map=device_map,
        )

        if adapter_path:
            from peft import PeftModel
            self.model = PeftModel.from_pretrained(self.model, adapter_path)

        if not torch.cuda.is_available():
            self.model.to("cpu")
        self.model.eval()

    def generate_one(self, prompt: str) -> Dict[str, Any]:
        import torch
        start = time.perf_counter()
        inputs = self.tokenizer(prompt, return_tensors="pt")
        if torch.cuda.is_available():
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
            torch.cuda.reset_peak_memory_stats()
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                use_cache=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        latency = time.perf_counter() - start
        full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        generated_text = full_text[len(prompt):] if full_text.startswith(prompt) else full_text
        gen_tokens = int(outputs.shape[-1] - inputs["input_ids"].shape[-1])
        tps = gen_tokens / latency if latency > 0 else 0.0
        vram = detect_vram_mb()
        return {
            "output_text": generated_text.strip(),
            "latency_sec": round(latency, 4),
            "generated_tokens": gen_tokens,
            "tokens_per_sec": round(tps, 4),
            "vram_mb": vram,
        }

    def stream_one(self, prompt: str) -> str:
        import torch
        from transformers import TextIteratorStreamer
        from threading import Thread
        streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)
        inputs = self.tokenizer(prompt, return_tensors="pt")
        if torch.cuda.is_available():
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        kwargs = dict(
            **inputs,
            max_new_tokens=self.max_new_tokens,
            do_sample=False,
            use_cache=True,
            streamer=streamer,
            pad_token_id=self.tokenizer.eos_token_id,
        )
        thread = Thread(target=self.model.generate, kwargs=kwargs)
        thread.start()
        chunks = []
        for piece in streamer:
            print(piece, end="", flush=True)
            chunks.append(piece)
        print()
        thread.join()
        return "".join(chunks).strip()

    def batch_generate(self, prompts: List[str]) -> List[str]:
        import torch
        inputs = self.tokenizer(prompts, return_tensors="pt", padding=True, truncation=True)
        if torch.cuda.is_available():
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                use_cache=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        decoded = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
        cleaned = []
        for prompt, text in zip(prompts, decoded):
            cleaned.append(text[len(prompt):].strip() if text.startswith(prompt) else text.strip())
        return cleaned

class GGUFRunner:
    def __init__(self, model_path: str, max_new_tokens: int = 96):
        from llama_cpp import Llama
        self.model_path = model_path
        self.max_new_tokens = max_new_tokens
        self.llm = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=max(1, os.cpu_count() or 1),
            verbose=False,
        )

    def generate_one(self, prompt: str) -> Dict[str, Any]:
        start = time.perf_counter()
        out = self.llm(
            prompt,
            max_tokens=self.max_new_tokens,
            temperature=0.0,
            top_p=1.0,
            echo=False,
            stream=False,
        )
        latency = time.perf_counter() - start
        text = out["choices"][0]["text"].strip()
        usage = out.get("usage", {})
        gen_tokens = int(usage.get("completion_tokens", 0))
        tps = gen_tokens / latency if latency > 0 else 0.0
        return {
            "output_text": text,
            "latency_sec": round(latency, 4),
            "generated_tokens": gen_tokens,
            "tokens_per_sec": round(tps, 4),
            "vram_mb": None,
        }

    def stream_one(self, prompt: str) -> str:
        pieces = []
        for chunk in self.llm(
            prompt,
            max_tokens=self.max_new_tokens,
            temperature=0.0,
            top_p=1.0,
            echo=False,
            stream=True,
        ):
            text = chunk["choices"][0]["text"]
            print(text, end="", flush=True)
            pieces.append(text)
        print()
        return "".join(pieces).strip()

    def batch_generate(self, prompts: List[str]) -> List[str]:
        # llama-cpp-python doesn't batch like transformers here; run sequentially but keep same API.
        return [self.generate_one(p)["output_text"] for p in prompts]

def build_runner(kind: str, model_path: str, adapter_path: Optional[str], max_new_tokens: int):
    if kind == "base":
        return HFRunner(model_path=model_path, adapter_path=None, max_new_tokens=max_new_tokens)
    if kind == "fine_tuned":
        return HFRunner(model_path=model_path, adapter_path=adapter_path, max_new_tokens=max_new_tokens)
    if kind == "gguf":
        return GGUFRunner(model_path=model_path, max_new_tokens=max_new_tokens)
    raise ValueError(f"Unsupported kind: {kind}")

def benchmark_model(
    kind: str,
    label: str,
    model_path: str,
    adapter_path: Optional[str],
    prompts: List[Dict[str, Any]],
    max_new_tokens: int,
    run_streaming: bool,
    run_batch: bool,
) -> List[Dict[str, Any]]:
    results = []
    runner = build_runner(kind=kind, model_path=model_path, adapter_path=adapter_path, max_new_tokens=max_new_tokens)

    # Multi-prompt test
    for item in prompts:
        prompt = build_prompt(item)
        res = runner.generate_one(prompt)
        res.update({
            "timestamp": now_ts(),
            "model_label": label,
            "model_kind": kind,
            "prompt_id": item["id"],
            "mode": "single",
            "accuracy": round(keyword_accuracy(res["output_text"], item["expected_keywords"]), 4),
            "prompt_preview": item["input"][:120],
        })
        results.append(res)

    # Streaming output mode
    if run_streaming and prompts:
        prompt = build_prompt(prompts[0])
        print(f"\n--- Streaming demo for {label} ---")
        start = time.perf_counter()
        stream_text = runner.stream_one(prompt)
        latency = time.perf_counter() - start
        results.append({
            "timestamp": now_ts(),
            "model_label": label,
            "model_kind": kind,
            "prompt_id": prompts[0]["id"],
            "mode": "streaming",
            "output_text": stream_text,
            "latency_sec": round(latency, 4),
            "generated_tokens": max(0, len(stream_text.split())),
            "tokens_per_sec": round((max(1, len(stream_text.split())) / latency), 4) if latency > 0 else 0.0,
            "vram_mb": detect_vram_mb(),
            "accuracy": round(keyword_accuracy(stream_text, prompts[0]["expected_keywords"]), 4),
            "prompt_preview": prompts[0]["input"][:120],
        })

    # Batch inference
    if run_batch and prompts:
        batch_prompts = [build_prompt(p) for p in prompts]
        start = time.perf_counter()
        outputs = runner.batch_generate(batch_prompts)
        latency = time.perf_counter() - start
        per_prompt_latency = latency / max(1, len(batch_prompts))
        total_tokens = sum(max(1, len(x.split())) for x in outputs)
        tps = total_tokens / latency if latency > 0 else 0.0
        for item, out_text in zip(prompts, outputs):
            results.append({
                "timestamp": now_ts(),
                "model_label": label,
                "model_kind": kind,
                "prompt_id": item["id"],
                "mode": "batch",
                "output_text": out_text,
                "latency_sec": round(per_prompt_latency, 4),
                "generated_tokens": max(1, len(out_text.split())),
                "tokens_per_sec": round(tps, 4),
                "vram_mb": detect_vram_mb(),
                "accuracy": round(keyword_accuracy(out_text, item["expected_keywords"]), 4),
                "prompt_preview": item["input"][:120],
            })

    return results

def save_results(rows: List[Dict[str, Any]], out_dir: Path) -> None:
    ensure_dir(out_dir)
    csv_path = out_dir / "results.csv"
    json_path = out_dir / "results.json"

    fields = [
        "timestamp", "model_label", "model_kind", "prompt_id", "mode", "latency_sec",
        "generated_tokens", "tokens_per_sec", "vram_mb", "accuracy", "prompt_preview", "output_text"
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in fields})

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    print(f"Saved CSV:  {csv_path}")
    print(f"Saved JSON: {json_path}")

def summarize(rows: List[Dict[str, Any]]) -> None:
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(row["model_label"], []).append(row)

    print("\n=== Summary ===")
    for label, items in groups.items():
        avg_latency = sum(i["latency_sec"] for i in items if i["latency_sec"] is not None) / len(items)
        avg_tps = sum(i["tokens_per_sec"] for i in items if i["tokens_per_sec"] is not None) / len(items)
        avg_acc = sum(i["accuracy"] for i in items if i["accuracy"] is not None) / len(items)
        vram_vals = [i["vram_mb"] for i in items if i.get("vram_mb") is not None]
        avg_vram = sum(vram_vals) / len(vram_vals) if vram_vals else None
        print(f"{label}: latency={avg_latency:.4f}s | tokens/sec={avg_tps:.4f} | accuracy={avg_acc:.4f} | vram_mb={avg_vram}")

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--base-model", required=True, help="HF base model path or repo id")
    p.add_argument("--fine-tuned-model", required=False, help="HF base model path used with adapter")
    p.add_argument("--adapter-path", required=False, help="PEFT adapter directory for fine-tuned model")
    p.add_argument("--gguf-model", required=False, help="GGUF model file path")
    p.add_argument("--output-dir", default="benchmarks")
    p.add_argument("--max-new-tokens", type=int, default=96)
    p.add_argument("--skip-streaming", action="store_true")
    p.add_argument("--skip-batch", action="store_true")
    return p.parse_args()

def main() -> None:
    args = parse_args()
    rows: List[Dict[str, Any]] = []

    rows.extend(benchmark_model(
        kind="base",
        label="base_model",
        model_path=args.base_model,
        adapter_path=None,
        prompts=PROMPTS,
        max_new_tokens=args.max_new_tokens,
        run_streaming=not args.skip_streaming,
        run_batch=not args.skip_batch,
    ))

    if args.fine_tuned_model and args.adapter_path:
        rows.extend(benchmark_model(
            kind="fine_tuned",
            label="fine_tuned_model",
            model_path=args.fine_tuned_model,
            adapter_path=args.adapter_path,
            prompts=PROMPTS,
            max_new_tokens=args.max_new_tokens,
            run_streaming=not args.skip_streaming,
            run_batch=not args.skip_batch,
        ))

    if args.gguf_model:
        rows.extend(benchmark_model(
            kind="gguf",
            label="quantized_gguf_model",
            model_path=args.gguf_model,
            adapter_path=None,
            prompts=PROMPTS,
            max_new_tokens=args.max_new_tokens,
            run_streaming=not args.skip_streaming,
            run_batch=not args.skip_batch,
        ))

    out_dir = Path(args.output_dir)
    save_results(rows, out_dir)
    summarize(rows)

if __name__ == "__main__":
    main()
