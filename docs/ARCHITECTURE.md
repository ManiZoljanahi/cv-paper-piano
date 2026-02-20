# Architecture Reference

## 1. System Overview

**CV Paper Piano** is a real-time Computer Vision (CV) application designed to assist playing piano on paper. It bridges the physical world (a piano printed on paper) and the digital world (sheet music logic) using Computer Vision.

The system operates on a **Sense-Think-Act** loop:
1.  **Sense:** Captures video frame and detects hand landmarks + ArUco markers.
2.  **Think:** Maps spatial coordinates to musical notes using a custom Homography algorithm and Per-Sheet Calibration algorithm. 
3.  **Act:** Renders visual overlays (UI) and synthesizes audio feedback.

## 2. Component Design

### A. The Vision Layer (`src/main.py`)
* **Input:** Webcam feed (default 30 FPS).
* **Fiducial Tracking:** Uses `cv2.aruco` to detect 2 corner markers on printed paper sheets.
* **Hand Tracking:** Uses `MediaPipe Hands` to identify fingertips (Landmark IDs: 8, 12, 16, 20).
* **Perspective Transform:** Calculates a 2D vector across the "Sheet Space" to map virtual keys.

### B. The Logic Layer (`src/piano_logic.py` & `main.py`)
* **Coordinate System:** Normalizes the piano keyboard into a 0.0 to 1.0 float range.
* **Per-Sheet Calibration:** To counter optical lens distortion (e.g., barrel/pincushion distortion at the edges of the camera view), the system uses a `SHEET_CONFIG` dictionary. Each physical page has independent tuning for Left Padding, Right Padding, and Linearity Bias.
* **Octave Management:** Dynamically calculates Octave shifts based on marker IDs to support the full 88-key range without recalibration.

### C. The Audio Layer (`src/audio_engine.py`)
* **Synthesis:** Uses `FluidSynth` to load SoundFonts (`.sf2` or `.sf3`) for realistic piano timbre.
* **Latency Management:** Implements `dsound` (Windows) or `alsa` (Linux) or `coreaudio` (Mac) drivers to minimize the delay between visual detection and audio trigger (<50ms target).

### D. The Data Layer (`src/db_manager.py`)
* **Storage:** SQLite database (`assets/database/piano_stats.db`) mapped to RAM (`:memory:`) during testing.
* **Schema:** Tracks `Sessions` and `Notes` to generate user progress reports.

## 3. Key Algorithms

### Advanced Perspective Calibration
We do not use standard 3D camera calibration. Instead, the "Sheet" is dynamically projected using independent margins to fix optical protrusion:
$$u_{raw} = \frac{i + 0.5}{num\_keys}$$
To correct for perspective squash, a linearity bias is applied:
$$u_{biased} = u_{raw}^{bias}$$
Finally, the coordinate is squeezed between the specific page's defined margins:
$$u = PADDING\_LEFT + (u_{biased} \cdot (1.0 - (PADDING\_LEFT + PADDING\_RIGHT)))$$

### Zig-Zag Key Layout
To handle the occlusion of white keys by black keys, the hit-boxes use a staggered Y-offset:
* **Black Keys:** Trigger zone is higher (offset 90px, closer to the fallboard).
* **White Keys:** Trigger zone is lower (offset 130px, closer to the player).