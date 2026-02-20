# CV Paper Piano: A Computer Vision Paper-based Piano

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green)

**CV Paper Piano** is a Computer Vision (CV) application that turns printed papar piano into a playable piano. 

Using only a standard webcam and computer vision, it tracks finger movements in real-time, overlays virtual guides on the paper keys, and provides instant audio-visual feedback—no expensive hardware or MIDI cables, or AR Headsets required.

---

## Features

* **Hardware Agnostic:** Works with printed paper sheets. No electric connection needed.
* **Per-Sheet Calibration:** Automatically corrects camera lens perspective distortion on a page-by-page basis for flawless geometric alignment.
* **Real-Time Tracking:** High-speed finger tracking using MediaPipe.
* **Smart Mapping:** Uses ArUco fiducial markers to map the physical 3D space to digital sheet music.
* **Minimal UI:** Non-intrusive augmented overlays that show you *where* to play without blocking your view of the keys.
* **Session Analytics:** Automatically logs practice sessions and accuracy to a local SQLite database.

## Quick Start

### 1. Check if FluidSynth is installed
```bash
fluidsynth --version
```
### if FluidSynth is not installed, then install it
* For Windows: Install [FluidSynth](https://github.com/FluidSynth/fluidsynth/releases) and add it to your System PATH (e.g., C:/tool)
* For Linux:
```bash
sudo apt update
sudo apt install fluidsynth
```
* For Mac:
```bash
brew install fluidsynth
```

### 2. Software Installation
```bash
# Clone the repository
git clone https://github.com/ManiZoljanahi/cv-paper-piano.git

# Create and activate Virtual Environment and install dependencies
python -m venv venv
venv\Scripts\activate # Windows
# On Linux / Mac: source venv/bin/activate
pip install -r requirements.txt

# Create an Environment file
copy .env.example .env # Windows
# On Linux / Mac: cp .env.example .env

# Run the generator
python src/generator.py 
```

### 3. Print the Piano Sheets inside `piano_pages` directory

### 4. Install Piano SoundFont
Install [Essential Keys-sforzando-v9.6.sf2](https://huggingface.co/datasets/projectlosangeles/soundfonts4u/resolve/main/Essential%20Keys-sforzando-v9.6.sf2) and change its name to `grand_piano.sf2`, and then put it in `assets/soundfonts` directory.
* **Hint:** Reduce SoundFont's storage by exporting `grand_piano.sf2` to `grand_piano.sf3`.

### 5. Hardware Setup
* Place the printed **ArUco Marker Piano Sheet** on your piano's music stand.
* Position your webcam to overlook the piano sheet (bird's-eye view or angled down).

### 6. Launch the application
```Bash
python main.py
```

## Technology
| Component |    Technology     |             Purpose              |
|   :---:   |       :---:       |              :---:               |
|   Vision  | OpenCV, MediaPipe | Image processing & Hand tracking |
|   Logic   |   Python (NumPy)  |  Coordinate mapping & Homography |
|   Audio   |     FluidSynth    |    Low-latency audio synthesis   |
|   GUI     |     PyWebView     |      Modern HTML/CSS frontend    |
|   Data    |      SQLite       |        Performance tracking      |

## Documentation
* [Architecture Guide](docs/ARCHITECTURE.md): Deep dive into the Homography logic and Per-Sheet perspective correction algorithm.
* [Contributing](docs/CONTRIBUTING.md): Guidelines for developers and testers.

## License
* This project is open-source and available under the [MIT License](LICENSE).