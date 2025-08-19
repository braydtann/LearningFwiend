#!/usr/bin/env python3
"""
Quiz Functionality Tests for LearningFwiend LMS Application
Tests quiz creation, publishing, student attempts, and analytics data structure
"""

import requests
import json
import os
import sys
from datetime import datetime
import time

# Configuration - Using Production Backend URL from frontend/.env
BACKEND_URL = "https://edusys-migration.preview.emergentagent.com/api"
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
                else:
                    self.log_result(
                        "Admin Login Test", 
                        "FAIL", 
                        "Login successful but missing token or wrong role",
                        f"Token: {bool(token)}, Role: {user_info.get('role')}"
                    )
            else:
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
                else:
                    self.log_result(
                        "Instructor Login Test", 
                        "FAIL", 
                        "Login successful but missing token or wrong role",
                        f"Token: {bool(token)}, Role: {user_info.get('role')}"
                    )
            else:
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
                "username_or_email": "student",
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
                else:
                    self.log_result(
                        "Student Login Test", 
                        "FAIL", 
                        "Login successful but missing token or wrong role",
                        f"Token: {bool(token)}, Role: {user_info.get('role')}"
                    )
            else:
                # Try to create a student user if login fails
                if "admin" in self.auth_tokens:
                    self.log_result(
                        "Student Login Test", 
                        "INFO", 
                        "Student login failed, attempting to create test student",
                        f"Login failed with status {response.status_code}"
                    )
                    
                    # Create a test student
                    student_data = {
                        "email": "quiz.test.student@learningfwiend.com",
                        "username": "quiz.test.student",
                        "full_name": "Quiz Test Student",
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
                        # Try login again with the created student
                        login_data_new = {
                            "username_or_email": "quiz.test.student@learningfwiend.com",
                            "password": "Student123!"
                        }
                        
                        login_response_new = requests.post(
                            f"{BACKEND_URL}/auth/login",
                            json=login_data_new,
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
    
    def test_quiz_creation_with_course_association(self):
        """Test Quiz Creation with Course Association"""
        if "instructor" not in self.auth_tokens:
            self.log_result(
                "Quiz Creation with Course Association", 
                "SKIP", 
                "No instructor token available for quiz creation test",
                "Instructor authentication required"
            )
            return False
        
        try:
            # First, create a course to associate with the quiz
            course_data = {
                "title": "Quiz Integration Test Course",
                "description": "Course for testing quiz integration functionality",
                "category": "Testing",
                "duration": "2 weeks",
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
                    "Quiz Creation with Course Association", 
                    "FAIL", 
                    "Failed to create test course for quiz association",
                    f"Course creation failed with status {course_response.status_code}"
                )
                return False
            
            created_course = course_response.json()
            course_id = created_course.get('id')
            
            # Now create a quiz associated with this course
            quiz_data = {
                "title": "Course Integration Quiz",
                "description": "Testing quiz creation with course association",
                "courseId": course_id,
                "questions": [
                    {
                        "type": "multiple_choice",
                        "question": "What is the purpose of this quiz?",
                        "options": ["Testing", "Learning", "Assessment", "All of the above"],
                        "correctAnswer": "3",
                        "points": 10,
                        "explanation": "This quiz is for testing integration functionality"
                    },
                    {
                        "type": "true_false",
                        "question": "This quiz is associated with a course",
                        "correctAnswer": "true",
                        "points": 5
                    }
                ],
                "timeLimit": 30,
                "attempts": 3,
                "passingScore": 70.0,
                "shuffleQuestions": False,
                "showResults": True,
                "isPublished": False  # Start as draft
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
            
            if quiz_response.status_code == 200:
                created_quiz = quiz_response.json()
                quiz_id = created_quiz.get('id')
                associated_course_id = created_quiz.get('courseId')
                course_name = created_quiz.get('courseName')
                
                if associated_course_id == course_id and course_name:
                    self.log_result(
                        "Quiz Creation with Course Association", 
                        "PASS", 
                        f"Successfully created quiz associated with course",
                        f"Quiz ID: {quiz_id}, Course ID: {course_id}, Course Name: {course_name}"
                    )
                    return {"quiz": created_quiz, "course": created_course}
                else:
                    self.log_result(
                        "Quiz Creation with Course Association", 
                        "FAIL", 
                        "Quiz created but course association failed",
                        f"Expected course ID: {course_id}, Got: {associated_course_id}"
                    )
            else:
                self.log_result(
                    "Quiz Creation with Course Association", 
                    "FAIL", 
                    f"Failed to create quiz with course association, status: {quiz_response.status_code}",
                    f"Response: {quiz_response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Quiz Creation with Course Association", 
                "FAIL", 
                "Failed to test quiz creation with course association",
                str(e)
            )
        return False
    
    def test_quiz_publishing(self):
        """Test Quiz Publishing"""
        # First create a quiz
        quiz_data = self.test_quiz_creation_with_course_association()
        if not quiz_data:
            self.log_result(
                "Quiz Publishing", 
                "SKIP", 
                "Could not create test quiz for publishing test",
                "Quiz creation required first"
            )
            return False
        
        quiz_id = quiz_data["quiz"]["id"]
        
        try:
            # Update quiz to publish it
            publish_data = {
                "isPublished": True
            }
            
            response = requests.put(
                f"{BACKEND_URL}/quizzes/{quiz_id}",
                json=publish_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if response.status_code == 200:
                updated_quiz = response.json()
                is_published = updated_quiz.get('isPublished')
                
                if is_published:
                    self.log_result(
                        "Quiz Publishing", 
                        "PASS", 
                        f"Successfully published quiz",
                        f"Quiz ID: {quiz_id}, Published: {is_published}"
                    )
                    return {"quiz": updated_quiz, "course": quiz_data["course"]}
                else:
                    self.log_result(
                        "Quiz Publishing", 
                        "FAIL", 
                        "Quiz update successful but not published",
                        f"isPublished: {is_published}"
                    )
            else:
                self.log_result(
                    "Quiz Publishing", 
                    "FAIL", 
                    f"Failed to publish quiz, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Quiz Publishing", 
                "FAIL", 
                "Failed to test quiz publishing",
                str(e)
            )
        return False
    
    def test_student_quiz_attempts(self):
        """Test Student Quiz Attempts"""
        # First ensure we have a published quiz
        quiz_data = self.test_quiz_publishing()
        if not quiz_data:
            self.log_result(
                "Student Quiz Attempts", 
                "SKIP", 
                "Could not create published quiz for student attempt test",
                "Published quiz required first"
            )
            return False
        
        if "learner" not in self.auth_tokens:
            self.log_result(
                "Student Quiz Attempts", 
                "SKIP", 
                "No student token available for quiz attempt test",
                "Student authentication required"
            )
            return False
        
        quiz_id = quiz_data["quiz"]["id"]
        
        try:
            # Student submits quiz attempt
            attempt_data = {
                "quizId": quiz_id,
                "answers": ["3", "true"]  # Correct answers for the test quiz
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
                attempt_result = response.json()
                attempt_id = attempt_result.get('id')
                score = attempt_result.get('score')
                is_passed = attempt_result.get('isPassed')
                student_name = attempt_result.get('studentName')
                
                self.log_result(
                    "Student Quiz Attempts", 
                    "PASS", 
                    f"Successfully submitted quiz attempt",
                    f"Attempt ID: {attempt_id}, Score: {score}%, Passed: {is_passed}, Student: {student_name}"
                )
                return {"attempt": attempt_result, "quiz": quiz_data["quiz"], "course": quiz_data["course"]}
            else:
                self.log_result(
                    "Student Quiz Attempts", 
                    "FAIL", 
                    f"Failed to submit quiz attempt, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Quiz Attempts", 
                "FAIL", 
                "Failed to test student quiz attempts",
                str(e)
            )
        return False
    
    def test_quiz_analytics_data_structure(self):
        """Test Quiz Analytics Data Structure"""
        # First ensure we have quiz attempts
        attempt_data = self.test_student_quiz_attempts()
        if not attempt_data:
            self.log_result(
                "Quiz Analytics Data Structure", 
                "SKIP", 
                "Could not create quiz attempt for analytics test",
                "Quiz attempt required first"
            )
            return False
        
        if "instructor" not in self.auth_tokens:
            self.log_result(
                "Quiz Analytics Data Structure", 
                "SKIP", 
                "No instructor token available for analytics test",
                "Instructor authentication required"
            )
            return False
        
        try:
            # Get quiz attempts for analytics
            response = requests.get(
                f"{BACKEND_URL}/quiz-attempts",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
            )
            
            if response.status_code == 200:
                attempts = response.json()
                
                if len(attempts) > 0:
                    sample_attempt = attempts[0]
                    required_fields = ['id', 'userId', 'studentName', 'score', 'isPassed', 'status', 'quizId', 'quizTitle']
                    
                    missing_fields = []
                    present_fields = []
                    
                    for field in required_fields:
                        if field in sample_attempt:
                            present_fields.append(field)
                        else:
                            missing_fields.append(field)
                    
                    if len(missing_fields) == 0:
                        self.log_result(
                            "Quiz Analytics Data Structure", 
                            "PASS", 
                            f"Quiz attempts contain all required fields for frontend analytics",
                            f"Fields verified: {', '.join(present_fields)}, Total attempts: {len(attempts)}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Quiz Analytics Data Structure", 
                            "FAIL", 
                            f"Quiz attempts missing required fields for analytics",
                            f"Missing: {', '.join(missing_fields)}, Present: {', '.join(present_fields)}"
                        )
                else:
                    self.log_result(
                        "Quiz Analytics Data Structure", 
                        "FAIL", 
                        "No quiz attempts found for analytics testing",
                        "At least one quiz attempt required"
                    )
            else:
                self.log_result(
                    "Quiz Analytics Data Structure", 
                    "FAIL", 
                    f"Failed to retrieve quiz attempts for analytics, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Quiz Analytics Data Structure", 
                "FAIL", 
                "Failed to test quiz analytics data structure",
                str(e)
            )
        return False
    
    def test_course_quiz_relationship(self):
        """Test Course-Quiz Relationship"""
        # First ensure we have quiz attempts with course association
        attempt_data = self.test_student_quiz_attempts()
        if not attempt_data:
            self.log_result(
                "Course-Quiz Relationship", 
                "SKIP", 
                "Could not create quiz attempt with course association",
                "Quiz attempt with course required first"
            )
            return False
        
        course_id = attempt_data["course"]["id"]
        
        if "instructor" not in self.auth_tokens:
            self.log_result(
                "Course-Quiz Relationship", 
                "SKIP", 
                "No instructor token available for course-quiz relationship test",
                "Instructor authentication required"
            )
            return False
        
        try:
            # Test filtering quizzes by course
            response = requests.get(
                f"{BACKEND_URL}/quizzes?course_id={course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
            )
            
            if response.status_code == 200:
                course_quizzes = response.json()
                
                # Verify all returned quizzes are associated with the course
                valid_associations = 0
                for quiz in course_quizzes:
                    if quiz.get('courseId') == course_id:
                        valid_associations += 1
                
                if len(course_quizzes) > 0 and valid_associations == len(course_quizzes):
                    self.log_result(
                        "Course-Quiz Relationship", 
                        "PASS", 
                        f"Successfully filtered quizzes by course",
                        f"Found {len(course_quizzes)} quizzes for course {course_id}, all properly associated"
                    )
                    return True
                else:
                    self.log_result(
                        "Course-Quiz Relationship", 
                        "FAIL", 
                        f"Course-quiz filtering returned invalid associations",
                        f"Total quizzes: {len(course_quizzes)}, Valid associations: {valid_associations}"
                    )
            else:
                self.log_result(
                    "Course-Quiz Relationship", 
                    "FAIL", 
                    f"Failed to filter quizzes by course, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course-Quiz Relationship", 
                "FAIL", 
                "Failed to test course-quiz relationship",
                str(e)
            )
        return False
    
    def test_student_performance_aggregation(self):
        """Test Student Performance Aggregation"""
        # First ensure we have quiz attempts
        attempt_data = self.test_student_quiz_attempts()
        if not attempt_data:
            self.log_result(
                "Student Performance Aggregation", 
                "SKIP", 
                "Could not create quiz attempt for performance aggregation test",
                "Quiz attempt required first"
            )
            return False
        
        if "instructor" not in self.auth_tokens:
            self.log_result(
                "Student Performance Aggregation", 
                "SKIP", 
                "No instructor token available for performance aggregation test",
                "Instructor authentication required"
            )
            return False
        
        try:
            # Get all quiz attempts for performance analysis
            response = requests.get(
                f"{BACKEND_URL}/quiz-attempts",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
            )
            
            if response.status_code == 200:
                attempts = response.json()
                
                if len(attempts) > 0:
                    # Verify all required fields for performance aggregation
                    performance_fields = ['userId', 'studentName', 'score', 'isPassed', 'status', 'quizId', 'quizTitle', 'completedAt']
                    
                    valid_attempts = 0
                    field_coverage = {}
                    
                    for attempt in attempts:
                        attempt_valid = True
                        for field in performance_fields:
                            if field in attempt:
                                field_coverage[field] = field_coverage.get(field, 0) + 1
                            else:
                                attempt_valid = False
                        
                        if attempt_valid:
                            valid_attempts += 1
                    
                    coverage_percentage = (valid_attempts / len(attempts)) * 100
                    
                    if coverage_percentage >= 100:
                        self.log_result(
                            "Student Performance Aggregation", 
                            "PASS", 
                            f"All quiz attempts contain required fields for performance aggregation",
                            f"Valid attempts: {valid_attempts}/{len(attempts)} ({coverage_percentage:.1f}%), Fields: {', '.join(performance_fields)}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Student Performance Aggregation", 
                            "FAIL", 
                            f"Some quiz attempts missing required fields for performance aggregation",
                            f"Valid attempts: {valid_attempts}/{len(attempts)} ({coverage_percentage:.1f}%), Field coverage: {field_coverage}"
                        )
                else:
                    self.log_result(
                        "Student Performance Aggregation", 
                        "FAIL", 
                        "No quiz attempts found for performance aggregation testing",
                        "At least one quiz attempt required"
                    )
            else:
                self.log_result(
                    "Student Performance Aggregation", 
                    "FAIL", 
                    f"Failed to retrieve quiz attempts for performance aggregation, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Performance Aggregation", 
                "FAIL", 
                "Failed to test student performance aggregation",
                str(e)
            )
        return False

    def run_quiz_tests(self):
        """Run all quiz functionality tests"""
        print("🧩 Starting Quiz Functionality Integration Tests")
        print("=" * 80)
        
        # Authentication Tests - Required for Quiz Testing
        print("\n🔐 Authentication Tests")
        print("-" * 50)
        self.test_admin_login()
        self.test_instructor_login()
        self.test_student_login()
        
        # Quiz Functionality Integration Tests - MAIN FOCUS
        print("\n🧩 Quiz Functionality Integration Tests")
        print("-" * 50)
        self.test_quiz_creation_with_course_association()
        self.test_quiz_publishing()
        self.test_student_quiz_attempts()
        self.test_quiz_analytics_data_structure()
        self.test_course_quiz_relationship()
        self.test_student_performance_aggregation()
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 QUIZ TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        if self.failed > 0:
            print(f"\n❌ {self.failed} tests failed. Check the details above.")
            return False
        else:
            print(f"\n🎉 All {self.passed} tests passed successfully!")
            return True

if __name__ == "__main__":
    tester = QuizTester()
    success = tester.run_quiz_tests()
    sys.exit(0 if success else 1)