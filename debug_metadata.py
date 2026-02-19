#!/usr/bin/env python
import sys
import re
sys.path.insert(0, 'backend')

from database import ParseHubDatabase

db = ParseHubDatabase()

# Check what project names exist in metadata
conn = db._get_connection()
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM metadata')
total = cursor.fetchone()[0]
print(f'Total metadata records: {total}')

cursor.execute('SELECT project_name FROM metadata LIMIT 10')
names = cursor.fetchall()
print('\nSample project names in metadata:')
for name in names:
    print(f'  - {name[0]}')

# Test the extraction with a real project title
test_title = '(MSA Pricing) Filter-technik.de_Hydraulikfilterelemente 16/2'
print(f'\nTesting extraction with: {test_title}')

# Show what the regex extracts
match = re.search(r'\)\s*([a-zA-Z0-9._-]+(?:_[a-zA-Z0-9._-]+)*)', test_title)
if match:
    extracted = match.group(1)
    print(f'Extracted project name: {extracted}')
    print(f'Extracted (lowercase): {extracted.lower()}')
    
    # Try to find in metadata
    cursor.execute('SELECT project_name FROM metadata WHERE LOWER(project_name) = ?', (extracted.lower(),))
    result = cursor.fetchone()
    if result:
        print(f'Found matching metadata: {result[0]}')
    else:
        print('No exact match found')
        
        # Try partial match
        cursor.execute('SELECT project_name FROM metadata WHERE LOWER(project_name) LIKE ? LIMIT 5', (f'{extracted.lower()}%',))
        results = cursor.fetchall()
        if results:
            print(f'Found {len(results)} partial matches:')
            for r in results:
                print(f'  - {r[0]}')
        else:
            print('No partial matches found')
else:
    print('Regex did not match - extraction failed')

conn.close()
