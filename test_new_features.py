#!/usr/bin/env python3
import requests
import time
import json

time.sleep(1)

print("=" * 70)
print("TESTING PROJECT SYNC AND SEARCH IMPLEMENTATION")
print("=" * 70)

API_KEY = "t_hmXetfMCq3"
BASE_URL = "http://localhost:5000"

# Test 1: Sync projects
print("\n[TEST 1] Syncing projects from ParseHub to database...")
print("-" * 70)

try:
    response = requests.post(
        f"{BASE_URL}/api/projects/sync",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={},
        timeout=120
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if response.status_code == 200:
        print("✅ Sync endpoint working!")
        sync_result = data
    else:
        print("❌ Sync endpoint failed!")
        sync_result = None
        
except Exception as e:
    print(f"❌ Error: {e}")
    sync_result = None

# Test 2: Search projects without filters
print("\n[TEST 2] Searching projects (no filters)...")
print("-" * 70)

try:
    response = requests.get(
        f"{BASE_URL}/api/projects/search",
        headers={"Authorization": f"Bearer {API_KEY}"},
        params={"limit": 10},
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    print(f"Total projects in DB: {data.get('total', 0)}")
    print(f"Projects returned: {len(data.get('projects', []))}")
    
    if data.get('projects') and len(data['projects']) > 0:
        first_project = data['projects'][0]
        print(f"\nFirst project:")
        print(f"  - Token: {first_project.get('token')}")
        print(f"  - Title: {first_project.get('title')}")
        print(f"  - Metadata linked: {len(first_project.get('metadata', []))}")
        
        if first_project.get('metadata'):
            print(f"  - First metadata:")
            m = first_project['metadata'][0]
            print(f"    - Region: {m.get('region')}")
            print(f"    - Country: {m.get('country')}")
            print(f"    - Brand: {m.get('brand')}")
        
        print("✅ Search endpoint working!")
    else:
        print("⚠️  No projects found in database")
        print("(This is expected if you haven't synced yet)")
        
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Search projects with filters
print("\n[TEST 3] Searching projects with filters...")
print("-" * 70)

try:
    response = requests.get(
        f"{BASE_URL}/api/projects/search",
        headers={"Authorization": f"Bearer {API_KEY}"},
        params={"region": "North America", "limit": 10},
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    print(f"Filtered projects returned: {len(data.get('projects', []))}")
    print("✅ Filtered search working!")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("TESTING COMPLETE")
print("=" * 70)
