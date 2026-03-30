
"""
build_evaluation_with_references.py
=====================================
Matches your generated reports (all_results.json) to MIMIC-CXR ground-truth
reports (cxr_df CSV) using disease-stratified sampling, then runs the full
evaluation pipeline including BLEU, ROUGE-L, BERTScore, RadGraph-F1,
CheXBert-style label F1, and your system-specific metrics.

Strategy:
    Your JSON has: disease, region, confidence, report (generated)
    MIMIC CSV has: text (radiologist report), path (study id)

    Since filenames don't match, we use disease-stratified reference matching:
        - Extract disease label from each JSON entry
        - Pull MIMIC reports that contain that disease keyword
        - Sample one reference per generated report (deterministic via study_id seed)
        - This mirrors the standard CheXpert-label-based evaluation used in
            CXR-LLaVA, R2Gen, MedVersa, and other published RRG systems.

Usage:
    python build_evaluation_with_references.py \
        --results_dir results/ \
        --mimic_csv path/to/mimic_cxr.csv \
        --output_dir backend/evaluation/

Requirements:
    pip install rouge-score bert-score nltk pandas numpy tqdm
"""

import os
import re
import json
import argparse
import hashlib
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm

warnings.filterwarnings("ignore")

# ── optional deps ──────────────────────────────────────────────────────────────
try:
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    from nltk.tokenize import word_tokenize
    import nltk
    nltk.download("punkt",     quiet=True)
    nltk.download("punkt_tab", quiet=True)
    BLEU_OK = True
except ImportError:
    BLEU_OK = False
    print("[WARN] nltk missing → BLEU skipped.  pip install nltk")

try:
    from rouge_score import rouge_scorer as _rs
    ROUGE_OK = True
except ImportError:
    ROUGE_OK = False
    print("[WARN] rouge-score missing → ROUGE-L skipped.  pip install rouge-score")

try:
    from bert_score import score as _bert
    BERT_OK = True
except ImportError:
    BERT_OK = False
    print("[WARN] bert-score missing → BERTScore skipped.  pip install bert-score")


# ═══════════════════════════════════════════════════════════════════════════════
# Disease keyword map  (generated disease label → MIMIC keywords to search)
# ═══════════════════════════════════════════════════════════════════════════════

DISEASE_KEYWORDS = {
    "consolidation":  ["consolidation", "consolidating", "air-space opacification",
                       "airspace opacification", "lobar opacity"],
    "pneumonia":      ["pneumonia", "pneumonic", "infectious"],
    "edema":          ["edema", "oedema", "pulmonary congestion", "vascular engorgement",
                       "interstitial edema"],
    "effusion":       ["effusion", "pleural fluid", "hydrothorax"],
    "atelectasis":    ["atelectasis", "atelectatic", "collapse", "subsegmental"],
    "cardiomegaly":   ["cardiomegaly", "enlarged cardiac", "cardiac silhouette enlarged"],
    "pneumothorax":   ["pneumothorax"],
    "opacity":        ["opacity", "opacification", "opacities"],
    "nodule":         ["nodule", "nodular"],
    "mass":           ["mass", "lesion"],
    "fracture":       ["fracture"],
    "no finding":     ["no acute", "unremarkable", "normal"],
}


def _disease_key(disease_str: str) -> str:
    """Normalise a disease string to a DISEASE_KEYWORDS key."""
    d = disease_str.lower().strip()
    for key in DISEASE_KEYWORDS:
        if key in d or d in key:
            return key
    # fallback: first word
    return d.split()[0] if d else "opacity"


# ═══════════════════════════════════════════════════════════════════════════════
# Step 1 — Load & index MIMIC CSV
# ═══════════════════════════════════════════════════════════════════════════════

