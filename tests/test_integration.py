""" This tests how different parts of your system (Logic, Audio, DB) work together. """

# Used to temporarily replace objects during a specific test.
from unittest.mock import patch

from src.piano_logic import PianoMapper
from src.db_manager import MusicDB

# Receives mock_audio_engine automatically from conftest.py. (mock_audio_engine is a fixture from conftest.py.)
def test_full_note_flow(mock_audio_engine):

    # Initializes logic.
    logic = PianoMapper()

    # Initializes db using ":memory:".
    # This creates a temporary RAM database that vanishes after the test, keeping things fast and clean.
    db = MusicDB(db_path=":memory:")

    # Starts a session (session_id).
    session_id = db.start_session()

    # Simulates looking at Page 1.
    logic.set_sheet_by_id(0)

    # Simulates touching the exact center of the page.
    # In piano_logic.py, get_note_at_percent(0.5) returns the note at index 6 (F#1).
    detected_note = logic.get_note_at_percent(0.5)

    # Simulates System Response (Checks the "If Hit" block in main.py.).
    if detected_note:
        # Calls Audio Playback.
        mock_audio_engine.note_on(detected_note)
        # Calls Database Logging.
        db.log_note(session_id, detected_note)

    # Verifies Logic.
    assert detected_note == "F#1"

    # Checks if the audio library's trigger function was actually touched.
    mock_audio_engine.fs.noteon.assert_called()

    # Queries the database to ensure the note "F#1" was successfully saved.
    cursor = db.conn.cursor()
    cursor.execute("SELECT note FROM Notes WHERE session_id=?", (session_id,))
    result = cursor.fetchone()

    assert result is not None
    assert result[0] == "F#1"

# Ensure the app tries a backup method if the main audio driver fails.
def test_audio_driver_fallback():

    # Temporarily replaces the Synth class inside the audio_engine file.
    with patch("src.audio_engine.Synth") as MockSynth:
        instance = MockSynth.return_value

        # Configures the mock so the first time start() is called, it crashes (simulating dsound failure).
        # The 2nd time start() is called, it returns None (simulating success).
        instance.start.side_effect = [Exception("dsound failed"), None]

        # Import inside function to ensure patch is active
        from src.audio_engine import AudioEngine

        # Initializes the engine.
        AudioEngine()

        # Verifies that the code tried twice, once for dsound, and once for default (Primary -> Fail -> Fallback).
        assert instance.start.call_count == 2