# Dataset Analysis Report

## Files Involved
- `data/train.jsonl`: Primary training dataset (1500 samples).
- `data/val.jsonl`: Validation dataset (600 samples).
- `utils/data_cleaner.py`: Cleaning, deduplication, and outlier removal script.

## Commands Run
To clean the raw medical data and generate the instruction-tuning datasets:
```bash
python3 utils/data_cleaner.py \
    --qa-path data/raw/qa_data.json \
    --extraction-path data/raw/extraction_data.json \
    --reasoning-json-path data/raw/reasoning.json \
    --output-dir data/processed
```

## Dataset Composition
- **QA Pairs**: 500 train / 200 val.
- **Reasoning (CoT)**: 500 train / 200 val.
- **Entity Extraction**: 500 train / 200 val.

## Analysis Code Snippet (IQR Logic)
```python
def remove_length_outliers(rows, tokenizer):
    lengths = [len(tokenizer.encode(f"{r['instruction']} {r['input']} {r['output']}")) for r in rows]
    q1, q3 = sorted(lengths)[len(lengths)//4], sorted(lengths)[3*len(lengths)//4]
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return [r for r, l in zip(rows, lengths) if lower <= l <= upper]
```

