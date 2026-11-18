import pandas as pd
from sklearn.metrics import accuracy_score, classification_report
from llm_classifier import classify_all
from qpg import classify as rule_classify, LEVELS

df = pd.read_csv("hard_test.csv")
df["id"] = [f"H{i:02d}" for i in range(1, len(df) + 1)]
rows = [{"id": r.id, "text": r.question} for r in df.itertuples()]

llm = classify_all(rows, rule_fallback=rule_classify)
print(f"LLM answered {sum(v['source'] == 'llm' for v in llm.values())}/{len(rows)} questions")

df["rule"] = df.question.apply(rule_classify)
df["llm"] = df.id.map(lambda i: llm[i]["level"])

for name in ["rule", "llm"]:
    print(f"\n=== {name}: {accuracy_score(df.true_bloom_level, df[name]):.2%}")
    print(classification_report(df.true_bloom_level, df[name], labels=LEVELS, zero_division=0))

print("\n--- Questions the LLM got wrong ---")
for r in df[df.llm != df.true_bloom_level].itertuples():
    print(f"[true={r.true_bloom_level} | llm={r.llm} | rule={r.rule}] {r.question}")