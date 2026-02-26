# Training Report

## Files Involved
- `notebooks/lora_train.ipynb`: Jupyter notebook for the training pipeline.
- `adapters/adapter_model.bin`: Saved LoRA weights.
- `adapters/adapter_config.json`: Metadata for the PEFT configuration.

## Commands Run
Environment setup and dependencies:
```bash
pip install torch transformers peft trl bitsandbytes accelerate
```

## Hyperparameters
- **Rank (r)**: 16
- **Alpha**: 32
- **Dropout**: 0.05
- **Optimizer**: AdamW (8-bit)
- **Batch Size**: 4
- **Precision**: 4-bit (NF4)

## LoRA Implementation Snippet
```python
peft_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)
model = get_peft_model(model, peft_config)
model.print_trainable_parameters()
```

