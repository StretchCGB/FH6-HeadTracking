# Changelog

## v1.4.0 — 2026-06-11
### Added
- `INVERT_YAW` setting — for users whose camera goes the wrong way horizontally
- F9 recentre hotkey — instantly snaps camera back to forward view
- FH6 telemetry auto-pause — tracking automatically pauses during menus, replays, rewinds (opt-in via `TELEMETRY_AUTO_PAUSE = True`)
- UDP telemetry forwarding — forward FH6 Data Out packets to SimHub or other apps while mod is active
- Improved config comments throughout

### Fixed
- Clarified in header that TrackIR is NOT supported by OpenTrack due to NaturalPoint legal issues

### Changed
- Version bump to v1.4.0

## v1.3.0 — 2026-06-07
### Fixed
- Webcam version now supports both old mediapipe (0.10.x) and new mediapipe (0.11+)
- `install_dependencies.bat` now pins mediapipe to 0.10.9 to avoid the `AttributeError: module 'mediapipe' has no attribute 'solutions'` error on newer installs

### Changed
- Webcam script auto-detects mediapipe API version at runtime — no manual changes needed

## v1.1.0 — 2026-06-02
### Changed
- Renamed `tobii/` folder to `opentrack/` to reflect broader device support
- Renamed `Launch_Tobii.bat` to `Launch_OpenTrack.bat`
- Renamed `FH6_Tobii_HeadTrack.py` to `FH6_OpenTrack_HeadTrack.py`
- Updated script header to list all compatible OpenTrack input sources
- Updated description to prominently feature TrackIR support

### Added
- TrackIR listed as first-class supported device throughout documentation
- "Any OpenTrack-compatible tracker" section in description
- SteamVR support listed as Coming Soon
- Catsmecha credited for confirming TrackIR compatibility
- MIT License
- BUILD.md with full source review guide for Nexus moderation
- CHANGELOG.md

## v1.0.0 — 2026-06-01
### Initial release
- Tobii Eye Tracker 5 support via OpenTrack UDP
- Webcam support via MediaPipe face mesh
- Non-linear curve for precision at small head angles
- Spike rejection filter for direction changes and bumps
- Hysteresis dead zone to prevent camera drift
- Alt-tab safe — input pauses when FH6 loses focus
- Live console bar showing head angle and camera state
