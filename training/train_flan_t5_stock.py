#!/usr/bin/env python3
"""
Fine-tune Flan-T5 on pseudo-labeled stock dataset.

Inputs:
- data/input/datasets/stock/train.jsonl (fields: input, target)

Outputs:
- data/output/models/finetuned-flan-t5-stock/
- data/output/experiments/stock/ (logs, metrics)
"""

import os
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List

import torch
from transformers import (
    T5Tokenizer,
    T5ForConditionalGeneration,
    Trainer,
    TrainingArguments,
)
from torch.utils.data import Dataset


class JsonlSeq2SeqDataset(Dataset):
    def __init__(self, jsonl_path: str, tokenizer: T5Tokenizer, source_max_len: int = 1024, target_max_len: int = 512):
        self.records: List[Dict[str, str]] = []
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                if "input" in obj and "target" in obj:
                    self.records.append({"input": obj["input"], "target": obj["target"]})
        self.tokenizer = tokenizer
        self.source_max_len = source_max_len
        self.target_max_len = target_max_len

    def __len__(self):
        return len(self.records)

    def __getitem__(self, idx: int):
        item = self.records[idx]
        source_enc = self.tokenizer(
            item["input"],
            max_length=self.source_max_len,
            truncation=True,
            padding="max_length",
            return_tensors="pt",
        )
        target_enc = self.tokenizer(
            item["target"],
            max_length=self.target_max_len,
            truncation=True,
            padding="max_length",
            return_tensors="pt",
        )
        labels = target_enc.input_ids.squeeze(0)
        labels[labels == self.tokenizer.pad_token_id] = -100
        return {
            "input_ids": source_enc.input_ids.squeeze(0),
            "attention_mask": source_enc.attention_mask.squeeze(0),
            "labels": labels,
        }


def main():
    data_path = Path("data/input/datasets/stock/train.jsonl")
    if not data_path.exists():
        raise FileNotFoundError("Missing data/input/datasets/stock/train.jsonl. Run prepare_stock_jsonL.py first.")

    out_models = Path("data/output/models/finetuned-flan-t5-stock")
    out_logs = Path("data/output/experiments/stock")
    out_models.mkdir(parents=True, exist_ok=True)
    out_logs.mkdir(parents=True, exist_ok=True)

    model_name = "google/flan-t5-base"
    print(f"Loading tokenizer and model: {model_name}")
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)

    print("Loading dataset...")
    dataset = JsonlSeq2SeqDataset(str(data_path), tokenizer)
    if len(dataset) == 0:
        raise RuntimeError("Empty dataset.")

    # Very small defaults; adjust per GPU/memory
    training_args = TrainingArguments(
        output_dir=str(out_logs),
        num_train_epochs=3,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        learning_rate=5e-5,
        weight_decay=0.01,
        logging_steps=10,
        save_steps=200,
        save_total_limit=2,
        fp16=torch.cuda.is_available(),
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        tokenizer=tokenizer,
    )

    print("Starting training...")
    trainer.train()

    print(f"Saving model to {out_models}")
    trainer.save_model(str(out_models))
    tokenizer.save_pretrained(str(out_models))
    print("Done.")


if __name__ == "__main__":
    main()


