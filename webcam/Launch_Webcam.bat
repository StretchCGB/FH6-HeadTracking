@echo off
title FH6 Webcam Head Tracking
color 0B

echo.
echo  ============================================================
echo   Forza Horizon 6 - Webcam Head Tracking
echo  ============================================================
echo.

set SCRIPT_PATH=%~dp0FH6_Webcam_HeadTrack.py

python --version >NUL 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found. Install from https://www.python.org/downloads/
    echo  Make sure to tick "Add Python to PATH" during install.
    pause & exit /b 1
)

python -c "import cv2" >NUL 2>&1
if errorlevel 1 (
    echo  [ERROR] opencv-python not installed.
    echo  Run install_dependencies.bat first!
    pause & exit /b 1
)

python -c "import mediapipe" >NUL 2>&1
if errorlevel 1 (
    echo  [ERROR] mediapipe not installed.
    echo  Run install_dependencies.bat first!
    pause & exit /b 1
)

echo  [OK] All dependencies found.
echo.
echo  ============================================================
echo   TIPS FOR BEST WEBCAM TRACKING:
echo   - Good lighting on your face (avoid backlight)
echo   - Webcam at eye level, centred on your face
echo   - Sit 40-80cm from camera
echo   - Plain background helps face detection
echo.
echo   STEPS:
echo   1. Make sure your webcam is plugged in
echo   2. Launch Forza Horizon 6
echo   3. In FH6: Advanced Controls - Mouse Free Look = ON
echo   4. In FH6: HUD and Gameplay  - Drift Camera    = ON
echo   5. In FH6: Camera View       - Driver (cockpit)
echo   6. A preview window will open - check your face is detected
echo   7. Drive and turn your head to look into corners!
echo   Press Ctrl+C to stop tracking.
echo  ============================================================
echo.

python "%SCRIPT_PATH%"
pause
