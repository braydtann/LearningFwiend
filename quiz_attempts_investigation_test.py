#!/usr/bin/env python3
"""
Quiz Attempts Investigation Test
===============================

Investigate quiz attempts storage and tracking in the system
to understand how quiz completion is tracked for multi-quiz progression.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://quiz-progress-fix.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

def authenticate_user(credentials):
    """Authenticate user"""
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json=credentials)
        
        if response.status_code == 200:
            data = response.json()
            return data["access_token"], data["user"]
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None, None

def get_headers(token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {token}"}

def investigate_quiz_attempts():
    """Investigate quiz attempts and related endpoints"""
    print("🔍 Investigating Quiz Attempts System")
    print("=" * 60)
    
    # Authenticate both users
    admin_token, admin_user = authenticate_user(ADMIN_CREDENTIALS)
    student_token, student_user = authenticate_user(STUDENT_CREDENTIALS)
    
    if not admin_token or not student_token:
        print("❌ Authentication failed")
        return
    
    print(f"✅ Admin authenticated: {admin_user['full_name']}")
    print(f"✅ Student authenticated: {student_user['full_name']}")
    print()
    
    # Test various quiz-related endpoints
    endpoints_to_test = [
        ("/quiz-attempts", "GET", student_token, "Student Quiz Attempts"),
        ("/admin/quiz-attempts", "GET", admin_token, "Admin Quiz Attempts"),
        ("/quizzes", "GET", student_token, "Available Quizzes"),
        ("/final-tests", "GET", student_token, "Available Final Tests"),
    ]
    
    for endpoint, method, token, description in endpoints_to_test:
        print(f"🔍 Testing {description}: {method} {endpoint}")
        
        try:
            if method == "GET":
                response = requests.get(f"{BACKEND_URL}{endpoint}", headers=get_headers(token))
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   Result: Found {len(data)} items")
                        if data and len(data) > 0:
                            # Show structure of first item
                            first_item = data[0]
                            if isinstance(first_item, dict):
                                keys = list(first_item.keys())
                                print(f"   Sample keys: {keys[:5]}{'...' if len(keys) > 5 else ''}")
                    elif isinstance(data, dict):
                        print(f"   Result: Dict with keys: {list(data.keys())}")
                    else:
                        print(f"   Result: {type(data)} - {str(data)[:100]}")
                except:
                    print(f"   Result: Non-JSON response")
            elif response.status_code == 404:
                print(f"   Result: Endpoint not found")
            elif response.status_code == 403:
                print(f"   Result: Access forbidden")
            else:
                print(f"   Result: Error - {response.text[:100]}")
            
        except Exception as e:
            print(f"   Error: {str(e)}")
        
        print()
    
    # Check if there are any quiz attempts in the database by looking at enrollments
    print("🔍 Checking Enrollment Progress for Quiz Completion Evidence")
    print("-" * 50)
    
    try:
        response = requests.get(f"{BACKEND_URL}/enrollments", headers=get_headers(student_token))
        
        if response.status_code == 200:
            enrollments = response.json()
            print(f"Found {len(enrollments)} enrollments for student")
            
            quiz_related_enrollments = 0
            for enrollment in enrollments:
                course_id = enrollment.get("courseId")
                progress = enrollment.get("progress", 0)
                
                # Get course details to check for quizzes
                course_response = requests.get(
                    f"{BACKEND_URL}/courses/{course_id}",
                    headers=get_headers(student_token)
                )
                
                if course_response.status_code == 200:
                    course = course_response.json()
                    course_title = course.get("title", "Unknown")
                    modules = course.get("modules", [])
                    
                    quiz_count = 0
                    for module in modules:
                        for lesson in module.get("lessons", []):
                            if lesson.get("type") == "quiz":
                                quiz_count += 1
                    
                    if quiz_count > 0:
                        quiz_related_enrollments += 1
                        print(f"  📚 '{course_title}': {quiz_count} quiz(s), progress: {progress}%")
                        
                        if progress > 0:
                            print(f"      🎯 Student has made progress - may indicate quiz attempts")
            
            print(f"\nSummary: {quiz_related_enrollments} enrollments in courses with quizzes")
            
        else:
            print(f"Failed to get enrollments: {response.status_code}")
    
    except Exception as e:
        print(f"Error checking enrollments: {str(e)}")
    
    print()
    
    # Test the quiz validation logic by checking a course with quizzes
    print("🔍 Testing Quiz Validation Logic")
    print("-" * 50)
    
    try:
        # Get a course with quizzes
        courses_response = requests.get(f"{BACKEND_URL}/courses", headers=get_headers(admin_token))
        
        if courses_response.status_code == 200:
            courses = courses_response.json()
            
            # Find a course with quizzes
            test_course = None
            for course in courses:
                course_detail_response = requests.get(
                    f"{BACKEND_URL}/courses/{course['id']}",
                    headers=get_headers(admin_token)
                )
                
                if course_detail_response.status_code == 200:
                    course_detail = course_detail_response.json()
                    modules = course_detail.get("modules", [])
                    
                    has_quiz = False
                    for module in modules:
                        for lesson in module.get("lessons", []):
                            if lesson.get("type") == "quiz":
                                has_quiz = True
                                break
                        if has_quiz:
                            break
                    
                    if has_quiz:
                        test_course = course_detail
                        break
            
            if test_course:
                course_id = test_course["id"]
                course_title = test_course.get("title", "Unknown")
                
                print(f"Testing with course: '{course_title}'")
                
                # Test progress update to 100% (should validate quiz completion)
                progress_data = {
                    "progress": 100.0,
                    "lastAccessedAt": datetime.utcnow().isoformat()
                }
                
                response = requests.put(
                    f"{BACKEND_URL}/enrollments/{course_id}/progress",
                    json=progress_data,
                    headers=get_headers(student_token)
                )
                
                print(f"100% progress update result: {response.status_code}")
                if response.status_code == 400:
                    print("✅ Quiz validation is working - completion blocked")
                    print(f"   Error message: {response.text[:200]}...")
                elif response.status_code == 200:
                    print("⚠️  Completion allowed - student may have completed quizzes")
                else:
                    print(f"❌ Unexpected response: {response.text[:100]}")
            else:
                print("No courses with quizzes found for testing")
    
    except Exception as e:
        print(f"Error testing quiz validation: {str(e)}")

if __name__ == "__main__":
    investigate_quiz_attempts()