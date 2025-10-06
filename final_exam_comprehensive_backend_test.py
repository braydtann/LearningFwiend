#!/usr/bin/env python3
"""
FINAL EXAM COMPREHENSIVE SYSTEM TEST - Backend Test
==================================================

COMPREHENSIVE TEST: Verify all aspects of the final exam system work correctly:
1. Final Test Creation & Data Structure
2. Answer Submission Format & Question ID Matching
3. Scoring Logic for All Question Types
4. Student Access and Authentication

Test Credentials:
- Admin: brayden.t@covesmart.com / Hawaii2020!
- Student: karlo.student@alder.com / StudentPermanent123!
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://lms-progression.preview.emergentagent.com/api"

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

def create_comprehensive_final_exam(token):
    """Create a comprehensive final exam with all question types"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create program
    program_data = {
        "title": "Comprehensive Final Exam Test Program",
        "description": "Program to test all final exam functionality",
        "duration": "4 weeks",
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
    
    # Create comprehensive final test with all question types
    final_test_data = {
        "title": "Comprehensive Final Exam - All Question Types",
        "description": "Final exam testing all question types and scoring scenarios",
        "programId": program['id'],
        "passingScore": 75.0,
        "timeLimit": 60,
        "maxAttempts": 3,
        "isPublished": True,
        "questions": [
            {
                "type": "multiple_choice",
                "question": "What is the largest planet in our solar system?",
                "options": ["Earth", "Mars", "Jupiter", "Saturn"],
                "correctAnswer": "2",  # Index 2 = "Jupiter"
                "points": 10,
                "explanation": "Jupiter is the largest planet in our solar system"
            },
            {
                "type": "true_false",
                "question": "The Great Wall of China is visible from space.",
                "options": ["True", "False"],
                "correctAnswer": "false",  # This is actually false
                "points": 10,
                "explanation": "The Great Wall is not visible from space with the naked eye"
            },
            {
                "type": "short_answer",
                "question": "What is the chemical symbol for gold?",
                "options": [],
                "correctAnswer": "au",
                "points": 15,
                "explanation": "Au is the chemical symbol for gold (from Latin 'aurum')"
            },
            {
                "type": "multiple_choice",
                "question": "Which programming language is known for its use in data science?",
                "options": ["JavaScript", "Python", "C++", "Assembly"],
                "correctAnswer": "1",  # Index 1 = "Python"
                "points": 10,
                "explanation": "Python is widely used in data science and machine learning"
            },
            {
                "type": "true_false",
                "question": "HTTP stands for HyperText Transfer Protocol.",
                "options": ["True", "False"],
                "correctAnswer": "true",
                "points": 10,
                "explanation": "HTTP does stand for HyperText Transfer Protocol"
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
            print(f"   - Passing Score: {test.get('passingScore', 'N/A')}%")
            return program, test
        else:
            print(f"❌ Final test creation failed: {response.status_code} - {response.text}")
            return program, None
    except Exception as e:
        print(f"❌ Final test creation error: {str(e)}")
        return program, None

def verify_data_structure_integrity(token, test_id):
    """Verify all data structure elements are correct"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BACKEND_URL}/final-tests/{test_id}", headers=headers)
        if response.status_code == 200:
            test = response.json()
            print(f"\n🔍 DATA STRUCTURE INTEGRITY CHECK:")
            print(f"   - Test ID: {test.get('id')}")
            print(f"   - Total Points: {test.get('totalPoints')}")
            print(f"   - Question Count: {len(test.get('questions', []))}")
            
            integrity_issues = []
            
            for i, question in enumerate(test.get('questions', [])):
                print(f"\n   Question {i+1} ({question.get('type')}):")
                print(f"     - ID: {question.get('id')}")
                print(f"     - Correct Answer: '{question.get('correctAnswer')}'")
                print(f"     - Points: {question.get('points')}")
                
                # Check for integrity issues
                if question.get('correctAnswer') is None:
                    integrity_issues.append(f"Q{i+1}: correctAnswer is None")
                if question.get('points') is None or question.get('points') <= 0:
                    integrity_issues.append(f"Q{i+1}: invalid points value")
                if not question.get('id'):
                    integrity_issues.append(f"Q{i+1}: missing question ID")
                    
            if integrity_issues:
                print(f"\n❌ INTEGRITY ISSUES FOUND:")
                for issue in integrity_issues:
                    print(f"     - {issue}")
                return test, False
            else:
                print(f"\n✅ ALL DATA STRUCTURE CHECKS PASSED")
                return test, True
                
        else:
            print(f"❌ Failed to get test data: {response.status_code}")
            return None, False
    except Exception as e:
        print(f"❌ Error checking data structure: {str(e)}")
        return None, False

def test_perfect_score_scenario(student_token, test, program_id):
    """Test scenario where student should get 100%"""
    headers = {"Authorization": f"Bearer {student_token}"}
    
    questions = test.get('questions', [])
    
    # Submit all correct answers
    attempt_data = {
        "testId": test['id'],
        "programId": program_id,
        "answers": [
            {"questionId": questions[0]['id'], "answer": "2"},      # Jupiter (correct)
            {"questionId": questions[1]['id'], "answer": "false"},  # Great Wall (correct)
            {"questionId": questions[2]['id'], "answer": "au"},     # Gold symbol (correct)
            {"questionId": questions[3]['id'], "answer": "1"},      # Python (correct)
            {"questionId": questions[4]['id'], "answer": "true"}    # HTTP (correct)
        ],
        "timeSpent": 1800  # 30 minutes
    }
    
    print(f"\n🎯 PERFECT SCORE SCENARIO (ALL CORRECT ANSWERS):")
    for i, answer in enumerate(attempt_data['answers']):
        print(f"   Q{i+1}: {answer['answer']} ✅")
    
    try:
        response = requests.post(f"{BACKEND_URL}/final-test-attempts", json=attempt_data, headers=headers)
        if response.status_code == 200:
            attempt = response.json()
            score = attempt.get('score', 0)
            points = attempt.get('pointsEarned', 0)
            total = attempt.get('totalPoints', 0)
            passed = attempt.get('isPassed', False)
            
            print(f"✅ Perfect score attempt submitted!")
            print(f"   - Score: {score}%")
            print(f"   - Points: {points}/{total}")
            print(f"   - Passed: {passed}")
            
            return score == 100 and passed
        else:
            print(f"❌ Perfect score attempt failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Perfect score attempt error: {str(e)}")
        return False

def test_failing_score_scenario(student_token, test, program_id):
    """Test scenario where student should fail (< 75%)"""
    headers = {"Authorization": f"Bearer {student_token}"}
    
    questions = test.get('questions', [])
    
    # Submit mostly incorrect answers (2 correct, 3 incorrect = 35/55 = 63.6%)
    attempt_data = {
        "testId": test['id'],
        "programId": program_id,
        "answers": [
            {"questionId": questions[0]['id'], "answer": "0"},       # Earth (incorrect)
            {"questionId": questions[1]['id'], "answer": "true"},    # Great Wall (incorrect)
            {"questionId": questions[2]['id'], "answer": "au"},      # Gold symbol (correct)
            {"questionId": questions[3]['id'], "answer": "0"},       # JavaScript (incorrect)
            {"questionId": questions[4]['id'], "answer": "true"}     # HTTP (correct)
        ],
        "timeSpent": 1200  # 20 minutes
    }
    
    print(f"\n🎯 FAILING SCORE SCENARIO (2/5 CORRECT = 63.6%):")
    correct_answers = ["2", "false", "au", "1", "true"]
    for i, answer in enumerate(attempt_data['answers']):
        status = "✅" if answer['answer'] == correct_answers[i] else "❌"
        print(f"   Q{i+1}: {answer['answer']} {status}")
    
    try:
        response = requests.post(f"{BACKEND_URL}/final-test-attempts", json=attempt_data, headers=headers)
        if response.status_code == 200:
            attempt = response.json()
            score = attempt.get('score', 0)
            points = attempt.get('pointsEarned', 0)
            total = attempt.get('totalPoints', 0)
            passed = attempt.get('isPassed', True)
            
            print(f"✅ Failing score attempt submitted!")
            print(f"   - Score: {score}%")
            print(f"   - Points: {points}/{total}")
            print(f"   - Passed: {passed}")
            print(f"   - Expected: ~63.6% (35/55 points), Should NOT pass")
            
            # Should be around 63.6% and should not pass
            expected_score = (35/55) * 100  # 63.64%
            return abs(score - expected_score) < 2 and not passed
        else:
            print(f"❌ Failing score attempt failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failing score attempt error: {str(e)}")
        return False

def test_edge_case_scenarios(student_token, test, program_id):
    """Test edge cases like empty answers, wrong question IDs, etc."""
    headers = {"Authorization": f"Bearer {student_token}"}
    
    questions = test.get('questions', [])
    
    print(f"\n🧪 EDGE CASE TESTING:")
    
    # Test 1: Submit with wrong question IDs (should fail gracefully)
    print(f"   Test 1: Wrong question IDs")
    attempt_data = {
        "testId": test['id'],
        "programId": program_id,
        "answers": [
            {"questionId": "wrong-id-1", "answer": "2"},
            {"questionId": "wrong-id-2", "answer": "false"},
            {"questionId": "wrong-id-3", "answer": "au"},
            {"questionId": "wrong-id-4", "answer": "1"},
            {"questionId": "wrong-id-5", "answer": "true"}
        ],
        "timeSpent": 600
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/final-test-attempts", json=attempt_data, headers=headers)
        if response.status_code == 200:
            attempt = response.json()
            score = attempt.get('score', 0)
            print(f"     ✅ Wrong IDs handled gracefully: {score}% (expected 0%)")
            edge_case_1_pass = score == 0
        else:
            print(f"     ❌ Wrong IDs caused error: {response.status_code}")
            edge_case_1_pass = False
    except Exception as e:
        print(f"     ❌ Wrong IDs caused exception: {str(e)}")
        edge_case_1_pass = False
    
    return edge_case_1_pass

def main():
    print("🎯 FINAL EXAM COMPREHENSIVE SYSTEM TEST")
    print("=" * 60)
    print("Testing all aspects of the final exam system")
    print()
    
    test_results = {
        "authentication": False,
        "test_creation": False,
        "data_integrity": False,
        "perfect_score": False,
        "failing_score": False,
        "edge_cases": False
    }
    
    # Step 1: Authentication
    print("1️⃣ AUTHENTICATION TESTING")
    admin_token, admin_user = authenticate_user(ADMIN_CREDENTIALS)
    student_token, student_user = authenticate_user(STUDENT_CREDENTIALS)
    
    if admin_token and student_token:
        print(f"✅ Admin: {admin_user['email']}")
        print(f"✅ Student: {student_user['email']}")
        test_results["authentication"] = True
    else:
        print("❌ Authentication failed")
        return
    
    # Step 2: Create comprehensive final exam
    print("\n2️⃣ FINAL EXAM CREATION")
    program, test = create_comprehensive_final_exam(admin_token)
    if test:
        test_results["test_creation"] = True
    else:
        print("❌ Cannot proceed without test creation")
        return
    
    # Step 3: Verify data structure integrity
    print("\n3️⃣ DATA STRUCTURE INTEGRITY")
    test_data, integrity_ok = verify_data_structure_integrity(admin_token, test['id'])
    if integrity_ok:
        test_results["data_integrity"] = True
    
    # Step 4: Test perfect score scenario
    print("\n4️⃣ PERFECT SCORE TESTING")
    perfect_score_ok = test_perfect_score_scenario(student_token, test_data, program['id'])
    if perfect_score_ok:
        test_results["perfect_score"] = True
    
    # Step 5: Test failing score scenario
    print("\n5️⃣ FAILING SCORE TESTING")
    failing_score_ok = test_failing_score_scenario(student_token, test_data, program['id'])
    if failing_score_ok:
        test_results["failing_score"] = True
    
    # Step 6: Test edge cases
    print("\n6️⃣ EDGE CASE TESTING")
    edge_cases_ok = test_edge_case_scenarios(student_token, test_data, program['id'])
    if edge_cases_ok:
        test_results["edge_cases"] = True
    
    # Final Summary
    print("\n" + "=" * 60)
    print("🎯 COMPREHENSIVE SYSTEM TEST SUMMARY")
    print("=" * 60)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, passed in test_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n📊 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
    success_rate = (passed_tests / total_tests) * 100
    print(f"📈 SUCCESS RATE: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 FINAL EXAM SYSTEM IS FULLY FUNCTIONAL!")
        print("✅ All critical functionality working correctly")
        print("✅ Students can take final exams and receive accurate scores")
        print("✅ Scoring logic handles all question types properly")
        print("✅ System ready for production use")
    elif success_rate >= 75:
        print("⚠️  FINAL EXAM SYSTEM IS MOSTLY FUNCTIONAL")
        print("✅ Core functionality working")
        print("⚠️  Some edge cases may need attention")
    else:
        print("❌ FINAL EXAM SYSTEM HAS CRITICAL ISSUES")
        print("🔍 Further investigation and fixes needed")
    
    print("\n✅ Comprehensive testing completed!")

if __name__ == "__main__":
    main()