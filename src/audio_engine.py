""" This module handles the actual generation of sound using the FluidSynth library. """

import os
from fluidsynth import Synth

# Forces the use of 'dsound' (DirectSound) on Windows ('alsa' for Linux and 'coreaudio' for Mac).
os.environ["SDL_AUDIODRIVER"] = "dsound"
os.environ["FLUID_AUDIO_DRIVER"] = "dsound"

class AudioEngine:
    def __init__(self):

        # Creates a synthesizer instance.
        self.fs = Synth()
        
        # Tries to start the audio driver. Has a fallback bare start() if DirectSound fails.
        try:
            self.fs.start(driver="dsound")
        except:
            self.fs.start()

        # Calculates the path to assets/soundfonts/grand_piano.sf2 or assets/soundfonts/grand_piano.sf3.
        current_dir = os.path.dirname(os.path.abspath(__file__))      # Or "grand_piano.sf3"
        sf2_path = os.path.join(current_dir, "..", "assets", "soundfonts", "grand_piano.sf2")

        # Checks if the file exists. If yes, loads it (sfload) and selects it (program_select). If no, prints a warning.
                    # Or (sf3_path)
        if os.path.exists(sf2_path):
                            # Or (sf3_path)
            sfid = self.fs.sfload(sf2_path)
            self.fs.program_select(0, sfid, 0, 0)
        else:                                  # Or {sf3_path}
            print(f"Warning: Soundfont not found at {sf2_path}")

        # Sends a MIDI Control Change message to set Channel 0 volume to Max.
        self.fs.cc(0, 7, 127)

    def note_on(self, note_str):

        # Converts a string (e.g., "C#4") to a MIDI integer using _note_to_midi.
        midi = self._note_to_midi(note_str)

        # If valid, sends noteon command (Channel 0, MIDI Number, Velocity 100).
        if midi:
            self.fs.noteon(0, midi, 100)

    def _note_to_midi(self, note):
        try:

            # A helper function. Defines a list notes_map.
            notes_map = [
                "C",
                "C#",
                "D",
                "D#",
                "E",
                "F",
                "F#",
                "G",
                "G#",
                "A",
                "A#",
                "B",
            ]

            # Parses the string to separate the Note Name (e.g., "C#") from the Octave (e.g., "3").
            if "#" in note:
                # e.g., C#3
                name = note[:2]  # C#
                octave = int(note[2])  # 3
            else:
                # e.g., C3
                name = note[:1]  # C
                octave = int(note[1])  # 3

            # This converts standard notation to MIDI numbers (where C4 is 60).
            return (octave + 1) * 12 + notes_map.index(name)
        except:
            return None