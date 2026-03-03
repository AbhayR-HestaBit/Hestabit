# Benchmark Report

This report presents performance metrics for various model versions.

## Files Involved
- `benchmarks/results.csv`: Table of latency and throughput benchmarks.
- `inference/test_inference.py`: Automated performance testing script.

## Commands Run
To execute the benchmark suite across all model types:
```bash
python3 inference/test_inference.py \
    --base-model TinyLlama/TinyLlama-1.1B-Chat-v1.0 \
    --fine-tuned-model TinyLlama/TinyLlama-1.1B-Chat-v1.0 \
    --adapter-path adapters/ \
    --gguf-model quantized/model.gguf
```

## Key Metrics Measured
- **TPS**: Tokens per Second (Throughput).
- **TTFT**: Time to First Token (Latency).
- **VRAM**: Peak GPU memory allocation.
- **Accuracy**: Keyword-based response evaluation.

## Performance Code Snippet
```python
start = time.perf_counter()
output = llm.generate(**inputs, max_new_tokens=96)
latency = time.perf_counter() - start
tokens_generated = output.shape[-1] - inputs["input_ids"].shape[-1]
tps = tokens_generated / latency
```


