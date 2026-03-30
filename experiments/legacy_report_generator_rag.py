"""
Legacy report generator for RAG (final): simple, structured, no patient info, no differential diagnosis.
"""
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
import os
from pathlib import Path
from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(_env_path)

llm = ChatGroq(
    temperature=0.2,
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
)

def legacy_generate_report_rag(disease, region, fuzzy_info, docs1, docs2=None, temperature=0.2):
    context = "\n".join([doc.page_content for doc in docs1[:5]])
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
    local_llm = ChatGroq(
        temperature=temperature,
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
    )
    response = local_llm.invoke([HumanMessage(content=prompt)])
    return response.content

def generate_baseline_rag_report(disease, region, fuzzy_info, docs, temperature=0.2):
    context = "\n".join([doc.page_content for doc in docs[:5]])
    prompt = f"""
You are an expert radiologist.

Write a radiology report based ONLY on:

Disease: {disease}
Region: {region}
Confidence: {fuzzy_info['lower']} - {fuzzy_info['upper']}

Medical Knowledge:
{context}

IMPORTANT:
- Do NOT use external knowledge
- Do NOT include differential diagnosis
- Keep it simple and direct

Output:

Radiology Report

Findings:
...

Interpretation:
...

Recommendation:
...
"""
    # Create a new LLM instance with the specified temperature
    local_llm = ChatGroq(
        temperature=temperature,
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
    )
    response = local_llm.invoke([HumanMessage(content=prompt)])
    return response.content
