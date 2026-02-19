#!/usr/bin/env python
import sys
import time
import requests

time.sleep(3)  # Wait for server

try:
    print('Testing /api/projects endpoint with 30s timeout...')
    start = time.time()
    response = requests.get('http://localhost:5000/api/projects', timeout=30)
    elapsed = time.time() - start
    
    print(f'Status: {response.status_code} (took {elapsed:.2f}s)')
    
    if response.status_code == 200:
        data = response.json()
        metadata_matches = data.get('metadata_matches', 0)
        total = data.get('total', 0)
        
        print(f'\nTotal projects: {total}')
        print(f'Metadata matches: {metadata_matches}')
        if total > 0:
            match_pct = 100 * metadata_matches / total
            print(f'Match percentage: {match_pct:.1f}%')
        
        by_website = data.get('by_website', [])
        print(f'Website groups: {len(by_website)}')
        
        # Show first 2 projects with metadata
        if by_website:
            print('\nFirst 2 projects with metadata:')
            count = 0
            for group in by_website[:3]:
                website = group.get('website', '?')
                projects = group.get('projects', [])
                for proj in projects:
                    if proj.get('metadata') and count < 2:
                        print(f'\n  {website}:')
                        print(f'    Title: {proj.get("title", "?")[:50]}...')
                        meta = proj['metadata']
                        print(f'    Region: {meta.get("region", "?")}')
                        print(f'    Country: {meta.get("country", "?")}')
                        print(f'    Brand: {meta.get("brand", "?")}')
                        count += 1
    else:
        print(f'Error: {response.status_code}')
        print(f'Response: {response.text[:200]}')
except Exception as e:
    print(f'Error: {str(e)}')
