#!/usr/bin/env python
import sys
import time
sys.path.insert(0, 'backend')

from database import ParseHubDatabase
from api_server import get_all_projects_with_cache
import os

db = ParseHubDatabase()

# Get all projects with longer timeout
api_key = os.getenv('PARSEHUB_API_KEY') or 't_hmXetfMCq3'

print('Getting projects from API...')
start = time.time()
projects = get_all_projects_with_cache(api_key)
fetch_time = time.time() - start
print(f'  Fetched {len(projects)} projects in {fetch_time:.2f}s')

# Test batch metadata matching
print('\nTesting batch metadata matching...')
start = time.time()
projects = db.match_projects_to_metadata_batch(projects)
batch_time = time.time() - start
print(f'  Matched in {batch_time:.2f}s')

# Count matches
metadata_matches = sum(1 for p in projects if p.get('metadata'))
print(f'\nMetadata matches: {metadata_matches}/{len(projects)}')

# Show first 3 projects with metadata
print('\nFirst 3 projects with metadata:')
count = 0
for proj in projects:
    if proj.get('metadata') and count < 3:
        meta = proj['metadata']
        print(f'\n  Project: {proj.get("title", "?")[:50]}...')
        print(f'    Website: {meta.get("website_url", "?")}')
        print(f'    Region: {meta.get("region", "?")}')
        print(f'    Country: {meta.get("country", "?")}')
        count += 1

print(f'\nTotal processing time: {fetch_time + batch_time:.2f}s')
