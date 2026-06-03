@echo off
title FH6 Tobii Head Tracking
color 0A

echo.
echo  ============================================================
echo   Forza Horizon 6 - Tobii Eye Tracker 5 Head Tracking
echo  ============================================================
echo.

set OPENTRACK_EXE=C:\Program Files (x86)\opentrack\opentrack.exe
set PROFILE_PATH=%~dp0..\shared\OpenTrack_FH6.ini
set SCRIPT_PATH=%~dp0FH6_Tobii_HeadTrack.py

python --version >NUL 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found. Install from https://www.python.org/downloads/
    echo  Make sure to tick "Add Python to PATH" during install.
    pause & exit /b 1
)

if not exist "%OPENTRACK_EXE%" (
    echo  [ERROR] OpenTrack not found at: %OPENTRACK_EXE%
    echo  Install from: https://github.com/opentrack/opentrack/releases
    pause & exit /b 1
)

echo  [1/2] Launching OpenTrack...
start "" "%OPENTRACK_EXE%" --profile "%PROFILE_PATH%"
timeout /t 3 /nobreak >NUL

echo  [2/2] Starting Tobii head tracking...
echo.
echo  ============================================================
echo   STEPS:
echo   1. In OpenTrack - click START
echo   2. Launch Forza Horizon 6
echo   3. In FH6: Advanced Controls - Mouse Free Look = ON
echo   4. In FH6: HUD and Gameplay  - Drift Camera    = ON
echo   5. In FH6: Camera View       - Driver (cockpit)
echo   6. Drive and turn your head to look into corners!
echo   Press Ctrl+C in this window to stop tracking.
echo  ============================================================
echo.

python "%SCRIPT_PATH%"
pause
