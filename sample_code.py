import sqlite3

def get_user(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    return user

def main():
    user_input = input("Enter username: ")
    user = get_user(user_input)
    if user:
        print(f"User found: {user}")
    else:
        print("User not found")

if __name__ == "__main__":
    main()