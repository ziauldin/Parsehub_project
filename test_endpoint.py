#!/usr/bin/env python
"""Quick test of the projects endpoint"""
import requests
import json

try:
    print("Testing /api/projects endpoint...")
    response = requests.get(
        'http://localhost:5000/api/projects',
        params={'api_key': 't_hmXetfMCq3'},
        timeout=15
    )
    
    print(f"Status Code: {response.status_code}")
    data = response.json()
    
    total = data.get('total_count', 0)
    projects = data.get('projects', [])
    
    print(f"✅ Total Projects Returned: {total}")
    print(f"✅ Projects Count: {len(projects)}")
    
    if projects:
        print(f"\nFirst 3 projects:")
        for i, proj in enumerate(projects[:3], 1):
            print(f"  {i}. {proj.get('name', 'Unknown')} (ID: {proj.get('id')})")
    
    if len(projects) > 20:
        print(f"✅ SUCCESS! Got more than 20 projects (previously limited to 20)")
    else:
        print(f"⚠️  Only got {len(projects)} projects")
        
except Exception as e:
    print(f"❌ Error: {e}")
