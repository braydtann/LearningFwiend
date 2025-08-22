#!/usr/bin/env python3
"""
Setup test users for comprehensive testing
"""

import requests
import json

BACKEND_URL = "https://lms-stability.preview.emergentagent.com/api"
TEST_TIMEOUT = 10

def setup_test_users():
    """Setup test users for testing"""
    print("🔧 Setting up test users...")
    
    # Login as admin first
    admin_login = {
        "username_or_email": "admin",
        "password": "NewAdmin123!"
    }
    
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json=admin_login,
        timeout=TEST_TIMEOUT,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 200:
        print(f"❌ Admin login failed: {response.status_code}")
        return False
    
    admin_token = response.json().get('access_token')
    print("✅ Admin login successful")
    
    # Check existing users
    users_response = requests.get(
        f"{BACKEND_URL}/auth/admin/users",
        timeout=TEST_TIMEOUT,
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    
    if users_response.status_code != 200:
        print(f"❌ Failed to get users: {users_response.status_code}")
        return False
    
    users = users_response.json()
    print(f"📊 Found {len(users)} existing users")
    
    # Check if we have required test users
    required_users = [
        {
            "username": "student",
            "email": "student@test.com",
            "full_name": "Test Student",
            "role": "learner",
            "password": "Student123!"
        },
        {
            "username": "instructor",
            "email": "instructor@test.com", 
            "full_name": "Test Instructor",
            "role": "instructor",
            "password": "Instructor123!"
        }
    ]
    
    existing_usernames = [user.get('username') for user in users]
    
    for user_data in required_users:
        if user_data['username'] not in existing_usernames:
            print(f"🔨 Creating user: {user_data['username']}")
            
            create_data = {
                "email": user_data['email'],
                "username": user_data['username'],
                "full_name": user_data['full_name'],
                "role": user_data['role'],
                "department": "Testing",
                "temporary_password": user_data['password']
            }
            
            create_response = requests.post(
                f"{BACKEND_URL}/auth/admin/create-user",
                json=create_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {admin_token}'
                }
            )
            
            if create_response.status_code == 200:
                print(f"✅ Created user: {user_data['username']}")
            else:
                print(f"❌ Failed to create {user_data['username']}: {create_response.status_code}")
                print(f"Response: {create_response.text}")
        else:
            print(f"✅ User {user_data['username']} already exists")
    
    # Test login for each required user
    test_logins = [
        {"username": "admin", "password": "NewAdmin123!"},
        {"username": "instructor", "password": "Instructor123!"},
        {"username": "student", "password": "Student123!"}
    ]
    
    print("\n🔐 Testing user logins...")
    for login_data in test_logins:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"username_or_email": login_data["username"], "password": login_data["password"]},
            timeout=TEST_TIMEOUT,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print(f"✅ {login_data['username']} login successful")
        else:
            print(f"❌ {login_data['username']} login failed: {response.status_code}")
            print(f"Response: {response.text}")
    
    return True

if __name__ == "__main__":
    setup_test_users()