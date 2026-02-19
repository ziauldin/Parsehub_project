#!/usr/bin/env python
import sys
sys.path.insert(0, 'backend')

from database import ParseHubDatabase

db = ParseHubDatabase()

# Check the metadata table schema
conn = db._get_connection()
cursor = conn.cursor()

# Get column names
cursor.execute("PRAGMA table_info(metadata)")
columns = cursor.fetchall()

print('Metadata table columns:')
for i, col in enumerate(columns):
    print(f'  {i}: {col[1]} ({col[2]})')

# Get one full record to see all the data
cursor.execute('SELECT * FROM metadata LIMIT 1')
row = cursor.fetchone()

if row:
    print('\nFirst metadata record:')
    for i, col in enumerate(columns):
        col_name = col[1]
        col_value = row[i] if i < len(row) else None
        print(f'  {col_name}: {col_value}')

# Check how many records we have
cursor.execute('SELECT COUNT(*) FROM metadata')
total = cursor.fetchone()[0]
print(f'\nTotal metadata records: {total}')

conn.close()
