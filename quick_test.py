#!/usr/bin/env python
"""Test if backend is running"""
import requests
import time
time.sleep(2)

try:
    r = requests.get("http://localhost:5000/api/health", timeout=3)
    print(f"OK: {r.status_code}")
except Exception as e:
    print(f"FAILED: {e}")
