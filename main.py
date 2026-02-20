""" The core application logic. """

import os
import sys
import time
import threading
import base64
import ctypes

# Disables TensorFlow logs
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
# Sets SDL_AUDIODRIVER to dsound
# Use 'dsound' for Windows, 'alsa' for Linux, 'coreaudio' for Mac
os.environ["SDL_AUDIODRIVER"] = "dsound"

# Uses ctypes to hide the black console window when running as an EXE.
if os.name == "nt":
    try:
        kernel32 = ctypes.windll.kernel32
        kernel32.SetStdHandle(-11, 0)
        kernel32.SetStdHandle(-12, 0)
    except Exception:
        pass

import cv2
import numpy as np
import mediapipe as mp
import webview

# Add the parent directory to Python system's path so we can import 'src'.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.piano_logic import PianoMapper
from src.audio_engine import AudioEngine
from src.db_manager import MusicDB

# Defines signal_ui_ready which web/script.js calls to trigger start_camera.
class JSApi:
    def __init__(self, app_instance):
        self._app = app_instance
    def signal_ui_ready(self):
        self._app.start_camera()

class PianoApp:
    def __init__(self):
        self.window = None
        self.running = False
        self.shutting_down = False
        self.logic = PianoMapper()

        # Initialize audio
        try:
            self.audio = AudioEngine()
        except:
            self.audio = None

        # Initialize database
        try:
            self.db = MusicDB()
            self.session = self.db.start_session()
        except:
            self.db = None

        # Mathematically builds the list FULL_88_KEYS containing every note from A0 to C8.
        self.FULL_88_KEYS = []
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        self.FULL_88_KEYS.extend(["A0", "A#0", "B0"])
        for octave in range(1, 8):
            for note in notes:
                self.FULL_88_KEYS.append(f"{note}{octave}")
        self.FULL_88_KEYS.append("C8")

        # Hardcodes the mapping. This ensures Perfect Pitch mapping across the whole keyboard.
        self.SHEET_MAP = {}
        self.SHEET_MAP[0] = self.FULL_88_KEYS[0:15]
        self.SHEET_MAP[2] = self.FULL_88_KEYS[15:31]
        self.SHEET_MAP[4] = self.FULL_88_KEYS[30:43]
        self.SHEET_MAP[6] = self.FULL_88_KEYS[45:62]
        self.SHEET_MAP[8] = self.FULL_88_KEYS[61:77]
        self.SHEET_MAP[10] = self.FULL_88_KEYS[76:88]

    # Launches _cv_loop in a background thread to keep the GUI responsive.
    def start_camera(self):
        if not self.running:
            self.running = True
            # Daemon=True means this thread dies when the main program dies.
            thread = threading.Thread(target=self._cv_loop, daemon=True)
            thread.start()

    # Opens Camera (Index 0 or 1).
    def _cv_loop(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(1)

        # Sets 1280x720 resolution.
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # Initializes MediaPipe Hands.
        # Configures to look for a maximum of 2 hands and uses a simple, fast tracking model.
        mp_hands = mp.solutions.hands.Hands(
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
            max_num_hands=2,
            model_complexity=0,
        )

        # Loads the ArUco 4x4 dictionary (the tyoe of markers you printed).
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        aruco_params = cv2.aruco.DetectorParameters()

        # Remembers what note each finger was playing last frame.
        finger_states = {}

        # Tracks which page we are looking at.
        current_sheet_id = -1
        active_keys_list = []
        frame_count = 0

        # Define the vertical Zig-Zag hit zones.
        OFFSET_BLACK = 90
        OFFSET_WHITE = 130
        # Defines how close a finger needs to be to trigger a note.
        HIT_RADIUS = 15

        # Holds the per-page calibration to fix the camera distortion.
        # Define specific padding for each sheet ID to fix mismatches.
        # 'pad_l': Left padding: Moves keys RIGHT (Pushing from left)
        # 'pad_r': Right padding: Moves keys LEFT (Pushing from right)
        # 'bias': 1.0 is linear. 0.95 pushes left, 1.05 pushes right.
        SHEET_CONFIG = {
            # Page 1 (Base/Low Notes) - Usually standard
            0: {"pad_l": 0.06, "pad_r": 0.06, "bias": 1.0},
            # Page 2 - Usually standard
            2: {"pad_l": 0.06, "pad_r": 0.06, "bias": 1.0},
            # Page 3 (The Problematic Sheet) - Mismatch Fix
            # Increased pad_l to push keys right, decreased pad_r slightly
            4: {"pad_l": 0.08, "pad_r": 0.04, "bias": 1.0},
            # Page 4
            6: {"pad_l": 0.06, "pad_r": 0.06, "bias": 1.0},
            # Page 5
            8: {"pad_l": 0.06, "pad_r": 0.06, "bias": 1.0},
            # Page 6 (High Notes)
            10: {"pad_l": 0.06, "pad_r": 0.06, "bias": 1.0},
        }
        # Default fallback
        DEFAULT_CONFIG = {"pad_l": 0.06, "pad_r": 0.06, "bias": 1.0}

        # Starts the continuous while loop.
        while self.running and not self.shutting_down:

            # Reads a frame.
            ret, raw_frame = cap.read()

            # If the frame is empty, waits 0.1 seconds, and then skips the rest of the loop.
            if not ret:
                time.sleep(0.1)
                continue

            # Increments the frame counter.
            frame_count += 1
            h, w, _ = raw_frame.shape

            # Detects ArUco markers. Gets the ID. Normalizes it (even numbers).
            corners, ids, _ = cv2.aruco.detectMarkers(raw_frame, aruco_dict, parameters=aruco_params)
            detected_id_display = "None"
            current_config = DEFAULT_CONFIG

            # Finds the lowest Marker ID.
            if ids is not None and len(ids) > 0:
                raw_id = int(np.min(ids))
                # Normalizes odd numbers to even numbers.
                normalized_id = raw_id if raw_id % 2 == 0 else raw_id - 1
                detected_id_display = str(normalized_id)
                # Fetches calibration for this specific sheet.
                current_config = SHEET_CONFIG.get(normalized_id, DEFAULT_CONFIG)

                # If the sheet changed from the last frame, it updates the active_keys_list from the SHEET_MAP.
                if normalized_id != current_sheet_id:
                    current_sheet_id = normalized_id
                    if normalized_id in self.SHEET_MAP:
                        active_keys_list = self.SHEET_MAP[normalized_id]
                    else:
                        active_keys_list = []

            # Flips the image so it acts like a mirror (intuitive for users).
            display_frame = cv2.flip(raw_frame, 1)
            # Resizes it to 854x480 for better performance.
            display_frame = cv2.resize(display_frame, (854, 480))
            dh, dw, _ = display_frame.shape
            # Converts color space to RGB for MediaPipe.
            rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)

            status = f"Sheet:{detected_id_display} Keys:{len(active_keys_list)}"
            is_locked = False
            key_targets = []

            # Calculates the center points of the ArUco markers.
            if ids is not None and len(ids) >= 2 and len(active_keys_list) > 0:
                centers = []
                for c in corners:
                    cx = np.mean(c[0][:, 0])
                    cy = np.mean(c[0][:, 1])
                    sx, sy = dw / w, dh / h
                    centers.append((dw - (cx * sx), cy * sy))

                # Sorts the center points of the ArUco markers left-to-right.
                centers.sort(key=lambda p: p[0])
                p_left, p_right = centers[0], centers[-1]

                # Calculates the 2D vector (bx, by) connecting them.
                bx = p_right[0] - p_left[0]
                by = p_right[1] - p_left[1]

                # Calculates the perpendicular vector (prep_x, perp_y) pointing "downward" on the paper to offset the keys.
                perp_x = by
                perp_y = -bx
                mag = (perp_x ** 2 + perp_y ** 2) ** 0.5
                if mag > 0:
                    perp_x /= mag
                    perp_y /= mag
                else:
                    perp_x, perp_y = 0, -1

                num_keys = len(active_keys_list)

                # Extract and use the specific values from the active config dictionary.
                PADDING_LEFT = current_config["pad_l"]
                PADDING_RIGHT = current_config["pad_r"]
                LINEARITY_BIAS = current_config["bias"]

                # Loops through the number of active keys.
                for i in range(num_keys):

                    # This separates the hit zones vertically.
                    note_name = active_keys_list[i]

                    # If note has #, offset is OFFSET_BLACK (90px).
                    if "#" in note_name:
                        current_offset = OFFSET_BLACK
                    # If natural, offset is OFFSET_WHITE (130px).
                    else:
                        current_offset = OFFSET_WHITE

                    # Calculates raw percentage.
                    u_raw = (i + 0.5) / num_keys
                    # Applies the Linearity Bias (Perspective Correction).
                    u_biased = u_raw ** LINEARITY_BIAS
                    # Calculates the usable space (applies Independent Padding).
                    usable_width = 1.0 - (PADDING_LEFT + PADDING_RIGHT)
                    # Squeezes the key into its final coordinate percentage.
                    u = PADDING_LEFT + (u_biased * usable_width)
                    # Finds exact pixel coordinates on the screen (project to screen coordinates).
                    base_x = p_left[0] + bx * u
                    base_y = p_left[1] + by * u
                    center_x = int(base_x + perp_x * current_offset)
                    center_y = int(base_y + perp_y * current_offset)
                    # Saves the target to key_targets.
                    key_targets.append({"pos": (center_x, center_y), "note": note_name, "hit": False})

                    # Draws a faint grey circle at target positions on the screen.
                    cv2.circle(
                        display_frame,
                        (center_x, center_y),
                        HIT_RADIUS,
                        (160, 160, 160),
                        1,
                    )
                is_locked = True

            # Analyzes the frame for hands.
            res = mp_hands.process(rgb)
            # If hands are found, it draws the skeletal skeleton over them.
            if res.multi_hand_landmarks:
                for hand_lm in res.multi_hand_landmarks:
                    mp.solutions.drawing_utils.draw_landmarks(
                        display_frame, hand_lm, mp.solutions.hands.HAND_CONNECTIONS
                    )

                    # Loops through the 4 fingertip landmark IDs (8=Index, 12=Middle, 16=Ring, 20=Pinky).
                    for tip_idx in [8, 12, 16, 20]:
                        # Converts normalized MediaPipe coordinates (0.0 to 1.0) into real pixel coordinates (fx, fy).
                        tip = hand_lm.landmark[tip_idx]
                        fx, fy = int(tip.x * dw), int(tip.y * dh)
                        fid = f"{tip_idx}"
                        if is_locked:
                            active_note = None

                            # Calculates Euclidean distance between fingertip and every key target.
                            for btn in key_targets:
                                tx, ty = btn["pos"]
                                dist = ((fx - tx) ** 2 + (fy - ty) ** 2) ** 0.5

                                # If distance < HIT_RADIUS:
                                if dist < HIT_RADIUS:
                                    # Marks it as a hit.
                                    active_note = btn["note"]
                                    btn["hit"] = True
                                    # Draws a solid green circle.
                                    cv2.circle(
                                        display_frame,
                                        (tx, ty),
                                        HIT_RADIUS,
                                        (0, 255, 0),
                                        -1,
                                    )
                                    # Draws text to show visual feedback.
                                    cv2.putText(
                                        display_frame,
                                        active_note,
                                        (tx - 10, ty - 20),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        0.5,
                                        (0, 255, 0),
                                        2,
                                    )
                                    # Break out of the loop (a finger can only press one key at a time).
                                    break

                            # Looks up what note this specific finger was playing in the previous frame.
                            previous_note = finger_states.get(fid)
                            if active_note:
                                # If the finger just hit a new note (different from previous frame for that finger):
                                if active_note != previous_note:
                                    if self.audio:
                                        # Plays audio.
                                        self.audio.note_on(active_note)
                                    if self.db:
                                        # Logs it to the database.
                                        self.db.log_note(self.session, active_note)
                                        # Sends a JavaScript command to update the HTML UI.
                                    self._send_js(f"highlightNoteString('{active_note}')")
                                    # Updates the finger's current state.
                                    finger_states[fid] = active_note
                            # If no note is pressed, clears the state to None.
                            else:
                                finger_states[fid] = None

            # Updates the UI every 2 frames for performance.
            if frame_count % 2 == 0 and not self.shutting_down:
                # Encodes the OpenCV frame into a JPEG.
                _, buf = cv2.imencode(".jpg", display_frame)
                # Converts it to a Base64 string
                b64 = base64.b64encode(buf).decode("utf-8")
                # Sends to JavaScript via evaluate_js to render the video on the webpage.
                self._send_js(f"updateFrame('{b64}')")
                self._send_js(f"updateStatus('{status}', {'false' if is_locked else 'true'})")

        cap.release()

    # Evaluate JavaScript code in the PyWebView window safely.
    def _send_js(self, code):
        if self.window and not self.shutting_down:
            try:
                self.window.evaluate_js(code)
            except:
                self.shutting_down = True

    # Breaks the while loop and closes the window safely.
    def quit(self):
        self.shutting_down = True
        self.running = False
        if self.window:
            self.window.destroy()

# Ensures the functions only run if the files is executed directly.
if __name__ == "__main__":
    # Creates the PianoApp instance.
    app = PianoApp()
    # Creates the JSApi bridge.
    api = JSApi(app)
    # Creates the webview window pointing to web/index.html.
    window = webview.create_window("CV Paper Piano", "web/index.html", js_api=api, width=1100, height=700)
    app.window = window
    # Binds the app.quit method to the window's close event.
    window.events.closed += app.quit
    # Starts the webview.
    webview.start(debug=False)