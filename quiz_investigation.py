#!/usr/bin/env python3
"""
Deep investigation of quiz question types in the backend
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "http://localhost:8001/api"
TEST_TIMEOUT = 15

ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

def investigate_quiz_questions():
    """Investigate actual quiz question structures"""
    
    # Login as admin
    login_response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json=ADMIN_CREDENTIALS,
        timeout=TEST_TIMEOUT,
        headers={'Content-Type': 'application/json'}
    )
    
    if login_response.status_code != 200:
        print("❌ Failed to login as admin")
        return
    
    token = login_response.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Get all courses
    courses_response = requests.get(f"{BACKEND_URL}/courses", timeout=TEST_TIMEOUT, headers=headers)
    
    if courses_response.status_code != 200:
        print("❌ Failed to get courses")
        return
    
    courses = courses_response.json()
    print(f"📚 Found {len(courses)} courses")
    
    quiz_data = []
    
    for course in courses:
        course_id = course.get('id')
        course_title = course.get('title', 'Unknown')
        
        # Get detailed course data
        course_response = requests.get(f"{BACKEND_URL}/courses/{course_id}", timeout=TEST_TIMEOUT, headers=headers)
        
        if course_response.status_code == 200:
            course_data = course_response.json()
            modules = course_data.get('modules', [])
            
            for module in modules:
                lessons = module.get('lessons', [])
                for lesson in lessons:
                    lesson_type = lesson.get('type', '').lower()
                    lesson_title = lesson.get('title', '')
                    
                    if 'quiz' in lesson_type or 'quiz' in lesson_title.lower():
                        questions = lesson.get('questions', [])
                        
                        if questions:
                            print(f"\n🎯 QUIZ FOUND: {course_title} -> {lesson_title}")
                            print(f"   Course ID: {course_id}")
                            print(f"   Lesson Type: {lesson_type}")
                            print(f"   Questions: {len(questions)}")
                            
                            for i, question in enumerate(questions):
                                print(f"\n   Question {i+1}:")
                                print(f"     Type: {question.get('type', 'N/A')}")
                                print(f"     Question: {question.get('question', 'N/A')[:100]}...")
                                print(f"     Options: {len(question.get('options', []))} options")
                                print(f"     Items: {len(question.get('items', []))} items")
                                print(f"     Correct Answer: {question.get('correctAnswer', 'N/A')}")
                                
                                # Show full structure for first few questions
                                if i < 2:
                                    print(f"     Full Structure: {json.dumps(question, indent=8)}")
                            
                            quiz_data.append({
                                'course_title': course_title,
                                'course_id': course_id,
                                'lesson_title': lesson_title,
                                'lesson_type': lesson_type,
                                'questions': questions
                            })
    
    print(f"\n📊 SUMMARY: Found {len(quiz_data)} quiz lessons across all courses")
    
    # Analyze question types
    all_question_types = set()
    for quiz in quiz_data:
        for question in quiz['questions']:
            q_type = question.get('type', 'unknown')
            all_question_types.add(q_type)
    
    print(f"\n🔍 QUESTION TYPES FOUND: {list(all_question_types)}")
    
    return quiz_data

if __name__ == "__main__":
    investigate_quiz_questions()