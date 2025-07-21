import sqlite3

# Connect to the admin database
admin_conn = sqlite3.connect("admin.db", check_same_thread=False)
admin_cursor = admin_conn.cursor()

# Initialize the admin table
def init_admin_db():
    admin_cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    admin_conn.commit()
