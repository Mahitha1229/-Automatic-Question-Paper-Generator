import os, requests

r = requests.get("https://api.groq.com/openai/v1/models",
                 headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"}, timeout=30)
print(r.status_code)
for m in r.json().get("data", []):
    print(m["id"])