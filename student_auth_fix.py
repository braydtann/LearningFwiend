#!/usr/bin/env python3
"""
Student Authentication Investigation and Fix
"""

import requests
import json

BACKEND_URL = "https://lms-chronology.emergent.host/api"

ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

def authenticate_admin():
    """Get admin token"""
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json=ADMIN_CREDENTIALS,
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    return None

def check_student_user():
    """Check if student user exists and reset password if needed"""
    admin_token = authenticate_admin()
    if not admin_token:
        print("❌ Failed to authenticate as admin")
        return
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Get all users to find the student
    response = requests.get(
        f"{BACKEND_URL}/auth/admin/users",
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        users = response.json()
        student_user = None
        
        for user in users:
            if user.get("email") == "karlo.student@alder.com":
                student_user = user
                break
        
        if student_user:
            print(f"✅ Found student user: {student_user.get('email')}")
            print(f"   User ID: {student_user.get('id')}")
            print(f"   Role: {student_user.get('role')}")
            print(f"   Active: {student_user.get('is_active')}")
            print(f"   First login required: {student_user.get('first_login_required')}")
            
            # Reset password
            reset_data = {
                "user_id": student_user.get("id"),
                "new_temporary_password": "StudentPermanent123!"
            }
            
            reset_response = requests.post(
                f"{BACKEND_URL}/auth/admin/reset-password",
                json=reset_data,
                headers=headers,
                timeout=10
            )
            
            if reset_response.status_code == 200:
                print("✅ Successfully reset student password")
                
                # Test login with reset password
                test_login = requests.post(
                    f"{BACKEND_URL}/auth/login",
                    json={
                        "username_or_email": "karlo.student@alder.com",
                        "password": "StudentPermanent123!"
                    },
                    timeout=10
                )
                
                if test_login.status_code == 200:
                    print("✅ Student login now working!")
                else:
                    print(f"❌ Student login still failing: {test_login.status_code} - {test_login.text}")
            else:
                print(f"❌ Failed to reset password: {reset_response.status_code} - {reset_response.text}")
        else:
            print("❌ Student user not found. Creating new student user...")
            
            # Create student user
            create_data = {
                "email": "karlo.student@alder.com",
                "username": "karlo.student",
                "full_name": "Karlo Student",
                "role": "learner",
                "temporary_password": "StudentPermanent123!"
            }
            
            create_response = requests.post(
                f"{BACKEND_URL}/auth/admin/create-user",
                json=create_data,
                headers=headers,
                timeout=10
            )
            
            if create_response.status_code == 200:
                print("✅ Successfully created student user")
                
                # Test login
                test_login = requests.post(
                    f"{BACKEND_URL}/auth/login",
                    json={
                        "username_or_email": "karlo.student@alder.com",
                        "password": "StudentPermanent123!"
                    },
                    timeout=10
                )
                
                if test_login.status_code == 200:
                    print("✅ New student login working!")
                else:
                    print(f"❌ New student login failing: {test_login.status_code} - {test_login.text}")
            else:
                print(f"❌ Failed to create student user: {create_response.status_code} - {create_response.text}")
    else:
        print(f"❌ Failed to get users: {response.status_code} - {response.text}")

if __name__ == "__main__":
    check_student_user()