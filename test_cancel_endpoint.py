#!/usr/bin/env python3
"""Test the cancel run endpoint"""

import requests
import json
import os

API_KEY = os.getenv("PARSEHUB_API_KEY", "")
BASE_URL = "http://localhost:5000"
# Match what the backend expects
BACKEND_API_KEY = os.getenv("BACKEND_API_KEY", "t_hmXetfMCq3")

def test_cancel_endpoint():
    """Test the cancel run endpoint"""
    print("Testing cancel run endpoint...")
    print(f"Using API Key: {BACKEND_API_KEY}")
    
    # First, check if we have any running projects
    print("\n1. Getting projects to find a running one...")
    response = requests.get(
        f"{BASE_URL}/api/projects",
        headers={"Authorization": f"Bearer {BACKEND_API_KEY}"}
    )
    
    if response.status_code != 200:
        print(f"Failed to get projects: {response.status_code}")
        print(response.text)
        return
    
    projects = response.json().get("projects", [])
    print(f"Found {len(projects)} projects")
    
    # Look for a running project
    running_project = None
    for project in projects:
        if project.get("last_run", {}).get("status") == "running":
            running_project = project
            break
    
    if not running_project:
        print("No running projects found. Starting a test project first...")
        # Get any project token and start it
        if projects:
            test_token = projects[0].get("token")
            print(f"Starting project {test_token}...")
            
            run_response = requests.post(
                f"{BASE_URL}/api/run",
                json={"token": test_token, "pages": 1},
                headers={"Authorization": f"Bearer {BACKEND_API_KEY}"}
            )
            
            if run_response.status_code == 200:
                run_data = run_response.json()
                running_project = {
                    "token": test_token,
                    "last_run": {
                        "run_token": run_data.get("runToken"),
                        "status": "running"
                    }
                }
                print(f"Started run: {running_project['last_run']['run_token']}")
            else:
                print(f"Failed to start project: {run_response.status_code}")
                print(run_response.text)
                return
    
    if not running_project:
        print("Could not find or start a running project")
        return
    
    run_token = running_project.get("last_run", {}).get("run_token")
    if not run_token:
        print(f"No run_token found for project: {running_project}")
        return
    
    print(f"\n2. Testing cancel endpoint with run_token: {run_token}")
    
    # Test the cancel endpoint
    cancel_response = requests.post(
        f"{BASE_URL}/api/runs/{run_token}/cancel",
        headers={"Authorization": f"Bearer {BACKEND_API_KEY}"}
    )
    
    print(f"Cancel response status: {cancel_response.status_code}")
    print(f"Cancel response: {json.dumps(cancel_response.json(), indent=2)}")
    
    if cancel_response.status_code == 200:
        print("\n✅ Cancel endpoint working correctly!")
    else:
        print(f"\n❌ Cancel endpoint returned error: {cancel_response.status_code}")
    
    return cancel_response.status_code == 200

if __name__ == "__main__":
    try:
        success = test_cancel_endpoint()
        exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
