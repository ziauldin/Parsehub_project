import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

API_KEY = os.getenv('PARSEHUB_API_KEY')
BASE_URL = os.getenv('PARSEHUB_BASE_URL', 'https://www.parsehub.com/api/v2')

with open("active_runs.json", "r") as f:
    active = json.load(f)

# Get Mann_Project
mann_run = None
for run in active["runs"]:
    if "Mann_Project" in run["project"]:
        mann_run = run
        break

if not mann_run:
    print("Error: Could not find Mann_Project")
    exit(1)

print(f"Fetching full project details for: {mann_run['project']}")
print(f"Token: {mann_run['token']}\n")

url = f"{BASE_URL}/projects/{mann_run['token']}"
params = {"api_key": API_KEY}
r = requests.get(url, params=params)

if r.status_code == 200:
    data = r.json()
    
    print("=" * 80)
    print("FULL PROJECT RESPONSE (pretty printed):")
    print("=" * 80)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("\n" + "=" * 80)
    
    # Look for download URLs or data links
    full_str = json.dumps(data)
    if "http" in full_str:
        print("\nFOUND URLS IN RESPONSE:")
        for line in full_str.split(","):
            if "http" in line:
                print(f"  {line.strip()}")
else:
    print(f"Error: {r.status_code}")
