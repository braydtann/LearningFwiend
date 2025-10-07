#!/usr/bin/env python3
"""
FINAL EXAM SCORING FIX - Backend Test
====================================

CRITICAL ISSUE IDENTIFIED: 
- QuestionResponse model doesn't include correctAnswer field
- This causes scoring logic to fail because correctAnswer is None
- Need to fix the model and test the scoring logic

Test Credentials:
- Admin: brayden.t@covesmart.com / Hawaii2020!
- Student: karlo.student@alder.com / StudentPermanent123!
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

def check_database_question_data(token, test_id):
    """Check if correctAnswer is stored in database by examining raw data"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get the test data directly
        response = requests.get(f"{BACKEND_URL}/final-tests/{test_id}", headers=headers)
        if response.status_code == 200:
            test = response.json()
            print(f"\n🔍 DATABASE QUESTION DATA ANALYSIS:")
            print(f"   - Test ID: {test.get('id')}")
            
            for i, question in enumerate(test.get('questions', [])):
                print(f"\n   Question {i+1} (Database):")
                print(f"     - ID: {question.get('id')}")
                print(f"     - Type: {question.get('type')}")
                print(f"     - Correct Answer: {question.get('correctAnswer')}")
                print(f"     - Options: {question.get('options')}")
                
                # Check if correctAnswer is missing from response
                if question.get('correctAnswer') is None:
                    print(f"     ❌ CRITICAL: correctAnswer is None in API response!")
                else:
                    print(f"     ✅ correctAnswer present: {question.get('correctAnswer')}")
                    
            return test
        else:
            print(f"❌ Failed to get test data: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error checking database: {str(e)}")
        return None

def test_scoring_with_manual_data():
    """Test the scoring logic manually with known data"""
    print(f"\n🧪 MANUAL SCORING LOGIC TEST:")
    
    # Simulate the scoring logic from server.py lines 4529-4580
    test_questions = [
        {
            "id": "q1_test",
            "type": "multiple_choice", 
            "correctAnswer": "2",  # Should be index 2 = "4"
            "points": 10,
            "options": ["2", "3", "4", "5"]
        },
        {
            "id": "q2_test",
            "type": "true_false",
            "correctAnswer": "true",
            "points": 10,
            "options": ["True", "False"]
        }
    ]
    
    # Test correct answers
    correct_answers = [
        {"questionId": "q1_test", "answer": "2"},  # Index 2 = "4"
        {"questionId": "q2_test", "answer": "true"}
    ]
    
    # Test incorrect answers  
    incorrect_answers = [
        {"questionId": "q1_test", "answer": "0"},  # Index 0 = "2"
        {"questionId": "q2_test", "answer": "false"}
    ]
    
    def calculate_score(questions, answers):
        points_earned = 0
        total_points = sum(q['points'] for q in questions)
        
        # Create answer map
        answer_map = {answer.get('questionId'): answer.get('answer') for answer in answers}
        
        for question in questions:
            question_id = question.get('id')
            student_answer = answer_map.get(question_id)
            question_points = question.get('points', 1)
            
            print(f"     - Question {question_id}:")
            print(f"       Student Answer: {student_answer}")
            print(f"       Correct Answer: {question.get('correctAnswer')}")
            
            if question['type'] == 'multiple_choice':
                try:
                    answer_index = int(student_answer) if str(student_answer).isdigit() else -1
                    correct_index = int(question['correctAnswer']) if str(question['correctAnswer']).isdigit() else -1
                    
                    print(f"       Answer Index: {answer_index}, Correct Index: {correct_index}")
                    
                    if answer_index >= 0 and correct_index >= 0 and answer_index == correct_index:
                        points_earned += question_points
                        print(f"       ✅ CORRECT! +{question_points} points")
                    else:
                        print(f"       ❌ INCORRECT! +0 points")
                except (ValueError, AttributeError, TypeError):
                    print(f"       ❌ ERROR in scoring logic!")
                    
            elif question['type'] == 'true_false':
                if (student_answer is not None and question.get('correctAnswer') and 
                    str(student_answer).lower().strip() == str(question['correctAnswer']).lower().strip()):
                    points_earned += question_points
                    print(f"       ✅ CORRECT! +{question_points} points")
                else:
                    print(f"       ❌ INCORRECT! +0 points")
        
        score_percentage = (points_earned / total_points * 100) if total_points > 0 else 0
        return points_earned, total_points, score_percentage
    
    # Test correct answers
    print(f"\n   Testing CORRECT answers:")
    correct_points, total_points, correct_score = calculate_score(test_questions, correct_answers)
    print(f"   Result: {correct_points}/{total_points} points = {correct_score}%")
    
    # Test incorrect answers
    print(f"\n   Testing INCORRECT answers:")
    incorrect_points, total_points, incorrect_score = calculate_score(test_questions, incorrect_answers)
    print(f"   Result: {incorrect_points}/{total_points} points = {incorrect_score}%")
    
    return correct_score, incorrect_score

