# ============================================================
#  Forza Horizon 6 - Webcam Head Tracking
#  Version: 1.0.0
#  Author:  [YourNexusUsername]
#  Nexus:   https://www.nexusmods.com/forzahorizon6
#
#  Uses your webcam + MediaPipe face mesh to estimate head
#  angle - no Tobii required!
#
#  Requirements (auto-installed by install_dependencies.bat):
#    pip install opencv-python mediapipe
#
#  FH6 Settings (do once):
#    Advanced Controls  -> Mouse Free Look  = ON
#    HUD & Gameplay     -> Drift Camera     = ON
#    Camera View        -> Driver (cockpit cam)
#
#  Tips for best webcam tracking:
#    - Good lighting on your face (avoid backlight)
#    - Webcam at eye level, roughly centred on your face
#    - Keep 40-80cm from camera
#    - A plain background helps MediaPipe track better
# ============================================================

import time
import sys
import ctypes
import math

# ============================================================
#  CONFIGURATION - Tweak these to your preference
# ============================================================

# Webcam device index (0 = default camera, 1 = second camera etc.)
CAMERA_INDEX = 0

# How far you turn your head for the camera to fully pan (degrees)
MAX_YAW   = 30.0
MAX_PITCH = 20.0

# Ignores tiny head movements below this threshold (0.0 - 0.3)
DEAD_ZONE = 0.18

# Smoothing: higher = smoother but slower (0.80 - 0.98)
SMOOTHING = 0.95

# Camera tracking speed
MOUSE_SPEED  = 5
RETURN_SPEED = 3

# Non-linear curve for precision at small angles (1.0 - 3.0)
CURVE = 2.5

# Maximum degrees per frame - filters sudden movements
MAX_DELTA_PER_FRAME = 6.0

# Set True if up/down feels backwards
INVERT_PITCH = False

# Show webcam preview window (useful for setup, turn off while racing)
SHOW_PREVIEW = True

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

def draw_bar(value, width=28):
    c      = width // 2
    filled = min(int(abs(value) * c), c)
    if value >= 0:
        bar = " " * c + "|" + "=" * filled + " " * (c - filled)
    else:
        bar = " " * (c - filled) + "=" * filled + "|" + " " * c
    return "[" + bar + "]"

def check_dependencies():
    missing = []
    try:
        import cv2
    except ImportError:
        missing.append("opencv-python")
    try:
        import mediapipe
    except ImportError:
        missing.append("mediapipe")
    if missing:
        print("")
        print("  [ERROR] Missing packages: " + ", ".join(missing))
        print("  Run install_dependencies.bat to fix this.")
        input("  Press Enter to exit...")
        sys.exit(1)

# ============================================================
#  HEAD POSE ESTIMATION
#  Uses MediaPipe face mesh landmarks to calculate yaw/pitch
# ============================================================

def get_head_angles(face_landmarks, frame_w, frame_h):
    """
    Estimates head yaw (left/right) and pitch (up/down) from
    MediaPipe face mesh landmarks using key facial points.
    Returns (yaw_degrees, pitch_degrees).
    """
    # Key landmark indices for pose estimation
    # Nose tip, chin, left eye corner, right eye corner, left mouth, right mouth
    NOSE_TIP    = 1
    CHIN        = 152
    LEFT_EYE    = 263
    RIGHT_EYE   = 33
    LEFT_MOUTH  = 287
    RIGHT_MOUTH = 57

    lm = face_landmarks.landmark

    def to_px(landmark):
        return (landmark.x * frame_w, landmark.y * frame_h)

    nose  = to_px(lm[NOSE_TIP])
    chin  = to_px(lm[CHIN])
    l_eye = to_px(lm[LEFT_EYE])
    r_eye = to_px(lm[RIGHT_EYE])

    # Yaw: difference between distances of nose to each eye
    # When looking left, nose moves closer to left eye
    dist_l = math.sqrt((nose[0] - l_eye[0])**2 + (nose[1] - l_eye[1])**2)
    dist_r = math.sqrt((nose[0] - r_eye[0])**2 + (nose[1] - r_eye[1])**2)
    eye_span = math.sqrt((l_eye[0] - r_eye[0])**2 + (l_eye[1] - r_eye[1])**2)

    if eye_span > 0:
        yaw_raw = (dist_r - dist_l) / eye_span * 90.0
    else:
        yaw_raw = 0.0

    # Pitch: vertical position of nose relative to eye-chin midpoint
    eye_mid_y  = (l_eye[1] + r_eye[1]) / 2.0
    face_height = abs(chin[1] - eye_mid_y)
    if face_height > 0:
        pitch_raw = ((nose[1] - eye_mid_y) / face_height - 0.45) * 120.0
    else:
        pitch_raw = 0.0

    return clamp(yaw_raw, -90, 90), clamp(pitch_raw, -60, 60)

# ============================================================
#  MAIN
# ============================================================

