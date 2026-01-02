import sqlite3
import os
import sys

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'. In this case, the database will be
    # in the same folder as the executable
    application_path = os.path.dirname(sys.executable)
    DATABASE_FILE = os.path.join(application_path, 'attendance.db')
else:
    DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'attendance.db')

class Database:
    def __init__(self):
        self.conn = None

    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(DATABASE_FILE)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def initialize_db(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS team_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance_statuses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    status TEXT NOT NULL UNIQUE,
                    color TEXT NOT NULL DEFAULT '#000000'
                )
            ''')

            # Add color column to existing table if it doesn't exist
            try:
                cursor.execute("SELECT color FROM attendance_statuses LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute("ALTER TABLE attendance_statuses ADD COLUMN color TEXT NOT NULL DEFAULT '#000000'")

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id INTEGER NOT NULL,
                    record_date TEXT NOT NULL,
                    status_id INTEGER NOT NULL,
                    notes TEXT,
                    FOREIGN KEY (member_id) REFERENCES team_members (id),
                    FOREIGN KEY (status_id) REFERENCES attendance_statuses (id),
                    UNIQUE(member_id, record_date)
                )
            ''')

            # Add notes column to existing table if it doesn't exist
            try:
                cursor.execute("SELECT notes FROM attendance_records LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute("ALTER TABLE attendance_records ADD COLUMN notes TEXT")
                
            conn.commit()

        self._seed_initial_data()

    def _seed_initial_data(self):
        """Seeds initial attendance statuses and their colors if they don't exist."""
        with self.connect() as conn:
            cursor = conn.cursor()
            initial_statuses = {
                "Work From Home": "#0000FF", # Blue
                "On Time": "#008000",      # Green
                "Late": "#FFA500",         # Orange
                "NA": "#808080"            # Gray
            }
            for status, color in initial_statuses.items():
                cursor.execute("INSERT OR IGNORE INTO attendance_statuses (status, color) VALUES (?, ?)", (status, color))
                # Update color for existing statuses that might have the default color
                cursor.execute("UPDATE attendance_statuses SET color = ? WHERE status = ? AND color = '#000000'", (color, status))
            conn.commit()

# Ensure the database is initialized when the module is imported or first used
db = Database()
db.initialize_db()
