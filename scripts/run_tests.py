"""
Comprehensive test suite for the modular Flask Task Manager application
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from app import create_app
from database import init_db
from models.user import User
from models.task import Task

class TestUserModel(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['DATABASE_PATH'] = ':memory:'
        self.app.config['TESTING'] = True
        
        with self.app.app_context():
            init_db()
    
    def test_user_creation(self):
        with self.app.app_context():
            user = User.create_user('testuser', 'testpass123')
            self.assertIsNotNone(user.id)
            self.assertEqual(user.username, 'testuser')
    
    def test_user_authentication(self):
        with self.app.app_context():
            user = User.create_user('testuser', 'testpass123')
            found_user = User.find_by_username('testuser')
            
            self.assertTrue(found_user.check_password('testpass123'))
            self.assertFalse(found_user.check_password('wrongpass'))

class TestTaskModel(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['DATABASE_PATH'] = ':memory:'
        self.app.config['TESTING'] = True
        
        with self.app.app_context():
            init_db()
            self.user = User.create_user('testuser', 'testpass123')
    
    def test_task_creation(self):
        with self.app.app_context():
            task = Task(
                title='Test Task',
                description='Test Description',
                status='pending',
                priority='high',
                is_urgent=True,
                user_id=self.user.id
            )
            task.save()
            
            self.assertIsNotNone(task.id)
            self.assertEqual(task.title, 'Test Task')
    
    def test_task_filtering(self):
        with self.app.app_context():
            # Create test tasks
            Task(title='Task 1', status='pending', priority='high', 
                 is_urgent=True, user_id=self.user.id).save()
            Task(title='Task 2', status='completed', priority='low', 
                 is_urgent=False, user_id=self.user.id).save()
            
            # Test filtering
            pending_tasks, _, _ = Task.find_by_user(
                self.user.id, status_filter='pending'
            )
            self.assertEqual(len(pending_tasks), 1)
            self.assertEqual(pending_tasks[0].title, 'Task 1')

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['DATABASE_PATH'] = ':memory:'
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        with self.app.app_context():
            init_db()
    
    def test_login_page(self):
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
    
    def test_login_functionality(self):
        # Test valid login
        response = self.client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def test_protected_route_redirect(self):
        response = self.client.get('/tasks/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

def run_all_tests():
    """Run all test suites"""
    print("=" * 60)
    print("RUNNING MODULAR FLASK APPLICATION TESTS")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestUserModel))
    suite.addTests(loader.loadTestsFromTestCase(TestTaskModel))
    suite.addTests(loader.loadTestsFromTestCase(TestRoutes))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print(f"TESTS COMPLETED: {result.testsRun} tests run")
    print(f"FAILURES: {len(result.failures)}")
    print(f"ERRORS: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
