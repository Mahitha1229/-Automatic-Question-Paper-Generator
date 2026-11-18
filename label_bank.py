from db import init_db, load_raw, save_raw
from llm_classifier import classify_all
from qpg import classify

init_db()
df = load_raw("sample")
rows = [{"id": r.id, "text": r.question} for r in df.itertuples()]
res = classify_all(rows, rule_fallback=classify)

done = 0
for qid, r in res.items():
    if r["source"] == "llm":
        m = df.id == qid
        df.loc[m, "bloom_level"] = r["level"]
        df.loc[m, "bloom_confidence"] = r["confidence"]
        df.loc[m, "bloom_source"] = "llm"
        done += 1
save_raw(df, "sample")
print(f"Saved LLM labels for {done}/{len(rows)} questions")