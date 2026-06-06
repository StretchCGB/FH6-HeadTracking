# ============================================================
#  Forza Horizon 6 - Head Tracking (OpenTrack Edition)
#  Version: 1.2.0
#  Author:  StretchCGB
#  Nexus:   https://www.nexusmods.com/forzahorizon6/mods/288
#
#  Compatible with any OpenTrack input source:
#   - Tobii Eye Tracker 5 (via Tobii Experience)
#   - TrackIR (via NaturalPoint software)
#   - Any other OpenTrack-supported tracker
#
#  Requirements:
#   - OpenTrack (output: UDP over network, port 4242)
#   - Python 3.x (no pip packages needed)
#
#  FH6 Settings (do once):
#   Advanced Controls -> Mouse Free Look = ON
#   HUD & Gameplay    -> Drift Camera    = ON
#   Camera View       -> Driver (cockpit cam)
#
#  Hotkeys while running:
#   F8     = Pause / Resume tracking (e.g. browsing the map)
#   Ctrl+C = Stop script completely
# ============================================================

import socket
import struct
import time
import sys
import ctypes
import threading

# ============================================================
#  CONFIGURATION - Tweak these to your preference
# ============================================================

# How far you turn your head for the camera to fully pan (degrees)
# Lower = less head movement needed. Raise if too sensitive.
MAX_YAW   = 45.0
MAX_PITCH = 25.0

# Ignores tiny head movements below this threshold
# Increase if camera drifts when your head is still (0.0 - 0.3)
DEAD_ZONE = 0.20

# How smoothly the camera follows your head
# Higher = smoother but slower. Lower = snappier but jittery.
# Range: 0.80 (responsive) to 0.98 (very smooth)
SMOOTHING = 0.97

# How fast the camera tracks your head position (pixels per frame)
MOUSE_SPEED = 5

# How fast the camera returns to centre when head is neutral
RETURN_SPEED = 3

# Non-linear curve: makes small head movements very precise
# 1.0 = linear, 2.0 = gentle curve, 3.0 = strong curve
CURVE = 3.0

# Maximum degrees the head can move per frame
# Filters out car jolts on direction changes / bumps
# Lower = more filtering. Raise if real looks get blocked.
MAX_DELTA_PER_FRAME = 8.0

# Set True if up/down camera feels backwards
INVERT_PITCH = False

# OpenTrack UDP port (must match OpenTrack output settings)
UDP_PORT = 4242

# Hotkey to pause/resume tracking (default: F8)
# Virtual key codes: F8=0x77, F9=0x78, F10=0x79, Pause=0x13
PAUSE_KEY = 0x77

# ============================================================
#  WINDOWS INPUT API
# ============================================================

PUL = ctypes.POINTER(ctypes.c_ulong)

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong), ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong), ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("mi", MouseInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("ii", Input_I)]

MOUSEEVENTF_MOVE      = 0x0001
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP   = 0x0010

