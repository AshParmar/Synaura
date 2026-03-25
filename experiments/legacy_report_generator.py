"""
Legacy report generator for experiments (no differential diagnosis section, simple prompt).
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

# Load .env from project root
_env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(_env_path)

llm = ChatGroq(
    temperature=0.2,
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
)

def legacy_generate_report(disease, region, fuzzy_info, docs1, docs2=None):
    # Only use docs1 for legacy experiments
    context = "\n".join([doc.page_content for doc in docs1[:5]])
    confidence_mid = (fuzzy_info['lower'] + fuzzy_info['upper']) / 2
    if confidence_mid > 0.95:
        phrase = "strongly suggestive of"
    elif confidence_mid > 0.85:
        phrase = "suggestive of"
    else:
        phrase = "possible"
    prompt = f"""
You are an expert radiologist generating a CHEST X-RAY report.

AI INPUT:
- Predicted Disease: {disease}
- Region: {region}
- Confidence Interval: {fuzzy_info['lower']} - {fuzzy_info['upper']}

SUPPORTING EVIDENCE:
{context}

Radiology Report

Findings:
(Describe imaging findings and explicitly mention region and pattern)

Interpretation:
- Start with: 'Findings are {phrase} of {disease}'
- Use extracted features to justify diagnosis
- Compare with ONE alternative if appropriate

Recommendation:
- Recommend clinical correlation
- Suggest CT ONLY if diagnosis is uncertain
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content
