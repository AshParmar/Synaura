
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
# Removed incomplete import
# Project root = parents[2] from backend/rag/this_file.py
_env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_env_path)


def generate_query(disease, region, fuzzy_info, llm):

    prompt = f"""
You are an expert radiologist.

An AI system analyzed a chest X-ray:

Disease: {disease}
Region: {region}
Confidence Interval: {fuzzy_info['lower']} - {fuzzy_info['upper']}

Generate a precise clinical search query.

The query must:
- describe radiological findings based on region
- include disease characteristics
- include possible causes
- include differential diagnoses if uncertainty exists

IMPORTANT:
- Keep it ONE sentence
- Use clinical language
- Reflect uncertainty if confidence < 0.98
- Focus on imaging findings (not general disease description)

Example:
"What are the radiological findings and differential diagnosis of pulmonary edema presenting as bilateral diffuse opacities on chest X-ray?"

Generate the query.
"""
    # llm must be passed in from caller

    response = llm.invoke([
        HumanMessage(content=prompt)
    ])
    return response.content.strip()