<<<<<<< HEAD
# ParseHub - Web Scraping Dashboard

A full-stack web scraping dashboard for ParseHub API integration with a Next.js frontend and Python backend.

## 📁 Project Structure

```
ParseHub/
├── backend/                 # Python backend (API integration, data processing)
│   ├── .env                # Environment variables (API keys, config)
│   ├── requirements.txt     # Python dependencies
│   ├── database.py         # SQLite database module
│   ├── fetch_projects.py   # Fetch projects from ParseHub
│   ├── run_projects.py     # Trigger project runs
│   ├── monitor_fast.py     # Monitor project execution (10s polling)
│   └── ... (other backend scripts)
│
├── frontend/               # Next.js frontend (React dashboard)
│   ├── .env.local         # Frontend environment (Next.js)
│   ├── package.json       # Node.js dependencies
│   ├── app/               # Next.js app structure
│   ├── components/        # React components
│   └── public/            # Static assets
│
├── start.ps1              # PowerShell startup script
├── start.bat              # Windows batch startup script
├── start.sh               # Linux/macOS bash startup script
├── start.py               # Python startup script
├── .venv/                 # Python virtual environment
├── .gitignore            # Git ignore rules
├── QUICKSTART.md         # Quick start guide
└── README.md             # This file
```

## 🚀 Quick Start

### **Fastest Way - Run the Startup Script** ⚡

Choose the script for your operating system:

**Windows (PowerShell):**
```bash
.\start.ps1
```

**Windows (Batch):**
```bash
start.bat
```

**Linux / macOS:**
```bash
./start.sh
```

**Or with Python:**
```bash
python start.py
```

The script will:
- ✅ Install dependencies if needed
- ✅ Verify configuration
- ✅ Start the Next.js development server
- ✅ Open http://localhost:3000

### Manual Setup (If Preferred)

1. **Install Python dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   - Edit `backend/.env` with your ParseHub API key:
   ```
   PARSEHUB_API_KEY=your_api_key
   PARSEHUB_BASE_URL=https://www.parsehub.com/api/v2
   ```

3. **Run Python scripts:**
   ```bash
   # Fetch all projects
   python fetch_projects.py
   
   # Run all projects
   python run_projects.py
   
   # Monitor with fast polling
   python monitor_fast.py
   ```

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```
   
   Application will be available at `http://localhost:3000`

3. **Build for production:**
   ```bash
   npm run build
   npm start
   ```

## 🔧 Environment Variables

### Backend (.env)
```
PARSEHUB_API_KEY=your_api_key_here
PARSEHUB_BASE_URL=https://www.parsehub.com/api/v2
DATABASE_PATH=parsehub.db
PORT=3000
```

### Frontend (.env.local)
```
PARSEHUB_API_KEY=your_api_key_here
PARSEHUB_BASE_URL=https://www.parsehub.com/api/v2
NEXT_PUBLIC_API_URL=http://localhost:3000
```

## 📊 Features

- **Real-time Monitoring**: Monitor project execution with live updates
- **One-Click Execution**: Run single or all projects with a button click
- **Live Dashboard**: Real-time statistics and project status
- **Data Export**: Export scraped data in multiple formats
- **Database Tracking**: SQLite database for historical data
- **Auto-Refresh**: 30-second auto-refresh for live updates

## 📚 Documentation

- **Backend Setup**: See `backend/ENV_SETUP.md`
- **Database**: See `backend/DATABASE_ANALYTICS.md`
- **Data Management**: See `backend/DATA_MANAGEMENT.md`
- **Solution Details**: See `backend/SOLUTION_SUMMARY.md`
- **Frontend Integration**: See `frontend/FRONTEND_INTEGRATION.md`

## 🔐 Security

- API keys stored in `.env` files (not committed to git)
- Use `.env.example` as template for setup
- Never share `.env` files with sensitive data
- Rotate API keys regularly

## 📝 License

Copyright © 2026 ParseHub Dashboard

## 🤝 Support

For issues or questions, refer to:
1. Backend: `backend/ENV_SETUP.md`
2. Database: `backend/DATABASE_ANALYTICS.md`
3. Frontend: Check Next.js documentation

---

**Last Updated**: February 16, 2026
=======
# Parsehub_project
>>>>>>> aa889f4d60a91749dd880b57970c47f8c0f7f659
