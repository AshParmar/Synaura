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


def generate_report(disease, region, fuzzy_info, docs):

    # -------------------------
    # 1. Filter relevant docs
    # -------------------------
    filtered_docs = [
        d for d in docs
        if disease.lower() in d.page_content.lower()
    ]

    if len(filtered_docs) == 0:
        filtered_docs = docs[:1]  # fallback

    context = "\n".join([doc.page_content for doc in filtered_docs])

    # -------------------------
    # 2. Strong controlled prompt
    # -------------------------
    prompt = f"""
You are an expert radiologist.

IMPORTANT RULES:
- The classifier has predicted: {disease}
- You MUST align with this diagnosis
- DO NOT contradict the prediction
- DO NOT say the image is normal
- DO NOT include patient information or placeholders

SPECIAL RULE:
- If disease is cardiomegaly → focus on heart enlargement and cardiothoracic ratio
- Do NOT incorrectly associate lung regions with heart diseases

X-ray Analysis:
Disease: {disease}
Region: {region}
Confidence Interval: {fuzzy_info['lower']} - {fuzzy_info['upper']}
Interpretation: {fuzzy_info['interpretation']}

Medical Knowledge:
{context}

Write a structured radiology report:

Radiology Report

Findings:
Interpretation:
Recommendation:

Use information from MULTIPLE sources.
If sources differ, mention uncertainty.
Do not rely on a single document.

Keep the report concise, accurate, and clinically consistent with {disease}.
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content
