@echo off
title FH6 Head Tracking - Install Dependencies
color 0A

echo.
echo  ============================================================
echo   FH6 Head Tracking - Installing Dependencies
echo  ============================================================
echo.

python --version >NUL 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found!
    echo.
    echo  Download Python from: https://www.python.org/downloads/
    echo  IMPORTANT: Tick "Add Python to PATH" during install!
    echo.
    pause & exit /b 1
)

echo  [OK] Python found.
echo.
echo  -------------------------------------------------------
echo   Tobii / OpenTrack version: No pip packages needed.
echo  -------------------------------------------------------
echo.
echo  -------------------------------------------------------
echo   Webcam version: Installing opencv-python + mediapipe
echo  -------------------------------------------------------
echo.

python -m pip install opencv-python --upgrade

echo.
echo  Installing mediapipe (pinned to 0.10.35 for compatibility)...
python -m pip install "mediapipe==0.10.35"

echo.
echo  ============================================================
echo   Done!
echo   - OpenTrack users: run opentrack\Launch_OpenTrack.bat
echo   - Webcam users:    run webcam\Launch_Webcam.bat
echo  ============================================================
echo.
pause
