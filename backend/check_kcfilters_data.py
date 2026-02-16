import json

with open("data_tzJ7P1HcEg4e.json", "r") as f:
    data = json.load(f)

print(f"Response keys: {list(data.keys())}")
print()

for key, value in data.items():
    if isinstance(value, list):
        print(f"{key}: LIST with {len(value)} items")
        if len(value) > 0 and isinstance(value[0], dict):
            print(f"  Sample record: {json.dumps(value[0], indent=2)[:200]}")
    elif isinstance(value, dict):
        print(f"{key}: DICT with keys: {list(value.keys())}")
    else:
        print(f"{key}: {type(value).__name__} (length: {len(str(value))})")
