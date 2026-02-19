#!/usr/bin/env python
"""Inspect project structure"""
import requests
import json

try:
    response = requests.get(
        'http://localhost:5000/api/projects',
        params={'api_key': 't_hmXetfMCq3'},
        timeout=15
    )
    
    data = response.json()
    projects = data.get('projects', [])
    
    print(f"Total projects: {len(projects)}")
    
    if projects:
        first_project = projects[0]
        print(f"\nFirst project keys: {list(first_project.keys())}")
        
        # Check for name/title fields
        for key in ['name', 'title', 'project_name']:
            if key in first_project:
                print(f"  {key}: {first_project[key]}")
    
except Exception as e:
    print(f"Error: {e}")
