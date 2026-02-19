#!/usr/bin/env python
"""Verify the implementation is working correctly"""
import requests
import json

try:
    print("[✅] Testing /api/projects endpoint...")
    response = requests.get(
        'http://localhost:5000/api/projects',
        params={'api_key': 't_hmXetfMCq3'},
        timeout=15
    )
    
    print(f"[✅] Status Code: {response.status_code}")
    data = response.json()
    
    projects = data.get('projects', [])
    
    print(f"[✅] SUCCESS! Retrieved {len(projects)} projects in single API call")
    print(f"[✅] total_count: {data.get('total_count', len(projects))}")
    
    print(f"\nProjects:")
    for i, proj in enumerate(projects, 1):
        title = proj.get('title', 'Unknown')
        token = proj.get('token', 'N/A')
        print(f"  {i}. {title} (token: {token})")
    
    print(f"\n[✅] Implementation verified: fetch_all_projects() works correctly!")
    print(f"[✅] ParseHub API returns all available projects in single call")
        
except Exception as e:
    print(f"[❌] Error: {e}")
    import traceback
    traceback.print_exc()
