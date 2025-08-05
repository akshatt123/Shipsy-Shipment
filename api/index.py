import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
import sqlite3
from werkzeug.security import generate_password_hash

# Import our modules
from config import Config
from routes.auth import auth_bp
from routes.shipments import shipments_bp
from routes.main import main_bp

# Create Flask app
app = Flask(__name__, 
           template_folder='../templates',
           static_folder='../static')
app.config.from_object(Config)

# Add proxy fix for Vercel
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Initialize database for serverless environment
def init_serverless_db():
    """Initialize database for serverless deployment"""
    db_path = '/tmp/shipments.db'  # Use /tmp for serverless
    
    conn = sqlite3.connect(db_path)
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
    
    # Create default user if not exists
    c.execute("SELECT * FROM users WHERE username = ?", ('admin',))
    if not c.fetchone():
        password_hash = generate_password_hash('admin123')
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                 ('admin', password_hash))
    
    conn.commit()
    conn.close()
    
    return db_path

# Initialize database on cold start
try:
    init_serverless_db()
except Exception as e:
    print(f"Database initialization error: {e}")

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(shipments_bp, url_prefix='/shipments')

# Add error handlers
@app.errorhandler(404)
def not_found(error):
    return "Page not found", 404

@app.errorhandler(500)
def internal_error(error):
    return "Internal server error", 500

# This is required for Vercel
def handler(request):
    return app(request.environ, lambda status, headers: None)

# For local development
if __name__ == '__main__':
    app.run(debug=True)
