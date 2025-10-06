#!/usr/bin/env python3
"""
URGENT: Final Exam Scoring Logic Debug - Step by Step Analysis
==============================================================

This test focuses specifically on the scoring logic data flow as requested:
1. Database vs API Data - verify scoring uses await db.final_tests.find_one() directly
2. Answer Format Matching - check questionId matching
3. Step-by-Step Debug - trace through questionId generation and answer_map lookup
4. Test Real Submission - capture exact data flow

Admin: brayden.t@covesmart.com / Hawaii2020!
Student: karlo.student@alder.com / StudentPermanent123!
"""

import requests
import json
import sys
from datetime import datetime
import uuid

BACKEND_URL = "https://lms-progression-1.preview.emergentagent.com/api"

ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"
STUDENT_EMAIL = "karlo.student@alder.com"
STUDENT_PASSWORD = "StudentPermanent123!"

class ScoringLogicDebugger:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.debug_data = {}
        
    def authenticate(self):
        """Authenticate both admin and student"""
        # Admin auth
        admin_response = requests.post(f"{BACKEND_URL}/auth/login", json={
            "username_or_email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if admin_response.status_code != 200:
            print(f"❌ Admin auth failed: {admin_response.status_code}")
            return False
            
        self.admin_token = admin_response.json()["access_token"]
        print(f"✅ Admin authenticated: {admin_response.json()['user']['full_name']}")
        
        # Student auth
        student_response = requests.post(f"{BACKEND_URL}/auth/login", json={
            "username_or_email": STUDENT_EMAIL,
            "password": STUDENT_PASSWORD
        })
        
        if student_response.status_code != 200:
            print(f"❌ Student auth failed: {student_response.status_code}")
            return False
            
        self.student_token = student_response.json()["access_token"]
        print(f"✅ Student authenticated: {student_response.json()['user']['full_name']}")
        
        return True
    
    def create_debug_test(self):
        """Create a test with explicit question IDs and correct answers"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Create program first
        program_data = {
            "title": f"Debug Program {datetime.now().strftime('%H%M%S')}",
            "description": "Debug scoring logic",
            "courseIds": [],
            "nestedProgramIds": []
        }
        
        program_response = requests.post(f"{BACKEND_URL}/programs", json=program_data, headers=headers)
        if program_response.status_code != 200:
            print(f"❌ Program creation failed: {program_response.status_code}")
            return None
            
        program = program_response.json()
        program_id = program["id"]
        
        # Create test with explicit structure
        test_data = {
            "title": f"Debug Test {datetime.now().strftime('%H%M%S')}",
            "description": "Debug scoring logic test",
            "programId": program_id,
            "questions": [
                {
                    "type": "multiple_choice",
                    "question": "What is 2 + 2?",
                    "options": ["1", "2", "4", "8"],  # Index 2 = "4" is correct
                    "correctAnswer": "2",  # String format
                    "points": 10,
                    "explanation": "2 + 2 = 4"
                },
                {
                    "type": "true_false",
                    "question": "The sky is blue.",
                    "correctAnswer": "true",  # String format
                    "points": 5,
                    "explanation": "The sky appears blue"
                }
            ],
            "timeLimit": 60,
            "maxAttempts": 5,
            "passingScore": 75.0,
            "shuffleQuestions": False,
            "showResults": True,
            "isPublished": True
        }
        
        test_response = requests.post(f"{BACKEND_URL}/final-tests", json=test_data, headers=headers)
        
        if test_response.status_code == 200:
            test = test_response.json()
            self.debug_test_id = test["id"]
            self.debug_program_id = program_id
            
            print(f"✅ Debug test created: {test['id']}")
            print(f"   Questions: {len(test['questions'])}")
            print(f"   Total Points: {test.get('totalPoints', 0)}")
            
            # Store for analysis
            self.debug_data["created_test"] = test
            
            return test
        else:
            print(f"❌ Test creation failed: {test_response.status_code}")
            print(f"   Error: {test_response.text}")
            return None
    
    def analyze_database_structure(self):
        """Get the test from database and analyze structure"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        response = requests.get(f"{BACKEND_URL}/final-tests/{self.debug_test_id}", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Failed to get test from database: {response.status_code}")
            return None
            
        stored_test = response.json()
        self.debug_data["stored_test"] = stored_test
        
        print("\n🔍 DATABASE STRUCTURE ANALYSIS:")
        print(f"   Test ID: {stored_test.get('id')}")
        print(f"   Questions Count: {len(stored_test.get('questions', []))}")
        print(f"   Total Points: {stored_test.get('totalPoints', 0)}")
        
        # Analyze each question
        for i, question in enumerate(stored_test.get('questions', [])):
            print(f"\n   Question {i+1}:")
            print(f"     ID: {question.get('id', 'MISSING_ID')}")
            print(f"     Type: {question.get('type', 'MISSING_TYPE')}")
            print(f"     Text: {question.get('question', 'MISSING_TEXT')[:50]}...")
            print(f"     Correct Answer: {question.get('correctAnswer', 'MISSING_CORRECT_ANSWER')}")
            print(f"     Points: {question.get('points', 'MISSING_POINTS')}")
            
            if question.get('type') == 'multiple_choice':
                print(f"     Options: {question.get('options', 'MISSING_OPTIONS')}")
        
        return stored_test
    
    def test_submission_with_debug(self):
        """Submit answers and trace the exact scoring logic"""
        stored_test = self.debug_data.get("stored_test")
        if not stored_test:
            print("❌ No stored test data for submission")
            return None
            
        questions = stored_test.get('questions', [])
        if len(questions) < 2:
            print("❌ Not enough questions for submission test")
            return None
            
        # Create submission with correct answers
        submission_data = {
            "testId": self.debug_test_id,
            "programId": self.debug_program_id,
            "answers": [
                {
                    "questionId": questions[0].get('id'),  # Multiple choice question
                    "answer": "2"  # Correct answer (index 2 = "4")
                },
                {
                    "questionId": questions[1].get('id'),  # True/false question
                    "answer": "true"  # Correct answer
                }
            ],
            "timeSpent": 60
        }
        
        print("\n🔍 SUBMISSION DATA ANALYSIS:")
        print(f"   Test ID: {submission_data['testId']}")
        print(f"   Program ID: {submission_data['programId']}")
        print(f"   Answers:")
        
        for i, answer in enumerate(submission_data['answers']):
            question = questions[i]
            print(f"     Answer {i+1}:")
            print(f"       Question ID: {answer['questionId']}")
            print(f"       Student Answer: {answer['answer']}")
            print(f"       Question Type: {question.get('type')}")
            print(f"       Correct Answer: {question.get('correctAnswer')}")
            print(f"       Expected Match: {answer['answer'] == str(question.get('correctAnswer'))}")
        
        # Submit the attempt
        student_headers = {"Authorization": f"Bearer {self.student_token}"}
        response = requests.post(f"{BACKEND_URL}/final-test-attempts", 
                               json=submission_data, headers=student_headers)
        
        print(f"\n🔍 SUBMISSION RESPONSE:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            self.debug_data["submission_result"] = result
            
            print(f"   Score: {result.get('score', 0)}%")
            print(f"   Points Earned: {result.get('pointsEarned', 0)}")
            print(f"   Total Points: {result.get('totalPoints', 0)}")
            print(f"   Passed: {result.get('isPassed', False)}")
            
            # Expected: Both answers correct = 15 points = 100%
            expected_score = 100.0
            expected_points = 15
            
            if result.get('score') == expected_score and result.get('pointsEarned') == expected_points:
                print("   ✅ SCORING CORRECT")
            else:
                print("   ❌ SCORING INCORRECT")
                print(f"   Expected: {expected_score}% ({expected_points} points)")
                print(f"   Actual: {result.get('score')}% ({result.get('pointsEarned')} points)")
            
            return result
        else:
            print(f"   Error: {response.text}")
            return None
    
    def simulate_backend_scoring_logic(self):
        """Simulate the exact backend scoring logic to identify issues"""
        stored_test = self.debug_data.get("stored_test")
        submission_data = self.debug_data.get("submission_result")
        
        if not stored_test or not submission_data:
            print("❌ Missing data for scoring simulation")
            return
            
        print("\n🔍 BACKEND SCORING LOGIC SIMULATION:")
        
        # Get the original submission data (we need to reconstruct it)
        questions = stored_test.get('questions', [])
        
        # Simulate answer_map creation
        answer_map = {}
        for i, question in enumerate(questions):
            if i == 0:  # Multiple choice
                answer_map[question.get('id')] = "2"
            elif i == 1:  # True/false
                answer_map[question.get('id')] = "true"
        
        print(f"   Answer Map: {answer_map}")
        
        # Simulate scoring loop
        points_earned = 0
        total_points = 0
        
        for question in questions:
            question_id = question.get('id')
            student_answer = answer_map.get(question_id)
            question_points = question.get('points', 1)
            total_points += question_points
            
            print(f"\n   Processing Question: {question_id}")
            print(f"     Type: {question.get('type')}")
            print(f"     Student Answer: {student_answer}")
            print(f"     Correct Answer: {question.get('correctAnswer')}")
            print(f"     Points: {question_points}")
            
            if question['type'] == 'multiple_choice':
                try:
                    answer_index = int(student_answer) if str(student_answer).isdigit() else -1
                    correct_index = int(question['correctAnswer']) if str(question['correctAnswer']).isdigit() else -1
                    
                    print(f"     Answer Index: {answer_index}")
                    print(f"     Correct Index: {correct_index}")
                    print(f"     Match: {answer_index == correct_index}")
                    
                    if answer_index >= 0 and correct_index >= 0 and answer_index == correct_index:
                        points_earned += question_points
                        print(f"     ✅ CORRECT - Earned {question_points} points")
                    else:
                        print(f"     ❌ INCORRECT - No points")
                except Exception as e:
                    print(f"     ❌ ERROR: {e}")
                    
            elif question['type'] == 'true_false':
                student_str = str(student_answer).lower().strip() if student_answer is not None else ""
                correct_str = str(question.get('correctAnswer')).lower().strip() if question.get('correctAnswer') else ""
                
                print(f"     Student String: '{student_str}'")
                print(f"     Correct String: '{correct_str}'")
                print(f"     Match: {student_str == correct_str}")
                
                if student_str == correct_str and student_str != "":
                    points_earned += question_points
                    print(f"     ✅ CORRECT - Earned {question_points} points")
                else:
                    print(f"     ❌ INCORRECT - No points")
        
        print(f"\n   FINAL CALCULATION:")
        print(f"     Points Earned: {points_earned}")
        print(f"     Total Points: {total_points}")
        
        score_percentage = (points_earned / total_points * 100) if total_points > 0 else 0
        print(f"     Score Percentage: {score_percentage}%")
        
        # Compare with actual result
        actual_score = submission_data.get('score', 0)
        actual_points = submission_data.get('pointsEarned', 0)
        
        print(f"\n   COMPARISON:")
        print(f"     Simulated: {score_percentage}% ({points_earned} points)")
        print(f"     Actual: {actual_score}% ({actual_points} points)")
        
        if abs(score_percentage - actual_score) < 0.01 and points_earned == actual_points:
            print("     ✅ LOGIC MATCHES")
        else:
            print("     ❌ LOGIC MISMATCH - BUG IDENTIFIED")
    
    def run_debug(self):
        """Run the complete debugging process"""
        print("🚨 URGENT: Final Exam Scoring Logic Debug")
        print("=" * 60)
        
        if not self.authenticate():
            return False
            
        test = self.create_debug_test()
        if not test:
            return False
            
        stored_test = self.analyze_database_structure()
        if not stored_test:
            return False
            
        result = self.test_submission_with_debug()
        if result is None:
            return False
            
        self.simulate_backend_scoring_logic()
        
        print("\n" + "=" * 60)
        print("🎯 DEBUG COMPLETE")
        
        return True

if __name__ == "__main__":
    debugger = ScoringLogicDebugger()
    success = debugger.run_debug()
    sys.exit(0 if success else 1)