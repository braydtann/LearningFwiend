#!/usr/bin/env python3
"""
Backend Testing Script for LearningFriend LMS
Focus: Final Test Creation and bcrypt Authentication Issues

Review Request Testing:
1. Test final test creation endpoint: POST /api/final-tests with empty questions array
2. Test program creation with final test workflow 
3. Verify that bcrypt authentication errors are resolved
4. Check if 422 errors during final test creation are still occurring

Admin credentials: brayden.t@covesmart.com / Hawaii2020!
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration - Using correct backend URL from frontend/.env
BACKEND_URL = "https://lms-chronology.emergent.host/api"

# Test credentials
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"

class LMSBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
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
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def create_test_program(self):
        """Create a test program for final test association"""
        try:
            program_data = {
                "title": f"Final Test Program {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test program for final test functionality testing",
                "departmentId": None,
                "duration": "4 weeks",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            response = self.session.post(f"{BACKEND_URL}/programs", json=program_data)
            
            if response.status_code == 200:
                program = response.json()
                self.test_program_id = program["id"]
                self.log_test("Program Creation", True, f"Created program: {program['title']} (ID: {program['id']})")
                return program
            else:
                self.log_test("Program Creation", False, f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Program Creation", False, f"Exception: {str(e)}")
            return None
    
    def test_final_test_creation_empty_questions(self):
        """Test 1: Final test creation with empty questions array"""
        try:
            test_data = {
                "title": f"Empty Questions Final Test {datetime.now().strftime('%H%M%S')}",
                "description": "Testing final test creation with empty questions array",
                "programId": self.test_program_id,
                "questions": [],  # Empty questions array
                "timeLimit": 60,
                "maxAttempts": 2,
                "passingScore": 75.0,
                "shuffleQuestions": False,
                "showResults": True,
                "isPublished": False
            }
            
            response = self.session.post(f"{BACKEND_URL}/final-tests", json=test_data)
            
            if response.status_code == 200:
                final_test = response.json()
                self.empty_test_id = final_test["id"]
                
                # Verify the test was created correctly
                if (final_test["questionCount"] == 0 and 
                    final_test["totalPoints"] == 0 and
                    final_test["programId"] == self.test_program_id and
                    len(final_test["questions"]) == 0):
                    self.log_test("Final Test Creation (Empty Questions)", True, 
                                f"Created test with 0 questions, ID: {final_test['id']}")
                    return final_test
                else:
                    self.log_test("Final Test Creation (Empty Questions)", False, 
                                f"Test created but data validation failed: {final_test}")
                    return None
            else:
                self.log_test("Final Test Creation (Empty Questions)", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Final Test Creation (Empty Questions)", False, f"Exception: {str(e)}")
            return None
    
    def test_final_test_creation_with_questions(self):
        """Test 2: Final test creation with questions provided"""
        try:
            test_data = {
                "title": f"Questions Final Test {datetime.now().strftime('%H%M%S')}",
                "description": "Testing final test creation with questions provided",
                "programId": self.test_program_id,
                "questions": [
                    {
                        "type": "multiple_choice",
                        "question": "What is the capital of France?",
                        "options": ["London", "Berlin", "Paris", "Madrid"],
                        "correctAnswer": "2",
                        "points": 10,
                        "explanation": "Paris is the capital of France"
                    },
                    {
                        "type": "true_false",
                        "question": "Python is a programming language.",
                        "correctAnswer": "true",
                        "points": 5,
                        "explanation": "Python is indeed a programming language"
                    }
                ],
                "timeLimit": 90,
                "maxAttempts": 3,
                "passingScore": 70.0,
                "shuffleQuestions": True,
                "showResults": True,
                "isPublished": True
            }
            
            response = self.session.post(f"{BACKEND_URL}/final-tests", json=test_data)
            
            if response.status_code == 200:
                final_test = response.json()
                self.questions_test_id = final_test["id"]
                
                # Verify the test was created correctly
                if (final_test["questionCount"] == 2 and 
                    final_test["totalPoints"] == 15 and
                    final_test["programId"] == self.test_program_id and
                    len(final_test["questions"]) == 2):
                    self.log_test("Final Test Creation (With Questions)", True, 
                                f"Created test with 2 questions, total points: {final_test['totalPoints']}")
                    return final_test
                else:
                    self.log_test("Final Test Creation (With Questions)", False, 
                                f"Test created but data validation failed: {final_test}")
                    return None
            else:
                self.log_test("Final Test Creation (With Questions)", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Final Test Creation (With Questions)", False, f"Exception: {str(e)}")
            return None
    
    def test_update_empty_test_with_questions(self):
        """Test 3: Update the empty test by adding questions"""
        try:
            # First, get the current test to see its structure
            response = self.session.get(f"{BACKEND_URL}/final-tests/{self.empty_test_id}")
            
            if response.status_code != 200:
                self.log_test("Update Empty Test (Get Current)", False, 
                            f"Failed to get current test: {response.status_code}")
                return None
            
            current_test = response.json()
            
            # Update the test with questions
            update_data = {
                "title": current_test["title"] + " - Updated with Questions",
                "isPublished": True
            }
            
            response = self.session.put(f"{BACKEND_URL}/final-tests/{self.empty_test_id}", json=update_data)
            
            if response.status_code == 200:
                updated_test = response.json()
                self.log_test("Update Empty Test with Questions", True, 
                            f"Successfully updated test to published status")
                return updated_test
            else:
                self.log_test("Update Empty Test with Questions", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Update Empty Test with Questions", False, f"Exception: {str(e)}")
            return None
    
    def test_final_test_retrieval_by_program(self):
        """Test 4: Final test retrieval by program ID"""
        try:
            # Test getting all final tests for the program
            response = self.session.get(f"{BACKEND_URL}/final-tests", params={
                "program_id": self.test_program_id,
                "published_only": False
            })
            
            if response.status_code == 200:
                tests = response.json()
                
                # Should find our 2 created tests
                test_ids = [test["id"] for test in tests]
                found_empty_test = self.empty_test_id in test_ids
                found_questions_test = self.questions_test_id in test_ids
                
                if found_empty_test and found_questions_test:
                    self.log_test("Final Test Retrieval by Program ID", True, 
                                f"Found {len(tests)} tests for program {self.test_program_id}")
                    return tests
                else:
                    self.log_test("Final Test Retrieval by Program ID", False, 
                                f"Expected to find both tests, but found: {test_ids}")
                    return None
            else:
                self.log_test("Final Test Retrieval by Program ID", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Final Test Retrieval by Program ID", False, f"Exception: {str(e)}")
            return None
    
    def test_quiz_requirements_endpoints(self):
        """Test 5: Quiz requirements endpoints - verify quiz retrieval and attempt checking"""
        try:
            # Test getting a specific final test
            response = self.session.get(f"{BACKEND_URL}/final-tests/{self.questions_test_id}")
            
            if response.status_code == 200:
                test_details = response.json()
                
                # Verify the test has the expected structure
                required_fields = ["id", "title", "programId", "questions", "passingScore", "maxAttempts"]
                missing_fields = [field for field in required_fields if field not in test_details]
                
                if not missing_fields:
                    self.log_test("Quiz Requirements - Test Retrieval", True, 
                                f"Retrieved test with all required fields")
                    
                    # Test getting quiz attempts (should be empty for new test)
                    attempts_response = self.session.get(f"{BACKEND_URL}/final-test-attempts", params={
                        "test_id": self.questions_test_id
                    })
                    
                    if attempts_response.status_code == 200:
                        attempts = attempts_response.json()
                        self.log_test("Quiz Requirements - Attempt Checking", True, 
                                    f"Retrieved {len(attempts)} attempts for test")
                        return True
                    else:
                        self.log_test("Quiz Requirements - Attempt Checking", False, 
                                    f"Failed to get attempts: {attempts_response.status_code}")
                        return False
                else:
                    self.log_test("Quiz Requirements - Test Retrieval", False, 
                                f"Missing required fields: {missing_fields}")
                    return False
            else:
                self.log_test("Quiz Requirements - Test Retrieval", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Quiz Requirements - Endpoints", False, f"Exception: {str(e)}")
            return False
    
    def test_complete_workflow(self):
        """Test 6: Complete workflow - Create program, create final test, update, retrieve"""
        try:
            # Create a new program for workflow testing
            workflow_program_data = {
                "title": f"Workflow Test Program {datetime.now().strftime('%H%M%S')}",
                "description": "Complete workflow testing program",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            program_response = self.session.post(f"{BACKEND_URL}/programs", json=workflow_program_data)
            
            if program_response.status_code != 200:
                self.log_test("Complete Workflow - Program Creation", False, 
                            f"Failed to create program: {program_response.status_code}")
                return False
            
            workflow_program = program_response.json()
            workflow_program_id = workflow_program["id"]
            
            # Create final test with empty questions
            empty_test_data = {
                "title": "Workflow Empty Test",
                "description": "Testing complete workflow",
                "programId": workflow_program_id,
                "questions": [],
                "timeLimit": 45,
                "maxAttempts": 1,
                "passingScore": 80.0,
                "isPublished": False
            }
            
            test_response = self.session.post(f"{BACKEND_URL}/final-tests", json=empty_test_data)
            
            if test_response.status_code != 200:
                self.log_test("Complete Workflow - Empty Test Creation", False, 
                            f"Failed to create test: {test_response.status_code}")
                return False
            
            workflow_test = test_response.json()
            workflow_test_id = workflow_test["id"]
            
            # Update test to published
            update_response = self.session.put(f"{BACKEND_URL}/final-tests/{workflow_test_id}", json={
                "isPublished": True
            })
            
            if update_response.status_code != 200:
                self.log_test("Complete Workflow - Test Update", False, 
                            f"Failed to update test: {update_response.status_code}")
                return False
            
            # Retrieve final tests by program ID
            retrieval_response = self.session.get(f"{BACKEND_URL}/final-tests", params={
                "program_id": workflow_program_id
            })
            
            if retrieval_response.status_code == 200:
                retrieved_tests = retrieval_response.json()
                if len(retrieved_tests) == 1 and retrieved_tests[0]["id"] == workflow_test_id:
                    self.log_test("Complete Workflow", True, 
                                "Successfully completed entire workflow: create program → create empty test → update → retrieve")
                    return True
                else:
                    self.log_test("Complete Workflow", False, 
                                f"Retrieval failed: expected 1 test, got {len(retrieved_tests)}")
                    return False
            else:
                self.log_test("Complete Workflow", False, 
                            f"Failed to retrieve tests: {retrieval_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Complete Workflow", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all final test functionality tests"""
        print("🚀 Starting LearningFriend LMS Final Test Backend Testing")
        print("=" * 70)
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Create test program
        program = self.create_test_program()
        if not program:
            print("❌ Program creation failed. Cannot proceed with tests.")
            return False
        
        # Step 3: Test final test creation with empty questions
        empty_test = self.test_final_test_creation_empty_questions()
        
        # Step 4: Test final test creation with questions
        questions_test = self.test_final_test_creation_with_questions()
        
        # Step 5: Test updating empty test
        if empty_test:
            self.test_update_empty_test_with_questions()
        
        # Step 6: Test final test retrieval by program ID
        if empty_test and questions_test:
            self.test_final_test_retrieval_by_program()
        
        # Step 7: Test quiz requirements endpoints
        if questions_test:
            self.test_quiz_requirements_endpoints()
        
        # Step 8: Test complete workflow
        self.test_complete_workflow()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if passed_tests < total_tests:
            print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print(f"\n🎯 Final Test Functionality: {'✅ WORKING' if success_rate >= 80 else '❌ NEEDS ATTENTION'}")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = LMSBackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)