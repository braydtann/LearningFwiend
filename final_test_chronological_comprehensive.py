#!/usr/bin/env python3
"""
Comprehensive Final Test with Chronological Order Questions Testing
Testing final test submission endpoint with chronological order answers and scoring.
"""

import requests
import json
import sys
from datetime import datetime
import uuid

class FinalTestChronologicalTester:
    def __init__(self):
        # Use the production URL from frontend/.env
        self.base_url = "https://lms-analytics-hub.preview.emergentagent.com/api"
        self.admin_token = None
        self.student_token = None
        self.test_results = []
        
        # Test credentials from review request
        self.admin_credentials = {
            "username_or_email": "brayden.t@covesmart.com",
            "password": "Hawaii2020!"
        }
        
        self.student_credentials = {
            "username_or_email": "karlo.student@alder.com", 
            "password": "StudentPermanent123!"
        }
        
        print(f"🔧 Backend URL: {self.base_url}")
        print("🎯 FINAL TEST CHRONOLOGICAL ORDER FUNCTIONALITY TESTING")
        print("=" * 80)

    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")

    def authenticate_admin(self):
        """Test admin authentication"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=self.admin_credentials,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('access_token')
                user_info = data.get('user', {})
                self.log_result(
                    "Admin Authentication", 
                    True, 
                    f"Logged in as {user_info.get('full_name')} ({user_info.get('role')})"
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Error: {str(e)}")
            return False

    def authenticate_student(self):
        """Test student authentication"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=self.student_credentials,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get('access_token')
                user_info = data.get('user', {})
                self.log_result(
                    "Student Authentication", 
                    True, 
                    f"Logged in as {user_info.get('full_name')} ({user_info.get('role')})"
                )
                return True
            else:
                self.log_result(
                    "Student Authentication", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                return False
                
        except Exception as e:
            self.log_result("Student Authentication", False, f"Error: {str(e)}")
            return False

    def get_or_create_program(self):
        """Get existing program or create one for testing"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # First try to get existing programs
            response = requests.get(
                f"{self.base_url}/programs",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                programs = response.json()
                if programs:
                    program = programs[0]  # Use first available program
                    self.log_result(
                        "Get Existing Program", 
                        True, 
                        f"Using existing program '{program['title']}'"
                    )
                    return program
            
            # If no programs exist, create one
            program_data = {
                "title": "Final Test Program - Chronological Order",
                "description": "A program for testing chronological order questions in final tests",
                "departmentId": None,
                "duration": "2 weeks",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            response = requests.post(
                f"{self.base_url}/programs",
                headers=headers,
                json=program_data,
                timeout=30
            )
            
            if response.status_code == 200:
                program = response.json()
                self.log_result(
                    "Create Test Program", 
                    True, 
                    f"Created program '{program['title']}'"
                )
                return program
            else:
                self.log_result(
                    "Create Test Program", 
                    False, 
                    f"Status: {response.status_code}"
                )
                return None
                
        except Exception as e:
            self.log_result("Get/Create Program", False, f"Error: {str(e)}")
            return None

    def create_final_test_with_chronological_questions(self, program):
        """Create a final test with chronological order questions"""
        try:
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            final_test_data = {
                "title": "Chronological Order Final Test",
                "description": "Final test with chronological order questions to test ordering functionality",
                "programId": program['id'],
                "timeLimit": 45,  # 45 minutes
                "maxAttempts": 3,
                "passingScore": 70.0,
                "shuffleQuestions": False,
                "showResults": True,
                "isPublished": True,
                "questions": [
                    {
                        "type": "chronological-order",
                        "question": "Arrange these major historical events in chronological order (earliest to latest):",
                        "items": [
                            "World War II ends (1945)",
                            "American Civil War begins (1861)", 
                            "Moon landing (1969)",
                            "Fall of Berlin Wall (1989)"
                        ],
                        "correctOrder": [1, 0, 2, 3],  # Civil War, WWII ends, Moon landing, Berlin Wall
                        "points": 25,
                        "explanation": "American Civil War (1861), WWII ends (1945), Moon landing (1969), Berlin Wall falls (1989)"
                    },
                    {
                        "type": "chronological-order", 
                        "question": "Put these technological inventions in chronological order:",
                        "items": [
                            "Personal Computer (1970s)",
                            "Telephone (1876)",
                            "Internet (1960s-1970s)", 
                            "Television (1920s)"
                        ],
                        "correctOrder": [1, 3, 2, 0],  # Telephone, TV, Internet, PC
                        "points": 25,
                        "explanation": "Telephone (1876), Television (1920s), Internet (1960s-1970s), Personal Computer (1970s)"
                    },
                    {
                        "type": "multiple-choice",
                        "question": "Which chronological ordering principle is most important when studying history?",
                        "options": [
                            "Alphabetical order",
                            "Temporal sequence",
                            "Geographical location", 
                            "Importance ranking"
                        ],
                        "correctAnswer": "1",  # Temporal sequence
                        "points": 15,
                        "explanation": "Temporal sequence (chronological order) is fundamental to understanding historical causation and context."
                    },
                    {
                        "type": "chronological-order",
                        "question": "Order these scientific discoveries chronologically:",
                        "items": [
                            "DNA structure discovered (1953)",
                            "Penicillin discovered (1928)",
                            "Theory of relativity (1905)",
                            "Atomic structure model (1911)"
                        ],
                        "correctOrder": [2, 3, 1, 0],  # Relativity, Atomic model, Penicillin, DNA
                        "points": 25,
                        "explanation": "Theory of relativity (1905), Atomic structure (1911), Penicillin (1928), DNA structure (1953)"
                    },
                    {
                        "type": "true_false",
                        "question": "Chronological order questions test a student's ability to sequence events in time.",
                        "correctAnswer": "true",
                        "points": 10,
                        "explanation": "Chronological order questions specifically assess temporal sequencing skills."
                    }
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/final-tests",
                headers=headers,
                json=final_test_data,
                timeout=30
            )
            
            if response.status_code == 200:
                test_data = response.json()
                self.log_result(
                    "Create Final Test with Chronological Questions", 
                    True, 
                    f"Created test '{test_data['title']}' with {test_data['questionCount']} questions ({test_data['totalPoints']} points)"
                )
                return test_data
            else:
                self.log_result(
                    "Create Final Test with Chronological Questions", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text[:500]}"
                )
                return None
                
        except Exception as e:
            self.log_result("Create Final Test with Chronological Questions", False, f"Error: {str(e)}")
            return None

    def verify_chronological_data_structure_in_final_test(self, test_data):
        """Verify chronological order questions have proper data structure in final test"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(
                f"{self.base_url}/final-tests/{test_data['id']}?include_answers=true",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                final_test = response.json()
                
                # Find chronological order questions
                chronological_questions = [
                    q for q in final_test.get('questions', []) 
                    if q.get('type') == 'chronological-order'
                ]
                
                if not chronological_questions:
                    self.log_result(
                        "Verify Chronological Data Structure in Final Test", 
                        False, 
                        "No chronological-order questions found in final test"
                    )
                    return False
                
                # Verify each chronological question
                all_valid = True
                for i, question in enumerate(chronological_questions):
                    checks = []
                    checks.append(("has items array", isinstance(question.get('items'), list)))
                    checks.append(("has correctOrder array", isinstance(question.get('correctOrder'), list)))
                    checks.append(("items not empty", len(question.get('items', [])) > 0))
                    checks.append(("correctOrder not empty", len(question.get('correctOrder', [])) > 0))
                    checks.append(("arrays same length", len(question.get('items', [])) == len(question.get('correctOrder', []))))
                    checks.append(("has points", question.get('points', 0) > 0))
                    
                    question_valid = all(check[1] for check in checks)
                    if not question_valid:
                        all_valid = False
                    
                    details = f"Question {i+1}: " + ", ".join([f"{check[0]}: {'✓' if check[1] else '✗'}" for check in checks])
                    print(f"    {details}")
                
                self.log_result(
                    "Verify Chronological Data Structure in Final Test", 
                    all_valid, 
                    f"Verified {len(chronological_questions)} chronological questions in final test"
                )
                return all_valid
            else:
                self.log_result(
                    "Verify Chronological Data Structure in Final Test", 
                    False, 
                    f"Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result("Verify Chronological Data Structure in Final Test", False, f"Error: {str(e)}")
            return False

    def test_final_test_submission_correct_chronological_answers(self, test_data):
        """Test final test submission with correct chronological order answers"""
        try:
            headers = {
                "Authorization": f"Bearer {self.student_token}",
                "Content-Type": "application/json"
            }
            
            # Submit correct answers for all questions
            # Based on the test structure: 3 chronological + 1 multiple choice + 1 true/false
            correct_answers = [
                [1, 0, 2, 3],  # First chronological question - correct order
                [1, 3, 2, 0],  # Second chronological question - correct order  
                "1",           # Multiple choice - correct answer
                [2, 3, 1, 0],  # Third chronological question - correct order
                "true"         # True/false - correct answer
            ]
            
            submission_data = {
                "finalTestId": test_data['id'],
                "answers": correct_answers
            }
            
            response = requests.post(
                f"{self.base_url}/final-test-attempts",
                headers=headers,
                json=submission_data,
                timeout=30
            )
            
            if response.status_code == 200:
                attempt_result = response.json()
                score = attempt_result.get('score', 0)
                is_passed = attempt_result.get('isPassed', False)
                points_earned = attempt_result.get('pointsEarned', 0)
                total_points = attempt_result.get('totalPoints', 0)
                
                self.log_result(
                    "Final Test Submission (Correct Chronological Answers)", 
                    True, 
                    f"Score: {score}%, Passed: {is_passed}, Points: {points_earned}/{total_points}"
                )
                return attempt_result
            else:
                self.log_result(
                    "Final Test Submission (Correct Chronological Answers)", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text[:500]}"
                )
                return None
                
        except Exception as e:
            self.log_result("Final Test Submission (Correct Chronological Answers)", False, f"Error: {str(e)}")
            return None

    def test_final_test_submission_incorrect_chronological_answers(self, test_data):
        """Test final test submission with incorrect chronological order answers"""
        try:
            headers = {
                "Authorization": f"Bearer {self.student_token}",
                "Content-Type": "application/json"
            }
            
            # Submit incorrect answers (reversed order for chronological questions)
            incorrect_answers = [
                [3, 2, 0, 1],  # First chronological question - reversed order (incorrect)
                [0, 2, 3, 1],  # Second chronological question - wrong order (incorrect)
                "0",           # Multiple choice - wrong answer
                [0, 1, 3, 2],  # Third chronological question - wrong order (incorrect)
                "false"        # True/false - wrong answer
            ]
            
            submission_data = {
                "finalTestId": test_data['id'],
                "answers": incorrect_answers
            }
            
            response = requests.post(
                f"{self.base_url}/final-test-attempts",
                headers=headers,
                json=submission_data,
                timeout=30
            )
            
            if response.status_code == 200:
                attempt_result = response.json()
                score = attempt_result.get('score', 0)
                is_passed = attempt_result.get('isPassed', False)
                points_earned = attempt_result.get('pointsEarned', 0)
                total_points = attempt_result.get('totalPoints', 0)
                
                self.log_result(
                    "Final Test Submission (Incorrect Chronological Answers)", 
                    True, 
                    f"Score: {score}%, Passed: {is_passed}, Points: {points_earned}/{total_points}"
                )
                return attempt_result
            else:
                self.log_result(
                    "Final Test Submission (Incorrect Chronological Answers)", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text[:500]}"
                )
                return None
                
        except Exception as e:
            self.log_result("Final Test Submission (Incorrect Chronological Answers)", False, f"Error: {str(e)}")
            return None

    def test_chronological_scoring_logic(self, correct_attempt, incorrect_attempt):
        """Verify chronological order scoring logic works correctly"""
        try:
            if not correct_attempt or not incorrect_attempt:
                self.log_result(
                    "Chronological Scoring Logic Verification", 
                    False, 
                    "Missing attempt data for comparison"
                )
                return False
            
            correct_score = correct_attempt.get('score', 0)
            incorrect_score = incorrect_attempt.get('score', 0)
            correct_passed = correct_attempt.get('isPassed', False)
            incorrect_passed = incorrect_attempt.get('isPassed', False)
            
            # Verify scoring logic
            checks = []
            checks.append(("Correct answers score higher", correct_score > incorrect_score))
            checks.append(("Correct answers pass", correct_passed == True))
            checks.append(("Incorrect answers fail", incorrect_passed == False))
            checks.append(("Score difference significant", (correct_score - incorrect_score) >= 50))
            
            all_valid = all(check[1] for check in checks)
            details = ", ".join([f"{check[0]}: {'✓' if check[1] else '✗'}" for check in checks])
            details += f" (Correct: {correct_score}%, Incorrect: {incorrect_score}%)"
            
            self.log_result(
                "Chronological Scoring Logic Verification", 
                all_valid, 
                details
            )
            return all_valid
                
        except Exception as e:
            self.log_result("Chronological Scoring Logic Verification", False, f"Error: {str(e)}")
            return False

    def get_student_final_test_attempts(self, test_id):
        """Get student's final test attempts"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.get(
                f"{self.base_url}/final-test-attempts?test_id={test_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                attempts = response.json()
                self.log_result(
                    "Get Student Final Test Attempts", 
                    True, 
                    f"Retrieved {len(attempts)} attempts"
                )
                return attempts
            else:
                self.log_result(
                    "Get Student Final Test Attempts", 
                    False, 
                    f"Status: {response.status_code}"
                )
                return []
                
        except Exception as e:
            self.log_result("Get Student Final Test Attempts", False, f"Error: {str(e)}")
            return []

    def run_comprehensive_test(self):
        """Run all chronological order final test functionality tests"""
        print("🎯 FINAL TEST CHRONOLOGICAL ORDER FUNCTIONALITY TESTING INITIATED")
        print("Testing chronological order functionality in final exams as requested")
        print("=" * 80)
        
        # Step 1: Authentication
        print("\n📋 STEP 1: AUTHENTICATION TESTING")
        if not self.authenticate_admin():
            print("❌ Admin authentication failed - cannot proceed")
            return False
            
        if not self.authenticate_student():
            print("❌ Student authentication failed - cannot proceed")
            return False
        
        # Step 2: Get or Create Program
        print("\n📋 STEP 2: GET/CREATE PROGRAM FOR FINAL TEST")
        program = self.get_or_create_program()
        if not program:
            print("❌ Program setup failed")
            return False
        
        # Step 3: Create Final Test with Chronological Questions
        print("\n📋 STEP 3: CREATE FINAL TEST WITH CHRONOLOGICAL ORDER QUESTIONS")
        test_data = self.create_final_test_with_chronological_questions(program)
        if not test_data:
            print("❌ Final test creation failed")
            return False
        
        # Step 4: Verify Chronological Data Structure
        print("\n📋 STEP 4: VERIFY CHRONOLOGICAL ORDER DATA STRUCTURE IN FINAL TEST")
        if not self.verify_chronological_data_structure_in_final_test(test_data):
            print("❌ Data structure verification failed")
            return False
        
        # Step 5: Test Correct Chronological Answers
        print("\n📋 STEP 5: TEST FINAL TEST SUBMISSION WITH CORRECT CHRONOLOGICAL ANSWERS")
        correct_attempt = self.test_final_test_submission_correct_chronological_answers(test_data)
        if not correct_attempt:
            print("❌ Correct answers submission failed")
            return False
        
        # Step 6: Test Incorrect Chronological Answers
        print("\n📋 STEP 6: TEST FINAL TEST SUBMISSION WITH INCORRECT CHRONOLOGICAL ANSWERS")
        incorrect_attempt = self.test_final_test_submission_incorrect_chronological_answers(test_data)
        if not incorrect_attempt:
            print("❌ Incorrect answers submission failed")
            return False
        
        # Step 7: Verify Scoring Logic
        print("\n📋 STEP 7: VERIFY CHRONOLOGICAL ORDER SCORING LOGIC")
        if not self.test_chronological_scoring_logic(correct_attempt, incorrect_attempt):
            print("❌ Scoring logic verification failed")
            return False
        
        # Step 8: Get Student Attempts
        print("\n📋 STEP 8: VERIFY STUDENT CAN ACCESS FINAL TEST ATTEMPTS")
        attempts = self.get_student_final_test_attempts(test_data['id'])
        if len(attempts) < 2:
            print("❌ Student attempts retrieval failed")
            return False
        
        return True

    def print_summary(self):
        """Print final summary of all test results"""
        print("\n" + "=" * 80)
        print("🎉 FINAL TEST CHRONOLOGICAL ORDER TESTING SUMMARY")
        print("=" * 80)
        
        passed_tests = [r for r in self.test_results if r['success']]
        failed_tests = [r for r in self.test_results if not r['success']]
        
        print(f"✅ PASSED: {len(passed_tests)}/{len(self.test_results)} tests")
        print(f"❌ FAILED: {len(failed_tests)}/{len(self.test_results)} tests")
        
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
        
        success_rate = (len(passed_tests) / len(self.test_results)) * 100 if self.test_results else 0
        print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}%")
        
        print("\n📋 CHRONOLOGICAL ORDER FUNCTIONALITY VERIFIED:")
        print("  • Final test creation with chronological order questions")
        print("  • Chronological order data structure (items[], correctOrder[])")
        print("  • Final test submission endpoint with chronological answers")
        print("  • Chronological order scoring logic (correct vs incorrect)")
        print("  • Student access to final test attempts")
        
        if success_rate >= 80:
            print("\n🎉 CHRONOLOGICAL ORDER FINAL TEST FUNCTIONALITY IS WORKING CORRECTLY")
        else:
            print("\n⚠️  CHRONOLOGICAL ORDER FINAL TEST FUNCTIONALITY NEEDS ATTENTION")
        
        return success_rate >= 80


def main():
    """Main test execution"""
    tester = FinalTestChronologicalTester()
    
    try:
        success = tester.run_comprehensive_test()
        tester.print_summary()
        
        if success:
            print("\n✅ All chronological order final test functionality is working correctly")
            print("📝 Chronological order questions tested in final exam context")
            sys.exit(0)
        else:
            print("\n❌ Issues found in chronological order final test functionality")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()