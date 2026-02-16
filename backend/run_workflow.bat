@echo off
REM ParseHub Automated Workflow Script for Windows
REM This runs the complete pipeline with proper data capture

echo.
echo 🚀 ParseHub Automated Workflow
echo ==============================
echo.

REM Step 1: Fetch projects
echo Step 1: Fetching projects...
D:\Parsehub\.venv\Scripts\python.exe fetch_projects.py
echo.

REM Step 2: Run all projects
echo Step 2: Starting all projects...
D:\Parsehub\.venv\Scripts\python.exe run_projects.py
echo.

REM Step 3: Monitor with FAST polling
echo Step 3: Monitoring projects (fast mode - 10s intervals)...
echo ⚠️  This is CRITICAL - data expires in ~30 mins!
echo Polling every 10 seconds to capture data before purging...
echo.
D:\Parsehub\.venv\Scripts\python.exe monitor_fast.py
echo.

REM Step 4: Show summary
echo Step 4: Displaying summary...
D:\Parsehub\.venv\Scripts\python.exe -c "
import json
results = json.load(open('monitoring_results.json'))
print('=' * 70)
print('📊 FINAL SUMMARY')
print('=' * 70)
print(f'Projects Run: {results[\"total_projects\"]}')
print(f'Data Saved: {results.get(\"data_saved_count\", 0)}')
print(f'Data Purged: {results.get(\"data_purged_count\", 0)}')
print(f'Failed: {results.get(\"failed_count\", 0)}')
print()
print('💾 Saved Files:')
for project in results['project_data']:
    if 'data_file' in project:
        print(f'  ✅ {project[\"project\"]}: {project[\"data_file\"]}')
    else:
        print(f'  ⚠️  {project[\"project\"]}: Data purged')
print('=' * 70)
"

echo.
echo ✅ Workflow complete!
pause
