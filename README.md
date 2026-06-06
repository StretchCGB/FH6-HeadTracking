# FH6 Head Tracking
**Forza Horizon 6 — Community Mod**
**Author:** StretchCGB | **Nexus Mods:** https://www.nexusmods.com/forzahorizon6/mods/288

Adds head tracking camera control to Forza Horizon 6 using your Tobii Eye Tracker 5, TrackIR, or any webcam. No game files are modified.

---

## How It Works

```
Tobii / TrackIR / any tracker
        │
    OpenTrack (UDP port 4242)
        │
FH6_OpenTrack_HeadTrack.py  ◄──  or  ──►  FH6_Webcam_HeadTrack.py
        │                                        │
        └──────────────┬─────────────────────────┘
                       │
           Windows SendInput API (ctypes)
           Simulates mouse movement + RMB hold
                       │
           Forza Horizon 6
           (Mouse Free Look — built-in game feature)
```

The scripts use **only**:
- Python standard library (`socket`, `struct`, `ctypes`, `time`, `sys`, `math`)
- `opencv-python` and `mediapipe` for the webcam version only
- Windows `SendInput` API via `ctypes` — no third party input libraries
- No game memory reading, no process injection, no game file modification

---

## Repository Structure

```
FH6-HeadTracking/
│
├── opentrack/
│   ├── FH6_OpenTrack_HeadTrack.py   # Main script - reads OpenTrack UDP, outputs mouse
│   └── Launch_OpenTrack.bat          # Launcher - starts OpenTrack + runs script
│
├── webcam/
│   ├── FH6_Webcam_HeadTrack.py      # Webcam script - MediaPipe face mesh + mouse output
│   └── Launch_Webcam.bat             # Launcher - dependency check + runs script
│
├── shared/
│   └── OpenTrack_FH6.ini            # Pre-configured OpenTrack profile (UDP output)
│
├── docs/
│   └── NEXUS_PAGE_COPY.txt          # Nexus mod page BBCode description
│
├── install_dependencies.bat          # Installs opencv-python + mediapipe via pip
├── README.md                         # This file
├── BUILD.md                          # Full build and install instructions
├── CHANGELOG.md                      # Version history
└── LICENSE                           # MIT License
```

---

## Quick Start

See [BUILD.md](BUILD.md) for full installation and build instructions.

**Requirements:** Windows 10/11, Python 3.8+, Forza Horizon 6 (PC)

---

## Security Notes for Nexus Moderation

This mod contains `.py` Python scripts and `.bat` batch files. Full source is available in this repository for review. Summary of what each file does:

| File | What it does |
|------|-------------|
| `FH6_OpenTrack_HeadTrack.py` | Opens UDP socket on 127.0.0.1:4242, reads head angle packets from OpenTrack, applies smoothing/curve maths, calls Windows `SendInput` to simulate mouse movement and RMB when FH6 is the foreground window |
| `FH6_Webcam_HeadTrack.py` | Opens webcam via OpenCV, runs MediaPipe face mesh to estimate head yaw/pitch, same output pipeline as above |
| `Launch_OpenTrack.bat` | Launches OpenTrack.exe with a profile path, then calls `python FH6_OpenTrack_HeadTrack.py` |
| `Launch_Webcam.bat` | Checks pip dependencies, then calls `python FH6_Webcam_HeadTrack.py` |
| `install_dependencies.bat` | Calls `pip install opencv-python mediapipe` |
| `OpenTrack_FH6.ini` | Plain text OpenTrack config — sets UDP output to 127.0.0.1:4242 |

No executables. No DLLs. No registry writes. No network connections except localhost UDP.

---

## License

MIT — see [LICENSE](LICENSE)
