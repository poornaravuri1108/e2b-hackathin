import sqlite3

DB_NAME = 'code_review.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Check if the table exists and has the correct schema
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'password' not in columns or 'role' not in columns:
        # If the table doesn't have the correct schema, drop it and recreate
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute('''CREATE TABLE users
                          (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)''')
        print("Table 'users' was recreated with the correct schema.")

    # Add some mock data
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", 
                   ('alice', 'password123', 'user'))
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", 
                   ('bob', 'securepass', 'admin'))
    
    conn.commit()
    conn.close()

def get_user(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def test_mock_data():
    init_db()  # This will now ensure the correct table structure

    # Test for existing users
    for username in ['alice', 'bob']:
        user = get_user(username)
        if user:
            print(f"User found: {user}")
        else:
            print(f"User not found: {username}")

    # Test for non-existing user
    non_existing = get_user('charlie')
    if non_existing:
        print(f"Unexpected user found: {non_existing}")
    else:
        print("As expected, 'charlie' was not found")

if __name__ == "__main__":
    test_mock_data()