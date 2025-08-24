#!/usr/bin/env python3
"""
Comprehensive Testing for All Quick Fixes - Review Request
"""

import requests
import json
import sys

BACKEND_URL = "https://quiz-rebuild.preview.emergentagent.com/api"
TEST_TIMEOUT = 10

class FixTester:
    def __init__(self):
        self.auth_tokens = {}
        self.test_results = []
        self.test_quiz_id = None
        
    def log_result(self, test_name, status, message, details=None):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'details': details
        }
        self.test_results.append(result)
        
        if status == 'PASS':
            print(f"✅ {test_name}: {message}")
        else:
            print(f"❌ {test_name}: {message}")
            if details:
                print(f"   Details: {details}")
    
    def setup_authentication(self):
        """Setup authentication tokens for all user types"""
        print("🔐 Setting up authentication...")
        
        users = [
            {"username": "admin", "password": "NewAdmin123!", "role": "admin"},
            {"username": "instructor", "password": "Instructor123!", "role": "instructor"},
            {"username": "student", "password": "Student123!", "role": "learner"}
        ]
        
        for user in users:
            login_data = {
                "username_or_email": user["username"],
                "password": user["password"]
            }
            
            try:
                response = requests.post(
                    f"{BACKEND_URL}/auth/login",
                    json=login_data,
                    timeout=TEST_TIMEOUT,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    token = response.json().get('access_token')
                    self.auth_tokens[user["role"]] = token
                    print(f"✅ {user['role'].title()} authentication successful")
                else:
                    print(f"❌ {user['role'].title()} authentication failed: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ {user['role'].title()} authentication error: {e}")
                return False
        
        return len(self.auth_tokens) == 3
    
    def test_quiz_question_model_validation(self):
        """Test Quiz API Question Model Validation fixes"""
        print("\n🧩 Testing Quiz API Question Model Validation")
        print("-" * 50)
        
        if "instructor" not in self.auth_tokens:
            self.log_result("Quiz Question Model Validation", "SKIP", "No instructor token")
            return False
        
        # Test 1: Multiple choice with string index
        mc_quiz = {
            "title": "Multiple Choice Test",
            "description": "Testing MC validation",
            "questions": [
                {
                    "type": "multiple_choice",
                    "question": "What is 2 + 2?",
                    "options": ["3", "4", "5", "6"],
                    "correctAnswer": "1",  # String index
                    "points": 10
                }
            ],
            "timeLimit": 30,
            "attempts": 3,
            "passingScore": 70.0,
            "isPublished": True
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/quizzes",
                json=mc_quiz,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if response.status_code == 200:
                quiz_data = response.json()
                self.test_quiz_id = quiz_data.get('id')
                self.log_result(
                    "Quiz Creation - Multiple Choice",
                    "PASS",
                    "Successfully created quiz with multiple choice questions",
                    f"Quiz ID: {self.test_quiz_id}"
                )
            else:
                self.log_result(
                    "Quiz Creation - Multiple Choice",
                    "FAIL",
                    f"Failed with status {response.status_code}",
                    response.text
                )
                return False
        except Exception as e:
            self.log_result("Quiz Creation - Multiple Choice", "FAIL", "Request failed", str(e))
            return False
        
        # Test 2: True/False with text answer
        tf_quiz = {
            "title": "True False Test",
            "description": "Testing T/F validation",
            "questions": [
                {
                    "type": "true_false",
                    "question": "The sky is blue.",
                    "options": [],
                    "correctAnswer": "true",  # Text answer
                    "points": 5
                }
            ],
            "timeLimit": 15,
            "attempts": 2,
            "passingScore": 80.0,
            "isPublished": True
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/quizzes",
                json=tf_quiz,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if response.status_code == 200:
                self.log_result(
                    "Quiz Creation - True/False",
                    "PASS",
                    "Successfully created quiz with true/false questions"
                )
            else:
                self.log_result(
                    "Quiz Creation - True/False",
                    "FAIL",
                    f"Failed with status {response.status_code}",
                    response.text
                )
                return False
        except Exception as e:
            self.log_result("Quiz Creation - True/False", "FAIL", "Request failed", str(e))
            return False
        
        # Test 3: Short answer with text validation
        sa_quiz = {
            "title": "Short Answer Test",
            "description": "Testing SA validation",
            "questions": [
                {
                    "type": "short_answer",
                    "question": "What is the capital of France?",
                    "options": [],
                    "correctAnswer": "Paris",  # Text answer
                    "points": 15
                }
            ],
            "timeLimit": 20,
            "attempts": 1,
            "passingScore": 90.0,
            "isPublished": True
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/quizzes",
                json=sa_quiz,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if response.status_code == 200:
                self.log_result(
                    "Quiz Creation - Short Answer",
                    "PASS",
                    "Successfully created quiz with short answer questions"
                )
            else:
                self.log_result(
                    "Quiz Creation - Short Answer",
                    "FAIL",
                    f"Failed with status {response.status_code}",
                    response.text
                )
                return False
        except Exception as e:
            self.log_result("Quiz Creation - Short Answer", "FAIL", "Request failed", str(e))
            return False
        
        return True
    
    def test_quiz_attempt_scoring(self):
        """Test Quiz Attempt Scoring improvements"""
        print("\n🎯 Testing Quiz Attempt Scoring Improvements")
        print("-" * 50)
        
        if "learner" not in self.auth_tokens or not self.test_quiz_id:
            self.log_result("Quiz Attempt Scoring", "SKIP", "Missing requirements")
            return False
        
        # Test correct answer scoring
        attempt_data = {
            "quizId": self.test_quiz_id,
            "answers": ["1"]  # Correct answer (index 1 = "4")
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/quiz-attempts",
                json=attempt_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["learner"]}'
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                score = result.get('score', 0)
                is_passed = result.get('isPassed', False)
                
                if score == 100.0 and is_passed:
                    self.log_result(
                        "Quiz Scoring - Correct Answer",
                        "PASS",
                        f"Scoring logic working correctly: {score}% (Passed: {is_passed})"
                    )
                else:
                    self.log_result(
                        "Quiz Scoring - Correct Answer",
                        "FAIL",
                        f"Unexpected score: {score}% (Passed: {is_passed})"
                    )
                    return False
            else:
                self.log_result(
                    "Quiz Scoring - Correct Answer",
                    "FAIL",
                    f"Failed with status {response.status_code}",
                    response.text
                )
                return False
        except Exception as e:
            self.log_result("Quiz Scoring - Correct Answer", "FAIL", "Request failed", str(e))
            return False
        
        # Test error handling with wrong answer count
        wrong_attempt = {
            "quizId": self.test_quiz_id,
            "answers": ["1", "2", "3"]  # Too many answers
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/quiz-attempts",
                json=wrong_attempt,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["learner"]}'
                }
            )
            
            if response.status_code == 400:
                self.log_result(
                    "Quiz Scoring - Error Handling",
                    "PASS",
                    "Properly handled incorrect answer count"
                )
            else:
                self.log_result(
                    "Quiz Scoring - Error Handling",
                    "FAIL",
                    f"Expected 400 but got {response.status_code}",
                    response.text
                )
                return False
        except Exception as e:
            self.log_result("Quiz Scoring - Error Handling", "FAIL", "Request failed", str(e))
            return False
        
        return True
    
    def test_certificate_enrollment_validation(self):
        """Test Certificate API Enrollment Validation flexibility"""
        print("\n🏆 Testing Certificate API Enrollment Validation")
        print("-" * 50)
        
        if "admin" not in self.auth_tokens or "instructor" not in self.auth_tokens:
            self.log_result("Certificate Enrollment Validation", "SKIP", "Missing tokens")
            return False
        
        # Get test data
        try:
            # Get users
            users_response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if users_response.status_code != 200:
                self.log_result("Certificate Test Setup", "FAIL", "Failed to get users")
                return False
            
            users = users_response.json()
            student_id = None
            for user in users:
                if user.get('role') == 'learner':
                    student_id = user.get('id')
                    break
            
            if not student_id:
                self.log_result("Certificate Test Setup", "FAIL", "No student found")
                return False
            
            # Get courses
            courses_response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if courses_response.status_code != 200:
                self.log_result("Certificate Test Setup", "FAIL", "Failed to get courses")
                return False
            
            courses = courses_response.json()
            if not courses:
                self.log_result("Certificate Test Setup", "FAIL", "No courses found")
                return False
            
            course_id = courses[0].get('id')
            
        except Exception as e:
            self.log_result("Certificate Test Setup", "FAIL", "Setup failed", str(e))
            return False
        
        # Test 1: Admin can create certificate WITHOUT enrollment
        cert_data = {
            "studentId": student_id,
            "courseId": course_id,
            "type": "completion",
            "template": "default"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/certificates",
                json=cert_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 200:
                self.log_result(
                    "Certificate - Admin Override",
                    "PASS",
                    "Admin successfully created certificate without enrollment"
                )
            else:
                self.log_result(
                    "Certificate - Admin Override",
                    "FAIL",
                    f"Admin failed with status {response.status_code}",
                    response.text
                )
                return False
        except Exception as e:
            self.log_result("Certificate - Admin Override", "FAIL", "Request failed", str(e))
            return False
        
        # Test 2: Instructor WITHOUT enrollment should fail
        try:
            response = requests.post(
                f"{BACKEND_URL}/certificates",
                json={
                    "studentId": student_id,
                    "courseId": course_id,
                    "type": "achievement",
                    "template": "premium"
                },
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if response.status_code == 400:
                self.log_result(
                    "Certificate - Instructor Enrollment Check",
                    "PASS",
                    "Instructor correctly denied without enrollment"
                )
            else:
                self.log_result(
                    "Certificate - Instructor Enrollment Check",
                    "FAIL",
                    f"Expected 400 but got {response.status_code}",
                    response.text
                )
                return False
        except Exception as e:
            self.log_result("Certificate - Instructor Enrollment Check", "FAIL", "Request failed", str(e))
            return False
        
        return True
    
    def test_input_validation_improvements(self):
        """Test stricter input validation improvements"""
        print("\n✅ Testing Input Validation Improvements")
        print("-" * 50)
        
        if "instructor" not in self.auth_tokens:
            self.log_result("Input Validation", "SKIP", "No instructor token")
            return False
        
        # Test 1: Empty course title
        invalid_course = {
            "title": "",
            "description": "Test",
            "category": "Testing"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/courses",
                json=invalid_course,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if response.status_code == 422:
                self.log_result(
                    "Input Validation - Empty Title",
                    "PASS",
                    "Properly rejected empty course title"
                )
            else:
                self.log_result(
                    "Input Validation - Empty Title",
                    "FAIL",
                    f"Expected 422 but got {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_result("Input Validation - Empty Title", "FAIL", "Request failed", str(e))
            return False
        
        # Test 2: Invalid access type
        invalid_access = {
            "title": "Valid Title",
            "description": "Test",
            "category": "Testing",
            "accessType": "invalid_type"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/courses",
                json=invalid_access,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if response.status_code == 422:
                self.log_result(
                    "Input Validation - Invalid Access Type",
                    "PASS",
                    "Properly rejected invalid access type"
                )
            else:
                self.log_result(
                    "Input Validation - Invalid Access Type",
                    "FAIL",
                    f"Expected 422 but got {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_result("Input Validation - Invalid Access Type", "FAIL", "Request failed", str(e))
            return False
        
        # Test 3: Quiz with no questions
        invalid_quiz = {
            "title": "Valid Quiz",
            "description": "Test",
            "questions": [],
            "timeLimit": 30,
            "attempts": 1,
            "passingScore": 70.0
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/quizzes",
                json=invalid_quiz,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if response.status_code == 422:
                self.log_result(
                    "Input Validation - No Questions",
                    "PASS",
                    "Properly rejected quiz with no questions"
                )
            else:
                self.log_result(
                    "Input Validation - No Questions",
                    "FAIL",
                    f"Expected 422 but got {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_result("Input Validation - No Questions", "FAIL", "Request failed", str(e))
            return False
        
        # Test 4: Invalid time limit
        invalid_time = {
            "title": "Valid Quiz",
            "description": "Test",
            "questions": [
                {
                    "type": "multiple_choice",
                    "question": "Test?",
                    "options": ["A", "B"],
                    "correctAnswer": "0",
                    "points": 10
                }
            ],
            "timeLimit": 500,  # Over limit
            "attempts": 1,
            "passingScore": 70.0
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/quizzes",
                json=invalid_time,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if response.status_code == 422:
                self.log_result(
                    "Input Validation - Invalid Time Limit",
                    "PASS",
                    "Properly rejected invalid time limit"
                )
            else:
                self.log_result(
                    "Input Validation - Invalid Time Limit",
                    "FAIL",
                    f"Expected 422 but got {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_result("Input Validation - Invalid Time Limit", "FAIL", "Request failed", str(e))
            return False
        
        return True
    
    def test_end_to_end_workflow(self):
        """Test end-to-end workflow to ensure no regression"""
        print("\n🔄 Testing End-to-End Workflow")
        print("-" * 50)
        
        if not all(role in self.auth_tokens for role in ["admin", "instructor", "learner"]):
            self.log_result("E2E Workflow", "SKIP", "Missing tokens")
            return False
        
        try:
            # Step 1: Create course
            course_data = {
                "title": "E2E Test Course",
                "description": "End-to-end testing course",
                "category": "Testing",
                "accessType": "open"
            }
            
            course_response = requests.post(
                f"{BACKEND_URL}/courses",
                json=course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if course_response.status_code != 200:
                self.log_result("E2E - Course Creation", "FAIL", f"Status {course_response.status_code}")
                return False
            
            course_id = course_response.json().get('id')
            
            # Step 2: Create quiz
            quiz_data = {
                "title": "E2E Test Quiz",
                "description": "End-to-end testing quiz",
                "courseId": course_id,
                "questions": [
                    {
                        "type": "multiple_choice",
                        "question": "What is this test for?",
                        "options": ["Testing", "Fun", "Learning", "All above"],
                        "correctAnswer": "3",
                        "points": 100
                    }
                ],
                "timeLimit": 10,
                "attempts": 1,
                "passingScore": 80.0,
                "isPublished": True
            }
            
            quiz_response = requests.post(
                f"{BACKEND_URL}/quizzes",
                json=quiz_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if quiz_response.status_code != 200:
                self.log_result("E2E - Quiz Creation", "FAIL", f"Status {quiz_response.status_code}")
                return False
            
            quiz_id = quiz_response.json().get('id')
            
            # Step 3: Student enrollment
            enrollment_data = {"courseId": course_id}
            
            enrollment_response = requests.post(
                f"{BACKEND_URL}/enrollments",
                json=enrollment_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["learner"]}'
                }
            )
            
            if enrollment_response.status_code != 200:
                self.log_result("E2E - Enrollment", "FAIL", f"Status {enrollment_response.status_code}")
                return False
            
            # Step 4: Quiz attempt
            attempt_data = {
                "quizId": quiz_id,
                "answers": ["3"]  # Correct answer
            }
            
            attempt_response = requests.post(
                f"{BACKEND_URL}/quiz-attempts",
                json=attempt_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["learner"]}'
                }
            )
            
            if attempt_response.status_code != 200:
                self.log_result("E2E - Quiz Attempt", "FAIL", f"Status {attempt_response.status_code}")
                return False
            
            attempt_result = attempt_response.json()
            if not attempt_result.get('isPassed', False):
                self.log_result("E2E - Quiz Pass", "FAIL", "Student did not pass quiz")
                return False
            
            # Step 5: Certificate creation
            me_response = requests.get(
                f"{BACKEND_URL}/auth/me",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["learner"]}'}
            )
            
            if me_response.status_code != 200:
                self.log_result("E2E - Get Student ID", "FAIL", f"Status {me_response.status_code}")
                return False
            
            student_id = me_response.json().get('id')
            
            cert_data = {
                "studentId": student_id,
                "courseId": course_id,
                "type": "completion",
                "template": "default"
            }
            
            cert_response = requests.post(
                f"{BACKEND_URL}/certificates",
                json=cert_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if cert_response.status_code == 200:
                self.log_result(
                    "E2E Workflow - Complete",
                    "PASS",
                    "Successfully completed: Course → Quiz → Attempt → Certificate"
                )
            else:
                self.log_result("E2E - Certificate", "FAIL", f"Status {cert_response.status_code}")
                return False
            
        except Exception as e:
            self.log_result("E2E Workflow", "FAIL", "Workflow failed", str(e))
            return False
        
        return True
    
    def run_all_tests(self):
        """Run all focused tests"""
        print("🎯 COMPREHENSIVE TESTING OF QUICK FIXES")
        print("=" * 60)
        
        # Check backend health
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=TEST_TIMEOUT)
            if response.status_code != 200:
                print(f"❌ Backend health check failed: {response.status_code}")
                return False
            print("✅ Backend is accessible")
        except Exception as e:
            print(f"❌ Backend not accessible: {e}")
            return False
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed")
            return False
        
        # Run all tests
        tests = [
            self.test_quiz_question_model_validation,
            self.test_quiz_attempt_scoring,
            self.test_certificate_enrollment_validation,
            self.test_input_validation_improvements,
            self.test_end_to_end_workflow
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {e}")
                failed += 1
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            print(f"{status_icon} {result['test']}: {result['message']}")
        
        print(f"\n📈 Overall Results:")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {(passed / (passed + failed) * 100):.1f}%")
        
        return failed == 0

if __name__ == "__main__":
    tester = FixTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All comprehensive tests PASSED!")
        sys.exit(0)
    else:
        print("\n⚠️  Some comprehensive tests FAILED!")
        sys.exit(1)