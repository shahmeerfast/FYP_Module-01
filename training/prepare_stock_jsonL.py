#!/usr/bin/env python3
"""
Prepare pseudo-labeled JSONL dataset from data/input/stock.txt for Flan-T5 fine-tuning.

Steps:
- Read data/input/stock.txt
- Chunk into paragraphs/sections
- Use existing Flan-T5 extractor to generate structured targets
- Write JSONL with fields: {"input": <prompted text>, "target": <extracted fields text>}

Outputs:
- data/input/datasets/stock/train.jsonl
"""

import os
import json
from pathlib import Path
from typing import List

import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration


def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def simple_paragraph_chunks(text: str) -> List[str]:
    # Split on blank lines; keep reasonably sized chunks
    raw_paras = [p.strip() for p in text.split("\n\n")]
    paras = [p for p in raw_paras if len(p.split()) >= 20]
    merged: List[str] = []
    buf = []
    word_limit = 180
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
        "1. Purpose\n"
        "2. Scope\n"
        "3. Product Functions\n"
        "4. Constraints\n"
        "5. Stakeholders\n\n"
        "Format your response as:\n"
        "Purpose: ...\n"
        "Scope: ...\n"
        "Product Functions: ...\n"
        "Constraints: ...\n"
        "Stakeholders: ...\n"
    )


def run_extractor(tokenizer: T5Tokenizer, model: T5ForConditionalGeneration, prompt: str) -> str:
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
    source_path = Path("data/input/stock.txt")
    out_dir = Path("data/input/datasets/stock")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "train.jsonl"

    if not source_path.exists():
        raise FileNotFoundError(f"Missing {source_path}")

    print("Loading base Flan-T5 model (google/flan-t5-base)...")
    tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
    model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")

    print("Reading and chunking source text...")
    text = read_text_file(str(source_path))
    chunks = simple_paragraph_chunks(text)
    if not chunks:
        raise RuntimeError("No sufficiently long chunks found in stock.txt")
    print(f"Prepared {len(chunks)} chunks")

    print("Generating pseudo-labels with the base model...")
    num_written = 0
    with open(out_path, "w", encoding="utf-8") as out_f:
        for idx, chunk in enumerate(chunks):
            prompt = build_prompt(chunk)
            target = run_extractor(tokenizer, model, prompt)
            record = {"input": prompt, "target": target}
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
            num_written += 1
            if (idx + 1) % 5 == 0:
                print(f".. {idx + 1}/{len(chunks)}")

    print(f"Wrote {num_written} examples to {out_path}")


if __name__ == "__main__":
    main()



