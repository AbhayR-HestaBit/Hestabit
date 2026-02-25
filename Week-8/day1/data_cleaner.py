

from __future__ import annotations

import argparse
import json
import random
import statistics
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from datasets import load_dataset
except ImportError:
    load_dataset = None
    logger.warning("datasets library not installed. HF reasoning will be unavailable.")

try:
    from transformers import AutoTokenizer
except ImportError:
    AutoTokenizer = None
    logger.warning("transformers library not installed. Token length analysis will use split().")


TARGETS = {
    "qa": {"train": 500, "val": 200},
    "reasoning": {"train": 500, "val": 200},
    "extraction": {"train": 500, "val": 200},
}


DEFAULT_REASONING_INSTRUCTION = (
    "Solve the medical reasoning problem carefully and provide the final answer clearly."
)


def read_json(path: Path) -> list[dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to read JSON from {path}: {e}")
        return []


def save_jsonl(rows: list[dict[str, str]], path: Path) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.error(f"Failed to save JSONL to {path}: {e}")


def dedupe_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    seen = set()
    cleaned = []
    for row in rows:
        key = (
            row["instruction"].strip(),
            row["input"].strip(),
            row["output"].strip(),
            row["category"].strip(),
        )
        if key not in seen:
            seen.add(key)
            cleaned.append(row)
    return cleaned


def build_qa_rows(items: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows = []
    for item in items:
        instruction = item.get("instruction", "").strip() or "Answer the medical question accurately."
        input_text = item.get("input", "").strip()
        output_text = item.get("output", "").strip()
        if input_text and output_text:
            rows.append(
                {
                    "instruction": instruction,
                    "input": input_text,
                    "output": output_text,
                    "category": "qa",
                    "source": "medical_meadow_wikidoc_medical_flashcards",
                }
            )
    return dedupe_rows(rows)


def build_extraction_rows(items: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows = []
    fixed_instruction = (
        "Extract the required medical entities from the text. Return only valid JSON."
    )
    for item in items:
        input_text = item.get("input", "").strip()
        output_text = item.get("output", "").strip()
        if input_text and output_text:
            rows.append(
                {
                    "instruction": fixed_instruction,
                    "input": input_text,
                    "output": output_text,
                    "category": "extraction",
                    "source": "entity-extraction-data",
                }
            )
    return dedupe_rows(rows)


def _reasoning_row(question: str, cot: str, response: str, source: str) -> dict[str, str] | None:
    question = str(question).strip()
    cot = str(cot).strip()
    response = str(response).strip()
    if not question or not response:
        return None

    input_text = f"Question: {question}"
    if cot:
        input_text += f"\n\nReasoning reference:\n{cot}"

    return {
        "instruction": DEFAULT_REASONING_INSTRUCTION,
        "input": input_text,
        "output": response,
        "category": "reasoning",
        "source": source,
    }


def build_reasoning_rows_from_local_json(path: Path) -> list[dict[str, str]]:
    items = read_json(path)
    rows: list[dict[str, str]] = []
    for item in items:
        row = _reasoning_row(
            item.get("Question", ""),
            item.get("Complex_CoT", ""),
            item.get("Response", ""),
            source=path.name,
        )
        if row is not None:
            rows.append(row)
    return dedupe_rows(rows)


def build_reasoning_rows_from_hf(hf_dataset: str, hf_subset: str) -> list[dict[str, str]]:
    if load_dataset is None:
        raise ImportError("datasets is not installed. Use: pip install datasets")

    dataset = load_dataset(hf_dataset, hf_subset, split="train")
    rows: list[dict[str, str]] = []
    for item in dataset:
        row = _reasoning_row(
            item.get("Question", ""),
            item.get("Complex_CoT", ""),
            item.get("Response", ""),
            source=f"{hf_dataset}:{hf_subset}",
        )
        if row is not None:
            rows.append(row)
    return dedupe_rows(rows)


def build_reasoning_rows(
    reasoning_json_path: Path | None,
    use_hf_reasoning: bool,
    hf_dataset: str,
    hf_subset: str,
) -> tuple[list[dict[str, str]], dict[str, int]]:
    all_rows: list[dict[str, str]] = []
    source_counts = {"local_reasoning": 0, "hf_reasoning": 0}

    if reasoning_json_path is not None:
        local_rows = build_reasoning_rows_from_local_json(reasoning_json_path)
        all_rows.extend(local_rows)
        source_counts["local_reasoning"] = len(local_rows)

    if use_hf_reasoning:
        hf_rows = build_reasoning_rows_from_hf(hf_dataset, hf_subset)
        all_rows.extend(hf_rows)
        source_counts["hf_reasoning"] = len(hf_rows)

    deduped = dedupe_rows(all_rows)
    return deduped, source_counts


def build_token_lengths(rows: list[dict[str, str]], tokenizer_name: str | None) -> list[int]:
    texts = [f"{r['instruction']}\n\n{r['input']}\n\n{r['output']}" for r in rows]

    if tokenizer_name and AutoTokenizer is not None:
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, use_fast=True)
        return [len(tokenizer.encode(text, add_special_tokens=True)) for text in texts]

    return [len(text.split()) for text in texts]


def iqr_bounds(values: list[int]) -> tuple[float, float]:
    ordered = sorted(values)
    if len(ordered) < 4:
        return float(min(ordered)), float(max(ordered))
    q1 = ordered[len(ordered) // 4]
    q3 = ordered[(3 * len(ordered)) // 4]
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr


def remove_length_outliers(
    rows: list[dict[str, str]], tokenizer_name: str | None
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    lengths = build_token_lengths(rows, tokenizer_name)
    low, high = iqr_bounds(lengths)
    kept, removed = [], []
    for row, length in zip(rows, lengths):
        if low <= length <= high:
            kept.append(row)
        else:
            removed.append(row)
    return kept, removed


def exact_split(
    rows: list[dict[str, str]], train_count: int, val_count: int, seed: int
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    required = train_count + val_count
    if len(rows) < required:
        raise ValueError(f"Need {required} rows but only found {len(rows)} usable rows.")
    shuffled = rows[:]
    random.Random(seed).shuffle(shuffled)
    selected = shuffled[:required]
    return selected[:train_count], selected[train_count:required]


def strip_metadata(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "instruction": row["instruction"],
            "input": row["input"],
            "output": row["output"],
        }
        for row in rows
    ]


def summarize(lengths: list[int]) -> dict[str, float]:
    ordered = sorted(lengths)
    return {
        "count": len(lengths),
        "min": ordered[0],
        "median": statistics.median(lengths),
        "max": ordered[-1],
        "mean": round(statistics.mean(lengths), 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qa-path", type=Path, required=True)
    parser.add_argument("--extraction-path", type=Path, required=True)
    parser.add_argument("--reasoning-json-path", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=Path("./week8_day1_output"))
    parser.add_argument(
        "--hf-dataset",
        type=str,
        default="FreedomIntelligence/medical-o1-reasoning-SFT",
    )
    parser.add_argument("--hf-subset", type=str, default="en")
    parser.add_argument(
        "--use-hf-reasoning",
        action="store_true",
        help="Include the Hugging Face reasoning dataset along with any local reasoning JSON file.",
    )
    parser.add_argument(
        "--tokenizer",
        type=str,
        default="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if args.reasoning_json_path is None and not args.use_hf_reasoning:
        raise ValueError(
            "Provide --reasoning-json-path or add --use-hf-reasoning so reasoning data is available."
        )

    output_dir = args.output_dir
    data_dir = output_dir / "data"
    analysis_dir = output_dir / "analysis"
    data_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    qa_rows = build_qa_rows(read_json(args.qa_path))
    extraction_rows = build_extraction_rows(read_json(args.extraction_path))
    reasoning_rows, reasoning_source_counts = build_reasoning_rows(
        reasoning_json_path=args.reasoning_json_path,
        use_hf_reasoning=args.use_hf_reasoning,
        hf_dataset=args.hf_dataset,
        hf_subset=args.hf_subset,
    )

    qa_clean, qa_removed = remove_length_outliers(qa_rows, args.tokenizer)
    reasoning_clean, reasoning_removed = remove_length_outliers(reasoning_rows, args.tokenizer)
    extraction_clean, extraction_removed = remove_length_outliers(extraction_rows, args.tokenizer)

    qa_train, qa_val = exact_split(qa_clean, TARGETS["qa"]["train"], TARGETS["qa"]["val"], args.seed)
    reasoning_train, reasoning_val = exact_split(
        reasoning_clean,
        TARGETS["reasoning"]["train"],
        TARGETS["reasoning"]["val"],
        args.seed + 1,
    )
    extraction_train, extraction_val = exact_split(
        extraction_clean,
        TARGETS["extraction"]["train"],
        TARGETS["extraction"]["val"],
        args.seed + 2,
    )

    train_rows = qa_train + reasoning_train + extraction_train
    val_rows = qa_val + reasoning_val + extraction_val
    random.Random(args.seed).shuffle(train_rows)
    random.Random(args.seed + 99).shuffle(val_rows)

    save_jsonl(strip_metadata(train_rows), data_dir / "train.jsonl")
    save_jsonl(strip_metadata(val_rows), data_dir / "val.jsonl")

    summary = {
        "targets": TARGETS,
        "reasoning_sources_used": {
            "reasoning_json_path": str(args.reasoning_json_path) if args.reasoning_json_path else None,
            "use_hf_reasoning": args.use_hf_reasoning,
            "hf_dataset": args.hf_dataset if args.use_hf_reasoning else None,
            "hf_subset": args.hf_subset if args.use_hf_reasoning else None,
        },
        "reasoning_source_counts_before_combined_dedup": reasoning_source_counts,
        "raw_counts": {
            "qa": len(qa_rows),
            "reasoning": len(reasoning_rows),
            "extraction": len(extraction_rows),
        },
        "clean_counts": {
            "qa": len(qa_clean),
            "reasoning": len(reasoning_clean),
            "extraction": len(extraction_clean),
        },
        "removed_outliers": {
            "qa": len(qa_removed),
            "reasoning": len(reasoning_removed),
            "extraction": len(extraction_removed),
        },
        "final_counts": {
            "train_total": len(train_rows),
            "val_total": len(val_rows),
            "train_breakdown": {"qa": 500, "reasoning": 500, "extraction": 500},
            "val_breakdown": {"qa": 200, "reasoning": 200, "extraction": 200},
        },
        "train_length_summary": summarize(build_token_lengths(train_rows, args.tokenizer)),
        "val_length_summary": summarize(build_token_lengths(val_rows, args.tokenizer)),
    }

    with (analysis_dir / "cleaning_summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved train set to: {data_dir / 'train.jsonl'}")
    logger.info(f"Saved val set to: {data_dir / 'val.jsonl'}")
    logger.info(f"Saved cleaning summary to: {analysis_dir / 'cleaning_summary.json'}")


if __name__ == "__main__":
    main()