def main():
    check_dependencies()
    import cv2
    import mediapipe as mp

    print("=" * 58)
    print("  FH6 Webcam Head Tracking  v1.0.0")
    print("=" * 58)
    print("  Smoothing: {}   Dead zone: {}   Curve: {}".format(SMOOTHING, DEAD_ZONE, CURVE))
    print("-" * 58)
    print("  FH6: Advanced Controls -> Mouse Free Look = ON")
    print("  FH6: HUD & Gameplay    -> Drift Camera    = ON")
    print("  FH6: Camera View       -> Driver (cockpit)")
    print("-" * 58)
    print("")
    print("  Opening camera {}...".format(CAMERA_INDEX))

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("  [ERROR] Could not open camera {}.".format(CAMERA_INDEX))
        print("  Try changing CAMERA_INDEX to 1 or 2 at the top of the script.")
        input("  Press Enter to exit...")
        sys.exit(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    print("  [OK] Camera opened.")

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh    = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6
    )
    print("  [OK] MediaPipe face mesh ready.")
    print("  [OK] Input system ready.")
    if SHOW_PREVIEW:
        print("  [OK] Preview window enabled (close it or set SHOW_PREVIEW=False to hide).")
    print("")
    print("  Position your face in the camera view, then launch FH6.")
    print("  Ctrl+C to stop.")
    print("")

    smooth_yaw   = 0.0
    smooth_pitch = 0.0
    cam_yaw      = 0.0
    cam_pitch    = 0.0
    rmb_held     = False
    prev_yaw     = 0.0
    prev_pitch   = 0.0
    last_print   = time.time()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("\n  [WARNING] Camera frame dropped.")
                time.sleep(0.05)
                continue

            frame_h, frame_w = frame.shape[:2]
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)

            raw_yaw, raw_pitch = 0.0, 0.0
            face_detected = False

            if results.multi_face_landmarks:
                face_detected = True
                raw_yaw, raw_pitch = get_head_angles(
                    results.multi_face_landmarks[0], frame_w, frame_h)

                # Spike rejection
                delta_yaw   = raw_yaw   - prev_yaw
                delta_pitch = raw_pitch - prev_pitch
                if abs(delta_yaw) > MAX_DELTA_PER_FRAME:
                    raw_yaw   = prev_yaw   + MAX_DELTA_PER_FRAME * (1 if delta_yaw > 0 else -1)
                if abs(delta_pitch) > MAX_DELTA_PER_FRAME:
                    raw_pitch = prev_pitch + MAX_DELTA_PER_FRAME * (1 if delta_pitch > 0 else -1)
                prev_yaw   = raw_yaw
                prev_pitch = raw_pitch

                # Normalise, dead zone, curve, smooth
                norm_yaw     = clamp(raw_yaw   / MAX_YAW,   -1.0, 1.0)
                norm_pitch   = clamp(raw_pitch / MAX_PITCH, -1.0, 1.0)
                dz_yaw       = apply_dead_zone(norm_yaw,   DEAD_ZONE)
                dz_pitch     = apply_dead_zone(norm_pitch, DEAD_ZONE)
                curved_yaw   = apply_curve(dz_yaw,   CURVE)
                curved_pitch = apply_curve(dz_pitch, CURVE)
                if INVERT_PITCH:
                    curved_pitch = -curved_pitch
                smooth_yaw   = smooth_val(smooth_yaw,   curved_yaw,   SMOOTHING)
                smooth_pitch = smooth_val(smooth_pitch, curved_pitch, SMOOTHING)
            else:
                # No face detected - smoothly return to neutral
                smooth_yaw   = smooth_val(smooth_yaw,   0.0, 0.85)
                smooth_pitch = smooth_val(smooth_pitch, 0.0, 0.85)

            fh6_focus = "Forza Horizon 6" in get_foreground_title()

            if fh6_focus and face_detected:
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
                if not fh6_focus:
                    smooth_yaw = smooth_pitch = cam_yaw = cam_pitch = 0.0

            # Preview window
            if SHOW_PREVIEW:
                color = (0, 255, 0) if face_detected else (0, 0, 255)
                label = "Yaw:{:+.1f} Pitch:{:+.1f}".format(raw_yaw, raw_pitch)
                cv2.putText(frame, label, (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                status = "IN GAME" if fh6_focus else "STANDBY"
                cv2.putText(frame, status, (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                if not face_detected:
                    cv2.putText(frame, "NO FACE DETECTED", (10, 90),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.imshow("FH6 Head Tracking - Preview (close to hide)", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # Console display
            if time.time() - last_print > 0.1:
                bar  = draw_bar(smooth_yaw)
                face = "face:OK " if face_detected else "face:--- "
                sys.stdout.write("\r  {} {:+5.1f}deg  {}RMB:{} {}    ".format(
                    bar, raw_yaw, face,
                    "ON " if rmb_held else "off",
                    "[IN GAME]" if fh6_focus else "[standby]"))
                sys.stdout.flush()
                last_print = time.time()

    except KeyboardInterrupt:
        pass
    finally:
        if rmb_held:
            send_input(MOUSEEVENTF_RIGHTUP)
        cap.release()
        cv2.destroyAllWindows()
        print("\n\n  Tracking stopped. Goodbye!")

if __name__ == "__main__":
    main()
