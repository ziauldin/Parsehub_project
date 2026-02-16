import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

API_KEY = os.getenv('PARSEHUB_API_KEY')
BASE_URL = os.getenv('PARSEHUB_BASE_URL', 'https://www.parsehub.com/api/v2')

# Test with Mann project that has data
run_token = "t-Hh5_Y6TnOU"

url = f"{BASE_URL}/runs/{run_token}/data"
params = {"api_key": API_KEY}

r = requests.get(url, params=params)
data = r.json()

print("Full response keys:", list(data.keys()))
print()

for key in data.keys():
    value = data[key]
    if isinstance(value, list):
        print(f"{key}: LIST with {len(value)} items")
        if len(value) > 0:
            print(f"  First item: {value[0]}")
    elif isinstance(value, dict):
        print(f"{key}: DICT with {len(value)} keys")
        print(f"  Keys: {list(value.keys())}")
    else:
        print(f"{key}: {type(value).__name__} = {value}")
