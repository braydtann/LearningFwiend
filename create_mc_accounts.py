#!/usr/bin/env python3
"""
Create Multiple Choice Test Accounts
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://lms-media-display.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

# Fallback admin credentials that work
FALLBACK_ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

def get_admin_token():
    """Get admin token using fallback admin"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=FALLBACK_ADMIN_CREDENTIALS,
            timeout=TEST_TIMEOUT,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token')
    except:
        pass
    return None

def create_mc_accounts():
    """Create Multiple Choice test accounts"""
    admin_token = get_admin_token()
    if not admin_token:
        print("❌ Cannot get admin token")
        return
    
    print(f"🚀 CREATING MULTIPLE CHOICE TEST ACCOUNTS")
    print("-" * 50)
    
    # Create MC Admin account
    mc_admin_data = {
        "email": "mc.admin.20250823_234459@testmc.com",
        "username": "mc.admin.20250823_234459",
        "full_name": "MC Admin Test User",
        "role": "admin",
        "department": "Testing",
        "temporary_password": "MCAdmin123!"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/admin/create-user",
            json=mc_admin_data,
            timeout=TEST_TIMEOUT,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {admin_token}'
            }
        )
        
        if response.status_code == 200:
            created_admin = response.json()
            print(f"✅ MC Admin account created successfully:")
            print(f"   Email: {created_admin.get('email')}")
            print(f"   Username: {created_admin.get('username')}")
            print(f"   Role: {created_admin.get('role')}")
            print(f"   ID: {created_admin.get('id')}")
        else:
            print(f"❌ MC Admin account creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error creating MC Admin account: {str(e)}")
    
    # Create MC Student account
    mc_student_data = {
        "email": "mc.student.20250823_234459@testmc.com",
        "username": "mc.student.20250823_234459",
        "full_name": "MC Student Test User",
        "role": "learner",
        "department": "Testing",
        "temporary_password": "MCStudent123!"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/admin/create-user",
            json=mc_student_data,
            timeout=TEST_TIMEOUT,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {admin_token}'
            }
        )
        
        if response.status_code == 200:
            created_student = response.json()
            print(f"✅ MC Student account created successfully:")
            print(f"   Email: {created_student.get('email')}")
            print(f"   Username: {created_student.get('username')}")
            print(f"   Role: {created_student.get('role')}")
            print(f"   ID: {created_student.get('id')}")
        else:
            print(f"❌ MC Student account creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error creating MC Student account: {str(e)}")

def test_mc_accounts():
    """Test Multiple Choice accounts after creation"""
    print(f"\n🔐 TESTING MC ACCOUNTS AFTER CREATION")
    print("-" * 50)
    
    # Test MC Admin
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "username_or_email": "mc.admin.20250823_234459@testmc.com",
                "password": "MCAdmin123!"
            },
            timeout=TEST_TIMEOUT,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            user_info = data.get('user', {})
            print(f"✅ MC Admin login successful: {user_info.get('email')} (Role: {user_info.get('role')})")
        else:
            print(f"❌ MC Admin login failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ MC Admin login error: {str(e)}")
    
    # Test MC Student
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "username_or_email": "mc.student.20250823_234459@testmc.com",
                "password": "MCStudent123!"
            },
            timeout=TEST_TIMEOUT,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            user_info = data.get('user', {})
            print(f"✅ MC Student login successful: {user_info.get('email')} (Role: {user_info.get('role')})")
        else:
            print(f"❌ MC Student login failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ MC Student login error: {str(e)}")

if __name__ == "__main__":
    create_mc_accounts()
    test_mc_accounts()