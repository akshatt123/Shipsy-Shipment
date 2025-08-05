"""
Database testing script for the Shipment Manager application
This script runs comprehensive tests on the database operations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from app import create_app
from database import init_db, get_db_stats
from models.user import User
from models.shipment import Shipment

class TestDatabase(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.app = create_app()
        self.app.config['DATABASE_PATH'] = ':memory:'
        self.app.config['TESTING'] = True
        
        with self.app.app_context():
            init_db()
    
    def test_database_initialization(self):
        """Test database initialization"""
        with self.app.app_context():
            stats = get_db_stats()
            self.assertIsNotNone(stats)
            self.assertIn('users', stats)
            self.assertIn('shipments', stats)
            self.assertGreaterEqual(stats['users'], 1)  # At least admin user

class TestUserModel(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['DATABASE_PATH'] = ':memory:'
        self.app.config['TESTING'] = True
        
        with self.app.app_context():
            init_db()
    
    def test_user_creation(self):
        """Test user creation"""
        with self.app.app_context():
            user = User.create_user('testuser', 'testpass123')
            self.assertIsNotNone(user.id)
            self.assertEqual(user.username, 'testuser')
    
    def test_user_authentication(self):
        """Test user authentication"""
        with self.app.app_context():
            user = User.create_user('testuser', 'testpass123')
            found_user = User.find_by_username('testuser')
            
            self.assertTrue(found_user.check_password('testpass123'))
            self.assertFalse(found_user.check_password('wrongpass'))
    
    def test_duplicate_username(self):
        """Test duplicate username handling"""
        with self.app.app_context():
            User.create_user('testuser', 'testpass123')
            
            with self.assertRaises(ValueError):
                User.create_user('testuser', 'anotherpass')

class TestShipmentModel(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['DATABASE_PATH'] = ':memory:'
        self.app.config['TESTING'] = True
        
        with self.app.app_context():
            init_db()
            self.user = User.create_user('testuser', 'testpass123')
    
    def test_shipment_creation(self):
        """Test shipment creation"""
        with self.app.app_context():
            shipment = Shipment(
                sender_name='Test Sender',
                sender_address='Test Address',
                recipient_name='Test Recipient',
                recipient_address='Test Recipient Address',
                package_description='Test Package',
                weight=2.5,
                status='pending',
                priority='urgent',
                is_express=True,
                user_id=self.user.id
            )
            shipment.save()
            
            self.assertIsNotNone(shipment.id)
            self.assertIsNotNone(shipment.tracking_number)
            self.assertTrue(shipment.tracking_number.startswith('SHP'))
            self.assertEqual(len(shipment.tracking_number), 11)  # SHP + 8 digits
    
    def test_cost_calculation(self):
        """Test shipping cost calculation"""
        with self.app.app_context():
            # Test standard shipping
            cost1 = Shipment.calculate_shipping_cost(2.0, 'standard', False)
            expected1 = 5.0 + (2.0 * 2.0)  # base + weight
            self.assertEqual(cost1, expected1)
            
            # Test express shipping
            cost2 = Shipment.calculate_shipping_cost(2.0, 'standard', True)
            expected2 = (5.0 + (2.0 * 2.0)) * 1.8  # base + weight, then express multiplier
            self.assertEqual(cost2, expected2)
            
            # Test urgent priority
            cost3 = Shipment.calculate_shipping_cost(2.0, 'urgent', False)
            expected3 = (5.0 + (2.0 * 2.0)) * 2.0  # base + weight, then priority multiplier
            self.assertEqual(cost3, expected3)
    
    def test_shipment_filtering(self):
        """Test shipment filtering"""
        with self.app.app_context():
            # Create test shipments
            shipment1 = Shipment(
                sender_name='Sender 1', sender_address='Address 1',
                recipient_name='Recipient 1', recipient_address='Address 1',
                status='pending', priority='high', is_express=True,
                user_id=self.user.id
            )
            shipment1.save()
            
            shipment2 = Shipment(
                sender_name='Sender 2', sender_address='Address 2',
                recipient_name='Recipient 2', recipient_address='Address 2',
                status='delivered', priority='low', is_express=False,
                user_id=self.user.id
            )
            shipment2.save()
            
            # Test status filtering
            pending_shipments, _, _ = Shipment.find_by_user(
                self.user.id, status_filter='pending'
            )
            self.assertEqual(len(pending_shipments), 1)
            self.assertEqual(pending_shipments[0].status, 'pending')
            
            # Test express filtering
            express_shipments, _, _ = Shipment.find_by_user(
                self.user.id, express_filter='true'
            )
            self.assertEqual(len(express_shipments), 1)
            self.assertTrue(express_shipments[0].is_express)
    
    def test_tracking_number_uniqueness(self):
        """Test tracking number uniqueness"""
        with self.app.app_context():
            tracking_numbers = set()
            
            # Create multiple shipments and check uniqueness
            for i in range(10):
                shipment = Shipment(
                    sender_name=f'Sender {i}',
                    sender_address=f'Address {i}',
                    recipient_name=f'Recipient {i}',
                    recipient_address=f'Address {i}',
                    user_id=self.user.id
                )
                shipment.save()
                
                self.assertNotIn(shipment.tracking_number, tracking_numbers)
                tracking_numbers.add(shipment.tracking_number)
    
    def test_shipment_search(self):
        """Test shipment search functionality"""
        with self.app.app_context():
            # Create test shipment
            shipment = Shipment(
                sender_name='John Doe Electronics',
                sender_address='123 Tech Street',
                recipient_name='Jane Smith',
                recipient_address='456 Business Ave',
                package_description='Laptop Computer',
                user_id=self.user.id
            )
            shipment.save()
            
            # Test search by sender name
            results, _, _ = Shipment.search_shipments(
                self.user.id, 'John Doe'
            )
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].sender_name, 'John Doe Electronics')
            
            # Test search by package description
            results, _, _ = Shipment.search_shipments(
                self.user.id, 'Laptop'
            )
            self.assertEqual(len(results), 1)
            
            # Test search with no results
            results, _, _ = Shipment.search_shipments(
                self.user.id, 'NonExistent'
            )
            self.assertEqual(len(results), 0)

def run_all_tests():
    """Run all database tests"""
    print("=" * 60)
    print("RUNNING DATABASE TESTS")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestUserModel))
    suite.addTests(loader.loadTestsFromTestCase(TestShipmentModel))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print(f"TESTS COMPLETED: {result.testsRun} tests run")
    print(f"FAILURES: {len(result.failures)}")
    print(f"ERRORS: {len(result.errors)}")
    print("=" * 60)
    
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED!")
        
        if result.failures:
            print("\nFAILURES:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")
        
        if result.errors:
            print("\nERRORS:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
