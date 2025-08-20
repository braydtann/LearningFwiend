#!/usr/bin/env python3
"""
Production Backend Investigation - Student User Analysis
"""

import requests
import json
from datetime import datetime

PRODUCTION_BACKEND_URL = "https://lms-evolution.emergent.host/api"
TEST_TIMEOUT = 15

def investigate_production_backend():
    print("🔍 INVESTIGATING PRODUCTION BACKEND ISSUES")
    print("=" * 60)
    
    # Step 1: Login as admin
    print("\n🔑 Step 1: Admin Login")
    admin_login_data = {
        "username_or_email": "brayden.t@covesmart.com",
        "password": "Hawaii2020!"
    }
    
    admin_response = requests.post(
        f"{PRODUCTION_BACKEND_URL}/auth/login",
        json=admin_login_data,
        timeout=TEST_TIMEOUT,
        headers={'Content-Type': 'application/json'}
    )
    
    if admin_response.status_code != 200:
        print("❌ Admin login failed")
        return
    
    admin_token = admin_response.json().get('access_token')
    print("✅ Admin login successful")
    
    # Step 2: Get all users to check if student exists
    print("\n👥 Step 2: Checking Users in Production Backend")
    users_response = requests.get(
        f"{PRODUCTION_BACKEND_URL}/auth/admin/users",
        timeout=TEST_TIMEOUT,
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    
    if users_response.status_code == 200:
        users = users_response.json()
        print(f"Found {len(users)} users in production backend:")
        
        student_user = None
        for user in users:
            role = user.get('role', 'unknown')
            email = user.get('email', 'N/A')
            username = user.get('username', 'N/A')
            full_name = user.get('full_name', 'N/A')
            
            print(f"  {role.upper()}: {full_name} | {email} | {username}")
            
            if email == 'karlo.student@alder.com':
                student_user = user
        
        if student_user:
            print(f"\n✅ Found target student: {student_user.get('email')}")
            print(f"   ID: {student_user.get('id')}")
            print(f"   Full Name: {student_user.get('full_name')}")
            print(f"   Username: {student_user.get('username')}")
            print(f"   First Login Required: {student_user.get('first_login_required')}")
            
            # Step 3: Reset student password
            print(f"\n🔄 Step 3: Resetting Student Password")
            reset_data = {
                "user_id": student_user.get('id'),
                "new_temporary_password": "StudentPermanent123!"
            }
            
            reset_response = requests.post(
                f"{PRODUCTION_BACKEND_URL}/auth/admin/reset-password",
                json=reset_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {admin_token}'
                }
            )
            
            if reset_response.status_code == 200:
                print("✅ Password reset successful")
                
                # Step 4: Try student login again
                print(f"\n🎓 Step 4: Testing Student Login After Reset")
                student_login_data = {
                    "username_or_email": "karlo.student@alder.com",
                    "password": "StudentPermanent123!"
                }
                
                student_response = requests.post(
                    f"{PRODUCTION_BACKEND_URL}/auth/login",
                    json=student_login_data,
                    timeout=TEST_TIMEOUT,
                    headers={'Content-Type': 'application/json'}
                )
                
                if student_response.status_code == 200:
                    student_data = student_response.json()
                    student_token = student_data.get('access_token')
                    print("✅ Student login successful after password reset")
                    
                    # Step 5: Test student APIs
                    print(f"\n📚 Step 5: Testing Student API Access")
                    
                    # Test courses API
                    courses_response = requests.get(
                        f"{PRODUCTION_BACKEND_URL}/courses",
                        timeout=TEST_TIMEOUT,
                        headers={'Authorization': f'Bearer {student_token}'}
                    )
                    
                    if courses_response.status_code == 200:
                        courses = courses_response.json()
                        print(f"✅ Courses API: {len(courses)} courses available")
                        
                        # Show sample courses
                        for i, course in enumerate(courses[:3]):
                            print(f"   {i+1}. {course.get('title', 'Unknown Title')}")
                    else:
                        print(f"❌ Courses API failed: {courses_response.status_code}")
                    
                    # Test enrollments API
                    enrollments_response = requests.get(
                        f"{PRODUCTION_BACKEND_URL}/enrollments",
                        timeout=TEST_TIMEOUT,
                        headers={'Authorization': f'Bearer {student_token}'}
                    )
                    
                    if enrollments_response.status_code == 200:
                        enrollments = enrollments_response.json()
                        print(f"✅ Enrollments API: {len(enrollments)} enrollments found")
                    else:
                        print(f"❌ Enrollments API failed: {enrollments_response.status_code}")
                    
                else:
                    print(f"❌ Student login still failed: {student_response.status_code}")
                    print(f"   Response: {student_response.text}")
            else:
                print(f"❌ Password reset failed: {reset_response.status_code}")
                print(f"   Response: {reset_response.text}")
        else:
            print(f"\n❌ Student karlo.student@alder.com not found in production backend")
            print("   Available students:")
            for user in users:
                if user.get('role') == 'learner':
                    print(f"     {user.get('email')} | {user.get('full_name')}")
    else:
        print(f"❌ Failed to get users: {users_response.status_code}")
    
    # Step 6: Check classrooms for QC1
    print(f"\n🏫 Step 6: Checking for QC1 Classroom")
    classrooms_response = requests.get(
        f"{PRODUCTION_BACKEND_URL}/classrooms",
        timeout=TEST_TIMEOUT,
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    
    if classrooms_response.status_code == 200:
        classrooms = classrooms_response.json()
        print(f"Found {len(classrooms)} classrooms:")
        
        qc1_found = False
        for classroom in classrooms:
            name = classroom.get('name', 'Unknown')
            print(f"  - {name}")
            if name.lower() == 'qc1':
                qc1_found = True
                print(f"    ✅ QC1 classroom found!")
                print(f"    Students: {len(classroom.get('studentIds', []))}")
                print(f"    Courses: {len(classroom.get('courseIds', []))}")
        
        if not qc1_found:
            print("❌ QC1 classroom not found in production backend")
    else:
        print(f"❌ Failed to get classrooms: {classrooms_response.status_code}")

if __name__ == "__main__":
    investigate_production_backend()