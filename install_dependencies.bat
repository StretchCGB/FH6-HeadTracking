@echo off
title FH6 Head Tracking - Install Dependencies
color 0A

echo.
echo  ============================================================
echo   FH6 Head Tracking - Install Dependencies
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
echo   Tobii version: No pip packages needed!
echo   (uses OpenTrack + built-in Windows APIs only)
echo  -------------------------------------------------------
echo.
echo  -------------------------------------------------------
echo   Webcam version: Installing opencv-python + mediapipe
echo  -------------------------------------------------------
echo.
python -m pip install opencv-python mediapipe --upgrade
echo.
echo  ============================================================
echo   Done! Dependencies installed.
echo   - Tobii users:  run tobii\Launch_Tobii.bat
echo   - Webcam users: run webcam\Launch_Webcam.bat
echo  ============================================================
echo.
pause
