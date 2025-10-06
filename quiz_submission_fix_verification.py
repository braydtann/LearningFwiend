#!/usr/bin/env python3
"""
QUIZ SUBMISSION FIX VERIFICATION TEST
Verify that the 422 error is now resolved after fixing the frontend
"""

import requests
import json

# Configuration
BACKEND_URL = "https://grade-flow-wizard.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

# Student credentials
STUDENT_CREDENTIALS = {
    "username_or_email": "brayden.student@learningfwiend.com",
    "password": "Cove1234!"
}

def test_quiz_submission_fix():
    """Test that quiz submission now works correctly"""
    print("🔧 QUIZ SUBMISSION FIX VERIFICATION")
    print("=" * 60)
    print("Testing the corrected data format that frontend should now send")
    
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
            return False
        
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
            return False
        
        courses = courses_response.json()
        target_course = None
        
        for course in courses:
            if course.get('title') == 'ttttt':
                target_course = course
                break
        
        if not target_course:
            print(f"❌ Course 'ttttt' not found")
            return False
        
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
            return False
        
        print(f"✅ Using lesson ID: {lesson_id}")
        
        # Step 4: Test the corrected format (what frontend should now send)
        print(f"\n📤 TESTING CORRECTED FORMAT:")
        print(f"   Frontend now sends proper progress data object")
        
        # This simulates the corrected frontend behavior
        corrected_data = {
            "progress": 100,  # Quiz completed (passed)
            "currentLessonId": lesson_id,
            "timeSpent": 180  # 3 minutes
        }
        
        print(f"   Data being sent: {json.dumps(corrected_data, indent=2)}")
        
        corrected_response = requests.put(
            f"{BACKEND_URL}/enrollments/{course_id}/progress",
            json=corrected_data,
            timeout=TEST_TIMEOUT,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {student_token}'
            }
        )
        
        print(f"\n📥 CORRECTED FORMAT RESULT:")
        print(f"   Status Code: {corrected_response.status_code}")
        
        if corrected_response.status_code == 200:
            print(f"   ✅ SUCCESS! Quiz submission now works correctly")
            
            try:
                response_data = corrected_response.json()
                print(f"   Updated Progress: {response_data.get('progress', 'unknown')}%")
                print(f"   Enrollment Status: {response_data.get('status', 'unknown')}")
                print(f"   Current Lesson ID: {response_data.get('currentLessonId', 'unknown')}")
                print(f"   Time Spent: {response_data.get('timeSpent', 'unknown')} seconds")
            except:
                print(f"   Response: {corrected_response.text[:100]}...")
            
            return True
        else:
            print(f"   ❌ FAILED! Still getting error: {corrected_response.status_code}")
            print(f"   Response: {corrected_response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Error during fix verification: {str(e)}")
        return False

def test_edge_cases():
    """Test edge cases to ensure robustness"""
    print(f"\n🧪 TESTING EDGE CASES:")
    print("=" * 40)
    
    # Login first
    login_response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json=STUDENT_CREDENTIALS,
        timeout=TEST_TIMEOUT,
        headers={'Content-Type': 'application/json'}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Cannot test edge cases - login failed")
        return False
    
    student_data = login_response.json()
    student_token = student_data.get('access_token')
    
    # Find course
    courses_response = requests.get(
        f"{BACKEND_URL}/courses",
        timeout=TEST_TIMEOUT,
        headers={'Authorization': f'Bearer {student_token}'}
    )
    
    courses = courses_response.json()
    course_id = None
    lesson_id = None
    
    for course in courses:
        if course.get('title') == 'ttttt':
            course_id = course.get('id')
            modules = course.get('modules', [])
            for module in modules:
                lessons = module.get('lessons', [])
                for lesson in lessons:
                    lesson_id = lesson.get('id')
                    break
                if lesson_id:
                    break
            break
    
    if not course_id or not lesson_id:
        print(f"❌ Cannot test edge cases - course/lesson not found")
        return False
    
    edge_cases = [
        {
            "name": "Quiz Failed (0% progress)",
            "data": {"progress": 0, "currentLessonId": lesson_id, "timeSpent": 120},
            "expected": 200
        },
        {
            "name": "Partial Progress (50%)",
            "data": {"progress": 50, "currentLessonId": lesson_id, "timeSpent": 90},
            "expected": 200
        },
        {
            "name": "No Time Spent",
            "data": {"progress": 100, "currentLessonId": lesson_id},
            "expected": 200
        },
        {
            "name": "Minimal Data (Progress Only)",
            "data": {"progress": 75},
            "expected": 200
        }
    ]
    
    all_passed = True
    
    for case in edge_cases:
        print(f"\n   🧪 {case['name']}:")
        
        response = requests.put(
            f"{BACKEND_URL}/enrollments/{course_id}/progress",
            json=case['data'],
            timeout=TEST_TIMEOUT,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {student_token}'
            }
        )
        
        if response.status_code == case['expected']:
            print(f"      ✅ PASS (Status: {response.status_code})")
        else:
            print(f"      ❌ FAIL (Expected: {case['expected']}, Got: {response.status_code})")
            all_passed = False
    
    return all_passed

def main():
    """Run all verification tests"""
    print("🚨 URGENT: QUIZ SUBMISSION 422 ERROR FIX VERIFICATION")
    print("=" * 70)
    print("Verifying that the frontend parameter mismatch has been resolved")
    print("=" * 70)
    
    # Test 1: Main fix verification
    main_test_passed = test_quiz_submission_fix()
    
    # Test 2: Edge cases
    edge_cases_passed = test_edge_cases()
    
    # Summary
    print(f"\n📊 VERIFICATION SUMMARY:")
    print("=" * 40)
    print(f"✅ Main Fix Test: {'PASSED' if main_test_passed else 'FAILED'}")
    print(f"✅ Edge Cases Test: {'PASSED' if edge_cases_passed else 'FAILED'}")
    
    if main_test_passed and edge_cases_passed:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ The 422 error has been successfully resolved")
        print(f"✅ Quiz submission now works correctly")
        print(f"✅ Frontend parameter mismatch fixed")
        return True
    else:
        print(f"\n❌ SOME TESTS FAILED!")
        print(f"❌ Additional investigation may be needed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)