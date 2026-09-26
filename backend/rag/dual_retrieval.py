
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

    # Accept multiple marker variants produced by different models:
    # Query1:, Query 1:, Query 1 (Support Path):, Query2:, Query 2:, etc.
    q1_match = re.search(
        r"(?is)query\s*1\s*(?:\([^)]*\))?\s*:\s*(.*?)(?=\n\s*query\s*2\s*(?:\([^)]*\))?\s*:|$)",
        text,
    )
    q2_match = re.search(
        r"(?is)query\s*2\s*(?:\([^)]*\))?\s*:\s*(.*)$",
        text,
    )

    if not q1_match or not q2_match:
        print("[generate_dual_queries] LLM output did not contain expected markers, using fallback.\nFull output:\n", text)
        q1 = f"Radiological features of {disease} in {region} on chest X-ray"
        q2 = f"Differential diagnosis of {region} opacities on chest X-ray including mimics of {disease}"
        return q1, q2

    q1 = q1_match.group(1).strip().strip('*').strip()
    q2 = q2_match.group(1).strip().strip('*').strip()

    if not q1 or not q2:
        print("[generate_dual_queries] Parsed empty query text, using fallback.\nFull output:\n", text)
        q1 = f"Radiological features of {disease} in {region} on chest X-ray"
        q2 = f"Differential diagnosis of {region} opacities on chest X-ray including mimics of {disease}"

    return q1, q2