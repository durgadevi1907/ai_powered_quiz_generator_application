import sqlite3
from database.db import DATABASE_PATH

def check_database():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("Checking users table:")
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        for user in users:
            print(f"ID: {user['id']}, Username: {user['username']}, Created: {user['created_at']}")
        
        print("\nChecking tokens table:")
        cursor.execute('SELECT * FROM tokens')
        tokens = cursor.fetchall()
        for token in tokens:
            print(f"ID: {token['id']}, User ID: {token['user_id']}, Created: {token['created_at']}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    check_database()