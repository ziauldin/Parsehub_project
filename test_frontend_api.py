#!/usr/bin/env python
"""Test frontend API endpoint directly"""
import requests
import json

print("Testing frontend /api/projects endpoint...")
try:
    r = requests.get("http://localhost:3000/api/projects", timeout=180)  # 180 seconds for pagination
    print(f"Status: {r.status_code}")
    
    data = r.json()
    projects = data.get('projects', [])
    
    print(f"\nFrontend response:")
    print(f"  - Projects count: {len(projects)}")
    print(f"  - total_count: {data.get('total_count')}")
    print(f"  - Response keys: {list(data.keys())}")
    
    if projects:
        print(f"\nProjects from frontend (first 5):")
        for i, p in enumerate(projects[:5], 1):
            title = p.get('title') or p.get('name', 'Unknown')
            print(f"  {i}. {title}")
    
    if len(projects) == 109:
        print(f"\n[SUCCESS] Frontend is returning all 109 projects!")
    else:
        print(f"\n[INFO] Frontend returning {len(projects)} projects")
        if len(projects) < 50:
            print("\nFull response:")
            print(json.dumps(data, indent=2)[:1000])
        
except requests.Timeout:
    print("ERROR: Frontend API timed out after 35 seconds")
except Exception as e:
    print(f"ERROR: {e}")
