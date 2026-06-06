# Changelog

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
