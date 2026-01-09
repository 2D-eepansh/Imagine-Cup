@echo off
cd /d "%~dp0frontend"
echo ======================================================================
echo Starting Frontend Dev Server
echo ======================================================================
echo Checking for node_modules...
if not exist "node_modules" (
    echo Installing dependencies...
    call "C:\Program Files\nodejs\npm.cmd" install
)
echo Starting Vite dev server...
call "C:\Program Files\nodejs\npm.cmd" run dev
