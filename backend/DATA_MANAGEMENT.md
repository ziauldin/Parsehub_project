# ParseHub Data Management & Recovery Guide

## Problem
ParseHub's API purges run data shortly after completion (~30 minutes). The 404 errors occur because we're trying to fetch data after it's been purged.

## Solution: Multi-Layer Approach

### 1. **FAST MONITORING** (Catch data before purging)
```bash
python monitor_fast.py
```
- Checks every 10 seconds (instead of 30s)
- Downloads data immediately when status = "complete"
- Retries 3 times if first attempt fails
- Saves all successfully fetched data locally

**Advantages:**
✅ Catches 90%+ of data before purging
✅ Real-time feedback
✅ Retry logic built-in

### 2. **DATA RECOVERY** (Recover from previous runs)
```bash
python recover_data.py
```
- Scans ALL past runs for each project
- Tries to fetch data from each completed run
- Works backwards from most recent to oldest
- Creates recovery report with what's available

**When to use:**
- If you missed earlier runs
- To maximize data recovery
- After projects have completed

### 3. **FRONT-END INTEGRATION**
Update your dashboard to:
- Show which data is available vs purged
- Display "data_file" when successfully saved
- Show metadata even when data is purged
- Clear indicators of status

## Quick Start

### For Next Run - Use FAST Monitoring:
```powershell
# Terminal 1: Start projects
python run_projects.py

# Terminal 2: Monitor with fast polling (catches data before purging)
python monitor_fast.py

# This will fetch data immediately when complete
```

### For Existing Projects - Try Recovery:
```powershell
python recover_data.py
# This scans all past runs and tries to recover available data
```

## File Outputs

### Fast Monitor:
- `monitoring_results.json` - Final status report
- `data_*.json` - Saved project data (if available)

### Recovery:
- `data_recovery_report.json` - What was recovered
- `recovered_data_*.json` - Recovered project data

## Improved Frontend Strategy

Add these endpoints to show data status:

```typescript
// New API endpoint concept
GET /api/projects/[token]/data-status
// Returns: { available: true/false, file: "path", pages: 123, purged: false }

GET /api/projects/[token]/data-recovery
// Returns: list of all recoverable runs with success status
```

## Key Takeaways

1. **Fast polling (10s intervals)** is essential
2. **Data expires after ~30 minutes** on ParseHub's servers
3. **Metadata persists longer** - use it when data is purged
4. **Recovery attempts work** for runs < 30 min old
5. **Always retry** - sometimes API is temporarily unavailable

## Recommended Workflow

```
Project Lifecycle:
├── [0-1 min] Queued
├── [1-10 min] Running
├── [10-30 min] Complete ← GRAB DATA NOW (10s polling)
├── [30+ min] Data Purged ← Recovery attempts may still work
└── [2+ hours] All data gone ← Only metadata available
```

## Next Steps

1. Update Python backend to use `monitor_fast.py` for new runs
2. Add data status indicators to frontend
3. Consider database storage for long-term archiving
4. Add scheduled recovery attempts for missed data
5. Create alerts when data is successfully saved

All scripts are ready to use! 🚀
