#!/usr/bin/env python
"""Test project caching"""
import requests
import time

print('Testing project fetch with caching...\n')

# First request - should fetch from API (slow)
print('Request 1 (cache miss - fetching from API):')
start = time.time()
r1 = requests.get('http://localhost:5000/api/projects', timeout=180)
elapsed1 = time.time() - start
data1 = r1.json()
print(f'  Status: {r1.status_code}')
print(f'  Projects: {len(data1.get("projects", []))}')
print(f'  Time: {elapsed1:.2f}s\n')

time.sleep(1)

# Second request - should return from cache (fast)
print('Request 2 (cache hit - same 5-minute window):')
start = time.time()
r2 = requests.get('http://localhost:5000/api/projects', timeout=30)
elapsed2 = time.time() - start
data2 = r2.json()
print(f'  Status: {r2.status_code}')
print(f'  Projects: {len(data2.get("projects", []))}')
print(f'  Time: {elapsed2:.2f}s\n')

if elapsed2 < 1:
    print(f'✅ Caching working! Speed improvement: {elapsed1/elapsed2:.1f}x faster (from {elapsed1:.1f}s to {elapsed2:.1f}s)')
else:
    print(f'⚠️ Cache may not be working - second request still slow ({elapsed2:.1f}s)')
