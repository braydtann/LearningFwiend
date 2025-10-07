#!/usr/bin/env python3
"""
Debug Course Structure - Examine the Sequential Quiz Progression Test Course
"""

import requests
import json

# Configuration
BACKEND_URL = "https://lms-progression-1.preview.emergentagent.com/api"
TARGET_COURSE_ID = "1234d28b-5336-40bc-a605-6685564bb15c"

# Admin credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

def main():
    session = requests.Session()
    
    # Authenticate as admin
    auth_response = session.post(
        f"{BACKEND_URL}/auth/login",
        json=ADMIN_CREDENTIALS,
        headers={"Content-Type": "application/json"}
    )
    
    if auth_response.status_code != 200:
        print(f"Authentication failed: {auth_response.status_code}")
        return
    
    token = auth_response.json()["access_token"]
    session.headers.update({"Authorization": f"Bearer {token}"})
    
    # Get course structure
    course_response = session.get(f"{BACKEND_URL}/courses/{TARGET_COURSE_ID}")
    
    if course_response.status_code != 200:
        print(f"Course fetch failed: {course_response.status_code}")
        return
    
    course = course_response.json()
    
    print("COURSE STRUCTURE ANALYSIS")
    print("=" * 50)
    print(f"Course Title: {course.get('title')}")
    print(f"Course ID: {course.get('id')}")
    print(f"Modules: {len(course.get('modules', []))}")
    print()
    
    for i, module in enumerate(course.get("modules", [])):
        print(f"MODULE {i+1}: {module.get('title')}")
        print(f"  Module ID: {module.get('id')}")
        print(f"  Lessons: {len(module.get('lessons', []))}")
        
        for j, lesson in enumerate(module.get("lessons", [])):
            print(f"    LESSON {j+1}: {lesson.get('title')}")
            print(f"      Lesson ID: {lesson.get('id')}")
            print(f"      Type: {lesson.get('type')}")
            
            if lesson.get("type") == "quiz":
                quiz_data = lesson.get("quiz")
                if quiz_data:
                    print(f"      Quiz ID: {quiz_data.get('id')}")
                    print(f"      Questions: {len(quiz_data.get('questions', []))}")
                    
                    # Show first question structure
                    questions = quiz_data.get("questions", [])
                    if questions:
                        first_q = questions[0]
                        print(f"      First Question:")
                        print(f"        ID: {first_q.get('id')}")
                        print(f"        Type: {first_q.get('type')}")
                        print(f"        Question: {first_q.get('question')[:50]}...")
                        print(f"        Correct Answer: {first_q.get('correctAnswer')} (type: {type(first_q.get('correctAnswer'))})")
                else:
                    print(f"      ERROR: Quiz lesson has no quiz data!")
            print()

if __name__ == "__main__":
    main()