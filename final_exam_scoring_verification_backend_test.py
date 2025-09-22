#!/usr/bin/env python3
"""
FINAL EXAM SCORING VERIFICATION - Backend Test
==============================================

VERIFICATION: After fixing QuestionResponse model to include correctAnswer field,
test that final exam scoring now works correctly.

Test Credentials:
- Admin: brayden.t@covesmart.com / Hawaii2020!
- Student: karlo.student@alder.com / StudentPermanent123!
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://lms-bug-fixes.preview.emergentagent.com/api"

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

def create_comprehensive_final_test(token):
    """Create a comprehensive final test with multiple question types"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # First create a program
    program_data = {
        "title": "Final Exam Scoring Verification Program",
        "description": "Program to verify final exam scoring works correctly",
        "duration": "2 weeks",
        "courseIds": [],
        "nestedProgramIds": []
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/programs", json=program_data, headers=headers)
        if response.status_code == 200:
            program = response.json()
            print(f"✅ Created test program: {program['id']}")
        else:
            print(f"❌ Program creation failed: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Program creation error: {str(e)}")
        return None, None
    
    # Create comprehensive final test
    final_test_data = {
        "title": "Comprehensive Scoring Verification Test",
        "description": "Test with multiple question types to verify scoring",
        "programId": program['id'],
        "passingScore": 75.0,
        "timeLimit": 45,
        "maxAttempts": 3,
        "isPublished": True,
        "questions": [
            {
                "type": "multiple_choice",
                "question": "What is the capital of France?",
                "options": ["London", "Berlin", "Paris", "Madrid"],
                "correctAnswer": "2",  # Index 2 = "Paris"
                "points": 10,
                "explanation": "Paris is the capital of France"
            },
            {
                "type": "true_false",
                "question": "Python is a programming language.",
                "options": ["True", "False"],
                "correctAnswer": "true",
                "points": 10,
                "explanation": "Python is indeed a programming language"
            },
            {
                "type": "short_answer",
                "question": "What does HTML stand for?",
                "options": [],
                "correctAnswer": "hypertext markup language",
                "points": 15,
                "explanation": "HTML stands for HyperText Markup Language"
            }
        ]
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/final-tests", json=final_test_data, headers=headers)
        if response.status_code == 200:
            test = response.json()
            print(f"✅ Created comprehensive final test: {test['id']}")
            print(f"   - Total Points: {test.get('totalPoints', 'N/A')}")
            print(f"   - Question Count: {len(test.get('questions', []))}")
            return program, test
        else:
            print(f"❌ Final test creation failed: {response.status_code} - {response.text}")
            return program, None
    except Exception as e:
        print(f"❌ Final test creation error: {str(e)}")
        return program, None

def verify_question_data_structure(token, test_id):
    """Verify that correctAnswer field is now present in API response"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BACKEND_URL}/final-tests/{test_id}", headers=headers)
        if response.status_code == 200:
            test = response.json()
            print(f"\n🔍 QUESTION DATA STRUCTURE VERIFICATION:")
            print(f"   - Test ID: {test.get('id')}")
            
            all_correct_answers_present = True
            
            for i, question in enumerate(test.get('questions', [])):
                print(f"\n   Question {i+1}:")
                print(f"     - ID: {question.get('id')}")
                print(f"     - Type: {question.get('type')}")
                print(f"     - Question: {question.get('question', '')[:50]}...")
                print(f"     - Correct Answer: {question.get('correctAnswer')}")
                print(f"     - Points: {question.get('points')}")
                
                if question.get('correctAnswer') is None:
                    print(f"     ❌ CRITICAL: correctAnswer is still None!")
                    all_correct_answers_present = False
                else:
                    print(f"     ✅ correctAnswer present: '{question.get('correctAnswer')}'")
                    
            return test, all_correct_answers_present
        else:
            print(f"❌ Failed to get test data: {response.status_code}")
            return None, False
    except Exception as e:
        print(f"❌ Error checking test data: {str(e)}")
        return None, False

def submit_perfect_answers(student_token, test, program_id):
    """Submit answers that should get 100% score"""
    headers = {"Authorization": f"Bearer {student_token}"}
    
    # Get question IDs from the test
    questions = test.get('questions', [])
    if len(questions) < 3:
        print("❌ Not enough questions in test")
        return None
    
    # Submit perfect answers based on the correct answers
    attempt_data = {
        "testId": test['id'],
        "programId": program_id,
        "answers": [
            {
                "questionId": questions[0]['id'],  # Multiple choice
                "answer": "2"  # Index 2 = "Paris"
            },
            {
                "questionId": questions[1]['id'],  # True/False
                "answer": "true"  # Correct
            },
            {
                "questionId": questions[2]['id'],  # Short answer
                "answer": "hypertext markup language"  # Exact match
            }
        ],
        "timeSpent": 600  # 10 minutes
    }
    
    print(f"\n🎯 SUBMITTING PERFECT ANSWERS:")
    for i, answer in enumerate(attempt_data['answers']):
        print(f"   Q{i+1}: {answer['questionId'][:8]}... → '{answer['answer']}'")
    
    try:
        response = requests.post(f"{BACKEND_URL}/final-test-attempts", json=attempt_data, headers=headers)
        if response.status_code == 200:
            attempt = response.json()
            print(f"\n✅ Perfect answers submitted successfully!")
            print(f"   - Attempt ID: {attempt['id']}")
            print(f"   - Score: {attempt.get('score', 'N/A')}%")
            print(f"   - Points Earned: {attempt.get('pointsEarned', 'N/A')}")
            print(f"   - Total Points: {attempt.get('totalPoints', 'N/A')}")
            print(f"   - Passed: {attempt.get('isPassed', 'N/A')}")
            
            return attempt
        else:
            print(f"❌ Perfect answers attempt failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Perfect answers attempt error: {str(e)}")
        return None

def submit_partial_answers(student_token, test, program_id):
    """Submit answers that should get partial score"""
    headers = {"Authorization": f"Bearer {student_token}"}
    
    questions = test.get('questions', [])
    if len(questions) < 3:
        print("❌ Not enough questions in test")
        return None
    
    # Submit partial answers (2 correct, 1 incorrect)
    attempt_data = {
        "testId": test['id'],
        "programId": program_id,
        "answers": [
            {
                "questionId": questions[0]['id'],  # Multiple choice
                "answer": "0"  # Index 0 = "London" (INCORRECT)
            },
            {
                "questionId": questions[1]['id'],  # True/False
                "answer": "true"  # CORRECT
            },
            {
                "questionId": questions[2]['id'],  # Short answer
                "answer": "hypertext markup language"  # CORRECT
            }
        ],
        "timeSpent": 450  # 7.5 minutes
    }
    
    print(f"\n🎯 SUBMITTING PARTIAL ANSWERS (2/3 correct):")
    for i, answer in enumerate(attempt_data['answers']):
        correct_status = "❌ INCORRECT" if i == 0 else "✅ CORRECT"
        print(f"   Q{i+1}: {answer['questionId'][:8]}... → '{answer['answer']}' {correct_status}")
    
    try:
        response = requests.post(f"{BACKEND_URL}/final-test-attempts", json=attempt_data, headers=headers)
        if response.status_code == 200:
            attempt = response.json()
            print(f"\n✅ Partial answers submitted successfully!")
            print(f"   - Score: {attempt.get('score', 'N/A')}%")
            print(f"   - Points Earned: {attempt.get('pointsEarned', 'N/A')}")
            print(f"   - Expected: 25/35 points = 71.4%")
            
            return attempt
        else:
            print(f"❌ Partial answers attempt failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Partial answers attempt error: {str(e)}")
        return None

def submit_all_wrong_answers(student_token, test, program_id):
    """Submit answers that should get 0% score"""
    headers = {"Authorization": f"Bearer {student_token}"}
    
    questions = test.get('questions', [])
    if len(questions) < 3:
        print("❌ Not enough questions in test")
        return None
    
    # Submit all wrong answers
    attempt_data = {
        "testId": test['id'],
        "programId": program_id,
        "answers": [
            {
                "questionId": questions[0]['id'],  # Multiple choice
                "answer": "1"  # Index 1 = "Berlin" (INCORRECT)
            },
            {
                "questionId": questions[1]['id'],  # True/False
                "answer": "false"  # INCORRECT
            },
            {
                "questionId": questions[2]['id'],  # Short answer
                "answer": "wrong answer"  # INCORRECT
            }
        ],
        "timeSpent": 300  # 5 minutes
    }
    
    print(f"\n🎯 SUBMITTING ALL WRONG ANSWERS:")
    for i, answer in enumerate(attempt_data['answers']):
        print(f"   Q{i+1}: {answer['questionId'][:8]}... → '{answer['answer']}' ❌ INCORRECT")
    
    try:
        response = requests.post(f"{BACKEND_URL}/final-test-attempts", json=attempt_data, headers=headers)
        if response.status_code == 200:
            attempt = response.json()
            print(f"\n✅ Wrong answers submitted successfully!")
            print(f"   - Score: {attempt.get('score', 'N/A')}%")
            print(f"   - Points Earned: {attempt.get('pointsEarned', 'N/A')}")
            print(f"   - Expected: 0/35 points = 0%")
            
            return attempt
        else:
            print(f"❌ Wrong answers attempt failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Wrong answers attempt error: {str(e)}")
        return None

def main():
    print("🔧 FINAL EXAM SCORING VERIFICATION - Backend Test")
    print("=" * 60)
    print("Verifying that final exam scoring now works correctly after fix")
    print()
    
    # Step 1: Authenticate as admin
    print("1️⃣ ADMIN AUTHENTICATION")
    admin_token, admin_user = authenticate_user(ADMIN_CREDENTIALS)
    if not admin_token:
        print("❌ Cannot proceed without admin authentication")
        return
    print(f"✅ Admin authenticated: {admin_user['email']}")
    
    # Step 2: Create comprehensive final test
    print("\n2️⃣ CREATING COMPREHENSIVE FINAL TEST")
    program, test = create_comprehensive_final_test(admin_token)
    if not test:
        print("❌ Cannot proceed without test creation")
        return
    
    # Step 3: Verify question data structure
    print("\n3️⃣ VERIFYING QUESTION DATA STRUCTURE")
    test_data, all_correct_answers_present = verify_question_data_structure(admin_token, test['id'])
    
    if not all_correct_answers_present:
        print("❌ CRITICAL: correctAnswer fields are still missing!")
        print("The fix may not have been applied correctly.")
        return
    else:
        print("✅ All correctAnswer fields are present in API response!")
    
    # Step 4: Authenticate as student
    print("\n4️⃣ STUDENT AUTHENTICATION")
    student_token, student_user = authenticate_user(STUDENT_CREDENTIALS)
    if not student_token:
        print("❌ Cannot proceed without student authentication")
        return
    print(f"✅ Student authenticated: {student_user['email']}")
    
    # Step 5: Test perfect answers (should get 100%)
    print("\n5️⃣ TESTING PERFECT ANSWERS (SHOULD GET 100%)")
    perfect_attempt = submit_perfect_answers(student_token, test_data, program['id'])
    
    # Step 6: Test partial answers (should get ~71%)
    print("\n6️⃣ TESTING PARTIAL ANSWERS (SHOULD GET ~71%)")
    partial_attempt = submit_partial_answers(student_token, test_data, program['id'])
    
    # Step 7: Test all wrong answers (should get 0%)
    print("\n7️⃣ TESTING ALL WRONG ANSWERS (SHOULD GET 0%)")
    wrong_attempt = submit_all_wrong_answers(student_token, test_data, program['id'])
    
    # Step 8: Summary and analysis
    print("\n" + "=" * 60)
    print("🎯 FINAL EXAM SCORING VERIFICATION SUMMARY")
    print("=" * 60)
    
    success_count = 0
    total_tests = 0
    
    if perfect_attempt:
        total_tests += 1
        perfect_score = perfect_attempt.get('score', 0)
        print(f"✅ Perfect answers: {perfect_score}%")
        if perfect_score == 100:
            print("   🎉 SUCCESS: Perfect answers scored 100%!")
            success_count += 1
        else:
            print(f"   ❌ ISSUE: Expected 100%, got {perfect_score}%")
    
    if partial_attempt:
        total_tests += 1
        partial_score = partial_attempt.get('score', 0)
        expected_partial = round((25/35) * 100, 1)  # 2 correct out of 3 questions
        print(f"✅ Partial answers: {partial_score}%")
        if abs(partial_score - expected_partial) < 1:  # Allow 1% tolerance
            print(f"   🎉 SUCCESS: Partial answers scored ~{expected_partial}%!")
            success_count += 1
        else:
            print(f"   ❌ ISSUE: Expected ~{expected_partial}%, got {partial_score}%")
    
    if wrong_attempt:
        total_tests += 1
        wrong_score = wrong_attempt.get('score', 0)
        print(f"✅ Wrong answers: {wrong_score}%")
        if wrong_score == 0:
            print("   🎉 SUCCESS: Wrong answers scored 0%!")
            success_count += 1
        else:
            print(f"   ❌ ISSUE: Expected 0%, got {wrong_score}%")
    
    print(f"\n📊 OVERALL RESULTS: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 FINAL EXAM SCORING FIX SUCCESSFUL!")
        print("✅ All scoring scenarios work correctly")
        print("✅ Students will now get proper scores based on their answers")
    else:
        print("❌ FINAL EXAM SCORING STILL HAS ISSUES")
        print("🔍 Further investigation needed")
    
    print("\n✅ Verification completed!")

if __name__ == "__main__":
    main()