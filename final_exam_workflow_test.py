#!/usr/bin/env python3
"""
Final Exam Complete Workflow Test
Testing the complete final exam workflow with correct API usage
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://fixfriend.preview.emergentagent.com/api"

# Test credentials
STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class FinalExamWorkflowTester:
    def __init__(self):
        self.student_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def authenticate_student(self):
        """Authenticate student and return token"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=STUDENT_CREDENTIALS)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                self.log_result("Student Authentication", True, 
                              f"User: {user_info.get('full_name', 'Unknown')} ({user_info.get('role', 'Unknown')})")
                return token
            else:
                self.log_result("Student Authentication", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Student Authentication", False, f"Exception: {str(e)}")
            return None
    
    def get_available_final_test(self):
        """Get an available final test for the student"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Get all final tests available to student
            response = requests.get(f"{BACKEND_URL}/final-tests", headers=headers)
            
            if response.status_code == 200:
                tests = response.json()
                published_tests = [t for t in tests if t.get('isPublished', False)]
                
                self.log_result("Get Available Final Tests", True, 
                              f"Found {len(published_tests)} published final tests")
                
                if published_tests:
                    # Return the first available test
                    test = published_tests[0]
                    test_title = test.get('title', 'Unknown')
                    test_id = test.get('id', 'Unknown')
                    program_id = test.get('programId', 'Unknown')
                    
                    print(f"   Selected Test: {test_title} (ID: {test_id})")
                    print(f"   Program ID: {program_id}")
                    
                    return test
                else:
                    self.log_result("Get Available Final Tests", False, "No published tests available")
                    return None
            else:
                self.log_result("Get Available Final Tests", False,
                              f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Get Available Final Tests", False, f"Exception: {str(e)}")
            return None
    
    def get_final_test_details(self, test_id):
        """Get detailed final test information including questions"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            response = requests.get(f"{BACKEND_URL}/final-tests/{test_id}", headers=headers)
            
            if response.status_code == 200:
                test_details = response.json()
                questions = test_details.get('questions', [])
                
                self.log_result("Get Final Test Details", True, 
                              f"Test has {len(questions)} questions")
                
                # Show question types
                question_types = {}
                for q in questions:
                    q_type = q.get('type', 'unknown')
                    question_types[q_type] = question_types.get(q_type, 0) + 1
                
                if question_types:
                    type_summary = ", ".join([f"{count} {qtype}" for qtype, count in question_types.items()])
                    print(f"   Question Types: {type_summary}")
                
                return test_details
            else:
                self.log_result("Get Final Test Details", False,
                              f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Get Final Test Details", False, f"Exception: {str(e)}")
            return None
    
    def create_sample_answers(self, questions):
        """Create sample answers for the test questions"""
        answers = []
        
        for question in questions:
            q_id = question.get('id')
            q_type = question.get('type', 'multiple-choice')
            
            if q_type == 'multiple-choice':
                # Select first option
                options = question.get('options', [])
                if options:
                    answers.append({
                        "questionId": q_id,
                        "answer": options[0]
                    })
                else:
                    answers.append({
                        "questionId": q_id,
                        "answer": "Option A"
                    })
            
            elif q_type == 'true-false':
                answers.append({
                    "questionId": q_id,
                    "answer": "true"
                })
            
            elif q_type == 'short-answer':
                answers.append({
                    "questionId": q_id,
                    "answer": "Sample short answer"
                })
            
            elif q_type == 'long-form':
                answers.append({
                    "questionId": q_id,
                    "answer": "This is a sample long-form answer for testing purposes."
                })
            
            elif q_type == 'select-all-that-apply':
                options = question.get('options', [])
                if options:
                    # Select first two options
                    selected = options[:2] if len(options) >= 2 else options
                    answers.append({
                        "questionId": q_id,
                        "answer": selected
                    })
                else:
                    answers.append({
                        "questionId": q_id,
                        "answer": ["Option A", "Option B"]
                    })
            
            elif q_type == 'chronological-order':
                items = question.get('items', [])
                if items:
                    # Reverse the order for testing
                    answers.append({
                        "questionId": q_id,
                        "answer": list(reversed(range(len(items))))
                    })
                else:
                    answers.append({
                        "questionId": q_id,
                        "answer": [0, 1, 2, 3]
                    })
            
            else:
                # Default answer
                answers.append({
                    "questionId": q_id,
                    "answer": "Default answer"
                })
        
        return answers
    
    def submit_final_test_attempt(self, test_id, program_id, answers):
        """Submit a final test attempt with correct API format"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Use correct field names as per backend API
            attempt_data = {
                "testId": test_id,  # Correct field name (not finalTestId)
                "programId": program_id,
                "answers": answers,
                "timeSpent": 1800  # 30 minutes in seconds
            }
            
            response = requests.post(f"{BACKEND_URL}/final-test-attempts", 
                                   headers=headers, json=attempt_data)
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                attempt_id = data.get('id', 'Unknown')
                score = data.get('score', 0)
                is_passed = data.get('isPassed', False)
                
                self.log_result("Submit Final Test Attempt", True,
                              f"Attempt ID: {attempt_id}, Score: {score}%, Passed: {is_passed}")
                return data
            
            elif response.status_code == 422:
                error_details = response.json()
                self.log_result("Submit Final Test Attempt", False,
                              f"422 ERROR: {json.dumps(error_details, indent=2)}")
                return None
            
            else:
                self.log_result("Submit Final Test Attempt", False,
                              f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Submit Final Test Attempt", False, f"Exception: {str(e)}")
            return None
    
    def get_student_attempts(self):
        """Get student's final test attempts"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            response = requests.get(f"{BACKEND_URL}/final-test-attempts", headers=headers)
            
            if response.status_code == 200:
                attempts = response.json()
                self.log_result("Get Student Attempts", True, 
                              f"Found {len(attempts)} previous attempts")
                
                # Show recent attempts
                for i, attempt in enumerate(attempts[:3]):
                    test_title = attempt.get('testTitle', 'Unknown')
                    score = attempt.get('score', 0)
                    is_passed = attempt.get('isPassed', False)
                    print(f"   Attempt {i+1}: {test_title} - Score: {score}%, Passed: {is_passed}")
                
                return attempts
            else:
                self.log_result("Get Student Attempts", False,
                              f"Status: {response.status_code}, Response: {response.text}")
                return []
                
        except Exception as e:
            self.log_result("Get Student Attempts", False, f"Exception: {str(e)}")
            return []
    
    def test_program_completion_requirement(self):
        """Test if program completion is required for final exam access"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Get student's programs
            response = requests.get(f"{BACKEND_URL}/programs", headers=headers)
            if response.status_code != 200:
                self.log_result("Program Completion Requirement Test", False, "Cannot get programs")
                return
            
            programs = response.json()
            
            for program in programs[:2]:  # Test first 2 programs
                program_id = program.get('id')
                program_title = program.get('title', 'Unknown')
                
                # Check access
                access_response = requests.get(f"{BACKEND_URL}/programs/{program_id}/access-check", headers=headers)
                if access_response.status_code == 200:
                    access_data = access_response.json()
                    has_access = access_data.get('hasAccess', False)
                    
                    # Get final tests for this program
                    tests_response = requests.get(f"{BACKEND_URL}/final-tests", 
                                                headers=headers, params={"program_id": program_id})
                    
                    if tests_response.status_code == 200:
                        tests = tests_response.json()
                        test_count = len(tests)
                        
                        self.log_result(f"Program Completion Check ({program_title})", True,
                                      f"Access: {has_access}, Final Tests: {test_count}")
                        
                        if has_access and test_count == 0:
                            self.log_result(f"Missing Final Tests ({program_title})", False,
                                          "Program accessible but no final tests available")
                    
        except Exception as e:
            self.log_result("Program Completion Requirement Test", False, f"Exception: {str(e)}")
    
    def run_complete_workflow_test(self):
        """Run complete final exam workflow test"""
        print("🎯 FINAL EXAM COMPLETE WORKFLOW TEST")
        print("=" * 60)
        
        # 1. Authenticate
        print("\n1. AUTHENTICATION")
        print("-" * 30)
        self.student_token = self.authenticate_student()
        
        if not self.student_token:
            print("❌ Authentication failed - cannot proceed")
            return
        
        # 2. Get available final test
        print("\n2. GET AVAILABLE FINAL TEST")
        print("-" * 30)
        test = self.get_available_final_test()
        
        if not test:
            print("❌ No available final tests - cannot proceed with workflow test")
            # Still run other tests
            self.test_program_completion_requirement()
            return
        
        # 3. Get test details
        print("\n3. GET FINAL TEST DETAILS")
        print("-" * 30)
        test_id = test.get('id')
        program_id = test.get('programId')
        
        test_details = self.get_final_test_details(test_id)
        
        if not test_details:
            print("❌ Cannot get test details - cannot proceed")
            return
        
        # 4. Create sample answers
        print("\n4. CREATE SAMPLE ANSWERS")
        print("-" * 30)
        questions = test_details.get('questions', [])
        answers = self.create_sample_answers(questions)
        
        self.log_result("Create Sample Answers", True, f"Created {len(answers)} answers for {len(questions)} questions")
        
        # 5. Submit test attempt
        print("\n5. SUBMIT FINAL TEST ATTEMPT")
        print("-" * 30)
        attempt_result = self.submit_final_test_attempt(test_id, program_id, answers)
        
        # 6. Get student attempts
        print("\n6. GET STUDENT ATTEMPTS HISTORY")
        print("-" * 30)
        attempts = self.get_student_attempts()
        
        # 7. Test program completion requirements
        print("\n7. PROGRAM COMPLETION REQUIREMENTS")
        print("-" * 30)
        self.test_program_completion_requirement()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 WORKFLOW TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings
        print("\n🔍 KEY FINDINGS:")
        
        # Check for 422 errors
        error_422_tests = [r for r in self.test_results if not r['success'] and '422' in r['details']]
        if error_422_tests:
            print("❌ 422 ERRORS IDENTIFIED:")
            for test in error_422_tests:
                print(f"   • {test['test']}")
                # Extract error details
                if 'testId' in test['details'] and 'finalTestId' in test['details']:
                    print("   • ROOT CAUSE: Frontend sending 'finalTestId' but backend expects 'testId'")
                if 'answers' in test['details'] and 'Field required' in test['details']:
                    print("   • ROOT CAUSE: Backend requires 'answers' field for test submission")
        else:
            print("✅ No 422 errors - API format is correct")
        
        # Check for missing tests
        missing_tests = [r for r in self.test_results if not r['success'] and 'no final tests' in r['details'].lower()]
        if missing_tests:
            print("❌ PROGRAMS WITH MISSING FINAL TESTS:")
            for test in missing_tests:
                print(f"   • {test['test']}")
        
        # Success indicators
        successful_submission = any(r['success'] and 'Submit Final Test Attempt' in r['test'] for r in self.test_results)
        if successful_submission:
            print("✅ Final test submission workflow is working correctly")
        
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "has_422_errors": len(error_422_tests) > 0,
            "has_missing_tests": len(missing_tests) > 0,
            "workflow_successful": successful_submission
        }

if __name__ == "__main__":
    tester = FinalExamWorkflowTester()
    results = tester.run_complete_workflow_test()
    
    # Exit with appropriate code
    sys.exit(0 if results["failed"] == 0 else 1)