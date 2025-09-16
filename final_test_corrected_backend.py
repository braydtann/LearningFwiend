#!/usr/bin/env python3
"""
Corrected Backend Test for Final Test Creation
Testing with proper question format based on validation errors
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://lms-chronology.emergent.host/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

def test_final_test_with_corrected_questions():
    """Test final test creation with corrected question format"""
    session = requests.Session()
    
    # Authenticate
    print("🔐 Authenticating...")
    auth_response = session.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
    
    if auth_response.status_code != 200:
        print(f"❌ Authentication failed: {auth_response.status_code}")
        return
    
    token = auth_response.json()['access_token']
    session.headers.update({'Authorization': f'Bearer {token}'})
    print("✅ Authentication successful")
    
    # Create program
    print("\n📚 Creating test program...")
    program_data = {
        "title": f"Corrected Test Program {datetime.now().strftime('%H%M%S')}",
        "description": "Test program with corrected question format",
        "courseIds": [],
        "nestedProgramIds": []
    }
    
    program_response = session.post(f"{BACKEND_URL}/programs", json=program_data)
    if program_response.status_code != 200:
        print(f"❌ Program creation failed: {program_response.status_code}")
        return
    
    program_id = program_response.json()['id']
    print(f"✅ Program created: {program_id}")
    
    # Test final test with corrected question format
    print("\n🎯 Testing final test with corrected questions...")
    final_test_data = {
        "title": f"Corrected Questions Test {datetime.now().strftime('%H%M%S')}",
        "description": "Testing with corrected question format",
        "programId": program_id,
        "questions": [
            {
                "type": "multiple_choice",  # Corrected from "multiple-choice"
                "question": "What is the primary purpose of a Learning Management System?",
                "options": [
                    "To manage student data",
                    "To deliver educational content and track progress",
                    "To create course schedules",
                    "To handle financial transactions"
                ],
                "correctAnswer": "1",  # Corrected to string
                "points": 10,
                "explanation": "LMS systems are designed to deliver educational content and track student progress."
            },
            {
                "type": "true_false",  # Corrected from "true-false"
                "question": "Final tests can be created without any questions initially.",
                "correctAnswer": "true",  # Corrected to string
                "points": 5,
                "explanation": "Yes, final tests can be created with empty questions array and questions added later."
            }
        ],
        "timeLimit": 45,
        "maxAttempts": 3,
        "passingScore": 80.0,
        "shuffleQuestions": True,
        "showResults": True,
        "isPublished": True
    }
    
    test_response = session.post(f"{BACKEND_URL}/final-tests", json=final_test_data)
    
    if test_response.status_code == 200:
        final_test = test_response.json()
        print(f"✅ Final test created successfully!")
        print(f"   Test ID: {final_test['id']}")
        print(f"   Questions: {final_test['questionCount']}")
        print(f"   Total Points: {final_test['totalPoints']}")
        print(f"   Published: {final_test['isPublished']}")
        
        # Test retrieval
        print("\n📋 Testing final test retrieval...")
        get_response = session.get(f"{BACKEND_URL}/final-tests/{final_test['id']}")
        
        if get_response.status_code == 200:
            retrieved_test = get_response.json()
            print(f"✅ Final test retrieved successfully!")
            print(f"   Questions in retrieved test: {len(retrieved_test['questions'])}")
            
            # Show question details
            for i, q in enumerate(retrieved_test['questions']):
                print(f"   Question {i+1}: {q['type']} - {q['points']} points")
        else:
            print(f"❌ Failed to retrieve test: {get_response.status_code}")
            
    elif test_response.status_code == 422:
        error_detail = test_response.json().get('detail', 'Unknown validation error')
        print(f"❌ 422 Validation Error still occurring:")
        print(f"   {error_detail}")
    else:
        print(f"❌ Final test creation failed: {test_response.status_code}")
        print(f"   Response: {test_response.text}")

if __name__ == "__main__":
    print("🚀 Testing Final Test Creation with Corrected Question Format")
    print("=" * 70)
    test_final_test_with_corrected_questions()