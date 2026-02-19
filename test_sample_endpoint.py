#!/usr/bin/env python
import sys
import time
import requests

time.sleep(3)  # Wait for server

try:
    print('Testing /api/projects-sample endpoint...')
    start = time.time()
    response = requests.get('http://localhost:5000/api/projects-sample', timeout=30)
    elapsed = time.time() - start
    
    print(f'Status: {response.status_code} (took {elapsed:.2f}s)')
    
    if response.status_code == 200:
        data = response.json()
        total = data.get('total', 0)
        metadata_matches = data.get('metadata_matches', 0)
        
        print(f'\nTotal projects: {total}')
        print(f'Metadata matches: {metadata_matches}')
        if total > 0:
            match_pct = 100 * metadata_matches / total
            print(f'Match percentage: {match_pct:.1f}%')
        
        projects = data.get('projects', [])
        
        # Show projects with metadata
        print('\nProjects with metadata:')
        count = 0
        for proj in projects:
            if proj.get('metadata') and count < 3:
                meta = proj['metadata']
                print(f'\n  Title: {proj.get("title", "?")[:50]}...')
                print(f'    Website: {meta.get("website_url", "?")}')
                print(f'    Region: {meta.get("region", "?")}')
                print(f'    Country: {meta.get("country", "?")}')
                count += 1
    else:
        print(f'Error: {response.status_code}')
        print(f'Response: {response.text[:200]}')
except Exception as e:
    print(f'Error: {str(e)}')
