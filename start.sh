#!/bin/bash

# ParseHub Frontend & Backend Startup Script (Linux/macOS)

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║       ParseHub - Frontend & Backend Startup           ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo "❌ Error: frontend directory not found!"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    echo "✅ Frontend dependencies installed"
    echo ""
fi

# Check backend directory
if [ -d "backend" ]; then
    echo "📁 Backend folder found at: backend/"
    
    if [ -f "backend/.env" ]; then
        echo "✅ Backend .env configuration found"
    else
        echo "⚠️  backend/.env not found - some features may not work"
    fi
else
    echo "⚠️  Backend folder not found"
fi

echo ""
echo "🚀 Starting Frontend Development Server..."
echo "   Application will be available at: http://localhost:3000"
echo ""

# Start the frontend
cd frontend
echo "▶️  Running: npm run dev"
echo ""
npm run dev