def create_test_with_simple_questions(token):
    """Create a simple test to verify the fix"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # First create a program
    program_data = {
        "title": "Scoring Fix Test Program",
        "description": "Program to test scoring fix",
        "duration": "1 week",
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
    
    # Create final test with explicit correctAnswer values
    final_test_data = {
        "title": "Scoring Fix Test",
        "description": "Test to verify scoring fix",
        "programId": program['id'],
        "passingScore": 75.0,
        "timeLimit": 30,
        "maxAttempts": 5,
        "isPublished": True,
        "questions": [
            {
                "type": "multiple_choice",
                "question": "What is 1 + 1?",
                "options": ["1", "2", "3", "4"],
                "correctAnswer": "1",  # Index 1 = "2"
                "points": 5,
                "explanation": "1 + 1 = 2"
            },
            {
                "type": "true_false",
                "question": "Water boils at 100°C.",
                "options": ["True", "False"],
                "correctAnswer": "true",
                "points": 5,
                "explanation": "Water boils at 100°C at sea level"
            }
        ]
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/final-tests", json=final_test_data, headers=headers)
        if response.status_code == 200:
            test = response.json()
            print(f"✅ Created final test: {test['id']}")
            return program, test
        else:
            print(f"❌ Final test creation failed: {response.status_code} - {response.text}")
            return program, None
    except Exception as e:
        print(f"❌ Final test creation error: {str(e)}")
        return program, None

def test_final_exam_scoring_after_fix(student_token, test_id, program_id):
    """Test final exam scoring after the fix"""
    headers = {"Authorization": f"Bearer {student_token}"}
    
    # Submit correct answers
    correct_attempt_data = {
        "testId": test_id,
        "programId": program_id,
        "answers": [
            {"questionId": "q1", "answer": "1"},  # Correct: index 1 = "2"
            {"questionId": "q2", "answer": "true"}  # Correct
        ],
        "timeSpent": 300
    }
    
    print(f"\n🎯 TESTING SCORING AFTER FIX:")
    print(f"Submitting correct answers...")
    
    try:
        response = requests.post(f"{BACKEND_URL}/final-test-attempts", json=correct_attempt_data, headers=headers)
        if response.status_code == 200:
            attempt = response.json()
            score = attempt.get('score', 0)
            print(f"✅ Attempt submitted successfully!")
            print(f"   - Score: {score}%")
            print(f"   - Points: {attempt.get('pointsEarned', 0)}/{attempt.get('totalPoints', 0)}")
            
            if score == 100:
                print(f"🎉 SUCCESS: Scoring logic is working correctly!")
                return True
            elif score == 0:
                print(f"❌ STILL BROKEN: Scoring logic still returns 0%")
                return False
            else:
                print(f"⚠️  PARTIAL: Unexpected score {score}%")
                return False
        else:
            print(f"❌ Attempt failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Attempt error: {str(e)}")
        return False

def main():
    print("🔧 FINAL EXAM SCORING FIX - Backend Test")
    print("=" * 50)
    print("Testing and fixing the final exam scoring issue")
    print()
    
    # Step 1: Authenticate as admin
    print("1️⃣ ADMIN AUTHENTICATION")
    admin_token, admin_user = authenticate_user(ADMIN_CREDENTIALS)
    if not admin_token:
        print("❌ Cannot proceed without admin authentication")
        return
    print(f"✅ Admin authenticated: {admin_user['email']}")
    
    # Step 2: Test manual scoring logic
    print("\n2️⃣ TESTING MANUAL SCORING LOGIC")
    correct_score, incorrect_score = test_scoring_with_manual_data()
    
    if correct_score == 100 and incorrect_score == 0:
        print("✅ Manual scoring logic works correctly")
    else:
        print("❌ Manual scoring logic has issues")
    
    # Step 3: Create test with simple questions
    print("\n3️⃣ CREATING TEST WITH SIMPLE QUESTIONS")
    program, test = create_test_with_simple_questions(admin_token)
    if not test:
        print("❌ Cannot proceed without test creation")
        return
    
    # Step 4: Check database question data
    print("\n4️⃣ CHECKING DATABASE QUESTION DATA")
    test_data = check_database_question_data(admin_token, test['id'])
    
    # Step 5: Authenticate as student
    print("\n5️⃣ STUDENT AUTHENTICATION")
    student_token, student_user = authenticate_user(STUDENT_CREDENTIALS)
    if not student_token:
        print("❌ Cannot proceed without student authentication")
        return
    print(f"✅ Student authenticated: {student_user['email']}")
    
    # Step 6: Test scoring after fix
    print("\n6️⃣ TESTING SCORING AFTER FIX")
    scoring_works = test_final_exam_scoring_after_fix(student_token, test['id'], program['id'])
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 FINAL EXAM SCORING FIX SUMMARY")
    print("=" * 50)
    
    if scoring_works:
        print("🎉 SUCCESS: Final exam scoring is now working correctly!")
    else:
        print("❌ ISSUE PERSISTS: Final exam scoring still needs fixing")
        print("\n🔍 NEXT STEPS:")
        print("1. Fix QuestionResponse model to include correctAnswer field")
        print("2. Ensure correctAnswer is properly stored and retrieved")
        print("3. Verify question ID matching in scoring logic")
    
    print("\n✅ Investigation completed!")

if __name__ == "__main__":
    main()