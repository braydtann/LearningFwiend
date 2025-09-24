#!/usr/bin/env python3
"""
FRONTEND BUG REPRODUCTION TEST
Reproduce the exact 422 error by sending data the way the frontend does
"""

import requests
import json

# Configuration
BACKEND_URL = "https://test-grading-fix.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

# Student credentials
STUDENT_CREDENTIALS = {
    "username_or_email": "brayden.student@learningfwiend.com",
    "password": "Cove1234!"
}

def test_frontend_bug_reproduction():
    """Reproduce the exact bug by sending lessonId as progressData"""
    print("🐛 REPRODUCING FRONTEND BUG - SENDING LESSON ID AS PROGRESS DATA")
    print("=" * 70)
    
    # Step 1: Login as student
    try:
        login_response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=STUDENT_CREDENTIALS,
            timeout=TEST_TIMEOUT,
            headers={'Content-Type': 'application/json'}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Student login failed: {login_response.status_code}")
            return
        
        student_data = login_response.json()
        student_token = student_data.get('access_token')
        print(f"✅ Student authenticated successfully")
        
        # Step 2: Find the course 'ttttt'
        courses_response = requests.get(
            f"{BACKEND_URL}/courses",
            timeout=TEST_TIMEOUT,
            headers={'Authorization': f'Bearer {student_token}'}
        )
        
        if courses_response.status_code != 200:
            print(f"❌ Failed to get courses: {courses_response.status_code}")
            return
        
        courses = courses_response.json()
        target_course = None
        
        for course in courses:
            if course.get('title') == 'ttttt':
                target_course = course
                break
        
        if not target_course:
            print(f"❌ Course 'ttttt' not found")
            return
        
        course_id = target_course.get('id')
        print(f"✅ Found course 'ttttt': {course_id}")
        
        # Step 3: Get a lesson ID from the course
        modules = target_course.get('modules', [])
        lesson_id = None
        
        for module in modules:
            lessons = module.get('lessons', [])
            for lesson in lessons:
                lesson_id = lesson.get('id')
                break
            if lesson_id:
                break
        
        if not lesson_id:
            print(f"❌ No lesson ID found in course")
            return
        
        print(f"✅ Using lesson ID: {lesson_id}")
        
        # Step 4: Reproduce the bug - send lessonId as progressData
        print(f"\n🚨 REPRODUCING BUG: Sending lesson ID as progress data")
        print(f"   This is what happens when frontend calls:")
        print(f"   updateEnrollmentProgress(courseId, lessonId, progressData)")
        print(f"   But AuthContext expects:")
        print(f"   updateEnrollmentProgress(courseId, progressData)")
        
        # This simulates the bug - lessonId becomes progressData
        bug_response = requests.put(
            f"{BACKEND_URL}/enrollments/{course_id}/progress",
            json=lesson_id,  # This is the bug - sending string instead of object
            timeout=TEST_TIMEOUT,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {student_token}'
            }
        )
        
        print(f"\n📥 BUG REPRODUCTION RESULT:")
        print(f"   Status Code: {bug_response.status_code}")
        print(f"   Response: {bug_response.text}")
        
        if bug_response.status_code == 422:
            print(f"\n🎯 SUCCESS! Reproduced the 422 error!")
            print(f"   This confirms the frontend is sending lesson ID as progress data")
            try:
                error_data = bug_response.json()
                print(f"   Error details: {error_data.get('detail', 'Unknown error')}")
            except:
                pass
        else:
            print(f"\n⚠️ Unexpected result - expected 422 error")
        
        # Step 5: Show the correct way
        print(f"\n✅ CORRECT WAY: Sending proper progress data object")
        
        correct_data = {
            "progress": 100.0,
            "currentLessonId": lesson_id,
            "timeSpent": 180
        }
        
        correct_response = requests.put(
            f"{BACKEND_URL}/enrollments/{course_id}/progress",
            json=correct_data,
            timeout=TEST_TIMEOUT,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {student_token}'
            }
        )
        
        print(f"   Status Code: {correct_response.status_code}")
        print(f"   Response: {correct_response.text[:100]}...")
        
        if correct_response.status_code == 200:
            print(f"   ✅ Correct format works perfectly!")
        
    except Exception as e:
        print(f"❌ Error during bug reproduction: {str(e)}")

if __name__ == "__main__":
    test_frontend_bug_reproduction()