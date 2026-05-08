"""
recall_evaluation.py
=====================
Semantic Recall@k using sentence-transformers cosine similarity.

Why semantic instead of keyword:
  Keyword matching always returns ~1.0 because your retrieved_contexts
  already contain the disease name. Semantic scoring gives real
  differentiated scores that show improvement across systems.

How it works:
  1. Embed the clinical query  (disease + region)
  2. Embed each retrieved document
  3. Compute cosine similarity between query and each doc
  4. Recall@k = mean of top-k similarity scores

Split-context bonus (DER / Hybrid / IMEDRAG):
  Also scores support contexts and differential contexts separately,
  showing the dual-retrieval advantage over flat retrieval systems.

Install:
    pip install sentence-transformers numpy

Run:
    python backend/evaluation/recall_evaluation.py
"""

import json
import numpy as np
from pathlib import Path
from tqdm import tqdm

try:
    from sentence_transformers import SentenceTransformer, util
    ST_OK = True
except ImportError:
    ST_OK = False
    print("[ERROR] pip install sentence-transformers")
    exit(1)

# =============================================================================
# CONFIGURE
# =============================================================================

# Best model for medical/clinical text similarity
# alternatives: "pritamdeka/S-PubMedBert-MS-MARCO"  (medical-specific, slower)
#               "all-MiniLM-L6-v2"                   (fast, general)
MODEL_NAME = "pritamdeka/S-PubMedBert-MS-MARCO"   # medical domain, best scores

RECALL_K_VALUES = [1, 3, 5, 10]

SYSTEMS = {
    "Baseline": r"results\baseline_llm\all_results.json",
    "Rag0": r"results\baseline_rag\all_results.json",
    "RAG":      r"results\final_rag\all_results.json",
    "RAG2":     r"results\final_rag2\all_results.json",
    "DER":      r"results\final_der\all_results.json",
    "Hybrid":   r"results\final_hybrid\all_results.json",
    "Synaura": r"results\final_reports_imedrag\all_results.json",
}

OUTPUT_PATH = r"backend\evaluation\recall_results.json"

# Relevance threshold — docs with similarity >= this count as a "hit"
# 0.5 is standard for medical retrieval evaluation
RELEVANCE_THRESHOLD = 0.50

# =============================================================================


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [data] if isinstance(data, dict) else data


def _bar(v, w=30):
    n = int(min(max(float(v), 0.), 1.0) * w)
    return "█" * n + "░" * (w - n)


def _get_contexts(entry):
    """Normalise both flat-list and split-dict context formats."""
    rc = entry.get("retrieved_contexts")

    if isinstance(rc, list):
        texts = [str(d).strip() for d in rc if d]
        return {"all": texts, "support": texts, "differential": []}

    if isinstance(rc, dict):
        support      = [str(d).strip() for d in rc.get("support",      []) if d]
        differential = [str(d).strip() for d in rc.get("differential", []) if d]
        return {"all": support + differential, "support": support, "differential": differential}

    # Fallback proxy
    proxy = (
        entry.get("support_query", "") + " " +
        entry.get("differential_query", "") + " " +
        entry.get("disease", "")
    ).strip()
    return {"all": [proxy], "support": [proxy], "differential": []}


def _build_query(entry):
    """Build a rich clinical query from entry fields."""
    disease = entry.get("disease", "")
    region  = entry.get("region",  "")
    sq      = entry.get("support_query", "")

    if sq:
        return sq   # use the actual support query if stored
    return f"{disease} chest X-ray radiological findings {region}".strip()


# =============================================================================
# Semantic Recall@k
# =============================================================================

def compute_semantic_recall(entries, model):
    """
    For each entry:
      - Embed the clinical query
      - Embed all retrieved documents
      - Compute cosine similarity scores
      - Recall@k = fraction of top-k docs with similarity >= RELEVANCE_THRESHOLD

    Also computes:
      - Mean Similarity@k  (continuous score, better for showing improvement)
      - Support vs Differential breakdown for split-context systems
    """
    results         = {k: [] for k in RECALL_K_VALUES}
    mean_sim        = {k: [] for k in RECALL_K_VALUES}
    support_sims    = []
    diff_sims       = []

    n_flat  = sum(1 for e in entries if isinstance(e.get("retrieved_contexts"), list))
    n_split = sum(1 for e in entries if isinstance(e.get("retrieved_contexts"), dict))
    n_proxy = len(entries) - n_flat - n_split

    for e in tqdm(entries, desc="  Embedding", ncols=65):
        query    = _build_query(e)
        contexts = _get_contexts(e)

        all_docs = contexts["all"]
        if not all_docs:
            continue

        # Encode query + all docs in one batch (efficient)
        query_emb = model.encode(query,    convert_to_tensor=True, show_progress_bar=False)
        doc_embs  = model.encode(all_docs, convert_to_tensor=True, show_progress_bar=False)

        # Cosine similarities: shape (n_docs,)
        sims = util.cos_sim(query_emb, doc_embs)[0].cpu().numpy()

        for k in RECALL_K_VALUES:
            top_k_sims = sims[:k]

            # Binary recall: at least one doc above threshold
            hit = float(np.any(top_k_sims >= RELEVANCE_THRESHOLD))
            results[k].append(hit)

            # Continuous mean similarity (better differentiator between systems)
            mean_sim[k].append(float(np.mean(top_k_sims)))

        # Support vs differential breakdown
        if contexts["support"] and contexts["differential"]:
            supp_embs = model.encode(
                contexts["support"], convert_to_tensor=True, show_progress_bar=False
            )
            diff_embs = model.encode(
                contexts["differential"], convert_to_tensor=True, show_progress_bar=False
            )
            s_sims = util.cos_sim(query_emb, supp_embs)[0].cpu().numpy()
            d_sims = util.cos_sim(query_emb, diff_embs)[0].cpu().numpy()
            support_sims.append(float(np.mean(s_sims)))
            diff_sims.append(float(np.mean(d_sims)))

    recall_scores  = {k: (float(np.mean(v)), float(np.std(v))) for k, v in results.items()}
    meansim_scores = {k: (float(np.mean(v)), float(np.std(v))) for k, v in mean_sim.items()}

    return recall_scores, meansim_scores, {
        "n_flat":    n_flat,
        "n_split":   n_split,
        "n_proxy":   n_proxy,
        "support_mean_sim":      round(float(np.mean(support_sims)), 4) if support_sims else None,
        "differential_mean_sim": round(float(np.mean(diff_sims)),    4) if diff_sims    else None,
    }


