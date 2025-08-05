import sqlite3
from werkzeug.security import generate_password_hash
from flask import current_app
import os

def get_db_connection():
    """Get database connection with row factory"""
    db_path = current_app.config.get('DATABASE_PATH', '/tmp/shipments.db')
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables and create default user"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create shipments table
    c.execute('''CREATE TABLE IF NOT EXISTS shipments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  tracking_number TEXT NOT NULL,
                  sender_name TEXT NOT NULL,
                  sender_address TEXT NOT NULL,
                  recipient_name TEXT NOT NULL,
                  recipient_address TEXT NOT NULL,
                  package_description TEXT,
                  weight REAL,
                  status TEXT NOT NULL DEFAULT 'pending',
                  priority TEXT NOT NULL DEFAULT 'standard',
                  is_express BOOLEAN NOT NULL DEFAULT 0,
                  shipping_cost REAL DEFAULT 0.0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  user_id INTEGER,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Create tasks table
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  description TEXT,
                  status TEXT NOT NULL DEFAULT 'pending',
                  priority TEXT NOT NULL DEFAULT 'medium',
                  is_urgent BOOLEAN NOT NULL DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  user_id INTEGER,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # # Create default user if not exists
    # c.execute("SELECT * FROM users WHERE username = ?", ('admin',))
    # if not c.fetchone():
    #     password_hash = generate_password_hash('admin123')
    #     c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
    #              ('admin', password_hash))
    
    conn.commit()
    conn.close()

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """Execute database query with proper connection handling"""
    conn = get_db_connection()
    try:
        if params:
            result = conn.execute(query, params)
        else:
            result = conn.execute(query)
        
        if fetch_one:
            return result.fetchone()
        elif fetch_all:
            return result.fetchall()
        else:
            conn.commit()
            return result.lastrowid
    except Exception as e:
        print(f"Database error: {e}")
        raise
    finally:
        conn.close()
