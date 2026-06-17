import json

with open(".secrets.baseline") as f:
    data = json.load(f)

for filename, secrets in data.get("results", {}).items():
    for secret in secrets:
        if not secret.get("is_verified", False):
            print(f"{filename}:{secret.get('line_number')}")
