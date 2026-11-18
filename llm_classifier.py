import os, json, requests

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-oss-20b"
LEVELS = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]

SYSTEM_PROMPT = """You are an expert in educational assessment. Classify each exam question
into exactly one level of Bloom's Taxonomy (revised):

- Remember: recall facts, definitions, terms (define, list, state, name)
- Understand: explain ideas or concepts in own words (explain, describe, summarize, classify)
- Apply: use knowledge in a new situation, solve, trace, implement (solve, compute, demonstrate)
- Analyze: break into parts, compare, find relationships (compare, differentiate, examine)
- Evaluate: judge, justify, critique, choose with reasons (justify, assess, critique)
- Create: design, build, propose something new (design, construct, develop, formulate)

Judge by the cognitive skill the question demands, not just its first word.
For MCQ / fill-in-the-blank, judge the skill needed to answer, not the format.

Reply with JSON only, in this form:
{"results": [{"id": <id>, "level": "<one of the six>", "confidence": <0-1>, "reason": "<max 12 words>"}]}"""


def classify_batch(questions, api_key=None, model=DEFAULT_MODEL):
    """questions: list of {"id": ..., "text": str}. Returns {id: {level, confidence, reason}}."""
    api_key = api_key or os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")

    user_msg = json.dumps([{"id": q["id"], "question": q["text"]} for q in questions])
    resp = requests.post(
        GROQ_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = json.loads(resp.json()["choices"][0]["message"]["content"])

    out = {}
    for r in data.get("results", []):
        level = str(r.get("level", "")).strip().capitalize()
        if level in LEVELS:
            out[r["id"]] = {
                "level": level,
                "confidence": float(r.get("confidence", 0.5)),
                "reason": r.get("reason", ""),
            }
    return out


def classify_all(questions, rule_fallback=None, batch_size=15, **kw):
    """Classify many questions. Falls back to rule_fallback(text) if the LLM fails or
    skips a question. Returns {id: {level, confidence, source, reason}}."""
    results = {}
    for i in range(0, len(questions), batch_size):
        batch = questions[i:i + batch_size]
        try:
            llm = classify_batch(batch, **kw)
        except Exception as e:
            print("LLM batch failed:", e)
            llm = {}
        for q in batch:
            if q["id"] in llm:
                results[q["id"]] = {**llm[q["id"]], "source": "llm"}
            elif rule_fallback:
                results[q["id"]] = {"level": rule_fallback(q["text"]),
                                    "confidence": 0.5, "source": "rule", "reason": ""}
    return results