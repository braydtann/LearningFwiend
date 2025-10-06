#!/usr/bin/env python3
"""
Admin Enrollment Script
======================

Enroll karlo.student in the multi-quiz course using admin privileges.
"""

import requests
import json
import uuid
from datetime import datetime, timezone

BACKEND_URL = "https://lms-progression-1.preview.emergentagent.com/api"

ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

def authenticate_admin():
    """Authenticate admin"""
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Admin authenticated")
            return data["access_token"]
        else:
            print(f"❌ Admin auth failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Auth error: {str(e)}")
        return None

def create_enrollment_directly():
    """Create enrollment by directly inserting into database via admin API"""
    token = authenticate_admin()
    if not token:
        return
    
    # Course and user info
    course_id = "3998fee5-ed4e-4500-9826-0092d393e407"
    user_id = "1007f897-35a6-4647-b2b3-cb4bb74ffe4a"
    
    # Create enrollment data
    enrollment_data = {
        "id": str(uuid.uuid4()),
        "userId": user_id,
        "courseId": course_id,
        "enrolledAt": datetime.now(timezone.utc).isoformat(),
        "status": "active",
        "progress": 1.0,  # Start with 1% to avoid reset issue
        "moduleProgress": [],
        "currentLessonId": None,
        "currentModuleId": None,
        "lastAccessedAt": datetime.now(timezone.utc).isoformat(),
        "timeSpent": 0
    }
    
    print("📝 Creating enrollment directly...")
    
    # Try multiple approaches
    approaches = [
        ("POST", f"{BACKEND_URL}/admin/enrollments"),
        ("POST", f"{BACKEND_URL}/enrollments"), 
        ("PUT", f"{BACKEND_URL}/admin/enroll-student"),
        ("POST", f"{BACKEND_URL}/admin/manual-enrollment")
    ]
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    for method, url in approaches:
        try:
            if method == "POST":
                response = requests.post(url, headers=headers, json=enrollment_data)
            elif method == "PUT":
                simple_data = {
                    "userId": user_id,
                    "courseId": course_id,
                    "userEmail": "karlo.student@alder.com"
                }
                response = requests.put(url, headers=headers, json=simple_data)
            
            print(f"   {method} {url}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ Enrollment created successfully via {url}!")
                return True
            elif response.status_code == 201:
                print(f"✅ Enrollment created successfully via {url}!")
                return True
                
        except Exception as e:
            print(f"   {method} {url}: Error - {str(e)}")
    
    print("❌ All enrollment approaches failed")
    return False

if __name__ == "__main__":
    print("🚀 Admin Enrollment for Multi-Quiz Testing")
    print("=" * 50)
    
    success = create_enrollment_directly()
    
    if success:
        print()
        print("✅ ENROLLMENT SUCCESSFUL!")
        print("🎯 karlo.student@alder.com is now enrolled in Multi-Quiz Progression Test Course")
        print()
        print("📋 TESTING READY:")
        print("1. Login as karlo.student@alder.com / StudentPermanent123!")
        print("2. Navigate to 'Multi-Quiz Progression Test Course'")
        print("3. Test multi-quiz progression functionality")
    else:
        print()
        print("⚠️  MANUAL ENROLLMENT NEEDED")
        print("Please use the admin interface to enroll karlo.student@alder.com")
        print("in the 'Multi-Quiz Progression Test Course'")