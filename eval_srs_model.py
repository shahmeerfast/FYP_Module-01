#!/usr/bin/env python3
"""
Evaluation for SRSModelGenerator outputs against reference SRS sections.

Usage:
  python eval_srs_model.py --data dataset.jsonl --limit 50

Dataset format (JSONL or JSON list):
  {
    "requirements": [ {"original_text": "..."}, ... ],
    "reference_sections": {
        "introduction": {"purpose": "...", "scope": "...", "overview": "...", "definitions": [...]},
        "overall_description": {"product_functions": [...], "constraints": [...]} \
        // additional keys are ignored by metrics if not used
    },
    "project_info": {"title": "...", "author": "...", "version": "..."} // optional
  }
"""

import argparse
import json
import logging
import os
import re
from typing import Any, Dict, List, Tuple

from rouge_score import rouge_scorer
from bert_score import score as bert_score
from rapidfuzz import fuzz

from srs_model_generator import SRSModelGenerator


def normalize_item(text: str) -> str:
    text = text or ""
    text = re.sub(r'^\d+[\.\)]\s*|^[-•*]\s*', '', text.strip().lower())
    text = re.sub(r'\s+', ' ', text)
    return text


def list_prf1(pred_items: List[str], ref_items: List[str], sim_cutoff: int = 90) -> Dict[str, float]:
    pred = [normalize_item(x) for x in (pred_items or []) if x]
    ref = [normalize_item(x) for x in (ref_items or []) if x]
    matched_ref = set()
    true_positive = 0
    for p in pred:
        best_idx, best_sim = -1, 0
        for i, r in enumerate(ref):
            sim = fuzz.token_set_ratio(p, r)
            if sim > best_sim:
                best_sim = sim
                best_idx = i
        if best_sim >= sim_cutoff and best_idx not in matched_ref:
            true_positive += 1
            matched_ref.add(best_idx)
    false_positive = max(len(pred) - true_positive, 0)
    false_negative = max(len(ref) - true_positive, 0)
    precision = true_positive / (true_positive + false_positive) if (true_positive + false_positive) else 0.0
    recall = true_positive / (true_positive + false_negative) if (true_positive + false_negative) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    jaccard = true_positive / (true_positive + false_positive + false_negative) if (true_positive + false_positive + false_negative) else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, "jaccard": jaccard}


def text_metrics(pred: str, ref: str) -> Dict[str, float]:
    pred = pred or ""
    ref = ref or ""
    rouge = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeLsum'], use_stemmer=True).score(ref, pred)
    _, _, bert_f1 = bert_score([pred], [ref], lang='en')
    return {
        "rouge1": float(rouge['rouge1'].fmeasure),
        "rouge2": float(rouge['rouge2'].fmeasure),
        "rougeL": float(rouge['rougeLsum'].fmeasure),
        "bert_f1": float(bert_f1[0]),
    }


def completeness(sections: Dict[str, Any], required_keys: Tuple[str, ...] = (
    'introduction.purpose',
    'introduction.scope',
    'overall_description.product_functions',
)) -> float:
    def get_path(d: Dict[str, Any], path: str) -> Any:
        cur: Any = d
        for k in path.split('.'):
            if not isinstance(cur, dict):
                return None
            cur = cur.get(k)
        return cur

    present = 0
    for key in required_keys:
        value = get_path(sections or {}, key)
        ok = False
        if isinstance(value, str):
            ok = len(value.strip()) > 0
        elif isinstance(value, list):
            ok = len(value) > 0
        present += 1 if ok else 0
    return present / len(required_keys) if required_keys else 1.0


