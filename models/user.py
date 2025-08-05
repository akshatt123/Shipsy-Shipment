from werkzeug.security import check_password_hash, generate_password_hash
from database import execute_query
import sqlite3

class User:
    def __init__(self, id=None, username=None, password_hash=None, created_at=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.created_at = created_at
    
    @staticmethod
    def find_by_username(username):
        """Find user by username"""
        try:
            user_data = execute_query(
                'SELECT * FROM users WHERE username = ?', 
                (username,), 
                fetch_one=True
            )
            if user_data:
                return User(
                    id=user_data['id'],
                    username=user_data['username'],
                    password_hash=user_data['password_hash'],
                    created_at=user_data['created_at']
                )
            return None
        except Exception as e:
            print(f"Error finding user by username: {e}")
            return None
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        try:
            user_data = execute_query(
                'SELECT * FROM users WHERE id = ?', 
                (user_id,), 
                fetch_one=True
            )
            if user_data:
                return User(
                    id=user_data['id'],
                    username=user_data['username'],
                    password_hash=user_data['password_hash'],
                    created_at=user_data['created_at']
                )
            return None
        except Exception as e:
            print(f"Error finding user by ID: {e}")
            return None
    
    def check_password(self, password):
        """Check if provided password matches user's password"""
        try:
            return check_password_hash(self.password_hash, password)
        except Exception as e:
            print(f"Error checking password: {e}")
            return False
    
    def save(self):
        """Save user to database"""
        try:
            if self.id:
                # Update existing user
                execute_query(
                    'UPDATE users SET username = ?, password_hash = ? WHERE id = ?',
                    (self.username, self.password_hash, self.id)
                )
            else:
                # Create new user
                self.id = execute_query(
                    'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                    (self.username, self.password_hash)
                )
            return self
        except sqlite3.IntegrityError:
            raise ValueError("Username already exists")
        except Exception as e:
            print(f"Error saving user: {e}")
            raise
    
    @staticmethod
    def create_user(username, password):
        """Create a new user with hashed password"""
        try:
            # Check if username already exists
            existing_user = User.find_by_username(username)
            if existing_user:
                raise ValueError("Username already exists")
            
            password_hash = generate_password_hash(password)
            user = User(username=username, password_hash=password_hash)
            return user.save()
        except Exception as e:
            print(f"Error creating user: {e}")
            raise
    
    @staticmethod
    def get_all_users():
        """Get all users (for admin purposes)"""
        try:
            users_data = execute_query(
                'SELECT id, username, created_at FROM users ORDER BY created_at DESC',
                fetch_all=True
            )
            return [User(id=user['id'], username=user['username'], 
                        created_at=user['created_at']) for user in users_data]
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    def delete(self):
        """Delete user and all associated shipments"""
        try:
            if self.id:
                # Delete user's shipments first (due to foreign key constraint)
                execute_query('DELETE FROM shipments WHERE user_id = ?', (self.id,))
                # Delete user
                execute_query('DELETE FROM users WHERE id = ?', (self.id,))
                return True
            return False
        except Exception as e:
            print(f"Error deleting user: {e}")
            raise
    
    def get_shipment_count(self):
        """Get count of shipments for this user"""
        try:
            if self.id:
                result = execute_query(
                    'SELECT COUNT(*) FROM shipments WHERE user_id = ?',
                    (self.id,),
                    fetch_one=True
                )
                return result[0] if result else 0
            return 0
        except Exception as e:
            print(f"Error getting shipment count: {e}")
            return 0
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at,
            'shipment_count': self.get_shipment_count()
        }