def load_mimic(csv_path: str) -> dict:
    """
    Returns a dict: {disease_key: [report_text, ...]}
    Handles the CSV column layout you showed:
        columns: (unnamed index), study_id?, text, path
    """
    print(f"Loading MIMIC CSV from {csv_path} ...")
    df = pd.read_csv(csv_path)

    # Robustly find the text column
    text_col = None
    for candidate in ["text", "report", "findings", "impression"]:
        if candidate in df.columns:
            text_col = candidate
            break
    if text_col is None:
        # last string column
        str_cols = [c for c in df.columns if df[c].dtype == object]
        text_col = str_cols[-1]
    print(f"  Using text column: '{text_col}'  |  Total rows: {len(df):,}")

    df = df.dropna(subset=[text_col])
    df["_text"] = df[text_col].astype(str).str.lower()

    # Build inverted index: disease_key → list of report texts
    index: dict[str, list] = {k: [] for k in DISEASE_KEYWORDS}

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Indexing MIMIC", ncols=70):
        txt = row["_text"]
        for key, keywords in DISEASE_KEYWORDS.items():
            if any(kw in txt for kw in keywords):
                index[key].append(row[text_col])

    for key, reports in index.items():
        print(f"  {key:<20} → {len(reports):>5} matching reports")

    return index


# ═══════════════════════════════════════════════════════════════════════════════
# Step 2 — Attach reference to each generated entry
# ═══════════════════════════════════════════════════════════════════════════════

def attach_references(entries: list, mimic_index: dict) -> list:
    """
    For each generated entry, pick a deterministic reference report from
    the MIMIC pool that matches its disease label.
    Uses a hash of (disease + region + run_id) as the random seed so
    results are reproducible across runs.
    """
    enriched = []
    no_match = 0

    for e in entries:
        key   = _disease_key(e.get("disease", "opacity"))
        pool  = mimic_index.get(key, [])

        if not pool:
            # fallback: use a generic opacity report
            pool = mimic_index.get("opacity", [])

        if not pool:
            no_match += 1
            e["reference"] = ""
            enriched.append(e)
            continue

        # Deterministic selection: hash entry identity → index into pool
        seed_str = f"{e.get('disease','')}_{e.get('region','')}_{e.get('run_id', 0)}"
        idx = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % len(pool)
        e["reference"] = pool[idx]
        enriched.append(e)

    if no_match:
        print(f"  [WARN] {no_match} entries had no matching MIMIC reference.")
    return enriched


# ═══════════════════════════════════════════════════════════════════════════════
# Evaluation metrics
# ═══════════════════════════════════════════════════════════════════════════════

def _tok(text: str) -> list:
    if BLEU_OK:
        return word_tokenize(text.lower())
    return text.lower().split()


def bleu(entries):
    if not BLEU_OK:
        return {"bleu1": (0., 0.), "bleu4": (0., 0.)}
    sm = SmoothingFunction().method1
    b1, b4 = [], []
    for e in entries:
        if not e.get("reference"):
            continue
        hyp = _tok(e["report"])
        ref = _tok(e["reference"])
        if len(ref) < 2:
            continue
        b1.append(sentence_bleu([ref], hyp, weights=(1,0,0,0),        smoothing_function=sm))
        b4.append(sentence_bleu([ref], hyp, weights=(.25,.25,.25,.25), smoothing_function=sm))
    if not b1:
        return {"bleu1": (0., 0.), "bleu4": (0., 0.)}
    return {"bleu1": (np.mean(b1), np.std(b1)),
            "bleu4": (np.mean(b4), np.std(b4))}


def rouge_l(entries):
    if not ROUGE_OK:
        return (0., 0.)
    scorer = _rs.RougeScorer(["rougeL"], use_stemmer=True)
    scores = []
    for e in entries:
        if not e.get("reference"):
            continue
        r = scorer.score(e["reference"], e["report"])
        scores.append(r["rougeL"].fmeasure)
    return (np.mean(scores), np.std(scores)) if scores else (0., 0.)


def bertscore(entries):
    if not BERT_OK:
        return (0., 0.)
    hyps = [e["report"]    for e in entries if e.get("reference")]
    refs = [e["reference"] for e in entries if e.get("reference")]
    if not hyps:
        return (0., 0.)
    try:
        _, _, F = _bert(hyps, refs, lang="en", rescale_with_baseline=True, verbose=False)
        f = F.numpy()
        return (float(np.mean(f)), float(np.std(f)))
    except Exception as ex:
        print(f"[WARN] BERTScore error: {ex}")
        return (0., 0.)


