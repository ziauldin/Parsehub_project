#!/usr/bin/env python3
import requests
import time
from io import BytesIO

time.sleep(1)

# Create a dummy Excel file content
dummy_xlsx = BytesIO(b'PK\x03\x04\x14\x00\x00\x00\x08\x00')

# Test direct backend POST with file
print("Testing backend import endpoint with file...")
response = requests.post(
    'http://localhost:5000/api/metadata/import',
    headers={'Authorization': 'Bearer t_hmXetfMCq3'},
    files={'file': ('test.xlsx', dummy_xlsx, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')},
    timeout=5
)

print(f'Status: {response.status_code}')
print(f'Content-Type: {response.headers.get("content-type")}')
print(f'Response: {response.text[:500]}')
