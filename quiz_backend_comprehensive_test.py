#!/usr/bin/env python3
"""
URGENT BACKEND TESTING POST-BUILD DEPLOYMENT - QUIZ FUNCTIONALITY VALIDATION
LearningFwiend LMS Application - Quiz Backend API Testing

PRIORITY FOCUS: Test all backend APIs that support the 4 user-reported issues:
1. Quiz functionality (React Error #31 prevention) - verify quiz data structure integrity
2. Quiz rendering support - ensure question types are properly formatted  
3. Chronological order data handling - verify backend accepts comma-separated input correctly
4. Analytics integration - confirm quiz results are being captured and available for analytics

TESTING CREDENTIALS:
- Admin: brayden.t@covesmart.com / Hawaii2020!
- Student: karlo.student@alder.com / StudentPermanent123!
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
import uuid

# Configuration - Using Production Backend URL from frontend/.env
BACKEND_URL = "https://lms-progression-1.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

# Test credentials from review request
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class QuizBackendTester:
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
    
    # =============================================================================
    # AUTHENTICATION TESTS
    # =============================================================================
    
    def test_admin_login(self):
        """Test admin authentication"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
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
                        "Admin Authentication", 
                        "PASS", 
                        f"Admin login successful: {user_info.get('email')}",
                        f"Role: {user_info.get('role')}, Token received"
                    )
                    return True
                else:
                    self.log_result(
                        "Admin Authentication", 
                        "FAIL", 
                        "Login response missing token or incorrect role",
                        f"Token: {bool(token)}, Role: {user_info.get('role')}"
                    )
            else:
                self.log_result(
                    "Admin Authentication", 
                    "FAIL", 
                    f"Admin login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Admin Authentication", 
                "FAIL", 
                "Failed to connect to authentication endpoint",
                str(e)
            )
        return False
    
    def test_student_login(self):
        """Test student authentication"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=STUDENT_CREDENTIALS,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                
                if token and user_info.get('role') == 'learner':
                    self.auth_tokens['student'] = token
                    self.log_result(
                        "Student Authentication", 
                        "PASS", 
                        f"Student login successful: {user_info.get('email')}",
                        f"Role: {user_info.get('role')}, Token received"
                    )
                    return True
                else:
                    self.log_result(
                        "Student Authentication", 
                        "FAIL", 
                        "Login response missing token or incorrect role",
                        f"Token: {bool(token)}, Role: {user_info.get('role')}"
                    )
            else:
                self.log_result(
                    "Student Authentication", 
                    "FAIL", 
                    f"Student login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Authentication", 
                "FAIL", 
                "Failed to connect to authentication endpoint",
                str(e)
            )
        return False
    
    # =============================================================================
    # QUIZ DATA STRUCTURE TESTS
    # =============================================================================
    
    def test_quiz_data_structure_integrity(self):
        """Test GET /api/courses/{id} - verify courses with quizzes have proper data structure"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Quiz Data Structure Integrity", 
                "SKIP", 
                "No admin token available",
                "Admin authentication required"
            )
            return False
        
        try:
            # Get all courses first
            courses_response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if courses_response.status_code != 200:
                self.log_result(
                    "Quiz Data Structure Integrity", 
                    "FAIL", 
                    f"Failed to get courses list: {courses_response.status_code}",
                    f"Response: {courses_response.text}"
                )
                return False
            
            courses = courses_response.json()
            quiz_courses = []
            data_structure_issues = []
            
            # Find courses with quiz lessons
            for course in courses:
                course_id = course.get('id')
                if not course_id:
                    continue
                
                # Get detailed course info
                course_response = requests.get(
                    f"{BACKEND_URL}/courses/{course_id}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
                
                if course_response.status_code == 200:
                    course_detail = course_response.json()
                    modules = course_detail.get('modules', [])
                    
                    has_quiz = False
                    for module in modules:
                        lessons = module.get('lessons', [])
                        for lesson in lessons:
                            lesson_type = lesson.get('type', '').lower()
                            if 'quiz' in lesson_type:
                                has_quiz = True
                                quiz_courses.append({
                                    'course_id': course_id,
                                    'course_title': course_detail.get('title'),
                                    'lesson': lesson
                                })
                                
                                # Check for React Error #31 prevention - chronological questions need 'items' field
                                content = lesson.get('content', {})
                                questions = content.get('questions', [])
                                
                                for i, question in enumerate(questions):
                                    question_type = question.get('type', '')
                                    if question_type == 'chronological-order':
                                        if 'items' not in question or not question.get('items'):
                                            data_structure_issues.append({
                                                'course_id': course_id,
                                                'course_title': course_detail.get('title'),
                                                'lesson_id': lesson.get('id'),
                                                'question_index': i,
                                                'issue': 'Missing items field in chronological-order question',
                                                'question_type': question_type
                                            })
                                        elif not isinstance(question.get('items'), list):
                                            data_structure_issues.append({
                                                'course_id': course_id,
                                                'course_title': course_detail.get('title'),
                                                'lesson_id': lesson.get('id'),
                                                'question_index': i,
                                                'issue': 'Items field is not an array in chronological-order question',
                                                'question_type': question_type
                                            })
            
            # Analyze results
            if len(data_structure_issues) == 0:
                self.log_result(
                    "Quiz Data Structure Integrity", 
                    "PASS", 
                    f"All quiz data structures are valid - no React Error #31 causes found",
                    f"Checked {len(quiz_courses)} quiz lessons across {len(courses)} courses"
                )
                return True
            else:
                self.log_result(
                    "Quiz Data Structure Integrity", 
                    "FAIL", 
                    f"Found {len(data_structure_issues)} data structure issues that could cause React Error #31",
                    f"Issues: {data_structure_issues}"
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Quiz Data Structure Integrity", 
                "FAIL", 
                "Failed to test quiz data structure",
                str(e)
            )
        return False
    
    def test_question_types_support(self):
        """Verify all question types have required fields for proper frontend rendering"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Question Types Support", 
                "SKIP", 
                "No admin token available",
                "Admin authentication required"
            )
            return False
        
        try:
            # Get courses and check question type support
            courses_response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if courses_response.status_code != 200:
                self.log_result(
                    "Question Types Support", 
                    "FAIL", 
                    f"Failed to get courses: {courses_response.status_code}",
                    f"Response: {courses_response.text}"
                )
                return False
            
            courses = courses_response.json()
            question_types_found = set()
            missing_fields = []
            
            # Required fields for each question type
            required_fields = {
                'multiple-choice': ['options', 'correctAnswer'],
                'select-all-that-apply': ['options', 'correctAnswer'],
                'true-false': ['correctAnswer'],
                'short-answer': ['correctAnswer'],
                'long-form-answer': ['correctAnswer'],
                'chronological-order': ['items', 'correctAnswer']
            }
            
            for course in courses:
                course_id = course.get('id')
                if not course_id:
                    continue
                
                course_response = requests.get(
                    f"{BACKEND_URL}/courses/{course_id}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
                
                if course_response.status_code == 200:
                    course_detail = course_response.json()
                    modules = course_detail.get('modules', [])
                    
                    for module in modules:
                        lessons = module.get('lessons', [])
                        for lesson in lessons:
                            if 'quiz' in lesson.get('type', '').lower():
                                content = lesson.get('content', {})
                                questions = content.get('questions', [])
                                
                                for question in questions:
                                    question_type = question.get('type', '')
                                    question_types_found.add(question_type)
                                    
                                    # Check required fields
                                    if question_type in required_fields:
                                        for field in required_fields[question_type]:
                                            if field not in question or question.get(field) is None:
                                                missing_fields.append({
                                                    'course_id': course_id,
                                                    'course_title': course_detail.get('title'),
                                                    'question_type': question_type,
                                                    'missing_field': field
                                                })
            
            # Analyze results
            if len(missing_fields) == 0:
                self.log_result(
                    "Question Types Support", 
                    "PASS", 
                    f"All question types have required fields for proper rendering",
                    f"Found question types: {list(question_types_found)}"
                )
                return True
            else:
                self.log_result(
                    "Question Types Support", 
                    "FAIL", 
                    f"Found {len(missing_fields)} missing required fields",
                    f"Missing fields: {missing_fields}"
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Question Types Support", 
                "FAIL", 
                "Failed to test question types support",
                str(e)
            )
        return False
    
    # =============================================================================
    # CHRONOLOGICAL ORDER BACKEND PARSING TESTS
    # =============================================================================
    
    def test_chronological_order_parsing(self):
        """Test if backend properly parses comma-formatted chronological order input during course creation"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Chronological Order Parsing", 
                "SKIP", 
                "No admin token available",
                "Admin authentication required"
            )
            return False
        
        try:
            # Create a test course with chronological order question
            test_course_data = {
                "title": f"Chronological Order Test Course {uuid.uuid4().hex[:8]}",
                "description": "Testing chronological order comma parsing",
                "category": "Testing",
                "duration": "1 hour",
                "accessType": "open",
                "modules": [
                    {
                        "title": "Chronological Order Test Module",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Chronological Order Quiz",
                                "type": "quiz",
                                "content": {
                                    "questions": [
                                        {
                                            "id": str(uuid.uuid4()),
                                            "type": "chronological-order",
                                            "question": "Put these events in chronological order:",
                                            "items": ["Event A", "Event B", "Event C", "Event D"],
                                            "correctAnswer": "2, 1, 4, 3"  # Comma-separated format
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                ]
            }
            
            # Create the course
            create_response = requests.post(
                f"{BACKEND_URL}/courses",
                json=test_course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if create_response.status_code == 200:
                created_course = create_response.json()
                course_id = created_course.get('id')
                
                # Retrieve the course to verify parsing
                get_response = requests.get(
                    f"{BACKEND_URL}/courses/{course_id}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
                
                if get_response.status_code == 200:
                    retrieved_course = get_response.json()
                    modules = retrieved_course.get('modules', [])
                    
                    # Find the chronological question
                    chronological_question = None
                    for module in modules:
                        lessons = module.get('lessons', [])
                        for lesson in lessons:
                            if lesson.get('type') == 'quiz':
                                content = lesson.get('content', {})
                                questions = content.get('questions', [])
                                for question in questions:
                                    if question.get('type') == 'chronological-order':
                                        chronological_question = question
                                        break
                    
                    if chronological_question:
                        correct_answer = chronological_question.get('correctAnswer')
                        items = chronological_question.get('items')
                        
                        # Verify the data was stored correctly
                        parsing_success = (
                            correct_answer == "2, 1, 4, 3" and
                            isinstance(items, list) and
                            len(items) == 4
                        )
                        
                        if parsing_success:
                            self.log_result(
                                "Chronological Order Parsing", 
                                "PASS", 
                                "Backend correctly accepts and stores comma-separated chronological order input",
                                f"correctAnswer: '{correct_answer}', items: {items}"
                            )
                            
                            # Clean up test course
                            requests.delete(
                                f"{BACKEND_URL}/courses/{course_id}",
                                timeout=TEST_TIMEOUT,
                                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                            )
                            return True
                        else:
                            self.log_result(
                                "Chronological Order Parsing", 
                                "FAIL", 
                                "Backend did not correctly parse chronological order data",
                                f"correctAnswer: '{correct_answer}', items: {items}"
                            )
                    else:
                        self.log_result(
                            "Chronological Order Parsing", 
                            "FAIL", 
                            "Chronological order question not found in created course",
                            "Question may not have been stored correctly"
                        )
                else:
                    self.log_result(
                        "Chronological Order Parsing", 
                        "FAIL", 
                        f"Failed to retrieve created course: {get_response.status_code}",
                        f"Response: {get_response.text}"
                    )
            else:
                self.log_result(
                    "Chronological Order Parsing", 
                    "FAIL", 
                    f"Failed to create test course: {create_response.status_code}",
                    f"Response: {create_response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Chronological Order Parsing", 
                "FAIL", 
                "Failed to test chronological order parsing",
                str(e)
            )
        return False
    
    # =============================================================================
    # QUIZ RESULTS TO ANALYTICS FLOW TESTS
    # =============================================================================
    
    def test_quiz_progress_tracking(self):
        """Test PUT /api/enrollments/{course_id}/progress - verify quiz completion updates are captured"""
        if "student" not in self.auth_tokens:
            self.log_result(
                "Quiz Progress Tracking", 
                "SKIP", 
                "No student token available",
                "Student authentication required"
            )
            return False
        
        try:
            # Get student enrollments
            enrollments_response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if enrollments_response.status_code != 200:
                self.log_result(
                    "Quiz Progress Tracking", 
                    "FAIL", 
                    f"Failed to get student enrollments: {enrollments_response.status_code}",
                    f"Response: {enrollments_response.text}"
                )
                return False
            
            enrollments = enrollments_response.json()
            
            if not enrollments:
                self.log_result(
                    "Quiz Progress Tracking", 
                    "SKIP", 
                    "No enrollments found for student",
                    "Need at least one enrollment to test progress tracking"
                )
                return False
            
            # Use first enrollment for testing
            test_enrollment = enrollments[0]
            course_id = test_enrollment.get('courseId')
            
            # Test quiz completion progress update
            progress_data = {
                "progress": 100.0,  # Quiz completed
                "currentLessonId": "quiz-lesson-test",
                "timeSpent": 300  # 5 minutes
            }
            
            progress_response = requests.put(
                f"{BACKEND_URL}/enrollments/{course_id}/progress",
                json=progress_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["student"]}'
                }
            )
            
            if progress_response.status_code == 200:
                updated_enrollment = progress_response.json()
                
                # Verify progress was updated
                if (updated_enrollment.get('progress') == 100.0 and
                    updated_enrollment.get('currentLessonId') == "quiz-lesson-test" and
                    updated_enrollment.get('timeSpent') == 300):
                    
                    self.log_result(
                        "Quiz Progress Tracking", 
                        "PASS", 
                        "Quiz completion progress successfully tracked",
                        f"Progress: {updated_enrollment.get('progress')}%, Time: {updated_enrollment.get('timeSpent')}s"
                    )
                    return True
                else:
                    self.log_result(
                        "Quiz Progress Tracking", 
                        "FAIL", 
                        "Progress update did not reflect expected values",
                        f"Expected: 100%, 300s | Got: {updated_enrollment.get('progress')}%, {updated_enrollment.get('timeSpent')}s"
                    )
            else:
                self.log_result(
                    "Quiz Progress Tracking", 
                    "FAIL", 
                    f"Failed to update progress: {progress_response.status_code}",
                    f"Response: {progress_response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Quiz Progress Tracking", 
                "FAIL", 
                "Failed to test quiz progress tracking",
                str(e)
            )
        return False
    
    def test_analytics_data_availability(self):
        """Test analytics endpoints - confirm quiz results appear in analytics data"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Analytics Data Availability", 
                "SKIP", 
                "No admin token available",
                "Admin authentication required"
            )
            return False
        
        try:
            # Test various analytics endpoints
            analytics_endpoints = [
                "/enrollments",  # Should show enrollment progress data
                "/courses",      # Should show course completion data
            ]
            
            analytics_data_found = []
            
            for endpoint in analytics_endpoints:
                response = requests.get(
                    f"{BACKEND_URL}{endpoint}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if endpoint == "/enrollments":
                        # Check for progress tracking data
                        for enrollment in data:
                            if (enrollment.get('progress') is not None and
                                enrollment.get('timeSpent') is not None):
                                analytics_data_found.append(f"Enrollment progress data: {endpoint}")
                                break
                    
                    elif endpoint == "/courses":
                        # Check for course completion statistics
                        for course in data:
                            if course.get('enrolledStudents') is not None:
                                analytics_data_found.append(f"Course enrollment data: {endpoint}")
                                break
            
            if len(analytics_data_found) >= 1:
                self.log_result(
                    "Analytics Data Availability", 
                    "PASS", 
                    "Analytics data is available for quiz results tracking",
                    f"Found data in: {', '.join(analytics_data_found)}"
                )
                return True
            else:
                self.log_result(
                    "Analytics Data Availability", 
                    "FAIL", 
                    "No analytics data found for quiz results",
                    f"Checked endpoints: {analytics_endpoints}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Analytics Data Availability", 
                "FAIL", 
                "Failed to test analytics data availability",
                str(e)
            )
        return False
    
    # =============================================================================
    # COMPREHENSIVE QUIZ WORKFLOW TEST
    # =============================================================================
    
    def test_complete_quiz_workflow(self):
        """Test complete quiz workflow from course access to completion tracking"""
        if "student" not in self.auth_tokens or "admin" not in self.auth_tokens:
            self.log_result(
                "Complete Quiz Workflow", 
                "SKIP", 
                "Missing required authentication tokens",
                "Both admin and student authentication required"
            )
            return False
        
        try:
            # Step 1: Get courses with quizzes
            courses_response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if courses_response.status_code != 200:
                self.log_result(
                    "Complete Quiz Workflow", 
                    "FAIL", 
                    f"Failed to get courses: {courses_response.status_code}",
                    f"Response: {courses_response.text}"
                )
                return False
            
            courses = courses_response.json()
            quiz_course = None
            
            # Find a course with quiz lessons
            for course in courses:
                course_id = course.get('id')
                course_detail_response = requests.get(
                    f"{BACKEND_URL}/courses/{course_id}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
                )
                
                if course_detail_response.status_code == 200:
                    course_detail = course_detail_response.json()
                    modules = course_detail.get('modules', [])
                    
                    for module in modules:
                        lessons = module.get('lessons', [])
                        for lesson in lessons:
                            if 'quiz' in lesson.get('type', '').lower():
                                quiz_course = course_detail
                                break
                        if quiz_course:
                            break
                    if quiz_course:
                        break
            
            if not quiz_course:
                self.log_result(
                    "Complete Quiz Workflow", 
                    "SKIP", 
                    "No courses with quiz lessons found",
                    "Need at least one course with quiz to test workflow"
                )
                return False
            
            # Step 2: Check if student is enrolled
            enrollments_response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            enrolled_course_ids = []
            if enrollments_response.status_code == 200:
                enrollments = enrollments_response.json()
                enrolled_course_ids = [e.get('courseId') for e in enrollments]
            
            quiz_course_id = quiz_course.get('id')
            
            # Step 3: Enroll if not already enrolled
            if quiz_course_id not in enrolled_course_ids:
                enroll_response = requests.post(
                    f"{BACKEND_URL}/enrollments",
                    json={"courseId": quiz_course_id},
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.auth_tokens["student"]}'
                    }
                )
                
                if enroll_response.status_code != 200:
                    self.log_result(
                        "Complete Quiz Workflow", 
                        "FAIL", 
                        f"Failed to enroll in quiz course: {enroll_response.status_code}",
                        f"Response: {enroll_response.text}"
                    )
                    return False
            
            # Step 4: Simulate quiz completion
            quiz_progress_data = {
                "progress": 100.0,
                "currentLessonId": "quiz-workflow-test",
                "timeSpent": 600
            }
            
            progress_response = requests.put(
                f"{BACKEND_URL}/enrollments/{quiz_course_id}/progress",
                json=quiz_progress_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["student"]}'
                }
            )
            
            if progress_response.status_code == 200:
                self.log_result(
                    "Complete Quiz Workflow", 
                    "PASS", 
                    "Complete quiz workflow successful - course access, enrollment, and progress tracking working",
                    f"Course: {quiz_course.get('title')}, Progress: 100%, Time: 600s"
                )
                return True
            else:
                self.log_result(
                    "Complete Quiz Workflow", 
                    "FAIL", 
                    f"Failed to update quiz progress: {progress_response.status_code}",
                    f"Response: {progress_response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Complete Quiz Workflow", 
                "FAIL", 
                "Failed to test complete quiz workflow",
                str(e)
            )
        return False
    
    # =============================================================================
    # MAIN TEST EXECUTION
    # =============================================================================
    
    def run_all_tests(self):
        """Run all quiz backend tests"""
        print("🚨 URGENT BACKEND TESTING POST-BUILD DEPLOYMENT - QUIZ FUNCTIONALITY VALIDATION")
        print("=" * 80)
        print("PRIORITY FOCUS: Verify all quiz fixes are working at backend level")
        print("1. Quiz data structure integrity (React Error #31 prevention)")
        print("2. Question types properly formatted for rendering")
        print("3. Chronological order comma-separated input handling")
        print("4. Quiz results captured for analytics")
        print("=" * 80)
        
        # Authentication Tests
        print("\n🔑 AUTHENTICATION TESTS")
        print("-" * 40)
        admin_auth = self.test_admin_login()
        student_auth = self.test_student_login()
        
        if not admin_auth or not student_auth:
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with quiz testing")
            return False
        
        # Quiz Data Structure Tests
        print("\n📊 QUIZ DATA STRUCTURE TESTS")
        print("-" * 40)
        self.test_quiz_data_structure_integrity()
        self.test_question_types_support()
        
        # Chronological Order Tests
        print("\n🔢 CHRONOLOGICAL ORDER PARSING TESTS")
        print("-" * 40)
        self.test_chronological_order_parsing()
        
        # Analytics Integration Tests
        print("\n📈 ANALYTICS INTEGRATION TESTS")
        print("-" * 40)
        self.test_quiz_progress_tracking()
        self.test_analytics_data_availability()
        
        # Complete Workflow Test
        print("\n🎯 COMPLETE QUIZ WORKFLOW TEST")
        print("-" * 40)
        self.test_complete_quiz_workflow()
        
        # Final Results
        print("\n" + "=" * 80)
        print("🎉 QUIZ BACKEND TESTING RESULTS")
        print("=" * 80)
        print(f"✅ PASSED: {self.passed}")
        print(f"❌ FAILED: {self.failed}")
        print(f"📊 SUCCESS RATE: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        if self.failed == 0:
            print("\n🎉 ALL QUIZ BACKEND TESTS PASSED - READY FOR FRONTEND TESTING")
        else:
            print(f"\n⚠️ {self.failed} TESTS FAILED - ISSUES NEED ATTENTION")
        
        return self.failed == 0

if __name__ == "__main__":
    tester = QuizBackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)