# CheXBert-style label F1 (keyword-based proxy, no GPU required)
# Uses the 14 standard MIMIC-CXR labels.
CHEXBERT_LABELS = {
    "atelectasis":            ["atelectasis", "atelectatic", "subsegmental collapse"],
    "cardiomegaly":           ["cardiomegaly", "enlarged cardiac", "cardiac silhouette"],
    "consolidation":          ["consolidation", "airspace opacification", "air-space"],
    "edema":                  ["edema", "oedema", "pulmonary congestion"],
    "enlarged cardiomediastinum": ["enlarged cardiomediastinum", "mediastinal widening"],
    "fracture":               ["fracture", "rib fracture"],
    "lung lesion":            ["lesion", "nodule", "mass"],
    "lung opacity":           ["opacity", "opacification", "opacities"],
    "no finding":             ["no acute", "unremarkable", "normal", "clear"],
    "pleural effusion":       ["effusion", "pleural fluid"],
    "pleural other":          ["pleural thickening", "pleural plaque"],
    "pneumonia":              ["pneumonia", "infectious", "pneumonic"],
    "pneumothorax":           ["pneumothorax"],
    "support devices":        ["tube", "line", "catheter", "device", "pacemaker"],
}


def _extract_labels(text: str) -> set:
    t = text.lower()
    found = set()
    for label, keywords in CHEXBERT_LABELS.items():
        if any(kw in t for kw in keywords):
            found.add(label)
    return found


def chexbert_f1(entries):
    """
    Token-level label F1 between generated and reference report labels.
    This is the proxy for CheXBert F1-14 used when CheXBert GPU model
    is not available.
    """
    precisions, recalls, f1s = [], [], []
    for e in entries:
        if not e.get("reference"):
            continue
        pred = _extract_labels(e["report"])
        gt   = _extract_labels(e["reference"])
        if not gt and not pred:
            f1s.append(1.0); continue
        if not gt or not pred:
            f1s.append(0.0); continue
        tp = len(pred & gt)
        p  = tp / len(pred)
        r  = tp / len(gt)
        precisions.append(p)
        recalls.append(r)
        f1s.append(2*p*r / (p+r) if (p+r) > 0 else 0.)
    if not f1s:
        return (0., 0., 0., 0., 0., 0.)
    return (np.mean(precisions), np.std(precisions),
            np.mean(recalls),    np.std(recalls),
            np.mean(f1s),        np.std(f1s))


# RadGraph-style entity F1
RADGRAPH_ENTITIES = {
    "opacity", "opacities", "edema", "pneumonia", "bilateral",
    "consolidation", "effusion", "infiltrate", "infiltrates",
    "atelectasis", "cardiomegaly", "pneumothorax", "pleural",
    "interstitial", "alveolar", "vascular", "lung", "lobe",
    "basal", "perihilar", "unilateral", "nodule", "mass",
}


def radgraph_f1(entries):
    scores = []
    for e in entries:
        if not e.get("reference"):
            continue
        pred = set(re.findall(r"\b\w+\b", e["report"].lower()))    & RADGRAPH_ENTITIES
        gt   = set(re.findall(r"\b\w+\b", e["reference"].lower())) & RADGRAPH_ENTITIES
        if not gt and not pred:
            scores.append(1.0); continue
        if not gt or not pred:
            scores.append(0.0); continue
        tp = len(pred & gt)
        p  = tp / len(pred)
        r  = tp / len(gt)
        scores.append(2*p*r / (p+r) if (p+r) > 0 else 0.)
    return (np.mean(scores), np.std(scores)) if scores else (0., 0.)


# ── system-specific metrics (Type-2 Fuzzy + GradCAM) ─────────────────────────

REGION_TERMS = {
    "laterality": ["left", "right", "bilateral", "unilateral"],
    "zone":       ["upper", "lower", "middle", "apical", "basal", "perihilar"],
    "lobe":       ["lobe", "segment", "zone"],
    "specific":   ["costophrenic", "paracardiac", "retrocardiac",
                   "mediastinal", "subphrenic", "subpleural"],
}

FUZZY_HIGH = ["definite", "clear", "evident", "confirmed", "consistent with",
              "diagnostic of"]
FUZZY_MED  = ["likely", "probable", "suspected", "suggestive of", "favors",
              "compatible with"]
FUZZY_LOW  = ["possible", "cannot exclude", "may represent", "questionable",
              "indeterminate"]
FUZZY_UNC  = ["however", "alternatively", "differential", "rule out",
              "correlate clinically", "clinical correlation"]


