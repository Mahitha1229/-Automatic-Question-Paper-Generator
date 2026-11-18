from sklearn.metrics import accuracy_score, classification_report
from db import load_raw
from llm_classifier import classify_all
from qpg import classify as rule_classify, LEVELS

df = load_raw("sample").dropna(subset=["true_bloom_level"]).copy()
if df.empty:
    raise SystemExit("No labelled questions found. Run 'python server.py' once first "
                     "so the database gets created from questions.csv.")

rows = [{"id": r.id, "text": r.question} for r in df.itertuples()]
llm = classify_all(rows, rule_fallback=rule_classify)
print(f"LLM answered {sum(v['source'] == 'llm' for v in llm.values())}/{len(rows)} questions")

df["rule"] = df.question.apply(rule_classify)
df["llm"] = df.id.map(lambda i: llm[i]["level"])

for name in ["rule", "llm"]:
    print(f"\n=== {name}: {accuracy_score(df.true_bloom_level, df[name]):.2%}")
    print(classification_report(df.true_bloom_level, df[name], labels=LEVELS, zero_division=0))