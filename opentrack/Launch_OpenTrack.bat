@echo off
title FH6 OpenTrack Head Tracking
color 0A

echo.
echo  ============================================================
echo   Forza Horizon 6 - OpenTrack Head Tracking
echo   Supports: Tobii Eye Tracker 5, TrackIR, and any
echo   other OpenTrack-compatible head tracking device
echo  ============================================================
echo.

set SCRIPT_PATH=%~dp0FH6_OpenTrack_HeadTrack.py
set PROFILE_PATH=%~dp0..\shared\OpenTrack_FH6.ini

:: --- Find OpenTrack in common install locations ---
set OPENTRACK_EXE=
if exist "C:\Program Files (x86)\opentrack\opentrack.exe" set OPENTRACK_EXE=C:\Program Files (x86)\opentrack\opentrack.exe
if exist "C:\Program Files\opentrack\opentrack.exe"       set OPENTRACK_EXE=C:\Program Files\opentrack\opentrack.exe
if exist "%LOCALAPPDATA%\opentrack\opentrack.exe"         set OPENTRACK_EXE=%LOCALAPPDATA%\opentrack\opentrack.exe
if exist "%APPDATA%\opentrack\opentrack.exe"              set OPENTRACK_EXE=%APPDATA%\opentrack\opentrack.exe

:: Check Python
python --version >NUL 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found.
    echo  Install from https://www.python.org/downloads/
    echo  Make sure to tick "Add Python to PATH" during install.
    echo.
    pause & exit /b 1
)
echo  [OK] Python found.

:: Launch OpenTrack if found, skip if not
if "%OPENTRACK_EXE%"=="" (
    echo  [WARNING] OpenTrack not found in common locations.
    echo  Please launch OpenTrack manually before continuing.
    echo  Then press any key to start the tracking script.
    echo.
    pause
) else (
    echo  [OK] OpenTrack found at: %OPENTRACK_EXE%
    echo  [1/2] Launching OpenTrack...
    start "" "%OPENTRACK_EXE%" --profile "%PROFILE_PATH%"
    timeout /t 3 /nobreak >NUL
)

echo  [2/2] Starting head tracking script...
echo.
echo  ============================================================
echo   STEPS:
echo   1. In OpenTrack - set Input to your device, click START
echo   2. Launch Forza Horizon 6
echo   3. Switch to Driver / Cockpit cam
echo.
echo   HOTKEYS (while script is running):
echo   F8          = Pause / Resume tracking (e.g. for map browsing)
echo   Ctrl+C      = Stop tracking completely
echo  ============================================================
echo.

python "%SCRIPT_PATH%"
pause
