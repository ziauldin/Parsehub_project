# Quick Start Guide

## 🚀 Running the Full Application

The easiest way to start ParseHub is to run the startup script for your operating system.

### Windows (PowerShell)
```bash
.\start.ps1
```

Or double-click `start.bat` for a simpler approach.

### Windows (Command Prompt / Batch)
```bash
start.bat
```

### Linux / macOS
```bash
chmod +x start.sh
./start.sh
```

## 📋 What the Startup Script Does

1. ✅ Checks if frontend dependencies are installed
2. ✅ Installs dependencies if needed
3. ✅ Verifies backend configuration
4. ✅ Starts the Next.js development server
5. ✅ Opens the application at **http://localhost:3000**

## 🔧 Manual Setup (If Needed)

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## ✨ Features Available

Once started, you can:
- 📊 View all ParseHub projects
- ▶️ Run projects with one click
- 📈 Monitor execution in real-time
- 💾 View and export scraped data
- 📉 Track analytics and statistics
- 🔄 Auto-refresh every 30 seconds

## 🌐 Access the Application

**Frontend Dashboard**: [http://localhost:3000](http://localhost:3000)

## 📁 Project Structure

```
ParseHub/
├── backend/          # Python backend (API integration, data processing)
├── frontend/         # Next.js React dashboard
├── start.ps1        # PowerShell startup script
├── start.bat        # Windows batch startup script
├── start.sh         # Linux/macOS bash startup script
└── README.md        # Main documentation
```

## 🔐 Environment Setup

**Backend** (`.env`):
```
PARSEHUB_API_KEY=your_api_key
PARSEHUB_BASE_URL=https://www.parsehub.com/api/v2
DATABASE_PATH=parsehub.db
```

**Frontend** (`.env.local`):
```
PARSEHUB_API_KEY=your_api_key
NEXT_PUBLIC_API_URL=http://localhost:3000
```

Both files should already exist if you've gone through initial setup.

## 🐛 Troubleshooting

### "npm: command not found"
- Install Node.js from [nodejs.org](https://nodejs.org)
- Restart your terminal

### "Module not found" in Python
- Make sure you're in the virtual environment: `.venv\Scripts\activate` (Windows)
- Run: `pip install -r backend/requirements.txt`

### Port 3000 already in use
- Kill the existing process or use a different port
- Edit `frontend/package.json` to change the dev server port

### Environment variables not loading
- Make sure `.env` files exist in `backend/` and `frontend/`
- Check `.env.example` for the required variables

## 📚 Additional Resources

- Backend Documentation: `backend/ENV_SETUP.md`
- Database Info: `backend/DATABASE_ANALYTICS.md`
- Frontend Info: `frontend/FRONTEND_INTEGRATION.md`

## 💡 Tips

- Keep the terminal window open while developing
- Use `Ctrl+C` to stop the development server
- Changes to React components auto-reload in the browser
- Check browser console (F12) for errors

---

**Ready to start?** Run `start.ps1` / `start.bat` / `start.sh` and visit http://localhost:3000! 🎉
