#!/usr/bin/env python3
"""
Debug Multiple Choice Scoring Test
==================================

This test debugs the scoring issue by examining the exact data structures.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://test-grading-fix.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

def authenticate():
    """Authenticate and return tokens"""
    try:
        # Admin auth
        response = requests.post(f"{API_BASE}/auth/login", json=ADMIN_CREDENTIALS)
        if response.status_code != 200:
            print(f"❌ Admin auth failed: {response.status_code}")
            return None, None
        admin_token = response.json()['access_token']
        
        # Student auth
        response = requests.post(f"{API_BASE}/auth/login", json=STUDENT_CREDENTIALS)
        if response.status_code != 200:
            print(f"❌ Student auth failed: {response.status_code}")
            return None, None
        student_token = response.json()['access_token']
        
        print("✅ Authentication successful")
        return admin_token, student_token
    except Exception as e:
        print(f"❌ Auth exception: {e}")
        return None, None

def create_debug_test(admin_token):
    """Create a simple test for debugging"""
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get or create program
        response = requests.get(f"{API_BASE}/programs", headers=headers)
        programs = response.json() if response.status_code == 200 else []
        
        if programs:
            program_id = programs[0]['id']
        else:
            # Create program
            program_data = {
                "title": "Debug Test Program",
                "description": "Debug program",
                "courseIds": [],
                "nestedProgramIds": []
            }
            response = requests.post(f"{API_BASE}/programs", json=program_data, headers=headers)
            if response.status_code != 200:
                print(f"❌ Program creation failed: {response.status_code}")
                return None
            program_id = response.json()['id']
        
        # Create simple test
        test_data = {
            "title": f"Debug Test - {datetime.now().strftime('%H%M%S')}",
            "description": "Debug test for scoring",
            "programId": program_id,
            "timeLimit": 5,
            "passingScore": 50,
            "isPublished": True,
            "questions": [
                {
                    "type": "multiple_choice",
                    "question": "What is 2 + 2?",
                    "options": ["3", "4", "5", "6"],
                    "correctAnswer": "1",  # Index 1 = "4"
                    "points": 50,
                    "explanation": "2 + 2 = 4"
                },
                {
                    "type": "true_false",
                    "question": "The sky is blue.",
                    "options": ["True", "False"],
                    "correctAnswer": "0",  # Index 0 = "True"
                    "points": 50,
                    "explanation": "The sky is blue"
                }
            ]
        }
        
        response = requests.post(f"{API_BASE}/final-tests", json=test_data, headers=headers)
        if response.status_code == 200:
            test_id = response.json()['id']
            print(f"✅ Created test: {test_id}")
            return test_id, program_id
        else:
            print(f"❌ Test creation failed: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Test creation exception: {e}")
        return None, None

def examine_test_structure(test_id, student_token):
    """Examine the test structure as seen by student"""
    try:
        headers = {"Authorization": f"Bearer {student_token}"}
        
        response = requests.get(f"{API_BASE}/final-tests/{test_id}", headers=headers)
        if response.status_code == 200:
            test_data = response.json()
            print("\n🔍 TEST STRUCTURE (Student View):")
            print(f"   Title: {test_data.get('title')}")
            print(f"   Total Points: {test_data.get('totalPoints')}")
            print(f"   Questions Count: {len(test_data.get('questions', []))}")
            
            for i, question in enumerate(test_data.get('questions', [])):
                print(f"\n   Question {i+1}:")
                print(f"     ID: {question.get('id')}")
                print(f"     Type: {question.get('type')}")
                print(f"     Question: {question.get('question')}")
                print(f"     Options: {question.get('options')}")
                print(f"     Points: {question.get('points')}")
                print(f"     Has correctAnswer: {'correctAnswer' in question}")
                if 'correctAnswer' in question:
                    print(f"     ⚠️ SECURITY ISSUE: correctAnswer visible to student: {question.get('correctAnswer')}")
            
            return test_data
        else:
            print(f"❌ Failed to get test structure: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Test structure exception: {e}")
        return None

def examine_test_structure_admin(test_id, admin_token):
    """Examine the test structure as seen by admin"""
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = requests.get(f"{API_BASE}/final-tests/{test_id}", headers=headers)
        if response.status_code == 200:
            test_data = response.json()
            print("\n🔍 TEST STRUCTURE (Admin View):")
            print(f"   Title: {test_data.get('title')}")
            print(f"   Total Points: {test_data.get('totalPoints')}")
            print(f"   Questions Count: {len(test_data.get('questions', []))}")
            
            for i, question in enumerate(test_data.get('questions', [])):
                print(f"\n   Question {i+1}:")
                print(f"     ID: {question.get('id')}")
                print(f"     Type: {question.get('type')}")
                print(f"     Question: {question.get('question')}")
                print(f"     Options: {question.get('options')}")
                print(f"     Points: {question.get('points')}")
                print(f"     Correct Answer: {question.get('correctAnswer')}")
            
            return test_data
        else:
            print(f"❌ Failed to get admin test structure: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Admin test structure exception: {e}")
        return None

def submit_debug_attempt(test_id, program_id, student_token, test_data):
    """Submit a debug attempt with detailed logging"""
    try:
        headers = {"Authorization": f"Bearer {student_token}"}
        
        # Get question IDs from the test data
        questions = test_data.get('questions', [])
        if not questions:
            print("❌ No questions found in test data")
            return None
        
        # Create answers using actual question IDs
        answers = []
        for i, question in enumerate(questions):
            question_id = question.get('id')
            if question['type'] == 'multiple_choice':
                # Submit correct answer (index 1 = "4")
                answers.append({"questionId": question_id, "answer": "1"})
            elif question['type'] == 'true_false':
                # Submit correct answer (index 0 = "True")
                answers.append({"questionId": question_id, "answer": "0"})
        
        print(f"\n🎯 SUBMITTING ATTEMPT:")
        print(f"   Test ID: {test_id}")
        print(f"   Program ID: {program_id}")
        print(f"   Answers:")
        for answer in answers:
            print(f"     Question ID: {answer['questionId']}, Answer: {answer['answer']}")
        
        attempt_data = {
            "testId": test_id,
            "programId": program_id,
            "answers": answers
        }
        
        response = requests.post(f"{API_BASE}/final-test-attempts", json=attempt_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ ATTEMPT SUBMITTED SUCCESSFULLY:")
            print(f"   Score: {result.get('score')}")
            print(f"   Percentage: {result.get('percentage')}")
            print(f"   Passed: {result.get('passed')}")
            print(f"   Total Points: {result.get('totalPoints')}")
            
            return result
        else:
            print(f"❌ Attempt submission failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Attempt submission exception: {e}")
        return None

def main():
    """Main debug execution"""
    print("🔍 DEBUG: Multiple Choice Scoring Issue Investigation")
    print("=" * 60)
    
    admin_token, student_token = authenticate()
    if not admin_token or not student_token:
        return
    
    test_id, program_id = create_debug_test(admin_token)
    if not test_id:
        return
    
    # Examine test structure from both perspectives
    admin_test_data = examine_test_structure_admin(test_id, admin_token)
    student_test_data = examine_test_structure(test_id, student_token)
    
    if not student_test_data:
        return
    
    # Submit attempt and analyze results
    result = submit_debug_attempt(test_id, program_id, student_token, student_test_data)
    
    if result:
        score = result.get('score', 0)
        if score == 0:
            print("\n🚨 CRITICAL ISSUE CONFIRMED:")
            print("   Student is getting 0% score for correct answers!")
            print("   This indicates the Multiple Choice scoring fix is NOT working.")
        else:
            print("\n✅ SCORING IS WORKING:")
            print("   Student received non-zero score for correct answers.")
    
    print("\n" + "=" * 60)
    print("🔍 DEBUG COMPLETE")

if __name__ == "__main__":
    main()