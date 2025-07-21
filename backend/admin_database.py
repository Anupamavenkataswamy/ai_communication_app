import sqlite3

# Connect to the database
admin_conn = sqlite3.connect("admins.db", check_same_thread=False)
admin_cursor = admin_conn.cursor()

# Create admin table
def init_admin_db():
    admin_cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    admin_conn.commit()

# Initialize DB
init_admin_db()
