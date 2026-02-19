#!/usr/bin/env python
"""Check ParseHub API response"""
import requests

# Check what ParseHub returns directly with the current API key
api_key = 't4oahuH8vOki'
r = requests.get('https://www.parsehub.com/api/v2/projects', params={'api_key': api_key}, timeout=10)
data = r.json()
print(f'ParseHub API direct call:')
print(f'  Projects returned: {len(data.get("projects", []))}')
print(f'  Total projects: {data.get("total_projects", "N/A")}')

# Now test the backend
print(f'\nBackend /api/projects call:')
r = requests.get('http://localhost:5000/api/projects', timeout=180)
data = r.json()
print(f'  Projects returned: {len(data.get("projects", []))}')
print(f'  Total count: {data.get("total_count", "N/A")}')
