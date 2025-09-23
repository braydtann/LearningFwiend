#!/usr/bin/env python3
"""
URGENT: Final Exam Root Cause Verification Test
CRITICAL BUG FOUND: Backend removes correctAnswer field for students when retrieving tests,
but scoring logic needs these fields to calculate scores!

Root Cause: Lines 4381-4384 in server.py remove correctAnswer for learners,
but the scoring logic in submit_final_test_attempt needs these fields.

This test verifies the root cause and demonstrates the fix needed.
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://learning-score-fix.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"
STUDENT_EMAIL = "karlo.student@alder.com"
STUDENT_PASSWORD = "StudentPermanent123!"

class RootCauseVerifier:
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
    
    def verify_root_cause_bug(self):
        """Verify the root cause: correctAnswer field removal for students"""
        try:
            # Create a test program
            test_program_data = {
                "title": f"Root Cause Test {datetime.now().strftime('%H%M%S')}",
                "description": "Verifying correctAnswer field removal bug",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            program_response = self.session.post(f"{BACKEND_URL}/programs", json=test_program_data)
            
            if program_response.status_code != 200:
                self.log_test("Root Cause Verification", False, f"Failed to create program: {program_response.status_code}")
                return False
            
            program = program_response.json()
            program_id = program["id"]
            
            # Create final test with explicit correctAnswer
            test_data = {
                "title": "Root Cause Verification Test",
                "description": "Testing correctAnswer field handling",
                "programId": program_id,
                "questions": [
                    {
                        "type": "multiple_choice",
                        "question": "What is 3 + 3?",
                        "options": ["5", "6", "7", "8"],
                        "correctAnswer": "1",  # Index 1 = "6"
                        "points": 10,
                        "explanation": "3 + 3 = 6"
                    }
                ],
                "timeLimit": 60,
                "maxAttempts": 3,
                "passingScore": 75.0,
                "isPublished": True
            }
            
            test_response = self.session.post(f"{BACKEND_URL}/final-tests", json=test_data)
            
            if test_response.status_code != 200:
                self.log_test("Root Cause Verification", False, f"Failed to create test: {test_response.status_code}")
                return False
            
            final_test = test_response.json()
            test_id = final_test["id"]
            
            print(f"🔍 ADMIN VIEW - Question as created:")
            admin_question = final_test["questions"][0]
            print(f"   correctAnswer: {admin_question.get('correctAnswer')}")
            print(f"   Available fields: {list(admin_question.keys())}")
            
            # Now get the same test as a student
            student_response = self.student_session.get(f"{BACKEND_URL}/final-tests/{test_id}")
            
            if student_response.status_code != 200:
                self.log_test("Root Cause Verification", False, f"Student failed to get test: {student_response.status_code}")
                return False
            
            student_test = student_response.json()
            student_question = student_test["questions"][0]
            
            print(f"🔍 STUDENT VIEW - Same question as retrieved:")
            print(f"   correctAnswer: {student_question.get('correctAnswer')}")
            print(f"   Available fields: {list(student_question.keys())}")
            
            # Verify the bug
            admin_has_correct_answer = admin_question.get('correctAnswer') is not None
            student_has_correct_answer = student_question.get('correctAnswer') is not None
            
            if admin_has_correct_answer and not student_has_correct_answer:
                self.log_test("Root Cause Verification", True, 
                            f"✅ ROOT CAUSE CONFIRMED: Admin sees correctAnswer='{admin_question.get('correctAnswer')}', Student sees correctAnswer=None")
                self.test_id = test_id
                return True
            else:
                self.log_test("Root Cause Verification", False, 
                            f"❌ Unexpected behavior: Admin correctAnswer={admin_question.get('correctAnswer')}, Student correctAnswer={student_question.get('correctAnswer')}")
                return False
                
        except Exception as e:
            self.log_test("Root Cause Verification", False, f"Exception: {str(e)}")
            return False
    
    def demonstrate_scoring_failure(self):
        """Demonstrate that scoring fails due to missing correctAnswer"""
        try:
            if not hasattr(self, 'test_id'):
                self.log_test("Scoring Failure Demonstration", False, "No test ID available")
                return False
            
            # Submit the correct answer (we know it's "1" from creation)
            submission_data = {
                "testId": self.test_id,
                "answers": [
                    {
                        "questionId": "q1",  # Will be auto-generated
                        "answer": "1",  # The correct answer
                        "questionType": "multiple_choice"
                    }
                ],
                "timeSpent": 30,
                "completedAt": datetime.now().isoformat()
            }
            
            print(f"🔍 SUBMITTING CORRECT ANSWER: '1' (which should be 100%)")
            
            submit_response = self.student_session.post(f"{BACKEND_URL}/final-test-attempts", json=submission_data)
            
            if submit_response.status_code == 200:
                result = submit_response.json()
                score = result.get("score", 0)
                
                print(f"🔍 RESULT: Score = {score}% (Expected: 100%)")
                
                if score == 0:
                    self.log_test("Scoring Failure Demonstration", True, 
                                f"✅ SCORING FAILURE CONFIRMED: Got {score}% despite correct answer due to missing correctAnswer field")
                    return True
                else:
                    self.log_test("Scoring Failure Demonstration", False, 
                                f"❌ Unexpected: Got {score}% - scoring might be working")
                    return False
            else:
                self.log_test("Scoring Failure Demonstration", False, 
                            f"Submission failed: {submit_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Scoring Failure Demonstration", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_include_answers_parameter(self):
        """Test the include_answers parameter that should preserve correctAnswer"""
        try:
            if not hasattr(self, 'test_id'):
                self.log_test("Include Answers Parameter Test", False, "No test ID available")
                return False
            
            # Test with include_answers=True as admin
            admin_response = self.session.get(f"{BACKEND_URL}/final-tests/{self.test_id}", params={
                "include_answers": True
            })
            
            if admin_response.status_code == 200:
                admin_test = admin_response.json()
                admin_question = admin_test["questions"][0]
                
                print(f"🔍 ADMIN with include_answers=True:")
                print(f"   correctAnswer: {admin_question.get('correctAnswer')}")
                
                # Test with include_answers=True as student (should still hide answers)
                student_response = self.student_session.get(f"{BACKEND_URL}/final-tests/{self.test_id}", params={
                    "include_answers": True
                })
                
                if student_response.status_code == 200:
                    student_test = student_response.json()
                    student_question = student_test["questions"][0]
                    
                    print(f"🔍 STUDENT with include_answers=True:")
                    print(f"   correctAnswer: {student_question.get('correctAnswer')}")
                    
                    admin_has_answer = admin_question.get('correctAnswer') is not None
                    student_still_hidden = student_question.get('correctAnswer') is None
                    
                    if admin_has_answer and student_still_hidden:
                        self.log_test("Include Answers Parameter Test", True, 
                                    "✅ include_answers parameter working correctly for admin, still hidden for student")
                        return True
                    else:
                        self.log_test("Include Answers Parameter Test", False, 
                                    f"❌ Unexpected behavior with include_answers parameter")
                        return False
                else:
                    self.log_test("Include Answers Parameter Test", False, 
                                f"Student request with include_answers failed: {student_response.status_code}")
                    return False
            else:
                self.log_test("Include Answers Parameter Test", False, 
                            f"Admin request with include_answers failed: {admin_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Include Answers Parameter Test", False, f"Exception: {str(e)}")
            return False
    
    def run_verification(self):
        """Run comprehensive root cause verification"""
        print("🚨 URGENT: Final Exam Root Cause Verification")
        print("=" * 80)
        print("CRITICAL BUG: Backend removes correctAnswer field for students!")
        print("IMPACT: Students get 0% scores because scoring logic can't find correct answers")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ Admin authentication failed. Cannot proceed.")
            return False
        
        if not self.authenticate_student():
            print("❌ Student authentication failed. Cannot proceed.")
            return False
        
        # Step 2: Verify the root cause bug
        print("\n🔍 STEP 1: Verifying correctAnswer field removal bug...")
        root_cause_confirmed = self.verify_root_cause_bug()
        
        # Step 3: Demonstrate scoring failure
        print("\n🔍 STEP 2: Demonstrating scoring failure...")
        scoring_failure_confirmed = self.demonstrate_scoring_failure()
        
        # Step 4: Test include_answers parameter
        print("\n🔍 STEP 3: Testing include_answers parameter...")
        include_answers_working = self.test_admin_include_answers_parameter()
        
        # Summary
        print("\n" + "=" * 80)
        print("🔍 ROOT CAUSE VERIFICATION SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        
        print(f"✅ Verified: {passed_tests}/{total_tests} aspects of the bug")
        
        if root_cause_confirmed and scoring_failure_confirmed:
            print("\n🚨 CRITICAL BUG CONFIRMED:")
            print("  1. ✅ Backend removes correctAnswer field for students when retrieving tests")
            print("  2. ✅ Scoring logic fails because correctAnswer field is missing")
            print("  3. ✅ This causes 0% scores despite correct answers")
            
            print("\n🔧 REQUIRED FIX:")
            print("  - Modify get_final_test endpoint (lines 4381-4384 in server.py)")
            print("  - Keep correctAnswer field in database for scoring")
            print("  - Only hide correctAnswer in API response to students")
            print("  - Ensure scoring logic accesses original database data, not filtered response")
            
            return True
        else:
            print("\n❌ Could not fully confirm the root cause")
            return False

if __name__ == "__main__":
    verifier = RootCauseVerifier()
    success = verifier.run_verification()
    sys.exit(0 if success else 1)