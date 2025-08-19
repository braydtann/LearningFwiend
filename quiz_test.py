#!/usr/bin/env python3
"""
Quiz Functionality Testing Suite for LearningFwiend LMS Application
Tests comprehensive quiz functionality as requested in the review
"""

import requests
import json
import os
import sys
from datetime import datetime
import time

# Configuration - Using Local Backend URL
BACKEND_URL = "http://localhost:8001/api"
TEST_TIMEOUT = 15

class QuizTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}  # Store auth tokens for different users
        
    def log_result(self, test_name, status, message, details=None):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.results.append(result)
        
        if status == 'PASS':
            self.passed += 1
            print(f"✅ {test_name}: {message}")
        elif status == 'SKIP':
            print(f"⏭️  {test_name}: {message}")
        else:
            self.failed += 1
            print(f"❌ {test_name}: {message}")
            if details:
                print(f"   Details: {details}")
    
    def test_admin_login(self):
        """Test admin user login"""
        try:
            login_data = {
                "username_or_email": "brayden.t@covesmart.com",
                "password": "Hawaii2020!"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                
                if token and user_info.get('role') == 'admin':
                    self.auth_tokens['admin'] = token
                    self.log_result(
                        "Admin Login Test", 
                        "PASS", 
                        f"Successfully logged in as admin: {user_info.get('email')}",
                        f"Token received, role verified: {user_info.get('role')}"
                    )
                    return True
            
            self.log_result(
                "Admin Login Test", 
                "FAIL", 
                f"Admin login failed with status {response.status_code}",
                f"Response: {response.text}"
            )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Admin Login Test", 
                "FAIL", 
                "Failed to test admin login",
                str(e)
            )
        return False
    
    def test_instructor_login(self):
        """Test instructor user login"""
        try:
            login_data = {
                "username_or_email": "instructor",
                "password": "Instructor123!"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                
                if token and user_info.get('role') == 'instructor':
                    self.auth_tokens['instructor'] = token
                    self.log_result(
                        "Instructor Login Test", 
                        "PASS", 
                        f"Successfully logged in as instructor: {user_info.get('username')}",
                        f"Token received, role verified: {user_info.get('role')}"
                    )
                    return True
            
            self.log_result(
                "Instructor Login Test", 
                "FAIL", 
                f"Instructor login failed with status {response.status_code}",
                f"Response: {response.text}"
            )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Instructor Login Test", 
                "FAIL", 
                "Failed to test instructor login",
                str(e)
            )
        return False
    
    def test_student_login(self):
        """Test student user login"""
        try:
            login_data = {
                "username_or_email": "test.student@learningfwiend.com",
                "password": "Student123!"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                
                if token and user_info.get('role') == 'learner':
                    self.auth_tokens['learner'] = token
                    self.log_result(
                        "Student Login Test", 
                        "PASS", 
                        f"Successfully logged in as student: {user_info.get('username')}",
                        f"Token received, role verified: {user_info.get('role')}"
                    )
                    return True
            
            # Try to create a student user if login fails
            if "admin" in self.auth_tokens:
                student_data = {
                    "email": "test.student@learningfwiend.com",
                    "username": "test.student",
                    "full_name": "Test Student",
                    "role": "learner",
                    "department": "Testing",
                    "temporary_password": "Student123!"
                }
                
                create_response = requests.post(
                    f"{BACKEND_URL}/auth/admin/create-user",
                    json=student_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                    }
                )
                
                if create_response.status_code == 200:
                    # Try login again
                    login_response_new = requests.post(
                        f"{BACKEND_URL}/auth/login",
                        json=login_data,
                        timeout=TEST_TIMEOUT,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if login_response_new.status_code == 200:
                        data = login_response_new.json()
                        token = data.get('access_token')
                        user_info = data.get('user', {})
                        
                        if token and user_info.get('role') == 'learner':
                            self.auth_tokens['learner'] = token
                            self.log_result(
                                "Student Login Test", 
                                "PASS", 
                                f"Successfully created and logged in as test student: {user_info.get('username')}",
                                f"Token received, role verified: {user_info.get('role')}"
                            )
                            return True
            
            self.log_result(
                "Student Login Test", 
                "FAIL", 
                f"Student login failed with status {response.status_code}",
                f"Response: {response.text}"
            )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Login Test", 
                "FAIL", 
                "Failed to test student login",
                str(e)
            )
        return False
    
    def test_quiz_creation_endpoint(self):
        """Test POST /api/quizzes - Create a test quiz to verify quiz creation works"""
        if "instructor" not in self.auth_tokens:
            self.log_result(
                "Quiz Creation Endpoint Test", 
                "SKIP", 
                "No instructor token available for quiz creation test",
                "Instructor authentication required"
            )
            return False
        
        try:
            # Create a test course first (quizzes need to be associated with courses)
            course_data = {
                "title": "Quiz Test Course",
                "description": "Course for testing quiz functionality",
                "category": "Testing",
                "duration": "1 week",
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
                self.log_result(
                    "Quiz Creation Endpoint Test", 
                    "FAIL", 
                    "Failed to create test course for quiz testing",
                    f"Course creation failed with status: {course_response.status_code}"
                )
                return False
            
            course = course_response.json()
            course_id = course.get('id')
            
            # Now create a quiz
            quiz_data = {
                "title": "Test Quiz - Backend API Testing",
                "description": "Comprehensive quiz to test backend quiz creation functionality",
                "courseId": course_id,
                "timeLimit": 30,
                "passingScore": 70,
                "questions": [
                    {
                        "type": "multiple_choice",
                        "question": "What is the primary purpose of this quiz?",
                        "options": [
                            "To test backend functionality",
                            "To confuse students", 
                            "To waste time",
                            "None of the above"
                        ],
                        "correctAnswer": "0",  # String index for multiple choice
                        "points": 10,
                        "explanation": "This quiz is designed to test the backend quiz creation API"
                    },
                    {
                        "type": "true_false",
                        "question": "Backend API testing is important for application reliability",
                        "correctAnswer": "true",  # String for true/false
                        "points": 5,
                        "explanation": "Testing APIs ensures they work correctly and reliably"
                    },
                    {
                        "type": "short_answer",
                        "question": "What HTTP method is used to create a new quiz?",
                        "correctAnswer": "POST",  # String for short answer
                        "points": 5,
                        "explanation": "POST method is used to create new resources"
                    }
                ]
            }
            
            response = requests.post(
                f"{BACKEND_URL}/quizzes",
                json=quiz_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if response.status_code == 200:
                created_quiz = response.json()
                quiz_id = created_quiz.get('id')
                
                # Verify quiz structure
                required_fields = ['id', 'title', 'description', 'courseId', 'timeLimit', 'passingScore', 'questions']
                missing_fields = [field for field in required_fields if field not in created_quiz]
                
                if not missing_fields and len(created_quiz.get('questions', [])) == 3:
                    self.log_result(
                        "Quiz Creation Endpoint Test", 
                        "PASS", 
                        f"Successfully created quiz with all required fields and questions",
                        f"Quiz ID: {quiz_id}, Questions: {len(created_quiz.get('questions', []))}, Course: {course_id}"
                    )
                    return created_quiz
                else:
                    self.log_result(
                        "Quiz Creation Endpoint Test", 
                        "FAIL", 
                        "Quiz created but missing required fields or questions",
                        f"Missing fields: {missing_fields}, Questions count: {len(created_quiz.get('questions', []))}"
                    )
            else:
                self.log_result(
                    "Quiz Creation Endpoint Test", 
                    "FAIL", 
                    f"Failed to create quiz, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Quiz Creation Endpoint Test", 
                "FAIL", 
                "Failed to test quiz creation endpoint",
                str(e)
            )
        return False
    
    def test_quiz_retrieval_endpoints(self):
        """Test quiz retrieval endpoints: GET /api/quizzes, GET /api/quizzes/{quiz_id}, GET /api/quizzes/my-quizzes"""
        if "instructor" not in self.auth_tokens:
            self.log_result(
                "Quiz Retrieval Endpoints Test", 
                "SKIP", 
                "No instructor token available for quiz retrieval test",
                "Instructor authentication required"
            )
            return False
        
        # First create a quiz to test retrieval
        created_quiz = self.test_quiz_creation_endpoint()
        if not created_quiz:
            self.log_result(
                "Quiz Retrieval Endpoints Test", 
                "SKIP", 
                "Could not create test quiz for retrieval testing",
                "Quiz creation required first"
            )
            return False
        
        quiz_id = created_quiz.get('id')
        successful_tests = []
        failed_tests = []
        
        try:
            # Test 1: GET /api/quizzes - List all quizzes
            response = requests.get(
                f"{BACKEND_URL}/quizzes",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
            )
            
            if response.status_code == 200:
                quizzes = response.json()
                if isinstance(quizzes, list) and len(quizzes) > 0:
                    successful_tests.append(f"✅ GET /api/quizzes - Retrieved {len(quizzes)} quizzes")
                else:
                    failed_tests.append(f"❌ GET /api/quizzes - Empty or invalid response")
            else:
                failed_tests.append(f"❌ GET /api/quizzes - Status: {response.status_code}")
            
            # Test 2: GET /api/quizzes/{quiz_id} - Get specific quiz details
            response = requests.get(
                f"{BACKEND_URL}/quizzes/{quiz_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
            )
            
            if response.status_code == 200:
                quiz_details = response.json()
                if quiz_details.get('id') == quiz_id and 'questions' in quiz_details:
                    successful_tests.append(f"✅ GET /api/quizzes/{quiz_id} - Retrieved quiz with questions")
                else:
                    failed_tests.append(f"❌ GET /api/quizzes/{quiz_id} - Invalid quiz data")
            else:
                failed_tests.append(f"❌ GET /api/quizzes/{quiz_id} - Status: {response.status_code}")
            
            # Test 3: GET /api/quizzes/my-quizzes - Get instructor's quizzes
            response = requests.get(
                f"{BACKEND_URL}/quizzes/my-quizzes",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
            )
            
            if response.status_code == 200:
                my_quizzes = response.json()
                if isinstance(my_quizzes, list):
                    successful_tests.append(f"✅ GET /api/quizzes/my-quizzes - Retrieved {len(my_quizzes)} instructor quizzes")
                else:
                    failed_tests.append(f"❌ GET /api/quizzes/my-quizzes - Invalid response format")
            else:
                failed_tests.append(f"❌ GET /api/quizzes/my-quizzes - Status: {response.status_code}")
            
            # Evaluate results
            if len(successful_tests) == 3 and len(failed_tests) == 0:
                self.log_result(
                    "Quiz Retrieval Endpoints Test", 
                    "PASS", 
                    "All quiz retrieval endpoints working correctly",
                    f"All tests passed: {'; '.join(successful_tests)}"
                )
                return True
            else:
                self.log_result(
                    "Quiz Retrieval Endpoints Test", 
                    "FAIL", 
                    f"Some quiz retrieval endpoints failed ({len(successful_tests)}/3 passed)",
                    f"Successful: {'; '.join(successful_tests)}; Failed: {'; '.join(failed_tests)}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Quiz Retrieval Endpoints Test", 
                "FAIL", 
                "Failed to test quiz retrieval endpoints",
                str(e)
            )
        return False
    
    def test_quiz_attempt_endpoints(self):
        """Test quiz attempt endpoints: POST /api/quiz-attempts, GET /api/quiz-attempts, GET /api/quiz-attempts/{attempt_id}"""
        if "learner" not in self.auth_tokens:
            self.log_result(
                "Quiz Attempt Endpoints Test", 
                "SKIP", 
                "No student token available for quiz attempt test",
                "Student authentication required"
            )
            return False
        
        # First create a quiz to attempt
        created_quiz = self.test_quiz_creation_endpoint()
        if not created_quiz:
            self.log_result(
                "Quiz Attempt Endpoints Test", 
                "SKIP", 
                "Could not create test quiz for attempt testing",
                "Quiz creation required first"
            )
            return False
        
        quiz_id = created_quiz.get('id')
        successful_tests = []
        failed_tests = []
        
        try:
            # Test 1: POST /api/quiz-attempts - Create quiz attempt (student taking quiz)
            attempt_data = {
                "quizId": quiz_id,
                "answers": ["0", "true", "POST"]  # Provide answers for all questions
            }
            
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
                created_attempt = response.json()
                attempt_id = created_attempt.get('id')
                if attempt_id and created_attempt.get('quizId') == quiz_id:
                    successful_tests.append(f"✅ POST /api/quiz-attempts - Created attempt {attempt_id}")
                else:
                    failed_tests.append(f"❌ POST /api/quiz-attempts - Invalid attempt data")
                    return False
            else:
                failed_tests.append(f"❌ POST /api/quiz-attempts - Status: {response.status_code}")
                return False
            
            # Test 2: GET /api/quiz-attempts - List quiz attempts
            response = requests.get(
                f"{BACKEND_URL}/quiz-attempts",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["learner"]}'}
            )
            
            if response.status_code == 200:
                attempts = response.json()
                if isinstance(attempts, list) and len(attempts) > 0:
                    successful_tests.append(f"✅ GET /api/quiz-attempts - Retrieved {len(attempts)} attempts")
                else:
                    failed_tests.append(f"❌ GET /api/quiz-attempts - Empty or invalid response")
            else:
                failed_tests.append(f"❌ GET /api/quiz-attempts - Status: {response.status_code}")
            
            # Test 3: GET /api/quiz-attempts/{attempt_id} - Get specific attempt details
            response = requests.get(
                f"{BACKEND_URL}/quiz-attempts/{attempt_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["learner"]}'}
            )
            
            if response.status_code == 200:
                attempt_details = response.json()
                if attempt_details.get('id') == attempt_id:
                    successful_tests.append(f"✅ GET /api/quiz-attempts/{attempt_id} - Retrieved attempt details")
                else:
                    failed_tests.append(f"❌ GET /api/quiz-attempts/{attempt_id} - Invalid attempt data")
            else:
                failed_tests.append(f"❌ GET /api/quiz-attempts/{attempt_id} - Status: {response.status_code}")
            
            # Evaluate results
            if len(successful_tests) == 3 and len(failed_tests) == 0:
                self.log_result(
                    "Quiz Attempt Endpoints Test", 
                    "PASS", 
                    "All quiz attempt endpoints working correctly",
                    f"All tests passed: {'; '.join(successful_tests)}"
                )
                return True
            else:
                self.log_result(
                    "Quiz Attempt Endpoints Test", 
                    "FAIL", 
                    f"Some quiz attempt endpoints failed ({len(successful_tests)}/3 passed)",
                    f"Successful: {'; '.join(successful_tests)}; Failed: {'; '.join(failed_tests)}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Quiz Attempt Endpoints Test", 
                "FAIL", 
                "Failed to test quiz attempt endpoints",
                str(e)
            )
        return False
    
    def test_quiz_results_analytics(self):
        """Test quiz results/analytics endpoints and data structure for results reporting"""
        if "instructor" not in self.auth_tokens:
            self.log_result(
                "Quiz Results Analytics Test", 
                "SKIP", 
                "No instructor token available for quiz analytics test",
                "Instructor authentication required"
            )
            return False
        
        # Create quiz and attempt for analytics testing
        created_quiz = self.test_quiz_creation_endpoint()
        if not created_quiz:
            self.log_result(
                "Quiz Results Analytics Test", 
                "SKIP", 
                "Could not create test quiz for analytics testing",
                "Quiz creation required first"
            )
            return False
        
        quiz_id = created_quiz.get('id')
        successful_tests = []
        failed_tests = []
        
        try:
            # Create a quiz attempt to have data for analytics
            attempt_data = {"quizId": quiz_id}
            attempt_response = requests.post(
                f"{BACKEND_URL}/quiz-attempts",
                json=attempt_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["learner"]}'
                }
            )
            
            if attempt_response.status_code == 200:
                attempt = attempt_response.json()
                successful_tests.append(f"✅ Quiz attempt created for analytics testing")
                
                # Test quiz attempt data structure for results reporting
                required_fields = ['id', 'quizId', 'userId', 'startedAt', 'status']
                missing_fields = [field for field in required_fields if field not in attempt]
                
                if not missing_fields:
                    successful_tests.append(f"✅ Quiz attempt has all required fields for analytics")
                else:
                    failed_tests.append(f"❌ Quiz attempt missing fields: {missing_fields}")
                
                # Test instructor access to quiz attempts (for analytics)
                attempts_response = requests.get(
                    f"{BACKEND_URL}/quiz-attempts",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
                )
                
                if attempts_response.status_code == 200:
                    attempts = attempts_response.json()
                    successful_tests.append(f"✅ Instructor can access quiz attempts for analytics")
                else:
                    failed_tests.append(f"❌ Instructor cannot access quiz attempts - Status: {attempts_response.status_code}")
                
                # Test quiz details for analytics (questions, scoring, etc.)
                quiz_response = requests.get(
                    f"{BACKEND_URL}/quizzes/{quiz_id}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
                )
                
                if quiz_response.status_code == 200:
                    quiz_details = quiz_response.json()
                    analytics_fields = ['questions', 'passingScore', 'timeLimit']
                    available_fields = [field for field in analytics_fields if field in quiz_details]
                    
                    if len(available_fields) == len(analytics_fields):
                        successful_tests.append(f"✅ Quiz has all required fields for analytics dashboard")
                    else:
                        failed_tests.append(f"❌ Quiz missing analytics fields: {set(analytics_fields) - set(available_fields)}")
                else:
                    failed_tests.append(f"❌ Cannot retrieve quiz details for analytics - Status: {quiz_response.status_code}")
            else:
                failed_tests.append(f"❌ Could not create quiz attempt for analytics testing - Status: {attempt_response.status_code}")
            
            # Evaluate results
            if len(successful_tests) >= 3 and len(failed_tests) == 0:
                self.log_result(
                    "Quiz Results Analytics Test", 
                    "PASS", 
                    "Quiz results/analytics data structure is complete and accessible",
                    f"Analytics capabilities verified: {'; '.join(successful_tests)}"
                )
                return True
            else:
                self.log_result(
                    "Quiz Results Analytics Test", 
                    "FAIL", 
                    f"Quiz analytics capabilities incomplete ({len(successful_tests)} successful, {len(failed_tests)} failed)",
                    f"Successful: {'; '.join(successful_tests)}; Failed: {'; '.join(failed_tests)}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Quiz Results Analytics Test", 
                "FAIL", 
                "Failed to test quiz results/analytics",
                str(e)
            )
        return False
    
    def test_complete_quiz_workflow(self):
        """Test the complete quiz workflow: creation → student attempts → results/analytics"""
        workflow_steps = []
        failed_steps = []
        
        try:
            # Step 1: Quiz Creation
            if self.test_quiz_creation_endpoint():
                workflow_steps.append("✅ Quiz Creation")
            else:
                failed_steps.append("❌ Quiz Creation")
                
            # Step 2: Quiz Retrieval
            if self.test_quiz_retrieval_endpoints():
                workflow_steps.append("✅ Quiz Retrieval")
            else:
                failed_steps.append("❌ Quiz Retrieval")
                
            # Step 3: Student Attempts
            if self.test_quiz_attempt_endpoints():
                workflow_steps.append("✅ Student Attempts")
            else:
                failed_steps.append("❌ Student Attempts")
                
            # Step 4: Results/Analytics
            if self.test_quiz_results_analytics():
                workflow_steps.append("✅ Results/Analytics")
            else:
                failed_steps.append("❌ Results/Analytics")
            
            # Evaluate complete workflow
            if len(workflow_steps) == 4 and len(failed_steps) == 0:
                self.log_result(
                    "Complete Quiz Workflow Test", 
                    "PASS", 
                    "Complete quiz workflow functioning correctly from creation to analytics",
                    f"All workflow steps successful: {'; '.join(workflow_steps)}"
                )
                return True
            else:
                self.log_result(
                    "Complete Quiz Workflow Test", 
                    "FAIL", 
                    f"Quiz workflow incomplete ({len(workflow_steps)}/4 steps successful)",
                    f"Successful: {'; '.join(workflow_steps)}; Failed: {'; '.join(failed_steps)}"
                )
        except Exception as e:
            self.log_result(
                "Complete Quiz Workflow Test", 
                "FAIL", 
                "Failed to test complete quiz workflow",
                str(e)
            )
        return False
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE QUIZ FUNCTIONALITY TEST RESULTS SUMMARY")
        print("="*80)
        
        print(f"\n✅ Tests Passed: {self.passed}")
        print(f"❌ Tests Failed: {self.failed}")
        print(f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        if self.failed > 0:
            print(f"\n🔍 FAILED TESTS:")
            for result in self.results:
                if result['status'] == 'FAIL':
                    print(f"   • {result['test']}: {result['message']}")
        
        print(f"\n✅ COMPREHENSIVE QUIZ FUNCTIONALITY TESTING COMPLETED")
        return self.results
    
    def run_quiz_tests(self):
        """Run comprehensive quiz functionality tests"""
        print("🚀 Starting Comprehensive Quiz Functionality Testing Suite")
        print("🔍 FOCUS: Complete Quiz Workflow Testing as Requested")
        print("=" * 80)
        
        # Authentication tests first
        print("\n🔐 AUTHENTICATION SETUP")
        print("=" * 50)
        self.test_admin_login()
        self.test_instructor_login()
        self.test_student_login()
        
        # Comprehensive Quiz Tests
        if self.auth_tokens:
            print("\n🧩 COMPREHENSIVE QUIZ FUNCTIONALITY TESTS")
            print("=" * 70)
            print("Testing complete quiz workflow as requested:")
            print("1. Quiz Creation Endpoint: POST /api/quizzes")
            print("2. Quiz Retrieval Endpoints: GET /api/quizzes, GET /api/quizzes/{quiz_id}, GET /api/quizzes/my-quizzes")
            print("3. Quiz Attempt Endpoints: POST /api/quiz-attempts, GET /api/quiz-attempts, GET /api/quiz-attempts/{attempt_id}")
            print("4. Quiz Results/Analytics: Check quiz analytics endpoints and data structure")
            print("5. Complete Quiz Workflow: creation → student attempts → results/analytics")
            print()
            
            # Execute comprehensive quiz testing
            self.test_quiz_creation_endpoint()
            self.test_quiz_retrieval_endpoints()
            self.test_quiz_attempt_endpoints()
            self.test_quiz_results_analytics()
            self.test_complete_quiz_workflow()
        
        return self.generate_summary()

if __name__ == "__main__":
    tester = QuizTester()
    results = tester.run_quiz_tests()