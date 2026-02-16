# ParseHub Frontend

Next.js frontend dashboard for ParseHub API integration.

## Features

- 📊 Real-time project monitoring
- 🚀 One-click project execution
- 📈 Live statistics dashboard
- 💾 Data export functionality
- 🔄 Auto-refresh every 30 seconds
- 🎨 Modern, responsive UI with Tailwind CSS

## Setup

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:3000`

## API Routes

- `GET /api/projects` - Fetch all projects
- `POST /api/projects/run` - Run a single project
- `POST /api/projects/run-all` - Run all projects
- `GET /api/projects/[token]/[runToken]` - Get run data

## Environment Variables

```
NEXT_PUBLIC_API_URL=http://localhost:3000
```
