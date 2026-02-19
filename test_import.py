#!/usr/bin/env python
import sys
sys.path.insert(0, 'backend')

try:
    print('Importing Flask app...')
    from api_server import app, db
    print('✓ App imported successfully')
    print('✓ Database imported successfully')
    print(f'✓ Routes: {len(app.url_map._rules)}')
    print('✓ Ready to start')
    
    # Test database connection
    print('\nTesting database...')
    all_metadata = db.get_all_metadata_by_website()
    print(f'✓ Metadata loaded: {len(all_metadata)} entries')
    
except Exception as e:
    print(f'✗ Error: {e}')
    import traceback
    traceback.print_exc()