def send_input(flags, dx=0, dy=0):
    extra  = ctypes.c_ulong(0)
    ii_    = Input_I()
    ii_.mi = MouseInput(dx, dy, 0, flags, 0, ctypes.pointer(extra))
    x      = Input(ctypes.c_ulong(0), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def get_foreground_title():
    try:
        hwnd   = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buf    = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value
    except:
        return ""

# ============================================================
#  MATHS HELPERS
# ============================================================

def apply_curve(value, exp):
    if value == 0.0: return 0.0
    sign = 1.0 if value > 0 else -1.0
    return sign * (abs(value) ** exp)

def apply_dead_zone(value, threshold):
    if abs(value) < threshold: return 0.0
    sign = 1.0 if value > 0 else -1.0
    return sign * (abs(value) - threshold) / (1.0 - threshold)

def smooth_val(current, target, factor):
    return current + (target - current) * (1.0 - factor)

def clamp(value, a, b):
    return max(a, min(b, value))

def draw_bar(value, width=30):
    c      = width // 2
    filled = min(int(abs(value) * c), c)
    if value >= 0:
        bar = " " * c + "|" + "=" * filled + " " * (c - filled)
    else:
        bar = " " * (c - filled) + "=" * filled + "|" + " " * c
    return "[" + bar + "]"

# ============================================================
#  MAIN
# ============================================================

def main():
    print("=" * 58)
    print("  FH6 Head Tracking (OpenTrack)  v1.2.0")
    print("  Author: StretchCGB")
    print("=" * 58)
    print("  Smoothing: {}   Dead zone: {}   Curve: {}".format(SMOOTHING, DEAD_ZONE, CURVE))
    print("  Spike filter: {}deg/frame   Speed: {}".format(MAX_DELTA_PER_FRAME, MOUSE_SPEED))
    print("-" * 58)
    print("  FH6: Advanced Controls -> Mouse Free Look = ON")
    print("  FH6: HUD & Gameplay    -> Drift Camera    = ON")
    print("  FH6: Camera View       -> Driver (cockpit)")
    print("-" * 58)
    print("  F8      = Pause / Resume tracking")
    print("  Ctrl+C  = Stop")
    print("-" * 58)
    print("")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("127.0.0.1", UDP_PORT))
        sock.settimeout(2.0)
        print("  [OK] Listening for OpenTrack on UDP port {}".format(UDP_PORT))
    except OSError as e:
        print("  [ERROR] Could not bind to port {} - is another instance running?".format(UDP_PORT))
        print("  " + str(e))
        input("  Press Enter to exit...")
        sys.exit(1)

    print("  [OK] Input system ready (safe to alt-tab)")
    print("  Move your head - camera only activates inside FH6.")
    print("")

    smooth_yaw   = 0.0
    smooth_pitch = 0.0
    cam_yaw      = 0.0
    cam_pitch    = 0.0
    rmb_held     = False
    prev_yaw     = 0.0
    prev_pitch   = 0.0
    last_print   = time.time()
    paused       = False
    key_was_down = False  # tracks previous F8 state for edge detection

    while True:
        try:
            # --- F8 pause/resume toggle ---
            # GetAsyncKeyState returns negative if key is currently down
            key_is_down = bool(ctypes.windll.user32.GetAsyncKeyState(PAUSE_KEY) & 0x8000)
            if key_is_down and not key_was_down:
                paused = not paused
                if paused:
                    # Release RMB immediately on pause
                    if rmb_held:
                        send_input(MOUSEEVENTF_RIGHTUP)
                        rmb_held  = False
                        cam_yaw   = 0.0
                        cam_pitch = 0.0
                    sys.stdout.write("\r  [PAUSED] F8 to resume                                        \n")
                    sys.stdout.flush()
                else:
                    sys.stdout.write("\r  [RESUMED]                                                     \n")
                    sys.stdout.flush()
            key_was_down = key_is_down

            # Skip tracking while paused
            if paused:
                time.sleep(0.05)
                continue

            data, _ = sock.recvfrom(48)

            if len(data) >= 48:
                values    = struct.unpack('6d', data[:48])
                raw_yaw   = values[3]
                raw_pitch = values[4]

                # Spike rejection - filters car jolts on direction changes
                delta_yaw   = raw_yaw   - prev_yaw
                delta_pitch = raw_pitch - prev_pitch
                if abs(delta_yaw) > MAX_DELTA_PER_FRAME:
                    raw_yaw   = prev_yaw   + MAX_DELTA_PER_FRAME * (1 if delta_yaw > 0 else -1)
                if abs(delta_pitch) > MAX_DELTA_PER_FRAME:
                    raw_pitch = prev_pitch + MAX_DELTA_PER_FRAME * (1 if delta_pitch > 0 else -1)
                prev_yaw   = raw_yaw
                prev_pitch = raw_pitch

                # Normalise, dead zone, curve, smooth
                norm_yaw   = clamp(raw_yaw   / MAX_YAW,   -1.0, 1.0)
                norm_pitch = clamp(raw_pitch / MAX_PITCH, -1.0, 1.0)
                dz_yaw     = apply_dead_zone(norm_yaw,   DEAD_ZONE)
                dz_pitch   = apply_dead_zone(norm_pitch, DEAD_ZONE)
                curved_yaw   = apply_curve(dz_yaw,   CURVE)
                curved_pitch = apply_curve(dz_pitch, CURVE)
                if INVERT_PITCH:
                    curved_pitch = -curved_pitch
                smooth_yaw   = smooth_val(smooth_yaw,   curved_yaw,   SMOOTHING)
                smooth_pitch = smooth_val(smooth_pitch, curved_pitch, SMOOTHING)

                # Only send input when FH6 is the focused window
                fh6_focus = "Forza Horizon 6" in get_foreground_title()

                if fh6_focus:
                    head_active = abs(smooth_yaw) > DEAD_ZONE or abs(smooth_pitch) > DEAD_ZONE

                    if head_active:
                        if not rmb_held:
                            send_input(MOUSEEVENTF_RIGHTDOWN)
                            rmb_held = True
                        delta_x = int((smooth_yaw   - cam_yaw)   * MOUSE_SPEED * 10)
                        delta_y = int((smooth_pitch - cam_pitch) * MOUSE_SPEED * 10)
                        if delta_x != 0 or delta_y != 0:
                            send_input(MOUSEEVENTF_MOVE, delta_x, delta_y)
                            cam_yaw   += delta_x / (MOUSE_SPEED * 10)
                            cam_pitch += delta_y / (MOUSE_SPEED * 10)
                    else:
                        if abs(cam_yaw) > 0.02 or abs(cam_pitch) > 0.02:
                            if not rmb_held:
                                send_input(MOUSEEVENTF_RIGHTDOWN)
                                rmb_held = True
                            ret_x = clamp(int(-cam_yaw   * RETURN_SPEED * 10), -20, 20)
                            ret_y = clamp(int(-cam_pitch * RETURN_SPEED * 10), -20, 20)
                            if ret_x != 0 or ret_y != 0:
                                send_input(MOUSEEVENTF_MOVE, ret_x, ret_y)
                                cam_yaw   += ret_x / (RETURN_SPEED * 10)
                                cam_pitch += ret_y / (RETURN_SPEED * 10)
                        else:
                            if rmb_held:
                                send_input(MOUSEEVENTF_RIGHTUP)
                                rmb_held  = False
                                cam_yaw   = 0.0
                                cam_pitch = 0.0
                else:
                    if rmb_held:
                        send_input(MOUSEEVENTF_RIGHTUP)
                        rmb_held = False
                    smooth_yaw = smooth_pitch = cam_yaw = cam_pitch = 0.0

                # Console display
                if time.time() - last_print > 0.1:
                    bar = draw_bar(smooth_yaw)
                    pause_str = " [F8:PAUSED]  " if paused else ""
                    sys.stdout.write("\r  {} {:+5.1f}deg  RMB:{} {}{}    ".format(
                        bar, raw_yaw,
                        "ON " if rmb_held else "off",
                        "[IN GAME]" if fh6_focus else "[standby]",
                        pause_str))
                    sys.stdout.flush()
                    last_print = time.time()

        except socket.timeout:
            if rmb_held:
                send_input(MOUSEEVENTF_RIGHTUP)
                rmb_held = False
            sys.stdout.write("\r  [WAITING] No data - is OpenTrack running and Started?          ")
            sys.stdout.flush()
        except KeyboardInterrupt:
            if rmb_held:
                send_input(MOUSEEVENTF_RIGHTUP)
            print("\n\n  Tracking stopped. Goodbye!")
            break
        except Exception as e:
            if rmb_held:
                send_input(MOUSEEVENTF_RIGHTUP)
                rmb_held = False
            print("\n  [ERROR] " + str(e))
            time.sleep(0.1)

if __name__ == "__main__":
    main()
