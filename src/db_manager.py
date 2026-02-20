""" This handles saving sessions and notes data to a SQLite database. """

import sqlite3
import os
from datetime import datetime

# SQLite wrapper for the Music Database.
class MusicDB:
    def __init__(self, db_path="assets/database/piano_stats.db"):

        # Ensures the directory assets/database/ exists.
        if os.path.dirname(db_path):
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Connects to piano_stats.db.
        # check_same_thread=False allows access from different threads (needed for the CV loop).
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()

    # Creates two tables: Sessions (stores session start time) and Notes (stores every note played, linked to a session).
    def create_tables(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Sessions (
                id INTEGER PRIMARY KEY,
                timestamp TEXT
            )
        """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Notes (
                id INTEGER PRIMARY KEY,
                session_id INTEGER,
                note INTEGER,
                timestamp TEXT
            )
        """
        )
        self.conn.commit()

    # Starts a new recording session.
    def start_session(self):
        cur = self.conn.cursor()
        now = datetime.now().isoformat()

        # Inserts the current timestamp into Sessions.
        cur.execute("INSERT INTO Sessions (timestamp) VALUES (?)", (now,))
        self.conn.commit()

        # Returns the lastrowid (the Session ID) so subsequent notes can be linked to it.
        return cur.lastrowid

    # Logs a single note event.
    def log_note(self, session_id, note):

        # Takes session_id and the note. Inserts a record into the Notes table with the current timestamp.
        if session_id:
            cur = self.conn.cursor()
            now = datetime.now().isoformat()
            cur.execute(
                """
                INSERT INTO Notes (session_id, note, timestamp)
                VALUES (?, ?, ?)
            """,
                (session_id, note, now),
            )
            self.conn.commit()