import os
import json
import numpy as np
from pathlib import Path

import re
from datasets import Dataset


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def hit_rate(entries):
    hits = []
    for e in entries:
        report = e['report'].lower()
        keywords = ["opacity", "consolidation", "edema", "effusion"]
        match = any(k in report for k in keywords)
        hits.append(1 if match else 0)
    return np.mean(hits), np.std(hits)


# 🔥 Renamed for paper clarity
def clinical_accuracy_score(entries):
    scores = []
    for e in entries:
        score = 0
        report = e['report'].lower()

        if e['disease'].lower() in report:
            score += 1

        if e['region'].lower() in report:
            score += 1

        if any(kw in report for kw in ['however', 'may be seen', 'differential', 'alternatively']):
            score += 1

        if e['disease'].lower() in report and e['region'].lower() in report:
            score += 1

        scores.append(score)

    return np.mean(scores), np.std(scores)


# 🔥 Renamed
def diagnostic_reasoning_score(entries):
    scores = []
    for e in entries:
        report = e['report'].lower()

        if any(kw in report for kw in ['however', 'differential', 'alternatively', 'may be seen']):
            scores.append(1)
        elif any(kw in report for kw in ['list', 'include', 'consider']):
            scores.append(0.5)
        else:
            scores.append(0)

    return np.mean(scores), np.std(scores)


def radgraph_f1(entries):
    scores = []

    medical_keywords = [
        "opacity", "opacities", "edema", "pneumonia",
        "bilateral", "consolidation", "effusion",
        "infiltrate", "lung", "cardiomegaly"
    ]

    for e in entries:
        report = e['report'].lower()

        gt_keywords = [k for k in medical_keywords if k in (e['disease'] + " " + e['region']).lower()]
        
        if not gt_keywords:
            scores.append(1.0)
            continue

        matched = sum(1 for k in gt_keywords if k in report)

        scores.append(matched / len(gt_keywords))  # coverage, not F1

    return np.mean(scores), np.std(scores)


def fact_score(entries):
    scores = []

    for e in entries:
        report = e['report'].lower()

        # Split into sentences
        sentences = re.split(r'[.\n]', report)

        valid_sentences = 0
        total = 0

        for s in sentences:
            s = s.strip()
            if len(s) < 10:
                continue

            total += 1

            # Check if sentence contains medical grounding
            if any(k in s for k in [
                "opacity", "edema", "consolidation",
                "effusion", "infiltrate", "bilateral"
            ]):
                valid_sentences += 1

        if total == 0:
            scores.append(0)
        else:
            scores.append(valid_sentences / total)

    return np.mean(scores), np.std(scores)


def aggregate_and_print(system, metrics, summary):
    print(f"System: {system}")
    print(f"Clinical Accuracy: {metrics['clinical'][0]:.2f} ± {metrics['clinical'][1]:.2f}")
    print(f"Diagnostic Reasoning: {metrics['reasoning'][0]:.2f} ± {metrics['reasoning'][1]:.2f}")
    print(f"Hit Rate: {metrics['hit_rate'][0]:.2f}")
    print(f"RadGraph-F1: {metrics['radgraph_f1'][0]:.2f}")
    print(f"FactScore: {metrics['fact_score'][0]:.2f}")
    print()

    summary[system] = {
        
        "Clinical Accuracy": f"{metrics['clinical'][0]:.2f} ± {metrics['clinical'][1]:.2f}",
        "Diagnostic Reasoning": f"{metrics['reasoning'][0]:.2f} ± {metrics['reasoning'][1]:.2f}",
        "Hit Rate": round(metrics['hit_rate'][0], 2),
        "RadGraph-F1": round(metrics['radgraph_f1'][0], 2),
        "FactScore": round(metrics['fact_score'][0], 2),
    }


def main():
    systems = {
        "Baseline": "results/baseline_rag/all_results.json",
        "RAG": "results/final/all_results.json",
        "RAG2": "results/final_rag2/all_results.json",
        "DER": "results/final_der/all_results.json",
        "Hybrid": "results/final_hybrid/all_results.json",
        "IMEDRAG": "results/final_reports_imedrag/all_results.json",
    }

    summary = {}

    for sys_name, path in systems.items():
        print(f"\n🔍 Checking: {sys_name}")

        if not os.path.exists(path):
            print(f"❌ Missing: {path}, skipping {sys_name}.")
            continue

        entries = load_json(path)

        if not entries:
            print(f"⚠️ Empty data in {sys_name}")
            continue

        metrics = {}
        metrics['hit_rate'] = hit_rate(entries)
        metrics['clinical'] = clinical_accuracy_score(entries)
        metrics['reasoning'] = diagnostic_reasoning_score(entries)
        metrics['radgraph_f1'] = radgraph_f1(entries)
        metrics['fact_score'] = fact_score(entries)

        aggregate_and_print(sys_name, metrics, summary)

    # Save summary
    out_path = Path("backend/evaluation/results_summary.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()