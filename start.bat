@echo off
setlocal enabledelayedexpansion

REM ParseHub Frontend & Backend Startup Script

title ParseHub - Starting Services
color 0A

echo.
echo ========================================================
echo      ParseHub - Frontend and Backend Startup
echo ========================================================
echo.

REM Check if frontend directory exists
if not exist "frontend" (
    echo Error: frontend directory not found!
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
    echo Frontend dependencies installed.
    echo.
)

REM Check backend directory
if exist "backend" (
    echo [OK] Backend folder found
    if exist "backend\.env" (
        echo [OK] Backend .env configuration found
    ) else (
        echo [WARN] backend\.env not found - some features may not work
    )
) else (
    echo [WARN] Backend folder not found
)

echo.
echo Starting Frontend Development Server...
echo Application will be available at: http://localhost:3000
echo.
echo.

REM Start the frontend
cd frontend
echo Running: npm run dev
npm run dev

pause
