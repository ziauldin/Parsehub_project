import requests
import json
from dotenv import load_dotenv
import os

load_dotenv('backend/.env')

api_key = 't4oahuH8vOki'  # Using the key you want all projects from
url = 'https://www.parsehub.com/api/v2/projects'

print('Testing ParseHub API pagination:')
print('='*60)
print()

# Test 1: No parameters
print('1. No limit parameter:')
r1 = requests.get(url, params={'api_key': api_key}, timeout=10)
data1 = r1.json()
count1 = len(data1.get('projects', []))
print(f'   Projects returned: {count1}')
print(f'   Response keys: {list(data1.keys())}')
print()

# Test 2: With limit=1000
print('2. With limit=1000:')
r2 = requests.get(url, params={'api_key': api_key, 'limit': 1000}, timeout=10)
data2 = r2.json()
count2 = len(data2.get('projects', []))
print(f'   Projects returned: {count2}')
print()

# Test 3: Check if offset works
print('3. With offset=0, limit=1000:')
r3 = requests.get(url, params={'api_key': api_key, 'offset': 0, 'limit': 1000}, timeout=10)
data3 = r3.json()
count3 = len(data3.get('projects', []))
print(f'   Projects returned: {count3}')
print()

# Show if there's pagination metadata
if 'offset' in data1 or 'limit' in data1 or 'total' in data1:
    print('4. Pagination metadata in response:')
    for key in ['offset', 'limit', 'total', 'total_count']:
        if key in data1:
            print(f'   {key}: {data1[key]}')
else:
    print('4. No pagination metadata found in response')
    print(f'   Full response keys: {data1.keys()}')

print()
print('='*60)
print(f'Summary: API with t4oahuH8vOki returns {count1} projects')
