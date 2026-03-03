# Day 4: Inference Optimisation And Benchmarking

## Folder Structure
```text
/benchmarks
├── results.csv             
└── results.json            
/inference
└── test_inference.py       
```

## Tasks Completed
- Comparative Analysis: Benchmarked the Base Model, Fine-tuned Model (LoRA), and Quantized GGUF model across multiple medical prompts.
- Metric Tracking: Measured Tokens per Second (TPS), VRAM allocation, Latency (TTFT), and keyword-based accuracy.
- Inference Features: Implemented streaming output mode, batch processing, and speculative decoding tests in `test_inference.py`.
- System Profiling: Analyzed the trade-offs between quantized INT4 speed on CPU vs. FP16 performance on GPU.

## Code Snippet (Benchmarking Logic)
```python
def benchmark_model(kind, label, model_path, adapter_path, prompts):
    runner = build_runner(kind=kind, model_path=model_path, adapter_path=adapter_path)
    for item in prompts:
        prompt = build_prompt(item)
        res = runner.generate_one(prompt)
        res.update({
            "model_label": label,
            "tokens_per_sec": round(res["generated_tokens"] / res["latency_sec"], 2),
            "accuracy": keyword_accuracy(res["output_text"], item["expected_keywords"])
        })
        results.append(res)
    return results
```

## Screenshots
![Inference Benchmarking Output](screenshots/infrence.png)
