#!/usr/bin/env python3
"""
Debug Final Test Creation - Investigate why correctAnswer is not being stored
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://lms-progression.preview.emergentagent.com/api"
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"

def debug_final_test_creation():
    session = requests.Session()
    
    # Step 1: Authenticate
    print("🔐 Authenticating...")
    auth_response = session.post(f"{BACKEND_URL}/auth/login", json={
        "username_or_email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if auth_response.status_code != 200:
        print(f"❌ Authentication failed: {auth_response.status_code}")
        return False
    
    token = auth_response.json()["access_token"]
    session.headers.update({"Authorization": f"Bearer {token}"})
    print("✅ Authenticated successfully")
    
    # Step 2: Create a simple program
    print("\n📚 Creating test program...")
    program_data = {
        "title": f"Debug Program {datetime.now().strftime('%H%M%S')}",
        "description": "Debug program for final test creation",
        "courseIds": [],
        "nestedProgramIds": []
    }
    
    program_response = session.post(f"{BACKEND_URL}/programs", json=program_data)
    if program_response.status_code != 200:
        print(f"❌ Program creation failed: {program_response.status_code}")
        return False
    
    program_id = program_response.json()["id"]
    print(f"✅ Program created: {program_id}")
    
    # Step 3: Create final test with explicit correctAnswer values
    print("\n📝 Creating final test with explicit correctAnswer values...")
    
    test_data = {
        "title": f"Debug Final Test {datetime.now().strftime('%H%M%S')}",
        "description": "Debug test to check correctAnswer storage",
        "programId": program_id,
        "questions": [
            {
                "type": "multiple_choice",
                "question": "What is 2 + 2?",
                "options": ["3", "4", "5", "6"],
                "correctAnswer": "1",  # Index 1 = "4"
                "points": 10,
                "explanation": "2 + 2 = 4"
            },
            {
                "type": "true_false",
                "question": "The sky is blue.",
                "correctAnswer": "true",
                "points": 10,
                "explanation": "Yes, the sky is blue"
            }
        ],
        "timeLimit": 15,
        "maxAttempts": 1,
        "passingScore": 75.0,
        "shuffleQuestions": False,
        "showResults": True,
        "isPublished": True
    }
    
    print("📤 Sending test data:")
    print(json.dumps(test_data, indent=2))
    
    test_response = session.post(f"{BACKEND_URL}/final-tests", json=test_data)
    
    if test_response.status_code != 200:
        print(f"❌ Final test creation failed: {test_response.status_code}")
        print(f"Response: {test_response.text}")
        return False
    
    test_result = test_response.json()
    test_id = test_result["id"]
    print(f"✅ Final test created: {test_id}")
    
    # Step 4: Retrieve the test to check if correctAnswer was stored
    print(f"\n🔍 Retrieving test to verify correctAnswer storage...")
    
    get_response = session.get(f"{BACKEND_URL}/final-tests/{test_id}")
    
    if get_response.status_code != 200:
        print(f"❌ Failed to retrieve test: {get_response.status_code}")
        return False
    
    retrieved_test = get_response.json()
    
    print("📥 Retrieved test structure:")
    print(json.dumps(retrieved_test, indent=2, default=str))
    
    # Step 5: Analyze the questions
    print(f"\n🔬 ANALYSIS:")
    questions = retrieved_test.get("questions", [])
    
    for i, question in enumerate(questions):
        print(f"\nQuestion {i+1}:")
        print(f"  Type: {question.get('type')}")
        print(f"  Question: {question.get('question')}")
        print(f"  Correct Answer: {question.get('correctAnswer')}")
        print(f"  Points: {question.get('points')}")
        
        if question.get('correctAnswer') is None:
            print(f"  🚨 ISSUE: correctAnswer is None!")
        else:
            print(f"  ✅ correctAnswer is present: {question.get('correctAnswer')}")
    
    # Step 6: Test submission to see scoring
    print(f"\n🎯 Testing submission and scoring...")
    
    # Switch to student account
    student_auth = session.post(f"{BACKEND_URL}/auth/login", json={
        "username_or_email": "karlo.student@alder.com",
        "password": "StudentPermanent123!"
    })
    
    if student_auth.status_code != 200:
        print(f"❌ Student authentication failed: {student_auth.status_code}")
        return False
    
    student_token = student_auth.json()["access_token"]
    session.headers.update({"Authorization": f"Bearer {student_token}"})
    
    # Submit correct answers
    answers = []
    for question in questions:
        answers.append({
            "questionId": question["id"],
            "answer": question.get("correctAnswer")  # Use the stored correct answer
        })
    
    submission_data = {
        "testId": test_id,
        "answers": answers,
        "timeSpent": 60
    }
    
    print("📤 Submitting answers:")
    print(json.dumps(submission_data, indent=2))
    
    submission_response = session.post(f"{BACKEND_URL}/final-test-attempts", json=submission_data)
    
    if submission_response.status_code != 200:
        print(f"❌ Submission failed: {submission_response.status_code}")
        print(f"Response: {submission_response.text}")
        return False
    
    attempt_result = submission_response.json()
    
    print(f"\n📊 SUBMISSION RESULT:")
    print(f"Score: {attempt_result.get('score')}%")
    print(f"Points Earned: {attempt_result.get('pointsEarned')}")
    print(f"Total Points: {attempt_result.get('totalPoints')}")
    print(f"Passed: {attempt_result.get('isPassed')}")
    
    if attempt_result.get('score', 0) > 0:
        print("✅ SUCCESS: Scoring is working correctly!")
        return True
    else:
        print("❌ FAILURE: Still getting 0% score")
        return False

if __name__ == "__main__":
    success = debug_final_test_creation()
    sys.exit(0 if success else 1)