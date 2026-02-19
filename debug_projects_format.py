#!/usr/bin/env python
import requests
import json

# Test /api/projects endpoint
response = requests.get(
    'http://localhost:5000/api/projects?limit=3',
    headers={'Authorization': 'Bearer t_hmXetfMCq3'},
    timeout=10
)

print(f"Status: {response.status_code}\n")

if response.status_code == 200:
    data = response.json()
    print(f"Total projects: {data.get('total')}")
    print(f"Projects returned: {len(data.get('projects', []))}\n")
    
    # Show first 3 projects in detail
    for i, proj in enumerate(data.get('projects', [])[:3], 1):
        print(f"Project {i}:")
        print(f"  Title: {proj.get('title', 'N/A')}")
        print(f"  Token: {proj.get('token', 'N/A')[:40]}")
        print()
else:
    print(f"Error: {response.text[:500]}")
