#!/usr/bin/env python3
"""
CRITICAL FINAL EXAM SCORING INVESTIGATION - Backend Test
=======================================================

ISSUE: Students are getting 0% scores on final exams regardless of correct answers.

INVESTIGATION AREAS:
1. Final Test Creation & Data Structure
2. Answer Submission Format  
3. Scoring Logic (lines 4529-4580 in server.py)
4. Question ID matching between submitted answers and stored questions

Test Credentials:
- Admin: brayden.t@covesmart.com / Hawaii2020!
- Student: karlo.student@alder.com / StudentPermanent123!
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://lms-progression-1.preview.emergentagent.com/api"

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
    """Authenticate user and return token"""
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json=credentials)
        if response.status_code == 200:
            data = response.json()
            return data['access_token'], data['user']
        else:
            print(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None, None

def create_test_program(token):
    """Create a test program for final exam"""
    headers = {"Authorization": f"Bearer {token}"}
    
    program_data = {
        "title": "Final Exam Scoring Test Program",
        "description": "Program to test final exam scoring logic",
        "duration": "2 weeks",
        "courseIds": [],
        "nestedProgramIds": []
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/programs", json=program_data, headers=headers)
        if response.status_code == 200:
            program = response.json()
            print(f"✅ Created test program: {program['id']}")
            return program
        else:
            print(f"❌ Program creation failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Program creation error: {str(e)}")
        return None

def create_final_test_with_debug_questions(token, program_id):
    """Create final test with specific questions to debug scoring"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create test with 2 simple questions
    final_test_data = {
        "title": "Scoring Debug Final Test",
        "description": "Test to debug final exam scoring issues",
        "programId": program_id,
        "passingScore": 75.0,
        "timeLimit": 30,
        "maxAttempts": 5,
        "isPublished": True,
        "questions": [
            {
                "id": "q1_multiple_choice",
                "type": "multiple_choice",
                "question": "What is 2 + 2?",
                "options": ["2", "3", "4", "5"],
                "correctAnswer": "2",  # Index 2 = "4"
                "points": 10,
                "explanation": "2 + 2 = 4"
            },
            {
                "id": "q2_true_false", 
                "type": "true_false",
                "question": "The sky is blue.",
                "options": ["True", "False"],
                "correctAnswer": "true",  # Should be "true"
                "points": 10,
                "explanation": "The sky appears blue due to light scattering"
            }
        ]
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/final-tests", json=final_test_data, headers=headers)
        if response.status_code == 200:
            test = response.json()
            print(f"✅ Created final test: {test['id']}")
            print(f"   - Total Points: {test.get('totalPoints', 'N/A')}")
            print(f"   - Question Count: {len(test.get('questions', []))}")
            
            # Debug: Print question details
            for i, q in enumerate(test.get('questions', [])):
                print(f"   - Q{i+1} ID: {q.get('id')}")
                print(f"     Type: {q.get('type')}")
                print(f"     Correct Answer: {q.get('correctAnswer')}")
                print(f"     Points: {q.get('points')}")
                
            return test
        else:
            print(f"❌ Final test creation failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Final test creation error: {str(e)}")
        return None

def submit_correct_answers(token, test_id, program_id):
    """Submit answers that should be 100% correct"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Submit correct answers based on the test questions
    attempt_data = {
        "testId": test_id,
        "programId": program_id,
        "answers": [
            {
                "questionId": "q1_multiple_choice",
                "answer": "2"  # Index 2 = "4" (correct answer)
            },
            {
                "questionId": "q2_true_false", 
                "answer": "true"  # Correct answer
            }
        ],
        "timeSpent": 300  # 5 minutes
    }
    
    print("\n🔍 DEBUGGING ANSWER SUBMISSION:")
    print(f"Test ID: {test_id}")
    print(f"Program ID: {program_id}")
    print("Answers being submitted:")
    for answer in attempt_data['answers']:
        print(f"  - Question ID: {answer['questionId']}")
        print(f"    Answer: {answer['answer']}")
    
    try:
        response = requests.post(f"{BACKEND_URL}/final-test-attempts", json=attempt_data, headers=headers)
        if response.status_code == 200:
            attempt = response.json()
            print(f"\n✅ Final test attempt submitted successfully!")
            print(f"   - Attempt ID: {attempt['id']}")
            print(f"   - Score: {attempt.get('score', 'N/A')}%")
            print(f"   - Points Earned: {attempt.get('pointsEarned', 'N/A')}")
            print(f"   - Total Points: {attempt.get('totalPoints', 'N/A')}")
            print(f"   - Passed: {attempt.get('isPassed', 'N/A')}")
            
            return attempt
        else:
            print(f"❌ Final test attempt failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Final test attempt error: {str(e)}")
        return None

def submit_incorrect_answers(token, test_id, program_id):
    """Submit answers that should be incorrect for comparison"""
    headers = {"Authorization": f"Bearer {token}"}
    
    attempt_data = {
        "testId": test_id,
        "programId": program_id,
        "answers": [
            {
                "questionId": "q1_multiple_choice",
                "answer": "0"  # Index 0 = "2" (incorrect)
            },
            {
                "questionId": "q2_true_false",
                "answer": "false"  # Incorrect answer
            }
        ],
        "timeSpent": 200
    }
    
    print("\n🔍 DEBUGGING INCORRECT ANSWER SUBMISSION:")
    for answer in attempt_data['answers']:
        print(f"  - Question ID: {answer['questionId']}")
        print(f"    Answer: {answer['answer']}")
    
    try:
        response = requests.post(f"{BACKEND_URL}/final-test-attempts", json=attempt_data, headers=headers)
        if response.status_code == 200:
            attempt = response.json()
            print(f"\n✅ Incorrect answers submitted successfully!")
            print(f"   - Score: {attempt.get('score', 'N/A')}%")
            print(f"   - Points Earned: {attempt.get('pointsEarned', 'N/A')}")
            print(f"   - Should be 0% if scoring works correctly")
            
            return attempt
        else:
            print(f"❌ Incorrect answer attempt failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Incorrect answer attempt error: {str(e)}")
        return None

def get_final_test_details(token, test_id):
    """Get final test details to verify data structure"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BACKEND_URL}/final-tests/{test_id}", headers=headers)
        if response.status_code == 200:
            test = response.json()
            print(f"\n🔍 FINAL TEST DATA STRUCTURE ANALYSIS:")
            print(f"   - Test ID: {test.get('id')}")
            print(f"   - Title: {test.get('title')}")
            print(f"   - Total Points: {test.get('totalPoints')}")
            print(f"   - Question Count: {len(test.get('questions', []))}")
            
            for i, question in enumerate(test.get('questions', [])):
                print(f"\n   Question {i+1}:")
                print(f"     - ID: {question.get('id')}")
                print(f"     - Type: {question.get('type')}")
                print(f"     - Question: {question.get('question', '')[:50]}...")
                print(f"     - Correct Answer: {question.get('correctAnswer')}")
                print(f"     - Points: {question.get('points')}")
                if question.get('options'):
                    print(f"     - Options: {question.get('options')}")
                    
            return test
        else:
            print(f"❌ Failed to get test details: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting test details: {str(e)}")
        return None

