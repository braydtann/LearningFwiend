#!/usr/bin/env python3
"""
Multiple Choice Account Verification and Password Reset
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://summarize-it-2.preview.emergentagent.com/api"
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

def check_mc_accounts():
    """Check if Multiple Choice accounts exist"""
    admin_token = get_admin_token()
    if not admin_token:
        print("❌ Cannot get admin token")
        return
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/auth/admin/users",
            timeout=TEST_TIMEOUT,
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        if response.status_code == 200:
            users = response.json()
            
            mc_admin = None
            mc_student = None
            
            for user in users:
                if user.get('email') == 'mc.admin.20250823_234459@testmc.com':
                    mc_admin = user
                elif user.get('email') == 'mc.student.20250823_234459@testmc.com':
                    mc_student = user
            
            print(f"🔍 MULTIPLE CHOICE ACCOUNT VERIFICATION")
            print("-" * 50)
            
            if mc_admin:
                print(f"✅ MC Admin account exists:")
                print(f"   Email: {mc_admin.get('email')}")
                print(f"   Username: {mc_admin.get('username')}")
                print(f"   Role: {mc_admin.get('role')}")
                print(f"   First login required: {mc_admin.get('first_login_required')}")
                print(f"   Active: {mc_admin.get('is_active')}")
                
                # Reset password
                reset_password(admin_token, mc_admin.get('id'), "MCAdmin123!", "MC Admin")
            else:
                print("❌ MC Admin account NOT FOUND")
            
            if mc_student:
                print(f"✅ MC Student account exists:")
                print(f"   Email: {mc_student.get('email')}")
                print(f"   Username: {mc_student.get('username')}")
                print(f"   Role: {mc_student.get('role')}")
                print(f"   First login required: {mc_student.get('first_login_required')}")
                print(f"   Active: {mc_student.get('is_active')}")
                
                # Reset password
                reset_password(admin_token, mc_student.get('id'), "MCStudent123!", "MC Student")
            else:
                print("❌ MC Student account NOT FOUND")
                
        else:
            print(f"❌ Failed to get users: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking accounts: {str(e)}")

def reset_password(admin_token, user_id, new_password, user_type):
    """Reset user password"""
    try:
        reset_data = {
            "user_id": user_id,
            "new_temporary_password": new_password
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
            print(f"✅ {user_type} password reset successful")
        else:
            print(f"❌ {user_type} password reset failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error resetting {user_type} password: {str(e)}")

def test_mc_accounts_after_reset():
    """Test Multiple Choice accounts after password reset"""
    print(f"\n🔐 TESTING MC ACCOUNTS AFTER PASSWORD RESET")
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
    except Exception as e:
        print(f"❌ MC Student login error: {str(e)}")

if __name__ == "__main__":
    check_mc_accounts()
    test_mc_accounts_after_reset()