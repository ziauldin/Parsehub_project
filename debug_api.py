#!/usr/bin/env python
"""Debug what the backend is returning"""
import requests
import json

print("Testing backend /api/projects endpoint...")
response = requests.get(
    'http://localhost:5000/api/projects',
    timeout=120  # Increased timeout for pagination through all projects
)

data = response.json()
projects = data.get('projects', [])

print(f'\n📊 Backend Response:')
print(f'  - Total projects: {len(projects)}')
print(f'  - Response keys: {list(data.keys())}')
print(f'  - total_count field: {data.get("total_count")}')

if projects:
    print(f'\nFirst 5 projects:')
    for i, p in enumerate(projects[:5], 1):
        title = p.get('title') or p.get('name', 'Unknown')
        print(f'  {i}. {title}')
        
# Also check what ParseHub API directly returns
print('\n\n🔗 Testing ParseHub API directly with t4oahuH8vOki...')
ph_response = requests.get(
    'https://www.parsehub.com/api/v2/projects',
    params={'api_key': 't4oahuH8vOki'},
    timeout=15
)

ph_data = ph_response.json()
ph_projects = ph_data.get('projects', [])
ph_total = ph_data.get('total_projects')

print(f'  - ParseHub returns: {len(ph_projects)} projects on first page')
print(f'  - ParseHub total_projects: {ph_total}')

if ph_projects:
    print(f'\nFirst 3 from ParseHub:')
    for i, p in enumerate(ph_projects[:3], 1):
        title = p.get('title') or p.get('name', 'Unknown')
        print(f'  {i}. {title}')

