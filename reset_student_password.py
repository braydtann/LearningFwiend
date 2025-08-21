#!/usr/bin/env python3
"""
STUDENT PASSWORD RESET AND VERIFICATION
Reset password for test.student@cleanenv.com and verify login
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://lms-evolution.emergent.host/api"
TEST_TIMEOUT = 15

ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

def get_admin_token():
    """Get admin authentication token"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=ADMIN_CREDENTIALS,
            timeout=TEST_TIMEOUT,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token')
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Admin login error: {str(e)}")
        return None

def find_student():
    """Find the test student in the system"""
    admin_token = get_admin_token()
    if not admin_token:
        return None
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/auth/admin/users",
            timeout=TEST_TIMEOUT,
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        if response.status_code == 200:
            users = response.json()
            for user in users:
                if user.get('email') == 'test.student@cleanenv.com':
                    print(f"✅ Found student: {user.get('email')} (ID: {user.get('id')})")
                    return user, admin_token
            
            print("❌ Student test.student@cleanenv.com not found in system")
            print(f"Found {len(users)} users:")
            for user in users:
                if user.get('role') == 'learner':
                    print(f"   🎓 {user.get('email')} - {user.get('full_name')}")
            return None, admin_token
        else:
            print(f"❌ Failed to get users: {response.status_code}")
            return None, admin_token
    except Exception as e:
        print(f"❌ Error finding student: {str(e)}")
        return None, admin_token

def reset_student_password(student, admin_token):
    """Reset student password"""
    try:
        reset_data = {
            "user_id": student.get('id'),
            "new_temporary_password": "CleanEnv123!"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/auth/admin/reset-password",
            json=reset_data,
            timeout=TEST_TIMEOUT,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {admin_token}'
            }
        )
        
        if response.status_code == 200:
            print(f"✅ Password reset successful for {student.get('email')}")
            return True
        else:
            print(f"❌ Password reset failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error resetting password: {str(e)}")
        return False

def test_student_login():
    """Test student login after password reset"""
    try:
        login_data = {
            "username_or_email": "test.student@cleanenv.com",
            "password": "CleanEnv123!"
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
            print(f"✅ Student login successful: {user_info.get('email')}")
            print(f"   Role: {user_info.get('role')}")
            print(f"   Name: {user_info.get('full_name')}")
            print(f"   ID: {user_info.get('id')}")
            return True
        else:
            print(f"❌ Student login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing student login: {str(e)}")
        return False

def main():
    print("🔧 STUDENT PASSWORD RESET AND VERIFICATION")
    print("=" * 50)
    
    # Step 1: Find student
    print("\n🔍 Step 1: Finding student...")
    student, admin_token = find_student()
    
    if not student:
        print("❌ Cannot proceed - student not found")
        return False
    
    # Step 2: Reset password
    print("\n🔑 Step 2: Resetting password...")
    reset_success = reset_student_password(student, admin_token)
    
    if not reset_success:
        print("❌ Cannot proceed - password reset failed")
        return False
    
    # Step 3: Test login
    print("\n🎓 Step 3: Testing student login...")
    login_success = test_student_login()
    
    if login_success:
        print("\n✅ Student authentication is now working!")
        print("Credentials: test.student@cleanenv.com / CleanEnv123!")
        return True
    else:
        print("\n❌ Student authentication still failing")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)