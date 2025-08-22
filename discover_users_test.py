#!/usr/bin/env python3
"""
DISCOVER EXISTING USERS ON REMOTE BACKEND
Using admin credentials to discover existing student accounts
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

def discover_existing_users():
    """Discover existing users on the backend"""
    print("🔍 DISCOVERING EXISTING USERS ON REMOTE BACKEND")
    print("=" * 60)
    
    admin_token = get_admin_token()
    if not admin_token:
        print("❌ Cannot proceed without admin token")
        return
    
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(
            f"{BACKEND_URL}/auth/admin/users",
            headers=headers,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Found {len(users)} total users on the backend")
            print()
            
            # Categorize users by role
            admins = [u for u in users if u.get('role') == 'admin']
            instructors = [u for u in users if u.get('role') == 'instructor']
            learners = [u for u in users if u.get('role') == 'learner']
            
            print(f"👑 ADMINS ({len(admins)}):")
            for admin in admins:
                print(f"   • {admin.get('email', 'No email')} - {admin.get('full_name', 'No name')}")
            print()
            
            print(f"🎓 INSTRUCTORS ({len(instructors)}):")
            for instructor in instructors:
                print(f"   • {instructor.get('email', 'No email')} - {instructor.get('full_name', 'No name')}")
            print()
            
            print(f"📚 LEARNERS/STUDENTS ({len(learners)}):")
            for learner in learners:
                active_status = "✅ Active" if learner.get('is_active', True) else "❌ Inactive"
                password_status = "🔑 Temp Password" if learner.get('first_login_required', False) else "🔓 Set Password"
                print(f"   • {learner.get('email', 'No email')} - {learner.get('full_name', 'No name')} ({active_status}, {password_status})")
            
            print()
            print("🎯 POTENTIAL STUDENT ACCOUNTS FOR TESTING:")
            print("-" * 50)
            
            # Focus on active learners
            active_learners = [l for l in learners if l.get('is_active', True)]
            
            if active_learners:
                print("The following student accounts exist and are active:")
                for i, learner in enumerate(active_learners[:10], 1):  # Show first 10
                    email = learner.get('email', 'No email')
                    name = learner.get('full_name', 'No name')
                    needs_password_change = learner.get('first_login_required', False)
                    
                    print(f"{i}. Email: {email}")
                    print(f"   Name: {name}")
                    print(f"   Status: {'Needs password change' if needs_password_change else 'Password already set'}")
                    print()
                
                print("💡 RECOMMENDATION:")
                print("Try contacting the system administrator to get passwords for these existing accounts,")
                print("or use the newly created test account from the previous test:")
                print("   Email: test.student.20250822233058@urgenttest.com")
                print("   Password: TestStudent123!")
            else:
                print("No active student accounts found. Use the newly created test account.")
            
        else:
            print(f"❌ Failed to get users: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error discovering users: {e}")

if __name__ == "__main__":
    discover_existing_users()