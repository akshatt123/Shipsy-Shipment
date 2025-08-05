from database import execute_query
from datetime import datetime
import math

class Task:
    def __init__(self, id=None, title=None, description=None, status='pending', 
                 priority='medium', is_urgent=False, created_at=None, 
                 updated_at=None, user_id=None):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.is_urgent = is_urgent
        self.created_at = created_at
        self.updated_at = updated_at
        self.user_id = user_id
    
    @staticmethod
    def find_by_id(task_id, user_id):
        """Find task by ID and user ID"""
        task_data = execute_query(
            'SELECT * FROM tasks WHERE id = ? AND user_id = ?',
            (task_id, user_id),
            fetch_one=True
        )
        if task_data:
            return Task._from_db_row(task_data)
        return None
    
    @staticmethod
    def find_by_user(user_id, status_filter=None, priority_filter=None, 
                     urgent_filter=None, page=1, per_page=5):
        """Find tasks by user with filtering and pagination"""
        # Build query with filters
        query = 'SELECT * FROM tasks WHERE user_id = ?'
        params = [user_id]
        
        if status_filter:
            query += ' AND status = ?'
            params.append(status_filter)
        
        if priority_filter:
            query += ' AND priority = ?'
            params.append(priority_filter)
        
        if urgent_filter:
            query += ' AND is_urgent = ?'
            params.append(1 if urgent_filter == 'true' else 0)
        
        # Count total records for pagination
        count_query = query.replace('SELECT *', 'SELECT COUNT(*)')
        total_count = execute_query(count_query, params, fetch_one=True)[0]
        
        # Get paginated results
        offset = (page - 1) * per_page
        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([per_page, offset])
        
        tasks_data = execute_query(query, params, fetch_all=True)
        tasks = [Task._from_db_row(task_data) for task_data in tasks_data]
        
        total_pages = math.ceil(total_count / per_page)
        
        return tasks, total_pages, total_count
    
    def save(self):
        """Save task to database"""
        if self.id:
            # Update existing task
            execute_query(
                '''UPDATE tasks 
                   SET title = ?, description = ?, status = ?, priority = ?, 
                       is_urgent = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE id = ? AND user_id = ?''',
                (self.title, self.description, self.status, self.priority, 
                 self.is_urgent, self.id, self.user_id)
            )
        else:
            # Create new task
            self.id = execute_query(
                '''INSERT INTO tasks (title, description, status, priority, is_urgent, user_id)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (self.title, self.description, self.status, self.priority, 
                 self.is_urgent, self.user_id)
            )
        return self
    
    def delete(self):
        """Delete task from database"""
        if self.id:
            execute_query(
                'DELETE FROM tasks WHERE id = ? AND user_id = ?',
                (self.id, self.user_id)
            )
            return True
        return False
    
    @staticmethod
    def _from_db_row(row):
        """Create Task instance from database row"""
        return Task(
            id=row['id'],
            title=row['title'],
            description=row['description'],
            status=row['status'],
            priority=row['priority'],
            is_urgent=bool(row['is_urgent']),
            created_at=row['created_at'],
            updated_at=row.get('updated_at'),
            user_id=row['user_id']
        )
    
    def to_dict(self):
        """Convert task to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'is_urgent': self.is_urgent,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'user_id': self.user_id
        }
    
    @staticmethod
    def get_status_choices():
        """Get available status choices"""
        return ['pending', 'in_progress', 'completed']
    
    @staticmethod
    def get_priority_choices():
        """Get available priority choices"""
        return ['low', 'medium', 'high']
