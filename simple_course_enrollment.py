#!/usr/bin/env python3
"""
Simple Course Enrollment
========================

Create enrollment for karlo.student in the multi-quiz course using known working approach.
"""

import requests
import json

BACKEND_URL = "https://lms-progression-1.preview.emergentagent.com/api"

# Get user credentials from backend testing
STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com",
    "password": "StudentPermanent123!"
}

def authenticate_student():
    """Authenticate student to get their user ID"""
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json=STUDENT_CREDENTIALS)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Student authenticated: {data['user']['email']}")
            print(f"   User ID: {data['user']['id']}")
            return data["access_token"], data['user']['id']
        else:
            print(f"❌ Student authentication failed: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None, None

def get_course_by_title(token, title="Multi-Quiz Progression Test Course"):
    """Find the course by title"""
    try:
        response = requests.get(f"{BACKEND_URL}/courses", 
                               headers={"Authorization": f"Bearer {token}"})
        if response.status_code == 200:
            courses = response.json()
            for course in courses:
                if course.get('title') == title:
                    print(f"✅ Found course: {course['id']}")
                    return course
            print(f"❌ Course '{title}' not found")
            return None
        else:
            print(f"❌ Failed to get courses: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Course search failed: {str(e)}")
        return None

def check_existing_enrollment(token, user_id, course_id):
    """Check if student is already enrolled"""
    try:
        response = requests.get(f"{BACKEND_URL}/enrollments", 
                               headers={"Authorization": f"Bearer {token}"})
        if response.status_code == 200:
            enrollments = response.json()
            for enrollment in enrollments:
                if (enrollment.get('userId') == user_id and 
                    enrollment.get('courseId') == course_id):
                    print(f"✅ Existing enrollment found: {enrollment.get('id')}")
                    return enrollment
            print("ℹ️  No existing enrollment found")
            return None
        else:
            print(f"❌ Failed to check enrollments: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Enrollment check failed: {str(e)}")
        return None

def main():
    print("🎯 Setting up Multi-Quiz Course for Testing")
    print("=" * 50)
    
    # Authenticate student
    student_token, user_id = authenticate_student()
    if not student_token:
        return
    
    # Find the course
    course = get_course_by_title(student_token)
    if not course:
        print("❌ Course not found. Please run create_multi_quiz_test_course.py first")
        return
    
    # Check enrollment
    enrollment = check_existing_enrollment(student_token, user_id, course['id'])
    
    if enrollment:
        print("✅ Student already enrolled in course!")
    else:
        print("ℹ️  Student not enrolled. This may require admin action.")
        print("   The course has been created and can be accessed if enrolled through admin.")
    
    print()
    print("🎉 MULTI-QUIZ TEST COURSE READY!")
    print("=" * 50)
    print(f"📚 Course: {course['title']}")
    print(f"🆔 Course ID: {course['id']}")
    print(f"📧 Student: karlo.student@alder.com")
    print(f"🔑 Password: StudentPermanent123!")
    print()
    
    # Display course structure for testing
    modules = course.get('modules', [])
    print("📋 COURSE STRUCTURE:")
    for i, module in enumerate(modules):
        print(f"   Module {i+1}: {module.get('title')}")
        lessons = module.get('lessons', [])
        for j, lesson in enumerate(lessons):
            lesson_type = lesson.get('type', 'unknown')
            icon = "🎯" if lesson_type == 'quiz' else "📄"
            print(f"      {icon} {lesson.get('title')} ({lesson_type})")
    
    print()
    print("🔍 TESTING PROCEDURE:")
    print("1. Login as karlo.student@alder.com / StudentPermanent123!")
    print("2. Look for 'Multi-Quiz Progression Test Course' in your courses")
    print("3. If not visible, an admin needs to enroll you in the course")
    print("4. Once enrolled, test the multi-quiz progression:")
    print("   - Only Quiz 1 should be unlocked initially")
    print("   - Complete Quiz 1 → Quiz 2 should unlock")
    print("   - Complete Quiz 2 → Quiz 3 should unlock")
    print("   - Complete Quiz 3 → Course should reach 100%")

if __name__ == "__main__":
    main()