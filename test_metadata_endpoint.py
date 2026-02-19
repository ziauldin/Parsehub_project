#!/usr/bin/env python3
import requests
import time

time.sleep(2)

# Test the metadata import endpoint
print("Testing metadata import endpoint...")
response = requests.post(
    'http://localhost:5000/api/metadata/import',
    headers={'Authorization': 'Bearer t_hmXetfMCq3'},
    timeout=5
)

print(f'Status: {response.status_code}')
print(f'Content-Type: {response.headers.get("content-type")}')
print(f'Response: {response.text}')
