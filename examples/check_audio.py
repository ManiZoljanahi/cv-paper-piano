""" This script is a diagnostic tool to verify that FluidSynth, the SoundFont, and the audio drivers are working correctly before running the main app. """

import sys
import os
import time

# Add the parent directory to Python system's path so we can import 'src'.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.audio_engine import AudioEngine 

def check_scale():
    print("Initializing Audio Engine...")

    # Wraps execution to catch errors (like missing SoundFonts).
    try:

        # Starts the audio engine.
        engine = AudioEngine()
        print("Playing C Major Scale...")

        # Defines a list of MIDI note numbers corresponding to a C Major scale (Middle C to High C).
        # C,  D,  E,  F,  G,  A,  B,  C
        scale = [60, 62, 64, 65, 67, 69, 71, 72]

        # Iterates through each note in the list.
        for note in scale:
            print(f"Playing note: {note}")

            # Triggers the sound.
            engine.note_on(note)

            # Waits 0.3 seconds (note duration).
            time.sleep(0.3)

            # Stops the note (though note_on usually handles decay, this is good practice).
            engine.note_off(note)

        # Prints success if the loop finishes.
        print("Success! Audio is working.")

    except Exception as e:
        print(f"Error: {e}")
        print("Did you put the .sf2 or .sf3 file in assets/soundfonts/?")

# Ensures the function only runs if the file is executed directly.
if __name__ == "__main__":
    check_scale()