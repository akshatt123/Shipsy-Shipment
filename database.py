import sqlite3
from werkzeug.security import generate_password_hash
from flask import current_app, g
import os
import threading

# Thread-local storage for database connections
_local = threading.local()

def get_db_connection():
    """Get database connection with proper configuration"""
    if not hasattr(_local, 'connection') or _local.connection is None:
        db_path = current_app.config.get('DATABASE_PATH', 'shipments.db')
        
        # Ensure directory exists for file-based databases
        if db_path != ':memory:':
            os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        _local.connection = sqlite3.connect(
            db_path,
            timeout=current_app.config.get('SQLITE_TIMEOUT', 20),
            check_same_thread=current_app.config.get('SQLITE_CHECK_SAME_THREAD', False)
        )
        _local.connection.row_factory = sqlite3.Row
        
        # Enable foreign key constraints
        _local.connection.execute('PRAGMA foreign_keys = ON')
        
    return _local.connection

def close_db_connection():
    """Close database connection"""
    if hasattr(_local, 'connection') and _local.connection is not None:
        _local.connection.close()
        _local.connection = None

def init_db():
    """Initialize database tables and create default data"""
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        # Create users table
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT UNIQUE NOT NULL,
                      password_hash TEXT NOT NULL,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Create shipments table with proper constraints
        c.execute('''CREATE TABLE IF NOT EXISTS shipments
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      tracking_number TEXT UNIQUE NOT NULL,
                      sender_name TEXT NOT NULL,
                      sender_address TEXT NOT NULL,
                      recipient_name TEXT NOT NULL,
                      recipient_address TEXT NOT NULL,
                      package_description TEXT,
                      weight REAL DEFAULT 0.0,
                      status TEXT NOT NULL DEFAULT 'pending',
                      priority TEXT NOT NULL DEFAULT 'standard',
                      is_express BOOLEAN NOT NULL DEFAULT 0,
                      shipping_cost REAL DEFAULT 0.0,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      user_id INTEGER NOT NULL,
                      FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                      CHECK (weight >= 0),
                      CHECK (shipping_cost >= 0),
                      CHECK (status IN ('pending', 'picked_up', 'in_transit', 'out_for_delivery', 'delivered', 'returned')),
                      CHECK (priority IN ('standard', 'priority', 'urgent')))''')
        
        # Create indexes for better performance
        c.execute('CREATE INDEX IF NOT EXISTS idx_shipments_user_id ON shipments(user_id)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_shipments_tracking_number ON shipments(tracking_number)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_shipments_status ON shipments(status)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_shipments_created_at ON shipments(created_at)')
        
        # Create default admin user if not exists
        c.execute("SELECT id FROM users WHERE username = ?", ('admin',))
        admin_user = c.fetchone()
        
        if not admin_user:
            password_hash = generate_password_hash('admin123')
            c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                     ('admin', password_hash))
            admin_id = c.lastrowid
            
            # Create sample shipments for demo
            sample_shipments = [
                ('SHP12345678', 'John Doe', '123 Main St, New York, NY 10001', 
                 'Jane Smith', '456 Oak Ave, Los Angeles, CA 90210', 
                 'Electronics - Laptop Computer', 2.5, 'in_transit', 'urgent', 1, 18.0),
                ('SHP87654321', 'ABC Company', '789 Business Blvd, Chicago, IL 60601',
                 'XYZ Corp', '321 Corporate Dr, Miami, FL 33101',
                 'Important Legal Documents', 0.5, 'delivered', 'priority', 0, 7.5),
                ('SHP11223344', 'Sarah Wilson', '555 Pine St, Seattle, WA 98101',
                 'Mike Johnson', '777 Elm Dr, Austin, TX 78701',
                 'Books and Educational Materials', 1.2, 'pending', 'standard', 0, 7.4),
                ('SHP99887766', 'Tech Solutions Inc', '999 Innovation Way, San Francisco, CA 94105',
                 'Global Enterprises', '111 Commerce Plaza, Boston, MA 02101',
                 'Server Hardware Components', 15.0, 'picked_up', 'urgent', 1, 54.0),
                ('SHP55443322', 'Maria Garcia', '222 Sunset Blvd, Phoenix, AZ 85001',
                 'Robert Chen', '888 Mountain View, Denver, CO 80201',
                 'Handmade Crafts and Artwork', 0.8, 'out_for_delivery', 'standard', 0, 6.6)
            ]
            
            for shipment in sample_shipments:
                c.execute('''INSERT INTO shipments 
                            (tracking_number, sender_name, sender_address, recipient_name, 
                             recipient_address, package_description, weight, status, priority, 
                             is_express, shipping_cost, user_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                         shipment + (admin_id,))
        
        conn.commit()
        print("Database initialized successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"Error initializing database: {e}")
        raise

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """Execute database query with proper connection handling and error management"""
    conn = get_db_connection()
    try:
        if params:
            cursor = conn.execute(query, params)
        else:
            cursor = conn.execute(query)
        
        if fetch_one:
            result = cursor.fetchone()
            return result
        elif fetch_all:
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return cursor.lastrowid
            
    except sqlite3.IntegrityError as e:
        conn.rollback()
        print(f"Database integrity error: {e}")
        raise ValueError(f"Database constraint violation: {e}")
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error: {e}")
        raise
    except Exception as e:
        conn.rollback()
        print(f"Unexpected error: {e}")
        raise

def get_db_stats():
    """Get database statistics for monitoring"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Get table counts
        c.execute("SELECT COUNT(*) FROM users")
        user_count = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM shipments")
        shipment_count = c.fetchone()[0]
        
        # Get shipment status distribution
        c.execute("""SELECT status, COUNT(*) as count 
                     FROM shipments 
                     GROUP BY status 
                     ORDER BY count DESC""")
        status_distribution = c.fetchall()
        
        return {
            'users': user_count,
            'shipments': shipment_count,
            'status_distribution': dict(status_distribution)
        }
    except Exception as e:
        print(f"Error getting database stats: {e}")
        return None

# Flask teardown handler
def close_db(error):
    """Close database connection at the end of request"""
    close_db_connection()
