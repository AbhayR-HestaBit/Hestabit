# Day 3: Quantisation (8-bit to 4-bit to GGUF)

For checking for models kindly go to this link: https://drive.google.com/drive/folders/1SylEVdlBRL4IVkiVSGnDfZJkdtm47HeY?usp=drive_link

## Folder Structure
```text
/quantized
├── model-int8/             
├── model-int4/             
└── model.gguf               
/reports
└── QUANTIZATION-NOTES.md    
```

## Tasks Completed
- Bit-depth Reduction: Converted the fine-tuned FP16 model into INT8 and INT4 formats using HF `bitsandbytes`, achieving up to 4x memory savings.
- Format Conversion: Used the `llama.cpp` conversion scripts to merge LoRA adapters and output a standalone `.gguf` file.
- GGUF Optimization: Targeted the `q4_0` quantization scheme for the best balance between model size and perplexity on CPU-based inference.
- Verification: Validated that the quantized formats remained functional and retained the medical knowledge learned during fine-tuning.

## Code Snippet (GGUF Conversion)
```bash
# Merging LoRA and converting to GGUF
python3 llama.cpp/convert_hf_to_gguf.py models/merged_fp16 \
    --outfile quantized/model.gguf \
    --outtype q4_0
```

## Screenshots
![Format Comparison](screenshots/compare.png)
![Quantized Model Files](screenshots/model.png)
