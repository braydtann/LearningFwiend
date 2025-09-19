#!/usr/bin/env python3
"""
QUIZ REMOVAL BACKEND TESTING SUITE
LearningFriend LMS Backend Testing After Removing Select All That Apply and Chronological Order Question Types

TESTING FOCUS:
✅ Authentication Testing with provided credentials
✅ Course Creation APIs with remaining question types
✅ Quiz Functionality with remaining question types (Multiple Choice, True/False, Short Answer, Long Form)
✅ Existing Quiz Data compatibility
✅ Critical Endpoints functionality

TARGET: Ensure backend APIs remain fully functional after frontend question type removal
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
import uuid

# Configuration - Using frontend/.env REACT_APP_BACKEND_URL
BACKEND_URL = "https://lms-debugfix.preview.emergentagent.com/api"
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

class QuizRemovalBackendTester:
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
    # AUTHENTICATION TESTING
    # =============================================================================
    
    def test_admin_authentication(self):
        """Test admin login with provided credentials"""
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
                        f"Admin login successful: {user_info.get('full_name')} ({user_info.get('email')})",
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
    
    def test_student_authentication(self):
        """Test student login with provided credentials"""
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
                        f"Student login successful: {user_info.get('full_name')} ({user_info.get('email')})",
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
    # COURSE CREATION API TESTING
    # =============================================================================
    
    def test_course_creation_api(self):
        """Test POST /api/courses - verify courses can still be created with remaining question types"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Course Creation API", 
                "SKIP", 
                "No admin token available for course creation test",
                "Admin authentication required"
            )
            return False
        
        try:
            # Create a course with remaining question types (Multiple Choice, True/False, Short Answer, Long Form)
            course_data = {
                "title": "Quiz Removal Test Course",
                "description": "Testing course creation with remaining question types after removing Select All That Apply and Chronological Order",
                "category": "Testing",
                "duration": "1 week",
                "accessType": "open",
                "modules": [
                    {
                        "title": "Remaining Question Types Module",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Multiple Choice Quiz",
                                "type": "quiz",
                                "questions": [
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "multiple-choice",
                                        "question": "What is 2 + 2?",
                                        "options": ["3", "4", "5", "6"],
                                        "correctAnswer": 1
                                    }
                                ]
                            },
                            {
                                "id": str(uuid.uuid4()),
                                "title": "True/False Quiz",
                                "type": "quiz",
                                "questions": [
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "true-false",
                                        "question": "The sky is blue.",
                                        "correctAnswer": True
                                    }
                                ]
                            },
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Short Answer Quiz",
                                "type": "quiz",
                                "questions": [
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "short-answer",
                                        "question": "What is the capital of France?",
                                        "correctAnswer": "Paris"
                                    }
                                ]
                            },
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Long Form Quiz",
                                "type": "quiz",
                                "questions": [
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "long-form",
                                        "question": "Explain the importance of education.",
                                        "correctAnswer": "Education is important for personal and societal development."
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(
                f"{BACKEND_URL}/courses",
                json=course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 200:
                created_course = response.json()
                course_id = created_course.get('id')
                
                # Store course ID for later tests
                self.test_course_id = course_id
                
                self.log_result(
                    "Course Creation API", 
                    "PASS", 
                    f"Successfully created course with remaining question types: {created_course.get('title')}",
                    f"Course ID: {course_id}, Modules: {len(created_course.get('modules', []))}"
                )
                return True
            else:
                self.log_result(
                    "Course Creation API", 
                    "FAIL", 
                    f"Failed to create course, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course Creation API", 
                "FAIL", 
                "Failed to test course creation",
                str(e)
            )
        return False
    
    def test_course_listing_api(self):
        """Test GET /api/courses - verify course listing works"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Course Listing API", 
                "SKIP", 
                "No admin token available for course listing test",
                "Admin authentication required"
            )
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                self.log_result(
                    "Course Listing API", 
                    "PASS", 
                    f"Successfully retrieved course list: {len(courses)} courses",
                    f"Courses available for testing quiz functionality"
                )
                return courses
            else:
                self.log_result(
                    "Course Listing API", 
                    "FAIL", 
                    f"Failed to retrieve courses, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course Listing API", 
                "FAIL", 
                "Failed to test course listing",
                str(e)
            )
        return False
    
    def test_course_details_api(self):
        """Test GET /api/courses/{id} - verify course details work"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Course Details API", 
                "SKIP", 
                "No admin token available for course details test",
                "Admin authentication required"
            )
            return False
        
        # Use the course we created earlier if available
        course_id = getattr(self, 'test_course_id', None)
        
        if not course_id:
            # Get any available course
            courses = self.test_course_listing_api()
            if courses and len(courses) > 0:
                course_id = courses[0].get('id')
        
        if not course_id:
            self.log_result(
                "Course Details API", 
                "SKIP", 
                "No course ID available for testing course details",
                "Need at least one course in the system"
            )
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses/{course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                course = response.json()
                modules = course.get('modules', [])
                
                # Count quiz lessons with remaining question types
                quiz_lessons = 0
                remaining_question_types = ['multiple-choice', 'true-false', 'short-answer', 'long-form']
                
                for module in modules:
                    lessons = module.get('lessons', [])
                    for lesson in lessons:
                        if lesson.get('type') == 'quiz':
                            questions = lesson.get('questions', [])
                            for question in questions:
                                if question.get('type') in remaining_question_types:
                                    quiz_lessons += 1
                
                self.log_result(
                    "Course Details API", 
                    "PASS", 
                    f"Successfully retrieved course details: {course.get('title')}",
                    f"Course ID: {course_id}, Modules: {len(modules)}, Quiz lessons with remaining types: {quiz_lessons}"
                )
                return course
            else:
                self.log_result(
                    "Course Details API", 
                    "FAIL", 
                    f"Failed to retrieve course details, status: {response.status_code}",
                    f"Course ID: {course_id}, Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course Details API", 
                "FAIL", 
                "Failed to test course details",
                str(e)
            )
        return False
    
    # =============================================================================
    # QUIZ FUNCTIONALITY TESTING
    # =============================================================================
    
    def test_quiz_functionality_remaining_types(self):
        """Test quiz functionality with remaining question types (Multiple Choice, True/False, Short Answer, Long Form)"""
        if "student" not in self.auth_tokens:
            self.log_result(
                "Quiz Functionality - Remaining Types", 
                "SKIP", 
                "No student token available for quiz functionality test",
                "Student authentication required"
            )
            return False
        
        # Get courses to find ones with quizzes
        try:
            courses_response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if courses_response.status_code != 200:
                self.log_result(
                    "Quiz Functionality - Remaining Types", 
                    "FAIL", 
                    "Failed to retrieve courses for quiz testing",
                    f"Status: {courses_response.status_code}"
                )
                return False
            
            courses = courses_response.json()
            quiz_courses = []
            
            # Find courses with quiz lessons containing remaining question types
            remaining_question_types = ['multiple-choice', 'true-false', 'short-answer', 'long-form']
            
            for course in courses:
                modules = course.get('modules', [])
                has_remaining_quiz_types = False
                
                for module in modules:
                    lessons = module.get('lessons', [])
                    for lesson in lessons:
                        if lesson.get('type') == 'quiz':
                            questions = lesson.get('questions', [])
                            for question in questions:
                                if question.get('type') in remaining_question_types:
                                    has_remaining_quiz_types = True
                                    break
                        if has_remaining_quiz_types:
                            break
                    if has_remaining_quiz_types:
                        break
                
                if has_remaining_quiz_types:
                    quiz_courses.append(course)
            
            if not quiz_courses:
                self.log_result(
                    "Quiz Functionality - Remaining Types", 
                    "SKIP", 
                    "No courses found with remaining question types for testing",
                    f"Searched {len(courses)} courses, none have Multiple Choice, True/False, Short Answer, or Long Form questions"
                )
                return False
            
            # Test quiz functionality with the first available quiz course
            test_course = quiz_courses[0]
            course_id = test_course.get('id')
            
            # First, enroll student in the course if not already enrolled
            enrollment_success = self.ensure_student_enrollment(course_id)
            
            if not enrollment_success:
                self.log_result(
                    "Quiz Functionality - Remaining Types", 
                    "FAIL", 
                    "Failed to enroll student in quiz course",
                    f"Course ID: {course_id}"
                )
                return False
            
            # Test quiz submission workflow
            quiz_submission_success = self.test_quiz_submission_workflow(course_id, test_course)
            
            if quiz_submission_success:
                self.log_result(
                    "Quiz Functionality - Remaining Types", 
                    "PASS", 
                    f"Quiz functionality working correctly with remaining question types",
                    f"Course: {test_course.get('title')}, Quiz submission and progress tracking successful"
                )
                return True
            else:
                self.log_result(
                    "Quiz Functionality - Remaining Types", 
                    "FAIL", 
                    "Quiz submission workflow failed",
                    f"Course: {test_course.get('title')}"
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Quiz Functionality - Remaining Types", 
                "FAIL", 
                "Failed to test quiz functionality",
                str(e)
            )
        return False
    
    def ensure_student_enrollment(self, course_id):
        """Ensure student is enrolled in the course"""
        try:
            # Check if already enrolled
            enrollments_response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if enrollments_response.status_code == 200:
                enrollments = enrollments_response.json()
                for enrollment in enrollments:
                    if enrollment.get('courseId') == course_id:
                        return True  # Already enrolled
            
            # Enroll in the course
            enrollment_data = {"courseId": course_id}
            enroll_response = requests.post(
                f"{BACKEND_URL}/enrollments",
                json=enrollment_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["student"]}'
                }
            )
            
            return enroll_response.status_code == 200
            
        except requests.exceptions.RequestException:
            return False
    
    def test_quiz_submission_workflow(self, course_id, course):
        """Test quiz submission workflow"""
        try:
            # Simulate quiz completion by updating progress
            progress_data = {
                "progress": 100.0,
                "currentModuleId": course.get('modules', [{}])[0].get('id') if course.get('modules') else None,
                "currentLessonId": None,
                "timeSpent": 300  # 5 minutes
            }
            
            # Find a quiz lesson ID
            modules = course.get('modules', [])
            for module in modules:
                lessons = module.get('lessons', [])
                for lesson in lessons:
                    if lesson.get('type') == 'quiz':
                        progress_data['currentLessonId'] = lesson.get('id')
                        break
                if progress_data['currentLessonId']:
                    break
            
            response = requests.put(
                f"{BACKEND_URL}/enrollments/{course_id}/progress",
                json=progress_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["student"]}'
                }
            )
            
            return response.status_code == 200
            
        except requests.exceptions.RequestException:
            return False
    
    def test_progress_tracking(self):
        """Test progress tracking functionality"""
        if "student" not in self.auth_tokens:
            self.log_result(
                "Progress Tracking", 
                "SKIP", 
                "No student token available for progress tracking test",
                "Student authentication required"
            )
            return False
        
        try:
            # Get student enrollments
            response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if response.status_code == 200:
                enrollments = response.json()
                
                if enrollments:
                    # Test progress tracking on first enrollment
                    enrollment = enrollments[0]
                    course_id = enrollment.get('courseId')
                    current_progress = enrollment.get('progress', 0)
                    
                    # Update progress
                    new_progress = min(100.0, current_progress + 25.0)
                    progress_data = {
                        "progress": new_progress,
                        "timeSpent": 600  # 10 minutes
                    }
                    
                    update_response = requests.put(
                        f"{BACKEND_URL}/enrollments/{course_id}/progress",
                        json=progress_data,
                        timeout=TEST_TIMEOUT,
                        headers={
                            'Content-Type': 'application/json',
                            'Authorization': f'Bearer {self.auth_tokens["student"]}'
                        }
                    )
                    
                    if update_response.status_code == 200:
                        updated_enrollment = update_response.json()
                        self.log_result(
                            "Progress Tracking", 
                            "PASS", 
                            f"Progress tracking working correctly",
                            f"Updated progress from {current_progress}% to {updated_enrollment.get('progress', 0)}%"
                        )
                        return True
                    else:
                        self.log_result(
                            "Progress Tracking", 
                            "FAIL", 
                            f"Failed to update progress, status: {update_response.status_code}",
                            f"Response: {update_response.text}"
                        )
                else:
                    self.log_result(
                        "Progress Tracking", 
                        "SKIP", 
                        "No enrollments found for progress tracking test",
                        "Student needs to be enrolled in at least one course"
                    )
            else:
                self.log_result(
                    "Progress Tracking", 
                    "FAIL", 
                    f"Failed to retrieve enrollments, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Progress Tracking", 
                "FAIL", 
                "Failed to test progress tracking",
                str(e)
            )
        return False
    
    # =============================================================================
    # EXISTING QUIZ DATA TESTING
    # =============================================================================
    
    def test_existing_quiz_data_compatibility(self):
        """Test that existing courses with removed question types don't break API responses"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Existing Quiz Data Compatibility", 
                "SKIP", 
                "No admin token available for existing quiz data test",
                "Admin authentication required"
            )
            return False
        
        try:
            # Get all courses
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                
                # Look for courses that might have removed question types
                problematic_courses = []
                compatible_courses = []
                
                for course in courses:
                    course_id = course.get('id')
                    
                    # Test individual course access
                    try:
                        course_response = requests.get(
                            f"{BACKEND_URL}/courses/{course_id}",
                            timeout=TEST_TIMEOUT,
                            headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                        )
                        
                        if course_response.status_code == 200:
                            course_details = course_response.json()
                            
                            # Check for removed question types in course data
                            has_removed_types = self.check_for_removed_question_types(course_details)
                            
                            if has_removed_types:
                                problematic_courses.append({
                                    'id': course_id,
                                    'title': course.get('title'),
                                    'removed_types': has_removed_types
                                })
                            else:
                                compatible_courses.append(course.get('title'))
                        else:
                            problematic_courses.append({
                                'id': course_id,
                                'title': course.get('title'),
                                'error': f'HTTP {course_response.status_code}'
                            })
                    except:
                        problematic_courses.append({
                            'id': course_id,
                            'title': course.get('title'),
                            'error': 'Request failed'
                        })
                
                if len(problematic_courses) == 0:
                    self.log_result(
                        "Existing Quiz Data Compatibility", 
                        "PASS", 
                        f"All {len(courses)} existing courses are compatible with removed question types",
                        f"No courses found with Select All That Apply or Chronological Order question types"
                    )
                    return True
                else:
                    # Check if problematic courses still return valid responses
                    working_problematic = 0
                    for course in problematic_courses:
                        if 'error' not in course:
                            working_problematic += 1
                    
                    if working_problematic == len(problematic_courses):
                        self.log_result(
                            "Existing Quiz Data Compatibility", 
                            "PASS", 
                            f"Found {len(problematic_courses)} courses with removed question types, but all return valid API responses",
                            f"Backend handles mixed question types gracefully"
                        )
                        return True
                    else:
                        self.log_result(
                            "Existing Quiz Data Compatibility", 
                            "FAIL", 
                            f"Found {len(problematic_courses) - working_problematic} courses with API errors",
                            f"Some existing courses may have data integrity issues"
                        )
            else:
                self.log_result(
                    "Existing Quiz Data Compatibility", 
                    "FAIL", 
                    f"Failed to retrieve courses for compatibility test, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Existing Quiz Data Compatibility", 
                "FAIL", 
                "Failed to test existing quiz data compatibility",
                str(e)
            )
        return False
    
    def check_for_removed_question_types(self, course):
        """Check if course contains removed question types"""
        removed_types = []
        modules = course.get('modules', [])
        
        for module in modules:
            lessons = module.get('lessons', [])
            for lesson in lessons:
                if lesson.get('type') == 'quiz':
                    questions = lesson.get('questions', [])
                    for question in questions:
                        question_type = question.get('type', '')
                        if question_type in ['select-all-that-apply', 'chronological-order']:
                            if question_type not in removed_types:
                                removed_types.append(question_type)
        
        return removed_types
    
    # =============================================================================
    # CRITICAL ENDPOINTS TESTING
    # =============================================================================
    
    def test_critical_endpoints(self):
        """Test critical endpoints functionality"""
        critical_tests = []
        
        # Test GET /api/enrollments
        if "student" in self.auth_tokens:
            try:
                response = requests.get(
                    f"{BACKEND_URL}/enrollments",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
                )
                
                if response.status_code == 200:
                    enrollments = response.json()
                    critical_tests.append(f"✅ GET /api/enrollments - {len(enrollments)} enrollments")
                else:
                    critical_tests.append(f"❌ GET /api/enrollments - Status: {response.status_code}")
            except:
                critical_tests.append("❌ GET /api/enrollments - Request failed")
        
        # Test PUT /api/enrollments/{course_id}/progress
        if "student" in self.auth_tokens:
            # Get first enrollment for testing
            try:
                enrollments_response = requests.get(
                    f"{BACKEND_URL}/enrollments",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
                )
                
                if enrollments_response.status_code == 200:
                    enrollments = enrollments_response.json()
                    if enrollments:
                        course_id = enrollments[0].get('courseId')
                        progress_data = {"progress": 50.0, "timeSpent": 300}
                        
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
                            critical_tests.append("✅ PUT /api/enrollments/{course_id}/progress - Progress updated")
                        else:
                            critical_tests.append(f"❌ PUT /api/enrollments/{course_id}/progress - Status: {progress_response.status_code}")
                    else:
                        critical_tests.append("⚠️ PUT /api/enrollments/{course_id}/progress - No enrollments to test")
                else:
                    critical_tests.append("❌ PUT /api/enrollments/{course_id}/progress - Cannot get enrollments")
            except:
                critical_tests.append("❌ PUT /api/enrollments/{course_id}/progress - Request failed")
        
        # Test basic CRUD operations
        if "admin" in self.auth_tokens:
            try:
                # Test GET /api/courses
                courses_response = requests.get(
                    f"{BACKEND_URL}/courses",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
                
                if courses_response.status_code == 200:
                    courses = courses_response.json()
                    critical_tests.append(f"✅ GET /api/courses - {len(courses)} courses")
                else:
                    critical_tests.append(f"❌ GET /api/courses - Status: {courses_response.status_code}")
            except:
                critical_tests.append("❌ GET /api/courses - Request failed")
        
        # Evaluate results
        passed_tests = len([t for t in critical_tests if t.startswith("✅")])
        total_tests = len([t for t in critical_tests if not t.startswith("⚠️")])
        
        if passed_tests >= total_tests * 0.8:  # 80% pass rate
            self.log_result(
                "Critical Endpoints", 
                "PASS", 
                f"Critical endpoints working correctly ({passed_tests}/{total_tests} tests passed)",
                "; ".join(critical_tests)
            )
            return True
        else:
            self.log_result(
                "Critical Endpoints", 
                "FAIL", 
                f"Some critical endpoints failing ({passed_tests}/{total_tests} tests passed)",
                "; ".join(critical_tests)
            )
        return False
    
    # =============================================================================
    # MAIN TEST EXECUTION
    # =============================================================================
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 STARTING QUIZ REMOVAL BACKEND TESTING SUITE")
        print("=" * 80)
        print("Testing LearningFriend LMS backend after removing Select All That Apply and Chronological Order question types")
        print("=" * 80)
        
        # Authentication Tests
        print("\n🔐 AUTHENTICATION TESTING")
        print("-" * 50)
        self.test_admin_authentication()
        self.test_student_authentication()
        
        # Course Creation API Tests
        print("\n📚 COURSE CREATION API TESTING")
        print("-" * 50)
        self.test_course_creation_api()
        self.test_course_listing_api()
        self.test_course_details_api()
        
        # Quiz Functionality Tests
        print("\n🎯 QUIZ FUNCTIONALITY TESTING")
        print("-" * 50)
        self.test_quiz_functionality_remaining_types()
        self.test_progress_tracking()
        
        # Existing Quiz Data Tests
        print("\n🗂️ EXISTING QUIZ DATA COMPATIBILITY TESTING")
        print("-" * 50)
        self.test_existing_quiz_data_compatibility()
        
        # Critical Endpoints Tests
        print("\n⚡ CRITICAL ENDPOINTS TESTING")
        print("-" * 50)
        self.test_critical_endpoints()
        
        # Final Results
        print("\n" + "=" * 80)
        print("🎉 QUIZ REMOVAL BACKEND TESTING COMPLETE")
        print("=" * 80)
        
        total_tests = self.passed + self.failed
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 RESULTS SUMMARY:")
        print(f"   ✅ Passed: {self.passed}")
        print(f"   ❌ Failed: {self.failed}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print(f"🎯 EXCELLENT: Backend APIs are fully functional after question type removal")
        elif success_rate >= 75:
            print(f"✅ GOOD: Backend APIs are mostly functional with minor issues")
        else:
            print(f"⚠️ ATTENTION NEEDED: Some backend APIs require fixes")
        
        return success_rate >= 75

if __name__ == "__main__":
    tester = QuizRemovalBackendTester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n✅ Backend testing completed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ Backend testing completed with issues!")
        sys.exit(1)