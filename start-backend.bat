@echo off
cd /d "%~dp0backend"
echo ======================================================================
echo Starting Backend API Server on http://localhost:8000
echo ======================================================================
python -m uvicorn main:app --reload --port 8000
