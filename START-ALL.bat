@echo off
echo ======================================================================
echo STARTING PORTFOLIO RISK INTELLIGENCE SYSTEM
echo ======================================================================
echo.
echo Backend will run on: http://localhost:8000
echo Frontend will run on: http://localhost:5173
echo.
echo Press CTRL+C in each window to stop the servers
echo ======================================================================
echo.

start "Backend API - Port 8000" cmd /k "%~dp0start-backend.bat"
timeout /t 3 /nobreak >nul
start "Frontend Dev - Port 5173" cmd /k "%~dp0start-frontend.bat"

echo.
echo Both servers are starting in separate windows...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
pause
