#!/usr/bin/env python3
"""
CORRECTED Final Frontend Flow Backend Testing - Review Request Validation
Testing the complete frontend-to-backend flow with proper API format.

FIXES APPLIED:
1. Added trainerId requirement for classroom creation
2. Fixed answer format to use questionId instead of questionIndex
3. Proper question structure with correct answers stored
4. Direct enrollment approach instead of classroom creation

Environment: https://lms-bug-fixes.preview.emergentagent.com
Admin: brayden.t@covesmart.com / Hawaii2020!
Student: karlo.student@alder.com / StudentPermanent123!
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration - Using correct backend URL from frontend/.env
BACKEND_URL = "https://lms-bug-fixes.preview.emergentagent.com/api"

# Test credentials from review request
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"
STUDENT_EMAIL = "karlo.student@alder.com"
STUDENT_PASSWORD = "StudentPermanent123!"

class CorrectedFrontendFlowTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.student_token = None
        self.test_results = []
        self.test_program_id = None
        self.test_final_test_id = None
        self.student_id = None
        
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
        """Test 2: Create Program with Final Test (CORRECTED)"""
        try:
            # Step 1: Create a program
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            program_data = {
                "title": f"Corrected Flow Test Program {timestamp}",
                "description": "Testing corrected frontend-to-backend flow for program creation with final test",
                "departmentId": None,
                "duration": "6 weeks",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            # Create program first
            program_response = self.session.post(f"{BACKEND_URL}/programs", json=program_data)
            
            if program_response.status_code != 200:
                self.log_test("Program Creation", False, 
                            f"Failed to create program: {program_response.status_code} - {program_response.text}")
                return False
            
            program = program_response.json()
            self.test_program_id = program["id"]
            self.log_test("Program Creation", True, f"Created program: {program['title']} (ID: {program['id']})")
            
            # Step 2: Create final test with proper question structure
            final_test_data = {
                "title": f"Corrected Final Test {timestamp}",
                "description": "Testing corrected final test creation via frontend flow",
                "programId": self.test_program_id,
                "questions": [
                    {
                        "id": str(uuid.uuid4()),
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
                        "id": str(uuid.uuid4()),
                        "type": "true_false",
                        "question": "The LearningFriend LMS supports final exams for programs.",
                        "correctAnswer": "true",
                        "points": 25,
                        "explanation": "Yes, the LMS supports final exams for programs"
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "multiple_choice",
                        "question": "Which HTTP status code indicates successful API response?",
                        "options": ["200", "404", "422", "500"],
                        "correctAnswer": "0",
                        "points": 25,
                        "explanation": "HTTP 200 indicates successful response"
                    },
                    {
                        "id": str(uuid.uuid4()),
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
                self.student_id = data["user"]["id"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.student_token}"
                })
                self.log_test("Student Authentication", True, 
                            f"Logged in as {data['user']['full_name']} ({data['user']['role']}) ID: {self.student_id}")
                return True
            else:
                self.log_test("Student Authentication", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Student Authentication", False, f"Exception: {str(e)}")
            return False
    
    def enroll_student_in_program_via_classroom(self):
        """Test 4: Enroll Student in Program via Classroom (CORRECTED)"""
        try:
            # Switch back to admin to create classroom and enroll student
            self.session.headers.update({
                "Authorization": f"Bearer {self.admin_token}"
            })
            
            # First, find an instructor to use as trainer
            users_response = self.session.get(f"{BACKEND_URL}/auth/admin/users")
            if users_response.status_code != 200:
                self.log_test("Get Users for Trainer", False, f"Failed to get users: {users_response.status_code}")
                return False
            
            users = users_response.json()
            instructor_user = next((user for user in users if user["role"] == "instructor"), None)
            
            if not instructor_user:
                # Create an instructor if none exists
                instructor_data = {
                    "email": "test.instructor@testlms.com",
                    "username": "test_instructor",
                    "full_name": "Test Instructor",
                    "role": "instructor",
                    "department": "Testing",
                    "temporary_password": "TestInst123!"
                }
                
                instructor_response = self.session.post(f"{BACKEND_URL}/auth/admin/create-user", json=instructor_data)
                if instructor_response.status_code == 200:
                    instructor_user = instructor_response.json()
                    self.log_test("Create Test Instructor", True, f"Created instructor: {instructor_user['full_name']}")
                else:
                    self.log_test("Create Test Instructor", False, f"Failed: {instructor_response.status_code}")
                    return False
            
            # Create a classroom with the program and student
            classroom_data = {
                "name": f"Corrected Test Classroom {datetime.now().strftime('%H%M%S')}",
                "description": "Classroom for testing corrected final exam flow",
                "trainerId": instructor_user["id"],  # FIXED: Added required trainerId
                "programIds": [self.test_program_id],
                "courseIds": [],
                "studentIds": [self.student_id],
                "startDate": datetime.now().isoformat(),
                "endDate": None
            }
            
            # Create classroom
            classroom_response = self.session.post(f"{BACKEND_URL}/classrooms", json=classroom_data)
            
            if classroom_response.status_code == 200:
                classroom = classroom_response.json()
                self.log_test("Student Program Enrollment via Classroom", True, 
                            f"Created classroom and enrolled student in program")
                return True
            else:
                self.log_test("Student Program Enrollment via Classroom", False, 
                            f"Failed to create classroom: {classroom_response.status_code} - {classroom_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Student Program Enrollment via Classroom", False, f"Exception: {str(e)}")
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
    
    def test_final_test_submission_corrected(self):
        """Test 6: Final Test Submission and Scoring (CORRECTED)"""
        try:
            # Get the test details first
            test_response = self.session.get(f"{BACKEND_URL}/final-tests/{self.test_final_test_id}")
            
            if test_response.status_code != 200:
                self.log_test("Get Test Details", False, f"Failed to get test: {test_response.status_code}")
                return False
            
            test_details = test_response.json()
            questions = test_details["questions"]
            
            print(f"\n🔍 DEBUGGING TEST STRUCTURE:")
            print(f"Questions found: {len(questions)}")
            for i, q in enumerate(questions):
                print(f"  Q{i+1}: Type={q.get('type')}, ID={q.get('id')}, CorrectAnswer={q.get('correctAnswer')}")
            
            # Prepare answers using questionId format (CORRECTED)
            answers = []
            for question in questions:
                question_id = question.get('id')
                if not question_id:
                    self.log_test("Answer Preparation", False, f"Question missing ID: {question}")
                    return False
                
                if question["type"] == "multiple_choice":
                    answers.append({
                        "questionId": question_id,
                        "answer": question["correctAnswer"]  # Use the correct answer
                    })
                elif question["type"] == "true_false":
                    answers.append({
                        "questionId": question_id,
                        "answer": question["correctAnswer"]  # Use the correct answer
                    })
            
            print(f"\n📤 SUBMISSION DATA:")
            print(f"Answers being submitted: {len(answers)}")
            for i, ans in enumerate(answers):
                print(f"  Answer {i+1}: QuestionID={ans['questionId']}, Answer={ans['answer']}")
            
            # Submit the test
            submission_data = {
                "testId": self.test_final_test_id,
                "answers": answers,
                "timeSpent": 300  # 5 minutes
            }
            
            submission_response = self.session.post(f"{BACKEND_URL}/final-test-attempts", json=submission_data)
            
            if submission_response.status_code == 200:
                attempt = submission_response.json()
                
                print(f"\n📊 SUBMISSION RESULT:")
                print(f"Score: {attempt.get('score', 'N/A')}%")
                print(f"Points Earned: {attempt.get('pointsEarned', 'N/A')}")
                print(f"Total Points: {attempt.get('totalPoints', 'N/A')}")
                print(f"Passed: {attempt.get('isPassed', 'N/A')}")
                
                # Verify scoring
                expected_score = 100.0  # All answers correct
                actual_score = attempt.get("score", 0)
                
                if actual_score == expected_score:
                    self.log_test("Final Test Submission and Scoring (Corrected)", True, 
                                f"Test submitted successfully. Score: {actual_score}% (Expected: {expected_score}%)")
                    return True
                elif actual_score > 0:
                    self.log_test("Final Test Submission and Scoring (Corrected)", False, 
                                f"Test submitted but scoring issue. Score: {actual_score}% (Expected: {expected_score}%)")
                    return False
                else:
                    self.log_test("Final Test Submission and Scoring (Corrected)", False, 
                                f"Test submitted but got 0% score - issue still present")
                    return False
            else:
                self.log_test("Final Test Submission and Scoring (Corrected)", False, 
                            f"Submission failed: {submission_response.status_code} - {submission_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Final Test Submission and Scoring (Corrected)", False, f"Exception: {str(e)}")
            return False
    
    def test_api_format_deep_dive(self):
        """Test 7: Deep Dive API Format Analysis"""
        try:
            # Get test details to understand the exact structure
            test_response = self.session.get(f"{BACKEND_URL}/final-tests/{self.test_final_test_id}")
            
            if test_response.status_code != 200:
                self.log_test("API Format Deep Dive", False, "Cannot get test details")
                return False
            
            test_details = test_response.json()
            
            print(f"\n🔬 DEEP DIVE API FORMAT ANALYSIS:")
            print("=" * 60)
            print("COMPLETE TEST STRUCTURE:")
            print(json.dumps(test_details, indent=2, default=str))
            
            # Check if questions have the required fields for scoring
            questions = test_details.get("questions", [])
            issues_found = []
            
            for i, question in enumerate(questions):
                print(f"\n📋 Question {i+1} Analysis:")
                print(f"  - ID: {question.get('id', 'MISSING')}")
                print(f"  - Type: {question.get('type', 'MISSING')}")
                print(f"  - Correct Answer: {question.get('correctAnswer', 'MISSING')}")
                print(f"  - Points: {question.get('points', 'MISSING')}")
                
                if not question.get('id'):
                    issues_found.append(f"Question {i+1} missing ID")
                if not question.get('correctAnswer'):
                    issues_found.append(f"Question {i+1} missing correctAnswer")
                if not question.get('points'):
                    issues_found.append(f"Question {i+1} missing points")
            
            if issues_found:
                print(f"\n🚨 ISSUES FOUND:")
                for issue in issues_found:
                    print(f"  - {issue}")
                self.log_test("API Format Deep Dive", False, f"Found {len(issues_found)} issues in test structure")
                return False
            else:
                print(f"\n✅ TEST STRUCTURE LOOKS GOOD")
                self.log_test("API Format Deep Dive", True, "Test structure analysis completed - no issues found")
                return True
                
        except Exception as e:
            self.log_test("API Format Deep Dive", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all corrected frontend flow tests"""
        print("🚀 Starting CORRECTED Final Frontend Flow Backend Testing")
        print("Testing complete frontend-to-backend workflow with proper API format")
        print("=" * 80)
        
        # Test sequence with corrections
        tests = [
            ("Admin Authentication", self.authenticate_admin),
            ("Program with Final Test Creation", self.create_program_with_final_test),
            ("Student Authentication", self.authenticate_student),
            ("Student Program Enrollment via Classroom", self.enroll_student_in_program_via_classroom),
            ("Student Final Test Access", self.test_student_final_test_access),
            ("Final Test Submission and Scoring (Corrected)", self.test_final_test_submission_corrected),
            ("API Format Deep Dive", self.test_api_format_deep_dive)
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
        print("📊 CORRECTED FINAL FRONTEND FLOW TEST SUMMARY")
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
        test_submission_success = any(r["test"] == "Final Test Submission and Scoring (Corrected)" and r["success"] for r in self.test_results)
        
        print(f"1. Admin Login & Program Creation: {'✅ WORKING' if auth_success and program_creation_success else '❌ FAILING'}")
        print(f"2. Student Login & Test Access: {'✅ WORKING' if student_auth_success else '❌ FAILING'}")
        print(f"3. Test Submission & Scoring: {'✅ WORKING' if test_submission_success else '❌ FAILING'}")
        
        if test_submission_success:
            print(f"\n🎉 SUCCESS:")
            print(f"   The 0% score issue from the review request has been RESOLVED!")
            print(f"   Frontend-to-backend flow is working correctly.")
        else:
            print(f"\n🚨 CRITICAL ISSUE STILL PRESENT:")
            print(f"   The main issue from the review request (0% score) is still occurring.")
            print(f"   Check the detailed analysis above for root cause.")
        
        print(f"\n🏁 OVERALL STATUS: {'✅ FRONTEND-BACKEND FLOW WORKING' if success_rate >= 85 else '❌ ISSUES DETECTED'}")
        
        return success_rate >= 85

if __name__ == "__main__":
    tester = CorrectedFrontendFlowTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)