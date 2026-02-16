#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start ParseHub Frontend and Backend services
.DESCRIPTION
    Starts the Next.js frontend development server at http://localhost:3000
    The frontend serves as the main application with built-in API routes.
#>

param(
    [switch]$Dev = $true,
    [switch]$Help = $false
)

if ($Help) {
    Write-Host @"
ParseHub Application Starter

Usage:
    .\start.ps1                  # Start both services in development mode
    .\start.ps1 -Help            # Show this help message

Services:
    - Frontend:  Next.js at http://localhost:3000
    - Backend:   Integrated APIs in Next.js routes

Environment Setup:
    - Ensure .venv is activated for Python
    - Ensure dependencies are installed (npm install, pip install -r requirements.txt)
"@
    exit 0
}

Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       ParseHub - Frontend & Backend Startup           ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if frontend directory exists
if (-not (Test-Path "frontend")) {
    Write-Host "❌ Error: frontend directory not found!" -ForegroundColor Red
    exit 1
}

# Check if node_modules exists in frontend
if (-not (Test-Path "frontend/node_modules")) {
    Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
    Push-Location frontend
    npm install
    Pop-Location
    Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green
    Write-Host ""
}

# Check backend directory
if (Test-Path "backend") {
    Write-Host "📁 Backend folder found at: backend/" -ForegroundColor Green
    
    # Check if Python virtual environment exists
    if (Test-Path "backend/.env") {
        Write-Host "✅ Backend .env configuration found" -ForegroundColor Green
    } else {
        Write-Host "⚠️  backend/.env not found - some features may not work" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Backend folder not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Starting Frontend Development Server..." -ForegroundColor Cyan
Write-Host "   Application will be available at: http://localhost:3000" -ForegroundColor Green
Write-Host ""

# Start the frontend
Push-Location frontend
Write-Host "📂 Current directory: $(Get-Location)" -ForegroundColor Gray
Write-Host "▶️  Running: npm run dev" -ForegroundColor Yellow
Write-Host ""

npm run dev

Pop-Location
