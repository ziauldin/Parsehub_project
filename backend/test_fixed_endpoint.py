import requests
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

API_KEY = os.getenv('PARSEHUB_API_KEY')
BASE_URL = os.getenv('PARSEHUB_BASE_URL', 'https://www.parsehub.com/api/v2')

def get_project_data(token):
    """Get project details including last run info"""
    url = f"{BASE_URL}/projects/{token}"
    params = {"api_key": API_KEY}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def fetch_run_data(token, run_token):
    """Fetch data from a specific run - FIXED ENDPOINT"""
    url = f"{BASE_URL}/runs/{run_token}/data"
    params = {"api_key": API_KEY}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

print("[*] Running FAST monitoring with CORRECTED endpoint\n")

with open("active_runs.json", "r") as f:
    active = json.load(f)

print("=" * 70)

for run in active["runs"]:
    token = run["token"]
    project = run["project"]
    run_token = run["run_token"]
    
    print(f"\nTesting: {project}")
    print(f"  Token: {token}")
    print(f"  Run Token: {run_token}")
    
    # Get project status
    project_info = get_project_data(token)
    if "error" in project_info:
        print(f"  ERROR: {project_info['error']}")
        continue
    
    last_run = project_info.get("last_run", {})
    status = last_run.get("status")
    pages = last_run.get("pages", 0)
    is_empty = last_run.get("is_empty", False)
    
    print(f"  Status: {status} | Pages: {pages} | Empty: {is_empty}")
    
    if status == "complete" and not is_empty:
        print(f"  [+] Has data - Fetching...")
        
        # Try to fetch data
        data = fetch_run_data(token, run_token)
        
        if "error" not in data:
            # Success
            filename = f"data_{token}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            records = len(data.get("product", []))
            print(f"  [SUCCESS] Saved {records} records to {filename}")
        else:
            print(f"  [FAILED] {data['error']}")
    else:
        print(f"  [SKIP] No data to fetch")

print("\n" + "=" * 70)
print("[*] Done!")
