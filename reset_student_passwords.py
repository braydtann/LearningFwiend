#!/usr/bin/env python3
"""
RESET STUDENT PASSWORDS FOR TESTING
Using admin credentials to reset passwords for existing student accounts
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://lms-evolution.emergent.host/api"
TEST_TIMEOUT = 15

ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

# Target student accounts to reset passwords for
TARGET_STUDENTS = [
    {
        "email": "karlo.student@alder.com",
        "name": "Karlo Student",
        "new_password": "StudentTest123!"
    },
    {
        "email": "test.student@cleanenv.com", 
        "name": "Test Student - Clean Environment",
        "new_password": "CleanEnv123!"
    },
    {
        "email": "brayden.student@covesmart.com",
        "name": "brayden student", 
        "new_password": "StudentCove123!"
    }
]

def get_admin_token():
    """Get admin authentication token"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=ADMIN_CREDENTIALS,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token')
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Admin login error: {e}")
        return None

def get_user_id_by_email(admin_token, email):
    """Get user ID by email address"""
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(
            f"{BACKEND_URL}/auth/admin/users",
            headers=headers,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            users = response.json()
            for user in users:
                if user.get('email') == email:
                    return user.get('id')
            return None
        else:
            print(f"❌ Failed to get users: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting users: {e}")
        return None

def reset_password(admin_token, user_id, new_password):
    """Reset user password using admin endpoint"""
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        reset_data = {
            "user_id": user_id,
            "new_temporary_password": new_password
        }
        
        response = requests.post(
            f"{BACKEND_URL}/auth/admin/reset-password",
            json=reset_data,
            headers=headers,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Status: {response.status_code}, Response: {response.text[:200]}"
    except Exception as e:
        return False, f"Error: {e}"

def test_login(email, password):
    """Test login with reset credentials"""
    try:
        credentials = {
            "username_or_email": email,
            "password": password
        }
        
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=credentials,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            user_info = data.get('user', {})
            return True, {
                'role': user_info.get('role'),
                'name': user_info.get('full_name'),
                'requires_password_change': data.get('requires_password_change', False)
            }
        else:
            return False, f"Status: {response.status_code}"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Main execution function"""
    print("🔑 RESETTING STUDENT PASSWORDS FOR TESTING")
    print("=" * 60)
    
    admin_token = get_admin_token()
    if not admin_token:
        print("❌ Cannot proceed without admin token")
        return
    
    print("✅ Admin authentication successful")
    print()
    
    working_credentials = []
    
    for student in TARGET_STUDENTS:
        email = student['email']
        name = student['name']
        new_password = student['new_password']
        
        print(f"🔄 Processing: {name} ({email})")
        
        # Get user ID
        user_id = get_user_id_by_email(admin_token, email)
        if not user_id:
            print(f"   ❌ User not found")
            continue
        
        print(f"   📋 User ID: {user_id}")
        
        # Reset password
        success, result = reset_password(admin_token, user_id, new_password)
        if not success:
            print(f"   ❌ Password reset failed: {result}")
            continue
        
        print(f"   ✅ Password reset successful")
        
        # Test login
        login_success, login_result = test_login(email, new_password)
        if login_success:
            print(f"   ✅ Login test successful - Role: {login_result['role']}")
            if login_result['requires_password_change']:
                print(f"   ⚠️  Requires password change on first login")
            
            working_credentials.append({
                'email': email,
                'password': new_password,
                'name': name,
                'role': login_result['role'],
                'requires_password_change': login_result['requires_password_change']
            })
        else:
            print(f"   ❌ Login test failed: {login_result}")
        
        print()
    
    # Summary
    print("🎯 FINAL WORKING CREDENTIALS SUMMARY")
    print("=" * 60)
    
    if working_credentials:
        print("✅ WORKING STUDENT CREDENTIALS:")
        print()
        
        for i, cred in enumerate(working_credentials, 1):
            print(f"{i}. Email: {cred['email']}")
            print(f"   Password: {cred['password']}")
            print(f"   Name: {cred['name']}")
            print(f"   Role: {cred['role']}")
            if cred['requires_password_change']:
                print(f"   ⚠️  Requires password change on first login")
            print()
        
        print("PLUS the previously created account:")
        print(f"{len(working_credentials)+1}. Email: test.student.20250822233058@urgenttest.com")
        print(f"   Password: TestStudent123!")
        print(f"   Name: Test Student 20250822233058")
        print(f"   Role: learner")
        print(f"   ⚠️  Requires password change on first login")
        print()
        
        print("🎉 SUCCESS: User now has multiple working student accounts for quiz testing!")
        
    else:
        print("❌ No working credentials established")
        print("Use the previously created account:")
        print("   Email: test.student.20250822233058@urgenttest.com")
        print("   Password: TestStudent123!")

if __name__ == "__main__":
    main()