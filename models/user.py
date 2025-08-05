from werkzeug.security import check_password_hash, generate_password_hash
from database import execute_query

class User:
    def __init__(self, id=None, username=None, password_hash=None, created_at=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.created_at = created_at
    
    @staticmethod
    def find_by_username(username):
        """Find user by username"""
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
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
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
    
    def check_password(self, password):
        """Check if provided password matches user's password"""
        return check_password_hash(self.password_hash, password)
    
    def save(self):
        """Save user to database"""
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
    
    @staticmethod
    def create_user(username, password):
        """Create a new user with hashed password"""
        password_hash = generate_password_hash(password)
        user = User(username=username, password_hash=password_hash)
        return user.save()
