#!/usr/bin/env python
import sys
sys.path.insert(0, 'backend')

from api_server import get_all_projects_with_cache
from database import ParseHubDatabase
import os
import re

db = ParseHubDatabase()

# Get all projects
api_key = os.getenv('PARSEHUB_API_KEY') or 't_hmXetfMCq3'
projects = get_all_projects_with_cache(api_key)

# Extract unique websites
websites = set()
for proj in projects:
    title = proj.get('title', '')
    website = db.extract_website_from_title(title)
    if website and website != 'Unknown':
        websites.add(website)

print(f'Found {len(websites)} unique websites')

# Take first 5 websites for sample metadata
conn = db._get_connection()
cursor = conn.cursor()

# Clear existing metadata (keep original test data)
# cursor.execute('DELETE FROM metadata WHERE id > 3')

# Add metadata for websites
updated = 0
for i, website in enumerate(list(sorted(websites))[:10]):
    project_name = website
    region = ['EMENA', 'APAC', 'Americas'][i % 3]
    country = ['Germany', 'Australia', 'USA', 'UK'][i % 4]
    brand = f'Brand-{website.split(".")[0]}'
    website_url = website
    status = 'active'
    
    try:
        cursor.execute('''
            INSERT INTO metadata 
            (personal_project_id, project_name, region, country, brand, website_url, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (f'proj_{i:03d}', project_name, region, country, brand, website_url, status))
        updated += 1
        print(f'Added metadata for {website} ({region}, {country})')
    except Exception as e:
        print(f'Error adding metadata for {website}: {e}')

conn.commit()

print(f'\nAdded {updated} metadata records')

# Verify
cursor.execute('SELECT COUNT(*) FROM metadata')
total = cursor.fetchone()[0]
print(f'Total metadata records now: {total}')

conn.close()
