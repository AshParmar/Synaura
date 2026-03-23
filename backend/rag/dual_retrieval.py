
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
# Removed incomplete import
# Project root = parents[2] from backend/rag/this_file.py
_env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_env_path)


def generate_dual_queries(disease, region, fuzzy_info, llm):

    prompt = f"""
You are an expert radiologist designing retrieval queries for clinical reasoning.

AI system output:
- Predicted Disease: {disease}
- Region: {region}
- Confidence Interval: {fuzzy_info['lower']} - {fuzzy_info['upper']}

Your task:
Generate TWO complementary search queries:

Query 1 (Support Path):
- Focus on confirming the predicted disease
- Include radiological findings specific to the region
- Emphasize imaging patterns seen in this disease

Query 2 (Differential Path):
- Focus on diseases that can mimic the same imaging findings
- Include overlapping radiological patterns in the SAME region
- Explicitly aim to retrieve alternative diagnoses

Uncertainty Rule:
- If confidence < 0.98 → make Query 2 strong and explicit
- If confidence ≥ 0.98 → Query 2 can still include possible mimics but less aggressive

STRICT RULES:
- Output EXACTLY in this format:
Query1: ...
Query2: ...
- Each query must be ONE sentence
- Use clinical radiology language
- Focus on chest X-ray imaging findings (NOT general disease theory)
- Avoid generic phrases like "what is"

GOOD EXAMPLE:

Query1: Radiological features of pulmonary edema presenting as bilateral diffuse opacities in lower lung fields on chest X-ray

Query2: Differential diagnosis of bilateral diffuse lung opacities on chest X-ray including ARDS, pneumonia, and interstitial lung disease

Now generate the queries.
"""

    response = llm.invoke([
        HumanMessage(content=prompt)
    ])
    text = response.content.strip()
    import re
    # Store regex patterns in variables
    query1_pattern = r"Query1 ?\(Support Path\) ?:"
    query2_pattern = r"Query2 ?\(Differential Path\) ?:"
    # Normalize markers for easier parsing
    text_norm = re.sub(query1_pattern, "Query1:", text, flags=re.IGNORECASE)
    text_norm = re.sub(query2_pattern, "Query2:", text_norm, flags=re.IGNORECASE)
    marker1 = "Query1:"
    marker2 = "Query2:"
    if marker1 not in text_norm or marker2 not in text_norm:
        print("[generate_dual_queries] LLM output did not contain expected markers.\nFull output:\n", text)
        raise ValueError("LLM output missing 'Query1:' or 'Query2:'. See printed output for details.")
    try:
        q1 = text_norm.split(marker1)[1].split(marker2)[0].strip()
        q2 = text_norm.split(marker2)[1].strip()
    except Exception as e:
        print("[generate_dual_queries] Error parsing LLM output:\n", text)
        raise ValueError(f"Failed to parse dual queries: {e}\nFull output:\n{text}")
    return q1, q2