""" Unit tests for the Database Manager. """

import pytest
from src.db_manager import MusicDB

# Decorates the function so it can be injected into test functions as an argument.
@pytest.fixture

# Creates a temporary, in-memory database (:memory:) so tests don't clutter the disk.
def db():
    return MusicDB(db_path=":memory:")

# Verifies that the Sessions table exists in the schema.
# Check if tables are created automatically.
def test_create_tables(db):
    cursor = db.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Sessions';")
    assert cursor.fetchone() is not None

# Checks if starting a session returns an Integer ID greater than 0.
def test_start_session(db):
    session_id = db.start_session()
    assert isinstance(session_id, int)
    assert session_id > 0

def test_log_note(db):

    # Starts a session.
    session_id = db.start_session()
    test_note = 60

    # Logs a note (60)
    db.log_note(session_id, test_note)
    cursor = db.conn.cursor()

    # Queries the DB to ensure the note was actually saved with the correct session ID.
    cursor.execute("SELECT note, session_id FROM Notes WHERE session_id=?", (session_id,))
    result = cursor.fetchone()

    assert result is not None
    assert result[0] == 60
    assert result[1] == session_id