def print_results(sys_name, recall, meansim, stats):
    fmt = "split" if stats["n_split"] > 0 else ("flat" if stats["n_flat"] > 0 else "proxy")
    print(f"\n  {'='*58}")
    print(f"  System : {sys_name}  [{fmt} contexts]  "
          f"({stats['n_flat']}F / {stats['n_split']}S / {stats['n_proxy']}P)")

    if stats["support_mean_sim"] is not None:
        print(f"  Support ctx mean similarity     : "
              f"{stats['support_mean_sim']:.4f}   "
              f"{_bar(stats['support_mean_sim'])}")
    if stats["differential_mean_sim"] is not None:
        print(f"  Differential ctx mean similarity: "
              f"{stats['differential_mean_sim']:.4f}   "
              f"{_bar(stats['differential_mean_sim'])}")

    print(f"\n  {'k':<6} {'Recall@k':<12} {'MeanSim@k':<14} Bar (MeanSim)")
    print(f"  {'-'*58}")
    for k in RECALL_K_VALUES:
        r_m, r_s  = recall[k]
        ms_m, ms_s = meansim[k]
        print(f"  @{k:<5} {r_m:.3f}±{r_s:.3f}   "
              f"{ms_m:.4f}±{ms_s:.4f}   {_bar(ms_m)}")


# =============================================================================
# Main
# =============================================================================

def main():
    print("=" * 60)
    print("  Semantic Recall@k Evaluation")
    print(f"  Model  : {MODEL_NAME}")
    print(f"  Thresh : {RELEVANCE_THRESHOLD}")
    print("=" * 60)

    print(f"\nLoading model: {MODEL_NAME} ...")
    model = SentenceTransformer(MODEL_NAME)
    print("  Model loaded.")

    all_recall  = {}
    all_meansim = {}
    all_stats   = {}

    for sys_name, path in SYSTEMS.items():
        if not Path(path).exists():
            print(f"\n[SKIP] {path} not found.")
            continue

        entries = load_json(path)
        print(f"\n[{sys_name}]  {len(entries)} entries")

        recall, meansim, stats = compute_semantic_recall(entries, model)
        print_results(sys_name, recall, meansim, stats)

        all_recall[sys_name]  = recall
        all_meansim[sys_name] = meansim
        all_stats[sys_name]   = stats

    # ── Delta table vs Baseline ───────────────────────────────────────
    if "Baseline" in all_recall and len(all_recall) > 1:
        others = [s for s in all_recall if s != "Baseline"]

        print(f"\n  {'='*60}")
        print("  Delta vs Baseline  (MeanSim@k — higher is better)")
        print(f"  {'-'*60}")
        print(f"  {'k':<8}" + "".join(f"{s:<16}" for s in others))

        for k in RECALL_K_VALUES:
            row = f"  @{k:<7}"
            for sn in others:
                d    = all_meansim[sn][k][0] - all_meansim["Baseline"][k][0]
                sign = "▲" if d > 0.001 else ("▼" if d < -0.001 else " ")
                row += f"{sign}{d:+.4f}          "
            print(row)

        print(f"\n  Delta vs Baseline  (Recall@k binary)")
        print(f"  {'k':<8}" + "".join(f"{s:<16}" for s in others))
        for k in RECALL_K_VALUES:
            row = f"  @{k:<7}"
            for sn in others:
                d    = all_recall[sn][k][0] - all_recall["Baseline"][k][0]
                sign = "▲" if d > 0.001 else ("▼" if d < -0.001 else " ")
                row += f"{sign}{d:+.4f}          "
            print(row)

    # ── Save ─────────────────────────────────────────────────────────
    out = Path(OUTPUT_PATH)
    out.parent.mkdir(parents=True, exist_ok=True)

    save_obj = {}
    for sn in all_recall:
        save_obj[sn] = {
            "recall_at_k":   {f"@{k}": list(v) for k, v in all_recall[sn].items()},
            "meansim_at_k":  {f"@{k}": list(v) for k, v in all_meansim[sn].items()},
            "context_stats": all_stats[sn],
        }

    with open(out, "w") as f:
        json.dump(save_obj, f, indent=2)

    print(f"\n[DONE] Saved -> {out}")


if __name__ == "__main__":
    main()