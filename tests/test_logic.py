""" Unit tests for the Piano Logic. """

from src.piano_logic import PianoMapper

# Checks if touching the very left edge (0.01) returns the first note of the active list.
def test_page_boundaries():
    logic = PianoMapper()
    logic.set_sheet_by_id(0)

    # The very far left edge (4%)
    assert logic.get_note_at_percent(0.04) == "C1"

# Verifies that a specific percentage corresponds to a specific sharp note.
def test_black_key_split():
    logic = PianoMapper()
    logic.set_sheet_by_id(0)

    # Slightly to the right (10%)
    assert logic.get_note_at_percent(0.10) == "C#1"

# Verifies that changing the marker ID changes the octave.
# Checks that passing Marker ID 2 updates the internal state to start at "C2" (Octave 2).
def test_octave_switching():
    logic = PianoMapper()

    # Default is Octave 1.
    assert logic.current_start_octave == 1

    # Simulate seeing Marker ID 2 (should be Octave 2).
    logic.set_sheet_by_id(2)
    assert logic.current_start_octave == 2

    # Verify the keys list updated (First note should be C2).
    assert logic.active_keys[0] == "C2"

# Verifies looking up a note by percentage.
# Checks that 0.0% on Marker 0 returns "C1".
def test_note_lookup():
    logic = PianoMapper()

    # Ensure we are on Octave 1.
    logic.set_sheet_by_id(0)

    # 0.0 (0%) -> First Index -> C1.
    assert logic.get_note_at_percent(0.0) == "C1"