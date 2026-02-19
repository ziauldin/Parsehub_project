#!/usr/bin/env python
"""Inspect the actual projects API response"""
import requests
import json

try:
    response = requests.get(
        'http://localhost:5000/api/projects',
        params={'api_key': 't_hmXetfMCq3'},
        timeout=15
    )
    
    data = response.json()
    print("Full Response:")
    print(json.dumps(data, indent=2)[:2000])  # Print first 2000 chars
    
except Exception as e:
    print(f"Error: {e}")
