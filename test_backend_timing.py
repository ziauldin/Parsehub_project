#!/usr/bin/env python
"""Test backend directly multiple times to see response time"""
import requests
import time

api_key = 't_hmXetfMCq3'

for i in range(3):
    start = time.time()
    try:
        r = requests.get(
            'http://localhost:5000/api/projects',
            params={'api_key': api_key},
            timeout=30
        )
        elapsed = time.time() - start
        data = r.json()
        projects = len(data.get('projects', []))
        print(f"[{i+1}] {elapsed:.1f}s - {projects} projects - Status: {r.status_code}")
    except Exception as e:
        elapsed = time.time() - start
        print(f"[{i+1}] {elapsed:.1f}s - ERROR: {e}")
    time.sleep(1)
