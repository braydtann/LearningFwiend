#!/usr/bin/env python3
"""
CRITICAL FIX: Quiz Scoring Issue Resolution
Root cause identified: Frontend sends answers as dictionary, backend expects list of dictionaries.

ISSUE: Frontend sends: {"questionId1": "answer1", "questionId2": "answer2"}
BACKEND EXPECTS: [{"questionId": "questionId1", "answer": "answer1"}, {"questionId": "questionId2", "answer": "answer2"}]

This explains why users get 0% scores - the backend can't parse the answers correctly.
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://lms-progression-1.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"
STUDENT_EMAIL = "karlo.student@alder.com"
STUDENT_PASSWORD = "StudentPermanent123!"

class QuizScoringFixer:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.student_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username_or_email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                self.log_test("Admin Authentication", True, f"Logged in as {data['user']['full_name']}")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def authenticate_student(self):
        """Authenticate as student user"""
        try:
            # Create new session for student
            student_session = requests.Session()
            response = student_session.post(f"{BACKEND_URL}/auth/login", json={
                "username_or_email": STUDENT_EMAIL,
                "password": STUDENT_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data["access_token"]
                self.student_session = student_session
                self.student_session.headers.update({
                    "Authorization": f"Bearer {self.student_token}"
                })
                self.log_test("Student Authentication", True, f"Logged in as {data['user']['full_name']}")
                return True
            else:
                self.log_test("Student Authentication", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Student Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_wrong_format_submission(self):
        """Test submission with wrong format (dictionary) - should fail"""
        try:
            # Create test program and exam
            program_data = {
                "title": f"Format Test Program {datetime.now().strftime('%H%M%S')}",
                "description": "Testing answer format compatibility",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            program_response = self.session.post(f"{BACKEND_URL}/programs", json=program_data)
            if program_response.status_code != 200:
                self.log_test("Wrong Format Test - Program Creation", False, f"Failed: {program_response.status_code}")
                return False
            
            program = program_response.json()
            program_id = program["id"]
            
            # Create final exam
            exam_data = {
                "title": "Format Test Exam",
                "description": "Testing answer format",
                "programId": program_id,
                "questions": [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "multiple_choice",
                        "question": "What is 2 + 2?",
                        "options": ["2", "3", "4", "5"],
                        "correctAnswer": "2",
                        "points": 50
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "true_false",
                        "question": "The sky is blue.",
                        "correctAnswer": "true",
                        "points": 50
                    }
                ],
                "timeLimit": 60,
                "passingScore": 75.0,
                "isPublished": True
            }
            
            test_response = self.session.post(f"{BACKEND_URL}/final-tests", json=exam_data)
            if test_response.status_code != 200:
                self.log_test("Wrong Format Test - Exam Creation", False, f"Failed: {test_response.status_code}")
                return False
            
            created_test = test_response.json()
            test_id = created_test["id"]
            questions = created_test.get('questions', [])
            
            # Test WRONG format (dictionary) - this is what frontend currently sends
            wrong_answers = {}
            for question in questions:
                q_id = question.get('id')
                if question.get('type') == 'multiple_choice':
                    wrong_answers[str(q_id)] = question.get('correctAnswer')
                elif question.get('type') == 'true_false':
                    wrong_answers[str(q_id)] = question.get('correctAnswer')
            
            wrong_submission = {
                "testId": test_id,
                "answers": wrong_answers,  # WRONG: Dictionary format
                "timeSpent": 120
            }
            
            print(f"    📤 Testing WRONG format (dictionary): {wrong_answers}")
            
            wrong_response = self.student_session.post(f"{BACKEND_URL}/final-test-attempts", json=wrong_submission)
            
            if wrong_response.status_code == 422:
                self.log_test("Wrong Format Test - Dictionary Format", True, 
                            f"Correctly rejected dictionary format with 422 error")
                return True
            else:
                self.log_test("Wrong Format Test - Dictionary Format", False, 
                            f"Expected 422 error, got: {wrong_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Wrong Format Test", False, f"Exception: {str(e)}")
            return False
    
    def test_correct_format_submission(self):
        """Test submission with correct format (list of dictionaries) - should work"""
        try:
            # Create test program and exam
            program_data = {
                "title": f"Correct Format Test {datetime.now().strftime('%H%M%S')}",
                "description": "Testing correct answer format",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            program_response = self.session.post(f"{BACKEND_URL}/programs", json=program_data)
            if program_response.status_code != 200:
                self.log_test("Correct Format Test - Program Creation", False, f"Failed: {program_response.status_code}")
                return False
            
            program = program_response.json()
            program_id = program["id"]
            
            # Create final exam
            exam_data = {
                "title": "Correct Format Test Exam",
                "description": "Testing correct answer format",
                "programId": program_id,
                "questions": [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "multiple_choice",
                        "question": "What is 5 + 3?",
                        "options": ["6", "7", "8", "9"],
                        "correctAnswer": "2",  # Index 2 = "8"
                        "points": 25
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "true_false",
                        "question": "Water boils at 100°C.",
                        "correctAnswer": "true",
                        "points": 25
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "multiple_choice",
                        "question": "What is the capital of Japan?",
                        "options": ["Seoul", "Beijing", "Tokyo", "Bangkok"],
                        "correctAnswer": "2",  # Index 2 = "Tokyo"
                        "points": 25
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "true_false",
                        "question": "The Earth is flat.",
                        "correctAnswer": "false",
                        "points": 25
                    }
                ],
                "timeLimit": 60,
                "passingScore": 75.0,
                "isPublished": True
            }
            
            test_response = self.session.post(f"{BACKEND_URL}/final-tests", json=exam_data)
            if test_response.status_code != 200:
                self.log_test("Correct Format Test - Exam Creation", False, f"Failed: {test_response.status_code}")
                return False
            
            created_test = test_response.json()
            test_id = created_test["id"]
            questions = created_test.get('questions', [])
            
            # Test CORRECT format (list of dictionaries)
            correct_answers = []
            for question in questions:
                q_id = question.get('id')
                if question.get('type') == 'multiple_choice':
                    correct_answers.append({
                        "questionId": str(q_id),
                        "answer": question.get('correctAnswer')
                    })
                elif question.get('type') == 'true_false':
                    correct_answers.append({
                        "questionId": str(q_id),
                        "answer": question.get('correctAnswer')
                    })
            
            correct_submission = {
                "testId": test_id,
                "answers": correct_answers,  # CORRECT: List of dictionaries format
                "timeSpent": 300
            }
            
            print(f"    📤 Testing CORRECT format (list of dictionaries):")
            for answer in correct_answers:
                print(f"      Question {answer['questionId'][:8]}...: {answer['answer']}")
            
            correct_response = self.student_session.post(f"{BACKEND_URL}/final-test-attempts", json=correct_submission)
            
            if correct_response.status_code == 200:
                result = correct_response.json()
                score = result.get('score', 0)
                passed = result.get('passed', False)
                
                print(f"    📊 EXAM RESULT:")
                print(f"      Score: {score}%")
                print(f"      Passed: {passed}")
                print(f"      Points: {result.get('pointsEarned', 0)}/{result.get('totalPoints', 0)}")
                
                if score == 100:
                    self.log_test("Correct Format Test - List Format", True, 
                                f"Perfect score achieved: {score}% with correct format")
                    return True
                elif score > 0:
                    self.log_test("Correct Format Test - List Format", True, 
                                f"Scoring working: {score}% (some answers may be wrong)")
                    return True
                else:
                    self.log_test("Correct Format Test - List Format", False, 
                                f"Still getting 0% score even with correct format")
                    return False
            else:
                self.log_test("Correct Format Test - List Format", False, 
                            f"Submission failed: {correct_response.status_code}, {correct_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Correct Format Test", False, f"Exception: {str(e)}")
            return False
    
    def test_comprehensive_scoring_scenarios(self):
        """Test various scoring scenarios to ensure the fix works"""
        try:
            # Create test program
            program_data = {
                "title": f"Comprehensive Scoring Test {datetime.now().strftime('%H%M%S')}",
                "description": "Testing all scoring scenarios",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            program_response = self.session.post(f"{BACKEND_URL}/programs", json=program_data)
            if program_response.status_code != 200:
                self.log_test("Comprehensive Test - Program Creation", False, f"Failed: {program_response.status_code}")
                return False
            
            program = program_response.json()
            program_id = program["id"]
            
            # Create comprehensive exam
            exam_data = {
                "title": "Comprehensive Scoring Test",
                "description": "Testing all scoring scenarios",
                "programId": program_id,
                "questions": [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "multiple_choice",
                        "question": "What is 10 × 5?",
                        "options": ["40", "45", "50", "55"],
                        "correctAnswer": "2",  # Index 2 = "50"
                        "points": 20
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "true_false",
                        "question": "Python is a programming language.",
                        "correctAnswer": "true",
                        "points": 20
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "multiple_choice",
                        "question": "Which planet is closest to the Sun?",
                        "options": ["Venus", "Mercury", "Earth", "Mars"],
                        "correctAnswer": "1",  # Index 1 = "Mercury"
                        "points": 20
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "true_false",
                        "question": "There are 24 hours in a day.",
                        "correctAnswer": "true",
                        "points": 20
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "multiple_choice",
                        "question": "What is the square root of 16?",
                        "options": ["2", "3", "4", "5"],
                        "correctAnswer": "2",  # Index 2 = "4"
                        "points": 20
                    }
                ],
                "timeLimit": 120,
                "passingScore": 60.0,
                "isPublished": True
            }
            
            test_response = self.session.post(f"{BACKEND_URL}/final-tests", json=exam_data)
            if test_response.status_code != 200:
                self.log_test("Comprehensive Test - Exam Creation", False, f"Failed: {test_response.status_code}")
                return False
            
            created_test = test_response.json()
            test_id = created_test["id"]
            questions = created_test.get('questions', [])
            
            # Test Scenario 1: All correct answers (should get 100%)
            all_correct = []
            for question in questions:
                all_correct.append({
                    "questionId": str(question.get('id')),
                    "answer": question.get('correctAnswer')
                })
            
            scenario1_response = self.student_session.post(f"{BACKEND_URL}/final-test-attempts", json={
                "testId": test_id,
                "answers": all_correct,
                "timeSpent": 600
            })
            
            if scenario1_response.status_code == 200:
                result1 = scenario1_response.json()
                score1 = result1.get('score', 0)
                self.log_test("Scenario 1 - All Correct", score1 == 100, 
                            f"Score: {score1}% (expected 100%)")
            else:
                self.log_test("Scenario 1 - All Correct", False, 
                            f"Failed: {scenario1_response.status_code}")
                return False
            
            # Test Scenario 2: Half correct answers (should get 60%)
            half_correct = []
            for i, question in enumerate(questions):
                if i < 3:  # First 3 correct (60 points out of 100)
                    half_correct.append({
                        "questionId": str(question.get('id')),
                        "answer": question.get('correctAnswer')
                    })
                else:  # Last 2 wrong
                    wrong_answer = "0" if question.get('type') == 'multiple_choice' else "false"
                    half_correct.append({
                        "questionId": str(question.get('id')),
                        "answer": wrong_answer
                    })
            
            scenario2_response = self.student_session.post(f"{BACKEND_URL}/final-test-attempts", json={
                "testId": test_id,
                "answers": half_correct,
                "timeSpent": 500
            })
            
            if scenario2_response.status_code == 200:
                result2 = scenario2_response.json()
                score2 = result2.get('score', 0)
                self.log_test("Scenario 2 - Half Correct", score2 == 60, 
                            f"Score: {score2}% (expected 60%)")
            else:
                self.log_test("Scenario 2 - Half Correct", False, 
                            f"Failed: {scenario2_response.status_code}")
                return False
            
            # Test Scenario 3: All wrong answers (should get 0%)
            all_wrong = []
            for question in questions:
                if question.get('type') == 'multiple_choice':
                    # Pick wrong answer (not the correct index)
                    correct_idx = int(question.get('correctAnswer', '0'))
                    wrong_idx = (correct_idx + 1) % len(question.get('options', []))
                    all_wrong.append({
                        "questionId": str(question.get('id')),
                        "answer": str(wrong_idx)
                    })
                else:  # true_false
                    wrong_answer = "false" if question.get('correctAnswer') == "true" else "true"
                    all_wrong.append({
                        "questionId": str(question.get('id')),
                        "answer": wrong_answer
                    })
            
            scenario3_response = self.student_session.post(f"{BACKEND_URL}/final-test-attempts", json={
                "testId": test_id,
                "answers": all_wrong,
                "timeSpent": 400
            })
            
            if scenario3_response.status_code == 200:
                result3 = scenario3_response.json()
                score3 = result3.get('score', 0)
                self.log_test("Scenario 3 - All Wrong", score3 == 0, 
                            f"Score: {score3}% (expected 0%)")
                return True
            else:
                self.log_test("Scenario 3 - All Wrong", False, 
                            f"Failed: {scenario3_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Comprehensive Test", False, f"Exception: {str(e)}")
            return False
    
    def run_fix_validation(self):
        """Run comprehensive validation of the quiz scoring fix"""
        print("🔧 QUIZ SCORING FIX VALIDATION")
        print("=" * 80)
        print("ROOT CAUSE: Frontend sends answers as dictionary, backend expects list")
        print("SOLUTION: Frontend must send answers as list of {questionId, answer} objects")
        print("=" * 80)
        
        # Step 1: Authenticate both users
        if not self.authenticate_admin():
            print("❌ Admin authentication failed. Cannot proceed.")
            return False
        
        if not self.authenticate_student():
            print("❌ Student authentication failed. Cannot proceed.")
            return False
        
        # Step 2: Test wrong format (should fail)
        print("\n🔍 PHASE 1: Testing Wrong Format (Dictionary)")
        print("-" * 50)
        self.test_wrong_format_submission()
        
        # Step 3: Test correct format (should work)
        print("\n🔍 PHASE 2: Testing Correct Format (List of Dictionaries)")
        print("-" * 50)
        self.test_correct_format_submission()
        
        # Step 4: Test comprehensive scenarios
        print("\n🔍 PHASE 3: Testing Comprehensive Scoring Scenarios")
        print("-" * 50)
        self.test_comprehensive_scoring_scenarios()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 FIX VALIDATION SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print(f"\n🎉 QUIZ SCORING FIX VALIDATED SUCCESSFULLY!")
            print(f"📋 FRONTEND FIX REQUIRED:")
            print(f"   Change: answers: {{questionId: answer}} ")
            print(f"   To:     answers: [{{questionId: 'id', answer: 'value'}}]")
        else:
            print(f"\n❌ Quiz scoring issues still exist")
            
        failed_tests = [r for r in self.test_results if not r["success"]]
        if failed_tests:
            print(f"\nFailed Tests:")
            for result in failed_tests:
                print(f"  - {result['test']}: {result['details']}")
        
        return success_rate >= 80

if __name__ == "__main__":
    fixer = QuizScoringFixer()
    success = fixer.run_fix_validation()
    sys.exit(0 if success else 1)