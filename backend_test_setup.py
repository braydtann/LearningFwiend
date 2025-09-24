#!/usr/bin/env python3
"""
Backend Test Setup - Create test users and verify authentication
"""

import requests
import json
import uuid

BACKEND_URL = "https://lms-analytics-hub.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

def setup_test_users():
    """Setup test users for comprehensive testing"""
    print("🔧 SETTING UP TEST USERS FOR COMPREHENSIVE TESTING")
    print("="*60)
    
    # First, login as admin to create test users
    admin_login = {
        "username_or_email": "admin",
        "password": "NewAdmin123!"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=admin_login,
            timeout=TEST_TIMEOUT,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code != 200:
            print(f"❌ Admin login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        admin_token = response.json().get('access_token')
        print("✅ Admin login successful")
        
    except Exception as e:
        print(f"❌ Admin login error: {str(e)}")
        return False
    
    # Get existing users first
    try:
        response = requests.get(
            f"{BACKEND_URL}/auth/admin/users",
            timeout=TEST_TIMEOUT,
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        if response.status_code == 200:
            existing_users = response.json()
            print(f"📋 Found {len(existing_users)} existing users:")
            
            for user in existing_users:
                print(f"   • {user.get('username')} ({user.get('email')}) - {user.get('role')}")
                
        else:
            print(f"❌ Failed to get existing users: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting users: {str(e)}")
    
    # Create test instructor if doesn't exist
    test_instructor = {
        "email": "test.instructor@learningfwiend.com",
        "username": "test.instructor",
        "full_name": "Test Instructor User",
        "role": "instructor",
        "department": "Testing",
        "temporary_password": "TestInstructor123!"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/admin/create-user",
            json=test_instructor,
            timeout=TEST_TIMEOUT,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {admin_token}'
            }
        )
        
        if response.status_code == 200:
            print("✅ Test instructor created successfully")
        elif response.status_code == 400 and "already exists" in response.text:
            print("ℹ️  Test instructor already exists")
        else:
            print(f"❌ Failed to create test instructor: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error creating test instructor: {str(e)}")
    
    # Create test learner if doesn't exist
    test_learner = {
        "email": "test.learner@learningfwiend.com",
        "username": "test.learner",
        "full_name": "Test Learner User",
        "role": "learner",
        "department": "Testing",
        "temporary_password": "TestLearner123!"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/admin/create-user",
            json=test_learner,
            timeout=TEST_TIMEOUT,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {admin_token}'
            }
        )
        
        if response.status_code == 200:
            print("✅ Test learner created successfully")
        elif response.status_code == 400 and "already exists" in response.text:
            print("ℹ️  Test learner already exists")
        else:
            print(f"❌ Failed to create test learner: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error creating test learner: {str(e)}")
    
    # Test login with all users
    test_credentials = [
        {"username": "admin", "password": "NewAdmin123!", "role": "admin"},
        {"username": "test.instructor", "password": "TestInstructor123!", "role": "instructor"},
        {"username": "test.learner", "password": "TestLearner123!", "role": "learner"},
        {"username": "instructor", "password": "Instructor123!", "role": "instructor"},  # Try original
        {"username": "student", "password": "Student123!", "role": "learner"}  # Try original
    ]
    
    print("\n🔐 TESTING LOGIN FOR ALL USERS:")
    print("-" * 40)
    
    working_credentials = []
    
    for creds in test_credentials:
        try:
            login_data = {
                "username_or_email": creds["username"],
                "password": creds["password"]
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                user_info = data.get('user', {})
                print(f"✅ {creds['username']} ({creds['role']}) - Login successful")
                print(f"   User ID: {user_info.get('id')}")
                print(f"   Requires password change: {data.get('requires_password_change')}")
                working_credentials.append(creds)
            else:
                print(f"❌ {creds['username']} ({creds['role']}) - Login failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {creds['username']} ({creds['role']}) - Login error: {str(e)}")
    
    print(f"\n📊 SUMMARY: {len(working_credentials)} out of {len(test_credentials)} users can login")
    
    if len(working_credentials) >= 2:  # Need at least admin and one other role
        print("✅ Sufficient users available for testing")
        return True
    else:
        print("❌ Insufficient users for comprehensive testing")
        return False

if __name__ == "__main__":
    setup_test_users()