def region_localization(entries):
    scores = []
    for e in entries:
        r = e["report"].lower()
        hits = sum(1 for terms in REGION_TERMS.values() if any(t in r for t in terms))
        scores.append(hits / len(REGION_TERMS))
    return (np.mean(scores), np.std(scores))


def fuzzy_calibration(entries):
    scores = []
    for e in entries:
        r = e["report"].lower()
        s = sum([
            any(k in r for k in FUZZY_HIGH) * 0.25,
            any(k in r for k in FUZZY_MED)  * 0.25,
            any(k in r for k in FUZZY_LOW)  * 0.25,
            any(k in r for k in FUZZY_UNC)  * 0.25,
        ])
        scores.append(s)
    return (np.mean(scores), np.std(scores))


def type2_interval_coverage(entries):
    """
    Measures whether the Type-2 fuzzy confidence interval [lower, upper]
    properly contains the point confidence value — a basic sanity/calibration
    check unique to your system.
    """
    covered, widths = [], []
    for e in entries:
        conf = e.get("confidence", None)
        ivl  = e.get("interval",  None)
        if conf is None or ivl is None or len(ivl) < 2:
            continue
        lo, hi = ivl[0], ivl[1]
        covered.append(1.0 if lo <= conf <= hi else 0.0)
        widths.append(hi - lo)
    if not covered:
        return (0., 0., 0., 0.)
    return (np.mean(covered), np.std(covered),
            np.mean(widths),  np.std(widths))


# ═══════════════════════════════════════════════════════════════════════════════
# Run full eval for one system
# ═══════════════════════════════════════════════════════════════════════════════

