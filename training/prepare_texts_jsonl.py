#!/usr/bin/env python3
"""
Prepare pseudo-labeled JSONL dataset from multiple text files for Flan-T5 fine-tuning.

Usage examples:
  python training/prepare_texts_jsonl.py --inputs "data/input/*.txt" --out_dir data/input/datasets/all_texts \
    --base_model google/flan-t5-base

Outputs:
  - <out_dir>/train.jsonl
  - Optional: <out_dir>/val.jsonl (if --val_ratio > 0)
"""

import os
import json
import glob
import random
from pathlib import Path
from typing import List

import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def simple_paragraph_chunks(text: str, word_limit: int = 180) -> List[str]:
    raw = [p.strip() for p in text.split("\n\n")]
    paras = [p for p in raw if len(p.split()) >= 20]
    merged: List[str] = []
    buf: List[str] = []
    for p in paras:
        if len(" ".join(buf + [p]).split()) > word_limit and buf:
            merged.append("\n".join(buf))
            buf = [p]
        else:
            buf.append(p)
    if buf:
        merged.append("\n".join(buf))
    return merged


def build_prompt(chunk: str) -> str:
    return (
        "Extract the following requirements fields from this text:\n\n"
        f"Text: {chunk}\n\n"
        "Please extract and format the following fields:\n"
        "1. Purpose\n2. Scope\n3. Product Functions\n4. Constraints\n5. Stakeholders\n\n"
        "Format your response as:\n"
        "Purpose: ...\nScope: ...\nProduct Functions: ...\nConstraints: ...\nStakeholders: ...\n"
    )


def generate_target(tokenizer: T5Tokenizer, model: T5ForConditionalGeneration, prompt: str) -> str:
    inputs = tokenizer.encode(prompt, return_tensors="pt", max_length=1024, truncation=True)
    with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_length=512,
            num_beams=4,
            early_stopping=True,
            temperature=0.7,
            do_sample=True,
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", required=True, help="Glob of input text files, e.g., data/input/*.txt")
    parser.add_argument("--out_dir", required=True, help="Output directory for JSONL files")
    parser.add_argument("--base_model", default="google/flan-t5-base", help="Base model for pseudo-labeling")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--val_ratio", type=float, default=0.0, help="0..0.5 to create val split")
    args = parser.parse_args()

    random.seed(args.seed)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(glob.glob(args.inputs))
    if not files:
        raise FileNotFoundError(f"No files matched: {args.inputs}")
    print(f"Found {len(files)} input files")

    print(f"Loading base model: {args.base_model}")
    tokenizer = T5Tokenizer.from_pretrained(args.base_model)
    model = T5ForConditionalGeneration.from_pretrained(args.base_model)

    examples: List[dict] = []
    for fi, file_path in enumerate(files):
        text = read_text(file_path)
        chunks = simple_paragraph_chunks(text)
        print(f"[{fi+1}/{len(files)}] {os.path.basename(file_path)} -> {len(chunks)} chunks")
        for chunk in chunks:
            prompt = build_prompt(chunk)
            target = generate_target(tokenizer, model, prompt)
            examples.append({"input": prompt, "target": target})

    # Train/val split
    random.shuffle(examples)
    if args.val_ratio > 0:
        n_val = max(1, int(len(examples) * args.val_ratio))
        val = examples[:n_val]
        train = examples[n_val:]
        with open(out_dir / "val.jsonl", "w", encoding="utf-8") as vf:
            for r in val:
                vf.write(json.dumps(r, ensure_ascii=False) + "\n")
    else:
        train = examples

    with open(out_dir / "train.jsonl", "w", encoding="utf-8") as tf:
        for r in train:
            tf.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Wrote train={len(train)} to {out_dir/'train.jsonl'}" + (f", val={len(examples)-len(train)}" if args.val_ratio>0 else ""))


if __name__ == "__main__":
    main()








