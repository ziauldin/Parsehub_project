@echo off
REM ==============================================
REM ParseHub Backend Startup Script
REM ==============================================
REM This script starts the Flask backend server
REM Run this in a separate PowerShell terminal

powershell -NoExit -Command "cd d:\Parsehub; .\.venv\Scripts\Activate.ps1; cd backend; python api_server.py"
