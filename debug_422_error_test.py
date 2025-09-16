#!/usr/bin/env python3
"""
Debug 422 Error Test - Understanding the exact cause of 422 errors
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://lms-chronology.emergent.host/api"
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"

def authenticate():
    """Authenticate and get token"""
    response = requests.post(f"{BACKEND_URL}/auth/login", json={
        "username_or_email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if response.status_code == 200:
        data = response.json()
        return data["access_token"]
    else:
        print(f"Authentication failed: {response.status_code} - {response.text}")
        return None

def create_program(token):
    """Create a test program"""
    headers = {"Authorization": f"Bearer {token}"}
    program_data = {
        "title": f"Debug Test Program {datetime.now().strftime('%H%M%S')}",
        "description": "Debug program for 422 error testing",
        "courseIds": [],
        "nestedProgramIds": []
    }
    
    response = requests.post(f"{BACKEND_URL}/programs", json=program_data, headers=headers)
    
    if response.status_code == 200:
        program = response.json()
        print(f"✅ Created program: {program['id']}")
        return program["id"]
    else:
        print(f"❌ Program creation failed: {response.status_code} - {response.text}")
        return None

def test_question_formats(token, program_id):
    """Test different question formats to identify 422 causes"""
    headers = {"Authorization": f"Bearer {token}"}
    
    test_cases = [
        {
            "name": "Correct Format - multiple_choice with string correctAnswer",
            "data": {
                "title": "Test 1",
                "description": "Correct format test",
                "programId": program_id,
                "questions": [{
                    "type": "multiple_choice",
                    "question": "Test question?",
                    "options": ["A", "B", "C", "D"],
                    "correctAnswer": "1",  # string
                    "points": 10
                }],
                "timeLimit": 60,
                "maxAttempts": 2,
                "passingScore": 75.0,
                "isPublished": False
            }
        },
        {
            "name": "Wrong Format - integer correctAnswer",
            "data": {
                "title": "Test 2",
                "description": "Wrong format test - integer",
                "programId": program_id,
                "questions": [{
                    "type": "multiple_choice",
                    "question": "Test question?",
                    "options": ["A", "B", "C", "D"],
                    "correctAnswer": 1,  # integer - should cause 422
                    "points": 10
                }],
                "timeLimit": 60,
                "maxAttempts": 2,
                "passingScore": 75.0,
                "isPublished": False
            }
        },
        {
            "name": "Wrong Format - object options",
            "data": {
                "title": "Test 3",
                "description": "Wrong format test - object options",
                "programId": program_id,
                "questions": [{
                    "type": "multiple_choice",
                    "question": "Test question?",
                    "options": [{"text": "A"}, {"text": "B"}],  # objects - should cause 422
                    "correctAnswer": "1",
                    "points": 10
                }],
                "timeLimit": 60,
                "maxAttempts": 2,
                "passingScore": 75.0,
                "isPublished": False
            }
        },
        {
            "name": "Wrong Format - hyphen in type",
            "data": {
                "title": "Test 4",
                "description": "Wrong format test - hyphen type",
                "programId": program_id,
                "questions": [{
                    "type": "multiple-choice",  # hyphen - should cause 422
                    "question": "Test question?",
                    "options": ["A", "B", "C", "D"],
                    "correctAnswer": "1",
                    "points": 10
                }],
                "timeLimit": 60,
                "maxAttempts": 2,
                "passingScore": 75.0,
                "isPublished": False
            }
        },
        {
            "name": "Missing required field - no correctAnswer",
            "data": {
                "title": "Test 5",
                "description": "Missing correctAnswer",
                "programId": program_id,
                "questions": [{
                    "type": "multiple_choice",
                    "question": "Test question?",
                    "options": ["A", "B", "C", "D"],
                    # "correctAnswer": missing
                    "points": 10
                }],
                "timeLimit": 60,
                "maxAttempts": 2,
                "passingScore": 75.0,
                "isPublished": False
            }
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        
        response = requests.post(f"{BACKEND_URL}/final-tests", 
                               json=test_case['data'], 
                               headers=headers)
        
        if response.status_code == 200:
            print(f"✅ SUCCESS: {response.status_code}")
            result = response.json()
            print(f"   Created test ID: {result['id']}")
        elif response.status_code == 422:
            print(f"❌ 422 ERROR: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Error details: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"   Raw error: {response.text}")
        else:
            print(f"❌ OTHER ERROR: {response.status_code}")
            print(f"   Response: {response.text}")
        
        results.append({
            "test": test_case['name'],
            "status_code": response.status_code,
            "success": response.status_code == 200
        })
    
    return results

def main():
    print("🔍 DEBUG: 422 Error Investigation")
    print("=" * 60)
    
    # Step 1: Authenticate
    token = authenticate()
    if not token:
        return False
    
    # Step 2: Create program
    program_id = create_program(token)
    if not program_id:
        return False
    
    # Step 3: Test different formats
    results = test_question_formats(token, program_id)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['test']}: {result['status_code']}")
    
    success_count = sum(1 for r in results if r["success"])
    print(f"\n🎯 Success Rate: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    
    return True

if __name__ == "__main__":
    main()