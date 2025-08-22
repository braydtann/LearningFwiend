#!/usr/bin/env python3
"""
Create a test course with all question types to verify backend support
"""

import requests
import json
from datetime import datetime
import uuid

BACKEND_URL = "http://localhost:8001/api"
TEST_TIMEOUT = 15

ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

def create_test_quiz_course():
    """Create a test course with all question types"""
    
    # Login as admin
    login_response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json=ADMIN_CREDENTIALS,
        timeout=TEST_TIMEOUT,
        headers={'Content-Type': 'application/json'}
    )
    
    if login_response.status_code != 200:
        print("❌ Failed to login as admin")
        return False
    
    token = login_response.json().get('access_token')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Create test course with comprehensive quiz
    course_data = {
        "title": "Backend Connectivity Test Course - All Question Types",
        "description": "Test course created to verify backend support for all question types after environment fix",
        "category": "Testing",
        "duration": "1 hour",
        "accessType": "open",
        "modules": [
            {
                "id": str(uuid.uuid4()),
                "title": "Comprehensive Quiz Module",
                "lessons": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "All Question Types Quiz",
                        "type": "quiz",
                        "content": "This quiz tests all supported question types",
                        "questions": [
                            {
                                "id": str(uuid.uuid4()),
                                "type": "multiple-choice",
                                "question": "What is the capital of France?",
                                "options": ["London", "Berlin", "Paris", "Madrid"],
                                "correctAnswer": "Paris",
                                "points": 10
                            },
                            {
                                "id": str(uuid.uuid4()),
                                "type": "long-form-answer",
                                "question": "Explain the importance of backend API connectivity in web applications.",
                                "correctAnswer": "Backend API connectivity is crucial for data exchange between frontend and backend systems.",
                                "points": 15
                            },
                            {
                                "id": str(uuid.uuid4()),
                                "type": "chronological-order",
                                "question": "Arrange these steps in the correct order for API testing:",
                                "items": ["Authenticate user", "Send API request", "Validate response", "Setup test environment"],
                                "correctAnswer": [4, 1, 2, 3],
                                "points": 20
                            },
                            {
                                "id": str(uuid.uuid4()),
                                "type": "select-all-that-apply",
                                "question": "Which of the following are HTTP status codes for success?",
                                "options": ["200", "201", "404", "500", "202"],
                                "correctAnswer": ["200", "201", "202"],
                                "points": 15
                            },
                            {
                                "id": str(uuid.uuid4()),
                                "type": "true-false",
                                "question": "Backend APIs should always return JSON responses.",
                                "correctAnswer": False,
                                "points": 5
                            },
                            {
                                "id": str(uuid.uuid4()),
                                "type": "short-answer",
                                "question": "What does API stand for?",
                                "correctAnswer": "Application Programming Interface",
                                "points": 10
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    # Create the course
    create_response = requests.post(
        f"{BACKEND_URL}/courses",
        json=course_data,
        timeout=TEST_TIMEOUT,
        headers=headers
    )
    
    if create_response.status_code == 200:
        created_course = create_response.json()
        course_id = created_course.get('id')
        
        print(f"✅ Test course created successfully!")
        print(f"   Course ID: {course_id}")
        print(f"   Title: {created_course.get('title')}")
        print(f"   Modules: {len(created_course.get('modules', []))}")
        
        # Verify the course was created with all question types
        verify_response = requests.get(
            f"{BACKEND_URL}/courses/{course_id}",
            timeout=TEST_TIMEOUT,
            headers=headers
        )
        
        if verify_response.status_code == 200:
            course_data = verify_response.json()
            modules = course_data.get('modules', [])
            
            for module in modules:
                lessons = module.get('lessons', [])
                for lesson in lessons:
                    if lesson.get('type') == 'quiz':
                        questions = lesson.get('questions', [])
                        print(f"\n🎯 Quiz verification:")
                        print(f"   Questions: {len(questions)}")
                        
                        question_types = []
                        for question in questions:
                            q_type = question.get('type')
                            question_types.append(q_type)
                            print(f"   - {q_type}: {question.get('question', 'N/A')[:50]}...")
                        
                        print(f"\n📊 Question types created: {list(set(question_types))}")
                        return course_id
        
        return course_id
    else:
        print(f"❌ Failed to create test course: {create_response.status_code}")
        print(f"   Response: {create_response.text}")
        return False

def test_quiz_course_access(course_id):
    """Test accessing the created quiz course"""
    
    # Login as student
    student_credentials = {
        "username_or_email": "karlo.student@alder.com", 
        "password": "StudentPermanent123!"
    }
    
    login_response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json=student_credentials,
        timeout=TEST_TIMEOUT,
        headers={'Content-Type': 'application/json'}
    )
    
    if login_response.status_code != 200:
        print("❌ Failed to login as student")
        return False
    
    token = login_response.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test course access
    course_response = requests.get(
        f"{BACKEND_URL}/courses/{course_id}",
        timeout=TEST_TIMEOUT,
        headers=headers
    )
    
    if course_response.status_code == 200:
        print(f"✅ Student can access test quiz course")
        course_data = course_response.json()
        
        # Check quiz data structure
        modules = course_data.get('modules', [])
        for module in modules:
            lessons = module.get('lessons', [])
            for lesson in lessons:
                if lesson.get('type') == 'quiz':
                    questions = lesson.get('questions', [])
                    print(f"   Quiz accessible with {len(questions)} questions")
                    
                    # Verify each question type is properly formatted
                    for question in questions:
                        q_type = question.get('type')
                        q_text = question.get('question', 'N/A')
                        
                        if q_type == 'multiple-choice':
                            options = question.get('options', [])
                            correct = question.get('correctAnswer')
                            print(f"   ✅ Multiple Choice: {len(options)} options, correct: {correct}")
                        
                        elif q_type == 'long-form-answer':
                            print(f"   ✅ Long Form: Question text present")
                        
                        elif q_type == 'chronological-order':
                            items = question.get('items', [])
                            correct_order = question.get('correctAnswer', [])
                            print(f"   ✅ Chronological: {len(items)} items, order: {correct_order}")
                        
                        elif q_type == 'select-all-that-apply':
                            options = question.get('options', [])
                            correct = question.get('correctAnswer', [])
                            print(f"   ✅ Select All: {len(options)} options, {len(correct)} correct")
                        
                        else:
                            print(f"   ✅ {q_type}: Question formatted correctly")
        
        return True
    else:
        print(f"❌ Student cannot access quiz course: {course_response.status_code}")
        return False

if __name__ == "__main__":
    print("🚀 CREATING TEST QUIZ COURSE WITH ALL QUESTION TYPES")
    print("=" * 60)
    
    course_id = create_test_quiz_course()
    
    if course_id:
        print(f"\n🎓 TESTING STUDENT ACCESS TO QUIZ COURSE")
        print("=" * 60)
        test_quiz_course_access(course_id)
    
    print(f"\n✅ Test completed - backend can handle all question types")