#!/usr/bin/env python3
import requests
import time

time.sleep(1)

# Test through frontend proxy
print("Testing metadata import through frontend proxy...")
response = requests.post(
    'http://localhost:3000/api/metadata/import',
    headers={'Authorization': 'Bearer t_hmXetfMCq3'},
    timeout=5
)

print(f'Status: {response.status_code}')
print(f'Content-Type: {response.headers.get("content-type")}')
print(f'Response: {response.text[:500]}')
