"""
Legacy report generator for RAG2 (final_rag2): advanced prompt, no explicit differential diagnosis section, encourages comparison and uncertainty.
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

def legacy_generate_report_rag2(disease, region, fuzzy_info, docs1, docs2=None, temperature=0.2):
    context = "\n".join([doc.page_content for doc in docs1[:5]])
    prompt = f"""
You are an expert radiologist.

Generate a concise and clinically realistic radiology report.

AI System Output:
- Predicted Disease: {disease}
- Region: {region}
- Confidence Interval: {fuzzy_info['lower']} - {fuzzy_info['upper']}

Supporting Evidence:
{context}

IMPORTANT RULES:
- Do not include Patient Information, Dates, or Notes, Dates in the report
- Do NOT include placeholders like Patient ID, Date, or Notes
- Prefer "suggestive of" instead of "consistent with" unless certainty is very high
- In Interpretation, explicitly compare the predicted disease with at least one alternative condition
- Focus ONLY on imaging findings and interpretation
- Do NOT include patient information or general explanations
- Do NOT assume details not supported by evidence
- Avoid over-specific claims (e.g., cardiogenic vs non-cardiogenic unless clearly supported)
- Use cautious language such as "suggestive of" or "consistent with"
- Compare supporting and alternative conditions before concluding
- Keep the report concise and clinically relevant

Output format:

Radiology Report

Findings:
...

Interpretation:
...

Recommendation:
...
"""
    local_llm = ChatGroq(
        temperature=temperature,
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
    )
    response = local_llm.invoke([HumanMessage(content=prompt)])
    return response.content
