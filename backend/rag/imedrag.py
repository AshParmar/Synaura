from langchain_core.messages import HumanMessage, SystemMessage

def refine_report(report, support_context, diff_context, llm):
    combined_context = support_context + "\n\n" + diff_context

    system_instruction = (
        "You are an expert Clinical Radiology Report Refiner.\n"
        "Your goal is to IMPROVE diagnostic reasoning while preserving structure.\n"
        "You may MODIFY weak reasoning but must NOT hallucinate.\n"
        "Output ONLY the final report."
    )

    prompt = f"""
Original Report:
{report}

Medical Evidence (reference only, DO NOT copy):
{combined_context}

-----------------------------------
CORE TASK
-----------------------------------
Refine the report by:
- Fixing weak or incorrect reasoning
- Improving diagnostic justification using imaging features
- Improving differential diagnosis quality
- Preserving structure unless incorrect

-----------------------------------
SMART CORRECTION RULES
-----------------------------------
- Strengthen weak reasoning using imaging features
- Rewrite generic differentials using feature-based justification
- Reorder differential based on imaging similarity
- Prefer improving reasoning over preserving wording

-----------------------------------
HARD CONSTRAINTS (CRITICAL)
-----------------------------------
- Do NOT add new findings not present in Original Report
- Do NOT copy or summarize Medical Evidence
- Do NOT introduce unrelated or rare diseases
- Do NOT add explanations, background, or teaching text
- Remove intermediate steps (e.g., STEP 1, STEP 2)
- Do NOT include subtypes or etiologies of the predicted disease
- Do NOT use clinical history, symptoms, or causes
- Use ONLY imaging-visible features (pattern, distribution, symmetry)

-----------------------------------
STYLE RULES
-----------------------------------
- Short, dense radiology-style sentences
- Avoid repetition between Findings and Interpretation
- Interpretation = WHY diagnosis fits (not description)
- Avoid textbook phrasing
- Avoid "as" explanations
- Prefer compressed reasoning (e.g., "pattern supports", "features favor")
- Avoid weak or non-imaging differentials
- Avoid causal phrases ("due to", "caused by", "history of")

-----------------------------------
INTERPRETATION CONTROLS
-----------------------------------
- Do NOT infer underlying etiology (e.g., cardiomyopathy)
- Stay at imaging diagnosis level only

-----------------------------------
CONFIDENCE LANGUAGE
-----------------------------------
- MUST strictly follow:
  >0.95 → "strongly suggestive of"
  0.85–0.95 → "suggestive of"
  <0.85 → "possible"

-----------------------------------
DIFFERENTIAL DIAGNOSIS
-----------------------------------
- MUST NOT include primary diagnosis
- 3–4 alternatives only
- Ranked most → least likely
- Each line ≤10 words
- MUST use imaging-based justification
- Must compare with current pattern (not generic)
- Avoid rare diseases unless strongly supported

-----------------------------------
OUTPUT FORMAT (STRICT)
-----------------------------------
Radiology Report

Findings:
...

Interpretation:
...

Recommendation:
...

Differential Diagnosis:
1. ...
2. ...
3. ...
4. ...

CRITICAL:
- Start EXACTLY with "Radiology Report"
- End EXACTLY after Differential Diagnosis
- No extra text
"""

    messages = [
        SystemMessage(content=system_instruction),
        HumanMessage(content=prompt)
    ]

    response = llm.invoke(messages)
    content = response.content.strip()

    # Hard cleanup
    if "Radiology Report" in content:
        content = content[content.find("Radiology Report"):]

    lines = content.split("\n")
    cleaned_lines = [
        l for l in lines
        if not l.lower().startswith((
            "note:", "i made", "changes:", "explanation:",
            "medical evidence", "step 1", "step 2"
        ))
    ]

    return "\n".join(cleaned_lines)