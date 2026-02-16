# Environment Variables Setup Guide

## Overview
This project uses environment variables to manage sensitive information like API keys and database paths. All sensitive data is stored in `.env` files which are **NOT** committed to version control.

## Files

### `.env` - Root Environment File
Located at the project root (`d:\Parsehub\.env`), contains:
- `PARSEHUB_API_KEY` - Your ParseHub API key
- `PARSEHUB_BASE_URL` - ParseHub API base URL
- `DATABASE_PATH` - Path to SQLite database
- `PORT` - Server port

### `.env.local` - Frontend Environment File
Located at `frontend/.env.local`, contains frontend-specific variables and is auto-loaded by Next.js.

### `.env.example` - Template Files
Template files showing what variables need to be configured:
- `.env.example` (root) - for backend/Python
- `frontend/.env.example` - for frontend

## Setup Instructions

### 1. Backend (Python)
```bash
# The .env file is already created with your API key
# To use different credentials, update the .env file:

PARSEHUB_API_KEY=your_new_api_key
PARSEHUB_BASE_URL=https://www.parsehub.com/api/v2
DATABASE_PATH=path/to/database.db
```

Make sure `python-dotenv` is installed:
```bash
pip install python-dotenv
# or
pip install -r requirements.txt
```

### 2. Frontend (Next.js)
```bash
# The frontend/.env.local file is already created
# Next.js automatically loads .env.local
# No additional setup needed!

# For development:
cd frontend
npm run dev

# For production:
npm run build
npm start
```

## How It Works

### Python Files
All Python scripts now load environment variables using:
```python
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv('PARSEHUB_API_KEY')
```

### Next.js API Routes
All TypeScript API routes use `process.env`:
```typescript
const API_KEY = process.env.PARSEHUB_API_KEY || ''
const BASE_URL = process.env.PARSEHUB_BASE_URL || 'https://www.parsehub.com/api/v2'
```

## Security Best Practices

✅ **DO:**
- Keep `.env` and `.env.local` in `.gitignore`
- Use `.env.example` to document required variables
- Use strong, unique API keys
- Rotate API keys regularly
- Never share `.env` files

❌ **DON'T:**
- Commit `.env` files to git
- Hardcode sensitive data in source files
- Share `.env` files via email or messaging
- Use the same API key across multiple projects

## Updated Files

### Backend Files
- `fetch_projects.py` ✅
- `run_projects.py` ✅
- `monitor_fast.py` ✅
- `monitor.py` ✅
- `recover_data.py` ✅
- `verify_projects.py` ✅
- `test_fixed_endpoint.py` ✅
- `test_all_endpoints.py` ✅
- `fetch_results.py` ✅
- `check_status.py` ✅
- `debug_api.py` ✅
- `debug_api2.py` ✅
- `debug_api3.py` ✅
- `check_data_status.py` ✅
- `find_data_endpoint.py` ✅
- `inspect_full_response.py` ✅
- `check_data_structure.py` ✅
- `database.py` ✅ (DATABASE_PATH now configurable)

### Frontend Files (API Routes)
- `frontend/app/api/projects/route.ts` ✅
- `frontend/app/api/projects/run/route.ts` ✅
- `frontend/app/api/projects/run-all/route.ts` ✅
- `frontend/app/api/projects/[token]/[runToken]/route.ts` ✅
- `frontend/app/api/analytics/route.ts` ✅

### Configuration Files
- `.env` - Created with current API key
- `.env.local` (frontend) - Created with configuration
- `.env.example` - Template for documentation
- `.env.example` (frontend) - Frontend template
- `.gitignore` - Updated to exclude sensitive files
- `requirements.txt` - Updated to include `python-dotenv`

## Troubleshooting

### Environment variables not loading in frontend
- Make sure `frontend/.env.local` exists
- Restart the Next.js dev server after changing env vars
- Variables prefixed with `NEXT_PUBLIC_` are exposed to browser

### 'python-dotenv' not found
```bash
pip install python-dotenv==1.0.0
```

### Database path errors
- Ensure `DATABASE_PATH` in `.env` points to a valid directory
- Check file permissions on the database directory

## Deployment

For production deployment:
1. Set environment variables in your hosting platform's dashboard (not via `.env` file)
2. Never push `.env` to production repositories
3. Use different API keys for development and production
4. Rotate API keys regularly

## Support

For issues with environment variables, check:
1. `.env` file exists in project root
2. Syntax is correct: `KEY=value` (no quotes needed)
3. No trailing spaces in values
4. Re-run/restart the application after changes
