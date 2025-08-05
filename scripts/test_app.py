"""
Test script for the Flask Task Manager application
This script demonstrates various test cases for the application
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
    response = requests.post(f"{BASE_URL}/login", data=TEST_USER)
    print(f"Valid login status: {response.status_code}")
    
    # Test invalid login
    invalid_user = {"username": "invalid", "password": "wrong"}
    response = requests.post(f"{BASE_URL}/login", data=invalid_user)
    print(f"Invalid login status: {response.status_code}")

def test_task_creation():
    """Test task creation with various inputs"""
    print("\nTesting task creation...")
    
    # Test cases for task creation
    test_tasks = [
        {
            "title": "Test Task 1",
            "description": "This is a test task",
            "status": "pending",
            "priority": "high",
            "is_urgent": True
        },
        {
            "title": "Test Task 2",
            "description": "",
            "status": "in_progress",
            "priority": "low",
            "is_urgent": False
        },
        {
            "title": "",  # Invalid - empty title
            "description": "Task with no title",
            "status": "pending",
            "priority": "medium",
            "is_urgent": False
        }
    ]
    
    for i, task in enumerate(test_tasks):
        print(f"Test case {i+1}: {task['title'] or 'Empty title'}")
        if not task['title']:
            print("  Expected: Should fail validation")
        else:
            print(f"  Expected: Should create task with priority {task['priority']}")

def test_filtering_and_pagination():
    """Test filtering and pagination functionality"""
    print("\nTesting filtering and pagination...")
    
    # Test filter combinations
    filter_tests = [
        {"status": "pending"},
        {"priority": "high"},
        {"urgent": "true"},
        {"status": "completed", "priority": "low"},
        {"page": "2"}
    ]
    
    for filter_test in filter_tests:
        print(f"Filter test: {filter_test}")
        print("  Expected: Should return filtered results")

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\nTesting edge cases...")
    
    edge_cases = [
        "Very long task title that exceeds normal length expectations and might cause display issues",
        "Task with special characters: !@#$%^&*()_+-=[]{}|;':\",./<>?",
        "Task with unicode: 🚀 Unicode Task with Emojis 📝",
        "",  # Empty title
        "   ",  # Whitespace only title
    ]
    
    for case in edge_cases:
        print(f"Edge case: '{case[:50]}{'...' if len(case) > 50 else ''}'")
        if not case.strip():
            print("  Expected: Should fail validation")
        else:
            print("  Expected: Should handle gracefully")

def run_all_tests():
    """Run all test cases"""
    print("=" * 50)
    print("TASK MANAGER APPLICATION TEST PLAN")
    print("=" * 50)
    
    test_login()
    test_task_creation()
    test_filtering_and_pagination()
    test_edge_cases()
    
    print("\n" + "=" * 50)
    print("TEST PLAN COMPLETE")
    print("=" * 50)
    print("\nNOTE: This is a test plan demonstration.")
    print("For actual testing, implement proper test framework like pytest.")

if __name__ == "__main__":
    run_all_tests()
