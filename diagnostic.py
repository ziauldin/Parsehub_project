#!/usr/bin/env python3
"""
Diagnostic script to verify all API endpoints and database setup
Run: python diagnostic.py
"""

import subprocess
import sys
import json
import requests
from pathlib import Path

def check_backend_running():
    """Check if Flask backend is running"""
    print("\n🔍 Checking Flask Backend...")
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("  ✅ Flask backend is running on http://localhost:5000")
            return True
        else:
            print(f"  ❌ Flask returned {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("  ❌ Flask backend is NOT running")
        print("     Start it with: python backend/api_server.py")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def check_frontend_running():
    """Check if Next.js frontend is running"""
    print("\n🔍 Checking Next.js Frontend...")
    try:
        response = requests.get('http://localhost:3000', timeout=5)
        if response.status_code == 200:
            print("  ✅ Next.js frontend is running on http://localhost:3000")
            return True
        else:
            print(f"  ❌ Frontend returned {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("  ❌ Next.js frontend is NOT running")
        print("     Start it with: npm run dev (in frontend directory)")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def check_database():
    """Check database connection and schema"""
    print("\n🔍 Checking Database...")
    try:
        sys.path.insert(0, 'backend')
        from database import ParseHubDatabase
        
        db = ParseHubDatabase()
        
        # Check tables exist
        conn = db.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['metadata', 'import_batches', 'projects', 'runs']
        missing = [t for t in required_tables if t not in tables]
        
        db.disconnect()
        
        if not missing:
            print(f"  ✅ Database connected. Found {len(tables)} tables")
            print(f"     Required tables: {', '.join(required_tables)}")
            return True
        else:
            print(f"  ❌ Missing tables: {', '.join(missing)}")
            print("     Run: python backend/database.py")
            return False
    except Exception as e:
        print(f"  ❌ Database error: {e}")
        return False

def check_api_endpoints():
    """Check if Flask API endpoints are registered"""
    print("\n🔍 Checking API Endpoints...")
    try:
        sys.path.insert(0, 'backend')
        from api_server import app
        
        required_endpoints = [
            '/api/metadata',
            '/api/metadata/<int:metadata_id>',
            '/api/metadata/import',
            '/api/metadata/import-history',
            '/api/filters/values',
            '/api/health',
        ]
        
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        
        missing = []
        for endpoint in required_endpoints:
            # Flask shows routes differently, need to check pattern
            pattern = endpoint.replace('<int:', '').replace('>', '')
            if not any(pattern in route for route in routes):
                missing.append(endpoint)
        
        if not missing:
            print(f"  ✅ All required endpoints found ({len(required_endpoints)} endpoints)")
            metadata_routes = [r for r in routes if 'metadata' in r]
            print(f"     Metadata routes: {', '.join(sorted(metadata_routes)[:3])}...")
            return True
        else:
            print(f"  ❌ Missing endpoints: {', '.join(missing)}")
            return False
    except Exception as e:
        print(f"  ❌ Error checking endpoints: {e}")
        return False

def check_frontend_routes():
    """Check if Next.js API route files exist"""
    print("\n🔍 Checking Next.js API Routes...")
    
    required_routes = [
        'frontend/app/api/metadata/route.ts',
        'frontend/app/api/metadata/[id]/route.ts',
        'frontend/app/api/import-history/route.ts',
        'frontend/app/api/filters/route.ts',
    ]
    
    missing = []
    for route in required_routes:
        if not Path(route).exists():
            missing.append(route)
    
    if not missing:
        print(f"  ✅ All Next.js route files exist ({len(required_routes)} routes)")
        for route in required_routes:
            print(f"     - {route}")
        return True
    else:
        print(f"  ❌ Missing route files:")
        for route in missing:
            print(f"     - {route}")
        return False

def test_metadata_api():
    """Test metadata API endpoint"""
    print("\n🔍 Testing Metadata API...")
    
    api_key = 't_hmXetfMCq3'
    
    try:
        # Test through Flask backend
        print("  Testing Flask: GET /api/metadata...")
        response = requests.get(
            'http://localhost:5000/api/metadata?limit=1',
            headers={'Authorization': f'Bearer {api_key}'},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"    ✅ Flask returned {data.get('count', 0)} records")
        else:
            print(f"    ❌ Flask returned {response.status_code}")
            try:
                print(f"       Response: {response.json()}")
            except:
                print(f"       Response: {response.text}")
        
        # Test through Next.js
        print("  Testing Next.js: GET /api/metadata...")
        response = requests.get(
            'http://localhost:3000/api/metadata?limit=1',
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"    ✅ Next.js proxy returned {data.get('count', 0)} records")
        else:
            print(f"    ❌ Next.js returned {response.status_code}")
            try:
                print(f"       Response: {response.json()}")
            except:
                print(f"       Response: {response.text}")
    
    except requests.exceptions.ConnectionError as e:
        print(f"  ⚠️  Connection error (service may not be running): {e}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

def main():
    """Run all checks"""
    print("=" * 60)
    print("ParseHub API Diagnostic Tool")
    print("=" * 60)
    
    checks = [
        ("Database", check_database),
        ("Flask Backend", check_backend_running),
        ("Next.js Frontend", check_frontend_running),
        ("API Endpoints", check_api_endpoints),
        ("Next.js Routes", check_frontend_routes),
    ]
    
    results = {}
    for name, check_fn in checks:
        results[name] = check_fn()
    
    # Test API if services are running
    if results.get("Flask Backend") and results.get("Next.js Frontend"):
        test_metadata_api()
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All checks passed! API should be working.")
        print("\nNext steps:")
        print("  1. Open browser to http://localhost:3000/projects")
        print("  2. Open DevTools (F12) and check Console tab")
        print("  3. Look for [Projects] logs showing fetched records")
    else:
        print("❌ Some checks failed. See details above.")
        print("\nCommon fixes:")
        print("  - Run 'python backend/database.py' to init database")
        print("  - Run 'python backend/api_server.py' to start Flask")
        print("  - Run 'npm run dev' in frontend/ to start Next.js")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
