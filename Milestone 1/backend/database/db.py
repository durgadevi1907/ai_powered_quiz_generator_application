import sqlite3
from sqlite3 import Error
import os

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')

def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        raise e

def init_db():
    conn = get_db_connection()
    try:
        c = conn.cursor()
        
        # Create users table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create tokens table for session management
        c.execute('''
            CREATE TABLE IF NOT EXISTS tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create quiz_attempts table
        c.execute('''
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                score INTEGER DEFAULT 0,
                total_questions INTEGER NOT NULL,
                status TEXT CHECK(status IN ('completed', 'incomplete')) DEFAULT 'incomplete',
                answers TEXT,  -- JSON string storing user's answers
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Add indexes for performance and data consistency
        c.execute('''
            CREATE INDEX IF NOT EXISTS idx_quiz_attempts_user_topic 
            ON quiz_attempts(user_id, topic, status)
        ''')
        
        conn.commit()
    except Error as e:
        print(f"Error initializing database: {e}")
        raise e
    finally:
        conn.close()

# Initialize database when module is imported
init_db()