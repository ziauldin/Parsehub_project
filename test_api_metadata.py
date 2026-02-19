#!/usr/bin/env python
import sys
import time
import requests
import json

time.sleep(2)  # Wait for server to start

try:
    response = requests.get('http://localhost:5000/api/projects', timeout=10)
    print(f'Status: {response.status_code}')
    
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
        
        # Show first 3 projects with metadata
        if by_website:
            print('\nFirst 3 projects:')
            for i, group in enumerate(by_website[:2]):
                website = group.get('website', '?')
                projects = group.get('projects', [])
                if projects:
                    for j, proj in enumerate(projects[:2]):
                        print(f'\n  {website} - Project {j+1}:')
                        print(f'    Title: {proj.get("title", "?")[:60]}...')
                        if proj.get('metadata'):
                            meta = proj['metadata']
                            print(f'    Metadata:')
                            print(f'      Region: {meta.get("region", "?")}')
                            print(f'      Country: {meta.get("country", "?")}')
                            print(f'      Brand: {meta.get("brand", "?")}')
                        else:
                            print(f'    Metadata: NO')
    else:
        print(f'Response text: {response.text[:200]}')
except Exception as e:
    print(f'Error: {str(e)}')
    import traceback
    traceback.print_exc()
