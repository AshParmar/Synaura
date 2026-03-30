import os
import json
import numpy as np
import google.generativeai as genai
from tqdm import tqdm
import dotenv

dotenv.load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

SYSTEMS = {
    "Baseline": r"results\baseline_rag\all_results.json",
    "RAG":      r"results\final\all_results.json",
    "RAG v2":   r"results\final_rag2\all_results.json",
    "DER":      r"results\final_der\all_results.json",
    "Hybrid":   r"results\final_hybrid\all_results.json",
    "IMEDRAG":  r"results\final_reports_imedrag\all_results.json",
}

def is_match(target, text):
    if not target or not text or len(text.strip()) < 5: 
        return False
    
    # Semantic check for medical synonyms
    prompt = f"Target Diagnosis: {target}\nDocument Text: {text[:2000]}\nDoes the document mention or describe this diagnosis? Answer YES or NO."
    try:
        # We only call the LLM if a simple string check fails to save time
        if target.lower() in text.lower(): return True
        res = model.generate_content(prompt)
        return "YES" in res.text.upper()
    except:
        return False

def run_strict_eval():
    print("🔬 Running STRICT Retrieval Evaluation (Source Docs Only)...")
    
    for sys_name, path in SYSTEMS.items():
        if not os.path.exists(path): continue
        with open(path, "r", encoding="utf-8") as f:
            entries = json.load(f)
        
        # Results storage
        results = {1: [], 3: [], 5: []}

        for e in tqdm(entries, desc=f"Evaluating {sys_name}", leave=False):
            target = e.get("disease", "")
            raw_ctx = e.get("retrieved_contexts", [])

            # --- THE "STRICT" EXTRACTION ---
            # We ignore the 'report' field entirely.
            # We treat the context as a list of documents.
            if isinstance(raw_ctx, str):
                # If your RAG saved contexts as one string, we treat it as one block
                docs = [raw_ctx]
            else:
                # If it's a list, we handle each chunk
                docs = [str(d.get("text", d)) if isinstance(d, dict) else str(d) for d in raw_ctx]

            for k in [1, 3, 5]:
                combined_text = " ".join(docs[:k])
                results[k].append(1 if is_match(target, combined_text) else 0)

        print(f"\n📊 System: {sys_name}")
        for k in [1, 3, 5]:
            hits = sum(results[k])
            print(f"  Recall@{k}: {np.mean(results[k]):.4f} ({hits}/{len(entries)})")

if __name__ == "__main__":
    run_strict_eval()