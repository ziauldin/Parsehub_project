#!/usr/bin/env python
"""Test imports to see where it hangs"""
import sys
import time

print("Starting import test...")
sys.stdout.flush()

try:
    print("[1] Importing Flask...")
    from flask import Flask
    print("    OK: Flask imported")
    sys.stdout.flush()
    
    print("[2] Importing database...")
    from backend.database import ParseHubDatabase
    print("    OK: Database imported")
    sys.stdout.flush()
    
    print("[3] Creating database instance...")
    db = ParseHubDatabase()
    print("    OK: Database instance created")
    sys.stdout.flush()
    
    print("[4] Importing MonitoringService...")
    from backend.monitoring_service import MonitoringService
    print("    OK: MonitoringService imported")
    sys.stdout.flush()
    
    print("[5] Creating MonitoringService instance...")
    monitoring_service = MonitoringService()
    print("    OK: MonitoringService instance created")
    sys.stdout.flush()
    
    print("[6] Importing AnalyticsService...")
    from backend.analytics_service import AnalyticsService
    print("    OK: AnalyticsService imported")
    sys.stdout.flush()
    
    print("[7] Creating AnalyticsService instance...")
    analytics_service = AnalyticsService()
    print("    OK: AnalyticsService instance created")
    sys.stdout.flush()
    
    print("[8] Importing ExcelImportService...")
    from backend.excel_import_service import ExcelImportService
    print("    OK: ExcelImportService imported")
    sys.stdout.flush()
    
    print("[9] Importing AutoRunnerService...")
    from backend.auto_runner_service import AutoRunnerService
    print("    OK: AutoRunnerService imported")
    sys.stdout.flush()
    
    print("[10] Importing api_server...")
    from backend import api_server
    print("    OK: api_server imported")
    sys.stdout.flush()
    
    print("\nSUCCESS: All imports successful!")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