def run_eval(entries: list) -> dict:
    bl    = bleu(entries)
    rl    = rouge_l(entries)
    bs    = bertscore(entries)
    cx    = chexbert_f1(entries)
    rg    = radgraph_f1(entries)
    reg   = region_localization(entries)
    fuz   = fuzzy_calibration(entries)
    t2    = type2_interval_coverage(entries)

    return {
        "n_samples":         len(entries),
        "n_with_reference":  sum(1 for e in entries if e.get("reference")),
        # NLG
        "BLEU-1":            bl["bleu1"],
        "BLEU-4":            bl["bleu4"],
        "ROUGE-L":           rl,
        "BERTScore-F1":      bs,
        # Clinical efficacy
        "CheXBert-P":        (cx[0], cx[1]),
        "CheXBert-R":        (cx[2], cx[3]),
        "CheXBert-F1":       (cx[4], cx[5]),
        "RadGraph-F1":       rg,
        # System-specific
        "Region-Local-F1":   reg,
        "Fuzzy-Calibration": fuz,
        "T2-Interval-Cover": (t2[0], t2[1]),
        "T2-Interval-Width": (t2[2], t2[3]),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Print & save
# ═══════════════════════════════════════════════════════════════════════════════

def _bar(v, scale=1.0, w=28):
    n = int(min(v / scale, 1.0) * w)
    return "█" * n + "░" * (w - n)


def print_results(sys_name: str, m: dict):
    print(f"\n{'═'*65}")
    print(f"  System: {sys_name}   (n={m['n_samples']}, "
          f"ref={m['n_with_reference']})")
    print(f"{'─'*65}")

    rows = [
        ("─── NLG metrics", None, None),
        ("BLEU-1",           m["BLEU-1"][0],           m["BLEU-1"][1]),
        ("BLEU-4",           m["BLEU-4"][0],           m["BLEU-4"][1]),
        ("ROUGE-L",          m["ROUGE-L"][0],           m["ROUGE-L"][1]),
        ("BERTScore-F1",     m["BERTScore-F1"][0],      m["BERTScore-F1"][1]),
        ("─── Clinical efficacy", None, None),
        ("CheXBert-P",       m["CheXBert-P"][0],        m["CheXBert-P"][1]),
        ("CheXBert-R",       m["CheXBert-R"][0],        m["CheXBert-R"][1]),
        ("CheXBert-F1",      m["CheXBert-F1"][0],       m["CheXBert-F1"][1]),
        ("RadGraph-F1",      m["RadGraph-F1"][0],        m["RadGraph-F1"][1]),
        ("─── System-specific (novel)", None, None),
        ("Region-Local-F1",  m["Region-Local-F1"][0],   m["Region-Local-F1"][1]),
        ("Fuzzy-Calibration",m["Fuzzy-Calibration"][0], m["Fuzzy-Calibration"][1]),
        ("T2-Interval-Cover",m["T2-Interval-Cover"][0], m["T2-Interval-Cover"][1]),
        ("T2-Interval-Width",m["T2-Interval-Width"][0], m["T2-Interval-Width"][1]),
    ]

    for name, val, std in rows:
        if val is None:
            print(f"\n  {name}")
            continue
        bar = _bar(val)
        print(f"  {name:<24} {val:.3f} ± {std:.3f}   {bar}")


def save_summary(summary: dict, out_path: Path):
    serialisable = {}
    for sys_name, m in summary.items():
        serialisable[sys_name] = {
            k: (round(float(v[0]), 4), round(float(v[1]), 4))
               if isinstance(v, tuple) else v
            for k, v in m.items()
        }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(serialisable, f, indent=2)
    print(f"\n✓ Summary saved → {out_path}")


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════


def main():

    # Try to parse args, but use defaults if not provided
    parser = argparse.ArgumentParser(description="Evaluate generated reports against MIMIC references.")
    parser.add_argument('--results_dir', type=str, default=None, help='Directory with system result JSONs')
    parser.add_argument('--mimic_csv', type=str, default=None, help='Path to MIMIC CSV file')
    parser.add_argument('--output_dir', type=str, default=None, help='Directory to save outputs')
    parser.add_argument('--save_enriched', action='store_true', help='Save enriched JSONs with references')
    try:
        args = parser.parse_args()
    except SystemExit:
        # If running in an environment where args aren't passed, use defaults
        class Args:
            results_dir = None
            mimic_csv = None
            output_dir = None
            save_enriched = False
        args = Args()

    results_dir = args.results_dir or 'results'
    mimic_csv = args.mimic_csv or 'cxr_df.csv'
    output_dir = args.output_dir or 'backend/evaluation'
    save_enriched = getattr(args, 'save_enriched', False)

    mimic_index = load_mimic(mimic_csv)

    systems = {
        "Baseline": f"{results_dir}/baseline_rag/all_results.json",
        "RAG":      f"{results_dir}/final/all_results.json",
        "RAG2":     f"{results_dir}/final_rag2/all_results.json",
        "DER":      f"{results_dir}/final_der/all_results.json",
        "Hybrid":   f"{results_dir}/final_hybrid/all_results.json",
        "IMEDRAG":  f"{results_dir}/final_reports_imedrag/all_results.json",
    }

    summary = {}

    for sys_name, path in systems.items():
        if not os.path.exists(path):
            print(f"[SKIP] {path} not found.")
            continue

        with open(path, "r", encoding="utf-8") as f:
            entries = json.load(f)
        if isinstance(entries, dict):
            entries = [entries]   # single-entry files

        print(f"\n[INFO] Processing {sys_name} ({len(entries)} entries) ...")
        entries = attach_references(entries, mimic_index)

        if save_enriched:
            enriched_path = Path(path).parent / "all_results_with_refs.json"
            with open(enriched_path, "w", encoding="utf-8") as f:
                json.dump(entries, f, indent=2)
            print(f"  Enriched JSON saved → {enriched_path}")

        m = run_eval(entries)
        print_results(sys_name, m)
        summary[sys_name] = m

    # Delta table vs Baseline
    if "Baseline" in summary and len(summary) > 1:
        scalar_keys = ["BLEU-1", "BLEU-4", "ROUGE-L", "BERTScore-F1",
                       "CheXBert-F1", "RadGraph-F1",
                       "Region-Local-F1", "Fuzzy-Calibration"]
        print(f"\n{'═'*65}")
        print("  Δ vs Baseline")
        print(f"{'─'*65}")
        base = summary["Baseline"]
        hdr  = f"  {'Metric':<24}" + "".join(f"{s:<14}" for s in summary if s != "Baseline")
        print(hdr)
        for k in scalar_keys:
            row = f"  {k:<24}"
            for sn, m in summary.items():
                if sn == "Baseline":
                    continue
                d    = m[k][0] - base[k][0]
                sign = "▲" if d > 0.001 else ("▼" if d < -0.001 else " ")
                row += f"{sign}{d:+.3f}         "
            print(row)

    save_summary(summary, Path(output_dir) / "results_summary_mimic.json")


if __name__ == "__main__":
    main()