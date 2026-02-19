#!/usr/bin/env python3
import requests
import json

print("=" * 70)
print("TESTING PROJECT SYNC AND SEARCH WITH FILTERS")
print("=" * 70)

# Test 1: Get all projects
print("\n[TEST 1] Get all projects from database...")
try:
    response = requests.get(
        'http://localhost:5000/api/projects/search',
        headers={'Authorization': 'Bearer t_hmXetfMCq3'},
        params={'limit': 5},
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if data.get('success'):
        print(f"Total projects: {data.get('total')}")
        print(f"Returned: {len(data.get('projects', []))}")
    else:
        print(f"ERROR: {data.get('error')}")
except Exception as e:
    print(f"Exception: {e}")

# Test 2: Filter by Region
print("\n[TEST 2] Filter by Region (APAC)...")
try:
    response = requests.get(
        'http://localhost:5000/api/projects/search',
        headers={'Authorization': 'Bearer t_hmXetfMCq3'},
        params={'region': 'APAC', 'limit': 5},
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if data.get('success'):
        projects = data.get('projects', [])
        print(f"Projects with APAC region: {len(projects)}")
        if projects:
            for i, p in enumerate(projects[:2]):
                print(f"  {i+1}. {p.get('title')}")
    else:
        print(f"ERROR: {data.get('error')}")
except Exception as e:
    print(f"Exception: {e}")

# Test 3: Filter by Brand
print("\n[TEST 3] Filter by Brand (Fleetguard)...")
try:
    response = requests.get(
        'http://localhost:5000/api/projects/search',
        headers={'Authorization': 'Bearer t_hmXetfMCq3'},
        params={'brand': 'Fleetguard', 'limit': 5},
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if data.get('success'):
        projects = data.get('projects', [])
        print(f"Projects with Fleetguard brand: {len(projects)}")
        if projects:
            for i, p in enumerate(projects[:2]):
                print(f"  {i+1}. {p.get('title')}")
    else:
        print(f"ERROR: {data.get('error')}")
except Exception as e:
    print(f"Exception: {e}")

# Test 4: Multiple filters
print("\n[TEST 4] Filter by Region + Country...")
try:
    response = requests.get(
        'http://localhost:5000/api/projects/search',
        headers={'Authorization': 'Bearer t_hmXetfMCq3'},
        params={'region': 'APAC', 'country': 'Australia', 'limit': 5},
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if data.get('success'):
        projects = data.get('projects', [])
        print(f"Projects (APAC + Australia): {len(projects)}")
        if projects:
            for i, p in enumerate(projects[:2]):
                metadata = p.get('metadata', [])
                region = metadata[0].get('region') if metadata else 'None'
                country = metadata[0].get('country') if metadata else 'None'
                print(f"  {i+1}. {p.get('title')}")
                print(f"     Region: {region}, Country: {country}")
    else:
        print(f"ERROR: {data.get('error')}")
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "=" * 70)
print("ALL TESTS COMPLETE")
print("=" * 70)
