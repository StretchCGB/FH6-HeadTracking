# Build & Installation Guide
**FH6 Head Tracking — StretchCGB**

This document covers everything needed to install, run, and verify the mod from source. There is no compilation step — these are pure Python scripts.

---

## Prerequisites

### All versions
| Software | Version | Download | Notes |
|----------|---------|----------|-------|
| Windows | 10 or 11 | — | Required for SendInput API |
| Python | 3.8 or newer | https://www.python.org/downloads/ | Tick **"Add Python to PATH"** |
| Forza Horizon 6 | Any | Steam / Xbox app | PC version only |

### OpenTrack version (Tobii / TrackIR / hardware trackers)
| Software | Download | Notes |
|----------|----------|-------|
| OpenTrack | https://github.com/opentrack/opentrack/releases | Latest stable release |
| Tobii Experience | https://gaming.tobii.com/getstarted/ | Tobii ET5 users only |
| TrackIR software | https://www.naturalpoint.com/trackir/ | TrackIR users only |

### Webcam version
No additional downloads. `install_dependencies.bat` handles everything.

---

## Installation Steps

### Step 1 — Python
Download and run the Python installer from https://www.python.org/downloads/

**Critical:** On the first installer screen, tick **"Add Python to PATH"** before clicking Install.

Verify in a command prompt:
```
python --version
```
Should return `Python 3.x.x`

### Step 2 — Extract the mod
Extract the zip to any location, for example:
```
C:\FH6-HeadTracking\
```

### Step 3 — Install Python dependencies (webcam version only)
Double-click `install_dependencies.bat` or run in a command prompt:
```
pip install opencv-python mediapipe
```
The OpenTrack version has no pip dependencies — it uses only Python standard library modules.

### Step 4 — OpenTrack setup (hardware tracker version only)
1. Install OpenTrack from https://github.com/opentrack/opentrack/releases
2. Open OpenTrack
3. Go to **Profile → Import** and select `shared\OpenTrack_FH6.ini`
4. Set **Input** to match your device:
   - Tobii Eye Tracker 5 → select **Tobii EyeX**
   - TrackIR → select **TrackIR**
   - Other → select the appropriate plugin
5. Verify **Output** is set to **UDP over network**
6. Click the wrench icon next to Output and confirm: IP = `127.0.0.1`, Port = `4242`

### Step 5 — FH6 in-game settings (one time)
Launch FH6 and set:
- **Settings → Advanced Controls → Mouse Free Look = ON**
- **Settings → HUD & Gameplay → Drift Camera = ON**
- **Settings → HUD & Gameplay → Camera View = Driver**

---

## Running the Mod

### OpenTrack version
1. Ensure your tracking hardware software is running
2. Run `opentrack\Launch_OpenTrack.bat` as Administrator
3. In OpenTrack click **Start** — verify the octopus responds to head movement
4. Launch FH6, switch to Driver/Cockpit cam, and drive

### Webcam version
1. Run `webcam\Launch_Webcam.bat` as Administrator
2. A preview window opens showing your webcam feed
3. Confirm face is detected (green text overlay)
4. Launch FH6, switch to Driver/Cockpit cam, and drive

---

## Running from Source (no bat files)

OpenTrack version:
```bash
# Terminal 1 - start OpenTrack manually with your preferred settings
# Then in Terminal 2:
python opentrack/FH6_OpenTrack_HeadTrack.py
```

Webcam version:
```bash
pip install opencv-python mediapipe
python webcam/FH6_Webcam_HeadTrack.py
```

---

## Verifying the Scripts Are Safe

You can audit the full source in this repository. Key things to verify:

**FH6_OpenTrack_HeadTrack.py**
- Opens one UDP socket on `127.0.0.1:4242` (localhost only, no internet)
- Reads 48-byte packets from OpenTrack (6 doubles: x,y,z,yaw,pitch,roll)
- Applies maths (dead zone, smoothing, curve)
- Calls `ctypes.windll.user32.SendInput` — standard Windows API for mouse simulation
- Calls `ctypes.windll.user32.GetForegroundWindow` — checks if FH6 is focused
- No file writes, no registry, no network except localhost

**FH6_Webcam_HeadTrack.py**
- Opens webcam via `cv2.VideoCapture(0)` — local camera only
- Runs MediaPipe FaceMesh — entirely local, no cloud/internet calls
- Same SendInput output pipeline as above
- No file writes, no registry, no network

**Batch files**
- `Launch_OpenTrack.bat` — calls `opentrack.exe --profile path` and `python script.py`
- `Launch_Webcam.bat` — checks pip packages, calls `python script.py`
- `install_dependencies.bat` — calls `pip install opencv-python mediapipe`

---

## Uninstalling

Stop the script (Ctrl+C). Delete the mod folder. Nothing is written outside the mod folder at any point.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md)
