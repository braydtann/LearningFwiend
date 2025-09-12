#!/usr/bin/env python3
"""
Focused Testing for Quiz and Certificate API Fixes
"""

import requests
import json
import sys

BACKEND_URL = "https://learning-analytics-2.preview.emergentagent.com/api"
TEST_TIMEOUT = 10

def test_quiz_creation():
    """Test quiz creation with different question types"""
    print("🧩 Testing Quiz API Question Model Validation")
    print("-" * 50)
    
    # First login as instructor
    login_data = {
        "username_or_email": "instructor",
        "password": "Instructor123!"
    }
    
    login_response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json=login_data,
        timeout=TEST_TIMEOUT,
        headers={'Content-Type': 'application/json'}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Failed to login as instructor: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return False
    
    instructor_token = login_response.json().get('access_token')
    
    # Test 1: Create quiz with multiple_choice questions
    multiple_choice_quiz = {
        "title": "Multiple Choice Validation Test",
        "description": "Testing multiple choice question validation",
        "questions": [
            {
                "type": "multiple_choice",
                "question": "What is 2 + 2?",
                "options": ["3", "4", "5", "6"],
                "correctAnswer": "1",  # Index as string
                "points": 10
            }
        ],
        "timeLimit": 30,
        "attempts": 3,
        "passingScore": 70.0,
        "isPublished": True
    }
    
    response = requests.post(
        f"{BACKEND_URL}/quizzes",
        json=multiple_choice_quiz,
        timeout=TEST_TIMEOUT,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {instructor_token}'
        }
    )
    
    if response.status_code == 200:
        quiz_data = response.json()
        print(f"✅ Successfully created multiple choice quiz: {quiz_data.get('id')}")
        return quiz_data.get('id')
    else:
        print(f"❌ Failed to create multiple choice quiz: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def test_certificate_creation():
    """Test certificate creation with admin override"""
    print("\n🏆 Testing Certificate API Enrollment Validation")
    print("-" * 50)
    
    # Login as admin
    login_data = {
        "username_or_email": "admin",
        "password": "NewAdmin123!"
    }
    
    login_response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json=login_data,
        timeout=TEST_TIMEOUT,
        headers={'Content-Type': 'application/json'}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Failed to login as admin: {login_response.status_code}")
        return False
    
    admin_token = login_response.json().get('access_token')
    
    # Get a student and course for testing
    users_response = requests.get(
        f"{BACKEND_URL}/auth/admin/users",
        timeout=TEST_TIMEOUT,
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    
    if users_response.status_code != 200:
        print(f"❌ Failed to get users: {users_response.status_code}")
        return False
    
    users = users_response.json()
    student_id = None
    for user in users:
        if user.get('role') == 'learner':
            student_id = user.get('id')
            break
    
    if not student_id:
        print("❌ No student found for certificate testing")
        return False
    
    # Get courses
    courses_response = requests.get(
        f"{BACKEND_URL}/courses",
        timeout=TEST_TIMEOUT,
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    
    if courses_response.status_code != 200:
        print(f"❌ Failed to get courses: {courses_response.status_code}")
        return False
    
    courses = courses_response.json()
    if not courses:
        print("❌ No courses found for certificate testing")
        return False
    
    course_id = courses[0].get('id')
    
    # Test admin can create certificate without enrollment
    certificate_data = {
        "studentId": student_id,
        "courseId": course_id,
        "type": "completion",
        "template": "default"
    }
    
    response = requests.post(
        f"{BACKEND_URL}/certificates",
        json=certificate_data,
        timeout=TEST_TIMEOUT,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {admin_token}'
        }
    )
    
    if response.status_code == 200:
        print(f"✅ Admin successfully created certificate without enrollment")
        return True
    else:
        print(f"❌ Admin failed to create certificate: {response.status_code}")
        print(f"Response: {response.text}")
        return False

if __name__ == "__main__":
    print("🎯 FOCUSED TESTING OF QUICK FIXES")
    print("=" * 50)
    
    # Test backend health first
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=TEST_TIMEOUT)
        if response.status_code == 200:
            print("✅ Backend is accessible")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        sys.exit(1)
    
    # Run focused tests
    quiz_success = test_quiz_creation()
    cert_success = test_certificate_creation()
    
    print("\n" + "=" * 50)
    print("📊 FOCUSED TEST SUMMARY")
    print("=" * 50)
    
    if quiz_success:
        print("✅ Quiz API Question Model Validation: PASS")
    else:
        print("❌ Quiz API Question Model Validation: FAIL")
    
    if cert_success:
        print("✅ Certificate API Enrollment Validation: PASS")
    else:
        print("❌ Certificate API Enrollment Validation: FAIL")
    
    if quiz_success and cert_success:
        print("\n🎉 All focused tests PASSED!")
        sys.exit(0)
    else:
        print("\n⚠️  Some focused tests FAILED!")
        sys.exit(1)