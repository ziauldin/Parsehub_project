#!/usr/bin/env python
"""Quick test of backend health"""
import requests
import sys

try:
    print("Testing backend health endpoint...")
    r = requests.get('http://localhost:5000/api/health', timeout=5)
    print(f'✅ Status: {r.status_code}')
    print(f'Response: {r.text}')
except requests.Timeout:
    print('❌ Request timed out after 5 seconds')
    sys.exit(1)
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
