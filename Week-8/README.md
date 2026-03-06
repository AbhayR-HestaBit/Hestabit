# Week 8: LLM Fine-Tuning & Deployment

## Folder Structure
```text
/
├── adapters/                
├── benchmarks/              
├── data/                    
├── deploy/                  
├── inference/               
├── notebooks/               
├── quantized/               
├── reports/                 
├── screenshots/             
├── utils/                   
├── DAY1.md                  
├── DAY2.md                  
├── DAY3.md                  
├── DAY4.md                  
├── DAY5.md                  
├── DATASET-ANALYSIS.md      
├── TRAINING-REPORT.md       
├── QUANTISATION-REPORT.md   
├── BENCHMARK-REPORT.md      
├── FINAL-REPORT.md          
├── streamlit_app.py         
```

## Task Completed

### Day 1
- Instruction Dataset Design: Built a diverse medical instruction tuning dataset containing three types of samples: QA (500), Reasoning (500), and Extraction (500) for the training set.
- Data Cleaning: Implemented a deduplication and cleaning pipeline in `data_cleaner.py` to ensure high-quality training data.
- Outlier Removal: Performed IQR-based token length analysis to identify and remove outliers, maintaining a consistent training signal.
- Tokenizer Alignment: Used the `TinyLlama` tokenizer to analyze sample lengths and ensure they fit within the model's context window.

### Day 2
- QLoRA Integration: Configured 4-bit quantization using `bitsandbytes` to fine-tune the 1.1B model on consumer-grade hardware (T4 GPU).
- LoRA Configuration: Set rank $r=16$ and $\alpha=32$, targeting all linear modules (q_proj, v_proj, etc.) for optimal performance.
- Training Pipeline: Managed the full training loop using `SFTTrainer` from the `trl` library, achieving a significant loss reduction over 3 epochs.
- Parameter Efficiency: Successfully restricted trainable parameters to ~2% of the total model size, drastically reducing memory overhead.

### Day 3
- Bit-depth Reduction: Converted the fine-tuned FP16 model into INT8 and INT4 formats using HF `bitsandbytes`, achieving up to 4x memory savings.
- Format Conversion: Used the `llama.cpp` conversion scripts to merge LoRA adapters and output a standalone `.gguf` file.
- GGUF Optimization: Targeted the `q4_0` quantization scheme for the best balance between model size and perplexity on CPU-based inference.
- Verification: Validated that the quantized formats remained functional and retained the medical knowledge learned during fine-tuning.

### Day 4
- Comparative Analysis: Benchmarked the Base Model, Fine-tuned Model (LoRA), and Quantized GGUF model across multiple medical prompts.
- Metric Tracking: Measured Tokens per Second (TPS), VRAM allocation, Latency (TTFT), and keyword-based accuracy.
- Inference Features: Implemented streaming output mode, batch processing, and speculative decoding tests in `test_inference.py`.
- System Profiling: Analyzed the trade-offs between quantized INT4 speed on CPU vs. FP16 performance on GPU.

### Day 5
- FastAPI Microservice: Developed a production-ready API with `/generate` and `/chat` endpoints supporting system prompts and session history.
- Model Caching: Implemented a singleton loader to prevent reloading the 1.1B model on every request, ensuring sub-second response times.
- Streamlit Frontend: Created a stunning user interface for real-time interaction with the fine-tuned medical assistant (managed via `streamlit_app.py`).
- Production Thinking: Added request ID tracking, session persistence, and error handling for robust local deployment.
