# backend/rag/report_generator.py

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

# Project root = parents[2] from backend/rag/this_file.py
_env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_env_path)

llm = ChatGroq(
    temperature=0.2,
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
)

def generate_report(disease, region, fuzzy_info, docs1, docs2):

    # -------------------------
    # 1. Prepare contexts (DER)
    # -------------------------
    support_context = "\n".join([doc.page_content for doc in docs1[:5]])
    diff_context = "\n".join([doc.page_content for doc in docs2[:5]])

    # -------------------------
    # 2. DER-aware prompt
    # -------------------------
    confidence_mid = (fuzzy_info['lower'] + fuzzy_info['upper']) / 2

    prompt = f"""
    You are an expert radiologist generating a CHEST X-RAY report.

    AI INPUT:
    - Predicted Disease: {disease}
    - Region: {region}
    - Confidence Interval: {fuzzy_info['lower']} - {fuzzy_info['upper']}

CONFIDENCE RULE:
- If confidence > 0.95 → use "strongly suggestive of"
- If 0.85–0.95 → use "suggestive of"
- If < 0.85 → use "possible" and expand differential

SUPPORT EVIDENCE:
{support_context}

DIFFERENTIAL EVIDENCE:
{diff_context}

-----------------------------------
STEP 1: Extract Imaging Features
-----------------------------------
From the findings, identify ONLY these features:

- Distribution: (bilateral / unilateral)
- Pattern: (diffuse / focal)
- Air bronchogram: (present / absent / not mentioned)
- Volume loss: (present / absent / not mentioned)

IMPORTANT:
- Do NOT assume features not present
- If unsure → mark "not mentioned"
- DO NOT include STEP 1 or feature extraction in final output

-----------------------------------
STEP 2: Generate Report (STRICT)
-----------------------------------

STRICT RULES:
- Assume modality is chest X-ray only
- DO NOT include Patient ID, dates, or extra sections
- DO NOT assume etiology (e.g., bacterial, cardiogenic)
- Do NOT include the predicted disease in differential
- Each condition must be clearly less likely or alternative
- Use ONLY extracted features for reasoning
- Avoid repetition
- Keep concise (2–3 sentences per section)

-----------------------------------
OUTPUT FORMAT (DO NOT MODIFY)
-----------------------------------

Radiology Report

Findings:
(Describe imaging findings and explicitly mention region and pattern)

Interpretation:
- Start with: "Findings are [confidence-based phrase] of [disease]"
- Use extracted features to justify diagnosis
- Compare with ONE alternative using feature differences

Recommendation:
- Recommend clinical correlation
- Suggest CT ONLY if diagnosis is uncertain

Differential Diagnosis:
- List 3–4 conditions
- Rank from most likely → least likely
- Each must include 1-line justification based ONLY on extracted features
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content