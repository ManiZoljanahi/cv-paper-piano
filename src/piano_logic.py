""" This manages the translation of "Where is my finger?" to "What note is this?" """

class PianoMapper:

    # Defines note_names (C through B). Sets default octave to 1.
    def __init__(self):
        self.note_names = [
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
        self.current_start_octave = 1
        self.active_keys = []
        self.update_active_keys()

    # Creates a list of strings (e.g., ["C1", "C#1", "D1"...]) for the current octave.
    def update_active_keys(self):

        # Strict 12-key generation
        self.active_keys = [f"{note}{self.current_start_octave}" for note in self.note_names]

    # Takes the ArUco marker ID seen by the camera.
    def set_sheet_by_id(self, marker_id):

        # Calculates normalized_octave = (marker_id // 2) + 1. (e.g., Markers 0 and 1 -> Octave 1).
        normalized_octave = int(marker_id // 2) + 1

        # Clamps value between 1 and 7.
        if normalized_octave < 1:
            normalized_octave = 1
        if normalized_octave > 7:
            normalized_octave = 7

        # Updates active_keys if the octave changed.
        if self.current_start_octave != normalized_octave:
            self.current_start_octave = normalized_octave
            self.update_active_keys()

    def get_note_at_percent(self, u):

        # Takes u (0.0 to 1.0), representing the horizontal position on the paper.
        if u < 0 or u >= 1.0:
            return None

        # Maps this percentage to an index in the active_keys list.
        idx = int(u * len(self.active_keys))

        # Returns the specific note name (e.g., "C#3").
        if 0 <= idx < len(self.active_keys):
            return self.active_keys[idx]

        return None