#!/usr/bin/env python
import sys
sys.path.insert(0, 'backend')

try:
    from database import ParseHubDatabase
    
    db = ParseHubDatabase()
    print('Database connected successfully')
    
    # Test the match_project_to_metadata method
    test_title = '(MSA Pricing) Filter-technik.de_Hydraulikfilterelemente 16/2'
    metadata = db.match_project_to_metadata(test_title)
    print(f'Test metadata match for title: {test_title[:50]}...')
    if metadata:
        print('  MATCHED:')
        print(f'    project_name: {metadata.get("project_name", "?")}')
        print(f'    region: {metadata.get("region", "?")}')
        print(f'    country: {metadata.get("country", "?")}')
        print(f'    brand: {metadata.get("brand", "?")}')
    else:
        print('  NO MATCH FOUND')
        
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
