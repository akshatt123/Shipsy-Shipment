"""
Test script for the Flask Shipment Manager application
This script demonstrates various test cases for the shipment management system
"""

import requests
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:5000"  # Change this to your deployed URL
TEST_USER = {"username": "admin", "password": "admin123"}

def test_login():
    """Test user authentication"""
    print("Testing login functionality...")
    
    # Test valid login
    response = requests.post(f"{BASE_URL}/auth/login", data=TEST_USER)
    print(f"Valid login status: {response.status_code}")
    
    # Test invalid login
    invalid_user = {"username": "invalid", "password": "wrong"}
    response = requests.post(f"{BASE_URL}/auth/login", data=invalid_user)
    print(f"Invalid login status: {response.status_code}")

def test_shipment_creation():
    """Test shipment creation with various inputs"""
    print("\nTesting shipment creation...")
    
    # Test cases for shipment creation
    test_shipments = [
        {
            "sender_name": "John Doe",
            "sender_address": "123 Main St, New York, NY 10001",
            "recipient_name": "Jane Smith",
            "recipient_address": "456 Oak Ave, Los Angeles, CA 90210",
            "package_description": "Electronics - Laptop",
            "weight": "2.5",
            "status": "pending",
            "priority": "urgent",
            "is_express": True
        },
        {
            "sender_name": "ABC Company",
            "sender_address": "789 Business Blvd, Chicago, IL 60601",
            "recipient_name": "XYZ Corp",
            "recipient_address": "321 Corporate Dr, Miami, FL 33101",
            "package_description": "Documents",
            "weight": "0.5",
            "status": "picked_up",
            "priority": "standard",
            "is_express": False
        },
        {
            "sender_name": "",  # Invalid - empty sender name
            "sender_address": "Invalid address",
            "recipient_name": "Test Recipient",
            "recipient_address": "Test Address",
            "package_description": "Test package",
            "weight": "1.0",
            "status": "pending",
            "priority": "standard",
            "is_express": False
        }
    ]
    
    for i, shipment in enumerate(test_shipments):
        print(f"Test case {i+1}: {shipment['sender_name'] or 'Empty sender name'}")
        if not shipment['sender_name']:
            print("  Expected: Should fail validation")
        else:
            print(f"  Expected: Should create shipment with priority {shipment['priority']}")
            print(f"  Expected cost calculation based on weight {shipment['weight']} kg")

def test_tracking_functionality():
    """Test shipment tracking functionality"""
    print("\nTesting tracking functionality...")
    
    tracking_tests = [
        "SHP12345678",  # Valid format
        "SHP87654321",  # Valid format
        "INVALID123",   # Invalid format
        "",             # Empty tracking number
        "shp12345678",  # Lowercase (should be converted)
    ]
    
    for tracking_number in tracking_tests:
        print(f"Tracking test: '{tracking_number}'")
        if not tracking_number:
            print("  Expected: Should show validation error")
        elif not tracking_number.startswith('SHP'):
            print("  Expected: Should handle invalid format gracefully")
        else:
            print("  Expected: Should show shipment details or 'not found' message")

def test_filtering_and_pagination():
    """Test filtering and pagination functionality"""
    print("\nTesting filtering and pagination...")
    
    # Test filter combinations
    filter_tests = [
        {"status": "pending"},
        {"status": "in_transit"},
        {"status": "delivered"},
        {"priority": "urgent"},
        {"priority": "standard"},
        {"express  "delivered"},
        {"priority": "urgent"},
        {"priority": "standard"},
        {"express": "true"},
        {"status": "in_transit", "priority": "urgent"},
        {"status": "delivered", "express": "true"},
        {"page": "2"}
    ]
    
    for filter_test in filter_tests:
        print(f"Filter test: {filter_test}")
        print("  Expected: Should return filtered results")

def test_cost_calculation():
    """Test shipping cost calculation"""
    print("\nTesting cost calculation...")
    
    cost_tests = [
        {"weight": 1.0, "priority": "standard", "express": False, "expected_range": (7.0, 8.0)},
        {"weight": 2.5, "priority": "urgent", "express": True, "expected_range": (18.0, 20.0)},
        {"weight": 0.5, "priority": "priority", "express": False, "expected_range": (7.5, 8.5)},
        {"weight": 10.0, "priority": "standard", "express": True, "expected_range": (40.0, 50.0)},
    ]
    
    for test in cost_tests:
        print(f"Cost test: {test['weight']}kg, {test['priority']}, Express: {test['express']}")
        print(f"  Expected cost range: ${test['expected_range'][0]:.2f} - ${test['expected_range'][1]:.2f}")

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\nTesting edge cases...")
    
    edge_cases = [
        "Very long sender name that exceeds normal length expectations and might cause display issues in the user interface",
        "Sender with special characters: !@#$%^&*()_+-=[]{}|;':\",./<>?",
        "Sender with unicode: 🚀 Unicode Sender with Emojis 📦",
        "",  # Empty sender name
        "   ",  # Whitespace only sender name
        "Normal Sender",  # Valid case for comparison
    ]
    
    for case in edge_cases:
        print(f"Edge case: '{case[:50]}{'...' if len(case) > 50 else ''}'")
        if not case.strip():
            print("  Expected: Should fail validation")
        else:
            print("  Expected: Should handle gracefully")

def test_weight_validation():
    """Test weight input validation"""
    print("\nTesting weight validation...")
    
    weight_tests = [
        "0.1",      # Valid minimum
        "999.9",    # Valid maximum
        "1000.1",   # Invalid - exceeds maximum
        "-1.0",     # Invalid - negative
        "abc",      # Invalid - not a number
        "",         # Empty - should default to 0
        "0",        # Zero weight
    ]
    
    for weight in weight_tests:
        print(f"Weight test: '{weight}'")
        if weight in ["-1.0", "1000.1", "abc"]:
            print("  Expected: Should show validation error")
        elif weight == "":
            print("  Expected: Should default to 0.0")
        else:
            print("  Expected: Should accept valid weight")

def run_all_tests():
    """Run all test cases"""
    print("=" * 60)
    print("SHIPMENT MANAGER APPLICATION TEST PLAN")
    print("=" * 60)
    
    test_login()
    test_shipment_creation()
    test_tracking_functionality()
    test_filtering_and_pagination()
    test_cost_calculation()
    test_edge_cases()
    test_weight_validation()
    
    print("\n" + "=" * 60)
    print("TEST PLAN COMPLETE")
    print("=" * 60)
    print("\nNOTE: This is a test plan demonstration.")
    print("For actual testing, implement proper test framework like pytest.")
    print("\nKey Features Tested:")
    print("✓ User authentication")
    print("✓ Shipment CRUD operations")
    print("✓ Tracking number generation and lookup")
    print("✓ Cost calculation algorithm")
    print("✓ Filtering and pagination")
    print("✓ Input validation and edge cases")
    print("✓ Express delivery toggle")
    print("✓ Status progression tracking")

if __name__ == "__main__":
    run_all_tests()