def evaluate_example(generator: SRSModelGenerator, example: Dict[str, Any]) -> Dict[str, Any]:
    requirements = example.get('requirements') or []
    ref_sections = example.get('reference_sections') or {}
    project_info = example.get('project_info') or None
    pred_doc = generator.generate_srs(requirements, project_info)
    pred_sections = pred_doc.sections

    # Free-text metrics
    text_pairs = [
        ('introduction.purpose', pred_sections.get('introduction', {}).get('purpose', ''), ref_sections.get('introduction', {}).get('purpose', '')),
        ('introduction.scope', pred_sections.get('introduction', {}).get('scope', ''), ref_sections.get('introduction', {}).get('scope', '')),
        ('introduction.overview', pred_sections.get('introduction', {}).get('overview', ''), ref_sections.get('introduction', {}).get('overview', '')),
        ('overall_description.product_perspective', pred_sections.get('overall_description', {}).get('product_perspective', ''), ref_sections.get('overall_description', {}).get('product_perspective', '')),
    ]
    text_scores = {name: text_metrics(pred, ref) for name, pred, ref in text_pairs}

    # List metrics
    list_pairs = [
        ('overall_description.product_functions', pred_sections.get('overall_description', {}).get('product_functions', []), ref_sections.get('overall_description', {}).get('product_functions', [])),
        ('overall_description.constraints', pred_sections.get('overall_description', {}).get('constraints', []), ref_sections.get('overall_description', {}).get('constraints', [])),
        ('introduction.definitions', pred_sections.get('introduction', {}).get('definitions', []), ref_sections.get('introduction', {}).get('definitions', [])),
    ]
    list_scores = {name: list_prf1(pred, ref) for name, pred, ref in list_pairs}

    # Completeness
    comp = completeness(pred_sections)

    return {
        "text": text_scores,
        "lists": list_scores,
        "completeness": comp,
    }


def average_scores(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    def avg(values: List[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    text_keys = {}
    list_keys = {}
    completeness_vals = []

    for r in results:
        completeness_vals.append(r.get('completeness', 0.0))
        for name, metrics in r.get('text', {}).items():
            for k, v in metrics.items():
                text_keys.setdefault((name, k), []).append(float(v))
        for name, metrics in r.get('lists', {}).items():
            for k, v in metrics.items():
                list_keys.setdefault((name, k), []).append(float(v))

    text_avg: Dict[str, Dict[str, float]] = {}
    for (name, k), vals in text_keys.items():
        text_avg.setdefault(name, {})[k] = avg(vals)

    list_avg: Dict[str, Dict[str, float]] = {}
    for (name, k), vals in list_keys.items():
        list_avg.setdefault(name, {})[k] = avg(vals)

    return {
        "text": text_avg,
        "lists": list_avg,
        "completeness": avg(completeness_vals),
    }


def iter_dataset(path: str) -> List[Dict[str, Any]]:
    # Use utf-8-sig to transparently handle UTF-8 BOM
    with open(path, 'r', encoding='utf-8-sig') as f:
        content = f.read().strip()
    if content.startswith('['):
        # JSON list
        return json.loads(content)
    # JSONL
    items: List[Dict[str, Any]] = []
    for i, raw_line in enumerate(content.splitlines(), start=1):
        # Remove any stray BOMs per line and whitespace
        line = (raw_line or '').replace('\ufeff', '').strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except json.JSONDecodeError as e:
            snippet = line[:200]
            raise ValueError(f"Invalid JSONL at line {i}: {e.msg} (pos {e.pos}). Snippet: {snippet}") from e
    return items


def main():
    parser = argparse.ArgumentParser(description="Evaluate SRSModelGenerator against references")
    parser.add_argument('--data', required=True, help='Path to JSONL or JSON dataset')
    parser.add_argument('--limit', type=int, default=0, help='Limit number of examples (0=all)')
    parser.add_argument('--model', type=str, default=None, help='Override model name (e.g., google/flan-t5-base)')
    parser.add_argument('--output', type=str, default=None, help='Optional path to save detailed results JSON')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    from srs_model_generator import ModelConfig
    config = ModelConfig()
    if args.model:
        config.flan_model_name = args.model
    generator = SRSModelGenerator(config)

    dataset = iter_dataset(args.data)
    if args.limit and args.limit > 0:
        dataset = dataset[:args.limit]

    results: List[Dict[str, Any]] = []
    for idx, ex in enumerate(dataset):
        logging.info("Evaluating item %d/%d", idx + 1, len(dataset))
        results.append(evaluate_example(generator, ex))

    summary = average_scores(results)

    print("\n=== Evaluation Summary ===")
    print(json.dumps(summary, indent=2))

    if args.output:
        payload = {"summary": summary, "details": results}
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print(f"Saved details to {args.output}")


if __name__ == '__main__':
    main()