def get_student_attempts(token, test_id):
    """Get student's attempts for this test"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BACKEND_URL}/final-test-attempts", headers=headers)
        if response.status_code == 200:
            attempts = response.json()
            test_attempts = [a for a in attempts if a.get('testId') == test_id]
            
            print(f"\n🔍 STUDENT ATTEMPTS ANALYSIS:")
            print(f"   - Total attempts for this test: {len(test_attempts)}")
            
            for i, attempt in enumerate(test_attempts):
                print(f"\n   Attempt {i+1}:")
                print(f"     - ID: {attempt.get('id')}")
                print(f"     - Score: {attempt.get('score')}%")
                print(f"     - Points Earned: {attempt.get('pointsEarned')}")
                print(f"     - Total Points: {attempt.get('totalPoints')}")
                print(f"     - Passed: {attempt.get('isPassed')}")
                print(f"     - Submitted At: {attempt.get('submittedAt')}")
                
            return test_attempts
        else:
            print(f"❌ Failed to get attempts: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error getting attempts: {str(e)}")
        return []

def main():
    print("🚨 CRITICAL FINAL EXAM SCORING INVESTIGATION")
    print("=" * 60)
    print("Testing final exam scoring logic to identify why students get 0%")
    print()
    
    # Step 1: Authenticate as admin
    print("1️⃣ ADMIN AUTHENTICATION")
    admin_token, admin_user = authenticate_user(ADMIN_CREDENTIALS)
    if not admin_token:
        print("❌ Cannot proceed without admin authentication")
        return
    print(f"✅ Admin authenticated: {admin_user['email']}")
    
    # Step 2: Create test program
    print("\n2️⃣ CREATING TEST PROGRAM")
    program = create_test_program(admin_token)
    if not program:
        print("❌ Cannot proceed without test program")
        return
    
    # Step 3: Create final test with debug questions
    print("\n3️⃣ CREATING FINAL TEST WITH DEBUG QUESTIONS")
    test = create_final_test_with_debug_questions(admin_token, program['id'])
    if not test:
        print("❌ Cannot proceed without final test")
        return
    
    # Step 4: Verify test data structure
    print("\n4️⃣ VERIFYING TEST DATA STRUCTURE")
    test_details = get_final_test_details(admin_token, test['id'])
    
    # Step 5: Authenticate as student
    print("\n5️⃣ STUDENT AUTHENTICATION")
    student_token, student_user = authenticate_user(STUDENT_CREDENTIALS)
    if not student_token:
        print("❌ Cannot proceed without student authentication")
        return
    print(f"✅ Student authenticated: {student_user['email']}")
    
    # Step 6: Submit correct answers (should get 100%)
    print("\n6️⃣ SUBMITTING CORRECT ANSWERS (SHOULD GET 100%)")
    correct_attempt = submit_correct_answers(student_token, test['id'], program['id'])
    
    # Step 7: Submit incorrect answers (should get 0%)
    print("\n7️⃣ SUBMITTING INCORRECT ANSWERS (SHOULD GET 0%)")
    incorrect_attempt = submit_incorrect_answers(student_token, test['id'], program['id'])
    
    # Step 8: Analyze all attempts
    print("\n8️⃣ ANALYZING ALL STUDENT ATTEMPTS")
    attempts = get_student_attempts(student_token, test['id'])
    
    # Step 9: Summary and diagnosis
    print("\n" + "=" * 60)
    print("🎯 FINAL EXAM SCORING INVESTIGATION SUMMARY")
    print("=" * 60)
    
    if correct_attempt:
        correct_score = correct_attempt.get('score', 0)
        print(f"✅ Correct answers attempt: {correct_score}%")
        if correct_score == 0:
            print("🚨 CRITICAL ISSUE: Correct answers scored 0% - SCORING LOGIC BROKEN")
        elif correct_score == 100:
            print("✅ Scoring logic working correctly for correct answers")
        else:
            print(f"⚠️  Unexpected score: {correct_score}% (should be 100%)")
    
    if incorrect_attempt:
        incorrect_score = incorrect_attempt.get('score', 0)
        print(f"✅ Incorrect answers attempt: {incorrect_score}%")
        if incorrect_score == 0:
            print("✅ Scoring logic working correctly for incorrect answers")
        else:
            print(f"⚠️  Unexpected score: {incorrect_score}% (should be 0%)")
    
    print(f"\nTotal attempts analyzed: {len(attempts)}")
    
    if correct_attempt and correct_attempt.get('score', 0) == 0:
        print("\n🔍 DEBUGGING RECOMMENDATIONS:")
        print("1. Check question ID matching in answer_map")
        print("2. Verify correctAnswer format (string vs integer)")
        print("3. Check answer format in submission")
        print("4. Review scoring logic in lines 4529-4580 of server.py")
        print("5. Verify totalPoints calculation")
    
    print("\n✅ Investigation completed!")

if __name__ == "__main__":
    main()