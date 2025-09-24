#!/usr/bin/env python3
"""
Final Frontend Flow Backend Testing - Review Request Validation
Testing the complete frontend-to-backend flow for program creation and final test taking.

This test validates the specific scenario mentioned in the review request:
1. Admin login and program creation with final test
2. Student login and test taking workflow
3. API format verification and error capture

Environment: https://test-grading-fix.preview.emergentagent.com
Admin: brayden.t@covesmart.com / Hawaii2020!
Student: karlo.student@alder.com / StudentPermanent123!

Focus Areas:
- Complete program creation workflow with final test questions
- Student authentication and test access
- Quiz submission and scoring validation
- API response format verification
- Error detection and logging
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration - Using correct backend URL from frontend/.env
BACKEND_URL = "https://test-grading-fix.preview.emergentagent.com/api"

# Test credentials from review request
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"
STUDENT_EMAIL = "karlo.student@alder.com"
STUDENT_PASSWORD = "StudentPermanent123!"

class FinalFrontendFlowTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.student_token = None
        self.test_results = []
        self.test_program_id = None
        self.test_final_test_id = None
        
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
        """Test 1: Admin Authentication"""
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
                self.log_test("Admin Authentication", True, 
                            f"Logged in as {data['user']['full_name']} ({data['user']['role']})")
                return True
            else:
                self.log_test("Admin Authentication", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def create_program_with_final_test(self):
        """Test 2: Create Program with Final Test (Frontend Flow Simulation)"""
        try:
            # Step 1: Create a program
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            program_data = {
                "title": f"Frontend Flow Test Program {timestamp}",
                "description": "Testing complete frontend-to-backend flow for program creation with final test",
                "departmentId": None,
                "duration": "6 weeks",
                "courseIds": [],
                "nestedProgramIds": [],
                "finalTest": {
                    "title": f"Final Test {timestamp}",
                    "description": "Testing final test creation via frontend flow",
                    "questions": [
                        {
                            "type": "multiple_choice",
                            "question": "What is the primary purpose of this test?",
                            "options": [
                                "To test frontend functionality",
                                "To validate backend APIs", 
                                "To verify complete workflow",
                                "All of the above"
                            ],
                            "correctAnswer": "3",
                            "points": 25,
                            "explanation": "This test validates the complete frontend-to-backend workflow"
                        },
                        {
                            "type": "true_false",
                            "question": "The LearningFriend LMS supports final exams for programs.",
                            "correctAnswer": "true",
                            "points": 25,
                            "explanation": "Yes, the LMS supports final exams for programs"
                        },
                        {
                            "type": "multiple_choice",
                            "question": "Which HTTP status code indicates successful API response?",
                            "options": ["200", "404", "422", "500"],
                            "correctAnswer": "0",
                            "points": 25,
                            "explanation": "HTTP 200 indicates successful response"
                        },
                        {
                            "type": "true_false",
                            "question": "Students need to be enrolled in a program to take its final test.",
                            "correctAnswer": "true",
                            "points": 25,
                            "explanation": "Students must be enrolled to access program final tests"
                        }
                    ],
                    "timeLimit": 30,
                    "maxAttempts": 2,
                    "passingScore": 75.0,
                    "shuffleQuestions": False,
                    "showResults": True,
                    "isPublished": True
                }
            }
            
            # Create program first
            program_response = self.session.post(f"{BACKEND_URL}/programs", json={
                "title": program_data["title"],
                "description": program_data["description"],
                "departmentId": program_data["departmentId"],
                "duration": program_data["duration"],
                "courseIds": program_data["courseIds"],
                "nestedProgramIds": program_data["nestedProgramIds"]
            })
            
            if program_response.status_code != 200:
                self.log_test("Program Creation", False, 
                            f"Failed to create program: {program_response.status_code} - {program_response.text}")
                return False
            
            program = program_response.json()
            self.test_program_id = program["id"]
            self.log_test("Program Creation", True, f"Created program: {program['title']} (ID: {program['id']})")
            
            # Step 2: Create final test for the program
            final_test_data = program_data["finalTest"]
            final_test_data["programId"] = self.test_program_id
            
            test_response = self.session.post(f"{BACKEND_URL}/final-tests", json=final_test_data)
            
            if test_response.status_code == 200:
                final_test = test_response.json()
                self.test_final_test_id = final_test["id"]
                
                # Verify test structure
                expected_questions = 4
                expected_total_points = 100
                
                if (final_test["questionCount"] == expected_questions and 
                    final_test["totalPoints"] == expected_total_points and
                    final_test["programId"] == self.test_program_id):
                    self.log_test("Final Test Creation", True, 
                                f"Created final test with {final_test['questionCount']} questions, "
                                f"total points: {final_test['totalPoints']}")
                    return True
                else:
                    self.log_test("Final Test Creation", False, 
                                f"Test created but validation failed. Expected: {expected_questions} questions, "
                                f"{expected_total_points} points. Got: {final_test['questionCount']} questions, "
                                f"{final_test['totalPoints']} points")
                    return False
            else:
                self.log_test("Final Test Creation", False, 
                            f"Status: {test_response.status_code}, Response: {test_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Program with Final Test Creation", False, f"Exception: {str(e)}")
            return False
    
    def authenticate_student(self):
        """Test 3: Student Authentication"""
        try:
            # Clear admin session and create new session for student
            self.session.headers.pop("Authorization", None)
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username_or_email": STUDENT_EMAIL,
                "password": STUDENT_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data["access_token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.student_token}"
                })
                self.log_test("Student Authentication", True, 
                            f"Logged in as {data['user']['full_name']} ({data['user']['role']})")
                return True
            else:
                self.log_test("Student Authentication", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Student Authentication", False, f"Exception: {str(e)}")
            return False
    
    def enroll_student_in_program(self):
        """Test 4: Enroll Student in Program (Simulate Classroom Assignment)"""
        try:
            # Switch back to admin to create classroom and enroll student
            self.session.headers.update({
                "Authorization": f"Bearer {self.admin_token}"
            })
            
            # Create a classroom with the program and student
            classroom_data = {
                "name": f"Test Classroom {datetime.now().strftime('%H%M%S')}",
                "description": "Classroom for testing final exam flow",
                "programIds": [self.test_program_id],
                "courseIds": [],
                "studentIds": [],  # Will be populated after getting student ID
                "instructorId": None,
                "startDate": datetime.now().isoformat(),
                "endDate": None,
                "isActive": True
            }
            
            # First, get student ID by email
            users_response = self.session.get(f"{BACKEND_URL}/auth/admin/users")
            if users_response.status_code != 200:
                self.log_test("Get Student ID", False, f"Failed to get users: {users_response.status_code}")
                return False
            
            users = users_response.json()
            student_user = next((user for user in users if user["email"] == STUDENT_EMAIL), None)
            
            if not student_user:
                self.log_test("Get Student ID", False, f"Student {STUDENT_EMAIL} not found")
                return False
            
            student_id = student_user["id"]
            classroom_data["studentIds"] = [student_id]
            
            # Create classroom
            classroom_response = self.session.post(f"{BACKEND_URL}/classrooms", json=classroom_data)
            
            if classroom_response.status_code == 200:
                classroom = classroom_response.json()
                self.log_test("Student Program Enrollment", True, 
                            f"Created classroom and enrolled student in program")
                return True
            else:
                self.log_test("Student Program Enrollment", False, 
                            f"Failed to create classroom: {classroom_response.status_code} - {classroom_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Student Program Enrollment", False, f"Exception: {str(e)}")
            return False
    
    def test_student_final_test_access(self):
        """Test 5: Student Final Test Access"""
        try:
            # Switch back to student session
            self.session.headers.update({
                "Authorization": f"Bearer {self.student_token}"
            })
            
            # Test getting final tests for the program
            response = self.session.get(f"{BACKEND_URL}/final-tests", params={
                "program_id": self.test_program_id
            })
            
            if response.status_code == 200:
                tests = response.json()
                
                # Find our test
                our_test = next((test for test in tests if test["id"] == self.test_final_test_id), None)
                
                if our_test:
                    self.log_test("Student Final Test Access", True, 
                                f"Student can access final test: {our_test['title']}")
                    return True
                else:
                    self.log_test("Student Final Test Access", False, 
                                f"Test not found in student's accessible tests. Found {len(tests)} tests")
                    return False
            else:
                self.log_test("Student Final Test Access", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Student Final Test Access", False, f"Exception: {str(e)}")
            return False
    
    def test_final_test_submission(self):
        """Test 6: Final Test Submission and Scoring"""
        try:
            # Get the test details first
            test_response = self.session.get(f"{BACKEND_URL}/final-tests/{self.test_final_test_id}")
            
            if test_response.status_code != 200:
                self.log_test("Get Test Details", False, f"Failed to get test: {test_response.status_code}")
                return False
            
            test_details = test_response.json()
            questions = test_details["questions"]
            
            # Prepare answers (answering all correctly for 100% score)
            answers = []
            for i, question in enumerate(questions):
                if question["type"] == "multiple_choice":
                    answers.append({
                        "questionIndex": i,
                        "answer": question["correctAnswer"]
                    })
                elif question["type"] == "true_false":
                    answers.append({
                        "questionIndex": i,
                        "answer": question["correctAnswer"]
                    })
            
            # Submit the test
            submission_data = {
                "testId": self.test_final_test_id,
                "answers": answers,
                "timeSpent": 300,  # 5 minutes
                "submittedAt": datetime.now().isoformat()
            }
            
            submission_response = self.session.post(f"{BACKEND_URL}/final-test-attempts", json=submission_data)
            
            if submission_response.status_code == 200:
                attempt = submission_response.json()
                
                # Verify scoring
                expected_score = 100.0  # All answers correct
                actual_score = attempt.get("score", 0)
                
                if actual_score == expected_score:
                    self.log_test("Final Test Submission and Scoring", True, 
                                f"Test submitted successfully. Score: {actual_score}% (Expected: {expected_score}%)")
                    return True
                elif actual_score > 0:
                    self.log_test("Final Test Submission and Scoring", False, 
                                f"Test submitted but scoring issue. Score: {actual_score}% (Expected: {expected_score}%)")
                    return False
                else:
                    self.log_test("Final Test Submission and Scoring", False, 
                                f"Test submitted but got 0% score - this is the main issue to investigate")
                    return False
            else:
                self.log_test("Final Test Submission and Scoring", False, 
                            f"Submission failed: {submission_response.status_code} - {submission_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Final Test Submission and Scoring", False, f"Exception: {str(e)}")
            return False
    
    def test_api_format_verification(self):
        """Test 7: API Format Verification - Capture submission data format"""
        try:
            # Get test details to understand expected format
            test_response = self.session.get(f"{BACKEND_URL}/final-tests/{self.test_final_test_id}")
            
            if test_response.status_code != 200:
                self.log_test("API Format Verification", False, "Cannot get test details for format verification")
                return False
            
            test_details = test_response.json()
            
            # Log the exact format being sent
            print("\n📋 API FORMAT VERIFICATION:")
            print("=" * 50)
            print("Test Structure:")
            print(json.dumps({
                "id": test_details["id"],
                "questionCount": test_details["questionCount"],
                "totalPoints": test_details["totalPoints"],
                "questions": [
                    {
                        "type": q["type"],
                        "correctAnswer": q["correctAnswer"],
                        "points": q["points"]
                    } for q in test_details["questions"]
                ]
            }, indent=2))
            
            # Test different answer formats to identify the correct one
            test_formats = [
                {
                    "name": "String Index Format",
                    "answers": [
                        {"questionIndex": 0, "answer": "3"},
                        {"questionIndex": 1, "answer": "true"},
                        {"questionIndex": 2, "answer": "0"},
                        {"questionIndex": 3, "answer": "true"}
                    ]
                },
                {
                    "name": "Integer Index Format", 
                    "answers": [
                        {"questionIndex": 0, "answer": 3},
                        {"questionIndex": 1, "answer": True},
                        {"questionIndex": 2, "answer": 0},
                        {"questionIndex": 3, "answer": True}
                    ]
                },
                {
                    "name": "Mixed Format",
                    "answers": [
                        {"questionIndex": 0, "answer": 3},
                        {"questionIndex": 1, "answer": "true"},
                        {"questionIndex": 2, "answer": 0},
                        {"questionIndex": 3, "answer": "true"}
                    ]
                }
            ]
            
            for format_test in test_formats:
                print(f"\nTesting {format_test['name']}:")
                print(json.dumps(format_test["answers"], indent=2))
                
                submission_data = {
                    "testId": self.test_final_test_id,
                    "answers": format_test["answers"],
                    "timeSpent": 60,
                    "submittedAt": datetime.now().isoformat()
                }
                
                # Test submission (but don't count towards attempts)
                test_response = self.session.post(f"{BACKEND_URL}/final-test-attempts/validate", json=submission_data)
                
                if test_response.status_code == 200:
                    result = test_response.json()
                    print(f"✅ Format accepted. Calculated score: {result.get('calculatedScore', 'N/A')}%")
                else:
                    print(f"❌ Format rejected: {test_response.status_code} - {test_response.text}")
            
            self.log_test("API Format Verification", True, "Completed format verification testing")
            return True
                
        except Exception as e:
            self.log_test("API Format Verification", False, f"Exception: {str(e)}")
            return False
    
    def test_error_scenarios(self):
        """Test 8: Error Scenarios and Edge Cases"""
        try:
            error_tests = []
            
            # Test 1: Invalid test ID
            invalid_response = self.session.get(f"{BACKEND_URL}/final-tests/invalid-test-id")
            error_tests.append({
                "test": "Invalid Test ID",
                "expected": 404,
                "actual": invalid_response.status_code,
                "success": invalid_response.status_code == 404
            })
            
            # Test 2: Unauthorized access (no token)
            no_auth_session = requests.Session()
            no_auth_response = no_auth_session.get(f"{BACKEND_URL}/final-tests/{self.test_final_test_id}")
            error_tests.append({
                "test": "Unauthorized Access",
                "expected": 401,
                "actual": no_auth_response.status_code,
                "success": no_auth_response.status_code == 401
            })
            
            # Test 3: Invalid submission format
            invalid_submission = self.session.post(f"{BACKEND_URL}/final-test-attempts", json={
                "testId": self.test_final_test_id,
                "answers": "invalid_format",  # Should be array
                "timeSpent": -1  # Invalid time
            })
            error_tests.append({
                "test": "Invalid Submission Format",
                "expected": 422,
                "actual": invalid_submission.status_code,
                "success": invalid_submission.status_code in [400, 422]
            })
            
            # Summary
            passed_error_tests = sum(1 for test in error_tests if test["success"])
            total_error_tests = len(error_tests)
            
            print(f"\n🔍 ERROR HANDLING VERIFICATION:")
            for test in error_tests:
                status = "✅" if test["success"] else "❌"
                print(f"{status} {test['test']}: Expected {test['expected']}, Got {test['actual']}")
            
            self.log_test("Error Scenarios Testing", passed_error_tests == total_error_tests, 
                        f"Passed {passed_error_tests}/{total_error_tests} error handling tests")
            
            return passed_error_tests == total_error_tests
                
        except Exception as e:
            self.log_test("Error Scenarios Testing", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all frontend flow tests"""
        print("🚀 Starting Final Frontend Flow Backend Testing")
        print("Testing complete frontend-to-backend workflow for program creation and final test taking")
        print("=" * 80)
        
        # Test sequence matching the review request
        tests = [
            ("Admin Authentication", self.authenticate_admin),
            ("Program with Final Test Creation", self.create_program_with_final_test),
            ("Student Authentication", self.authenticate_student),
            ("Student Program Enrollment", self.enroll_student_in_program),
            ("Student Final Test Access", self.test_student_final_test_access),
            ("Final Test Submission and Scoring", self.test_final_test_submission),
            ("API Format Verification", self.test_api_format_verification),
            ("Error Scenarios Testing", self.test_error_scenarios)
        ]
        
        # Run tests in sequence
        for test_name, test_func in tests:
            print(f"\n🔄 Running: {test_name}")
            success = test_func()
            if not success and test_name in ["Admin Authentication", "Program with Final Test Creation"]:
                print(f"❌ Critical test failed: {test_name}. Stopping execution.")
                break
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 FINAL FRONTEND FLOW TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if passed_tests < total_tests:
            print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
            print("\n🔍 FAILED TESTS ANALYSIS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  ❌ {result['test']}")
                    print(f"     Issue: {result['details']}")
        
        # Specific analysis for the review request
        print(f"\n🎯 REVIEW REQUEST ANALYSIS:")
        print("=" * 50)
        
        auth_success = any(r["test"] == "Admin Authentication" and r["success"] for r in self.test_results)
        program_creation_success = any(r["test"] == "Program with Final Test Creation" and r["success"] for r in self.test_results)
        student_auth_success = any(r["test"] == "Student Authentication" and r["success"] for r in self.test_results)
        test_submission_success = any(r["test"] == "Final Test Submission and Scoring" and r["success"] for r in self.test_results)
        
        print(f"1. Admin Login & Program Creation: {'✅ WORKING' if auth_success and program_creation_success else '❌ FAILING'}")
        print(f"2. Student Login & Test Access: {'✅ WORKING' if student_auth_success else '❌ FAILING'}")
        print(f"3. Test Submission & Scoring: {'✅ WORKING' if test_submission_success else '❌ FAILING'}")
        
        if not test_submission_success:
            print(f"\n🚨 CRITICAL ISSUE DETECTED:")
            print(f"   The main issue from the review request (0% score) appears to be present.")
            print(f"   Check the 'Final Test Submission and Scoring' test details above.")
        
        print(f"\n🏁 OVERALL STATUS: {'✅ FRONTEND-BACKEND FLOW WORKING' if success_rate >= 75 else '❌ ISSUES DETECTED'}")
        
        return success_rate >= 75

if __name__ == "__main__":
    tester = FinalFrontendFlowTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)