import sqlite3

def init_feedback_db():
    conn = sqlite3.connect("feedback.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT,
            question TEXT,
            answer TEXT,
            score INTEGER,
            feedback TEXT,
            mode TEXT,
            submitted_at TEXT
        )
    ''')
    conn.commit()
    conn.close()
