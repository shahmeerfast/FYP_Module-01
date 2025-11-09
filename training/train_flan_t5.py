#!/usr/bin/env python3
"""
Generic Flan-T5 trainer for our JSONL format.

Usage examples:
  # Train from base
  python training/train_flan_t5.py --data data/input/datasets/all_texts/train.jsonl \
    --base_model google/flan-t5-base --out_dir data/output/models/finetuned-flan-all

  # Continue from existing finetuned model (domain-adapt further)
  python training/train_flan_t5.py --data data/input/datasets/more/train.jsonl \
    --resume_from data/output/models/finetuned-flan-t5-stock --out_dir data/output/models/finetuned-flan-continued
"""

import json
from pathlib import Path
from typing import Dict, List
import argparse

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
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Path to train.jsonl")
    parser.add_argument("--out_dir", required=True, help="Output model directory")
    parser.add_argument("--base_model", default="google/flan-t5-base", help="Base model name if not resuming")
    parser.add_argument("--resume_from", default="", help="Existing model dir to start from (optional)")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch_size", type=int, default=1)
    parser.add_argument("--grad_accum", type=int, default=8)
    parser.add_argument("--lr", type=float, default=5e-5)
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        raise FileNotFoundError(f"Missing {data_path}")
    out_dir = Path(args.out_dir)
    out_dir.parent.mkdir(parents=True, exist_ok=True)
    out_logs = Path("data/output/experiments/custom")
    out_logs.mkdir(parents=True, exist_ok=True)

    model_source = args.resume_from if args.resume_from else args.base_model
    print(f"Loading tokenizer and model from: {model_source}")
    tokenizer = T5Tokenizer.from_pretrained(model_source)
    model = T5ForConditionalGeneration.from_pretrained(model_source)

    print("Loading dataset...")
    dataset = JsonlSeq2SeqDataset(str(data_path), tokenizer)
    if len(dataset) == 0:
        raise RuntimeError("Empty dataset.")

    training_args = TrainingArguments(
        output_dir=str(out_logs),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
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

    print(f"Saving model to {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(out_dir))
    tokenizer.save_pretrained(str(out_dir))
    print("Done.")


if __name__ == "__main__":
    main()








