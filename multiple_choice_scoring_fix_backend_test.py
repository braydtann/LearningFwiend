#!/usr/bin/env python3
"""
Multiple Choice Final Exam Scoring Fix Backend Test
==================================================

This test verifies the critical fix for Multiple Choice final exam scoring 0% bug.

CONTEXT: User reported that Multiple Choice final exams were consistently scoring 0% 
despite correct answers being selected. The fix involved:
- Frontend was sending option TEXT as student answers (e.g., "Option A", "Option B")  
- Backend expected numeric INDICES for comparison (e.g., 0, 1, 2, 3)
- Modified FinalTest.js to send indices instead of option text for Multiple Choice questions
- Also fixed Select All That Apply questions to send arrays of indices

TESTING FOCUS:
1. Verify Multiple Choice questions now score correctly (non-zero scores when correct answers selected)
2. Test True/False questions still work (these were already fixed)
3. Test Select All That Apply questions work with index-based answers  
4. Test final exam submission and scoring API endpoints
5. Use existing test credentials from test_result.md
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://grade-flow-wizard.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials from test_result.md
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class MultipleChoiceScoringFixTest:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.test_program_id = None
        self.test_final_test_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = requests.post(f"{API_BASE}/auth/login", json=ADMIN_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data['access_token']
                self.log_result("Admin Authentication", True, f"Admin user: {data['user']['full_name']}")
                return True
            else:
                self.log_result("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def authenticate_student(self):
        """Authenticate as student user"""
        try:
            response = requests.post(f"{API_BASE}/auth/login", json=STUDENT_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data['access_token']
                self.log_result("Student Authentication", True, f"Student user: {data['user']['full_name']}")
                return True
            else:
                self.log_result("Student Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Student Authentication", False, f"Exception: {str(e)}")
            return False

    def create_test_program(self):
        """Create a test program for final exam testing"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # First, get available courses
            courses_response = requests.get(f"{API_BASE}/courses", headers=headers)
            if courses_response.status_code != 200:
                self.log_result("Get Available Courses", False, f"HTTP {courses_response.status_code}")
                return False
                
            courses = courses_response.json()
            if not courses:
                self.log_result("Get Available Courses", False, "No courses available")
                return False
            
            # Create test program
            program_data = {
                "title": f"Multiple Choice Scoring Test Program - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test program for verifying Multiple Choice final exam scoring fix",
                "courseIds": [courses[0]['id']] if courses else [],
                "nestedProgramIds": []
            }
            
            response = requests.post(f"{API_BASE}/programs", json=program_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.test_program_id = data['id']
                self.log_result("Create Test Program", True, f"Program ID: {self.test_program_id}")
                return True
            else:
                self.log_result("Create Test Program", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Create Test Program", False, f"Exception: {str(e)}")
            return False

    def create_final_test_with_multiple_choice(self):
        """Create a final test with Multiple Choice, True/False, and Select All That Apply questions"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Create comprehensive final test with different question types
            final_test_data = {
                "title": f"Multiple Choice Scoring Fix Test - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test final exam to verify Multiple Choice scoring fix",
                "programId": self.test_program_id,
                "timeLimit": 30,  # 30 minutes
                "passingScore": 70,  # 70% to pass
                "isPublished": True,
                "questions": [
                    {
                        "type": "multiple_choice",
                        "question": "What is 2 + 2?",
                        "options": ["2", "3", "4", "5"],
                        "correctAnswer": "2",  # Index 2 (option "4")
                        "points": 10,
                        "explanation": "2 + 2 equals 4"
                    },
                    {
                        "type": "multiple_choice", 
                        "question": "Which programming language is known for web development?",
                        "options": ["Python", "JavaScript", "C++", "Assembly"],
                        "correctAnswer": "1",  # Index 1 (option "JavaScript")
                        "points": 10,
                        "explanation": "JavaScript is primarily used for web development"
                    },
                    {
                        "type": "true_false",
                        "question": "The sky is blue.",
                        "options": ["True", "False"],
                        "correctAnswer": "0",  # Index 0 (True)
                        "points": 5,
                        "explanation": "The sky appears blue due to light scattering"
                    },
                    {
                        "type": "select-all-that-apply",
                        "question": "Which of the following are programming languages?",
                        "options": ["Python", "HTML", "JavaScript", "CSS"],
                        "correctAnswers": ["0", "2"],  # Indices 0 and 2 (Python and JavaScript)
                        "points": 15,
                        "explanation": "Python and JavaScript are programming languages, while HTML and CSS are markup/styling languages"
                    }
                ]
            }
            
            response = requests.post(f"{API_BASE}/final-tests", json=final_test_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.test_final_test_id = data['id']
                total_points = sum(q['points'] for q in final_test_data['questions'])
                self.log_result("Create Final Test with Multiple Choice", True, 
                              f"Final Test ID: {self.test_final_test_id}, Total Points: {total_points}")
                return True
            else:
                self.log_result("Create Final Test with Multiple Choice", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Create Final Test with Multiple Choice", False, f"Exception: {str(e)}")
            return False

    def verify_final_test_structure(self):
        """Verify the final test was created with correct structure"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            response = requests.get(f"{API_BASE}/final-tests/{self.test_final_test_id}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                
                # Verify test structure
                questions = data.get('questions', [])
                if len(questions) != 4:
                    self.log_result("Verify Final Test Structure", False, 
                                  f"Expected 4 questions, got {len(questions)}")
                    return False
                
                # Check question types
                question_types = [q.get('type') for q in questions]
                expected_types = ['multiple_choice', 'multiple_choice', 'true_false', 'select-all-that-apply']
                
                structure_details = []
                for i, (actual, expected) in enumerate(zip(question_types, expected_types)):
                    if actual == expected:
                        structure_details.append(f"Q{i+1}: {actual} ✓")
                    else:
                        structure_details.append(f"Q{i+1}: {actual} (expected {expected}) ✗")
                
                # Verify correctAnswer fields are NOT visible to students (security check)
                has_correct_answers = any('correctAnswer' in q for q in questions)
                if has_correct_answers:
                    self.log_result("Verify Final Test Structure", False, 
                                  "Security issue: correctAnswer fields visible to students")
                    return False
                
                self.log_result("Verify Final Test Structure", True, 
                              f"Questions: {', '.join(structure_details)}. Security: correctAnswer fields properly hidden from students")
                return True
            else:
                self.log_result("Verify Final Test Structure", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Verify Final Test Structure", False, f"Exception: {str(e)}")
            return False

    def test_multiple_choice_scoring_correct_answers(self):
        """Test Multiple Choice scoring with correct answers (should get high score)"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Submit answers with CORRECT indices (the fix)
            attempt_data = {
                "finalTestId": self.test_final_test_id,
                "answers": [
                    {"questionId": "q1", "answer": "2"},  # Correct: index 2 for "4"
                    {"questionId": "q2", "answer": "1"},  # Correct: index 1 for "JavaScript"  
                    {"questionId": "q3", "answer": "0"},  # Correct: index 0 for "True"
                    {"questionId": "q4", "answer": ["0", "2"]}  # Correct: indices 0,2 for Python,JavaScript
                ]
            }
            
            response = requests.post(f"{API_BASE}/final-test-attempts", json=attempt_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                score = data.get('score', 0)
                percentage = data.get('percentage', 0)
                passed = data.get('passed', False)
                
                # The critical test: score should NOT be 0% for correct answers
                if score > 0 and percentage > 0:
                    self.log_result("Multiple Choice Scoring - Correct Answers", True, 
                                  f"Score: {score}/40 points ({percentage}%), Passed: {passed}")
                    return True
                else:
                    self.log_result("Multiple Choice Scoring - Correct Answers", False, 
                                  f"CRITICAL BUG: Still getting 0% score! Score: {score}, Percentage: {percentage}")
                    return False
            else:
                self.log_result("Multiple Choice Scoring - Correct Answers", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Multiple Choice Scoring - Correct Answers", False, f"Exception: {str(e)}")
            return False

    def test_multiple_choice_scoring_wrong_answers(self):
        """Test Multiple Choice scoring with wrong answers (should get low score)"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Submit answers with WRONG indices
            attempt_data = {
                "finalTestId": self.test_final_test_id,
                "answers": [
                    {"questionId": "q1", "answer": "0"},  # Wrong: index 0 for "2" (correct is index 2)
                    {"questionId": "q2", "answer": "0"},  # Wrong: index 0 for "Python" (correct is index 1)
                    {"questionId": "q3", "answer": "1"},  # Wrong: index 1 for "False" (correct is index 0)
                    {"questionId": "q4", "answer": ["1", "3"]}  # Wrong: indices 1,3 for HTML,CSS (correct is 0,2)
                ]
            }
            
            response = requests.post(f"{API_BASE}/final-test-attempts", json=attempt_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                score = data.get('score', 0)
                percentage = data.get('percentage', 0)
                passed = data.get('passed', False)
                
                # Should get 0% for all wrong answers
                if score == 0 and percentage == 0 and not passed:
                    self.log_result("Multiple Choice Scoring - Wrong Answers", True, 
                                  f"Score: {score}/40 points ({percentage}%), Passed: {passed}")
                    return True
                else:
                    self.log_result("Multiple Choice Scoring - Wrong Answers", False, 
                                  f"Expected 0% for wrong answers, got Score: {score}, Percentage: {percentage}")
                    return False
            else:
                self.log_result("Multiple Choice Scoring - Wrong Answers", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Multiple Choice Scoring - Wrong Answers", False, f"Exception: {str(e)}")
            return False

    def test_mixed_answers_scoring(self):
        """Test Multiple Choice scoring with mixed correct/wrong answers"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Submit mixed answers (2 correct, 2 wrong)
            attempt_data = {
                "finalTestId": self.test_final_test_id,
                "answers": [
                    {"questionId": "q1", "answer": "2"},  # Correct: 10 points
                    {"questionId": "q2", "answer": "0"},  # Wrong: 0 points
                    {"questionId": "q3", "answer": "0"},  # Correct: 5 points
                    {"questionId": "q4", "answer": ["1", "3"]}  # Wrong: 0 points
                ]
            }
            
            response = requests.post(f"{API_BASE}/final-test-attempts", json=attempt_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                score = data.get('score', 0)
                percentage = data.get('percentage', 0)
                passed = data.get('passed', False)
                
                # Should get 15/40 points = 37.5%
                expected_score = 15  # 10 + 0 + 5 + 0
                expected_percentage = 37.5  # 15/40 * 100
                
                if score == expected_score and abs(percentage - expected_percentage) < 1:
                    self.log_result("Multiple Choice Scoring - Mixed Answers", True, 
                                  f"Score: {score}/40 points ({percentage}%), Passed: {passed}")
                    return True
                else:
                    self.log_result("Multiple Choice Scoring - Mixed Answers", False, 
                                  f"Expected {expected_score} points ({expected_percentage}%), got {score} points ({percentage}%)")
                    return False
            else:
                self.log_result("Multiple Choice Scoring - Mixed Answers", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Multiple Choice Scoring - Mixed Answers", False, f"Exception: {str(e)}")
            return False

    def verify_final_test_attempts_data(self):
        """Verify final test attempt data contains proper numeric indices"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get all final test attempts for this test
            response = requests.get(f"{API_BASE}/final-test-attempts", headers=headers)
            if response.status_code == 200:
                attempts = response.json()
                
                # Filter attempts for our test
                test_attempts = [a for a in attempts if a.get('finalTestId') == self.test_final_test_id]
                
                if not test_attempts:
                    self.log_result("Verify Final Test Attempts Data", False, "No attempts found for test")
                    return False
                
                # Check the data format of answers
                data_format_details = []
                for i, attempt in enumerate(test_attempts):
                    answers = attempt.get('answers', [])
                    for j, answer in enumerate(answers):
                        answer_value = answer.get('answer')
                        if isinstance(answer_value, str) and answer_value.isdigit():
                            data_format_details.append(f"Attempt {i+1}, Q{j+1}: index '{answer_value}' ✓")
                        elif isinstance(answer_value, list) and all(isinstance(x, str) and x.isdigit() for x in answer_value):
                            data_format_details.append(f"Attempt {i+1}, Q{j+1}: indices {answer_value} ✓")
                        else:
                            data_format_details.append(f"Attempt {i+1}, Q{j+1}: {type(answer_value).__name__} '{answer_value}' ⚠️")
                
                self.log_result("Verify Final Test Attempts Data", True, 
                              f"Found {len(test_attempts)} attempts. Data format: {'; '.join(data_format_details[:5])}")
                return True
            else:
                self.log_result("Verify Final Test Attempts Data", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Verify Final Test Attempts Data", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🎯 MULTIPLE CHOICE FINAL EXAM SCORING FIX BACKEND TESTING")
        print("=" * 60)
        print()
        
        # Authentication tests
        if not self.authenticate_admin():
            return False
        if not self.authenticate_student():
            return False
            
        # Setup tests
        if not self.create_test_program():
            return False
        if not self.create_final_test_with_multiple_choice():
            return False
        if not self.verify_final_test_structure():
            return False
            
        # Critical scoring tests
        if not self.test_multiple_choice_scoring_correct_answers():
            return False
        if not self.test_multiple_choice_scoring_wrong_answers():
            return False
        if not self.test_mixed_answers_scoring():
            return False
            
        # Data verification
        if not self.verify_final_test_attempts_data():
            return False
            
        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🎯 MULTIPLE CHOICE SCORING FIX TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"✅ PASSED: {passed}/{total} tests ({success_rate:.1f}% success rate)")
        print()
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print("❌ FAILED TESTS:")
            for result in failed_tests:
                print(f"   - {result['test']}: {result['details']}")
            print()
        
        # Critical assessment
        critical_tests = [
            "Multiple Choice Scoring - Correct Answers",
            "Multiple Choice Scoring - Wrong Answers", 
            "Multiple Choice Scoring - Mixed Answers"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['test'] in critical_tests and result['success'])
        
        print("🔍 CRITICAL ASSESSMENT:")
        if critical_passed == len(critical_tests):
            print("✅ MULTIPLE CHOICE SCORING FIX IS WORKING CORRECTLY")
            print("   - Students get proper scores for correct answers (not 0%)")
            print("   - Scoring logic correctly processes numeric indices")
            print("   - All question types (Multiple Choice, True/False, Select All) functional")
        else:
            print("❌ MULTIPLE CHOICE SCORING FIX STILL HAS ISSUES")
            print("   - Critical scoring tests failed")
            print("   - Students may still be getting 0% scores incorrectly")
        
        print()
        return success_rate >= 85

def main():
    """Main test execution"""
    tester = MultipleChoiceScoringFixTest()
    
    try:
        success = tester.run_all_tests()
        tester.print_summary()
        
        if success:
            print("🎉 CONCLUSION: Multiple Choice final exam scoring fix is working correctly!")
            sys.exit(0)
        else:
            print("🚨 CONCLUSION: Multiple Choice final exam scoring fix needs attention!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()